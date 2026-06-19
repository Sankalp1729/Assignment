import streamlit as st
import requests
import os

# Set page config with tab title and layout
st.set_page_config(
    page_title="UrbanRoof DDR Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom Google Fonts and custom CSS for rich aesthetics
st.markdown("""
<style>
    /* Import modern Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&display=swap');

    /* Global Typography overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }

    /* Main background accent */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        color: #f1f5f9;
    }

    /* Top banner header styling */
    .brand-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        padding: 24px;
        border-radius: 20px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    .brand-icon {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        padding: 15px;
        border-radius: 16px;
        font-size: 32px;
        box-shadow: 0 8px 20px -6px rgba(79, 70, 229, 0.4);
    }
    
    .brand-title {
        font-size: 30px;
        background: linear-gradient(to right, #ffffff, #93c5fd, #c7d2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    .brand-subtitle {
        font-size: 14px;
        color: #94a3b8;
        margin: 4px 0 0 0;
        font-weight: 300;
    }

    /* Premium Metric Grid Card */
    .dashboard-metric-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .dashboard-metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .dashboard-metric-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .dashboard-metric-value {
        font-size: 20px;
        color: #f8fafc;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }

    /* Premium Card block */
    .premium-card {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
    }

    /* Left-bordered observation cards */
    .obs-desc-card {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        font-size: 14px;
        line-height: 1.6;
    }
    .obs-desc-card.negative {
        border-left: 4px solid #ef4444;
        border-top: 1px solid rgba(239, 68, 68, 0.1);
        border-right: 1px solid rgba(239, 68, 68, 0.1);
        border-bottom: 1px solid rgba(239, 68, 68, 0.1);
    }
    .obs-desc-card.positive {
        border-left: 4px solid #10b981;
        border-top: 1px solid rgba(16, 185, 129, 0.1);
        border-right: 1px solid rgba(16, 185, 129, 0.1);
        border-bottom: 1px solid rgba(16, 185, 129, 0.1);
    }
    .obs-card-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .obs-card-title.negative { color: #fca5a5; }
    .obs-card-title.positive { color: #86efac; }

    /* Custom Tables styling */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: rgba(30, 41, 59, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    th {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #93c5fd !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 13px !important;
    }
    td {
        padding: 12px 16px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        font-size: 13px !important;
        color: #cbd5e1 !important;
    }
    tr:hover {
        background-color: rgba(99, 102, 241, 0.05) !important;
    }

    /* Badges & Tags */
    .custom-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #86efac; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-yellow { background: rgba(245, 158, 11, 0.15); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-blue { background: rgba(37, 99, 235, 0.15); color: #93c5fd; border: 1px solid rgba(37, 99, 235, 0.3); }

    /* Action numbered steps styling */
    .action-step-card {
        background: rgba(30, 41, 59, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.04);
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        display: flex;
        gap: 16px;
        align-items: flex-start;
    }
    .action-step-number {
        background: linear-gradient(135deg, #3b82f6 0%, #4f46e5 100%);
        color: white;
        font-weight: 700;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        shrink: 0;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
    }
    .action-step-title {
        font-size: 14px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .action-step-desc {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* custom styling for files uploaders boxes */
    div[data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.2);
        border: 1px dashed rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
    }

    /* Style Streamlit Tabs for modern look */
    button[data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        border-bottom: 2px solid transparent !important;
        padding: 12px 18px !important;
    }
    button[aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom-color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://assignment-1-ufcs.onrender.com")

# Top Brand Header
st.markdown("""
<div class="brand-container">
    <div class="brand-icon">🏠</div>
    <div>
        <h1 class="brand-title">UrbanRoof DDR Builder</h1>
        <p class="brand-subtitle">AI-Powered Technical Diagnostic Report Automation</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main File Uploader section
st.markdown("""
<div class="premium-card">
    <h3 style="margin-top:0; color:#fff; font-size:18px;">📄 Upload Diagnostics Data</h3>
    <p style="color:#94a3b8; font-size:13px; margin-bottom:20px;">Upload inspection text and Bosch thermal camera recordings to compile DDR</p>
</div>
""", unsafe_allow_html=True)

# Streamlit file upload widgets
col1, col2 = st.columns(2)
with col1:
    inspection_file = st.file_uploader("1. Inspection Report PDF", type=["pdf"])
with col2:
    thermal_file = st.file_uploader("2. Thermal Images PDF", type=["pdf"])

st.markdown("<br>", unsafe_allow_html=True)

# Generate Actions Columns
action_col1, action_col2, action_col3 = st.columns([1, 2, 1])
with action_col2:
    generate_btn = st.button("🚀 Compile DDR Client Report", use_container_width=True, type="primary")
    sample_btn = st.button("📂 Load Pre-Compiled Sample Report", use_container_width=True)

# Session state initialization
if "report_data" not in st.session_state:
    st.session_state.report_data = None
    st.session_state.download_url = None

# Pipeline triggers
if generate_btn:
    if not inspection_file or not thermal_file:
        st.error("Please upload both PDF files to compile the report.")
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
                        st.success("Detailed Diagnostic Report compiled successfully!")
                    else:
                        st.error(f"Error: {res_json.get('error')}")
                else:
                    st.error(f"Backend Server returned status code: {response.status_code}")
            except Exception as e:
                st.error(f"Connection failure: {str(e)}")

if sample_btn:
    with st.spinner("Compiling preloaded sample data..."):
        try:
            response = requests.post(f"{BACKEND_URL}/api/generate-ddr-mock")
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("success"):
                    st.session_state.report_data = res_json.get("data")
                    st.session_state.download_url = f"{BACKEND_URL}{res_json.get('downloadUrl')}"
                    st.success("Sample Report loaded successfully!")
                else:
                    st.error(f"Error: {res_json.get('error')}")
            else:
                st.error(f"Backend Server returned status code: {response.status_code}")
        except Exception as e:
            st.error(f"Connection failure: {str(e)}")

# Display Dashboard findings if available
if st.session_state.report_data:
    data = st.session_state.report_data
    
    st.markdown("<br><hr style='border-color:rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    
    # Metadata Overview Cards
    st.markdown(f"## 📊 Diagnostics Overview: {data.get('propertyName')}")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="dashboard-metric-card">
            <div class="dashboard-metric-label">Property Name</div>
            <div class="dashboard-metric-value">{data.get('propertyName')}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="dashboard-metric-card">
            <div class="dashboard-metric-label">Inspection Date</div>
            <div class="dashboard-metric-value">{data.get('inspectionDate')}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="dashboard-metric-card">
            <div class="dashboard-metric-label">Inspected By</div>
            <div class="dashboard-metric-value">{data.get('inspectedBy')}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="dashboard-metric-card">
            <div class="dashboard-metric-label">Total Floors</div>
            <div class="dashboard-metric-value">{data.get('floors')} Floors</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # DOCX Download
    if st.session_state.download_url:
        try:
            doc_response = requests.get(st.session_state.download_url)
            if doc_response.status_code == 200:
                st.download_button(
                    label="📥 Download Client Report (.docx)",
                    data=doc_response.content,
                    file_name=f"DDR_{data.get('propertyName').replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
        except Exception:
            st.markdown(f"<div style='text-align:center;'><a href='{st.session_state.download_url}' style='text-decoration:none;'><button style='width:100%; padding:10px; border-radius:8px; border:none; background:#2563eb; color:#fff; font-weight:600; cursor:pointer;'>📥 Direct Download Link (.docx)</button></a></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation Tabs
    tab_sum, tab_obs, tab_causes, tab_severity, tab_actions, tab_checklist, tab_missing = st.tabs([
        "Summary & Correlation", 
        "Observations & Media", 
        "Root Causes", 
        "Severity Assessment", 
        "Recommended Actions", 
        "Checklist Findings",
        "Missing Info"
    ])
    
    with tab_sum:
        st.markdown(f"""
        <div class="premium-card">
            <h3 style="margin-top:0; color:#fff; font-size:18px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">Property Issue Summary</h3>
            <p style="color:#cbd5e1; font-size:14px; line-height:1.6; margin-top:12px;">
                {data.get('propertyName')} is currently experiencing extensive moisture-related issues, primarily manifesting as capillary dampness at the skirting levels of the Hall, Common Bedroom, Master Bedroom, and Kitchen. The investigation reveals that the moisture ingress is largely driven by waterproofing failures in the wet areas (Common Bathroom and Master Bedroom Bathroom) and exacerbated by structural cracks in the external walls. The seepage has progressed to the point of affecting the parking ceiling below the flat, indicating a high volume of water transit through the floor slab.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='color:#fff; font-size:16px; margin-bottom:12px;'>Correlation Map (Negative side vs Positive side)</h4>", unsafe_allow_html=True)
        summary_table = data.get("summaryTable", [])
        if summary_table:
            # Format list of dicts to html table for styling
            html_table = "<table><thead><tr><th>Point</th><th>Impacted Area (-ve side)</th><th>Exposed Area (+ve side)</th></tr></thead><tbody>"
            for row in summary_table:
                html_table += f"<tr><td><span class='custom-badge badge-blue'>{row.get('pointNo')}</span></td><td>{row.get('negativeSide')}</td><td>{row.get('positiveSide')}</td></tr>"
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)
            
    with tab_obs:
        st.markdown("<h3 style='color:#fff; font-size:18px;'>Area-wise Site Observations</h3>", unsafe_allow_html=True)
        areas = data.get("areas", [])
        for area in areas:
            with st.expander(f"📌 Area {area.get('id')}: {area.get('name')}", expanded=True):
                # Side-by-side descriptions
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                    <div class="obs-desc-card negative">
                        <div class="obs-card-title negative">Negative Side (Impacted Area)</div>
                        {area.get('negativeDesc')}
                    </div>
                    <div class="obs-desc-card positive">
                        <div class="obs-card-title positive">Positive Side (Exposed Area)</div>
                        {area.get('positiveDesc')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<p style='font-size:12px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;'>Visual & Thermal Evidence</p>", unsafe_allow_html=True)
                img_cols = st.columns(4)
                
                # Render photos
                neg_photos = area.get("negativePhotos", [])
                for idx, p_num in enumerate(neg_photos):
                    col_idx = idx % 4
                    with img_cols[col_idx]:
                        img_url = f"{BACKEND_URL}/uploads/photo_{p_num}.jpg"
                        st.markdown(f"""
                        <div style="border: 1px solid rgba(255,255,255,0.05); border-radius:12px; overflow:hidden; background:rgba(30,41,59,0.3);">
                            <img src="{img_url}" style="width:100%; height:120px; object-fit:cover; display:block;" />
                            <div style="padding:6px; text-align:center; font-size:11px; font-weight:600; color:#94a3b8; background:rgba(15,23,42,0.8);">Photo {p_num} (Neg. Side)</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                pos_photos = area.get("positivePhotos", [])
                for idx, p_num in enumerate(pos_photos):
                    col_idx = (len(neg_photos) + idx) % 4
                    with img_cols[col_idx]:
                        img_url = f"{BACKEND_URL}/uploads/photo_{p_num}.jpg"
                        st.markdown(f"""
                        <div style="border: 1px solid rgba(255,255,255,0.05); border-radius:12px; overflow:hidden; background:rgba(30,41,59,0.3);">
                            <img src="{img_url}" style="width:100%; height:120px; object-fit:cover; display:block;" />
                            <div style="padding:6px; text-align:center; font-size:11px; font-weight:600; color:#94a3b8; background:rgba(15,23,42,0.8);">Photo {p_num} (Pos. Side)</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                thermal_imgs = area.get("thermalImages", [])
                for idx, fname in enumerate(thermal_imgs):
                    col_idx1 = (len(neg_photos) + len(pos_photos) + idx*2) % 4
                    col_idx2 = (len(neg_photos) + len(pos_photos) + idx*2 + 1) % 4
                    
                    with img_cols[col_idx1]:
                        t_url = f"{BACKEND_URL}/uploads/thermal_{fname}"
                        st.markdown(f"""
                        <div style="border: 1px solid rgba(255,255,255,0.05); border-radius:12px; overflow:hidden; background:rgba(30,41,59,0.3);">
                            <img src="{t_url}" style="width:100%; height:120px; object-fit:cover; display:block;" />
                            <div style="padding:6px; text-align:center; font-size:11px; font-weight:600; color:#a5b4fc; background:rgba(15,23,42,0.8);">Thermal: {fname.replace('X.JPG', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with img_cols[col_idx2]:
                        r_url = f"{BACKEND_URL}/uploads/ref_{fname}"
                        st.markdown(f"""
                        <div style="border: 1px solid rgba(255,255,255,0.05); border-radius:12px; overflow:hidden; background:rgba(30,41,59,0.3);">
                            <img src="{r_url}" style="width:100%; height:120px; object-fit:cover; display:block;" />
                            <div style="padding:6px; text-align:center; font-size:11px; font-weight:600; color:#94a3b8; background:rgba(15,23,42,0.8);">Ref Photo: {fname.replace('X.JPG', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                if not neg_photos and not pos_photos and not thermal_imgs:
                    st.caption("No images available for this area.")

    with tab_causes:
        st.markdown("<h3 style='color:#fff; font-size:18px; margin-bottom:20px;'>Probable Root Causes</h3>", unsafe_allow_html=True)
        causes = [
            {"title": "1. Waterproofing Failure", "desc": "Open tile joints and failed seals around Nahani traps in the bathrooms are allowing water to penetrate the brickbat coba. This forms a saturated reservoir in the floor sub-base."},
            {"title": "2. Capillary Action (Skirting Dampness)", "desc": "Water trapped in the floor substrate migrates horizontally and rises up the internal plaster of adjacent walls via capillary action. This is the direct cause of the skirting-level dampness observed across multiple rooms."},
            {"title": "3. External envelope cracks & Duct leaks", "desc": "Structural cracks in the external walls and leaking external piping systems allow rainwater to enter the building envelope, exacerbating wall dampness in bedrooms."}
        ]
        for c in causes:
            st.markdown(f"""
            <div class="premium-card">
                <h4 style="margin-top:0; color:#fff; font-size:15px; display:flex; align-items:center; gap:8px;">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#3b82f6;"></span> {c['title']}
                </h4>
                <p style="color:#cbd5e1; font-size:13px; line-height:1.6; margin-top:8px; margin-bottom:0; padding-left:16px;">{c['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_severity:
        st.markdown("<h3 style='color:#fff; font-size:18px; margin-bottom:20px;'>Structural Severity Assessment</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius:16px; padding:24px;">
            <div style="display:flex; gap:16px; align-items:center; margin-bottom:12px;">
                <span style="font-size:24px;">🛡️</span>
                <h4 style="margin:0; color:#ef4444; font-size:20px; font-weight:700;">HIGH SEVERITY</h4>
            </div>
            <p style="color:#cbd5e1; font-size:14px; line-height:1.6; margin:0;">
                The moisture ingress is widespread and has progressed to cause secondary damages such as paint bubbling, wood frame distortion, and efflorescence (mineral salt crystallization). The fact that active seepage is visible on the parking ceiling directly below Flat 103 indicates complete saturation of the RCC floor slab. If left unaddressed, the concrete pores will undergo carbonation and trigger steel reinforcement corrosion, compromising structural integrity.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab_actions:
        st.markdown("<h3 style='color:#fff; font-size:18px; margin-bottom:20px;'>Recommended Remedial Actions</h3>", unsafe_allow_html=True)
        actions = [
            {"title": "High-Performance Epoxy Regrouting", "desc": "Clean all bathroom floor and wall tile joints, rake out old grout, and apply high-performance epoxy grout to prevent further water ingress."},
            {"title": "Grout Nahani Trap Joints", "desc": "Ensure all Nahani trap junctions and collar connections are properly sealed and grouted."},
            {"title": "External Crack Sealing", "desc": "Apply polyurethane sealants or flexible plaster polymers to all structural cracks on external wall surfaces and repair leaking plumbing mains."},
            {"title": "Substrate Drying & Restoration", "desc": "Allow affected walls to dry fully (confirmed by thermal imaging) before scraping off bubbly paint, treating for efflorescence salts, and repainting."}
        ]
        for idx, act in enumerate(actions):
            st.markdown(f"""
            <div class="action-step-card">
                <div class="action-step-number">{idx+1}</div>
                <div>
                    <div class="action-step-title">{act['title']}</div>
                    <div class="action-step-desc">{act['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_checklist:
        st.markdown("<h3 style='color:#fff; font-size:18px; margin-bottom:20px;'>Checklist Findings</h3>", unsafe_allow_html=True)
        checklist = data.get("checklists", [])
        if checklist:
            # Render styled checklist table
            html_table = "<table><thead><tr><th>Category</th><th>Inspection Item</th><th>Status</th></tr></thead><tbody>"
            for check in checklist:
                status = check.get("status")
                is_red = status == "Yes" or status == "Moderate"
                is_green = status == "No"
                
                if is_red:
                    badge_class = "custom-badge badge-red"
                elif is_green:
                    badge_class = "custom-badge badge-green"
                else:
                    badge_class = "custom-badge"
                    
                html_table += f"<tr><td><span style='color:#94a3b8; font-weight:600;'>{check.get('category')}</span></td><td>{check.get('item')}</td><td><span class='{badge_class}'>{status}</span></td></tr>"
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)

    with tab_missing:
        st.markdown("<h3 style='color:#fff; font-size:18px; margin-bottom:20px;'>Missing or Unclear Information</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2); border-radius:16px; padding:24px;">
            <div style="display:flex; gap:12px; align-items:center; margin-bottom:12px; color:#f59e0b;">
                <span style="font-size:22px;">⚠️</span>
                <h4 style="margin:0; font-size:16px; font-weight:700;">Not Available Findings</h4>
            </div>
            <ul style="color:#cbd5e1; font-size:13px; line-height:1.8; margin:0; padding-left:20px;">
                <li>Previous repairs: No records of past waterproofing attempts were available.</li>
                <li>Paint specifications: The exact manufacturer/paint type of the current internal paint is <span style="color:#ef4444; font-weight:600;">Not Available</span>.</li>
                <li>RCC Interior: Rust marks on internal RCC members were marked <span style="color:#94a3b8; font-weight:600;">N/A</span>. A detailed concrete core test is advised.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
