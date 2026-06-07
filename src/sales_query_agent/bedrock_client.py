from typing import Any, Protocol

from sales_query_agent.config import AppConfig
from sales_query_agent.prompts import build_sql_generation_prompt
from sales_query_agent.sql_validation import validate_sales_sql


class BedrockConverseClient(Protocol):
    def converse(self, **kwargs: Any) -> dict[str, Any]: ...


def generate_sql_with_bedrock(
    question: str,
    config: AppConfig,
    bedrock_client: BedrockConverseClient,
) -> str:
    prompt = build_sql_generation_prompt(question)
    response = bedrock_client.converse(
        modelId=config.bedrock_model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "temperature": 0,
            "maxTokens": 512,
        },
    )

    text = _extract_text_response(response)
    sql = _strip_markdown_fences(text)

    if not sql:
        raise ValueError("Bedrock returned an empty SQL response")

    validation = validate_sales_sql(sql)
    if not validation.is_valid:
        raise ValueError(f"Bedrock returned unsafe SQL: {validation.error}")

    return sql


def _extract_text_response(response: dict[str, Any]) -> str:
    content = response["output"]["message"]["content"]
    return "".join(block.get("text", "") for block in content).strip()


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()

    if stripped.startswith("```sql") and stripped.endswith("```"):
        return stripped.removeprefix("```sql").removesuffix("```").strip()

    if stripped.startswith("```") and stripped.endswith("```"):
        return stripped.removeprefix("```").removesuffix("```").strip()

    return stripped
