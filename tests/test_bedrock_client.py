import pytest
from botocore.exceptions import ClientError

from sales_query_agent.bedrock_client import (
    BedrockProviderError,
    OutOfScopeQuestionError,
    generate_sales_query_plan_with_bedrock,
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
    client = FakeBedrockClient(
        '{"output_type":"table","sql":"SELECT producto FROM ventas LIMIT 5"}'
    )

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
    client = FakeBedrockClient(
        '{"output_type":"table","sql":"SELECT producto FROM ventas LIMIT 5"}'
    )

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
    client = FakeBedrockClient(
        '```json\n{"output_type":"table","sql":"SELECT producto FROM ventas LIMIT 5"}\n```'
    )

    sql = generate_sql_with_bedrock(
        question="Muestra ventas",
        config=config,
        bedrock_client=client,
    )

    assert sql == "SELECT producto FROM ventas LIMIT 5"


def test_generate_sql_with_bedrock_rejects_empty_model_response(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient("   ")

    with pytest.raises(ValueError, match="Bedrock returned an empty response"):
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


@pytest.mark.parametrize("output_type", ["table", "chart", "csv", "excel"])
def test_generate_sales_query_plan_with_bedrock_parses_supported_output_types(tmp_path, output_type):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient(
        f'{{"output_type":"{output_type}","sql":"SELECT producto, cantidad FROM ventas LIMIT 5"}}'
    )

    plan = generate_sales_query_plan_with_bedrock(
        question="hazme un gráfico de ventas por sede",
        config=config,
        bedrock_client=client,
    )

    assert plan.output_type == output_type
    assert plan.sql == "SELECT producto, cantidad FROM ventas LIMIT 5"


@pytest.mark.parametrize("chart_type", ["bar", "pie", "line", "scatter"])
def test_generate_sales_query_plan_with_bedrock_parses_supported_chart_types(tmp_path, chart_type):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient(
        f'{{"output_type":"chart","chart_type":"{chart_type}","sql":"SELECT producto, cantidad FROM ventas LIMIT 5"}}'
    )

    plan = generate_sales_query_plan_with_bedrock(
        question="hazme un gráfico de ventas",
        config=config,
        bedrock_client=client,
    )

    assert plan.output_type == "chart"
    assert plan.chart_type == chart_type


def test_generate_sales_query_plan_with_bedrock_defaults_chart_type_to_bar(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient(
        '{"output_type":"chart","sql":"SELECT producto, cantidad FROM ventas LIMIT 5"}'
    )

    plan = generate_sales_query_plan_with_bedrock(
        question="hazme un gráfico de ventas",
        config=config,
        bedrock_client=client,
    )

    assert plan.chart_type == "bar"


def test_generate_sales_query_plan_with_bedrock_ignores_chart_type_for_non_chart_outputs(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient(
        '{"output_type":"table","chart_type":"pie","sql":"SELECT producto, cantidad FROM ventas LIMIT 5"}'
    )

    plan = generate_sales_query_plan_with_bedrock(
        question="muestra ventas",
        config=config,
        bedrock_client=client,
    )

    assert plan.output_type == "table"
    assert plan.chart_type is None


def test_generate_sales_query_plan_with_bedrock_rejects_unsupported_chart_type(tmp_path):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient(
        '{"output_type":"chart","chart_type":"histogram","sql":"SELECT producto, cantidad FROM ventas LIMIT 5"}'
    )

    with pytest.raises(ValueError, match="unsupported chart_type"):
        generate_sales_query_plan_with_bedrock(
            question="hazme un gráfico de ventas",
            config=config,
            bedrock_client=client,
        )


@pytest.mark.parametrize(
    "model_response, expected_error",
    [
        ("not json", "invalid JSON"),
        ('["not", "object"]', "non-object"),
        ('{"output_type":"chart"}', "unexpected keys"),
        ('{"output_type":"chart","sql":"SELECT producto FROM ventas LIMIT 5","extra":true}', "unexpected keys"),
        ('{"output_type":"pdf","sql":"SELECT producto FROM ventas LIMIT 5"}', "unsupported output_type"),
        ('{"output_type":[],"sql":"SELECT producto FROM ventas LIMIT 5"}', "unsupported output_type"),
        ('{"output_type":"csv","sql":"   "}', "empty SQL response"),
        ("UNSUPPORTED_OUTPUT", "invalid JSON"),
    ],
)
def test_generate_sales_query_plan_with_bedrock_rejects_invalid_structured_output(
    tmp_path, model_response, expected_error
):
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=tmp_path / "sales.db",
    )
    client = FakeBedrockClient(model_response)

    with pytest.raises(ValueError, match=expected_error):
        generate_sales_query_plan_with_bedrock(
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
    client = FakeBedrockClient(
        '{"output_type":"table","sql":"DROP TABLE ventas"}'
    )

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
    client = FakeBedrockClient(
        '{"output_type":"table","sql":"SELECT * FROM ventas; DROP TABLE ventas;"}'
    )

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
    client = FakeBedrockClient(
        '{"output_type":"table","sql":"SELECT * FROM usuarios"}'
    )

    sql = generate_sql_with_bedrock(
        question="Muestra usuarios",
        config=config,
        bedrock_client=client,
    )

    assert sql == "SELECT * FROM usuarios"
