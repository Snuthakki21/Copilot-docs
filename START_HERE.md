# Mainframe Modernization Workbench

A local React interface and persistent Python workflow for source analysis, one SME review, synthetic testing, full source coverage and editable PowerPoint reporting. The executable converter supports a bounded flat COBOL record profile. Unsupported behavior remains blocked; arbitrary application conversion and observed mainframe parity are not claimed.

## Set up once

Use CPython 3.12. On Windows run `./scripts/Setup.ps1`, then `./scripts/Start.ps1` in PowerShell. Open http://127.0.0.1:8765. On Linux/macOS run `bash scripts/setup.sh`, then `.venv/bin/python -m workbench`. Setup installs all 21 exact Python dependencies from a SHA256-verified lock using wheels, checks command failures, and reuses a compatible environment. The committed React bundle needs no Node installation.

Uvicorn serves only 127.0.0.1. Keep the workspace on local disk; one Coordinator owns it at a time. Stop the UI before using the CLI on the same workspace. Ctrl+C and restart preserve state, quota and evidence. Windows wheel availability is verified; native Windows/PowerShell execution remains untested here.

Run `python -m workbench.preflight --workspace WORKSPACE --manifest MANIFEST --json`
in the configured environment, or use **Setup → Run local preflight** in the UI.
Local readiness, conversion support and live connectivity are separate results.
[docs/OPERATIONS.md](docs/OPERATIONS.md) lists every required setup input, the
failure/recovery matrix and the acceptance checklist.

## Start a process

1. Put the complete UTF-8 text export in **`Endeavor/`**, or select source files in the UI. Local exports retain relative filenames and exact bytes. Every supplied text file is inventoried, including unknown extensions, with explicit scope/reasons.
2. Supply a job/step Markdown manifest following **`examples/process-input.md`**, or the editable **Excel intake template** available in the UI and at `examples/intake-template.xlsx`. It records ordered jobs/steps, programs, input/output groups and conditions. Use a stable process ID.
3. Click **Start process**. Analysis, provisional target generation and the single SME packet are automatic. The timeline and **Source coverage** tab show actual stages, every original line, target spans, witnesses, omissions and reasons.
4. Download `sme-checklist.xlsx` for the actual SMEs. They select Yes, No or Not sure and supply corrections/reviewer attribution. Preserve the questions, Metadata and Context. Import that one returned workbook under **SME review**. Agents may not supply answers.
5. Verification, per-rule adversarial mutations, knowledge updates and the management PPT continue automatically. Pause/Resume/Cancel use durable checkpoints. Transient stage failures receive at most three attempts; permanent failures retain a named blocker.
6. Download **Tests & reports** artifacts: coverage JSON/CSV/XLSX/HTML, current/portfolio metrics and history, synthetic comparisons, target SQLite and the editable six-slide `management.pptx`. `COMPLETED_WITH_BLOCKERS` records unresolved work, not successful parity.

Expected results come from source behavior and are frozen before Python execution. Conversion credit requires intact intake, source, target, actual human return and reproducible verification/adversarial evidence. Unsupported code is not excused as mainframe-specific without a verified replacement. Line accountability, applicable line verification and semantic units have separate denominators.

## One prompt for Copilot or Claude Code

`AGENTS.md`, `CLAUDE.md` and `.github/copilot-instructions.md` reference **[prompts/START_MODERNIZATION.md](prompts/START_MODERNIZATION.md)**. Give that prompt, the manifest path and workspace path to the agent. It executes the existing engine:

```sh
python -m workbench.runner run --manifest MANIFEST --workspace WORKSPACE
```

The command returns the single packet and waits for the genuine reviewer. Place the completed workbook at `WORKSPACE/processes/PROCESS_ID/input/sme-return-inbox.xlsx`, then continue with actual attribution:

```sh
python -m workbench.runner resume PROCESS_ID --workspace WORKSPACE --reviewer "ACTUAL REVIEWER"
python -m workbench.runner bundle PROCESS_ID --workspace WORKSPACE
```

An operator who already knows the reviewer can use `--watch --reviewer "ACTUAL REVIEWER" --timeout 3600` to wait for the inbox and continue automatically. Waiting is bounded; timeout preserves evidence and needs a later Resume. Repeated Start reuses identical frozen intake; changed input requires a new process ID. Bundle collects source, target, review, synthetic data, comparisons, coverage and PPT in an immutable ZIP.

Folder checks run in the CLI and core workflow, including UI operations. Agents must run `python -m workbench.layout --workspace WORKSPACE` before and after work and follow **[docs/WORKSPACE_LAYOUT.md](docs/WORKSPACE_LAYOUT.md)**. Output cannot be scattered at root or generated as Markdown per rule. Frozen evidence is never reorganized in place.

## Connections and knowledge

Set private environment variables before launch; `.env.example` is a template, not automatically loaded. Source accounts must be read-only. No legacy programs/jobs execute and no synthetic data is uploaded.

- **Zowe CLI:** authenticate it yourself and set `WB_ZOWE_PROFILE`. Typed dataset/member lists and source-member reads exist. Start records bounded catalogue discovery; transformation currently uses the supplied local snapshot. No exhaustive estate claim or guessed arbitrary member retrieval.
- **Db2 MCP:** set `WB_DB2_MCP_URL` and `WB_DB2_MCP_TOKEN`. The server needs structured typed `db2_list_schemas`, `db2_list_tables`, `db2_describe_table`, `db2_sample_rows` tools. For `tools/db2_mcp_server.py`, provision `pyodbc`/IBM ODBC driver separately and set private `WB_DB2_ODBC_CONNECTION`. Bounded schema/table traversal requires no prelisted schema/table allowlist. It records cursors and complete/partial evidence; no arbitrary SQL or automatic business-data sampling. Supported negotiated protocols: 2025-06-18 and 2025-03-26.
- **LLM:** configure an approved OpenAI-compatible chat-completions URL/model/token with `WB_LLM_URL`, `WB_LLM_MODEL`, `WB_LLM_TOKEN`. Explicit `WB_ALLOW_SOURCE_EGRESS=true` permits up to 16 KB of source/background excerpts. Validated suggestions enter the one checklist and usage is recorded. Suggestions cannot replace source rules or execute commands. Deterministic conversion works without an LLM.

No live source/provider connection is certified here. Discovered database schemas are not automatically imported as synthetic fixture contracts. Configuration is not connectivity.

Put Devin/background articles in **`knowledge/inbox/context.md`**, maximum 16 KB; frozen content is unverified background. Confirmed source/version/reviewer-bound facts accumulate in **`knowledge/records.json`** and one **`knowledge/INDEX.md`**. Past answers do not approve changed source automatically.

Use the **Knowledge** tab to inspect mainframe file classifications, utility
behavior, risks and required evidence. Standard knowledge lives in
**[knowledge/mainframe-catalog.json](knowledge/mainframe-catalog.json)** with its
plain-language **[guide](knowledge/README.md)**. Add application/vendor utility
facts to **`WORKSPACE/knowledge/application-knowledge.json`**; setup initializes
it from **[examples/application-knowledge.json](examples/application-knowledge.json)**.
Each new process freezes that knowledge in `analysis/mainframe-knowledge.json`.
Recognition does not grant conversion support; unknown files and missing
utility adapters stay blocked and enter the one SME review.

Each process has `input/`, `analysis/`, `review/`, `synthetic/`, `target/`, `reports/` and `tests/`. Shared programs use `shared/target/python/HASH.py`. Back up the entire workspace; do not edit ledger/hashes/snapshots. Source, credentials and runtime evidence remain ignored by git. See the folder contract for exact filenames.

## Examples and development

**Run fictional example** exercises the real worker and requires its review return. UI demos are excluded from production totals. `PYTHONPATH=. python tools/demo_e2e.py --root NEW_TEST_WORKSPACE` runs two fictional processes, 256 cases each, with automatic Yes **test fixtures only**. They are never real SME approval.

Standalone generator: `PYTHONPATH=. python tools/synthetic_cases.py --source examples/Endeavor/ELIGIBLE.cbl --copybooks examples/Endeavor --output NEW_CASES.json`. UI development: Node 22+, `npm ci` in `frontend/`, then `npm run typecheck` and `npm run build`.

[docs/MIGRATION_CONTRACT.md](docs/MIGRATION_CONTRACT.md) defines supported behavior, metrics and remaining adapters. [docs/MASTER_PROMPT.md](docs/MASTER_PROMPT.md) is the full extension/design contract, not a competing workflow. [VALIDATION.md](VALIDATION.md) records actual checks and residual limits.

[docs/THIRTY_PASS_REVIEW.md](docs/THIRTY_PASS_REVIEW.md) records the 30-area
adversarial review, reproduced fixes, repeatable checks and acceptance limits.
