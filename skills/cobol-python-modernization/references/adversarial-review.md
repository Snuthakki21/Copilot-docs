# Adversarial Review Protocol

Perform this after generation and normal tests. Assume no trust in the lineage or Python; source JCL/COBOL/copybooks/DB2/control cards are the evidence of record. The review is a parity review, not a refactoring review.

Classify every finding as one of two types:
- **Migration mismatch:** Python differs from proven source behavior. This is a defect and blocks 100%.
- **Preserved legacy quirk:** source behavior looks suspicious/incorrect but Python reproduces it faithfully. Document it; do not repair it in this migration and do not count it as a migration defect.

1. Rebuild the job step graph from source JCL independently. Compare step order, conditional execution, return codes, overrides, DDs, utilities, parameters, datasets, and scheduler-relevant semantics.
2. For each program, re-read source and enumerate rules without consulting `job.py` first. Then map each rule to `lineage.md`, `job.py`, and tests. Missing, merged, split, reordered, weakened, or strengthened rules are migration mismatches unless source evidence proves equivalence.
3. Where executable logic conflicts with comments, names, documentation, or apparent business intent, record the conflict and use executable source behavior as the parity expectation unless stronger source evidence resolves it.
4. Reconcile all inputs/outputs: record layout, encoding, record length, delimiter/blocking, sort/collation, duplicate handling, headers/trailers, counts, file naming/GDG behavior, empty files, rejects, and partial-output behavior. Do not “normalize” odd source behavior during comparison.
5. Reconcile DB behavior: SQL predicates, joins, cursor ordering, NULL indicators, SQLCODE branches, numeric precision/scale, timestamps, transaction boundaries, isolation/locking assumptions, commit frequency, rollback, duplicate keys, and DB2-specific semantics translated to SQLite/Oracle.
6. Construct counterexamples around every branch/boundary: zero/one/max values, negative/signed values, precision boundaries, malformed records, missing optional fields, duplicate keys, first/last record, EOF, no rows/many rows, NULLs, date boundaries, restart after partial progress, and rerun after success. Expected results come from source behavior, including defects/quirks.
7. Compare SQLite/job outputs with independently source-derived expectations. Prefer exact row/file equality. Canonicalize only when source behavior proves ordering is immaterial; do not canonicalize away an ordering mismatch.
8. Inspect generated Python for introduced differences: changed defaults, stricter validation, altered exceptions, reordered side effects, deduplication, changed rounding/truncation, implicit retries, added rollback/atomicity, changed commit frequency, altered return codes, or changed partial-write/restart behavior. “Better” behavior is still a migration mismatch when the source did something else.
9. Security review: identify path traversal, SQL injection, unsafe subprocess/deserialization/eval/exec, embedded secrets, sensitive logs, temp-file exposure, or unbounded resource risks. Remediation must preserve business behavior. If a security fix necessarily changes source behavior, record the conflict as unresolved and block 100% rather than silently choosing new semantics.
10. Verify `run.jil` invokes exactly the tested command/configuration and preserves source-consistent success/failure behavior. Verify Oracle/SQLite DDL supports the Python behavior and source constraints.
11. Re-run compilation, tests, coverage, scanners, and `scripts/modernization_tools.py`. Any open source/Python mismatch, unresolved behavior, introduced security defect, failed test, or coverage below 80% blocks 100%. Preserved legacy quirks do not block parity by themselves.
