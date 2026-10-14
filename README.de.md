# LearnerCue: Frühwarnhinweise für Lernende mit OULAD

LearnerCue (zuvor LernRadar) ist ein Streamlit-Prototyp für die wöchentliche Sichtung von Kursen. Er ordnet **alle noch angemeldeten Kurseinträge** innerhalb jedes Kursdurchlaufs nach einem Modellwert. Farbige, auch textlich benannte Rangbereiche helfen bei der Sichtung (oberste rund 10 %, nächste rund 10 %, übrige Personen); sie sind keine geprüften persönlichen Risikogrenzen. Ein Eintrag ist ein Anlass für eine fachliche Sichtung und gegebenenfalls ein Unterstützungsangebot, keine automatische Entscheidung über Lernende.

**[Live-Demo ausprobieren](https://fwsproject-cjpggxprduvuak9kugbusk.streamlit.app/)** · Öffne dort „Synthetische Demo starten“. Die öffentliche Testdatei zeigt die Bedienung und enthält keine echten Lernenden; die historischen Modellkennzahlen stehen in dieser README.

## Fragestellung

Welche zu einem Kurstag noch angemeldeten Lernenden sollten bei begrenzter Betreuungskapazität zuerst geprüft werden, wenn das gemeinsame Ziel ein **späterer Kursabbruch oder das spätere Kursergebnis `Fail`** ist?

Der Prototyp betrachtet 16 wöchentliche Stichtage: Tag 6, 13, …, 111. Die Modelle unterscheiden für eine einzelne Person **nicht**, ob eher ein Abbruch oder ein Nichtbestehen bevorsteht. Ein Kurseintrag ist die Anmeldung einer Person zu einem bestimmten Kursdurchlauf; dieselbe Person kann mehrere Kurseinträge haben.

## Datengrundlage

Das anonymisierte [Open University Learning Analytics Dataset (OULAD)](https://research.stem.open.ac.uk/ouanalyse/dataset/) umfasst sieben Module mit 22 Durchläufen aus 2013 und 2014. Verwendet werden insbesondere `studentInfo.csv`, `studentRegistration.csv`, `assessments.csv`, `studentAssessment.csv` und `studentVle.csv`. VLE steht für *Virtual Learning Environment*, die virtuelle Lernumgebung. Die historischen Kursdurchläufe dauern 234 bis 269 Tage; Tag 27 liegt entsprechend noch am Anfang eines Kurses.

Die [Originalveröffentlichung](https://pmc.ncbi.nlm.nih.gov/articles/PMC5704676/) ordnet AAA, BBB und GGG den **Sozialwissenschaften** sowie CCC, DDD, EEE und FFF dem Bereich **STEM** zu. Die Modulnamen wurden zur Anonymisierung durch Codes ersetzt; konkrete Kurstitel, Lehrpläne oder Lerninhalte lassen sich aus OULAD nicht zuverlässig ablesen. `vle.csv` enthält Materialtypen und geplante Wochen, nicht die Texte der Lernmaterialien. Die sieben Originaltabellen, die Fachbereiche je Modul und die Dauer der 2014J-Durchläufe sind in der App unter **📚 Über das Projekt** erklärt. Die Module wurden unter Auswahlkriterien wie verfügbaren VLE-Daten, mehreren Durchläufen, größeren Gruppen und einem nennenswerten Anteil nicht bestandener Fälle ausgewählt. Daher ist OULAD keine Zufallsstichprobe aller Weiterbildungen.

Für jeden Stichtag enthält die aufbereitete Wochenbasis nur Kurseinträge, die zu diesem Zeitpunkt noch angemeldet sind. Als späterer Fall zählt ein bestätigter Abbruch nach dem Stichtag oder das Kursergebnis `Fail`. Fälle ohne lesbaren Abmeldetag lassen sich für diese zeitliche Abgrenzung nicht zuverlässig zuordnen. Die Wochenbasis unter `data/processed/oulad_wochenmodellbasis_tag6_bis111.csv` umfasst 423.510 Datenstände mit 13 Spalten. Mehrere Datenstände können zum selben Kurseintrag gehören.

Die exportierten Modelle nutzen folgende Eingaben bis zum jeweiligen Stichtag:

| Eingabe | Bedeutung |
| --- | --- |
| `code_module`, `code_presentation` | Modul und Kursdurchlauf |
| `anmeldetag` | Tag der Anmeldung relativ zum Kursbeginn |
| `assessments_faellig` | Zahl bis dahin fälliger Assessments |
| `abgaben` | Zahl erfasster eigener Abgaben |
| `banked_faellige` | Zahl fälliger, angerechneter Leistungen |
| `assessments_fehlend` | Zahl fälliger Leistungen ohne erfasste Erfüllung |
| `klicks_bis_stichtag` | Erfasste VLE-Klicks seit Kursbeginn |
| `klicks_letzte_7_tage` | Erfasste VLE-Klicks in der letzten Kurswoche |

`id_student` dient nur zur Zuordnung und Trennung von Personen, `stichtag` zur Auswahl des Wochenmodells. Beide sind keine Modellmerkmale. Assessment-Punktzahlen werden nicht verwendet, weil für die Bekanntgabe der Bewertung kein verlässlicher Zeitpunkt vorliegt.

## Vorgehen und Bewertung

1. Rohdateien, Schlüssel, fehlende Werte und Abmeldezeitpunkte geprüft.
2. Zunächst einen Hinweis für spätere Abmeldungen ab Tag 14 untersucht.
3. Auf Tag 28 und das gemeinsame Ziel „Abbruch oder Fail“ erweitert; einfache Regeln, logistische Regression, Random Forest und Histogram Gradient Boosting verglichen.
4. Die Tag-28-Auswertung zeitlich mit 2014J geprüft. Anschließend Wochenstände bis Tag 111, getrennte Modelle je Woche und eine wiederholte kursweise Hinweisauswahl untersucht.
5. Den Bildungsabschluss zusätzlich geprüft und wegen der starken Verschiebung von Hinweisen zwischen Bildungsgruppen **nicht** in die exportierten Modelle übernommen.
6. Altersgruppe, frühere Modulversuche, belegte Credits und eine deklarierte Einschränkung deskriptiv gesichtet; frühere Versuche zusätzlich auf mehreren Stichtagen im Modell verglichen.
7. Die Modelle und eine CSV ohne spätere Ergebnisse für die Vorführung exportiert; eine lokale Streamlit-Oberfläche erstellt.

Die früheren Vergleiche innerhalb der Entwicklungsdaten trennten Trainings- und Validierungsgruppen nach `id_student`. Die exportierten 16 Pipelines verwenden `HistGradientBoostingClassifier` und jeweils nur Trainingsdaten desselben Stichtags aus Präsentationen vor 2014J. Für die Demo und zeitliche Auswertung wurden aus 2014J die 1.403 Personen ausgeschlossen, die auch in früheren Präsentationen vorkommen. Das Training umfasst 282.519 wöchentliche Datenstände; die Demo 121.447 Datenstände von 8.682 unterschiedlichen Kurseinträgen. Die Demo enthält weder `final_result` noch die Zielvariable.

**Average Precision (AP)** bewertet die Reihenfolge aller Kurseinträge anhand des späteren Ergebnisses. **Trefferquote** bezeichnet den Anteil späterer Fälle unter den Hinweisen; **Recall** den Anteil aller späteren Fälle, die einen Hinweis erhalten. Die tatsächliche Fallquote gehört als Vergleichswert immer dazu. Bei der kursweisen Auswahl werden die obersten 10 beziehungsweise 20 % **pro Kursdurchlauf und Stichtag** markiert, bei kleinen Kursen aufgerundet.

### Explorative zeitliche Ergebnisse

Auf 2014J erreicht das Wochenmodell an Tag 27 bei 7.828 noch angemeldeten Kurseinträgen eine AP von **0,625** gegenüber **0,429** für eine Referenz aus Kurs- und Anmeldedaten; der spätere Fallanteil beträgt **37,6 %**. Bei 20 % Hinweisen je Kurs sind es 1.567 Hinweise mit 1.006 Treffern: **64,2 % Trefferquote** und **34,1 % Recall** an diesem Stichtag.

Bei einer Simulation von 16 wöchentlichen Sichtungen in 2014J erhalten mit der 20-%-Auswahl insgesamt **4.768 von 8.682 Kurseinträgen** mindestens einmal einen Hinweis (54,9 %). Von 3.800 späteren Abbrüchen oder Nichtbestehen werden **2.761** mindestens einmal erkannt (72,7 % kumulativer Recall). Die Trefferquote der erstmaligen Hinweise beträgt 57,9 %. Die wiederholten Wochenhinweise dürfen dabei nicht als unterschiedliche Personen gezählt werden. Ein Wochenbudget von 20 % bedeutet über 16 Wochen also keine Gesamtquote von 20 %.

Diese Zahlen stammen aus einer **explorativen** zeitlichen Prüfung: 2014J wurde während der Projektentwicklung mehrfach eingesehen und beeinflusste Entscheidungen. Die Werte sind daher kein Ergebnis eines unberührten Abschlusstests und kein Nachweis der Wirkung einer Intervention. Die verglichenen Stichtage enthalten unterschiedliche noch angemeldete Gruppen; ein höherer Wert in einer späteren Woche beweist nicht, dass diese Woche der beste Zeitpunkt für Unterstützung ist.

In `12_zusatzmerkmale.ipynb` verbesserten frühere Modulversuche die AP innerhalb der Entwicklungsdaten an Tag 27 im Mittel von 0,717 auf 0,720 und den Recall bei 20 % Hinweisen von 33,3 % auf 33,7 %. Der Gewinn ist klein; die exportierten Modelle und die App verwenden dieses Zusatzmerkmal derzeit nicht. Zusammenhänge mit Alter oder einer deklarierten Einschränkung sind keine individuellen Ursachen und wurden nicht in die Modelle übernommen.

### Frühere Tag-28-Analyse

Die erste Tag-28-Modellbasis umfasst 27.422 Kurseinträge, darunter 12.044 spätere Abbrüche oder `Fail` (43,9 %). Im damaligen zurückgelegten Prüfteil erreichte Histogram Gradient Boosting eine AP von 0,709 gegenüber 0,514 für die Referenz aus Kurs- und Anmeldedaten. Diese Auswertung verwendete einen anderen Stichtag und eine andere Aufteilung als die wöchentlichen Analysen; die Werte sollten nicht direkt miteinander verglichen werden. Der Tag-28-Prototyp wurde durch die Wochenversion abgelöst.

## Lokale Anwendung

Nach dem Klonen im Projektordner die Abhängigkeiten mit der versionierten `uv.lock` abgleichen und mit [uv](https://docs.astral.sh/uv/) starten:

```powershell
uv sync --locked
uv run streamlit run app.py
```

Die App benötigt neben dem Code `models/oulad_wochen/schema.json` und die 16 gespeicherten Modelle `tag_006.joblib` bis `tag_111.joblib`. Diese Modelldateien und `uv.lock` wurden für das Repository versioniert; prüfe nach einem frischen Klon, ob sie tatsächlich vorhanden sind. Nach dem Start stehen die synthetische Demo und der Upload zur Wahl.

Für einen **frischen Klon** lässt sich die mitgelieferte `examples/learnercue_ui_sample.csv` mit „Synthetische Demo starten“ direkt öffnen oder herunterladen und hochladen. Sie enthält 120 **synthetische** Wochenstände zu BBB und CCC an Tag 6, 13 und 20. Kennungen, Beobachtungen und die mit den echten Modellen berechnete Rangfolge dienen ausschließlich dazu, die Bedienung zu prüfen. Aus dieser Datei darf keine Trefferquote, Modellgüte oder Aussage über reale Lernende abgeleitet werden.

Für die **fachliche Projektvorführung** die lokale `data/demo/oulad_wochen_2014j.csv` verwenden. Sie wird durch `11_wochenmodelle_export.ipynb` aus der vorbereiteten Wochenbasis erzeugt und liegt wegen des ignorierten Ordners `data/` nicht im Git-Repository. Wenn sie im Projektordner vorhanden ist, erscheint ihr Download statt der kleinen Testdatei. Ohne sie lässt sich eine entsprechend vorbereitete eigene CSV hochladen; OULAD-Rohdateien sind **kein** direktes Upload-Format.

Die CSV braucht genau diese **Pflichtspalten** (weitere Spalten werden ignoriert):

```text
code_module,code_presentation,id_student,stichtag,anmeldetag,assessments_faellig,abgaben,banked_faellige,assessments_fehlend,klicks_bis_stichtag,klicks_letzte_7_tage
```

Die App prüft die Eingaben und lädt für jeden enthaltenen Stichtag sein Modell. Danach wählt man einen von zwei deutlich getrennten Einstiegen: **Coach** mit „Diese Woche“ und „Kurs prüfen“, oder **Leitung und Lead Coach** mit einem vorläufigen Planungsszenario. Aus der Wochenübersicht lässt sich ein Kurs **durch Klick auf seine Tabellenzeile** oder über die Kurswahl direkt öffnen. „Kurs prüfen“ zeigt standardmäßig **alle Personen des Kurses in Modellreihenfolge**; ein Zeilenklick oder die Personenauswahl darunter öffnet Beobachtungen und den ausdrücklich simulierten Bearbeitungsstand. Optional zeigt „Jetzt prüfen“ vorrangige Einträge mit Beispielstatus „noch nicht gesichtet“ sowie an diesem Kurstag fällige Beispiel-Wiedervorlagen. Wartende Antworten, Gespräche und spätere Wiedervorlagen werden nicht als fällig markiert. Eine Person weiter unten kann bei fälliger Wiedervorlage ebenfalls in dieser Ansicht stehen; der Rang in der Gesamtliste bleibt sichtbar. Die Arbeitsansicht wertet keine echten Kontakte aus und trifft keine automatische Kontaktentscheidung.

Ein dritter Einstieg **Über das Projekt** erläutert Daten, anonymisierte Module, Modellweg, historischen Vergleich, möglichen Nutzen und Grenzen. Die ausführlichen Erklärungen sind auch **vor dem Upload** über **Hilfe & Hintergrund → Über die Demo** zugänglich. Der Hilfedialog enthält daneben Ablauf und Glossar. Im Kursbereich wird ein belegter Fachbereich und für 2014J die Kursdauer genannt, kein erfundener Kurstitel. Bei wichtigen Spalten und Einstellungen erscheint zusätzlich eine Erklärung als Tooltip. Der jüngste enthaltene Kurstag ist voreingestellt. Modellwerte dienen nur zur Reihenfolge und sind keine geprüften individuellen Ausfallwahrscheinlichkeiten.

Deutsch und Englisch lassen sich oben auf der Seite wechseln. Das helle und dunkle Farbschema ist in `.streamlit/config.toml` definiert; der Wechsel erfolgt über das Streamlit-Menü oben rechts unter **Settings → Theme**. Die Gestaltung nutzt die nativen Bedienelemente, sodass Beschriftungen und Hinweise in beiden Modi lesbar bleiben. Bekannte CSV-Fehler erscheinen auch auf Englisch; für unerwartete Meldungen gibt es eine englische Zusammenfassung und bei Bedarf technische Details.

Unter **Kurs prüfen** erstellt **Kursbericht herunterladen** einen lokalen, druckbaren HTML-Bericht mit der vollständigen Kursreihenfolge für den gewählten Tag, **auch wenn „Jetzt prüfen“ aktiv ist**. Er enthält anonymisierte IDs, beobachtete Leistungs- und Klickzahlen sowie gegebenenfalls den im aktuellen Browser simulierten Bearbeitungsstand, aber keine Ergebnisvariable und keine gesicherte persönliche Risikowahrscheinlichkeit. Der Bericht sollte wegen der Kennungen geschützt aufbewahrt werden. Für die ausgewählte Person zeigt ein optionaler Bereich einen neutralen Nachrichtentext, den ein Coach selbst prüfen und kopieren kann. Es werden keine Nachrichten versendet. **Fehler melden** öffnet ein Formular für einen lokal gespeicherten Textbericht; es versendet weder Daten noch einen Bericht automatisch. Der optionale GitHub-Link ist nur für Berichte ohne personenbezogene Daten geeignet.

„Neu“ und „schon früher“ beziehen sich ausschließlich auf vorrangige Rangbereiche in den Wochen **dieser CSV**, nicht auf Kontakte. Daneben kann man für eine Person einen **Beispielstatus** wie „Nachricht vorbereitet“, „Antwort ausstehend“ oder „Wiedervorlage an Tag …“ setzen. Dieser Status gilt nur während der Browser-Sitzung und ist keine Dokumentation tatsächlich geführter Gespräche. Die Leitungsansicht berechnet Listenhistorie nur für die gewählten vorrangigen Rangbereiche. Für die Kapazitätsrechnung lassen sich die erste Gruppe, beide vorrangigen Gruppen oder **alle Kurseinträge** auswählen; Minuten und Kontaktanteile sind Annahmen. **Diese Leitungskennzahlen sind ein vorläufiges Konzept; ein belastbares Managementprodukt wäre ein separates Projekt.** Die CSV enthält keine späteren Kursergebnisse. Die getrennten Einstiege sind keine Benutzerrollen mit Zugriffsrechten. An Tag 27 umfasste die historische 20-%-Auswahl nur 34,1 % der späteren Fälle; die Coach-Liste blendet die übrigen Kurseinträge nicht mehr aus. Klicks und offene Leistungen sind beobachtete Daten, keine nachgewiesenen Gründe für einen individuellen Hinweis. Ein kurzer Test der Bedienbarkeit ist in `docs/ux_kurztest.md` vorbereitet; `docs/ux_checkliste.md` enthält nacheinander abharkbare Prüfungen.

Die Coach-Ansicht beantwortet unter „Ab wann gilt eine Person als gefährdet?“ zwei verschiedene Fragen: Ein Modellhinweis ist für noch angemeldete Kurseinträge ab Tag 6 wöchentlich möglich; eine **validierte individuelle Risikoschwelle** oder ein nachgewiesener Beginn persönlicher Gefährdung existiert nicht. Die obersten rund 10 und nächsten rund 10 % sind Sichtungsgruppen je Kurs. Bei ausgewählten Personen zeigt die Detailansicht den aktuellen Rang und gegebenenfalls den ersten Tag auf der vorrangigen Liste **innerhalb der hochgeladenen Wochen**. Auch Personen außerhalb dieser Gruppen können später abbrechen oder nicht bestehen.

## Öffentliche Portfoliodemo

GitHub Pages kann die Portfolioseite mit einem Link zur App zeigen, aber keinen Python-Prozess für Streamlit ausführen. LinkedIn kann denselben externen Link im Profil hervorheben; es hostet die App nicht. Eine passende Hosting-Option ist **Streamlit Community Cloud**:

1. Unter [share.streamlit.io](https://share.streamlit.io/) mit GitHub verbinden und eine neue App aus dem öffentlichen Repository `TonyWillert/FWS_Project`, Branch `main`, Einstieg `app.py` anlegen.
2. In den erweiterten Einstellungen **Python 3.14** wählen: `pyproject.toml` verlangt mindestens 3.14 und `.python-version` enthält 3.14. Community Cloud erkennt die vorhandene `uv.lock` für die Abhängigkeiten. Die 16 gespeicherten Modelle und das Schema müssen im Repository bleiben.
3. Nach dem Start die synthetische Demo mit einem Klick öffnen und den Weg **Coach → Diese Woche → Kurs prüfen → Person → Kursbericht** im öffentlichen Browser prüfen. Die lokale Datei unter `data/demo/` wird nicht mit Git übertragen und ist online nicht verfügbar.
4. Die Live-Demo läuft unter [LearnerCue auf Streamlit Community Cloud](https://fwsproject-cjpggxprduvuak9kugbusk.streamlit.app/). In der öffentlichen App keine echten personenbezogenen Kursdaten hochladen.

Die öffentliche Testdatei demonstriert die Bedienung; die historischen Kennzahlen in dieser README stammen aus der getrennten OULAD-Auswertung. Der lokale OULAD-Durchlauf bleibt für eine fachliche Projektvorführung nötig.

## Nutzen und möglicher Einsatzkontext

Der bisher nachgewiesene Nutzen ist eine bessere **Reihenfolge für die fachliche Sichtung** der historischen OULAD-Kurse bei einer festgelegten Betreuungskapazität. Der Prototyp beweist nicht, dass ein Unterstützungsangebot spätere Abbrüche oder ein Nichtbestehen verhindert. Für eine Weiterbildungseinrichtung müssten zuerst Ergebnisdefinition, Interventionszeitpunkt und verfügbares Betreuungsteam festgelegt, eigene Kursdaten aufbereitet und ein Modell auf späteren eigenen Durchläufen unabhängig geprüft werden. Ein laufender Betrieb bräuchte zudem verlässliche Datenimporte, begrenzte Zugriffsrechte und einen von Menschen gepflegten Bearbeitungsstand. Die gespeicherten OULAD-Modelle sind nicht für eine unmittelbare Bewertung realer Lernender einer anderen Einrichtung validiert.

## Projektdateien und Reproduktion

| Datei | Inhalt |
| --- | --- |
| `01_datensichtung.ipynb` | Rohdaten und erste Modellbasen |
| `02_modellvergleich.ipynb` bis `04_abschlussbewertung.ipynb` | Frühe Untersuchung des Abbruchs ab Tag 14 |
| `05_tag28_modellvergleich.ipynb` | Tag-28-Modellvergleich und Bewertung |
| `06_zeitliche_pruefung.ipynb` | Zeitliche Prüfung der Tag-28-Variante |
| `07_getrennte_risiken.ipynb` | Explorative Unterscheidung von Abbruch und Nichtbestehen |
| `08_zeitfenster.ipynb`, `09_wochenvergleich.ipynb` | Wochenstände, Stichtage und wiederholte Hinweise |
| `10_bildungshintergrund.ipynb` | Zusatzmerkmal Bildungsabschluss und Gruppenvergleich |
| `11_wochenmodelle_export.ipynb` | Training und Export der Wochenmodelle, Schema und Demo-CSV |
| `12_zusatzmerkmale.ipynb` | Deskriptive Sichtung und Vergleich zusätzlicher Merkmale |
| `app.py`, `ui_text.py`, `reporting.py` | Oberfläche, deutsche und englische Bedientexte, lokaler Kursbericht |
| `coach_workflow.py` | Kleine Regel für die optionale simulierte Arbeitsansicht |
| `project_context.py` | Zweisprachiger Daten- und Modulhintergrund samt Quellen und Grenzen für die Oberfläche |
| `weekly_logic.py` | CSV-Prüfung, Modellbewertung und Hinweisauswahl |
| `operations.py` | Aggregation und Kapazitätsrechnung für die Leitungsansicht |
| `.streamlit/config.toml` | Hell- und Dunkelmodus der lokalen Oberfläche |
| `docs/ux_kurztest.md` | Aufgaben und Beobachtungsbogen für einen ersten Verständlichkeitstest |
| `docs/ux_checkliste.md` | Checkliste für Funktion, Verständlichkeit und Lesbarkeit |
| `docs/operations_guide.md` | Kontaktstrategie, historische Fallzahlen und Planungsannahmen |
| `assets/learnercue.svg` | Vektorlogo und Browser-Icon |
| `models/oulad_wochen/` | Gespeichertes Schema und 16 Modell-Pipelines |
| `examples/learnercue_ui_sample.csv` | Kleine synthetische CSV für einen Bedienungstest nach frischem Klon |

Die OULAD-Rohdaten und die aufbereiteten Dateien unter `data/` liegen lokal und werden nicht mit Git versioniert. Zum erneuten Erzeugen müssen die Rohdateien in der erwarteten Projektstruktur vorliegen und gegebenenfalls absolute Pfade in den frühen Notebooks an den eigenen Rechner angepasst werden. Das Exportnotebook setzt die vorbereitete Wochenbasis voraus; es erstellt sie nicht aus den Roh-CSV-Dateien. Die Ausführung der Notebooks ist daher in der beschriebenen Abhängigkeitsreihenfolge nötig. Gespeicherte `joblib`-Modelle nur aus vertrauenswürdigen Quellen laden.

## Grenzen und nächste Schritte

- OULAD beschreibt ausgewählte historische Fernstudienkurse; eine Übertragung auf heutige Weiterbildungen, andere Einrichtungen oder alle Lernenden ist nicht belegt.
- Die ursprünglichen Modultitel und konkreten Lehrinhalte sind nicht verfügbar; Fachbereiche und Metadaten geben keine Auskunft über individuelle Lernschwierigkeiten in einem Fach.
- Nur zum jeweiligen Stichtag noch angemeldete Personen können einen Hinweis bekommen. Bereits erfolgte Abbrüche können damit nicht verhindert werden.
- Das gemeinsame Ziel verschmilzt Abbruch und Nichtbestehen. Der explorative Drei-Klassen-Versuch lieferte keine ausreichend verlässliche individuelle Risikorichtung für eine getrennte Anzeige.
- VLE-Klicks sind weder Lernzeit noch Verständnis; Lernen außerhalb der Plattform bleibt unsichtbar. Auch ein fehlendes Assessment kann im Einzelfall Daten- oder Prozessgründe haben.
- Der Bildungsabschluss verbesserte die mittlere Modellgüte an ausgewählten Stichtagen, verschob aber die Hinweise stark zwischen Bildungsgruppen. Auch ohne dieses Merkmal können andere Eingaben Ungleichheiten abbilden; die Gruppenprüfung ist nicht abgeschlossen.
- Die Prüfgruppe 2014J ist durch wiederholte Einsicht während der Entwicklung explorativ. Eine unabhängige zeitliche und externe Prüfung sowie die Bewertung von Fehlhinweisen und möglicher Benachteiligung fehlen.
- Eine hohe Trefferquote belegt weder kausale Gründe noch, dass eine Ansprache den Kursverlauf verbessert. Vor einem realen Einsatz braucht es fachlich abgestimmte Maßnahmen, Datenschutzprüfung und eine Bewertung im jeweiligen Bildungskontext.

Der erste Verständlichkeitstest zeigte: Schrift und Aufbau waren teils zu klein bzw. unübersichtlich, die Testperson wollte einen Kurs intuitiv aus der Tabelle öffnen und verstand „Fällige Leistungen ohne Erfüllung“ nicht. Nach dieser Überarbeitung folgt ein erneuter Test von Einstieg, vollständiger Liste, Begriffen, Beispielstatus und Leitungsansicht. Ein Test mit Coaches aus der Erwachsenenbildung wäre zusätzlich nötig, um die Passung zum Arbeitsalltag zu beurteilen. Ein gestufter Kontakt mit früher optionaler Nachricht und späterer persönlicher Sichtung ist eine **ungeprüfte Hypothese**; OULAD enthält keine geeigneten Daten, um deren Wirkung oder Zeitersparnis zu belegen. Bei Änderungen an Features, Zielvariable, Modellen oder Demo-Daten müssen `project_context.py`, diese README und die historischen Kennzahlen in der App gemeinsam geprüft und aktualisiert werden.

## Quelle

Kuzilek, J., Hlosta, M. & Zdrahal, Z. (2017): [Open University Learning Analytics dataset](https://doi.org/10.1038/sdata.2017.171). *Scientific Data*, 4, 170171. Der Datensatz wird unter [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) bereitgestellt.
