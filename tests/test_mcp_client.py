import os
import subprocess
import sys
from pathlib import Path

import pytest

from sales_query_agent.mcp_client import (
    McpQueryError,
    _sanitize_error_detail,
    describe_table_via_mcp,
    execute_readonly_sales_query_via_mcp,
    list_tables_via_mcp,
)


def seed_test_database(tmp_path: Path) -> Path:
    db_path = tmp_path / "sales.db"
    env = os.environ.copy()
    env["SALES_DB_PATH"] = str(db_path)

    subprocess.run(
        [sys.executable, "scripts/seed_database.py"],
        check=True,
        env=env,
    )

    return db_path


def test_execute_readonly_sales_query_via_mcp_returns_rows(tmp_path):
    db_path = seed_test_database(tmp_path)

    result = execute_readonly_sales_query_via_mcp(
        "SELECT vendedor, cantidad FROM ventas LIMIT 2",
        db_path=db_path,
    )

    assert result.columns == ["vendedor", "cantidad"]
    assert len(result.rows) == 2
    assert set(result.rows[0]) == {"vendedor", "cantidad"}


def test_execute_readonly_sales_query_via_mcp_returns_empty_result(tmp_path):
    db_path = seed_test_database(tmp_path)

    result = execute_readonly_sales_query_via_mcp(
        "SELECT vendedor FROM ventas WHERE sede = 'No existe' LIMIT 5",
        db_path=db_path,
    )

    assert result.columns == []
    assert result.rows == []


def test_execute_readonly_sales_query_via_mcp_rejects_unsafe_sql_before_mcp(tmp_path):
    db_path = tmp_path / "sales.db"

    with pytest.raises(McpQueryError, match="Unsafe SQL rejected before MCP execution"):
        execute_readonly_sales_query_via_mcp(
            "DROP TABLE ventas",
            db_path=db_path,
        )


def test_list_tables_via_mcp_returns_sales_table(tmp_path):
    db_path = seed_test_database(tmp_path)

    tables = list_tables_via_mcp(db_path)

    assert "ventas" in tables


def test_describe_table_via_mcp_returns_sales_schema(tmp_path):
    db_path = seed_test_database(tmp_path)

    schema = describe_table_via_mcp("ventas", db_path)
    column_names = {column["name"] for column in schema}

    assert {
        "id",
        "vendedor",
        "sede",
        "producto",
        "cantidad",
        "precio",
        "fecha",
    }.issubset(column_names)


def test_sanitize_error_detail_redacts_common_secret_values():
    detail = _sanitize_error_detail(
        "failure token=abc123 password=hunter2 aws_access_key_id=AKIA1234567890ABCDEF"
    )

    assert "abc123" not in detail
    assert "hunter2" not in detail
    assert "AKIA1234567890ABCDEF" not in detail
    assert "token=<redacted>" in detail
