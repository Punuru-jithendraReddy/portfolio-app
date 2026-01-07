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

st.set_page_config(layout="wide", page_title="Portfolio Admin", page_icon="⚙️")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: 700; color: #0E1117;}
    .contact-card {
        padding: 15px; border-radius: 10px; background-color: #f8f9fa; 
        margin-bottom: 15px; border: 1px solid #e9ecef; display: flex; align-items: center;
        text-decoration: none !important; color: inherit !important;
    }
    .contact-icon-box {
        margin-right: 15px; width: 40px; height: 40px; 
        display: flex; justify-content: center; align-items: center;
    }
    .contact-icon-img { width: 100%; height: 100%; object-fit: contain; }
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
def render_image(image_path, width=None):
    if not image_path: return
    
    # Clean logic for both URL and Local
    if image_path.startswith("http"):
        st.image(image_path, width=width)
    else:
        # Check local assets
        filename = os.path.basename(image_path)
        possible_paths = [os.path.join(BASE_DIR, "assets", filename), os.path.join(BASE_DIR, filename)]
        for path in possible_paths:
            if os.path.exists(path):
                st.image(path, width=width)
                return
        # Fallback if missing
        st.image("https://placehold.co/600x400/png?text=Image+Missing", width=width)

# --- INITIALIZE ---
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    render_image(prof.get('image_url'), width=120)
    st.markdown('</div>', unsafe_allow_html=True)
    
    selected = option_menu(None, ["Home", "Experience", "Projects", "Skills", "Contact"], 
                           icons=["house", "briefcase", "rocket", "cpu", "envelope"], default_index=0)
    st.markdown("---")
    
    if not st.session_state.is_admin:
        with st.expander("🔒 Admin Login"):
            if st.button("Login") and st.text_input("Password", type="password") == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
    else:
        st.success("Admin Mode")
        st.download_button("📥 Download Updated data.json", 
                           data=json.dumps(st.session_state.data, indent=4), 
                           file_name="data.json", mime="application/json")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# --- HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Profile"):
            n_name = st.text_input("Name", prof.get('name', ''))
            n_role = st.text_input("Role", prof.get('role', ''))
            n_sum = st.text_area("Summary", prof.get('summary', ''), height=150)
            n_img = st.text_input("Image URL", prof.get('image_url', ''))
            
            c1, c2, c3 = st.columns(3)
            m1 = c1.text_input("Dashboards", mets.get('dashboards', ''))
            m2 = c2.text_input("Reduction", mets.get('manual_reduction', ''))
            m3 = c3.text_input("Efficiency", mets.get('efficiency', ''))
            
            if st.button("Save Home"):
                st.session_state.data['profile'].update({"name": n_name, "role": n_role, "summary": n_sum, "image_url": n_img})
                st.session_state.data['metrics'] = {"dashboards": m1, "manual_reduction": m2, "efficiency": m3}
                save_data(st.session_state.data)
                st.rerun()

    c1, c2 = st.columns([2, 1])
    with c1:
        st.title(prof.get('name', 'Name'))
        st.subheader(prof.get('role', 'Role'))
        st.write(prof.get('summary', ''))
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Dashboards", mets.get('dashboards', '0'))
        mc2.metric("Work Reduced", mets.get('manual_reduction', '0%'))
        mc3.metric("Efficiency", mets.get('efficiency', '0%'))
    with c2:
        render_image(prof.get('image_url'), width=300)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.header("Experience")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
        
        # 1. ADD NEW
        with tab_add:
            r = st.text_input("Role", key="new_r")
            c = st.text_input("Company", key="new_c")
            d = st.text_input("Date", key="new_d")
            desc = st.text_area("Description (Use • for bullets)", key="new_desc", height=200)
            if st.button("Save Job"):
                st.session_state.data.setdefault('experience', []).insert(0, {"role": r, "company": c, "date": d, "description": desc})
                save_data(st.session_state.data)
                st.rerun()
        
        # 2. EDIT / DELETE
        with tab_edit:
            exp_list = st.session_state.data.get('experience', [])
            if not exp_list:
                st.info("No jobs to edit.")
            else:
                sel_idx = st.selectbox("Select Job", range(len(exp_list)), format_func=lambda x: f"{exp_list[x]['role']} @ {exp_list[x]['company']}")
                curr_job = exp_list[sel_idx]
                
                er = st.text_input("Edit Role", curr_job['role'])
                ec = st.text_input("Edit Company", curr_job['company'])
                ed = st.text_input("Edit Date", curr_job['date'])
                edesc = st.text_area("Edit Description", curr_job['description'], height=200)
                
                c1, c2 = st.columns(2)
                if c1.button("Update Job"):
                    st.session_state.data['experience'][sel_idx] = {"role": er, "company": ec, "date": ed, "description": edesc}
                    save_data(st.session_state.data)
                    st.rerun()
                if c2.button("Delete Job", type="primary"):
                    st.session_state.data['experience'].pop(sel_idx)
                    save_data(st.session_state.data)
                    st.rerun()

    for job in st.session_state.data.get('experience', []):
        st.subheader(job.get('role', 'Role'))
        st.caption(f"{job.get('company', 'Company')} | {job.get('date', 'Date')}")
        st.write(job.get('description', ''))
        st.divider()

# --- PROJECTS ---
elif selected == "Projects":
    st.header("Projects")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
        
        # 1. ADD NEW
        with tab_add:
            pt = st.text_input("Title", key="np_t")
            pc = st.text_input("Category", key="np_c")
            pi = st.text_input("Image URL", key="np_i")
            pp = st.text_area("Problem", key="np_p", height=100)
            ps = st.text_area("Solution", key="np_s", height=100)
            pimp = st.text_area("Impact", key="np_imp", height=100)
            
            if st.button("Save Project"):
                st.session_state.data.setdefault('projects', []).append({"title": pt, "category": pc, "image": pi, "problem": pp, "solution": ps, "impact": pimp})
                save_data(st.session_state.data)
                st.rerun()
        
        # 2. EDIT / DELETE
        with tab_edit:
            proj_list = st.session_state.data.get('projects', [])
            if not proj_list:
                st.info("No projects to edit.")
            else:
                sel_p_idx = st.selectbox("Select Project", range(len(proj_list)), format_func=lambda x: proj_list[x]['title'])
                curr_p = proj_list[sel_p_idx]
                
                ep_t = st.text_input("Edit Title", curr_p.get('title', ''))
                ep_c = st.text_input("Edit Category", curr_p.get('category', ''))
                ep_i = st.text_input("Edit Image URL", curr_p.get('image', ''))
                ep_p = st.text_area("Edit Problem", curr_p.get('problem', ''), height=100)
                ep_s = st.text_area("Edit Solution", curr_p.get('solution', ''), height=100)
                ep_imp = st.text_area("Edit Impact", curr_p.get('impact', ''), height=100)
                
                c1, c2 = st.columns(2)
                if c1.button("Update Project"):
                    st.session_state.data['projects'][sel_p_idx] = {"title": ep_t, "category": ep_c, "image": ep_i, "problem": ep_p, "solution": ep_s, "impact": ep_imp}
                    save_data(st.session_state.data)
                    st.rerun()
                if c2.button("Delete Project", type="primary"):
                    st.session_state.data['projects'].pop(sel_p_idx)
                    save_data(st.session_state.data)
                    st.rerun()

    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            with st.container(border=True):
                render_image(p.get('image', ''), width=None)
                st.subheader(p.get('title', 'Project'))
                st.caption(p.get('category', 'General'))
                if p.get('problem'): st.info(f"**Problem:** {p['problem']}")
                if p.get('solution'): st.success(f"**Solution:** {p['solution']}")
                if p.get('impact'): st.warning(f"**Impact:** {p['impact']}")

# --- SKILLS & CONTACT ---
# (Standard display logic for Skills and Contact remains the same for brevity)
elif selected == "Skills":
    st.header("Skills")
    skills = st.session_state.data.get('skills', {})
    c1, c2 = st.columns(2)
    with c1:
        if skills:
            fig = go.Figure(data=go.Scatterpolar(r=list(skills.values()), theta=list(skills.keys()), fill='toself'))
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if st.session_state.is_admin:
            with st.form("sk"):
                n = st.text_input("Skill Name"); v = st.slider("Value", 0, 100, 50)
                if st.form_submit_button("Add/Update"):
                    st.session_state.data.setdefault('skills', {})[n] = v
                    save_data(st.session_state.data)
                    st.rerun()
            del_sk = st.selectbox("Delete", ["-"] + list(skills.keys()))
            if del_sk != "-" and st.button("Delete"):
                del st.session_state.data['skills'][del_sk]
                save_data(st.session_state.data); st.rerun()
        for s, v in skills.items(): st.write(f"**{s}**"); st.progress(v)

elif selected == "Contact":
    st.header("Contact")
    prof = st.session_state.data.get('profile', {})
    c1, c2 = st.columns([1, 2])
    with c1: render_image(prof.get('image_url'), width=150)
    with c2:
        for item in prof.get('contact_info', []):
            icon, val, lbl = item.get('icon', ''), item.get('value', '#'), item.get('label', 'Link')
            icon_html = f'<img src="{icon}" class="contact-icon-img">' if icon else "🔗"
            st.markdown(f"""<a href="{val}" target="_blank" style="text-decoration:none;"><div class="contact-card"><div class="contact-icon-box">{icon_html}</div><div><div style="font-weight:bold; color:#555">{lbl}</div><div style="color:#0077b5">{val}</div></div></div></a>""", unsafe_allow_html=True)
