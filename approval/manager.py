"""Approval policy helpers.

Approval state in the workflow is represented explicitly in ``AgentState`` so
that LangGraph can interrupt and resume cleanly.
"""


def build_approval_request(action, details):
    return {"action": action, "details": details, "status": "pending"}