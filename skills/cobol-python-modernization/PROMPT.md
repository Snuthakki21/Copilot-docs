# Devin Invocation Prompt

Use the `cobol-python-modernization` skill for this task and use the repository-level `DEVOPS_PLAYBOOK.txt` as the operational delivery reference.

I am providing an Excel workbook containing one or more batch jobs. Its columns identify job, step, program, inputs, and outputs (header spelling may vary). Use the repository and branch I identify as the source of truth and discover everything else yourself. Do not ask me for COBOL/JCL/DB2 details that can be found in the branch. Record the exact source commit and SHA-256 of the workbook before generation.

For every distinct job, trace the complete source JCL and every program/artifact it references: COBOL, copybooks/includes, PROCs, DB2 SQL/tables, utilities, sort/control cards, file definitions, called programs, and relevant working/converted code. Production/source behavior is authoritative; working/converted code is supporting evidence only unless source proves equivalence.

Create one output folder per job and follow the skill output contract exactly. At minimum each job contains `lineage.md`, one fully commented/documented `job.py`, `run.jil`, `oracle.sql`, `sqlite.sql`, `validation_report.md`, `traceability.json`, and `tests/test_job.py`. Every Python function must explain in plain English its Purpose, Inputs, Outputs, Side effects, Failure behavior, and Rule IDs. Use SQLite to execute and validate database behavior now; make Oracle DDL and Python DB boundaries ready for later Oracle replacement. Prefer stdlib and approved dependencies from enterprise Artifactory. Apply Ponytail v4.9.0 only after fully understanding the source.

The Python and JIL must match the complete job intent and all programs underneath it, not merely translate syntax. Preserve file semantics, DB2 behavior, decimal precision, ordering, conditions, return codes, restart/rerun behavior, failures, and outputs. Also verify configuration, observability, reproducibility, idempotency, large-file behavior, safe output/transaction semantics, and test-data provenance.

Run functional validation with source-derived fixtures and SQLite, obtain at least 80% coverage across generated `.py` files, then perform the independent adversarial review plus final security/defect checks. A job may receive **100%** only when every discovered rule is traced and tested, documentation/provenance gates pass, coverage is at least 80%, reconciliation passes, and there are zero unresolved source behaviors, introduced defects, or open security findings. Otherwise fail closed and score 0%.

Repository: <OWNER/REPO OR LOCAL PATH>
Branch: <BRANCH>
Excel: <PATH TO XLSX>
Output root: <OUTPUT DIRECTORY, default modernized/>
