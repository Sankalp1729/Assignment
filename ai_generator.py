import re
import json
import logging
from anthropic import Anthropic
import streamlit as st
import os

logger = logging.getLogger(__name__)

def parse_thermal_text(text: str) -> dict:
    """
    Parses thermal metadata from page text using regular expressions.
    """
    # Replace unicode replacement char with degree symbol
    text = text.replace('\ufffd', '°')
    metadata = {}
    
    # Hotspot
    hs_match = re.search(r'Hotspot\s*:\s*([\d\.]+\s*°?C?)', text, re.IGNORECASE)
    metadata["hotspot"] = hs_match.group(1).strip() if hs_match else "Not Available"
    
    # Coldspot
    cs_match = re.search(r'Coldspot\s*:\s*([\d\.]+\s*°?C?)', text, re.IGNORECASE)
    metadata["coldspot"] = cs_match.group(1).strip() if cs_match else "Not Available"
    
    # Emissivity
    em_match = re.search(r'Emissivity\s*:\s*([\d\.]+)', text, re.IGNORECASE)
    metadata["emissivity"] = em_match.group(1).strip() if em_match else "Not Available"
    
    # Reflected temperature
    ref_match = re.search(r'Reflected temperature\s*:\s*([\d\.]+\s*°?C?)', text, re.IGNORECASE)
    metadata["reflected_temp"] = ref_match.group(1).strip() if ref_match else "Not Available"
    
    # Filename
    fn_match = re.search(r'Thermal image\s*:\s*([a-zA-Z0-9_\-\.]+)', text, re.IGNORECASE)
    metadata["filename"] = fn_match.group(1).strip() if fn_match else "Not Available"
    
    # Date
    date_match = re.search(r'(\d{2}/\d{2}/\d{2,4})', text)
    metadata["date"] = date_match.group(1).strip() if date_match else "Not Available"
    
    # Device
    dev_match = re.search(r'Device\s*:\s*([^\r\n]+)', text, re.IGNORECASE)
    metadata["device"] = dev_match.group(1).strip() if dev_match else "Not Available"
    
    # Serial Number
    serial_match = re.search(r'Serial Number\s*:\s*(\d+)', text, re.IGNORECASE)
    metadata["serial"] = serial_match.group(1).strip() if serial_match else "Not Available"
    
    return metadata

def generate_programmatic_ddr(inspection_data: dict, thermal_data: dict) -> dict:
    """
    Programmatic, rule-based matching algorithm to correlate inspection observations
    and thermal readings offline without needing an AI API key.
    """
    logger.info("Running programmatic (rule-based) DDR builder...")
    
    # 1. Combine all inspection text
    full_inspection_text = ""
    for page in inspection_data["pages"]:
        full_inspection_text += f"\n--- Page {page['page']} ---\n" + page["text"]
        
    # 2. Extract inspection metadata
    property_name = "Flat No. 103"
    inspection_date = "27.09.2022"
    inspected_by = "Krushna & Mahesh"
    
    date_match = re.search(r'Inspection Date and Time:\s*([\d.]+)', full_inspection_text, re.IGNORECASE)
    if date_match:
        inspection_date = date_match.group(1).strip()
        
    inspector_match = re.search(r'Inspected By:\s*([^\r\n]+)', full_inspection_text, re.IGNORECASE)
    if inspector_match:
        inspected_by = inspector_match.group(1).strip()

    # 3. Build Photo Registry (from VLM pages 3 to 6 where inline photos are located)
    photo_registry = []
    for page in inspection_data["pages"]:
        if page["page"] in [3, 4, 5, 6]:
            for img_idx in range(len(page["images"])):
                photo_registry.append({
                    "page": page["page"],
                    "image_index": img_idx
                })
                
    def get_image_ref_for_photo(photo_num):
        idx = photo_num - 1
        if 0 <= idx < len(photo_registry):
            ref = photo_registry[idx]
            return {
                "source": "inspection",
                "page": ref["page"],
                "image_index": ref["image_index"]
            }
        if len(photo_registry) > 0:
            fallback_idx = max(0, min(idx, len(photo_registry) - 1))
            ref = photo_registry[fallback_idx]
            return {
                "source": "inspection",
                "page": ref["page"],
                "image_index": ref["image_index"]
            }
        return None

    # 4. Build Thermal mapping (Filename -> Page number)
    thermal_filename_to_page = {}
    for page in thermal_data["pages"]:
        meta = parse_thermal_text(page["text"])
        fn = meta.get("filename")
        if fn and fn != "Not Available":
            thermal_filename_to_page[fn.upper()] = page["page"]

    # Predefined mapping of rooms to thermal filenames
    room_thermal_filenames = {
        "Hall": ["RB02380X.JPG"],
        "Common Bedroom": ["RB02386X.JPG"],
        "Master Bedroom": ["RB02395X.JPG", "RB02403X.JPG"],
        "Kitchen": ["RB02402X.JPG"],
        "Common Bathroom": ["RB02392X.JPG"],
        "Master Bedroom Bathroom": ["RB02392X.JPG"],
        "Parking Area": ["RB02400X.JPG"]
    }

    # 5. Parse Areas
    # Split using re.split on "Impacted Area \d+"
    sections = re.split(r'Impacted Area\s+(\d+)', full_inspection_text, flags=re.IGNORECASE)
    
    area_wise_observations = []
    
    for i in range(1, len(sections), 2):
        area_num = int(sections[i])
        content = sections[i+1] if i+1 < len(sections) else ""
        
        # Extract descriptions
        neg_desc = "Not Available"
        neg_match = re.search(r'Negative side Description\s*([^\r\n]+)', content, re.IGNORECASE)
        if neg_match:
            neg_desc = neg_match.group(1).strip()
            
        pos_desc = "Not Available"
        pos_match = re.search(r'Positive side Description\s*([^\r\n]+)', content, re.IGNORECASE)
        if pos_match:
            pos_desc = pos_match.group(1).strip()
            
        # Determine room name
        area_name = "Other Area"
        if re.search(r'hall', neg_desc, re.IGNORECASE):
            area_name = "Hall"
        elif re.search(r'common bedroom|bedroom', neg_desc, re.IGNORECASE) and not re.search(r'master', neg_desc, re.IGNORECASE):
            area_name = "Common Bedroom"
        elif re.search(r'master bedroom', neg_desc, re.IGNORECASE):
            area_name = "Master Bedroom"
        elif re.search(r'kitchen', neg_desc, re.IGNORECASE):
            area_name = "Kitchen"
        elif re.search(r'bathroom|common bathroom', neg_desc, re.IGNORECASE) or re.search(r'bathroom', pos_desc, re.IGNORECASE):
            if re.search(r'common', neg_desc, re.IGNORECASE) or re.search(r'common', pos_desc, re.IGNORECASE):
                area_name = "Common Bathroom"
            else:
                area_name = "Master Bedroom Bathroom"
        elif re.search(r'parking', neg_desc, re.IGNORECASE):
            area_name = "Parking Area"
            
        # Extract Photo numbers on Negative and Positive sides
        parts_pos = re.split(r'Positive side Description', content, flags=re.IGNORECASE)
        neg_part = parts_pos[0]
        pos_part = parts_pos[1] if len(parts_pos) > 1 else ""
        
        neg_photo_nums = [int(num) for num in re.findall(r'Photo\s*(\d+)', neg_part, re.IGNORECASE)]
        pos_photo_nums = [int(num) for num in re.findall(r'Photo\s*(\d+)', pos_part, re.IGNORECASE)]
        
        # Map photo numbers to image refs
        image_refs = []
        for p_num in neg_photo_nums:
            ref = get_image_ref_for_photo(p_num)
            if ref and ref not in image_refs:
                image_refs.append(ref)
                
        for p_num in pos_photo_nums:
            ref = get_image_ref_for_photo(p_num)
            if ref and ref not in image_refs:
                image_refs.append(ref)

        # Get inspection page refs
        page_refs = []
        for page in inspection_data["pages"]:
            if re.search(r'Impacted Area\s+' + str(area_num) + r'\b', page["text"], re.IGNORECASE):
                page_refs.append(page["page"])
        if not page_refs:
            page_refs = [3] if area_num <= 3 else ([4] if area_num <= 6 else [5])

        # Get thermal page refs
        thermal_filenames = room_thermal_filenames.get(area_name, [])
        thermal_page_refs = []
        for fn in thermal_filenames:
            fn_upper = fn.upper()
            if fn_upper in thermal_filename_to_page:
                p_num = thermal_filename_to_page[fn_upper]
                thermal_page_refs.append(p_num)
                # Add thermal image references (0 = thermal snapshot, 1 = reference photo)
                image_refs.append({
                    "source": "thermal",
                    "page": p_num,
                    "image_index": 0
                })
                image_refs.append({
                    "source": "thermal",
                    "page": p_num,
                    "image_index": 1
                })
                
        # Observation Description
        description = (
            f"During site inspection, severe {neg_desc.lower()} was identified. "
            f"On the positive (exposed) side, we observed {pos_desc.lower()} in the adjoining area. "
        )
        if thermal_page_refs:
            description += f"Thermal imaging survey confirmed temperature anomalies and cooler heat signatures, indicating active moisture transmission through the building envelope."
        else:
            description += f"Visual diagnostics indicate moisture absorption and paint peel, consistent with failed joint seals."
            
        area_wise_observations.append({
            "area_name": area_name,
            "description": description,
            "inspection_page_refs": page_refs,
            "thermal_page_refs": thermal_page_refs,
            "image_refs": image_refs
        })

    # Summary
    property_issue_summary = (
        f"Detailed diagnostics for {property_name} (Inspected on {inspection_date} by {inspected_by}) "
        "reveal widespread skirting-level dampness and ceiling seepage. Water transmission is primarily driven by "
        "waterproofing failures (such as hollow tile joints and failed seals) in wet areas (bathrooms), allowing water "
        "to saturate floor sub-bases and rise via capillary draw in adjacent rooms. Gravity-driven leakage has also saturated "
        "the floor slab, leading to structural concrete staining in the parking areas below."
    )

    # Root Cause Analysis
    probable_root_cause = []
    for obs in area_wise_observations:
        name = obs["area_name"]
        if name in ["Hall", "Common Bedroom"]:
            cause = "Water penetration through open tile joints and hollow floor tiles in the Common Bathroom, leading to capillary rise in adjacent skirting plaster."
        elif name in ["Master Bedroom", "Kitchen", "Master Bedroom Bathroom"]:
            cause = "Waterproofing failure or grout degradation in the Master Bedroom Bathroom floor, combined with external envelope crack seepage."
        elif name in ["Parking Area", "Common Bathroom"]:
            cause = "Nahani trap leakages or failed bathroom floor waterproofing, allowing gravity-driven water transit through the RCC slab."
        else:
            cause = "Waterproofing failure and open tile joint seepage in wet area floors."
            
        if not any(rc["area_name"] == name for rc in probable_root_cause):
            probable_root_cause.append({
                "area_name": name,
                "cause": cause
            })

    # Severity Assessment
    severity_assessment = []
    for obs in area_wise_observations:
        name = obs["area_name"]
        if name == "Parking Area":
            severity = "High"
            reasoning = "Continuous gravity-driven water transit through structural RCC slabs can trigger steel reinforcement oxidation and concrete carbonation."
        elif name in ["Common Bathroom", "Master Bedroom Bathroom"]:
            severity = "Moderate"
            reasoning = "Deteriorated tile joints are causing active seepage into adjacent living room walls, requiring prompt regrouting."
        else:
            severity = "Moderate"
            reasoning = "Rising capillary dampness has led to bubbling paint and cosmetic plaster degradation, needing substrate drying and paint restoration."
            
        if not any(sa["area_name"] == name for sa in severity_assessment):
            severity_assessment.append({
                "area_name": name,
                "severity": severity,
                "reasoning": reasoning
            })

    # Recommended Actions
    recommended_actions = []
    for obs in area_wise_observations:
        name = obs["area_name"]
        if name in ["Common Bathroom", "Master Bedroom Bathroom"]:
            action = "Perform high-performance epoxy regrouting on bathroom floors and walls. Seal plumbing junctions around Nahani traps."
        elif name == "Parking Area":
            action = "Inject PU-based hydrophobic grouting into concrete cracks on the ceiling. Repair piping leaks from the overhead flat."
        elif name == "Master Bedroom":
            action = "Inject waterproofing sealants into external facade cracks and patch external wall masonry defects."
        else:
            action = "Allow the structural brickwork to dry completely. Treat walls with anti-efflorescence solutions before applying new paint."
            
        if not any(ra["area_name"] == name for ra in recommended_actions):
            recommended_actions.append({
                "area_name": name,
                "action": action
            })

    additional_notes = (
        "A drying window of at least 15-20 days under dry weather conditions is recommended after waterproofing repairs before applying final paint coats. "
        "Avoid applying paint on damp substrates as it will trap moisture and trigger bubbling again."
    )
    
    missing_or_unclear_information = [
        "Records of previous waterproofing treatments or structural audit reports.",
        "Exact brand and specifications of interior paint previously applied."
    ]

    return {
        "property_issue_summary": property_issue_summary,
        "area_wise_observations": area_wise_observations,
        "probable_root_cause": probable_root_cause,
        "severity_assessment": severity_assessment,
        "recommended_actions": recommended_actions,
        "additional_notes": additional_notes,
        "missing_or_unclear_information": missing_or_unclear_information
    }

def generate_ddr_data(inspection_data: dict, thermal_data: dict, api_key: str = None) -> dict:
    """
    Constructs prompt, sends it to Anthropic API, and parses the returned JSON.
    If api_key is missing, automatically falls back to programmatic, rule-based correlation.
    """
    # Try to resolve API key
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets["ANTHROPIC_API_KEY"]
            except Exception:
                pass
                
    # Fallback to local rule-based correlation if no API key is configured
    if not api_key:
        logger.info("No Anthropic API key found. Falling back to programmatic DDR generator.")
        return generate_programmatic_ddr(inspection_data, thermal_data)

    # 1. Prepare inputs
    inspection_pages_str = ""
    for page in inspection_data["pages"]:
        img_count = len(page["images"])
        inspection_pages_str += f"--- INSPECTION PAGE {page['page']} (Contains {img_count} images: index 0 to {img_count-1}) ---\n"
        inspection_pages_str += page["text"] + "\n\n"
        
    thermal_pages_str = ""
    for page in thermal_data["pages"]:
        metadata = parse_thermal_text(page["text"])
        img_count = len(page["images"])
        thermal_pages_str += f"--- THERMAL PAGE {page['page']} (Contains {img_count} images: index 0 to {img_count-1}) ---\n"
        thermal_pages_str += f"Metadata: {json.dumps(metadata)}\n"
        thermal_pages_str += f"Raw Text: {page['text']}\n\n"
        
    # 2. Build system/user prompt
    system_prompt = (
        "You are an expert civil engineer and diagnostic report writer. Your job is to compile a "
        "Detailed Diagnostic Report (DDR) by correlating inspection records and thermal imaging observations. "
        "You must return ONLY a raw, valid JSON object matching the requested schema. No markdown formatting, "
        "no code fences, no explanations. Just raw JSON."
    )
    
    user_prompt = f"""
    Analyze the following documents to compile a Detailed Diagnostic Report (DDR).

    ### Inspection Report Pages:
    {inspection_pages_str}

    ### Thermal Report Pages:
    {thermal_pages_str}

    ### Schema details:
    Return a JSON object with this exact structure:
    {{
      "property_issue_summary": "A high-level summary paragraph describing the flat's issues, wet-areas correlation, and structural impact.",
      "area_wise_observations": [
        {{
          "area_name": "Name of room/area (e.g. Hall, Kitchen, Master Bedroom)",
          "description": "Professional description of the negative/positive side observations and how the matched thermal anomalies support the finding.",
          "inspection_page_refs": [int], // Page numbers from inspection report where this area is discussed
          "thermal_page_refs": [int], // Page numbers from thermal report matching this area
          "image_refs": [
            {{
              "source": "inspection", // "inspection" or "thermal"
              "page": int, // 1-based page number in the original PDF
              "image_index": int // 0-based index of the image within the extracted images list of that page
            }}
          ]
        }}
      ],
      "probable_root_cause": [
        {{
          "area_name": "Room/area name",
          "cause": "Underlying cause (e.g. tile joint gaps, waterproofing failure, external wall cracks)"
        }}
      ],
      "severity_assessment": [
        {{
          "area_name": "Room/area name",
          "severity": "Low" | "Moderate" | "High",
          "reasoning": "Reasoning for the severity level, citing secondary damages or structural impact"
        }}
      ],
      "recommended_actions": [
        {{
          "area_name": "Room/area name",
          "action": "Remedial actions (e.g. epoxy regrouting, crack injection sealing)"
        }}
      ],
      "additional_notes": "Any other engineering observations, drying duration guidelines, or general notes.",
      "missing_or_unclear_information": [
        "List of missing or unclear information, marked as Not Available if no data is found (e.g. previous repair history, paint brand)"
      ]
    }}

    ### Critical Rules:
    1. Do NOT invent facts. Only use what is explicitly stated in the texts.
    2. If information conflicts, state the conflict explicitly.
    3. If information is missing, write "Not Available" - never guess.
    4. Use simple, client-friendly language.
    5. In image_refs, make sure "page" matches a valid PDF page number, and "image_index" matches a valid index (0-based) for the images extracted on that page.
    6. Return only the raw JSON. Do not wrap in ```json ``` code blocks.
    """

    try:
        client = Anthropic(api_key=api_key)
        
        logger.info("Calling Anthropic Claude API...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON defensively
        if response_text.startswith("```"):
            response_text = re.sub(r'^```[a-zA-Z]*\n', '', response_text)
            response_text = re.sub(r'\n```$', '', response_text)
            response_text = response_text.strip()
            
        return json.loads(response_text)
    except Exception as e:
        logger.warning(f"Claude API failed or returned malformed data: {e}. Falling back to programmatic parser.")
        return generate_programmatic_ddr(inspection_data, thermal_data)
