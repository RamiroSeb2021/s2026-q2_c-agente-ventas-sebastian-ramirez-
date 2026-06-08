# Implementation Tasks: Streamlit Sales Query Agent

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 700-1100 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 → PR 5 |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

## Task Slices

### Slice 1 — uv scaffold and deterministic data seeding

- [x] **Scaffold Python project files** in `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, and `.gitignore` for a testable Python app; keep generated artifacts (`data/*.csv`, `*.db`, `outputs/`) ignored and document only non-secret config keys in `.env.example`.
- [x] **RED: add seed tests** in `tests/test_seed_database.py` covering required `ventas` columns, SQLite table creation expectations, row count, and required values for `scripts/seed_database.py`.
- [x] **GREEN: implement deterministic seeding** in `scripts/seed_database.py` to generate `data/sales.db` from fixed seeds without Bedrock involvement.
- [x] **REFACTOR: normalize seed configuration** in `scripts/seed_database.py` so `SALES_DB_PATH` can override the default database path for local runs, tests, and future Compose startup.
- [x] **Validate Slice 1** with `uv run pytest tests/test_seed_database.py`; manual SQLite inspection confirmed the generated `ventas` table is readable through `sqlite3`.

### Slice 2 — SQL validation and Bedrock adapter

- [x] **RED: add SQL validator tests** in `tests/test_sql_validation.py` for safe `SELECT` queries, rejected multi-statement SQL, rejected DDL/DML, rejected unknown tables/columns, SQLite-specific unsafe commands such as `PRAGMA` and `ATTACH`, mandatory `LIMIT`, date grouping, and rejected SQL comments.
- [x] **GREEN: implement SQL validator** in `src/sales_query_agent/sql_validation.py` with a structured validation result used before query execution.
- [x] **GREEN: implement Bedrock configuration/client/prompt modules** in `src/sales_query_agent/config.py`, `src/sales_query_agent/bedrock_client.py`, and `src/sales_query_agent/prompts.py` so Bedrock generates candidate SQL only, with sanitized config/provider errors and explicit `ventas` schema prompting.
- [x] **TRIANGULATE: add Bedrock-facing tests** in `tests/test_prompts.py`, `tests/test_bedrock_client.py`, and `tests/test_config.py` for required environment handling, SQL-only prompt constraints, supported refusal sentinels, and user-facing error behavior when config is missing.
- [x] **Validate Slice 2** with `uv run pytest`; the current full suite passes.

### Slice 3 — MCP connector decision, wrapper, and LangGraph flow

- [x] **Finalize the SQLite MCP connector choice** by selecting `mcp-server-sqlite`, run through `uv`, and documenting why it satisfies the assignment better than direct `sqlite3`.
- [x] **RED: add MCP wrapper tests** in `tests/test_mcp_client.py` for validated read-query execution and empty results through the MCP tool boundary.
- [x] **GREEN: implement MCP wrapper** in `src/sales_query_agent/mcp_client.py` to connect to `mcp-server-sqlite` against `data/sales.db` and expose `execute_readonly_sales_query_via_mcp(sql, db_path)`.
- [ ] **DEFERRED: implement richer multi-node LangGraph state flow** with separate nodes for SQL generation, SQL validation, MCP execution, and result formatting; current slice intentionally uses the minimal `src/sales_query_agent/agent_graph.py` boundary and keeps this expansion for a later review unit.
- [x] **GREEN: add minimal LangGraph boundary** in `src/sales_query_agent/agent_graph.py` so Streamlit calls an agent framework entrypoint before the existing query service; keep richer multi-node MCP orchestration deferred.
- [ ] **REFACTOR: consolidate typed state/result models** in `src/agent/graph.py` and/or `src/models.py` if needed so UI integration does not duplicate normalization logic.
- [x] **Validate current Slice 3 boundary** with pytest coverage for MCP wrapper and minimal graph; richer multi-node graph validation remains deferred with that future task.

### Slice 4 — Streamlit UI and unsupported-output handling

- [ ] **RED: add UI-focused tests where practical** in `tests/test_app_smoke.py` or module-level tests for empty-result handling, visible SQL, fixed MCP status/test display, unsupported chart/export messaging, and sanitized error propagation from the graph layer.
- [ ] **GREEN: implement Streamlit entrypoint** in `app.py` and any small UI helper module under `src/ui/` to accept natural-language questions, show configured MCP status/test controls in the sidebar, always show generated SQL, render table results, and clearly defer charts/CSV/Excel in the first slice.
- [x] **REFACTOR: convert Streamlit input/output to chat UI** in `app.py` with `st.session_state.messages`, `st.chat_input`, prior-message rendering through `st.chat_message`, assistant SQL/table rendering for in-scope questions, and assistant-only refusal for out-of-scope questions.
- [x] **REFACTOR: add mandatory LIMIT guardrail** in the prompt and SQL validator so full-table or no-limit requests cannot execute unbounded queries; validate with prompt and SQL validator regression tests.
- [x] **TRIANGULATE: connect app to minimal LangGraph flow** by wiring `app.py` to `src/sales_query_agent/agent_graph.py` without embedding SQL generation, validation, or SQLite access inside the UI layer.
- [ ] **Validate Slice 4** by running, once files exist: `uv run pytest tests/test_app_smoke.py` and a manual Streamlit check using a representative question such as “Top 5 productos más vendidos en Medellín”.

### Slice 5 — Docker/Compose packaging, docs, and end-to-end verification

- [x] **Implement partial Docker packaging** in `Dockerfile` and `compose.yaml` so the app installs from `pyproject.toml`/`uv.lock`, keeps secrets out of the image, runs the seed/init command before the app service, and keeps SQLite MCP execution inside the app-managed connector process for this slice.
- [ ] **Document runtime and architecture** in `README.md` and, if needed, `docs/architecture.md` or `docs/usage.md`, covering `uv`, deterministic data generation, Bedrock role, MCP role, Compose startup order, and first-slice limitations.
- [ ] **Add verification guidance** to `README.md` and/or `openspec/changes/streamlit-sales-query-agent/verify-report.md` template notes with commands to run after files exist: targeted `uv run pytest ...`, `uv run streamlit run app.py`, and `docker compose up --build`.
- [ ] **Run end-to-end verification** after implementation exists: seed generation, MCP connectivity, visible SQL in Streamlit, table output for a happy-path sales query, empty-result handling, unsupported output messaging, and Docker Compose startup.

## Recommended Apply Order

- Slice 1 is complete; it establishes reproducible scaffolding and generated data artifacts.
- Apply Slice 2 next; Bedrock and SQL safety should exist before MCP and UI work.
- Apply Slice 3 before Slice 4; the UI should consume a stable graph/MCP boundary.
- Apply Slice 5 last; packaging should reflect working app behavior instead of guessing early.

## Split Warning

- Do **not** attempt all slices in one apply step.
- The likely total diff is well above the 400-line review budget because it spans scaffolding, tests, Bedrock integration, LangGraph orchestration, MCP integration, Streamlit UI, and Docker/Compose.
- Preferred chain:
  - **PR 1:** Slice 1
  - **PR 2:** Slice 2
  - **PR 3:** Slice 3
  - **PR 4:** Slice 4
  - **PR 5:** Slice 5
