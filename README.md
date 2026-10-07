# Frühwarnhinweise für Lernende mit OULAD

## Fragestellung

Welche Lernenden, die am Ende von Kurstag 28 noch angemeldet sind, sollten bei begrenzter Betreuungskapazität zuerst ein Unterstützungsangebot erhalten?

Das Projekt untersucht, ob sich ein späterer Kursabbruch oder das Kursergebnis `Fail` anhand der bis Tag 28 verfügbaren Daten vorhersagen lässt. Ein Hinweis soll eine unterstützende Ansprache ermöglichen; er ist keine automatische Entscheidung über eine Person.

## Datengrundlage

Verwendet wird der anonymisierte [Open University Learning Analytics Dataset (OULAD)](https://research.stem.open.ac.uk/ouanalyse/dataset/) mit Kurs-, Anmelde-, Assessment- und Aktivitätsdaten aus 2013 und 2014. Für die aktuelle Analyse werden insbesondere `studentInfo.csv`, `studentRegistration.csv`, `assessments.csv`, `studentAssessment.csv` und `studentVle.csv` genutzt.

Die aufbereitete Tag-28-Modellbasis enthält 27.422 Kurseinträge. Bei 12.044 davon (43,9 %) trat später ein Abbruch oder das Kursergebnis `Fail` ein. Die Modellbasis liegt unter `data/processed/oulad_tag28_modellbasis.csv`.

## Bisheriges Vorgehen

1. Datenstruktur, fehlende Werte und Verknüpfungen der Tabellen geprüft.
2. Zunächst eine Vorhersage späterer Abmeldungen ab Tag 14 untersucht.
3. Die Fragestellung auf Tag 28 und das gemeinsame Ziel „späterer Abbruch oder Fail“ erweitert.
4. Merkmale aus Kurs und Anmeldung, VLE-Klicks sowie bis Tag 28 fälligen und erfüllten Assessments erstellt.
5. Einfache Referenzen, logistische Regression und Histogram Gradient Boosting verglichen.

Kurseinträge derselben Person bleiben bei der Aufteilung jeweils gemeinsam im Training oder in der Bewertung. Der Modellvergleich verwendet fünf Validierungs-Folds innerhalb der Entwicklungsdaten und einen zurückgelegten Prüfteil. Assessment-Punktzahlen werden nicht als frühe Merkmale verwendet, da kein Zeitpunkt vorliegt, ab dem die Bewertung bekannt war.

## Vorläufige Ergebnisse

Im zurückgelegten Prüfteil mit 5.474 Kurseinträgen erreicht das Modell mit Histogram Gradient Boosting eine Average Precision (AP) von **0,709**. Ein Referenzmodell allein mit Kurs- und Anmeldedaten erreicht **0,514**.

Bei einer Auswahl der höchsten Modellwerte **über alle Kurse hinweg** ergeben sich:

| Anteil mit Hinweis | Trefferquote | Erkannte spätere Fälle (Recall) |
| ---: | ---: | ---: |
| 10 % | 89,6 % | 20,1 % |
| 20 % | 76,9 % | 34,6 % |

Für eine spätere Anwendung erscheint eine Auswahl **innerhalb jedes Kursdurchlaufs** sinnvoller: Bei der kursübergreifenden Auswahl erhielt ein Modul im Prüfteil keinen einzigen Hinweis. Die kursweise Auswahl wurde bisher nur explorativ innerhalb der Entwicklungsdaten geprüft und benötigt noch eine gesonderte Bewertung.

## Geplanter Prototyp

Geplant ist eine einfache lokale Browseroberfläche, die einen vorbereiteten Datensatz einliest. Sie soll einen Überblick über Kurse und relevante Kennzahlen zeigen sowie innerhalb eines gewählten Kursdurchlaufs die Lernenden mit den höchsten Modellwerten anzeigen. Die Oberfläche ist **noch nicht umgesetzt**.

## Grenzen

- Die Daten stammen aus ausgewählten historischen Kursen einer Universität. Eine Übertragung auf heutige Weiterbildungen oder andere Einrichtungen ist nicht belegt.
- Das Modell erfasst nur Personen, die am Ende von Tag 28 noch angemeldet sind.
- „Abbruch“ und „Fail“ haben möglicherweise unterschiedliche Ursachen und erfordern unterschiedliche Unterstützung.
- VLE-Klicks bilden weder Verständnis noch Lernen außerhalb der Plattform zuverlässig ab.
- Ein Zusammenhang zwischen Merkmalen und späterem Ergebnis beweist nicht, dass eine Ansprache den Verlauf verbessert.
- Die Fragestellung wurde nach erster Sichtung des gesamten Datensatzes entwickelt. Auch die Entscheidung für eine kursweise Auswahl entstand nach einer Diagnose des Prüfteils. Deren Güte ist daher noch nicht unabhängig bestätigt.

## Projektdateien

- `01_datensichtung.ipynb`: Datensichtung und Erstellung der Modellbasen.
- `02_modellvergleich.ipynb` bis `04_abschlussbewertung.ipynb`: frühere Untersuchung der Abmeldung ab Tag 14.
- `05_tag28_modellvergleich.ipynb`: aktueller Modellvergleich und Auswertung für Tag 28.
- `06_zeitliche_pruefung.ipynb`: Prüfung des festgelegten Modells auf 2014J.
- `data/demo/oulad_tag28_demo.csv`: historische Vorführdaten ohne späteres
  Kursergebnis; die Browseroberfläche dafür ist noch geplant.

Die Rohdaten liegen lokal im Ordner `Daten OULAD`. Zum erneuten Ausführen muss der absolute Projektpfad in `01_datensichtung.ipynb` gegebenenfalls an den eigenen Rechner angepasst werden. Danach kann `05_tag28_modellvergleich.ipynb` die erzeugte Tag-28-Modellbasis einlesen.

## Nächste Schritte

- Kursweise Auswahl belastbar bewerten und den Einsatzumfang festlegen.
- Modelltraining und Vorhersage für den Prototyp reproduzierbar machen.
- Oberfläche, Ergebnisdarstellung und Präsentation erstellen.

## Quelle

Kuzilek, J., Hlosta, M. & Zdrahal, Z. (2017):
[Open University Learning Analytics dataset](https://doi.org/10.1038/sdata.2017.171).

Für die geplante Ansicht werden Hinweise innerhalb jeder Kurspräsentation
vergeben. Diese Auswahl erreicht im zurückgelegten Prüfteil bei rund 10 %
Hinweisen eine Trefferquote von 84,9 % und einen Recall von 19,5 %.
Sie wurde zuvor auch innerhalb der Entwicklungsdaten untersucht. Da die
Entscheidung für diese Auswahl nach Sichtung des Prüfteils entstand, ist
dessen kursweise Auswertung explorativ und noch keine unabhängige
Bestätigung.

## Zeitliche Nachprüfung

Zusätzlich zum bisherigen Modellvergleich wurde das festgelegte Verfahren
auf einem späteren Kursdurchlauf geprüft: Training mit 11.031
Kurseinträgen aus 2013, Prüfung mit 9.123 Einträgen aus 2014J.
Personen, die in beiden Zeiträumen vorkamen, wurden aus dem Training
entfernt.

Das Modell mit Histogram Gradient Boosting erreicht auf 2014J eine
Average Precision (AP) von 0,635; ein Referenzmodell aus Kurs- und
Anmeldedaten erreicht 0,424. Bei einer Auswahl innerhalb jeder
Kurspräsentation ergeben sich:

| Hinweise je Kurs | Hinweise | Treffer | Trefferquote | Recall |
| ---: | ---: | ---: | ---: | ---: |
| 10 % | 915 | 729 | 79,7 % | 19,9 % |
| 20 % | 1.827 | 1.225 | 67,0 % | 33,4 % |

Die einfache Regel „fälliges Assessment bis Tag 28 nicht erfüllt“
erzeugt 634 Hinweise mit 528 Treffern. Das Modell findet bei der
10-%-Auswahl zusätzlich 228 spätere Fälle unter 325 Personen, die
diese Regel nicht markiert.

CCC war in den Trainingsdaten aus 2013 nicht vertreten. Die Ergebnisse
für dieses Modul und die zeitliche Prüfung insgesamt sind daher kein
Nachweis für eine zuverlässige Übertragung auf neue Einrichtungen.
Die Modell- und Auswahlentscheidungen wurden zudem bereits durch
frühere Analysen des OULAD-Datensatzes beeinflusst.