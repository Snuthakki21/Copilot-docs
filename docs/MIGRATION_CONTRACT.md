# Implemented contract and limits

This release implements the operator workflow for **flat, record-based COBOL predicates**. The full master prompt is the desired modernization contract; unsupported requirements below remain explicit implementation gaps. A prompt cannot supply missing source semantics, credentials or a safe execution sandbox.

| Area | Implemented | Boundary / next adapter |
|---|---|---|
| Source | Complete original line-order accounting, hashes, supported copybook field layouts, program inventory | Flat IF/ELSE/END-IF; comparisons and AND/OR; literal MOVE, CONTINUE, GOBACK/STOP RUN. No nested IF, PERFORM, READ/WRITE, arithmetic, SQL, CICS, REDEFINES, OCCURS, signed/packed decimals or continuation. |
| Layouts | Unsigned PIC 9 and fixed-width PIC X, simple 01/05/77 declarations, defaults, group-correlated fixtures | JSON record transport; not EBCDIC, packed binary, COMP-3, VSAM or native dataset serialization. |
| Conversion | Audited generated Python for fully supported programs, immutable shared versions | Source-order rule behavior is preserved; syntactic line-for-line Python correspondence is not claimed. Unsupported programs receive no full executable translation. No code is silently retired as mainframe-only. |
| Jobs | Named method per job, ordered steps and RC comparisons; actual record-adapter job comparison | Same field-name sets required between programs. One integration baseline, not exhaustive path testing. DSN reads/writes, external scheduler, procedure expansion and restart semantics require adapters. |
| LLM | Explicit opt-in excerpts, bounded structured analysis, suggestions in the SME packet, reported token usage | No autonomous arbitrary generated-code execution, auto-repair, unrestricted tools or generic agent-loop implementation. |
| Synthetic data | Deterministic seed, layout bounds, threshold neighbors, matching/mismatching attributes, grouped records, bounded interactions | Maximum 256 cases per program; branch-outcome coverage for the modeled IR only. No claim of every possible record/path/condition combination. |
| Oracle | Independent source IR interpreter freezes expected results before generated Python execution | Both depend on the parser; parser errors remain a shared risk. No observed mainframe oracle or mainframe execution. |
| Verification | Full output/trace/RC comparisons, independent source-order job interpretation, deliberate predicate mutation, denied import checks | Input rejection occurs in the JSON adapter. No native mainframe malformed-record semantics are claimed. Unit suite and mutation checks do not substitute for actual legacy execution evidence. |
| SME | One frozen packet / one valid return per process, immutable question identity, Yes/No/Not sure, corrections retained | Corrections requiring new semantics remain blockers. A Yes on an unsupported-item description does not make its conversion supported. |
| Knowledge | One input Markdown file, versioned confirmed facts in SQLite and one JSON/index pair | No semantic cross-process auto-approval or autonomous interpretation of corrected prose. |
| Connectors | Typed read-only Zowe CLI and authenticated Db2 MCP/gateway; partial catalog discovery | Credentials, IBM drivers and source exports must be supplied. No preapproved schema list required. Automatic multi-location dependency resolution is not yet implemented. |
| UI | Local React intake/prompt/file workflow, real stage events, rules, source accounting, lineage cards, review import and report downloads | No target business CICS screen modernization in this subset. Workbench screens and control APIs are not counted as business replacements. |
| Reporting | Editable PPT, XLSX/CSV/JSON, snapshots, unique/membership metrics, LOC, supported rule tests and blockers | CICS/VSAM/interfaces unknown until evidenced. Db2 metric is distinct references in supplied SQL, not a confirmed estate table count. Physical/code LOC convention differs by source kind and is not equivalent complexity. |
| Inspection | PPT reopened, editable table count and canvas bounds checked, hashes recorded | No PowerPoint/LibreOffice rendering or visual clipping certification in this environment. Browser rendering and Windows launch remain unverified. |

## Metric rules

Source assets deduplicate by kind, name and SHA256. Process memberships count references separately. Production portfolio totals exclude processes created with the UI demo flag. Revisions with changed hashes count as distinct versions, not necessarily distinct logical programs; titles use **versions** accordingly. Snapshot history in SQLite is retained, and the report workbook includes previous non-demo snapshots. A report is a point-in-time view before its own terminal transition.

A known rule is credited only when its SME answer is Yes, its whole supported program has no source blockers or output differences, and both decision outcomes have witnesses. `known_rule_verification_percent` divides those rules by all **extracted known rules**. It is never called total modernization percentage. Unsupported lines, unknown rules, uncertainty, omitted behavior and coverage gaps are shown separately and prevent `COMPLETED`. No “not applicable” exclusion has been implemented or credited.

`COMPLETED` means the supported source-derived POC profile finished its local tests and report checks without recorded blockers. It does not mean all possible legacy inputs were proved equivalent. `COMPLETED_WITH_BLOCKERS` records finished processing with unresolved gaps. Report failure leaves `REPORTING_FAILED`; resume retains the single-SME quota.

## Adversarial review

Each supported program receives a deterministic mutation and denied-capability check. The workbench itself receives one independent reviewer pass before publication. A configurable independent model review for each future process is still an implementation gap; the runtime report explicitly describes its deterministic review method.
