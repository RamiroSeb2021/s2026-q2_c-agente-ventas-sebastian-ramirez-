# Technical Design: Streamlit Sales Query Agent

## Summary

This design defines the `streamlit-sales-query-agent` flow: a Streamlit app where a user asks a natural-language sales question, Amazon Bedrock generates a candidate SQLite `SELECT` query, the app validates the query deterministically, and query execution uses a SQLite MCP boundary over a locally generated SQLite database.

Current implementation status: the chat UI, Bedrock adapter, SQL validator, Docker packaging, minimal LangGraph boundary, and `mcp-server-sqlite` execution boundary are implemented; richer multi-node orchestration remains future work.

The first slice intentionally returns a visible SQL query and a table result only. Charts and CSV/Excel exports remain future extensions.

## Design Goals

- Prove the core assignment flow end-to-end with a small, reviewable implementation.
- Use Bedrock for semantic intent and SQL generation only.
- Generate reproducible simulated sales data locally with a fixed-seed Python script.
- Preserve a swappable SQL execution boundary around the current `mcp-server-sqlite` connector.
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
  creates data/sales.db
        │
        ▼
SQLite MCP server/connector
  mcp-server-sqlite read_query tool
        │
        ▼
Streamlit app
  app.py UI shell
  src/sales_query_agent/agent_graph.py minimal LangGraph boundary
  src/sales_query_agent/bedrock_client.py Bedrock adapter
  src/sales_query_agent/prompts.py SQL-generation prompts
  src/sales_query_agent/sql_validation.py deterministic validator
  src/sales_query_agent/mcp_client.py narrow MCP query wrapper
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

1. Local setup runs the deterministic seed command before app startup.
2. `scripts/seed_database.py` creates/refreshes the generated SQLite artifact:
   - `data/sales.db`
3. Current runtime launches `mcp-server-sqlite` against the generated database path through the MCP Python SDK.
4. User submits a question in Streamlit.
5. Current runtime calls a minimal LangGraph boundary, which builds agent state with the user question, config, and Bedrock client before delegating to the query service.
6. `src/sales_query_agent/bedrock_client.py` sends the prompt to Amazon Bedrock.
7. Bedrock returns candidate SQL.
8. `src/sales_query_agent/sql_validation.py` validates the SQL.
9. If valid, `src/sales_query_agent/mcp_client.py` calls the SQLite MCP connector's `read_query` tool.
10. Streamlit displays the interaction in chat form:
    - the user question as a user chat message;
    - generated SQL, always visible inside the assistant message for successful in-scope queries;
    - table results, empty-state message, or sanitized error inside the assistant message.
11. For out-of-scope questions, Streamlit displays only a polite assistant refusal and skips SQL/table rendering.

## Module Boundaries

### `app.py`

Streamlit entrypoint and UI composition only.

Responsibilities:

- Page title, chat prompt input, loading/error states.
- Sidebar/settings panel with configured AWS region/model, generated DB path, MCP connection status, and a "test MCP connection" control.
- Maintain `st.session_state.messages` and render prior conversation turns with `st.chat_message`.
- Accept new questions with `st.chat_input`, then append and render the user message immediately.
- Display generated SQL and result table inside the assistant chat message for successful in-scope sales questions.
- Show a polite assistant refusal for out-of-scope questions, with no generated SQL block and no dataframe.
- Show unsupported-output notice for chart/export requests in first slice.
- Call the agent graph; do not generate SQL, validate SQL, or query SQLite directly.
- Do not implement a generic MCP administration UI. The MCP target is fixed/configured by environment or Compose, and Streamlit only displays/tests that configured connection.

### `src/sales_query_agent/config.py`

Configuration loading and validation.

Responsibilities:

- Read `AWS_REGION`, `MODEL_ID`, and fixed/configured app/MCP settings from environment.
- Define generated paths such as `data/sales.db`.
- Define MCP connection settings such as transport, URL/command/service name, and database path according to the selected connector.
- Validate required settings with clear user-facing messages.
- Never read or store AWS secret values directly; rely on the AWS credential chain.

### `src/sales_query_agent/bedrock_client.py`

Bedrock adapter.

Responsibilities:

- Create the Bedrock runtime client.
- Invoke the configured model.
- Return the model response as text or structured candidate SQL.
- Convert provider errors into sanitized application errors.

Pattern to reuse: the previous Bedrock chat repo's separation of config and Bedrock client calls. Do not reuse its chat-specific prompt behavior directly.

### `src/sales_query_agent/prompts.py`

Prompt and schema instructions.

Responsibilities:

- Define the `ventas` schema context.
- Instruct the model to produce one SQLite `SELECT` query only.
- State that the model must not create, alter, insert, update, delete, or generate dataset rows.
- Include output format guidance, ideally a small structured format for candidate SQL and optional unsupported-output intent.

Prompting is not the safety boundary; it only reduces invalid outputs. The deterministic validator remains mandatory.

### `src/sales_query_agent/agent_graph.py`

Minimal LangGraph orchestration boundary implemented in the current slice.

Current state fields:

- `question: str`
- `config: AppConfig`
- `bedrock_client: BedrockConverseClient`
- `result: SalesQuestionResult | None`

Current node:

1. `answer_sales_question`: delegates to the existing query service and returns the result in graph state.

Future MCP work should expand this graph into separate generate, validate, execute-via-MCP, and format nodes. The graph must not call any execution node when validation fails.

### `src/sales_query_agent/sql_validation.py`

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

Current implementation note: the first validator is intentionally conservative token/regex validation, not a complete SQL parser. Its safety boundary is the combination of single-statement `SELECT`, schema allowlist, blocked keyword rejection, comment rejection, required numeric `LIMIT`, and execution through the MCP SQLite `read_query` tool only. Use a SQL parser library in a later slice if broader SQL support is needed.

### `src/sales_query_agent/mcp_client.py`

Narrow SQLite MCP wrapper.

Responsibilities:

- Launch and connect to `mcp-server-sqlite` with the fixed generated database path.
- Expose a narrow app-level surface: validated `execute_readonly_sales_query(sql)` for chat execution plus fixed sidebar diagnostics for listing configured tables and describing `ventas`.
- Accept only SQL that has passed `src/sales_query_agent/sql_validation.py`.
- Return normalized columns and rows for Streamlit.
- Surface connector failures without exposing stack traces or secrets in the UI.
- Keep user configuration out of the browser: no arbitrary MCP command/transport registration from Streamlit in the first slice.

This wrapper is the authoritative query execution path for sales queries. The older direct SQLite helper remains available for low-level/local tests but is no longer used by the query service.

### `scripts/seed_database.py`

Deterministic data generator and DB initializer.

Responsibilities:

- Use a fixed random seed defined in code or config.
- Generate repeatable sellers, branches, products, quantities, prices, and dates.
- Create or refresh `data/sales.db` with the `ventas` table.
- Be idempotent: repeated runs with the same seed produce equivalent data.

The script is source of truth; `data/sales.db` is a generated artifact ignored by git.

## SQLite MCP Connector Decision

The selected connector is `mcp-server-sqlite`, run through `uv run --frozen --no-dev mcp-server-sqlite --db-path <path>` and called with the MCP Python SDK.

Decision for design: **keep the connector choice as an explicit implementation decision**, with these evaluation criteria:

- Supports SQLite database files.
- Runs locally in Docker/Compose or as a managed subprocess.
- Provides a stable MCP transport supported by the Python app or chosen framework.
- Can be configured by environment/Compose rather than arbitrary browser input.
- Can be configured to operate on the generated `data/sales.db` path.
- Allows a narrow query-execution tool/resource interface.
- Has acceptable maintenance status and setup complexity for a 3-4 hour assignment.
- Does not require committing generated DB files or credentials.

Candidate classes to evaluate during apply:

- A Docker-capable SQLite MCP server as a separate Compose service.
- A Python MCP SQLite server installed through `uv` and launched as a managed subprocess.

Do not silently replace MCP with direct `sqlite3` querying. If the selected connector cannot be made to work in time, implementation must document the deferral and keep `src/sales_query_agent/mcp_client.py` as a swappable boundary, but that would be a risk against assignment acceptance.

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
    mounts: ~/.aws:/root/.aws for AWS SSO local dev, if needed
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
- Do not bake `.env`, AWS credentials, generated DB, or outputs into the image.
- Provide `.env.example` with non-secret values such as `AWS_REGION` and `MODEL_ID`.
- For local Bedrock credentials, rely on AWS credential chain or mount `~/.aws:/root/.aws` in Compose when using AWS SSO; SSO token refresh can require write access to the cache directory.

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
- MCP SQLite execution receives only validated SQL.
- Valid sales SQL must include a numeric `LIMIT` clause so prompt or export-like requests cannot dump the full table unbounded.
- SQLite query execution goes through the MCP `read_query` tool after validation; do not bypass validation or embed SQL execution in the UI.
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
  - rejects otherwise valid sales queries without `LIMIT`;
  - rejects `PRAGMA`, `ATTACH`, and `DETACH`.
- Unit or integration test for MCP wrapper:
  - wrapper does not execute when validation fails;
  - wrapper handles connector errors cleanly.
- Manual Streamlit validation:
  - ask “Top 5 productos más vendidos en Medellín”;
  - verify the user question appears as a user chat message;
  - verify generated SQL is visible;
  - verify table output appears in the assistant chat message;
  - ask an out-of-scope question and verify the assistant refuses without showing SQL or a dataframe.

Command names must not be documented as verified until implementation files exist and commands have run successfully.

## Review Budget and Work Slicing

The session review budget is 400 changed lines. Implementation should be split if needed:

1. Scaffold and seed script with tests.
2. Bedrock/config/prompts and SQL validator with tests.
3. Minimal LangGraph boundary, then MCP wrapper and richer graph flow.
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
- Docker/Compose pattern with runtime AWS configuration mount; AWS SSO may require write access for token cache refresh.

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
