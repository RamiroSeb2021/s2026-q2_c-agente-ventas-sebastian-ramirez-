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


def build_sql_generation_prompt(question: str) -> str:
    return f"""\
You are helping generate SQLite SQL for a sales analysis assignment.

Use only this database schema:

{SALES_SCHEMA_DESCRIPTION}

Rules:
- If the user question is not about analyzing sales data in the ventas table,
  return exactly {OUT_OF_SCOPE_SENTINEL}.
- Otherwise return strict JSON only: a compact JSON object with these keys:
  - "output_type": one of "table", "chart", "csv", or "excel".
  - "sql": the generated SQLite SELECT query.
  - "chart_type": include only when "output_type" is "chart"; choose one of "bar", "pie", "line", or "scatter".
- Infer "output_type" semantically from the user's requested result format.
- Use "table" when the user asks a normal sales question without requesting a chart or export.
- Use "chart" for visual graph/plot requests, "csv" for CSV/download-as-CSV requests, and "excel" for Excel/XLSX spreadsheet requests.
- For chart requests, choose "bar" for category ranking or comparison such as producto, sede, or vendedor plus an aggregate.
- Choose "pie" for composition or participation by category.
- Choose "line" for temporal, monthly, or date trends using fecha or strftime.
- Choose "scatter" only when the SQL returns two numeric metrics.
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
- Return only the JSON object or exactly {OUT_OF_SCOPE_SENTINEL}.
- Example JSON response:
  {{"output_type":"chart","chart_type":"bar","sql":"SELECT producto, SUM(cantidad) AS total_vendido FROM ventas GROUP BY producto ORDER BY total_vendido DESC LIMIT 5"}}

User question:
{question}
"""
