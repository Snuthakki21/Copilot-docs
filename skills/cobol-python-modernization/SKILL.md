---
name: cobol-python-modernization
description: Use when modernizing a file-based mainframe batch job identified by Excel job/step/program/input/output metadata and backed by JCL, COBOL, copybooks, DB2 SQL, utilities, control cards, or scheduler definitions into one Python job implementation with auditable parity.
argument-hint: "<excel-path> [source-branch]"
---

# COBOL to Python Modernization

## Core principle

Trace first, translate second, prove last. Never infer success from plausible Python. A job is complete only when every discovered source behavior has evidence in the lineage, Python, scheduler artifact, tests, and validation manifest. **When evidence is missing, fail closed**: produce the diagnostics, do not claim parity, and do not ask the user to restate information that can be discovered from the repository.

**Efficiency rule:** apply **Ponytail v4.9.0** after full source tracing: reuse repository patterns, prefer Python stdlib, use `sqlite3` for validation, add a dependency only when semantics or scale require it. Never simplify away validation, security, numeric/file semantics, restart behavior, or requested outputs.

## Required inputs and discovery

The user supplies an Excel workbook and identifies the source repository/branch. The workbook may contain multiple jobs and columns equivalent to `job`, `step`, `program`, `inputs`, `outputs`. Use `scripts.modernization_tools.workbook_rows()` to normalize it. For each job, recursively resolve from JCL into every referenced COBOL program, COPY/include, PROC, control card, DB2 SQL/table, sort/merge/utility step, dataset/file definition, and called subprogram available on the branch. Search production/source and working/converted directories; working code is evidence, never automatically authoritative over production.

Do not ask for missing implementation details. If a referenced artifact truly cannot be found, record it as unresolved, generate the best evidence-backed partial artifacts, and score the job 0 rather than fabricate behavior.

## Per-job workflow

1. Read the entire JCL/job definition and build the ordered step graph, including conditional execution, return-code handling, overrides, DD statements, DISP/GDG behavior, utilities, parameters, and restart/checkpoint semantics.
2. For each step, fully trace the invoked program and all reachable source artifacts. Extract atomic rules with stable IDs (`R001`, `R002`, ...), source locations, inputs, transformations, state/DB effects, outputs, error paths, and ordering dependencies.
3. Write `lineage.md` first. Explain the job end-to-end in plain English, then each step/program, then a rule table linking source evidence to intended Python behavior. Make it understandable to an executive while retaining source-level detail for an engineer.
4. Write exactly one primary `job.py` per job. It may contain classes/functions, but all job business logic stays in that file. Preserve source ordering and semantics; comments must identify rule IDs and why behavior exists. Use stdlib-first. SQLite is the executable DB surrogate; keep SQL/data-access boundaries explicit so Oracle replacement is mechanical.
5. Write `run.jil` for the Autosys target, invoking the Python job with explicit paths/arguments/environment placeholders and success/failure exit behavior. Autosys uses JIL; do not mislabel it as legacy JCL. Generate legacy `run.jcl` only when the user explicitly requires a mainframe execution artifact.
6. Write `oracle.sql` and `sqlite.sql` for every created/loaded table needed by the job. Preserve keys, nullability, precision/scale, defaults, uniqueness, indexes needed for semantics, and note DB2→Oracle/SQLite type or SQL differences.
7. Write `tests/test_job.py`. Tests must cover rules, edge cases, failures, file/DB side effects, and ordering. Measure all generated `.py` files; **80% is a floor, not a target to game**.
8. Execute the job against representative fixtures and SQLite where source-compatible fixtures can be built. Compare record counts, key aggregates, row/file content, ordering where meaningful, rejects, return codes, DB state, and rerun/restart/idempotency behavior.
9. Perform an independent adversarial review using `references/adversarial-review.md`. Treat generated artifacts as untrusted and re-derive expectations from source evidence. Record defects and security findings rather than rationalizing them.
10. Write `validation_report.md` and `traceability.json`, then run `python scripts/modernization_tools.py <job-folder>`. A **100%** score is allowed only when the validator passes: every rule has source, Python, and test traces; Python coverage is at least 80%; unresolved behavior, introduced defects, and security findings are all zero.

## Required outputs

Follow `references/output-contract.md` exactly. One Excel file may yield many job folders; never mix rules or artifacts across jobs.

## Mainframe semantics that must be checked

Use `references/mainframe-edge-cases.md`. At minimum examine fixed/variable records, EBCDIC/text encoding, signed/packed/binary decimals, PIC scaling/truncation, REDEFINES, OCCURS/DEPENDING ON, copybooks, sort stability/collation, duplicate keys, EOF/empty files, GDGs, DISP, utility/control-card semantics, COBOL conditionals/88 levels, PERFORM/GO TO fall-through, SQLCODE/NULL indicators, cursor ordering, commit/rollback/isolation, date/timestamp behavior, DB2-specific SQL, return codes, abends, restartability, partial writes, reruns, and concurrent file/table access.

## Security and defect gate

At the final step run available repository-approved linters/scanners from the user's Artifactory/toolchain (for example Bandit/Ruff if already available); never fetch unapproved packages from public registries. Independently inspect command construction, path traversal, SQL parameterization, secrets/logging, temporary files/permissions, unsafe deserialization/eval/exec, shell use, denial-of-service risks from unbounded inputs, and error messages. Compile all Python and run the complete test suite. Any unresolved high/medium security issue or functional defect blocks 100%.

## ACU discipline

Batch repository reads by job and reuse a source index across steps. Parse each source file once, cache rule/source references, use deterministic scripts for Excel normalization and final gating, and reserve model reasoning for semantic extraction, DB2/COBOL translation, and adversarial comparison. Do not repeatedly narrate already-established facts into generated artifacts.

## Common mistakes

| Mistake | Required correction |
|---|---|
| Translating COBOL paragraph-by-paragraph | Reconstruct job intent and rules first; Python mirrors semantics, not syntax. |
| Treating working/converted code as truth | Production JCL/COBOL/DB2 is authoritative unless source evidence proves otherwise. |
| Claiming 100% because tests pass | Require full rule traceability, ≥80% coverage, zero unresolved items, zero defects, zero security findings. |
| Using pandas by default | Prefer stdlib streaming/`csv`/`sqlite3`; use pandas only when it materially reduces correct code or is already approved. |
| Ignoring scheduler semantics | Preserve parameters, environment, dependencies, return codes, and failure behavior in `run.jil`. |
