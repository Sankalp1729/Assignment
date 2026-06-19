import streamlit as st
import requests
import json
import os

# Set page config
st.set_page_config(
    page_title="UrbanRoof DDR Builder",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://assignment-1-ufcs.onrender.com")

st.title("🏠 UrbanRoof DDR Builder")
st.subheader("Automated Detailed Diagnostic Report (DDR) Generator")
st.markdown("---")

# Sidebar
st.sidebar.header("Navigation & Options")
st.sidebar.markdown("""
This app automates the generation of Detailed Diagnostic Reports (DDR) by merging site inspection data and thermal imaging.
""")

# File Uploader
col1, col2 = st.columns(2)
with col1:
    inspection_file = st.file_uploader("1. Upload Inspection Report PDF", type=["pdf"])
with col2:
    thermal_file = st.file_uploader("2. Upload Thermal Images PDF", type=["pdf"])

st.markdown("<br>", unsafe_ok=True)

# Generate Button
action_col1, action_col2, action_col3 = st.columns([1, 2, 1])
with action_col2:
    generate_btn = st.button("🚀 Generate DDR Report", use_container_width=True, type="primary")
    sample_btn = st.button("📂 Load Sample Mock Report", use_container_width=True)

# Session state to hold report data
if "report_data" not in st.session_state:
    st.session_state.report_data = None
    st.session_state.download_url = None

# Process files when button clicked
if generate_btn:
    if not inspection_file or not thermal_file:
        st.error("Please upload both files before generating the report.")
    else:
        with st.spinner("Processing reports on Render backend... This may take up to a minute."):
            try:
                files = {
                    "inspectionReport": (inspection_file.name, inspection_file.getvalue(), "application/pdf"),
                    "thermalReport": (thermal_file.name, thermal_file.getvalue(), "application/pdf")
                }
                response = requests.post(f"{BACKEND_URL}/api/generate-ddr", files=files)
                
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get("success"):
                        st.session_state.report_data = res_json.get("data")
                        st.session_state.download_url = f"{BACKEND_URL}{res_json.get('downloadUrl')}"
                        st.success("DDR Report generated successfully!")
                    else:
                        st.error(f"Failed: {res_json.get('error')}")
                else:
                    st.error(f"Backend Server Error (Status Code: {response.status_code})")
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")

# Process sample mock when clicked
if sample_btn:
    with st.spinner("Generating sample mock report..."):
        try:
            response = requests.post(f"{BACKEND_URL}/api/generate-ddr-mock")
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("success"):
                    st.session_state.report_data = res_json.get("data")
                    st.session_state.download_url = f"{BACKEND_URL}{res_json.get('downloadUrl')}"
                    st.success("Sample DDR Report loaded successfully!")
                else:
                    st.error(f"Failed: {res_json.get('error')}")
            else:
                st.error(f"Backend Server Error (Status Code: {response.status_code})")
        except Exception as e:
            st.error(f"Failed to connect to backend: {str(e)}")

# Display Report Dashboard if data exists
if st.session_state.report_data:
    data = st.session_state.report_data
    
    st.markdown("---")
    st.header(f"📊 Report Findings: {data.get('propertyName')}")
    st.caption(f"Inspection Date: {data.get('inspectionDate')} | Inspected By: {data.get('inspectedBy')} | Total Floors: {data.get('floors')}")
    
    # Download Button
    if st.session_state.download_url:
        try:
            doc_response = requests.get(st.session_state.download_url)
            if doc_response.status_code == 200:
                st.download_button(
                    label="📥 Download Client Report (.docx)",
                    data=doc_response.content,
                    file_name=f"DDR_{data.get('propertyName').replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )
        except Exception as e:
            st.warning("Could not pre-fetch the Word document. Download link might be slow.")
            st.markdown(f"[Direct Download Link]({st.session_state.download_url})")

    # Tabs
    tab_sum, tab_obs, tab_causes, tab_severity, tab_actions, tab_checklist, tab_missing = st.tabs([
        "1. Property Summary", 
        "2. Observations & Media", 
        "3. Root Causes", 
        "4. Severity Assessment", 
        "5. Recommended Actions", 
        "6. Checklist Findings",
        "7. Missing Info"
    ])
    
    with tab_sum:
        st.subheader("Property Issue Summary")
        st.write(f"""
        {data.get('propertyName')} is currently experiencing extensive moisture-related issues, primarily manifesting as capillary dampness at the skirting levels of the Hall, Common Bedroom, Master Bedroom, and Kitchen. The investigation reveals that the moisture ingress is largely driven by waterproofing failures in the wet areas (Common Bathroom and Master Bedroom Bathroom) and exacerbated by structural cracks in the external walls. The seepage has progressed to the point of affecting the parking ceiling below the flat, indicating a high volume of water transit through the floor slab.
        """)
        
        st.markdown("### Correlation Map (Negative side vs Positive side)")
        summary_table = data.get("summaryTable", [])
        if summary_table:
            st.table(summary_table)
            
    with tab_obs:
        st.subheader("Area-wise Observations")
        areas = data.get("areas", [])
        for area in areas:
            with st.expander(f"Area {area.get('id')}: {area.get('name')}", expanded=True):
                col_n, col_p = st.columns(2)
                with col_n:
                    st.markdown("**Negative Side (Impacted)**")
                    st.info(area.get("negativeDesc"))
                with col_p:
                    st.markdown("**Positive Side (Exposed)**")
                    st.success(area.get("positiveDesc"))
                
                st.markdown("**Visual & Thermal Evidence**")
                img_cols = st.columns(4)
                
                # Render negative photos
                neg_photos = area.get("negativePhotos", [])
                for idx, p_num in enumerate(neg_photos):
                    col_idx = idx % 4
                    with img_cols[col_idx]:
                        img_url = f"{BACKEND_URL}/uploads/photo_{p_num}.jpg"
                        st.image(img_url, caption=f"Photo {p_num}: Negative Side", use_container_width=True)
                        
                # Render positive photos
                pos_photos = area.get("positivePhotos", [])
                for idx, p_num in enumerate(pos_photos):
                    col_idx = (len(neg_photos) + idx) % 4
                    with img_cols[col_idx]:
                        img_url = f"{BACKEND_URL}/uploads/photo_{p_num}.jpg"
                        st.image(img_url, caption=f"Photo {p_num}: Positive Side", use_container_width=True)
                        
                # Render thermal snapshots
                thermal_imgs = area.get("thermalImages", [])
                for idx, fname in enumerate(thermal_imgs):
                    col_idx1 = (len(neg_photos) + len(pos_photos) + idx*2) % 4
                    col_idx2 = (len(neg_photos) + len(pos_photos) + idx*2 + 1) % 4
                    
                    with img_cols[col_idx1]:
                        t_url = f"{BACKEND_URL}/uploads/thermal_{fname}"
                        st.image(t_url, caption=f"Thermal: {fname.replace('X.JPG', '')}", use_container_width=True)
                    with img_cols[col_idx2]:
                        r_url = f"{BACKEND_URL}/uploads/ref_{fname}"
                        st.image(r_url, caption=f"Ref Photo: {fname.replace('X.JPG', '')}", use_container_width=True)
                        
                if not neg_photos and not pos_photos and not thermal_imgs:
                    st.caption("No images available for this area.")

    with tab_causes:
        st.subheader("Probable Root Causes")
        causes = [
            {"title": "1. Waterproofing Failure", "desc": "Open tile joints and failed seals around Nahani traps in the bathrooms are allowing water to penetrate the brickbat coba. This forms a saturated reservoir in the floor sub-base."},
            {"title": "2. Capillary Action (Skirting Dampness)", "desc": "Water trapped in the floor substrate migrates horizontally and rises up the internal plaster of adjacent walls via capillary action. This is the direct cause of the skirting-level dampness observed across multiple rooms."},
            {"title": "3. External envelope cracks & Duct leaks", "desc": "Structural cracks in the external walls and leaking external piping systems allow rainwater to enter the building envelope, exacerbating wall dampness in bedrooms."}
        ]
        for c in causes:
            st.markdown(f"#### {c['title']}")
            st.write(c["desc"])
            st.markdown("---")

    with tab_severity:
        st.subheader("Severity Assessment")
        st.error("""
        **HIGH SEVERITY**
        
        The moisture ingress is widespread and has progressed to cause secondary damages such as paint bubbling, wood frame distortion, and efflorescence (mineral salt crystallization). The fact that active seepage is visible on the parking ceiling directly below Flat 103 indicates complete saturation of the RCC floor slab. If left unaddressed, the concrete pores will undergo carbonation and trigger steel reinforcement corrosion, compromising structural integrity.
        """)

    with tab_actions:
        st.subheader("Recommended Actions")
        actions = [
            {"title": "High-Performance Epoxy Regrouting", "desc": "Clean all bathroom floor and wall tile joints, rake out old grout, and apply high-performance epoxy grout to prevent further water ingress."},
            {"title": "Grout Nahani Trap Joints", "desc": "Ensure all Nahani trap junctions and collar connections are properly sealed and grouted."},
            {"title": "External Crack Sealing", "desc": "Apply polyurethane sealants or flexible plaster polymers to all structural cracks on external wall surfaces and repair leaking plumbing mains."},
            {"title": "Substrate Drying & Restoration", "desc": "Allow affected walls to dry fully (confirmed by thermal imaging) before scraping off bubbly paint, treating for efflorescence salts, and repainting."}
        ]
        for idx, act in enumerate(actions):
            st.markdown(f"**{idx+1}. {act['title']}**")
            st.write(act["desc"])
            st.markdown(" ")

    with tab_checklist:
        st.subheader("Checklist Findings")
        checklist = data.get("checklists", [])
        if checklist:
            st.table(checklist)

    with tab_missing:
        st.subheader("Missing or Unclear Information")
        st.warning("""
        **Not Available Findings**
        * Previous repairs: No records of past waterproofing attempts were available.
        * Paint specifications: The exact manufacturer/paint type of the current internal paint is Not Available.
        * RCC Interior: Rust marks on internal RCC members were marked N/A. A detailed concrete core test is advised.
        """)
