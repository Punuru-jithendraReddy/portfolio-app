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
ADMIN_PASSWORD = "admin" 

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="🎨")

# --- 1. MODERN CSS STYLING ---
st.markdown("""
<style>
    /* Global Font & Spacing */
    .main { padding-top: 2rem; }
    
    /* HERO SECTION (Home) */
    .hero-name { font-size: 3rem; font-weight: 800; color: #1E293B; margin-bottom: 0; line-height: 1.2; }
    .hero-role { font-size: 1.5rem; font-weight: 500; color: #4F8BF9; margin-top: 0; margin-bottom: 1rem; }
    .hero-summary { font-size: 1.1rem; color: #475569; line-height: 1.6; }
    
    /* METRIC CARDS */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #4F8BF9; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #4F8BF9; }
    .metric-label { font-size: 0.9rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 1px; }

    /* CONTACT CARDS */
    .contact-container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 2rem; }
    .contact-btn {
        display: flex; align-items: center; justify-content: flex-start;
        background: white; border: 1px solid #E2E8F0;
        padding: 15px 25px; border-radius: 15px;
        text-decoration: none !important; color: #1E293B !important;
        width: 100%; max-width: 400px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
    }
    .contact-btn:hover { background: #F8FAFC; border-color: #4F8BF9; transform: scale(1.02); }
    .contact-icon { width: 40px; height: 40px; margin-right: 15px; object-fit: contain; }
    .contact-text h4 { margin: 0; font-size: 1rem; font-weight: 700; color: #334155; }
    .contact-text p { margin: 0; font-size: 0.9rem; color: #64748B; }

    /* PROJECT CARDS (Keeping your preferred style but cleaning it up) */
    .project-header { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; }
    
    /* SKILL BARS */
    .skill-container { margin-bottom: 15px; }
    .skill-label { font-weight: 600; margin-bottom: 5px; display: block; color: #334155; }
    .skill-bar-bg { background: #E2E8F0; border-radius: 8px; height: 10px; width: 100%; overflow: hidden; }
    .skill-bar-fill { background: linear-gradient(90deg, #4F8BF9 0%, #2563EB 100%); height: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- HELPER: DATA MANAGER ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        st.toast("Saved! Download JSON to update GitHub.", icon="💾")
    except Exception as e:
        st.error(f"Save failed: {e}")

# --- HELPER: IMAGE RENDERER ---
def render_image(image_path, width=None, style=""):
    if not image_path: return
    
    # 1. Path Logic
    if image_path.startswith("http"):
        final_path = image_path
    else:
        filename = os.path.basename(image_path)
        possible_paths = [os.path.join(BASE_DIR, "assets", filename), os.path.join(BASE_DIR, filename)]
        final_path = "https://placehold.co/600x400/png?text=Image+Missing"
        for path in possible_paths:
            if os.path.exists(path):
                final_path = path
                break
    
    # 2. Render
    if width: 
        st.image(final_path, width=width)
    else: 
        st.image(final_path, use_container_width=True)

# --- INITIALIZE ---
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    st.markdown('<div style="text-align: center; margin-bottom: 20px;">', unsafe_allow_html=True)
    # Circle mask for profile pic
    if prof.get('image_url'):
        render_image(prof.get('image_url'), width=140)
    st.markdown('</div>', unsafe_allow_html=True)
    
    selected = option_menu(None, ["Home", "Experience", "Projects", "Skills", "Contact"], 
                           icons=["house", "briefcase", "rocket", "cpu", "envelope"], default_index=0,
                           styles={
                               "nav-link-selected": {"background-color": "#4F8BF9"},
                           })
    st.markdown("---")
    
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Access"):
            if st.button("Login") and st.text_input("Password", type="password") == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
    else:
        st.success("Admin Mode")
        st.download_button("📥 Download JSON", 
                           data=json.dumps(st.session_state.data, indent=4), 
                           file_name="data.json", mime="application/json")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    
    # --- ADMIN: EDIT HOME ---
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Profile & Metrics"):
            n_name = st.text_input("Name", prof.get('name', ''))
            n_role = st.text_input("Role", prof.get('role', ''))
            n_sum = st.text_area("Summary", prof.get('summary', ''), height=150)
            n_img = st.text_input("Image URL", prof.get('image_url', ''))
            c1, c2, c3 = st.columns(3)
            m1 = c1.text_input("Dashboards", mets.get('dashboards', ''))
            m2 = c2.text_input("Reduction", mets.get('manual_reduction', ''))
            m3 = c3.text_input("Efficiency", mets.get('efficiency', ''))
            
            if st.button("Save Home Changes"):
                st.session_state.data['profile'].update({"name": n_name, "role": n_role, "summary": n_sum, "image_url": n_img})
                st.session_state.data['metrics'] = {"dashboards": m1, "manual_reduction": m2, "efficiency": m3}
                save_data(st.session_state.data)
                st.rerun()

    # --- UI: HERO SECTION ---
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown(f'<div style="padding-top: 20px;">', unsafe_allow_html=True)
        st.markdown(f'<h1 class="hero-name">{prof.get("name", "Name")}</h1>', unsafe_allow_html=True)
        st.markdown(f'<h3 class="hero-role">{prof.get("role", "Role")}</h3>', unsafe_allow_html=True)
        st.markdown(f'<p class="hero-summary">{prof.get("summary", "")}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Metrics Row
        st.markdown("<br>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{mets.get('dashboards','0')}</div>
                <div class="metric-label">Dashboards</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{mets.get('manual_reduction','0%')}</div>
                <div class="metric-label">Reduction</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{mets.get('efficiency','0%')}</div>
                <div class="metric-label">Efficiency</div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        render_image(prof.get('image_url'), width=350)
        st.markdown('</div>', unsafe_allow_html=True)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    st.markdown("---")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
        with tab_add:
            r = st.text_input("Role", key="new_r")
            c = st.text_input("Company", key="new_c")
            d = st.text_input("Date", key="new_d")
            desc = st.text_area("Description (Use • for bullets)", key="new_desc", height=200)
            if st.button("Save Job"):
                st.session_state.data.setdefault('experience', []).insert(0, {"role": r, "company": c, "date": d, "description": desc})
                save_data(st.session_state.data); st.rerun()
        with tab_edit:
            exp_list = st.session_state.data.get('experience', [])
            if exp_list:
                sel_idx = st.selectbox("Select Job", range(len(exp_list)), format_func=lambda x: f"{exp_list[x]['role']}")
                curr_job = exp_list[sel_idx]
                er = st.text_input("Role", curr_job['role'])
                ec = st.text_input("Company", curr_job['company'])
                ed = st.text_input("Date", curr_job['date'])
                edesc = st.text_area("Description", curr_job['description'], height=200)
                c1, c2 = st.columns(2)
                if c1.button("Update"):
                    st.session_state.data['experience'][sel_idx] = {"role": er, "company": ec, "date": ed, "description": edesc}
                    save_data(st.session_state.data); st.rerun()
                if c2.button("Delete", type="primary"):
                    st.session_state.data['experience'].pop(sel_idx)
                    save_data(st.session_state.data); st.rerun()

    for job in st.session_state.data.get('experience', []):
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                st.caption(job.get('date', 'Date'))
            with c2:
                st.markdown(f"### {job.get('role', 'Role')}")
                st.markdown(f"**{job.get('company', 'Company')}**")
                st.markdown(job.get('description', ''))
        st.divider()

# --- PROJECTS ---
elif selected == "Projects":
    st.title("Projects")
    st.markdown("---")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
        with tab_add:
            pt = st.text_input("Title", key="np_t")
            pc = st.text_input("Category", key="np_c")
            pi = st.text_input("Image URL", key="np_i")
            pp = st.text_area("Problem", key="np_p", height=100)
            ps = st.text_area("Solution", key="np_s", height=100)
            pimp = st.text_area("Impact", key="np_imp", height=100)
            if st.button("Save Project"):
                st.session_state.data.setdefault('projects', []).append({"title": pt, "category": pc, "image": pi, "problem": pp, "solution": ps, "impact": pimp})
                save_data(st.session_state.data); st.rerun()
        with tab_edit:
            proj_list = st.session_state.data.get('projects', [])
            if proj_list:
                sel_p_idx = st.selectbox("Select Project", range(len(proj_list)), format_func=lambda x: proj_list[x]['title'])
                curr_p = proj_list[sel_p_idx]
                ep_t = st.text_input("Title", curr_p.get('title', ''))
                ep_c = st.text_input("Category", curr_p.get('category', ''))
                ep_i = st.text_input("Image URL", curr_p.get('image', ''))
                ep_p = st.text_area("Problem", curr_p.get('problem', ''), height=100)
                ep_s = st.text_area("Solution", curr_p.get('solution', ''), height=100)
                ep_imp = st.text_area("Impact", curr_p.get('impact', ''), height=100)
                c1, c2 = st.columns(2)
                if c1.button("Update"):
                    st.session_state.data['projects'][sel_p_idx] = {"title": ep_t, "category": ep_c, "image": ep_i, "problem": ep_p, "solution": ep_s, "impact": ep_imp}
                    save_data(st.session_state.data); st.rerun()
                if c2.button("Delete", type="primary"):
                    st.session_state.data['projects'].pop(sel_p_idx)
                    save_data(st.session_state.data); st.rerun()

    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            with st.container(border=True):
                render_image(p.get('image', ''))
                st.markdown(f"<div class='project-header'>{p.get('title', 'Project')}</div>", unsafe_allow_html=True)
                st.caption(f"📂 {p.get('category', 'General')}")
                if p.get('problem'): st.info(f"**Problem:**\n{p['problem']}")
                if p.get('solution'): st.success(f"**Solution:**\n{p['solution']}")
                if p.get('impact'): st.warning(f"**Impact:**\n{p['impact']}")

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    st.markdown("---")
    skills = st.session_state.data.get('skills', {})
    
    c1, c2 = st.columns([1.5, 1])
    
    # Left: Radar Chart
    with c1:
        if skills:
            fig = go.Figure(data=go.Scatterpolar(
                r=list(skills.values()),
                theta=list(skills.keys()),
                fill='toself',
                marker=dict(color='#4F8BF9')
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Right: Progress Bars (Custom CSS Styled)
    with c2:
        if st.session_state.is_admin:
            with st.form("sk"):
                n = st.text_input("Skill Name"); v = st.slider("Value", 0, 100, 50)
                if st.form_submit_button("Add/Update"):
                    st.session_state.data.setdefault('skills', {})[n] = v
                    save_data(st.session_state.data); st.rerun()
            del_sk = st.selectbox("Delete", ["-"] + list(skills.keys()))
            if del_sk != "-" and st.button("Delete Skill", type="primary"):
                del st.session_state.data['skills'][del_sk]
                save_data(st.session_state.data); st.rerun()
        
        # Public View: Modern Bars
        for s, v in skills.items():
            st.markdown(f"""
            <div class="skill-container">
                <span class="skill-label">{s} <span style="float:right">{v}%</span></span>
                <div class="skill-bar-bg">
                    <div class="skill-bar-fill" style="width: {v}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Get In Touch")
    st.markdown("---")
    prof = st.session_state.data.get('profile', {})
    
    # Center the content
    c_main = st.columns([1, 2, 1])
    with c_main[1]:
        st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
        render_image(prof.get('image_url'), width=180)
        st.markdown(f"<h2>{prof.get('name','')}</h2>", unsafe_allow_html=True)
        st.write("Feel free to reach out via email or connect on LinkedIn.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display Cards
        st.markdown('<div class="contact-container">', unsafe_allow_html=True)
        for item in prof.get('contact_info', []):
            icon_url = item.get('icon', '')
            val = item.get('value', '#')
            label = item.get('label', 'Link')
            
            st.markdown(f"""
            <a href="{val}" target="_blank" class="contact-btn">
                <img src="{icon_url}" class="contact-icon">
                <div class="contact-text">
                    <h4>{label}</h4>
                    <p>Click to Connect</p>
                </div>
            </a>
            <br>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
