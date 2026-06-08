import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sales_query_agent.config import AppConfig, load_config
from sales_query_agent.bedrock_client import (
    BedrockProviderError,
    OutOfScopeQuestionError,
    UnsupportedOutputError,
    create_bedrock_runtime_client,
)
from sales_query_agent.agent_graph import answer_sales_question_with_graph
from sales_query_agent.mcp_client import (
    McpQueryError,
    describe_table_via_mcp,
    list_tables_via_mcp,
)


st.set_page_config(
    page_title="Sales Query Agent",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def get_config() -> AppConfig:
    return load_config()


@st.cache_resource
def get_bedrock_client(region_name: str):
    return create_bedrock_runtime_client(region_name)


st.title("Sales Query Agent")
st.caption("Ask questions about the local ventas table and inspect the generated SQL.")


def render_mcp_diagnostics() -> None:
    st.sidebar.header("MCP diagnostics")

    try:
        config = get_config()
    except ValueError as error:
        st.sidebar.error(str(error))
        return

    if st.sidebar.button("List tables"):
        try:
            _ensure_database_exists(config.sales_db_path)
            tables = list_tables_via_mcp(config.sales_db_path)
            st.sidebar.write(tables)
        except Exception as error:
            st.sidebar.error(_format_mcp_diagnostic_error(error, "list tables"))

    if st.sidebar.button("Describe ventas"):
        try:
            _ensure_database_exists(config.sales_db_path)
            schema = describe_table_via_mcp("ventas", config.sales_db_path)
            st.sidebar.dataframe(schema, use_container_width=True)
        except Exception as error:
            st.sidebar.error(_format_mcp_diagnostic_error(error, "describe ventas"))


def _ensure_database_exists(db_path: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError("The configured sales database is missing. Run the seed command before checking MCP diagnostics.")


def _format_mcp_diagnostic_error(error: Exception, action: str) -> str:
    if isinstance(error, FileNotFoundError):
        return str(error)

    if isinstance(error, McpQueryError):
        return f"Could not {action}: the MCP SQLite connector reported an error. {error}"

    return f"Could not {action}: the MCP SQLite connector is unavailable or the database could not be opened."


def render_assistant_message(message: dict) -> None:
    kind = message.get("kind", "success")
    content = message.get("content", "")

    if kind == "success":
        st.markdown(content)
        if message.get("generated_sql"):
            st.subheader("Generated SQL")
            st.code(message["generated_sql"], language="sql")
        st.subheader("Results")
        if message["rows"]:
            st.dataframe(message["rows"], use_container_width=True)
        else:
            st.info("The query ran successfully but returned no rows.")
    elif kind == "info":
        st.info(content)
    else:
        st.error(content)


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
            "rows": result.rows,
        }
    except OutOfScopeQuestionError as error:
        return {
            "role": "assistant",
            "kind": "info",
            "content": str(error),
        }
    except UnsupportedOutputError as error:
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
    except Exception:
        return {
            "role": "assistant",
            "kind": "error",
            "content": "The agent could not answer the question.",
        }


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            render_assistant_message(message)

if prompt := st.chat_input("Ask a sales question"):
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL and querying sales data..."):
            assistant_message = build_assistant_message(prompt)

        render_assistant_message(assistant_message)
        st.session_state.messages.append(assistant_message)
