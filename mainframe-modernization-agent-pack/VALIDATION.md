# Validation and adversarial-review record

Revision 4 · checked 2026-10-01 · intended workstation: Windows 11 / VS Code Local

## Executed checks
- 42 Db2/MCP offline tests passed, including official Python MCP SDK initialize/list/call/error/shutdown with a test-only fake IBM backend
- 20 Zowe unit/configuration/argument tests passed; no actual Node/Zowe or mainframe connection was started
- 2 Headroom-launcher environment/entrypoint tests passed; the upstream Headroom runtime was not executed
- Five additional hermetic Zowe extraction lifecycle scenarios were checked: retained successful JSON, invalid JSON rejected/deleted, unsuccessful response rejected/deleted, oversized pending output terminated/deleted, and nonzero exit output deleted
- Authored Python syntax, JSON configuration, YAML/frontmatter and relative-document links checked
- 10 native agent profiles, 12 skills and 3 VS Code Local prompt files checked for appropriate frontmatter
- Pinned vendored UI/UX Pro Max source hashes and license/provenance records checked; its Python source was parsed, not executed

Reproduce the three packaged offline suites with the approved Python environment:
`& .\.venv\Scripts\python.exe tools\run_tests.py`

## Adversarial cases and resulting changes
- SQL/identifier injection: no arbitrary-SQL tool; strict argument schemas/identifier validation, parameterized values, explicit schema/table allowlists and base-table checks
- Credentials: root .env only, no interpolation/process-env override, no credentials in driver DSN or command arguments, static error messages, suppressed raw native diagnostics
- TLS: SSL required; public certificate parsing, fixed Db2 certificate location, symlink/path escape rejection, bundled-driver version check before connection, hostname verification and DBA SELECT-only account requirement
- Windows execution: Zowe uses absolute approved Node plus verified @zowe/cli JS entrypoint rather than a .cmd shell shim; hostile PATH/Node variables and unrelated Db2 secrets are not inherited
- MCP protocol/resource boundaries: bounded input frames, malformed UTF-8 rejected instead of altered, strict tool arguments, row/response caps, isolated query deadlines and cancellation retaining the single-call permit until cleanup
- Precision: tagged exact decimals/large integers/binary/date values and explicit pagination/cross-call snapshot limitations
- Test portability: replaced reliance on the host trust store with a synthetic test-only public certificate; no private key distributed
- Headroom isolation: no root .env access or credential forwarding; its foreground MCP process receives a minimal environment and upstream-documented no-telemetry/no-update flags
- Source evidence: accepted Zowe JSON is preserved locally with hash/path; text view is explicitly not an original binary record export

The Zowe byte cap limits accepted evidence. The polling implementation can temporarily allow the pending file to exceed the cap before termination; it is not a strict peak disk-write quota. Read-only driver hints are advisory: real database grants remain the security boundary. Approved installed package integrity and a trusted local workstation remain prerequisites; these tools are not a sandbox against compromised dependencies or a hostile local administrator.

## Package availability verification
The official IBM ibm_db 3.3.0 Windows CPython 3.12 x64 wheel was downloaded for archive inspection, not installed/executed. Its SHA256 matched PyPI:
`70147f6885ae7b02f440e5a73be6cf44667d0d708ffec9695d2e5881b9e0ed41`
Its ibm_db extension and clidriver/bin/db2level.exe were present in RECORD. The adapter deliberately rejects unverified external-client layouts.

Official PyPI metadata for headroom-ai 0.39.1 includes a Windows x64 ABI3 wheel. This proves distribution availability only; the resolved dependency environment, tokenizer assets and actual Windows runtime still need approved provisioning and smoke testing.

## Explicitly NOT verified
- User's Windows execution, Copilot agent/skill discovery or automatic routing in the actual enterprise client
- IBM native driver execution, entitlement/licensing, real Db2 authentication, TLS handshake or account privileges
- Actual z/OSMF/Zowe connectivity, dataset visibility, site plugins/profiles or record conversion
- Headroom's runtime/quality/cost behavior or claimed token savings
- Any real source inventory, complete Db2 catalog introspection, migrated business code, baseline equivalence, executive figures or production readiness

The supplied Db2 tools cover allowlisted base-table metadata and bounded scalar rows. They are not unrestricted catalog/SQL access, views/LOB/XML support or a consistent snapshot export. Unsupported requirements must remain visible gaps. No real credentials, endpoints, private keys, employer source/data or certificates are included. certs/.gitkeep is the empty destination; tests/fixtures/test-only-ca.pem is a synthetic public test certificate that must never be used for production.

## Before real use
Complete the local .env/cert setup privately, obtain approved dependency/driver provisioning and DBA grants, review workspace MCP definitions before trusting the folder, then run local validation followed by an explicitly intended connection check. Inspect the safe status and required per-tool scope. Keep failures and untested requirements visible. Never turn off TLS, broaden grants or change expected results to make a check pass.
