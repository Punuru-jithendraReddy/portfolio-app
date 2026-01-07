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

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="✨")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* GLOBAL */
    .main { padding-top: 1rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #0F172A; }
    
    /* SKILL BARS */
    .skill-text { font-weight: 600; color: #334155; margin-bottom: 5px; display: flex; justify-content: space-between; }
    
    /* CONTACT CARDS */
    .contact-card-modern {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        text-decoration: none !important;
        color: inherit !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s, border-color 0.2s;
        display: block;
    }
    .contact-card-modern:hover {
        transform: translateY(-5px);
        border-color: #3B82F6;
        box-shadow: 0 8px 15px rgba(59, 130, 246, 0.1);
    }
    .contact-icon-big { width: 40px; height: 40px; margin-bottom: 10px; object-fit: contain; }
    .contact-label { font-size: 1.1rem; font-weight: 700; color: #1E293B; margin-bottom: 5px; }
    .contact-val { font-size: 0.9rem; color: #3B82F6; }

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

# --- IMAGE RENDERER (Auto-Fix for GitHub Links) ---
def render_image(image_path, width=None):
    if not image_path: return
    
    # AUTO-FIX: Convert GitHub Blob link to Raw link
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    
    if image_path.startswith("http"):
        st.image(image_path, width=width)
    else:
        filename = os.path.basename(image_path)
        possible_paths = [os.path.join(BASE_DIR, "assets", filename), os.path.join(BASE_DIR, filename)]
        found = False
        for path in possible_paths:
            if os.path.exists(path):
                st.image(path, width=width)
                found = True
                break
        if not found:
            st.image("https://placehold.co/600x400/png?text=No+Image", width=width)

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
        st.markdown("<br>", unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Dashboards", mets.get('dashboards', '0'))
        mc2.metric("Work Reduced", mets.get('manual_reduction', '0%'))
        mc3.metric("Efficiency", mets.get('efficiency', '0%'))
    with c2:
        st.markdown('<div style="padding: 20px;">', unsafe_allow_html=True)
        render_image(prof.get('image_url'), width=350)
        st.markdown('</div>', unsafe_allow_html=True)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Professional Experience")
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add", "✏️ Edit"])
        with tab_add:
            r = st.text_input("Role", key="nr"); c = st.text_input("Company", key="nc")
            d = st.text_input("Date", key="nd"); desc = st.text_area("Desc", key="ndes", height=150)
            if st.button("Save"):
                st.session_state.data.setdefault('experience', []).insert(0, {"role": r, "company": c, "date": d, "description": desc})
                save_data(st.session_state.data); st.rerun()
        with tab_edit:
            exp_list = st.session_state.data.get('experience', [])
            if exp_list:
                idx = st.selectbox("Select", range(len(exp_list)), format_func=lambda x: f"{exp_list[x]['role']}")
                curr = exp_list[idx]
                er = st.text_input("Role", curr['role']); ec = st.text_input("Company", curr['company'])
                ed = st.text_input("Date", curr['date']); edesc = st.text_area("Desc", curr['description'], height=150)
                c1, c2 = st.columns(2)
                if c1.button("Update"): st.session_state.data['experience'][idx] = {"role": er, "company": ec, "date": ed, "description": edesc}; save_data(st.session_state.data); st.rerun()
                if c2.button("Delete", type="primary"): st.session_state.data['experience'].pop(idx); save_data(st.session_state.data); st.rerun()

    for job in st.session_state.data.get('experience', []):
        with st.container(border=True):
            st.markdown(f"### {job.get('role', 'Role')}")
            st.caption(f"**{job.get('company', 'Company')}** | {job.get('date', 'Date')}")
            st.markdown(job.get('description', ''))

# --- PROJECTS ---
elif selected == "Projects":
    st.title("Projects")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add", "✏️ Edit"])
        with tab_add:
            pt = st.text_input("Title"); pc = st.text_input("Category")
            pi = st.text_input("Image"); pp = st.text_area("Problem")
            ps = st.text_area("Solution"); pimp = st.text_area("Impact")
            if st.button("Save"):
                st.session_state.data.setdefault('projects', []).append({"title": pt, "category": pc, "image": pi, "problem": pp, "solution": ps, "impact": pimp})
                save_data(st.session_state.data); st.rerun()
        with tab_edit:
            pl = st.session_state.data.get('projects', [])
            if pl:
                pidx = st.selectbox("Select", range(len(pl)), format_func=lambda x: pl[x]['title'])
                cp = pl[pidx]
                ept = st.text_input("Title", cp['title']); epc = st.text_input("Category", cp['category'])
                epi = st.text_input("Image", cp['image']); epp = st.text_area("Prob", cp['problem'])
                eps = st.text_area("Sol", cp.get('solution','')); epimp = st.text_area("Imp", cp.get('impact',''))
                if st.button("Update"): st.session_state.data['projects'][pidx] = {"title": ept, "category": epc, "image": epi, "problem": epp, "solution": eps, "impact": epimp}; save_data(st.session_state.data); st.rerun()
                if st.button("Delete", type="primary"): st.session_state.data['projects'].pop(pidx); save_data(st.session_state.data); st.rerun()

    # --- UI: FIXED DESIGN (No raw HTML text, no congestion) ---
    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            with st.container(border=True):
                render_image(p.get('image', ''), width=None)
                st.subheader(p.get('title', 'Project'))
                st.caption(f"📂 {p.get('category', 'General')}")
                
                # FIXED: Using native Streamlit elements instead of HTML strings
                # This fixes the "<div class..." text appearing on screen
                if p.get('problem'):
                    with st.expander("🚨 Problem", expanded=True):
                        st.write(p['problem'])
                
                if p.get('solution'):
                    with st.expander("💡 Solution", expanded=False):
                        st.write(p['solution'])
                
                if p.get('impact'):
                    with st.expander("🚀 Impact", expanded=False):
                        st.write(p['impact'])

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    
    if st.session_state.is_admin:
        with st.form("sk"):
            n = st.text_input("Skill"); v = st.slider("Val", 0, 100, 50)
            if st.form_submit_button("Add"): 
                st.session_state.data.setdefault('skills', {})[n] = v; save_data(st.session_state.data); st.rerun()
        if st.button("Delete All", type="primary"): 
            st.session_state.data['skills'] = {}; save_data(st.session_state.data); st.rerun()

    # --- UI: SPIDER CHART TOP CENTER ---
    if skills:
        col_chart1, col_chart2, col_chart3 = st.columns([1, 2, 1])
        with col_chart2:
            fig = go.Figure(data=go.Scatterpolar(
                r=list(skills.values()), theta=list(skills.keys()), fill='toself',
                marker=dict(color='#3B82F6')
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, margin=dict(l=40, r=40, t=30, b=30), height=300)
            st.plotly_chart(fig, use_container_width=True)

    # --- UI: SKILLS LIST DOWN WITH PERCENTAGES ---
    st.markdown("### Proficiency Levels")
    s_cols = st.columns(3)
    skill_items = list(skills.items())
    for i, (s, v) in enumerate(skill_items):
        with s_cols[i % 3]:
            st.markdown(f"""
            <div style="margin-bottom:15px;">
                <div class="skill-text">
                    <span>{s}</span>
                    <span>{v}%</span>
                </div>
                <div style="background:#E2E8F0; border-radius:6px; height:8px; width:100%;">
                    <div style="background:linear-gradient(90deg, #3B82F6, #2563EB); border-radius:6px; height:100%; width:{v}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Get In Touch")
    prof = st.session_state.data.get('profile', {})
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    for i, item in enumerate(prof.get('contact_info', [])):
        # Alternate columns for grid look
        with (c1 if i % 2 == 0 else c2):
            icon_url = item.get('icon', '')
            val = item.get('value', '#')
            label = item.get('label', 'Link')
            
            # Icon HTML (Auto-fix for local vs web)
            if icon_url.startswith("http"): 
                img_tag = f'<img src="{icon_url}" class="contact-icon-big">' 
            else:
                img_tag = '<span style="font-size:40px; display:block; margin-bottom:10px;">🔗</span>'
            
            st.markdown(f"""
            <a href="{val}" target="_blank" class="contact-card-modern">
                {img_tag}
                <div class="contact-label">{label}</div>
                <div class="contact-val">{val}</div>
            </a>
            <br>
            """, unsafe_allow_html=True)
