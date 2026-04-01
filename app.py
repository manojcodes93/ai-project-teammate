import streamlit as st
from agents.product_manager import run_product_manager
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
render_sidebar_logo()

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "AI Teammates", "Code Reviewer"],
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

    col1, col2 = st.columns([4, 6])

    with col1:
        st.markdown("""
        <div style="background-color: #161b22; border: 1px solid #30363d; 
                    border-radius: 8px; padding: 20px;">
            <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
                Configure Your Request
            </h3>
        </div>
        """, unsafe_allow_html=True)

        project_idea = st.text_input(
            "Project Idea",
            placeholder="Describe your new feature or app...",
        )

        if "selected_teammate" not in st.session_state:
            st.session_state.selected_teammate = "Product Manager"

        teammate = render_teammate_selector(st.session_state.selected_teammate)
        st.session_state.selected_teammate = teammate

        generate = st.button("Generate")

    with col2:
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
                st.session_state.ai_output = result

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

    col1, col2 = st.columns(2)

    with col1:
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
            height=400,
            placeholder="Paste your Python, JavaScript, or any code here...",
            label_visibility="collapsed"
        )
        submitted = st.button("Review Code")

    with col2:
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

        if "review_output" in st.session_state:
            st.markdown(f"""
            <div style="background-color: #161b22; border: 1px solid #30363d;
                        border-radius: 8px; padding: 20px;">
                <div style="background-color: #1a1e24; border: 1px solid #da3633;
                            border-radius: 6px; padding: 16px; margin-bottom: 12px;">
                    <p style="color: #f85149; font-size: 13px; font-weight: 600; margin: 0 0 8px 0;">
                        Bugs Found
                    </p>
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                        {st.session_state.review_output}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #161b22; border: 1px solid #30363d;
                        border-radius: 8px; padding: 48px 24px; text-align: center; min-height: 400px;">
                <p style="color: #8b949e; font-size: 14px; margin-top: 80px;">
                    Paste your code and click "Review Code" to get started
                </p>
            </div>
            """, unsafe_allow_html=True)