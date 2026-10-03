# Mainframe workbench implementation plan

> For agentic workers: use Superpowers executing-plans to implement this plan inline. The user has authorized implementation and new-branch publication.

**Goal:** Deliver a locally runnable modernization POC with a clean GitHub branch, persistent workflow, one SME exchange, source-derived synthetic testing, metrics and editable PowerPoint.

**Architecture:** A React/TypeScript operator UI talks to FastAPI on loopback. One coordinator owns process state and SQLite ledger writes. Deterministic source analysis, conversion, fixtures and reports run from versioned evidence. Configured read-only connectors and an optional structured LLM enrich analysis without granting general shell authority.

**Tech stack:** Python 3.12+, FastAPI, SQLite, React/TypeScript, openpyxl, python-docx, python-pptx, Pillow. Exact tested versions recorded in VALIDATION.md and dependency files.

**Spec:** MASTER_PROMPT.md. The latest user instruction authorizes publishing to a new branch in Snuthakki21/Copilot-docs with only prompt-related files. Existing branches remain untouched. Inline research replaces the inaccessible external Deep Research session.

## Global constraints

- Mainframe access is read-only: no job submission, source writes or fixture uploads.
- Source-derived expectations and actual Python results have separate versions and provenance.
- Exactly one SME questionnaire/return round per process; unresolved answers produce blockers.
- Ordinary target code requires an approved execution boundary. The built-in deterministic, audited expression subset is capability constrained; arbitrary LLM code is never executed by it.
- Supported source syntax has an explicit boundary and full line accounting. Unsupported constructs are never credited as verified.
- Generated-code counts exclude workbench code. Shared object totals use unions, process memberships remain separate.
- Every terminal successful/blocked process needs inspected report artifacts; report failure stays nonterminal.
- No private source/data, secrets, runtime ledger, dependencies or unrelated old repository items enter the public branch.

## Review focus

1. Malformed or hostile paths/documents and workbook identity changes must fail without overwriting evidence.
2. Pause, crash/recovery and duplicate Start/import must not repeat SME issuance or inflate accomplishments.
3. Source changes/shared versions must invalidate dependent evidence, not silently inherit passes.
4. Unknown syntax, coverage gaps, empty data and contradictory responses must retain blockers and truthful denominators.
5. Source/LLM/connector content cannot issue privileged tools or execute arbitrary target code.

### Task 1: Durable state and intake

Files: workbench/domain.py, intake.py, ledger.py, schema.sql; tests/test_foundation.py.

Interfaces: Ledger(root) owns connections and serialized writes; create_process/intake_snapshot/event/save/load/history expose JSON-safe records. parse_manifest(text) returns ordered jobs/steps and named inputs/outputs.

- [ ] Write failing tests for job/step ordering, invalid IDs/path escape, duplicate process identity, durable events and atomic SME quota.
- [ ] Run unittest, confirm missing behavior, implement validated storage/intake and SQL migrations.
- [ ] Verify the task suite and commit with progress evidence.

### Task 2: Source analysis, oracle and translation

Files: workbench/source.py, reference.py, target.py, fixtures.py; tests/test_source.py; examples/Endeavor/ and process Markdown.

Interfaces: analyze_sources(files,manifest) returns assets, source spans, field layouts, atomic rule IR, dependencies and blockers; emit_program(program) returns audited Python source; derive_contract(analysis) consumes source IR; run_source_reference and run_generated_target independently produce results.

- [ ] Write failing tests for threshold/ELSE behavior, source spans, copybooks, unknown syntax, changed source hash and deliberately incorrect target outputs.
- [ ] Implement the documented subset and correlated scenario planning; preserve unsupported behavior.
- [ ] Run source/fixture/target tests, verify expectations independently and commit.

### Task 3: One SME round and automatic continuation

Files: workbench/review.py, coordinator.py, knowledge.py; tests/test_workflow.py.

Interfaces: export_packet(process,analysis,directory) produces versioned XLSX/DOCX/HTML; import_answers validates identities against frozen packet and consumes the one round atomically; Coordinator.advance(pid) saves each stage and resumes without operator approvals.

- [ ] Test packet tampering, missing/No/Not sure answers, duplicate import, pause/cancel and restarted coordinator.
- [ ] Implement provisional analysis, one packet, returned answers, target/fixtures/comparison, bounded repair and blockers.
- [ ] Verify knowledge applicability and two-process shared reuse, then commit.

### Task 4: Read-only connections and structured LLM

Files: workbench/connectors.py, provider.py; tests/test_integrations.py; .env.example.

Interfaces: explicit typed Zowe list/read methods; Db2 catalog discovery through configured MCP read tools; provider.analyze(excerpts,policy) returns bounded validated suggestions and actual usage, never unrestricted tools.

- [ ] Test denied write operations, unapproved egress, malformed result envelopes, timeout and bounded output.
- [ ] Implement real adapter paths and separately labeled offline fixtures; record live status as unverified unless actually connected.
- [ ] Verify fixture protocol boundaries and commit.

### Task 5: Metrics and reports

Files: workbench/metrics.py, reports.py; tests/test_reports.py.

Interfaces: snapshot(process,portfolio) defines unique/membership/LOC/disposition/coverage metrics; generate_reports writes XLSX/CSV/HTML/PPTX plus evidence/inspection manifest from the same frozen snapshot.

- [ ] Test shared-object deduplication, historical scope growth, unknown denominators, PPTX content, and failed-report noncompletion.
- [ ] Generate editable tables/charts, before/after evidence and slide previews with overflow inspection.
- [ ] Verify reports for successful and blocked processes, then commit.

### Task 6: API and operator UI

Files: workbench/api.py, serve.py, __main__.py; frontend/src/App.tsx, styles.css, build.mjs, package.json, lockfile; tests/test_api.py and browser test.

Interfaces: same-origin session token and Origin/Host checks; process/intake/start/pause/resume/cancel/review/artifact/portfolio routes; React renders actual state/history/lineage and accessible forms, no fabricated progress.

- [ ] Test unauthorized mutations, process escape, current artifact access, and full HTTP user journey.
- [ ] Build React assets, connect all buttons and display empty/error/loading states.
- [ ] Verify browser flow, responsive rendering and build/type checks, then commit.

### Task 7: Release, adversarial review and clean publication

Files: START_HERE.md, VALIDATION.md, docs/MIGRATION_CONTRACT.md, docs/RESEARCH_REVIEW.md, requirements.lock, Windows scripts, release validation/manifest.

- [ ] Run end-to-end demo from fictional COBOL through SME return, local target, comparison and PPT; add a second process and verify union metrics.
- [ ] Obtain one independent whole-branch adversarial review under the executing-plans skill; fix important findings with regression evidence.
- [ ] Run final full suite/build/browser checks and document remaining live/platform/unsupported boundaries.
- [ ] Audit the publication allowlist, create a fresh GitHub tree, commit and new branch without force, and verify remote file tree/commit.

## Execution result

Implemented and verified the documented POC boundary. Full suite 30/30; TypeScript check/build passed; complete HTTP review/return/report journey passed; two fictional fixture processes each ran 256 cases with shared-version deduplication. See RELEASE_REVIEW.md for four fixed adversarial findings and deferred items; MIGRATION_CONTRACT.md identifies requirements not implemented. Browser and PowerPoint rendering gates remain unverified. Clean GitHub tree publication is the final step.
