import os
import subprocess
import sys
from pathlib import Path

from sales_query_agent.agent_graph import answer_sales_question_with_graph
from sales_query_agent.config import AppConfig


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


def test_answer_sales_question_with_graph_returns_result(tmp_path):
    db_path = seed_test_database(tmp_path)
    config = AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=db_path,
    )
    bedrock_client = FakeBedrockClient(
        "SELECT vendedor, SUM(cantidad) AS total_vendido FROM ventas GROUP BY vendedor LIMIT 1"
    )

    result = answer_sales_question_with_graph(
        question="quien es el vendedor que vendio más?",
        config=config,
        bedrock_client=bedrock_client,
    )

    assert result.generated_sql == (
        "SELECT vendedor, SUM(cantidad) AS total_vendido FROM ventas GROUP BY vendedor LIMIT 1"
    )
    assert result.columns == ["vendedor", "total_vendido"]
    assert len(result.rows) == 1
