"""
Observation Merger - Combine observations from multiple document sources
Handles fuzzy matching of areas and conflict detection
"""

from typing import List, Dict, Any, Set
from rapidfuzz import fuzz


def match_areas(area1: str, area2: str, threshold: int = 70) -> bool:
    """
    Match similar area names using fuzzy string matching.
    
    Args:
        area1: First area name
        area2: Second area name
        threshold: Matching threshold (0-100, default 70)
        
    Returns:
        True if areas are similar enough to be considered the same location
        
    Examples:
        match_areas("Living Room Wall", "living room") → True
        match_areas("Bedroom Window", "Bedroom") → True
        match_areas("Kitchen", "Garage") → False
    """
    if not area1 or not area2:
        return False
    
    # Normalize and compare
    normalized1 = area1.lower().strip()
    normalized2 = area2.lower().strip()
    
    # Exact match
    if normalized1 == normalized2:
        return True
    
    # Fuzzy match using token_set_ratio (handles order differences)
    similarity = fuzz.token_set_ratio(normalized1, normalized2)
    return similarity > threshold


def merge_observations(
    inspection_obs: List[Dict[str, Any]],
    thermal_obs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge inspection observations with thermal observations.
    
    Intelligently matches areas using fuzzy matching and combines observations.
    Handles cases where one document type has data but the other doesn't.
    
    Args:
        inspection_obs: List of observations from inspection report
        thermal_obs: List of observations from thermal report
        
    Returns:
        List of merged observations, each containing:
        - area: Location name
        - inspection_issue: Issue from inspection (or "Not Available")
        - thermal_issue: Issue from thermal (or "Not Available")
        - description: Combined description from both sources
        - severity_hint: Severity from inspection source
        - thermal_flag: Whether thermal data was available for this area
        - matched: Was a thermal match found
        
    Example:
        >>> inspection = [{"area": "Wall", "issue": "Crack", ...}]
        >>> thermal = [{"area": "living room wall", "issue": "Heat Loss", ...}]
        >>> merged = merge_observations(inspection, thermal)
        >>> # Will match despite different capitalization
    """
    merged = []
    used_thermal: Set[int] = set()
    
    # Process each inspection observation
    for ins in inspection_obs:
        ins_area = ins.get("area", "unknown")
        ins_issue = ins.get("issue", "unknown")
        ins_description = ins.get("description", "")
        ins_severity = ins.get("severity_hint", "unknown")
        
        matched = False
        best_match_idx = -1
        best_similarity = 0
        
        # Find best matching thermal observation for this area
        for idx, therm in enumerate(thermal_obs):
            if idx in used_thermal:
                continue  # Already matched
            
            therm_area = therm.get("area", "unknown")
            
            if match_areas(ins_area, therm_area):
                # Keep track of best match (highest similarity)
                similarity = fuzz.token_set_ratio(
                    ins_area.lower().strip(),
                    therm_area.lower().strip()
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_idx = idx
                    matched = True
        
        # If we found a thermal match, use it
        if matched and best_match_idx >= 0:
            therm = thermal_obs[best_match_idx]
            used_thermal.add(best_match_idx)
            
            therm_issue = therm.get("issue", "unknown")
            therm_description = therm.get("description", "")
            
            final_area = ins_area if ins_area.strip() and ins_area.lower() not in ["", "general area", "general", "unknown"] else therm.get("area", "unknown")
            merged.append({
                "area": final_area,
                "inspection_issue": ins_issue,
                "thermal_issue": therm_issue,
                "description": ins_description + " | " + therm_description,
                "severity_hint": ins_severity,
                "thermal_flag": True,
                "matched": True,
                "similarity_score": best_similarity
            })
        else:
            # No thermal match found
            merged.append({
                "area": ins_area,
                "inspection_issue": ins_issue,
                "thermal_issue": "Not Available",
                "description": ins_description,
                "severity_hint": ins_severity,
                "thermal_flag": False,
                "matched": False,
                "similarity_score": 0
            })
    
    # Add unmatched thermal observations
    for idx, therm in enumerate(thermal_obs):
        if idx not in used_thermal:
            therm_area = therm.get("area", "unknown")
            therm_issue = therm.get("issue", "unknown")
            therm_description = therm.get("description", "")
            
            merged.append({
                "area": therm_area,
                "inspection_issue": "Not Available",
                "thermal_issue": therm_issue,
                "description": therm_description,
                "severity_hint": "unknown",
                "thermal_flag": True,
                "matched": False,
                "similarity_score": 0
            })
    
    return merged


def detect_conflicts(merged_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect logical conflicts between inspection and thermal observations.
    
    Identifies discrepancies that warrant further investigation:
    - Minor physical issues with major thermal anomalies
    - Contradictory assessments
    - Areas with missing complementary data
    
    Args:
        merged_data: List of merged observations from merge_observations()
        
    Returns:
        List of conflict records, each containing:
        - area: Location of conflict
        - conflict_type: Type of conflict detected
        - inspection_severity: Severity from inspection
        - thermal_present: Whether thermal data exists
        - confidence: How serious the conflict is
        - recommendation: Suggested action
        
    Example:
        >>> merged = [
        ...   {"area": "Wall", "severity_hint": "minor", 
        ...    "inspection_issue": "Crack", "thermal_issue": "Heat Loss", ...}
        ... ]
        >>> conflicts = detect_conflicts(merged)
    """
    conflicts = []
    
    for item in merged_data:
        area = item.get("area", "unknown")
        inspection_issue = item.get("inspection_issue", "Not Available")
        thermal_issue = item.get("thermal_issue", "Not Available")
        inspection_severity = item.get("severity_hint", "unknown")
        thermal_flag = item.get("thermal_flag", False)
        
        # Conflict 1: Minor physical issue but thermal anomaly present
        if (inspection_issue != "Not Available" and 
            thermal_issue != "Not Available" and 
            inspection_severity == "minor"):
            
            # Minor crack but heat loss detected = potential structural issue
            if "heat" in thermal_issue.lower() or "thermal" in thermal_issue.lower():
                conflicts.append({
                    "area": area,
                    "conflict_type": "Minor physical issue with thermal anomaly",
                    "inspection_issue": inspection_issue,
                    "inspection_severity": inspection_severity,
                    "thermal_issue": thermal_issue,
                    "confidence": "HIGH",
                    "note": "Minor issue present but thermal signature suggests more significant problem",
                    "recommendation": "Investigate if crack is allowing thermal loss"
                })
        
        # Conflict 2: Missing thermal data where inspection found issues
        if (inspection_issue != "Not Available" and 
            inspection_severity == "major" and 
            thermal_issue == "Not Available"):
            
            conflicts.append({
                "area": area,
                "conflict_type": "Major issue without thermal verification",
                "inspection_issue": inspection_issue,
                "inspection_severity": inspection_severity,
                "thermal_issue": thermal_issue,
                "confidence": "MEDIUM",
                "note": "Major issue detected but no thermal data available",
                "recommendation": "Conduct thermal imaging to correlate issue"
            })
        
        # Conflict 3: Thermal issue without physical manifestation
        if (inspection_issue == "Not Available" and 
            thermal_issue != "Not Available"):
            
            conflicts.append({
                "area": area,
                "conflict_type": "Thermal anomaly without physical inspection",
                "inspection_issue": inspection_issue,
                "thermal_issue": thermal_issue,
                "confidence": "MEDIUM",
                "note": "Thermal issue detected but no corresponding physical observation",
                "recommendation": "Schedule detailed inspection of this area"
            })
    
    return conflicts


def get_merge_statistics(merged_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics about merged observations.
    
    Args:
        merged_data: List of merged observations
        
    Returns:
        Dictionary with statistics about merging
    """
    total = len(merged_data)
    matched = sum(1 for item in merged_data if item.get("matched", False))
    inspection_only = sum(1 for item in merged_data 
                         if item.get("inspection_issue") != "Not Available" 
                         and item.get("thermal_issue") == "Not Available")
    thermal_only = sum(1 for item in merged_data 
                      if item.get("inspection_issue") == "Not Available" 
                      and item.get("thermal_issue") != "Not Available")
    both_present = sum(1 for item in merged_data 
                      if item.get("inspection_issue") != "Not Available" 
                      and item.get("thermal_issue") != "Not Available")
    
    return {
        "total_observations": total,
        "matched_pairs": matched,
        "inspection_only": inspection_only,
        "thermal_only": thermal_only,
        "both_present": both_present,
        "match_rate": f"{(matched/total*100):.1f}%" if total > 0 else "0%"
    }
