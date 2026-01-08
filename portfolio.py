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
    /* GLOBAL FONTS */
    .main { padding-top: 1rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #0F172A; }
    
    /* 0. COLUMN SETUP */
    /* This allows absolute positioning of the button inside the column */
    [data-testid="column"] {
        position: relative !important;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* 1. PROJECT CARD */
    .project-card {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        
        display: flex;
        flex-direction: column;
        height: 100%;
        
        /* Space for the bottom button */
        padding-bottom: 80px; 
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .project-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.1);
        border-color: #3B82F6;
    }

    /* CARD IMAGES */
    .p-img-container { 
        width: 100%; 
        height: 180px; 
        overflow: hidden; 
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #f1f5f9;
    }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* TEXT STYLES */
    .p-title { 
        font-size: 1.2rem; 
        font-weight: 700; 
        color: #1E293B; 
        margin-bottom: 8px; 
        line-height: 1.3;
    }
    
    .p-cat {
        font-size: 0.75rem;
        font-weight: 700;
        color: #3B82F6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }

    .p-detail { 
        font-size: 0.85rem; 
        color: #475569; 
        margin-bottom: 6px; 
        line-height: 1.5; 
    }
    .p-label { font-weight: 600; color: #334155; }

    /* 2. BUTTON POSITIONING & STYLING (Full Width Fix) */
    
    /* Target the container of the button inside columns */
    div[data-testid="column"] .stButton {
        position: absolute !important;
        bottom: 20px !important;
        left: 20px !important;
        /* Calculate width: 100% of column minus 20px left padding and 20px right padding */
        width: calc(100% - 40px) !important; 
        z-index: 10 !important;
    }

    /* Style the actual button (Rectangle) */
    div[data-testid="column"] .stButton button {
        background: #EFF6FF !important; /* Light blue bg */
        color: #2563EB !important;      /* Blue text */
        border: 1px solid #DBEAFE !important;
        border-radius: 8px !important;
        width: 100% !important;         /* Force button to fill the container calculated above */
        height: auto !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="column"] .stButton button:hover {
        background: #2563EB !important;
        color: white !important;
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2) !important;
    }
    
    div[data-testid="column"] .stButton button p {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="column"] .stButton button:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* OTHER CARDS */
    .metric-card, .timeline-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    if image_path.startswith("http"): return image_path
    return image_path

def render_image(image_path, width=None):
    src = get_img_src(image_path)
    if width: st.image(src, width=width)
    else: st.image(src, use_container_width=True)

# --- INITIALIZE ---
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    st.markdown('<div style="text-align: center; margin-bottom:20px;">', unsafe_allow_html=True)
    if prof.get('image_url'): render_image(prof.get('image_url'), width=140)
    st.markdown('</div>', unsafe_allow_html=True)
    
    selected = option_menu(None, ["Home", "Experience", "Projects", "Skills", "Contact"], 
                           icons=["house", "briefcase", "rocket", "cpu", "envelope"], default_index=0,
                           styles={"nav-link-selected": {"background-color": "#3B82F6"}})
    st.markdown("---")
    
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin"):
            if st.button("Login") and st.text_input("Pass", type="password") == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
    else:
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6; margin-top:0;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("dashboards","0")}</div><div style="font-size:0.85rem; color:#64748B;">DASHBOARDS</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("manual_reduction","0%")}</div><div style="font-size:0.85rem; color:#64748B;">REDUCTION</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("efficiency","0%")}</div><div style="font-size:0.85rem; color:#64748B;">EFFICIENCY</div></div>', unsafe_allow_html=True)
    with c2: render_image(prof.get('image_url'), width=350)

# --- PROJECTS ---
elif selected == "Projects":
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None

    projects = st.session_state.data.get('projects', [])

    if st.session_state.selected_project is not None:
        idx = st.session_state.selected_project
        p = projects[idx]
        if st.button("← Back to Projects"):
            st.session_state.selected_project = None
            st.rerun()
        st.title(p.get('title'))
        st.caption(f"📂 {p.get('category')}")
        dash_img = p.get('dashboard_image') or p.get('image')
        if dash_img.endswith('.mp4'): st.video(dash_img)
        else: st.image(get_img_src(dash_img), use_container_width=True)
        st.markdown("### 📝 Details")
        st.write(p.get('details', 'Description coming soon.'))
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.info(f"**🚨 Problem**\n{p.get('problem')}")
        c2.success(f"**💡 Solution**\n{p.get('solution')}")
        c3.warning(f"**🚀 Impact**\n{p.get('impact')}")
    else:
        st.title("Projects")
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            batch = projects[i : i+2]
            for j, p in enumerate(batch):
                actual_idx = i + j
                with cols[j]:
                    img_src = get_img_src(p.get('image', ''))
                    
                    # 1. CARD HTML
                    st.markdown(f"""
                    <div class="project-card">
                        <div class="p-img-container">
                            <img src="{img_src}" class="p-img">
                        </div>
                        <div class="p-cat">{p.get('category')}</div>
                        <div class="p-title">{p.get('title')}</div>
                        <div class='p-detail'><span class='p-label'>🚨 Problem:</span> {p.get('problem')}</div>
                        <div class='p-detail'><span class='p-label'>💡 Solution:</span> {p.get('solution')}</div>
                        <div class='p-detail'><span class='p-label'>🚀 Impact:</span> {p.get('impact')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. BUTTON (FULL WIDTH FIX)
                    if st.button("More Information", key=f"btn_{actual_idx}"):
                        st.session_state.selected_project = actual_idx
                        st.rerun()
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    if skills:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            fig = go.Figure(data=go.Scatterpolar(r=list(skills.values()), theta=list(skills.keys()), fill='toself', marker=dict(color='#3B82F6')))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Proficiency")
    s_cols = st.columns(4)
    skill_items = list(skills.items())
    for i, (s, v) in enumerate(skill_items):
        with s_cols[i % 4]:
            st.markdown(f'<div class="metric-card"><b>{s}</b><div style="color:#3B82F6; font-size:1.2rem; font-weight:800;">{v}%</div><progress value="{v}" max="100" style="width:100%;"></progress></div>', unsafe_allow_html=True)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f'<div class="timeline-card" style="border-left: 6px solid #3B82F6;"><b>{job.get("role")}</b> @ {job.get("company")}<br><small>{job.get("date")}</small><p>{job.get("description")}</p></div>', unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    c1, c2 = st.columns(2)
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f'<a href="{item.get("value")}" target="_blank" style="text-decoration:none;"><div class="metric-card"><img src="{item.get("icon")}" width="40"><br><b>{item.get("label")}</b></div></a>', unsafe_allow_html=True)
