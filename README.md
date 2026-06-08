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
- Streamlit chat output can render semantic Bedrock-selected table, chart, CSV, and Excel responses, including deterministic Plotly bar, pie, line, and scatter charts.
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

## Output formats

Bedrock returns a structured query plan with `output_type`, `sql`, and optional `chart_type` for chart outputs. The app uses that semantic plan instead of Streamlit keyword checks.

Supported successful SQL-backed outputs:

- `table`: show generated SQL and dataframe results.
- `chart`: show generated SQL, dataframe results, and a deterministic Plotly chart selected from the validated `chart_type`.
- `csv`: show generated SQL, dataframe results, and a CSV download button.
- `excel`: show generated SQL, dataframe results, and an Excel download button.

If a query returns no rows, the UI shows an empty-result state and skips chart/download rendering.

Supported safe chart matrix:

| `chart_type` | Intended use | Required SQL result shape |
| --- | --- | --- |
| `bar` | Category ranking or comparison | exactly 2 columns: category + numeric value |
| `pie` | Category composition or participation | exactly 2 columns: category + numeric value |
| `line` | Temporal/month/date trend | exactly 2 columns: ordered category/date + numeric value |
| `scatter` | Relationship between two metrics | 2 numeric columns, or 1 label column plus 2 numeric columns |

When Bedrock omits `chart_type` for a chart response, the app defaults to `bar` for backwards compatibility. Unsupported chart types are rejected before rendering; the app never executes arbitrary Plotly function names from the model.

SQLite query execution goes through `mcp-server-sqlite`; SQL validation still runs before the MCP tool call.
