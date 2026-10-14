"""LangGraph nodes for BuildWithCrew."""

import os
from typing import Any, Dict

from agents.developer import run_developer
from agents.documentation import run_documentation
from agents.product_manager import run_product_manager
from agents.reviewer import run_reviewer
from agents.tester import run_tester

from tools.file_tools import write_project_file
from tools.summary_tools import generate_project_summary
from tools.test_tools import run_project_tests, summarize_test_result
from tools.workspace import create_workspace, write_files

from utils.config import MAX_DEVELOPER_ATTEMPTS, MAX_REVIEW_CYCLES
from utils.helpers import get_history, save_to_history, save_workflow_run
from observability.logging import get_logger
from utils.parsing import extract_code_files, parse_review

from approval.manager import build_approval_request

from langgraph.types import interrupt

log = get_logger("graph.nodes")


def product_manager_node(state: Dict[str, Any]) -> Dict[str, Any]:
    request = state.get("request", "")
    log.info("node_enter", extra={"event_data": {"node": "product_manager", "thread_id": state.get("thread_id")}})
    try:
        requirements = run_product_manager(request)
    except Exception as exc:  # pragma: no cover - surfaced to graph
        log.error("node_error", extra={"event_data": {"node": "product_manager", "error": str(exc)}})
        return {
            "status": "failed",
            "error": f"Product Manager failed: {exc}",
            "requirements": "",
            "events": [f"Product Manager failed: {exc}"],
        }

    new_state = {
        "requirements": requirements,
        "stage": "product_manager_complete",
        "status": "running",
        "events": ["Product Manager completed: requirements generated."],
    }
    log.info("node_exit", extra={"event_data": {"node": "product_manager"}})
    return new_state


def developer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    request = state.get("request", "")
    requirements = state.get("requirements", "")
    files = dict(state.get("files") or {})
    feedback_parts = []
    if state.get("test_failures"):
        feedback_parts.append("Test failures:\n" + "\n".join(state["test_failures"]))
    if state.get("review_output") and not state.get("review_passed", False):
        feedback_parts.append("Review feedback:\n" + str(state.get("review_output")))

    feedback = "\n\n".join(feedback_parts) if feedback_parts else None

    prompt = requirements or request
    if feedback:
        prompt = f"{prompt}\n\n{feedback}"

    log.info("node_enter", extra={"event_data": {"node": "developer", "thread_id": state.get("thread_id")}})
    try:
        response = run_developer(prompt, feedback=feedback, existing_code=files)
    except Exception as exc:
        log.error("node_error", extra={"event_data": {"node": "developer", "error": str(exc)}})
        return {
            "status": "failed",
            "error": f"Developer failed: {exc}",
            "events": [f"Developer failed: {exc}"],
        }

    generated_files = extract_code_files(response)
    if not generated_files and response.strip():
        generated_files = {"main.py": response.strip()}

    # Merge new files into the shared file set.
    merged_files = dict(files)
    for name, content in generated_files.items():
        merged_files[name] = content

    # Write files into a per-run workspace through the controlled tool layer.
    workspace = state.get("workspace_path")
    if not workspace:
        workspace = str(create_workspace("project"))
    for name, content in generated_files.items():
        write_project_file(workspace, name, content, overwrite=True)

    developer_attempts = int(state.get("developer_attempts", 0)) + 1
    review_cycles = state.get("review_cycles", 0)

    # Reset test status for the new attempt.
    new_state = {
        "files": merged_files,
        "workspace_path": workspace,
        "developer_output": response,
        "developer_attempts": developer_attempts,
        "tests_passed": False,
        "test_results": {},
        "test_failures": [],
        "review_passed": False,
        "status": "running",
        "stage": "developer_complete",
        "events": [
            f"Developer completed attempt {developer_attempts}: {', '.join(sorted(generated_files.keys())) or 'no files'}"
        ],
    }
    if "max_developer_attempts" not in state:
        new_state["max_developer_attempts"] = MAX_DEVELOPER_ATTEMPTS
    if "max_review_cycles" not in state:
        new_state["max_review_cycles"] = MAX_REVIEW_CYCLES

    log.info(
        "node_exit",
        extra={
            "event_data": {
                "node": "developer",
                "files": sorted(generated_files.keys()),
                "developer_attempts": developer_attempts,
            }
        },
    )
    return new_state


def tester_node(state: Dict[str, Any]) -> Dict[str, Any]:
    files = state.get("files") or {}
    workspace = state.get("workspace_path")
    if not workspace:
        workspace = str(create_workspace("project"))
        from tools.workspace import write_files

        write_files(workspace, files)

    # Write current files to the workspace.
    from tools.workspace import write_files

    write_files(workspace, files)

    test_strategy = ""
    try:
        main_code = "\n\n".join(f"# {name}\n{content}" for name, content in files.items())
        test_strategy = run_tester(state.get("request", ""), code=main_code)
    except Exception as exc:
        test_strategy = f"Tester strategy unavailable: {exc}"

    log.info("node_enter", extra={"event_data": {"node": "tester", "thread_id": state.get("thread_id")}})

    result = run_project_tests(
        workspace=workspace,
        command=["python", "-m", "compileall", "-q", "."],
        files=files,
    )

    tests_passed = bool(result.get("ok"))
    failures = [] if tests_passed else [summarize_test_result(result)]
    if result.get("status") == "unavailable":
        failures = [summarize_test_result(result)]

    event = (
        "Tester: tests passed."
        if tests_passed
        else f"Tester: {result.get('status', 'failed')} (sandbox may be unavailable)."
    )
    new_state = {
        "workspace_path": workspace,
        "test_strategy": test_strategy,
        "test_results": result,
        "tests_passed": tests_passed,
        "test_failures": failures,
        "stage": "tester_complete",
        "status": "running",
        "events": [event],
    }
    log.info(
        "node_exit",
        extra={
            "event_data": {
                "node": "tester",
                "status": result.get("status"),
                "passed": tests_passed,
            }
        },
    )
    return new_state


def approval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Interrupt before running generated tests when approval is required."""
    from utils.config import REQUIRES_TEST_APPROVAL

    requires = state.get("requires_test_approval", REQUIRES_TEST_APPROVAL)
    if not requires:
        return {"events": ["Approval not required; continuing."]}

    if state.get("approval_granted"):
        return {"events": ["Approval already granted."]}

    approval_request = build_approval_request(
        "run_generated_tests",
        {"workspace": state.get("workspace_path"), "files": list((state.get("files") or {}).keys())},
    )
    decision = interrupt(approval_request)
    approved = False
    if isinstance(decision, dict):
        approved = bool(decision.get("approved"))
    elif isinstance(decision, bool):
        approved = decision

    if not approved:
        return {
            "status": "cancelled",
            "pending_approval": approval_request,
            "approval_granted": False,
            "error": "Human approval was rejected; tests were not run.",
            "stage": "approval_rejected",
            "events": ["Human approval rejected; run cancelled."],
        }

    approved_request = approval_request.copy()
    approved_request = {"status": "approved", "approved": True, "details": approval_request.get("details")}
    return {
        "pending_approval": approved_request,
        "approval_granted": True,
        "status": "running",
        "stage": "approval_granted",
        "events": ["Human approval granted; continuing."],
    }


def code_reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    files = state.get("files") or {}
    code = "\n\n".join(f"# {name}\n{content}" for name, content in files.items())
    log.info("node_enter", extra={"event_data": {"node": "code_reviewer", "thread_id": state.get("thread_id")}})

    try:
        review_output = run_reviewer(code)
    except Exception as exc:
        log.error("node_error", extra={"event_data": {"node": "code_reviewer", "error": str(exc)}})
        return {
            "status": "failed",
            "error": f"Code Reviewer failed: {exc}",
            "events": [f"Code Reviewer failed: {exc}"],
        }

    sections = parse_review(review_output)
    bugs = sections.get("BUGS", "")
    review_passed = "no bugs" in bugs.lower() or "no bugs found" in review_output.lower()

    review_cycles = int(state.get("review_cycles", 0))
    if not review_passed:
        review_cycles += 1

    new_state = {
        "review_output": review_output,
        "review_cycles": review_cycles,
        "review_passed": review_passed,
        "stage": "code_reviewer_complete",
        "status": "running",
        "events": [
            "Code Reviewer passed."
            if review_passed
            else f"Code Reviewer requested changes (cycle {review_cycles})."
        ],
    }
    log.info(
        "node_exit",
        extra={"event_data": {"node": "code_reviewer", "review_passed": review_passed, "review_cycles": review_cycles}},
    )
    return new_state


def documentation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    request = state.get("request", "")
    files = state.get("files") or {}
    log.info("node_enter", extra={"event_data": {"node": "documentation", "thread_id": state.get("thread_id")}})

    try:
        documentation = run_documentation(request, files=files)
    except Exception as exc:
        log.error("node_error", extra={"event_data": {"node": "documentation", "error": str(exc)}})
        return {
            "status": "failed",
            "error": f"Documentation failed: {exc}",
            "events": [f"Documentation failed: {exc}"],
        }

    return {
        "documentation": documentation,
        "stage": "documentation_complete",
        "status": "running",
        "events": ["Documentation completed."],
    }


def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    files = state.get("files") or {}
    test_results = state.get("test_results") or {}
    thread_id = state.get("thread_id", "")

    if state.get("status") in {"failed", "cancelled"}:
        final_status = state.get("status")
    elif state.get("tests_passed") and state.get("review_passed", True):
        final_status = "success"
    elif state.get("tests_passed"):
        final_status = "success"
    else:
        final_status = "failed"

    summary = generate_project_summary(
        state.get("request", ""),
        files,
        test_results,
        state.get("review_output", ""),
        state.get("documentation", ""),
    )

    try:
        save_workflow_run(
            thread_id=thread_id,
            request=state.get("request", ""),
            status=final_status,
            file_count=len(files),
            developer_attempts=int(state.get("developer_attempts", 0)),
            summary=summary,
        )
    except Exception as exc:  # pragma: no cover - storage failures should not kill run
        log.error("finalize_storage_error", extra={"event_data": {"error": str(exc)}})

    # Preserve existing single-agent history functionality.
    try:
        if final_status == "success":
            save_to_history(
                state.get("request", "")[:120],
                "BuildWithCrew Workflow",
                summary,
            )
    except Exception:
        pass

    final_result = {
        "status": final_status,
        "request": state.get("request", ""),
        "files": files,
        "test_results": test_results,
        "review_output": state.get("review_output", ""),
        "documentation": state.get("documentation", ""),
        "developer_attempts": state.get("developer_attempts", 0),
        "review_cycles": state.get("review_cycles", 0),
        "summary": summary,
    }

    log.info(
        "workflow_finalize",
        extra={
            "event_data": {
                "thread_id": thread_id,
                "status": final_status,
                "file_count": len(files),
                "developer_attempts": state.get("developer_attempts", 0),
            }
        },
    )

    return {
        "status": final_status,
        "final_result": final_result,
        "stage": "complete",
        "events": [f"Workflow finalized with status: {final_status}."],
    }