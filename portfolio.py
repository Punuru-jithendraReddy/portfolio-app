import streamlit as st
import json
import os
import textwrap
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ADMIN_PASSWORD = "admin" 

st.set_page_config(layout="wide", page_title="Portfolio", page_icon="✨")

# --- CUSTOM CSS (UNCHANGED) ---
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: var(--text-color) !important; }
    p, div, span { color: var(--text-color); }
    @keyframes fadeInUp { from { opacity:0; transform:translateY(20px);} to {opacity:1; transform:none;} }
    @keyframes zoomIn { from { opacity:0; transform:scale(0.95);} to {opacity:1; transform:none;} }
    [data-testid="column"] { display:flex; flex-direction:column; height:100%; }

    .project-card {
        background-color: var(--secondary-background-color);
        border:1px solid rgba(128,128,128,0.2);
        border-radius:12px;
        padding:20px;
        min-height:480px;
        padding-bottom:70px;
        margin-bottom:20px;
        animation:fadeInUp .6s ease-out;
        position:relative;
    }
    .project-card:hover { border-color:#3B82F6; transform:translateY(-3px); }

    .p-img-container { width:100%; height:180px; overflow:hidden; border-radius:15px; margin-bottom:15px; }
    .p-img { width:100%; height:100%; object-fit:cover; }

    .p-cat-overlay {
        position:absolute; top:30px; left:30px;
        background:var(--background-color);
        color:#3B82F6;
        padding:5px 12px;
        border-radius:20px;
        font-size:.7rem;
        font-weight:800;
        z-index:5;
    }

    .p-title { font-size:1.2rem; font-weight:700; margin-bottom:15px; }
    .p-row { display:flex; margin-bottom:10px; }
    .p-label { min-width:85px; font-weight:700; font-size:.85rem; }
    .p-val {
        font-size:.85rem;
        line-height:1.5;
        opacity:.8;
        display:-webkit-box;
        -webkit-line-clamp:3;
        -webkit-box-orient:vertical;
        overflow:hidden;
    }

    div[data-testid="column"] .stButton {
        position:absolute; bottom:20px; right:20px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"profile":{}, "metrics":{}, "experience":[], "projects":[], "skills":{}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_img_src(path):
    if not path:
        return "https://placehold.co/600x400?text=No+Image"
    if "github.com" in path and "/blob/" in path:
        return path.replace("github.com", "raw.githubusercontent.com").replace("/blob/","/")
    return path

if "data" not in st.session_state:
    st.session_state.data = load_data()
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- SIDEBAR ---
with st.sidebar:
    selected = option_menu(
        None,
        ["Home", "Experience", "Projects", "Skills", "Contact"],
        icons=["house","briefcase","rocket","cpu","envelope"],
        default_index=0
    )

# ----------------------------
# HOME (UNCHANGED)
# ----------------------------
if selected == "Home":
    st.title("Home")

# ----------------------------
# EXPERIENCE (UNCHANGED)
# ----------------------------
elif selected == "Experience":
    st.title("Experience")

# ----------------------------
# 🔥 PROJECTS (CATEGORY FILTER + SECTION)
# ----------------------------
elif selected == "Projects":

    projects = st.session_state.data.get("projects", [])

    if "selected_project" not in st.session_state:
        st.session_state.selected_project = None

    # ---- CATEGORY FILTER ----
    categories = sorted(set([p.get("category","Uncategorized") for p in projects]))
    categories.insert(0, "All")

    selected_category = st.selectbox("Filter by Category", categories)

    # ---- PROJECT DETAIL VIEW ----
    if st.session_state.selected_project is not None:
        p = projects[st.session_state.selected_project]

        if st.button("← Back to Projects"):
            st.session_state.selected_project = None
            st.rerun()

        st.title(p.get("title"))
        st.caption(f"📂 {p.get('category')}")
        st.image(get_img_src(p.get("image")), use_container_width=True)
        st.markdown("### 📝 Details")
        st.write(p.get("details"))

    # ---- CATEGORY SECTIONS ----
    else:
        st.title("Projects")

        for cat in categories:
            if cat != "All":
                cat_projects = [p for p in projects if p.get("category") == cat]
            else:
                cat_projects = projects

            if not cat_projects:
                continue

            st.markdown(f"## {cat}")

            for i in range(0, len(cat_projects), 2):
                cols = st.columns(2)
                for j, p in enumerate(cat_projects[i:i+2]):
                    with cols[j]:
                        idx = projects.index(p)
                        html = f"""
                        <div class="project-card">
                            <div class="p-cat-overlay">{p.get("category")}</div>
                            <div class="p-img-container">
                                <img src="{get_img_src(p.get("image"))}" class="p-img">
                            </div>
                            <div class="p-title">{p.get("title")}</div>
                            <div class="p-row"><div class="p-label">🚨 Problem:</div><div class="p-val">{p.get("problem")}</div></div>
                            <div class="p-row"><div class="p-label">💡 Solution:</div><div class="p-val">{p.get("solution")}</div></div>
                            <div class="p-row"><div class="p-label">🚀 Impact:</div><div class="p-val">{p.get("impact")}</div></div>
                        </div>
                        """
                        st.markdown(html, unsafe_allow_html=True)
                        if st.button("More Information ➜", key=f"btn_{idx}"):
                            st.session_state.selected_project = idx
                            st.rerun()

# ----------------------------
# SKILLS (UNCHANGED)
# ----------------------------
elif selected == "Skills":
    st.title("Skills")

# ----------------------------
# CONTACT (UNCHANGED)
# ----------------------------
elif selected == "Contact":
    st.title("Contact")
