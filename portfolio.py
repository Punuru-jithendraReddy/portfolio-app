import streamlit as st
import json
import os
import requests
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import textwrap

# ==========================================
# 1. CONFIG & SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ADMIN_PASSWORD = "admin" 

st.set_page_config(
    layout="wide", 
    page_title="Portfolio", 
    page_icon="✨",
    initial_sidebar_state="expanded" 
)

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'data' not in st.session_state: 
    # Load data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f: st.session_state.data = json.load(f)
    else:
        st.session_state.data = {"profile": {}, "metrics": {}, "projects": [], "experience": [], "skills": {}}

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_project' not in st.session_state: st.session_state.selected_project = None

# ==========================================
# 2. CSS: STRICT DESKTOP/MOBILE SEPARATION
# ==========================================
st.markdown("""
<style>
    /* --- SHARED THEME --- */
    .main { padding-top: 2rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: var(--text-color); }
    
    /* HIDE STREAMLIT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* =========================================
       DESKTOP VIEW (Default)
       ========================================= */
    /* By default, hide the mobile nav */
    .mobile-nav-wrapper { display: none !important; }
    
    /* Project Detail Boxes (Desktop Style) */
    .detail-row { display: flex; flex-direction: row; gap: 20px; width: 100%; margin-bottom: 20px; }
    .detail-box { flex: 1; padding: 20px; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2); }
    .d-blue { background-color: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); }
    .d-green { background-color: rgba(34, 197, 94, 0.1); border-color: rgba(34, 197, 94, 0.3); }
    .d-yellow { background-color: rgba(234, 179, 8, 0.1); border-color: rgba(234, 179, 8, 0.3); }
    .box-title { font-weight: 800; margin-bottom: 10px; }

    /* =========================================
       MOBILE VIEW (Max Width 768px)
       ========================================= */
    @media (max-width: 768px) {
        /* 1. HIDE SIDEBAR COMPLETELY */
        section[data-testid="stSidebar"] { display: none !important; }
        
        /* 2. SHOW BOTTOM NAV */
        .mobile-nav-wrapper { 
            display: block !important; 
            position: fixed; bottom: 0; left: 0; right: 0;
            background: var(--secondary-background-color);
            z-index: 99999;
            border-top: 1px solid rgba(128,128,128,0.2);
            padding-bottom: 15px; /* iOS Home Bar area */
        }
        
        /* 3. ADJUST PADDING (So content isn't hidden behind nav) */
        .block-container { padding-bottom: 120px !important; padding-top: 1rem !important; }
        
        /* 4. MOBILE CARD STYLING */
        .project-card, .metric-card, .timeline-card {
            margin-bottom: 15px !important;
        }
        
        /* Stack detail boxes vertically on mobile */
        .detail-row { flex-direction: column !important; }
    }
    
    /* COMPONENT STYLES */
    .project-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .metric-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 10px; padding: 15px; text-align: center;
    }
    .timeline-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-left: 4px solid #3B82F6;
        border-radius: 8px; padding: 15px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_img_src(image_path):
    if not image_path: return "https://placehold.co/600x400/png?text=No+Image"
    if "github.com" in image_path and "/blob/" in image_path:
        return image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return image_path

# ==========================================
# 4. NAVIGATION LOGIC (SYNCED)
# ==========================================
menu_opts = ["Home", "Experience", "Projects", "Skills", "Contact"]
menu_icons = ["house", "briefcase", "rocket", "cpu", "envelope"]

# Determine index
try:
    current_index = menu_opts.index(st.session_state.page)
except:
    current_index = 0

# --- A. DESKTOP SIDEBAR ---
with st.sidebar:
    # Profile Image
    prof = st.session_state.data.get('profile', {})
    if prof.get('image_url'):
        st.image(get_img_src(prof.get('image_url')), width=120)
        
    # Nav Menu
    nav_desktop = option_menu(
        None, menu_opts, icons=menu_icons, 
        default_index=current_index, 
        key="nav_desktop",
        styles={"nav-link-selected": {"background-color": "#3B82F6"}}
    )
    
    # Desktop Admin
    st.markdown("---")
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin"):
            pwd = st.text_input("Password", type="password", key="desk_pwd")
            if st.button("Login", key="desk_login"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
    else:
        if st.button("Logout", key="desk_logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- B. MOBILE BOTTOM NAV (Hidden on Desktop via CSS) ---
st.markdown('<div class="mobile-nav-wrapper">', unsafe_allow_html=True)
nav_mobile = option_menu(
    None, menu_opts, icons=menu_icons, 
    default_index=current_index, 
    orientation="horizontal",
    key="nav_mobile",
    styles={
        "container": {"padding": "5px", "background-color": "transparent"},
        "nav-link": {"font-size": "12px", "margin": "0px", "padding": "10px"},
        "nav-link-selected": {"background-color": "#3B82F6"}
    }
)
st.markdown('</div>', unsafe_allow_html=True)

# --- SYNC LOGIC (Prevents Infinite Loop) ---
# We check which widget differs from the current state variable
if nav_desktop != st.session_state.page:
    st.session_state.page = nav_desktop
    st.rerun()
elif nav_mobile != st.session_state.page:
    st.session_state.page = nav_mobile
    st.rerun()

# Use 'selected' for the rest of the app
selected = st.session_state.page

if selected != "Projects":
    st.session_state.selected_project = None

# ==========================================
# 5. PAGE CONTENT
# ==========================================

# --- HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    
    # Admin Edit
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Profile"):
            st.session_state.data['profile']['name'] = st.text_input("Name", prof.get('name'))
            st.session_state.data['profile']['role'] = st.text_input("Role", prof.get('role'))
            st.session_state.data['profile']['summary'] = st.text_area("Summary", prof.get('summary'))
            
    c1, c2 = st.columns([2, 1])
    with c1:
        st.title(prof.get('name', 'Name'))
        st.subheader(prof.get('role', 'Role'))
        st.write(prof.get('summary', ''))
        
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><h2 style="color:#3B82F6">{mets.get("dashboards","0")}</h2><small>Dashboards</small></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><h2 style="color:#3B82F6">{mets.get("manual_reduction","0")}</h2><small>Reduction</small></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><h2 style="color:#3B82F6">{mets.get("efficiency","0")}</h2><small>Efficiency</small></div>', unsafe_allow_html=True)

# --- PROJECTS ---
elif selected == "Projects":
    projects = st.session_state.data.get('projects', [])

    # 1. ADMIN MODE
    if st.session_state.is_admin:
        with st.expander("➕ Add / Edit Projects"):
            # Simple add form
            with st.form("new_proj"):
                st.subheader("Add New Project")
                t = st.text_input("Title")
                c = st.text_input("Category")
                i = st.text_input("Image URL")
                prob = st.text_area("Problem")
                sol = st.text_area("Solution")
                imp = st.text_area("Impact")
                det = st.text_area("Details")
                if st.form_submit_button("Create Project"):
                    projects.append({"title":t, "category":c, "image":i, "problem":prob, "solution":sol, "impact":imp, "details":det})
                    st.rerun()

    # 2. DETAIL VIEW
    if st.session_state.selected_project is not None:
        idx = st.session_state.selected_project
        if idx < len(projects):
            p = projects[idx]
            if st.button("← Back to List"):
                st.session_state.selected_project = None
                st.rerun()
            
            st.title(p.get('title'))
            st.caption(p.get('category'))
            
            # Image
            st.image(get_img_src(p.get('image')), use_container_width=True)
            
            # Description
            st.markdown("### About")
            st.write(p.get('details'))
            
            st.markdown("---")
            
            # --- THE RESTORED PROBLEM/SOLUTION/IMPACT BOXES ---
            html_boxes = f"""
            <div class="detail-row">
                <div class="detail-box d-blue">
                    <div class="box-title">🚨 Problem</div>
                    {p.get('problem')}
                </div>
                <div class="detail-box d-green">
                    <div class="box-title">💡 Solution</div>
                    {p.get('solution')}
                </div>
                <div class="detail-box d-yellow">
                    <div class="box-title">🚀 Impact</div>
                    {p.get('impact')}
                </div>
            </div>
            """
            st.markdown(html_boxes, unsafe_allow_html=True)
            
        else:
            st.session_state.selected_project = None
            st.rerun()

    # 3. LIST VIEW
    else:
        st.title("Projects")
        
        # Filter
        cats = sorted(list(set([p.get('category', 'Other') for p in projects])))
        sel_cat = st.selectbox("Category", ["All"] + cats)
        
        filtered = projects if sel_cat == "All" else [p for p in projects if p.get('category') == sel_cat]
        
        # Render Grid (2 columns on desktop, auto-stack on mobile)
        for i in range(0, len(filtered), 2):
            cols = st.columns(2)
            batch = filtered[i:i+2]
            for j, p in enumerate(batch):
                actual_idx = projects.index(p)
                with cols[j]:
                    st.markdown(f"""
                    <div class="project-card">
                        <div style="font-weight:bold; font-size:1.2rem; margin-bottom:5px;">{p.get('title')}</div>
                        <div style="font-size:0.9rem; opacity:0.8; margin-bottom:15px;">{p.get('category')}</div>
                        <img src="{get_img_src(p.get('image'))}" style="width:100%; height:150px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
                        <div style="font-size:0.85rem; margin-bottom:15px;">{p.get('problem')[:100]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Button must be outside HTML block to work
                    if st.button(f"View Details", key=f"btn_{actual_idx}"):
                        st.session_state.selected_project = actual_idx
                        st.rerun()

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    
    # Admin Edit
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Skills"):
            data_list = [{"Skill":k, "Value":v} for k,v in skills.items()]
            edited = st.data_editor(data_list, num_rows="dynamic")
            st.session_state.data['skills'] = {r['Skill']: int(r['Value']) for r in edited if r['Skill']}

    if skills:
        col1, col2 = st.columns([1, 1])
        with col1:
            # Radar Chart
            fig = go.Figure(go.Scatterpolar(
                r=list(skills.values()), theta=list(skills.keys()), fill='toself',
                line=dict(color='#3B82F6'), marker=dict(color='#3B82F6')
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,100], showticklabels=False), bgcolor='rgba(0,0,0,0)'),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20), height=350, showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            st.subheader("Proficiency Levels")
            for s, v in skills.items():
                st.markdown(f"**{s}**")
                st.progress(v)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    exp = st.session_state.data.get('experience', [])
    
    if st.session_state.is_admin:
        with st.expander("➕ Add Experience"):
            with st.form("add_exp"):
                r = st.text_input("Role")
                c = st.text_input("Company")
                d = st.text_input("Date")
                desc = st.text_area("Description")
                if st.form_submit_button("Add"):
                    exp.insert(0, {"role":r, "company":c, "date":d, "description":desc})
                    st.rerun()
            if st.button("Clear Last Entry"):
                if exp: exp.pop(0)
                st.rerun()

    for job in exp:
        st.markdown(f"""
        <div class="timeline-card">
            <div style="font-size:1.1rem; font-weight:bold;">{job.get('role')}</div>
            <div style="color:#3B82F6; font-weight:600;">{job.get('company')}</div>
            <div style="font-size:0.85rem; opacity:0.7; margin-bottom:10px;">{job.get('date')}</div>
            <div>{job.get('description')}</div>
        </div>
        """, unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    
    # Grid
    c1, c2 = st.columns(2)
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i%2==0 else c2):
            st.markdown(f"""
            <a href="{item.get('value')}" style="text-decoration:none;">
                <div class="metric-card">
                    <img src="{item.get('icon')}" width="30">
                    <div style="color:var(--text-color); margin-top:5px;">{item.get('label')}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

    # MOBILE ADMIN ACCESS (Since sidebar is hidden on mobile)
    st.markdown("---")
    st.caption("Admin Access")
    if not st.session_state.is_admin:
        with st.form("mobile_login"):
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Unlock"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
    else:
        st.success("Admin Active")
        if st.button("Logout", key="mob_logout"):
            st.session_state.is_admin = False
            st.rerun()
