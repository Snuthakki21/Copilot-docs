# Mainframe modernization

This branch is reserved for the mainframe modernization framework. Unrelated document generators, presentation examples, marketing prompts, scratch files, and the abandoned upload workflow have been removed from its current file tree.

## Start here

Read [the project handoff](mainframe-modernization-framework/CONTINUE_HERE.md) for the established requirements, target configuration, artifact identities, historical verification results, and unfinished work. The handoff is preserved byte-for-byte from commit `1627b2f8425500414ff58681ed24e79316923652`.

## Current delivery status

**This revision contains project documentation only. The executable v2 framework, its ZIP, and its modernization PowerPoint have not been committed to this branch.** The branch name is not evidence of completed validation. No application tests were run by this cleanup.

The existing archive to recover and publish is `Mainframe_Migration_Workbench_v2.zip` (521,452 bytes), SHA-256 `c2f93897b77676f823633c678aa95e8e5a4238e24657a54c6d813bcc32df363a`. Its identity was checked against the locally available archive during cleanup; that does not make it downloadable from this repository. Do not substitute an older package or invent a download URL.

When publication is completed, keep operating prompts in `mainframe-modernization-framework/prompts/` and the self-contained work-laptop package in `mainframe-modernization-framework/mainframe-modernization/`. Those implementation directories are not present in this revision. Do not add empty executable stubs, encoded upload fragments, obsolete package versions, or workflows that depend on absent files.

## Branch scope

Cleanup applies only to `mainframe-modernization-v2-verified-20260905`. It is a normal commit with history preserved, not a force-push or purge. The previous branch tip was `5fb01c80d918a3e169797ea5e97a88f8d694f834`. No change to `main` or other branches is part of this cleanup.

Do not merge this cleanup into `main` unless deleting the unrelated files there is also intended. This public branch is for the generic framework and synthetic examples, not bank source code, customer data, credentials, or real SME knowledge.
