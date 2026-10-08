"""LernRadar: Wochenmonitor für den OULAD-Portfolio-Prototyp."""

from pathlib import Path

import pandas as pd
import streamlit as st

from weekly_logic import (
    KURS,
    SCHLUESSEL,
    UploadFehler,
    bewerte_wochen,
    lade_modell,
    lade_schema,
    pruefe_csv,
)


PROJEKTORDNER = Path(__file__).resolve().parent
MODELLORDNER = PROJEKTORDNER / "models" / "oulad_wochen"
SCHEMADATEI = MODELLORDNER / "schema.json"
DEMODATEI = PROJEKTORDNER / "data" / "demo" / "oulad_wochen_2014j.csv"

st.set_page_config(page_title="LernRadar | Wochenmonitor", layout="wide")

st.markdown(
    """
    <style>
    .block-container { max-width: 1240px; padding-top: 2rem; }
    .lr-hero { background: linear-gradient(105deg, #102948, #17676d);
               color: white; padding: 1.5rem 1.8rem; border-radius: 16px;
               margin-bottom: 1.3rem; }
    .lr-hero h1 { color: white; margin: 0; font-size: 2.2rem; }
    .lr-hero p { margin: .5rem 0 0; color: #e3f6f4; }
    div[data-testid="stMetric"] { background: #f2f7f8; padding: .8rem 1rem;
                                   border-radius: 12px; }
    </style>
    <div class="lr-hero">
      <h1>LernRadar</h1>
      <p>Wöchentliche Übersicht für eine unterstützende Sichtung von Kursen</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 1 · Wochenstände hochladen")
st.write(
    "Lade eine **aufbereitete OULAD-CSV** mit einem oder mehreren Stichtagen hoch. "
    "Jede Zeile beschreibt einen noch angemeldeten Kurseintrag an einem Kurstag. "
    "Für die Auswahl der obersten 10 oder 20 % sollte jeweils der vollständige "
    "Kursdurchlauf im Upload enthalten sein."
)

with st.expander("Kurzanleitung und benötigte Daten"):
    st.markdown(
        "1. Lade die Vorführdatei herunter oder bereite Kursdaten im Wochenformat auf.\n"
        "2. Lade die CSV hoch und wähle den Kurstag.\n"
        "3. Sieh dir die Kursübersicht an; öffne dann einen Kursdurchlauf.\n"
        "4. Prüfe Hinweise und beobachtete Merkmale fachlich, bevor du Kontakt aufnimmst."
    )
    st.caption(
        "Die OULAD-Rohdateien lassen sich hier nicht direkt hochladen. "
        "Die benötigte Datei entsteht durch die Aufbereitung in den Notebooks."
    )

if DEMODATEI.exists():
    st.download_button(
        "OULAD-Vorführdatei herunterladen",
        data=DEMODATEI.read_bytes(),
        file_name=DEMODATEI.name,
        mime="text/csv",
    )

upload = st.file_uploader("Wochen-CSV auswählen", type="csv")

# Vor dem Upload gibt es weder Grafiken noch Modellhinweise.
if upload is None:
    st.info("Nach dem Upload erscheinen Kursübersicht und Hinweise.")
    st.stop()

try:
    schema = lade_schema(MODELLORDNER)
except (UploadFehler, OSError, ValueError) as fehler:
    st.error(str(fehler))
    st.stop()

with st.expander("Erwartete Spalten der hochgeladenen CSV"):
    st.code(", ".join(schema["eingabespalten"]), language=None)
    st.caption("Zusätzliche Spalten, auch spätere Kursergebnisse, werden ignoriert.")


@st.cache_resource(show_spinner=False)
def modell_fuer_tag(stichtag: int, geaendert_ns: int | None):
    """Lädt ein Modell einmal pro Stichtag und Dateiversion."""
    return lade_modell(MODELLORDNER, schema, stichtag)


@st.cache_data(show_spinner=False)
def verarbeite_upload(dateiinhalt: bytes, dateisignatur: tuple):
    """Prüft und bewertet den Upload einmal pro Datei und Modellversion."""
    daten = pruefe_csv(dateiinhalt, schema)
    versionszeiten = dict(dateisignatur[1])
    return bewerte_wochen(
        daten,
        schema,
        lambda tag: modell_fuer_tag(tag, versionszeiten[tag]),
    )


# Ein erneuter Modell-Export macht den Streamlit-Cache automatisch ungültig.
signatur = (
    SCHEMADATEI.stat().st_mtime_ns,
    tuple(
        (
            int(tag),
            pfad.stat().st_mtime_ns if pfad.exists() else None,
        )
        for tag in schema["stichtage"]
        for pfad in [MODELLORDNER / schema["modellpfad_muster"].format(stichtag=tag)]
    ),
)

try:
    with st.spinner("Wochenstände werden geprüft und bewertet …"):
        daten = verarbeite_upload(upload.getvalue(), signatur)
except (UploadFehler, OSError, ValueError) as fehler:
    st.error(str(fehler))
    st.stop()
except Exception as fehler:
    st.error(f"Die Modellbewertung ist fehlgeschlagen: {fehler}")
    st.stop()

verfuegbare_tage = sorted(int(tag) for tag in daten["stichtag"].unique())
vorgabe = verfuegbare_tage.index(27) if 27 in verfuegbare_tage else len(verfuegbare_tage) - 1
meldung = (
    f"{len(daten):,} Wochenstände eingelesen · "
    f"{len(daten[SCHLUESSEL].drop_duplicates()):,} verschiedene Kurseinträge."
)
st.success(meldung.replace(",", "."))

st.markdown("### 2 · Woche wählen")
stichtag = st.selectbox(
    "Kurstag",
    verfuegbare_tage,
    index=vorgabe,
    format_func=lambda tag: f"Tag {tag} · Woche {(tag + 1) // 7}",
)
woche = daten.loc[daten["stichtag"].eq(stichtag)].copy()
hinweise = woche["hinweisstufe"].ne("Kein Hinweis")

if len(verfuegbare_tage) == 1 and stichtag != 6:
    st.warning(
        "Dieser Upload enthält nur einen Stichtag. Ob ein Hinweis schon "
        "in einer früheren Woche bestand, lässt sich damit nicht feststellen."
    )
else:
    st.caption(
        "‚Erstmals‘ und ‚wiederholt‘ beziehen sich ausschließlich auf "
        "die Wochenstände dieser hochgeladenen Datei."
    )

tab_ueberblick, tab_kurs, tab_verlauf, tab_hilfe = st.tabs(
    ["Überblick", "Kurs & Hinweise", "Verlauf", "Einordnung"]
)

with tab_ueberblick:
    st.subheader(f"Überblick am Ende von Tag {stichtag}")
    st.caption(
        "Die Grafiken beschreiben hochgeladene Kurseinträge. Eine Person "
        "kann in mehreren Kursdurchläufen stehen."
    )
    a, b, c, d = st.columns(4)
    a.metric("Kurseinträge", len(woche))
    b.metric("Kursdurchläufe", woche[KURS].drop_duplicates().shape[0])
    c.metric("Hinweise (oberste 20 % je Kurs)", int(hinweise.sum()))
    d.metric(
        "Erstmals im Upload",
        int(woche["hinweisstatus"].eq("Erstmals im Upload").sum())
        if len(verfuegbare_tage) > 1 or stichtag == 6 else "–",
    )

    uebersicht = (
        woche.assign(
            hohe_prioritaet=woche["hinweisstufe"].eq("Hohe Priorität"),
            weitere_pruefung=woche["hinweisstufe"].eq("Weitere Prüfung"),
            offenes_assessment=woche["assessments_fehlend"].gt(0),
        )
        .groupby(KURS, as_index=False)
        .agg(
            kurseintraege=("id_student", "size"),
            hohe_prioritaet=("hohe_prioritaet", "sum"),
            weitere_pruefung=("weitere_pruefung", "sum"),
            offenes_assessment=("offenes_assessment", "sum"),
        )
    )
    uebersicht["Kurs"] = (
        uebersicht["code_module"] + " " + uebersicht["code_presentation"]
    )
    uebersicht["Anteil mit offenem Assessment (%)"] = (
        100 * uebersicht["offenes_assessment"] / uebersicht["kurseintraege"]
    ).round(1)

    links, rechts = st.columns(2)
    with links:
        st.markdown("**Kurseinträge je Kursdurchlauf**")
        st.bar_chart(uebersicht, x="Kurs", y="kurseintraege")
        st.caption("Größe der im Upload enthaltenen Kursdurchläufe.")
    with rechts:
        st.markdown("**Anteil mit offenem fälligem Assessment**")
        st.bar_chart(uebersicht, x="Kurs", y="Anteil mit offenem Assessment (%)")
        st.caption(
            "Anteil der Kurseinträge mit mindestens einer bis zum Stichtag "
            "fälligen Leistung ohne erfasste Erfüllung."
        )
    st.dataframe(
        uebersicht[
            ["Kurs", "kurseintraege", "hohe_prioritaet",
             "weitere_pruefung", "offenes_assessment"]
        ].rename(columns={
            "kurseintraege": "Kurseinträge",
            "hohe_prioritaet": "Hohe Priorität (10 %)",
            "weitere_pruefung": "Weitere Prüfung (nächste 10 %)",
            "offenes_assessment": "Mit offenem fälligem Assessment",
        }),
        hide_index=True,
    )

with tab_kurs:
    st.subheader("Einen Kursdurchlauf prüfen")
    kurse = woche[KURS].drop_duplicates().sort_values(KURS).reset_index(drop=True)
    kurse["Name"] = kurse["code_module"] + " " + kurse["code_presentation"]
    wahl = st.selectbox("Kursdurchlauf", range(len(kurse)),
                         format_func=lambda i: kurse.iloc[i]["Name"])
    modul = kurse.iloc[wahl]["code_module"]
    praesentation = kurse.iloc[wahl]["code_presentation"]
    kurs = woche.loc[
        woche["code_module"].eq(modul)
        & woche["code_presentation"].eq(praesentation)
    ].sort_values("modellwert", ascending=False, kind="stable")

    quote = st.radio(
        "Umfang der Prüfliste",
        [10, 20],
        format_func=lambda wert: (
            "Nur hohe Priorität (10 %)" if wert == 10
            else "Hohe Priorität und weitere Prüfung (20 %)"
        ),
        horizontal=True,
    )
    ausgewaehlt = kurs.loc[
        kurs["hinweisstufe"].eq("Hohe Priorität")
        if quote == 10 else kurs["hinweisstufe"].ne("Kein Hinweis")
    ].copy()

    a, b, c, d = st.columns(4)
    a.metric("Kurseinträge", len(kurs))
    b.metric("Auf der Prüfliste", len(ausgewaehlt))
    c.metric(
        "Davon erstmals im Upload",
        int(ausgewaehlt["hinweisstatus"].eq("Erstmals im Upload").sum())
        if len(verfuegbare_tage) > 1 or stichtag == 6 else "–",
    )
    d.metric("Mit offenem Assessment", int(kurs["assessments_fehlend"].gt(0).sum()))

    st.info(
        "Die Liste priorisiert eine fachliche Sichtung. Das Modellziel ist "
        "späterer Abbruch **oder** späteres Nichtbestehen; es bestimmt "
        "für eine einzelne Person nicht die Art des möglichen Ergebnisses."
    )
    st.dataframe(
        ausgewaehlt[
            ["id_student", "hinweisstufe", "hinweisstatus",
             "assessments_faellig", "assessments_fehlend", "abgaben",
             "klicks_letzte_7_tage", "klicks_bis_stichtag"]
        ].rename(columns={
            "id_student": "Anonymisierte ID",
            "hinweisstufe": "Prüfgruppe",
            "hinweisstatus": "Verlauf des Hinweises",
            "assessments_faellig": "Fällige Assessments",
            "assessments_fehlend": "Ohne erfasste Erfüllung",
            "abgaben": "Eigene Abgaben",
            "klicks_letzte_7_tage": "VLE-Klicks letzte 7 Tage",
            "klicks_bis_stichtag": "VLE-Klicks bis Tag",
        }),
        hide_index=True,
    )
    st.caption(
        "Die Reihenfolge folgt dem Modellwert innerhalb dieses Kurses. "
        "Ein Modellwert ist hier keine geprüfte individuelle Ausfallwahrscheinlichkeit."
    )

    st.markdown("**Offene fällige Assessments in diesem Kurs**")
    verteilung = (
        kurs["assessments_fehlend"].clip(upper=3)
        .value_counts().reindex([0, 1, 2, 3], fill_value=0)
    )
    st.bar_chart(pd.DataFrame({
        "Offene Assessments": ["0", "1", "2", "3 oder mehr"],
        "Kurseinträge": verteilung.to_numpy(),
    }), x="Offene Assessments", y="Kurseinträge")
    st.caption(
        "Gezählt werden bis zum gewählten Tag fällige Assessments ohne "
        "erfasste eigene oder angerechnete Erfüllung."
    )

    if not ausgewaehlt.empty:
        st.markdown("#### Einen Hinweis genauer ansehen")
        positionen = list(range(len(ausgewaehlt)))
        person = st.selectbox(
            "Kurseintrag",
            positionen,
            format_func=lambda i: (
                f"ID {ausgewaehlt.iloc[i]['id_student']} · "
                f"{ausgewaehlt.iloc[i]['hinweisstufe']}"
            ),
        )
        eintrag = ausgewaehlt.iloc[person]
        st.caption(
            "Dies sind beobachtete Daten bis zum ausgewählten Tag. "
            "Sie erklären nicht kausal, warum das Modell den Hinweis vergibt."
        )
        beobachtungen = []
        offen = int(eintrag["assessments_fehlend"])
        if offen:
            beobachtungen.append(
                f"{offen} fällige Assessments ohne erfasste Erfüllung."
            )
        if eintrag["klicks_letzte_7_tage"] == 0:
            beobachtungen.append("Keine erfassten VLE-Klicks in den letzten sieben Tagen.")
        elif eintrag["klicks_letzte_7_tage"] < kurs["klicks_letzte_7_tage"].median():
            beobachtungen.append(
                "Weniger VLE-Klicks in den letzten sieben Tagen "
                "als der Median dieses Kursdurchlaufs."
            )
        if not beobachtungen:
            beobachtungen.append(
                "Keines dieser einfachen Einzelmerkmale fällt auf; "
                "der Modellhinweis beruht auf der Kombination der Eingaben."
            )
        for beobachtung in beobachtungen:
            st.write("• " + beobachtung)
        st.caption(
            "Nächster Schritt: Angaben und Unterstützungsbedarf persönlich prüfen. "
            "Der Hinweis allein begründet keine negative Entscheidung."
        )

        person_verlauf = daten.loc[
            daten["code_module"].eq(modul)
            & daten["code_presentation"].eq(praesentation)
            & daten["id_student"].eq(eintrag["id_student"])
            & daten["stichtag"].le(stichtag)
        ].sort_values("stichtag")
        if len(person_verlauf) > 1:
            st.markdown("**Erfasste Klicks dieser Person in den letzten sieben Tagen je Stichtag**")
            st.line_chart(person_verlauf, x="stichtag", y="klicks_letzte_7_tage")
            st.caption("Klicks messen Plattformnutzung, nicht Lernzeit oder Verständnis.")

with tab_verlauf:
    st.subheader("Verlauf der hochgeladenen Kurswochen")
    st.caption(
        "Ein wiederholter Hinweis ist eine erneute Anzeige desselben "
        "Kurseintrags. Er bedeutet nicht automatisch, dass erneut Kontakt nötig ist."
    )
    verlauf = (
        daten.assign(
            neuer_hinweis=daten["hinweisstatus"].eq("Erstmals im Upload"),
            wiederholung=daten["hinweisstatus"].eq("Wiederholt im Upload"),
        )
        .groupby("stichtag", as_index=False)
        .agg(
            kurseintraege=("id_student", "size"),
            neue_hinweise=("neuer_hinweis", "sum"),
            wiederholte_hinweise=("wiederholung", "sum"),
        )
    )
    if len(verlauf) > 1:
        st.line_chart(verlauf, x="stichtag", y="kurseintraege")
        st.caption("Kurseinträge, die am jeweiligen Kurstag im Upload enthalten sind.")
        st.bar_chart(verlauf, x="stichtag", y=["neue_hinweise", "wiederholte_hinweise"])
        st.caption(
            "Die Hinweise sind je Kursdurchlauf auf 20 % begrenzt. "
            "‚Neu‘ gilt nur relativ zu den hochgeladenen Wochen."
        )
    else:
        st.info("Für einen zeitlichen Verlauf bitte mehrere Kurswochen hochladen.")
    st.dataframe(
        verlauf.rename(columns={
            "stichtag": "Kurstag",
            "kurseintraege": "Kurseinträge",
            "neue_hinweise": "Erstmals im Upload",
            "wiederholte_hinweise": "Wiederholt im Upload",
        }),
        hide_index=True,
    )

with tab_hilfe:
    st.subheader("Was bedeuten die Angaben?")
    st.markdown(
        "- **VLE (Virtual Learning Environment):** die virtuelle Lernumgebung. "
        "Klicks zeigen nur erfasste Interaktionen.\n"
        "- **Assessment:** eine im Kurs vorgesehene bewertete Leistung. "
        "‚Ohne erfasste Erfüllung‘ berücksichtigt eigene und angerechnete Abgaben.\n"
        "- **Hohe Priorität:** oberste 10 % der Modellreihenfolge je Kurs. "
        "**Weitere Prüfung:** die nächsten 10 %.\n"
        "- **Erstmals/Wiederholt:** nur anhand der im Upload vorhandenen Wochen."
    )
    st.markdown("**Grenzen des Prototyps**")
    st.write(
        "Die Modelle wurden mit historischen OULAD-Kursen trainiert. "
        "2014J dient als explorative zeitliche Prüfung und Demo. "
        "Das gemeinsame Modellziel lautet Abbruch oder Nichtbestehen; "
        "die Art eines individuellen Risikos und die Wirkung von Unterstützung "
        "werden damit nicht bestimmt. Ein Einsatz in anderen Bildungskontexten "
        "erfordert eine neue Daten- und Güteprüfung."
    )
