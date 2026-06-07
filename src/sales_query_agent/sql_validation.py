from dataclasses import dataclass
import re


ALLOWED_COLUMNS = {
    "id",
    "vendedor",
    "sede",
    "producto",
    "cantidad",
    "precio",
    "fecha",
}

ALLOWED_FUNCTIONS = {
    "sum",
    "count",
    "avg",
    "min",
    "max",
}

BLOCKED_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "detach",
    "pragma",
    "vacuum",
    "begin",
    "commit",
    "rollback",
}


@dataclass(frozen=True)
class SqlValidationResult:
    is_valid: bool
    error: str | None = None


def validate_sales_sql(sql: str) -> SqlValidationResult:
    normalized_sql = sql.strip()
    lowered_sql = normalized_sql.lower()

    if not lowered_sql.startswith("select"):
        return SqlValidationResult(
            is_valid=False,
            error="Only SELECT statements are allowed",
        )

    if _has_multiple_statements(normalized_sql):
        return SqlValidationResult(
            is_valid=False,
            error="Multiple statements are not allowed",
        )

    if _contains_blocked_keyword(lowered_sql):
        return SqlValidationResult(
            is_valid=False,
            error="Only SELECT statements are allowed",
        )

    if not _uses_only_sales_table(lowered_sql):
        return SqlValidationResult(
            is_valid=False,
            error="Only the ventas table is allowed",
        )

    invalid_column = _find_invalid_column(lowered_sql)
    if invalid_column is not None:
        return SqlValidationResult(
            is_valid=False,
            error=f"Column is not allowed: {invalid_column}",
        )

    return SqlValidationResult(is_valid=True)


def _has_multiple_statements(sql: str) -> bool:
    statements = [
        statement.strip() for statement in sql.split(";") if statement.strip()
    ]
    return len(statements) > 1


def _contains_blocked_keyword(lowered_sql: str) -> bool:
    return any(
        re.search(rf"\b{keyword}\b", lowered_sql) for keyword in BLOCKED_KEYWORDS
    )


def _uses_only_sales_table(lowered_sql: str) -> bool:
    table_matches = re.findall(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", lowered_sql)
    table_matches += re.findall(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", lowered_sql)

    if not table_matches:
        return False

    return all(table == "ventas" for table in table_matches)


def _find_invalid_column(lowered_sql: str) -> str | None:
    sql_without_string_literals = _remove_string_literals(lowered_sql)

    aliases = set(
        re.findall(
            r"\bas\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            sql_without_string_literals,
        )
    )

    tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", sql_without_string_literals)

    ignored_tokens = {
        "select",
        "from",
        "where",
        "group",
        "by",
        "order",
        "limit",
        "as",
        "desc",
        "asc",
        "and",
        "or",
        "ventas",
    }

    for token in tokens:
        if token in ignored_tokens:
            continue

        if token in aliases:
            continue

        if token in ALLOWED_FUNCTIONS:
            continue

        if token not in ALLOWED_COLUMNS:
            return token

    return None


def _remove_string_literals(lowered_sql: str) -> str:
    return re.sub(r"'([^']|'')*'", "''", lowered_sql)
