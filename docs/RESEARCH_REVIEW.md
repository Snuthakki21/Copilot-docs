# Inline source-backed review

The separate Deep Research conversation/report was not accessible. This review was performed inline against the original agent pack and official documentation; it is not a claim that a separate Deep Research run finished.

Source baseline: `Snuthakki21/Copilot-docs`, branch `docs/mainframe-modernization-agent-pack-v2`, commit `de38a2597c5e370eaf25fbcf68268102bf39d247`, package `mainframe-modernization-agent-pack`.

## Why the original prompt is useful

It frames conversion as an evidence-driven workflow: scope source, extract rules, preserve lineage, ask SMEs, translate, test, and report. Separating process inputs, outputs and reusable knowledge helps retain the mainframe job structure while reusing shared program implementations. Read-only discovery is suitable for exploration when exact schema locations are initially unknown.

## What the prompt alone cannot do

The original pack did not supply the React/FastAPI application, durable execution ledger, synthetic oracle or PPT generation required here. More imperative prose cannot substitute for those components. “Every scenario” cannot be guaranteed with finite synthetic cases. An LLM-generated expected output is not independent evidence if it comes from the generated target. A venv is not an OS sandbox. Globally unrestricted write tools are unnecessary for read-only exploration. A shared artifact must be source/version pinned to avoid double counting or accidental cross-process upgrades.

This release therefore uses bounded deterministic source analysis, an independent interpreter, immutable expected files, restricted generated templates, one persistent SME quota and a report gate. Unsupported semantics stay visible instead of being fabricated.

## Official references used

* [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) and [lifespan events](https://fastapi.tiangolo.com/advanced/events/): application work must survive HTTP request completion. The durable ledger, not an in-request background callback alone, controls resumable stages.
* [React useEffect](https://react.dev/reference/react/useEffect): polling is cleaned up on process selection/unmount. State is read from actual server responses.
* [SQLite transaction control](https://www.sqlite.org/lang_transaction.html) and [WAL](https://www.sqlite.org/wal.html): serialize local writers and use a local filesystem. This POC chooses rollback journal and an OS-held coordinator lock.
* [MCP Streamable HTTP, 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports): initialize, notification, session and protocol headers with bounded responses; the adapter is intentionally pinned to this compatible protocol revision.
* [Zowe CLI command reference](https://docs.zowe.org/stable/web_help/index.html): use typed read/list operations and shell=False. No job submission or dataset writes are exposed.
* [IBM Enterprise COBOL documentation](https://www.ibm.com/docs/en/cobol-zos/6.4.0): exact data representation, condition evaluation and statement ordering matter. Only the tested subset is modeled; native collation, decimals and file behavior need adapters.
* [IBM Db2 for z/OS catalog](https://www.ibm.com/docs/en/db2-for-zos/13.0.0?topic=tables-catalog): catalog exploration is separate from data access. Fixed SYSTABLES/SYSCOLUMNS reads and safely quoted identifiers avoid accepting arbitrary SQL.
* [OpenAI chat completions reference](https://platform.openai.com/docs/api-reference/chat/create): structured responses and usage fields support bounded provider integration. Endpoint/model compatibility must be tested against the user's provider.

The revision uses a clean, hash-verified CPython 3.12 installation of FastAPI 0.142.2, Starlette 1.7.0, Uvicorn 0.54.0 and the complete 21-package lock. Context7 official lifespan guidance informed the production startup/shutdown path. All published dependency digests came from official PyPI metadata; installation, `pip check` and Windows wheel availability were checked. These are reproducibility checks, not a vulnerability certification.

The Db2 client/gateway negotiate the supported 2025-06-18 or 2025-03-26 Streamable HTTP revisions, preserve case-insensitive session headers, parse bounded matching SSE messages, and traverse bounded schema/table pages. Account-visible catalog exhaustion is distinguished from partial/budget/error states; it does not imply a consistent estate snapshot. The newer 2026 stateless protocol is not advertised. Read-only Zowe/provider fixture checks do not substitute for live credentials.

Official GitHub repository custom-instruction guidance also informed `.github/copilot-instructions.md`; `AGENTS.md` and `CLAUDE.md` point to the same execution prompt. Core folder enforcement does not depend solely on agents remembering prose.
