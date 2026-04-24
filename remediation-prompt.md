# Synthetic Data Generator Remediation Prompt (GPT-4.1 tuned)

**Paste this entire file as a single message into GitHub Copilot Chat after `.github/copilot-instructions.md` is in place. Model MUST be GPT-4.1.**

---

## TASK (autonomous run — DO NOT yield until Output Contract is emitted)

You are an autonomous remediation agent. Your turn ends ONLY when every row #1–#35 has `PASS|FIXED|FAIL` with a cited test id AND every GATE 1–21 has run AND the final Output Contract is emitted. Nothing short of that counts as done.

You have tools: read files, write files, run terminal commands. USE THEM. Every fact about the codebase, the xlsx, or the PDF MUST come from a fresh tool call in THIS session.

**Forbidden phrases in your output** (if you catch yourself writing one, STOP and do the action instead):

- "I would…" → do it instead.
- "The user should…" → you do it.
- "I'll continue when you…" → keep going now.
- "Based on typical Flask apps…" → read the actual `app.py`.
- "The rules file likely contains…" → open the xlsx with the file-read tool.
- "Assuming the coverage threshold is 65%…" → open the PDF; fallback to 65% ONLY after confirming silence, and log the fallback.
- `[PASS]` without a green `pytest` line executed in THIS session → write `[FAIL]` instead.

Follow the 8-step protocol below for every non-trivial action. Any claim without the protocol is a hallucination and MUST be rejected by you. A PASS without a cited test id is a hallucination.

---

## 8-STEP PROTOCOL — EXECUTE IN ORDER, NO SKIPS

1. **OBSERVE** — State in one sentence what you are about to do.
2. **CITE** — State the source anchor `(file, tab_or_page, row_or_line)`. If the anchor does not exist in sources 1–3, you MUST emit `SOURCE_MISSING: <what>` and SKIP this item. DO NOT invent an anchor.
3. **VERIFY** — You MUST call the file-read tool NOW and quote the supporting text/headers/cells. DO NOT recite from memory. If the source does not say what you expected, correct or abort.
4. **REASON** — State premise → premise → conclusion in 2–3 short lines.
5. **TEST-FIRST** — You MUST write a failing test BEFORE editing production code. Id: `test_req_<n>_*`, `test_nfr_<n>_*`, or `test_bug_<short>_*`. Run it; confirm RED.
6. **ACT** — Perform the edit. No scope creep. No "while I'm here" refactoring of unrelated code.
7. **TEST-RUN** — You MUST execute `pytest` (or equivalent) for the new test plus the full suite. Paste the exit code and the test id line from the output. If RED, loop to REASON (max 3 attempts; then FAIL the row).
8. **VERIFY** — Re-read the edited artifact via the file-read tool AND confirm the test id appears in the green output. If either fails, revert and retry. DO NOT proceed to the next row until this step returns true.

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

## NON-NEGOTIABLE EXECUTION RULES (read before starting PHASE 3A)

- You WILL iterate all 35 rows. You WILL NOT stop at row 10 and summarize. You WILL NOT stop at row 20 and ask if you should continue.
- You WILL run all 21 gates after the rows.
- You WILL emit the Output Contract as the final message.
- Every 5 rows, you MAY emit a single progress marker line: `PROGRESS: row <n>/35`. This is NOT the final report. Continue immediately.
- If a row consumes 3 attempts without a green test, mark `[FAIL] #<n> — <file:line> — <next action>` and move to the next row. DO NOT stall.
- If a tool call returns an error, fix the call and retry. DO NOT fall back to guessing.

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

## CLOSING MANDATE — RE-READ BEFORE EMITTING ANYTHING

- Functional `[PASS]` requires a green `test_req_<n>_*` line from a `pytest` run executed in THIS session.
- NFR `[PASS]` requires a green `test_nfr_<n>_*` line from a `pytest` run executed in THIS session.
- Bug `[REGRESSION-GREEN]` requires a green `test_bug_<short>_*` line from a `pytest` run executed in THIS session.
- No green line → the row is `[FAIL]`. There is no third option.
- No final report before all 35 rows + 21 gates are attempted. Progress markers are NOT the final report.
- The final report follows the Output Contract from `.github/copilot-instructions.md` exactly. No prose, no preamble, no congratulations, no emojis, no "let me know if…".

If you are about to claim a row `[PASS]` without a green test id from THIS session — **STOP**. Either write the test and run it green, or mark `[FAIL]`. Evidence or nothing.
