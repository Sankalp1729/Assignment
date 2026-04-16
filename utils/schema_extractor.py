"""
Schema extraction using Gemini API.
Extracts areas, issue types, and units from inspection text.
"""

import json
from typing import Dict, Any, List, Optional
from utils.gemini_client import GeminiClient, get_gemini_client


def extract_schema(text: str, client: Optional[GeminiClient] = None) -> Dict[str, Any]:
    """
    Extract schema (areas, issue types, units) from inspection report text.
    Returns CLEAN, structured JSON only.
    
    Args:
        text: Raw text from inspection report
        client: GeminiClient instance (creates one if not provided)
        
    Returns:
        Dictionary with extracted schema:
        {
            "areas": ["bedroom", "wall", ...],
            "issue_types": ["crack", "moisture", ...],
            "units": ["°C", "mm", ...]
        }
    """
    if client is None:
        client = get_gemini_client()
        if client is None:
            return {"areas": [], "issue_types": [], "units": [], "error": "Gemini not available"}
    
    # Limit text to avoid token overflow
    text_sample = text[:2000]
    
    # STRICT prompt for clean JSON only
    prompt = f"""Extract structured data from this text. Return ONLY valid JSON. No markdown. No explanation.

Extract:
1. Areas/Locations (physical areas mentioned)
2. Issue types (types of problems or defects)
3. Units of Measurement (e.g., °C, mm)

RULES:
- Return ONLY JSON
- No code blocks
- No extra text
- If no items found, return empty array []

Format:
{{
  "areas": [],
  "issue_types": [],
  "units": []
}}

Text:
{text_sample}"""
    
    result = client.ask_json(prompt, temperature=0.1)
    
    # Validate and clean result
    if "error" in result:
        print(f"  ⚠ Schema extraction returned error")
        return {
            "areas": [],
            "issue_types": [],
            "units": [],
            "extraction_error": result.get("error")
        }
    
    # Ensure required fields exist
    schema = {
        "areas": result.get("areas", []),
        "issue_types": result.get("issue_types", []),
        "units": result.get("units", []),
    }
    
    # Validate types (should be lists)
    for key in ["areas", "issue_types", "units"]:
        if not isinstance(schema[key], list):
            schema[key] = []
    
    # Clean up: remove duplicates, convert to lowercase, remove empty strings
    schema["areas"] = list(set([str(a).strip().lower() for a in schema["areas"] if a]))
    schema["issue_types"] = list(set([str(t).strip().lower() for t in schema["issue_types"] if t]))
    schema["units"] = list(set([str(u).strip() for u in schema["units"] if u]))
    
    return schema


def extract_observations(
    text: str,
    schema: Dict[str, Any],
    doc_type: str = "inspection",
    client: Optional[GeminiClient] = None
) -> Dict[str, Any]:
    """
    Extract observations (issues) from text using identified schema.
    Returns CLEAN, structured JSON only.
    
    Args:
        text: Raw text from report
        schema: Schema from extract_schema()
        doc_type: "inspection", "thermal", etc.
        client: GeminiClient instance
        
    Returns:
        Dictionary with extracted observations:
        {
            "observations": [
                {
                    "area": "bedroom",
                    "issue_type": "crack",
                    "description": "...",
                    "severity": "high",
                    "confidence": 0.85
                },
                ...
            ]
        }
    """
    if client is None:
        client = get_gemini_client()
        if client is None:
            return {"error": "Gemini not available", "observations": []}
    
    text_sample = text[:2000]
    areas_str = ", ".join(schema.get("areas", [])[:10]) if schema.get("areas") else "various areas"
    issues_str = ", ".join(schema.get("issue_types", [])[:10]) if schema.get("issue_types") else "various issues"
    
    # STRICT prompt for clean JSON only
    prompt = f"""Extract observations from this {doc_type} report. Return ONLY valid JSON. No markdown. No explanation.

For each issue found, extract:
- area: The location/area
- issue_type: Type of issue
- description: What was observed
- severity: critical/high/medium/low
- confidence: 0.0-1.0

Known areas: {areas_str}
Known issues: {issues_str}

RULES:
- Return ONLY JSON array
- No code blocks
- No extra text
- Extract only clear observations from text

Format:
[
  {{"area": "...", "issue_type": "...", "description": "...", "severity": "...", "confidence": 0.X}},
  ...
]

Text:
{text_sample}"""
    
    result = client.ask_json(prompt, temperature=0.1)
    
    # Handle errors
    if "error" in result:
        print(f"  ⚠ Observation extraction returned error")
        return {"observations": [], "extraction_error": result.get("error")}
    
    # Result should be a list if successful
    observations = result if isinstance(result, list) else result.get("observations", [])
    
    # Validate each observation
    validated = []
    for obs in observations:
        if isinstance(obs, dict) and all(k in obs for k in ["area", "issue_type", "description", "severity"]):
            try:
                confidence = float(obs.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            except (ValueError, TypeError):
                confidence = 0.5
            
            validated.append({
                "area": str(obs.get("area", "")).strip().lower(),
                "issue_type": str(obs.get("issue_type", "")).strip().lower(),
                "description": str(obs.get("description", "")).strip(),
                "severity": str(obs.get("severity", "low")).lower(),
                "confidence": confidence
            })
    
    return {"observations": validated}


def extract_schema_and_observations(
    text: str,
    doc_type: str = "inspection",
    client: Optional[GeminiClient] = None
) -> Dict[str, Any]:
    """
    One-step extraction of both schema and observations.
    Recommended for convenience.
    
    Args:
        text: Raw text from report
        doc_type: "inspection", "thermal", etc.
        client: GeminiClient instance
        
    Returns:
        Combined result with schema and observations
    """
    if client is None:
        client = get_gemini_client()
        if client is None:
            return {
                "schema": {"areas": [], "issue_types": [], "units": []},
                "observations": {"observations": []},
                "error": "Gemini not available"
            }
    
    print(f"  📊 Extracting schema...")
    schema = extract_schema(text, client)
    
    print(f"  📋 Extracting observations...")
    observations = extract_observations(text, schema, doc_type, client)
    
    return {
        "schema": schema,
        "observations": observations,
        "document_type": doc_type,
        "text_length": len(text)
    }
