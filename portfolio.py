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
    
    /* 0. COLUMN POSITIONING - THE PERMANENT FIX */
    /* We make the column relative so we can pin the button to its bottom-right corner */
    [data-testid="column"] {
        position: relative !important;
        display: flex;
        flex-direction: column;
    }

    /* 1. HERO METRIC CARDS */
    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #3B82F6; }

    /* 2. PROJECT CARDS */
    .project-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 0px; 
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 540px; 
        padding-bottom: 70px; /* Space for the button inside the card */
    }
    .project-card:hover { transform: translateY(-5px); border-color: #3B82F6; }

    .p-img-container { width: 100%; height: 200px; overflow: hidden; border-bottom: 1px solid #e2e8f0; flex-shrink: 0; }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    
    .p-content { padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }
    .p-title { font-size: 1.25rem; font-weight: 800; color: #1E293B; margin-bottom: 10px; }
    .p-detail { font-size: 0.90rem; color: #475569; margin-bottom: 8px; line-height: 1.4; }
    
    /* CATEGORY PILL (Top-Left inside Image) */
    .p-cat-overlay { 
        position: absolute; top: 15px; left: 15px; z-index: 10;
        background-color: white; color: #3B82F6; padding: 4px 12px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 800; text-transform: uppercase; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 1px solid #E2E8F0;
    }

    /* 6. BUTTON STYLING (Pinned to Bottom-Right inside the card) */
    [data-testid="column"] .stButton {
        position: absolute !important;
        bottom: 25px !important;
        right: 25px !important;
        z-index: 99 !important;
    }

    [data-testid="column"] .stButton button {
        background-color: #F0F9FF !important; color: #0284C7 !important;
        border: 1px solid #BAE6FD !important; border-radius: 8px !important;
        padding: 0.4rem 1.0rem !important; font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="column"] .stButton button:hover {
        background-color: #E0F2FE !important; border-color: #0284C7 !important;
    }

</style>
""", unsafe_allow_html=True)

# --- DATA MANAGER ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
        st.toast("Saved!", icon="💾")
    except Exception as e: st.error(f"Save failed: {e}")

def get_img_src(image_path):
    if not image_path: return "https://placehold.co/600x400/png?text=No+Image"
    return image_path

# --- INITIALIZE ---
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    selected = option_menu(None, ["Home", "Projects", "Experience", "Skills", "Contact"], 
                           icons=["house", "rocket", "briefcase", "cpu", "envelope"], default_index=0,
                           styles={"nav-link-selected": {"background-color": "#3B82F6"}})
    st.markdown("---")
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin"):
            if st.button("Login") and st.text_input("Pass", type="password") == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()

# --- HOME SECTION ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        mc1, mc2, mc3 = st.columns(3)
        mc1.markdown(f'<div class="metric-card"><b>{mets.get("dashboards","0")}</b><br>Dashboards</div>', unsafe_allow_html=True)
        mc2.markdown(f'<div class="metric-card"><b>{mets.get("manual_reduction","0%")}</b><br>Reduction</div>', unsafe_allow_html=True)
        mc3.markdown(f'<div class="metric-card"><b>{mets.get("efficiency","0%")}</b><br>Efficiency</div>', unsafe_allow_html=True)
    with c2: st.image(prof.get('image_url'), width=350)

# --- PROJECTS SECTION ---
elif selected == "Projects":
    if 'selected_project' not in st.session_state: st.session_state.selected_project = None
    projects = st.session_state.data.get('projects', [])

    if st.session_state.selected_project is not None:
        p = projects[st.session_state.selected_project]
        if st.button("← Back"): st.session_state.selected_project = None; st.rerun()
        st.title(p.get('title'))
        img_src = p.get('dashboard_image') or p.get('image')
        if img_src.endswith('.mp4'): st.video(img_src)
        else: st.image(img_src, use_container_width=True)
        st.write(p.get('details', 'Description coming soon.'))
    else:
        st.title("Featured Projects")
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            batch = projects[i : i+2]
            for j, p in enumerate(batch):
                actual_idx = i + j
                with cols[j]:
                    st.markdown(f"""
                    <div class="project-card">
                        <div class="p-cat-overlay">{p.get('category')}</div>
                        <div class="p-img-container"><img src="{p.get('image')}" class="p-img"></div>
                        <div class="p-content">
                            <div class="p-title">{p.get('title')}</div>
                            <div class='p-detail'><b>🚨 Problem:</b> {p.get('problem')}</div>
                            <div class='p-detail'><b>💡 Solution:</b> {p.get('solution')}</div>
                            <div class='p-detail'><b>🚀 Impact:</b> {p.get('impact')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View Case Study ➡", key=f"btn_{actual_idx}"):
                        st.session_state.selected_project = actual_idx
                        st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

# --- OTHER SECTIONS ---
elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.info(f"**{job.get('role')}** @ {job.get('company')} ({job.get('date')})")
        st.write(job.get('description'))

elif selected == "Skills":
    st.title("Skills")
    skills = st.session_state.data.get('skills', {})
    for s, v in skills.items():
        st.write(f"**{s}**")
        st.progress(v/100)

elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    st.write(f"📧 Email: {prof.get('email')}")
    st.write(f"🔗 LinkedIn: {prof.get('linkedin')}")
