"""LearnerCue: wöchentliche fachliche Sichtung historischer OULAD-Kurse."""

import hashlib
from io import BytesIO
import logging
import math
from pathlib import Path

import pandas as pd
import streamlit as st

from coach_workflow import next_step_reason
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
UI_BEISPIEL = PROJEKTORDNER / "examples" / "learnercue_ui_sample.csv"
LOGO = PROJEKTORDNER / "assets" / "learnercue.svg"

st.set_page_config(
    page_title="LearnerCue | Course review", page_icon=str(LOGO), layout="wide"
)
# Größere Grundschrift und klare Klickflächen nach dem ersten Verständlichkeitstest.
st.markdown(
    """<style>
    .block-container {max-width: 1280px; padding-top: 5rem}
    .stApp p, .stApp label {font-size: 1.06rem; line-height: 1.55}
    .stApp button {min-height: 2.7rem}
    </style>""",
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
hat_upload = (
    st.session_state.get("wochen_csv") is not None
    or st.session_state.get("sample_active_v1", False)
)
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
    elif UI_BEISPIEL.exists():
        st.download_button(
            tr(language, "sample_download"),
            data=UI_BEISPIEL.read_bytes(),
            file_name=UI_BEISPIEL.name,
            mime="text/csv",
        )
        st.caption(tr(language, "sample_limit"))
    if UI_BEISPIEL.exists():
        sample_active = st.session_state.get("sample_active_v1", False)
        if st.button(tr(language, "sample_stop" if sample_active else "sample_start")):
            st.session_state["sample_active_v1"] = not sample_active
            st.rerun()
    else:
        sample_active = False
    upload = None
    if not sample_active:
        upload = st.file_uploader(
            tr(language, "upload_label"), type="csv", key="wochen_csv",
            help=tr(language, "upload_help"),
        )
        st.caption(tr(language, "upload_help"))

if sample_active:
    upload = BytesIO(UI_BEISPIEL.read_bytes())
    upload.name = UI_BEISPIEL.name

if upload is None:
    st.info(tr(language, "no_upload"))
    st.stop()

synthetic_upload = UI_BEISPIEL.exists() and upload.getvalue() == UI_BEISPIEL.read_bytes()
if synthetic_upload:
    st.warning(tr(language, "sample_limit"))

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
overview = overview.sort_values("course")
course_names = overview["course"].tolist()


def choose_area(area: str):
    """Wechselt zwischen den getrennten Einstiegen der Demo."""
    st.session_state["area_v3"] = area


def choose_coach_view(name: str):
    st.session_state["coach_view_v3"] = name


def open_course(name: str):
    """Öffnet nach einem Klick die Prüfliste des gewählten Kursdurchlaufs."""
    st.session_state["course_focus"] = name
    st.session_state["course_select_v3"] = name
    st.session_state["area_v3"] = "coach"
    st.session_state["coach_view_v3"] = "course"


def open_context():
    """Öffnet die belegten Hintergrundinfos zu Modulen und Demo."""
    st.session_state["area_v3"] = "background"


area = st.session_state.get("area_v3", "home")
if area not in ("home", "coach", "manager", "background"):
    area = "home"

if area == "home":
    st.header(tr(language, "area_title"))
    st.write(tr(language, "area_intro"))
    coach_card, manager_card = st.columns(2, gap="large")
    with coach_card, st.container(border=True):
        st.subheader(tr(language, "area_coach_title"))
        st.write(tr(language, "area_coach_desc"))
        st.button(
            tr(language, "area_coach_button"), type="primary",
            use_container_width=True, on_click=choose_area, args=("coach",),
        )
    with manager_card, st.container(border=True):
        st.subheader(tr(language, "area_manager_title"))
        st.write(tr(language, "area_manager_desc"))
        st.button(
            tr(language, "area_manager_button"),
            use_container_width=True, on_click=choose_area, args=("manager",),
        )
    st.button(tr(language, "nav_background"), on_click=open_context)
    st.stop()

heading, switch = st.columns([3, 1], vertical_alignment="center")
heading.caption(tr(language, "area_current_" + area))
switch.button(
    tr(language, "area_switch"), use_container_width=True,
    on_click=choose_area, args=("home",),
)
if area == "coach":
    overview_nav, course_nav = st.columns(2)
    overview_nav.button(
        tr(language, "nav_week"), type="primary" if st.session_state.get("coach_view_v3", "week") == "week" else "secondary",
        use_container_width=True, on_click=choose_coach_view, args=("week",),
    )
    course_nav.button(
        tr(language, "nav_course"), type="primary" if st.session_state.get("coach_view_v3", "week") == "course" else "secondary",
        use_container_width=True, on_click=choose_coach_view, args=("course",),
    )
    view = st.session_state.get("coach_view_v3", "week")
else:
    view = area

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
    course_picker, course_button = st.columns([3, 1], vertical_alignment="bottom")
    with course_picker:
        chosen = st.selectbox(tr(language, "course_choose"), course_names)
    with course_button:
        st.button(
            tr(language, "open_list"), type="primary", use_container_width=True,
            on_click=open_course, args=(chosen,),
        )
    st.caption(tr(language, "course_row_hint"))
    displayed = overview[["course", "entries", "alerts", "due"]].copy()
    if history_known:
        displayed = overview[
            ["course", "entries", "alerts", "first", "repeated", "due"]
        ].copy()
    event = st.dataframe(
        displayed,
        hide_index=True, width="stretch",
        key=f"course_overview_{day}_{st.session_state.get('overview_epoch_v3', 0)}",
        on_select="rerun", selection_mode="single-row",
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
    if event.selection.rows:
        open_course(str(displayed.iloc[event.selection.rows[0]]["course"]))
        # Eine alte Zeilenauswahl darf beim Zurückkehren nicht erneut öffnen.
        st.session_state["overview_epoch_v3"] = st.session_state.get("overview_epoch_v3", 0) + 1
        st.rerun()

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
    if st.session_state.get("course_select_v3") not in course_names:
        st.session_state["course_select_v3"] = course_names[0]
    course_name = st.selectbox(
        tr(language, "course_label"), course_names, key="course_select_v3",
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

    # Die ganze Kursgruppe bleibt sichtbar. Die bestehenden 10/20-%-Markierungen
    # beschreiben nur relative Sichtungsstufen, keine validierte Risikoschwelle.
    count_short = int(course["hinweisstufe"].eq("Hohe Priorität").sum())
    count_extended = int(course["hinweisstufe"].ne("Kein Hinweis").sum())
    first_metric, next_metric, rest_metric = st.columns(3)
    first_metric.metric(tr(language, "priority_first"), count_short)
    next_metric.metric(tr(language, "priority_next"), count_extended - count_short)
    rest_metric.metric(tr(language, "priority_rest"), len(course) - count_extended)
    st.info(tr(language, "priority_explain"))
    with st.expander(tr(language, "risk_when_title")):
        st.markdown(tr(language, "risk_when_explain", day=day))
    with st.expander(tr(language, "scope_evidence_title")):
        st.write(tr(language, "scope_evidence"))

    review = course.copy().reset_index(drop=True)
    review["rang"] = range(1, len(review) + 1)

    def list_history(entry):
        if entry["hinweisstufe"] != "Kein Hinweis":
            return local_status(language, entry["hinweisstatus"])
        if pd.notna(entry["ersthinweis_tag"]) and entry["ersthinweis_tag"] < day:
            return tr(language, "status_prior")
        return tr(language, "status_never")

    review["listenverlauf"] = review.apply(list_history, axis=1)
    file_key = hashlib.sha256(upload.getvalue()).hexdigest()[:16]
    demo_states = st.session_state.setdefault("demo_contact_v3", {})

    def entry_key(entry):
        return (
            f"{file_key}:{entry['code_module']}:"
            f"{entry['code_presentation']}:{entry['id_student']}"
        )

    def contact_label(entry):
        record = demo_states.get(entry_key(entry), {"status": "open"})
        if record["status"] == "followup":
            due_day = record["day"]
            key = "demo_due" if due_day <= day else "demo_followup_day"
            return tr(language, key, day=due_day)
        return tr(language, "demo_" + record["status"])

    review["bearbeitungsstand"] = review.apply(contact_label, axis=1)
    review["naechster_schritt"] = review.apply(
        lambda entry: next_step_reason(
            entry["hinweisstufe"], demo_states.get(entry_key(entry), {"status": "open"}), day
        ), axis=1,
    )
    open_count = int(review["naechster_schritt"].eq("review").sum())
    due_count = int(review["naechster_schritt"].eq("due").sum())
    st.markdown(f"**{tr(language, 'worklist_title')}**")
    st.caption(tr(language, "worklist_explain", open=open_count, due=due_count))
    list_view = st.radio(
        tr(language, "worklist_choose"), ["all", "next"],
        format_func=lambda value: tr(language, "worklist_" + value),
        horizontal=True, key=f"list_view_{file_key}_{course_name}_{day}",
    )
    visible = review if list_view == "all" else review.loc[review["naechster_schritt"].notna()]
    st.write(tr(language, "list_summary", n=len(visible), total=len(review)))
    # Bericht und Oberfläche verwenden exakt dieselbe vollständige Rangliste.
    st.download_button(
        tr(language, "report_button"),
        data=course_report(
            course, review, day=day, name=course_name,
            scope=tr(language, "scope_all"),
            selection=tr(language, "filter_all"),
            language=language, synthetic=synthetic_upload,
        ),
        file_name=tr(language, "report_file", day=day, course=course_name.replace(" ", "_")),
        mime="text/html",
        help=tr(language, "report_help"),
    )
    if list_view == "next":
        st.caption(tr(language, "report_full"))
    if visible.empty:
        st.info(tr(language, "worklist_empty"))
        st.stop()
    displayed = visible[
        ["rang", "id_student", "hinweisstufe", "listenverlauf",
         "bearbeitungsstand", "assessments_fehlend"]
    ].copy()
    displayed["hinweisstufe"] = displayed["hinweisstufe"].map(
        lambda value: local_group(language, value)
    )
    colors = {
        tr(language, "group_high"): "background-color: #F5DDD4; color: #302620;",
        tr(language, "group_more"): "background-color: #FAE9C8; color: #302920;",
        tr(language, "group_remaining"): "background-color: #E9F1EC; color: #25332E;",
    }
    styled = displayed.style.apply(
        lambda row: [colors[row["hinweisstufe"]]] * len(row), axis=1
    )
    person_options = visible.index.tolist()
    person_key = f"person_select_v4_{file_key}_{course_name}_{day}_{list_view}"
    if st.session_state.get(person_key) not in person_options:
        st.session_state[person_key] = person_options[0]
    event = st.dataframe(
            styled, hide_index=True, width="stretch", row_height=38,
            key=f"roster_{file_key}_{course_name}_{day}_{list_view}_{st.session_state.get('roster_epoch_v4', 0)}",
            on_select="rerun", selection_mode="single-row",
            column_config={
                "rang": st.column_config.NumberColumn(tr(language, "col_rank"), format="%d"),
                "id_student": st.column_config.NumberColumn(
                    tr(language, "col_id"), help=tr(language, "col_id_help"), format="%d"
                ),
                "hinweisstufe": st.column_config.TextColumn(
                    tr(language, "col_group"), help=tr(language, "col_group_help")
                ),
                "listenverlauf": st.column_config.TextColumn(
                    tr(language, "col_status"), help=tr(language, "col_status_help")
                ),
                "bearbeitungsstand": st.column_config.TextColumn(
                    tr(language, "col_demo_status"), help=tr(language, "demo_status_limit")
                ),
                "assessments_fehlend": st.column_config.NumberColumn(
                    tr(language, "col_missing"), help=tr(language, "col_due_help")
                ),
            },
    )
    if event.selection.rows:
        selected_row = person_options[event.selection.rows[0]]
        if st.session_state[person_key] != selected_row:
            st.session_state[person_key] = selected_row
        # Die Zeile darf die spätere Auswahl im Dropdown nicht erneut überschreiben.
        st.session_state["roster_epoch_v4"] = st.session_state.get("roster_epoch_v4", 0) + 1
        st.rerun()
    st.caption(tr(language, "missing_explain"))
    selected = st.selectbox(
        tr(language, "person_choose"), person_options,
        format_func=lambda index: f"#{review.loc[index, 'rang']} · ID {review.loc[index, 'id_student']}",
        key=person_key,
    )
    entry = review.loc[selected]
    st.markdown(tr(language, "detail_title", id=entry["id_student"], day=day))
    st.caption(tr(
        language, "person_priority_current", day=day, rank=entry["rang"],
        total=len(review), group=local_group(language, entry["hinweisstufe"]),
    ))
    if pd.notna(entry["ersthinweis_tag"]) and entry["ersthinweis_tag"] <= day:
        st.caption(tr(language, "person_priority_first", first=int(entry["ersthinweis_tag"])))
    else:
        st.caption(tr(language, "person_priority_none", day=day))
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
    elif pd.notna(entry["ersthinweis_tag"]) and entry["ersthinweis_tag"] < day:
        st.info(tr(language, "next_step_repeat"))
    elif not due:
        st.info(tr(language, "next_step_first"))
    st.caption(tr(language, "next_step_shared"))

    st.markdown(f"**{tr(language, 'demo_status_title')}**")
    state_key = entry_key(entry)
    saved = demo_states.get(state_key, {"status": "open"})
    status_options = ["open", "draft", "waiting", "talking", "followup", "done"]
    status = st.selectbox(
        tr(language, "demo_status_choose"), status_options,
        index=status_options.index(saved["status"]),
        format_func=lambda value: tr(language, "demo_" + value),
        key=f"status_{state_key}",
    )
    followup_day = None
    if status == "followup":
        followup_day = st.number_input(
            tr(language, "demo_followup_choose"), min_value=0, max_value=269,
            value=int(saved.get("day", min(day + 7, 269))), step=1,
            key=f"followup_{state_key}",
        )
    if st.button(tr(language, "demo_status_save")):
        demo_states[state_key] = {"status": status, "day": followup_day}
        st.rerun()
    st.caption(tr(language, "demo_status_limit"))
    st.caption(tr(language, "next_step_record"))
    with st.expander(tr(language, "draft_title")):
        st.write(tr(language, "draft_label"))
        st.code(tr(language, "draft_text"), language=None)
        st.caption(tr(language, "draft_limit"))

elif view == "manager":
    st.subheader(tr(language, "manager_title"))
    st.info(tr(language, "manager_provisional"))
    st.write(tr(language, "manager_intro"))
    manager_scope = st.radio(
        tr(language, "manager_scope"), ["short", "extended", "all"],
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
    a, b = st.columns(2)
    c, d = st.columns(2)
    a.metric(tr(language, "manager_selected"), selected_total)
    if history_available:
        b.metric(tr(language, "manager_first"), int(workload["first"].sum()))
    else:
        b.metric(tr(language, "manager_due"), int(workload["due_work"].sum()))
    c.metric(tr(language, "manager_hours"), f"{hours_total:.1f} h")
    d.metric(
        tr(language, "manager_coaches"), coach_capacity,
        help=tr(language, "manager_coaches_help"),
    )
    history_note = (
        "manager_history_all" if manager_scope == "all" else
        "manager_history" if history_available else "manager_history_missing"
    )
    st.caption(tr(language, history_note))

    st.markdown(f"**{tr(language, 'manager_chart')}**")
    st.bar_chart(
        workload.sort_values("workload_hours", ascending=False).set_index("course")["workload_hours"].rename(
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
    st.info(tr(language, "manager_decisions"))
    st.caption(tr(language, "manager_limits"))
    st.caption(tr(language, "manager_no_roles"))

else:
    render_project_context(language)
