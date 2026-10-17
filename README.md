# LearnerCue: Early support signals from OULAD

**Status: Completed portfolio project · Interactive Streamlit prototype.** [Portfolio case study](https://tonywillert.github.io/Portfolio/#learnercue)

[Try the live Streamlit demo](https://fwsproject-cjpggxprduvuak9kugbusk.streamlit.app/) · [Watch the 40-second demo](assets/learnercue_demo.mp4) · [Deutsche Dokumentation](README.de.md)

LearnerCue (formerly LernRadar) is a Streamlit prototype for weekly course review. It ranks **all learners still enrolled** in each course presentation by a model score. The top approximately 10%, the next approximately 10%, and everyone else are labelled review groups, **not validated individual risk thresholds**. A signal invites a coach to review the situation and consider support; it is not an automated decision about a learner.

**Primary workflow and output:** Start the sample or upload a prepared weekly CSV → choose a course day and course → inspect the **weekly review list** → check an entry and consider an offer of support. The management view adds a workload estimate. The [60–90-second walkthrough](docs/demo_walkthrough.md) gives the exact clicks for a live tour or screen recording.

In the public app, select **“Start guided example”** (or **“Geführtes Beispiel starten”**). Its fabricated records demonstrate the interface. The historical model results below come from a separate OULAD analysis.

The optional **40-second demo video** sits directly below the start button in an expandable section. It shows the Coach workflow from the course overview to the review list and a possible next step. The video is silent, with English captions, and uses the synthetic sample. It is stored in this repository and played directly in the app.

## The question

Which learners still enrolled on a given course day should coaches review first when support capacity is limited and the outcome of interest is **subsequent withdrawal or a final result of `Fail`**?

The prototype uses 16 weekly checkpoints, days 6, 13, …, 111. Its models do **not** distinguish whether an individual may withdraw or fail. One course entry means one person's enrolment in a particular course presentation; a person may have multiple entries.

## Data and features

The anonymised [Open University Learning Analytics Dataset (OULAD)](https://research.stem.open.ac.uk/ouanalyse/dataset/) covers seven modules and 22 presentations in 2013–14. The project mainly uses `studentInfo.csv`, `studentRegistration.csv`, `assessments.csv`, `studentAssessment.csv`, and `studentVle.csv`. VLE means virtual learning environment. Historical presentations run for 234–269 days, so day 27 is early in a course.

The [original publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC5704676/) groups AAA, BBB, and GGG under social sciences and CCC, DDD, EEE, and FFF under STEM. Module names are anonymised; actual course titles, syllabi, and learning content cannot reliably be inferred. The `vle.csv` file describes material types and planned weeks, not lesson texts. The app's **About the project** area explains the seven source tables, subject groups, and 2014J course durations. OULAD's module selection included criteria such as available VLE data, repeat presentations, larger cohorts, and a meaningful proportion of unsuccessful outcomes; it is not a random sample of all continuing education.

At each checkpoint, the prepared dataset contains only course entries still enrolled then. A later case is a recorded withdrawal after that checkpoint or a final `Fail`. Withdrawal without a readable date cannot be assigned reliably to this time-specific outcome. The processed weekly basis at `data/processed/oulad_wochenmodellbasis_tag6_bis111.csv` contains **423,510 snapshots and 13 columns**. An entry may appear in several weekly snapshots.

| Model input | Meaning |
| --- | --- |
| `code_module`, `code_presentation` | Module and presentation |
| `anmeldetag` | Enrolment day relative to course start |
| `assessments_faellig` | Number of assessments due so far |
| `abgaben` | Number of recorded submissions |
| `banked_faellige` | Number of due assessments covered by credit transfer |
| `assessments_fehlend` | Number of due assessments without recorded completion |
| `klicks_bis_stichtag` | Recorded VLE clicks up to the checkpoint |
| `klicks_letzte_7_tage` | Recorded VLE clicks in the preceding seven days |

`id_student` identifies and separates people, and `stichtag` selects the weekly model; neither is a model feature. Grades are excluded because a reliable timestamp for when a grade became known is unavailable.

## Development and evaluation

1. Inspected raw tables, keys, missing values, and withdrawal dates.
2. First investigated later withdrawals using a day-14 checkpoint.
3. Expanded to day 28 and the combined withdrawal-or-`Fail` outcome; compared simple rules, logistic regression, random forest, and histogram gradient boosting.
4. Evaluated the day-28 approach temporally on 2014J, then explored weekly snapshots through day 111, one model per week, and repeated course-level review selections.
5. Examined education level but excluded it from the exported models because it shifted alerts substantially between education groups.
6. Descriptively reviewed age group, previous module attempts, registered credits, and declared disability; also compared previous attempts as a feature at several checkpoints.
7. Exported the models and a demo CSV without later outcomes, then built the local Streamlit interface.

Earlier development comparisons separated training and validation groups by `id_student`. The 16 exported pipelines use `HistGradientBoostingClassifier`, each trained on its checkpoint in presentations before 2014J. For the 2014J demo and temporal assessment, **1,403 people** also present in earlier presentations were excluded. Training comprises **282,519 weekly snapshots**; the demo comprises **121,447 snapshots from 8,682 distinct course entries**. The demo file has neither `final_result` nor the target variable.

**Average precision (AP)** measures how well the ranking orders all entries against their later outcomes. **Precision** is the share of signalled entries that become cases; **recall** is the share of all later cases that receive a signal. The outcome prevalence is an essential reference. The top 10% or 20% is selected **within each presentation at each checkpoint**, rounding up in small courses.

### Exploratory temporal results

At day 27 in 2014J, the weekly model scores **AP 0.625**, compared with **0.429** for a reference using course and enrolment data, among **7,828** still-enrolled entries. Later outcome prevalence is **37.6%**. Selecting approximately 20% per course yields **1,567 signals**, including **1,006 later cases**: **64.2% precision** and **34.1% recall** at that checkpoint.

Across a simulation of 16 weekly reviews in 2014J, **4,768 of 8,682 entries** (54.9%) receive at least one signal with the 20% weekly selection. It identifies **2,761 of 3,800 later cases** at least once (**72.7% cumulative recall**). Precision at the first signal is 57.9%. Repeated weekly signals must not be counted as distinct people: a weekly capacity of 20% does not mean that only 20% are ever selected.

These are **exploratory** temporal results. The 2014J group was inspected repeatedly during development and influenced decisions, so it is not an untouched final test. The figures do not establish that outreach changes outcomes. Different checkpoints contain different still-enrolled populations; a higher metric in a later week alone does not establish the best time to intervene.

In `12_zusatzmerkmale.ipynb`, adding previous module attempts raised mean development AP at day 27 from 0.717 to 0.720 and recall at 20% from 33.3% to 33.7%. That gain was small, and the exported models do not use the feature. Associations with age or declared disability do not establish individual causes, and those attributes were not added.

### Earlier day-28 analysis

The initial day-28 dataset contains **27,422 entries**, including **12,044** later withdrawals or `Fail` results (43.9%). On its then-held-out evaluation split, histogram gradient boosting achieved AP **0.709**, versus **0.514** for a course-and-enrolment reference. Its checkpoint and split differ from those of the weekly analysis, so the figures are not directly comparable. The weekly version supersedes that prototype.

## Run the app locally

After cloning, install from the committed lockfile using [uv](https://docs.astral.sh/uv/):

```sh
uv sync --locked
uv run streamlit run app.py
```

The app requires `models/oulad_wochen/schema.json` and the 16 saved models `tag_006.joblib` through `tag_111.joblib`. They and `uv.lock` are committed. After launch, **Start guided example** is the main action; upload a prepared CSV in the expandable file area.

**Start guided example** loads `examples/learnercue_ui_sample.csv` and opens the Coach view directly. A button opens BBB 2014J; “Review now” is initially selected and an example entry appears beneath the list with observations and a possible next step. You can finish the guide while keeping the sample open. The file can also be downloaded. It contains **120 synthetic snapshots** for BBB and CCC at days 6, 13, and 20. The identifiers and observations are fabricated, and its rankings are computed with the saved models solely to test the interface. **Do not calculate model performance or draw conclusions about real learners from this file.**

For a research presentation using historical OULAD data, use the locally generated `data/demo/oulad_wochen_2014j.csv`. Notebook `11_wochenmodelle_export.ipynb` exports it from the prepared weekly dataset. The `data/` directory is Git-ignored, so this file is not part of the repository or public deployment. When present locally, its download replaces the smaller synthetic sample. You can also upload another prepared CSV; raw OULAD tables are **not** directly accepted.

Required CSV columns (additional columns are ignored):

```text
code_module,code_presentation,id_student,stichtag,anmeldetag,assessments_faellig,abgaben,banked_faellige,assessments_fehlend,klicks_bis_stichtag,klicks_letzte_7_tage
```

The app validates the input and loads a model for each included checkpoint. It opens the **Coach** weekly overview by default; **Change area** leads to **Management / Lead Coach** or the project background. In the weekly overview, click a course table row or use the course selector. With your own upload, course review displays **the full roster in model order** by default; the guided synthetic example initially selects “Review now.” Click a row or select a person to inspect observations and an explicitly simulated workflow status. “Review now” focuses on priority entries marked “not yet reviewed” and example follow-ups due that day. Replies pending, conversations, and later follow-ups are not due. A lower-ranked person with a due follow-up may also appear, with their full-roster rank visible. This view neither records real contacts nor decides automatically whom to contact.

**About the project** explains the data, anonymised modules, model path, historical comparison, possible value, and limits. Before upload, the same background is accessible through **Help & background → About the demo**. Help also contains the short main workflow and a glossary. Longer explanations of the rank groups sit in an expandable section on the course page, so the review list stays prominent. The course page displays the supported subject area and, for 2014J, course duration, rather than inventing a course title. Tooltips explain key columns and controls. The most recent uploaded checkpoint is selected initially. Model scores determine ordering; they are **not calibrated personal probabilities of failure**.

Switch between German and English at the top. Light and dark themes are defined in `.streamlit/config.toml` and selected in Streamlit's **Settings → Theme** menu. Known CSV errors are translated; unexpected errors have an English summary and optional technical details.

**Optional: download the full course report** opens a local printable HTML report for the full course ranking on the selected day, even while “Review now” is active. It includes anonymised IDs, observed assessment and click counts, and any simulated status in the current browser session, but no target outcome or established personal risk probability. Protect the report because it contains identifiers. An optional neutral message draft for a selected learner can be reviewed and copied by a coach; **no messages are sent**. **Report an issue** saves a text report locally and sends nothing automatically. The optional GitHub link is suitable only for reports without personal data.

“New” and “seen before” describe priority rank groups within the **uploaded CSV's weeks**, not contact history. Example states such as “message prepared,” “awaiting reply,” or “follow up on day …” last only for the browser session and are not records of actual conversations. Management list history covers the selected priority groups; its capacity estimate can include the first group, both groups, or all entries. Contact shares and minutes are assumptions. **The management KPIs are a provisional concept; a dependable management product would be a separate project.** The CSV omits later outcomes. The entry points do not implement access control. At day 27, the historical 20% selection covered only 34.1% of later cases, which is why the coach roster retains everyone. Clicks and missing assessments are observations, not demonstrated causes of an individual signal.

The coach view also answers **“When is a learner considered at risk?”** A model signal can appear weekly from day 6 for entries still enrolled. There is **no validated individual risk threshold or proven onset of personal risk**. The first two approximately 10% groups are review priorities within each course. A selected person's details show the current rank and, when applicable, the first day in a priority group **among uploaded weeks**. People outside those groups can also later withdraw or fail.

## Public portfolio demo

GitHub Pages hosts a portfolio page linking to the app; it cannot run the Streamlit Python process. LinkedIn can feature the external link but does not host the app. The live app is deployed on [Streamlit Community Cloud](https://share.streamlit.io/) from the public `TonyWillert/FWS_Project` repository, `main` branch, and `app.py`. Its deployment uses Python 3.14 as specified by `pyproject.toml` and `.python-version`, the committed `uv.lock`, models, and schema.

[Open the LearnerCue demo](https://fwsproject-cjpggxprduvuak9kugbusk.streamlit.app/) and try **Start guided example → This week → Open BBB 2014J → Weekly review list → Example entry and next step**. Then check “Everyone in course,” Change area, and the optional course report. Do **not** upload real personal course data to the public app. Historical metrics here derive from the separate OULAD evaluation; a local OULAD export is needed for a research walkthrough.

## Value and potential use

The demonstrated value is a better **order for human review** of the historical OULAD courses under a specified support capacity. The prototype does not show that support prevents withdrawal or failure. Before use in another institution, define its outcome, intervention timing, and coach capacity; prepare its own data; and test a model independently on later local courses. Operation would also require reliable imports, restricted access, and a human-maintained workflow history. These saved OULAD models are **not validated for assessing real learners elsewhere**.

## Project map and reproduction

| File | Role |
| --- | --- |
| `01_datensichtung.ipynb` | Raw data inspection and first model datasets |
| `02_modellvergleich.ipynb`–`04_abschlussbewertung.ipynb` | Early day-14 withdrawal investigation |
| `05_tag28_modellvergleich.ipynb` | Day-28 model comparison and assessment |
| `06_zeitliche_pruefung.ipynb` | Temporal assessment of day-28 version |
| `07_getrennte_risiken.ipynb` | Exploratory separation of withdrawal and failure |
| `08_zeitfenster.ipynb`, `09_wochenvergleich.ipynb` | Weekly snapshots, checkpoints, repeated signals |
| `10_bildungshintergrund.ipynb` | Education feature and group comparison |
| `11_wochenmodelle_export.ipynb` | Weekly training, model/schema export, demo CSV |
| `12_zusatzmerkmale.ipynb` | Descriptive review and extra feature comparisons |
| `app.py`, `ui_text.py`, `reporting.py` | App, bilingual UI text, local course report |
| `coach_workflow.py` | Rule for optional simulated work queue |
| `project_context.py` | Bilingual data and module background, sources, limits |
| `weekly_logic.py` | CSV validation, scoring, review group selection |
| `operations.py` | Management aggregation and capacity estimate |
| `.streamlit/config.toml` | Light and dark themes |
| `docs/ux_kurztest.md`, `docs/ux_checkliste.md` | First usability test and review checklist (German) |
| `docs/demo_walkthrough.md` | Short click path for a live or recorded walkthrough |
| `docs/reproduction.md` | Raw data layout, notebook order, and expected exports |
| `docs/operations_guide.md` | Contact strategy and planning assumptions (German) |
| `src/portfolio_projekt/paths.py` | Shared project path for all analysis notebooks |
| `assets/learnercue.svg` | Vector logo and browser icon |
| `assets/learnercue_demo.mp4` | Short Coach walkthrough with English captions |
| `models/oulad_wochen/` | Schema and 16 saved model pipelines |
| `examples/learnercue_ui_sample.csv` | Small synthetic CSV for a fresh clone |

Raw OULAD data and processed `data/` files remain local. Run `uv sync --locked` after cloning or updating, then select this project's `.venv` as the notebook kernel. All twelve analysis notebooks use the installed project package to locate the repository, independently of the working directory; no personal Windows path needs editing.

The shortest route from raw CSVs to the current weekly models is **01 → 08 → 11**, running every cell of each notebook with a fresh kernel. Notebook 01 creates the day-28 basis needed by a consistency check in 08. Notebook 08 creates **both** `oulad_wochenmodellbasis.csv` and `oulad_wochenmodellbasis_tag6_bis111.csv`; notebook 11 requires both before training and exporting. See [the reproduction guide](docs/reproduction.md) for the input layout, full notebook map, and recorded reference counts. Load saved `joblib` models only from trusted sources.

## Limits and next steps

- OULAD describes selected historical distance-learning courses. Transfer to present-day continuing education, other providers, or all learners is unproven.
- Original course titles and learning content are unavailable. Subject metadata cannot establish an individual's learning difficulty in a subject.
- Signals apply only while an entry is still enrolled. A withdrawal that has already happened cannot be prevented by that signal.
- The combined target merges withdrawal and failure. An exploratory three-class approach did not provide a sufficiently reliable individual direction of risk for a separate display.
- VLE clicks are neither study time nor comprehension; offline learning is invisible. Missing assessments can reflect data or process issues.
- Education level improved average metrics at selected checkpoints but shifted signals substantially between groups. Other inputs may still encode inequalities; the group review remains incomplete.
- Repeated inspection of 2014J makes this evaluation exploratory. An independent temporal and external test, analysis of false alerts, and assessment of possible unequal impact are still needed.
- High precision establishes neither a causal explanation nor a benefit from outreach. Real use requires carefully designed support, privacy review, and evaluation in the institution's context.

An initial usability test found small type and a confusing layout in places; its participant expected to open a course by clicking its table row and did not understand the label for due assessments without recorded completion. After the interface changes, another test should cover the entry point, full roster, terminology, example states, and management view. Testing with adult-education coaches would help assess fit with their actual work. An early optional neutral message followed by later personal review is an **untested hypothesis**: OULAD cannot demonstrate its effect or time savings. When features, target, models, or demo data change, review `project_context.py`, this README, and the historical metrics in the app together.

## Source

Kuzilek, J., Hlosta, M. & Zdrahal, Z. (2017): [Open University Learning Analytics dataset](https://doi.org/10.1038/sdata.2017.171). *Scientific Data*, 4, 170171. Dataset licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
