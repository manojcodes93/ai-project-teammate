import streamlit as st
from agents.product_manager import run_product_manager
from agents.developer import run_developer
from agents.tester import run_tester
from agents.reviewer import run_reviewer
from agents.documentation import run_documentation
from ui.dashboard import apply_custom_css, render_agent_card, render_output, LOTTIE_URLS

# Page config
st.set_page_config(
    page_title="BuildWithCrew",
    page_icon="🛠️",
    layout="wide"
)

apply_custom_css()

st.sidebar.title("BuildWithCrew")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "AI Teammates", "Code Reviewer"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='color: #8b949e; font-size: 13px;'>Powered by Groq & Llama 3</p>", unsafe_allow_html=True)

# Home Page
if page == "Home":
    st.title("BuildWithCrew")
    st.markdown("<p style='color: #8b949e; font-size: 18px;'>Your AI-powered development team — built to help you ship faster.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        render_agent_card("Product Manager", "Generates features, roadmap, milestones and user stories for your project.", LOTTIE_URLS["robot"])
        render_agent_card("Tester", "Generates test cases, edge cases and bug scenarios.", LOTTIE_URLS["testing"])

    with col2:
        render_agent_card("Developer", "Generates folder structure, tech stack and starter code.", LOTTIE_URLS["coding"])
        render_agent_card("Documentation", "Generates README, installation guide and API docs.", LOTTIE_URLS["docs"])

    st.markdown("---")
    render_agent_card("Code Reviewer", "Reviews your code for bugs, optimizations and best practices.", LOTTIE_URLS["review"])

# AI Teammates Page
elif page == "AI Teammates":
    st.title("AI Teammates")
    st.markdown("<p style='color: #8b949e;'>Select a teammate and enter your project idea to get started.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        project_idea = st.text_input("Enter your project idea", placeholder="e.g. Build a Resume Analyzer")

    with col2:
        teammate = st.selectbox("Select Teammate", [
            "Product Manager",
            "Developer",
            "Tester",
            "Documentation"
        ])

    if st.button("Generate"):
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

            st.success("Done!")
            render_output(result)

# Code Reviewer Page
elif page == "Code Reviewer":
    st.title("Code Reviewer")
    st.markdown("<p style='color: #8b949e;'>Paste your code below and get instant AI feedback.</p>", unsafe_allow_html=True)
    st.markdown("---")

    code = st.text_area("Paste your code here", height=300, placeholder="Paste your Python, JavaScript, or any code here...")

    if st.button("Review Code"):
        if code.strip() == "":
            st.warning("Please paste some code!")
        else:
            with st.spinner("Reviewing your code..."):
                result = run_reviewer(code)

            st.success("Done!")
            render_output(result)