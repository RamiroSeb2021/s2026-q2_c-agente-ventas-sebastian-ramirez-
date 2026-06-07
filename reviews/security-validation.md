## Review

- Correct:
  - Repo state is accurately framed as pre-implementation: no runnable app/test/Docker files yet in `AGENTS.md:25-28` and `openspec/config.yaml:21-27`.
  - Existing guidance already says to keep AWS credentials out of source/images (`AGENTS.md:233-235`, `openspec/config.yaml:91`) and prefer read-only SQL (`AGENTS.md:237`, `openspec/config.yaml:101`).
  - MCP preference is documented (`AGENTS.md:13`, `AGENTS.md:138`, `AGENTS.md:244`, `openspec/config.yaml:17`, `openspec/config.yaml:38`).

- Fixed:
  - None. I did not edit or create `reviews/security-validation.md` because the task also said “Do not edit files”; I’m returning findings inline.

- Blocker:
  - **Prompt-only SQL safety is insufficient.** The proposal says Bedrock generates SQL and the app executes it (`openspec/changes/streamlit-sales-query-agent/proposal.md:27-30`), but the only SQL mitigation is schema prompt context plus graceful SQLite errors (`proposal.md:33-35`). Before code, spec/design should require app-side validation: single statement, `SELECT`-only AST parsing, no `PRAGMA`, `ATTACH`, `DETACH`, DDL/DML, semicolon chains, unknown tables, or unknown columns.
  - **Schema allowlist is missing as an enforceable requirement.** The allowed table/columns are known (`AGENTS.md:84-94`, `proposal.md:11`), but the proposal only mentions hallucinated columns as an error case (`proposal.md:34`). Add a MUST requirement that generated SQL may reference only `ventas(id, vendedor, sede, producto, cantidad, precio, fecha)` and approved aggregate/scalar functions.
  - **MCP execution boundary is unresolved.** The project prefers MCP-compatible SQL access (`openspec/config.yaml:17`, `AGENTS.md:13`), but the proposal describes direct execution without naming a connector or its permissions (`proposal.md:30`). Design should require either: MCP server configured read-only/table-allowlisted, plus local validator before tool execution; or a documented reason for not using MCP per `AGENTS.md:244`.
  - **Generated DB artifacts are not protected.** The proposal will create `ventas.db` (`proposal.md:11`), while repo guidance treats local DBs as generated artifacts (`AGENTS.md:238`). Current `.gitignore` only ignores `.atl/` (`.gitignore:1-2`). Add requirements to track the seed CSV intentionally, but ignore/generated DB files such as `*.db`, `*.sqlite*`, `outputs/`, and runtime export directories.
  - **Credential and Docker requirements should be specified before implementation.** The reference repo uses `.env.example` for non-secret config only (`/home/sebastian-ramirez/trabajo/s2026-q2_c-llmbedrock-sebastian-ramirez/.env.example:1-2`), ignores real `.env` files (`reference .gitignore:6-9`), excludes secrets from Docker context (`reference .dockerignore:1-12`), and mounts AWS credentials read-only (`reference docker-compose.yml:7-12`, `README.md:85-93`). Add equivalent requirements here: no AWS keys in `.env`, image, or repo; use AWS credential chain; if Docker Compose is added, mount `~/.aws` read-only or pass env safely.
  - **Error handling is underspecified.** Proposal only says “handle SQLite execution errors gracefully” (`proposal.md:34`) and clear AWS errors (`proposal.md:35`). Add requirements that validation failures stop before MCP execution, user-facing errors are sanitized, raw stack traces/secrets are not displayed, and technical diagnostics are limited to local logs/debug mode.

- Note:
  - `plan.md` and `progress.md` were requested but are absent; direct reads returned `ENOENT`.
  - No `spec.md`, `design.md`, or tasks exist yet under `openspec/changes/streamlit-sales-query-agent`; only `proposal.md` is present.
  - Add validation tasks before coding: unit tests for SQL validator reject/allow cases, read-only SQLite/MCP execution tests, generated artifact ignore checks, config validation for `AWS_REGION`/`MODEL_ID`, and documented commands once `pyproject.toml` exists, e.g. `uv run pytest`.