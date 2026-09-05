# Mainframe modernization: continue the existing project

**Handoff date: 2026-09-05.** This is a persistent, public project handoff, not a claim that the complete executable framework has been published. Read the availability section before attempting implementation. These notes replace reliance on an earlier chat, temporary sandbox links, or attachments for project context.

## 1. Repository, baseline, and availability

Repository: https://github.com/Snuthakki21/Copilot-docs

Project area: `mainframe-modernization-framework/`.

The working baseline delivered in the earlier session is **Mainframe Migration Workbench v2 / release 2.0.0**, archive `Mainframe_Migration_Workbench_v2.zip`. Its top-level directory is `mainframe_migration/`. Earlier workbench ZIPs are historical and must not be mixed into v2.

**At the time this handoff was published, this repository did not contain the v2 source archive, extracted implementation, PowerPoint, full receipt, or original test logs. This publication preserves context; it does not complete the requested artifact publication.** Do not invent download URLs for those files. A filename or checksum is an identity reference, not a retrieval link. Later commits may resolve this; inspect the current tree before repeating this status.

The earlier session's files were inspected locally when preparing this handoff. The v2 archive was 521,452 bytes and had SHA-256:

`c2f93897b77676f823633c678aa95e8e5a4238e24657a54c6d813bcc32df363a`

The continuation bundle contained the same v2 archive bytes. Original files may be present as session files or in a subsequently published location. Check available files and connected GitHub first. Do not silently recreate a different implementation and call it the recovered v2 package.

## 2. Goal and business context

Build a generic, low-supervision, agent-operated framework for migrating mainframe batch processes while preserving existing behavior. Start with one end-to-end process of roughly five or six jobs, then reuse the framework across the application. The setting is enterprise banking; organization-specific integrations and rules are deferred. Do not publish bank source, customer data, credentials, real SME knowledge, or private chat transcripts to this public repository. The framework and synthetic demonstration are the publication scope.

The application has COBOL programs, JCL jobs/steps, files, utilities, possible Db2 interactions, and mainframe screens. Much of its meaning resides with SMEs rather than complete documentation. UI replacement was background context, not an implemented deliverable. AutoSys was mentioned; do not infer actual scheduling dependencies from uncertain terminology or from the synthetic example.

No actual bank process source checkout, source revision, real process inventory, or captured mainframe baseline was supplied in the earlier sessions. `PAYMENTS` is an instruction example, not a confirmed bank process. The shipped demonstration is synthetic.

## 3. Settled environment: do not ask again

- The work laptop is Windows. Python and ordinary virtual environments are allowed. Python 3.10 was discussed, but the framework must check the actual supported installed runtime rather than assume a version.
- Python packages available through Artifactory may be installed. GitHub and Artifactory are the stated work-laptop routes. Do not assume public package repositories, administrator rights, Docker, WSL, or unrestricted network access.
- GitHub Copilot in VS Code is approved. Do not reopen its approval discussion. Devin is another intended coding-agent environment; a live Devin execution has not been verified.
- The user manually clones the mainframe repositories and manages their Git changes. The migration runner must not automatically clone, pull, branch, commit, or push.
- Separately, the user explicitly asked for publication of this generic framework and its documents to this public Copilot documentation repository. That publication is not authorization for the runner to change bank repositories or publish bank inputs.
- SQLite is acceptable for local validation, not an assumed permanent production architecture.

## 4. Inputs and dependency discovery

The user supplies an Excel inventory with A = job, B = step, C = program, D = inputs, E = outputs. JCL and available related sources are in a manually checked-out repository. Jobs can contain several steps. Inputs and outputs can be multiple files or database effects.

Treat Excel as a starting index, not proof that the dependency list is complete. Trace available JCL, programs, copybooks, called programs, procedures, utility control cards, layouts, SQL objects, control files, runtime settings, and execution evidence recursively. Detect missing or ambiguous members instead of inventing them. PDF context was mentioned; PDF ingestion must not be represented as implemented merely because it was discussed.

SMEs have limited time and understand mainframe code, not Python/Java/C#. Investigate the repository first, consolidate currently discoverable gaps, and ask only necessary questions in plain business/mainframe English. They supply missing information and help validate against actual mainframe results. They are not expected to explain every program or justify every unusual rule. New supplied sources can reveal further dependencies; do not promise an impossible one-and-only question round.

## 5. Controlling migration rules

**Preserve what the executable source does, not what an AI thinks the business should do.** Retain apparent bugs, thresholds, exceptions, truncation, ordering, duplicate handling, error behavior, transaction boundaries, and unexercised branches. A surprising rule may exist for a production edge case. Do not silently change behavior to agree with comments, intuition, or a preferred design.

**No automatic repair loop.** Review and validation must not modify sealed generated candidates, source files, expected results, inputs, or comparison rules to manufacture a pass. Preserve a failed candidate and report the discrepancy. A separately authorized new attempt can address a migration error; it is not permission to patch repeatedly until green. Do not automatically increment an attempt number to evade this rule.

Corrections to the migration framework itself are distinct from repairs to application behavior and require regression evidence. Earlier suggestions involving TODOs, target stubs, business-rule cleanup, or automatic repairs were superseded by the user's explicit instructions.

AI analyzes source and generates/reviews code. Local deterministic software reads test records, runs the generated application, and performs comparisons. AI is not the business-record processing engine or the calculator of expected results.

The user's normal operation is one Copilot/Devin kickoff, not separately operated discovery, conversion, execution, and comparison commands. Internal tools may have multiple stages; the agent operates them. One file per native job is the default, with several steps inside a job file and justified shared runtime/adapter files. Use extensive plain-English comments explaining intent, inputs, outputs, and source references. Do not present placeholders as completed functionality.

## 6. Independent language and database configuration

Use one central `target.json` in the framework root. The choices are:

- `language`: `python`, `dotnet` (C#), or `java`.
- `database`: `sqlite`, `oracle`, or `bigquery`.

Change the two existing values independently; do not replace the entire configuration with a two-field excerpt. The delivered default was Python/SQLite. Other entries include runtime versions, declared dependencies, and names of connection environment variables, not credentials. Declared versions are not proof that packages are available or approved in Artifactory.

The v2 architecture separates source-linked behavior models, native-language implementation, logical schema, target database components, immutable candidate artifacts, and validation records. Database-only changes can reuse eligible job implementations; language changes can reuse eligible source models. Changes to source or dependencies invalidate affected work. Switching back can reuse an intact target artifact while running fresh validation.

Do not treat SQLite DDL or an old Python implementation as the original business specification. Do not repeatedly translate Python to C# to Java and assume the chain preserves intent. Prior v1 outputs are historical evidence, not automatically portable target artifacts. A previous SQLite pass must never become an Oracle/BigQuery validation pass without target-specific evidence.

## 7. Reuse, persistent knowledge, and reporting

Limit AI credit consumption with source/dependency-aware reuse, checkpoints, and bounded work. Cache identities must include relevant sources, copybooks, schemas, configuration, knowledge decisions, and framework versions. Reusing analysis or code is separate from reusing test results. Stale or changed artifacts must be rejected, not silently repaired.

Persist approved SME answers and terminology in project files, not chat memory. Record provenance, scope, approval, and contradictions. Distinguish application-wide knowledge from process-specific exceptions and genuinely global facts. Do not automatically widen a process answer into a global rule.

**Known gap:** v2's knowledge implementation was reported to support exact process names or `global`, not the requested application-level reuse. Its shipped answers store was empty. Application-scoped knowledge, precedence, conflict handling, and dependent-cache invalidation remain implementation tasks, not completed features.

Produce native code, appropriate DDL, test evidence, and one consolidated human-facing process report. The report should show what was discovered, generated, reused, executed, validated, blocked, and not yet tested, with source traceability, coverage limitations, differences, and one consolidated SME question section. Environment questions should not be mixed with questions for mainframe SMEs. Distinguish generated, compiled, recording-tested, live-target validated, and organizationally approved.

## 8. Existing v2 implementation map

These are paths **inside the previously delivered archive**, not currently published source URLs:

- `modernize.py`: command entry point.
- `target.json`: language/database and related target settings.
- `migration/inventory.py`, `discovery.py`, `compiler.py`, `runtime.py`, `runner.py`, `report.py`.
- `migration/targets/config.py`, `controller.py`, `model.py`, `schema.py`, `emit.py`, `package.py`, `verify.py`, `matrix.py`, `agent.py`.
- `migration/targets/templates/`: Python, Java, and C# runtime/adapter templates.
- `knowledge/answers.json`, `knowledge/README.md`.
- `sample/`: synthetic mainframe inputs and expected evidence.
- `tests/`, `tests_target/`, `tools/verify_package.py`.
- `AGENTS.md`, `.agents/skills/migrate-process/SKILL.md`, `.github/copilot-instructions.md`.
- `START_HERE.md`, `docs/OPERATING_TARGETS.md`, `docs/AGENT_CONTRACT.md`, `docs/SUPPORT_AND_LIMITS.md`, `docs/RETARGETING_DESIGN.md`, and `evidence/v2/`.

Recorded user commands, to be verified against recovered source before use:

```powershell
.\VERIFY-WINDOWS.cmd
```

```powershell
python modernize.py run --config "processes/PAYMENTS/process.json"
```

The report location was `output/PAYMENTS/modernization_report.html`. A bare Python command is not represented as a hidden API for invoking an IDE agent. Refer to the packaged skill for the agent-operated generation route.

## 9. Historical verification: do not claim it was rerun now

The original receipt timestamp was `2026-09-05T15:09:56.415774+00:00`. It recorded Linux, Python 3.13.5, SQLite 3.46.1, 91 passing regression tests with zero skips on that host, generation of all nine target combinations, and 301 manifest-tracked shipped-file hashes matching. The sample had five jobs, six steps, and 13 source members. Forty-seven original sample files were recorded as unchanged. Coverage was 52 of 53 mapped statements, not complete path coverage.

| Target | Recorded execution evidence |
|---|---|
| Python + SQLite | Generated, compiled, real SQLite comparisons passed. |
| Python + Oracle / BigQuery | Generated, compiled, operation-recording checks passed; no live target database tests. |
| Java + SQLite / Oracle / BigQuery | Generated, compiled, operation-recording checks passed; no actual provider/live database validation. |
| C#/.NET targets | Generated, not compiled or executed because the SDK was unavailable. |

The six executed targets each recorded 18 exact file comparisons, three database-snapshot or transaction-record comparisons, and 15 job-return-code checks across three synthetic scenarios. Recording tests validate application output and operation intent; they are not proof of driver/database equivalence.

No native Windows, live Copilot/Devin, or IBM mainframe run was recorded. The expected results were independently enumerated synthetic expectations, not captured bank production results. The review was performed in the assistant session, not an external third-party certification.

Historical defect/injection checks included CALL parameter aliasing, missing dependencies, wrong thresholds, altered candidates/caches/baselines, return codes, and no automatic repair. These descriptions are historical evidence summaries; consult the actual original logs after recovering them.

The front end remains a restricted COBOL/JCL subset. General PROC/symbol/conditional handling, packed/binary/variable records, VSAM/CICS/IMS/GDG behavior, full SQL/SQLCODE/SQLSTATE/cursor/locking semantics, production restart/resilience/scale, live Oracle/BigQuery state comparison, automatic ETL generation, and bank release qualification are not established. Some unsupported features block the agent path too. The sample's BigQuery primary-key requirement was recorded as a capability blocker, not discarded to obtain a pass.

## 10. Artifact identity catalog

These hashes were computed from the files available during publication. They identify existing historical deliverables; **they are not download locations**. The original source archive and full evidence have not been uploaded by this handoff-only change.

| Historical artifact | Bytes | SHA-256 |
|---|---:|---|
| `Mainframe_Migration_Workbench_v2.zip` | 521452 | `c2f93897b77676f823633c678aa95e8e5a4238e24657a54c6d813bcc32df363a` |
| `Migration_Targets_Playbook_v2.pptx` | 83456 | `e1cb92b144223fec34b3e81c779a72e86b5cca5207c09e76d0bb5af61fcbb7d5` |
| `V2_Retargeting_Verification_Report.html` | 34577 | `760eed9a80119767be1fc244d25a32aa975b91a909dd8c0a22646a15c4ef8589` |
| `V2_Verification_Receipt.json` | 310045 | `636fbf69e6e1803a6ae299cebe5d8421b983ed1643c340b2014aab0da042d165` |
| `V2_Extracted_Full_Test_Log.txt` | 19310 | `55f4e404dcf4bc3fa11b5cd7de7667a77d5558cf24412b4b6914ba3f85afeb96` |
| `Mainframe_Modernization_Continuation_Brief.md` | 32818 | `572eb8c6810b15e6280a788684070e720ae3c9485db9478b2d6ffbf105487c29` |
| `Mainframe_Modernization_Continuation_Bundle.zip` | 520482 | `a3360b352b1b884661d4ed74101d790d07f4d4bc98081187ce0cb7bc0d77f7dc` |

## 11. Requested final repository arrangement

The following is the requested end state, not a claim that all these paths already exist:

```text
Copilot-docs/
  mainframe-modernization-framework/
    CONTINUE_HERE.md
    README.md
    prompts/
      kickoff.md
      resume.md
      retarget.md
      knowledge.md
      verify.md
    mainframe-modernization/
      complete runnable framework, target.json, skills, tests,
      synthetic sample, documentation, presentation, and evidence
```

The child must be self-contained when copied to the work laptop. Parent prompts operate on it, but it cannot depend on files left behind in the parent. Include essential operating instructions inside the child too. Any changed path layout must be tested rather than assumed compatible.

## 12. Next actions and acceptance criteria

1. Read this handoff, inspect the actual repository tree and available files, and report the accessible baseline. The repository identity is now resolved: `Snuthakki21/Copilot-docs`, default branch `main`. Do not ask the user to identify it again.
2. Recover the exact original v2 package and full evidence where accessible, verify their hashes, and finish the requested public artifact publication with working links. If the package is unavailable, state that precise blocker without pretending this handoff contains executable source. Do not ask the user to repeat all requirements.
3. Finish the parent/portable-child arrangement and operating prompts. Preserve behavior and existing evidence; do not modify old baselines or silently replace the historical archive.
4. Implement the missing application-scoped knowledge behavior with tests for precedence, approval, conflicts, cross-process reuse, and targeted invalidation.
5. Close execution gaps where the required runtimes and target services are actually available. Mark other targets not executed or blocked. Do not use missing-runtime or mocked/recording checks as evidence of live equivalence.
6. Build the final ZIP, extract that exact ZIP into a fresh folder with spaces, test from the extracted copy, verify file hashes, and document actual commands, results, failures, environment, and limits. Synchronize code, configuration, README, prompts, and presentation.
7. Update this handoff and publication status with verified repository URLs and revision identifiers. Do not mark historical test results as newly run.

Use Superpowers for planning/testing/review discipline and Context7 for current library documentation where available. GitHub is the intended publication location. Product Design was requested for usability, not for replacing this workflow with an unrelated UI project. Keep the user informed with brief concrete progress, minimize setup effort, and do not reopen settled decisions.

**The first response in a continuation session should state what is actually accessible and the next concrete action. Continue from the existing project, not from a new brainstorming exercise.**
