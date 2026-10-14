"""LangGraph construction and execution helpers for BuildWithCrew."""

from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    approval_node,
    code_reviewer_node,
    developer_node,
    documentation_node,
    finalize_node,
    product_manager_node,
    tester_node,
)
from graph.routing import route_after_review, route_after_tests
from graph.state import AgentState


def route_after_approval(state):
    if state.get("status") == "cancelled":
        return "finalize_failure"
    return "tester"


def build_workflow():
    """Build the (uncompiled) BuildWithCrew StateGraph."""
    builder = StateGraph(AgentState)

    builder.add_node("product_manager", product_manager_node)
    builder.add_node("developer", developer_node)
    builder.add_node("approval", approval_node)
    builder.add_node("tester", tester_node)
    builder.add_node("code_reviewer", code_reviewer_node)
    builder.add_node("documentation", documentation_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "product_manager")
    builder.add_edge("product_manager", "developer")
    builder.add_edge("developer", "approval")
    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {"tester": "tester", "finalize_failure": "finalize"},
    )
    builder.add_conditional_edges(
        "tester",
        route_after_tests,
        {
            "developer": "developer",
            "code_reviewer": "code_reviewer",
            "finalize_failure": "finalize",
        },
    )
    builder.add_conditional_edges(
        "code_reviewer",
        route_after_review,
        {
            "developer": "developer",
            "documentation": "documentation",
            "finalize_failure": "finalize",
        },
    )
    builder.add_edge("documentation", "finalize")
    builder.add_edge("finalize", END)

    return builder


def compile_workflow(checkpointer=None):
    builder = build_workflow()
    return builder.compile(checkpointer=checkpointer)
