# Revision review and fixes

## Additional knowledge, setup and failure analysis

This follow-up added a visible standard/applications catalog, evidence-based
classification, offline preflight, frozen per-process knowledge, UI inspection
and explicit agent instructions. Independent reviewers reproduced the following
issues; each is fixed and covered by regressions. Final integrated validation:
**242 tests passed**, including the production HTTP workflow and automatic PPT.
The final independent control/performance review passed 80 targeted tests in
13.378 seconds without a release-blocking finding in the reviewed changes.

| Finding | Resolution |
|---|---|
| Extension-only analysis missed extensionless members or trusted misleading suffixes | Structural evidence with conflicts/unknowns retained; compatible COPY/JCL dependencies resolved conservatively. |
| Standard/custom utilities had no visible semantic contract | Versioned 17-family catalog, source/control-card requirements, editable application facts and unverified SME context; recognition never grants conversion support. |
| Utilities absent from the manifest disappeared from utility findings | Actual anchored JCL invocations retained with path/line provenance, including unnamed steps and native national-character names. |
| Mutable application knowledge could influence existing evidence | Validated snapshot and baseline frozen at intake; Resume and coverage use the original snapshot. |
| Populated malformed Markdown/Excel rows were silently skipped | Every populated intake row is validated; missing identifiers, fractional/bool order values and normalized job collisions are rejected before intake. |
| Exported target accepted malformed input while the harness pre-rejected it | New target contract embeds guards; every invalid record enters generated Python; guard mutations and job rejection behavior are tested. |
| New guard ordering changed after canonical ledger serialization | Sorted version 2 field handling; target and case roundtrip regression; original version 1 fingerprints unchanged. |
| Unused exports inflated selected portfolio counts | Selected versions derived from per-process membership; discovered inventory reported separately. |
| SQL comments/literals inflated table references | New classification path masks comments/literals and labels conservative static references; no estate-inventory claim. |
| New guard/knowledge work exceeded the original HTTP deadline | Compile each checked target once per suite/mutant and project small durable controls; retain every record/checkpoint; original deadline passes. |
| Small newline-heavy input could create millions of coverage rows | Shared 100,000 aggregate physical-line bound enforced before immutable intake/analysis. No truncation. |
| Setup could report success after diagnostic failure or erase custom knowledge | Explicit failures stop setup; initialization never overwrites application edits; preflight separates readiness from support/connectivity. |

The operating matrix in `OPERATIONS.md` records native data, utility, scheduler,
transaction, recovery and environmental requirements. The standard reference
links IBM documentation; Zowe setup/read-only guidance was also checked through
the user-requested Context7 plugin. All source operations remain read-only.

## Earlier foundation review

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
