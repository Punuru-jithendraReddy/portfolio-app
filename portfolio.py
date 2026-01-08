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
    
    /* CRITICAL: REMOVE SPACE BETWEEN HTML AND BUTTON */
    [data-testid="column"] [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }

    /* 1. HERO METRIC CARDS */
    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); 
        border-color: #3B82F6; 
    }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #3B82F6; }
    .metric-label { font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; }

    /* 2. TIMELINE CARDS */
    .timeline-card {
        background: white; border-radius: 12px; padding: 24px;
        margin-bottom: 20px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .timeline-card:hover { 
        transform: translateX(8px); 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
    }
    .t-role { font-size: 1.3rem; font-weight: 700; color: #1E293B; margin: 0; }
    .t-company { font-size: 1rem; font-weight: 600; color: #3B82F6; margin-bottom: 8px; display: inline-block;}
    .t-date { font-size: 0.85rem; color: #94A3B8; float: right; font-weight: 500; }
    .t-desc { font-size: 0.95rem; color: #334155; line-height: 1.6; margin-top: 10px; white-space: pre-line; }

    /* 3. PROJECT CARDS */
    .project-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 0px; 
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 540px; 
        
        /* Padding at the bottom provides space for the button inside the card */
        padding-bottom: 75px; 
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
        flex-shrink: 0;
    }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    
    .p-content { 
        padding: 20px; 
        flex-grow: 1;
        display: flex; 
        flex-direction: column; 
    }
    
    /* CATEGORY OVERLAY: Top-Left corner of the card over the image */
    .p-cat-overlay { 
        position: absolute;
        top: 15px;
        left: 15px;
        z-index: 10;
        background-color: white;
        color: #3B82F6;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem; 
        font-weight: 800; 
        text-transform: uppercase; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        letter-spacing: 0.5px;
        border: 1px solid #E2E8F0;
    }

    .p-title { font-size: 1.25rem; font-weight: 800; color: #1E293B; margin-bottom: 10px; }
    .p-detail { font-size: 0.90rem; color: #475569; margin-bottom: 8px; line-height: 1.4; }

    /* 6. BUTTON STYLING: PULL INSIDE BOTTOM-RIGHT */
    [data-testid="column"] .stButton {
        margin-top: -65px !important; /* Move button UP into the card padding */
        padding-bottom: 15px !important;
        display: flex !important;
        justify-content: flex-end !important; /* Align to the RIGHT */
        position: relative !important;
        z-index: 99 !important;
    }

    [data-testid="column"] .stButton button {
        margin-right: 15px !important; /* Space from the right edge */
        background-color: #F0F9FF !important; /* Light Blue */
        color: #0284C7 !important; /* Dark Blue Text */
        border: 1px solid #BAE6FD !important; /* Light Blue Border */
        border-radius: 8px !important;
        padding: 0.4rem 1.0rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="column"] .stButton button:hover {
        background-color: #E0F2FE !important;
        border-color: #0284C7 !important;
        color: #0369A1 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* 4. SKILL METRICS */
    .skill-metric {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        border: 1px solid #E2E8F0;
        margin-bottom: 10px;
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
        st.toast("Saved! Download JSON to update GitHub.", icon="💾")
    except Exception as e: st.error(f"Save failed: {e}")

def get_img_src(image_path):
    if not image_path: return "https://placehold.co/600x400/png?text=No+Image"
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    if image_path.startswith("http"): return image_path
    
    filename = os.path.basename(image_path)
    possible_paths = [os.path.join(BASE_DIR, "assets", filename), os.path.join(BASE_DIR, filename)]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://placehold.co/600x400/png?text=Missing"

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
        with st.expander("🔒 Admin Login"):
            if st.button("Login") and st.text_input("Password", type="password") == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
    else:
        st.success("Admin Mode")
        st.download_button("📥 Download JSON", data=json.dumps(st.session_state.data, indent=4), file_name="data.json", mime="application/json")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Profile"):
            n_name = st.text_input("Name", prof.get('name', '')); n_role = st.text_input("Role", prof.get('role', ''))
            n_sum = st.text_area("Summary", prof.get('summary', ''), height=150); n_img = st.text_input("Image URL", prof.get('image_url', ''))
            c1, c2, c3 = st.columns(3)
            m1 = c1.text_input("Dashboards", mets.get('dashboards', '')); m2 = c2.text_input("Reduction", mets.get('manual_reduction', ''))
            m3 = c3.text_input("Efficiency", mets.get('efficiency', ''))
            if st.button("Save Home"):
                st.session_state.data['profile'].update({"name": n_name, "role": n_role, "summary": n_sum, "image_url": n_img})
                st.session_state.data['metrics'] = {"dashboards": m1, "manual_reduction": m2, "efficiency": m3}
                save_data(st.session_state.data); st.rerun()

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6; margin-top:0;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("dashboards","0")}</div><div class="metric-label">Dashboards</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("manual_reduction","0%")}</div><div class="metric-label">Reduction</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("efficiency","0%")}</div><div class="metric-label">Efficiency</div></div>', unsafe_allow_html=True)
    with c2:
        render_image(prof.get('image_url'), width=350)

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
        
        st.markdown("### 📝 Detailed Description")
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
                    st.markdown(f"""
                    <div class="project-card">
                        <div class="p-cat-overlay">{p.get('category')}</div>
                        <div class="p-img-container">
                            <img src="{img_src}" class="p-img">
                        </div>
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
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

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
            st.markdown(f'<div class="skill-metric"><div style="font-weight:bold;">{s}</div><div style="color:#3B82F6; font-size:1.2rem; font-weight:800;">{v}%</div><progress value="{v}" max="100" style="width:100%;"></progress></div>', unsafe_allow_html=True)

# --- REMAINING SECTIONS (Experience/Contact) ---
elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f'<div class="timeline-card"><span class="t-date">{job.get("date")}</span><div class="t-role">{job.get("role")}</div><div class="t-company">{job.get("company")}</div><div class="t-desc">{job.get("description")}</div></div>', unsafe_allow_html=True)

elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    c1, c2 = st.columns(2)
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f'<a href="{item.get("value")}" target="_blank" style="text-decoration:none;"><div class="metric-card"><img src="{item.get("icon")}" width="40"><br><b>{item.get("label")}</b><br>{item.get("value")}</div></a>', unsafe_allow_html=True)
