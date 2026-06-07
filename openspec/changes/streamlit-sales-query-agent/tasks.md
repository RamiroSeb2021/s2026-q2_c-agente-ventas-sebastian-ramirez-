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

- [ ] **Scaffold Python project files** in `pyproject.toml`, `uv.lock`, `.python-version` (if used), `.env.example`, and `.gitignore` for a Streamlit + Bedrock + LangGraph + testable Python app; keep generated artifacts (`data/*.csv`, `*.db`, `outputs/`) ignored and document only non-secret config keys in `.env.example`.
- [ ] **RED: add seed reproducibility tests** in `tests/test_seed_database.py` covering fixed-seed reproducibility, required `ventas` columns, and SQLite table creation expectations for `scripts/seed_database.py`.
- [ ] **GREEN: implement deterministic seeding** in `scripts/seed_database.py` and any minimal helper such as `src/data_seed.py` to generate `data/ventas.csv` and `data/ventas.db` from a fixed random seed without Bedrock involvement.
- [ ] **REFACTOR: normalize seed configuration** in `src/config.py` and `scripts/seed_database.py` so paths/seed values are explicit, idempotent, and reusable by local runs and Compose startup.
- [ ] **Validate Slice 1** by running, once files exist: `uv run pytest tests/test_seed_database.py` and a manual check that `data/ventas.db` contains a `ventas` table with the expected schema.

### Slice 2 — SQL validation and Bedrock adapter

- [ ] **RED: add SQL validator tests** in `tests/test_sql_validation.py` for safe `SELECT` queries, rejected multi-statement SQL, rejected DDL/DML, rejected unknown tables/columns, and rejected SQLite-specific unsafe commands such as `PRAGMA` and `ATTACH`.
- [ ] **GREEN: implement SQL validator** in `src/sql_validation.py` with a structured validation result used before any MCP execution.
- [ ] **GREEN: implement Bedrock configuration/client/prompt modules** in `src/config.py`, `src/bedrock_client.py`, and `src/prompts.py` so Bedrock generates candidate SQL only, with sanitized config/provider errors and explicit `ventas` schema prompting.
- [ ] **TRIANGULATE: add Bedrock-facing tests** in `tests/test_prompts.py` and/or `tests/test_config.py` for required environment handling, SQL-only prompt constraints, and user-facing error behavior when config is missing.
- [ ] **Validate Slice 2** by running, once files exist: `uv run pytest tests/test_sql_validation.py tests/test_config.py tests/test_prompts.py`.

### Slice 3 — MCP connector decision, wrapper, and LangGraph flow

- [ ] **Finalize the SQLite MCP connector choice** by updating `openspec/changes/streamlit-sales-query-agent/design.md` with the selected package/image, transport, and why it satisfies the assignment better than direct `sqlite3`; keep the app-facing boundary in `src/mcp_client.py` narrow (`execute_readonly_sales_query`).
- [ ] **RED: add MCP wrapper and orchestration tests** in `tests/test_mcp_client.py` and `tests/test_graph.py` for validation-gated execution, fixed/configured connection health checks, connector failure handling, state transitions, and “do not call MCP when SQL validation fails.”
- [ ] **GREEN: implement MCP wrapper** in `src/mcp_client.py` and any thin adapter needed to connect to the chosen fixed/configured SQLite MCP server/connector against `data/ventas.db`; expose `check_connection()` plus `execute_readonly_sales_query(sql)` only.
- [ ] **GREEN: implement LangGraph state flow** in `src/agent/graph.py` with nodes for SQL generation, SQL validation, MCP execution, and result formatting; keep Bedrock, validation, and MCP concerns separated.
- [ ] **REFACTOR: consolidate typed state/result models** in `src/agent/graph.py` and/or `src/models.py` if needed so UI integration does not duplicate normalization logic.
- [ ] **Validate Slice 3** by running, once files exist: `uv run pytest tests/test_mcp_client.py tests/test_graph.py` and a focused manual connector smoke check against a generated `data/ventas.db`.

### Slice 4 — Streamlit UI and unsupported-output handling

- [ ] **RED: add UI-focused tests where practical** in `tests/test_app_smoke.py` or module-level tests for empty-result handling, visible SQL, fixed MCP status/test display, unsupported chart/export messaging, and sanitized error propagation from the graph layer.
- [ ] **GREEN: implement Streamlit entrypoint** in `app.py` and any small UI helper module under `src/ui/` to accept natural-language questions, show configured MCP status/test controls in the sidebar, always show generated SQL, render table results, and clearly defer charts/CSV/Excel in the first slice.
- [ ] **TRIANGULATE: connect app to LangGraph flow** by wiring `app.py` to `src/agent/graph.py` without embedding SQL generation, validation, or SQLite access inside the UI layer.
- [ ] **Validate Slice 4** by running, once files exist: `uv run pytest tests/test_app_smoke.py` and a manual Streamlit check using a representative question such as “Top 5 productos más vendidos en Medellín”.

### Slice 5 — Docker/Compose packaging, docs, and end-to-end verification

- [ ] **Implement Docker packaging** in `Dockerfile` and `compose.yaml` so the app installs from `pyproject.toml`/`uv.lock`, keeps secrets out of the image, runs the seed/init command before DB-dependent services, and models separate `seed`, `sqlite-mcp`, and `app` responsibilities with fixed MCP connection settings when feasible.
- [ ] **Document runtime and architecture** in `README.md` and, if needed, `docs/architecture.md` or `docs/usage.md`, covering `uv`, deterministic data generation, Bedrock role, MCP role, Compose startup order, and first-slice limitations.
- [ ] **Add verification guidance** to `README.md` and/or `openspec/changes/streamlit-sales-query-agent/verify-report.md` template notes with commands to run after files exist: targeted `uv run pytest ...`, `uv run streamlit run app.py`, and `docker compose up --build`.
- [ ] **Run end-to-end verification** after implementation exists: seed generation, MCP connectivity, visible SQL in Streamlit, table output for a happy-path sales query, empty-result handling, unsupported output messaging, and Docker Compose startup.

## Recommended Apply Order

- Apply Slice 1 first; it establishes reproducible scaffolding and generated data artifacts.
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
