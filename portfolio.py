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
st.set_page_config(
    layout="wide", 
    page_title="Portfolio", 
    page_icon="✨",
    initial_sidebar_state="expanded"
)

# Gets the current directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ADMIN_PASSWORD = "admin" 

# ==========================================
# 2. APP-LIKE MOBILE CSS FRAMEWORK
# ==========================================
st.markdown("""
<style>
    /* --- GLOBAL THEME VARIABLES --- */
    :root {
        --primary-color: #3B82F6;
        --bg-color: #ffffff;
        --card-bg: #f8f9fa;
        --text-color: #000000;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0E1117;
            --card-bg: #262730;
            --text-color: #ffffff;
        }
    }

    /* --- 1. MEDIA QUERY: MOBILE VIEW (< 768px) --- */
    @media only screen and (max-width: 768px) {
        
        /* HIDE THE SIDEBAR ON MOBILE */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* HIDE THE HAMBURGER MENU (App feel) */
        button[kind="header"] {
            display: none !important;
        }
        
        /* ADJUST TOP PADDING FOR STICKY NAV */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 5rem !important;
        }

        /* MOBILE NAV VISIBLE */
        .mobile-nav-container {
            display: block !important;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 9999;
            background-color: var(--card-bg);
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            padding: 10px 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* FORCE SINGLE COLUMN IN GRIDS */
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 auto !important;
            min-width: 100% !important;
        }
    }

    /* --- 2. MEDIA QUERY: DESKTOP VIEW (> 768px) --- */
    @media only screen and (min-width: 769px) {
        /* HIDE MOBILE NAV ON DESKTOP */
        .mobile-nav-container {
            display: none !important;
        }
        
        /* SHOW SIDEBAR */
        section[data-testid="stSidebar"] {
            display: block !important;
        }
    }

    /* --- 3. GENERAL STYLING (Cards, etc.) --- */
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    
    /* Project Cards */
    .project-card {
        background-color: var(--card-bg); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .project-card:hover { border-color: #3B82F6; }

    /* Images */
    .p-img-container { 
        width: 100%; height: 180px; overflow: hidden; 
        border-radius: 15px; margin-bottom: 15px; 
    }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* Metrics */
    .metric-card {
        background: var(--card-bg); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px; padding: 20px; text-align: center;
        margin-bottom: 10px;
    }

    /* Timelines */
    .timeline-card {
        background: var(--card-bg);
        border-radius: 12px; padding: 20px; margin-bottom: 20px;
        border-left: 6px solid #3B82F6;
        border: 1px solid rgba(128,128,128,0.1);
        border-left-width: 6px;
    }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA MANAGER
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
        if check_url_exists(image_path): return image_path
        else: return "https://placehold.co/600x400/png?text=Updating+Soon"
    return image_path

def render_image(image_path, width=None):
    src = get_img_src(image_path)
    if width: st.image(src, width=width)
    else: st.image(src, use_container_width=True)

# Initialize Session State
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'current_page' not in st.session_state: st.session_state.current_page = "Home"

# ==========================================
# 4. NAVIGATION SYSTEM (HYBRID)
# ==========================================
menu_options = ["Home", "Experience", "Projects", "Skills", "Contact"]
icons_list = ["house", "briefcase", "rocket", "cpu", "envelope"]

# --- A. MOBILE NAVIGATION (TOP STICKY BAR) ---
# This container is hidden on Desktop via CSS
with st.container():
    st.markdown('<div class="mobile-nav-container">', unsafe_allow_html=True)
    # Use a horizontal menu for mobile app feel
    selected_mobile = option_menu(
        menu_title=None,
        options=menu_options,
        icons=icons_list,
        default_index=menu_options.index(st.session_state.current_page),
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#3B82F6"},
        },
        key="mobile_menu"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- B. DESKTOP NAVIGATION (SIDEBAR) ---
# This sidebar is hidden on Mobile via CSS
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    if prof.get('image_url'):
        img_src = get_img_src(prof.get('image_url'))
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="{img_src}" style="width: 140px; border-radius: 10px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </div>
        """, unsafe_allow_html=True)

    selected_desktop = option_menu(
        menu_title=None, 
        options=menu_options, 
        icons=icons_list, 
        default_index=menu_options.index(st.session_state.current_page),
        styles={"nav-link-selected": {"background-color": "#3B82F6"}},
        key="desktop_menu"
    )
    
    st.markdown('<div style="height: 1px; background-color: rgba(128,128,128,0.2); margin: 20px 0;"></div>', unsafe_allow_html=True)
    
    # Admin Panel (Only visible on Desktop Sidebar)
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Access"):
            with st.form("admin_auth"):
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    if password == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.rerun()
    else:
        st.success("Admin Active")
        json_string = json.dumps(st.session_state.data, indent=4)
        st.download_button("💾 Download JSON", json_string, "data.json", "application/json")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- C. SYNC NAVIGATION LOGIC ---
# Determine which menu was actually clicked
# If the user clicked mobile, update page. If desktop, update page.
if selected_mobile != st.session_state.current_page:
    st.session_state.current_page = selected_mobile
    st.rerun()
elif selected_desktop != st.session_state.current_page:
    st.session_state.current_page = selected_desktop
    st.rerun()

selected = st.session_state.current_page

# Reset project selection if moving away from Projects tab
if selected != "Projects":
    st.session_state.selected_project = None

# ==========================================
# 5. PAGE CONTENT RENDERING
# ==========================================

# --- PAGE: HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})

    # On Mobile, Columns stack automatically.
    # We use a reverse order for mobile (Image on top) vs Desktop (Text on left)
    # But for simplicity, we keep standard order, Streamlit handles stacking.
    
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown(f"<h1 style='font-size:3rem; margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6 !important; margin-top:0;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        
        st.markdown("### Key Metrics")
        mc1, mc2, mc3 = st.columns(3)
        with mc1: 
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("dashboards","0")}</div><div style="font-size:0.8rem; opacity:0.7;">DASHBOARDS</div></div>', unsafe_allow_html=True)
        with mc2: 
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("manual_reduction","0%")}</div><div style="font-size:0.8rem; opacity:0.7;">REDUCTION</div></div>', unsafe_allow_html=True)
        with mc3: 
            st.markdown(f'<div class="metric-card"><div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("efficiency","0%")}</div><div style="font-size:0.8rem; opacity:0.7;">EFFICIENCY</div></div>', unsafe_allow_html=True)

    with c2:
        render_image(prof.get('image_url'))
    
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Home"):
            st.session_state.data['profile']['name'] = st.text_input("Name", prof.get('name'))
            st.session_state.data['profile']['role'] = st.text_input("Role", prof.get('role'))
            st.session_state.data['profile']['summary'] = st.text_area("Summary", prof.get('summary'))
            st.session_state.data['profile']['image_url'] = st.text_input("Img URL", prof.get('image_url'))


# --- PAGE: PROJECTS ---
elif selected == "Projects":
    projects = st.session_state.data.get('projects', [])
    
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None

    # DETAIL VIEW
    if st.session_state.selected_project is not None:
        idx = st.session_state.selected_project
        if idx < len(projects):
            p = projects[idx]
            if st.button("← Back"):
                st.session_state.selected_project = None
                st.rerun()
            
            st.title(p.get('title'))
            st.caption(f"📂 {p.get('category')}")
            
            # Media
            dash_img = p.get('dashboard_image') or p.get('image')
            normalized_url = get_img_src(dash_img)
            if dash_img and dash_img.endswith('.mp4'):
                st.video(normalized_url)
            else:
                st.image(normalized_url, use_container_width=True)

            # Details
            st.write(p.get('details', 'Description coming soon.'))
            
            # Simple Blocks for Mobile Compatibility
            st.info(f"**Problem:** {p.get('problem')}")
            st.success(f"**Solution:** {p.get('solution')}")
            st.warning(f"**Impact:** {p.get('impact')}")
            
        else:
            st.session_state.selected_project = None
            st.rerun()
            
    # LIST VIEW
    else:
        st.title("Projects")
        categories = sorted(list(set([p.get('category', 'Other') for p in projects])))
        cat_filter = st.selectbox("Filter", ["All"] + categories)
        
        target_cats = categories if cat_filter == "All" else [cat_filter]
        
        for cat in target_cats:
            cat_projs = [p for p in projects if p.get('category', 'Other') == cat]
            if not cat_projs: continue
            
            st.markdown(f"### {cat}")
            
            # Create a grid that collapses on mobile
            cols = st.columns(2) 
            for i, p in enumerate(cat_projs):
                actual_idx = projects.index(p)
                img_src = get_img_src(p.get('image', ''))
                
                with cols[i % 2]:
                    html_card = f"""
                    <div class="project-card">
                        <div class="p-img-container"><img src="{img_src}" class="p-img"></div>
                        <div style="font-weight:700; font-size:1.1rem; margin-bottom:10px;">{p.get('title')}</div>
                        <div style="font-size:0.9rem; opacity:0.8; margin-bottom:15px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{p.get('problem')}</div>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
                    if st.button(f"View {p.get('title')}", key=f"btn_{actual_idx}"):
                        st.session_state.selected_project = actual_idx
                        st.rerun()

    if st.session_state.is_admin:
        with st.expander("➕ Add Project"):
            with st.form("add_p"):
                t = st.text_input("Title")
                if st.form_submit_button("Add"):
                    st.session_state.data['projects'].append({"title": t, "category": "New"})
                    st.rerun()

# --- PAGE: SKILLS ---
elif selected == "Skills":
    st.title("Skills")
    skills = st.session_state.data.get('skills', {})
    
    # 1. Chart View (Desktop Preferred, scales on mobile)
    if skills:
        r_vals = list(skills.values())
        theta_vals = list(skills.keys())
        fig = go.Figure(go.Scatterpolar(
            r=r_vals, theta=theta_vals, fill='toself', 
            line=dict(color='#3B82F6'), marker=dict(color='#3B82F6')
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
            showlegend=False, 
            height=350, # Reduced height for mobile
            margin=dict(t=20, b=20, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 2. List View (Better for Mobile)
    st.markdown("### Proficiency")
    for s, v in skills.items():
        st.markdown(f"""
        <div style="margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <b>{s}</b>
                <span style="color:#3B82F6; font-weight:bold;">{v}%</span>
            </div>
            <div style="width:100%; background-color:#e0e0e0; border-radius:5px; height:8px;">
                <div style="width:{v}%; background-color:#3B82F6; height:8px; border-radius:5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.is_admin:
        with st.expander("✏️ Edit Skills"):
            s_data = [{"Skill":k, "Value":v} for k,v in skills.items()]
            edf = st.data_editor(s_data, num_rows="dynamic")
            st.session_state.data['skills'] = {r['Skill']: int(r['Value']) for r in edf if r['Skill']}

# --- PAGE: EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="timeline-card">
            <h4 style="margin:0;">{job.get("role")}</h4>
            <div style="color:#3B82F6; font-weight:600;">{job.get("company")}</div>
            <small style="opacity:0.6;">{job.get("date")}</small>
            <p style="margin-top:10px; opacity:0.8;">{job.get("description")}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.is_admin:
        with st.expander("➕ Add Experience"):
            with st.form("add_exp"):
                r = st.text_input("Role")
                c = st.text_input("Company")
                d = st.text_input("Date")
                desc = st.text_area("Desc")
                if st.form_submit_button("Add"):
                    st.session_state.data['experience'].insert(0, {"role":r, "company":c, "date":d, "description":desc})
                    st.rerun()

# --- PAGE: CONTACT ---
elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    
    # Responsive Grid: 1 column on mobile (auto), 2 on desktop
    c1, c2 = st.columns(2)
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"""
            <a href="{item.get("value")}" target="_blank" style="text-decoration:none; color:inherit;">
                <div class="metric-card" style="display:flex; align-items:center; gap:15px; text-align:left;">
                    <img src="{item.get("icon")}" width="30">
                    <div>
                        <div style="font-weight:bold;">{item.get("label")}</div>
                        <div style="font-size:0.85rem; opacity:0.7;">Click to Connect</div>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Contacts"):
            c_data = [{"Label":x['label'], "Value":x['value'], "Icon":x['icon']} for x in prof.get('contact_info', [])]
            edf = st.data_editor(c_data, num_rows="dynamic")
            st.session_state.data['profile']['contact_info'] = [{"label":r['Label'], "value":r['Value'], "icon":r['Icon']} for r in edf if r['Label']]
