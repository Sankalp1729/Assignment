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
    
    # Truncate to avoid token limits (Gemini handles ~1M tokens but let's be safe)
    truncated_text = page_text[:2000]
    
    prompt = f"""You are an AI system that extracts structured observations from inspection reports.

From the text below, extract ALL observations about building issues, defects, or problems.

Each observation MUST include:
- area: The specific location/room/surface (e.g., "Bedroom Wall", "Living Room Ceiling")
- issue: The type of issue in one or two words (e.g., "Crack", "Moisture Damage", "Thermal Loss")
- description: A clear, concise description of what was observed
- severity_hint: The severity level (minor/major/unknown)

STRICT RULES:
- Return ONLY valid JSON array
- Do NOT include explanations
- Do NOT include markdown code blocks
- Each item must have all 4 fields
- If area/issue cannot be determined, use "unknown"
- If severity cannot be determined, use "unknown"

Return format - ONLY this, nothing else:
[
  {{
    "area": "...",
    "issue": "...",
    "description": "...",
    "severity_hint": "minor|major|unknown"
  }}
]

TEXT TO ANALYZE:
{truncated_text}"""

    result = ask_gemini_json(prompt)
    
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
        return observations
    
    elif isinstance(result, dict) and "error" in result:
        print(f"  ⚠ Gemini error: {result.get('error')}")
        return []
    
    else:
        print(f"  ⚠ Unexpected result type: {type(result)}")
        return []


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
