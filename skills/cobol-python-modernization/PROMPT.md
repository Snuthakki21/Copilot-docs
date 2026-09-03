# Devin Invocation Prompt

Use the `cobol-python-modernization` skill for this task.

I am providing an Excel workbook containing one or more batch jobs. Its columns identify job, step, program, inputs, and outputs (header spelling may vary). Use the repository and branch I identify as the source of truth and discover everything else yourself. Do not ask me for COBOL/JCL/DB2 details that can be found in the branch.

For every distinct job in the Excel file, trace the complete source JCL and every program/artifact it references: COBOL, copybooks/includes, PROCs, DB2 SQL/tables, utilities, sort/control cards, file definitions, called programs, and relevant working/converted code. Production/source behavior is authoritative; working/converted code is supporting evidence only unless the source proves equivalence.

Create one output folder per job and follow the skill output contract exactly. At minimum each job must contain `lineage.md`, one fully commented `job.py` containing all job business logic, `run.jil` for Autosys execution, `oracle.sql`, `sqlite.sql`, `validation_report.md`, `traceability.json`, and `tests/test_job.py`. Use SQLite to execute and validate database behavior now; make Oracle DDL and Python DB boundaries ready for later Oracle replacement. Prefer Python standard library and approved dependencies already available through the enterprise Artifactory; do not pull arbitrary public packages. Apply Ponytail v4.9.0 principles only after fully understanding the source.

The Python and JIL must match the complete job intent and all programs underneath it, not merely translate syntax. Extract every source rule, assign a stable rule ID, and trace it from source → lineage → Python → test. Preserve file semantics, DB2 behavior, numeric precision, ordering, conditions, return codes, restart/rerun behavior, failures, and outputs. Explain the JCL and each program in plain English before the detailed mapping so both executives and interns can follow it.

Run functional validation with source-derived fixtures and SQLite, obtain at least 80% coverage across generated `.py` files, and then perform the skill's independent adversarial review plus final security/defect checks. A job may receive a **100%** rating only when every discovered rule is traced and tested, coverage is at least 80%, SQLite/file reconciliation passes, and there are zero unresolved source behaviors, introduced defects, or open security findings. If anything is missing or unverifiable, fail closed: still produce the evidence-backed artifacts and blockers, but score the job 0% rather than guessing.

Repository: <OWNER/REPO OR LOCAL PATH>
Branch: <BRANCH>
Excel: <PATH TO XLSX>
Output root: <OUTPUT DIRECTORY, default modernized/>
