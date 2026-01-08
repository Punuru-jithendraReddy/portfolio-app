import streamlit as st
import json
import os
import base64
import textwrap
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
    
    /* --- ANIMATIONS DEFINITIONS --- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 20px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }
    
    @keyframes zoomIn {
        from { opacity: 0; transform: scale3d(0.95, 0.95, 0.95); }
        to { opacity: 1; transform: scale3d(1, 1, 1); }
    }

    /* 0. COLUMN SETUP */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* 1. PROJECT CARD DESIGN */
    .project-card {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        position: relative; 
        
        display: flex;
        flex-direction: column;
        
        flex: 1;
        height: 100%; 
        min-height: 450px; 
        
        padding-bottom: 70px; 
        margin-bottom: 20px; 
        
        /* ANIMATION */
        animation: fadeInUp 0.6s ease-out;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .project-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.1);
        border-color: #3B82F6;
    }

    /* PROJECT IMAGES */
    .p-img-container { 
        width: 100%; 
        height: 180px; 
        overflow: hidden; 
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #f1f5f9;
        flex-shrink: 0; 
    }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* CATEGORY OVERLAY */
    .p-cat-overlay {
        position: absolute;
        top: 30px; 
        left: 30px;
        background-color: rgba(255, 255, 255, 0.95);
        color: #3B82F6;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 5;
        border: 1px solid #e2e8f0;
    }

    /* PROJECT TEXT */
    .p-title { 
        font-size: 1.2rem; 
        font-weight: 700; 
        color: #0F172A;
        margin-bottom: 15px; 
        line-height: 1.3;
        flex-grow: 0; 
    }
    
    .p-details-container { flex-grow: 1; }

    .p-row {
        display: flex;       
        align-items: flex-start; 
        margin-bottom: 10px; 
    }
    
    .p-label {
        min-width: 85px;    
        flex-shrink: 0;     
        font-weight: 700;
        color: #1E293B;
        font-size: 0.85rem;
    }
    
    .p-val {
        font-size: 0.85rem;
        color: #334155;
        line-height: 1.5;
    }

    /* 2. BUTTON STYLING */
    div[data-testid="column"] .stButton {
        position: absolute !important;
        bottom: 20px !important; 
        right: 20px !important;      
        left: unset !important;      
        width: auto !important;      
        text-align: right !important;
        z-index: 10 !important;
    }

    div[data-testid="column"] .stButton button {
        background: #EFF6FF !important;
        color: #2563EB !important;
        border: 1px solid #DBEAFE !important;
        border-radius: 8px !important;
        width: auto !important; 
        font-size: 0.90rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.0rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
        float: right !important; 
    }

    div[data-testid="column"] .stButton button:hover {
        background: #2563EB !important;
        color: white !important;
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2) !important;
    }
    
    div[data-testid="column"] .stButton button:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    /* 3. DETAILED VIEW BOXES */
    .detail-row {
        display: flex;
        flex-direction: row;
        gap: 20px;
        width: 100%;
        margin-bottom: 20px;
        flex-wrap: wrap; 
        animation: zoomIn 0.5s ease-out;
    }
    
    .detail-box {
        flex: 1; 
        display: flex;
        flex-direction: column;
        padding: 20px;
        border-radius: 10px;
        min-width: 200px;
    }

    .box-title {
        font-weight: 800;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
    }

    .box-content {
        font-size: 0.95rem;
        line-height: 1.6;
        font-weight: 500;
    }

    .d-blue { background-color: #EFF6FF; border: 1px solid #DBEAFE; color: #172554; } 
    .d-green { background-color: #F0FDF4; border: 1px solid #DCFCE7; color: #14532D; } 
    .d-yellow { background-color: #FEFCE8; border: 1px solid #FEF9C3; color: #78350F; } 

    /* 4. OTHER CARDS */
    .timeline-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 24px; margin-bottom: 20px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        animation: fadeInUp 0.6s ease-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .timeline-card:hover { transform: translateX(5px); }

    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        animation: zoomIn 0.5s ease-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #3B82F6; }

    /* SKILL BARS */
    .skill-metric {
        background: white;
        border: 1px solid #f1f5f9;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        animation: fadeInUp 0.7s ease-out;
    }

    /* Progress Bar */
    progress { accent-color: #3B82F6; }
    progress::-webkit-progress-value { background-color: #3B82F6 !important; }
    progress::-moz-progress-bar { background-color: #3B82F6 !important; }

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
    
    if prof.get('image_url'):
        img_src = get_img_src(prof.get('image_url'))
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="{img_src}" style="width: 140px; border-radius: 10px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </div>
        """, unsafe_allow_html=True)
    
    selected = option_menu(None, ["Home", "Experience", "Projects", "Skills", "Contact"], 
                           icons=["house", "briefcase", "rocket", "cpu", "envelope"], default_index=0,
                           styles={"nav-link-selected": {"background-color": "#3B82F6"}})
    st.markdown("---")
    
    # --- FIXED ADMIN LOGIN LOGIC ---
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Access"):
            # Using st.form ensures the button and input work together reliably
            with st.form("admin_auth"):
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    if password == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error("Incorrect password")
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
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0; animation: fadeInUp 0.5s ease-out;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6; margin-top:0; animation: fadeInUp 0.6s ease-out;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
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
        
        # --- DETAILED VIEW BOXES ---
        html_details = textwrap.dedent(f"""
            <div class="detail-row">
                <div class="detail-box d-blue">
                    <div class="box-title">🚨 Problem</div>
                    <div class="box-content">{p.get('problem')}</div>
                </div>
                <div class="detail-box d-green">
                    <div class="box-title">💡 Solution</div>
                    <div class="box-content">{p.get('solution')}</div>
                </div>
                <div class="detail-box d-yellow">
                    <div class="box-title">🚀 Impact</div>
                    <div class="box-content">{p.get('impact')}</div>
                </div>
            </div>
        """)
        st.markdown(html_details, unsafe_allow_html=True)

    else:
        st.title("Projects")
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            batch = projects[i : i+2]
            for j, p in enumerate(batch):
                actual_idx = i + j
                with cols[j]:
                    img_src = get_img_src(p.get('image', ''))
                    
                    # --- PROJECT CARD ---
                    html_content = textwrap.dedent(f"""
                        <div class="project-card">
                            <div class="p-cat-overlay">{p.get('category')}</div>
                            <div class="p-img-container"><img src="{img_src}" class="p-img"></div>
                            <div class="p-title">{p.get('title')}</div>
                            <div class="p-details-container">
                                <div class="p-row"><div class="p-label">🚨 Problem:</div><div class="p-val">{p.get('problem')}</div></div>
                                <div class="p-row"><div class="p-label">💡 Solution:</div><div class="p-val">{p.get('solution')}</div></div>
                                <div class="p-row"><div class="p-label">🚀 Impact:</div><div class="p-val">{p.get('impact')}</div></div>
                            </div>
                        </div>
                    """)
                    st.markdown(html_content, unsafe_allow_html=True)
                    
                    if st.button("More Information ➜", key=f"btn_{actual_idx}"):
                        st.session_state.selected_project = actual_idx
                        st.rerun()
            st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    
    if skills:
        # SPIDER CHART
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            r_vals = list(skills.values())
            theta_vals = list(skills.keys())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=theta_vals,
                fill='toself',
                name='Skills',
                line=dict(color='#3B82F6', width=2),
                marker=dict(color='#3B82F6')
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, ticks='', gridcolor='#E2E8F0'),
                    angularaxis=dict(showticklabels=True, gridcolor='#E2E8F0'),
                    gridshape='linear',
                    bgcolor='white'
                ),
                showlegend=False,
                height=400,
                margin=dict(t=40, b=40, l=40, r=40)
            )
            st.plotly_chart(fig, use_container_width=True)

    # PROFICIENCY BARS
    st.markdown("### Proficiency")
    s_cols = st.columns(4)
    skill_items = list(skills.items())
    for i, (s, v) in enumerate(skill_items):
        with s_cols[i % 4]:
            st.markdown(f"""
            <div class="skill-metric">
                <b>{s}</b>
                <div style="color:#3B82F6; font-size:1.2rem; font-weight:800;">{v}%</div>
                <progress value="{v}" max="100" style="width:100%; height:8px; border-radius:5px;"></progress>
            </div>
            """, unsafe_allow_html=True)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="timeline-card">
            <b>{job.get("role")}</b> @ {job.get("company")}<br>
            <small>{job.get("date")}</small>
            <div class="timeline-desc" style="white-space:pre-line; color:#475569; margin-top:10px; line-height:1.6; font-size:0.95rem;">{job.get("description")}</div>
        </div>
        """, unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    c1, c2 = st.columns(2)
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f'<a href="{item.get("value")}" target="_blank" style="text-decoration:none;"><div class="metric-card"><img src="{item.get("icon")}" width="40"><br><b>{item.get("label")}</b></div></a>', unsafe_allow_html=True)
