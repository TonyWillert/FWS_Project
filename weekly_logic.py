"""CSV-Prüfung und kursweise Hinweise für den OULAD-Wochenprototyp."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


SCHLUESSEL = ["code_module", "code_presentation", "id_student"]
KURS = ["code_module", "code_presentation"]
ZAHLSPALTEN = [
    "assessments_faellig",
    "abgaben",
    "banked_faellige",
    "assessments_fehlend",
    "klicks_bis_stichtag",
    "klicks_letzte_7_tage",
]


class UploadFehler(ValueError):
    """Eine hochgeladene Datei passt nicht zum Wochenmodell."""


def lade_schema(modellordner: Path) -> dict:
    """Liest das beim Modell-Export erzeugte CSV- und Modell-Schema."""
    pfad = modellordner / "schema.json"
    if not pfad.exists():
        raise UploadFehler(f"Das Wochen-Schema fehlt: {pfad}")
    schema = json.loads(pfad.read_text(encoding="utf-8"))
    for feld in ("stichtage", "eingabespalten", "modellspalten", "modellpfad_muster"):
        if feld not in schema:
            raise UploadFehler(f"Im Wochen-Schema fehlt: {feld}")
    return schema


def pruefe_csv(dateiinhalt: bytes, schema: dict) -> pd.DataFrame:
    """Prüft einen oder mehrere Wochenstände, bevor ein Modell geladen wird."""
    try:
        original = pd.read_csv(BytesIO(dateiinhalt), low_memory=False)
    except Exception as fehler:
        raise UploadFehler(f"Die CSV konnte nicht gelesen werden: {fehler}") from fehler

    pflicht = schema["eingabespalten"]
    fehlend = [spalte for spalte in pflicht if spalte not in original.columns]
    if fehlend:
        raise UploadFehler("Diese Spalten fehlen: " + ", ".join(fehlend))
    if original.empty:
        raise UploadFehler("Die CSV enthält keine Kurseinträge.")

    # Zusätzliche Spalten, insbesondere spätere Ergebnisse, werden verworfen.
    daten = original[pflicht].copy()
    if daten[pflicht].isna().any().any():
        raise UploadFehler("Benötigte Spalten enthalten leere Werte.")

    for spalte in KURS:
        daten[spalte] = daten[spalte].astype(str).str.strip()
        if daten[spalte].eq("").any():
            raise UploadFehler(f"Leere Kurskennung in {spalte}.")

    numerisch = ["stichtag", "anmeldetag"] + ZAHLSPALTEN
    for spalte in numerisch:
        daten[spalte] = pd.to_numeric(daten[spalte], errors="coerce")
    if daten[numerisch].isna().any().any():
        raise UploadFehler("Stichtag, Anmeldung, Klicks und Assessments müssen Zahlen sein.")

    if (daten["stichtag"] % 1 != 0).any():
        raise UploadFehler("Stichtage müssen ganze Kurstage sein.")
    daten["stichtag"] = daten["stichtag"].astype(int)
    ungueltige_tage = sorted(set(daten["stichtag"]) - set(schema["stichtage"]))
    if ungueltige_tage:
        raise UploadFehler(f"Für diese Stichtage gibt es kein Modell: {ungueltige_tage}")

    if (daten["anmeldetag"] > daten["stichtag"]).any():
        raise UploadFehler("Ein Kurseintrag wurde erst nach seinem Stichtag angemeldet.")
    if (daten[ZAHLSPALTEN] < 0).any().any():
        raise UploadFehler("Klicks und Assessmentzahlen dürfen nicht negativ sein.")
    if ((daten[ZAHLSPALTEN] % 1) != 0).any().any():
        raise UploadFehler("Klicks und Assessmentzahlen müssen ganze Zahlen sein.")
    if (daten["assessments_fehlend"] > daten["assessments_faellig"]).any():
        raise UploadFehler("Fehlende Assessments übersteigen die fälligen Assessments.")
    if (daten["klicks_letzte_7_tage"] > daten["klicks_bis_stichtag"]).any():
        raise UploadFehler("Klicks der letzten Woche übersteigen die gesamten Klicks.")
    if daten.duplicated(["stichtag"] + SCHLUESSEL).any():
        raise UploadFehler("Ein Kurseintrag steht am selben Stichtag mehrfach in der CSV.")
    return daten


def lade_modell(modellordner: Path, schema: dict, stichtag: int):
    """Lädt die zum Stichtag passende gespeicherte Pipeline."""
    dateiname = schema["modellpfad_muster"].format(stichtag=stichtag)
    datei = modellordner / dateiname
    if not datei.exists():
        raise UploadFehler(f"Das Modell für Tag {stichtag} fehlt: {datei.name}")
    return joblib.load(datei)


def bewerte_wochen(daten: pd.DataFrame, schema: dict, modell_laden) -> pd.DataFrame:
    """Bewertet jede Woche und markiert die obersten 10 und 20 % je Kurs."""
    bewertet = []
    for tag in sorted(daten["stichtag"].unique()):
        woche = daten.loc[daten["stichtag"].eq(tag)].copy()
        modell = modell_laden(int(tag))

        # 2014J ist als Kurspräsentation im Training unbekannt und wird
        # vom gespeicherten Encoder absichtlich zugelassen. Ein völlig
        # unbekanntes Modul soll dagegen nicht stillschweigend bewertet werden.
        bekannte_module = set(
            modell.named_steps["vorbereitung"]
            .named_transformers_["kategorien"].categories_[0]
        )
        unbekannt = set(woche["code_module"]) - bekannte_module
        if unbekannt:
            raise UploadFehler(
                "Für diese Module gibt es keine Trainingsdaten: "
                + ", ".join(sorted(unbekannt))
            )

        klassen = np.asarray(modell.classes_)
        positive_klasse = np.flatnonzero(klassen == 1)
        if len(positive_klasse) != 1:
            raise UploadFehler(f"Das Modell für Tag {tag} hat keine positive Klasse 1.")
        woche["modellwert"] = modell.predict_proba(
            woche[schema["modellspalten"]]
        )[:, positive_klasse[0]]
        if not np.isfinite(woche["modellwert"]).all():
            raise UploadFehler(f"Das Modell für Tag {tag} lieferte ungültige Werte.")
        bewertet.append(woche)

    ergebnis = pd.concat(bewertet).sort_index().copy()
    gruppen = ["stichtag"] + KURS
    groesse = ergebnis.groupby(gruppen)["modellwert"].transform("size")
    rang = ergebnis.groupby(gruppen)["modellwert"].rank(
        ascending=False, method="first"
    )

    hoch = rang.le(np.ceil(groesse * 0.10))
    hinweis = rang.le(np.ceil(groesse * 0.20))
    ergebnis["hinweisstufe"] = np.select(
        [hoch, hinweis], ["Hohe Priorität", "Weitere Prüfung"],
        default="Kein Hinweis",
    )

    # Ein Kurseintrag erhält nur dann einen neuen Hinweis, wenn er im
    # hochgeladenen Verlauf zuvor noch nie unter den obersten 20 % war.
    erste_tage = (
        ergebnis.loc[hinweis]
        .groupby(SCHLUESSEL)["stichtag"]
        .min()
        .rename("ersthinweis_tag")
    )
    ergebnis = ergebnis.join(erste_tage, on=SCHLUESSEL)
    ergebnis["hinweisstatus"] = "Kein Hinweis"
    ergebnis.loc[hinweis, "hinweisstatus"] = "Wiederholt im Upload"
    ergebnis.loc[
        hinweis & ergebnis["stichtag"].eq(ergebnis["ersthinweis_tag"]),
        "hinweisstatus",
    ] = "Erstmals im Upload"

    if len(daten["stichtag"].unique()) == 1 and daten["stichtag"].iloc[0] != 6:
        ergebnis.loc[hinweis, "hinweisstatus"] = "Ohne Verlauf"
    return ergebnis
