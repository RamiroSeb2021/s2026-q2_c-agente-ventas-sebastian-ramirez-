import os
import subprocess
import sys
from pathlib import Path

import pytest

from sales_query_agent.database import execute_readonly_sales_query


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


def test_execute_readonly_sales_query_returns_columns_and_rows(tmp_path):
    db_path = seed_test_database(tmp_path)

    result = execute_readonly_sales_query(
        "SELECT producto, cantidad FROM ventas LIMIT 3",
        db_path=db_path,
    )

    assert result.columns == ["producto", "cantidad"]
    assert len(result.rows) == 3
    assert set(result.rows[0]) == {"producto", "cantidad"}


def test_execute_readonly_sales_query_supports_aggregates(tmp_path):
    db_path = seed_test_database(tmp_path)

    result = execute_readonly_sales_query(
        """
        SELECT vendedor, SUM(cantidad * precio) AS total_ventas
        FROM ventas
        GROUP BY vendedor
        ORDER BY total_ventas DESC
        LIMIT 1
        """,
        db_path=db_path,
    )

    assert result.columns == ["vendedor", "total_ventas"]
    assert len(result.rows) == 1
    assert result.rows[0]["vendedor"]
    assert result.rows[0]["total_ventas"] > 0


def test_execute_readonly_sales_query_rejects_invalid_sql_before_execution(tmp_path):
    db_path = seed_test_database(tmp_path)

    with pytest.raises(ValueError, match="Only SELECT statements are allowed"):
        execute_readonly_sales_query("DROP TABLE ventas", db_path=db_path)


def test_execute_readonly_sales_query_rejects_unknown_columns(tmp_path):
    db_path = seed_test_database(tmp_path)

    with pytest.raises(ValueError, match="Column is not allowed"):
        execute_readonly_sales_query("SELECT email FROM ventas", db_path=db_path)
