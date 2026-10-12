"""Kleine, ausdrücklich simulierte Arbeitsansicht für die Kurssichtung."""

from typing import Mapping


def next_step_reason(priority: str, record: Mapping[str, object], day: int) -> str | None:
    """Kennzeichnet offene Sichtungen und fällige Wiedervorlagen.

    Frühere Modellhinweise sind keine Kontakte. Wartende Antworten oder eine
    künftige Wiedervorlage werden ohne vereinbarten Fälligkeitstag nicht fällig.
    """
    status = record.get("status", "open")
    if status == "followup" and record.get("day") is not None:
        if int(record["day"]) <= day:
            return "due"
    if status == "open" and priority != "Kein Hinweis":
        return "review"
    return None
