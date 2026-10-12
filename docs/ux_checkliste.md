# LearnerCue – UX-Checkliste

Diese Punkte nacheinander in der laufenden App prüfen. Hake sie erst ab, wenn du sie selbst gesehen hast. Für den Verständlichkeitstest sollte eine andere Person möglichst ohne Erklärungen vorgehen.

## Einstieg

- [ ] Die App zeigt vor dem Upload keine Kursgrafiken oder Hinweise.
- [ ] Logo und Titel, Sprache, Hilfe und Fehlerbericht sind sichtbar; die obere Menüleiste verdeckt nichts.
- [ ] In einem frischen Klon lässt sich die synthetische Testdatei herunterladen und hochladen; mit lokal vorhandener OULAD-2014J-Datei erscheint stattdessen deren Download.
- [ ] Die synthetische Datei wird nach dem Upload als reiner Bedienungstest gekennzeichnet; die fachliche Vorführung verwendet die OULAD-2014J-Datei.
- [ ] Eine ungeeignete CSV erzeugt eine verständliche Fehlermeldung.
- [ ] Schon vor einem Upload zeigt **Hilfe & Hintergrund → Über die Demo** Datenherkunft, Modultabelle, Modellweg und Grenzen.

## Wöchentliche Sichtung

- [ ] Der angezeigte Kurstag ist erkennbar; der jüngste hochgeladene Tag ist voreingestellt.
- [ ] Die Bereichswahl führt getrennt zu Coach, Leitung und Projekthintergrund; innerhalb der Coach-Ansicht gibt es keine Leitungsregisterkarte.
- [ ] Die Navigation Diese Woche / Kurs prüfen sowie der Wechsel zurück zur Bereichswahl funktionieren mit Maus und Tastatur.
- [ ] Ich kann in eigenen Worten erklären, dass „neu in vorrangiger Sichtung“ einen ersten Hinweis **in den hochgeladenen Wochen** meint, nicht einen ersten Kontakt.
- [ ] Die optionale Wochentabelle enthält verständliche Spalten und erklärt, dass dieselbe Person in mehreren Wochen auftauchen kann.
- [ ] Ein Klick auf eine Kurszeile oder die oben sichtbare Kurswahl öffnet den richtigen Kurs; BBB ist ohne Hinweis auffindbar.
- [ ] Im Kursbereich stimmen Fachbereich und gegebenenfalls 2014J-Dauer mit der Projekttabelle überein; „Mehr über die OULAD-Kurse“ führt zum Hintergrund.

## Projektwissen und Grenzen

- [ ] AAA, BBB, GGG sind als Sozialwissenschaften; CCC, DDD, EEE, FFF als STEM beschriftet. Konkrete Modultitel werden nicht behauptet.
- [ ] Die Beschreibung unterscheidet sieben OULAD-Rohdateien, die aufbereitete Demo-CSV und die exportierten Wochenmodelle.
- [ ] Ich erkenne, dass die Demo keine späteren Kursergebnisse enthält und 2014J kein unberührter Abschlusstest ist.
- [ ] Die App benennt die bis zum Stichtag genutzten Merkmale, das gemeinsame spätere Ergebnis, den belegten historischen Vergleich und den noch ungeprüften Nutzen einer Ansprache.
- [ ] Quellenlinks öffnen die offizielle Datensatzseite und die Originalveröffentlichung; Deutsch und Englisch erklären dieselben Fakten.
- [ ] Nach Änderungen an Modellmerkmalen, Ziel, Wochen oder Demo-Zahlen sind `project_context.py` und README zusammen geprüft.

## Personen und Betreuung

- [ ] Alle Personen des Kurses sind in Modellreihenfolge sichtbar, mit Rangnummer, Text und Farbe für die drei relativen Sichtungsgruppen.
- [ ] Ein Klick auf eine Personenzeile öffnet genau diese ID; die Auswahl per Dropdown funktioniert ebenfalls. Nach einem Wechsel von Kurstag, Kurs oder Filter bleibt keine veraltete Auswahl hängen.
- [ ] „Jetzt prüfen“ enthält nur vorrangige Einträge mit Beispielstatus „noch nicht gesichtet“ und an diesem Kurstag fällige Beispiel-Wiedervorlagen, auch wenn deren Rang derzeit nachrangig ist.
- [ ] Antwort ausstehend, Gespräch, abgeschlossener Eintrag und eine erst später fällige Wiedervorlage tauchen nicht als aktuell fällig auf; die Ansicht „Alle im Kurs“ ist jederzeit verfügbar.
- [ ] Mir ist klar, dass auch weiter unten spätere Abbrüche oder Nichtbestehen vorkommen können und die Gruppen keine validierten Risikoschwellen sind.
- [ ] Ich kann einzelne Personen und ihre beobachteten Merkmale ansehen, ohne diese Merkmale als erwiesene Ursache zu missverstehen.
- [ ] Der neutrale Nachrichtentext ist als Entwurf erkennbar und wird nicht automatisch versendet.
- [ ] Der Beispielstatus und die Wiedervorlage sind als Sitzungssimulation erkennbar und erscheinen in Liste und Bericht; echte Kontakte werden nicht behauptet.
- [ ] Der Kursbericht passt zu Kurstag, Kurs und vollständiger Rangliste, auch bei aktivem Filter „Jetzt prüfen“.
- [ ] Der Kontaktvorschlag unterscheidet offene Leistungen und frühere Listenhinweise; er löst keine Nachricht aus.

## Leitung und Kapazität

- [ ] Die Leitungsansicht zeigt Summen je Kurs und keine Lernenden-IDs.
- [ ] Erste Prioritätsgruppe, beide vorrangigen Gruppen und die ganze Kursgruppe ändern Eintragszahl und geschätzte Stunden nachvollziehbar.
- [ ] Null Prozent geplante Nachrichten und Gespräche lässt nur die Sichtungszeit übrig.
- [ ] „Erstmals vorrangig“ zählt bei der ersten Gruppe nur frühere Zugehörigkeit zu dieser Gruppe; bei der ganzen Kursgruppe wird keine triviale Listenhistorie angezeigt.
- [ ] Eine CSV mit nur Tag 27 erzeugt keine vermeintlich „erstmaligen“ Hinweise.
- [ ] Coach-Kapazitäten sind als Szenario erkennbar, nicht als tatsächliche Kontakte oder gemessener Personalbedarf.
- [ ] Der Leitungsbereich ist als vorläufiges Konzept und mögliches separates Folgeprojekt benannt.

## Lesbarkeit und Bedienung

- [ ] „Kurs öffnen“, die Zeilenauswahl und alle anderen Buttons sind in Hell- und Dunkelmodus gut lesbar.
- [ ] Bei 200 % Browser-Zoom bleiben Sprachwahl, Navigation, Prüfliste und Dialoge bedienbar.
- [ ] Die wichtigsten Schritte sind mit Tastatur erreichbar und eine Testperson versteht Beschriftungen und Hilfe.
- [ ] Wenn verfügbar: Screenreader liest Navigation, Tabellenspalten und Hilfetexte verständlich vor.
- [ ] Deutsch und Englisch sind durchgängig; der Fehlerbericht enthält keine Kursdaten automatisch.

## Vor einem echten Einsatz außerhalb von OULAD

- [ ] Kontaktmöglichkeit und Bearbeitungsstand sind fachlich definiert und geschützt gespeichert.
- [ ] Rückmeldungen der Lernenden und mögliche Unterstützungsangebote sind mit Coaches abgestimmt.
- [ ] Eine eigene, unabhängige zeitliche Prüfung und eine Prüfung der Gruppenunterschiede liegen vor.
- [ ] Ein Mensch prüft Nachrichtentexte und Empfänger vor jedem Versand; die App allein trifft keine Entscheidung.
