# Reproduce the LearnerCue analysis

The public app can run with the committed models and synthetic sample. Rebuilding
the historical analysis additionally requires the original OULAD CSVs, stored
locally. The saved notebook outputs describe earlier OULAD runs; execute the
notebooks to obtain results for your own copy of the data.

## 1. Prepare the environment and inputs

From a fresh clone:

```sh
git clone https://github.com/TonyWillert/FWS_Project.git
cd FWS_Project
uv sync --locked
uv run python -c "from portfolio_projekt.paths import projektwurzel; print(projektwurzel())"
```

The project specifies Python 3.14 and commits `uv.lock`. Select the Python
interpreter in this clone's `.venv` as the notebook kernel. `uv sync` installs
the project package in editable mode; its path helper locates this clone even
when a notebook starts from a subdirectory or an unrelated working directory.
After switching clones, select the environment belonging to the new clone.

Download OULAD from the [official dataset page](https://research.stem.open.ac.uk/ouanalyse/dataset/)
and place these unpacked CSVs directly in `Daten OULAD/` inside the clone:

| CSV | Used for |
| --- | --- |
| `studentInfo.csv` | Course entries, later outcomes, and descriptive attributes |
| `studentRegistration.csv` | Registration and withdrawal dates |
| `courses.csv` | Course duration |
| `assessments.csv` | Assessment plans and course assignment |
| `studentAssessment.csv` | Submission dates and transferred credits |
| `studentVle.csv` | Platform click records, read in chunks |

The download also includes `vle.csv`, describing platform materials; the minimal
model-export route below does not read that table. Raw data and generated
`data/` files are excluded from Git. A clone alone therefore does not contain
the historical analysis inputs.

## 2. Rebuild the current weekly models

Use **Restart kernel, then run all cells** for each notebook in this order.
Each notebook receives a fresh kernel; the CSVs carry data between notebooks.

| Order | Notebook | Input | Output |
| --- | --- | --- | --- |
| 1 | `01_datensichtung.ipynb` | The six raw tables above | Three day-14 bases and `data/processed/oulad_tag28_modellbasis.csv` |
| 2 | `08_zeitfenster.ipynb` | Raw tables and the day-28 basis for its click-count consistency check | Both weekly bases listed below |
| 3 | `11_wochenmodelle_export.ipynb` | Both weekly bases and `studentInfo.csv` | Sixteen weekly model files, schema, and historical demo CSV |

Notebook 08 writes:

- `data/processed/oulad_wochenmodellbasis.csv`: the earlier selection of
  checkpoints, including days after 111.
- `data/processed/oulad_wochenmodellbasis_tag6_bis111.csv`: all sixteen weekly
  checkpoints from day 6 through day 111.

Notebook 11 uses the second file for training and the first file as an
additional source of earlier enrolments when excluding overlapping people from
2014J. **Both are required.** It creates:

- `models/oulad_wochen/tag_006.joblib` through `tag_111.joblib` at seven-day intervals;
- `models/oulad_wochen/schema.json`;
- `data/demo/oulad_wochen_2014j.csv`, without the target or `final_result`.

Run the export on a working branch: notebook 11 writes the model files and
schema that are tracked in Git. Review regenerated artifacts before committing
them. The path update itself retains the previously exported models and results.

## 3. Reproduce the development comparisons

The other notebooks explain and evaluate the development path. They are not
prerequisites for training the current weekly exports.

| Notebooks | Dependency and purpose |
| --- | --- |
| `02`–`04` | The day-14 bases from `01`; early model comparisons and assessment |
| `05` | The day-28 basis from `01`; model comparisons, earlier model export, and day-28 demo |
| `06`–`07` | The day-28 basis from `01`; temporal and separate-outcome investigations |
| `09` | Both weekly bases from `08` and raw outcome/registration tables; weekly comparisons and temporal evaluation |
| `10` | The day-6-to-111 basis and `studentInfo.csv`; education-group investigation |
| `12` | The day-6-to-111 basis and `studentInfo.csv`; extra-feature comparisons |

Run a notebook's dependencies first, then execute that notebook with a fresh
kernel. Running all numbered notebooks in order also follows these dependencies.
Notebook 05 writes the older day-28 artifacts; notebook 11 writes the current
weekly artifacts.

## 4. Compare with the recorded OULAD run

These are the reference counts already reported by the project, rather than
expectations for a reduced or synthetic test dataset:

| Item | Recorded count |
| --- | ---: |
| Day-28 model basis from `01` | 27,422 course entries |
| Day-6-to-111 weekly basis from `08` | 423,510 rows, 13 columns |
| Weekly training snapshots from `11` | 282,519 |
| People excluded from the 2014J demo | 1,403 |
| 2014J demo snapshots | 121,447 |
| Distinct course entries in that demo | 8,682 |

If counts differ, check the raw inputs, notebook order, and selected environment
before interpreting model metrics. A successful run does not turn the
exploratory 2014J evaluation into an untouched test or establish intervention
effectiveness.

Finally run `uv run streamlit run app.py` from the project directory. Open the
guided synthetic example, or upload the locally generated historical demo CSV
for a research walkthrough. The historical CSV remains local; the public app
continues to use the committed synthetic sample.
