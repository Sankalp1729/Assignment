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

def generate_ddr_data(inspection_data: dict, thermal_data: dict) -> dict:
    """
    Constructs prompt, sends it to Anthropic API, and parses the returned JSON.
    """
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

    # 3. Call API
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            pass
            
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured in environment or Streamlit secrets.")
        
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
    
    # 4. Parse JSON defensively
    # Strip markdown code fences if model accidentally output them
    if response_text.startswith("```"):
        response_text = re.sub(r'^```[a-zA-Z]*\n', '', response_text)
        response_text = re.sub(r'\n```$', '', response_text)
        response_text = response_text.strip()
        
    try:
        ddr_dict = json.loads(response_text)
        return ddr_dict
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from Claude: {e}")
        # Return a dictionary wrapping the raw response so the user can debug
        return {
            "error": "JSON_PARSE_ERROR",
            "message": str(e),
            "raw_response": response_text
        }
