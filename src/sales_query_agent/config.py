import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SALES_DB_PATH = Path("data/sales.db")


@dataclass(frozen=True)
class AppConfig:
    aws_region: str
    bedrock_model_id: str
    sales_db_path: Path


def load_config() -> AppConfig:
    aws_region = _required_env("AWS_REGION")
    bedrock_model_id = _required_env("BEDROCK_MODEL_ID")
    sales_db_path = Path(os.environ.get("SALES_DB_PATH", DEFAULT_SALES_DB_PATH))

    return AppConfig(
        aws_region=aws_region,
        bedrock_model_id=bedrock_model_id,
        sales_db_path=sales_db_path,
    )


def _required_env(name: str) -> str:
    value = os.environ.get(name)

    if value is None or value.strip() == "":
        raise ValueError(f"{name} is required")

    return value
