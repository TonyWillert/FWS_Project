"""Belegte Hintergrundinformationen für die zweisprachige OULAD-Demo.

Modulbereiche und Zahl der Durchläufe: Kuzilek et al. (2017), Tabelle 1.
Längen der Durchläufe 2014J: OULAD courses.csv (im Projekt geprüft).
Diese Angaben dienen der Erklärung und werden nicht als neue Merkmale trainiert.
"""

from __future__ import annotations

import pandas as pd


DATASET_URL = "https://research.stem.open.ac.uk/ouanalyse/dataset/"
PAPER_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5704676/"

# Code, Fachbereich, Zahl der veröffentlichten Durchläufe, Länge von 2014J.
MODULES = [
    ("AAA", "social", 2, 269),
    ("BBB", "social", 4, 262),
    ("CCC", "stem", 2, 269),
    ("DDD", "stem", 4, 262),
    ("EEE", "stem", 3, 269),
    ("FFF", "stem", 4, 269),
    ("GGG", "social", 3, 269),
]

RAW_FILES = [
    ("courses.csv", "courses"),
    ("assessments.csv", "assessments"),
    ("vle.csv", "vle"),
    ("studentInfo.csv", "info"),
    ("studentRegistration.csv", "registration"),
    ("studentAssessment.csv", "student_assessments"),
    ("studentVle.csv", "student_vle"),
]

CONTEXT = {
    "de": {
        "title": "Über die Demo und ihre Daten",
        "lead": (
            "LearnerCue ist ein **lokaler Forschungsprototyp**: Eine vorbereitete "
            "CSV wird hochgeladen, und ein Modell sortiert die zu diesem "
            "Kurstag noch angemeldeten Kurseinträge innerhalb jedes Kurses. "
            "Die kurze Liste umfasst etwa 10 %, die erweiterte etwa 20 %. "
            "Ein Eintrag bedeutet: *fachlich prüfen und gegebenenfalls Hilfe anbieten*."
        ),
        "source_title": "Herkunft und Aufbau",
        "source_body": (
            "Grundlage ist der anonymisierte **Open University Learning Analytics "
            "Dataset (OULAD)**: sieben ausgewählte Module mit 22 Durchläufen "
            "aus 2013 und 2014. Die Dateien enthalten Kursstruktur, An- und "
            "Abmeldung, Aufgaben, Ergebnisse und täglich zusammengefasste "
            "Interaktionen mit der virtuellen Lernumgebung (VLE). Ein "
            "Kurseintrag ist die Teilnahme einer Person an einem bestimmten "
            "Durchlauf; dieselbe Person kann in mehreren Kursen vorkommen."
        ),
        "selection": (
            "Für OULAD wurden unter anderem nur Module mit mehreren Durchläufen, "
            "verfügbaren VLE-Daten, größeren Gruppen und einer nennenswerten "
            "Zahl nicht bestandener Fälle ausgewählt. Es handelt sich deshalb "
            "nicht um eine Zufallsstichprobe aller Weiterbildungen."
        ),
        "files_title": "Was in den sieben Originaldateien steckt",
        "files_columns": ("Datei", "Was sie enthält"),
        "files": {
            "courses": "Modul, Durchlauf und Dauer; die Dauer ist kein Merkmal der exportierten Modelle.",
            "assessments": "Art und Fälligkeit der Aufgaben; Basis für frühe fällige Leistungen.",
            "vle": "Materialtypen und geplante Wochen; keine lesbaren Lehrinhalte oder Lehrpläne.",
            "info": "Demografie und finales Kursergebnis. Das Ergebnis dient nur der rückblickenden Modellbewertung, nicht als Upload-Merkmal.",
            "registration": "Anmeldetag und gegebenenfalls Abmeldetag; für Stichtag und spätere Abbruchzuordnung.",
            "student_assessments": "Frühe Abgaben und angerechnete Leistungen. Punktzahlen sind im aktuellen Modell nicht enthalten.",
            "student_vle": "Tagesweise erfasste Plattforminteraktionen; daraus werden Klicksummen bis zum Stichtag gebildet.",
        },
        "courses_title": "Was wissen wir über die sieben Module?",
        "courses_columns": ("Modul", "Grober Fachbereich", "Durchläufe im Datensatz", "Dauer 2014J (Tage)"),
        "social": "Sozialwissenschaften",
        "stem": "STEM (Mathematik, Informatik, Naturwissenschaften, Technik)",
        "courses_note": (
            "Fachbereich und Zahl der Durchläufe stammen aus der Originalstudie; "
            "die Dauer von 2014J aus `courses.csv`. Diese Tabelle beschreibt "
            "OULAD insgesamt, nicht die Größe der gerade hochgeladenen CSV."
        ),
        "course_profile": "{module} {presentation}: {field}; Dauer dieses Durchlaufs: {days} Tage. Der konkrete Modultitel ist anonymisiert.",
        "course_profile_other": "{module} {presentation}: {field}. Der konkrete Modultitel ist anonymisiert. Die Projekttabelle nennt nur die Dauer von 2014J.",
        "course_about_button": "Mehr über die OULAD-Kurse",
        "content_title": "Sind die konkreten Kursinhalte bekannt?",
        "content_body": (
            "Die Originalstudie nennt nur diese **breiten Fachbereiche**. "
            "Modulnamen wurden absichtlich durch AAA bis GGG ersetzt. "
            "Es gibt in OULAD keine verlässliche Zuordnung von AAA–GGG "
            "zu konkreten Modultiteln, Lehrplänen oder Themen. `vle.csv` "
            "nennt Materialtypen und Zeitfenster; das ist kein Einblick "
            "in den eigentlichen Inhalt einer Vorlesung oder Aufgabe."
        ),
        "demo_title": "Was passiert mit der Vorführdatei?",
        "demo_body": (
            "Die lokal erzeugte Datei `oulad_wochen_2014j.csv` umfasst 121.447 "
            "wöchentliche Datenstände zu 8.682 unterschiedlichen Kurseinträgen "
            "aus 2014J. Sie enthält **keine späteren Kursergebnisse**. "
            "Für die exportierten 16 Wochenmodelle wurden frühere "
            "Durchläufe als Trainingsdaten genutzt; 1.403 Personen mit "
            "Überschneidungen wurden aus der Demo ausgeschlossen. Nach dem "
            "Upload prüft die App Pflichtspalten und Werte, lädt das Modell "
            "für den gewählten Tag und ordnet je Kurs die höchsten Modellwerte "
            "den kurzen beziehungsweise erweiterten Prüflisten zu."
        ),
        "model_title": "Welche Angaben beeinflussen die Reihenfolge?",
        "model_body": (
            "Die Modelle nutzen **Modul und Durchlauf**, Anmeldetag, "
            "bis zum Stichtag fällige, abgegebene, angerechnete und noch "
            "fehlende Aufgaben sowie **Klicks insgesamt und in den letzten "
            "sieben Tagen**. Für Tag 6, 13, …, 111 gibt es jeweils ein "
            "eigenes Histogram-Gradient-Boosting-Modell. Die anonymisierte "
            "ID verbindet nur Datenstände; sie ist kein Modellmerkmal. "
            "Bildungsabschluss, Alter, Einschränkung und Assessment-Noten "
            "gehen nicht in die exportierten Modelle ein."
        ),
        "label_body": (
            "Beim Training wurde rückblickend geprüft, ob eine am Stichtag "
            "noch angemeldete Person **später abbrach oder mit `Fail` "
            "abschloss**. Die Art des späteren Ereignisses wird in der App "
            "nicht einzeln vorhergesagt. Die Modellwerte sortieren die "
            "Prüfliste; sie sind hier **keine geprüften persönlichen "
            "Ausfallwahrscheinlichkeiten**."
        ),
        "evidence_title": "Wie gut war die historische Einordnung?",
        "evidence_body": (
            "Bei der explorativen Auswertung von 2014J an Tag 27 standen "
            "**1.006 von 2.947** späteren Fällen auf der erweiterten "
            "Prüfliste (34,1 % Recall). Insgesamt gab es 1.567 Hinweise; "
            "nicht alle führten später zu Abbruch oder `Fail`. Die Average "
            "Precision betrug 0,625 gegenüber 0,429 für ein Modell allein "
            "mit Kurs und Anmeldung. Über 16 wöchentliche Sichtungen "
            "erschienen 4.768 von 8.682 Kurseinträgen mindestens einmal "
            "auf einer erweiterten Liste (54,9 %). 2014J wurde bei der "
            "Entwicklung mehrfach betrachtet: Das ist **kein unberührter "
            "Abschlusstest** und keine Zusage für neue Kurse."
        ),
        "benefit_title": "Worin liegt der mögliche Mehrwert?",
        "benefit_body": (
            "Die App bündelt bereits vorhandene Kursdaten in einer "
            "nach Kurs sortierten Sichtung und macht die mögliche "
            "Betreuungsarbeit planbar. Coaches können Beobachtungen prüfen "
            "und passende Hilfe anbieten; die Leitungsansicht zeigt "
            "Planungsannahmen für Zeit und Kapazität. Der nachgewiesene "
            "Gewinn betrifft bisher nur die **Reihenfolge historischer "
            "Fälle**. Ob eine Ansprache Lernverläufe verbessert oder "
            "Arbeitszeit spart, muss erst in einer Einrichtung gemessen werden."
        ),
        "ideas_title": "Was ließe sich an Kursunterschieden noch prüfen?",
        "ideas_body": (
            "`assessments.csv` erlaubt künftig eine Trennung fälliger "
            "Aufgaben nach Aufgabentyp. Die Verbindung von `vle.csv` "
            "und `studentVle.csv` könnte frühe Interaktionen nach "
            "Materialtyp und geplanter Kurswoche unterscheiden. Das "
            "wären **neue Merkmale**, keine wiedergefundenen Kursinhalte. "
            "Sie müssten je Kurs und Stichtag ohne spätere Informationen "
            "gebildet und erneut zeitlich und nach Gruppen geprüft werden."
        ),
        "limits_title": "Wichtige Grenzen",
        "limits": [
            "OULAD ist ein ausgewählter historischer Datensatz einer Fernuniversität; die Übertragung auf heutige Weiterbildungen ist ungeprüft.",
            "Klickzahlen messen weder Verständnis noch Lernzeit außerhalb der Plattform; auch fehlende Aufgaben können technische oder organisatorische Gründe haben.",
            "Abbruch und Nichtbestehen sind verschiedene Ereignisse, werden hier aber gemeinsam priorisiert. Die konkrete Unterstützung entscheidet ein Mensch.",
            "Nur bis zum Stichtag noch angemeldete Personen und Wochen bis Tag 111 werden bewertet. Frühere Abbrüche und spätere Kursphasen sind nicht Teil dieses Prototyps.",
            "Demo und Modelle enthalten keine Namen oder Kontaktwege. Die App versendet nichts, dokumentiert keine Gespräche und trennt Zugriffsrechte nicht nach Rollen.",
            "Die Wirkung einer Ansprache, Gruppenunterschiede und Einsatzkosten sind nicht unabhängig für eine andere Einrichtung belegt.",
        ],
        "sources_title": "Quellen und vertiefende Dokumentation",
        "source_label": "Offizielle Datensatzseite",
        "paper_label": "Originalveröffentlichung mit Modultabelle und Anonymisierung",
        "readme_note": "Im Projektordner beschreiben README und Analyse-Notebooks die konkreten Berechnungen und ihre bisherigen Ergebnisse.",
    },
    "en": {
        "title": "About the demo and its data",
        "lead": (
            "LearnerCue is a **local research prototype**: upload a prepared "
            "CSV, and a model ranks the course entries still enrolled on a "
            "selected day within each course. The short list covers roughly "
            "10% and the extended list roughly 20%. A listed entry is an "
            "invitation to *review the situation and consider offering help*."
        ),
        "source_title": "Source and structure",
        "source_body": (
            "The anonymised **Open University Learning Analytics Dataset "
            "(OULAD)** contains seven selected modules taught in 22 "
            "presentations during 2013 and 2014. Its files describe course "
            "structure, registration, assignments, outcomes and daily "
            "summaries of activity in the Virtual Learning Environment (VLE). "
            "A course entry is one person's enrolment in one presentation; "
            "the same person may have several course entries."
        ),
        "selection": (
            "The published selection required, among other things, multiple "
            "presentations, available VLE data, sizeable groups and a "
            "significant number of failures. It is not a random sample "
            "of all training programmes."
        ),
        "files_title": "What the seven original files contain",
        "files_columns": ("File", "Contents"),
        "files": {
            "courses": "Module, presentation and length; length is not an exported model feature.",
            "assessments": "Assessment types and due dates used to count early due work.",
            "vle": "Material types and planned weeks; no readable teaching content or syllabus.",
            "info": "Demographics and final outcome. Outcomes are used only in retrospective evaluation, not as upload features.",
            "registration": "Registration and possible withdrawal dates; used for eligibility and later withdrawal labels.",
            "student_assessments": "Early submissions and credited work. Assessment scores are not included in the current model.",
            "student_vle": "Daily recorded platform interactions, aggregated into clicks up to the selected day.",
        },
        "courses_title": "What do we know about the seven modules?",
        "courses_columns": ("Module", "Broad field", "Presentations in dataset", "2014J length (days)"),
        "social": "Social sciences",
        "stem": "STEM (science, technology, engineering and mathematics)",
        "courses_note": (
            "Fields and presentation counts come from the original paper; "
            "2014J lengths come from `courses.csv`. This table describes the "
            "published dataset, not the size of the uploaded CSV."
        ),
        "course_profile": "{module} {presentation}: {field}; this presentation lasts {days} days. The actual module title is anonymised.",
        "course_profile_other": "{module} {presentation}: {field}. The actual module title is anonymised. The project table shows length only for 2014J.",
        "course_about_button": "About the OULAD modules",
        "content_title": "Do we know the actual course content?",
        "content_body": (
            "The original publication provides only **broad subject fields**. "
            "Module names were deliberately replaced with AAA–GGG. "
            "OULAD does not reliably map these codes to actual titles, "
            "syllabuses or topics. `vle.csv` lists material types and time "
            "windows, not the teaching content of a lecture or assignment."
        ),
        "demo_title": "What happens to the demo file?",
        "demo_body": (
            "The locally generated `oulad_wochen_2014j.csv` contains 121,447 "
            "weekly records for 8,682 distinct course entries in 2014J. "
            "It contains **no later outcomes**. The 16 exported weekly models "
            "were trained on earlier presentations; 1,403 people with "
            "overlap were excluded from the demo. After upload, the app "
            "checks the required columns and values, loads the model for "
            "the selected day and places the highest ranked entries "
            "within each course on short and extended review lists."
        ),
        "model_title": "Which data influence the ranking?",
        "model_body": (
            "The models use **module and presentation**, registration day, "
            "due, submitted, credited and still outstanding assessments "
            "up to the selected day, plus **total clicks and clicks in "
            "the last seven days**. There is a separate histogram gradient "
            "boosting model for days 6, 13, …, 111. The anonymised ID "
            "only joins records and is not a model feature. Prior education, "
            "age, declared disability and assessment scores are not "
            "features of the exported models."
        ),
        "label_body": (
            "During training, the later result was checked only for those "
            "still enrolled at the selected day: **later withdrawal or a "
            "final `Fail`**. The app does not predict which of the two "
            "will happen for an individual. Model scores order the "
            "review list; they are **not validated personal probabilities**."
        ),
        "evidence_title": "What happened in the historical evaluation?",
        "evidence_body": (
            "In the exploratory 2014J evaluation on day 27, **1,006 of "
            "2,947** later cases were on the extended review lists "
            "(34.1% recall). There were 1,567 alerts overall; not all "
            "later resulted in withdrawal or `Fail`. Average precision "
            "was 0.625 versus 0.429 for a reference using course and "
            "registration alone. Across 16 weekly reviews, 4,768 of "
            "8,682 course entries appeared on an extended list at least "
            "once (54.9%). 2014J was consulted repeatedly during model "
            "development, so this is **not an untouched final test** "
            "or a promise for new courses."
        ),
        "benefit_title": "Where could this help?",
        "benefit_body": (
            "The app brings existing course data into one review order and "
            "makes potential support workload visible. Coaches can verify "
            "observations and offer suitable help; the management view "
            "shows adjustable assumptions about time and capacity. The "
            "demonstrated benefit so far concerns only **ranking "
            "historical cases**. Whether outreach improves learning "
            "or saves time must be measured in a real provider setting."
        ),
        "ideas_title": "What could be investigated about course differences?",
        "ideas_body": (
            "`assessments.csv` could support counts of due work by "
            "assessment type. Joining `vle.csv` with `studentVle.csv` "
            "might distinguish early interactions by resource type and "
            "planned week. These would be **new features**, not recovered "
            "course content. They would require date-safe construction "
            "and another evaluation over time and across groups."
        ),
        "limits_title": "Main limitations",
        "limits": [
            "OULAD is a selected historical distance-learning dataset from one university; transfer to current training providers has not been validated.",
            "Clicks do not measure understanding or study outside the platform; apparent missing work can also reflect technical or administrative issues.",
            "Withdrawal and failure are different events but are prioritised together here. A person decides what support is suitable.",
            "Only learners still enrolled at the chosen day and weeks up to day 111 are covered. Earlier withdrawals and later course stages are outside this prototype.",
            "The demo and models contain no names or contact details. The app sends nothing, records no conversations and does not enforce user roles.",
            "The effects of outreach, group differences and operational costs have not been independently established for another provider.",
        ],
        "sources_title": "Sources and further documentation",
        "source_label": "Official dataset page",
        "paper_label": "Original paper with module table and anonymisation details",
        "readme_note": "The project README and analysis notebooks describe the exact computations and current results.",
    },
}


def module_overview(language: str) -> pd.DataFrame:
    """Erstellt die veröffentlichte Modultabelle in der Oberflächensprache."""
    copy = CONTEXT[language]
    return pd.DataFrame(
        [
            (module, copy[field], runs, days)
            for module, field, runs, days in MODULES
        ],
        columns=copy["courses_columns"],
    )


def file_overview(language: str) -> pd.DataFrame:
    """Beschreibt die Originaltabellen, ohne Daten aus der Demo zu erfinden."""
    copy = CONTEXT[language]
    return pd.DataFrame(
        [(filename, copy["files"][key]) for filename, key in RAW_FILES],
        columns=copy["files_columns"],
    )


def course_profile(language: str, module: str, presentation: str) -> str | None:
    """Nennt nur belegte Fachbereiche und die Dauer des bekannten 2014J-Laufs."""
    copy = CONTEXT[language]
    for code, field, _, days in MODULES:
        if module == code:
            key = "course_profile" if presentation == "2014J" else "course_profile_other"
            return copy[key].format(
                module=module, presentation=presentation, field=copy[field], days=days
            )
    return None
