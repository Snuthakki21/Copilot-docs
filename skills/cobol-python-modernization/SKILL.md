---
name: cobol-python-modernization
description: Use when modernizing a file-based mainframe batch job identified by Excel job/step/program/input/output metadata and backed by JCL, COBOL, copybooks, DB2 SQL, utilities, control cards, or scheduler definitions into one Python job implementation with auditable parity.
argument-hint: "<excel-path> [source-branch]"
---

# COBOL to Python Modernization

## Core principle

Trace first, translate second, prove last. The governing requirement is **behavioral preservation**. The existing source system is the contract, including defects, quirks, odd branches, inconsistent rules, surprising calculations, unusual return codes, and behavior that appears incorrect. **Do not correct, improve, normalize, reinterpret, optimize away, or redesign source behavior during migration.** Mirror what the source actually does. Suspicious behavior may be called out in lineage and validation as an observation, but the generated Python must preserve it unless source evidence itself proves a different behavior.

Never infer success from plausible Python. A job is complete only when every discovered source behavior has evidence in the lineage, Python, scheduler artifact, tests, and validation manifest. **When evidence is missing, fail closed**: produce diagnostics, do not invent behavior, and do not ask the user to restate information discoverable from the repository.

The review is evidence-only. No material claim about source behavior, Python behavior, parity, root cause, impact, or remediation may be stated as fact without direct supporting source/Python/test/reconciliation evidence. When evidence cannot support a conclusion, write `UNKNOWN — UNVERIFIED`, record it in `traceability.json.unsupported_claims` or `unresolved`, and block 100%. Never fill an evidence gap with a plausible explanation.

**Efficiency rule:** apply **Ponytail v4.9.0** only after full source tracing. Reuse repository patterns, prefer Python stdlib, use `sqlite3` for validation, stream large files where that does not alter semantics, and add dependencies only when needed. Efficiency may reduce implementation complexity; it may never change source behavior.

## Required inputs and discovery

The user supplies an Excel workbook and identifies the source repository/branch. The workbook may contain multiple jobs and columns equivalent to `job`, `step`, `program`, `inputs`, `outputs`. Use `scripts.modernization_tools.workbook_rows()` to normalize it. Record the exact source commit and SHA-256 of the workbook before analysis.

For each job, recursively resolve from JCL into every referenced COBOL program, COPY/include, PROC, control card, DB2 SQL/table, sort/merge/utility step, dataset/file definition, and called subprogram available on the branch. Search production/source and working/converted directories. Production/source behavior is authoritative; working/converted code is supporting evidence unless source evidence establishes equivalence.

Do not ask for missing implementation details. If a referenced artifact truly cannot be found, record it as unresolved, generate the best evidence-backed partial artifacts, and score the job 0 rather than fabricate behavior.

## Fidelity rules

- Preserve **observed behavior**, not intended business meaning. If comments, names, or documentation disagree with executable logic, document the conflict and mirror executable behavior unless stronger source evidence resolves it.
- Preserve source defects and quirks. If the COBOL uses a suspicious predicate, calculation, truncation, default, fall-through, SQL condition, duplicate rule, or return-code path, reproduce it and label it as an observed legacy behavior in lineage/validation.
- Do not silently repair data-quality problems, duplicate handling, null behavior, date logic, arithmetic, error handling, commit frequency, ordering, restart behavior, or file-write behavior.
- Do not introduce “best practice” semantics that change outcomes. Transactions, atomic writes, retries, idempotency protections, stricter validation, or new defaults may be added only when they are behaviorally equivalent to the source. Otherwise record them as future remediation candidates outside this migration.
- Do not collapse two source branches because they appear redundant. Preserve both when they can produce different control flow, side effects, logging, SQL, files, return codes, or timing/order.
- A suspected bug is not a migration defect if Python reproduces the source bug exactly. A migration defect is a difference between source behavior and Python behavior.

## Per-job workflow

1. Read the entire JCL/job definition and build the ordered step graph, including conditional execution, return-code handling, overrides, DD statements, DISP/GDG behavior, utilities, parameters, and restart/checkpoint semantics.
2. For each step, fully trace the invoked program and all reachable source artifacts. Extract atomic rules with stable IDs (`R001`, `R002`, ...), source locations, inputs, transformations, state/DB effects, outputs, error paths, ordering dependencies, and observed quirks.
3. Write `lineage.md` first. Explain the job end-to-end in plain English, then each step/program, then a rule table linking source evidence to intended Python behavior. Clearly distinguish **observed source behavior** from commentary about whether that behavior looks suspicious. Never let the commentary alter the implementation.
4. Write exactly one primary `job.py` per job. All job business logic stays in that file. Preserve source ordering and semantics. Every function must have a plain-English docstring with `Purpose:`, `Inputs:`, `Outputs:`, `Side effects:`, `Failure behavior:`, and `Rule IDs:`. Comments explain non-obvious legacy behavior and cite rule IDs; where behavior looks wrong, comments should say it is intentionally preserved from source rather than “fixing” it.
5. Write `run.jil` for the Autosys target, invoking the Python job with explicit paths/arguments/environment placeholders and source-consistent success/failure exit behavior. Autosys uses JIL; generate legacy `run.jcl` only when explicitly required.
6. Write `oracle.sql` and `sqlite.sql` for every created/loaded table needed by the migrated job. Preserve behavior-relevant keys, nullability, precision/scale, defaults, uniqueness, indexes, and DB2 semantics. Where Oracle/SQLite cannot exactly reproduce DB2 behavior, document the difference and block 100% until the behavioral impact is resolved or proven irrelevant.
7. Write `tests/test_job.py`. Tests must be source-derived and prove parity, including legacy quirks and suspicious behavior. Do not write tests for what the code “should” do; write tests for what source evidence proves it does. Measure all generated `.py` files; **80% is a floor, not a target to game**.
8. Execute the job against representative source-derived fixtures and SQLite. Compare record counts, key aggregates, row/file content, ordering where meaningful, rejects, return codes, DB state, and rerun/restart behavior. Exact source-equivalent oddities are PASS conditions, not defects.
9. Perform the independent adversarial review in `references/adversarial-review.md`. The reviewer asks “Where does Python differ from source?” rather than “How should this logic be improved?”
10. Write `validation_report.md` and `traceability.json`. The validation report must contain an executive summary, a Rule Parity Matrix for every stable Rule ID, and detailed discrepancy analysis for every FAIL. For each rule show source code evidence, source behavior in plain English, Python code evidence, Python behavior in plain English, validation/test evidence, and PASS/FAIL/UNVERIFIED. Every FAIL must explain the exact discrepancy, evidence-backed root cause, observed impact, required remediation to restore source parity, and revalidation required. Never infer missing facts; use `UNKNOWN — UNVERIFIED` when evidence is insufficient.
11. Run `python scripts/modernization_tools.py <job-folder>`. A **100%** score is allowed only when complete rule traces, documented functions, source provenance, validation-report completeness, zero unsupported claims, Python coverage ≥80%, and zero unresolved migration mismatches/security defects are present. Suspicious-but-faithfully-preserved source behavior is documented separately and does not reduce parity.

## Required outputs

Follow `references/output-contract.md` exactly. One Excel file may yield many job folders; never mix rules or artifacts across jobs.

## Quality defaults that do not change behavior

- Use `decimal.Decimal` when needed to reproduce COBOL/DB2 decimal semantics exactly. Match source scale, rounding/truncation, overflow, and sign handling rather than applying a preferred financial convention.
- Prefer streaming and bounded batches for large files only when record ordering, restart behavior, side effects, and outputs remain equivalent.
- Keep environment configuration outside business logic where this is behavior-neutral. Do not convert hard-coded business constants into configurable values merely because configurability seems cleaner.
- Logging/comments may improve explainability, but must not introduce control-flow, timing, retry, validation, or data changes.
- Keep generated code boring and inspectable. Avoid framework layers, generic migration engines, and abstractions that obscure source-to-target traceability.

## Mainframe semantics that must be checked

Use `references/mainframe-edge-cases.md`. At minimum examine fixed/variable records, EBCDIC/text encoding, signed/packed/binary decimals, PIC scaling/truncation, REDEFINES, OCCURS/DEPENDING ON, copybooks, sort stability/collation, duplicate keys, EOF/empty files, GDGs, DISP, utility/control-card semantics, COBOL conditionals/88 levels, PERFORM/GO TO fall-through, SQLCODE/NULL indicators, cursor ordering, commit/rollback/isolation, date/timestamp behavior, DB2-specific SQL, return codes, abends, restartability, partial writes, reruns, and concurrent file/table access.

## Security and defect gate

At the final step run available repository-approved linters/scanners from the user's Artifactory/toolchain; never fetch unapproved packages from public registries. Security fixes may protect the new runtime but must not silently alter business outcomes. If a security issue cannot be remediated without changing legacy behavior, document the conflict and block 100% rather than choosing new behavior unilaterally. Compile all Python and run the complete test suite.

## ACU discipline

Batch repository reads by job and reuse a source index across steps. Parse each source file once, cache rule/source references, hash inputs once, and use deterministic scripts for Excel normalization, documentation checks, provenance checks, validation-report checks, and final gating. Reserve model reasoning for semantic extraction, DB2/COBOL translation, and adversarial comparison. Do not repeatedly narrate established facts or re-open unchanged source files.

## Common mistakes

| Mistake | Required correction |
|---|---|
| Translating COBOL paragraph-by-paragraph | Reconstruct executable job behavior and rules first; Python mirrors semantics, not syntax. |
| “Fixing” logic that looks incorrect | Preserve it exactly, flag it as an observed legacy behavior, and leave remediation for a separate effort. |
| Treating comments/business names as stronger than execution | Document disagreement and preserve executable source behavior unless stronger evidence resolves it. |
| Treating working/converted code as truth | Production JCL/COBOL/DB2 is authoritative unless source evidence proves otherwise. |
| Adding retries/atomicity/idempotency as best practices | Add only if behaviorally equivalent; otherwise document as future remediation. |
| Claiming 100% because tests pass | Require provenance, documented functions, complete validation report, full rule traceability, ≥80% coverage, zero unsupported claims, and zero migration mismatches. |
| Comments explain syntax instead of intent | Explain source behavior, quirks, side effects, failures, and rule IDs in plain English. |
