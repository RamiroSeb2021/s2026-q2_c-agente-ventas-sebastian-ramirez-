# Proposal: Streamlit Sales Query Agent (First Slice)

## Motivation & Problem

The repository now has a verified Slice 1 Python/uv scaffold and deterministic SQLite `ventas` seed, but still lacks a runnable Streamlit application for the Agentic AI sales analysis assignment. To incrementally build the solution and minimize risk, the remaining vertical slices must prove the core assumptions: using Amazon Bedrock for semantic intent and SQL generation, querying a local SQL database through MCP, and rendering the result in a Streamlit UI, all managed via `uv`.

The assignment explicitly recommends MCP-compatible connectors for database access. Therefore, this first slice should not treat SQLite as a private in-process implementation detail. It should model SQLite as a local SQL system exposed to the app through a preexisting SQLite MCP server or connector.

## Proposed Change

Implement the first functional slice of the sales agent. The application will use Streamlit for the user interface and Amazon Bedrock to translate natural-language sales questions into validated SQLite `SELECT` queries. Sales data will be generated locally by a deterministic Python seed script and loaded into a generated local SQLite database. SQL execution will happen through a SQLite MCP server/connector, not by directly querying SQLite from the Streamlit app.

The UI will explicitly show the generated SQL for transparency and educational purposes, followed by the query result table.

## Scope (First Slice)

- **Dependency Management**: Use the existing `uv` project configuration in `pyproject.toml` and `uv.lock`.
- **Data Generation**: Reuse the completed deterministic `scripts/seed_database.py` seed script, which creates the local SQLite `ventas` table with fixed-seed sample data.
- **Generated Data Artifacts**: Treat `data/sales.db` as a reproducible runtime artifact, not source of truth.
- **MCP SQL Access**: Use a preexisting SQLite MCP server/connector to expose the generated SQLite database to the app. The Streamlit app should act as the MCP client or use a framework integration that calls the MCP tool boundary.
- **LLM Integration**: Use Amazon Bedrock to detect user intent and generate valid SQLite queries over the known `ventas` schema.
- **SQL Safety**: Validate generated SQL before MCP execution. Allow only a single read-only `SELECT` statement against the `ventas` table and approved columns/functions.
- **User Interface**: Build a Streamlit app where users can input natural-language sales questions.
- **Transparency**: Always display the generated SQL query to the user before the results.
- **Output**: Display the query results as a data table in the UI.
- **Architecture**: Begin setting up the basic agent framework (LangChain/LangGraph/Strands) as required by the assignment constraints, while keeping Bedrock, SQL validation, MCP access, and Streamlit UI modular.

## Non-Goals (First Slice)

- Generating charts or visual plots (e.g., Plotly, Matplotlib).
- Exporting results to CSV or Excel files.
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

## Docker / Compose Direction

Docker packaging remains a target for the assignment. The design should plan for:

- a Streamlit app container built from `pyproject.toml` and `uv.lock` using `uv`;
- a SQLite MCP server as a separate Compose service or a clearly documented managed subprocess, with preference for a separate service if feasible;
- a seed/init command that runs the deterministic Python script before the app and MCP server depend on the generated DB;
- a shared read/write data volume or bind mount for generated data files and the generated SQLite database;
- `.env` for non-secret app configuration such as `AWS_REGION` and `MODEL_ID`;
- AWS credentials provided through the normal AWS credential chain, for local development commonly by mounting `~/.aws:/root/.aws:ro`;
- no AWS credentials, `.env`, generated DB files, or runtime exports committed to the repository.

## User Flow

1. User prepares dependencies with `uv` using the existing `pyproject.toml` and `uv.lock`.
2. User launches the Streamlit app locally, eventually through `uv run streamlit run app.py` or Docker Compose once those files exist.
3. Docker Compose or the local setup runs the deterministic seed script to generate `data/sales.db` if needed.
4. The SQLite database is exposed through a SQLite MCP server/connector.
5. User enters a natural-language question (e.g., "Top 5 productos más vendidos en Medellín").
6. The application sends the schema and question to the agent framework powered by Amazon Bedrock.
7. The agent generates a SQL query based on semantic intent.
8. The app validates that the SQL is read-only, single-statement, and limited to the allowed `ventas` schema.
9. The Streamlit UI displays the generated SQL query.
10. The app executes the validated query through the SQLite MCP server/connector.
11. The Streamlit UI renders the returned data as a table.

## Data and Artifact Policy

- Commit the deterministic seed script, not generated datasets.
- Do not commit generated CSV datasets (`data/*.csv`) unless explicitly requested as a tiny example artifact.
- Do not commit generated SQLite databases (`*.db`, `*.sqlite`, `*.sqlite3`).
- Do not commit runtime output folders such as `outputs/`.
- The seed script plus fixed random seed is the source of truth; CSV and SQLite DB files can be regenerated.

## Risks & Edge Cases

- **Dataset reproducibility**: Randomly generated data can drift across runs if not controlled. Mitigation: use a fixed random seed and document the seed command used by Docker Compose/local setup.
- **MCP connector choice**: The exact SQLite MCP server/connector must be selected during design. Mitigation: evaluate a preexisting connector and document why it was chosen; if MCP is deferred, explicitly justify the deferral and keep the SQL access module swappable.
- **LLM hallucinations**: Bedrock might generate invalid SQL or target non-existent columns. Mitigation: provide strict table schema context and validate SQL before MCP execution.
- **Unsafe SQL**: Prompt instructions alone cannot guarantee safety. Mitigation: enforce single-statement `SELECT` only; reject `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `ATTACH`, `DETACH`, `PRAGMA`, semicolon chains, unknown tables, and unknown columns.
- **AWS configuration**: Users running the app locally without properly configured AWS credentials for Bedrock will face application errors. Mitigation: add startup validation or clear sanitized error messages if credentials, region, or model access are missing.
- **Docker credential leakage**: Docker images and repository files must not contain AWS credentials. Mitigation: use `.env.example` for non-secret variables only, ignore real `.env`, and mount AWS credentials read-only for local development if needed.
- **Error exposure**: Raw stack traces may leak sensitive paths or config. Mitigation: show friendly user-facing errors and keep technical diagnostics limited to local logs/debug mode.

## Open Questions

- Which specific agent framework (LangChain, LangGraph, or Strands) will be selected to wrap the Bedrock call and MCP tool access for this initial slice? (To be resolved in the design phase.)
- Which preexisting SQLite MCP server/connector will be used, and will it run as a Compose service or as a local managed subprocess? (To be resolved in the design phase.)
