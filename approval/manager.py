"""Approval policy helpers.

Approval state in the workflow is represented explicitly in ``AgentState`` so
that LangGraph can interrupt and resume cleanly.
"""


def approval_required_for_overwrite(existing_file: bool) -> bool:
    from utils.config import REQUIRES_OVERWRITE_APPROVAL

    return bool(existing_file and REQUIRES_OVERWRITE_APPROVAL)


def build_approval_request(action, details):
    return {"action": action, "details": details, "status": "pending"}


def apply_decision(request, approved: bool):
    request = dict(request or {})
    request["status"] = "approved" if approved else "rejected"
    request["approved"] = bool(approved)
    return request