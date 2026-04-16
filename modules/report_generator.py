"""Report generation module - Create client-friendly DDR reports"""

import json
from typing import Dict, Any
from datetime import datetime
from .data_models import (
    DDRReport,
    StructuredData,
    ReasoningOutput,
    Observation,
    SeverityLevel,
)


class ReportGenerator:
    """Generates client-ready DDR reports"""

    def __init__(self):
        pass

    def generate_ddr_report(
        self,
        structured_data: StructuredData,
        reasoning_output: ReasoningOutput,
    ) -> DDRReport:
        """
        Generate complete DDR report from structured data and reasoning.
        """
        report = DDRReport(
            report_id=f"ddr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generation_date=datetime.now(),
            property_summary=self._generate_property_summary(structured_data),
            area_wise_observations=self._generate_area_wise_observations(
                structured_data
            ),
            root_cause_analysis=self._generate_root_cause_analysis(reasoning_output),
            severity_assessment=self._generate_severity_assessment(
                structured_data, reasoning_output
            ),
            recommended_actions=self._generate_recommended_actions(structured_data),
            missing_information=reasoning_output.missing_data,
            conflicts_noted=reasoning_output.conflicts,
            image_mappings=self._create_image_mappings(structured_data),
        )

        return report

    def _generate_property_summary(self, structured_data: StructuredData) -> Dict[str, Any]:
        """Generate overall property summary"""
        all_obs = structured_data.all_observations

        summary = {
            "total_observations": len(all_obs),
            "areas_affected": len(structured_data.area_wise_data),
            "categories_identified": len(structured_data.category_wise_data),
            "critical_count": len(
                [o for o in all_obs if o.severity == SeverityLevel.CRITICAL]
            ),
            "high_count": len([o for o in all_obs if o.severity == SeverityLevel.HIGH]),
            "medium_count": len(
                [o for o in all_obs if o.severity == SeverityLevel.MEDIUM]
            ),
            "low_count": len([o for o in all_obs if o.severity == SeverityLevel.LOW]),
            "not_available_count": len(
                [o for o in all_obs if o.severity == SeverityLevel.NOT_AVAILABLE]
            ),
        }

        # Overall status
        if summary["critical_count"] > 0:
            summary["overall_status"] = "CRITICAL - Immediate attention required"
        elif summary["high_count"] > 2:
            summary["overall_status"] = "HIGH PRIORITY - Urgent attention needed"
        elif summary["medium_count"] > 0:
            summary["overall_status"] = "MEDIUM PRIORITY - Schedule maintenance"
        else:
            summary["overall_status"] = "LOW PRIORITY - Monitor situation"

        return summary

    def _generate_area_wise_observations(
        self, structured_data: StructuredData
    ) -> Dict[str, Any]:
        """Generate area-wise detailed observations"""
        area_observations = {}

        for area, obs_list in structured_data.area_wise_data.items():
            # Summarize by severity
            by_severity = {}
            for obs in obs_list:
                severity = obs.severity.value
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(
                    {
                        "category": obs.category,
                        "description": obs.description,
                        "confidence": obs.confidence,
                        "source": obs.document_type.value,
                        "observation_id": obs.observation_id,
                    }
                )

            area_observations[area] = {
                "total_issues": len(obs_list),
                "severity_breakdown": {
                    severity: len(issues) for severity, issues in by_severity.items()
                },
                "issues_by_severity": by_severity,
            }

        return area_observations

    def _generate_root_cause_analysis(
        self, reasoning_output: ReasoningOutput
    ) -> list:
        """Generate root cause analysis"""
        analysis = []

        for category, cause in reasoning_output.root_causes.items():
            analysis.append(
                {
                    "category": category,
                    "identified_cause": cause,
                    "confidence": "High"
                    if cause != "Requires further investigation"
                    else "Low",
                }
            )

        return analysis

    def _generate_severity_assessment(
        self, structured_data: StructuredData, reasoning_output: ReasoningOutput
    ) -> Dict[str, Any]:
        """Generate severity assessment"""
        all_obs = structured_data.all_observations

        assessment = {
            "immediate_action_required": [
                {
                    "area": obs.area,
                    "category": obs.category,
                    "description": obs.description,
                    "reason": "CRITICAL severity",
                }
                for obs in all_obs
                if obs.severity == SeverityLevel.CRITICAL
            ],
            "high_priority": [
                {
                    "area": obs.area,
                    "category": obs.category,
                    "description": obs.description,
                    "reason": "HIGH severity",
                }
                for obs in all_obs
                if obs.severity == SeverityLevel.HIGH
            ],
            "conflicts_affecting_assessment": [
                {
                    "conflict_id": conflict.conflict_id,
                    "description": conflict.description,
                    "resolution_status": conflict.resolution_status,
                }
                for conflict in reasoning_output.conflicts
            ],
        }

        return assessment

    def _generate_recommended_actions(
        self, structured_data: StructuredData
    ) -> list:
        """Generate recommended actions"""
        actions = []
        action_templates = {
            "Structural": "Conduct detailed structural inspection and assess stability",
            "Thermal": "Review insulation and consider thermal retrofitting",
            "Moisture": "Identify and seal water ingress points, improve drainage",
            "Aging": "Replace or restore aged components",
            "Other": "Further investigation recommended",
        }

        categories_with_issues = set(
            obs.category for obs in structured_data.all_observations
        )

        for category in categories_with_issues:
            template = action_templates.get(category, action_templates["Other"])
            actions.append(
                {
                    "category": category,
                    "recommended_action": template,
                    "priority": "Urgent"
                    if any(
                        obs.category == category
                        and obs.severity
                        in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
                        for obs in structured_data.all_observations
                    )
                    else "Standard",
                }
            )

        return actions

    def _create_image_mappings(self, structured_data: StructuredData) -> Dict[str, list]:
        """Create mappings between observations and images"""
        mappings = {}

        for obs in structured_data.all_observations:
            if obs.image_references:
                mappings[obs.observation_id] = obs.image_references

        return mappings

    def export_to_json(self, report: DDRReport, output_path: str) -> None:
        """Export report to JSON"""
        report_dict = {
            "report_id": report.report_id,
            "generation_date": report.generation_date.isoformat(),
            "property_summary": report.property_summary,
            "area_wise_observations": report.area_wise_observations,
            "root_cause_analysis": report.root_cause_analysis,
            "severity_assessment": report.severity_assessment,
            "recommended_actions": report.recommended_actions,
            "missing_information": [
                {
                    "data_type": md.data_type,
                    "expected_source": md.expected_source,
                    "reason": md.reason,
                }
                for md in report.missing_information
            ],
            "conflicts_noted": [
                {
                    "conflict_id": c.conflict_id,
                    "description": c.description,
                    "resolution_status": c.resolution_status,
                    "note": c.notes,
                }
                for c in report.conflicts_noted
            ],
            "image_mappings": report.image_mappings,
        }

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)

    def export_to_text(self, report: DDRReport, output_path: str) -> None:
        """Export report to human-readable text format"""
        with open(output_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("DETAILED DIAGNOSTIC REPORT (DDR)\n")
            f.write(f"Report ID: {report.report_id}\n")
            f.write(f"Generated: {report.generation_date}\n")
            f.write("=" * 80 + "\n\n")

            # Property Summary
            f.write("PROPERTY SUMMARY\n")
            f.write("-" * 80 + "\n")
            for key, value in report.property_summary.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            # Area-wise Observations
            f.write("AREA-WISE OBSERVATIONS\n")
            f.write("-" * 80 + "\n")
            for area, data in report.area_wise_observations.items():
                f.write(f"\n{area}:\n")
                f.write(f"  Total Issues: {data['total_issues']}\n")
                for severity, count in data["severity_breakdown"].items():
                    f.write(f"  {severity}: {count}\n")

            # Root Cause Analysis
            f.write("\n\nROOT CAUSE ANALYSIS\n")
            f.write("-" * 80 + "\n")
            for analysis in report.root_cause_analysis:
                f.write(f"\n{analysis['category']}:\n")
                f.write(f"  Cause: {analysis['identified_cause']}\n")
                f.write(f"  Confidence: {analysis['confidence']}\n")

            # Recommended Actions
            f.write("\n\nRECOMMENDED ACTIONS\n")
            f.write("-" * 80 + "\n")
            for action in report.recommended_actions:
                f.write(f"\n{action['category']} ({action['priority']}):\n")
                f.write(f"  {action['recommended_action']}\n")

            # Missing Information
            if report.missing_information:
                f.write("\n\nMISSING INFORMATION\n")
                f.write("-" * 80 + "\n")
                for missing in report.missing_information:
                    f.write(f"\n{missing.data_type}:\n")
                    f.write(f"  Expected from: {missing.expected_source}\n")
                    f.write(f"  Reason: {missing.reason}\n")

            # Conflicts
            if report.conflicts_noted:
                f.write("\n\nCONFLICTS NOTED\n")
                f.write("-" * 80 + "\n")
                for conflict in report.conflicts_noted:
                    f.write(f"\n{conflict.conflict_id}:\n")
                    f.write(f"  {conflict.description}\n")
                    f.write(f"  Status: {conflict.resolution_status}\n")
