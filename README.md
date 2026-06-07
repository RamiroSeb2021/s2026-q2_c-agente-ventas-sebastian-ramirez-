# Sales Query Agent

Practical assignment scaffold for an Agentic AI sales analysis app.

Current verified slice:

- Deterministic SQLite seed script for the `ventas` table.
- Faker-generated Colombian seller and branch data.
- Pytest coverage for database creation, schema, row count, and required values.

## Verified commands

```bash
uv run python scripts/seed_database.py
uv run pytest
```
