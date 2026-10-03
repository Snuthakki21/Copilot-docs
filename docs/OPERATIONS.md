# Setup, failure handling and acceptance

This is the operating checklist for an application owner, SME and Copilot/Claude
agent. The workbench automates the implemented POC profile after setup and one
human review. Recognizing a mainframe file or utility does **not** mean that its
behavior can be converted by this release. Unknown or unsupported behavior
stays visible and prevents successful completion. No finite test suite can
guarantee every possible failure or input has been covered.

## What you provide once

| Input | Put it here / action | Why it is needed |
|---|---|---|
| Workstation | CPython 3.12, local writable disk, setup script; use the committed UI bundle | Installs locked dependencies and avoids a Node requirement for operators. Native Windows execution still needs a workstation smoke test. |
| Application export | `WORKSPACE/Endeavor/` | Complete, readable UTF-8 source export with original relative member names. Include called programs, COPY dependencies, JCL, PROCs, INCLUDEs, control cards, BMS and SQL/DDL where applicable. A manifest alone cannot replace missing source. |
| Initial process | Markdown following `examples/process-input.md`, or the UI Excel template | Ordered jobs, steps, program/utility names, input/output groups and conditions. A new source version uses a new process ID. |
| Custom knowledge | `WORKSPACE/knowledge/application-knowledge.json`; start with `examples/application-knowledge.json` | Application/vendor utilities, aliases, semantics, evidence, record layouts, control-card behavior and known dependencies. The standard catalog is visible in `knowledge/mainframe-catalog.json`. |
| Background articles | `WORKSPACE/knowledge/inbox/context.md`, up to 16 KB | Devin/application notes. Treated as unverified evidence, never executable instructions or approval. |
| Zowe, when used | Authenticated CLI profile; `WB_ZOWE_PROFILE` | Account-visible read-only catalog/source operations. Profile presence is not successful authentication or complete discovery. |
| Db2, when used | Authenticated typed MCP URL/token; IBM ODBC driver and `pyodbc` for the bundled gateway | Schema/table descriptions without a prior schema allowlist. Discovery and sample access are distinct; no arbitrary SQL or automatic row sampling. |
| LLM, when used | Approved endpoint, model and token; explicit source-egress setting | Optional bounded suggestions. It does not enlarge the deterministic converter's supported syntax. |
| Actual SME return | One issued checklist, completed by the real reviewer; import once with attribution | Confirms or corrects interpretations. Unanswered/No/corrected items remain unresolved; no second questionnaire is generated. |

Private environment variables are set in your shell before launch. `.env.example`
is an example, not an auto-loaded credential file. Do not paste credentials into
source, knowledge, intake or review files. Stop the running UI before starting a
CLI Coordinator against the same workspace.

## Preflight and one-button operation

After setup, run:

```sh
python -m workbench.preflight --workspace WORKSPACE --manifest MANIFEST --json
python -m workbench.runner run --workspace WORKSPACE --manifest MANIFEST
```

The UI Setup screen offers the same local checks. `READY` means local setup can
proceed to analysis; it does not mean the process is convertible, a network
connection was reached, or mainframe equivalence was proved. Inspect
`conversion_status`, the individual checks and named remediation. Preflight
does not connect to the mainframe or modify it. The core workflow also validates
input placement, catalog schema and immutable snapshots, even if an agent
forgets preflight.

Start creates immutable input and knowledge snapshots. Analysis classifies every
supplied file, extracts supported behavior, records unresolved utilities and
issues one comprehensive SME packet. Importing the authentic return triggers
synthetic generation, Python execution, comparison, adversarial mutation checks,
coverage and the management PPT. Download the final bundle. A bounded CLI wait
may expire before completion; inspect status and Resume. Do not create another
process merely because a command timed out.

`knowledge/application-knowledge.json` is editable before a new process. Each
process freezes the exact standard and custom knowledge in
`processes/PROCESS_ID/analysis/mainframe-knowledge.json`. Editing the current
catalog cannot rewrite a prior process's interpretation or consume a second
review. Historical runs created before catalogs retain their original analysis
format and do not gain classification evidence retroactively.

The POC intake limit is 200 files, 512,000 UTF-8 bytes per file, 8 MiB combined
and 100,000 physical lines combined. Coverage requires a row for every line;
the line cap prevents a small newline-heavy export from exhausting report
memory or Excel row capacity. Over-limit exports are rejected, never truncated.
Use a complete process-scoped export within these bounds; do not omit required
dependencies to make it fit. Larger real processes need a tested streaming
analysis/report extension before this release can accept them. The single SME
packet supports at most 2,000 items; mandatory synthetic witnesses must fit the
recorded 256-case-per-program budget or remain an explicit verification gap.

## Failure and recovery matrix

| What can go wrong | Detection / treatment | Required action or remaining boundary |
|---|---|---|
| Excel declares a smaller range than its actual job rows, has duplicate/out-of-bounds cells or malformed XML | Intake checks actual worksheet cell locations against declared dimensions before reading job rows; malformed structure produces a named validation error | Repair the workbook using the supplied template. No hidden rows are silently discarded. XML entity/declaration checks also cover UTF-16/32. |
| Wrong Python, missing package/wheel, broken UI bundle | Setup exits on failure; preflight checks runtime, dependencies and assets | Use the supported environment and locked installation. Do not ignore install errors. |
| Full/read-only disk, unsuitable shared filesystem | Preflight checks access/capacity; writes fail explicitly and retain state | Use local disk with headroom and backups. Filesystem behavior, antivirus interference and sudden hardware failure cannot be certified by a permission check. |
| Two workers, occupied port, browser opens early | Single-writer OS lock; optional port diagnostic; launch scripts check failures | Stop the other owner, then restart. Never delete the lock or ledger to bypass the check. |
| Missing/partial/truncated source export | File/byte bounds, manifest resolution, classification and full-line accounting | Supply complete exports and dependency lists. Account-visible discovery cannot prove that inaccessible libraries do not exist. |
| Binary/EBCDIC data mistaken for UTF-8 source | Text decoding/intake bounds; unrecognized content stays blocked | Export source as text without changing program columns. Keep business data formats in the custom knowledge; native record conversion needs an adapter. |
| Member has no suffix, misleading suffix or multiple plausible types | Content evidence plus names, COPY references and manifest context; conflicts recorded | Inspect classification evidence. Unknown/conflicting files remain in scope and are not excused as comments. |
| Case-only, Unicode-normalized, file/directory or reserved-name collision | Intake rejects ambiguous source paths before writing a process | Preserve unique portable relative names and explicit library provenance. Do not let Windows overwrite a member silently. |
| Duplicate member/program across libraries | Ambiguous dependency or program identity rejected | Supply the actual search order/version provenance; current converter does not infer STEPLIB/COPY resolution across libraries. |
| Malformed/partly blank intake row or colliding job method | Strict Markdown/Excel row, identity and ordering validation | Fix the named row before Start. No populated row is silently dropped. |
| JCL PROCs, symbols, INCLUDEs, conditions, GDGs, DD concatenation or DISP | Recognized/accounted; unsupported native semantics block credit | Add a source-supported adapter with expansion, lifecycle and error/restart tests. Never delete allocation behavior merely because IEFBR14 does no program work. |
| Standard utility name recognized but semantics differ by site/version | Catalog captures evidence, risks and needed inputs; no utility adapter inferred | Supply utility version, options, control cards, exits, return codes and side effects. SORT may be a site-selected product. |
| Custom utility/wrapper hides calls, filters or side effects | Editable application catalog and unresolved utility findings enter the one review | Document underlying programs, files, controls, RCs and failures. A catalog entry does not execute code or turn support on. |
| COBOL compiler or storage semantics differ | Unsupported constructs explicitly blocked | Record compiler/options, decimals, signs, truncation, rounding, overflow, padding, collating sequence, REDEFINES/OCCURS, working storage and run-unit lifetime. Implement and test each needed adapter. |
| SQL/Db2 and SQLite differ | SQL behavior remains unsupported; discovered references are not converted tables | Resolve nulls, decimals, CCSID/collation, timestamps, isolation, commits/rollback, cursors, SQLCODE, constraints and concurrency before claiming parity. |
| VSAM/IMS/MQ/files are not ordinary SQLite rows | File families/utility risks retained; native I/O not credited | Preserve access mode, record/key layout, duplicate keys, status codes, locks and transaction/message semantics. |
| CICS screen appears mapped but actions differ | BMS/source inventory retained; no business UI/API credit without implementation | Capture map fields/attributes, AID keys, validation, state, navigation, COMMAREA/channels and transaction/security behavior. Workbench UI screens are not replacements. |
| Scheduler/external interface unavailable | Scope questions and source blockers; job adapter covers only the declared bounded profile | Include calendars, triggers, time zones, cutoffs, dependencies, endpoints, acknowledgments and retries. Python step order alone is not CA7 parity. |
| Connection denied, token expired, TLS/proxy/driver mismatch | Configuration separated from live/partial discovery evidence; bounded retries/timeouts | Repair the actual account/driver/certificate. Never disable read-only enforcement or infer empty catalog means no assets. |
| Discovery pagination ends at a limit or data changes mid-scan | Cursors, counts and partial/complete account-visible evidence | Preserve the cursor and timestamps. Current discovery is not a transactional estate snapshot or automatic dependency fetcher. |
| Source/target/catalog/SME/report bytes changed | Recorded immutable hashes, source/analysis replay, return identity and artifact checks | Restore an intact backup or start a separately identified process from the original evidence. Never recalculate hashes to certify modified history. |
| Stale knowledge or hostile instructions in source/notes | Data-only bounded catalog; frozen provenance; no executable catalog fields or automatic approval | Review evidence for this source/version. Prior confirmations are interpretations, not permission to execute commands or approve changed rules. |
| Too few or unrealistic synthetic records | Source-derived mandatory branches/boundaries/matches, deterministic interactions and witness counts | Record missing obligations explicitly. Four sample rows cannot certify 85 rules; 256 cases is a budget, not exhaustive coverage. |
| Expected results copied from target | Expectations frozen from independent source IR before target execution | Shared parser remains a common-mode risk; SME/source review and mutation checks help but cannot establish observed legacy parity. |
| Invalid data accepted by exported Python | New target contract embeds input validation; direct target rejection is tested | Distinguish malformed input rejection from business-rule failure. JSON validation is not proof of native malformed EBCDIC-record behavior. |
| Good tests miss a rule, overwritten effect or incorrect boundary | Per-rule mutation checks and explicit surviving/missing witness gaps | Treat masked or surviving mutations as unresolved; do not invent passing evidence. |
| Crash, pause, cancellation, duplicate Start/return or expired wait | Durable stage state, bounded retries, idempotent matching return, quota and cancellation checks | Resume the recorded stage after resolving the cause. Do not rewrite outputs or reissue a checklist. |
| Partial SME response or a correction requires new semantics | Actual answer/correction retained; no automatic Yes or second round | Deliver the blocked report with exact unresolved items. One review cannot guarantee all unknown business facts will be resolved. |
| Misleading completion percentages or double counts | Full-line, semantic-unit and known-rule denominators separated; unique versions vs memberships | Use counts with scope/evidence labels. Unknown is not zero and lines of code are not equivalent complexity. |
| Report generated but missing/damaged | Inspection, metric consistency, report hashes and terminal acceptance gate | `REPORTING_FAILED` is not completed. Preserve evidence, repair the named cause and Resume. |
| OS/native application behavior differs from test host | Published validation identifies tested and untested environments | Run the real workstation/Zowe/Db2/provider smoke checks. Browser rendering and native PowerPoint need local confirmation. |

## Acceptance before calling a process done

- Every exported file and physical source line has a disposition. Missing or
  unclassified source remains visible; omitted behavior has a specific reason.
- A mainframe-specific omission has a concrete replacement, target mapping and
  verification before it is credited. Unsupported does not mean unnecessary.
- Source-derived expected records, executed outputs, mismatch details, failed
  tests, witness/mutation coverage, target versions and the actual human return
  are preserved and reproducible.
- Shared targets remain content-addressed; process outputs stay under the seven
  process categories. No credentials or live application exports enter git.
- The management deck and reports show the same accepted metric snapshot,
  before/after scope, LOC, rules, programs/copybooks, screens/APIs, data assets,
  interfaces and unresolved/unknown counts without inventing missing metrics.
- `COMPLETED_WITH_BLOCKERS` means processing finished with unresolved work.
  `COMPLETED` certifies only this bounded local POC profile, never production
  readiness, every possible scenario or observed mainframe equivalence.

Standard utility/source knowledge and official references are maintained in
[knowledge/README.md](../knowledge/README.md). Detailed implemented limits are in
[MIGRATION_CONTRACT.md](MIGRATION_CONTRACT.md). Agents execute
[START_MODERNIZATION.md](../prompts/START_MODERNIZATION.md) and must read these
files before interpreting native behavior or extending support.
