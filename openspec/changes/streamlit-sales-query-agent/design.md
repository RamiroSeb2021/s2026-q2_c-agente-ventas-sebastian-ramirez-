# Technical Design: Streamlit Sales Query Agent

## Summary

This design defines the first implementation slice for `streamlit-sales-query-agent`: a Streamlit app where a user asks a natural-language sales question, Amazon Bedrock generates a candidate SQLite `SELECT` query, the app validates the query deterministically, and query execution happens through a SQLite MCP boundary over a locally generated SQLite database.

The first slice intentionally returns a visible SQL query and a table result only. Charts and CSV/Excel exports remain future extensions.

## Design Goals

- Prove the core assignment flow end-to-end with a small, reviewable implementation.
- Use Bedrock for semantic intent and SQL generation only.
- Generate reproducible simulated sales data locally with a fixed-seed Python script.
- Execute validated SQL through an MCP SQLite connector, not direct app-side SQLite querying.
- Keep the Streamlit UI, Bedrock adapter, agent orchestration, SQL validation, MCP access, and data seeding modular.
- Prepare for Docker/Compose packaging without embedding AWS credentials or generated data in source control.

## Non-Goals for First Slice

- Charts, Plotly/Matplotlib/Altair visuals, and dashboard layout polish.
- CSV/Excel export generation.
- Production database connectivity.
- Multi-agent planning loops or complex tool routing beyond the SQL query flow.
- LLM-generated datasets or LLM-driven database mutation.

## High-Level Architecture

```text
scripts/seed_database.py
  fixed random seed
  generates data/ventas.csv
  creates data/ventas.db
        │
        ▼
SQLite MCP server/connector
  exposes generated SQLite DB as an MCP tool/resource
        │
        ▼
Streamlit app
  app.py UI shell
  src/agent/graph.py orchestration
  src/bedrock_client.py Bedrock adapter
  src/prompts.py SQL-generation prompts
  src/sql_validation.py deterministic validator
  src/mcp_client.py narrow MCP query wrapper
        │
        ▼
User sees generated SQL + table result
```

Bedrock never creates the dataset and never executes SQL. It only receives the user question plus schema context and returns a candidate SQL query or structured response containing SQL.

## Recommended Orchestration Framework

Use **LangGraph** for the first slice.

Rationale:

- The flow is naturally stateful and staged: `question -> generate_sql -> validate_sql -> execute_query -> format_result`.
- The `eci_genai` reference demonstrates LangGraph concepts such as state graphs, explicit nodes, tool routing, and visualization. Those patterns map well to this assignment and are teachable.
- LangGraph keeps the MCP execution node separate from SQL generation and validation, making it harder to accidentally bypass validation.
- Plain LangChain would also work, but LangGraph better documents the control flow for an educational project.

If implementation later chooses LangChain or Strands, it must preserve the same node boundaries and explain why the alternate framework is simpler.

## Runtime Data Flow

1. Local setup or Compose runs the deterministic seed command.
2. `scripts/seed_database.py` creates/refreshes generated artifacts:
   - `data/ventas.csv`
   - `data/ventas.db`
3. SQLite MCP connector starts against the generated database path.
4. User submits a question in Streamlit.
5. `src/agent/graph.py` builds agent state with the user question and schema description.
6. `src/bedrock_client.py` sends the prompt to Amazon Bedrock.
7. Bedrock returns candidate SQL.
8. `src/sql_validation.py` validates the SQL.
9. If valid, `src/mcp_client.py` executes the query through the SQLite MCP connector.
10. Streamlit displays:
    - generated SQL, always visible;
    - table results, empty-state message, or sanitized error.

## Module Boundaries

### `app.py`

Streamlit entrypoint and UI composition only.

Responsibilities:

- Page title, prompt input, loading/error states.
- Sidebar/settings panel with configured AWS region/model, generated DB path, MCP connection status, and a "test MCP connection" control.
- Display generated SQL and result table.
- Show unsupported-output notice for chart/export requests in first slice.
- Call the agent graph; do not generate SQL, validate SQL, or query SQLite directly.
- Do not implement a generic MCP administration UI. The MCP target is fixed/configured by environment or Compose, and Streamlit only displays/tests that configured connection.

### `src/config.py`

Configuration loading and validation.

Responsibilities:

- Read `AWS_REGION`, `MODEL_ID`, and fixed/configured app/MCP settings from environment.
- Define generated paths such as `data/ventas.db` and `data/ventas.csv`.
- Define MCP connection settings such as transport, URL/command/service name, and database path according to the selected connector.
- Validate required settings with clear user-facing messages.
- Never read or store AWS secret values directly; rely on the AWS credential chain.

### `src/bedrock_client.py` or `src/llm.py`

Bedrock adapter.

Responsibilities:

- Create the Bedrock runtime client.
- Invoke the configured model.
- Return the model response as text or structured candidate SQL.
- Convert provider errors into sanitized application errors.

Pattern to reuse: the previous Bedrock chat repo's separation of config and Bedrock client calls. Do not reuse its chat-specific prompt behavior directly.

### `src/prompts.py`

Prompt and schema instructions.

Responsibilities:

- Define the `ventas` schema context.
- Instruct the model to produce one SQLite `SELECT` query only.
- State that the model must not create, alter, insert, update, delete, or generate dataset rows.
- Include output format guidance, ideally a small structured format for candidate SQL and optional unsupported-output intent.

Prompting is not the safety boundary; it only reduces invalid outputs. The deterministic validator remains mandatory.

### `src/agent/graph.py`

LangGraph orchestration.

Proposed state fields:

- `question: str`
- `generated_sql: str | None`
- `validation_error: str | None`
- `rows: list[dict] | None`
- `columns: list[str] | None`
- `user_message: str | None`
- `unsupported_output_requested: bool`
- `error: str | None`

Proposed nodes:

1. `generate_sql`: call Bedrock with schema-aware prompt.
2. `validate_sql`: call deterministic validator.
3. `execute_sql_via_mcp`: call narrow MCP wrapper only if validation passed.
4. `format_result`: normalize success, empty result, or error for the UI.

The graph must not call the MCP execution node when validation fails.

### `src/sql_validation.py`

Deterministic SQL validator independent of Bedrock.

Responsibilities:

- Accept a candidate SQL string.
- Reject unsafe or unsupported SQL before MCP execution.
- Return a structured result such as `{ok, normalized_sql, error}`.

Validation rules:

- Exactly one SQL statement.
- Statement must be `SELECT` only.
- Query may reference only table `ventas`.
- Query may reference only columns:
  - `id`
  - `vendedor`
  - `sede`
  - `producto`
  - `cantidad`
  - `precio`
  - `fecha`
- Reject `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, `TRUNCATE`, `ATTACH`, `DETACH`, `PRAGMA`, `VACUUM`, transaction statements, and semicolon chains.
- Reject multiple statements and comments that hide additional statements.
- Allow common read-only aggregate/scalar functions needed for the assignment, such as `SUM`, `COUNT`, `AVG`, `MIN`, `MAX`, date extraction supported by SQLite, and arithmetic expressions over allowed columns.

Implementation note for later apply phase: use a SQL parser library when feasible instead of fragile keyword-only checks. If a library is not selected, keep the first validator conservative and document limitations.

### `src/mcp_client.py` or `src/sql_tool.py`

Narrow SQLite MCP wrapper.

Responsibilities:

- Connect to the fixed/configured SQLite MCP server/connector.
- Expose only two app-level operations: `check_connection()` for UI status/testing and `execute_readonly_sales_query(sql)` for validated query execution.
- Accept only SQL that has passed `src/sql_validation.py`.
- Return normalized columns and rows for Streamlit.
- Surface connector failures without exposing stack traces or secrets in the UI.
- Keep user configuration out of the browser: no arbitrary MCP command/transport registration from Streamlit in the first slice.

This wrapper is the only authoritative first-slice query execution path. Direct SQLite access is allowed only inside deterministic seed/init code.

### `scripts/seed_database.py`

Deterministic data generator and DB initializer.

Responsibilities:

- Use a fixed random seed defined in code or config.
- Generate repeatable sellers, branches, products, quantities, prices, and dates.
- Write `data/ventas.csv` as a generated artifact.
- Create or refresh `data/ventas.db` with the `ventas` table.
- Be idempotent: repeated runs with the same seed produce equivalent data.

The script is source of truth; `data/ventas.csv` and `data/ventas.db` are generated artifacts ignored by git.

## SQLite MCP Connector Decision

The design requires a preexisting SQLite MCP connector, but this phase does not verify a specific package by installing or running it.

Decision for design: **keep the connector choice as an explicit implementation decision**, with these evaluation criteria:

- Supports SQLite database files.
- Runs locally in Docker/Compose or as a managed subprocess.
- Provides a stable MCP transport supported by the Python app or chosen framework.
- Can be configured by environment/Compose rather than arbitrary browser input.
- Can be configured to operate on the generated `data/ventas.db` path.
- Allows a narrow query-execution tool/resource interface.
- Has acceptable maintenance status and setup complexity for a 3-4 hour assignment.
- Does not require committing generated DB files or credentials.

Candidate classes to evaluate during apply:

- A Docker-capable SQLite MCP server as a separate Compose service.
- A Python MCP SQLite server installed through `uv` and launched as a managed subprocess.

Do not silently replace MCP with direct `sqlite3` querying. If the selected connector cannot be made to work in time, implementation must document the deferral and keep `src/mcp_client.py` as a swappable boundary, but that would be a risk against assignment acceptance.

## Docker / Compose Topology

Target local topology:

```text
compose.yaml
  seed service or init command
    runs: uv run python scripts/seed_database.py
    writes: generated data volume

  sqlite-mcp service
    depends_on: seed completed successfully, if supported
    mounts: generated data volume
    exposes: MCP transport for app

  app service
    builds: Dockerfile with uv
    depends_on: sqlite-mcp
    env_file: .env
    environment: fixed MCP connection settings
    mounts: ~/.aws:/root/.aws:ro for local dev, if needed
    serves: Streamlit on 8501
    UI: shows MCP status/test, but does not let users register arbitrary MCP servers
```

Depending on Compose features and selected MCP connector, the seed step can be represented as:

- a one-shot `seed` service; or
- an app entrypoint/prestart command; or
- a documented local command before `docker compose up`.

Preference: one-shot `seed` service because it makes the dependency visible and keeps Bedrock/app startup separate from data generation.

Docker rules:

- Build app dependencies from `pyproject.toml` and `uv.lock` using `uv`.
- Do not bake `.env`, AWS credentials, generated CSV, generated DB, or outputs into the image.
- Provide `.env.example` with non-secret values such as `AWS_REGION` and `MODEL_ID`.
- For local Bedrock credentials, rely on AWS credential chain or mount `~/.aws:/root/.aws:ro` in Compose.

## Dependency Plan with `uv`

First-slice dependencies should be declared in `pyproject.toml` and locked in `uv.lock`.

Likely runtime categories:

- UI: `streamlit`
- AWS: `boto3` or Bedrock-compatible LangChain integration
- Agent orchestration: `langgraph` plus required LangChain core packages
- Data handling: Python stdlib `csv`, `sqlite3`, `random`, `datetime` may be enough for seeding; `pandas` is optional for table normalization but not required
- MCP: selected MCP client/server packages or Docker image integration
- SQL parsing/validation: a parser library if selected during apply

Likely dev group:

- test runner (`pytest`) once tests are introduced
- formatter/linter (`ruff`)
- optional type checker if kept within budget

Do not run `uv sync` until `pyproject.toml` exists and dependencies are inspected.

## Error Handling and Security

User-facing errors must be clear and sanitized.

Expected error classes:

- Missing Bedrock config or credentials.
- Bedrock generation failure.
- Invalid or unsafe generated SQL.
- MCP connector unavailable.
- SQLite query execution failure through MCP.
- Empty result set.
- Unsupported chart/export request in first slice.

Security boundaries:

- Bedrock output is untrusted until validated.
- MCP execution receives only validated SQL.
- No direct app-side SQL execution in first-slice query flow.
- No AWS credentials in repo, Docker image, generated files, or logs.
- No generic shell tools or `eval`-based dispatch.

## Validation Plan

During apply/verify, add focused validation appropriate to the first slice:

- Unit tests for deterministic seeding:
  - same seed produces equivalent `ventas` rows;
  - required columns exist;
  - generated DB contains the `ventas` table.
- Unit tests for SQL validation:
  - accepts representative safe `SELECT` queries;
  - rejects DML/DDL;
  - rejects multi-statement SQL;
  - rejects unknown tables and columns;
  - rejects `PRAGMA`, `ATTACH`, and `DETACH`.
- Unit or integration test for MCP wrapper:
  - wrapper does not execute when validation fails;
  - wrapper handles connector errors cleanly.
- Manual Streamlit validation:
  - ask “Top 5 productos más vendidos en Medellín”;
  - verify generated SQL is visible;
  - verify table output appears.

Command names must not be documented as verified until implementation files exist and commands have run successfully.

## Review Budget and Work Slicing

The session review budget is 400 changed lines. Implementation should be split if needed:

1. Scaffold and seed script with tests.
2. Bedrock/config/prompts and SQL validator with tests.
3. MCP wrapper and LangGraph flow.
4. Streamlit UI integration.
5. Docker/Compose packaging.

If a slice approaches the budget, pause before continuing and propose a narrower follow-up change.

## Lessons from Reference Projects

### Previous Bedrock Streamlit App

Reuse:

- modular `app.py` + `src/` separation;
- config module for `AWS_REGION` and `MODEL_ID`;
- Bedrock client wrapper;
- `.env.example` for non-secret config;
- Docker/Compose pattern with read-only AWS credential mount.

Do not copy blindly:

- previous chat UI semantics;
- direct conversation-only prompt;
- any behavior that bypasses SQL validation or MCP.

### `eci_genai`

Reuse:

- `uv` project and lockfile mindset;
- dev dependency grouping;
- LangGraph as a teachable orchestration pattern;
- educational documentation flow;
- Compose as local reproducibility wrapper.

Avoid:

- notebook-time dependency installation;
- OpenAI-specific production classes;
- `eval` tool dispatch;
- generic shell-command tools;
- GPU/CUDA containers;
- RAG/vector-store scope in the first slice.

## Future Extensions

After the first slice is working:

- Add chart intent and chart rendering with Plotly, Matplotlib, or Altair.
- Add CSV and Excel export actions.
- Add richer result summarization in natural language.
- Add optional graph visualization for LangGraph flow documentation.
- Add support for additional SQL backends if a future assignment requires it.
- Harden MCP connector configuration for read-only execution if the chosen connector supports permission controls.
