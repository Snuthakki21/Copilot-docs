# Mainframe → Python + SQLite modernization kit, revision 2

## What this is
A reusable, platform-neutral seven-role agent specification with a controlled workflow, memory, review, evidence and reporting design. It is not an installed agent framework, a completed repository inventory, or a working migration. No source-system connections have been exercised. All measurements begin as unknown until collected.

Only four maintained configuration/instruction files are supplied:
1. START_HERE.md — this operating guide, including the prompts you use
2. AGENTS.md — role instructions, evidence contracts, metric definitions and quality gates
3. PROJECT.yaml — your process, repository scope and connection settings
4. MEMORY.md — a small current-state index, never a second specification

Start in a fresh approved workspace. Replace the previous pack's instructions with this revision; do not load both sets. Preserve any real project evidence, decisions and work, and have the coordinator reconcile them before proceeding. This pack does not delete older project work.

## The workflow, in the exact order
| Stage | What the agent does | What you review / exit evidence |
|---|---|---|
| 0. Set up | Confirm repository/export folder, ordered jobs, source access, permitted extraction location, privacy constraints and tool versions | One grouped list of missing inputs; no invented permissions |
| 1. Inventory everything | Freeze the Git commit; enumerate all tracked files and classify logical Endevor-export objects, languages and LOC | Repository inventory, unknowns, counting rules and baseline ID |
| 2. Find this process | Trace each job through steps, programs, utilities, files and Db2 dependencies using repository + Zowe CLI + Db2 MCP | Process map, verified scope %, shared objects, external objects and blockers |
| 3. Explain every part | Segment every in-scope source file, derive the smallest testable rules and all utility effects | Source-segment review packet and simple rule cards with evidence |
| 4. Get SME decisions | Show plain-English conditions/actions/examples/exceptions; resolve questions and proposed utility-only omissions | Named SME approval of exact rule/specification versions; rejected/pending remain visible |
| 5. Confirm the implementation | Present bounded segments, approved rules, target mapping and tests | Your explicit confirmation of that versioned implementation slice; SME approval alone is insufficient |
| 6. Convert and review | Implement compact readable Python/SQLite, preserving 1-to-1 traceability; segment all generated code/config/schema/tests | Review every generated segment; run tests and resolve reviewer changes |
| 7. Prove parity | Run approved fixtures and compare mainframe/file/Db2 reference results against Python files and SQLite tables | Record-level/cell-level comparison evidence plus restart/failure tests; investigate all differences |
| 8. Accept the slice | Reconcile source coverage, target coverage, SME decisions, human code reviews, tests and comparisons | Accepted only if every required gate passed for current versions |
| 9. Repeat and report | Process the next ready dependency slice; regenerate simple evidence views and management PPT | Measured converted/reviewed/validated/accepted/remaining scope; blockers and calibrated forecast |
| 10. End-to-end readiness | Test the complete job chain, shared consumers, peak workload and recovery; prepare cutover/rollback | Technical and business sign-off with explicit readiness limitations |
| 11. Release, if authorized | Carry out separately approved migration/deployment/cutover and agreed post-cutover checks | Verified released version and reconciliation, or a release-ready handover if authorization is absent |

Stages 3–8 repeat for approved slices to avoid waiting for the entire codebase. Cross-slice dependencies must be resolved first. Complete the full-folder tracked-entry enumeration and classification manifest before process scoping or implementation. Unknown classifications and inaccessible content remain explicit records; only independent setup may proceed before this inventory gate. Final portfolio percentages remain provisional until object identities and the denominator are reconciled. Source/spec changes reopen affected gates.

## What “review every piece of code” means
Every in-scope source line and every delivered target line belongs to a stable review segment. Use cohesive paragraphs/functions/SQL blocks/control-card sections, not arbitrary cuts. Start around 30–100 substantive lines per segment where practical; record an exception for cohesive larger units. These sizes are review ergonomics, not a complexity standard.

Declarations, copybooks, utility controls, orchestration, schemas, tests, configuration and generated adapters are included. Non-executable ranges are labeled and accounted for, not hidden. Shared helpers are reviewed once per version, with consumer-specific mappings/tests. Segment records include exact path, line range, content hash, reviewer, disposition, comments, rules and evidence. A change invalidates affected approvals. An AI review never substitutes for required human review.

A business SME approves what the rules should do. A designated technical reviewer approves code. You confirm the implementation scope. If one person fills multiple roles, record those decisions separately. Nobody should be forced to pretend they understood technical code just because they understood a business example.

## The simple evidence you get
One review packet with three generated views, all from the same tracking database:
- Business rules: “When / do this / otherwise / example / exception / your decision”
- Code segments: source section, target section, what changed, reviewer status and tests
- Comparison evidence: same input/state, legacy result, Python/SQLite result, difference and pass/fail/blocked

Every card links to its underlying source snapshot, exact code version and test result. Counts are useful summaries; they never replace detailed comparisons.

## Minimal and stable workspace
```
START_HERE.md       AGENTS.md       PROJECT.yaml       MEMORY.md
.migration/
  ledger.sqlite        # one canonical record store, including state, decisions and history
  evidence/            # immutable approved extracts, manifests and reference results
  cache/               # reproducible parsed/indexed data keyed by content/context hash
src/                   # compact Python implementation
schema/                # SQLite DDL/migrations
tests/                # tests and approved fixtures (directory name: tests)
reports/
  review.html          # one current business + source/target code review packet
  progress.pptx        # current management presentation
  metrics.csv          # exact figures underlying the presentation
  archive/             # versioned approved/reporting snapshots only
```
The migration tracking ledger and the application's SQLite database are separate files. Runtime application database paths live in PROJECT.yaml. Do not create extra Markdown status reports, duplicated rules or per-agent diary files. New top-level paths require a reason recorded in the ledger. Files produced by prescribed build/test tools can use their normal directories, registered in the manifest. Temporary output stays in cache; source evidence and approvals are never discarded as cleanup.

## Prompts to use
### First run
Read AGENTS.md and initialize this workflow from PROJECT.yaml. I initially know only the ordered jobs and the configured GitHub export folder. Inventory the entire repository scope before reporting this process's share. Use approved read-only Zowe and Db2 MCP access to resolve dependencies. Produce the segmented source review and plain-English SME rule packet. Do not implement until SME decisions and my explicit confirmation are recorded. Keep all state in the ledger and the compact MEMORY index. Ask one grouped question for missing required inputs; continue safe independent work.

### Resume
Resume from PROJECT.yaml, MEMORY.md and the ledger's current state. Retrieve only the relevant AGENTS sections and evidence ranges. Check source/decision/code freshness, reuse applicable verified answers, invalidate affected work when needed, and continue the next authorized slice. Do not restart completed discovery. Stop at the next required human decision with a simple review packet.

### Record SME decisions
For rule IDs [IDs], the SME [name/role] decided [exact answer], applying to baseline/spec version [version]. Record the answer and its scope, retain source-observed behavior separately, and show affected segments/tests. Ask if the interpretation is ambiguous. This decision does not authorize implementation by itself.

### Confirm implementation
I confirm implementation of slice [ID], approved specification [version], including rule IDs [IDs] and the listed source-to-target mappings, within the approved local workspace using approved fixtures. Implement, run tests, and produce the generated-code segments for human review and legacy comparisons. This does not authorize source-system writes, production jobs, restricted data export, deployment or cutover. Save this exact authorization, its versioned slice membership and limitations in the ledger. Advance that slice’s authorized milestone to LOCAL_IMPLEMENTATION_REVIEW_AND_VALIDATION in PROJECT.yaml and saved state so resume does not stop at the earlier inventory milestone. Continue within this authorization; other slices remain unapproved.

### Record code review
Reviewer [name/role] [approves / requests changes to] segments [IDs] at hashes/commit [version], with comments [comments]. Apply only changes covered by my authorization. Reopen affected rules/approvals when behavior changes, rerun tests and comparisons, and present new code segments for review. Do not transfer approval to changed code automatically.

### Make the management PowerPoint
Use the reporting role in AGENTS.md. Generate an editable PPTX and its metrics.csv from one frozen ledger snapshot. Show total repository scope, this process's share, complexity/risks, segments converted/reviewed/validated/accepted, remaining work, blockers, and the evidence-based route to finish. Show provisional denominators and missing measurements honestly. Validate calculations and render every slide before delivery. Do not make up a completion date or publish to others.

## Definitions you can rely on
- Converted: target implementation exists for the mapped source behavior; this is not acceptance.
- Reviewed: required humans approved the current source/rule/code versions in their respective roles.
- Validated: required tests and matched legacy comparisons passed for the current versions.
- Accepted: all required reviews, SME/user decisions, tests and comparison gates passed.
- Remaining: approved planned work not yet accepted, plus separately visible unresolved/unplanned scope.

## Setup and limits
Provide the exact repository and Endevor export-folder path, ordered jobs, approved source connections/destinations and reviewer roles when you start. Do not put credentials into the files. No metrics can be computed from this kit alone. Native custom-agent installation is platform-specific; this pack works as role instructions and does not claim to register agents automatically.
