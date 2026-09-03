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

Do not create shared business-logic modules across jobs. Shared tooling belongs to the skill; generated business logic belongs to that job's `job.py`. The repository-level `DEVOPS_PLAYBOOK.txt` is shared across the modernization effort and is not duplicated into job folders.

## `lineage.md`

Required order: executive summary; source inventory; exact source commit/workbook hash; JCL step flow; program-by-program explanation; input/output datasets; DB2/table interactions; rule catalog; error/restart behavior; DB2→SQLite/Oracle notes; source-to-target trace table; unresolved items. Each rule has a stable ID and source location.

## `job.py`

One executable Python file containing all business logic for the job. Include a module-level plain-English job summary, explicit configuration/input validation, deterministic step orchestration, rule-ID comments, safe file handling, parameterized SQL, transaction boundaries, structured logging, and non-zero exit codes on failure. Preserve business behavior, not COBOL syntax. Avoid hidden globals and network dependencies.

Every function must contain a plain English docstring using this compact contract:

```text
Purpose: What business or orchestration responsibility this function performs.
Inputs: Each argument/input and the business meaning or expected format.
Outputs: Return value and/or files/tables/records produced.
Side effects: Files, database state, logging, counters, checkpoints, or other state changed.
Failure behavior: Validation errors, exceptions, rollback/cleanup, and exit implications.
Rule IDs: Source rule IDs implemented or supported by this function.
```

Docstrings must be understandable without reading COBOL first. Comments inside functions explain why non-obvious logic exists and cite Rule IDs; do not narrate obvious Python syntax. Function names should describe business intent (`validate_account_record`, `load_customer_balances`) rather than mechanical sequence (`process_data_2`).

Generated Python also must be operationally safe: configuration externalized and validated; large-file processing streaming or bounded; DB transactions explicit; output replacement atomic where appropriate; idempotency/restart behavior deliberate; logs useful without exposing secrets or record payloads.

## `run.jil`

Autosys JIL invoking `python job.py ...`. Include job name, command, machine/container placeholder, owner placeholder, working directory, environment/profile placeholders when needed, stdout/stderr destinations, and success/failure semantics. Reflect source parameters/dependencies that belong at scheduler level. Never embed credentials.

## `oracle.sql` / `sqlite.sql`

DDL for every table created or loaded by the Python job. Include primary/unique keys and semantics-relevant indexes/constraints. Use Oracle target datatypes in `oracle.sql`; use validation-compatible SQLite types/constraints in `sqlite.sql`. Add comments for unavoidable semantic differences.

## `tests/test_job.py`

Runnable tests for business rules and job orchestration. Fixtures and expected results must have test-data provenance from source layouts/rules rather than being reverse-engineered from `job.py`. Cover normal, boundary, reject/error, DB transaction, empty-input, duplicate, restart/rerun, configuration, and ordering cases where applicable.

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
      "intent": "Reject records whose status is closed",
      "python": ["job.py:88-94"],
      "tests": ["tests/test_job.py::test_r001_closed_rejected"]
    }
  ],
  "coverage_percent": 92.4,
  "security_findings": [],
  "defects": [],
  "unresolved": []
}
```

Do not set empty findings because a scan/review was skipped. Empty means the required review was performed and found none. `source_commit` and `workbook_sha256` make the result reproducible and must represent the exact evidence used.

## `validation_report.md`

State PASS/FAIL first. Then: source/provenance completeness; rule trace coverage; function-documentation gate; test/coverage results; SQLite execution/reconciliation; file comparisons; DB comparisons; scheduler review; DDL review; operational-readiness review; adversarial findings and fixes; security scan/review; residual differences; final score. The score is `100%` only when `scripts/modernization_tools.py <job-folder>` exits 0. Otherwise score `0%` and explain blockers; do not use subjective partial percentages.
