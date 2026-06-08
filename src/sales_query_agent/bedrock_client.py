import json
from dataclasses import dataclass
from typing import Any, Literal, Protocol

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from sales_query_agent.config import AppConfig
from sales_query_agent.prompts import (
    OUT_OF_SCOPE_SENTINEL,
    build_sql_generation_prompt,
)


OutputType = Literal["table", "chart", "csv", "excel"]
ChartType = Literal["bar", "pie", "line", "scatter"]
SUPPORTED_OUTPUT_TYPES: set[str] = {"table", "chart", "csv", "excel"}
SUPPORTED_CHART_TYPES: set[str] = {"bar", "pie", "line", "scatter"}


@dataclass(frozen=True)
class SalesQueryPlan:
    output_type: OutputType
    sql: str
    chart_type: ChartType | None = None


class BedrockConverseClient(Protocol):
    def converse(self, **kwargs: Any) -> dict[str, Any]: ...


class OutOfScopeQuestionError(ValueError):
    pass


class UnsupportedOutputError(ValueError):
    pass


class BedrockProviderError(ValueError):
    pass


def create_bedrock_runtime_client(region_name: str) -> BedrockConverseClient:
    return boto3.client("bedrock-runtime", region_name=region_name)


def generate_sql_with_bedrock(
    question: str,
    config: AppConfig,
    bedrock_client: BedrockConverseClient,
) -> str:
    return generate_sales_query_plan_with_bedrock(
        question=question,
        config=config,
        bedrock_client=bedrock_client,
    ).sql


def generate_sales_query_plan_with_bedrock(
    question: str,
    config: AppConfig,
    bedrock_client: BedrockConverseClient,
) -> SalesQueryPlan:
    prompt = build_sql_generation_prompt(question)
    try:
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
    except NoCredentialsError as error:
        raise BedrockProviderError(
            "AWS credentials were not found. Configure your local AWS credentials before asking the agent."
        ) from error
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        raise BedrockProviderError(
            f"Bedrock request failed ({error_code}). Check AWS region, credentials, and model access."
        ) from error
    except BotoCoreError as error:
        raise BedrockProviderError(
            "AWS client error. Check your local AWS configuration and try again."
        ) from error

    text = _extract_text_response(response)
    candidate = _strip_markdown_fences(text)

    if candidate == OUT_OF_SCOPE_SENTINEL:
        raise OutOfScopeQuestionError(
            "This agent can only answer questions about sales data in the ventas table."
        )

    if not candidate:
        raise ValueError("Bedrock returned an empty response")

    return _parse_sales_query_plan(candidate)


def _extract_text_response(response: dict[str, Any]) -> str:
    content = response["output"]["message"]["content"]
    return "".join(block.get("text", "") for block in content).strip()


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()

    if stripped.startswith("```json") and stripped.endswith("```"):
        return stripped.removeprefix("```json").removesuffix("```").strip()

    if stripped.startswith("```sql") and stripped.endswith("```"):
        return stripped.removeprefix("```sql").removesuffix("```").strip()

    if stripped.startswith("```") and stripped.endswith("```"):
        return stripped.removeprefix("```").removesuffix("```").strip()

    return stripped


def _parse_sales_query_plan(candidate: str) -> SalesQueryPlan:
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise ValueError("Bedrock returned invalid JSON for the sales query plan") from error

    if not isinstance(parsed, dict):
        raise ValueError("Bedrock returned a non-object sales query plan")

    keys = set(parsed.keys())
    if not {"output_type", "sql"}.issubset(keys) or not keys.issubset(
        {"output_type", "sql", "chart_type"}
    ):
        raise ValueError("Bedrock returned a sales query plan with unexpected keys")

    output_type = parsed["output_type"]
    sql = parsed["sql"]

    if not isinstance(output_type, str) or output_type not in SUPPORTED_OUTPUT_TYPES:
        raise ValueError("Bedrock returned an unsupported output_type")

    chart_type = parsed.get("chart_type")
    if output_type == "chart":
        if chart_type is None:
            chart_type = "bar"
        if not isinstance(chart_type, str) or chart_type not in SUPPORTED_CHART_TYPES:
            raise ValueError("Bedrock returned an unsupported chart_type")
    else:
        chart_type = None

    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("Bedrock returned an empty SQL response")

    return SalesQueryPlan(output_type=output_type, sql=sql.strip(), chart_type=chart_type)
