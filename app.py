import hashlib
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sales_query_agent.config import AppConfig, load_config
from sales_query_agent.bedrock_client import (
    BedrockProviderError,
    OutOfScopeQuestionError,
    create_bedrock_runtime_client,
)
from sales_query_agent.agent_graph import answer_sales_question_with_graph
from sales_query_agent.mcp_client import (
    McpQueryError,
    describe_table_via_mcp,
    list_tables_via_mcp,
)
from sales_query_agent.outputs import (
    build_chart,
    build_csv_bytes,
    build_excel_bytes,
    rows_to_dataframe,
)


st.set_page_config(
    page_title="Agente de Ventas",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def get_config() -> AppConfig:
    return load_config()


@st.cache_resource
def get_bedrock_client(region_name: str):
    return create_bedrock_runtime_client(region_name)


st.title("Agente de Ventas")
st.caption("Hacé preguntas sobre la tabla local ventas y revisá el SQL generado.")


def render_mcp_diagnostics() -> None:
    st.sidebar.header("Diagnósticos MCP")

    try:
        config = get_config()
    except ValueError as error:
        st.sidebar.error(str(error))
        return

    if st.sidebar.button("Listar tablas"):
        try:
            _ensure_database_exists(config.sales_db_path)
            tables = list_tables_via_mcp(config.sales_db_path)
            st.sidebar.write(tables)
        except Exception as error:
            st.sidebar.error(_format_mcp_diagnostic_error(error, "listar tablas"))

    if st.sidebar.button("Describir ventas"):
        try:
            _ensure_database_exists(config.sales_db_path)
            schema = describe_table_via_mcp("ventas", config.sales_db_path)
            st.sidebar.dataframe(schema, use_container_width=True)
        except Exception as error:
            st.sidebar.error(_format_mcp_diagnostic_error(error, "describir ventas"))


def _ensure_database_exists(db_path: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError("No existe la base de datos de ventas configurada. Ejecutá el comando de seed antes de revisar diagnósticos MCP.")


def _format_mcp_diagnostic_error(error: Exception, action: str) -> str:
    if isinstance(error, FileNotFoundError):
        return str(error)

    if isinstance(error, McpQueryError):
        return f"No se pudo {action}: el conector MCP SQLite reportó un error. {error}"

    return f"No se pudo {action}: el conector MCP SQLite no está disponible o la base de datos no se pudo abrir."


def render_assistant_message(message: dict) -> None:
    kind = message.get("kind", "success")
    content = message.get("content", "")

    if kind == "success":
        st.markdown(content)
        if message.get("generated_sql"):
            st.subheader("SQL generado")
            st.code(message["generated_sql"], language="sql")
        st.subheader("Resultados")
        if message["rows"]:
            dataframe = rows_to_dataframe(message["rows"], message.get("columns", []))
            st.dataframe(dataframe, use_container_width=True)
            render_requested_output(message)
        else:
            st.info("La consulta se ejecutó correctamente, pero no devolvió filas.")
    elif kind == "info":
        st.info(content)
    else:
        st.error(content)


def render_requested_output(message: dict) -> None:
    output_type = message.get("output_type", "table")
    if output_type == "chart":
        chart = build_chart(
            message["rows"],
            message.get("columns", []),
            chart_type=message.get("chart_type") or "bar",
        )
        if chart.figure is not None:
            st.plotly_chart(
                chart.figure,
                use_container_width=True,
                key=f"plotly-chart-{message_key(message)}",
            )
        elif chart.message:
            st.info(chart.message)
    elif output_type == "csv":
        st.download_button(
            label="Descargar CSV",
            data=build_csv_bytes(message["rows"], message.get("columns", [])),
            file_name="sales-results.csv",
            mime="text/csv",
            key=f"download-csv-{message_key(message)}",
        )
    elif output_type == "excel":
        st.download_button(
            label="Descargar Excel",
            data=build_excel_bytes(message["rows"], message.get("columns", [])),
            file_name="sales-results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download-excel-{message_key(message)}",
        )


def message_key(message: dict) -> str:
    if message.get("message_id"):
        return message["message_id"]

    key_source = f"{message.get('generated_sql', '')}|{message.get('output_type', '')}"
    return hashlib.sha256(key_source.encode("utf-8")).hexdigest()[:12]


render_mcp_diagnostics()


def build_assistant_message(question: str) -> dict:
    try:
        config = get_config()
        bedrock_client = get_bedrock_client(config.aws_region)

        result = answer_sales_question_with_graph(
            question=question,
            config=config,
            bedrock_client=bedrock_client,
        )

        return {
            "role": "assistant",
            "kind": "success",
            "content": result.response_text,
            "generated_sql": result.generated_sql,
            "output_type": result.output_type,
            "chart_type": result.chart_type,
            "columns": result.columns,
            "rows": result.rows,
        }
    except OutOfScopeQuestionError as error:
        return {
            "role": "assistant",
            "kind": "info",
            "content": str(error),
        }
    except ValueError as error:
        return {
            "role": "assistant",
            "kind": "error",
            "content": str(error),
        }
    except BedrockProviderError as error:
        return {
            "role": "assistant",
            "kind": "error",
            "content": str(error),
        }
    except McpQueryError as error:
        return {
            "role": "assistant",
            "kind": "error",
            "content": f"El conector MCP SQLite no pudo completar la consulta. {error}",
        }
    except FileNotFoundError:
        return {
            "role": "assistant",
            "kind": "error",
            "content": "No existe la base de datos de ventas configurada. Ejecutá el comando de seed antes de hacer preguntas.",
        }
    except Exception:
        return {
            "role": "assistant",
            "kind": "error",
            "content": "El agente no pudo responder la pregunta.",
        }


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            render_assistant_message(message)

if prompt := st.chat_input("Hacé una pregunta sobre ventas"):
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generando SQL y consultando datos de ventas..."):
            assistant_message = build_assistant_message(prompt)
            assistant_message["message_id"] = f"assistant-{len(st.session_state.messages)}"

        render_assistant_message(assistant_message)
        st.session_state.messages.append(assistant_message)
