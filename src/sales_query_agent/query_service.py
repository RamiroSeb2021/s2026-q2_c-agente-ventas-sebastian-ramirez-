from dataclasses import dataclass
from typing import Any

from sales_query_agent.bedrock_client import (
    BedrockConverseClient,
    ChartType,
    OutputType,
    generate_sales_query_plan_with_bedrock,
)
from sales_query_agent.config import AppConfig
from sales_query_agent.mcp_client import execute_readonly_sales_query_via_mcp
from sales_query_agent.sql_validation import validate_sales_sql


@dataclass(frozen=True)
class SalesQuestionResult:
    generated_sql: str
    output_type: OutputType
    chart_type: ChartType | None
    columns: list[str]
    rows: list[dict[str, Any]]
    response_text: str = "Este es el SQL generado y los datos de ventas encontrados."


def answer_sales_question(
    question: str,
    config: AppConfig,
    bedrock_client: BedrockConverseClient,
) -> SalesQuestionResult:
    query_plan = generate_sales_query_plan_with_bedrock(
        question=question,
        config=config,
        bedrock_client=bedrock_client,
    )

    validation = validate_sales_sql(query_plan.sql)
    if not validation.is_valid:
        raise ValueError(f"Bedrock returned unsafe SQL: {validation.error}")

    query_result = execute_readonly_sales_query_via_mcp(
        query_plan.sql,
        db_path=config.sales_db_path,
    )

    return SalesQuestionResult(
        generated_sql=query_plan.sql,
        output_type=query_plan.output_type,
        chart_type=query_plan.chart_type,
        columns=query_result.columns,
        rows=query_result.rows,
    )
