import streamlit as st
import streamlit as st

def main():

    import html
    import re
    import streamlit.components.v1 as components

    from agents.product_manager import run_product_manager
    from utils.helpers import init_db, save_to_history, get_history, delete_history_item, clear_all_history
    from agents.developer import run_developer
    from agents.tester import run_tester
    from agents.reviewer import run_reviewer
    from agents.documentation import run_documentation

    from ui.dashboard import (
        apply_custom_css,
        render_sidebar_logo,
        render_hero,
        render_agent_cards,
        render_teammate_selector,
        render_output_panel,
        render_review_output
    )

    st.set_page_config(
        page_title="BuildWithCrew",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    init_db()
    render_sidebar_logo()

    st.set_page_config(
        page_title="BuildWithCrew",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.write("App starting...")

    query_params = st.query_params

    pages = ["Home", "AI Teammates", "Code Reviewer", "History"]
    page = query_params.get("page", "Home")

    if page not in pages:
        page = "Home"

    page = st.sidebar.radio(
        "Navigate",
        pages,
        index=pages.index(page),
        label_visibility="collapsed"
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <p style='color: #8b949e; font-size: 12px; padding: 0 16px;'>
        Powered by Groq & Llama 3
    </p>
    """, unsafe_allow_html=True)

    # ---- Home Page ----
    if page == "Home":
        render_hero()
        render_agent_cards()

    # ---- AI Teammates Page ----
    elif page == "AI Teammates":
        st.markdown("""
        <h1 style="font-size: 24px; font-weight: 700; color: #e6edf3; margin-bottom: 24px;">
            AI Teammates
        </h1>
        """, unsafe_allow_html=True)

        project_idea = st.text_input(
            "Project Idea",
            placeholder="Describe your new feature or app...",
            key="project_idea_input"
        )

        if "selected_teammate" not in st.session_state:
            st.session_state.selected_teammate = "Product Manager"

        teammate = render_teammate_selector(st.session_state.selected_teammate)
        st.session_state.selected_teammate = teammate

        generate = st.button("Generate")

        st.markdown("---")
        st.markdown('<div id="output"></div>', unsafe_allow_html=True)
        st.markdown("""
        <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
            AI Output
        </h3>
        """, unsafe_allow_html=True)

        if generate:
            if project_idea.strip() == "":
                st.warning("Please enter a project idea!")
            else:
                with st.spinner(f"{teammate} AI is thinking..."):
                    if teammate == "Product Manager":
                        result = run_product_manager(project_idea)
                    elif teammate == "Developer":
                        result = run_developer(project_idea)
                    elif teammate == "Tester":
                        result = run_tester(project_idea)
                    elif teammate == "Documentation":
                        result = run_documentation(project_idea)
                    else:
                        result = "Error: No teammate selected"
                if result:
                    st.session_state.ai_output = result
                    save_to_history(project_idea, teammate, result)
                    
                    components.html("""
                    <script>
                    setTimeout(function() {
                        const el = window.parent.document.getElementById("output");
                        if (el) {
                            el.scrollIntoView({
                                behavior: "smooth",
                                block: "start"
                            });
                        }
                    }, 500);
                    </script>
                    """, height=0)
                    

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
            label_visibility="collapsed"
        )
        submitted = st.button("Review Code")

        st.markdown("---")

        st.markdown('<div id="review-output"></div>', unsafe_allow_html=True)

        st.markdown("""
        <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
            AI Review
        </h3>
        """, unsafe_allow_html=True)

        if submitted:
            if code.strip() == "":
                st.warning("Please paste some code!")
            else:
                with st.spinner("Reviewing your code..."):
                    result = run_reviewer(code)
                st.session_state.review_output = result
                
                components.html("""
                <script>
                setTimeout(function() {
                    const el = window.parent.document.getElementById("review-output");
                    if (el) {
                        el.scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });
                    }
                }, 500);
                </script>
                """, height=0)
                

        if "review_output" in st.session_state:
            raw = st.session_state.review_output

            bugs = ""
            optimizations = ""
            best_practices = ""

            if "BUGS:" in raw:
                bugs = raw.split("BUGS:")[1].split("OPTIMIZATIONS:")[0].strip()
            if "OPTIMIZATIONS:" in raw:
                optimizations = raw.split("OPTIMIZATIONS:")[1].split("BEST PRACTICES:")[0].strip()
            if "BEST PRACTICES:" in raw:
                best_practices = raw.split("BEST PRACTICES:")[1].split("CORRECTED CODE:")[0].strip()
            if "CORRECTED CODE:" in raw:
                corrected = raw.split("CORRECTED CODE:")[1].strip()

                corrected = corrected.replace("```html", "")
                corrected = corrected.replace("```python", "")
                corrected = corrected.replace("```", "")

                corrected = html.unescape(corrected)

                corrected = re.sub(r"</?pre[^>]*>", "", corrected)
                corrected = re.sub(r"</?div[^>]*>", "", corrected)

                corrected = corrected.replace("html\n", "")
                corrected = corrected.replace("html", "", 1)

                corrected = corrected.strip()

            else:
                corrected = ""

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="background-color: #1a1e24; border: 1px solid #da3633;
                            border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #f85149; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">
                        Bugs Found
                    </p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {bugs if bugs else "No bugs found"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background-color: #1a1e0a; border: 1px solid #d29922;
                            border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #e3b341; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">
                        Optimizations
                    </p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {optimizations if optimizations else "No optimizations needed"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: #0a1a0a; border: 1px solid #238636;
                            border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #3fb950; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">
                        Best Practices
                    </p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {best_practices if best_practices else "Code follows best practices"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""<p style="color: #58a6ff; font-size: 13px; font-weight: 700;">Corrected Code</p>""", unsafe_allow_html=True)
                if corrected:
                    st.code(corrected, language="python")

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
            agent_colors = {
                "Product Manager": "#238636",
                "Developer": "#1f6feb",
                "Tester": "#8957e5",
                "Documentation": "#2aa198"
            }

            if st.button("Clear All History"):
                clear_all_history()
                st.rerun()

            for item in history:
                item_id, project_idea, teammate, output, created_at = item
                color = agent_colors.get(teammate, "#238636")

                with st.container():
                    st.markdown(f"""
                    <div style="
                        background-color: #161b22;
                        border: 1px solid #30363d;
                        border-left: 3px solid {color};
                        border-radius: 8px;
                        padding: 16px 20px;
                        margin-bottom: 8px;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 4px 0;">
                                    {project_idea}
                                </p>
                                <p style="font-size: 12px; color: #8b949e; margin: 0;">
                                    {created_at}
                                </p>
                            </div>
                            <span style="
                                background-color: {color}22;
                                color: {color};
                                padding: 4px 10px;
                                border-radius: 20px;
                                font-size: 12px;
                                font-weight: 600;
                            ">{teammate}</span>
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