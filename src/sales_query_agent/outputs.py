from dataclasses import dataclass
from io import BytesIO
from typing import Any

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


@dataclass(frozen=True)
class ChartResult:
    figure: Figure | None
    message: str | None = None


def rows_to_dataframe(rows: list[dict[str, Any]], columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns or None)


def build_chart(rows: list[dict[str, Any]], columns: list[str], chart_type: str = "bar") -> ChartResult:
    if not rows:
        return ChartResult(figure=None, message="El gráfico necesita filas para renderizarse.")

    if chart_type not in {"bar", "pie", "line", "scatter"}:
        return ChartResult(figure=None, message="El gráfico recibió un tipo no soportado.")

    if chart_type == "scatter":
        return _build_scatter_chart(rows, columns)

    if len(columns) != 2:
        return ChartResult(
            figure=None,
            message="Este tipo de gráfico necesita un resultado de dos columnas.",
        )

    first_column, second_column = columns
    dataframe = rows_to_dataframe(rows, columns)

    numeric_values = pd.to_numeric(dataframe[second_column], errors="coerce")
    if numeric_values.isna().any():
        return ChartResult(
            figure=None,
            message="Este tipo de gráfico necesita que la segunda columna sea numérica.",
        )

    dataframe[second_column] = numeric_values

    if chart_type == "pie":
        figure = px.pie(dataframe, names=first_column, values=second_column)
    elif chart_type == "line":
        figure = px.line(dataframe, x=first_column, y=second_column)
    else:
        figure = px.bar(dataframe, x=first_column, y=second_column)

    return ChartResult(figure=figure)


def _build_scatter_chart(rows: list[dict[str, Any]], columns: list[str]) -> ChartResult:
    if len(columns) == 2:
        x_column, y_column = columns
        hover_column = None
    elif len(columns) == 3:
        hover_column, x_column, y_column = columns
    else:
        return ChartResult(
            figure=None,
            message="El gráfico de dispersión necesita dos columnas numéricas o una etiqueta más dos columnas numéricas.",
        )

    dataframe = rows_to_dataframe(rows, columns)
    numeric_x = pd.to_numeric(dataframe[x_column], errors="coerce")
    numeric_y = pd.to_numeric(dataframe[y_column], errors="coerce")
    if numeric_x.isna().any() or numeric_y.isna().any():
        return ChartResult(
            figure=None,
            message="El gráfico de dispersión necesita que sus columnas X e Y sean numéricas.",
        )

    dataframe[x_column] = numeric_x
    dataframe[y_column] = numeric_y
    return ChartResult(
        figure=px.scatter(
            dataframe,
            x=x_column,
            y=y_column,
            hover_name=hover_column,
        )
    )


def build_csv_bytes(rows: list[dict[str, Any]], columns: list[str]) -> bytes:
    dataframe = rows_to_dataframe(rows, columns)
    return dataframe.to_csv(index=False).encode("utf-8")


def build_excel_bytes(rows: list[dict[str, Any]], columns: list[str]) -> bytes:
    dataframe = rows_to_dataframe(rows, columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="sales_results")

    return output.getvalue()
