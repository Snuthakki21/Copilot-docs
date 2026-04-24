# Synthetic Data Generator Remediation Prompt

**Paste this entire file as a single message into GitHub Copilot Chat after `.github/copilot-instructions.md` is in place.**

---

## TASK

Remediate the synthetic data generator in the current working directory to production-ready state per `.github/copilot-instructions.md`. Apply the 8-step protocol below to every non-trivial action. A claim or edit without the protocol is a hallucination and must be rejected by you. A PASS without a cited test id is a hallucination.

---

## REASONING PROTOCOL — OBSERVE → CITE → VERIFY → REASON → TEST-FIRST → ACT → TEST-RUN → VERIFY

Think in this exact 8-part structure (one short line per part where possible):

1. **OBSERVE** — what I am about to do.
2. **CITE** — source anchor as (file, tab_or_page, row_or_line). If none, emit `SOURCE_MISSING: <what>` and STOP that item.
3. **VERIFY** — read the cited source now (no memory). Quote the supporting text/headers/cells. If it does not actually say what I thought, correct or abort.
4. **REASON** — premise → premise → conclusion, deriving the concrete change.
5. **TEST-FIRST** — write a failing test that, when green, proves the change. Id: `test_req_<n>_*`, `test_nfr_<n>_*`, or `test_bug_<short>_*`. Assertions draw on values from sources 1–3.
6. **ACT** — perform exactly the edit implied. No scope creep.
7. **TEST-RUN** — run the new test plus the full suite. Capture exit code + failing tests. If new test still red, loop back to REASON (max 3 attempts; then FAIL the row).
8. **VERIFY** — re-read the edited artifact + test report. Confirm the artifact matches intent AND the test id appears in the green set. If not, revert and retry.

---

## PHASE 1 — DISCOVERY (no edits)

Apply steps 1–4 only. Produce an internal inventory mapping each responsibility to `file:line` or `MISSING`:

- Flask entry + routes
- Tachyon adapter (file upload, file delete, ingest, chat)
- Rules xlsx parser; Data Inputs parser; JSONL writers
- LangChain agent + sub-agent framework
- Decision-flow executor (PREC/POSTC/HVHS/Adverse Action + Global/Validation/Error/Traffic Cop)
- Coverage computer; Coverage Gap Fill handler
- UI: Parse, Reload Data and Rules, Coverage Gap Fill, Generate buttons; Log tab; Coverage tab
- Report writers: Synthetic CSV, Coverage HTML+CSV+JSON, Compliance HTML+CSV+JSON
- Log sink(s) that the Log tab reads from
- Existing test runner + coverage tool
- Config loader (env handling)
- Any security/observability middleware already in place

For each MISSING responsibility, choose a conventional placement in the existing layout; cite the convention.

---

## PHASE 2 — TEST SCAFFOLD (mandatory before edits)

Build fixtures and stubs:

- Pin read-only copies of `Synthetic Data Generator Rules Inputs.xlsx` and `Synthetic Data Generator Data Inputs.xlsx` under `tests/fixtures`.
- At fixture-setup time, parse the Rules xlsx and compute `expected_rule_counts` per tab → save as `expected_rule_counts.json`. NEVER hand-author rule counts.
- Extract the coverage threshold from `AI Power Synthetic Data Generation.pdf` at fixture-setup time; cache it. Record source = PDF or fallback=65%.
- Provide a Tachyon stub layer with identical method signatures for file upload, file delete, ingest, chat (VCR-style or explicit fake). Real endpoints verified only in GATE 3.
- Provide a deterministic clock + seeded RNG fixture.
- Provide a PII fixture (small held-out "real-data" CSV) for NFR-N4 data-privacy testing.
- Provide a fault-injection helper for Tachyon stubs (500 / timeout / connection refused) for NFR reliability tests.

---

## PHASE 3A — FUNCTIONAL REQUIREMENT + AUTO-FIX LOOP

Iterate rows #1–#20 in order. Apply the full 8-step protocol per row. Write the test first; run it red; implement; run it green. Max 3 attempts per row; on failure log `FAIL #n <file:line>` and continue.

| #  | CHECK | AUTO-FIX | TEST ASSERTION |
|----|-------|----------|----------------|
| 1  | One JSONL per rule tab emitted | Per-tab JSONL emitter | For each expected rule-bearing tab, JSONL exists; row count == active count in `expected_rule_counts.json` |
| 2  | Informational tabs classified + logged + skipped | Classifier requires `{rule_id, condition, action}` headers | POSTC Tables, PREC Tables, Policy Lookup Tables, Policy Exception Rank Table absent from JSONL set; present in informational log |
| 3  | Inactive rows filtered | Detect status header + inactive set | Mixed-status synthetic tab → only active rule_ids survive |
| 4  | `rule_count` invariant under record count | Parse-phase counting, cached | Parse + count; then generate N=10, 100, 1000 → count unchanged |
| 5  | Previous Tachyon uploads deleted before re-parse | Delete at top of Parse/Reload | With Tachyon fake pre-populated, Parse → delete calls precede upload calls |
| 6  | File + chat + ingest calls logged with status + duration | Logging decorator on Tachyon client | Each fake endpoint → exactly one log record with url, method, status, bytes, duration, correlation_id |
| 7  | Log tab reads from persisted sink | Unified sink | Write known record → query Log-tab handler → round-trip equality |
| 8  | RAG always enabled | Delete toggles everywhere | Grep zero live refs to `use_rag|enable_rag|rag_enabled|RAG_ENABLED`; retrieval invoked unconditionally on Generate |
| 9  | Decision-flow order from Data inputs tab | Load at startup; reject hard-coded | Mutate fixture decision-flow order → executor's observed order changes accordingly |
| 10 | Explainability columns in CSV | Extend schema + writer | Generate N=10 → all 7 columns exist and populated |
| 11 | Approved iff approve-path passed | Executor is single source of truth | For every row: `approved == all approve-path rules PASS in _rule_trace` |
| 12 | Schema fidelity to Data inputs | Build schema from tab; validate every row | Every row conforms to per-field type/length/nullability/domain from Data inputs |
| 13 | Sample rows preserved byte-for-byte | Raw read + write first | `sha256(first M rows of CSV) == sha256(sample rows in Data inputs)` |
| 14 | Deterministic with seed | Seed threaded through agents + RNGs | Two runs with seed=42 → byte-identical generated rows |
| 15 | Coverage threshold honored | Iterate until met or gap report | Measured coverage ≥ threshold OR gap report lists exact uncovered rule_ids |
| 16 | Coverage Gap Fill click writes Log tab entry | Wire click handler → unified sink | Invoke handler → query Log tab → entry with recognizable marker present |
| 17 | Flask stable (startup, 50MB upload, 1000 records) | Apply bug table | App starts; upload 50MB; Generate 1000 — zero exceptions, zero orphan threads |
| 18 | Three artifacts in all formats | Run writers unconditionally | After Generate: 7 files exist (CSV + 3×Coverage + 3×Compliance), non-empty, parse cleanly |
| 19 | No hallucinated fields | Cross-check against Data inputs | Every emitted column name appears in Data inputs; zero unknowns |
| 20 | Dead code + dead files removed (including `.md`, notebooks, scripts, fixtures, deps, env vars) | Run cleanup audit across code + tests + build + CI + Docker + Makefile + UI templates; delete every artifact with zero live refs; only `README.md` (if built/deployed), `LICENSE`, `CHANGELOG` (if published) may remain as markdown | For every file in the repo (excluding `.git` and build output): grep shows at least one live reference OR the file is in the whitelist `{README.md built, LICENSE, CHANGELOG published}`; `requirements`/`pyproject` list has no unused deps (`pip-deptree` / `deptry` clean); `.env.example` has no unused keys |

---

## PHASE 3B — NFR REQUIREMENT + AUTO-FIX LOOP

Iterate rows #21–#35 in order. Same 8-step protocol; test-id prefix `test_nfr_<n>_*`.

| #  | NFR       | CHECK | AUTO-FIX | TEST ASSERTION |
|----|-----------|-------|----------|----------------|
| 21 | PERF      | `Generate(1000)` ≤ budget (PDF or fallback 120s); `Parse(xlsx)` ≤ 30s | Profile + optimize hot path; batch RAG retrieval; avoid per-record PDF/xlsx reparse | Run `Generate(1000)` under timer; elapsed ≤ budget; `Parse(xlsx)` ≤ 30s |
| 22 | SEC-sec   | No hard-coded secrets; secrets via env | Move to env; central config loader; redact in logs | Grep for common secret patterns → zero hits; log records containing Authorization/api_key/token show REDACTED |
| 23 | SEC-inp   | Upload size capped; path traversal blocked; unknown sheets skipped | Enforce `MAX_UPLOAD_MB`; validate filenames; allowlist sheet names derived from PDF+Data inputs | Oversize upload rejected 413; filename `../x` rejected; unknown xlsx sheet logged and skipped |
| 24 | PRIVACY   | No literal PII reuse in generated data | Generate per Data inputs domain lists; forbid passthrough | Generated CSV intersected with held-out real-data fixture = ∅ |
| 25 | RELIAB    | Every network call has timeout + retries (exp backoff+jitter) | Wrap Tachyon/S3 clients; typed exceptions | Injected 500 → retried 3× with increasing waits (jitter != 0); final raise typed error |
| 26 | RESIL     | Tachyon/vector-DB outage → clear error surface; no crash | try/except around adapter; user toast + correlation_id | Fake all Tachyon endpoints down → UI returns error with correlation_id; Flask worker still alive; Reload retries |
| 27 | OBSERV    | Structured JSON logs with correlation_id + level + durations | Logger formatter + middleware | Tail log file → every record parses as JSON; every request has correlation_id; each pipeline phase has start+end with duration field |
| 28 | MAINT     | Coverage ≥ threshold; complexity ≤ 15; file ≤ 600 lines; function ≤ 80 lines | Refactor violators; lint rule | `pytest-cov` + `radon` (or equivalent) → all bounds satisfied |
| 29 | CONFIG    | No magic numbers in business logic; central config | Extract constants; config module | Lint/grep shows numeric literals (besides 0/1 idioms) only in config module; all thresholds read from env/config |
| 30 | PORTAB    | Windows + Linux compatible | pathlib; `os.sep`-free strings; no POSIX-only calls | Tests pass on Windows (required); import + lint clean on Linux (CI or container) |
| 31 | CONCUR    | No shared mutable state without a lock in request handlers | Per-request objects; locks around shared caches | Race-condition test: 10 concurrent Generate requests → no corruption of shared cache; no duplicate correlation_ids |
| 32 | RESRC     | `MAX_CONTENT_LENGTH` set; streaming for large N; RSS ≤ 1GB | Flask config; streaming writers | N=1000 peak RSS ≤ 1GB (psutil); N=10000 does not fully materialize in memory |
| 33 | ERRSURF   | UI shows correlation_id + error_code; no stack traces | Error handler strips internals for UI; full in server log | Trigger server error → UI body has correlation_id + error_code; no traceback string; server log contains full stack |
| 34 | AUDIT     | Run manifest written per Generate | Manifest writer hooked into pipeline tail | After Generate: manifest JSON exists with xlsx sha256, pdf sha256, seed, outputs[] with sha256, timestamp |
| 35 | BACKP     | Gap-fill bounded (`N_MAX_ITERATIONS`); no infinite loops | Iteration cap + gap-report fallback | Force no-progress scenario → stops at `N_MAX_ITERATIONS` and emits gap report; no loop > cap |

---

## BUG REGRESSION TABLE (apply under protocol)

| SYMPTOM | ROOT CAUSE | FIX | REGRESSION TEST |
|---------|------------|-----|-----------------|
| Rule count scales with record count | Counter inside record loop / post-gen traces / inactive not filtered | Count at parse only; `len(set(active rule_ids))` | `test_bug_rulecount_invariant` |
| Coverage < threshold | No iterate-until-met; inactive in denominator; gaps not fed back | Iterate; exclude inactive; target uncovered rule_ids | `test_bug_coverage_threshold` |
| Gap Fill no log entry | Handler logs to stdout, not Log tab sink | Point handler at unified sink | `test_bug_gapfill_logged` |
| Tachyon calls not logged | Client calls unwrapped | Decorator on file/chat/ingest | `test_bug_tachyon_logged` |
| Flask crashing | Route exceptions / blocking calls / non-threadsafe globals / unstreamed uploads / missing `MAX_CONTENT_LENGTH` / reloader + threads / dev server | Global error handler; background tasks; streamed + capped uploads; waitress on Windows | `test_bug_flask_stable` |
| Approved actually denied | Two decision sources | Executor only | `test_bug_decision_consistency` |
| RAG sometimes disabled | Toggle path exists | Delete toggles | `test_bug_rag_always_on` |

---

## TRAPS

- `rule_count` is a property of the xlsx, invariant under record count.
- Informational tabs lack `rule_id/condition/action` — log + skip.
- Status header name varies — detect by header set.
- Sample rows: first, unmodified, byte-for-byte.
- Decision-flow order lives in Data inputs, not Rules.
- RAG toggles hide in six places: env, config, query param, feature flag, UI, function defaults.
- Log tab sink and console logger may differ — unify.
- `gunicorn` does not run on Windows; use `waitress`.
- Coverage denominator excludes inactive rules.
- Two code paths can each compute approval — keep only the executor.
- Default Flask `MAX_CONTENT_LENGTH` + non-streamed read = crash.
- Seed must propagate to every sub-agent and every random/numpy call.
- Expected rule counts in tests MUST be derived from the pinned xlsx at fixture-setup time, never hand-authored.
- Secrets can hide in config defaults, test fixtures, and docstrings — grep them all.
- Retries without jitter produce thundering-herd on shared Tachyon outages — always jitter.
- JSON logs with embedded newlines break log parsers — escape or forbid.

---

## PHASE 3C — CLEANUP AUDIT (mandatory; executes after Phases 3A and 3B)

Apply the 8-step protocol to the repository as a whole. Produce an internal map of every file in the repo (excluding `.git/` and build output) and every symbol in each code file; for each artifact decide KEEP or DELETE:

**KEEP criteria** (at least one must hold):
- Imported, required, or referenced by live application code
- Imported or referenced by the live test suite
- Referenced by build config (`Makefile`, `pyproject.toml`, `package.json`, `setup.cfg`, `Dockerfile`)
- Referenced by CI (`.github/workflows`, `.gitlab-ci.yml`, etc.)
- Referenced by UI templates (`templates/`, `static/`, `assets/`)
- Whitelisted root metadata: `README.md` (only if built or deployed), `LICENSE`, `CHANGELOG` (only if CI publishes it), `.gitignore`, `.env.example` (only if loader references each key)
- Runtime asset required by Flask (e.g., `templates/*.html`, `static/*.{css,js,png}`)

**DELETE criteria** (any triggers deletion after a grep confirms zero live refs):
- Stray `.md` files: plan drafts, design notes, scratch docs, tutorials
- Orphan Jupyter notebooks (`.ipynb`), sample scripts, demos
- Commented-out code blocks and `# TODO` blocks with no issue link
- Legacy modules superseded by current implementation
- Unused fixtures, unused test helpers
- Unused dependencies in `requirements.txt` / `pyproject.toml` / `package.json` (`deptry` or equivalent)
- Unused env vars in `.env.example`
- Dead branches of `if use_rag: ... else: ...` style collapses
- Mock endpoints, stub scripts, old migration scripts no longer needed
- Empty `__init__.py` outside needed package roots

**AMBIGUOUS items**: resolve by tightening the grep (include build configs, CI, templates); if still unclear, DELETE and rely on tests (GATE 2) to expose necessary reinstates. Do not keep "just in case."

Report each deletion as `DELETED: <path:lines> — <reason>`.

---

## PHASE 4 — GATES

Run GATES 1–21 from `.github/copilot-instructions.md` in order (functional 1–10, NFR 11–20, cleanliness 21). On any failure: diagnose under the 8-step protocol, auto-fix test-first, re-run from GATE 1. Max 3 full cycles.

---

## PHASE 5 — FINAL REPORT

Emit exactly the OUTPUT CONTRACT from `.github/copilot-instructions.md`. Nothing else.

---

## FINAL REMINDER

- Functional PASS requires `test_req_<n>_*` green.
- NFR PASS requires `test_nfr_<n>_*` green.
- Bug REGRESSION-GREEN requires `test_bug_<short>_*` green.
- No green test → not done. Evidence or nothing.

If you are about to claim a row PASS without a green test id — **STOP**. Either write the test and run it green, or mark FAIL. Evidence or nothing.
