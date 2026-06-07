from pathlib import Path

import pytest

from sales_query_agent.config import AppConfig, load_config


def test_load_config_reads_environment(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku")
    monkeypatch.setenv("SALES_DB_PATH", "data/sales.db")

    config = load_config()

    assert config == AppConfig(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-3-haiku",
        sales_db_path=Path("data/sales.db"),
    )


def test_load_config_uses_default_sales_db_path(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku")
    monkeypatch.delenv("SALES_DB_PATH", raising=False)

    config = load_config()

    assert config.sales_db_path == Path("data/sales.db")


def test_load_config_requires_aws_region(monkeypatch):
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku")

    with pytest.raises(ValueError, match="AWS_REGION is required"):
        load_config()


def test_load_config_requires_bedrock_model_id(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)

    with pytest.raises(ValueError, match="BEDROCK_MODEL_ID is required"):
        load_config()
