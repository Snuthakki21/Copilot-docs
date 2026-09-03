# Adversarial Review Protocol

Perform this after generation and normal tests. Assume no trust in the lineage, Python, or prior analysis; source JCL/COBOL/copybooks/DB2/control cards are the evidence of record. The review is a parity review, not a refactoring review.

## Evidence-only rule

The review must contain **no unsupported claims**. Every factual statement about source behavior, Python behavior, parity, root cause, impact, or remediation must be supported by concrete evidence: an exact source location/excerpt, Python location/excerpt, test/fixture result, file/DB comparison, or scheduler/DDL evidence. Do not convert likelihood into fact.

When evidence is insufficient, write `UNKNOWN — UNVERIFIED` or `UNKNOWN — additional source tracing required`, add the item to `unsupported_claims` or `unresolved`, and block 100%. Never invent a missing branch, business meaning, root cause, expected output, DB2 semantic, or remediation merely because it is plausible.

Classify every finding as one of three types:
- **Migration mismatch:** Python differs from proven source behavior. This is a defect and blocks 100%.
- **Preserved legacy quirk:** source behavior looks suspicious/incorrect but Python reproduces it faithfully. Document it; do not repair it and do not count it as a migration defect.
- **Unverified:** evidence is insufficient to establish parity or cause. This blocks 100% until resolved from source/test evidence.

1. Rebuild the job step graph from source JCL independently. For every conclusion record the JCL/PROC/control-card evidence used. Compare step order, conditional execution, return codes, overrides, DDs, utilities, parameters, datasets, and scheduler-relevant semantics.
2. For each program, re-read source and enumerate rules without consulting `job.py` first. Every rule must retain its source location. Then map each rule to lineage, Python, and tests. Missing, merged, split, reordered, weakened, or strengthened rules are migration mismatches unless source evidence proves equivalence.
3. Where executable logic conflicts with comments, names, documentation, or apparent business intent, record both pieces of evidence and use executable source behavior as the parity expectation unless stronger source evidence resolves it. Do not infer intent.
4. Reconcile all inputs/outputs from evidence: record layout, encoding, record length, delimiter/blocking, sort/collation, duplicate handling, headers/trailers, counts, file naming/GDG behavior, empty files, rejects, and partial-output behavior. Do not normalize odd source behavior during comparison.
5. Reconcile DB behavior using actual embedded SQL, declarations, SQLCODE/indicator handling and applicable DDL/control evidence: predicates, joins, cursor ordering, NULLs, numeric precision/scale, timestamps, transaction boundaries, isolation/locking, commit frequency, rollback, duplicate keys, and DB2-specific semantics. If a DB2→SQLite/Oracle semantic cannot be proven equivalent, classify it Unverified or Migration mismatch, not assumed-equivalent.
6. Construct counterexamples around every source-proven branch/boundary. Expected results must be independently derived from source evidence, not from `job.py` or from what seems reasonable.
7. Compare SQLite/job outputs with independently source-derived expectations. Prefer exact row/file equality. Canonicalize only when source evidence proves ordering is immaterial; record that evidence.
8. Inspect generated Python for introduced differences: changed defaults, stricter validation, altered exceptions, reordered side effects, deduplication, changed rounding/truncation, implicit retries, added rollback/atomicity, changed commit frequency, altered return codes, or changed partial-write/restart behavior. “Better” behavior is still a migration mismatch when source differs.
9. For every failed parity rule, state the discrepancy first. State a root cause only when evidence proves it. Otherwise use `UNKNOWN — additional source tracing required`. Required remediation must point to the exact Python/test/DDL/JIL location to change and the source behavior it must reproduce.
10. Security review: identify path traversal, SQL injection, unsafe subprocess/deserialization/eval/exec, embedded secrets, sensitive logs, temp-file exposure, or unbounded resource risks. Remediation must preserve business behavior. If a security fix necessarily changes source behavior, record the conflict as unresolved and block 100%.
11. Verify `run.jil` invokes exactly the tested command/configuration and preserves source-consistent success/failure behavior. Verify Oracle/SQLite DDL supports the Python behavior and source constraints.
12. Perform an **unsupported-claim sweep**: take every material sentence in `validation_report.md` and confirm it is either (a) linked to evidence, (b) explicitly labeled observation/opinion, or (c) explicitly `UNKNOWN/UNVERIFIED`. Put any unsupported factual claim in `traceability.json.unsupported_claims`.
13. Re-run compilation, tests, coverage, scanners, and `scripts/modernization_tools.py`. Any source/Python mismatch, unresolved behavior, unsupported claim, introduced security defect, failed test, or coverage below 80% blocks 100%. Preserved legacy quirks do not block parity by themselves.
