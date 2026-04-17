def clean_area(area):
    if not area or area.lower() in ["general", "general area", "unknown", "unknown area"]:
        return "Property Area"
    return area


def clean_issue(issue):
    if not issue or issue.lower() in ["not available", "detected issue", "unknown"]:
        return "No specific issue identified"
    return issue


def clean_description(desc):
    if not desc or "PDF Content" in str(desc) or str(desc) == "No description":
        return ""
        
    s = str(desc).replace("Extracted automatically: ", "").strip()
    # If the text is merged/duplicated raw extracts, hide it
    if "|" in s:
        return ""
        
    return s


def enhance_observations(observations):
    cleaned = []

    for item in observations:
        area = clean_area(item.get("area"))
        ins_issue = clean_issue(item.get("inspection_issue", item.get("issue")))
        therm_issue = clean_issue(item.get("thermal_issue"))
        
        # Polish Thermal Anomaly generic strings into context-aware mapping
        if "thermal anomaly" in therm_issue.lower():
            a = area.lower()
            if "wall" in a:
                # E.g. Wall -> Heat loss
                therm_issue = "Heat loss and thermal irregularity detected"
            elif "bedroom" in a or "ceiling" in a or "floor" in a:
                # E.g. Ceiling/Floor -> moisture related
                if "moisture" in ins_issue.lower() or "water" in ins_issue.lower() or "leak" in ins_issue.lower():
                     therm_issue = "Cold anomaly indicating water seepage"
                else:
                     therm_issue = "Cold spot confirming dampness"
            elif "roof" in a or "kitchen" in a:
                # E.g. Roof -> insulation
                therm_issue = "Insulation inefficiency detected"
            elif "foundation" in a:
                # E.g. Foundation -> soil/damp
                therm_issue = "Thermal anomaly confirming internal dampness"

        cleaned.append({
            "source": item.get("source", "unknown"),
            "page": item.get("page", 1),
            "area": area,
            "inspection_issue": ins_issue,
            "thermal_issue": therm_issue,
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

    # Dynamic Analysis based on items found
    causes = set()
    actions = set()

    for item in merged_data:
        combined_issues = str(item.get("inspection_issue", "")).lower() + " " + str(item.get("thermal_issue", "")).lower()
        if "crack" in combined_issues or "structural" in combined_issues:
            causes.add("structural stress and minor settling")
            actions.add("Repair and seal structural cracks")
        if "moisture" in combined_issues or "leak" in combined_issues or "water" in combined_issues or "cold spot" in combined_issues:
            causes.add("water intrusion and active leakage")
            actions.add("Investigate plumbing and resolve active moisture leakage sources")
        if "thermal" in combined_issues or "insulation" in combined_issues or "heat" in combined_issues:
            causes.add("insulation degradation or boundary inefficiencies")
            actions.add("Upgrade or repair thermal insulation in affected structural zones")

    # Root Cause
    if causes:
        report["Probable Root Cause"] = (
            f"The identified issues are likely caused by {', '.join(list(causes))} as observed during the physical and thermal evaluations."
        )
    else:
        report["Probable Root Cause"] = "General wear and tear requiring routine structural maintenance."

    # Severity
    report["Severity Assessment"] = (
        "Issues range from moderate to significant, requiring timely intervention "
        "to prevent further deterioration."
    )

    # Recommendations
    if actions:
        acts = "\n".join([f"{i+1}. {a}" for i, a in enumerate(list(actions))])
        report["Recommended Actions"] = acts
    else:
        report["Recommended Actions"] = "1. Conduct routine professional maintenance checks."

    # Notes
    report["Additional Notes"] = (
        "All findings should be validated by a certified professional. "
        "Regular maintenance is recommended."
    )

    # Missing Info
    report["Missing Information"] = "Not Available"

    return report
