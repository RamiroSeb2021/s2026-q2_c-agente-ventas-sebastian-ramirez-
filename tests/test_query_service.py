import os
import subprocess
import sys
from pathlib import Path

import pytest

from sales_query_agent.config import AppConfig
from sales_query_agent.query_service import answer_sales_question


class FakeBedrockClient:
    def __init__(self, text: str):
        self.text = text

    def converse(self, **kwargs):
        return {
            "output": {
                "message": {
                    "content": [
                        {"text": self.text},
                    ]
                }
            }
        }


def seed_test_database(tmp_path: Path) -> Path:
    db_path = tmp_path / "sales.db"
    env = os.environ.copy()
    env["SALES_DB_PATH"] = str(db_path)

    subprocess.run(
        [sys.executable, "scripts/seed_database.py"],
        check=True,
        env=env,
    )

    return db_path


def test_answer_sales_question_returns_generated_sql_and_rows(tmp_path):
    db_path = seed_test_database(tmp_path)
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=db_path,
    )
    bedrock_client = FakeBedrockClient(
        '{"output_type":"table","sql":"SELECT producto, cantidad FROM ventas LIMIT 2"}'
    )

    result = answer_sales_question(
        question="Muestra dos ventas",
        config=config,
        bedrock_client=bedrock_client,
    )

    assert result.generated_sql == "SELECT producto, cantidad FROM ventas LIMIT 2"
    assert result.output_type == "table"
    assert result.columns == ["producto", "cantidad"]
    assert len(result.rows) == 2


def test_answer_sales_question_propagates_output_type(tmp_path):
    db_path = seed_test_database(tmp_path)
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=db_path,
    )
    bedrock_client = FakeBedrockClient(
        '{"output_type":"chart","sql":"SELECT producto, SUM(cantidad) AS total_vendido FROM ventas GROUP BY producto LIMIT 5"}'
    )

    result = answer_sales_question(
        question="Hazme un gráfico de productos vendidos",
        config=config,
        bedrock_client=bedrock_client,
    )

    assert result.output_type == "chart"
    assert result.generated_sql == "SELECT producto, SUM(cantidad) AS total_vendido FROM ventas GROUP BY producto LIMIT 5"


def test_answer_sales_question_propagates_chart_type(tmp_path):
    db_path = seed_test_database(tmp_path)
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=db_path,
    )
    bedrock_client = FakeBedrockClient(
        '{"output_type":"chart","chart_type":"pie","sql":"SELECT producto, SUM(cantidad) AS total_vendido FROM ventas GROUP BY producto LIMIT 5"}'
    )

    result = answer_sales_question(
        question="Hazme un gráfico de participación por producto",
        config=config,
        bedrock_client=bedrock_client,
    )

    assert result.output_type == "chart"
    assert result.chart_type == "pie"


def test_answer_sales_question_rejects_unsafe_bedrock_sql_before_execution(tmp_path):
    db_path = seed_test_database(tmp_path)
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=db_path,
    )
    bedrock_client = FakeBedrockClient(
        '{"output_type":"excel","sql":"DROP TABLE ventas"}'
    )

    with pytest.raises(ValueError, match="Bedrock returned unsafe SQL"):
        answer_sales_question(
            question="Borra la tabla",
            config=config,
            bedrock_client=bedrock_client,
        )
