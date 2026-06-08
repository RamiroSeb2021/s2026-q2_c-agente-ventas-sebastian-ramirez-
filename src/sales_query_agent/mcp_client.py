import ast
import asyncio
from pathlib import Path
import re
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from sales_query_agent.database import QueryResult
from sales_query_agent.sql_validation import validate_sales_sql


class McpQueryError(ValueError):
    pass


def execute_readonly_sales_query_via_mcp(sql: str, db_path: Path) -> QueryResult:
    validation = validate_sales_sql(sql)
    if not validation.is_valid:
        raise McpQueryError(f"Unsafe SQL rejected before MCP execution: {validation.error}")

    return asyncio.run(_execute_readonly_sales_query_via_mcp(sql, db_path))


def list_tables_via_mcp(db_path: Path) -> list[str]:
    return asyncio.run(_list_tables_via_mcp(db_path))


def describe_table_via_mcp(table_name: str, db_path: Path) -> list[dict[str, Any]]:
    return asyncio.run(_describe_table_via_mcp(table_name, db_path))


async def _execute_readonly_sales_query_via_mcp(sql: str, db_path: Path) -> QueryResult:
    result = await _call_sqlite_mcp_tool(
        tool_name="read_query",
        arguments={"query": sql},
        db_path=db_path,
    )

    rows = _extract_rows(result.content)
    columns = list(rows[0].keys()) if rows else []

    return QueryResult(columns=columns, rows=rows)


async def _list_tables_via_mcp(db_path: Path) -> list[str]:
    result = await _call_sqlite_mcp_tool(
        tool_name="list_tables",
        arguments={},
        db_path=db_path,
    )

    return _extract_list(result.content)


async def _describe_table_via_mcp(
    table_name: str,
    db_path: Path,
) -> list[dict[str, Any]]:
    result = await _call_sqlite_mcp_tool(
        tool_name="describe_table",
        arguments={"table_name": table_name},
        db_path=db_path,
    )

    return _extract_rows(result.content)


async def _call_sqlite_mcp_tool(tool_name: str, arguments: dict[str, Any], db_path: Path):
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--frozen",
            "--no-dev",
            "mcp-server-sqlite",
            "--db-path",
            str(db_path),
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)

    if result.isError:
        detail = _extract_safe_error_detail(result.content)
        message = f"MCP SQLite tool failed: {tool_name}"
        if detail:
            message = f"{message}: {detail}"
        raise McpQueryError(message)

    return result


def _extract_rows(content: list[Any]) -> list[dict[str, Any]]:
    if not content:
        return []

    text = getattr(content[0], "text", "")
    if not text:
        return []

    parsed = ast.literal_eval(text)
    if not isinstance(parsed, list):
        raise McpQueryError("MCP SQLite returned an unexpected result format")

    for row in parsed:
        if not isinstance(row, dict):
            raise McpQueryError("MCP SQLite returned a non-object row")

    return parsed


def _extract_list(content: list[Any]) -> list[str]:
    if not content:
        return []

    text = getattr(content[0], "text", "")
    if not text:
        return []

    parsed = ast.literal_eval(text)
    if not isinstance(parsed, list):
        raise McpQueryError("MCP SQLite returned an unexpected list format")

    normalized_items = []
    for item in parsed:
        if isinstance(item, dict) and "name" in item:
            normalized_items.append(str(item["name"]))
        else:
            normalized_items.append(str(item))

    return normalized_items


def _extract_safe_error_detail(content: list[Any]) -> str:
    if not content:
        return ""

    details = []
    for block in content:
        text = getattr(block, "text", "")
        if text:
            details.append(str(text))

    return _sanitize_error_detail(" ".join(details))


def _sanitize_error_detail(detail: str) -> str:
    sanitized = " ".join(detail.split())
    sanitized = re.sub(
        r"(?i)(aws_access_key_id|aws_secret_access_key|aws_session_token|password|token)\s*[=:]\s*\S+",
        r"\1=<redacted>",
        sanitized,
    )
    sanitized = re.sub(r"AKIA[0-9A-Z]{16}", "<redacted-access-key>", sanitized)
    return sanitized[:240]
