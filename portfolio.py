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
            "profile": {"name": "Your Name", "role": "Data Analyst", "summary": "Summary here", "image_url": "", "contact_info": []},
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
    if not image_path: return "https://placehold.co/400x400/png?text=Me"
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return image_path

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'mobile_page' not in st.session_state: st.session_state.mobile_page = "Home"

# ==========================================
# 3. CSS (FIXED TOOLTIPS & LAYOUT)
# ==========================================
st.markdown("""
<style>
    /* GLOBAL THEME */
    .main { padding-top: 1rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: var(--text-color) !important; }
    p, div, span { color: var(--text-color); }
    
    /* REMOVE DEFAULT STREAMLIT PADDING/MARGINS THAT INTERFERE */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    
    /* =========================================
       LAYOUT TOGGLING
       ========================================= */
    .desktop-view { display: block; }
    .mobile-view { display: none !important; }

    @media (max-width: 800px) {
        .desktop-view { display: none !important; }
        .mobile-view { display: block !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        div[data-testid="collapsedControl"] { display: none !important; }
    }

    /* =========================================
       DESKTOP STYLES
       ========================================= */
    
    /* 1. METRIC CARDS & TOOLTIPS (FIXED OVERFLOW) */
    /* We must allow overflow on the Streamlit columns for tooltips to popup correctly */
    div[data-testid="column"] { overflow: visible !important; }
    
    .metric-card { 
        background: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px; 
        padding: 20px; 
        text-align: center; 
        position: relative;
        transition: transform 0.3s ease;
        z-index: 1;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #3B82F6; z-index: 100; }
    
    .tooltip-text { 
        visibility: hidden; 
        width: 220px; 
        background-color: #262730; 
        color: #fff; 
        text-align: left; 
        border-radius: 8px; 
        padding: 12px; 
        position: absolute; 
        z-index: 9999; 
        bottom: 115%; 
        left: 50%; 
        transform: translateX(-50%);
        opacity: 0; 
        transition: opacity 0.2s;
        font-size: 0.8rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #3B82F6;
        pointer-events: none;
    }
    .metric-card:hover .tooltip-text { visibility: visible; opacity: 1; }

    /* 2. PROJECT CARDS (ORIGINAL LOOK) */
    .project-card {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex; flex-direction: column; height: 100%; 
        min-height: 520px; /* Taller to fit P/S/I */
        position: relative;
    }
    .p-img-container { width: 100%; height: 180px; overflow: hidden; border-radius: 10px; margin-bottom: 15px; flex-shrink: 0; }
    .p-img { width: 100%; height: 100%; object-fit: cover; }
    .p-cat-overlay {
        position: absolute; top: 30px; left: 30px;
        background-color: var(--background-color); color: #3B82F6; padding: 4px 10px; border-radius: 15px;
        font-size: 0.7rem; font-weight: 800; text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .p-section { margin-top: 10px; font-size: 0.85rem; line-height: 1.4; }
    .p-label { font-weight: 700; color: #3B82F6; margin-right: 5px; display: inline-block; }

    /* =========================================
       MOBILE STYLES
       ========================================= */
    .mobile-header { 
        position: sticky; top: 0; z-index: 500; 
        background: var(--background-color); 
        padding: 15px 5px; 
        border-bottom: 1px solid rgba(128,128,128,0.1); 
        display: flex; align-items: center; justify-content: space-between; 
        margin-bottom: 20px; 
    }
    .mobile-profile-pic { 
        width: 50px; height: 50px; border-radius: 50%; object-fit: cover; 
        border: 2px solid #3B82F6; 
        background-color: #333; /* Fallback color */
    }
    .mobile-card { 
        background: var(--secondary-background-color); 
        border-radius: 12px; padding: 15px; margin-bottom: 15px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border: 1px solid rgba(128,128,128,0.1);
    }
    .m-p-label { font-weight: 700; color: #3B82F6; font-size: 0.8rem; margin-top: 8px; }
    .m-p-text { font-size: 0.85rem; opacity: 0.9; margin-bottom: 5px; line-height: 1.4; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DESKTOP VIEW
# ==========================================
st.markdown('<div class="desktop-view">', unsafe_allow_html=True)

# --- SIDEBAR: THE ONLY NAVIGATION & ADMIN ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    if prof.get('image_url'):
        st.image(get_img_src(prof.get('image_url')), width=130)
    
    # SINGLE NAVIGATION SOURCE
    selected = option_menu(
        menu_title=None,
        options=["Home", "Projects", "Experience", "Skills", "Contact"], 
        icons=["house", "rocket", "briefcase", "cpu", "envelope"], 
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#3B82F6"}}
    )
    
    st.markdown("---")
    
    # SINGLE ADMIN SOURCE (Bottom of Sidebar)
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin"):
            with st.form("sidebar_admin_auth"):
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    if password == ADMIN_PASSWORD:
                        st.session_state.is_admin = True
                        st.rerun()
    else:
        st.success("Admin Mode")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- DESKTOP CONTENT ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6 !important;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        
        # Tooltip Content
        tt_dash = "<b>Projects:</b><br>• 10+ dashboards<br>• KPI variance analysis"
        tt_red = "<b>Impact:</b><br>• Saved 20 hrs/week<br>• 90% error reduction"
        tt_eff = "<b>Gains:</b><br>• Real-time data<br>• Faster decisions"

        mc1, mc2, mc3 = st.columns(3)
        with mc1: 
            st.markdown(f'''
            <div class="metric-card">
                <div class="tooltip-text">{tt_dash}</div>
                <div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("dashboards","0")}</div>
                <div style="font-size:0.8rem; opacity:0.7;">DASHBOARDS</div>
            </div>''', unsafe_allow_html=True)
        with mc2: 
            st.markdown(f'''
            <div class="metric-card">
                <div class="tooltip-text">{tt_red}</div>
                <div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("manual_reduction","0%")}</div>
                <div style="font-size:0.8rem; opacity:0.7;">REDUCTION</div>
            </div>''', unsafe_allow_html=True)
        with mc3: 
            st.markdown(f'''
            <div class="metric-card">
                <div class="tooltip-text">{tt_eff}</div>
                <div style="font-size:1.8rem; font-weight:800; color:#3B82F6;">{mets.get("efficiency","0%")}</div>
                <div style="font-size:0.8rem; opacity:0.7;">EFFICIENCY</div>
            </div>''', unsafe_allow_html=True)

elif selected == "Projects":
    st.title("Projects")
    projects = st.session_state.data.get('projects', [])
    
    # Using columns for grid layout
    for i in range(0, len(projects), 2):
        cols = st.columns(2)
        batch = projects[i : i+2]
        for j, p in enumerate(batch):
            with cols[j]:
                img_src = get_img_src(p.get('image', ''))
                # Explicitly rendering Problem/Solution/Impact in the card
                st.markdown(f"""
                    <div class="project-card">
                        <div class="p-cat-overlay">{p.get('category')}</div>
                        <div class="p-img-container"><img src="{img_src}" class="p-img"></div>
                        <div style="font-size:1.2rem; font-weight:700; margin-bottom:10px;">{p.get('title')}</div>
                        
                        <div class="p-section"><span class="p-label">🚨 Problem:</span>{p.get('problem')}</div>
                        <div class="p-section"><span class="p-label">💡 Solution:</span>{p.get('solution')}</div>
                        <div class="p-section"><span class="p-label">🚀 Impact:</span>{p.get('impact')}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div style="background:var(--secondary-background-color); padding:20px; border-radius:10px; border-left:5px solid #3B82F6; margin-bottom:15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="font-weight:bold; font-size:1.1rem;">{job.get("role")} @ {job.get("company")}</div>
            <small style="opacity:0.7;">{job.get("date")}</small>
            <div style="margin-top:10px; line-height:1.6;">{job.get("description")}</div>
        </div>""", unsafe_allow_html=True)

elif selected == "Skills":
    st.title("Skills")
    skills = st.session_state.data.get('skills', {})
    if skills:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            # STATIC CHART + CUSTOM HOVER
            fig = go.Figure(go.Scatterpolar(
                r=list(skills.values()), 
                theta=list(skills.keys()), 
                fill='toself',
                hovertemplate='I am %{r}% proficient in %{theta}<extra></extra>' # Custom Tooltip
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False, 
                height=400, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                dragmode=False # Static
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False}) # staticPlot=False to allow hover
    
    st.markdown("### Proficiency")
    s_cols = st.columns(4)
    for i, (s, v) in enumerate(skills.items()):
        with s_cols[i % 4]:
            # Skill % Visible
            st.markdown(f"""
            <div style="background:var(--secondary-background-color); padding:15px; border-radius:8px; margin-bottom:10px; text-align:center;">
                <b>{s}</b>
                <div style="color:#3B82F6; font-size:1.2rem; font-weight:800;">{v}%</div>
                <progress value="{v}" max="100" style="width:100%; height:6px;"></progress>
            </div>""", unsafe_allow_html=True)

elif selected == "Contact":
    st.title("Contact")
    for item in st.session_state.data.get('profile', {}).get('contact_info', []):
        st.markdown(f'<div class="metric-card"><b>{item.get("label")}</b>: <a href="{item.get("value")}">{item.get("value")}</a></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # END DESKTOP

# ==========================================
# 5. MOBILE VIEW
# ==========================================
st.markdown('<div class="mobile-view">', unsafe_allow_html=True)

# 1. MOBILE HEADER (Photo Fix)
prof = st.session_state.data.get('profile', {})
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

# 2. MOBILE CONTENT
if st.session_state.mobile_page == "Home":
    st.markdown(f"#### 👋 Hi, I'm {prof.get('name').split(' ')[0]}")
    st.write(prof.get('summary'))
    
    # Metrics
    mets = st.session_state.data.get('metrics', {})
    metrics_data = [("📊", mets.get("dashboards"), "Dashboards"), ("⚡", mets.get("manual_reduction"), "Reduction"), ("📈", mets.get("efficiency"), "Efficiency")]
    
    st.markdown("<div style='display:flex; gap:10px; overflow-x:auto; padding-bottom:10px;'>", unsafe_allow_html=True)
    for icon, val, lbl in metrics_data:
        st.markdown(f"""
        <div style="background:var(--secondary-background-color); padding:10px; border-radius:10px; min-width:100px; text-align:center;">
            <div style="font-size:1.5rem;">{icon}</div>
            <div style="font-weight:bold; color:#3B82F6;">{val}</div>
            <div style="font-size:0.7rem;">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Skills Summary on Mobile Home
    st.markdown("### Top Skills")
    skills = st.session_state.data.get('skills', {})
    skill_html = "<div style='display:flex; flex-wrap:wrap; gap:8px;'>"
    for s, v in skills.items():
        skill_html += f"<span style='background:rgba(59,130,246,0.1); color:#3B82F6; padding:5px 10px; border-radius:15px; font-size:0.8rem; font-weight:600;'>{s} {v}%</span>"
    skill_html += "</div>"
    st.markdown(skill_html, unsafe_allow_html=True)

elif st.session_state.mobile_page == "Projects":
    st.markdown("### Projects")
    for p in st.session_state.data.get('projects', []):
        img = get_img_src(p.get('image'))
        # Added P/S/I VISIBILITY
        st.markdown(f"""
        <div class="mobile-card">
            <img src="{img}" style="width:100%; height:140px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
            <div style="font-weight:800; font-size:1.1rem; margin-bottom:5px;">{p.get('title')}</div>
            <div style="font-size:0.75rem; color:#3B82F6; margin-bottom:10px; text-transform:uppercase;">{p.get('category')}</div>
            
            <div class="m-p-label">🚨 Problem</div>
            <div class="m-p-text">{p.get('problem')}</div>
            
            <div class="m-p-label">💡 Solution</div>
            <div class="m-p-text">{p.get('solution')}</div>
            
            <div class="m-p-label">🚀 Impact</div>
            <div class="m-p-text">{p.get('impact')}</div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.mobile_page == "Experience":
    st.markdown("### Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="mobile-card" style="border-left: 4px solid #3B82F6;">
            <div style="font-weight:700;">{job.get('role')}</div>
            <div style="font-size:0.9rem; opacity:0.8;">{job.get('company')}</div>
            <div style="font-size:0.75rem; opacity:0.6; margin-bottom:8px;">{job.get('date')}</div>
            <div style="font-size:0.85rem;">{job.get('description')}</div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.mobile_page == "Contact":
    st.markdown("### Contact")
    for item in st.session_state.data.get('profile', {}).get('contact_info', []):
        st.markdown(f"""
        <div class="mobile-card" style="display:flex; align-items:center; gap:10px;">
            <div style="font-size:1.2rem;">📬</div>
            <div>
                <div style="font-weight:600;">{item.get('label')}</div>
                <div style="font-size:0.8rem; opacity:0.8;">{item.get('value')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 3. MOBILE NAVIGATION BUTTONS
st.markdown("---")
mc1, mc2, mc3, mc4 = st.columns(4)
def m_btn(lbl, key):
    if st.button(lbl, key=f"mob_{key}", use_container_width=True):
        st.session_state.mobile_page = key
        st.rerun()

with mc1: m_btn("🏠", "Home")
with mc2: m_btn("🚀", "Projects")
with mc3: m_btn("💼", "Experience")
with mc4: m_btn("📬", "Contact")

st.markdown('</div>', unsafe_allow_html=True)
