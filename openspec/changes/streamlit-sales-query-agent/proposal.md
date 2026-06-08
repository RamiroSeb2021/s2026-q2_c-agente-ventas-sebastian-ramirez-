# Proposal: Streamlit Sales Query Agent (First Slice)

## Motivation & Problem

The repository now has a verified Python/uv scaffold, deterministic SQLite `ventas` seed, Bedrock SQL generation, and a chat-style Streamlit path. The remaining vertical slices must keep improving the solution toward the full assignment target: Amazon Bedrock for semantic intent and SQL generation, a local SQL database exposed through MCP, and Streamlit output rendering, all managed via `uv`.

The assignment explicitly recommends MCP-compatible connectors for database access. Current implementation now uses `mcp-server-sqlite` through the MCP Python SDK and its `read_query` tool after deterministic SQL validation.

## Proposed Change

Implement the current functional Streamlit/Bedrock/MCP slice of the sales agent. The application uses Streamlit for the user interface, a minimal LangGraph boundary for agent-framework routing, and Amazon Bedrock to translate natural-language sales questions into validated SQLite `SELECT` queries. Sales data is generated locally by a deterministic Python seed script and loaded into a generated local SQLite database. SQL execution happens through the `mcp-server-sqlite` MCP server via the `read_query` tool.

The UI will explicitly show the generated SQL for transparency and educational purposes, followed by the dataframe result and optional chart or download requested semantically by the user.

## Scope (First Slice)

- **Dependency Management**: Use the existing `uv` project configuration in `pyproject.toml` and `uv.lock`.
- **Data Generation**: Reuse the completed deterministic `scripts/seed_database.py` seed script, which creates the local SQLite `ventas` table with fixed-seed sample data.
- **Generated Data Artifacts**: Treat `data/sales.db` as a reproducible runtime artifact, not source of truth.
- **MCP SQL Access**: Use `mcp-server-sqlite` to expose the generated SQLite database to the app through MCP; the Streamlit app continues calling the agent boundary rather than database code directly.
- **LLM Integration**: Use Amazon Bedrock to detect sales intent, output intent, and generate valid SQLite queries over the known `ventas` schema.
- **SQL Safety**: Validate generated SQL before MCP execution. Allow only a single read-only `SELECT` statement against the `ventas` table and approved columns/functions, require a numeric `LIMIT`, reject comments and blocked write/admin keywords, and execute only through the MCP SQLite `read_query` tool.
- **User Interface**: Build a chat-style Streamlit app where users can submit natural-language sales questions with `st.chat_input` and review prior user/assistant messages.
- **Transparency**: Always display the generated SQL query to the user before the results.
- **Output**: Display the query results as a dataframe in the UI, with semantic chart, CSV, and Excel outputs when requested.
- **Architecture**: Begin setting up the basic agent framework (LangChain/LangGraph/Strands) as required by the assignment constraints, while keeping Bedrock, SQL validation, MCP access, and Streamlit UI modular.

## Non-Goals (Current Slice)

- Advanced multi-agent routing or complex tool-calling loops.
- Production database connectivity beyond the local SQLite assignment database.
- Full Docker implementation may be deferred, but the design must define how Docker/Compose will run the Streamlit app, SQLite MCP server, generated database, `.env`, and AWS credentials safely.

## Target Architecture

```text
scripts/seed_database.py    deterministic fixed-seed data generator
   ↓ creates/refreshes
data/sales.db               generated local SQLite database
   ↓ exposed through
SQLite MCP server/connector
   ↓ MCP tool call
Streamlit app + agent modules
   ↓ semantic SQL generation
Amazon Bedrock
```

The previous Bedrock chat project at `/home/sebastian-ramirez/trabajo/s2026-q2_c-llmbedrock-sebastian-ramirez` may be used as a reference for modular Streamlit, Bedrock configuration, `uv`, Docker, `.env.example`, and AWS credential handling patterns. It must not be copied blindly because this assignment adds a SQL/MCP boundary and query-safety requirements.

## Packaging Constraints

Packaging for this assignment must preserve these constraints:

- a Streamlit runtime built from `pyproject.toml` and `uv.lock` using `uv`;
- a SQLite MCP server or managed subprocess that is fixed by configuration, not user-entered from the browser;
- a seed/init command that runs the deterministic Python script before the app and MCP server depend on the generated DB;
- a shared read/write data volume or bind mount for generated data files and the generated SQLite database;
- `.env` for non-secret app configuration such as `AWS_REGION` and `BEDROCK_MODEL_ID`;
- AWS credentials provided through the normal AWS credential chain; for local AWS SSO development, Compose may mount `~/.aws:/root/.aws` read-write so botocore can refresh SSO token cache files;
- no AWS credentials, `.env`, generated DB files, or runtime exports committed to the repository.

## User Flow

1. User prepares dependencies with `uv` using the existing `pyproject.toml` and `uv.lock`.
2. User launches the Streamlit app locally through the documented runtime entrypoint.
3. Local `uv` runs can use the deterministic seed script directly before the app starts.
4. Current runtime uses `src/sales_query_agent/mcp_client.py` to launch `mcp-server-sqlite` and call its `read_query` tool.
5. User enters a natural-language question in the chat input (e.g., "Top 5 productos más vendidos en Medellín").
6. The application sends the schema and question to the agent framework powered by Amazon Bedrock.
7. The agent generates a structured query plan with semantic `output_type` and SQL.
8. The app validates that the SQL is read-only, single-statement, and limited to the allowed `ventas` schema.
9. The Streamlit UI displays the generated SQL query.
10. The app executes the validated query through the SQLite MCP connector.
11. The Streamlit UI renders the assistant response as a chat message with the generated SQL, returned dataframe, and optional chart/CSV/Excel output.
12. If the question is outside the `ventas` sales-analysis scope, the assistant chat message politely refuses and does not show SQL or a dataframe.

## Data and Artifact Policy

- Commit the deterministic seed script, not generated datasets.
- Do not commit generated CSV datasets (`data/*.csv`) unless explicitly requested as a tiny example artifact.
- Do not commit generated SQLite databases (`*.db`, `*.sqlite`, `*.sqlite3`).
- Do not commit runtime output folders such as `outputs/`.
- The seed script plus fixed random seed is the source of truth; CSV and SQLite DB files can be regenerated.

## Risks & Edge Cases

- **Dataset reproducibility**: Randomly generated data can drift across runs if not controlled. Mitigation: use a fixed random seed and document the seed command used by Docker Compose/local setup.
- **MCP connector choice**: The implementation uses `mcp-server-sqlite`, which exposes `read_query` for validated `SELECT` statements. Mitigation: keep the app-facing MCP wrapper narrow so another connector can replace it if needed.
- **LLM hallucinations**: Bedrock might generate invalid SQL or target non-existent columns. Mitigation: provide strict table schema context and validate SQL before MCP execution.
- **Unsafe SQL**: Prompt instructions alone cannot guarantee safety. Mitigation: enforce single-statement `SELECT` only; reject `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `ATTACH`, `DETACH`, `PRAGMA`, semicolon chains, unknown tables, and unknown columns.
- **Validator limitations**: The current validator is conservative token/regex validation, not a complete SQL parser. Mitigation: keep the accepted SQL subset intentionally narrow for this slice and add a parser later if broader SQL is required.
- **AWS configuration**: Users running the app locally without properly configured AWS credentials for Bedrock will face application errors. Mitigation: add startup validation or clear sanitized error messages if credentials, region, or model access are missing.
- **Credential leakage**: Runtime images and repository files must not contain AWS credentials. Mitigation: use `.env.example` for non-secret variables only, ignore real `.env`, and provide AWS credentials only at runtime.
- **Error exposure**: Raw stack traces may leak sensitive paths or config. Mitigation: show friendly user-facing errors and keep technical diagnostics limited to local logs/debug mode.

## Resolved Decisions

- Agent framework: use LangGraph as a minimal boundary before the query service in this slice.
- SQLite MCP connector: use `mcp-server-sqlite` as a managed subprocess through the MCP Python SDK.
