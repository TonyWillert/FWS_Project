# LernRadar: Frühwarnhinweise für Lernende mit OULAD

LernRadar ist ein lokaler Streamlit-Prototyp für die wöchentliche Sichtung von Kursen. Er ordnet Kurseinträge innerhalb jedes Kursdurchlaufs nach einem Modellwert und zeigt die obersten 10 % als **hohe Priorität** sowie die nächsten 10 % zur **weiteren Prüfung**. Ein Hinweis ist ein Anlass für eine fachliche Sichtung und gegebenenfalls ein Unterstützungsangebot, keine automatische Entscheidung über Lernende.

## Fragestellung

Welche zu einem Kurstag noch angemeldeten Lernenden sollten bei begrenzter Betreuungskapazität zuerst geprüft werden, wenn das gemeinsame Ziel ein **späterer Kursabbruch oder das spätere Kursergebnis `Fail`** ist?

Der Prototyp betrachtet 16 wöchentliche Stichtage: Tag 6, 13, …, 111. Die Modelle unterscheiden für eine einzelne Person **nicht**, ob eher ein Abbruch oder ein Nichtbestehen bevorsteht. Ein Kurseintrag ist die Anmeldung einer Person zu einem bestimmten Kursdurchlauf; dieselbe Person kann mehrere Kurseinträge haben.

## Datengrundlage

Das anonymisierte [Open University Learning Analytics Dataset (OULAD)](https://research.stem.open.ac.uk/ouanalyse/dataset/) umfasst sieben Module mit 22 Durchläufen aus 2013 und 2014. Verwendet werden insbesondere `studentInfo.csv`, `studentRegistration.csv`, `assessments.csv`, `studentAssessment.csv` und `studentVle.csv`. VLE steht für *Virtual Learning Environment*, die virtuelle Lernumgebung. Die historischen Kursdurchläufe dauern 234 bis 269 Tage; Tag 27 liegt entsprechend noch am Anfang eines Kurses.

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
6. Die Modelle und eine CSV ohne spätere Ergebnisse für die Vorführung exportiert; eine lokale Streamlit-Oberfläche erstellt.

Die früheren Vergleiche innerhalb der Entwicklungsdaten trennten Trainings- und Validierungsgruppen nach `id_student`. Die exportierten 16 Pipelines verwenden `HistGradientBoostingClassifier` und jeweils nur Trainingsdaten desselben Stichtags aus Präsentationen vor 2014J. Für die Demo und zeitliche Auswertung wurden aus 2014J die 1.403 Personen ausgeschlossen, die auch in früheren Präsentationen vorkommen. Das Training umfasst 282.519 wöchentliche Datenstände; die Demo 121.447 Datenstände von 8.682 unterschiedlichen Kurseinträgen. Die Demo enthält weder `final_result` noch die Zielvariable.

**Average Precision (AP)** bewertet die Reihenfolge aller Kurseinträge anhand des späteren Ergebnisses. **Trefferquote** bezeichnet den Anteil späterer Fälle unter den Hinweisen; **Recall** den Anteil aller späteren Fälle, die einen Hinweis erhalten. Die tatsächliche Fallquote gehört als Vergleichswert immer dazu. Bei der kursweisen Auswahl werden die obersten 10 beziehungsweise 20 % **pro Kursdurchlauf und Stichtag** markiert, bei kleinen Kursen aufgerundet.

### Explorative zeitliche Ergebnisse

Auf 2014J erreicht das Wochenmodell an Tag 27 bei 7.828 noch angemeldeten Kurseinträgen eine AP von **0,625** gegenüber **0,429** für eine Referenz aus Kurs- und Anmeldedaten; der spätere Fallanteil beträgt **37,6 %**. Bei 20 % Hinweisen je Kurs sind es 1.567 Hinweise mit 1.006 Treffern: **64,2 % Trefferquote** und **34,1 % Recall** an diesem Stichtag.

Bei einer Simulation von 16 wöchentlichen Sichtungen in 2014J erhalten mit der 20-%-Auswahl insgesamt **4.768 von 8.682 Kurseinträgen** mindestens einmal einen Hinweis (54,9 %). Von 3.800 späteren Abbrüchen oder Nichtbestehen werden **2.761** mindestens einmal erkannt (72,7 % kumulativer Recall). Die Trefferquote der erstmaligen Hinweise beträgt 57,9 %. Die wiederholten Wochenhinweise dürfen dabei nicht als unterschiedliche Personen gezählt werden. Ein Wochenbudget von 20 % bedeutet über 16 Wochen also keine Gesamtquote von 20 %.

Diese Zahlen stammen aus einer **explorativen** zeitlichen Prüfung: 2014J wurde während der Projektentwicklung mehrfach eingesehen und beeinflusste Entscheidungen. Die Werte sind daher kein Ergebnis eines unberührten Abschlusstests und kein Nachweis der Wirkung einer Intervention. Die verglichenen Stichtage enthalten unterschiedliche noch angemeldete Gruppen; ein höherer Wert in einer späteren Woche beweist nicht, dass diese Woche der beste Zeitpunkt für Unterstützung ist.

### Frühere Tag-28-Analyse

Die erste Tag-28-Modellbasis umfasst 27.422 Kurseinträge, darunter 12.044 spätere Abbrüche oder `Fail` (43,9 %). Im damaligen zurückgelegten Prüfteil erreichte Histogram Gradient Boosting eine AP von 0,709 gegenüber 0,514 für die Referenz aus Kurs- und Anmeldedaten. Diese Auswertung verwendete einen anderen Stichtag und eine andere Aufteilung als die wöchentlichen Analysen; die Werte sollten nicht direkt miteinander verglichen werden. Der Tag-28-Prototyp wurde durch die Wochenversion abgelöst.

## Lokale Anwendung

Nach dem Klonen im Projektordner die Abhängigkeiten mit der versionierten `uv.lock` abgleichen und mit [uv](https://docs.astral.sh/uv/) starten:

```powershell
uv sync --locked
uv run streamlit run app.py
```

Die App benötigt `app.py`, `weekly_logic.py`, `models/oulad_wochen/schema.json` und die 16 Dateien `tag_006.joblib` bis `tag_111.joblib`. Nach dem Start erscheint zunächst nur der Upload. Für die Vorführung kann lokal `data/demo/oulad_wochen_2014j.csv` heruntergeladen und anschließend hochgeladen werden. Diese Datei wird durch `11_wochenmodelle_export.ipynb` erzeugt und liegt wegen des ignorierten Ordners `data/` nicht im Git-Repository. Ohne die lokale Datei lässt sich eine entsprechend vorbereitete eigene CSV hochladen; OULAD-Rohdateien sind **kein** direktes Upload-Format.

Die CSV braucht genau diese **Pflichtspalten** (weitere Spalten werden ignoriert):

```text
code_module,code_presentation,id_student,stichtag,anmeldetag,assessments_faellig,abgaben,banked_faellige,assessments_fehlend,klicks_bis_stichtag,klicks_letzte_7_tage
```

Die App prüft die Eingaben und lädt für jeden enthaltenen Stichtag sein Modell. Danach zeigt sie einen Überblick je Kursdurchlauf, eine sortierte Prüfliste mit den obersten 10 oder 20 %, beobachtete Klick- und Assessmentwerte, den Verlauf der hochgeladenen Wochen sowie eine kurze Einordnung der Grenzen. „Erstmals“ und „wiederholt“ beziehen sich ausschließlich auf die Wochen, die in **dieser CSV** stehen. Modellwerte werden zur Reihenfolge genutzt; sie sind keine geprüften individuellen Ausfallwahrscheinlichkeiten. Aussagen zu Klicks oder offenen Leistungen beschreiben Beobachtungen und keine nachgewiesenen Gründe für einen Modellhinweis.

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
| `app.py`, `weekly_logic.py` | Oberfläche sowie CSV-Prüfung, Modellbewertung und Hinweisauswahl |
| `models/oulad_wochen/` | Gespeichertes Schema und 16 Modell-Pipelines |

Die OULAD-Rohdaten und die aufbereiteten Dateien unter `data/` liegen lokal und werden nicht mit Git versioniert. Zum erneuten Erzeugen müssen die Rohdateien in der erwarteten Projektstruktur vorliegen und gegebenenfalls absolute Pfade in den frühen Notebooks an den eigenen Rechner angepasst werden. Das Exportnotebook setzt die vorbereitete Wochenbasis voraus; es erstellt sie nicht aus den Roh-CSV-Dateien. Die Ausführung der Notebooks ist daher in der beschriebenen Abhängigkeitsreihenfolge nötig. Gespeicherte `joblib`-Modelle nur aus vertrauenswürdigen Quellen laden.

## Grenzen und nächste Schritte

- OULAD beschreibt ausgewählte historische Fernstudienkurse; eine Übertragung auf heutige Weiterbildungen, andere Einrichtungen oder alle Lernenden ist nicht belegt.
- Nur zum jeweiligen Stichtag noch angemeldete Personen können einen Hinweis bekommen. Bereits erfolgte Abbrüche können damit nicht verhindert werden.
- Das gemeinsame Ziel verschmilzt Abbruch und Nichtbestehen. Der explorative Drei-Klassen-Versuch lieferte keine ausreichend verlässliche individuelle Risikorichtung für eine getrennte Anzeige.
- VLE-Klicks sind weder Lernzeit noch Verständnis; Lernen außerhalb der Plattform bleibt unsichtbar. Auch ein fehlendes Assessment kann im Einzelfall Daten- oder Prozessgründe haben.
- Der Bildungsabschluss verbesserte die mittlere Modellgüte an ausgewählten Stichtagen, verschob aber die Hinweise stark zwischen Bildungsgruppen. Auch ohne dieses Merkmal können andere Eingaben Ungleichheiten abbilden; die Gruppenprüfung ist nicht abgeschlossen.
- Die Prüfgruppe 2014J ist durch wiederholte Einsicht während der Entwicklung explorativ. Eine unabhängige zeitliche und externe Prüfung sowie die Bewertung von Fehlhinweisen und möglicher Benachteiligung fehlen.
- Eine hohe Trefferquote belegt weder kausale Gründe noch, dass eine Ansprache den Kursverlauf verbessert. Vor einem realen Einsatz braucht es fachlich abgestimmte Maßnahmen, Datenschutzprüfung und eine Bewertung im jeweiligen Bildungskontext.

Als Nächstes werden die verbleibenden Datenmöglichkeiten und methodischen Grenzen bewertet. Anschließend folgt ein Verständlichkeitstest der Oberfläche mit einer fachfremden Person und die Vorbereitung der Präsentation.

## Quelle

Kuzilek, J., Hlosta, M. & Zdrahal, Z. (2017): [Open University Learning Analytics dataset](https://doi.org/10.1038/sdata.2017.171). *Scientific Data*, 4, 170171. Der Datensatz wird unter [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) bereitgestellt.