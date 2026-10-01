---
name: runtime-tool-preflight
description: "Verify the supplied Db2 MCP, Headroom MCP and Zowe connection prerequisites without exposing secrets or silently installing tools. Use before source connection work or troubleshooting startup."
---

# Included runtime preflight

Read the setup section in START_HERE. Check paths/dependency presence through the supplied safe local validators, never by displaying .env or private certificate contents. Use only the included MCP definitions and the existing approved Zowe CLI. Do not invent a plugin adapter or activate an omitted integration.

Confirm the actual Python/driver/MCP versions, configuration presence, cert format/path, TLS enforcement and user-approved source scope. Report configuration-valid, dependency-missing, client-started, connection-tested and data-access-tested as separate states. Do not install software or change trust/credentials automatically.

VS Code starts eligible configured servers according to its Workspace Trust/autostart behavior. Missing prerequisites must fail safely; fix them and restart through MCP: List Servers. No read-only claim replaces DBA SELECT-only permissions or account-level mainframe controls.

For Headroom, use only official standalone tools when appropriate. Do not claim it intercepts other servers. Preserve raw evidence outside its temporary cache; never use lossy compression as byte/record proof. Use context-budget before any optional compression. Do not stack claimed savings.

Record safe status codes and dependency/version evidence in canonical state. Never put passwords, DSNs, raw driver exceptions, certificate contents or complete connection objects into model output.
