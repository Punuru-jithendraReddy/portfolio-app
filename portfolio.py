import streamlit as st
import json
import os
import base64
from streamlit_option_menu import option_menu
from PIL import Image
import plotly.graph_objects as go

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
ADMIN_PASSWORD = "admin"

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="✨")

# --- CUSTOM CSS ---
st.markdown("""
<style>
/* GLOBAL */
.main { padding-top: 1rem; }
h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #0F172A; }

/* PROJECT CARDS */
.project-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    flex-direction: column;
    min-height: 540px;
    position: relative;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 20px -5px rgba(59, 130, 246, 0.25);
    border-color: #3B82F6;
}

.p-img-container {
    width: 100%;
    height: 200px;
    overflow: hidden;
    border-bottom: 1px solid #e2e8f0;
}

.p-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.p-content {
    padding: 20px;
    flex-grow: 1;
}

.p-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1E293B;
    margin-bottom: 10px;
}

.p-detail {
    font-size: 0.9rem;
    color: #475569;
    margin-bottom: 8px;
}

.p-cat-overlay {
    position: absolute;
    top: 15px;
    left: 15px;
    background: white;
    color: #3B82F6;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
    border: 1px solid #E2E8F0;
}

/* ✅ BUTTON INSIDE CARD */
.case-btn {
    position: absolute;
    bottom: 20px;
    right: 20px;
}

.case-btn button {
    background-color: #F0F9FF !important;
    color: #0284C7 !important;
    border: 1px solid #BAE6FD !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

.case-btn button:hover {
    background-color: #E0F2FE !important;
    border-color: #0284C7 !important;
    color: #0369A1 !important;
}
</style>
""", unsafe_allow_html=True)

# --- DATA ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None

# --- SIDEBAR ---
with st.sidebar:
    selected = option_menu(None, ["Home", "Projects"], icons=["house", "rocket"], default_index=1)

# --- PROJECTS ---
if selected == "Projects":
    projects = st.session_state.data.get('projects', [])

    if st.session_state.selected_project is not None:
        p = projects[st.session_state.selected_project]
        if st.button("← Back to Projects"):
            st.session_state.selected_project = None
            st.rerun()

        st.title(p.get('title'))
        st.image(p.get('image'), use_container_width=True)
        st.write(p.get('details'))

    else:
        st.title("Projects")
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            for j, p in enumerate(projects[i:i+2]):
                idx = i + j
                with cols[j]:
                    st.markdown(f"""
                    <div class="project-card">
                        <div class="p-cat-overlay">{p.get('category')}</div>
                        <div class="p-img-container">
                            <img src="{p.get('image')}" class="p-img">
                        </div>
                        <div class="p-content">
                            <div class="p-title">{p.get('title')}</div>
                            <div class="p-detail"><b>🚨 Problem:</b> {p.get('problem')}</div>
                            <div class="p-detail"><b>💡 Solution:</b> {p.get('solution')}</div>
                            <div class="p-detail"><b>🚀 Impact:</b> {p.get('impact')}</div>
                        </div>
                        <div class="case-btn"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("View Case Study →", key=f"btn_{idx}"):
                        st.session_state.selected_project = idx
                        st.rerun()
