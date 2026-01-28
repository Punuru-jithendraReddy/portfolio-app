# ==========================================
# 10. PAGE: CONTACT (AJAX FIX)
# ==========================================
elif selected == "Contact":
    if st.session_state.is_admin:
        with st.expander("✏️ Edit Contact Info"):
            contacts = st.session_state.data.get('profile', {}).get('contact_info', [])
            contact_list = [{"Label": c['label'], "Value": c['value'], "Icon": c['icon']} for c in contacts]
            edited_contacts = st.data_editor(contact_list, num_rows="dynamic")
            new_contacts = [{"label": r['Label'], "value": r['Value'], "icon": r['Icon']} for r in edited_contacts if r['Label']]
            st.session_state.data['profile']['contact_info'] = new_contacts

    st.title("Get in Touch")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### Send a Message")
        
        # --- AJAX FORM SCRIPT ---
        # This script intercepts the submit button, prevents the page reload, 
        # sends the data in the background, and updates the button text.
        contact_form = f"""
        <script>
        function submitForm(event) {{
            event.preventDefault(); // Prevent page reload
            
            var btn = document.getElementById("myBtn");
            var form = document.getElementById("myForm");
            var status = document.getElementById("status_msg");
            
            // 1. Change Button Look
            var originalText = btn.innerHTML;
            btn.innerHTML = "⏳ Sending...";
            btn.disabled = true;

            // 2. Collect Data
            var formData = new FormData(form);
            
            // 3. Send Data via Fetch (AJAX)
            fetch("https://formsubmit.co/ajax/{CONTACT_EMAIL}", {{
                method: "POST",
                body: formData,
                headers: {{ 
                    'Accept': 'application/json' 
                }}
            }})
            .then(response => {{
                if (response.ok) {{
                    // Success
                    btn.innerHTML = "✅ Message Sent!";
                    btn.style.backgroundColor = "#22c55e"; // Green color
                    form.reset(); // Clear the inputs
                }} else {{
                    // Error
                    btn.innerHTML = "❌ Error";
                    btn.disabled = false;
                    setTimeout(() => {{ btn.innerHTML = originalText; }}, 3000);
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                btn.innerHTML = "❌ Error";
                btn.disabled = false;
                setTimeout(() => {{ btn.innerHTML = originalText; }}, 3000);
            }});
        }}
        </script>

        <form id="myForm" onsubmit="submitForm(event)">
             <input type="hidden" name="_captcha" value="false">
             <input type="hidden" name="_template" value="table">
             
             <input type="text" name="name" placeholder="Your Name" required style="width:100%; padding: 12px; margin-bottom:15px; border: 1px solid #ccc; border-radius: 8px; background-color: var(--secondary-background-color); color: var(--text-color);">
             <input type="email" name="email" placeholder="Your Email" required style="width:100%; padding: 12px; margin-bottom:15px; border: 1px solid #ccc; border-radius: 8px; background-color: var(--secondary-background-color); color: var(--text-color);">
             <textarea name="message" placeholder="Your Message" required style="width:100%; padding: 12px; margin-bottom:15px; border: 1px solid #ccc; border-radius: 8px; min-height: 150px; background-color: var(--secondary-background-color); color: var(--text-color);"></textarea>
             
             <button id="myBtn" type="submit" style="background-color:#3B82F6; color:white; padding:12px 24px; border:none; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">Send Message</button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)

    with c2:
        st.markdown("### Connect")
        prof = st.session_state.data.get('profile', {})
        for item in prof.get('contact_info', []):
            st.markdown(f'<a href="{item.get("value")}" target="_blank" style="text-decoration:none;"><div class="metric-card" style="margin-bottom:15px; padding:15px;"><img src="{item.get("icon")}" width="30"><br><b style="color:var(--text-color); font-size:0.9rem;">{item.get("label")}</b></div></a>', unsafe_allow_html=True)
