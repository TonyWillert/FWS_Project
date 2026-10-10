"""LearnerCue: wöchentliche fachliche Sichtung historischer OULAD-Kurse."""

import logging
import math
from pathlib import Path

import streamlit as st

from operations import course_workload
from project_context import (
    CONTEXT, DATASET_URL, PAPER_URL, course_profile, file_overview, module_overview,
)
from reporting import course_report
from ui_text import local_group, local_status, local_upload_error, tr
from weekly_logic import (
    KURS,
    UploadFehler,
    bewerte_wochen,
    lade_modell,
    lade_schema,
    pruefe_csv,
)

logger = logging.getLogger(__name__)
PROJEKTORDNER = Path(__file__).resolve().parent
MODELLORDNER = PROJEKTORDNER / "models" / "oulad_wochen"
SCHEMADATEI = MODELLORDNER / "schema.json"
DEMODATEI = PROJEKTORDNER / "data" / "demo" / "oulad_wochen_2014j.csv"
LOGO = PROJEKTORDNER / "assets" / "learnercue.svg"

st.set_page_config(
    page_title="LearnerCue | Course review", page_icon=str(LOGO), layout="wide"
)
# Abstand zur festen Streamlit-Leiste: Bedienelemente beginnen darunter.
st.markdown(
    "<style>.block-container {max-width: 1180px; padding-top: 5rem}</style>",
    unsafe_allow_html=True,
)

marke, kopf = st.columns([1, 11], vertical_alignment="center")
with marke:
    st.image(str(LOGO), width=54)
with kopf:
    st.title("LearnerCue")
st.caption(tr(st.session_state.get("language_v2", "de"), "tagline"))

# Sprachwahl und Hilfe stehen in einer eigenen Zeile; bei schmaler Ansicht
# verdrängen sie weder das Logo noch die feste Menüleiste.
sprache, hilfe, fehlerknopf = st.columns([2, 1, 1], vertical_alignment="bottom")
with sprache:
    language = st.selectbox(
        "Sprache / Language",
        ["de", "en"],
        format_func=lambda code: "Deutsch" if code == "de" else "English",
        key="language_v2",
    )


def render_project_context(selected_language: str):
    """Zeigt belegte OULAD-Fakten und den Stand des Prototyps zweisprachig."""
    content = CONTEXT[selected_language]
    st.subheader(content["title"])
    st.markdown(content["lead"])

    with st.expander(content["source_title"], expanded=True):
        st.write(content["source_body"])
        st.caption(content["selection"])
        st.markdown(f"**{content['files_title']}**")
        st.dataframe(file_overview(selected_language), hide_index=True, width="stretch")

    st.markdown(f"**{content['courses_title']}**")
    st.dataframe(module_overview(selected_language), hide_index=True, width="stretch")
    st.caption(content["courses_note"])
    st.markdown(f"**{content['content_title']}**")
    st.write(content["content_body"])

    with st.expander(content["demo_title"]):
        st.write(content["demo_body"])
    with st.expander(content["model_title"]):
        st.write(content["model_body"])
        st.write(content["label_body"])
    with st.expander(content["evidence_title"]):
        st.write(content["evidence_body"])

    st.markdown(f"**{content['benefit_title']}**")
    st.write(content["benefit_body"])
    with st.expander(content["ideas_title"]):
        st.write(content["ideas_body"])
    with st.expander(content["limits_title"], expanded=True):
        for limit in content["limits"]:
            st.markdown(f"- {limit}")

    st.markdown(f"**{content['sources_title']}**")
    st.markdown(f"- [{content['source_label']}]({DATASET_URL})")
    st.markdown(f"- [{content['paper_label']}]({PAPER_URL})")
    st.caption(content["readme_note"])


@st.dialog(tr(language, "help_title"), width="large")
def show_help():
    """Bietet eine kurze Bedienhilfe und den ausführlichen Hintergrund vor Upload."""
    quick, background = st.tabs(
        [tr(language, "help_quick"), tr(language, "help_background")]
    )
    with quick:
        st.subheader(tr(language, "help_start"))
        st.markdown(tr(language, "help_steps"))
        st.info(tr(language, "theme_help"))
        st.subheader(tr(language, "glossary"))
        for key in (
            "gloss_entry", "gloss_course", "gloss_hint", "gloss_first",
            "gloss_vle", "gloss_assessment", "gloss_score", "gloss_csv",
            "gloss_ap", "gloss_recall",
        ):
            st.write(tr(language, key))
        st.subheader(tr(language, "limitations"))
        st.write(tr(language, "limits_text"))
        st.subheader(tr(language, "manager_method"))
        st.write(tr(language, "manager_formula"))
    with background:
        render_project_context(language)


@st.dialog(tr(language, "bug_title"), width="large")
def show_bug_report():
    """Sammelt einen Bericht ausschließlich zum lokalen Herunterladen."""
    st.write(tr(language, "bug_intro"))
    observed = st.text_area(tr(language, "bug_observed"), key="bug_observed")
    expected = st.text_area(tr(language, "bug_expected"), key="bug_expected")
    steps = st.text_area(tr(language, "bug_steps"), key="bug_steps")
    st.warning(tr(language, "bug_privacy"))
    # Keine Kursdatei, ID oder sonstige Upload-Daten werden automatisch beigelegt.
    body = (
        "LearnerCue — bug report\n\n"
        f"Observed / Beobachtet:\n{observed}\n\n"
        f"Expected / Erwartet:\n{expected}\n\n"
        f"Steps / Schritte:\n{steps}\n"
    )
    st.download_button(
        tr(language, "bug_download"),
        data=body.encode("utf-8"),
        file_name="learnercue_bug_report.txt",
        mime="text/plain",
        disabled=not observed.strip(),
    )
    if not observed.strip():
        st.caption(tr(language, "bug_missing"))
    st.link_button(
        tr(language, "bug_issue"),
        "https://github.com/TonyWillert/FWS_Project/issues/new",
    )


with hilfe:
    if st.button(tr(language, "help_button"), use_container_width=True):
        show_help()
with fehlerknopf:
    if st.button(tr(language, "bug_button"), use_container_width=True):
        show_bug_report()

# Vor einem Upload sind weder Kursgrafiken noch Hinweise sichtbar.
hat_upload = st.session_state.get("wochen_csv") is not None
with st.expander(
    tr(language, "change_data" if hat_upload else "data_title"),
    expanded=not hat_upload,
):
    st.write(tr(language, "data_intro"))
    if DEMODATEI.exists():
        st.download_button(
            tr(language, "demo_download"),
            data=DEMODATEI.read_bytes(),
            file_name=DEMODATEI.name,
            mime="text/csv",
        )
    upload = st.file_uploader(
        tr(language, "upload_label"), type="csv", key="wochen_csv",
        help=tr(language, "upload_help"),
    )
    st.caption(tr(language, "upload_help"))

if upload is None:
    st.info(tr(language, "no_upload"))
    st.stop()

try:
    schema = lade_schema(MODELLORDNER)
except (UploadFehler, OSError, ValueError) as error:
    # Fehlende lokale Modelldateien sind ein technischer Fehler, kein CSV-Fehler.
    logger.warning("Wochenmodell konnte nicht geladen werden: %s", error)
    st.error(tr(language, "model_error"))
    st.stop()


@st.cache_resource(show_spinner=False)
def model_for_day(day: int, version_ns: int | None):
    """Lädt eine Pipeline je Kurstag und Dateiversion aus dem Projektordner."""
    return lade_modell(MODELLORDNER, schema, day)


@st.cache_data(show_spinner=False)
def process_upload(content: bytes, signature: tuple):
    """Prüft und bewertet die CSV nur erneut, wenn Datei oder Modelle wechseln."""
    validated = pruefe_csv(content, schema)
    version_times = dict(signature[1])
    return bewerte_wochen(
        validated, schema,
        lambda day: model_for_day(day, version_times[day]),
    )


# Eine neue Modelldatei macht die zwischengespeicherten Ergebnisse ungültig.
try:
    signature = (
        SCHEMADATEI.stat().st_mtime_ns,
        tuple(
            (
                int(day),
                path.stat().st_mtime_ns if path.exists() else None,
            )
            for day in schema["stichtage"]
            for path in [
                MODELLORDNER / schema["modellpfad_muster"].format(stichtag=day)
            ]
        ),
    )
    with st.spinner(tr(language, "load_spinner")):
        data = process_upload(upload.getvalue(), signature)
except UploadFehler as error:
    message = local_upload_error(language, str(error))
    st.error(message)
    if language == "en" and message == tr(language, "upload_error"):
        with st.expander(tr(language, "technical_details")):
            st.code(str(error), language=None)
    st.stop()
except (OSError, ValueError):
    logger.exception("Fehler beim Lesen der Modell-Dateien")
    st.error(tr(language, "model_error"))
    st.stop()
except Exception:
    logger.exception("Unerwarteter Fehler bei der Modellbewertung")
    st.error(tr(language, "model_error"))
    st.stop()

# Der jüngste im Upload enthaltene Stichtag ist für den Coach voreingestellt.
days = sorted(int(day) for day in data["stichtag"].unique())
st.caption(tr(language, "loaded", n=len(data), file=upload.name))
day = st.selectbox(
    tr(language, "day_label"), days, index=len(days) - 1,
    format_func=lambda value: tr(
        language, "day_option", day=value, week=(value + 1) // 7
    ),
)
week = data.loc[data["stichtag"].eq(day)].copy()
history_known = day == 6 or any(earlier < day for earlier in days)
st.caption(tr(language, "history_known" if history_known else "history_unknown"))

# Diese Kursübersicht zeigt nur einen Datenstand je Kurs und ausgewähltem Tag.
overview = (
    week.assign(
        is_alert=week["hinweisstufe"].ne("Kein Hinweis"),
        first=week["hinweisstatus"].eq("Erstmals im Upload"),
        repeated=week["hinweisstatus"].eq("Wiederholt im Upload"),
        due=week["assessments_fehlend"].gt(0),
    )
    .groupby(KURS, as_index=False)
    .agg(
        entries=("id_student", "size"),
        alerts=("is_alert", "sum"),
        first=("first", "sum"),
        repeated=("repeated", "sum"),
        due=("due", "sum"),
    )
)
overview["course"] = overview["code_module"] + " " + overview["code_presentation"]
overview = overview.sort_values(
    ["first", "alerts", "course"], ascending=[False, False, True]
)
course_names = overview["course"].tolist()


def open_course(name: str):
    """Öffnet nach einem Klick die Prüfliste des gewählten Kursdurchlaufs."""
    st.session_state["course_focus"] = name
    st.session_state["view_v2"] = "course"


def open_context():
    """Öffnet die belegten Hintergrundinfos zu Modulen und Demo."""
    st.session_state["view_v2"] = "background"


view = st.radio(
    tr(language, "nav"), ["week", "course", "manager", "background"],
    format_func=lambda value: tr(language, "nav_" + value),
    horizontal=True, key="view_v2",
)

if view == "week":
    st.subheader(tr(language, "nav_week"))
    st.write(tr(language, "week_intro"))
    left, middle, right = st.columns(3)
    left.metric(tr(language, "metric_entries"), len(week))
    middle.metric(tr(language, "metric_courses"), len(overview))
    right.metric(
        tr(language, "metric_hints"), int(overview["alerts"].sum()),
        help=tr(language, "metric_hints_help"),
    )
    displayed = overview[["course", "entries", "alerts", "due"]].copy()
    if history_known:
        displayed = overview[
            ["course", "entries", "alerts", "first", "repeated", "due"]
        ].copy()
    st.dataframe(
        displayed,
        hide_index=True, width="stretch",
        column_config={
            "course": st.column_config.TextColumn(tr(language, "col_course")),
            "entries": st.column_config.NumberColumn(tr(language, "col_entries")),
            "alerts": st.column_config.NumberColumn(
                tr(language, "col_review"), help=tr(language, "col_review_help")
            ),
            "first": st.column_config.NumberColumn(tr(language, "col_first")),
            "repeated": st.column_config.NumberColumn(tr(language, "col_repeat")),
            "due": st.column_config.NumberColumn(
                tr(language, "col_due"), help=tr(language, "col_due_help")
            ),
        },
    )
    chosen = st.selectbox(tr(language, "course_choose"), course_names)
    st.button(
        tr(language, "open_list"), type="primary",
        on_click=open_course, args=(chosen,),
    )

    # Die tabellarische Historie zählt Hinweise je Woche, nicht Kontakte.
    if len(days) > 1:
        with st.expander(tr(language, "trend_open")):
            trend = (
                data.assign(
                    first=data["hinweisstatus"].eq("Erstmals im Upload"),
                    repeated=data["hinweisstatus"].eq("Wiederholt im Upload"),
                )
                .groupby("stichtag", as_index=False)
                .agg(first=("first", "sum"), repeated=("repeated", "sum"))
                .rename(columns={
                    "stichtag": tr(language, "day_label"),
                    "first": tr(language, "col_first"),
                    "repeated": tr(language, "col_repeat"),
                })
            )
            st.write(tr(language, "trend_intro"))
            st.dataframe(
                trend, hide_index=True, width="stretch",
                column_config={
                    tr(language, "day_label"): st.column_config.NumberColumn(
                        tr(language, "trend_day"), format="%d"
                    ),
                    tr(language, "col_first"): st.column_config.NumberColumn(
                        tr(language, "col_first"), help=tr(language, "col_first_help")
                    ),
                    tr(language, "col_repeat"): st.column_config.NumberColumn(
                        tr(language, "col_repeat"), help=tr(language, "col_repeat_help")
                    ),
                },
            )
            st.caption(tr(language, "trend_caption"))

elif view == "course":
    st.subheader(tr(language, "course_title"))
    focus = st.session_state.get("course_focus", course_names[0])
    course_name = st.selectbox(
        tr(language, "course_label"), course_names,
        index=course_names.index(focus) if focus in course_names else 0,
    )
    st.session_state["course_focus"] = course_name
    info = overview.loc[overview["course"].eq(course_name)].iloc[0]
    course = week.loc[
        week["code_module"].eq(info["code_module"])
        & week["code_presentation"].eq(info["code_presentation"])
    ].sort_values("modellwert", ascending=False, kind="stable")
    profile = course_profile(
        language, str(info["code_module"]), str(info["code_presentation"])
    )
    if profile:
        st.caption(profile)
        st.button(CONTEXT[language]["course_about_button"], on_click=open_context)
    st.caption(tr(language, "course_caution"))

    # Angezeigt werden echte Personenzahlen; 10/20 Prozent sind nur die Quote.
    count_short = int(course["hinweisstufe"].eq("Hohe Priorität").sum())
    count_extended = int(course["hinweisstufe"].ne("Kein Hinweis").sum())
    options = ["extended", "short"]
    def scope_label(value: str) -> str:
        """Beschriftet die Auswahl mit der konkreten Kursgröße."""
        return tr(
            language, "scope_more" if value == "extended" else "scope_less",
            n=count_extended if value == "extended" else count_short,
            total=len(course),
        )

    scope = st.radio(
        tr(language, "scope_label"), options,
        format_func=scope_label, help=tr(language, "scope_help"),
    )
    st.info(tr(
        language, "scope_caption", n=(count_short if scope == "short" else count_extended),
        total=len(course), remaining=len(course) - (count_short if scope == "short" else count_extended),
    ))
    with st.expander(tr(language, "scope_evidence_title")):
        st.write(tr(language, "scope_evidence"))
    if scope == "short":
        review = course.loc[course["hinweisstufe"].eq("Hohe Priorität")].copy()
        review["hinweisstatus"] = review["hinweisstatus_10"]
    else:
        review = course.loc[course["hinweisstufe"].ne("Kein Hinweis")].copy()

    chosen_filter = "all"
    if history_known:
        chosen_filter = st.radio(
            tr(language, "filter_label"), ["all", "first", "repeat"],
            format_func=lambda value: tr(language, "filter_" + value),
            horizontal=True, help=tr(language, "gloss_first"),
        )
        if chosen_filter != "all":
            status = (
                "Erstmals im Upload" if chosen_filter == "first"
                else "Wiederholt im Upload"
            )
            review = review.loc[review["hinweisstatus"].eq(status)].copy()

    st.write(tr(language, "list_summary", n=len(review), total=len(course)))
    # Bericht und Oberfläche verwenden exakt dieselben bereits gefilterten Zeilen.
    st.download_button(
        tr(language, "report_button"),
        data=course_report(
            course, review, day=day, name=course_name,
            scope=scope_label(scope),
            selection=tr(language, "filter_" + chosen_filter),
            language=language,
        ),
        file_name=tr(language, "report_file", day=day, course=course_name.replace(" ", "_")),
        mime="text/html",
        help=tr(language, "report_help"),
    )
    if review.empty:
        st.info(tr(language, "list_empty"))
    else:
        displayed = review[
            ["id_student", "hinweisstufe", "hinweisstatus",
             "assessments_fehlend", "klicks_letzte_7_tage"]
        ].copy()
        displayed["hinweisstufe"] = displayed["hinweisstufe"].map(
            lambda value: local_group(language, value)
        )
        displayed["hinweisstatus"] = displayed["hinweisstatus"].map(
            lambda value: local_status(language, value)
        )
        st.dataframe(
            displayed, hide_index=True, width="stretch",
            column_config={
                "id_student": st.column_config.NumberColumn(
                    tr(language, "col_id"), help=tr(language, "col_id_help"), format="%d"
                ),
                "hinweisstufe": st.column_config.TextColumn(
                    tr(language, "col_group"), help=tr(language, "col_group_help")
                ),
                "hinweisstatus": st.column_config.TextColumn(
                    tr(language, "col_status"), help=tr(language, "col_status_help")
                ),
                "assessments_fehlend": st.column_config.NumberColumn(
                    tr(language, "col_missing"), help=tr(language, "col_due_help")
                ),
                "klicks_letzte_7_tage": st.column_config.NumberColumn(
                    tr(language, "col_clicks"), help=tr(language, "col_clicks_help")
                ),
            },
        )
        selected = st.selectbox(
            tr(language, "person_choose"), range(len(review)),
            format_func=lambda index: f"ID {review.iloc[index]['id_student']}",
        )
        entry = review.iloc[selected]
        st.markdown(tr(language, "detail_title", id=entry["id_student"], day=day))
        observations = []
        questions = []
        due = int(entry["assessments_fehlend"])
        if due:
            observations.append(tr(language, "due_observation", n=due))
            questions.append(tr(language, "due_question"))
        clicks = int(entry["klicks_letzte_7_tage"])
        median = course["klicks_letzte_7_tage"].median()
        if clicks == 0:
            observations.append(tr(language, "zero_observation"))
            questions.append(tr(language, "zero_question"))
        elif clicks < median:
            observations.append(tr(language, "low_observation"))
        if not observations:
            observations.append(tr(language, "no_observation"))
        for observation in observations:
            st.write("• " + observation)
        st.markdown(f"**{tr(language, 'conversation')}**")
        for question in questions:
            st.write("• " + question)
        st.write("• " + tr(language, "general_question"))
        st.caption(tr(language, "detail_limit"))
        st.markdown(f"**{tr(language, 'next_step_title')}**")
        if due:
            st.info(tr(language, "next_step_due"))
        if history_known and entry["hinweisstatus"] == "Wiederholt im Upload":
            st.info(tr(language, "next_step_repeat"))
        elif not due:
            st.info(tr(language, "next_step_first"))
        st.caption(tr(language, "next_step_shared"))
        st.caption(tr(language, "next_step_record"))
        with st.expander(tr(language, "draft_title")):
            st.write(tr(language, "draft_label"))
            st.code(tr(language, "draft_text"), language=None)
            st.caption(tr(language, "draft_limit"))

    # Kein zweites Klickdiagramm für dieselbe Person: Werte stehen in der Liste.
    st.caption(tr(language, "contact_limit"))

elif view == "manager":
    st.subheader(tr(language, "manager_title"))
    st.write(tr(language, "manager_intro"))
    manager_scope = st.radio(
        tr(language, "manager_scope"), ["short", "extended"],
        index=1, horizontal=True,
        format_func=lambda value: tr(language, "manager_" + value),
        help=tr(language, "manager_scope_help"),
    )

    with st.expander(tr(language, "manager_scenario"), expanded=True):
        review_minutes = st.number_input(
            tr(language, "manager_review_min"), min_value=0.0,
            max_value=120.0, value=2.0, step=1.0,
        )
        email_inputs, call_inputs = st.columns(2)
        with email_inputs:
            email_percent = st.slider(
                tr(language, "manager_email_pct"), 0, 100, 50, step=5,
            )
            email_minutes = st.number_input(
                tr(language, "manager_email_min"), min_value=0.0,
                max_value=120.0, value=4.0, step=1.0,
            )
        with call_inputs:
            call_percent = st.slider(
                tr(language, "manager_call_pct"), 0, 100, 10, step=5,
            )
            call_minutes = st.number_input(
                tr(language, "manager_call_min"), min_value=0.0,
                max_value=180.0, value=20.0, step=5.0,
            )
        hours_per_coach = st.number_input(
            tr(language, "manager_hours_coach"), min_value=0.5,
            max_value=60.0, value=8.0, step=0.5,
        )
        st.caption(tr(language, "manager_assumptions"))

    workload, history_available = course_workload(
        data, day, manager_scope,
        review_minutes=review_minutes,
        email_percent=email_percent,
        email_minutes=email_minutes,
        call_percent=call_percent,
        call_minutes=call_minutes,
    )
    selected_total = int(workload["selected"].sum())
    hours_total = float(workload["workload_hours"].sum())
    coach_capacity = math.ceil(hours_total / hours_per_coach)
    a, b, c, d = st.columns(4)
    a.metric(tr(language, "manager_selected"), selected_total)
    if history_available:
        b.metric(tr(language, "manager_first"), int(workload["first"].sum()))
    else:
        b.metric(tr(language, "manager_first_unknown"), "—")
    c.metric(tr(language, "manager_hours"), f"{hours_total:.1f} h")
    d.metric(
        tr(language, "manager_coaches"), coach_capacity,
        help=tr(language, "manager_coaches_help"),
    )
    st.caption(tr(language, "manager_history" if history_available else "manager_history_missing"))

    st.markdown(f"**{tr(language, 'manager_chart')}**")
    st.bar_chart(
        workload.set_index("course")["workload_hours"].rename(
            tr(language, "manager_course_hours")
        ),
    )
    st.markdown(f"**{tr(language, 'manager_table')}**")
    columns = [
        "course", "entries", "selected", "due_work",
        "planned_emails", "planned_calls", "workload_hours",
    ]
    if history_available:
        columns[3:3] = ["first", "repeated"]
    shown = workload[columns].copy()
    shown["workload_hours"] = shown["workload_hours"].round(1)
    labels = {
        "course": "manager_course",
        "entries": "manager_entries",
        "selected": "manager_hints",
        "first": "manager_new",
        "repeated": "manager_repeat",
        "due_work": "manager_due",
        "planned_emails": "manager_emails",
        "planned_calls": "manager_calls",
        "workload_hours": "manager_course_hours",
    }
    st.dataframe(
        shown.rename(columns={name: tr(language, labels[name]) for name in columns}),
        hide_index=True, width="stretch",
    )
    with st.expander(tr(language, "manager_method")):
        st.write(tr(language, "manager_formula"))
    st.caption(tr(language, "manager_limits"))
    st.caption(tr(language, "manager_no_roles"))

else:
    render_project_context(language)
