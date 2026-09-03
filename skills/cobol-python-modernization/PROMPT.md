# Devin Invocation Prompt

Use the `cobol-python-modernization` skill for this task.

I am providing an Excel workbook containing one or more batch jobs. Its columns identify job, step, program, inputs, and outputs (header spelling may vary). Use the repository and branch I identify as the source of truth and discover everything else yourself. Do not ask me for COBOL/JCL/DB2 details that can be found in the branch. Record the exact source commit and SHA-256 of the workbook before generation.

For every distinct job, trace the complete source JCL and every program/artifact it references: COBOL, copybooks/includes, PROCs, DB2 SQL/tables, utilities, sort/control cards, file definitions, called programs, and relevant working/converted code. Production/source behavior is authoritative; working/converted code is supporting evidence only unless source proves equivalence.

The migration requirement is **behavioral preservation**. Mirror exactly what the source does, even when that behavior appears incorrect, inconsistent, redundant, inefficient, or defective. **Do not fix, reinterpret, normalize, optimize away, or redesign legacy logic.** Preserve quirks, suspicious predicates/calculations, truncation, ordering, duplicate behavior, null/default behavior, error handling, commit behavior, return codes, partial-output behavior, and restart/rerun semantics when source evidence shows them. You may flag suspicious behavior in lineage/validation, but do not change it in Python. A suspected source bug reproduced exactly in Python is parity; changing it is a migration defect.

Create one output folder per job and follow the skill output contract exactly. At minimum each job contains `lineage.md`, one fully commented/documented `job.py`, `run.jil`, `oracle.sql`, `sqlite.sql`, `validation_report.md`, `traceability.json`, and `tests/test_job.py`. Every Python function must explain in plain English its Purpose, Inputs, Outputs, Side effects, Failure behavior, and Rule IDs. Apply Ponytail v4.9.0 only after fully understanding source behavior, and only to reduce unnecessary implementation complexity without changing outcomes.

The Python and JIL must mirror the complete job and every program underneath it. Extract every source rule, assign a stable rule ID, and trace source → lineage → Python → test. Tests must prove source behavior, including legacy quirks; do not write expectations for what the logic "should" do. Use SQLite to execute and validate database behavior now and make Oracle DDL/data-access boundaries ready for later Oracle replacement. If SQLite/Oracle cannot reproduce a DB2 behavior exactly, document the mismatch and block 100% rather than silently choosing different semantics.

The `validation_report.md` is the definitive comparison artifact. Start with an executive summary, then create a **Rule Parity Matrix** covering every Rule ID. For each rule show: the COBOL/JCL/DB2 source code evidence; what that source code does in **plain English**; the matching Python code evidence; what the Python does in **plain English**; the validation/test evidence; and a PASS/FAIL/UNVERIFIED parity result. If a rule fails, explain in plain English the exact discrepancy, evidence-backed root cause, observed impact, the specific remediation required to make Python mirror the source, and what must be revalidated afterward.

The review must be **evidence-only**. Do not make any unsupported factual claim about source behavior, Python behavior, root cause, impact, or remediation. Every material conclusion must point to source/Python/test/reconciliation evidence. If evidence is insufficient, say `UNKNOWN — UNVERIFIED` or `UNKNOWN — additional source tracing required`, add the item to `traceability.json.unsupported_claims` or `unresolved`, and keep the job at 0%. Never fill an evidence gap with a plausible explanation. Preserve suspicious legacy behavior when Python matches it and label it `PASS — PRESERVED LEGACY BEHAVIOR` rather than treating it as a migration defect.

Run functional validation with source-derived fixtures and SQLite, obtain at least 80% coverage across generated `.py` files, then perform the independent adversarial review plus final security/defect checks. A job may receive **100%** only when every discovered behavior is accounted for and mirrored, every rule is traced and tested, validation-report/documentation/provenance gates pass, coverage is at least 80%, reconciliation passes, `unsupported_claims` is empty, and there are zero unresolved migration mismatches or introduced security/functional defects. Otherwise fail closed and score 0%.

Repository: <OWNER/REPO OR LOCAL PATH>
Branch: <BRANCH>
Excel: <PATH TO XLSX>
Output root: <OUTPUT DIRECTORY, default modernized/>
