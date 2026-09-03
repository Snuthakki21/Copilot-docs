# Adversarial Review Protocol

Perform this after generation and normal tests. Assume no trust in the lineage or Python; source JCL/COBOL/copybooks/DB2/control cards are the evidence of record.

1. Rebuild the job step graph from source JCL independently. Compare step order, conditional execution, return codes, overrides, DDs, utilities, parameters, datasets, and scheduler-relevant semantics.
2. For each program, re-read source and enumerate rules without consulting `job.py` first. Then map each rule to `lineage.md`, `job.py`, and tests. Missing, merged, split, reordered, or weakened rules are defects until justified by evidence.
3. Reconcile all inputs/outputs: record layout, encoding, record length, delimiter/blocking, sort/collation, duplicate handling, headers/trailers, counts, file naming/GDG behavior, empty files, rejects, and partial-output behavior.
4. Reconcile DB behavior: SQL predicates, joins, cursor ordering, NULL indicators, SQLCODE branches, numeric precision/scale, timestamps, transaction boundaries, isolation/locking assumptions, commit frequency, rollback, duplicate keys, and DB2-specific semantics translated to SQLite/Oracle.
5. Construct counterexamples around every branch/boundary: zero/one/max values, negative/signed values, precision boundaries, malformed records, missing optional fields, duplicate keys, first/last record, EOF, no rows/many rows, NULLs, date boundaries, restart after partial progress, and rerun after success.
6. Compare observed SQLite/job outputs with independently calculated expectations. Prefer exact row/file equality; where nondeterministic ordering is source-irrelevant, compare canonicalized content and document why.
7. Inspect generated Python for introduced defects: swallowed exceptions, wrong defaults, mutation/order bugs, non-atomic writes, incomplete rollback, incorrect return codes, path assumptions, locale/timezone dependence, integer/decimal conversion, and memory blowups from reading large mainframe files wholesale.
8. Security review: validate untrusted paths/parameters, prohibit path traversal, parameterize SQL, avoid `shell=True`, `eval`, `exec`, unsafe pickle/deserialization, embedded secrets, world-readable sensitive temp files, sensitive logs, and uncontrolled resource consumption. Use approved static scanners when present.
9. Verify `run.jil` invokes exactly the tested command/configuration and contains no secret. Verify Oracle/SQLite DDL supports the Python behavior and source constraints.
10. Re-run compilation, tests, coverage, scanners, and `scripts/modernization_tools.py`. Any open mismatch, unresolved source, security finding, failed test, or coverage below 80% blocks 100%.
