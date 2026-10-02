---
name: research-plan-implement
description: "Use a compact research-plan-implement workflow with evidence and approval checkpoints for coding work. Use when preparing or changing a bounded feature; preserve the stricter mainframe SME, architecture and user-confirmation gates."
---

# Research, plan, implement

A repository-only adaptation of the upstream RPI workflow. Native Copilot roles/skills replace Claude-specific commands, hooks and agent setup. No .claude installation or new planning-file hierarchy is required.

Research: inspect the actual code, dependencies, constraints and tests. Record evidence and unknowns in the existing ledger. Check previous scoped decisions before asking.
Plan: define a bounded outcome, affected files/interfaces, alternatives only where meaningful, test expectations and rollback/error handling. Record the plan in canonical task state; avoid duplicate Markdown reports. Obtain approvals required by the migration contract.
Implement: make the smallest cohesive authorized change, keep app/schema ownership explicit, add or adjust tests and report actual results. Reuse approved components; avoid speculative frameworks or unrelated cleanup.
Review: compare the diff to the approved goal, inspect unexpected deletions/dependencies/behavior changes, and run relevant checks using existing tools. Preserve human segment review and real legacy comparisons; self-review alone cannot pass them.
Finish: state implemented, reviewed, tested, blocked and not-run separately. Update the existing memory index/state with pointers, not long transcripts.

This does not import upstream plugins, command executors, hooks, automatic permissions or model settings. Its workflow is subordinate to all source-fidelity and human-review gates.
