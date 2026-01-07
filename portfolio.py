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

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="💼")

# --- 1. THE SAFETY NET DATA (Fallback if JSON is missing) ---
# This ensures your app is NEVER blank.
DEFAULT_DATA = {
    "profile": {
        "name": "Jithendra Reddy Punuru",
        "role": "Software Engineer",
        "summary": "I'm a Software Engineer specializing in the Microsoft Power Platform...",
        # Using a public placeholder so it always shows up
        "image_url": "https://placehold.co/400x400/png?text=Profile+Pic", 
        "contact_info": [
            {
                "label": "Email",
                "value": "mailto:jithendrareddypunuru@gmail.com",
                "icon": "https://img.icons8.com/color/48/gmail-new.png"
            },
            {
                "label": "LinkedIn",
                "value": "https://www.linkedin.com/in/jithendrareddypunuru/",
                "icon": "https://img.icons8.com/color/48/linkedin.png"
            }
        ]
    },
    "experience": [],
    "projects": [],
    "skills": {"Power BI": 90, "Python": 85},
    "metrics": {"dashboards": "8+", "efficiency": "30%", "manual_reduction": "40%"}
}

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
    """Tries to load JSON. If file is missing/empty, returns DEFAULT_DATA."""
    if not os.path.exists(DATA_FILE):
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Merge with default to ensure no keys are missing
            if not data: return DEFAULT_DATA
            return data
    except:
        return DEFAULT_DATA

def save_data(data):
    """Saves changes to the local session file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        st.toast("Changes Saved locally! Download to make permanent.", icon="✅")
    except Exception as e:
        st.error(f"Save failed: {e}")

# --- HELPER: IMAGE RENDERER ---
def render_image(image_path, width=None):
    # If no path, use the default placeholder from DEFAULT_DATA
    if not image_path:
        image_path = DEFAULT_DATA['profile']['image_url']
    
    # 1. Web URL (Always works)
    if image_path.startswith("http"):
        st.image(image_path, width=width)
        return

    # 2. Local File (Only works if file exists)
    # We strip any folder names and look directly in current directory or assets
    filename = os.path.basename(image_path)
    possible_paths = [
        os.path.join(BASE_DIR, "assets", filename),
        os.path.join(BASE_DIR, filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            st.image(path, width=width)
            return
            
    # 3. Fallback if local file missing
    st.image("https://placehold.co/400x400/png?text=Image+Missing", width=width)

# --- MAIN APP LOGIC ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    prof = st.session_state.data.get('profile', DEFAULT_DATA['profile'])
    
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
        # DOWNLOAD BUTTON (Required for Streamlit Cloud persistence)
        st.download_button(
            label="📥 Download Updated data.json",
            data=json.dumps(st.session_state.data, indent=4),
            file_name="data.json",
            mime="application/json"
        )
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
            n_sum = st.text_area("Summary", prof.get('summary', ''))
            n_img = st.text_input("Image URL (http...)", prof.get('image_url', ''))
            
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
        
        # Metrics Display
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
        with st.expander("➕ Add Job"):
            r = st.text_input("Role")
            c = st.text_input("Company")
            d = st.text_input("Date (e.g. Jan 2024 - Present)")
            desc = st.text_area("Description")
            if st.button("Add"):
                st.session_state.data.setdefault('experience', []).insert(0, {"role": r, "company": c, "date": d, "description": desc})
                save_data(st.session_state.data)
                st.rerun()
                
    for job in st.session_state.data.get('experience', []):
        st.subheader(job['role'])
        st.caption(f"{job['company']} | {job['date']}")
        st.write(job['description'])
        st.divider()

# --- PROJECTS ---
elif selected == "Projects":
    st.header("Projects")
    
    if st.session_state.is_admin:
        with st.expander("➕ Add Project"):
            pt = st.text_input("Title")
            pc = st.text_input("Category")
            pi = st.text_input("Image URL (http...)")
            pp = st.text_area("Problem")
            if st.button("Add Project"):
                st.session_state.data.setdefault('projects', []).append({"title": pt, "category": pc, "image": pi, "problem": pp})
                save_data(st.session_state.data)
                st.rerun()

    cols = st.columns(2)
    for i, p in enumerate(st.session_state.data.get('projects', [])):
        with cols[i%2]:
            with st.container(border=True):
                render_image(p.get('image', ''), width=None)
                st.subheader(p.get('title', 'Project'))
                st.caption(p.get('category', 'General'))
                st.write(p.get('problem', ''))

# --- SKILLS ---
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
                n = st.text_input("Skill")
                v = st.slider("Val", 0, 100, 50)
                if st.form_submit_button("Add"):
                    st.session_state.data.setdefault('skills', {})[n] = v
                    save_data(st.session_state.data)
                    st.rerun()
        for s, v in skills.items():
            st.write(f"**{s}**")
            st.progress(v)

# --- CONTACT ---
elif selected == "Contact":
    st.header("Contact")
    prof = st.session_state.data.get('profile', {})
    
    c1, c2 = st.columns([1, 2])
    with c1:
        render_image(prof.get('image_url'), width=150)
    
    with c2:
        for item in prof.get('contact_info', []):
            icon_url = item.get('icon', '')
            val = item.get('value', '#')
            label = item.get('label', 'Link')
            
            # Simple Image Tag for Icon
            icon_html = f'<img src="{icon_url}" class="contact-icon-img">' if icon_url else "🔗"
            
            st.markdown(f"""
            <a href="{val}" target="_blank" style="text-decoration:none;">
                <div class="contact-card">
                    <div class="contact-icon-box">{icon_html}</div>
                    <div>
                        <div style="font-weight:bold; color:#555">{label}</div>
                        <div style="color:#0077b5">{val}</div>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)
