import streamlit as st
from agents.product_manager import run_product_manager
from agents.developer import run_developer
from agents.tester import run_tester
from agents.reviewer import run_reviewer
from agents.documentation import run_documentation

st.set_page_config(
    page_title = "AI Project Teammate",
    page_icon="🤖",
    layout = "wide"
)

st.sidebar.title("AI Project Teammate")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "AI Teammates", "Code Reviewer"]
)

if page == "Home":
    st.title("Welcome to AI Project Teammate")
    st.markdown("""
    ### Your AI-powered development team!
    - **Product Manager** — Features, roadmap, user stories
    - **Developer** — Folder structure, tech stack, starter code
    - **Tester** — Test cases, edge cases, bug scenarios
    - **Reviewer** — Code review, optimization suggestions
    - **Documentation** — README, installation guide
    """)


elif page == "AI Teammates":
    st.title("AI Teammates")

    project_idea = st.text_input("Enter your project idea", placeholder="e.g. Build a Resume Analyzer")

    teammate = st.selectbox("Select AI Teammate", [
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
            st.markdown(result)

elif page == "Code Reviewer":
    st.title("Code Reviewer")

    code = st.text_area("Paste your code here", height=300)

    if st.button("Review Code"):
        if code.strip() == "":
            st.warning("Please paste some code!")
        else:
            with st.spinner("Reviewing your code..."):
                result = run_reviewer(code)
            
            st.success("Done!")
            st.markdown(result)