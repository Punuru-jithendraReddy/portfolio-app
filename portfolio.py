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

st.set_page_config(
    layout="wide", 
    page_title="Portfolio", 
    page_icon="✨",
    initial_sidebar_state="expanded" 
)

# Initialize Page State if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Helper to update page from callbacks
def set_page(page_name):
    st.session_state.current_page = page_name

# ==========================================
# 2. CSS: DUAL LAYOUT ENGINE (DESKTOP VS MOBILE)
# ==========================================
st.markdown("""
<style>
    /* --- GENERAL THEME --- */
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: var(--text-color) !important; }
    
    /* --- 1. DESKTOP MODE (Default) --- */
    /* Hide the mobile bottom nav by default */
    .mobile-nav-container { display: none !important; }
    
    /* --- 2. MOBILE MODE (Triggered on small screens) --- */
    @media (max-width: 768px) {
        
        /* HIDE SIDEBAR COMPLETELY */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* SHOW BOTTOM NAV */
        .mobile-nav-container {
            display: block !important;
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: var(--secondary-background-color);
            z-index: 99999;
            border-top: 1px solid rgba(128,128,128,0.2);
            padding-bottom: 5px; /* Safety padding for iPhone home bar */
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }

        /* ADJUST CONTENT PADDING so it doesn't get hidden behind bottom bar */
        .block-container {
            padding-bottom: 100px !important;
            padding-top: 2rem !important;
        }

        /* Adjust Header for Mobile */
        h1 { font-size: 2.2rem !important; }
        
        /* Make cards full width on mobile */
        div[data-testid="column"] { width: 100% !important; flex: 1 1 auto !important; }
    }

    /* --- COMPONENT STYLING (Shared) --- */
    
    /* Project Cards */
    .project-card {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px; 
        transition: transform 0.2s;
    }
    
    /* Images */
    .p-img-container { 
        width: 100%; height: 180px; overflow: hidden; 
        border-radius: 10px; margin-bottom: 15px; 
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    
    /* Timeline & Metrics */
    .timeline-card {
        background: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 20px; margin-bottom: 15px; border-left: 5px solid #3B82F6;
    }
    .metric-card {
        background: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 15px; text-align: center; margin-bottom: 10px;
    }

    /* Remove Streamlit default excessive margins */
    .stMarkdown { margin-bottom: 0px !important; }
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
    return image_path

def render_image(image_path, width=None):
    src = get_img_src(image_path)
    if width: st.image(src, width=width)
    else: st.image(src, use_container_width=True)

# Initialize Session
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_project' not in st.session_state: st.session_state.selected_project = None

# ==========================================
# 4. NAVIGATION LOGIC (THE SPLIT)
# ==========================================
menu_options = ["Home", "Experience", "Projects", "Skills", "Contact"]
menu_icons = ["house", "briefcase", "rocket", "cpu", "envelope"]

# --- A. DESKTOP SIDEBAR (Visible on Desktop, Hidden on Mobile via CSS) ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    if prof.get('image_url'):
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="{get_img_src(prof.get('image_url'))}" style="width: 140px; border-radius: 10px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </div>
        """, unsafe_allow_html=True)
    
    # We use a key to sync this, but manual handling prevents loop issues
    desktop_selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        default_index=menu_options.index(st.session_state.current_page),
        styles={"nav-link-selected": {"background-color": "#3B82F6"}},
        key="desktop_nav"
    )

    # Admin Panel (Desktop Only Location)
    st.markdown('<div style="height: 1px; background-color: rgba(128,128,128,0.2); margin: 20px 0;"></div>', unsafe_allow_html=True)
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Access"):
            with st.form("admin_auth_desktop"):
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    if password == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error("Incorrect password")
    else:
        st.success("Admin Active")
        json_string = json.dumps(st.session_state.data, indent=4)
        st.download_button("💾 Backup Data", data=json_string, file_name="data.json", mime="application/json")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- B. MOBILE BOTTOM BAR (Visible on Mobile, Hidden on Desktop via CSS) ---
# We render this container at the bottom using the CSS class .mobile-nav-container
st.markdown('<div class="mobile-nav-container">', unsafe_allow_html=True)
mobile_selected = option_menu(
    menu_title=None,
    options=menu_options,
    icons=menu_icons,
    default_index=menu_options.index(st.session_state.current_page),
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"font-size": "14px"}, 
        "nav-link": {"font-size": "10px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#3B82F6"},
    },
    key="mobile_nav"
)
st.markdown('</div>', unsafe_allow_html=True)

# --- SYNC LOGIC ---
# Determine which nav triggered the change and update the Master Page State
if desktop_selected != st.session_state.current_page:
    st.session_state.current_page = desktop_selected
    st.rerun()
elif mobile_selected != st.session_state.current_page:
    st.session_state.current_page = mobile_selected
    st.rerun()

# Set the active variable for the rest of the script
selected = st.session_state.current_page

if selected != "Projects":
    st.session_state.selected_project = None

# ==========================================
# 5. PAGE: HOME
# ==========================================
if selected == "Home":
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Home Page Details"):
            st.session_state.data['profile']['name'] = st.text_input("Name", st.session_state.data['profile'].get('name', ''))
            st.session_state.data['profile']['role'] = st.text_input("Role", st.session_state.data['profile'].get('role', ''))
            st.session_state.data['profile']['summary'] = st.text_area("Summary", st.session_state.data['profile'].get('summary', ''))
            st.session_state.data['profile']['image_url'] = st.text_input("Profile Image URL", st.session_state.data['profile'].get('image_url', ''))
            
            c1, c2, c3 = st.columns(3)
            with c1: st.session_state.data['metrics']['dashboards'] = st.text_input("Metric 1", st.session_state.data['metrics'].get('dashboards', ''))
            with c2: st.session_state.data['metrics']['manual_reduction'] = st.text_input("Metric 2", st.session_state.data['metrics'].get('manual_reduction', ''))
            with c3: st.session_state.data['metrics']['efficiency'] = st.text_input("Metric 3", st.session_state.data['metrics'].get('efficiency', ''))

    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})

    # Use cols for layout, but they stack on mobile due to width:100% CSS
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1 style='margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6 !important; margin-top:0;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        
        st.markdown("<br>", unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns(3)
        
        with mc1: 
            st.markdown(f'''<div class="metric-card"><div style="font-size:1.5rem; font-weight:800; color:#3B82F6;">{mets.get("dashboards","0")}</div><div style="font-size:0.8rem; opacity:0.7;">DASHBOARDS</div></div>''', unsafe_allow_html=True)
        with mc2: 
            st.markdown(f'''<div class="metric-card"><div style="font-size:1.5rem; font-weight:800; color:#3B82F6;">{mets.get("manual_reduction","0%")}</div><div style="font-size:0.8rem; opacity:0.7;">REDUCTION</div></div>''', unsafe_allow_html=True)
        with mc3: 
            st.markdown(f'''<div class="metric-card"><div style="font-size:1.5rem; font-weight:800; color:#3B82F6;">{mets.get("efficiency","0%")}</div><div style="font-size:0.8rem; opacity:0.7;">EFFICIENCY</div></div>''', unsafe_allow_html=True)

    with c2: 
        # Only show image here on Desktop. On mobile, we might want it smaller or hidden if space is tight.
        # But for now, we render it. CSS flex-wrap will handle the stacking.
        render_image(prof.get('image_url'))

# ==========================================
# 6. PAGE: PROJECTS
# ==========================================
elif selected == "Projects":
    projects = st.session_state.data.get('projects', [])

    # ADMIN: ADD/EDIT
    if st.session_state.is_admin:
        with st.expander("✏️ Manage Projects"):
            project_titles = [p.get('title', 'Untitled') for p in projects]
            project_titles.insert(0, "➕ Add New Project")
            selected_proj = st.selectbox("Select Project", project_titles)
            
            if selected_proj == "➕ Add New Project":
                with st.form("add_proj"):
                    new_title = st.text_input("Title")
                    new_cat = st.text_input("Category")
                    new_img = st.text_input("Image URL")
                    new_prob = st.text_area("Problem")
                    new_sol = st.text_area("Solution")
                    new_imp = st.text_area("Impact")
                    new_det = st.text_area("Details")
                    if st.form_submit_button("Add Project"):
                        st.session_state.data['projects'].append({
                            "title": new_title, "category": new_cat, "image": new_img,
                            "problem": new_prob, "solution": new_sol, "impact": new_imp, "details": new_det
                        })
                        st.rerun()
            else:
                idx = project_titles.index(selected_proj) - 1
                proj = projects[idx]
                with st.form(f"edit_proj_{idx}"):
                    proj['title'] = st.text_input("Title", proj.get('title'))
                    proj['category'] = st.text_input("Category", proj.get('category'))
                    proj['image'] = st.text_input("Image URL", proj.get('image'))
                    proj['problem'] = st.text_area("Problem", proj.get('problem'))
                    proj['solution'] = st.text_area("Solution", proj.get('solution'))
                    proj['impact'] = st.text_area("Impact", proj.get('impact'))
                    proj['details'] = st.text_area("Details", proj.get('details'))
                    if st.form_submit_button("Update"): st.rerun()
                    if st.form_submit_button("Delete", type="primary"):
                        st.session_state.data['projects'].pop(idx)
                        st.rerun()

    # VIEW: DETAILS OR LIST
    if st.session_state.selected_project is not None:
        # PROJECT DETAIL VIEW
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
            normalized_url = dash_img
            if normalized_url and "github.com" in normalized_url and "/blob/" in normalized_url:
                normalized_url = normalized_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

            if dash_img and dash_img.endswith('.mp4'): 
                if check_url_exists(normalized_url): st.video(normalized_url)
                else: st.image("https://placehold.co/600x400/png?text=Media+Error")
            else: 
                st.image(get_img_src(dash_img), use_container_width=True)

            st.markdown("### Details")
            st.write(p.get('details', ''))
            
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1: st.info(f"**Problem:**\n\n{p.get('problem')}")
            with c2: st.success(f"**Solution:**\n\n{p.get('solution')}")
            with c3: st.warning(f"**Impact:**\n\n{p.get('impact')}")
        else:
            st.session_state.selected_project = None
            st.rerun()
    else:
        # PROJECT LIST VIEW
        st.title("Projects")
        categories = sorted(list(set([p.get('category', 'Other') for p in projects])))
        selected_cat_filter = st.selectbox("Filter", ["All"] + categories)

        cats_to_show = categories if selected_cat_filter == "All" else [selected_cat_filter]

        for cat in cats_to_show:
            cat_projects = [p for p in projects if p.get('category', 'Other') == cat]
            if not cat_projects: continue
            
            st.subheader(cat)
            # Render rows of 2 for desktop, CSS makes them 1 for mobile
            for i in range(0, len(cat_projects), 2):
                cols = st.columns(2)
                batch = cat_projects[i : i+2]
                for j, p in enumerate(batch):
                    actual_idx = projects.index(p)
                    with cols[j]:
                        img_src = get_img_src(p.get('image', ''))
                        st.markdown(f"""
                        <div class="project-card">
                            <div class="p-img-container"><img src="{img_src}" class="p-img"></div>
                            <div style="font-weight:700; font-size:1.1rem; margin-bottom:5px;">{p.get('title')}</div>
                            <div style="font-size:0.85rem; opacity:0.8; margin-bottom:10px; line-height:1.4;">
                                {p.get('problem')[:80]}...
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"View Details", key=f"btn_{actual_idx}"):
                            st.session_state.selected_project = actual_idx
                            st.rerun()

# ==========================================
# 7. PAGE: SKILLS
# ==========================================
elif selected == "Skills":
    st.title("Skills")
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Skills"):
            skills_list = [{"Skill": k, "Value": v} for k, v in st.session_state.data.get('skills', {}).items()]
            edited_df = st.data_editor(skills_list, num_rows="dynamic")
            st.session_state.data['skills'] = {row['Skill']: int(row['Value']) for row in edited_df if row['Skill']}

    skills = st.session_state.data.get('skills', {})
    if skills:
        c1, c2 = st.columns([1, 1])
        with c1:
            # Radar Chart
            r_vals = list(skills.values())
            theta_vals = list(skills.keys())
            fig = go.Figure(go.Scatterpolar(
                r=r_vals, theta=theta_vals, fill='toself', 
                line=dict(color='#3B82F6'), marker=dict(color='#3B82F6')
            ))
            fig.update_layout(
                dragmode=False,
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False), bgcolor='rgba(0,0,0,0)'),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False, height=300, margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with c2:
            st.subheader("Proficiency")
            for s, v in skills.items():
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:600; font-size:0.9rem;">
                        <span>{s}</span><span>{v}%</span>
                    </div>
                    <div style="width:100%; background-color:rgba(128,128,128,0.2); border-radius:5px; height:8px;">
                        <div style="width:{v}%; background-color:#3B82F6; height:8px; border-radius:5px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# 8. PAGE: EXPERIENCE
# ==========================================
elif selected == "Experience":
    st.title("Experience")
    exp_list = st.session_state.data.get('experience', [])
    
    if st.session_state.is_admin:
        with st.expander("✏️ Add Experience"):
            with st.form("add_exp"):
                n_role = st.text_input("Role")
                n_comp = st.text_input("Company")
                n_date = st.text_input("Date")
                n_desc = st.text_area("Description")
                if st.form_submit_button("Add"):
                    exp_list.insert(0, {"role": n_role, "company": n_comp, "date": n_date, "description": n_desc})
                    st.rerun()
        
        # Simple list for editing/deleting existing
        for i, job in enumerate(exp_list):
            if st.button(f"🗑️ Delete {job.get('role')}", key=f"del_exp_{i}"):
                exp_list.pop(i)
                st.rerun()

    for job in exp_list:
        st.markdown(f"""
        <div class="timeline-card">
            <div style="font-weight:bold; font-size:1.1rem;">{job.get("role")}</div>
            <div style="color:#3B82F6; font-weight:600;">@{job.get("company")}</div>
            <small style="opacity:0.7;">{job.get("date")}</small>
            <div style="margin-top:10px; opacity:0.9; line-height:1.5;">{job.get("description")}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 9. PAGE: CONTACT (INCL. MOBILE ADMIN)
# ==========================================
elif selected == "Contact":
    st.title("Contact")
    prof = st.session_state.data.get('profile', {})
    
    # Contact Grid
    c1, c2 = st.columns(2)
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f'''
                <a href="{item.get("value")}" target="_blank" style="text-decoration:none;">
                <div class="metric-card">
                    <img src="{item.get("icon")}" width="30"><br>
                    <span style="color:var(--text-color); font-weight:600; font-size:0.9rem;">{item.get("label")}</span>
                </div>
                </a>
            ''', unsafe_allow_html=True)
            
    # --- MOBILE ADMIN LOGIN ACCESS ---
    # Since Sidebar is hidden on mobile, we place the Admin Login here for mobile users.
    # We use a CSS class specific for mobile to show a hint, but the form functions for everyone.
    st.markdown("---")
    st.markdown("### ⚙️ Admin Area")
    
    if not st.session_state.is_admin:
        with st.form("admin_auth_mobile"):
            password = st.text_input("Enter Admin Password", type="password")
            if st.form_submit_button("Login to Admin Mode"):
                if password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
    else:
        st.success("You are logged in as Admin")
        if st.button("Logout (Mobile)", type="primary"):
            st.session_state.is_admin = False
            st.rerun()
