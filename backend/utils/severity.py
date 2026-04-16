"""
Rule-Based Severity Scoring
Computes severity using logic rules, not random AI decisions
"""

from typing import Dict, Any


def calculate_severity(item: Dict[str, Any]) -> str:
    """
    Calculate severity score based on rule-based logic.
    
    This function analyzes observation data using predefined rules
    to determine severity level. Uses multiple signals:
    - thermal_flag: Whether thermal anomaly present
    - inspection_issue: Type of physical issue
    - severity_hint: Initial assessment
    - matched: Whether data sources aligned
    
    Args:
        item: Merged observation dictionary with:
            - inspection_issue
            - thermal_issue
            - severity_hint
            - thermal_flag
            - area
            - description
            
    Returns:
        Severity level: "Critical" | "High" | "Medium" | "Low"
        
    Rule Priority (highest to lowest):
    1. Structural + Thermal = Critical
    2. Major with thermal = High
    3. Any thermal anomaly = Medium/High
    4. Major physical issue = High
    5. Minor physical issue = Low
    6. Default = Medium
    """
    
    # Extract and normalize fields
    inspection_issue = item.get("inspection_issue", "").lower()
    thermal_issue = item.get("thermal_issue", "").lower()
    severity_hint = item.get("severity_hint", "").lower()
    thermal_flag = item.get("thermal_flag", False)
    description = item.get("description", "").lower()
    
    # Rule 1: Structural issues with thermal anomaly = CRITICAL
    # (indicates potential safety risk)
    structural_keywords = ["structural", "foundation", "crack in", "subsidence", "load-bearing"]
    if any(keyword in inspection_issue for keyword in structural_keywords) and thermal_flag:
        return "Critical"
    
    # Rule 2: Major physical issue (severity_hint) + Thermal anomaly = HIGH
    # (double confirmation of problem)
    if severity_hint == "major" and thermal_flag:
        return "High"
    
    # Rule 3: Major crack without thermal verification = HIGH
    # (needs investigation despite lack of thermal confirmation)
    if "crack" in inspection_issue and severity_hint == "major":
        return "High"
    
    # Rule 4: Any thermal anomaly (heat loss, moisture, thermal bridge) = MEDIUM/HIGH
    # Based on what type of thermal issue
    if thermal_flag:
        thermal_keywords_high = ["heat loss", "thermal loss", "moisture and thermal", "major"]
        thermal_keywords_medium = ["thermal bridge", "cold spot", "anomaly"]
        
        if any(keyword in thermal_issue for keyword in thermal_keywords_high):
            return "High"
        elif any(keyword in thermal_issue for keyword in thermal_keywords_medium):
            return "Medium"
        else:
            return "Medium"  # Default for thermal issues
    
    # Rule 5: Moisture/water damage = HIGH (can escalate quickly)
    if "moisture" in inspection_issue or "water" in inspection_issue:
        if severity_hint == "major":
            return "High"
        else:
            return "Medium"
    
    # Rule 6: Minor physical issue alone = LOW
    if severity_hint == "minor" and not thermal_flag:
        return "Low"
    
    # Rule 7: Minor issue but thermal anomaly = MEDIUM
    # (indicates underscore potential problem)
    if severity_hint == "minor" and thermal_flag:
        return "Medium"
    
    # Rule 8: Major (but no other context) = HIGH
    if severity_hint == "major":
        return "High"
    
    # Default: No clear data = MEDIUM (conservative)
    return "Medium"


def get_severity_color(severity: str) -> str:
    """
    Get color code for severity level (useful for HTML/reports).
    
    Args:
        severity: Severity level string
        
    Returns:
        Hex color code
    """
    color_map = {
        "critical": "#d32f2f",  # Dark red
        "high": "#f57c00",      # Orange
        "medium": "#fbc02d",    # Yellow
        "low": "#388e3c"        # Green
    }
    return color_map.get(severity.lower(), "#999999")  # Gray default


def get_severity_description(severity: str) -> str:
    """
    Get human-friendly description of severity level.
    
    Args:
        severity: Severity level
        
    Returns:
        Description string
    """
    descriptions = {
        "critical": "Immediate action required - potential safety or structural risk",
        "high": "Significant issue requiring prompt investigation and remediation",
        "medium": "Important concern that should be addressed within reasonable timeframe",
        "low": "Minor issue - can be monitored or addressed in routine maintenance"
    }
    return descriptions.get(severity.lower(), "Unknown severity level")


def apply_severity_to_merged_data(merged_data: list) -> list:
    """
    Apply rule-based severity scoring to all merged observations.
    
    Args:
        merged_data: List of merged observation dictionaries
        
    Returns:
        Same list with "severity" field added to each item
    """
    for item in merged_data:
        # Calculate severity score
        item["severity"] = calculate_severity(item)
        
        # Add color for visualization
        item["severity_color"] = get_severity_color(item["severity"])
        
        # Add description
        item["severity_description"] = get_severity_description(item["severity"])
    
    return merged_data


def get_severity_summary(merged_data: list) -> Dict[str, int]:
    """
    Count observations by severity level.
    
    Args:
        merged_data: List of merged observations with severity calculated
        
    Returns:
        Dictionary with counts for each severity level
    """
    summary = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }
    
    for item in merged_data:
        severity = item.get("severity", "Medium")
        summary[severity] = summary.get(severity, 0) + 1
    
    return summary


# Example of rule-based scoring (for reference)
SEVERITY_RULES = """
RULE-BASED SEVERITY SCORING LOGIC
==================================

Severity levels: Critical → High → Medium → Low

Rule Priority (evaluated top to bottom):

1. CRITICAL (Structural + Thermal)
   - Condition: Structural issue AND thermal anomaly
   - Rationale: Indicates potential structural failure
   - Examples: Foundation crack with heat loss

2. HIGH (Major + Thermal OR Major Crack)
   - Condition: (Major severity + thermal) OR (Crack + Major)
   - Rationale: Double confirmation or known dangerous condition
   - Examples: Major crack in wall, moisture damage with thermal

3. HIGH (Major Alone)
   - Condition: severity_hint == "major"
   - Rationale: Known to be significant regardless of thermal
   - Examples: Structural crack, main wall damage

4. MEDIUM/HIGH (Thermal Anomaly)
   - Condition: thermal_flag == true
   - Rationale: Requires investigation
   - Sub-rules:
     - Heat/moisture thermal = HIGH
     - Thermal bridge/cold spot = MEDIUM

5. MEDIUM (Minor + Thermal)
   - Condition: severity_hint == "minor" AND thermal_flag
   - Rationale: Indicates hidden issue despite minor physical appearance
   - Examples: Small crack but significant thermal loss

6. LOW (Minor Physical)
   - Condition: severity_hint == "minor" AND NOT thermal_flag
   - Rationale: Known to be minor, no other concerns
   - Examples: Small cosmetic crack without thermal issues

7. DEFAULT = MEDIUM
   - Applied when no specific rules match
   - Conservative approach: assume medium priority
"""
