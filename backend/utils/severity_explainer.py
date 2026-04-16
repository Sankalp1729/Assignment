"""
Severity Explanation Module
Uses Gemini to generate client-friendly explanations for severity scores
"""

from typing import Dict, Any, Optional
from utils.gemini_client import ask_gemini, init_gemini


def explain_severity(item: Dict[str, Any]) -> Optional[str]:
    """
    Generate Gemini-powered explanation for why issue has specific severity.
    
    Args:
        item: Observation item with:
            - area
            - inspection_issue
            - thermal_issue
            - severity
            - description
            
    Returns:
        Explanation string or None if API unavailable
    """
    
    # Ensure Gemini initialized
    init_gemini()
    
    area = item.get("area", "Unknown area")
    inspection = item.get("inspection_issue", "Unknown issue")
    thermal = item.get("thermal_issue", "Not Available")
    severity = item.get("severity", "Medium")
    description = item.get("description", "")
    
    prompt = f"""Explain in 1-2 client-friendly sentences why this issue is classified as {severity} severity.

Location: {area}
Physical Issue: {inspection}
Thermal Finding: {thermal}
Details: {description}

Be professional but clear. Suitable for homeowner.
"""

    try:
        explanation = ask_gemini(prompt)
        return explanation if explanation and "ERROR" not in explanation else None
    except Exception as e:
        print(f"⚠ Could not generate explanation: {str(e)[:50]}")
        return None


def generate_severity_explanations(merged_data: list, use_gemini: bool = False) -> list:
    """
    Add explanations to all items (using Gemini if available).
    
    Args:
        merged_data: List of merged observations
        use_gemini: Whether to attempt Gemini explanations
        
    Returns:
        Updated list with severity_explanation field
    """
    
    for item in merged_data:
        if use_gemini:
            # Try Gemini explanation
            explanation = explain_severity(item)
            if explanation:
                item["severity_explanation"] = explanation
            else:
                # Fallback
                item["severity_explanation"] = get_default_explanation(item)
        else:
            # Use rule-based explanations
            item["severity_explanation"] = get_default_explanation(item)
    
    return merged_data


def get_default_explanation(item: Dict[str, Any]) -> str:
    """
    Generate rule-based explanation without Gemini.
    
    Args:
        item: Observation with severity score
        
    Returns:
        Explanation string
    """
    severity = item.get("severity", "Medium")
    inspection = item.get("inspection_issue", "issue")
    thermal = item.get("thermal_issue", "")
    
    # Build explanation based on severity and data
    if severity == "Critical":
        if thermal != "Not Available":
            return f"Structural {inspection} combined with thermal anomaly indicates significant risk requiring immediate professional assessment."
        else:
            return f"Structural concern with {inspection} requires urgent professional evaluation."
    
    elif severity == "High":
        if thermal != "Not Available" and thermal.lower() != "not available":
            return f"The {inspection} paired with thermal evidence of {thermal} suggests a substantial issue warranting prompt remediation."
        else:
            return f"The {inspection} is classified as a significant concern that should be addressed promptly."
    
    elif severity == "Medium":
        if thermal != "Not Available" and thermal.lower() != "not available":
            return f"While the physical {inspection} appears minor, thermal imaging confirms an underlying issue that requires investigation."
        else:
            return f"This {inspection} should be monitored and addressed within a reasonable timeframe."
    
    else:  # Low
        return f"The {inspection} is relatively minor and can typically be addressed during routine maintenance."


def format_severity_report(merged_data: list) -> str:
    """
    Format observations into readable severity report.
    
    Args:
        merged_data: List of observations with severity
        
    Returns:
        Formatted report string
    """
    from utils.severity import get_severity_summary
    
    summary = get_severity_summary(merged_data)
    
    report = "SEVERITY ASSESSMENT REPORT\n"
    report += "=" * 50 + "\n\n"
    
    # Summary
    report += "SUMMARY:\n"
    for severity in ["Critical", "High", "Medium", "Low"]:
        count = summary.get(severity, 0)
        if count > 0:
            report += f"  {severity}: {count} issue(s)\n"
    
    report += "\n" + "=" * 50 + "\n"
    report += "DETAILED FINDINGS:\n\n"
    
    # Sort by severity priority
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    sorted_items = sorted(
        merged_data,
        key=lambda x: severity_order.get(x.get("severity", "Medium"), 99)
    )
    
    for i, item in enumerate(sorted_items, 1):
        severity = item.get("severity", "Unknown")
        area = item.get("area", "Unknown")
        inspection = item.get("inspection_issue", "")
        thermal = item.get("thermal_issue", "")
        explanation = item.get("severity_explanation", "")
        
        report += f"{i}. [{severity.upper()}] {area}\n"
        report += f"   Issue: {inspection}\n"
        if thermal != "Not Available":
            report += f"   Thermal: {thermal}\n"
        if explanation:
            report += f"   Note: {explanation}\n"
        report += "\n"
    
    return report
