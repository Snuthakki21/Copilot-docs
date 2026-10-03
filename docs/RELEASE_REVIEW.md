# Revision review and fixes

A fresh independent reviewer inspected the entire workbench and reproduced failures rather than accepting implementation-owner claims. All reproduced high/medium findings were fixed and independently rechecked. The reviewer ran 85 focused integration tests, then 51 final recovery/runner/coverage tests after the last corrections; both runs passed. Final integrated and transport checks are recorded in VALIDATION.md.

| Finding | Fix and regression evidence |
|---|---|
| Incomplete source reporting and ambiguous conversion percentages | Every supplied file/line is preserved in JSON/CSV/XLSX/HTML with explicit scope, target spans/versions, witnesses, reasons and replacement. Separate applicable-line, unit and known-rule denominators. |
| COBOL sentence periods, malformed literals, string comments/collation, division ambiguity and storage lifetime could lose semantics | Quote-aware parsing, complete grammar and LINKAGE/USING profile; unsupported behavior blocks. Source/dependency hashes pin target provenance. |
| Ignored JCL DD/trailing options, ambiguous jobs and unsafe conditions | Exact cards/manifest reconciliation and validated RC grammar; native I/O/scheduler behavior stays blocked. |
| Mutation covered only an initial predicate or missed budget obligations | Every modeled decision/boundary/effect is mutated. Surviving masked effects and missing mandatory witnesses are explicit gaps. |
| Active-stage locks delayed controls; failed-stage Pause broke Resume | Short control locks, durable callbacks, allowed-state guards, bounded retries and checkpoint-aware cancellation. Reports preserve cancelled/incomplete evidence. |
| Recovery could skip verification, double-count history or spend another packet quota | Durable stage replay, frozen packet reuse, atomic report/history/terminal acceptance and preserved one-return quota. Failure/crash tests exercise real storage. |
| Changed manifest could still receive credit, repeated Start or bundle | Creation-time raw-byte manifest hash and parsed identity/job checks across boundaries. Changed/missing baselines fail closed without silently repinning. |
| Altered SQLite or issued companions could be delivered as original evidence | All registered artifacts are hash-bound; SQLite is explicitly closed, opened read-only and reconciled against exact frozen actual rows/schema. Changed targets/downloads/bundles are refused. |
| Context/Metadata could change without invalidating returned checklist | Exact frozen content, labels, dimensions, sheets, identities and formula checks before accepting the one return. |
| Oversized question/evidence silently truncated into an impossible return | Bounded human-facing display with complete immutable Context detail, UTF-16 cell/document preflight and actual exported-workbook validation before quota issuance. |
| Failed/crashed packet draft poisoned strict folder validation | Private same-filesystem staging outside process folders, normal cleanup and hard-crash/restart regression. |
| Unknown source inherited unrelated comment syntax | Comments are source-kind/grammar-aware. Unknown behavior remains applicable and blocked. |
| Final deck omitted its just-completed process | One consistent projected final metric model, accepted atomically; demos/blocked work get no completion credit. |
| New gates made blocked reports inaccessible or prevented older workspaces starting | Intact pinned diagnostic reports remain downloadable. Unbaselined legacy evidence is preserved/uncredited; new blocked reports and new intake work without repinning or executing legacy targets. |
| MCP negotiation/session headers/catalog cursors were ignored | Validated supported-version negotiation, case-insensitive sessions, matching bounded SSE and paginated typed catalogues with complete/partial evidence. |
| Folder prose could be bypassed by UI/programmatic writers | One shared prompt and agent entrypoints, strict root/process allowlists and core guards before mutation/registration. Private scratch is designated, not allowed by arbitrary name prefix. |
| Invalid uploads returned generic failures or changed local source bytes | Bounded JSON stream, named malformed/type/UTF-8 errors, strict browser text decoding, byte-exact CRLF snapshots and cleared rejected selection. |
| Dependencies were only directly pinned | Complete 21-package/419-hash lock, official registry digests, clean install/pip check, idempotent bootstrap and verified Windows wheel set. |

The five previously deferred smaller findings are resolved: controls/Cancel UI, accurate LOC label, stale unbuilt master-prompt text, Context integrity and complete hashed dependency packaging.

This review establishes regression evidence within the supported profile. Remaining capabilities are stated in MIGRATION_CONTRACT.md: broad/native COBOL, CICS/SQL/dataset/scheduler adapters, live integrations and observed legacy parity are not certified. The source interpreter and extractor share a parser, and finite synthetic testing cannot prove absence of every defect. Native Windows/browser/PowerPoint validation is disclosed separately; Artifact Tool slide rendering is not PowerPoint execution.
