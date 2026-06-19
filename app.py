import streamlit as st
import os
import io
import json
import tempfile
import logging
from PIL import Image

# Set page config with tab title and layout
st.set_page_config(
    page_title="UrbanRoof DDR Generator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from extractor import extract_pdf
from ai_generator import generate_ddr_data
from docx_export import export_to_docx

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
        margin-bottom: 20px;
    }
    th {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #93c5fd !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 13px !important;
        text-align: left;
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
        flex-shrink: 0;
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
</style>
""", unsafe_allow_html=True)

# Pre-compiled sample DDR response to allow instant offline testing
MOCK_SAMPLE_DDR = {
  "property_issue_summary": "The property (Flat No. 103) exhibits widespread moisture ingress and skirting-level dampness across the Hall, Bedrooms, and Kitchen. The seepage is heavily correlated with plumbing and waterproofing failures (e.g., tile joint gaps and hollowness) in the adjacent wet areas, including the Common Bathroom and Master Bedroom Bathroom. Active leakage has also migrated through the floor slab, causing visible ceiling dampness and structural seepage in the parking area below.",
  "area_wise_observations": [
    {
      "area_name": "Hall",
      "description": "Severe dampness is observed at the skirting level of the Hall. This is on the negative side of the Common Bathroom, where significant tile hollowness was noted. Thermal imaging (RB02380X.JPG) confirmed a temperature anomaly indicating active moisture movement behind the wall.",
      "inspection_page_refs": [3],
      "thermal_page_refs": [1],
      "image_refs": [
        {"source": "inspection", "page": 3, "image_index": 0},
        {"source": "inspection", "page": 3, "image_index": 1},
        {"source": "thermal", "page": 1, "image_index": 0},
        {"source": "thermal", "page": 1, "image_index": 1}
      ]
    },
    {
      "area_name": "Common Bedroom",
      "description": "Skirting-level dampness is present along the bedroom walls. The adjacent Common Bathroom exhibits tile hollowness and joint gaps, allowing water to saturate the sub-base and rise via capillary action. Thermal scan (RB02386X.JPG) shows clear cooler moisture patterns at the base of the wall.",
      "inspection_page_refs": [3],
      "thermal_page_refs": [2],
      "image_refs": [
        {"source": "inspection", "page": 3, "image_index": 11},
        {"source": "inspection", "page": 3, "image_index": 12},
        {"source": "thermal", "page": 2, "image_index": 0},
        {"source": "thermal", "page": 2, "image_index": 1}
      ]
    },
    {
      "area_name": "Master Bedroom",
      "description": "Significant skirting-level dampness is observed in the Master Bedroom. The positive side (Master Bedroom Bathroom) shows severe tile hollowness. Additionally, dampness is present on the bedroom wall, matching structural cracks on the external wall envelope and duct issues. Thermal readings (RB02395X.JPG, RB02403X.JPG) show notable temperature deltas corresponding to damp plaster.",
      "inspection_page_refs": [3, 4],
      "thermal_page_refs": [3, 5],
      "image_refs": [
        {"source": "inspection", "page": 3, "image_index": 19},
        {"source": "inspection", "page": 3, "image_index": 20},
        {"source": "inspection", "page": 4, "image_index": 0},
        {"source": "inspection", "page": 4, "image_index": 1},
        {"source": "thermal", "page": 3, "image_index": 0},
        {"source": "thermal", "page": 5, "image_index": 0}
      ]
    },
    {
      "area_name": "Kitchen",
      "description": "Dampness is rising along the Kitchen skirting. The adjoining wall borders the Master Bedroom Bathroom, which has waterproofing defects. The thermal scan (RB02402X.JPG) reveals localized cold zones indicating moisture accumulation.",
      "inspection_page_refs": [3, 4],
      "thermal_page_refs": [4],
      "image_refs": [
        {"source": "inspection", "page": 3, "image_index": 30},
        {"source": "inspection", "page": 4, "image_index": 2},
        {"source": "thermal", "page": 4, "image_index": 0},
        {"source": "thermal", "page": 4, "image_index": 1}
      ]
    },
    {
      "area_name": "Parking Area",
      "description": "Active water seepage and efflorescence are visible on the concrete ceiling of the parking lot directly below the flat. This correlates with the tile hollowness and plumbing issues in the Common Bathroom above, proving that moisture has penetrated the RCC slab.",
      "inspection_page_refs": [4, 5],
      "thermal_page_refs": [6],
      "image_refs": [
        {"source": "inspection", "page": 4, "image_index": 11},
        {"source": "inspection", "page": 5, "image_index": 0},
        {"source": "thermal", "page": 6, "image_index": 0}
      ]
    },
    {
      "area_name": "Common Bathroom",
      "description": "Mild dampness is noted at the ceiling of the Common Bathroom. The positive side exposes the toilet above (Flat 203), where tile joints are open and minor outlet leakage exists.",
      "inspection_page_refs": [5],
      "thermal_page_refs": [7],
      "image_refs": [
        {"source": "inspection", "page": 5, "image_index": 9},
        {"source": "inspection", "page": 5, "image_index": 10},
        {"source": "thermal", "page": 7, "image_index": 0}
      ]
    }
  ],
  "probable_root_cause": [
    {"area_name": "Hall & Common Bedroom", "cause": "Water penetration through open tile joints and hollow floor tiles in the Common Bathroom, leading to sub-base saturation and capillary rise."},
    {"area_name": "Master Bedroom & Kitchen", "cause": "Failed tile grouting and waterproofing barrier in the Master Bedroom Bathroom, combined with external facade cracks allowing rainwater ingress."},
    {"area_name": "Parking Area Ceiling", "cause": "Nahani trap leakages and waterproofing failure in the Common Bathroom floor, allowing gravity-driven water transit through the concrete slab."}
  ],
  "severity_assessment": [
    {"area_name": "Hall & Bedrooms", "severity": "Moderate", "reasoning": "Capillary moisture rise has caused peeling paint and salt deposit formation (efflorescence), requiring localized plaster treatment and repainting."},
    {"area_name": "Parking Area Ceiling", "severity": "High", "reasoning": "Ongoing seepage through the RCC structural slab can lead to concrete carbonation and steel reinforcement corrosion if not addressed."}
  ],
  "recommended_actions": [
    {"area_name": "Common & MB Bathrooms", "action": "Rake out old grout and apply high-performance epoxy regrouting on floors and walls. Seal junctions around plumbing traps."},
    {"area_name": "External Walls", "action": "Seal structural cracks on the external envelope using elastic polyurethane paint or specialized exterior crack fillers."},
    {"area_name": "Affected Rooms", "action": "Allow walls to dry completely (verified by thermal imaging) before scraping bubbly paint, treating for salts, and repainting."}
  ],
  "additional_notes": "A drying window of at least 15-20 days under dry weather conditions is recommended after waterproofing repairs before applying final paint coats. Continuous monitoring of moisture levels is advised.",
  "missing_or_unclear_information": [
    "Records of previous waterproofing treatments or structural audit results.",
    "Active leak rates from plumbing pipes inside the ducts."
  ]
}

# Sidebar configuration
st.sidebar.markdown("### ⚙️ Engine Settings")
st.sidebar.info("This application operates entirely in Python, processing PDF extraction and Word compilation locally.")

api_key_input = st.sidebar.text_input("Anthropic API Key", type="password", help="Provide your Anthropic API key to run active Claude analysis on custom uploaded PDFs.")

# Resolve API Key
def get_api_key():
    if api_key_input.strip():
        return api_key_input.strip()
    # Fallback to st.secrets
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    # Fallback to environment variable
    return os.environ.get("ANTHROPIC_API_KEY")

api_key = get_api_key()
if api_key:
    st.sidebar.success("Anthropic Key loaded successfully!")
else:
    st.sidebar.warning("No Anthropic Key detected. Custom compilation is locked, but you can load the sample report immediately.")

# Top Brand Header
st.markdown("""
<div class="brand-container">
    <div class="brand-icon">🏠</div>
    <div>
        <h1 class="brand-title">UrbanRoof DDR Generator</h1>
        <p class="brand-subtitle">Local Python-Native Site Inspection & Thermal Analysis Engine</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main File Uploader section
st.markdown("""
<div class="premium-card">
    <h3 style="margin-top:0; color:#fff; font-size:18px;">📄 Upload Diagnostics Data</h3>
    <p style="color:#94a3b8; font-size:13px; margin-bottom:20px;">Upload inspection text and Bosch thermal camera recordings to compile a client-ready Detailed Diagnostic Report (DDR).</p>
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
    # Disable active generate button if API key or files are missing
    generate_disabled = not (inspection_file and thermal_file and api_key)
    generate_btn = st.button("🚀 Compile DDR Client Report", use_container_width=True, type="primary", disabled=generate_disabled)
    
    if generate_disabled and inspection_file and thermal_file:
        st.caption("<div style='text-align:center; color:#f87171;'>Please provide an Anthropic API Key in the sidebar to enable compilation.</div>", unsafe_allow_html=True)
        
    sample_btn = st.button("📂 Load Pre-Compiled Sample Report", use_container_width=True)

# Initialize Session State
if "ddr_data" not in st.session_state:
    st.session_state.ddr_data = None
    st.session_state.inspection_data = None
    st.session_state.thermal_data = None
    st.session_state.docx_bytes = None

def run_compilation(insp_path, therm_path, use_mock_ai=False):
    # Setup status container
    with st.status("Initializing Local DDR Pipeline...", expanded=True) as status_box:
        # Step 1: Extract Inspection PDF
        status_box.update(label="Extracting inspection report...", state="running")
        logger.info("Extracting inspection report...")
        inspection_data = extract_pdf(insp_path)
        
        # Step 2: Extract Thermal PDF
        status_box.update(label="Extracting thermal report...", state="running")
        logger.info("Extracting thermal report...")
        thermal_data = extract_pdf(therm_path)
        
        # Step 3: Run Claude AI analysis or use pre-compiled mock
        status_box.update(label="Analyzing with AI (Claude Sonnet)...", state="running")
        logger.info("Running AI analysis...")
        if use_mock_ai:
            ddr_data = MOCK_SAMPLE_DDR
        else:
            # Temporarily inject API key for the generator
            os.environ["ANTHROPIC_API_KEY"] = api_key
            ddr_data = generate_ddr_data(inspection_data, thermal_data)
            
        if not ddr_data or "error" in ddr_data:
            status_box.update(label="AI Analysis Failed", state="error")
            raise ValueError(f"AI Generator error: {ddr_data.get('message') if ddr_data else 'Unknown'}")
            
        # Step 4: Build DOCX report with embedded images
        status_box.update(label="Building Word report document...", state="running")
        logger.info("Building Word report document...")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_docx_path = os.path.join(tmp_dir, "report.docx")
            export_to_docx(ddr_data, inspection_data, thermal_data, temp_docx_path)
            with open(temp_docx_path, "rb") as f:
                docx_bytes = f.read()
                
        status_box.update(label="DDR Client Report Compiled successfully!", state="complete")
        
        return ddr_data, inspection_data, thermal_data, docx_bytes

# Generate trigger
if generate_btn:
    try:
        # Write files to temp on disk for extraction
        with tempfile.TemporaryDirectory() as upload_tmp_dir:
            insp_path = os.path.join(upload_tmp_dir, "inspection.pdf")
            therm_path = os.path.join(upload_tmp_dir, "thermal.pdf")
            
            with open(insp_path, "wb") as f:
                f.write(inspection_file.getvalue())
            with open(therm_path, "wb") as f:
                f.write(thermal_file.getvalue())
                
            ddr_data, inspection_data, thermal_data, docx_bytes = run_compilation(insp_path, therm_path)
            
            # Save to session state
            st.session_state.ddr_data = ddr_data
            st.session_state.inspection_data = inspection_data
            st.session_state.thermal_data = thermal_data
            st.session_state.docx_bytes = docx_bytes
            
            st.success("Compilation finished!")
            
    except Exception as e:
        st.error(f"Compilation pipeline failed: {e}")

# Sample trigger
if sample_btn:
    try:
        sample_inspection_path = "Sample_Report.pdf"
        sample_thermal_path = "Thermal_Images.pdf"
        
        if not os.path.exists(sample_inspection_path) or not os.path.exists(sample_thermal_path):
            st.error("Sample PDF reports are not present in the workspace directory.")
        else:
            ddr_data, inspection_data, thermal_data, docx_bytes = run_compilation(
                sample_inspection_path, sample_thermal_path, use_mock_ai=True
            )
            
            # Save to session state
            st.session_state.ddr_data = ddr_data
            st.session_state.inspection_data = inspection_data
            st.session_state.thermal_data = thermal_data
            st.session_state.docx_bytes = docx_bytes
            
            st.success("Pre-compiled sample report loaded successfully!")
            
    except Exception as e:
        st.error(f"Sample compilation pipeline failed: {e}")

# Render Results
if st.session_state.ddr_data:
    ddr_data = st.session_state.ddr_data
    inspection_data = st.session_state.inspection_data
    thermal_data = st.session_state.thermal_data
    docx_bytes = st.session_state.docx_bytes
    
    st.markdown("<br><hr style='border-color:rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    st.markdown("## 📊 Rendered Detailed Diagnostic Report (DDR)")
    
    # Download button at the top for convenience
    if docx_bytes:
        st.download_button(
            label="📥 Download Client Report (.docx)",
            data=docx_bytes,
            file_name="UrbanRoof_Detailed_Diagnostic_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
    # UI Sections organized in order
    
    # 1. Property Issue Summary
    st.markdown("### 1. Property Summary")
    st.markdown(f"""
    <div class="premium-card" style="margin-bottom:30px;">
        <p style="color:#cbd5e1; font-size:14.5px; line-height:1.7; margin:0;">
            {ddr_data.get('property_issue_summary', 'Not Available')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Area-wise Observations
    st.markdown("### 2. Area-wise Observations")
    for area in ddr_data.get("area_wise_observations", []):
        area_name = area.get("area_name", "Unknown Area")
        desc = area.get("description", "Not Available")
        insp_refs = ", ".join(map(str, area.get("inspection_page_refs", []))) or "N/A"
        therm_refs = ", ".join(map(str, area.get("thermal_page_refs", []))) or "N/A"
        image_refs = area.get("image_refs", [])
        
        with st.expander(f"📌 {area_name}", expanded=True):
            st.markdown(f"""
            <div style="margin-bottom:15px; padding:15px; background:rgba(30, 41, 59, 0.2); border-radius:12px;">
                <p style="margin-top:0; line-height:1.6; color:#e2e8f0; font-size:14px;">{desc}</p>
                <div style="font-size:12px; color:#94a3b8; margin-top:8px;">
                    <strong>Inspection Page Refs:</strong> Page(s) {insp_refs} | 
                    <strong>Thermal Page Refs:</strong> Page(s) {therm_refs}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if image_refs:
                st.markdown("<p style='font-size:11.5px; font-weight:700; color:#cbd5e1; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;'>Extracted Images & Thermal Snapshots</p>", unsafe_allow_html=True)
                
                # Setup side-by-side layout (columns) for images in this expander
                img_cols = st.columns(min(4, len(image_refs)))
                for idx, ref in enumerate(image_refs):
                    source = ref.get("source")
                    page_num = ref.get("page")
                    img_idx = ref.get("image_index")
                    
                    target_pdf = inspection_data if source == "inspection" else thermal_data
                    target_page = next((p for p in target_pdf["pages"] if p["page"] == page_num), None)
                    
                    col = img_cols[idx % len(img_cols)]
                    
                    if target_page and img_idx < len(target_page["images"]):
                        pil_img = target_page["images"][img_idx]
                        
                        # Display Image inline in columns
                        with col:
                            st.image(
                                pil_img, 
                                caption=f"{source.capitalize()} P.{page_num} Image {img_idx}",
                                use_container_width=True
                            )
                    else:
                        with col:
                            st.caption(f"Image {source}_p{page_num}_idx{img_idx} (Not Available)")
            else:
                st.caption("No images referenced for this area.")
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Probable Root Cause
    st.markdown("### 3. Probable Root Cause Analysis")
    root_causes = ddr_data.get("probable_root_cause", [])
    if root_causes:
        html_rc = "<table><thead><tr><th>Impacted Area</th><th>Root Cause Finding</th></tr></thead><tbody>"
        for rc in root_causes:
            html_rc += f"<tr><td><strong>{rc.get('area_name', 'Not Available')}</strong></td><td>{rc.get('cause', 'Not Available')}</td></tr>"
        html_rc += "</tbody></table>"
        st.markdown(html_rc, unsafe_allow_html=True)
    else:
        st.info("No root cause mappings generated.")
        
    # 4. Severity Assessment
    st.markdown("### 4. Structural Severity Assessment")
    severities = ddr_data.get("severity_assessment", [])
    if severities:
        for item in severities:
            sev = item.get("severity", "Low")
            badge_class = "badge-green"
            if sev.lower() == "high":
                badge_class = "badge-red"
            elif sev.lower() == "moderate":
                badge_class = "badge-yellow"
                
            st.markdown(f"""
            <div class="premium-card" style="padding:16px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="font-size:15px; color:#fff;">{item.get('area_name', 'Not Available')}</strong>
                    <span class="custom-badge {badge_class}">{sev.upper()}</span>
                </div>
                <p style="color:#cbd5e1; font-size:13.5px; margin:0; line-height:1.6;">
                    {item.get('reasoning', 'Not Available')}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No severity assessments generated.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5. Recommended Actions
    st.markdown("### 5. Recommended Remedial Actions")
    actions = ddr_data.get("recommended_actions", [])
    if actions:
        for idx, act in enumerate(actions):
            st.markdown(f"""
            <div class="action-step-card">
                <div class="action-step-number">{idx+1}</div>
                <div>
                    <div class="action-step-title">{act.get('area_name', 'Not Available')}</div>
                    <div class="action-step-desc">{act.get('action', 'Not Available')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recommended actions generated.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6. Additional Notes
    st.markdown("### 6. Additional Notes & Guidelines")
    st.markdown(f"""
    <div class="premium-card" style="padding:20px;">
        <p style="color:#cbd5e1; font-size:13.5px; line-height:1.6; margin:0;">
            {ddr_data.get('additional_notes', 'Not Available')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 7. Missing or Unclear Information
    st.markdown("### 7. Missing or Unclear Information")
    missing_info = ddr_data.get("missing_or_unclear_information", [])
    if missing_info:
        warning_content = "<strong>Flagged items needing verification:</strong><ul style='margin-top:8px; margin-bottom:0; padding-left:20px; font-size:13px; line-height:1.6; color:#fef08a;'>"
        for item in missing_info:
            warning_content += f"<li>{item}</li>"
        warning_content += "</ul>"
        st.warning(warning_content, icon="⚠️")
    else:
        st.info("No missing or unclear information was flagged.")
        
    # Download button at the bottom
    st.markdown("<br><hr style='border-color:rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    if docx_bytes:
        st.download_button(
            label="📥 Download Client Report (.docx)",
            data=docx_bytes,
            file_name="UrbanRoof_Detailed_Diagnostic_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True,
            key="download_bottom"
        )
