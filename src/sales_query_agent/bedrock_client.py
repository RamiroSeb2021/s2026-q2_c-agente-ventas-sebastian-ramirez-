from typing import Any, Protocol

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from sales_query_agent.config import AppConfig
from sales_query_agent.prompts import (
    OUT_OF_SCOPE_SENTINEL,
    UNSUPPORTED_OUTPUT_SENTINEL,
    build_sql_generation_prompt,
)


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
    sql = _strip_markdown_fences(text)

    if sql == OUT_OF_SCOPE_SENTINEL:
        raise OutOfScopeQuestionError(
            "This agent can only answer questions about sales data in the ventas table."
        )

    if sql == UNSUPPORTED_OUTPUT_SENTINEL:
        raise UnsupportedOutputError(
            "Charts, CSV, Excel, and file exports are not supported in this slice yet. I can still answer with generated SQL and a table."
        )

    if not sql:
        raise ValueError("Bedrock returned an empty SQL response")

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
