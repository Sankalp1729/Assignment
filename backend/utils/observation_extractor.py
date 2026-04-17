"""
Structured Observation Extraction from PDF Text
Converts page text into clean observation JSON using Gemini
"""

from typing import List, Dict, Any, Optional
from utils.gemini_client import ask_gemini_json, init_gemini


def extract_observations(page_text: str) -> List[Dict[str, Any]]:
    """
    Extract structured observations from a single page of text.
    
    Args:
        page_text: Text from a single PDF page
        
    Returns:
        List of observations, each with:
        - area: Location/room where issue found
        - issue: Type of problem (crack, moisture, thermal loss, etc.)
        - description: Detailed description of the observation
        - severity_hint: Severity level (minor/major/unknown)
    """
    
    # Ensure Gemini is initialized
    init_gemini()
    
    prompt = f"""
Extract detailed observations from the text.

Each observation must include:
- area (specific location like "Living Room Wall")
- issue (specific problem like "crack", "leakage")
- description (clear explanation from text)
- severity_hint (minor/major based on wording)

STRICT RULES:
- Use ONLY information from text
- DO NOT use generic words like "detected issue"
- DO NOT return placeholders
- Return ONLY JSON list

Example:
[
  {{
    "area": "Living Room Wall",
    "issue": "Crack",
    "description": "Visible structural crack near ceiling corner",
    "severity_hint": "minor"
  }}
]

Text:
{page_text}
"""

    print(f"[DEBUG] Extracting observations from {len(page_text)} chars of text")
    result = ask_gemini_json(prompt)
    print(f"[DEBUG] RAW GEMINI RESPONSE: {result}")
    
    # Validate result is a list
    if isinstance(result, list):
        # Clean and validate each observation
        observations = []
        for obs in result:
            if isinstance(obs, dict):
                # Ensure all required fields exist
                clean_obs = {
                    "area": str(obs.get("area", "unknown")).strip() or "unknown",
                    "issue": str(obs.get("issue", "unknown")).strip() or "unknown",
                    "description": str(obs.get("description", "")).strip() or "No description",
                    "severity_hint": str(obs.get("severity_hint", "unknown")).strip().lower() or "unknown"
                }
                observations.append(clean_obs)
    
    elif isinstance(result, dict) and "error" in result:
        error_msg = result.get('error')
        print(f"  ⚠ Gemini error: {error_msg}")
        observations = []
    
    else:
        print(f"  ⚠ Unexpected result type: {type(result)}")
        observations = []

    if not observations:
        import re
        observations = []
        text_lower = page_text.lower()
        
        # Define area + keywords mapping
        rules = {
            "Living Room": ["living room", "lounge"],
            "Bedroom": ["bedroom"],
            "Kitchen": ["kitchen"],
            "Bathroom": ["bathroom", "washroom"],
            "Balcony": ["balcony"],
            "Wall": ["wall"],
            "Ceiling": ["ceiling"],
            "Floor": ["floor"],
            "Exterior": ["exterior"],
            "Roof": ["roof"],
            "Foundation": ["foundation", "basement"]
        }

        raw_observations = []
        for area, keywords in rules.items():
            if any(k in text_lower for k in keywords):
                # Detect ONLY relevant issues
                if "crack" in text_lower or "fracture" in text_lower:
                    raw_observations.append({
                        "area": area,
                        "issue": "Crack",
                        "description": f"Extracted automatically: Crack or fracture detected in {area}.",
                        "severity_hint": "major"
                    })
                elif "leak" in text_lower or "moisture" in text_lower or "damp" in text_lower or "water" in text_lower:
                    raw_observations.append({
                        "area": area,
                        "issue": "Moisture/Leakage",
                        "description": f"Extracted automatically: Moisture or leakage detected in {area}.",
                        "severity_hint": "major"
                    })
                elif "structur" in text_lower:
                    raw_observations.append({
                        "area": area,
                        "issue": "Structural defect",
                        "description": f"Extracted automatically: Structural defect detected in {area}.",
                        "severity_hint": "major"
                    })
                elif "thermal" in text_lower or "temperature" in text_lower or "heat" in text_lower or "cold" in text_lower:
                    raw_observations.append({
                        "area": area,
                        "issue": "Thermal anomaly",
                        "description": f"Extracted automatically: Thermal irregularity detected in {area}.",
                        "severity_hint": "minor"
                    })
                elif "insulation" in text_lower:
                    raw_observations.append({
                        "area": area,
                        "issue": "Insulation issue",
                        "description": f"Extracted automatically: Insulation issue detected in {area}.",
                        "severity_hint": "minor"
                    })
                    
        # Remove duplicates
        seen = set()
        for obs in raw_observations:
            key = (obs["area"], obs["issue"])
            if key not in seen:
                seen.add(key)
                observations.append(obs)

    print("FINAL OBS:", observations)
    return observations


def extract_observations_batch(page_texts: List[str]) -> List[Dict[str, Any]]:
    """
    Extract observations from multiple pages.
    
    Args:
        page_texts: List of text strings from PDF pages
        
    Returns:
        Combined list of all observations from all pages
    """
    all_observations = []
    
    for page_num, text in enumerate(page_texts, 1):
        if not text or not text.strip():
            print(f"  ⏭ Page {page_num}: No text (skipped)")
            continue
            
        print(f"  🔍 Extracting from page {page_num}...")
        obs = extract_observations(text)
        all_observations.extend(obs)
        print(f"    ✓ Found {len(obs)} observation(s)")
    
    return all_observations
