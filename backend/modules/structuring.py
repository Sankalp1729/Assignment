"""Data structuring module - Organize extracted data into coherent schemas"""

from typing import Dict, List, Any
from collections import defaultdict
from .data_models import (
    ExtractionResult,
    StructuredData,
    Observation,
    ImageReference,
)


class DataStructurer:
    """Organizes raw extracted data into structured schemas"""

    def __init__(self):
        pass

    def structure_extraction_results(
        self, extraction_results: List[ExtractionResult]
    ) -> StructuredData:
        """
        Organize multiple extraction results into a coherent structure.
        
        Creates:
        1. Area-wise grouping (Terrace, South Wall, etc.)
        2. Category-wise grouping (Structural, Thermal, Moisture, etc.)
        3. Unified observation list
        4. Unified image list
        """
        area_wise_data = defaultdict(list)
        category_wise_data = defaultdict(list)
        all_observations = []
        all_images = []

        # Aggregate data from all sources
        for result in extraction_results:
            all_observations.extend(result.observations)
            all_images.extend(result.images)

            # Group by area
            for obs in result.observations:
                area_wise_data[obs.area].append(obs)

            # Group by category
            for obs in result.observations:
                category_wise_data[obs.category].append(obs)

        # Sort by severity within each area
        for area in area_wise_data:
            area_wise_data[area].sort(
                key=lambda x: (x.severity.value, -x.confidence), reverse=False
            )

        structured_data = StructuredData(
            area_wise_data=dict(area_wise_data),
            category_wise_data=dict(category_wise_data),
            all_observations=all_observations,
            all_images=all_images,
            extraction_results=extraction_results,
        )

        return structured_data

    def create_area_summary(self, observations: List[Observation]) -> Dict[str, Any]:
        """
        Create a summary for a specific area.
        
        Summary includes:
        - Issue count by severity
        - Categories present
        - Key observations
        """
        summary = {
            "total_issues": len(observations),
            "severity_breakdown": self._count_by_severity(observations),
            "categories": list(set(obs.category for obs in observations)),
            "high_priority_issues": [
                obs.description
                for obs in observations
                if obs.severity.value in ["CRITICAL", "HIGH"]
            ],
        }
        return summary

    def create_category_summary(
        self, observations: List[Observation]
    ) -> Dict[str, Any]:
        """
        Create a summary for a specific category.
        
        Summary includes:
        - Issue count by severity
        - Areas affected
        - Key patterns
        """
        summary = {
            "total_issues": len(observations),
            "severity_breakdown": self._count_by_severity(observations),
            "areas_affected": list(set(obs.area for obs in observations)),
            "average_confidence": sum(obs.confidence for obs in observations)
            / len(observations)
            if observations
            else 0,
        }
        return summary

    def _count_by_severity(self, observations: List[Observation]) -> Dict[str, int]:
        """Count observations by severity level"""
        severity_count = defaultdict(int)
        for obs in observations:
            severity_count[obs.severity.value] += 1
        return dict(severity_count)

    def identify_related_observations(
        self, observations: List[Observation]
    ) -> Dict[str, List[str]]:
        """
        Identify observations that are likely related.
        
        Relationships:
        - Same area + same category
        - Common image references
        - Sequential pages in document
        """
        relationships = defaultdict(list)

        for obs1 in observations:
            for obs2 in observations:
                if obs1.observation_id >= obs2.observation_id:
                    continue

                # Same area + same category
                if obs1.area == obs2.area and obs1.category == obs2.category:
                    relationships[obs1.observation_id].append(obs2.observation_id)
                    continue

                # Common image references
                common_images = set(obs1.image_references) & set(
                    obs2.image_references
                )
                if common_images:
                    relationships[obs1.observation_id].append(obs2.observation_id)

        return dict(relationships)

    def validate_structure(self, structured_data: StructuredData) -> Dict[str, Any]:
        """
        Validate the structured data for consistency and completeness.
        """
        validation = {
            "valid": True,
            "warnings": [],
            "stats": {
                "total_observations": len(structured_data.all_observations),
                "areas": len(structured_data.area_wise_data),
                "categories": len(structured_data.category_wise_data),
                "images": len(structured_data.all_images),
            },
        }

        # Check for observations without area
        unassigned = [
            obs
            for obs in structured_data.all_observations
            if obs.area == "Not Specified"
        ]
        if unassigned:
            validation["warnings"].append(
                f"{len(unassigned)} observations without specific area assignment"
            )

        # Check for observations without category
        uncategorized = [
            obs
            for obs in structured_data.all_observations
            if obs.category == "Other"
        ]
        if uncategorized:
            validation["warnings"].append(
                f"{len(uncategorized)} observations without specific category"
            )

        return validation
