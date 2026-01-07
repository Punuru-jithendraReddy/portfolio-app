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
    
    /* HERO CARDS */
    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #3B82F6; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #3B82F6; }
    .metric-label { font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; }

    /* TIMELINE CARDS */
    .timeline-card {
        background: white; border-radius: 12px; padding: 24px;
        margin-bottom: 20px;
        border-left: 6px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .timeline-card:hover { transform: translateX(5px); box-shadow: 0 10px 15px rgba(0,0,0,0.05); }
    .t-role { font-size: 1.3rem; font-weight: 700; color: #1E293B; margin: 0; }
    .t-company { font-size: 1rem; font-weight: 600; color: #3B82F6; margin-bottom: 8px; display: inline-block;}
    .t-date { font-size: 0.85rem; color: #94A3B8; float: right; font-weight: 500; }
    .t-desc { font-size: 0.95rem; color: #334155; line-height: 1.6; margin-top: 10px; white-space: pre-line; }

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

    /* UTILS */
    .project-text { margin-bottom: 8px; font-size: 0.95rem; }
    .stImage > img { border-radius: 8px; }
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

# --- IMAGE RENDERER ---
def render_image(image_path, width=None):
    if not image_path: return
    
    # Auto-Fix GitHub Blob Links
    if "github.com" in image_path and "/blob/" in image_path:
        image_path = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    
    final_path = None
    if image_path.startswith("http"):
        final_path = image_path
    else:
        filename = os.path.basename(image_path)
        possible_paths = [os.path.join(BASE_DIR, "assets", filename), os.path.join(BASE_DIR, filename)]
        for path in possible_paths:
            if os.path.exists(path):
                final_path = path
                break
        if not final_path:
            final_path = "https://placehold.co/600x400/png?text=Image+Missing"

    # FIXED: Use container width if specific width is None
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
        with mc1: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("dashboards","0")}</div><div class="metric-label">Dashboards</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("manual_reduction","0%")}</div><div class="metric-label">Reduction</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-card"><div class="metric-value">{mets.get("efficiency","0%")}</div><div class="metric-label">Efficiency</div></div>', unsafe_allow_html=True)
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
        st.markdown(f"""
        <div class="timeline-card">
            <span class="t-date">{job.get('date')}</span>
            <div class="t-role">{job.get('role')}</div>
            <div class="t-company">{job.get('company')}</div>
            <div class="t-desc">{job.get('description')}</div>
        </div>
        """, unsafe_allow_html=True)

# --- PROJECTS (FIXED: NO DROPDOWNS) ---
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

    # --- UI: CLEAN CARDS (Info Visible Directly) ---
    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            with st.container(border=True):
                # Image
                render_image(p.get('image', ''), width=None)
                
                # Header
                st.subheader(p.get('title', 'Project'))
                st.caption(f"📂 {p.get('category', 'General')}")
                
                st.markdown("---") # Divider for cleanliness
                
                # Details - VISIBLE (No Expanders)
                if p.get('problem'):
                    st.markdown(f"**🚨 Problem:** {p['problem']}")
                    st.write("") # Spacer
                
                if p.get('solution'):
                    st.markdown(f"**💡 Solution:** {p['solution']}")
                    st.write("")
                
                if p.get('impact'):
                    st.markdown(f"**🚀 Impact:** {p['impact']}")

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

    c1, c2 = st.columns([1, 1])
    
    # Left: Spider Chart
    with c1:
        if skills:
            fig = go.Figure(data=go.Scatterpolar(
                r=list(skills.values()), theta=list(skills.keys()), fill='toself',
                marker=dict(color='#3B82F6')
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, margin=dict(l=40, r=40, t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)

    # Right: List with Percentages
    with c2:
        st.markdown("### Proficiency")
        for s, v in skills.items():
            st.write(f"**{s}** ({v}%)")
            st.progress(v)

# --- CONTACT ---
elif selected == "Contact":
    st.title("Get In Touch")
    prof = st.session_state.data.get('profile', {})
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    for i, item in enumerate(prof.get('contact_info', [])):
        with (c1 if i % 2 == 0 else c2):
            icon_url = item.get('icon', '')
            val = item.get('value', '#')
            label = item.get('label', 'Link')
            
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
