import pytest
from botocore.exceptions import ClientError

from sales_query_agent.bedrock_client import (
    BedrockProviderError,
    OutOfScopeQuestionError,
    UnsupportedOutputError,
    generate_sql_with_bedrock,
)
from sales_query_agent.config import AppConfig


class FakeBedrockClient:
    def __init__(self, text: str):
        self.text = text
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "output": {
                "message": {
                    "content": [
                        {"text": self.text},
                    ]
                }
            }
        }


class FailingBedrockClient:
    def converse(self, **kwargs):
        raise ClientError(
            {
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "raw provider detail that should not be shown",
                }
            },
            "Converse",
        )


def test_generate_sql_with_bedrock_calls_converse_with_prompt(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("SELECT producto FROM ventas LIMIT 5")

    sql = generate_sql_with_bedrock(
        question="Top productos en Medellín",
        config=config,
        bedrock_client=client,
    )

    assert sql == "SELECT producto FROM ventas LIMIT 5"
    assert client.calls[0]["modelId"] == "anthropic.claude-3-haiku"
    assert client.calls[0]["messages"][0]["role"] == "user"
    assert "Top productos en Medellín" in client.calls[0]["messages"][0]["content"][0]["text"]


def test_generate_sql_with_bedrock_uses_deterministic_inference_config(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("SELECT * FROM ventas LIMIT 5")

    generate_sql_with_bedrock(
        question="Muestra ventas",
        config=config,
        bedrock_client=client,
    )

    assert client.calls[0]["inferenceConfig"] == {
        "temperature": 0,
        "maxTokens": 512,
    }


def test_generate_sql_with_bedrock_strips_markdown_fences(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("```sql\nSELECT * FROM ventas LIMIT 5\n```")

    sql = generate_sql_with_bedrock(
        question="Muestra ventas",
        config=config,
        bedrock_client=client,
    )

    assert sql == "SELECT * FROM ventas LIMIT 5"


def test_generate_sql_with_bedrock_rejects_empty_model_response(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("   ")

    with pytest.raises(ValueError, match="Bedrock returned an empty SQL response"):
        generate_sql_with_bedrock(
            question="Muestra ventas",
            config=config,
            bedrock_client=client,
        )


def test_generate_sql_with_bedrock_sanitizes_client_error_message(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )

    with pytest.raises(BedrockProviderError) as error:
        generate_sql_with_bedrock(
            question="Muestra ventas",
            config=config,
            bedrock_client=FailingBedrockClient(),
        )

    assert "AccessDeniedException" in str(error.value)
    assert "raw provider detail" not in str(error.value)


def test_generate_sql_with_bedrock_rejects_out_of_scope_sentinel(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("OUT_OF_SCOPE")

    with pytest.raises(OutOfScopeQuestionError, match="sales data in the ventas table"):
        generate_sql_with_bedrock(
            question="hola",
            config=config,
            bedrock_client=client,
        )


def test_generate_sql_with_bedrock_rejects_unsupported_output_sentinel(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("UNSUPPORTED_OUTPUT")

    with pytest.raises(UnsupportedOutputError, match="not supported in this slice"):
        generate_sql_with_bedrock(
            question="hazme un gráfico de ventas por sede",
            config=config,
            bedrock_client=client,
        )


def test_generate_sql_with_bedrock_returns_candidate_sql_for_orchestration_validation(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("DROP TABLE ventas")

    sql = generate_sql_with_bedrock(
        question="Borra la tabla",
        config=config,
        bedrock_client=client,
    )

    assert sql == "DROP TABLE ventas"


def test_generate_sql_with_bedrock_returns_multiple_statement_candidate(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("SELECT * FROM ventas; DROP TABLE ventas;")

    sql = generate_sql_with_bedrock(
        question="Muestra ventas",
        config=config,
        bedrock_client=client,
    )

    assert sql == "SELECT * FROM ventas; DROP TABLE ventas;"


def test_generate_sql_with_bedrock_returns_other_table_candidate(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("SELECT * FROM usuarios")

    sql = generate_sql_with_bedrock(
        question="Muestra usuarios",
        config=config,
        bedrock_client=client,
    )

    assert sql == "SELECT * FROM usuarios"
