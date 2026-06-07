from sales_query_agent.prompts import build_sql_generation_prompt


def test_build_sql_generation_prompt_includes_user_question():
    prompt = build_sql_generation_prompt("Top 5 productos más vendidos en Medellín")

    assert "Top 5 productos más vendidos en Medellín" in prompt


def test_build_sql_generation_prompt_includes_sales_schema():
    prompt = build_sql_generation_prompt("Pregunta de prueba")

    expected_columns = [
        "id",
        "vendedor",
        "sede",
        "producto",
        "cantidad",
        "precio",
        "fecha",
    ]

    assert "ventas" in prompt
    for column in expected_columns:
        assert column in prompt


def test_build_sql_generation_prompt_requires_select_only():
    prompt = build_sql_generation_prompt("Pregunta de prueba")

    assert "SELECT" in prompt
    assert "Do not generate INSERT" in prompt
    assert "Do not generate UPDATE" in prompt
    assert "Do not generate DELETE" in prompt
    assert "Do not generate DROP" in prompt


def test_build_sql_generation_prompt_requires_sql_only_output():
    prompt = build_sql_generation_prompt("Pregunta de prueba")

    assert "Return only the SQL query" in prompt
    assert "Do not include markdown" in prompt
