"""Druckbarer, lokaler Bericht für die aktuelle fachliche Kurssichtung."""

from html import escape

import pandas as pd

from ui_text import local_group, local_status, tr


def course_report(
    course: pd.DataFrame,
    review: pd.DataFrame,
    *,
    day: int,
    name: str,
    scope: str,
    selection: str,
    language: str,
) -> bytes:
    """Erstellt ein eigenständiges HTML mit genau dem sichtbaren Listenfilter."""
    def h(value: object) -> str:
        """Schützt hochgeladene Werte vor HTML- und Markup-Ausführung."""
        return escape(str(value), quote=True)
    title = tr(language, "report_title")
    columns = [
        tr(language, key)
        for key in ("col_id", "col_group", "col_status", "col_missing", "col_clicks")
    ]
    headers = "".join(f"<th scope='col'>{h(label)}</th>" for label in columns)
    rows = []
    for row in review.itertuples(index=False):
        values = [
            row.id_student,
            local_group(language, row.hinweisstufe),
            local_status(language, row.hinweisstatus),
            int(row.assessments_fehlend),
            int(row.klicks_letzte_7_tage),
        ]
        rows.append("<tr>" + "".join(f"<td>{h(value)}</td>" for value in values) + "</tr>")

    due = int(review["assessments_fehlend"].gt(0).sum())
    summary = tr(language, "report_numbers", n=len(course), selected=len(review), due=due)
    snapshot = tr(language, "report_snapshot", day=day, course=name)
    document = f"""<!doctype html>
<html lang="{h(language)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(title)} · {h(name)}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font: 15px/1.55 system-ui, sans-serif; max-width: 1050px;
          margin: 2rem auto; padding: 0 1.25rem; color: #252923; }}
  h1 {{ color: #274d43; margin-bottom: .2rem; }}
  .subtle {{ color: #526159; }}
  .notice {{ background: #f3f2ec; border-left: 4px solid #bb6a45;
             padding: .8rem 1rem; margin: 1.4rem 0; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border-bottom: 1px solid #d9dfda; text-align: left;
             padding: .55rem .45rem; }}
  th {{ background: #ecf3ed; }}
  tr {{ break-inside: avoid; }}
  @media print {{ body {{ margin: 0; }} .print-tip {{ display: none; }} }}
</style>
</head>
<body>
<h1>{h(title)}</h1>
<p class="subtle">{h(snapshot)}</p>
<p>{h(summary)}</p>
<p><strong>{h(tr(language, 'report_scope'))}:</strong> {h(scope)} · {h(selection)}</p>
<p class="notice">{h(tr(language, 'report_note'))}</p>
<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="print-tip subtle">{h(tr(language, 'report_print'))}</p>
</body>
</html>"""
    return document.encode("utf-8")
