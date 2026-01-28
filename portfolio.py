import streamlit as st
import json
import os
import textwrap
import requests
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ADMIN_PASSWORD = "admin" 

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="🧑‍💻")

# ==========================================
# 2. DATA MANAGER
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE): 
         return {
            "profile": {"name": "Your Name", "role": "Your Role", "summary": "Summary here", "image_url": "", "contact_info": []},
            "metrics": {"dashboards": "10+", "manual_reduction": "50%", "efficiency": "30%"},
            "experience": [],
            "projects": [],
            "skills": {}
        }
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

@st.cache_data(ttl=3600)
def check_url_exists(url):
    try:
        response = requests.head(url, timeout=1.5)
        return response.status_code < 400
    except:
        return False

def get_img_src(image_path):
    if not image_path: return "https://placehold.co/600x400/png?text=No+Image"
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    if image_path.startswith("http"):
        if check_url_exists(image_path):
            return image_path
        else:
            return "https://placehold.co/600x400/png?text=Updating+Soon"
    return image_path

def render_image(image_path, width=None):
    src = get_img_src(image_path)
    if width: st.image(src, width=width)
    else: st.image(src, use_container_width=True)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'mobile_nav' not in st.session_state: st.session_state.mobile_nav = "Home"

# ==========================================
# 3. CSS: DUAL LAYOUT ENGINE
# ==========================================
st.markdown("""
<style>
    /* --- THEME ADAPTIVE COLORS --- */
    .main { padding-top: 1rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: var(--text-color) !important; }
    p, div, span { color: var(--text-color); }

    /* =========================================
       DESKTOP vs MOBILE TOGGLE
       ========================================= */
    /* Default: Show Desktop, Hide Mobile */
    .desktop-layout { display: block; }
    .mobile-layout { display: none !important; }
    
    /* Hide the sidebar on mobile */
    @media (max-width: 800px) {
        section[data-testid="stSidebar"] { display: none; }
        .desktop-layout { display: none !important; }
        .mobile-layout { display: block !important; }
    }

    /* =========================================
       SHARED STYLES (Cards, Animations)
       ========================================= */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 20px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }
    
    .project-card {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        position: relative; 
        display: flex;
        flex-direction: column;
        flex: 1;
        margin-bottom: 20px; 
        animation: fadeInUp 0.6s ease-out;
    }
    
    .metric-card {
        background: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        position: relative;
    }
    
    .timeline-card {
        background: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 24px; margin-bottom: 20px; border-left: 6px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    /* Images & Text Helpers */
    .p-img-container { width: 100%; height: 180px; overflow: hidden; border-radius: 15px; margin-bottom: 15px; border: 1px solid rgba(128, 128, 128, 0.1); }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    .p-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; }
    .p-row { display: flex; align-items: flex-start; margin-bottom: 8px; }
    .p-label { min-width: 80px; font-weight: 700; font-size: 0.85rem; opacity: 0.9; }
    .p-val { font-size: 0.85rem; opacity: 0.8; }
    
    /* =========================================
       MOBILE SPECIFIC STYLES
       ========================================= */
    .mobile-header {
        position: sticky; top: 0; z-index: 100;
        background: var(--background-color);
        padding: 15px 5px;
        border-bottom: 1px solid rgba(128,128,128,0.1);
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 20px;
    }
    
    .mobile-profile-pic {
        width: 50px; height: 50px; border-radius: 50%; object-fit: cover;
        border: 2px solid #3B82F6;
    }
    
    .mobile-card {
        background: var(--secondary-background-color);
        border-radius: 16px; padding: 16px; margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Bottom Navigation Bar */
    .bottom-nav {
        position: fixed; bottom: 0; left: 0; width: 100%;
        height: 65px;
        background: var(--secondary-background-color);
        border-top: 1px solid rgba(128,128,128,0.2);
        display: flex; justify-content: space-around; align-items: center;
        z-index: 9999;
        padding-bottom: 5px; /* Safe area */
    }
    
    .nav-item {
        background: none; border: none; cursor: pointer;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        color: var(--text-color); opacity: 0.6; font-size: 10px;
        width: 100%; height: 100%;
    }
    
    .nav-item.active {
        opacity: 1; color: #3B82F6;
    }
    
    .nav-icon { font-size: 20px; margin-bottom: 4px; }
    
    /* Adjust Streamlit specific paddings for mobile view */
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

</style>
""", unsafe_allow_html=True)

# Helper function to inject the wrapper start
def layout_start(layout_type):
    st.markdown(f'<div class="{layout_type}">', unsafe_allow_html=True)

# Helper function to inject the wrapper end
def layout_end():
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 4. DESKTOP LOGIC (Existing Code Wrapped)
# ==========================================
layout_start("desktop-layout")

# --- DESKTOP SIDEBAR ---
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
    
    if selected != "Projects":
        st.session_state.selected_project = None
    
    st.markdown("---")
    
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Access"):
            with st.form("admin_auth"):
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    if password == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error("Incorrect password")
    else:
        st.success("Admin Mode Active")
        json_string = json.dumps(st.session_state.data, indent=4)
        st.download_button("💾 Download Config", json_string, "data.json", "application/json")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- DESKTOP PAGE CONTENT ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    
    # (Admin editing logic hidden for brevity - assumes logic works)
    if st.session_state.is_admin:
         st.info("Admin: Edit details in sidebar or expanders above (simplified for layout demo)")

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6 !important;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        
        mc1, mc2, mc3 = st.columns(3)
        with mc1: 
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("dashboards","0")}</div><div class="metric-label">DASHBOARDS</div></div>', unsafe_allow_html=True)
        with mc2: 
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("manual_reduction","0%")}</div><div class="metric-label">REDUCTION</div></div>', unsafe_allow_html=True)
        with mc3: 
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("efficiency","0%")}</div><div class="metric-label">EFFICIENCY</div></div>', unsafe_allow_html=True)
    with c2: render_image(prof.get('image_url'), width=350)

elif selected == "Projects":
    projects = st.session_state.data.get('projects', [])
    if st.session_state.selected_project is not None:
        idx = st.session_state.selected_project
        if idx < len(projects):
            p = projects[idx]
            if st.button("← Back"):
                st.session_state.selected_project = None
                st.rerun()
            st.title(p.get('title'))
            st.image(get_img_src(p.get('image')), use_container_width=True)
            st.write(p.get('details'))
    else:
        st.title("Projects")
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            batch = projects[i:i+2]
            for j, p in enumerate(batch):
                with cols[j]:
                    img_src = get_img_src(p.get('image', ''))
                    st.markdown(f"""
                        <div class="project-card">
                            <div class="p-img-container"><img src="{img_src}" class="p-img"></div>
                            <div class="p-title">{p.get('title')}</div>
                            <div class="p-val">{p.get('problem')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("View Details", key=f"d_btn_{projects.index(p)}"):
                        st.session_state.selected_project = projects.index(p)
                        st.rerun()

elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="timeline-card">
            <div style="font-weight:bold; font-size:1.1rem;">{job.get("role")} @ {job.get("company")}</div>
            <small style="opacity:0.7;">{job.get("date")}</small>
            <div style="margin-top:10px;">{job.get("description")}</div>
        </div>
        """, unsafe_allow_html=True)

elif selected == "Skills":
    st.title("Skills")
    skills = st.session_state.data.get('skills', {})
    if skills:
        fig = go.Figure(data=go.Scatterpolar(r=list(skills.values()), theta=list(skills.keys()), fill='toself'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=400, margin=dict(t=20, b=20, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    for item in prof.get('contact_info', []):
        st.markdown(f'<a href="{item.get("value")}" target="_blank"><div class="metric-card"><b>{item.get("label")}</b></div></a>', unsafe_allow_html=True)

layout_end() # END DESKTOP LAYOUT


# ==========================================
# 5. MOBILE LOGIC (New "App" Experience)
# ==========================================
layout_start("mobile-layout")

# --- MOBILE NAVIGATION HANDLER ---
# We use st.radio disguised as a bottom bar logic using columns, 
# but for true custom styling we will use buttons in columns that update state
# Note: Streamlit buttons cause re-runs. 

# Get Data
prof = st.session_state.data.get('profile', {})
metrics = st.session_state.data.get('metrics', {})
projects = st.session_state.data.get('projects', [])
exp = st.session_state.data.get('experience', [])
skills = st.session_state.data.get('skills', {})

# --- MOBILE HEADER ---
# Simple header with Avatar and Name
img_src = get_img_src(prof.get('image_url'))
st.markdown(f"""
<div class="mobile-header">
    <div>
        <div style="font-weight: 800; font-size: 1.2rem;">{prof.get('name')}</div>
        <div style="font-size: 0.8rem; opacity: 0.7;">{prof.get('role')}</div>
    </div>
    <img src="{img_src}" class="mobile-profile-pic">
</div>
""", unsafe_allow_html=True)

# --- MOBILE CONTENT ROUTER ---
if st.session_state.mobile_nav == "Home":
    st.markdown(f"#### 👋 Hi, I'm {prof.get('name').split(' ')[0]}")
    st.markdown(f"<div style='margin-bottom:20px; font-size:0.95rem; line-height:1.5;'>{prof.get('summary')}</div>", unsafe_allow_html=True)
    
    # Horizontal Scroll Metrics
    st.markdown("<div style='display:flex; gap:10px; overflow-x:auto; padding-bottom:10px;'>", unsafe_allow_html=True)
    m_items = [
        ("📊", metrics.get("dashboards"), "Dashboards"),
        ("⚡", metrics.get("manual_reduction"), "Reduction"),
        ("📈", metrics.get("efficiency"), "Efficiency")
    ]
    cols = st.columns(3)
    for i, (icon, val, lbl) in enumerate(m_items):
        with cols[i]:
            st.markdown(f"""
            <div style="background:var(--secondary-background-color); padding:15px; border-radius:12px; text-align:center; min-width:100px;">
                <div style="font-size:1.2rem;">{icon}</div>
                <div style="font-weight:800; color:#3B82F6; font-size:1.1rem;">{val}</div>
                <div style="font-size:0.7rem; opacity:0.7;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### Featured Project")
    if projects:
        p = projects[0] # Show first project
        p_img = get_img_src(p.get('image'))
        st.markdown(f"""
        <div class="mobile-card">
            <img src="{p_img}" style="width:100%; height:150px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
            <div style="font-weight:700; font-size:1.1rem; margin-bottom:5px;">{p.get('title')}</div>
            <div style="font-size:0.85rem; opacity:0.8; margin-bottom:10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                {p.get('problem')}
            </div>
            <div style="font-size:0.7rem; color:#3B82F6; font-weight:700; text-transform:uppercase;">{p.get('category')}</div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.mobile_nav == "Projects":
    st.markdown("### My Projects")
    for idx, p in enumerate(projects):
        p_img = get_img_src(p.get('image'))
        with st.container():
            st.markdown(f"""
            <div class="mobile-card">
                <div style="display:flex; gap:15px;">
                    <img src="{p_img}" style="width:80px; height:80px; object-fit:cover; border-radius:8px;">
                    <div>
                        <div style="font-weight:700; font-size:1rem;">{p.get('title')}</div>
                        <div style="font-size:0.7rem; opacity:0.6; margin-bottom:4px;">{p.get('category')}</div>
                        <div style="font-size:0.8rem; line-height:1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{p.get('problem')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Mobile "Read More" logic would ideally open a modal, 
            # but for simplicity we keep it linear in this list view
            with st.expander(f"Read More about {p.get('title')}"):
                st.write(f"**Solution:** {p.get('solution')}")
                st.write(f"**Impact:** {p.get('impact')}")

elif st.session_state.mobile_nav == "Exp":
    st.markdown("### Career Path")
    for job in exp:
        st.markdown(f"""
        <div class="mobile-card" style="border-left: 4px solid #3B82F6;">
            <div style="font-weight:700;">{job.get('role')}</div>
            <div style="font-size:0.9rem; opacity:0.8;">{job.get('company')}</div>
            <div style="font-size:0.75rem; opacity:0.6; margin-bottom:10px;">{job.get('date')}</div>
            <div style="font-size:0.85rem; line-height:1.5;">{job.get('description')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Skills")
    # Simple chip view for mobile
    skill_html = "<div style='display:flex; flex-wrap:wrap; gap:8px;'>"
    for s, v in skills.items():
        skill_html += f"<span style='background:rgba(59,130,246,0.1); color:#3B82F6; padding:5px 10px; border-radius:15px; font-size:0.8rem; font-weight:600;'>{s}</span>"
    skill_html += "</div>"
    st.markdown(skill_html, unsafe_allow_html=True)

elif st.session_state.mobile_nav == "Contact":
    st.markdown("### Get in Touch")
    prof = st.session_state.data.get('profile', {})
    
    for item in prof.get('contact_info', []):
        st.markdown(f"""
        <a href="{item.get('value')}" target="_blank" style="text-decoration:none; color:inherit;">
            <div class="mobile-card" style="display:flex; align-items:center; gap:15px;">
                <img src="{item.get('icon')}" width="30">
                <div style="font-weight:600;">{item.get('label')}</div>
                <div style="margin-left:auto;">➜</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

# --- MOBILE BOTTOM NAVIGATION ---
# This uses st.columns to create clickable buttons that update session state
# We use custom CSS to fix them to the bottom
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True) # Spacer

# We render the HTML for the navbar structure
# But we need Streamlit interactivity. 
# Workaround: Put st.buttons in a container, style them to be fixed bottom.
# However, styling Streamlit buttons to be fixed position is tricky and often breaks.
# Better approach for reliable mobile navigation: 
# Use standard st.columns at the bottom of the script, 
# but visually it will just be buttons at the bottom of the page content.
# For a TRUE sticky footer in pure Streamlit python, we rely on the CSS 'bottom-nav' class defined earlier.
# But since we can't easily inject 'onclick' into custom HTML to change python state, 
# we will use Streamlit columns at the very end and style them to look like a tab bar.

# Since we can't purely emulate an app bar with state change via CSS only, 
# we will stick the navigation buttons at the bottom of the content flow 
# OR use a 3rd party component. 
# To keep it pure Streamlit, we will use a set of buttons at the top or bottom 
# designed for mobile.

# Let's put the navigation controls immediately after the Header for better UX in Streamlit's linear flow
# OR use columns with `key` tracking.

# Redoing Mobile Nav for Streamlit limitation:
# We will place a "Tab Bar" at the TOP of the mobile view (below header) 
# because fixed-bottom buttons in Streamlit are unstable.

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

# Helper to style buttons
def nav_btn(label, key_val, icon):
    active = st.session_state.mobile_nav == key_val
    bt = st.button(f"{icon}\n{label}", key=f"mob_nav_{key_val}", use_container_width=True)
    if bt:
        st.session_state.mobile_nav = key_val
        st.rerun()

with col1: nav_btn("Home", "Home", "🏠")
with col2: nav_btn("Work", "Projects", "🚀")
with col3: nav_btn("Career", "Exp", "💼")
with col4: nav_btn("Contact", "Contact", "📬")


layout_end() # END MOBILE LAYOUT
