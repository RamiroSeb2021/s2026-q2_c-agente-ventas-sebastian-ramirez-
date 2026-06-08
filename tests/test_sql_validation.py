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


def test_rejects_select_star_from_sales_table():
    result = validate_sales_sql("SELECT * FROM ventas LIMIT 10")

    assert not result.is_valid
    assert "SELECT * is not allowed" in result.error


def test_accepts_where_filter_with_string_literal():
    result = validate_sales_sql("SELECT producto FROM ventas WHERE sede = 'Medellín' LIMIT 10")

    assert result.is_valid


def test_accepts_arithmetic_expression_over_allowed_columns():
    result = validate_sales_sql(
        "SELECT vendedor, SUM(cantidad * precio) AS total_ventas FROM ventas GROUP BY vendedor LIMIT 10"
    )

    assert result.is_valid


def test_accepts_month_grouping_with_sqlite_date_function():
    result = validate_sales_sql(
        """
        SELECT strftime('%m', fecha) AS mes, SUM(cantidad) AS total_vendido
        FROM ventas
        GROUP BY mes
        ORDER BY total_vendido DESC
        LIMIT 1
        """
    )

    assert result.is_valid


def test_accepts_between_date_filter():
    result = validate_sales_sql(
        """
        SELECT vendedor, SUM(cantidad) AS total_vendido
        FROM ventas
        WHERE fecha BETWEEN '2025-01-01' AND '2025-01-31'
        GROUP BY vendedor
        ORDER BY total_vendido DESC
        LIMIT 1
        """
    )

    assert result.is_valid


def test_accepts_distinct_month_query():
    result = validate_sales_sql(
        """
        SELECT DISTINCT strftime('%m', fecha) AS mes
        FROM ventas
        ORDER BY mes ASC
        LIMIT 12
        """
    )

    assert result.is_valid


def test_accepts_common_where_operators():
    result = validate_sales_sql(
        """
        SELECT producto, cantidad
        FROM ventas
        WHERE producto IN ('Camera', 'Smartphone')
          AND sede LIKE 'San%'
          AND precio IS NOT NULL
        ORDER BY cantidad DESC
        LIMIT 10 OFFSET 0
        """
    )

    assert result.is_valid


def test_accepts_case_expression():
    result = validate_sales_sql(
        """
        SELECT producto,
               CASE WHEN cantidad >= 5 THEN 'high' ELSE 'low' END AS nivel
        FROM ventas
        LIMIT 10
        """
    )

    assert result.is_valid


def test_accepts_having_clause():
    result = validate_sales_sql(
        """
        SELECT vendedor, SUM(cantidad) AS total_vendido
        FROM ventas
        GROUP BY vendedor
        HAVING total_vendido > 10
        ORDER BY total_vendido DESC
        LIMIT 5
        """
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


def test_rejects_line_comment():
    result = validate_sales_sql("SELECT * FROM ventas LIMIT 10 -- hidden comment")

    assert not result.is_valid
    assert "SQL comments are not allowed" in result.error


def test_rejects_block_comment():
    result = validate_sales_sql("SELECT * FROM ventas LIMIT 10 /* hidden comment */")

    assert not result.is_valid
    assert "SQL comments are not allowed" in result.error


def test_rejects_unknown_table():
    result = validate_sales_sql("SELECT * FROM usuarios")

    assert not result.is_valid
    assert "Only the ventas table is allowed" in result.error


def test_rejects_comma_separated_unknown_table():
    result = validate_sales_sql("SELECT producto FROM ventas, usuarios LIMIT 10")

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


def test_rejects_sales_query_without_limit():
    result = validate_sales_sql("SELECT id, vendedor, sede, producto, cantidad, precio, fecha FROM ventas")

    assert not result.is_valid
    assert "A LIMIT clause is required" in result.error


def test_rejects_fake_limit_inside_string_literal():
    result = validate_sales_sql("SELECT producto FROM ventas WHERE producto = 'limit 10'")

    assert not result.is_valid
    assert "A LIMIT clause is required" in result.error
