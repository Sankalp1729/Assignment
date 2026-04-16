"""
Gemini-based structured observation extraction.
Converts schema data into standardized Observation objects with confidence scoring.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

import google.generativeai as genai

# Import core data models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.data_models import (
    Observation, SeverityLevel, DocumentType
)


logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Observation confidence levels."""
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30


@dataclass
class ExtractionContext:
    """Context information for observation extraction."""
    document_type: str
    source_filename: str
    extraction_method: str = "gemini"
    additional_notes: str = ""


class GeminiObservationExtractor:
    """
    Converts schema data into structured Observation objects.
    Uses Gemini for intelligent categorization and severity assessment.
    """

    CATEGORY_MAPPING = {
        "structural": "Structural",
        "thermal": "Thermal",
        "electrical": "Electrical",
        "plumbing": "Plumbing",
        "roofing": "Roofing",
        "moisture": "Moisture",
        "finishing": "Finishing",
        "insulation": "Insulation",
        "hvac": "HVAC",
        "exterior": "Exterior",
        "default": "Structural"
    }

    SEVERITY_PROMPT = """
You are a building defect severity expert. Given the following issue description, 
determine the appropriate severity level:

Issue: {issue_description}
Category: {category}
Location: {location}

Return ONLY one of: CRITICAL, HIGH, MEDIUM, LOW

Criteria:
- CRITICAL: Safety hazard, structural risk, immediate remediation needed
- HIGH: Major defect, affects usability, urgent remediation needed
- MEDIUM: Noticeable defect, should be addressed within months
- LOW: Minor defect, cosmetic or can be monitored

Return only the single word severity level. No explanation."""

    CATEGORY_PROMPT = """
You are a building inspection expert. Categorize this observation:

Description: {description}
Location: {location}
Original category hint: {hint}

Return ONLY one of these categories:
structural, thermal, electrical, plumbing, roofing, moisture, finishing, insulation, hvac, exterior

Return only the category name. No explanation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize observation extractor."""
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def extract_observations(
        self,
        schema_data: Dict[str, Any],
        context: ExtractionContext,
        images: Optional[List[bytes]] = None
    ) -> Tuple[List[Observation], Dict[str, Any]]:
        """
        Convert schema data into Observation objects.
        
        Args:
            schema_data: Extracted schema dictionary
            context: ExtractionContext with metadata
            images: Optional list of image bytes
            
        Returns:
            Tuple of (observations_list, extraction_metadata)
        """
        observations = []
        metadata = {
            "total_issues_found": 0,
            "confidence_scores": [],
            "categorization_method": "gemini",
            "extraction_errors": []
        }
        
        # Extract issues from schema
        issues = self._extract_issues_from_schema(schema_data)
        logger.info(f"Found {len(issues)} issues to convert to observations")
        
        for issue in issues:
            try:
                # Determine category
                category = self._determine_category(issue, images)
                
                # Determine severity
                severity = self._determine_severity(issue, category)
                
                # Calculate confidence
                confidence = self._calculate_observation_confidence(issue, category, severity)
                
                # Generate observation ID
                obs_id = self._generate_observation_id(context, len(observations))
                
                # Map document type
                doc_type = self._map_document_type(context.document_type)
                
                # Create observation
                observation = Observation(
                    observation_id=obs_id,
                    document_type=doc_type,
                    area=issue.get("location", "Unknown Area"),
                    category=category,
                    description=issue.get("description", ""),
                    severity=severity,
                    confidence=confidence,
                    image_references=issue.get("image_refs", []),
                    raw_data=issue  # Store original data
                )
                
                observations.append(observation)
                metadata["confidence_scores"].append(confidence)
                
            except Exception as e:
                error_msg = f"Failed to extract observation from issue {issue}: {str(e)}"
                logger.error(error_msg)
                metadata["extraction_errors"].append(error_msg)
        
        metadata["total_issues_found"] = len(observations)
        metadata["avg_confidence"] = sum(metadata["confidence_scores"]) / len(metadata["confidence_scores"]) if metadata["confidence_scores"] else 0
        
        return observations, metadata

    def _extract_issues_from_schema(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract individual issues/findings from schema."""
        issues = []
        
        # Common keys for issues lists
        issue_keys = [
            "Identified Issues", "identified_issues", "issues",
            "Thermal Anomalies", "thermal_anomalies", "anomalies",
            "Moisture Reading Locations", "moisture_readings", "readings",
            "Main Findings", "findings", "observations"
        ]
        
        for key in issue_keys:
            if key in schema_data:
                items = schema_data[key]
                if isinstance(items, list):
                    issues.extend(items)
                elif isinstance(items, dict):
                    issues.append(items)
        
        # If no issues found, try to extract from free-form text
        if not issues and "findings_text" in schema_data:
            issues.append({
                "description": schema_data["findings_text"],
                "location": schema_data.get("location", "Property"),
                "severity_hint": schema_data.get("severity", "MEDIUM")
            })
        
        return issues

    def _determine_category(self, issue: Dict[str, Any], images: Optional[List[bytes]] = None) -> str:
        """Determine observation category using Gemini."""
        hint = issue.get("category", issue.get("Category", "structural"))
        description = issue.get("description", issue.get("Description", ""))
        location = issue.get("location", issue.get("Location", "Unknown"))
        
        # Create categorization prompt
        prompt = self.CATEGORY_PROMPT.format(
            description=description[:300],
            location=location,
            hint=hint
        )
        
        try:
            response = self.model.generate_content(prompt)
            category_str = response.text.strip().lower()
            
            # Map to category string
            for key, cat_str in self.CATEGORY_MAPPING.items():
                if key != "default" and key in category_str:
                    logger.debug(f"Categorized as: {cat_str}")
                    return cat_str
            
            # Fallback to hint or default
            for key, cat_str in self.CATEGORY_MAPPING.items():
                if key != "default" and key in hint.lower():
                    return cat_str
            
            return self.CATEGORY_MAPPING["default"]
            
        except Exception as e:
            logger.warning(f"Gemini categorization failed: {e}, using fallback")
            return self.CATEGORY_MAPPING.get(hint.lower(), Category.STRUCTURAL)

    def _determine_severity(self, issue: Dict[str, Any], category: str) -> SeverityLevel:
        """Determine severity using Gemini."""
        description = issue.get("description", issue.get("Description", ""))
        location = issue.get("location", issue.get("Location", ""))
        severity_hint = issue.get("severity", issue.get("Severity", ""))
        
        # Check if severity already provided
        if severity_hint:
            try:
                return SeverityLevel[severity_hint.upper()]
            except (KeyError, AttributeError):
                pass
        
        # Use Gemini to assess severity
        prompt = self.SEVERITY_PROMPT.format(
            issue_description=description[:300],
            category=category.value,
            location=location
        )
        
        try:
            response = self.model.generate_content(prompt)
            severity_str = response.text.strip().upper()
            
            # Map to SeverityLevel enum
            if "CRITICAL" in severity_str:
                return SeverityLevel.CRITICAL
            elif "HIGH" in severity_str:
                return SeverityLevel.HIGH
            elif "MEDIUM" in severity_str:
                return SeverityLevel.MEDIUM
            elif "LOW" in severity_str:
                return SeverityLevel.LOW
            
        except Exception as e:
            logger.warning(f"Gemini severity assessment failed: {e}")
        
        # Fallback based on keywords
        desc_lower = description.lower()
        if any(w in desc_lower for w in ["critical", "urgent", "danger", "hazard", "unsafe"]):
            return SeverityLevel.CRITICAL
        elif any(w in desc_lower for w in ["major", "significant", "failure", "broken"]):
            return SeverityLevel.HIGH
        elif any(w in desc_lower for w in ["moderate", "noticeable", "damage"]):
            return SeverityLevel.MEDIUM
        
        return SeverityLevel.LOW

    def _calculate_observation_confidence(
        self,
        issue: Dict[str, Any],
        category: str,
        severity: SeverityLevel
    ) -> float:
        """Calculate confidence score for observation (0-1)."""
        # Base confidence
        confidence = 0.5
        
        # Factor 1: Issue description completeness
        description_length = len(issue.get("description", ""))
        if description_length > 100:
            confidence += 0.15
        elif description_length > 50:
            confidence += 0.10
        
        # Factor 2: Location specificity
        location = issue.get("location", "")
        if location and location != "Unknown":
            confidence += 0.10
        
        # Factor 3: Recommended action presence
        if "recommended" in str(issue).lower() or "action" in str(issue).lower():
            confidence += 0.10
        
        # Factor 4: Image references
        if issue.get("image_refs"):
            confidence += 0.10
        
        # Factor 5: Severity level confidence
        if severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
            confidence += 0.05  # High severity more certain
        
        return min(1.0, max(0.3, confidence))

    def _generate_observation_id(self, context: ExtractionContext, index: int) -> str:
        """Generate unique observation ID."""
        import hashlib
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d")
        source_hash = hashlib.md5(context.source_filename.encode()).hexdigest()[:4]
        return f"OBS_{timestamp}_{source_hash}_{index + 1:03d}"

    def _map_document_type(self, doc_type_str: str) -> DocumentType:
        """Map string document type to DocumentType enum."""
        doc_type_lower = doc_type_str.lower()
        
        if "thermal" in doc_type_lower:
            return DocumentType.THERMAL_REPORT
        elif "inspection" in doc_type_lower:
            return DocumentType.INSPECTION_REPORT
        else:
            return DocumentType.OTHER

    def batch_extract_observations(
        self,
        schemas: List[Dict[str, Any]],
        contexts: List[ExtractionContext],
        images_list: Optional[List[List[bytes]]] = None
    ) -> List[Tuple[List[Observation], Dict[str, Any]]]:
        """
        Extract observations from multiple schemas.
        
        Args:
            schemas: List of schema dictionaries
            contexts: List of ExtractionContext objects
            images_list: Optional list of image lists
            
        Returns:
            List of (observations, metadata) tuples
        """
        results = []
        
        for idx, schema in enumerate(schemas):
            context = contexts[idx]
            images = images_list[idx] if images_list and idx < len(images_list) else None
            
            obs, meta = self.extract_observations(schema, context, images)
            results.append((obs, meta))
        
        return results

    def merge_observations(
        self,
        observation_batches: List[List[Observation]]
    ) -> Tuple[List[Observation], Dict[str, Any]]:
        """
        Merge observations from multiple sources.
        Deduplicates and combines observations from different documents.
        """
        merged = []
        metadata = {
            "total_input_observations": sum(len(b) for b in observation_batches),
            "merge_strategy": "gemini_deduplication",
            "duplicates_removed": 0
        }
        
        # Flatten all observations
        all_obs = [obs for batch in observation_batches for obs in batch]
        
        # Simple deduplication: same area + category + similar description
        seen = set()
        for obs in all_obs:
            # Create dedup key
            key = f"{obs.area}_{obs.category.value}_{obs.severity.value}"
            
            if key not in seen:
                merged.append(obs)
                seen.add(key)
            else:
                metadata["duplicates_removed"] += 1
        
        metadata["total_merged_observations"] = len(merged)
        
        return merged, metadata
