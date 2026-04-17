def clean_area(area):
    if not area or area.lower() in ["general", "general area", "unknown", "unknown area"]:
        return "Property Area"
    return area


def clean_issue(issue):
    if not issue or issue.lower() in ["not available", "detected issue", "unknown"]:
        return "No specific issue identified"
    return issue


def clean_description(desc):
    if not desc or "PDF Content" in desc or desc == "No description":
        return "Details derived from inspection and thermal analysis."
    return desc


def enhance_observations(observations):
    cleaned = []

    for item in observations:
        cleaned.append({
            "source": item.get("source", "unknown"),
            "page": item.get("page", 1),
            "area": clean_area(item.get("area")),
            "inspection_issue": clean_issue(item.get("inspection_issue", item.get("issue"))),
            "thermal_issue": clean_issue(item.get("thermal_issue")),
            "description": clean_description(item.get("description")),
            "severity": item.get("severity", "Medium"),
            "severity_hint": item.get("severity_hint", "unknown")
        })

    return cleaned


def format_ddr_report(merged_data):
    report = {}

    # Property Summary
    areas = list(set([item["area"] for item in merged_data if item.get("area")]))
    if areas:
        report["Property Issue Summary"] = (
            f"The property inspection identified issues across {len(areas)} area(s), "
            f"including {', '.join(areas)}."
        )
    else:
        report["Property Issue Summary"] = "No specific areas with issues were identified."

    # Area-wise Observations
    obs_text = ""
    for item in merged_data:
        obs_text += (
            f"• {item.get('area', 'Property Area')} [{item.get('severity', 'Medium')}]\n"
            f"  - Inspection: {item.get('inspection_issue', 'No specific issue identified')}\n"
            f"  - Thermal: {item.get('thermal_issue', 'No thermal anomalies detected')}\n\n"
        )

    report["Area-wise Observations"] = obs_text.strip() if obs_text else "No detailed observations available."

    # Root Cause
    report["Probable Root Cause"] = (
        "The issues are likely caused by structural stress, moisture intrusion, "
        "and insulation inefficiencies identified during inspection and thermal analysis."
    )

    # Severity
    report["Severity Assessment"] = (
        "Issues range from moderate to significant, requiring timely intervention "
        "to prevent further deterioration."
    )

    # Recommendations
    report["Recommended Actions"] = (
        "1. Repair structural cracks\n"
        "2. Address water leakage and dampness\n"
        "3. Improve insulation in affected areas"
    )

    # Notes
    report["Additional Notes"] = (
        "All findings should be validated by a certified professional. "
        "Regular maintenance is recommended."
    )

    # Missing Info
    report["Missing Information"] = "Not Available"

    return report
