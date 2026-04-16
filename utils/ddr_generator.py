"""
STEP 8: DDR (Detailed Diagnostic Report) Generator

Generates professional, client-ready property diagnostic reports
by creating sections sequentially for better control and quality.

Architecture:
- Section generation: Each section created independently
- Fallback system: Works offline with template-based generation
- Output: Structured report dict → Text file export
"""

import json
import re
from typing import Dict, List, Any, Optional
from utils.gemini_client import ask_gemini


def _prepare_data_for_prompt(data: Any) -> str:
    """
    Convert complex data structures to readable format for Gemini.
    
    Args:
        data: Dict, list, or any JSON-serializable data
        
    Returns:
        Formatted string representation for prompt
    """
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)
    return str(data)


def generate_section(
    section_name: str,
    data: Dict[str, Any],
    use_gemini: bool = True
) -> str:
    """
    Generate a single report section using Gemini or template.
    
    Args:
        section_name: Name of the section to generate
        data: Merged observations and metadata
        use_gemini: Whether to use Gemini (True) or template-based (False)
        
    Returns:
        Generated section content (string)
    """
    data_str = _prepare_data_for_prompt(data)
    
    prompt = f"""You are a professional property inspector generating a Detailed Diagnostic Report (DDR).

Generate the section: "{section_name}"

CRITICAL RULES:
1. Use simple, client-friendly language (no jargon)
2. Do NOT invent information beyond the data provided
3. If specific data is missing → explicitly state "Not Available"
4. Be professional but approachable
5. Keep it concise but informative
6. Use bullet points where appropriate

DATA PROVIDED:
{data_str}

Generate ONLY the section content. No headers. No preamble. Just the content."""

    try:
        if use_gemini:
            content = ask_gemini(prompt)
            return content if content else _get_template_section(section_name, data)
        else:
            return _get_template_section(section_name, data)
    except Exception as e:
        print(f"⚠️  Gemini failed for '{section_name}': {str(e)[:100]}")
        return _get_template_section(section_name, data)


def _get_template_section(section_name: str, data: Dict[str, Any]) -> str:
    """
    Generate section content using templates (offline fallback).
    
    Args:
        section_name: Name of section
        data: Merged observations
        
    Returns:
        Template-based section content
    """
    # Extract useful context from data
    observations = data if isinstance(data, list) else data.get("observations", [])
    
    templates = {
        "Property Issue Summary": _template_issue_summary(observations),
        "Area-wise Observations": _template_area_observations(observations),
        "Probable Root Cause": _template_root_cause(observations),
        "Severity Assessment": _template_severity_assessment(observations),
        "Recommended Actions": _template_recommended_actions(observations),
        "Additional Notes": _template_additional_notes(observations),
        "Missing Information": _template_missing_information(data),
    }
    
    return templates.get(section_name, f"Data: {_prepare_data_for_prompt(data)}")


def _template_issue_summary(observations: List[Dict]) -> str:
    """Template for Property Issue Summary."""
    if not observations:
        return "Not Available - No observations data provided."
    
    critical_count = sum(1 for o in observations if o.get("severity") == "Critical")
    high_count = sum(1 for o in observations if o.get("severity") == "High")
    
    summary = f"Property diagnostic reveals {len(observations)} significant issues:\n"
    if critical_count > 0:
        summary += f"• {critical_count} CRITICAL issue(s) requiring immediate attention\n"
    if high_count > 0:
        summary += f"• {high_count} HIGH priority issue(s) needing prompt remediation\n"
    
    areas = [o.get("area", "Unknown") for o in observations]
    summary += f"\nAffected areas: {', '.join(set(areas))}"
    
    return summary


def _template_area_observations(observations: List[Dict]) -> str:
    """Template for Area-wise Observations."""
    if not observations:
        return "Not Available - No detailed observations provided."
    
    content = ""
    for obs in observations:
        area = obs.get("area", "Unknown Area")
        inspection = obs.get("inspection_issue", "Not specified")
        thermal = obs.get("thermal_issue", "Not detected")
        severity = obs.get("severity", "Unknown")
        
        content += f"\n• {area} [{severity}]\n"
        content += f"  - Inspection Finding: {inspection}\n"
        content += f"  - Thermal Finding: {thermal}\n"
    
    return content.strip()


def _template_root_cause(observations: List[Dict]) -> str:
    """Template for Probable Root Cause."""
    if not observations:
        return "Not Available - Insufficient data for analysis."
    
    # Identify common patterns
    moisture_issues = sum(1 for o in observations 
                         if "moisture" in o.get("inspection_issue", "").lower() 
                         or "moisture" in o.get("thermal_issue", "").lower())
    
    thermal_issues = sum(1 for o in observations if o.get("thermal_flag"))
    structural_issues = sum(1 for o in observations 
                           if "structural" in o.get("inspection_issue", "").lower() 
                           or "crack" in o.get("inspection_issue", "").lower())
    
    causes = []
    if moisture_issues > 0:
        causes.append(f"Moisture intrusion ({moisture_issues} area(s))")
    if thermal_issues > 0:
        causes.append(f"Insufficient insulation/thermal bridging ({thermal_issues} area(s))")
    if structural_issues > 0:
        causes.append(f"Structural settling/movement ({structural_issues} area(s))")
    
    if causes:
        return "Primary causes:\n• " + "\n• ".join(causes)
    else:
        return "Based on available data, issues appear localized to specific areas."


def _template_severity_assessment(observations: List[Dict]) -> str:
    """Template for Severity Assessment."""
    if not observations:
        return "Not Available - No severity data."
    
    severity_breakdown = {}
    for obs in observations:
        severity = obs.get("severity", "Unknown")
        severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
    
    content = "Severity Distribution:\n"
    for severity in ["Critical", "High", "Medium", "Low"]:
        if severity in severity_breakdown:
            count = severity_breakdown[severity]
            content += f"• {severity}: {count} issue(s)\n"
    
    content += "\nOverall Assessment: "
    if severity_breakdown.get("Critical", 0) > 0:
        content += "Property requires immediate professional attention for critical issues."
    elif severity_breakdown.get("High", 0) > 0:
        content += "Property requires prompt remediation of high-priority issues."
    else:
        content += "Property issues are manageable with appropriate maintenance planning."
    
    return content


def _template_recommended_actions(observations: List[Dict]) -> str:
    """Template for Recommended Actions."""
    if not observations:
        return "Not Available - No data for recommendations."
    
    actions = []
    
    # Check for structural issues
    structural = [o for o in observations 
                  if "structural" in o.get("inspection_issue", "").lower()]
    if structural:
        actions.append("1. IMMEDIATE: Consult structural engineer for assessment")
        actions.append("2. Document all cracks and investigate settlement patterns")
    
    # Check for moisture
    moisture = [o for o in observations 
               if "moisture" in o.get("inspection_issue", "").lower()]
    if moisture:
        actions.append("3. Inspect grading and drainage around foundation")
        actions.append("4. Seal cracks and apply waterproofing sealant")
    
    # Check for thermal
    thermal = [o for o in observations if o.get("thermal_flag")]
    if thermal:
        actions.append("5. Evaluate insulation adequacy and thermal bridging")
        actions.append("6. Consider insulation upgrade in affected areas")
    
    # Generic action
    critical_issues = [o for o in observations if o.get("severity") == "Critical"]
    if critical_issues:
        actions.insert(0, "PRIORITY: Address all critical issues within 30 days")
    
    content = "\n".join(actions) if actions else "Monitor property condition and schedule follow-up inspection in 6 months."
    
    return content


def _template_additional_notes(observations: List[Dict]) -> str:
    """Template for Additional Notes."""
    return (
        "• All observations should be verified by qualified professionals\n"
        "• This report is based on visual inspection and thermal imaging\n"
        "• Specific remediation costs require quotes from contractors\n"
        "• Regular maintenance can prevent escalation of minor issues"
    )


def _template_missing_information(data: Any) -> str:
    """Template for Missing Information."""
    conflicts = data if isinstance(data, dict) else {}
    
    if not conflicts:
        return "All required information was available for this inspection."
    
    conflict_list = conflicts.get("conflicts", []) if isinstance(conflicts, dict) else []
    if not conflict_list:
        return "All required information was available for this inspection."
    
    content = "The following information discrepancies were identified:\n"
    for conflict in conflict_list[:5]:  # Limit to 5
        if isinstance(conflict, dict):
            area = conflict.get("area", "Unknown")
            reason = conflict.get("reason", "Data mismatch")
            content += f"• {area}: {reason}\n"
    
    if len(conflict_list) > 5:
        content += f"• ... and {len(conflict_list) - 5} more"
    
    return content


def generate_ddr_report(
    merged_data: List[Dict[str, Any]],
    conflicts: Optional[Dict[str, Any]] = None,
    use_gemini: bool = False
) -> Dict[str, str]:
    """
    Generate complete DDR report with all sections.
    
    Args:
        merged_data: List of merged observations from STEP 6
        conflicts: Conflict data from STEP 6
        use_gemini: Whether to use Gemini API (False = templates)
        
    Returns:
        Dictionary with section names as keys and content as values
    """
    report = {}
    
    sections = [
        "Property Issue Summary",
        "Area-wise Observations",
        "Probable Root Cause",
        "Severity Assessment",
        "Recommended Actions",
        "Additional Notes",
        "Missing Information",
    ]
    
    print(f"📄 Generating DDR Report ({len(sections)} sections)...")
    
    for i, section_name in enumerate(sections, 1):
        print(f"  [{i}/{len(sections)}] Generating: {section_name}...", end=" ", flush=True)
        
        # Use merged_data for all sections except Missing Information
        data_for_section = conflicts if section_name == "Missing Information" else merged_data
        
        try:
            content = generate_section(section_name, data_for_section, use_gemini=use_gemini)
            report[section_name] = content
            print("✓")
        except Exception as e:
            print(f"✗ ({str(e)[:50]})")
            report[section_name] = f"[Error generating section: {str(e)[:100]}]"
    
    print(f"✅ Report generated with {len(report)} sections")
    
    return report


def save_report(report: Dict[str, str], filename: str = "outputs/ddr_report.txt") -> bool:
    """
    Save generated report to text file.
    
    Args:
        report: Dictionary with sections and content
        filename: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("DETAILED DIAGNOSTIC REPORT (DDR)\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {import_datetime().now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for section, content in report.items():
                f.write(f"\n{'='*70}\n")
                f.write(f"{section.upper()}\n")
                f.write(f"{'='*70}\n\n")
                f.write(content)
                f.write("\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")
        
        return True
    except Exception as e:
        print(f"❌ Error saving report: {str(e)}")
        return False


def import_datetime():
    """Helper to import datetime."""
    from datetime import datetime
    return datetime


def format_report_for_console(report: Dict[str, str]) -> str:
    """
    Format report for console display.
    
    Args:
        report: Generated report dictionary
        
    Returns:
        Formatted string for console output
    """
    formatted = "\n" + "="*70 + "\n"
    formatted += "DETAILED DIAGNOSTIC REPORT (DDR)\n"
    formatted += "="*70 + "\n"
    
    for section, content in report.items():
        formatted += f"\n📋 {section.upper()}\n"
        formatted += "-" * 70 + "\n"
        formatted += content
        formatted += "\n"
    
    formatted += "\n" + "="*70 + "\n"
    return formatted


def export_to_json(report: Dict[str, str], filename: str = "outputs/ddr_report.json") -> bool:
    """
    Export report as JSON for programmatic access.
    
    Args:
        report: Generated report dictionary
        filename: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error exporting JSON: {str(e)}")
        return False


# Summary statistics
def get_report_summary(merged_data: List[Dict]) -> Dict[str, Any]:
    """
    Generate summary statistics for the report.
    
    Args:
        merged_data: List of merged observations
        
    Returns:
        Dictionary with summary stats
    """
    summary = {
        "total_issues": len(merged_data),
        "by_severity": {
            "Critical": sum(1 for o in merged_data if o.get("severity") == "Critical"),
            "High": sum(1 for o in merged_data if o.get("severity") == "High"),
            "Medium": sum(1 for o in merged_data if o.get("severity") == "Medium"),
            "Low": sum(1 for o in merged_data if o.get("severity") == "Low"),
        },
        "thermal_issues": sum(1 for o in merged_data if o.get("thermal_flag")),
        "areas_affected": len(set(o.get("area", "Unknown") for o in merged_data)),
        "unique_areas": sorted(set(o.get("area", "Unknown") for o in merged_data)),
    }
    return summary
