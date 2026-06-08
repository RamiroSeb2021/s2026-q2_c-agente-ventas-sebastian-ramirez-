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

OUT_OF_SCOPE_SENTINEL = "OUT_OF_SCOPE"
UNSUPPORTED_OUTPUT_SENTINEL = "UNSUPPORTED_OUTPUT"


def build_sql_generation_prompt(question: str) -> str:
    return f"""\
You are helping generate SQLite SQL for a sales analysis assignment.

Use only this database schema:

{SALES_SCHEMA_DESCRIPTION}

Rules:
- If the user question is not about analyzing sales data in the ventas table,
  return exactly {OUT_OF_SCOPE_SENTINEL}.
- If the user asks for a chart, CSV, Excel, file export, or download,
  return exactly {UNSUPPORTED_OUTPUT_SENTINEL} because this slice only supports SQL and table output.
- Generate exactly one SQLite SELECT query.
- Do not use SELECT *; list the needed allowed columns explicitly.
- Always include a LIMIT clause to avoid returning the full table.
- If the user asks for all rows, every row, or no limit, still include a safe LIMIT.
- The sample sales dates are in 2025.
- If the user mentions a month without a year, do not invent a year. Filter by month with strftime('%m', fecha), for example January/enero uses strftime('%m', fecha) = '01'.
- Query only the ventas table.
- Use only the listed columns.
- Do not generate INSERT statements.
- Do not generate UPDATE statements.
- Do not generate DELETE statements.
- Do not generate DROP statements.
- Do not generate CREATE, ALTER, PRAGMA, ATTACH, DETACH, or VACUUM statements.
- Do not include markdown fences, comments, explanation, or extra text.
- Return only the SQL query, exactly {OUT_OF_SCOPE_SENTINEL}, or exactly {UNSUPPORTED_OUTPUT_SENTINEL}.

User question:
{question}
"""
