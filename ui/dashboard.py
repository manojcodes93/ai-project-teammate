import streamlit as st
from streamlit_lottie import st_lottie
import requests
import base64

def get_logo_base64():
    try:
        with open("assets/logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def apply_custom_css():
    st.markdown("""
    <style>
    /* ---- Global ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
        padding-top: 0 !important;
    }

    /* ---- Hide radio circles completely ---- */
    [data-testid="stSidebar"] input[type="radio"] {
        display: none !important;
    }

    [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
        display: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        width: 100% !important;
    }

    /* ---- Radio group layout ---- */
    [data-testid="stSidebar"] .stRadio > div {
        display: flex !important;
        flex-direction: column !important;
        gap: 2px !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        display: flex !important;
        align-items: center !important;
        padding: 10px 16px !important;
        border-radius: 6px !important;
        border-left: 3px solid transparent !important;
        color: #8b949e !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: #21262d !important;
        color: #ffffff !important;
        border-left: 3px solid #238636 !important;
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
        background-color: #21262d !important;
        color: #ffffff !important;
        border-left: 3px solid #238636 !important;
    }

    /* ---- Inputs ---- */
    .stTextInput input, .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #238636 !important;
        box-shadow: 0 0 0 3px rgba(35, 134, 54, 0.15) !important;
    }

    /* ---- Buttons ---- */
    .stButton button {
        background-color: #238636 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        background-color: #2ea043 !important;
        box-shadow: 0 0 12px rgba(46, 160, 67, 0.4) !important;
    }
    
    /* ---- Selectbox cursor pointer ---- */
    .stSelectbox div[data-baseweb="select"] {
        cursor: pointer !important;
    }

    .stSelectbox div[data-baseweb="select"] * {
        cursor: pointer !important;
    }
                
    div[data-baseweb="select"] {
        cursor: pointer !important;
    }

    div[data-baseweb="select"] * {
        cursor: pointer !important;
    }

    /* ---- Hide default streamlit elements ---- */
    #MainMenu, footer { visibility: hidden; }

    /* ---- Make sidebar reopen arrow visible ---- */
    [data-testid="collapsedControl"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 0 6px 6px 0 !important;
        visibility: visible !important;
        display: flex !important;
    }

    [data-testid="collapsedControl"] svg {
        fill: #8b949e !important;
    }

    [data-testid="collapsedControl"]:hover {
        background-color: #21262d !important;
        border-color: #238636 !important;
    }

    [data-testid="collapsedControl"]:hover svg {
        fill: #ffffff !important;
    }

    .block-container { padding-top: 2.5rem !important; }
                
    /* ---- Hide press enter to apply ---- */
    .stTextInput div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* ---- Scrollbar ---- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

    </style>
    """, unsafe_allow_html=True)


def render_sidebar_logo():
    logo_base64 = get_logo_base64()
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="36" height="36" style="border-radius: 50%;"/>'
    else:
        logo_html = '<div style="background:#238636;width:24px;height:24px;border-radius:50%;"></div>'
    
    st.sidebar.markdown(f"""
    <div style="padding: 20px 16px 10px 16px; border-bottom: 1px solid #30363d; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            {logo_html}
            <span style="font-size: 16px; font-weight: 700; color: #ffffff;">BuildWithCrew</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #161b22 0%, #0e1117 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 48px 40px;
        margin-bottom: 24px;
        background-image: radial-gradient(#21262d 1px, transparent 1px);
        background-size: 24px 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
    ">
        <h1 style="font-size: 42px; font-weight: 700; color: #ffffff; margin: 0 0 12px 0; line-height: 1.2;">
            Build Faster With Your AI Crew
        </h1>
        <p style="font-size: 17px; color: #8b949e; margin: 0 0 28px 0; max-width: 560px; margin-left: auto; margin-right: auto;">
            Simulate a full software development team with AI — from planning to deployment
        </p>
        <div style="display: flex; gap: 12px; justify-content: center;">
            <a href="?page=AI+Teammates" style="
                background-color: #238636;
                color: white;
                padding: 10px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
            ">Start Building</a>
            <a href="?page=Code+Reviewer" style="
                background-color: transparent;
                color: #c9d1d9;
                padding: 10px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #30363d;
            ">Review Code</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_agent_cards():
    agents = [
        {"title": "Product Manager", "desc": "Defines requirements, features and roadmap", "color": "#238636"},
        {"title": "Developer", "desc": "Writes and reviews code and architecture", "color": "#1f6feb"},
        {"title": "Tester", "desc": "Conducts automated and manual testing", "color": "#8957e5"},
        {"title": "Code Reviewer", "desc": "Reviews code for bugs and best practices", "color": "#db6d28"},
        {"title": "Documentation", "desc": "Creates user and developer documentation", "color": "#2aa198"},
    ]

    st.markdown("""
    <h2 style="font-size: 18px; font-weight: 600; color: #e6edf3; margin: 0 0 16px 0;">
        Your AI Teammates
    </h2>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, agent in enumerate(agents):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                background-color: #161b22;
                border: 1px solid #30363d;
                border-top: 3px solid {agent['color']};
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 16px;
                transition: all 0.2s ease;
            ">
                <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0 0 6px 0;">
                    {agent['title']}
                </h3>
                <p style="font-size: 13px; color: #8b949e; margin: 0 0 16px 0; line-height: 1.5;">
                    {agent['desc']}
                </p>
            </div>
            """, unsafe_allow_html=True)


def render_teammate_selector(selected):
    agents = [
        {"key": "Product Manager", "icon": "PM", "desc": "Defines requirements and roadmap"},
        {"key": "Developer", "icon": "Dev", "desc": "Writes and reviews code"},
        {"key": "Tester", "icon": "QA", "desc": "Conducts automated and manual testing"},
        {"key": "Documentation", "icon": "Doc", "desc": "Creates user and developer docs"},
    ]

    st.markdown("""
    <p style="font-size: 13px; font-weight: 500; color: #e6edf3; margin: 0 0 8px 0;">
        Teammate Selector
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]

    for i, agent in enumerate(agents):
        is_selected = selected == agent["key"]
        border_color = "#238636" if is_selected else "#30363d"
        bg_color = "#1a2e1a" if is_selected else "#161b22"

        with cols[i]:
            st.markdown(f"""
            <div style="
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 14px;
                margin-bottom: 8px;
            ">
                <p style="font-size: 14px; font-weight: 600; color: #e6edf3; margin: 0 0 4px 0;">
                    {agent['key']}
                </p>
                <p style="font-size: 12px; color: #8b949e; margin: 0;">
                    {agent['desc']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    result = st.selectbox(
        "Select Teammate",
        ["Product Manager", "Developer", "Tester", "Documentation"],
        index=["Product Manager", "Developer", "Tester", "Documentation"].index(selected),
        label_visibility="collapsed"
    )
    return result


def render_output_panel(result=None):
    if result is None:
        st.markdown("""
        <div style="
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 48px 24px;
            text-align: center;
            height: 100%;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        ">
            <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;">⚙</div>
            <p style="color: #8b949e; font-size: 14px; margin: 0;">
                Select a teammate and enter your project idea to get started
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(result)

def render_review_output(result=None):
    if result is None:
        st.markdown("""
        <div style="
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 48px 24px;
            text-align: center;
            min-height: 400px;
        ">
            <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;">🤖</div>
            <p style="color: #8b949e; font-size: 14px;">
                Paste your code and click "Review Code" to get started
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        ">
            <div style="display: flex; justify-content: space-between; 
                        align-items: center; margin-bottom: 16px;">
                <h3 style="font-size: 15px; font-weight: 600; color: #e6edf3; margin: 0;">
                    AI Review
                </h3>
                <span style="background-color: #21262d; color: #8b949e; padding: 6px 12px;
                             border-radius: 6px; font-size: 12px; cursor: pointer;">
                    Copy All
                </span>
            </div>
            <div style="background-color: #1a1e24; border: 1px solid #da3633;
                        border-radius: 6px; padding: 16px; margin-bottom: 12px;">
                <p style="color: #f85149; font-size: 13px; font-weight: 600; margin: 0 0 8px 0;">
                    Bugs Found
                </p>
                <div style="color: #e6edf3; font-size: 13px; line-height: 1.8;">
                    {result}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)