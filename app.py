from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st


PROJEKTORDNER = Path(__file__).resolve().parent
MODELLDATEI = PROJEKTORDNER / "models" / "oulad_tag28_boosting.joblib"
SCHEMADATEI = PROJEKTORDNER / "models" / "oulad_tag28_schema.json"
DEMODATEI = PROJEKTORDNER / "data" / "demo" / "oulad_tag28_demo.csv"

st.set_page_config(
    page_title="LernRadar | Tag 28",
    layout="wide",
)

st.title("LernRadar")
st.caption("Portfolio-Prototyp · Unterstützungsbedarf am Ende von Kurstag 28")

st.markdown("### 1 · Daten hochladen")
st.write(
    "Lade eine **aufbereitete Tag-28-CSV** hoch. Jede Zeile steht für "
    "einen zu diesem Zeitpunkt noch angemeldeten Kurseintrag. "
    "Für eine sinnvolle kursweise Auswahl sollte die Datei jeweils "
    "den vollständigen Kursdurchlauf enthalten."
)

if DEMODATEI.exists():
    st.download_button(
        "OULAD-Vorführdatei herunterladen",
        data=DEMODATEI.read_bytes(),
        file_name="oulad_tag28_demo.csv",
        mime="text/csv",
    )

upload = st.file_uploader(
    "Tag-28-CSV auswählen",
    type="csv",
)

# Bis hierhin gibt es noch keine Grafiken oder Modellhinweise.
if upload is None:
    st.info("Nach dem Upload erscheinen Kursübersicht und Hinweise.")
    st.stop()

if not MODELLDATEI.exists() or not SCHEMADATEI.exists():
    st.error(
        "Modell oder CSV-Schema fehlen. Erzeuge beide mit der "
        "Speicherzelle in Notebook 05."
    )
    st.stop()

schema = json.loads(SCHEMADATEI.read_text(encoding="utf-8"))
schluessel = schema["schluessel"]
merkmale = schema["merkmale"]
pflichtspalten = list(dict.fromkeys(schluessel + merkmale))

with st.expander("Welche Spalten muss die CSV enthalten?"):
    st.write(", ".join(pflichtspalten))
    st.caption(
        "OULAD-Rohdateien wie studentVle.csv müssen zuvor "
        "zur Tag-28-Modellbasis aufbereitet werden."
    )


@st.cache_resource
def lade_modell():
    """Lädt das lokal gespeicherte Modell für die Vorhersage."""
    return joblib.load(MODELLDATEI)


try:
    daten = pd.read_csv(upload)
except Exception as fehler:
    st.error(f"Die CSV konnte nicht gelesen werden: {fehler}")
    st.stop()

fehlend = [
    spalte for spalte in pflichtspalten
    if spalte not in daten.columns
]
if fehlend:
    st.error("Diese Spalten fehlen: " + ", ".join(fehlend))
    st.stop()

if daten.empty:
    st.error("Die CSV enthält keine Kurseinträge.")
    st.stop()

# Später bekannte Ergebnisse aus einer CSV nicht als Eingaben verwenden.
daten = daten[pflichtspalten].copy()

zahlenspalten = [
    spalte for spalte in merkmale
    if spalte not in ["code_module", "code_presentation"]
]
for spalte in zahlenspalten:
    daten[spalte] = pd.to_numeric(daten[spalte], errors="coerce")

if daten[pflichtspalten].isna().any().any():
    st.error("Benötigte Spalten enthalten leere oder ungültige Werte.")
    st.stop()

if daten.duplicated(schluessel).any():
    st.error("Mindestens ein Kurseintrag steht mehrfach in der CSV.")
    st.stop()

if (daten["anmeldetag"] > 28).any():
    st.error("Ein Kurseintrag wurde erst nach Tag 28 angemeldet.")
    st.stop()

nichtnegative = [
    spalte for spalte in zahlenspalten
    if spalte != "anmeldetag"
]
if (daten[nichtnegative] < 0).any().any():
    st.error("Klick- und Assessmentzahlen dürfen nicht negativ sein.")
    st.stop()

try:
    modell = lade_modell()

    # Unbekannte historische Kurskennungen nicht stillschweigend bewerten.
    kategorien = (
        modell.named_steps["vorbereitung"]
        .named_transformers_["kategorien"]
        .categories_
    )
    unbekannte_module = (
        set(daten["code_module"]) - set(kategorien[0])
    )
    unbekannte_praesentationen = (
        set(daten["code_presentation"]) - set(kategorien[1])
    )
    if unbekannte_module or unbekannte_praesentationen:
        st.error(
            "Die Datei enthält Kurskennungen, die das gespeicherte "
            "Modell nicht aus seinem Training kennt. Dafür ist "
            "eine neue Prüfung des Modells erforderlich."
        )
        st.stop()

    # Der Wert dient hier nur zur Sortierung innerhalb eines Kurses.
    daten["modellwert"] = modell.predict_proba(
        daten[merkmale]
    )[:, 1]
except Exception as fehler:
    st.error(f"Die Modellbewertung ist fehlgeschlagen: {fehler}")
    st.stop()

st.success(f"{len(daten):,} Kurseinträge eingelesen.".replace(",", "."))


# Gesamtsicht: Was enthält die hochgeladene Datei?
st.markdown("### 2 · Überblick über die Kurse")
st.caption(
    "Die Grafiken beschreiben ausschließlich die hochgeladene Datei. "
    "Ein Kurseintrag ist eine Anmeldung in einem Kursdurchlauf; "
    "eine Person kann mehrfach vorkommen."
)

uebersicht = (
    daten.groupby(
        ["code_module", "code_presentation"],
        as_index=False,
    )
    .agg(
        kurseintraege=("id_student", "size"),
        mit_offenem_assessment=(
            "assessments_fehlend_bis28",
            lambda werte: int((werte > 0).sum()),
        ),
    )
)
uebersicht["Kurs"] = (
    uebersicht["code_module"]
    + " "
    + uebersicht["code_presentation"]
)

a, b, c = st.columns(3)
a.metric("Kurseinträge", len(daten))
b.metric("Kursdurchläufe", len(uebersicht))
c.metric(
    "Mit offenem fälligem Assessment",
    int((daten["assessments_fehlend_bis28"] > 0).sum()),
)

st.markdown("**Kurseinträge je Modul**")
st.bar_chart(
    uebersicht.groupby("code_module", as_index=False)[
        "kurseintraege"
    ].sum(),
    x="code_module",
    y="kurseintraege",
)
st.caption(
    "Die Balken zeigen, wie viele Einträge der Upload je Modul "
    "enthält. Sie zeigen noch keine gefährdeten Personen."
)

st.dataframe(
    uebersicht[
        ["Kurs", "kurseintraege", "mit_offenem_assessment"]
    ].rename(columns={
        "kurseintraege": "Kurseinträge",
        "mit_offenem_assessment": "Mit offenem Assessment",
    }),
    hide_index=True,
)


# Ein Kursdurchlauf: Hier wird die Kapazität der Betreuung festgelegt.
st.markdown("### 3 · Einen Kursdurchlauf betrachten")

wahl = st.selectbox(
    "Kursdurchlauf auswählen",
    range(len(uebersicht)),
    format_func=lambda i: uebersicht.iloc[i]["Kurs"],
)

modul = uebersicht.iloc[wahl]["code_module"]
praesentation = uebersicht.iloc[wahl]["code_presentation"]

kurs = daten.loc[
    daten["code_module"].eq(modul)
    & daten["code_presentation"].eq(praesentation)
].sort_values(
    "modellwert",
    ascending=False,
    kind="stable",
).copy()

quote = st.radio(
    "Kapazität für eine erste unterstützende Prüfung",
    [10, 20],
    format_func=lambda wert: f"{wert} % der Kurseinträge",
    horizontal=True,
)

anzahl = int(np.ceil(len(kurs) * quote / 100))
auswahl = kurs.head(anzahl).copy()
auswahl["Position"] = np.arange(1, len(auswahl) + 1)

st.caption(
    "Das Modell sortiert die hochgeladenen Kurseinträge dieses "
    "Kursdurchlaufs. Die Position ist eine Reihenfolge für die "
    "Prüfung, keine Note und keine gemessene Ausfallwahrscheinlichkeit."
)

a, b, c = st.columns(3)
a.metric("Kurseinträge", len(kurs))
b.metric("Hinweise für die erste Prüfung", len(auswahl))
c.metric(
    "Mit offenem fälligem Assessment",
    int((kurs["assessments_fehlend_bis28"] > 0).sum()),
)

# Unterschiedlich lange Zeitfenster auf Klicks pro Kalendertag bringen.
klickgrafik = pd.DataFrame({
    "Zeitraum": ["Tag 0–6", "Tag 7–14", "Tag 15–28"],
    "Median Klicks pro Tag": [
        (kurs["klicks_tag_0_bis_6"] / 7).median(),
        (kurs["klicks_tag_7_bis_14"] / 8).median(),
        (kurs["klicks_tag_15_bis_28"] / 14).median(),
    ],
})

st.markdown("**Erfasste VLE-Aktivität im Kursverlauf**")
st.bar_chart(
    klickgrafik,
    x="Zeitraum",
    y="Median Klicks pro Tag",
)
st.caption(
    "Gezeigt wird je Zeitfenster der Median der durchschnittlichen "
    "Klicks pro Kalendertag und Kurseintrag. Klicks messen "
    "Plattformnutzung, nicht Lernzeit oder Verständnis."
)

verteilung = (
    kurs["assessments_fehlend_bis28"]
    .clip(upper=3)
    .value_counts()
    .reindex([0, 1, 2, 3], fill_value=0)
)

st.markdown("**Fällige Assessments ohne erfasste Erfüllung**")
st.bar_chart(
    pd.DataFrame({
        "Offene Assessments": ["0", "1", "2", "3 oder mehr"],
        "Kurseinträge": verteilung.to_numpy(),
    }),
    x="Offene Assessments",
    y="Kurseinträge",
)
st.caption(
    "Gezählt werden Assessments mit Fälligkeit bis Tag 28, "
    "für die bis dahin keine eigene oder angerechnete Erfüllung "
    "erfasst wurde."
)


# Hinweise für eine unterstützende Sichtung.
st.markdown("### 4 · Kurseinträge für die erste Prüfung")
st.info(
    "Das Modellziel ist **spätere Abmeldung oder Nichtbestehen**. "
    "Es unterscheidet für einen einzelnen Hinweis nicht, "
    "welches dieser Ergebnisse eintreten könnte."
)

st.dataframe(
    auswahl[
        [
            "Position",
            "id_student",
            "assessments_fehlend_bis28",
            "klicks_tag_0_bis_6",
            "klicks_tag_7_bis_14",
            "klicks_tag_15_bis_28",
        ]
    ].rename(columns={
        "id_student": "Anonymisierte ID",
        "assessments_fehlend_bis28": "Offene Assessments",
        "klicks_tag_0_bis_6": "Klicks Tag 0–6",
        "klicks_tag_7_bis_14": "Klicks Tag 7–14",
        "klicks_tag_15_bis_28": "Klicks Tag 15–28",
    }),
    hide_index=True,
)

person = st.selectbox(
    "Einen Kurseintrag genauer ansehen",
    range(len(auswahl)),
    format_func=lambda i: (
        f"ID {auswahl.iloc[i]['id_student']} "
        f"· Position {i + 1}"
    ),
)
eintrag = auswahl.iloc[person]

st.markdown(f"#### Beobachtungen zu ID {eintrag['id_student']}")
st.caption(
    "Die folgenden Punkte sind beobachtete Merkmale bis Tag 28. "
    "Sie sind keine geprüfte Erklärung, warum das Modell "
    "diesen Eintrag ausgewählt hat."
)

beobachtungen = []

offen = int(eintrag["assessments_fehlend_bis28"])
if offen > 0:
    beobachtungen.append(
        f"{offen} bis Tag 28 fällige Assessments ohne "
        "erfasste Erfüllung."
    )

klickspalten = [
    "klicks_tag_0_bis_6",
    "klicks_tag_7_bis_14",
    "klicks_tag_15_bis_28",
]
klicks_person = eintrag[klickspalten].sum()
klicks_median = kurs[klickspalten].sum(axis=1).median()

if klicks_person < klicks_median:
    beobachtungen.append(
        "Weniger erfasste VLE-Klicks bis Tag 28 "
        "als der Median dieses Kursdurchlaufs."
    )

if eintrag["klicks_tag_15_bis_28"] == 0:
    beobachtungen.append(
        "Keine erfassten VLE-Klicks an Tag 15–28."
    )
elif (
    eintrag["klicks_tag_15_bis_28"] / 14
    < eintrag["klicks_tag_7_bis_14"] / 8
):
    beobachtungen.append(
        "Weniger Klicks pro Tag an Tag 15–28 "
        "als an Tag 7–14."
    )

if beobachtungen:
    for beobachtung in beobachtungen:
        st.write("• " + beobachtung)
else:
    st.write(
        "Keines der hier beschriebenen Einzelmerkmale fällt auf. "
        "Der Modellhinweis entsteht aus der Kombination "
        "mehrerer Eingaben."
    )

st.caption(
    "Ein sinnvoller nächster Schritt wäre, den Abgabestatus "
    "und den tatsächlichen Unterstützungsbedarf persönlich "
    "zu prüfen. Ein Modellhinweis allein begründet keine "
    "negative Entscheidung."
)

with st.expander("Alle Kurseinträge mit offenem fälligem Assessment"):
    offene_eintraege = kurs[
        kurs["assessments_fehlend_bis28"] > 0
    ]
    st.dataframe(
        offene_eintraege[
            ["id_student", "assessments_fehlend_bis28"]
        ].rename(columns={
            "id_student": "Anonymisierte ID",
            "assessments_fehlend_bis28": "Offene Assessments",
        }),
        hide_index=True,
    )