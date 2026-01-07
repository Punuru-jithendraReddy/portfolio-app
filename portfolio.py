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

# --- MODERN UI CSS ---
st.markdown("""
<style>
    /* GLOBAL */
    .main { padding-top: 1rem; }
    h1, h2, h3 { color: #1E293B; font-family: 'Segoe UI', sans-serif; }
    
    /* 1. HERO SECTION (Home) */
    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #4F8BF9; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #4F8BF9; }
    .metric-label { font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; }

    /* 2. EXPERIENCE CARDS (Timeline Style) */
    .job-card {
        background: white; border-radius: 10px; padding: 20px;
        margin-bottom: 20px; border-left: 5px solid #4F8BF9; /* Accent Line */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .job-card:hover { box-shadow: 0 8px 16px rgba(0,0,0,0.1); transform: translateX(5px); }
    .job-role { font-size: 1.2rem; font-weight: 700; color: #1E293B; margin: 0; }
    .job-company { font-size: 1rem; font-weight: 600; color: #4F8BF9; margin-bottom: 5px; }
    .job-date { font-size: 0.85rem; color: #94A3B8; font-style: italic; margin-bottom: 10px; display: block; }
    .job-desc { font-size: 0.95rem; color: #475569; line-height: 1.6; white-space: pre-line; }

    /* 3. PROJECT CARDS (Hover Animation Added) */
    .project-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 0; overflow: hidden; height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s; /* Animation */
    }
    .project-card:hover { 
        transform: translateY(-8px); 
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.15); 
        border-color: #4F8BF9; 
    }
    .p-content { padding: 20px; }
    .p-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 5px; color: #1E293B; }
    .p-cat { font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 15px; }
    
    /* 4. COMPACT CONTACT BUTTONS */
    .contact-btn {
        display: flex; align-items: center; justify-content: center;
        background: white; border: 1px solid #E2E8F0;
        padding: 12px 20px; border-radius: 50px; /* Pill Shape */
        text-decoration: none !important; color: #1E293B !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.2s; margin: 5px;
    }
    .contact-btn:hover { background: #F1F5F9; transform: scale(1.05); border-color: #4F8BF9; }
    .contact-icon { width: 24px; height: 24px; margin-right: 10px; }
    .contact-text { font-weight: 600; font-size: 1rem; }

    /* 5. SKILL BARS (Compact) */
    .skill-box { margin-bottom: 12px; }
    .skill-name { font-weight: 600; font-size: 0.9rem; color: #334155; margin-bottom: 4px; display: block; }
    .skill-bg { background: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden; }
    .skill-fill { background: linear-gradient(90deg, #4F8BF9, #2563EB); height: 100%; border-radius: 4px; }
    
    /* UTILS */
    .stImage { border-radius: 12px; }
    .stImage > img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- HELPER: DATA MANAGER ---
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

# --- HELPER: IMAGE RENDERER ---
def render_image(image_path, width=None):
    if not image_path: return
    
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
    
    if width: st.image(final_path, width=width)
    else: st.image(final_path, use_container_width=True)

# --- INITIALIZE ---
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    st.markdown('<div style="text-align: center; margin-bottom:10px;">', unsafe_allow_html=True)
    if prof.get('image_url'): render_image(prof.get('image_url'), width=140)
    st.markdown('</div>', unsafe_allow_html=True)
    
    selected = option_menu(None, ["Home", "Experience", "Projects", "Skills", "Contact"], 
                           icons=["house", "briefcase", "rocket", "cpu", "envelope"], default_index=0,
                           styles={"nav-link-selected": {"background-color": "#4F8BF9"}})
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
                save_data(st.session_state.data); st.rerun()

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown(f"<h1 style='margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#4F8BF9; margin-top:0;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.write(prof.get('summary', ''))
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("dashboards","0")}</div><div class="metric-label">Dashboards</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("manual_reduction","0%")}</div><div class="metric-label">Reduction</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("efficiency","0%")}</div><div class="metric-label">Efficiency</div></div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div style="padding: 20px;">', unsafe_allow_html=True)
        render_image(prof.get('image_url'), width=350)
        st.markdown('</div>', unsafe_allow_html=True)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
        with tab_add:
            r = st.text_input("Role", key="nr")
            c = st.text_input("Company", key="nc")
            d = st.text_input("Date", key="nd")
            desc = st.text_area("Description", key="ndes", height=150)
            if st.button("Save Job"):
                st.session_state.data.setdefault('experience', []).insert(0, {"role": r, "company": c, "date": d, "description": desc})
                save_data(st.session_state.data); st.rerun()
        with tab_edit:
            exp_list = st.session_state.data.get('experience', [])
            if exp_list:
                idx = st.selectbox("Select Job", range(len(exp_list)), format_func=lambda x: f"{exp_list[x]['role']}")
                curr = exp_list[idx]
                er = st.text_input("Role", curr['role'])
                ec = st.text_input("Company", curr['company'])
                ed = st.text_input("Date", curr['date'])
                edesc = st.text_area("Desc", curr['description'], height=150)
                c1, c2 = st.columns(2)
                if c1.button("Update"):
                    st.session_state.data['experience'][idx] = {"role": er, "company": ec, "date": ed, "description": edesc}
                    save_data(st.session_state.data); st.rerun()
                if c2.button("Delete", type="primary"):
                    st.session_state.data['experience'].pop(idx); save_data(st.session_state.data); st.rerun()

    # --- UI: TIMELINE CARDS ---
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="job-card">
            <h3 class="job-role">{job.get('role')}</h3>
            <div class="job-company">{job.get('company')}</div>
            <span class="job-date">{job.get('date')}</span>
            <div class="job-desc">{job.get('description')}</div>
        </div>
        """, unsafe_allow_html=True)

# --- PROJECTS ---
elif selected == "Projects":
    st.title("Projects")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add New", "✏️ Edit / Delete"])
        with tab_add:
            pt = st.text_input("Title", key="npt"); pc = st.text_input("Category", key="npc")
            pi = st.text_input("Image", key="npi"); pp = st.text_area("Problem", key="npp")
            ps = st.text_area("Solution", key="nps"); pimp = st.text_area("Impact", key="npimp")
            if st.button("Save Project"):
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
                if st.button("Update"):
                    st.session_state.data['projects'][pidx] = {"title": ept, "category": epc, "image": epi, "problem": epp, "solution": eps, "impact": epimp}
                    save_data(st.session_state.data); st.rerun()
                if st.button("Delete", type="primary"):
                    st.session_state.data['projects'].pop(pidx); save_data(st.session_state.data); st.rerun()

    # --- UI: ANIMATED CARDS ---
    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            # Container for the hover effect wrapper
            with st.container():
                st.markdown(f"""
                <div class="project-card">
                    """, unsafe_allow_html=True)
                
                # Image
                render_image(p.get('image',''))
                
                # Content
                st.markdown(f"""
                    <div class="p-content">
                        <div class="p-title">{p.get('title')}</div>
                        <div class="p-cat">📂 {p.get('category')}</div>
                """, unsafe_allow_html=True)
                
                if p.get('problem'): st.info(f"**Problem:** {p['problem']}")
                if p.get('solution'): st.success(f"**Solution:** {p['solution']}")
                if p.get('impact'): st.warning(f"**Impact:** {p['impact']}")
                
                st.markdown("</div></div><br>", unsafe_allow_html=True)

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    
    # 2-Column Layout: Left = Radar, Right = List
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        if skills:
            fig = go.Figure(data=go.Scatterpolar(
                r=list(skills.values()), theta=list(skills.keys()), fill='toself',
                marker=dict(color='#4F8BF9')
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, margin=dict(l=40, r=40, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        if st.session_state.is_admin:
            with st.form("sk"):
                n = st.text_input("Skill"); v = st.slider("Val", 0, 100, 50)
                if st.form_submit_button("Add"): 
                    st.session_state.data.setdefault('skills', {})[n] = v; save_data(st.session_state.data); st.rerun()
            if st.button("Clear All Skills", type="primary"):
                st.session_state.data['skills'] = {}; save_data(st.session_state.data); st.rerun()
        
        # --- UI: COMPACT 2-COL GRID FOR BARS (NO VERTICAL SCROLL) ---
        # Split the skills list into 2 columns automatically
        s_cols = st.columns(2)
        skill_items = list(skills.items())
        
        for i, (s, v) in enumerate(skill_items):
            with s_cols[i % 2]: # Alternate columns
                st.markdown(f"""
                <div class="skill-box">
                    <span class="skill-name">{s}</span>
                    <div class="skill-bg">
                        <div class="skill-fill" style="width: {v}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Contact Me")
    prof = st.session_state.data.get('profile', {})
    
    # --- UI: HORIZONTAL ROW (No Vertical Scroll) ---
    st.markdown('<div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px;">', unsafe_allow_html=True)
    
    for item in prof.get('contact_info', []):
        icon = item.get('icon', '')
        val = item.get('value', '#')
        lbl = item.get('label', 'Link')
        
        # Icon HTML
        if icon.startswith("http"): img_tag = f'<img src="{icon}" class="contact-icon">'
        else: img_tag = '<span style="font-size:24px;">🔗</span>'
        
        # Render Button
        st.markdown(f"""
        <a href="{val}" target="_blank" class="contact-btn">
            {img_tag}
            <div class="contact-text">{lbl}</div>
        </a>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
