"""Aggregierte Planungszahlen für die wöchentliche Kursbetreuung."""

from __future__ import annotations

import math

import pandas as pd

from weekly_logic import KURS, SCHLUESSEL


def course_workload(
    data: pd.DataFrame,
    day: int,
    scope: str,
    *,
    review_minutes: float,
    email_percent: int,
    email_minutes: float,
    call_percent: int,
    call_minutes: float,
) -> tuple[pd.DataFrame, bool]:
    """Plant Aufwand je Kurs; die Kontaktanteile sind Annahmen, keine Prognosen.

    Eine Person zählt am gewählten Tag und im gewählten Kurs nur einmal. Bei
    einer kurzen Liste wird auch ihre frühere Listenzugehörigkeit anhand der
    kurzen Listen berechnet, nicht anhand der bisherigen 20-%-Markierung.
    """
    if scope not in ("short", "extended"):
        raise ValueError("Unbekannter Listenumfang")
    if any(value < 0 for value in (review_minutes, email_minutes, call_minutes)):
        raise ValueError("Minuten dürfen nicht negativ sein")
    if not 0 <= email_percent <= 100 or not 0 <= call_percent <= 100:
        raise ValueError("Kontaktanteile müssen zwischen 0 und 100 liegen")

    week = data.loc[data["stichtag"].eq(day)]
    if week.empty:
        raise ValueError("Für diesen Kurstag liegen keine Daten vor")
    if week.duplicated(SCHLUESSEL).any():
        raise ValueError("Doppelte Kurseinträge am selben Stichtag")

    def chosen(frame: pd.DataFrame) -> pd.DataFrame:
        if scope == "short":
            return frame.loc[frame["hinweisstufe"].eq("Hohe Priorität")]
        return frame.loc[frame["hinweisstufe"].ne("Kein Hinweis")]

    selected = chosen(week).copy()
    previous = data.loc[data["stichtag"].lt(day)]
    history_known = day == 6 or not previous.empty
    if history_known:
        prior_keys = pd.MultiIndex.from_frame(chosen(previous)[SCHLUESSEL])
        current_keys = pd.MultiIndex.from_frame(selected[SCHLUESSEL])
        selected["first_in_file"] = ~current_keys.isin(prior_keys)

    courses = (
        week.groupby(KURS, as_index=False)
        .size()
        .rename(columns={"size": "entries"})
    )
    selected["due_work"] = selected["assessments_fehlend"].gt(0)
    aggregates = {"selected": ("id_student", "size"), "due_work": ("due_work", "sum")}
    if history_known:
        aggregates["first"] = ("first_in_file", "sum")
    counts = selected.groupby(KURS, as_index=False).agg(**aggregates)
    courses = courses.merge(counts, on=KURS, how="left", validate="one_to_one")
    for column in ("selected", "due_work", "first"):
        if column in courses:
            courses[column] = courses[column].fillna(0).astype(int)
    if history_known:
        courses["repeated"] = courses["selected"] - courses["first"]

    # Pro Kurs wird auf ganze Kontakte aufgerundet. E-Mail und Gespräch sind
    # getrennte Annahmen; dieselbe Person kann beides erhalten.
    courses["planned_emails"] = (
        courses["selected"] * email_percent / 100
    ).apply(math.ceil)
    courses["planned_calls"] = (
        courses["selected"] * call_percent / 100
    ).apply(math.ceil)
    courses["review_hours"] = courses["selected"] * review_minutes / 60
    courses["email_hours"] = courses["planned_emails"] * email_minutes / 60
    courses["call_hours"] = courses["planned_calls"] * call_minutes / 60
    courses["workload_hours"] = (
        courses["review_hours"] + courses["email_hours"] + courses["call_hours"]
    )
    courses["course"] = courses["code_module"] + " " + courses["code_presentation"]
    return courses.sort_values("course").reset_index(drop=True), history_known
