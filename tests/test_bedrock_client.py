import pytest

from sales_query_agent.bedrock_client import generate_sql_with_bedrock
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


def test_generate_sql_with_bedrock_rejects_unsafe_model_sql(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("DROP TABLE ventas")

    with pytest.raises(ValueError, match="Bedrock returned unsafe SQL"):
        generate_sql_with_bedrock(
            question="Borra la tabla",
            config=config,
            bedrock_client=client,
        )


def test_generate_sql_with_bedrock_rejects_multiple_statement_model_sql(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("SELECT * FROM ventas; DROP TABLE ventas;")

    with pytest.raises(ValueError, match="Multiple statements are not allowed"):
        generate_sql_with_bedrock(
            question="Muestra ventas",
            config=config,
            bedrock_client=client,
        )


def test_generate_sql_with_bedrock_rejects_other_tables(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("SELECT * FROM usuarios")

    with pytest.raises(ValueError, match="Only the ventas table is allowed"):
        generate_sql_with_bedrock(
            question="Muestra usuarios",
            config=config,
            bedrock_client=client,
        )
