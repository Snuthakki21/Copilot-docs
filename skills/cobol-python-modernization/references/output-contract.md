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
    fixtures/
    validation.db
```

Do not create shared business-logic modules across jobs. Shared tooling belongs to the skill; generated business logic belongs to that job's `job.py`.

## Governing parity rule

The artifacts document and reproduce **observed legacy behavior**, even when that behavior is suspicious or appears incorrect. The migration must not change source logic to match a preferred interpretation, comment, business expectation, or modern best practice. Suspicious behavior is documented as an observation; it is not repaired in the migration unless source evidence itself proves the executable behavior differs.

## Evidence-only accuracy rule

Every material factual claim in lineage and validation must be supported by concrete evidence: exact source location/excerpt, Python location/excerpt, test/fixture result, file/DB reconciliation, or scheduler/DDL evidence. Never convert a plausible inference into a fact. If evidence is insufficient, write `UNKNOWN — UNVERIFIED`, add the item to `unsupported_claims` or `unresolved`, and block 100% until evidence resolves it.

## `lineage.md`

Required order: executive summary; source inventory; exact source commit/workbook hash; JCL step flow; program-by-program explanation; input/output datasets; DB2/table interactions; rule catalog; legacy quirks/suspicious behavior; error/restart behavior; DB2→SQLite/Oracle notes; source-to-target trace table; unresolved items. Each rule has a stable ID and source location.

When behavior looks wrong, explicitly separate:
- **Observed source behavior:** what the executable source actually does.
- **Observation:** why the behavior may look unusual or suspicious.
- **Migration action:** `PRESERVE` unless stronger source evidence proves another behavior.

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

Docstrings must be understandable without reading COBOL first. Comments inside functions explain why non-obvious logic exists and cite Rule IDs. If a rule appears defective, comment that it is intentionally preserved from source; do not silently correct it.

Do not introduce retries, stricter validation, atomic replacement, idempotency controls, transaction changes, ordering changes, deduplication, or alternate defaults unless they are proven behaviorally equivalent to the source.

## `run.jil`

Autosys JIL invoking `python job.py ...`. Include job name, command, machine/container placeholder, owner placeholder, working directory, environment/profile placeholders when needed, stdout/stderr destinations, and success/failure semantics. Preserve source job parameters, dependencies, return-code interpretation, and restart behavior that belong at scheduler level. Never embed credentials.

## `oracle.sql` / `sqlite.sql`

DDL for every table created or loaded by the Python job. Include behavior-relevant primary/unique keys, nullability, precision/scale, defaults, indexes/constraints, and DB2 semantics. Document any behavior that Oracle/SQLite cannot reproduce exactly and block 100% if it can affect results.

## `tests/test_job.py`

Runnable parity tests for business rules and job orchestration. Fixtures and expected results must have test-data provenance from source layouts/rules rather than being reverse-engineered from `job.py`. Tests assert what source evidence proves actually happens—including suspicious legacy behavior—not what the logic should ideally do.

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

`defects` means defects introduced by the migration, not known/suspected defects faithfully reproduced from source. `unsupported_claims` contains any material validation/lineage assertion for which the reviewer cannot point to sufficient evidence. A non-empty `unsupported_claims` list blocks 100%.

## `validation_report.md`

This is the primary human-readable parity artifact. It must be understandable by an executive who cannot read COBOL and useful to an engineer who must fix a mismatch.

### Required top-level structure

1. **Executive Validation Summary** — PASS/FAIL, final score, job purpose, source commit/workbook hash, number of rules checked, passed rules, failed rules, unresolved/unverified items, coverage, and one-paragraph conclusion.
2. **Rule Parity Matrix** — one row for every stable Rule ID discovered from JCL/COBOL/DB2/control-card behavior.
3. **Detailed Discrepancies** — one subsection for every failed rule; omit only when every rule passes.
4. **Preserved Legacy Quirks** — suspicious or apparently incorrect source behavior that Python mirrors exactly. These are not migration defects.
5. **File / Database / Scheduler Reconciliation** — input/output counts, row/file comparisons, DB state, ordering, return codes, restart/rerun behavior, DDL/JIL checks.
6. **Test / Coverage / Security Results** — tests, ≥80% coverage, adversarial review and security/defect results.
7. **Final Verdict** — 100% only when no behaviorally material source/Python mismatch, unresolved evidence gap, or unsupported factual claim remains; otherwise 0% with blockers.

### Rule Parity Matrix

For every rule, include all of these fields. Do not replace them with a generic summary.

| Field | Required content |
|---|---|
| **Rule ID** | Stable lineage ID, e.g. `R017`. |
| **Job / Step / Program** | Exact context in which the rule executes. |
| **Source location** | File/member and line/paragraph/JCL-step/control-card reference. |
| **Source code evidence** | The smallest relevant COBOL/JCL/DB2/control-card excerpt or precise source reference needed to prove the behavior. |
| **Source behavior in plain English** | What the source actually does, including conditions, calculations, side effects, outputs and failure behavior. Explain it without assuming COBOL knowledge. |
| **Python location** | `job.py` function/line range implementing the rule. |
| **Python code evidence** | The smallest relevant Python excerpt or precise source reference needed to prove the implementation. |
| **Python behavior in plain English** | What the Python actually does when executed. Do not merely restate the code syntax. |
| **Validation evidence** | Test IDs, fixture/case, SQLite/file comparison or other evidence used. |
| **Parity result** | `PASS` only when source and Python behavior are materially equivalent; `FAIL` for a proven mismatch; `UNVERIFIED` when evidence is insufficient. |
| **Discrepancy** | `None` for PASS. For FAIL, a plain-English statement of exactly what behavior differs. For UNVERIFIED, state what cannot yet be proven. |
| **Root cause** | `N/A` for PASS. For FAIL, state only an evidence-backed cause. If not proven, use `UNKNOWN — additional source tracing required`. |
| **Required remediation** | `None` for PASS. For FAIL, the specific change needed in Python/tests/DDL/JIL to restore source parity. For UNVERIFIED, state the evidence needed before remediation can be prescribed safely. |

A reviewer should be able to read one row and answer: **What did COBOL do? What does Python do? Are they the same? If not, exactly why not and what must be changed? If we cannot prove the answer, is that uncertainty explicitly visible?**

### Detailed Discrepancies

For each `FAIL`, add a subsection using this structure:

```text
Rule ID / Job / Step / Program:
Severity to parity: BLOCKING

Source code evidence:
<source excerpt/reference>

Source behavior in plain English:
<clear explanation>

Python code evidence:
<Python excerpt/reference>

Python behavior in plain English:
<clear explanation>

Discrepancy:
<exact behavioral difference>

Why this discrepancy exists / Root cause:
<evidence-backed cause; UNKNOWN if not proven>

Observed impact:
<records, files, DB state, control flow, return codes, ordering, restart behavior, etc.>

Required remediation to restore parity:
<specific Python/test/DDL/JIL action; never redesign legacy business logic>

Validation required after remediation:
<tests/reconciliation that must be rerun>

Evidence supporting this conclusion:
<source/Python/test/reconciliation references>

Status:
OPEN | RESOLVED AND REVALIDATED
```

Never guess a root cause, impact, or remediation. If evidence does not establish it, write `UNKNOWN — additional source tracing required`, add the unsupported point to `traceability.json.unsupported_claims` or `unresolved`, and keep the job at 0%.

### Preserved legacy quirks

Use the same source/plain-English/Python/plain-English comparison when useful, but label the result `PASS — PRESERVED LEGACY BEHAVIOR`. Explain why it looks suspicious and explicitly state that no correction was made because behavioral preservation is the migration contract.

The adversarial question is: **Does Python behave differently from source anywhere?** It is not: **Can the source logic be improved?** A faithfully reproduced source defect is parity. A source/Python difference is a migration defect.

The score is `100%` only when `scripts/modernization_tools.py <job-folder>` exits 0 and no behaviorally material source/Python mismatch, unresolved evidence gap, or unsupported factual claim remains. Otherwise score `0%` and explain blockers; do not use subjective partial percentages.
