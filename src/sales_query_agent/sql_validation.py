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
    "strftime",
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
    """Conservatively validate the first-slice sales SQL subset.

    This is token/regex validation, not a complete SQL parser. It intentionally
    accepts only a narrow read-only subset before MCP execution: one SELECT
    statement, the ventas schema allowlist, no comments, no blocked keywords,
    and a numeric LIMIT clause.
    """
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

    if _contains_sql_comment(normalized_sql):
        return SqlValidationResult(
            is_valid=False,
            error="SQL comments are not allowed",
        )

    if not _uses_only_sales_table(lowered_sql):
        return SqlValidationResult(
            is_valid=False,
            error="Only the ventas table is allowed",
        )

    if _contains_select_star(lowered_sql):
        return SqlValidationResult(
            is_valid=False,
            error="SELECT * is not allowed; list allowed ventas columns explicitly",
        )

    invalid_column = _find_invalid_column(lowered_sql)
    if invalid_column is not None:
        return SqlValidationResult(
            is_valid=False,
            error=f"Column is not allowed: {invalid_column}",
        )

    if not _has_limit_clause(lowered_sql):
        return SqlValidationResult(
            is_valid=False,
            error="A LIMIT clause is required",
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


def _contains_sql_comment(sql: str) -> bool:
    return "--" in sql or "/*" in sql or "*/" in sql


def _contains_select_star(lowered_sql: str) -> bool:
    sql_without_string_literals = _remove_string_literals(lowered_sql)
    return re.search(r"\bselect\s+(?:distinct\s+)?\*\s+\bfrom\b", sql_without_string_literals) is not None


def _uses_only_sales_table(lowered_sql: str) -> bool:
    table_matches = re.findall(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", lowered_sql)
    table_matches += re.findall(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", lowered_sql)
    table_matches += _find_comma_separated_tables(lowered_sql)

    if not table_matches:
        return False

    return all(table == "ventas" for table in table_matches)


def _find_comma_separated_tables(lowered_sql: str) -> list[str]:
    from_clauses = re.findall(
        r"\bfrom\s+(.+?)(?:\bwhere\b|\bgroup\b|\border\b|\blimit\b|$)",
        lowered_sql,
    )
    comma_tables: list[str] = []

    for from_clause in from_clauses:
        if "," not in from_clause:
            continue

        for table_ref in from_clause.split(","):
            table_match = re.match(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)\b", table_ref)
            if table_match:
                comma_tables.append(table_match.group(1))

    return comma_tables


def _has_limit_clause(lowered_sql: str) -> bool:
    sql_without_string_literals = _remove_string_literals(lowered_sql)
    return re.search(r"\blimit\s+\d+\b", sql_without_string_literals) is not None


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
        "distinct",
        "from",
        "where",
        "group",
        "by",
        "having",
        "order",
        "limit",
        "offset",
        "as",
        "desc",
        "asc",
        "nulls",
        "first",
        "last",
        "and",
        "or",
        "not",
        "between",
        "in",
        "is",
        "null",
        "true",
        "false",
        "like",
        "glob",
        "regexp",
        "match",
        "escape",
        "collate",
        "case",
        "when",
        "then",
        "else",
        "end",
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
