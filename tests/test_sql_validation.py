from sales_query_agent.sql_validation import validate_sales_sql


def test_accepts_simple_select_from_sales_table():
    result = validate_sales_sql("SELECT producto, cantidad FROM ventas LIMIT 10")

    assert result.is_valid
    assert result.error is None


def test_accepts_aggregate_select():
    result = validate_sales_sql(
        """
        SELECT producto, SUM(cantidad) AS total_vendido
        FROM ventas
        GROUP BY producto
        ORDER BY total_vendido DESC
        LIMIT 5
        """
    )

    assert result.is_valid


def test_accepts_select_all_from_sales_table():
    result = validate_sales_sql("SELECT * FROM ventas LIMIT 10")

    assert result.is_valid


def test_accepts_where_filter_with_string_literal():
    result = validate_sales_sql("SELECT producto FROM ventas WHERE sede = 'Medellín'")

    assert result.is_valid


def test_accepts_arithmetic_expression_over_allowed_columns():
    result = validate_sales_sql(
        "SELECT vendedor, SUM(cantidad * precio) AS total_ventas FROM ventas GROUP BY vendedor"
    )

    assert result.is_valid


def test_rejects_delete_statement():
    result = validate_sales_sql("DELETE FROM ventas")

    assert not result.is_valid
    assert "Only SELECT statements are allowed" in result.error


def test_rejects_drop_statement():
    result = validate_sales_sql("DROP TABLE ventas")

    assert not result.is_valid
    assert "Only SELECT statements are allowed" in result.error


def test_rejects_multiple_statements():
    result = validate_sales_sql("SELECT * FROM ventas; DROP TABLE ventas;")

    assert not result.is_valid
    assert "Multiple statements are not allowed" in result.error


def test_rejects_unknown_table():
    result = validate_sales_sql("SELECT * FROM usuarios")

    assert not result.is_valid
    assert "Only the ventas table is allowed" in result.error


def test_rejects_unknown_column():
    result = validate_sales_sql("SELECT email FROM ventas")

    assert not result.is_valid
    assert "Column is not allowed" in result.error


def test_rejects_pragma():
    result = validate_sales_sql("PRAGMA table_info(ventas)")

    assert not result.is_valid
    assert "Only SELECT statements are allowed" in result.error


def test_rejects_unknown_column_even_with_where_filter():
    result = validate_sales_sql("SELECT producto FROM ventas WHERE email = 'test@example.com'")

    assert not result.is_valid
    assert "Column is not allowed" in result.error
