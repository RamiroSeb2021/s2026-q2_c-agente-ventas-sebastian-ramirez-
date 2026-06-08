from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from sales_query_agent.bedrock_client import BedrockConverseClient
from sales_query_agent.config import AppConfig
from sales_query_agent.query_service import SalesQuestionResult, answer_sales_question


class SalesAgentState(TypedDict):
    question: str
    config: AppConfig
    bedrock_client: BedrockConverseClient
    result: SalesQuestionResult | None


def answer_sales_question_with_graph(
    question: str,
    config: AppConfig,
    bedrock_client: BedrockConverseClient,
) -> SalesQuestionResult:
    graph = _build_sales_agent_graph()

    final_state = graph.invoke(
        {
            "question": question,
            "config": config,
            "bedrock_client": bedrock_client,
            "result": None,
        }
    )

    result = final_state["result"]
    if result is None:
        raise RuntimeError("Sales agent graph finished without a result")

    return result


def _build_sales_agent_graph():
    workflow = StateGraph(SalesAgentState)
    workflow.add_node("answer_sales_question", _answer_sales_question_node)
    workflow.set_entry_point("answer_sales_question")
    workflow.add_edge("answer_sales_question", END)

    return workflow.compile()


def _answer_sales_question_node(state: SalesAgentState) -> dict[str, Any]:
    result = answer_sales_question(
        question=state["question"],
        config=state["config"],
        bedrock_client=state["bedrock_client"],
    )

    return {"result": result}
