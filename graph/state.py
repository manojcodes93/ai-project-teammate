"""Typed shared state for the BuildWithCrew LangGraph workflow."""

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed between workflow nodes.

    Fields are intentionally flat and typed so routing decisions can be made
    without parsing natural language.
    """

    request: str
    requirements: str
    files: Dict[str, str]
    current_file: str
    workspace_path: str

    test_strategy: str
    test_results: Dict[str, Any]
    tests_passed: bool
    test_failures: List[str]

    review_output: str
    review_findings: List[str]
    review_passed: bool
    review_cycles: int

    documentation: str

    developer_attempts: int
    max_developer_attempts: int
    max_review_cycles: int

    thread_id: str
    status: str  # running | success | failed | cancelled | waiting_approval
    error: str

    # Human approval
    pending_approval: Optional[Dict[str, Any]]
    approval_granted: bool
    requires_test_approval: bool

    # Observable events (merged across nodes)
    events: Annotated[List[str], operator.add]

    # Final structured result
    final_result: Dict[str, Any]
