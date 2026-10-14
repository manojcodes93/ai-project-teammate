"""Conditional routing functions for BuildWithCrew."""

from utils.config import MAX_DEVELOPER_ATTEMPTS


def route_after_tests(state):
    tests_passed = bool(state.get("tests_passed"))
    developer_attempts = int(state.get("developer_attempts", 0))
    max_attempts = int(state.get("max_developer_attempts", MAX_DEVELOPER_ATTEMPTS))

    if state.get("status") == "cancelled":
        return "finalize_failure"
    if tests_passed:
        return "code_reviewer"
    if developer_attempts < max_attempts:
        return "developer"
    return "finalize_failure"


def route_after_review(state):
    max_review_cycles = int(state.get("max_review_cycles", 2))
    review_cycles = int(state.get("review_cycles", 0))

    if state.get("status") == "cancelled":
        return "finalize_failure"
    if state.get("review_passed", False):
        return "documentation"
    if review_cycles <= max_review_cycles:
        return "developer"
    return "finalize_failure"
