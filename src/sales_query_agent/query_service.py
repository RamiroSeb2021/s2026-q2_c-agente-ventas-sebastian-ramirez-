from dataclasses import dataclass
from typing import Any

from sales_query_agent.bedrock_client import BedrockConverseClient, generate_sql_with_bedrock
from sales_query_agent.config import AppConfig
from sales_query_agent.mcp_client import execute_readonly_sales_query_via_mcp
from sales_query_agent.sql_validation import validate_sales_sql


@dataclass(frozen=True)
class SalesQuestionResult:
    generated_sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    response_text: str = "Here is the SQL I generated and the matching sales data."


def answer_sales_question(
    question: str,
    config: AppConfig,
    bedrock_client: BedrockConverseClient,
) -> SalesQuestionResult:
    generated_sql = generate_sql_with_bedrock(
        question=question,
        config=config,
        bedrock_client=bedrock_client,
    )

    validation = validate_sales_sql(generated_sql)
    if not validation.is_valid:
        raise ValueError(f"Bedrock returned unsafe SQL: {validation.error}")

    query_result = execute_readonly_sales_query_via_mcp(
        generated_sql,
        db_path=config.sales_db_path,
    )

    return SalesQuestionResult(
        generated_sql=generated_sql,
        columns=query_result.columns,
        rows=query_result.rows,
    )
