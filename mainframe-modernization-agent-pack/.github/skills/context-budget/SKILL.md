---
name: context-budget
description: "Reduce repeated source reads and oversized Copilot context using existing tools and durable evidence. Use automatically during discovery, coding, review and reporting; no proxy, MCP index service or compression runtime is required."
---

# Context budget without extra services

Use this original workflow instead of assuming Headroom, RTK, codebase-memory-mcp, Paperclip or Graphify is running. It adopts the general intent of narrow retrieval, caching, short outputs and explicit ownership without recreating those products or their advertised savings.

1. Read the small current memory index and task state first. Search applicable prior decisions before asking again.
2. Use the existing repository search/navigation tools to enumerate exact candidate files, then inspect relevant ranges with necessary declarations/call context. Never infer completeness from an index or language-count claim.
3. Save full necessary source and raw tool/test evidence to the approved local workspace. Pass the model compact IDs/counts/status and retrieval pointers. Complete required pagination to storage even when context is bounded.
4. Cache reusable extracts/parses/decisions by content hash, source baseline, tool/parser version and target profile. Invalidate changed items and their dependents. A modification time or previous summary alone is not proof of freshness.
5. Request narrow tool output at the source where supported. Keep full stdout/stderr and comparisons in evidence; summarizing for display must never hide errors, warnings, byte differences, numeric values, encoding, record order or failed cases.
6. Delegate one bounded task with IDs/ranges/contracts. Avoid full-transcript handoffs, duplicate agents analyzing identical artifacts, and unnecessary parallelism. Use sequential role work when built-in subagents are unavailable.
7. Keep one canonical ledger and derived review/report views; no competing diaries. Return new findings, blockers and next action instead of restating all work.
8. If context or cost budget is reached, checkpoint and continue later. Do not reduce coverage, change expected results or mark an unfinished task complete to fit a budget.
9. Measure reported input/output/cached tokens and relevant tool volume/rework per accepted comparable slice when available. Label estimates; no guaranteed percentage, synthetic billing or summed vendor saving claims.

Skill routing is automatic by task intent in the repository instructions. Actual actions still obey permissions, human gates and available tools. Nothing here installs, launches, proxies, watches or rewrites tools.
