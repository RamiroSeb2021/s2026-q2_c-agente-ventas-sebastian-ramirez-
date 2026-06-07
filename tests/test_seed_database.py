import os
import sqlite3
import subprocess
import sys
from pathlib import Path


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


def test_seed_database_creates_sales_database(tmp_path):
    db_path = seed_test_database(tmp_path)

    assert db_path.exists()


def test_sales_table_has_expected_schema(tmp_path):
    db_path = seed_test_database(tmp_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(ventas)")
        columns = [row[1] for row in cursor.fetchall()]

    assert columns == [
        "id",
        "vendedor",
        "sede",
        "producto",
        "cantidad",
        "precio",
        "fecha",
    ]


def test_sales_table_has_seeded_rows(tmp_path):
    db_path = seed_test_database(tmp_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM ventas")
        row_count = cursor.fetchone()[0]

    assert row_count == 100


def test_sales_rows_have_required_values(tmp_path):
    db_path = seed_test_database(tmp_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT vendedor, sede, producto, cantidad, precio, fecha
            FROM ventas
            LIMIT 1
            """
        )
        row = cursor.fetchone()

    vendedor, sede, producto, cantidad, precio, fecha = row

    assert vendedor
    assert sede
    assert producto
    assert cantidad > 0
    assert precio > 0
    assert fecha
