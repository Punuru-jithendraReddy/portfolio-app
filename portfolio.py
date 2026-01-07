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

# --- UI OVERHAUL (CSS) ---
st.markdown("""
<style>
    /* GLOBAL FONTS & COLORS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #0F172A; }
    p { color: #475569; }

    /* 1. HERO METRICS (Home) */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0; border-radius: 16px;
        padding: 25px; text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); border-color: #3B82F6; }
    .metric-value { font-size: 2.2rem; font-weight: 800; color: #3B82F6; }
    .metric-label { font-size: 0.9rem; font-weight: 600; color: #64748B; letter-spacing: 1px; }

    /* 2. TIMELINE EXPERIENCE (Polished) */
    .timeline-card {
        background: white; border-radius: 12px; padding: 24px;
        margin-bottom: 20px;
        border-left: 6px solid #3B82F6; /* The Timeline Line */
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s;
    }
    .timeline-card:hover { transform: translateX(8px); box-shadow: 0 10px 15px rgba(0,0,0,0.05); }
    .t-role { font-size: 1.3rem; font-weight: 700; color: #1E293B; margin: 0; }
    .t-company { font-size: 1rem; font-weight: 600; color: #3B82F6; margin-bottom: 8px; display: inline-block;}
    .t-date { font-size: 0.85rem; color: #94A3B8; float: right; font-weight: 500; }
    .t-desc { font-size: 0.95rem; color: #334155; line-height: 1.6; margin-top: 10px; white-space: pre-line; }

    /* 3. PROJECT CARDS (Animated) */
    .project-card-container {
        background: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 16px;
        overflow: hidden; height: 100%; position: relative;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bouncy Animation */
    }
    .project-card-container:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(59, 130, 246, 0.25);
        border-color: #3B82F6;
    }
    .p-img-box { width: 100%; height: 180px; overflow: hidden; background: #F1F5F9; }
    .p-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
    .project-card-container:hover .p-img { transform: scale(1.1); } /* Zoom Image on Hover */
    
    .p-body { padding: 20px; }
    .p-title { font-size: 1.25rem; font-weight: 800; color: #0F172A; margin-bottom: 5px; }
    .p-cat { font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; background: #F1F5F9; padding: 4px 10px; border-radius: 20px; display: inline-block; margin-bottom: 12px; }
    .p-text { font-size: 0.9rem; color: #475569; margin-bottom: 8px; line-height: 1.5; }

    /* 4. SKILL GRID (No Scroll) */
    .skill-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 15px; display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 10px; transition: 0.2s;
    }
    .skill-card:hover { border-color: #3B82F6; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.1); }
    .skill-name { font-weight: 700; color: #334155; font-size: 0.95rem; }
    .skill-bar-track { width: 60%; height: 8px; background: #F1F5F9; border-radius: 4px; overflow: hidden; }
    .skill-bar-fill { height: 100%; background: linear-gradient(90deg, #3B82F6, #2563EB); border-radius: 4px; }

    /* 5. CONTACT DOCK */
    .contact-dock {
        display: flex; gap: 30px; justify-content: center; align-items: center; flex-wrap: wrap; margin-top: 30px;
    }
    .contact-btn {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        width: 140px; height: 120px;
        background: white; border: 1px solid #E2E8F0; border-radius: 20px;
        text-decoration: none !important; color: #334155 !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .contact-btn:hover {
        transform: translateY(-8px);
        background: #EFF6FF; border-color: #3B82F6;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
    }
    .c-icon { width: 40px; height: 40px; margin-bottom: 10px; object-fit: contain; }
    .c-text { font-weight: 700; font-size: 1rem; }
    
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
def get_image_path(image_path):
    if not image_path: return "https://placehold.co/600x400/png?text=No+Image"
    if image_path.startswith("http"): return image_path
    
    filename = os.path.basename(image_path)
    possible_paths = [os.path.join(BASE_DIR, "assets", filename), os.path.join(BASE_DIR, filename)]
    for path in possible_paths:
        if os.path.exists(path): return path
    return "https://placehold.co/600x400/png?text=Missing"

# --- INITIALIZE ---
if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', {})
    st.markdown('<div style="text-align: center; margin-bottom:20px;">', unsafe_allow_html=True)
    if prof.get('image_url'):
        st.image(get_image_path(prof.get('image_url')), width=140)
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
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{prof.get('name', 'Name')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#3B82F6; margin-top:0;'>{prof.get('role', 'Role')}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.1rem; line-height:1.6;'>{prof.get('summary', '')}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("dashboards","0")}</div><div class="metric-label">Dashboards</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("manual_reduction","0%")}</div><div class="metric-label">Reduction</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("efficiency","0%")}</div><div class="metric-label">Efficiency</div></div>', unsafe_allow_html=True)
        
    with c2:
        st.image(get_image_path(prof.get('image_url')), use_container_width=True)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Professional Experience")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add", "✏️ Edit"])
        with tab_add:
            r = st.text_input("Role", key="nr"); c = st.text_input("Company", key="nc")
            d = st.text_input("Date", key="nd"); desc = st.text_area("Desc", key="ndes", height=150)
            if st.button("Save Job"):
                st.session_state.data.setdefault('experience', []).insert(0, {"role": r, "company": c, "date": d, "description": desc})
                save_data(st.session_state.data); st.rerun()
        with tab_edit:
            exp_list = st.session_state.data.get('experience', [])
            if exp_list:
                idx = st.selectbox("Select", range(len(exp_list)), format_func=lambda x: f"{exp_list[x]['role']}")
                curr = exp_list[idx]
                er = st.text_input("Role", curr['role']); ec = st.text_input("Company", curr['company'])
                ed = st.text_input("Date", curr['date']); edesc = st.text_area("Desc", curr['description'], height=150)
                col1, col2 = st.columns(2)
                if col1.button("Update"): st.session_state.data['experience'][idx] = {"role": er, "company": ec, "date": ed, "description": edesc}; save_data(st.session_state.data); st.rerun()
                if col2.button("Delete", type="primary"): st.session_state.data['experience'].pop(idx); save_data(st.session_state.data); st.rerun()

    # --- UI: POLISHED TIMELINE CARDS ---
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"""
        <div class="timeline-card">
            <span class="t-date">{job.get('date')}</span>
            <div class="t-role">{job.get('role')}</div>
            <div class="t-company">{job.get('company')}</div>
            <div class="t-desc">{job.get('description')}</div>
        </div>
        """, unsafe_allow_html=True)

# --- PROJECTS ---
elif selected == "Projects":
    st.title("Projects")
    
    if st.session_state.is_admin:
        tab_add, tab_edit = st.tabs(["➕ Add", "✏️ Edit"])
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
                if st.button("Update"): st.session_state.data['projects'][pidx] = {"title": ept, "category": epc, "image": epi, "problem": epp, "solution": eps, "impact": epimp}; save_data(st.session_state.data); st.rerun()
                if st.button("Delete", type="primary"): st.session_state.data['projects'].pop(pidx); save_data(st.session_state.data); st.rerun()

    # --- UI: ANIMATED HTML CARDS ---
    # We use st.columns but inside we render pure HTML for the card to ensure the hover effect applies to the whole box
    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            img_src = get_image_path(p.get('image', ''))
            
            # Note: We put the image in a div, and the text in another div, all wrapped in a container
            html_card = f"""
            <div class="project-card-container">
                <div class="p-img-box">
                    <img src="{img_src}" class="p-img">
                </div>
                <div class="p-body">
                    <div class="p-title">{p.get('title')}</div>
                    <div class="p-cat">{p.get('category')}</div>
                    
                    {'<div class="p-text"><b>🚨 Problem:</b> ' + p['problem'] + '</div>' if p.get('problem') else ''}
                    {'<div class="p-text"><b>💡 Solution:</b> ' + p['solution'] + '</div>' if p.get('solution') else ''}
                    {'<div class="p-text"><b>🚀 Impact:</b> ' + p['impact'] + '</div>' if p.get('impact') else ''}
                </div>
            </div>
            <div style="height: 25px"></div> """
            st.markdown(html_card, unsafe_allow_html=True)

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    
    if st.session_state.is_admin:
        with st.form("sk"):
            n = st.text_input("Skill"); v = st.slider("Val", 0, 100, 50)
            if st.form_submit_button("Add"): st.session_state.data.setdefault('skills', {})[n] = v; save_data(st.session_state.data); st.rerun()
        if st.button("Delete All", type="primary"): st.session_state.data['skills'] = {}; save_data(st.session_state.data); st.rerun()

    # --- UI: 3-COLUMN GRID (No Scroll) ---
    s_cols = st.columns(3)
    s_items = list(skills.items())
    
    for i, (s, v) in enumerate(s_items):
        with s_cols[i % 3]:
            st.markdown(f"""
            <div class="skill-card">
                <span class="skill-name">{s}</span>
                <div class="skill-bar-track">
                    <div class="skill-bar-fill" style="width: {v}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Get In Touch")
    prof = st.session_state.data.get('profile', {})
    
    st.markdown(f"<div style='text-align:center'><h2>{prof.get('name')}</h2><p>Connect with me on social media or send an email.</p></div>", unsafe_allow_html=True)
    
    # --- UI: CENTERED DOCK (No Scroll) ---
    st.markdown('<div class="contact-dock">', unsafe_allow_html=True)
    
    for item in prof.get('contact_info', []):
        icon = item.get('icon', '')
        val = item.get('value', '#')
        lbl = item.get('label', 'Link')
        
        # Resolve icon path if local, else use URL
        if not icon.startswith("http"):
            # If we were rendering Python we'd use base64, but for this HTML loop, 
            # we rely on public URLs for icons OR fallback. 
            # To fix "Invisible Icon" for local files in HTML mode, we really need public URLs.
            # Using a fallback emoji if it's not http to ensure something shows.
            img_tag = '<span style="font-size:30px;">🔗</span>'
        else:
            img_tag = f'<img src="{icon}" class="c-icon">'
            
        st.markdown(f"""
        <a href="{val}" target="_blank" class="contact-btn">
            {img_tag}
            <span class="c-text">{lbl}</span>
        </a>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
