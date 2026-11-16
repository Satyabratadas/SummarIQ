# SummarIQ — Project Plan

Status: planning. This document describes where the project stands today, what is
wrong with it, and the plan to turn it from a course prototype into a tool that
researchers would actually use.

---

## 1. The problem worth solving

A researcher triaging papers has a PDF (or an arXiv link), not a `.tex` file. They
want to know in two minutes: what is claimed, how it was done, what the key
equations mean, and whether the paper is worth a full read. They also need to
trust the answer, which means every statement in the summary must be traceable
back to a passage in the paper.

**Product goal:** give SummarIQ a PDF or an arXiv ID and get back a structured,
source-grounded summary with the key equations rendered and explained.

What makes this more than a generic "chat with PDF" tool:

- Math-aware: equations are extracted as LaTeX, ranked, rendered and explained
  with their symbols defined. Most summarizers drop or garble math.
- Grounded: each summary point links to the section/paragraph it came from.
- Measured: quality is tracked on a fixed evaluation set, not judged by eye.

## 2. Where the project stands today

Pipeline: `.tex` upload → regex extraction → regex cleaning → T5-small (hosted on
a Kaggle notebook behind ngrok) → JSON → Gradio UI. Prometheus + Grafana for
metrics.

### 2.1 Product gaps

| Gap | Detail |
|---|---|
| LaTeX only | `/summarize-latex` accepts a single `.tex` file. The README advertises PDF support, but the only PDF code (`src/extractor/extract_usingcv.py`) is an unused script that crops contours with OpenCV and produces no LaTeX. |
| Single-file LaTeX only | `\input`/`\include` are not followed, so multi-file arXiv sources (the common case) lose most of their content. |
| Inference is not deployable | `SummarizerRemote` calls a hard-coded ngrok URL that only works while a Kaggle notebook is running. |

### 2.2 Quality problems (why the summaries are weak)

1. **The served model is stock `t5-small`.** The fine-tuned BART from
   `Notebooks/bart_train.ipynb` is never served. T5-small is not an instruction
   model, so the long prompts are echoed back into the output, which is why
   `strip_prompt_artifacts` exists with 20+ regexes. Leaked prompt text is still
   visible in `src/utils/response_server/api_response.json`.
2. **`clean_text` destroys the meaning.** It deletes all math, every
   parenthetical, every single-letter word and all non-ASCII characters. The
   model receives sentences like "Let be complex projective variety and its
   rational endomorphism" — the subject of the sentence is gone before
   summarization starts.
3. **Chunking does not summarize.** Sections are split into blind 180-word
   chunks, each chunk is summarized independently and the results are
   concatenated. There is no cross-chunk context and little real compression.
   Abstract input is truncated at 512 tokens.
4. **Equation ranking is fitted to one paper.** `score_equation` rewards
   literal symbols such as `I_f` and `K_X`. The extractor keeps only the first
   10 matches, counts every inline `$x$` as an equation, and misses `align*`,
   `equation*`, `gather`, `multline`.
5. **Extraction is fragile regex.** Nested braces in `\title{}`, comments,
   custom macros, `\subsection`, and papers without `\section` are not handled.

### 2.3 Evaluation problems

- The only numbers (ROUGE-1 39.0 / ROUGE-2 15.7 / ROUGE-L 24.2, 300 validation
  papers from `ccdv/arxiv-summarization`) belong to a BART-base run that is not
  the deployed model, and they measure abstract generation, not the
  section-wise output the product returns.
- No measurement of extraction quality, faithfulness, or equation selection.
- `summariq_prediction_confidence` is hard-coded to `1.0`.
- The SHAP/Fairlearn notebook uses a tree explainer on a different model; it
  says nothing about the summarizer.

### 2.4 Engineering problems

- **A live ngrok auth token is committed** in `Notebooks/kaggle_server_run.ipynb`.
  It must be revoked in the ngrok dashboard; removing it from the file is not
  enough because it stays in git history.
- `alert_rules.yml` is never mounted into the Prometheus container, so no alert
  can fire.
- The Docker image installs torch, transformers and a full TeX Live even though
  inference is remote; `requirements.txt` is not used by the Dockerfile and is
  missing `prometheus_client`; `requirements_projects.txt` contains
  TensorFlow-macOS but not torch/transformers.
- Imports only work because of how `PYTHONPATH` and the working directory happen
  to line up (`app:app` vs `src.models...`).
- No tests, no CI, no config management, no upload size/type validation, no
  request timeouts, bare `except`, CORS `*` with credentials.
- `summarizer_local.py` and `summarizer_remote.py` are ~230 duplicated lines.
- Feedback comments are counted in Prometheus and then discarded.
- User-supplied LaTeX is compiled with `pdflatex` on the server.
- `__pycache__/` and sample PDFs are tracked in git.

## 3. Target design

```
 PDF upload ─┐
 arXiv ID  ──┼─► Ingest router ─► Paper (one canonical schema) ─► Summarize ─► Verify ─► API / UI
 .tex / zip ─┘        │                     │                        │           │
                      │                     └─► Equation rank+explain            └─► Store + cache
                      └─ arXiv ID: use LaTeX source when it exists, else the PDF
```

### 3.1 Ingestion — three inputs, one schema

- **arXiv ID / URL (new, highest value).** Download the e-print source. When
  LaTeX is available, parse it — this is the most accurate path and reuses the
  existing strength of the project. Fall back to the PDF otherwise.
- **PDF (new).** Use a document-layout model that outputs section structure and
  formulas as LaTeX. Candidates to benchmark on our own data before choosing:
  Docling, Marker, MinerU, Nougat (formulas), GROBID (metadata, references,
  section tree). Check licences before committing to one; several are
  copyleft or restrict commercial use.
- **LaTeX (improve).** Accept a `.zip`/`.tar.gz` project, resolve `\input`,
  strip comments, expand simple `\newcommand` macros, and replace the regexes
  with a real parser (`pylatexenc` or `TexSoup`, or LaTeXML for hard cases).

All three produce the same `Paper` object (pydantic): metadata, a section tree
of paragraphs with stable IDs, equations with label, surrounding context and
reference count, plus figure/table captions and the bibliography. Everything
downstream depends only on this schema.

### 3.2 Summarization

- A `Summarizer` interface with interchangeable backends:
  - **LLM backend (default):** a hosted LLM API, or a self-hosted open model
    behind an OpenAI-compatible server. This is the only option that handles
    full-paper context and math-heavy text well enough for real users.
  - **Seq2seq backend (baseline):** a long-input model (LED / LongT5 /
    PEGASUS-X) fine-tuned on `ccdv/arxiv-summarization`, kept as a measured,
    cheap, offline baseline. Replaces T5-small and the ngrok tunnel.
- Keep the math in the text. Stop deleting it; pass LaTeX through.
- Section-aware map-reduce: summarize each section with the abstract as shared
  context, then compose the final structured output — TL;DR, problem,
  contributions, method, results, limitations.
- Structured JSON output validated against a schema; each point carries the
  paragraph IDs that support it.

### 3.3 Equations

- Candidates are display equations only. Rank by: has a label, number of
  `\ref`/`\eqref` mentions, appears in a definition/theorem/method section,
  position, and whether it is cited in the abstract-level summary.
- Explain each selected equation from its surrounding paragraph: what it
  states and what each symbol means.
- Render in the browser with KaTeX/MathJax. This removes server-side
  `pdflatex`, ImageMagick and about a gigabyte of TeX Live from the image, and
  closes the untrusted-LaTeX compilation risk.

### 3.4 Verification

- Check every summary sentence against its cited paragraphs with an
  entailment/faithfulness scorer; drop or flag unsupported sentences.
- Expose a real confidence value from that score and remove the constant gauge.

### 3.5 Serving

- Parsing plus summarizing takes tens of seconds, so the API becomes
  asynchronous: `POST /papers` returns a job ID, `GET /papers/{id}` returns
  status and result. Start with a simple worker and move to Redis + a task
  queue when needed.
- Cache by content hash / arXiv ID + pipeline version so a paper is processed
  once.
- Postgres (SQLite for local dev) for papers, summaries and feedback, with
  feedback tied to the exact summary and pipeline version it rated.
- Upload limits, content-type checks, timeouts and retries on outbound calls,
  API key auth and rate limiting, restricted CORS, structured logs.
- Config through environment variables (`pydantic-settings`); no URLs, paths
  or secrets in code.

## 4. Data

Local data lives outside the repository and stays there. The code finds it
through `SUMMARIQ_DATA_DIR`.

| Folder | Contents | Size |
|---|---|---|
| `Training_pdf/` | 361 arXiv PDFs | ~707 MB |
| `Traning_latex_files/` | 59 arXiv source directories (multi-file LaTeX) | ~69 MB |
| `Test_pdf/` | 9 mixed `.pdf` / `.tex` files | ~1.6 MB |

Facts that shape how it can be used:

- The PDF set and the LaTeX set share **no** arXiv IDs.
- The collection is small and skewed towards algebraic geometry.
- There are no reference summaries other than each paper's own abstract.

So this data is not a training set for a summarizer. It is the right raw
material for an **evaluation set**, which the project currently lacks:

1. **Pair it up.** For every arXiv ID, fetch the missing counterpart so each
   paper has both PDF and LaTeX source (extend `src/utils/load_data.py`).
   LaTeX then acts as ground truth for the PDF parser: section titles, section
   text and equations can be scored automatically.
2. **Broaden it.** Add ~40 papers per category across cs.LG, cs.CV, cs.CL,
   stat.ML, physics and math so results are not specific to one field.
3. **Freeze splits.** `dev` for iteration and `test` touched only for reported
   numbers. Commit a manifest (arXiv ID, version, checksum, category, split) —
   never the files — so anyone can rebuild the set with one script.
4. **Golden subset.** 30–50 papers with a hand-checked summary rubric and
   hand-picked key equations, for the metrics that cannot be automated.

For fine-tuning the seq2seq baseline, keep using `ccdv/arxiv-summarization`.

## 5. Evaluation

A single command (`python -m summariq.eval ...`) produces one report per
pipeline version.

| Stage | Metric | Reference |
|---|---|---|
| PDF parsing | section-title F1, text similarity per section | paired LaTeX |
| Equation extraction | recall of display equations, normalized edit distance | paired LaTeX |
| Equation ranking | precision@5 | golden subset |
| Summary content | ROUGE-L, BERTScore vs abstract | abstract |
| Summary faithfulness | share of sentences supported by cited passages | source paper |
| Summary usefulness | 1–5 rubric: coverage, correctness, clarity | golden subset |
| System | p50/p95 latency per stage, cost per paper, failure rate | — |

Results are reported per arXiv category and per paper length. That slice
analysis replaces the current fairness notebook with something that actually
describes this system. A small smoke subset runs in CI to catch regressions.

## 6. Repository layout (target)

```
summariq/
  config.py            settings from environment
  schema.py            Paper, Section, Equation, Summary
  ingest/              router.py, arxiv.py, latex/, pdf/
  summarize/           base.py, llm.py, seq2seq.py, pipeline.py, prompts/
  equations/           rank.py, explain.py
  verify/              faithfulness.py
  eval/                datasets.py, metrics.py, run.py
  api/                 main.py, routes/, jobs.py, storage.py, metrics.py
ui/                    Gradio app (web front end later)
scripts/               fetch_arxiv.py, build_manifest.py
tests/                 unit + fixtures (a few tiny .tex / .pdf samples)
deploy/                Dockerfile, docker-compose.yml, prometheus/, grafana/
data/                  manifest only; real data is git-ignored
notebooks/             experiments only, no outputs or secrets committed
docs/                  report, poster, architecture
pyproject.toml         one pinned dependency source, ruff + pytest config
```

## 7. Roadmap

Each phase ends with something that runs and a number that improved.

**Phase 0 — Hygiene (1–2 days)**
- Revoke the ngrok token; strip notebook outputs; add `nbstripout`.
- `.gitignore` for `__pycache__`, data, env files; remove tracked caches.
- `pyproject.toml` with pinned deps, `ruff`, `pytest`, GitHub Actions.
- Move to the package layout; delete the duplicated summarizer; settings module.
- Mount `alert_rules.yml`; remove the constant confidence gauge.
- Correct the README so it only claims what works.
- *Done when:* `docker compose up` works from a clean clone and CI is green.

**Phase 1 — Evaluation set and baseline (about a week)**
- Paired PDF + LaTeX fetch script, manifest, frozen splits.
- Eval harness with the metrics in section 5.
- Record the current pipeline's scores as the baseline to beat.
- *Done when:* one command prints the baseline table.

**Phase 2 — Ingestion (1–2 weeks)**
- `Paper` schema; proper LaTeX parser with multi-file projects.
- arXiv ID input.
- Benchmark PDF parsers on the paired set; integrate the winner.
- *Done when:* PDF parsing reaches the agreed section-F1 and equation-recall
  targets on `dev`, and all three inputs return the same schema.

**Phase 3 — Summary quality (1–2 weeks)**
- `Summarizer` interface, LLM backend, long-input seq2seq baseline.
- Section-aware pipeline with structured, cited output.
- New equation ranking and explanations; faithfulness check.
- *Done when:* faithfulness and rubric scores clearly beat the Phase 1 baseline
  on `test`, with a comparison table across backends.

**Phase 4 — Production serving (1–2 weeks)**
- Async jobs, caching, database, feedback storage.
- Auth, rate limits, upload validation, timeouts.
- Slim multi-stage image, health checks, per-stage metrics and cost tracking,
  dashboards and alerts that reflect them.
- Deploy to one cloud target with a public demo URL.
- *Done when:* a stranger can submit an arXiv ID on the hosted demo and get a
  result, and a failed job is visible on the dashboard.

**Phase 5 — Product polish**
- Side-by-side reader: summary on the left, source passage highlighted on click.
- Export to Markdown / BibTeX note; shareable result links.
- Multi-paper comparison and "what is new versus paper X".
- Use stored feedback to pick evaluation cases and prompt changes.

## 8. Decisions still open

- Hosted LLM versus self-hosted model as the default backend (cost, privacy,
  quality). The interface in 3.2 keeps this reversible.
- Which PDF parser — decided by the Phase 2 benchmark and licence check.
- Whether the iOS prototype stays in scope; a web UI reaches users sooner.
