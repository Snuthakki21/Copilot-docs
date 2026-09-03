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
  "unresolved": []
}
```

`defects` means defects introduced by the migration, not known/suspected defects faithfully reproduced from source. Legacy quirks should be documented in lineage/validation and associated rule intent. `source_commit` and `workbook_sha256` represent the exact evidence used.

## `validation_report.md`

State PASS/FAIL first. Then: source/provenance completeness; rule trace coverage; function-documentation gate; test/coverage results; SQLite execution/reconciliation; file comparisons; DB comparisons; scheduler review; DDL review; preserved legacy quirks/suspicious behaviors; adversarial findings and fixes; security review; residual migration differences; final score.

The adversarial question is: **Does Python behave differently from source anywhere?** It is not: **Can the source logic be improved?** A faithfully reproduced source defect is parity. A source/Python difference is a migration defect.

The score is `100%` only when `scripts/modernization_tools.py <job-folder>` exits 0 and no behaviorally material source/Python mismatch remains. Otherwise score `0%` and explain blockers; do not use subjective partial percentages.
