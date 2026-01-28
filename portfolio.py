import streamlit as st
import json
import os
import textwrap
import requests
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
RESUME_FILE = os.path.join(BASE_DIR, 'resume.pdf') 
ADMIN_PASSWORD = "admin" 
CONTACT_EMAIL = "jithendrareddypunuru@gmail.com" # <--- YOUR EMAIL

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="🧑‍💻")

# ==========================================
# 2. CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Poppins', sans-serif; }
    .main { padding-top: 1rem; }
    h1, h2, h3 { color: var(--text-color) !important; }
    
    /* CARD STYLES */
    .metric-card {
        background: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px; 
        text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .project-card {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    input, textarea { font-family: 'Poppins', sans-serif; }
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

def get_img_src(image_path):
    if not image_path: return "https://placehold.co/600x400/png?text=No+Image"
    return image_path

def render_image(image_path, width=None):
    st.image(get_img_src(image_path), use_container_width=True)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    selected = option_menu(None, ["Home", "Experience", "Projects", "Skills", "Contact"], 
                           icons=["house", "briefcase", "rocket", "cpu", "envelope"], default_index=0,
                           styles={"nav-link-selected": {"background-color": "#3B82F6"}})
    
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE, "rb") as pdf_file:
            st.download_button("📄 Download CV", data=pdf_file.read(), file_name="resume.pdf", mime='application/octet-stream')

# ==========================================
# 5. PAGES
# ==========================================

# --- HOME ---
if selected == "Home":
    prof = st.session_state.data.get('profile', {})
    mets = st.session_state.data.get('metrics', {})
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.title(prof.get('name', 'Name'))
        st.subheader(prof.get('role', 'Role'))
        st.write(prof.get('summary', ''))
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.metric("Dashboards", mets.get("dashboards"))
        with mc2: st.metric("Reduction", mets.get("manual_reduction"))
        with mc3: st.metric("Efficiency", mets.get("efficiency"))
    with c2: render_image(prof.get('image_url'))

# --- PROJECTS ---
elif selected == "Projects":
    st.title("Projects")
    projects = st.session_state.data.get('projects', [])
    for p in projects:
        st.markdown(f"### {p.get('title')}")
        st.info(f"Problem: {p.get('problem')}")
        st.success(f"Solution: {p.get('solution')}")
        st.warning(f"Impact: {p.get('impact')}")
        st.markdown("---")

# --- SKILLS ---
elif selected == "Skills":
    st.title("Technical Skills")
    skills = st.session_state.data.get('skills', {})
    if skills:
        st.bar_chart(skills)

# --- EXPERIENCE ---
elif selected == "Experience":
    st.title("Experience")
    for job in st.session_state.data.get('experience', []):
        st.markdown(f"**{job.get('role')}** @ {job.get('company')}")
        st.text(job.get('date'))
        st.write(job.get('description'))
        st.markdown("---")

# --- CONTACT (DEBUG MODE) ---
elif selected == "Contact":
    st.title("Get in Touch")
    st.write("Fill out this form to activate your email connection.")

    with st.form("contact_form"):
        name = st.text_input("Name")
        email_sender = st.text_input("Your Email") # Changed var name to avoid conflict
        message = st.text_area("Message")
        submit_button = st.form_submit_button("Send Message")
    
    if submit_button:
        if not name or not email_sender or not message:
            st.warning("⚠️ Please fill out all fields.")
        else:
            st.info("⏳ Attempting to send...")
            try:
                # We use requests to get the exact server response
                response = requests.post(
                    f"https://formsubmit.co/{CONTACT_EMAIL}",
                    data={"name": name, "email": email_sender, "message": message, "_captcha": "false"}
                )
                
                # --- DEBUGGING OUTPUT ---
                if response.status_code == 200:
                    st.success("✅ Success! The server accepted the message.")
                    st.balloons()
                    st.markdown("### 🚨 IMPORTANT:")
                    st.markdown("**Check your email (Spam Folder) right now for an activation link from FormSubmit.**")
                else:
                    st.error(f"❌ Failed with Status Code: {response.status_code}")
                    st.write("Server Response:", response.text)
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
