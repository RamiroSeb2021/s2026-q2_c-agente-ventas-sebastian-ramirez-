SALES_SCHEMA_DESCRIPTION = """\
Table: ventas
Columns:
- id: sale identifier
- vendedor: seller name
- sede: branch or city
- producto: product sold
- cantidad: quantity sold
- precio: unit price
- fecha: sale date in ISO format
"""


def build_sql_generation_prompt(question: str) -> str:
    return f"""\
You are helping generate SQLite SQL for a sales analysis assignment.

Use only this database schema:

{SALES_SCHEMA_DESCRIPTION}

Rules:
- Generate exactly one SQLite SELECT query.
- Query only the ventas table.
- Use only the listed columns.
- Do not generate INSERT statements.
- Do not generate UPDATE statements.
- Do not generate DELETE statements.
- Do not generate DROP statements.
- Do not generate CREATE, ALTER, PRAGMA, ATTACH, DETACH, or VACUUM statements.
- Do not include markdown fences, comments, explanation, or extra text.
- Return only the SQL query.

User question:
{question}
"""
