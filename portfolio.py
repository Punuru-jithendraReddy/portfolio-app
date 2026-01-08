# --- PROJECTS ---
elif selected == "Projects":
    # 1. Initialize Session State for Project Selection
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None

    # --- ADMIN: ADD/EDIT PROJECTS (Only show in List View) ---
    if st.session_state.is_admin and st.session_state.selected_project is None:
        st.title("Projects Manager")
        tab_add, tab_edit = st.tabs(["➕ Add", "✏️ Edit"])
        with tab_add:
            pt = st.text_input("Title"); pc = st.text_input("Category")
            pi = st.text_input("Thumbnail Image"); pdi = st.text_input("Dashboard Image (Detail)"); 
            pp = st.text_area("Problem"); ps = st.text_area("Solution"); pimp = st.text_area("Impact")
            pdet = st.text_area("Long Description (Detail)")
            if st.button("Save"):
                new_proj = {
                    "title": pt, "category": pc, "image": pi, "dashboard_image": pdi,
                    "problem": pp, "solution": ps, "impact": pimp, "details": pdet
                }
                st.session_state.data.setdefault('projects', []).append(new_proj)
                save_data(st.session_state.data); st.rerun()
        
        with tab_edit:
            pl = st.session_state.data.get('projects', [])
            if pl:
                pidx = st.selectbox("Select Project to Edit", range(len(pl)), format_func=lambda x: pl[x]['title'])
                cp = pl[pidx]
                ept = st.text_input("Title", cp['title'], key="ept"); epc = st.text_input("Category", cp['category'], key="epc")
                epi = st.text_input("Thumbnail", cp['image'], key="epi"); epdi = st.text_input("Dashboard Img", cp.get('dashboard_image',''), key="epdi")
                epp = st.text_area("Prob", cp['problem'], key="epp"); eps = st.text_area("Sol", cp.get('solution',''), key="eps")
                epimp = st.text_area("Imp", cp.get('impact',''), key="epimp"); epdet = st.text_area("Long Desc", cp.get('details',''), key="epdet")
                
                c1, c2 = st.columns(2)
                if c1.button("Update"): 
                    st.session_state.data['projects'][pidx] = {
                        "title": ept, "category": epc, "image": epi, "dashboard_image": epdi, 
                        "problem": epp, "solution": eps, "impact": epimp, "details": epdet
                    }
                    save_data(st.session_state.data); st.rerun()
                if c2.button("Delete", type="primary"): 
                    st.session_state.data['projects'].pop(pidx); save_data(st.session_state.data); st.rerun()
        st.markdown("---")

    # --- VIEW LOGIC ---
    projects = st.session_state.data.get('projects', [])

    # VIEW A: DETAILED PROJECT VIEW
    if st.session_state.selected_project is not None:
        idx = st.session_state.selected_project
        if 0 <= idx < len(projects):
            p = projects[idx]
            
            # Back Button
            if st.button("← Back to Projects"):
                st.session_state.selected_project = None
                st.rerun()

            # Header
            st.title(p.get('title'))
            st.caption(f"📂 {p.get('category')} | 🚧 Problem Solved: {p.get('problem')}")
            
            # Main Dashboard Display (Image or Video)
            dash_img = p.get('dashboard_image') or p.get('image') # Fallback to thumbnail if no dashboard img
            if dash_img:
                if dash_img.endswith('.mp4'):
                    st.video(dash_img)
                else:
                    st.image(get_img_src(dash_img), use_container_width=True)
            
            # Deep Dive Content
            st.markdown("### 📝 Project Details")
            st.write(p.get('details', 'No detailed description available.'))
            
            # Summary Metrics (Reused from card data)
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.info(f"**🚨 The Problem**\n\n{p.get('problem')}")
            with c2: 
                st.success(f"**💡 The Solution**\n\n{p.get('solution')}")
            with c3: 
                st.warning(f"**🚀 The Impact**\n\n{p.get('impact')}")

        else:
            st.error("Project not found.")
            if st.button("Go Back"):
                st.session_state.selected_project = None
                st.rerun()

    # VIEW B: MAIN GALLERY (LIST VIEW)
    else:
        st.title("Projects")
        # Loop through projects
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            batch = projects[i : i+2]
            
            for j, p in enumerate(batch):
                actual_idx = i + j
                with cols[j]:
                    # 1. Render The Visual Card (Same as before)
                    img_src = get_img_src(p.get('image', ''))
                    
                    details_html = ""
                    if p.get('problem'): details_html += f"<div class='p-detail'><b>🚨 Problem:</b> {p['problem']}</div>"
                    if p.get('solution'): details_html += f"<div class='p-detail'><b>💡 Solution:</b> {p['solution']}</div>"
                    if p.get('impact'): details_html += f"<div class='p-detail'><b>🚀 Impact:</b> {p['impact']}</div>"

                    st.markdown(f"""
                    <div class="project-card">
                        <div class="p-img-container">
                            <img src="{img_src}" class="p-img">
                        </div>
                        <div class="p-content">
                            <div class="p-title">{p.get('title')}</div>
                            <div class="p-cat">📂 {p.get('category')}</div>
                            {details_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. Add the "View Details" Button BELOW the card
                    # We use a unique key for every button based on the index
                    if st.button(f"View Case Study ➡", key=f"btn_{actual_idx}"):
                        st.session_state.selected_project = actual_idx
                        st.rerun()
            
            # Spacer between rows
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
