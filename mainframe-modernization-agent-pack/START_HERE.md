# Mainframe modernization kit, revision 3

## What this is
A reusable, platform-neutral nine-role agent specification with a controlled workflow, target architecture assessment, memory, review, evidence and reporting design. It is not an installed agent framework, a completed repository inventory, or a working migration. No source-system or target connections have been exercised. All measurements begin as unknown until collected.

Only four maintained configuration/instruction files are supplied:
1. START_HERE.md — this operating guide, including the prompts you use
2. AGENTS.md — role instructions, evidence contracts, metric definitions and quality gates
3. PROJECT.yaml — your process, repository scope, connection settings and target-profile choices
4. MEMORY.md — a small current-state index, never a second specification

Start in a fresh approved workspace. Replace the previous pack's instructions with this revision; do not load both sets. Preserve any real project evidence, decisions and work, and have the coordinator reconcile them before proceeding. This pack does not delete older project work.

Revision 3 changes: discovery and business specifications are target-neutral; architecture assessment now precedes target-specific implementation; application-code generation and database/schema/data-script generation are separate roles; runtime, storage, scheduler, messaging and UI choices are independent. It adds explicit category coverage and profile-specific evidence while preserving the earlier full-repository inventory, one-to-one atomic rules/utilities, SME-then-user gates, human review, matched parity and memory/token controls. Python/SQLite remains an optional local reference profile.

## Target choices and confirmed GCP components
The requested GCP data target is BigQuery and its scheduler/orchestrator is Cloud Composer (Apache Airflow). These component choices are recorded; they do not yet approve the complete architecture or implementation. Assess the discovered behavior/workload and complete the independent dimensions before approving a versioned profile:
- Application language: Java, Python or C# on .NET, with exact runtime/toolchain versions
- Database/storage: SQLite for an assessed local/reference use, Oracle with its edition/version, or a specifically named and approved GCP data service with engine/dialect where applicable; assess file/object storage separately
- Deployment platform/runtime: approved local, on-premises or cloud environment, with exact execution service, topology and constraints
- Scheduler/orchestration, messaging/integration and UI: separate assessed choices, each backed by discovered contracts or an evidence-backed not-applicable decision

GCP is a platform, not a single database. BigQuery is an analytics data warehouse with supported DML and ACID multi-statement transactions, subject to documented limits; it is not a drop-in transactional Db2 replacement. Here the user explicitly chose BigQuery and Cloud Composer; do not ask them to choose those components again or silently substitute another GCP database. Application execution runtime, messaging/MQ replacement and UI remain open for assessment. Cloud Composer DAG definitions use Python; they can orchestrate separately selected Java, Python or C#/.NET workloads through approved operators/execution services. Choosing Oracle does not choose a deployment platform. The pack supplies assessment and generation contracts, not a claim that every combination is supported. Unsupported required behavior blocks that profile or slice until resolved. Optional Python/SQLite is neither an automatic target selection nor proof of parity for Oracle or the BigQuery/Composer profile. Verify BigQuery numeric/rounding behavior, unenforced primary/foreign keys, transaction boundaries and costs, and Composer dependency/calendar/retry/restart semantics before implementation.

## The workflow, in the exact order
| Stage | What the agent does | What you review / exit evidence |
|---|---|---|
| 0. Set up | Confirm repository/export folder, ordered jobs, source access, permitted extraction location, privacy constraints, reviewers and tool versions | One grouped list of missing inputs; no invented permissions; target preferences may remain unconfirmed |
| 1. Inventory everything | Freeze the Git commit; enumerate all tracked files, classify logical Endevor-export objects, languages and LOC, and fill the required category coverage matrix | Repository inventory, category status, unknowns, counting rules and baseline ID |
| 2. Find this process | Trace each job through steps, programs, utilities, files, Db2, screens, schedules and interfaces using repository + approved Zowe CLI + Db2 MCP evidence | Process map, verified unique source scope %, shared objects, external objects and blockers |
| 3. Explain every part | Segment every in-scope source file; derive target-neutral smallest testable rules, utility effects and operational/interface contracts | Source-segment review packet and simple rule cards with evidence |
| 4. Get SME decisions | Show plain-English conditions/actions/examples/exceptions; resolve questions and proposed utility-only omissions | Named SME approval of exact rule/specification versions; rejected/pending remain visible |
| 5. Assess and approve architecture | Compare only relevant candidate profiles against required semantics, compatibility, security, cost and operations; define app/database/adapter interfaces | Versioned architecture and compatibility decisions approved by the user; unsupported behavior blocked; behavior changes return to SME review |
| 6. Confirm the implementation | Present bounded segments, SME-approved rules, approved target profile, interface handshake, mappings and tests | Your explicit confirmation of that versioned profile-specific implementation slice; SME or architecture approval alone is insufficient |
| 7. Convert and review | Generate application code and database/schema/data scripts in separate roles; implement approved adapters; preserve 1-to-1 traceability and segment all outputs | Human review of every generated code/config/schema/script/test segment; run tests and resolve reviewer changes |
| 8. Prove parity | Compare matched mainframe/file/Db2 reference results with the actual approved target runtime, storage and services | Profile-specific record/cell/byte and behavioral evidence, including restart/failure tests; investigate all differences |
| 9. Accept the slice | Reconcile source coverage, target coverage, architecture/SME/user decisions, human reviews, tests and comparisons | Accepted only if every required gate passed for the current source, profile and target versions |
| 10. Repeat and report | Process the next ready dependency slice; regenerate simple evidence views and management PPT | Unique source process share; separate per-profile converted/reviewed/validated/accepted/remaining work; blockers and calibrated forecast |
| 11. End-to-end readiness | Test the complete job chain and relevant online/interface flows, shared consumers, peak workload and recovery; prepare cutover/rollback | Technical and business sign-off with explicit profile-specific readiness limitations |
| 12. Release, if authorized | Carry out separately approved migration/deployment/cutover and agreed post-cutover checks | Verified released version and reconciliation, or a release-ready handover if authorization is absent |

Stages 3–9 repeat for approved slices to avoid waiting for the entire codebase. Cross-slice dependencies must be resolved first. Complete the full-folder tracked-entry enumeration and classification manifest before process scoping or implementation. Unknown classifications and inaccessible content remain explicit records; only independent setup may proceed before this inventory gate. Final portfolio percentages remain provisional until object identities and the denominator are reconciled. Neutral discovery/specification can continue while target choices remain open; architecture options may be researched without generating target implementation. Architecture approval is required before target-specific generation, and changes reopen affected gates.

## Required category coverage
Treat these eight visible categories as the full supplied table for this revision: Batch COBOL program; JCL job*; JCL PROC; Copybook / record layout; CICS screen; DB2 table; CA7 schedules*; MQ interfaces. The visible Total row is an aggregate, not a ninth category. Utilities and other discovered dependencies must also be covered. AGENTS.md defines the evidence and status matrix.

The supplied image does not establish any numeric cell values or asterisk-note meanings. Preserve the labels, leave counts unknown until measured, and do not invent footnotes. Another image is not required to use or complete this pack. Category presence and relevance must be established from project evidence; not-applicable needs an explicit reviewed reason and is never permission to drop business behavior.

## What “review every piece of code” means
Every in-scope source line and every delivered target line belongs to a stable review segment. Use cohesive paragraphs/functions/SQL blocks/control-card sections, not arbitrary cuts. Start around 30–100 substantive lines per segment where practical; record an exception for cohesive larger units. These sizes are review ergonomics, not a complexity standard.

Declarations, copybooks, utility controls, orchestration, schemas, data scripts, tests, configuration, UI and generated adapters are included. Non-executable ranges are labeled and accounted for, not hidden. Shared helpers are reviewed once per applicable version/profile, with consumer-specific mappings/tests. Segment records include exact path, line range, content hash, reviewer, disposition, comments, rules and evidence. A change invalidates affected approvals. An AI review never substitutes for required human review.

A business SME approves what the rules should do. A designated technical reviewer approves code. You approve the architecture and confirm the implementation scope. If one person fills multiple roles, record those decisions separately. Nobody should be forced to pretend they understood technical code just because they understood a business example.

## The simple evidence you get
One review packet with three generated views, all from the same tracking database:
- Business rules: “When / do this / otherwise / example / exception / your decision”
- Code segments: source section, target profile/section, what changed, reviewer status and tests
- Comparison evidence: same input/state, legacy result, named target-profile result, difference and pass/fail/blocked

Every card links to its underlying source snapshot, exact code/profile version and test result. Architecture and category coverage are navigable views from the same records. Counts are useful summaries; they never replace detailed comparisons.

## Minimal and stable workspace
```
START_HERE.md       AGENTS.md       PROJECT.yaml       MEMORY.md
.migration/
  ledger.sqlite        # canonical tracking store; independent of target database choice
  evidence/            # immutable approved extracts, manifests and reference results
  cache/               # reproducible parsed/indexed data keyed by content/context hash
src/<profile-id>/       # chosen application language and approved runtime adapters
schema/<profile-id>/    # chosen database DDL/migrations/data scripts; manifests include ownership
tests/                 # shared source fixtures + profile-namespaced tests and results
reports/
  review.html          # current business + source/target + architecture review packet
  progress.pptx        # current management presentation
  metrics.csv          # exact figures underlying the presentation
  archive/             # versioned approved/reporting snapshots only
```
The SQLite migration tracking ledger is separate from every target application's database/storage. Keeping the ledger in SQLite does not require target SQLite. Target paths or approved environment aliases live in each profile in PROJECT.yaml; no credentials belong there. Do not create extra Markdown status reports, duplicated rules or per-agent diary files. New top-level paths require a reason recorded in the ledger. Files produced by prescribed build/test tools can use their normal directories, registered in the manifest. Temporary output stays in cache; source evidence and approvals are never discarded as cleanup.

## Prompts to use
### First run
Read AGENTS.md and initialize this workflow from PROJECT.yaml. My initial source inputs are the ordered jobs and the configured GitHub export folder. Inventory the entire repository scope and required category matrix before reporting this process's share. Use approved read-only Zowe and Db2 MCP access to resolve dependencies. Produce the segmented source review and target-neutral plain-English SME rule packet. Assess the requested BigQuery + Cloud Composer profile, or another explicitly requested profile, without silently choosing remaining services or replacing these selected GCP components. Do not implement until SME decisions, architecture approval and my explicit profile-specific slice confirmation are recorded. Keep state in the ledger and compact MEMORY index. Ask one grouped question for missing required inputs; continue safe independent work. Treat the eight visible categories as the full supplied table; do not wait for another image or invent counts.

### Resume
Resume from PROJECT.yaml, MEMORY.md and the ledger's current state. Retrieve only the relevant AGENTS sections and evidence ranges. Check source/decision/profile/interface/code freshness, reuse applicable verified answers, invalidate affected work when needed, and continue the next authorized slice. Do not restart completed discovery. Stop at the next required human decision with a simple review packet.

### Record SME decisions
For rule IDs [IDs], the SME [name/role] decided [exact answer], applying to baseline/spec version [version]. Record the answer and its scope, retain source-observed behavior separately, and show affected segments/tests. Ask if the interpretation is ambiguous. This decision does not authorize implementation by itself.

### Assess and approve the target architecture
Compare application language [Java / Python / C# on .NET], database/storage [Oracle / optional SQLite reference / requested BigQuery], deployment/runtime [constraints], scheduler [Cloud Composer for the requested GCP profile], messaging and UI against the approved source requirements. Leave undecided choices open. Show supported-by-evidence, unverified and blocked behaviors, service/version assumptions, security, operations and cost evidence. Present the exact profile and app/database/adapter interface contracts for my approval before target-specific implementation. Record approval of profile [ID/version/hash] only when I explicitly give it; assessment alone grants no implementation or provisioning permission.

### Confirm implementation
I confirm implementation of slice [ID], approved specification [version], approved target profile [ID/version/hash] and interface contract [version/hash], including rule IDs [IDs] and the listed source-to-target mappings, within the approved local workspace using approved fixtures. Generate application code and database/schema/data scripts in separate roles, implement approved adapters, run authorized tests, and produce all generated-code segments for human review and legacy comparisons. This does not authorize source-system writes, production jobs, restricted data export, cloud provisioning, spending, deployment or cutover. Save this exact authorization, its versioned slice/profile membership and limitations in the ledger. Advance that slice/profile's authorized milestone to LOCAL_IMPLEMENTATION_REVIEW_AND_VALIDATION in PROJECT.yaml and saved state so resume does not stop at the earlier inventory milestone. Continue within this authorization; other slices/profiles remain unapproved. If actual target validation needs additional access or permission, mark it blocked and ask rather than treating local-reference success as target parity.

### Record code review
Reviewer [name/role] [approves / requests changes to] segments [IDs] at hashes/commit [version], for profile [ID/version/hash or source-neutral], with comments [comments]. Apply only changes covered by my authorization. Reopen affected rules/approvals when behavior changes, rerun profile-specific tests and comparisons, and present new code segments for review. Do not transfer approval to changed code or another profile automatically.

### Make the management PowerPoint
Use the reporting role in AGENTS.md. Generate an editable PPTX and its metrics.csv from one frozen ledger snapshot. Show total repository scope, this process's unique source share, category coverage, complexity/risks, profile-specific segments converted/reviewed/validated/accepted, remaining work, blockers, and the evidence-based route to finish. Separate multi-target implementation totals from source process percentages. Show provisional denominators and missing measurements honestly. Validate calculations and render every slide before delivery. Do not make up a completion date or publish to others.

## Definitions you can rely on
- Converted: target implementation exists for the mapped source behavior in the named profile; this is not acceptance
- Reviewed: required humans approved the current source/rule/profile/code versions in their respective roles
- Validated: required tests and matched legacy comparisons passed on the named actual target profile and current versions
- Accepted: all required architecture, human review, SME/user, testing and comparison gates passed for the named slice/profile
- Remaining: approved planned work not yet accepted, plus separately visible unresolved/unplanned scope

## Setup and limits
Provide the exact repository and Endevor export-folder path, ordered jobs, approved source connections/destinations and reviewer roles when you start. BigQuery and Cloud Composer are already selected GCP components; language, execution runtime and any remaining choices still need assessed decisions before target generation. Do not put credentials into the files. No metrics can be computed from this kit alone. Native custom-agent installation is platform-specific; this pack works as role instructions and does not claim to register agents automatically. The language/service choices are candidates, not a tested support matrix or a production-readiness certification.
