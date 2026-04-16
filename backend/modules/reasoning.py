"""Reasoning module - Cross-reference documents, detect conflicts, identify missing data"""

from typing import List, Dict, Any, Tuple
from .data_models import (
    Observation,
    DocumentType,
    ConflictRecord,
    MissingData,
    ReasoningOutput,
    StructuredData,
    SeverityLevel,
)


class ReasoningEngine:
    """Performs reasoning across multiple documents"""

    def __init__(self):
        self.conflict_threshold = 0.6  # Confidence mismatch threshold

    def analyze_structured_data(self, structured_data: StructuredData) -> ReasoningOutput:
        """
        Perform comprehensive reasoning on structured data.
        
        1. Detect conflicts between documents
        2. Identify missing information
        3. Extract root causes
        4. Generate cross-document insights
        """
        # Detect conflicts
        conflicts = self._detect_conflicts(structured_data.all_observations)

        # Identify missing data
        missing_data = self._identify_missing_data(
            structured_data.area_wise_data,
            structured_data.extraction_results,
        )

        # Extract root causes
        root_causes = self._extract_root_causes(structured_data.all_observations)

        # Generate insights
        insights = self._generate_insights(structured_data)

        reasoning_output = ReasoningOutput(
            conflicts=conflicts,
            missing_data=missing_data,
            root_causes=root_causes,
            cross_doc_insights=insights,
        )

        return reasoning_output

    def _detect_conflicts(self, observations: List[Observation]) -> List[ConflictRecord]:
        """
        Detect conflicting observations across documents.
        
        Conflict detection:
        - Same area, same category, but different severity from different sources
        - Temperature conflicts (thermal vs inspection)
        - Contradictory descriptions
        """
        conflicts = []

        # Group by area and category
        grouped = {}
        for obs in observations:
            key = (obs.area, obs.category)
            if key not in grouped:
                grouped[key] = {"thermal": [], "inspection": [], "other": []}

            if obs.document_type == DocumentType.THERMAL_REPORT:
                grouped[key]["thermal"].append(obs)
            elif obs.document_type == DocumentType.INSPECTION_REPORT:
                grouped[key]["inspection"].append(obs)
            else:
                grouped[key]["other"].append(obs)

        # Check for conflicts in each group
        for (area, category), obs_groups in grouped.items():
            # Check severity conflicts
            if obs_groups["thermal"] and obs_groups["inspection"]:
                thermal_obs = obs_groups["thermal"]
                inspection_obs = obs_groups["inspection"]

                # Check for significant severity mismatches
                thermal_severities = [obs.severity for obs in thermal_obs]
                inspection_severities = [obs.severity for obs in inspection_obs]

                if self._has_severity_conflict(thermal_severities, inspection_severities):
                    conflict = ConflictRecord(
                        conflict_id=f"conflict_{area}_{category}",
                        observations=thermal_obs + inspection_obs,
                        description=f"Severity mismatch for {category} in {area}: "
                        f"Thermal reports {thermal_severities}, "
                        f"Inspection reports {inspection_severities}",
                    )
                    conflicts.append(conflict)

        return conflicts

    def _has_severity_conflict(
        self, severities1: List[SeverityLevel], severities2: List[SeverityLevel]
    ) -> bool:
        """Check if two severity lists have significant conflicts"""
        severity_order = {
            SeverityLevel.CRITICAL: 1,
            SeverityLevel.HIGH: 2,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.LOW: 4,
            SeverityLevel.NOT_AVAILABLE: 5,
        }

        # Filter out NOT_AVAILABLE
        s1 = [s for s in severities1 if s != SeverityLevel.NOT_AVAILABLE]
        s2 = [s for s in severities2 if s != SeverityLevel.NOT_AVAILABLE]

        if not s1 or not s2:
            return False

        # Get weighted averages
        avg1 = sum(severity_order[s] for s in s1) / len(s1)
        avg2 = sum(severity_order[s] for s in s2) / len(s2)

        # Conflict if difference > threshold (2 levels apart)
        return abs(avg1 - avg2) >= 2

    def _identify_missing_data(
        self,
        area_wise_data: Dict[str, List[Observation]],
        extraction_results: List,
    ) -> List[MissingData]:
        """
        Identify missing information.
        
        Missing data types:
        - Thermal readings for specific areas (if thermal report exists but incomplete)
        - Inspection notes for specific areas
        - Images for critical areas
        """
        missing_data = []

        # Check if thermal report was provided
        has_thermal_report = any(
            result.document_type == DocumentType.THERMAL_REPORT
            for result in extraction_results
        )

        if has_thermal_report:
            # Check which areas lack thermal data
            areas_with_thermal = set()
            for result in extraction_results:
                if result.document_type == DocumentType.THERMAL_REPORT:
                    for obs in result.observations:
                        areas_with_thermal.add(obs.area)

            # Common areas to check
            common_areas = ["Terrace", "South Wall", "East Wall", "West Wall", "Foundation"]
            for area in common_areas:
                if area not in areas_with_thermal and area in area_wise_data:
                    missing = MissingData(
                        data_type=f"thermal_readings_{area.lower().replace(' ', '_')}",
                        expected_source="THERMAL_REPORT",
                        reason="Thermal data not available for this area",
                    )
                    missing_data.append(missing)

        return missing_data

    def _extract_root_causes(
        self, observations: List[Observation]
    ) -> Dict[str, str]:
        """
        Extract root causes from observations.
        
        Root cause analysis:
        - Group related issues
        - Identify common causes
        - Avoid speculation (only from explicit descriptions)
        """
        root_causes = {}

        # Group by category
        by_category = {}
        for obs in observations:
            if obs.category not in by_category:
                by_category[obs.category] = []
            by_category[obs.category].append(obs)

        # Extract causes for each category
        for category, obs_list in by_category.items():
            # Look for causative keywords in descriptions
            causes = self._extract_cause_keywords(obs_list)
            if causes:
                root_causes[category] = ", ".join(causes)
            elif obs_list and obs_list[0].severity != SeverityLevel.NOT_AVAILABLE:
                # If no explicit cause, mark as "Requires further investigation"
                root_causes[category] = "Requires further investigation"

        return root_causes

    def _extract_cause_keywords(self, observations: List[Observation]) -> List[str]:
        """Extract cause-related keywords from observations"""
        cause_keywords = {
            "water": ["water leakage", "moisture", "dampness", "wet"],
            "structural": ["crack", "settlement", "fracture", "damage"],
            "thermal": ["thermal loss", "insulation", "temperature", "heat"],
            "aging": ["aged", "worn", "deterioration", "old"],
        }

        found_causes = set()

        for obs in observations:
            desc_lower = obs.description.lower()
            for cause, keywords in cause_keywords.items():
                if any(kw in desc_lower for kw in keywords):
                    found_causes.add(cause.capitalize())

        return list(found_causes)

    def _generate_insights(self, structured_data: StructuredData) -> List[str]:
        """Generate cross-document insights"""
        insights = []

        # Insight 1: Multiple issues in same area
        for area, obs_list in structured_data.area_wise_data.items():
            if len(obs_list) > 3:
                insights.append(
                    f"Area '{area}' has multiple issues ({len(obs_list)}), suggesting "
                    "systematic problem or multiple root causes."
                )

        # Insight 2: Corroborating evidence from multiple documents
        for category, obs_list in structured_data.category_wise_data.items():
            doc_types = set(obs.document_type for obs in obs_list)
            if len(doc_types) > 1:
                insights.append(
                    f"Category '{category}' is corroborated by multiple document types "
                    "(inspection and thermal), increasing confidence."
                )

        # Insight 3: High-confidence observations
        high_confidence = [
            obs for obs in structured_data.all_observations if obs.confidence > 0.8
        ]
        if len(high_confidence) >= 3:
            insights.append(
                f"Found {len(high_confidence)} high-confidence observations, "
                "indicating clear and documented issues."
            )

        return insights
