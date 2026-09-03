# Output Contract

For workbook `<input.xlsx>`, write to a single modernization root such as `modernized/`. Create one folder per distinct normalized job name:

```text
modernized/
  <JOB_NAME>/
    lineage.md
    job.py
    run.jil
    oracle.sql
    sqlite.sql
    validation_report.md
    traceability.json
    tests/
      test_job.py
    fixtures/              # only source-derived/generated test fixtures actually used
    validation.db          # generated locally when SQLite execution is performed; omit from git if large/sensitive
```

Do not create shared business-logic modules across jobs. Shared tooling belongs to the skill; generated business logic belongs to that job's `job.py`.

## Governing parity rule

The artifacts document and reproduce **observed legacy behavior**, even when that behavior is suspicious or appears incorrect. The migration must not change source logic to match a preferred interpretation, comment, business expectation, or modern best practice. Suspicious behavior is documented as an observation; it is not repaired in the migration unless source evidence itself proves the executable behavior differs.

## `lineage.md`

Required order: executive summary; source inventory; exact source commit/workbook hash; JCL step flow; program-by-program explanation; input/output datasets; DB2/table interactions; rule catalog; legacy quirks/suspicious behavior; error/restart behavior; DB2→SQLite/Oracle notes; source-to-target trace table; unresolved items. Each rule has a stable ID and source location.

When behavior looks wrong, explicitly separate:
- **Observed source behavior:** what the executable source actually does.
- **Observation:** why the behavior may look unusual or suspicious.
- **Migration action:** `PRESERVE` unless stronger source evidence proves another behavior.

Do not change logic merely because the observation identifies a likely legacy defect.

## `job.py`

One executable Python file containing all business logic for the job. Include a module-level plain-English job summary, explicit source-equivalent input/configuration handling, deterministic step orchestration, rule-ID comments, source-equivalent file handling, parameterized SQL where behaviorally equivalent, transaction boundaries matching source semantics, and source-consistent exit codes. Preserve business behavior, not COBOL syntax.

Every function must contain a plain English docstring using this compact contract:

```text
Purpose: What source business/orchestration responsibility this function mirrors.
Inputs: Each argument/input and its source business meaning or expected format.
Outputs: Return value and/or files/tables/records produced.
Side effects: Files, database state, logging, counters, checkpoints, or other state changed.
Failure behavior: Source-equivalent validation/errors/rollback/cleanup/exit implications.
Rule IDs: Source rule IDs implemented or supported by this function.
```

Docstrings must be understandable without reading COBOL first. Comments inside functions explain why non-obvious logic exists and cite Rule IDs. If a rule appears defective, comment that it is intentionally preserved from source; do not silently correct it. Function names should describe source business intent rather than mechanical sequence.

Do not introduce retries, stricter validation, atomic replacement, idempotency controls, transaction changes, ordering changes, deduplication, or alternate defaults unless they are proven behaviorally equivalent to the source. If a security/runtime necessity would change source outcomes, record it as an unresolved migration mismatch rather than choosing new behavior.

## `run.jil`

Autosys JIL invoking `python job.py ...`. Include job name, command, machine/container placeholder, owner placeholder, working directory, environment/profile placeholders when needed, stdout/stderr destinations, and success/failure semantics. Preserve source job parameters, dependencies, return-code interpretation, and restart behavior that belong at scheduler level. Never embed credentials.

## `oracle.sql` / `sqlite.sql`

DDL for every table created or loaded by the Python job. Include behavior-relevant primary/unique keys, nullability, precision/scale, defaults, indexes/constraints, and DB2 semantics. Use Oracle target datatypes in `oracle.sql`; use validation-compatible SQLite types/constraints in `sqlite.sql`. Document any behavior that Oracle/SQLite cannot reproduce exactly and block 100% if it can affect results.

## `tests/test_job.py`

Runnable parity tests for business rules and job orchestration. Fixtures and expected results must have test-data provenance from source layouts/rules rather than being reverse-engineered from `job.py`. Tests assert what source evidence proves actually happens—including suspicious legacy behavior—not what the logic should ideally do. Cover normal, boundary, reject/error, DB transaction, empty-input, duplicate, restart/rerun, configuration, and ordering cases where applicable.

## `traceability.json`

Machine gate. Minimum shape:

```json
{
  "job": "JOB1",
  "source_commit": "<exact immutable commit SHA>",
  "workbook_sha256": "<64-char SHA-256>",
  "rules": [
    {
      "id": "R001",
      "source": "path/PROGRAM.cbl:120-146",
      "intent": "Observed source behavior in plain English",
      "python": ["job.py:88-94"],
      "tests": ["tests/test_job.py::test_r001_source_behavior"]
    }
  ],
  "coverage_percent": 92.4,
  "security_findings": [],
  "defects": [],
  "unresolved": [],
  "unsupported_claims": []
}
```

`defects` means defects introduced by the migration, not known/suspected defects faithfully reproduced from source. Legacy quirks should be documented in lineage/validation and associated rule intent. `source_commit` and `workbook_sha256` represent the exact evidence used. `unsupported_claims` must list any material validation/review conclusion that cannot be tied to concrete source/Python/test/reconciliation evidence; a non-empty list blocks 100%.

## `validation_report.md`

This is the primary human parity artifact. It must let a reviewer understand exactly what the legacy source does, exactly what Python does, and whether they match without having to infer either side.

### Required structure

1. **Executive Validation Summary** — job, source commit/workbook hash, overall PASS/FAIL, final score, rule counts (total/pass/fail/unverified/preserved-legacy), coverage, unresolved count, unsupported-claim count, and a one-paragraph factual conclusion.
2. **Job-Level Parity Summary** — source JCL execution in plain English versus Python orchestration in plain English; inputs/outputs; DB interactions; step order/conditions; return codes; restart/rerun behavior; overall job-level verdict.
3. **Rule Parity Matrix** — one entry for **every stable Rule ID** in `traceability.json`.
4. **Detailed Discrepancies** — one subsection for every `FAIL` or `UNVERIFIED` Rule ID.
5. **Preserved Legacy Behaviors** — suspicious/incorrect-looking source behaviors that Python intentionally mirrors; these are parity PASS items, not migration defects.
6. **Reconciliation Evidence** — file/record counts, exact/canonicalized comparisons, DB row/aggregate comparisons, return codes, ordering checks, restart/rerun checks, and fixture provenance.
7. **Test/Coverage and Review Evidence** — tests, coverage, adversarial review, security review, DDL/JIL review, unresolved/unsupported claims.
8. **Final Verdict** — explicit 100% or 0%, with blocking Rule IDs if not 100%.

### Rule Parity Matrix contract

For each Rule ID include:

- **Rule ID / source program / step**
- **Source code evidence:** exact JCL/COBOL/copybook/DB2/control-card path and line/paragraph reference plus the smallest useful code excerpt.
- **Source behavior — plain English:** describe only what that cited source demonstrably does: triggering condition, transformation/calculation, side effects, outputs, errors/return code, and ordering/state implications when relevant.
- **Python code evidence:** `job.py` function and line range plus the smallest useful code excerpt.
- **Python behavior — plain English:** describe what the cited Python demonstrably does using the same dimensions as source behavior.
- **Validation evidence:** exact test name/fixture/reconciliation result used to compare them.
- **Parity result:** `PASS`, `FAIL`, or `UNVERIFIED`. For suspicious source behavior faithfully mirrored in Python use `PASS — PRESERVED LEGACY BEHAVIOR`.
- **Reviewer explanation:** concise plain-English explanation of why the evidence establishes the result.

Do not merely say “equivalent” or “mismatch.” The report must show the code/evidence and explain both behaviors independently before comparing them.

### Detailed discrepancy contract

For every `FAIL`, include:

```text
Rule ID:
Source expectation: <plain English, backed by cited source evidence>
Python behavior: <plain English, backed by cited Python evidence>
Exact discrepancy: <specific behavioral difference>
Root cause: <why Python differs, only when proven by evidence>
Observed impact: <specific files/records/rows/state/return-code/order affected, only when proven>
Required remediation: <specific Python change needed to restore source parity; do not change source business logic>
Revalidation required: <tests/reconciliation that must be rerun>
Status: OPEN | RESOLVED AND REVALIDATED
```

For `UNVERIFIED`, replace unsupported conclusions with `UNKNOWN — UNVERIFIED`, state exactly which evidence is missing, and record it in `traceability.json.unsupported_claims` or `unresolved`. Never invent a root cause, impact, intent, or remediation to make the report look complete.

### Evidence and accuracy rules

- Every Rule ID in `traceability.json` must appear in the Rule Parity Matrix. No silent omissions.
- Every material factual statement about source/Python behavior, root cause, impact, or remediation must be traceable to concrete evidence included or referenced in the report.
- Code excerpts are evidence; plain English is an explanation of that evidence, never a replacement for it.
- If source behavior cannot be proven from available artifacts, mark it `UNVERIFIED`; never infer what COBOL “probably” means.
- If Python behavior cannot be proven from code/tests/results, mark it `UNVERIFIED`.
- If root cause cannot be proven, write `Root cause: UNKNOWN — UNVERIFIED` rather than speculating.
- A non-empty `unsupported_claims` or unresolved list blocks 100%.

The adversarial question is: **Does Python behave differently from source anywhere?** It is not: **Can the source logic be improved?** A faithfully reproduced source defect is parity. A source/Python difference is a migration defect.

The score is `100%` only when `scripts/modernization_tools.py <job-folder>` exits 0 and every Rule ID is evidence-backed PASS (including preserved-legacy PASS). Otherwise score `0%` and explain blockers; do not use subjective partial percentages.
