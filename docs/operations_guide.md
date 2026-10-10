# Von der Prüfliste zum Unterstützungsangebot

Die Liste zeigt eine **Reihenfolge zur fachlichen Sichtung**. Sie legt weder
automatisch Kontakte fest noch sagt sie, welche Hilfe eine Person braucht.
Die Modellwerte sind hier nicht als individuelle Wahrscheinlichkeiten geprüft.

## Wie groß ist die Aufgabe?

In der früheren **2014J-Auswertung am Ende von Tag 28** gab es:

| Modul | Noch angemeldete Kurseinträge | Später Abbruch oder `Fail` |
| --- | ---: | ---: |
| AAA | 348 | 95 |
| BBB | 1.773 | 622 |
| CCC | 1.990 | 976 |
| DDD | 1.447 | 655 |
| EEE | 1.016 | 332 |
| FFF | 1.834 | 717 |
| GGG | 715 | 271 |
| **Gesamt** | **9.123** | **3.668** |

Darunter waren insgesamt 1.693 spätere Abbrüche und 1.975 Ergebnisse
`Fail`. Diese Tabelle stammt aus der **älteren Tag-28-Prüfgruppe** und ist
nicht die Prüfgruppe der aktuellen Wochenmodelle.

Für das aktuelle Wochenmodell umfasst die Tag-27-Prüfgruppe in 2014J
7.828 Einträge, davon 2.947 spätere Fälle. Auf den rund 20-%-Prüflisten
standen 1.567 Kurseinträge. 1.006 von ihnen gehörten später zu den Fällen;
1.941 spätere Fälle standen an diesem Tag nicht auf den Listen. Über 16
Wochen erhielten 4.768 von 8.682 Kurseinträgen mindestens einmal einen
Hinweis. Deshalb ist die Zahl späterer Fälle weder die Zahl persönlicher
Gespräche noch ein sinnvolles Wochenbudget.

### Abbruch und `Fail` für die aktuelle Wochenprüfung getrennt zählen

Die Demo-CSV enthält absichtlich kein späteres Ergebnis. Für die
**retrospektive** Auswertung kann die folgende Zelle im Notebook
`11_wochenmodelle_export.ipynb` direkt nach dessen erster Codezelle
ausgeführt werden. Sie trainiert kein Modell und verwendet `studentInfo.csv`
nur zur späteren Bewertung, nicht zur Vorhersage:

```python
ergebnisse = pd.read_csv(
    projektordner / "Daten OULAD" / "studentInfo.csv",
    usecols=schluessel + ["final_result"],
)
assert not ergebnisse.duplicated(schluessel).any()

tag27 = pruefung.loc[
    pruefung["stichtag"].eq(27),
    schluessel + ["abbruch_oder_fail"],
].merge(ergebnisse, on=schluessel, how="left", validate="one_to_one")

assert tag27["final_result"].notna().all()
assert tag27["abbruch_oder_fail"].eq(
    tag27["final_result"].isin(["Withdrawn", "Fail"])
).all()

tabelle = pd.crosstab(tag27["code_module"], tag27["final_result"])
tabelle = tabelle.reindex(
    columns=["Withdrawn", "Fail", "Pass", "Distinction"],
    fill_value=0,
)
tabelle.insert(0, "Kurseinträge", tabelle.sum(axis=1))
tabelle["Abbruch oder Fail"] = tabelle["Withdrawn"] + tabelle["Fail"]
tabelle["Anteil %"] = (
    100 * tabelle["Abbruch oder Fail"] / tabelle["Kurseinträge"]
).round(1)
display(tabelle)
```

## Kontaktweg als prüfbarer Arbeitsvorschlag

1. **Sichtung:** Offene fällige Leistungen und Plattformaktivität mit den
   Kursdaten abgleichen. Ein Datenfehler oder Lernen außerhalb der Plattform
   kann sonst falsch eingeordnet werden.
2. **Unterstützung anbieten:** Eine kurze, neutrale Nachricht kann ein
   niedriger Einstieg sein. Der Coach prüft Text und Empfänger; die App
   verschickt keine Nachrichten. Keine Aussage wie „Das Modell sagt, dass
   Sie abbrechen werden“ verwenden.
3. **Gespräch anbieten:** Wenn eine Leistung tatsächlich offen ist, eine
   zeitnahe Klärung nötig wird, die Person um Hilfe bittet oder trotz eines
   früheren Kontakts eine Schwierigkeit fortbesteht, kann ein Telefonat
   oder Videotermin sinnvoll sein. Ein wiederholter Modellhinweis allein
   belegt keinen fehlenden Kontakt.
4. **Gruppentermin:** Bei derselben fachlichen oder technischen Frage
   mehrerer Personen kann ein freiwilliger Termin effizient sein. Die
   individuelle Prüfliste gehört nicht in einen Gruppenraum.
5. **Dokumentation:** Tatsächlich erfolgte Kontakte, Antworten und weitere
   Schritte müssen in einem geschützten Betreuungssystem dokumentiert werden.
   Die aktuelle App hat weder Kontaktdaten noch einen dauerhaften
   Bearbeitungsstand oder getrennte Zugriffsrechte.

Für einen Schwellenwert „ab hier anrufen, darunter mailen“ gibt es für
dieses OULAD-Modell **keine validierte Grundlage**. Eine kleine randomisierte
Studie fand bei personalisierten E-Mail-Erinnerungen mehr rechtzeitige
Aktivität, prüfte aber keine verhinderten Abbrüche
([Bälter et al., 2023](https://formative.jmir.org/2023/1/e43977)).
Eine Studie der Open University fand einen Nutzen eines **Bündels** aus
Text, Telefon und E-Mail, ohne die einzelnen Kanäle zu trennen
([Herodotou et al., 2020](https://learning-analytics.info/index.php/JLA/article/view/6682)).
Ein anderes Feldexperiment zeigte, dass eine gute Vorhersage allein die
Abbruchquote nicht senkt
([Plak et al., 2022](https://onlinelibrary.wiley.com/doi/10.1111/hequ.12298)).
Die Reihenfolge oben ist daher ein Arbeitsentwurf für einen Pilotversuch,
keine belegte Therapie- oder Kontaktregel.

## Was die Leitungsansicht rechnet

Pro Kurs und gewähltem Kurstag zählen die 10-%- oder 20-%-Listen
Kurseinträge. Die Leitung wählt Minuten je Sichtung, die geplanten Anteile
für Nachricht und Gespräch, deren Dauer und die je Coach dafür verfügbaren
Wochenstunden. Nachricht und Gespräch können dieselbe Person betreffen.
Die Anzahl geplanter Kontakte wird **je Kurs** auf ganze Personen
aufgerundet. Dann gilt:

> Geschätzte Stunden = Listeneinträge × Sichtungsminuten / 60
> + geplante Nachrichten × Nachrichtenminuten / 60
> + geplante Gespräche × Gesprächsminuten / 60.

„Benötigte Coach-Kapazitäten“ ist diese Stundenzahl geteilt durch die
angegebenen freien Stunden je Coach und aufgerundet. Die 20-%-Auswahl
an Tag 27 hatte historisch 1.567 Einträge; schon zwei Minuten Sichtung
je Eintrag wären rund 52 Stunden. Geplante Nachrichten, Gespräche und
Rückfragen erhöhen die Zeit. Die Kennzahl ist ein **Szenario**, kein
gemessener Personalbedarf. Die App kennt weder tatsächliche Antworten
noch verhinderte Abbrüche; ein realistischer Pilot müsste Aufwand und
Nutzen im jeweiligen Weiterbildungskontext gesondert messen.
