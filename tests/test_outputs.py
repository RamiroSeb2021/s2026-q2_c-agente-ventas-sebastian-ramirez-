from io import BytesIO

import pandas as pd

from sales_query_agent.outputs import build_chart, build_csv_bytes, build_excel_bytes, rows_to_dataframe


def test_rows_to_dataframe_preserves_column_order():
    dataframe = rows_to_dataframe(
        [{"total": 10, "producto": "A"}],
        ["producto", "total"],
    )

    assert list(dataframe.columns) == ["producto", "total"]


def test_build_chart_returns_bar_chart_for_category_and_numeric_value():
    chart = build_chart(
        [
            {"producto": "A", "total": 10},
            {"producto": "B", "total": 5},
        ],
        ["producto", "total"],
    )

    assert chart.figure is not None
    assert chart.message is None
    assert chart.figure.data[0].type == "bar"


def test_build_chart_returns_pie_chart_for_category_and_numeric_value():
    chart = build_chart(
        [
            {"producto": "A", "total": 10},
            {"producto": "B", "total": 5},
        ],
        ["producto", "total"],
        chart_type="pie",
    )

    assert chart.figure is not None
    assert chart.message is None
    assert chart.figure.data[0].type == "pie"


def test_build_chart_returns_line_chart_for_ordered_category_and_numeric_value():
    chart = build_chart(
        [
            {"month": "2025-01", "total": 10},
            {"month": "2025-02", "total": 15},
        ],
        ["month", "total"],
        chart_type="line",
    )

    assert chart.figure is not None
    assert chart.message is None
    assert chart.figure.data[0].type == "scatter"
    assert chart.figure.data[0].mode == "lines"


def test_build_chart_returns_scatter_chart_for_two_numeric_values():
    chart = build_chart(
        [
            {"quantity": 3, "revenue": 30},
            {"quantity": 7, "revenue": 84},
        ],
        ["quantity", "revenue"],
        chart_type="scatter",
    )

    assert chart.figure is not None
    assert chart.message is None
    assert chart.figure.data[0].type == "scatter"


def test_build_chart_returns_scatter_chart_for_label_and_two_numeric_values():
    chart = build_chart(
        [
            {"producto": "A", "quantity": 3, "revenue": 30},
            {"producto": "B", "quantity": 7, "revenue": 84},
        ],
        ["producto", "quantity", "revenue"],
        chart_type="scatter",
    )

    assert chart.figure is not None
    assert chart.message is None
    assert chart.figure.data[0].type == "scatter"


def test_build_chart_rejects_results_that_are_not_two_columns():
    chart = build_chart(
        [{"producto": "A", "sede": "Medellín", "total": 10}],
        ["producto", "sede", "total"],
    )

    assert chart.figure is None
    assert "dos columnas" in chart.message


def test_build_chart_rejects_non_numeric_second_column():
    chart = build_chart(
        [{"producto": "A", "sede": "Medellín"}],
        ["producto", "sede"],
    )

    assert chart.figure is None
    assert "numérica" in chart.message


def test_build_chart_rejects_scatter_with_non_numeric_first_column():
    chart = build_chart(
        [{"producto": "A", "total": 10}],
        ["producto", "total"],
        chart_type="scatter",
    )

    assert chart.figure is None
    assert "columnas X e Y" in chart.message


def test_build_chart_rejects_unsupported_chart_type():
    chart = build_chart(
        [{"producto": "A", "total": 10}],
        ["producto", "total"],
        chart_type="histogram",
    )

    assert chart.figure is None
    assert "tipo no soportado" in chart.message


def test_build_csv_bytes_exports_rows():
    content = build_csv_bytes(
        [{"producto": "A", "total": 10}],
        ["producto", "total"],
    ).decode("utf-8")

    assert content == "producto,total\nA,10\n"


def test_build_excel_bytes_exports_rows():
    content = build_excel_bytes(
        [{"producto": "A", "total": 10}],
        ["producto", "total"],
    )
    dataframe = pd.read_excel(BytesIO(content))

    assert dataframe.to_dict("records") == [{"producto": "A", "total": 10}]
