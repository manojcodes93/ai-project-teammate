import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

LOTTIE_URLS = {
    "robot": "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json",
    "coding": "https://assets5.lottiefiles.com/packages/lf20_w51pcehl.json",
    "testing": "https://assets4.lottiefiles.com/packages/lf20_49rdyysj.json",
    "docs": "https://assets9.lottiefiles.com/packages/lf20_bn5winlb.json",
    "review": "https://assets3.lottiefiles.com/packages/lf20_qp1q7mct.json"
}

def apply_custom_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #c9d1d9 !important;
        font-size: 16px;
        padding: 8px 0;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #c9d1d9 !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #238636, #2ea043) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2ea043, #3fb950) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4) !important;
    }
    .output-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        margin-top: 20px;
        line-height: 1.8;
    }
    .agent-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        border-color: #238636;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.2);
    }
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    h2, h3 {
        color: #c9d1d9 !important;
    }
    .stSuccess {
        background-color: #1a3a2a !important;
        border: 1px solid #238636 !important;
        border-radius: 8px !important;
    }
    .stWarning {
        background-color: #2a1f00 !important;
        border: 1px solid #d29922 !important;
        border-radius: 8px !important;
    }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0e1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


def render_agent_card(title, description, lottie_url=None):
    with st.container():
        st.markdown(f"""
        <div class="agent-card">
            <h3>{title}</h3>
            <p style="color: #8b949e; margin: 0;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        if lottie_url:
            animation = load_lottie(lottie_url)
            if animation:
                st_lottie(animation, height=120, key=title)


def render_output(content):
    st.markdown(f"""
    <div class="output-card">
        {content}
    </div>
    """, unsafe_allow_html=True)