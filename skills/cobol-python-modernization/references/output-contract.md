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

## `lineage.md`

Required order: executive summary; source inventory; JCL step flow; program-by-program explanation; input/output datasets; DB2/table interactions; rule catalog; error/restart behavior; DB2→SQLite/Oracle notes; source-to-target trace table; unresolved items. Each rule has a stable ID and source location.

## `job.py`

One executable Python file containing all business logic for the job. Include a module-level job summary, explicit configuration/input validation, deterministic step orchestration, rule-ID comments, safe file handling, parameterized SQL, transaction boundaries, and non-zero exit codes on failure. Preserve business behavior, not COBOL syntax. Avoid hidden globals and network dependencies.

## `run.jil`

Autosys JIL definition invoking `python job.py ...`. Include job name, command, machine/container placeholder, owner placeholder, working directory, environment/profile placeholders when needed, stdout/stderr destinations, and success/failure semantics. Reflect the source job's parameters/dependencies that belong at scheduler level. Never embed credentials.

## `oracle.sql` / `sqlite.sql`

DDL for every table created or loaded by the Python job. Include primary/unique keys and semantics-relevant indexes/constraints. Use Oracle target datatypes in `oracle.sql`; use validation-compatible SQLite types/constraints in `sqlite.sql`. Add comments for unavoidable semantic differences.

## `tests/test_job.py`

Runnable tests for business rules and job orchestration. Tests must use fixtures derived from source layouts/rules, not fabricated expectations that merely match the Python implementation. Cover normal, boundary, reject/error, DB transaction, empty-input, duplicate, restart/rerun, and ordering cases where applicable.

## `traceability.json`

Machine gate. Minimum shape:

```json
{
  "job": "JOB1",
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

Do not set empty findings because a scan/review was skipped. Empty means the required review was performed and found none.

## `validation_report.md`

State PASS/FAIL first. Then: source completeness; rule trace coverage; test/coverage results; SQLite execution/reconciliation; file comparisons; DB comparisons; scheduler review; DDL review; adversarial findings and fixes; security scan/review; residual differences; final score. The score is `100%` only when `scripts/modernization_tools.py <job-folder>` exits 0. Otherwise score `0%` and explain blockers; do not use subjective partial percentages.
