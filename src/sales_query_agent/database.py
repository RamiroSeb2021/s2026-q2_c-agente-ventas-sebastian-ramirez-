"""Temporary local SQLite execution boundary for Slice 2.

The assignment target remains MCP-mediated SQL access. This module exists to
test the validator and result normalization against the deterministic local
database before choosing and wiring the SQLite MCP connector. Future MCP code
should preserve this app-facing contract and replace the direct sqlite3 call at
the boundary, not bypass validation.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sales_query_agent.sql_validation import validate_sales_sql


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[dict[str, Any]]


def execute_readonly_sales_query(sql: str, db_path: Path) -> QueryResult:
    validation = validate_sales_sql(sql)
    if not validation.is_valid:
        raise ValueError(validation.error)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql)
        rows = cursor.fetchall()

    columns = [description[0] for description in cursor.description or []]
    normalized_rows = [dict(row) for row in rows]

    return QueryResult(columns=columns, rows=normalized_rows)
