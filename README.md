# Sales Query Agent

Practical assignment scaffold for an Agentic AI sales analysis app.

## Current verified state

- Deterministic SQLite seed script for the `ventas` table.
- Faker-generated Colombian seller and branch data.
- Pytest coverage for database creation, schema, row count, and required values.
- Read-only SQL validation and execution against the local SQLite database.
- Bedrock SQL-generation prompt/client boundary with mocked test coverage.
- Query service that connects natural-language questions to generated SQL and query results.
- Chat-style Streamlit UI in `app.py` for asking questions and viewing generated SQL plus table results.
- Minimal LangGraph agent boundary before the query service.
- SQLite query execution through the `mcp-server-sqlite` MCP server using its `read_query` tool.
- Sidebar MCP diagnostics can list tables and describe `ventas`; natural-language chat remains limited to sales-analysis questions.

## Configuration

Copy `.env.example` values into your shell or local environment before running the app:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
export SALES_DB_PATH=data/sales.db
```

AWS credentials must come from your normal local AWS configuration or environment. Do not commit credentials.

## Verified commands

```bash
uv run python scripts/seed_database.py
uv run pytest
```

## Local app command

```bash
uv run streamlit run app.py
```

This command is available for local runtime checks. Use `uv run pytest` as the automated verification command; full chat-to-Bedrock-to-MCP end-to-end verification is still tracked as remaining manual work.

## SQL validation scope

SQL validation is intentionally conservative in this slice. It uses token and regex checks rather than a full SQL parser, and it only permits a narrow read-only subset:

- one SQL statement;
- `SELECT` only;
- references to the `ventas` table and its allowlisted columns only;
- no SQL comments;
- blocked write/admin keywords rejected;
- a numeric `LIMIT` clause required;
- execution through the MCP SQLite `read_query` tool after validation.

## Docker usage

Create a local environment file:

```bash
cp .env.example .env
```

Manual, not-yet-end-to-end-verified Docker runtime check:

```bash
docker compose up --build
```

Full `docker compose up --build` should be run as the manual runtime check after refreshing AWS SSO credentials.

Compose reads environment values from `.env`, runs the deterministic seed command in a one-shot `seed` service, publishes the app on `http://localhost:8501`, and mounts `./data:/app/data` so `SALES_DB_PATH=data/sales.db` points at the local generated database.
It also mounts your local AWS configuration into the container so profile-based credentials such as AWS SSO can be reused by boto3. Run `aws sso login --profile <profile-name>` on the host before starting Compose when using SSO.

SQLite query execution goes through `mcp-server-sqlite`; SQL validation still runs before the MCP tool call.

Docker and Compose files are present as packaging support, but full Docker/Compose end-to-end application verification has not been completed yet.
