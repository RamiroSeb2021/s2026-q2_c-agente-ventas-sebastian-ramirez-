from dataclasses import dataclass
from typing import Any

from sales_query_agent.bedrock_client import (
    BedrockConverseClient,
    generate_sql_with_bedrock,
)
from sales_query_agent.config import AppConfig
from sales_query_agent.database import execute_readonly_sales_query


@dataclass(frozen=True)
class SalesQuestionResult:
    generated_sql: str
    columns: list[str]
    rows: list[dict[str, Any]]


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
    query_result = execute_readonly_sales_query(
        generated_sql,
        db_path=config.sales_db_path,
    )

    return SalesQuestionResult(
        generated_sql=generated_sql,
        columns=query_result.columns,
        rows=query_result.rows,
    )
