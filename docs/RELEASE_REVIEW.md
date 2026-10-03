# Independent adversarial review and disposition

One fresh reviewer inspected the whole workbench, ran the existing 26 tests, and independently reproduced four integrity findings. The implementation author fixed all four in one pass. Four regression tests failed on the previous implementation and passed after the changes; the resulting full suite passed **30/30**.

| Finding | Verified fix |
|---|---|
| Worker failure after SME return could skip verification on Resume and certify an empty run | Resume records the actual failed queued stage; failure remains a blocker until successful stage recovery. Reporting adds a verification-incomplete blocker unless verification finished. The regression injects a fixture-generator failure, resumes, and requires a real run before completion. |
| Blank free-format indentation triggered fixed-format truncation | Blank indentation remains free format; only numeric sequence areas or explicit fixed-format indicators enter normalization. Nonblank content that would be discarded beyond column 72 blocks conversion. Full original lines are retained alongside normalized lines. A long AND condition is interpreted in full. |
| JCL prefix matching ignored trailing conditions/options and manifest disagreement | Full supported card grammar is checked. Unsupported clauses remain blockers; source job/step/program sequence is reconciled with the manifest. A source COND or renamed step cannot silently pass as Always. |
| Yes plus contradictory correction received approval/knowledge credit | Any nonempty correction remains unresolved. The original rule receives no verified metric credit or confirmed knowledge entry. The single returned file is retained and no further questionnaire is issued. |

Deferred smaller findings, retained for transparency:

1. Pause/cancel are checkpoint operations; an active stage holds the coordinator lock. The UI exposes Pause/Resume, but no Cancel button. API cancellation remains available.
2. The sample PPT's LOC comparison label says COBOL + copybook while source LOC currently includes all inventoried source asset kinds. The canonical JSON field is `source_code_loc`; do not interpret the label as an exact COBOL-only figure.
3. The full historical master prompt still contains an older “has not been built” statement. Its release preface and migration contract describe the executable POC and take precedence for current status.
4. Returned checklist identities and source snapshot are checked, but explanatory Context-sheet changes are not checked. Consult the frozen packet.json/DOCX when reviewing a disputed return.
5. requirements.lock pins direct versions but does not fully lock transitive versions or package hashes. Fresh registry installation and vulnerability certification were not performed in this environment.

The reviewer explicitly did not certify live Db2/Zowe/provider connections, Windows behavior, browser accessibility/rendering, PPT visual clipping, dependency vulnerability status or GitHub publication. Platform limitations are recorded in VALIDATION.md; remote publication is verified separately.

Implementation decisions:

* Execute only source-derived audited templates. Arbitrary LLM code requires a separately approved OS sandbox; this costs broad automatic conversion capability and leaves unsupported syntax blocked.
* Keep source support explicit. Unsupported syntax/data representation and missing evidence remain unresolved rather than being inferred as equivalent; this costs operator-ready conversion for complex real processes.
* Use serialized local SQLite rollback journaling and an OS coordinator lock. This favors local single-writer reliability over concurrent/network-hosted operation.
