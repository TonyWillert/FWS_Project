# LearnerCue: Frühwarnhinweise für Lernende mit OULAD

LearnerCue (zuvor LernRadar) ist ein lokaler Streamlit-Prototyp für die wöchentliche Sichtung von Kursen. Er ordnet Kurseinträge innerhalb jedes Kursdurchlaufs nach einem Modellwert und bietet eine kürzere Prüfliste mit den obersten rund 10 % sowie eine erweiterte Prüfliste mit den obersten rund 20 % an. Die tatsächliche Zahl der Einträge steht direkt in der Auswahl. Ein Hinweis ist ein Anlass für eine fachliche Sichtung und gegebenenfalls ein Unterstützungsangebot, keine automatische Entscheidung über Lernende.

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

Die App benötigt `app.py`, `weekly_logic.py`, `operations.py`, `ui_text.py`, `reporting.py`, `models/oulad_wochen/schema.json` und die 16 Dateien `tag_006.joblib` bis `tag_111.joblib`. Nach dem Start erscheint zunächst nur der Upload. Für die Vorführung kann lokal `data/demo/oulad_wochen_2014j.csv` heruntergeladen und anschließend hochgeladen werden. Diese Datei wird durch `11_wochenmodelle_export.ipynb` erzeugt und liegt wegen des ignorierten Ordners `data/` nicht im Git-Repository. Ohne die lokale Datei lässt sich eine entsprechend vorbereitete eigene CSV hochladen; OULAD-Rohdateien sind **kein** direktes Upload-Format.

Die CSV braucht genau diese **Pflichtspalten** (weitere Spalten werden ignoriert):

```text
code_module,code_presentation,id_student,stichtag,anmeldetag,assessments_faellig,abgaben,banked_faellige,assessments_fehlend,klicks_bis_stichtag,klicks_letzte_7_tage
```

Die App prüft die Eingaben und lädt für jeden enthaltenen Stichtag sein Modell. Danach gibt es vier Ansichten: **🗓️ Diese Woche** zeigt Kurse und die Zahl der Hinweise; **👥 Kurs prüfen** enthält die nach Modellwert geordnete Liste und beobachtete Angaben zu einer ausgewählten Person; **📊 Leitung & Kapazität** fasst Kurse zusammen und zeigt einen anpassbaren möglichen Zeitbedarf; **📚 Über das Projekt** erläutert Daten, anonymisierte Module, Modellweg, historischen Vergleich, möglichen Nutzen und Grenzen. Die ausführlichen Erklärungen sind auch **vor dem Upload** über **Hilfe & Hintergrund → Über die Demo** zugänglich. Der Hilfedialog enthält daneben Ablauf und Glossar. Im Kursbereich wird ein belegter Fachbereich und für 2014J die Kursdauer genannt, kein erfundener Kurstitel. Bei wichtigen Spalten und Einstellungen erscheint zusätzlich eine Erklärung als Tooltip. Die Hinweise je hochgeladener Woche sind optional als Tabelle verfügbar. Der jüngste enthaltene Kurstag ist voreingestellt. Modellwerte dienen nur zur Reihenfolge und sind keine geprüften individuellen Ausfallwahrscheinlichkeiten.

Deutsch und Englisch lassen sich oben auf der Seite wechseln. Das helle und dunkle Farbschema ist in `.streamlit/config.toml` definiert; der Wechsel erfolgt über das Streamlit-Menü oben rechts unter **Settings → Theme**. Die Gestaltung nutzt die nativen Bedienelemente, sodass Beschriftungen und Hinweise in beiden Modi lesbar bleiben. Bekannte CSV-Fehler erscheinen auch auf Englisch; für unerwartete Meldungen gibt es eine englische Zusammenfassung und bei Bedarf technische Details.

Unter **Kurs prüfen** erstellt **Kursbericht herunterladen** einen lokalen, druckbaren HTML-Bericht für genau den gewählten Kurs, Kurstag, Listenumfang und Statusfilter. Er enthält die Zusammenfassung und die aktuell sichtbaren anonymisierten IDs samt beobachteten Leistungs- und Klickzahlen, aber keine Ergebnisvariable und keine gesicherte persönliche Risikowahrscheinlichkeit. Der Bericht sollte wegen der Kennungen geschützt aufbewahrt werden. Für die ausgewählte Person zeigt ein optionaler Bereich einen neutralen Nachrichtentext, den ein Coach selbst prüfen und kopieren kann. Es werden keine Nachrichten versendet. **Fehler melden** öffnet ein Formular für einen lokal gespeicherten Textbericht; es versendet weder Daten noch einen Bericht automatisch. Der optionale GitHub-Link ist nur für Berichte ohne personenbezogene Daten geeignet.

„Neu auf Liste“ und „Schon früher auf Liste“ beziehen sich ausschließlich auf die Wochen, die in **dieser CSV** stehen. Die Leitungsansicht berechnet diese Angaben passend zur dort gewählten 10- oder 20-%-Liste. Die Kapazitätsrechnung verwendet frei wählbare Minuten und Kontaktanteile je Kurs: Sie zeigt eine Planung, keine tatsächlich gesendeten Nachrichten oder geführten Gespräche. Die CSV enthält keine späteren Kursergebnisse. Die Ansichten sind im Prototyp nicht durch Benutzerrollen getrennt. Die App kennt keine Kontakte und speichert keine Bearbeitungsstände. Die 10-/20-%-Auswahl begrenzt die Anzahl der sichtbaren Kurseinträge; an Tag 27 umfasste die historische 20-%-Auswahl nur 34,1 % der späteren Fälle. Klicks und offene Leistungen sind beobachtete Daten, keine nachgewiesenen Gründe für einen individuellen Hinweis. Ein kurzer Test der Bedienbarkeit ist in `docs/ux_kurztest.md` vorbereitet; `docs/ux_checkliste.md` enthält nacheinander abharkbare Prüfungen.

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
| `project_context.py` | Zweisprachiger Daten- und Modulhintergrund samt Quellen und Grenzen für die Oberfläche |
| `weekly_logic.py` | CSV-Prüfung, Modellbewertung und Hinweisauswahl |
| `operations.py` | Aggregation und Kapazitätsrechnung für die Leitungsansicht |
| `.streamlit/config.toml` | Hell- und Dunkelmodus der lokalen Oberfläche |
| `docs/ux_kurztest.md` | Aufgaben und Beobachtungsbogen für einen ersten Verständlichkeitstest |
| `docs/ux_checkliste.md` | Checkliste für Funktion, Verständlichkeit und Lesbarkeit |
| `docs/operations_guide.md` | Kontaktstrategie, historische Fallzahlen und Planungsannahmen |
| `assets/learnercue.svg` | Vektorlogo und Browser-Icon |
| `models/oulad_wochen/` | Gespeichertes Schema und 16 Modell-Pipelines |

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

Als Nächstes folgt ein Verständlichkeitstest der überarbeiteten Oberfläche mit einer fachfremden Person. Anschließend werden Sprache und Anordnung nach den Beobachtungen angepasst und die Präsentation vorbereitet. Ein Test mit einer Person aus der Erwachsenenbildung wäre zusätzlich nötig, um die Passung zum Arbeitsalltag zu beurteilen. Bei Änderungen an Features, Zielvariable, Modellen oder Demo-Daten müssen `project_context.py`, diese README und die historischen Kennzahlen in der App gemeinsam geprüft und aktualisiert werden.

## Quelle

Kuzilek, J., Hlosta, M. & Zdrahal, Z. (2017): [Open University Learning Analytics dataset](https://doi.org/10.1038/sdata.2017.171). *Scientific Data*, 4, 170171. Der Datensatz wird unter [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) bereitgestellt.
