import html

import streamlit as st
import streamlit.components.v1 as components

from agents.product_manager import run_product_manager
from agents.developer import run_developer
from agents.tester import run_tester
from agents.reviewer import run_reviewer
from agents.documentation import run_documentation

from utils.helpers import (
    init_db,
    save_to_history,
    get_history,
    delete_history_item,
    clear_all_history,
)
from utils.agents import agent_color
from utils.parsing import extract_code, parse_review, safe_block as _safe_block
from runtime.engine import WorkflowEngine
from sandbox.executor import docker_available

from ui.dashboard import (
    apply_custom_css,
    render_sidebar_logo,
    render_hero,
    render_agent_cards,
    render_teammate_selector,
    render_output_panel,
)

# Must be the FIRST Streamlit call, at module level.
st.set_page_config(
    page_title="BuildWithCrew",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = ["Home", "AI Teammates", "Code Reviewer", "Project Workflow", "History"]


def _scroll_to(element_id):
    markup = f"""
    <script>
    setTimeout(function() {{
        const el = window.parent.document.getElementById("{element_id}");
        if (el) {{ el.scrollIntoView({{ behavior: "smooth", block: "start" }}); }}
    }}, 500);
    </script>
    """
    if hasattr(st, "iframe"):
        st.iframe(markup, height=1)
    else:
        components.html(markup, height=0)


def _render_workflow_stepper(values):
    values = values or {}
    status = values.get("status", "running")
    stage = values.get("stage", "")

    done_map = {
        "Product Manager": bool(values.get("requirements")),
        "Developer": bool(values.get("files")),
        "Tester": bool(values.get("test_results")),
        "Code Reviewer": bool(values.get("review_output")),
        "Documentation": bool(values.get("documentation")),
    }
    current_map = {
        "product_manager_complete": "Developer",
        "developer_complete": "Tester",
        "tester_complete": "Code Reviewer",
        "code_reviewer_complete": "Documentation",
        "documentation_complete": "Documentation",
        "approval_granted": "Tester",
    }
    current = None if status in {"success", "failed", "cancelled"} else current_map.get(stage, "Product Manager")

    cols = st.columns(5)
    for col, name in zip(cols, done_map):
        done = done_map[name]
        active = name == current
        color = "#238636" if done else ("#1f6feb" if active else "#30363d")
        suffix = " done" if done else (" now" if active else "")
        col.markdown(
            f"<div style='border-top:4px solid {color};padding-top:6px;text-align:center;"
            f"font-size:12px;color:{color};font-weight:600;'>{name}{suffix}</div>",
            unsafe_allow_html=True,
        )


def main():
    apply_custom_css()
    init_db()
    render_sidebar_logo()

    # ---- Navigation: keep the query string and the radio in sync ----
    qp_page = st.query_params.get("page")
    if qp_page in PAGES:
        st.session_state.page = qp_page
        del st.query_params["page"]

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    page = st.sidebar.radio(
        "Navigate",
        PAGES,
        key="page",
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <p style='color: #8b949e; font-size: 12px; padding: 0 16px;'>
        Powered by Groq
    </p>
    """, unsafe_allow_html=True)

    # ---- Home ----
    if page == "Home":
        render_hero()
        render_agent_cards()

    # ---- AI Teammates ----
    elif page == "AI Teammates":
        st.markdown("""
        <h1 style="font-size: 24px; font-weight: 700; color: #e6edf3; margin-bottom: 24px;">
            AI Teammates
        </h1>
        """, unsafe_allow_html=True)

        project_idea = st.text_input(
            "Project Idea",
            placeholder="Describe your new feature or app...",
            key="project_idea_input",
        )

        if "selected_teammate" not in st.session_state:
            st.session_state.selected_teammate = "Product Manager"

        teammate = render_teammate_selector()

        # Clear stale output when the selected teammate changes.
        if st.session_state.get("output_for_teammate") != teammate:
            st.session_state.pop("ai_output", None)
            st.session_state.output_for_teammate = teammate

        generate = st.button("Generate", type="primary")

        st.markdown("---")
        st.markdown('<div id="output"></div>', unsafe_allow_html=True)
        st.markdown("""
        <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
            AI Output
        </h3>
        """, unsafe_allow_html=True)

        if generate:
            if not project_idea.strip():
                st.warning("Please enter a project idea!")
            else:
                result = None
                with st.spinner(f"{teammate} AI is thinking..."):
                    try:
                        if teammate == "Product Manager":
                            result = run_product_manager(project_idea)
                        elif teammate == "Developer":
                            result = run_developer(project_idea)
                        elif teammate == "Tester":
                            result = run_tester(project_idea)
                        elif teammate == "Documentation":
                            result = run_documentation(project_idea)
                        else:
                            st.error(f"Unknown teammate: {teammate}")
                    except Exception as exc:
                        st.error(f"Failed to generate a response: {exc}")

                if result:
                    st.session_state.ai_output = result
                    save_to_history(project_idea, teammate, result)
                    _scroll_to("output")

        if "ai_output" in st.session_state:
            render_output_panel(st.session_state.ai_output)
        else:
            render_output_panel()

    # ---- Code Reviewer Page ----
    elif page == "Code Reviewer":
        st.markdown("""
        <h1 style="font-size: 24px; font-weight: 700; color: #e6edf3; margin-bottom: 24px;">
            Code Reviewer
        </h1>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background-color: #161b22; border: 1px solid #30363d;
                    border-radius: 8px; padding: 20px 20px 0 20px;">
            <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
                Paste Your Code
            </h3>
        </div>
        """, unsafe_allow_html=True)

        code = st.text_area(
            "code_input",
            height=300,
            placeholder="Paste your Python, JavaScript, or any code here...",
            label_visibility="collapsed",
        )
        submitted = st.button("Review Code", type="primary")

        st.markdown("---")
        st.markdown('<div id="review-output"></div>', unsafe_allow_html=True)
        st.markdown("""
        <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
            AI Review
        </h3>
        """, unsafe_allow_html=True)

        if submitted:
            if not code.strip():
                st.warning("Please paste some code!")
            else:
                result = None
                with st.spinner("Reviewing your code..."):
                    try:
                        result = run_reviewer(code)
                    except Exception as exc:
                        st.error(f"Failed to review code: {exc}")

                if result:
                    st.session_state.review_output = result
                    snippet = next(
                        (line.strip() for line in code.splitlines() if line.strip()),
                        "Code review",
                    )
                    save_to_history(snippet[:120], "Code Reviewer", result)
                    _scroll_to("review-output")

        if "review_output" in st.session_state:
            sections = parse_review(st.session_state.review_output)
            bugs = sections.get("BUGS", "")
            optimizations = sections.get("OPTIMIZATIONS", "")
            best_practices = sections.get("BEST PRACTICES", "")
            language, corrected = extract_code(sections.get("CORRECTED CODE", ""))

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="background-color: #1a1e24; border: 1px solid #da3633;
                            border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #f85149; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">Bugs Found</p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {_safe_block(bugs) or "No bugs found"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background-color: #1a1e0a; border: 1px solid #d29922;
                            border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #e3b341; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">Optimizations</p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {_safe_block(optimizations) or "No optimizations needed"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: #1a1e24; border: 1px solid #8957e5;
                            border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #a371f7; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">Best Practices</p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {_safe_block(best_practices) or "Code follows best practices"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if corrected:
                    st.markdown("""
                    <p style="color: #58a6ff; font-size: 13px; font-weight: 700;
                              margin: 0 0 8px 0;">Corrected Code</p>
                    """, unsafe_allow_html=True)
                    st.code(corrected, language=language)

    # ---- Project Workflow Page ----
    elif page == "Project Workflow":
        st.markdown("""
        <h1 style="font-size: 24px; font-weight: 700; color: #e6edf3; margin-bottom: 8px;">
            Project Workflow
        </h1>
        <p style="color: #8b949e; font-size: 14px; margin-bottom: 24px;">
            Build a project with the five-agent LangGraph workflow.
        </p>
        """, unsafe_allow_html=True)

        if not docker_available():
            st.warning(
                "Docker is not available in this environment. Generated-code "
                "tests will be reported as unavailable instead of running. "
                "Install/start Docker to execute tests for real."
            )

        if "workflow_engine" not in st.session_state:
            st.session_state.workflow_engine = WorkflowEngine()

        engine = st.session_state.workflow_engine

        request = st.text_area(
            "Project request",
            placeholder="Describe the project you want BuildWithCrew to build...",
            key="workflow_request",
            height=120,
        )

        settings_cols = st.columns(3)
        with settings_cols[0]:
            max_attempts = st.number_input(
                "Max developer attempts",
                min_value=1,
                max_value=10,
                value=int(st.session_state.get("workflow_max_attempts", 3)),
                key="workflow_max_attempts_input",
            )
            st.session_state.workflow_max_attempts = int(max_attempts)
        with settings_cols[1]:
            approval_required = st.checkbox(
                "Require test approval",
                value=bool(st.session_state.get("workflow_approval_required", False)),
                key="workflow_approval_required_input",
            )
            st.session_state.workflow_approval_required = bool(approval_required)
        with settings_cols[2]:
            st.caption("Sandbox: Docker-based, network disabled by default.")

        running = bool(st.session_state.get("workflow_running", False))
        build_clicked = st.button("Build Project", type="primary", key="build_project_btn", disabled=running)
        cancel_clicked = st.button("Cancel run", key="cancel_run_btn", disabled=not running)

        if cancel_clicked:
            st.session_state.workflow_cancel_requested = True

        if (not running) and build_clicked:
            if not request.strip():
                st.warning("Please enter a project request.")
            else:
                st.session_state.workflow_running = True
                st.session_state.workflow_cancel_requested = False
                thread_id, stream = engine.stream(
                    request.strip(),
                    requires_test_approval=bool(st.session_state.get("workflow_approval_required", False)),
                    max_developer_attempts=int(st.session_state.get("workflow_max_attempts", 3)),
                )
                st.session_state.workflow_thread_id = thread_id
                progress_box = st.empty()
                event_box = st.empty()
                result_container = st.empty()

                try:
                    for _chunk in stream:
                        if st.session_state.get("workflow_cancel_requested"):
                            engine.cancel(thread_id)
                            break

                        snapshot = engine.get_state(thread_id)
                        values = getattr(snapshot, "values", {}) or {}
                        st.session_state.workflow_values = values

                        with progress_box.container():
                            _render_workflow_stepper(values)
                            st.markdown(f"**Status:** {values.get('status', 'running')}")
                            st.markdown(f"**Stage:** {values.get('stage', '')}")
                            st.markdown(
                                f"**Developer attempts:** "
                                f"{values.get('developer_attempts', 0)} / "
                                f"{st.session_state.get('workflow_max_attempts', 3)}"
                            )
                            st.markdown(f"**Tests passed:** {values.get('tests_passed', False)}")
                            st.markdown(f"**Review passed:** {values.get('review_passed', False)}")

                        with event_box.container():
                            st.markdown("#### Live Workflow Events")
                            events = values.get("events") or []
                            if not events:
                                st.caption("Waiting for the first node to report progress...")
                            else:
                                for event_text in reversed(events[-20:]):
                                    st.caption(event_text)

                        with result_container.container():
                            files = values.get("files") or {}
                            if files:
                                st.markdown("#### Generated Files")
                                for name, content in files.items():
                                    with st.expander(name):
                                        st.code(content)
                            if values.get("test_results"):
                                st.markdown("#### Latest Test Results")
                                st.json(values.get("test_results"))
                            if getattr(snapshot, "interrupts", None):
                                st.warning("Human approval required before continuing.")
                                pending = values.get("pending_approval", {})
                                st.json(pending)
                except Exception as exc:
                    st.error(f"Workflow failed: {exc}")
                finally:
                    st.session_state.workflow_running = False

                st.rerun()

        thread_id = st.session_state.get("workflow_thread_id")
        if thread_id:
            values = st.session_state.get("workflow_values") or {}
            if not values:
                try:
                    snapshot = engine.get_state(thread_id)
                    values = getattr(snapshot, "values", {}) or {}
                except Exception:
                    values = {}

            st.markdown(f"**Thread ID:** {thread_id}")
            status = values.get("status", "running")
            if status == "cancelled":
                st.info("Run cancelled.")
            elif status == "failed":
                st.error("Run failed.")
            elif status == "success":
                st.success("Run completed successfully.")

            _render_workflow_stepper(values)

            events = values.get("events") or []
            with st.expander("Workflow events", expanded=True):
                if not events:
                    st.caption("No events recorded yet.")
                for event_text in reversed(events[-40:]):
                    st.caption(event_text)

            st.markdown("#### Progress")
            st.write(f"Developer attempts: {values.get('developer_attempts', 0)}")
            st.write(f"Tests passed: {values.get('tests_passed', False)}")
            st.write(f"Review passed: {values.get('review_passed', False)}")
            st.write(f"Stage: {values.get('stage', '')}")

            files = values.get("files") or {}
            if files:
                st.markdown("#### Generated Files")
                for name, content in files.items():
                    with st.expander(name):
                        st.code(content)

            test_results = values.get("test_results") or {}
            if test_results:
                st.markdown("#### Test Results")
                st.json(test_results)

            review_output = values.get("review_output")
            if review_output:
                st.markdown("#### Code Review")
                st.markdown(review_output)

            documentation = values.get("documentation")
            if documentation:
                st.markdown("#### Documentation")
                st.markdown(documentation)

            final_result = values.get("final_result")
            if final_result:
                st.markdown("#### Final Result")
                st.json(final_result)

            snapshot = None
            try:
                snapshot = engine.get_state(thread_id)
            except Exception:
                snapshot = None
            if snapshot is not None and getattr(snapshot, "interrupts", None):
                st.warning("Human approval required before continuing.")
                pending = values.get("pending_approval", {})
                st.json(pending)
                col1, col2 = st.columns(2)
                if col1.button("Approve", key=f"approve_{thread_id}"):
                    st.session_state.workflow_running = True
                    st.session_state.workflow_cancel_requested = False
                    stream = engine.resume_stream(thread_id, {"approved": True})
                    progress_box = st.empty()
                    event_box = st.empty()
                    try:
                        for _chunk in stream:
                            if st.session_state.get("workflow_cancel_requested"):
                                engine.cancel(thread_id)
                                break
                            snapshot2 = engine.get_state(thread_id)
                            values2 = getattr(snapshot2, "values", {}) or {}
                            st.session_state.workflow_values = values2
                            with progress_box.container():
                                _render_workflow_stepper(values2)
                                st.markdown(f"**Status:** {values2.get('status', 'running')}")
                            with event_box.container():
                                st.markdown("#### Live Workflow Events")
                                for event_text in reversed(values2.get("events", [])[-20:]):
                                    st.caption(event_text)
                    except Exception as exc:
                        st.error(f"Workflow failed: {exc}")
                    finally:
                        st.session_state.workflow_running = False
                    st.rerun()
                if col2.button("Reject", key=f"reject_{thread_id}"):
                    st.session_state.workflow_running = True
                    stream = engine.resume_stream(thread_id, {"approved": False})
                    try:
                        for _chunk in stream:
                            pass
                    except Exception as exc:
                        st.error(f"Workflow failed: {exc}")
                    finally:
                        st.session_state.workflow_running = False
                    st.rerun()

    # ---- History Page ----
    elif page == "History":
        st.markdown("""
        <h1 style="font-size: 24px; font-weight: 700; color: #e6edf3; margin-bottom: 8px;">
            Project History
        </h1>
        <p style="color: #8b949e; font-size: 14px; margin-bottom: 24px;">
            All your past AI generations in one place.
        </p>
        """, unsafe_allow_html=True)

        history = get_history()

        if not history:
            st.markdown("""
            <div style="background-color: #161b22; border: 1px solid #30363d;
                        border-radius: 8px; padding: 48px 24px; text-align: center;">
                <p style="color: #8b949e; font-size: 14px;">
                    No history yet. Start generating to see your history here!
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("Clear All History"):
                clear_all_history()
                st.rerun()

            for item in history:
                item_id, project_idea, teammate, output, created_at = item
                color = agent_color(teammate)

                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #161b22; border: 1px solid #30363d;
                                border-left: 3px solid {color}; border-radius: 8px;
                                padding: 16px 20px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 4px 0;">
                                    {html.escape(project_idea)}
                                </p>
                                <p style="font-size: 12px; color: #8b949e; margin: 0;">{html.escape(str(created_at))}</p>
                            </div>
                            <span style="background-color: {color}22; color: {color}; padding: 4px 10px;
                                         border-radius: 20px; font-size: 12px; font-weight: 600;">
                                {html.escape(teammate)}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns([8, 1])
                    with col1:
                        with st.expander("View Output"):
                            st.markdown(output)
                    with col2:
                        if st.button("Delete", key=f"del_{item_id}"):
                            delete_history_item(item_id)
                            st.rerun()


if __name__ == "__main__":
    main()
