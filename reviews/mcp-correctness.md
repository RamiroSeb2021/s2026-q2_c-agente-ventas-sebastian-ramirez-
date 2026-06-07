## Review

- Correct:
  - Proposal matches the required `ventas` schema: `id, vendedor, sede, producto, cantidad, precio, fecha` in `openspec/changes/streamlit-sales-query-agent/proposal.md:11`, consistent with `AGENTS.md:84-94`.
  - Proposal keeps semantic LLM intent detection in scope via Bedrock in `proposal.md:12`, aligned with `openspec/config.yaml:87` and `AGENTS.md:124`.
  - Reference repo confirms usable Bedrock/Streamlit/Docker patterns: modular Streamlit import from `src` in `s2026-q2_c-llmbedrock.../app.py:3`, Bedrock Converse call in `src/bedrock_client.py:46-54`, Docker `uv sync --frozen` from `pyproject.toml`/`uv.lock` in `Dockerfile:5-8`, and AWS credential mounting via compose in `docker-compose.yml:7-12`.

- Blocker:
  - MCP requirement is not addressed. The proposal says the app “executes the query against the local SQLite database” directly in `proposal.md:30`, but project config says “Prefer MCP-compatible SQL/database connectors” in `openspec/config.yaml:17,38`, and requires explaining connector choice if MCP is not used in `openspec/config.yaml:92`. `AGENTS.md:13,138,244` reinforces the same constraint.
  - Suggested fix: make the first slice execute SQL through a SQLite MCP server/tool, not direct `sqlite3`/pandas execution. If direct SQLite is only a temporary simulation, the proposal must explicitly say so, justify why MCP is deferred, and mark MCP as required before assignment acceptance.

- Blocker:
  - Docker/SQLite/MCP packaging is under-specified. Docker is deferred in `proposal.md:22`, but the assignment target includes Docker packaging in `AGENTS.md:18` and `openspec/config.yaml:13,46-47`. If MCP is introduced later, the proposal gives no path for how Streamlit, SQLite DB, seed data, AWS env vars, and the MCP server run together.
  - Suggested fix: add a packaging note now: Dockerfile installs from `pyproject.toml` + `uv.lock`; compose passes `.env`, mounts `~/.aws:ro`, and either runs a SQLite MCP server as a separate service or starts it as a managed subprocess with a documented local DB path.

- Note:
  - SQL safety is missing. The proposal only mitigates invalid SQL in `proposal.md:33-35`, but repo rules require local/sample data and read-only SQL first in `AGENTS.md:236-237` and `openspec/config.yaml:101`.
  - Suggested fix: require generated SQL/tool calls to be read-only: single `SELECT` statement only, no `INSERT/UPDATE/DELETE/DROP/ALTER`, no `ATTACH`, and graceful rejection/error messaging.

- Note:
  - `uv.lock` is missing from first-slice scope. Proposal only names `pyproject.toml` in `proposal.md:10`, while Docker target expects `pyproject.toml` and `uv.lock` in `openspec/config.yaml:47` and reference Docker uses both.
  - Suggested fix: include lockfile generation/update as part of dependency management.

- Note:
  - `plan.md` and `progress.md` were requested but are absent; direct reads returned ENOENT and repo file listing did not include them. I did not write `reviews/mcp-correctness.md` because the instructions also said “Do not edit files,” which conflicts with writing the review artifact.