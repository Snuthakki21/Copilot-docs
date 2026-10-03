# Mainframe Modernization Workbench

A local React interface for a persistent, evidence-driven modernization POC. The implementation is runnable, but it deliberately supports a small COBOL execution subset. It does **not** automatically translate arbitrary mainframe applications. Read the capability boundary in `docs/MIGRATION_CONTRACT.md` before assessing a real process.

## Start on Windows

Install Python 3.12. From PowerShell in this folder, run `./scripts/Setup.ps1`, then `./scripts/Start.ps1`. Open http://127.0.0.1:8765. The committed React bundle works without Node. Stop the application with Ctrl+C in its console; restart with the same command and folder to retain state. Windows scripts are provided but have not been executed on Windows in this validation environment.

On Linux/macOS run `bash scripts/setup.sh`, then `.venv/bin/python -m workbench`. Keep the workspace on a local disk. One coordinator owns each workspace; use separate folders for separate workspaces. This is a single-user loopback tool, not an internet service.

## Use it

1. Put your complete text export in **`Endeavor/`** at the repository root, or choose its source files in the UI. The files must include the programs and copybooks for your process. The current upload picker accepts individual files; nested exports can be read automatically from local `Endeavor/` or supplied as relative paths through JSON intake.
2. Create a process with a job/step Markdown manifest following **`examples/process-input.md`**. An editable Excel template is provided at **`examples/intake-template.xlsx`**. Excel intake is also accepted: sheet `Intake`, B1 process ID, B2 process name, row 4 containing the eight exact column headers from the example, and rows 5 onward containing the steps. Source exports can be selected in the same form. IDs must be unique.
3. Click **Start**. Analysis, provisional conversion and the single SME packet are automatic. Download its XLSX and optional DOCX/HTML companion. Give the worksheet to SMEs. Each row has Yes, No, Not sure, a correction cell and reviewer name.
4. In **SME review**, enter the reviewer name and import the returned XLSX. Verification and the report continue automatically. Unanswered/uncertain/corrected items are retained as blockers when they cannot be resolved deterministically from the frozen source. No second SME questionnaire is generated.
5. Download source accounting, expected/actual case evidence, the target SQLite file and the **management.pptx** from **Tests & reports**. `COMPLETED_WITH_BLOCKERS` means the bounded run and report finished with unresolved work; it is not a parity certification.

Try **Run fictional example** for a real local execution of the included source, not a simulated timeline. The example still requires its returned review file. Demonstrations are excluded from production portfolio totals. `PYTHONPATH=. python tools/demo_e2e.py --root /path/to/new/test-workspace` performs two fictional fixture workflows and checks shared-program counts; its automatic Yes answers are **test fixtures only**, never real SME approval.

## Connections

Set private environment variables **before** starting; `.env.example` is a template, not automatically loaded. Do not commit credentials. The app never uploads synthetic data or executes anything on the mainframe.

* **Zowe CLI:** install and authenticate Zowe yourself with a read-only account. Set `WB_ZOWE_PROFILE` to an existing base profile. Typed list datasets, list members and read member adapters are available. Start performs bounded catalog discovery. It does not guess and fetch arbitrary production members; required process source must currently be in the exported snapshot. CLI behavior on your installed version must be verified in your environment.
* **Db2 MCP:** set `WB_DB2_MCP_URL` and `WB_DB2_MCP_TOKEN`. It must expose `db2_list_schemas`, `db2_list_tables`, `db2_describe_table`, `db2_sample_rows` with structured responses. For a compatible gateway, install `pyodbc` and the IBM ODBC driver, set the private `WB_DB2_ODBC_CONNECTION`, and run `python tools/db2_mcp_server.py`. Discovery needs no prelisted schema/table allowlist. Reads use fixed parameterized catalog SQL, bounded rows and a read-only account. Current Start records the first catalog page and labels the result partial; automatically traversing an entire estate and importing its schemas into fixture contracts is future work. No live mainframe or Db2 connection has been validated here.
* **LLM:** configure an approved OpenAI-compatible **chat completions** URL, model and token using `WB_LLM_URL`, `WB_LLM_MODEL`, `WB_LLM_TOKEN`. Set `WB_ALLOW_SOURCE_EGRESS=true` only when your source may be sent to that endpoint. Analysis sends at most 16 KB of excerpts/background, receives bounded structured suggestions and records reported usage. These suggestions enter the one SME checklist; they cannot overwrite source rules, issue tool commands or execute arbitrary code. Without an LLM the deterministic supported POC still runs. No live provider request was made during validation; local protocol fixtures were used.

## Where to put knowledge

Put your Devin/background articles in **`knowledge/inbox/context.md`** (maximum 16 KB). Start freezes its hash and includes it in the review context as unverified background. The LLM can use it when explicitly configured for source egress. Source-confirmed rule knowledge accumulates in **`knowledge/records.json`** and a single **`knowledge/INDEX.md`**, with reviewer and source-version provenance. It does not silently turn past SME answers into approval for a changed program. Automatic cross-process semantic inference is not implemented.

## Output structure

```
Endeavor/                              # your exported source (private)
knowledge/inbox/context.md             # your supplied articles (private)
knowledge/{records.json,INDEX.md}       # compact reviewed knowledge (private)
.migration/ledger.sqlite               # process state, quota, events, history
shared/target/python/<sha256>.py        # immutable reused target versions
processes/<process-id>/
  input/{process-input.md,sources/,sme-return.xlsx}
  analysis/source-analysis.json
  review/{packet.json,sme-checklist.xlsx,sme-checklist.docx,sme-checklist.html}
  synthetic/run-NNNN/<program>/{expected.json,actual-and-comparison.json}
  target/run-NNNN/{target.sqlite,jobs.py,job-comparison.json}
  reports/report-NNNN/{metrics.json,metrics.csv,metrics.xlsx,management.pptx,inspection.json}
```

All generated evidence is local and excluded from git. Copy or back up the entire workspace to retain evidence; do not edit ledger/source/target hashes in place. The final shared Python artifact is in the local `shared/target/python/` directory; the UI currently exposes registered per-process artifacts, not arbitrary filesystem reads.

The standalone source-grounded script is `PYTHONPATH=. python tools/synthetic_cases.py --source examples/Endeavor/ELIGIBLE.cbl --copybooks examples/Endeavor --output /path/to/new/cases.json`. Expectations are calculated from supported source predicates and layouts before target execution.

To edit the UI, install Node 22+, run `npm ci` inside `frontend/`, then `npm run typecheck` and `npm run build`. The package lock pins frontend versions; offline validation used integrity-checked cached packages. Python direct versions are pinned to the tested compatibility baseline. Upgrade/retest dependencies and perform your organization's security review before broader deployment.
