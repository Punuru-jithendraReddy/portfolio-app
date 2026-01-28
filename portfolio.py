import streamlit as st
import json
import os
import requests
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# ==========================================
# 1. SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ADMIN_PASSWORD = "admin" 

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="🧑‍💻")

# ==========================================
# 2. DATA FUNCTIONS
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

def get_img_src(image_path):
    # FORCE A FALLBACK IMAGE IF EMPTY
    if not image_path: return "https://placehold.co/400x400/png?text=Me"
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return image_path

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'mobile_page' not in st.session_state: st.session_state.mobile_page = "Home"

# ==========================================
# 3. CSS (STRICT LAYOUT CONTROL)
# ==========================================
st.markdown("""
<style>
    /* 1. HIDE DEFAULT STREAMLIT ELEMENTS THAT CAUSE CLUTTER */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* 2. LAYOUT SWITCHER */
    .desktop-layout { display: block; }
    .mobile-layout { display: none !important; }
    
    @media (max-width: 800px) {
        .desktop-layout { display: none !important; }
        .mobile-layout { display: block !important; }
        
        /* FORCE HIDE SIDEBAR ON MOBILE */
        section[data-testid="stSidebar"] { display: none !important; }
        div[data-testid="collapsedControl"] { display: none !important; }
    }

    /* 3. CARD STYLES */
    .metric-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .project-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* 4. MOBILE SPECIFIC */
    .mobile-header {
        position: sticky; top: 0; z-index: 999;
        background: var(--background-color);
        padding: 10px 0;
        border-bottom: 1px solid rgba(128,128,128,0.1);
        display: flex; align-items: center; justify-content: space-between;
    }
    .mobile-profile-pic {
        width: 50px; height: 50px; border-radius: 50%; object-fit: cover;
        border: 2px solid #3B82F6;
    }
    
    /* 5. TOOLTIP FIX */
    .tooltip-container {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.8rem;
    }
    .tooltip-container:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DESKTOP VIEW
# ==========================================
st.markdown('<div class="desktop-layout">', unsafe_allow_html=True)

# --- SIDEBAR (THE ONLY NAVIGATION) ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    if prof.get('image_url'):
        st.image(get_img_src(prof.get('image_url')), width=130)
    
    # 1. NAVIGATION
    selected = option_menu(
        menu_title=None, # Title hidden to save space
        options=["Home", "Projects", "Experience", "Skills", "Contact"], 
        icons=["house", "rocket", "briefcase", "cpu", "envelope"], 
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#3B82F6"}}
    )
    
    st.markdown("---")
    
    # 2. ADMIN (THE ONLY ADMIN PANEL)
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Login"):
            password = st.text_input("Password", type="password", key="sidebar_pw")
            if st.button("Login", key="sidebar_login_btn"):
                if password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
    else:
        st.success("Logged In")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- CONTENT ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})

    c1, c2 = st.columns([2, 1])
    with c1:
        st.title(prof.get('name', 'Name'))
        st.markdown(f"### {prof.get('role', 'Role')}")
        st.write(prof.get('summary', ''))
        
        st.markdown("---")
        
        # METRICS WITH TOOLTIPS
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="tooltip-container">
                <div class="metric-card">
                    <h2 style="color:#3B82F6; margin:0;">{mets.get('dashboards')}</h2>
                    <small>Dashboards</small>
                </div>
                <span class="tooltip-text"><b>Key Projects:</b><br>10+ dashboards supporting data-driven decisions</span>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="tooltip-container">
                <div class="metric-card">
                    <h2 style="color:#3B82F6; margin:0;">{mets.get('manual_reduction')}</h2>
                    <small>Reduction</small>
                </div>
                <span class="tooltip-text"><b>Impact:</b><br>Automated 15+ manual reports, saved 20 hrs/week</span>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="tooltip-container">
                <div class="metric-card">
                    <h2 style="color:#3B82F6; margin:0;">{mets.get('efficiency')}</h2>
                    <small>Efficiency</small>
                </div>
                <span class="tooltip-text"><b>Gains:</b><br>Faster decision making & real-time access</span>
            </div>
            """, unsafe_allow_html=True)

elif selected == "Projects":
    st.title("Projects")
    projects = st.session_state.data.get('projects', [])
    
    for i in range(0, len(projects), 2):
        cols = st.columns(2)
        batch = projects[i : i+2]
        for j, p in enumerate(batch):
            with cols[j]:
                img_src = get_img_src(p.get('image', ''))
                # PLAIN HTML FOR ROBUSTNESS
                st.markdown(f"""
                <div class="project-card">
                    <img src="{img_src}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                    <h3 style="margin-top:10px;">{p.get('title')}</h3>
                    <p style="color:#3B82F6; font-size:0.8rem; text-transform:uppercase; font-weight:bold;">{p.get('category')}</p>
                    <hr style="margin:10px 0;">
                    <p><b>🚨 Problem:</b> {p.get('problem')}</p>
                    <p><b>💡 Solution:</b> {p.get('solution')}</p>
                    <p><b>🚀 Impact:</b> {p.get('impact')}</p>
                </div>
                """, unsafe_allow_html=True)

elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div style="padding:20px; background:var(--secondary-background-color); border-radius:10px; border-left: 5px solid #3B82F6; margin-bottom:15px;">
            <h4>{job.get('role')} @ {job.get('company')}</h4>
            <small>{job.get('date')}</small>
            <p style="margin-top:10px;">{job.get('description')}</p>
        </div>
        """, unsafe_allow_html=True)

elif selected == "Skills":
    st.title("Skills")
    skills = st.session_state.data.get('skills', {})
    
    if skills:
        col_chart, col_list = st.columns([1.5, 1])
        with col_chart:
            # SPIDER CHART - STATIC BUT INTERACTIVE TOOLTIP
            fig = go.Figure(go.Scatterpolar(
                r=list(skills.values()),
                theta=list(skills.keys()),
                fill='toself',
                name='Skills',
                hovertemplate='I am <b>%{r}%</b> proficient in <b>%{theta}</b><extra></extra>' # THE REQUESTED TOOLTIP
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                dragmode=False, # STATIC: Cannot drag/pan
                height=400,
                margin=dict(t=20, b=20, l=40, r=40)
            )
            # config={'staticPlot': False} ensures hover works even if drag is disabled
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
            
        with col_list:
            st.markdown("### Proficiency Levels")
            for s, v in skills.items():
                st.caption(f"{s} ({v}%)")
                st.progress(v)

elif selected == "Contact":
    st.title("Contact")
    for item in st.session_state.data.get('profile', {}).get('contact_info', []):
        st.info(f"**{item.get('label')}**: {item.get('value')}", icon="📬")

st.markdown('</div>', unsafe_allow_html=True) # END DESKTOP

# ==========================================
# 5. MOBILE VIEW
# ==========================================
st.markdown('<div class="mobile-layout">', unsafe_allow_html=True)

# 1. MOBILE HEADER (Photo Fix)
prof = st.session_state.data.get('profile', {})
img_src = get_img_src(prof.get('image_url'))

st.markdown(f"""
<div class="mobile-header">
    <div>
        <div style="font-weight: 800; font-size: 1.2rem;">{prof.get('name', 'Portfolio')}</div>
        <div style="font-size: 0.8rem; opacity: 0.7;">{prof.get('role', 'Analyst')}</div>
    </div>
    <img src="{img_src}" class="mobile-profile-pic">
</div>
""", unsafe_allow_html=True)

# 2. MOBILE CONTENT
if st.session_state.mobile_page == "Home":
    st.write(prof.get('summary'))
    
    st.markdown("### Key Metrics")
    mets = st.session_state.data.get('metrics', {})
    m_cols = st.columns(3)
    with m_cols[0]: st.metric("Dashboards", mets.get('dashboards'))
    with m_cols[1]: st.metric("Reduction", mets.get('manual_reduction'))
    with m_cols[2]: st.metric("Efficiency", mets.get('efficiency'))
    
    st.markdown("### Top Skills")
    skills = st.session_state.data.get('skills', {})
    for s, v in list(skills.items())[:4]: # Show top 4
        st.caption(f"{s} - {v}%")
        st.progress(v)

elif st.session_state.mobile_page == "Projects":
    st.markdown("### Projects")
    for p in st.session_state.data.get('projects', []):
        img = get_img_src(p.get('image'))
        st.markdown(f"""
        <div class="project-card">
            <img src="{img}" style="width:100%; height:150px; object-fit:cover; border-radius:10px;">
            <h4 style="margin:10px 0;">{p.get('title')}</h4>
            <p style="font-size:0.8rem; color:#3B82F6;">{p.get('category')}</p>
            <div style="font-size:0.85rem; margin-top:10px;">
                <p><b>🚨 Problem:</b> {p.get('problem')}</p>
                <p><b>💡 Solution:</b> {p.get('solution')}</p>
                <p><b>🚀 Impact:</b> {p.get('impact')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.mobile_page == "Experience":
    st.markdown("### Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="project-card" style="border-left: 5px solid #3B82F6;">
            <b>{job.get('role')}</b>
            <div style="font-size:0.8rem; opacity:0.8;">{job.get('company')} | {job.get('date')}</div>
            <p style="font-size:0.9rem; margin-top:5px;">{job.get('description')}</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.mobile_page == "Contact":
    st.markdown("### Contact")
    for item in st.session_state.data.get('profile', {}).get('contact_info', []):
        st.info(f"{item.get('label')}: {item.get('value')}")

# 3. MOBILE NAV (BOTTOM)
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
if c1.button("🏠", use_container_width=True): st.session_state.mobile_page = "Home"; st.rerun()
if c2.button("🚀", use_container_width=True): st.session_state.mobile_page = "Projects"; st.rerun()
if c3.button("💼", use_container_width=True): st.session_state.mobile_page = "Experience"; st.rerun()
if c4.button("📬", use_container_width=True): st.session_state.mobile_page = "Contact"; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
