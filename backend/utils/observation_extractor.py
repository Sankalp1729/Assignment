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
        
        # Detect areas using headings (simple rule)
        area_matches = re.findall(r"(living room|bedroom|kitchen|bathroom|wall|ceiling|floor|exterior|balcony|staircase|roof|foundation)", text_lower)
        if not area_matches:
            area_matches = ["General Area"]

        # Detect issues
        issues = []
        if "crack" in text_lower or "fracture" in text_lower:
            issues.append("Crack")
        if "leak" in text_lower or "moisture" in text_lower or "damp" in text_lower or "water" in text_lower:
            issues.append("Moisture/Leakage")
        if "thermal" in text_lower or "temperature" in text_lower or "heat" in text_lower or "cold" in text_lower:
            issues.append("Thermal anomaly")
        if "insulation" in text_lower:
            issues.append("Insulation issue")
        if "structural" in text_lower:
            issues.append("Structural defect")
            
        if not issues:
            issues.append("Detected issue")

        # Create observations
        for area in set(area_matches):
            for issue in issues:
                observations.append({
                    "area": area.title(),
                    "issue": issue,
                    "description": f"Extracted automatically: {issue} detected in {area.title()}.",
                    "severity_hint": "major" if issue in ["Crack", "Moisture/Leakage", "Structural defect"] else "minor"
                })

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
