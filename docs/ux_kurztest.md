# LearnerCue: kurzer Verständlichkeitstest

Ziel: Prüfen, ob eine Person ohne Statistikkenntnisse die Oberfläche bedienen und einen Hinweis richtig einordnen kann. Dieser Test bewertet die Bedienung, nicht die Eignung der Modelle für eine Weiterbildung.

## Vorbereitung

1. App mit `uv run streamlit run app.py` starten.
2. Für die fachliche Vorführung die lokale Datei `data/demo/oulad_wochen_2014j.csv` bereithalten. Sie enthält keine späteren Kursergebnisse. Für einen reinen Bedienungstest nach einem frischen Klon kann die mitgelieferte synthetische Datei genutzt werden; ihre Ränge sagen nichts über die historische Modellgüte.
3. Der Testperson nur sagen: „Du betreust mehrere Kurse und möchtest heute schauen, wo ein unterstützendes Gespräch sinnvoll sein könnte.“ Danach möglichst nicht durch die Oberfläche führen. Für die Leitungsansicht später die Rolle wechseln.
4. Beobachten, wo sie zögert, welche Wörter sie selbst benutzt und welche Erklärung sie erwartet. Bei Problemen zunächst nachfragen: „Was würdest du hier vermuten?“

## Aufgaben für die Testperson

1. Lade die Vorführdatei hoch und finde heraus, für welchen Kurstag du gerade Daten siehst.
2. Öffne die Coach-Ansicht und wähle BBB direkt aus der Kursübersicht. Zeige eine Person, die dort **neu in der vorrangigen Sichtung** erscheint. Was bedeutet „neu“ hier genau?
3. Beschreibe in eigenen Worten, was die App über diese Person tatsächlich beobachtet hat und was du vor einer Ansprache noch prüfen würdest.
4. Sind alle Personen des Kurses sichtbar? Erkläre, was die drei farbigen Gruppen und die Rangnummer bedeuten. Kann die App daraus schließen, dass eine Person sicher abbrechen oder nicht bestehen wird?
5. Klicke eine Personenzeile an und wähle anschließend eine andere Person über das Dropdown. Wechsle zwischen „Alle im Kurs“ und „Jetzt prüfen“. Welche Einträge erscheinen dort, und bleibt der ursprüngliche Rang erkennbar?
6. Ändere bei einer vorrangigen Person den **Beispielstatus** zu „Antwort ausstehend“; sie sollte nicht mehr unter „Jetzt prüfen“ stehen. Setze für eine andere Person eine Wiedervorlage für den gewählten oder einen früheren Kurstag und prüfe, ob sie dort erscheint. Eine spätere Wiedervorlage sollte dort noch nicht erscheinen. Was passiert beim Schließen der Browser-Sitzung?
7. Öffne **Über die Demo**, zunächst ohne Upload und später über die Bereichswahl. Erkläre, was wir über BBB oder CCC wissen und welche konkreten Kursinhalte unbekannt bleiben. Sind die verwendeten Daten, der historische Modellvergleich und die Grenzen verständlich?
8. Lade bei aktivem „Jetzt prüfen“ einen Bericht herunter. Prüfe, ob Kurs, Tag, **vollständige** Rangliste und Beispielstatus mit der Gesamtansicht übereinstimmen.
9. Stelle die Seite auf Englisch und den Dunkelmodus um; prüfe dann 200 % Browser-Zoom. Sind die Bedienung und die wichtigsten Hinweise weiterhin verständlich und lesbar?
10. Öffne „Fehler melden“. Erkennst du, dass der Bericht lokal heruntergeladen wird und keine Daten automatisch versendet werden?
11. Wechsle über die Bereichswahl zur **Leitung**. Ist erkennbar, dass ihre Kennzahlen nur ein vorläufiges Planungsszenario und kein fertiges KPI-Produkt sind?

## Beobachtungen festhalten

| Aufgabe | Ohne Hilfe geschafft? | Wo gab es Unsicherheit? | Wortlaut oder Verbesserungsidee |
| --- | --- | --- | --- |
| Upload und Kurstag |  |  |  |
| Kurs und neue Anzeige |  |  |  |
| Person und Gesprächsanlass |  |  |  |
| Bedeutung der Prüfliste |  |  |  |
| Zeilenauswahl und „Jetzt prüfen“ |  |  |  |
| Glossar und Kontaktstatus |  |  |  |
| Projektbereich und Kursinhalte |  |  |  |
| Kursbericht |  |  |  |
| Englisch und Dunkelmodus |  |  |  |
| Fehlerbericht |  |  |  |
| Leitungsansicht und Planungsannahmen |  |  |  |

Abschlussfragen: „Welche Information hat dir gefehlt?“ und „Welche Anzeige war überflüssig?“ Danach gezielt die Stellen ändern, die im Test tatsächlich Schwierigkeiten verursacht haben. Eine fachfremde Person prüft Verständlichkeit; ein späterer Test mit einem Coach aus der Erwachsenenbildung prüft zusätzlich den Arbeitsablauf.
