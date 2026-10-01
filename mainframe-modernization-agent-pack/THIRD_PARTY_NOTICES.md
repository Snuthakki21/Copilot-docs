# Third-party notices

## UI/UX Pro Max

Source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/09170eec67eefd46a7ae85de61b40c194020f997

Copyright (c) 2024 Next Level Builder. Licensed under MIT; the full copyright, permission notice, and disclaimer are preserved in `.github/skills/ui-ux-pro-max/LICENSE` from the repository root.

The skill entrypoint is an adaptation dated 2026-10-01. Four Python runtime files, 35 CSV catalogs, and two JSON provenance/license metadata files are unchanged pinned upstream copies. Exact paths and Git blob hashes are in `.github/skills/ui-ux-pro-max/UPSTREAM-MANIFEST.json`; scope, changes, and static-review limitations are in its `SOURCE.md`.

Catalogs may refer to separately licensed fonts, icon sets, libraries, and snippets. Their actual binary assets or packages are not included. Retained Google Fonts license metadata is informational; using an actual asset requires checking its own license and workplace approval. The package does not grant permission to install or fetch referenced assets.

## Frontend Design

Source: https://github.com/anthropics/skills/tree/8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4/skills/frontend-design

Anthropic's frontend-design skill is licensed under Apache License 2.0. The unchanged full license is preserved in `.github/skills/frontend-design/LICENSE.txt` from the repository root. The modified text-only skill is marked as an adaptation dated 2026-10-01; changes and original source hashes are recorded in its `SOURCE.md`. No upstream endorsement is implied.

## Distribution and verification

Keep these notices and each source license with redistributed copies. This package vendors selected repository files; it does not install or reproduce the complete upstream plugins. Upstream executables were not run during packaging. Static syntax, structured-data, dependency, and pinned-source-integrity checks do not establish runtime correctness or workplace authorization.

## Additional text-only Copilot adaptations

All modified entrypoints identify the adaptation in their own SOURCE.md and preserve the full applicable license alongside the skill. No upstream endorsement or complete plugin implementation is claimed.

| Supplied skill | Upstream / pinned revision | License / scope |
|---|---|---|
| answer-first | ayghri/i-have-adhd · 839872f9d1cd634fed642b4589ce7226199cc15f | MIT; presentation only, no health assertions or persistent mode override |
| careful-coding | DietrichGebert/ponytail · e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156 | MIT; minimal correct-change guidance, stronger project review/tests retained |
| research-plan-implement | shanraisshan/claude-code-best-practice · c7b1a7e4021a6d6ceb2667219a022dbec4281d09 | MIT; selected workflow concepts, no Claude hooks/runtime/settings |
| impeccable-review | pbakaus/impeccable · c74755d920985f7a92cef691ca970ba95f90126e | Apache-2.0; LICENSE + NOTICE retained; manual/text review subset, no launcher/detector/browser setup |
| taste-design | Leonxlnx/taste-skill · ce26fc25c0e5e8cab638f883de62d9a86ee5e45b | MIT; selected optional visual lens, no mandatory dependencies/assets/motion |

multica-ai/andrej-karpathy-skills at 2c606141936f1eeef17fa3043a72095b4765b9c2 is referenced only. Its README declared MIT but the inspected tree contained no complete LICENSE and the repository metadata identified none. Its source text is not distributed; the generic engineering checklist is independently worded.

## Runtime dependencies and excluded runtime integrations

The authored Db2 MCP uses separately installed official Python MCP SDK and IBM ibm_db dependencies; their requirements and IBM driver licensing restrictions are documented with the server. Their package code/binaries are not copied into this archive. The Windows IBM 3.3.0 CPython 3.12 x64 wheel was inspected against the official PyPI SHA256, without installation or native execution; see VALIDATION.md.

Headroom is configured using its official standalone stdio MCP entrypoint, from headroomlabs-ai/headroom revision f824a270f132516443deeef2555076bf4cd40a34 and headroom-ai[mcp] 0.39.1 (Apache-2.0). Its source/binary is not vendored. The published 0.39.1 distribution includes a Windows x64 ABI3 wheel; this establishes package availability, not runtime validation on the user's machine. Telemetry/update checks are set off via upstream-documented environment controls. No proxy, OAuth credential flow, API rewrite, auto-installer or companion software is supplied.

No runtime code/configuration for codebase-memory-mcp, RTK, Paperclip or Graphify is distributed. The first requires its persistent coordination daemon, RTK lacks an official MCP entrypoint at the inspected revision, and Paperclip needs a separate app/database server. Graphify's installation exception is not used automatically. Source-index/cache/short-output principles are independently implemented as instructions in context-budget; no vendor performance claim or functional emulation is implied.
