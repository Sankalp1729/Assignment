"""
Gemini-enhanced conflict detection and resolution.
Merges observations from multiple sources with AI-assisted conflict analysis.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

import google.generativeai as genai

# Import core models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.data_models import (
    Observation, SeverityLevel, ConflictRecord
)


logger = logging.getLogger(__name__)


@dataclass
class ConflictAnalysis:
    """Analysis result for a conflict."""
    conflict_id: str
    severity_discrepancy: str  # e.g., "HIGH vs MEDIUM"
    likely_cause: str
    recommendation: str
    confidence: float  # 0-1
    resolved_severity: SeverityLevel


class GeminiConflictResolver:
    """
    Detects and resolves conflicts between observations from different documents.
    Uses Gemini to intelligently assess which observation is more reliable.
    """

    CONFLICT_ANALYSIS_PROMPT = """
You are a building inspection expert analyzing conflicting assessments.

Document 1: {doc1_type}
- Observation: {obs1_description}
- Location: {obs1_location}
- Category: {obs1_category}
- Severity: {obs1_severity}

Document 2: {doc2_type}
- Observation: {obs2_description}
- Location: {obs2_location}
- Category: {obs2_category}
- Severity: {obs2_severity}

Analyze this conflict and provide a JSON response with:
{{
    "likely_cause": "Why are the assessments different?",
    "more_reliable_document": "{doc_choice}",
    "confidence_in_resolution": 0.0-1.0,
    "recommended_severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "explanation": "Why this resolution?"
}}

Be concise but thorough in your analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize conflict resolver."""
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def detect_conflicts(
        self,
        observations_batch1: List[Observation],
        observations_batch2: List[Observation],
        severity_threshold: int = 2
    ) -> Tuple[List[ConflictAnalysis], List[Observation]]:
        """
        Detect conflicts between two sets of observations.
        
        Args:
            observations_batch1: Observations from document 1
            observations_batch2: Observations from document 2
            severity_threshold: Minimum severity level difference to flag conflict
            
        Returns:
            Tuple of (conflicts_list, merged_observations)
        """
        conflicts = []
        merged = list(observations_batch1)  # Start with batch 1
        
        severity_order = {
            SeverityLevel.CRITICAL: 1,
            SeverityLevel.HIGH: 2,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.LOW: 4,
            SeverityLevel.NOT_AVAILABLE: 5
        }
        
        # Find matching observations (same area + category)
        for obs2 in observations_batch2:
            matching_obs1 = self._find_matching_observation(obs2, observations_batch1)
            
            if matching_obs1:
                # Check severity discrepancy
                sev1_rank = severity_order.get(matching_obs1.severity, 5)
                sev2_rank = severity_order.get(obs2.severity, 5)
                discrepancy = abs(sev1_rank - sev2_rank)
                
                if discrepancy >= severity_threshold:
                    # Analyze conflict
                    analysis = self._analyze_conflict_with_gemini(
                        matching_obs1, obs2,
                        discrepancy
                    )
                    conflicts.append(analysis)
                    
                    # Use resolved severity
                    merged_obs = self._merge_observations(
                        matching_obs1, obs2, analysis.resolved_severity
                    )
                    # Replace obs1 with merged version
                    idx = merged.index(matching_obs1)
                    merged[idx] = merged_obs
                else:
                    # Minor discrepancy, just use average
                    merged_obs = self._merge_observations(matching_obs1, obs2)
                    idx = merged.index(matching_obs1)
                    merged[idx] = merged_obs
            else:
                # No match, add as new observation
                merged.append(obs2)
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        return conflicts, merged

    def _find_matching_observation(
        self,
        obs: Observation,
        candidates: List[Observation]
    ) -> Optional[Observation]:
        """Find matching observation in candidates (same area + category)."""
        for candidate in candidates:
            if (candidate.area.lower() == obs.area.lower() and
                candidate.category == obs.category):
                return candidate
        return None

    def _analyze_conflict_with_gemini(
        self,
        obs1: Observation,
        obs2: Observation,
        discrepancy: int
    ) -> ConflictAnalysis:
        """Use Gemini to analyze conflict between observations."""
        
        prompt = self.CONFLICT_ANALYSIS_PROMPT.format(
            doc1_type=obs1.document_type.value,
            obs1_description=obs1.description[:200],
            obs1_location=obs1.area,
            obs1_category=obs1.category.value,
            obs1_severity=obs1.severity.value,
            doc2_type=obs2.document_type.value,
            obs2_description=obs2.description[:200],
            obs2_location=obs2.area,
            obs2_category=obs2.category.value,
            obs2_severity=obs2.severity.value,
            doc_choice=obs1.document_type.value
        )
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = {}
            
            # Map resolved severity
            sev_str = analysis_data.get("recommended_severity", "MEDIUM").upper()
            try:
                resolved_sev = SeverityLevel[sev_str]
            except KeyError:
                resolved_sev = SeverityLevel.MEDIUM
            
            conflict = ConflictAnalysis(
                conflict_id=f"CONF_{obs1.observation_id}_{obs2.observation_id}",
                severity_discrepancy=f"{obs1.severity.value} vs {obs2.severity.value}",
                likely_cause=analysis_data.get("likely_cause", "Assessment differences"),
                recommendation=analysis_data.get("explanation", "Merged assessment"),
                confidence=float(analysis_data.get("confidence_in_resolution", 0.5)),
                resolved_severity=resolved_sev
            )
            
            logger.info(f"Analyzed conflict: {conflict.severity_discrepancy} -> {conflict.resolved_severity.value}")
            return conflict
            
        except Exception as e:
            logger.error(f"Gemini conflict analysis failed: {e}")
            # Fallback: use higher severity
            higher_sev = obs1.severity if severity_order.get(obs1.severity, 5) < severity_order.get(obs2.severity, 5) else obs2.severity
            
            return ConflictAnalysis(
                conflict_id=f"CONF_{obs1.observation_id}_{obs2.observation_id}",
                severity_discrepancy=f"{obs1.severity.value} vs {obs2.severity.value}",
                likely_cause="Multiple sources provided different assessments",
                recommendation="Used higher severity as conservative estimate",
                confidence=0.5,
                resolved_severity=higher_sev
            )

    def _merge_observations(
        self,
        obs1: Observation,
        obs2: Observation,
        resolved_severity: Optional[SeverityLevel] = None
    ) -> Observation:
        """Merge two observations into one."""
        # Average confidence
        avg_confidence = (obs1.confidence + obs2.confidence) / 2
        
        # Combine descriptions
        combined_desc = f"{obs1.description} [Also reported: {obs2.description}]"
        
        # Combine image references
        combined_images = list(set(obs1.image_references + obs2.image_references))
        
        # Use resolved severity or higher severity
        if resolved_severity is None:
            severity_order = {
                SeverityLevel.CRITICAL: 1,
                SeverityLevel.HIGH: 2,
                SeverityLevel.MEDIUM: 3,
                SeverityLevel.LOW: 4,
                SeverityLevel.NOT_AVAILABLE: 5
            }
            sev1_rank = severity_order.get(obs1.severity, 5)
            sev2_rank = severity_order.get(obs2.severity, 5)
            final_severity = obs1.severity if sev1_rank < sev2_rank else obs2.severity
        else:
            final_severity = resolved_severity
        
        # Create merged observation
        merged = Observation(
            observation_id=obs1.observation_id,  # Keep first ID
            document_type=obs1.document_type,
            area=obs1.area,
            category=obs1.category,
            description=combined_desc,
            severity=final_severity,
            confidence=avg_confidence,
            image_references=combined_images,
            raw_data={
                "merged_from": [obs1.observation_id, obs2.observation_id],
                "original_obs1": asdict(obs1),
                "original_obs2": asdict(obs2)
            }
        )
        
        return merged

    def create_conflict_records(
        self,
        analyses: List[ConflictAnalysis]
    ) -> List[ConflictRecord]:
        """Convert conflict analyses into ConflictRecord objects."""
        records = []
        
        for analysis in analyses:
            record = ConflictRecord(
                conflict_id=analysis.conflict_id,
                severity_discrepancy=analysis.severity_discrepancy,
                source_documents=[],  # Would be populated from obs1, obs2
                likely_cause=analysis.likely_cause,
                recommendation=analysis.recommendation,
                confidence_in_resolution=analysis.confidence
            )
            records.append(record)
        
        return records

    def batch_detect_conflicts(
        self,
        observation_sets: List[List[Observation]]
    ) -> Tuple[List[ConflictAnalysis], List[Observation]]:
        """
        Detect conflicts across multiple observation sets.
        Iteratively merges each set with the previous merged result.
        """
        if not observation_sets:
            return [], []
        
        all_conflicts = []
        merged = list(observation_sets[0])
        
        for obs_set in observation_sets[1:]:
            conflicts, merged = self.detect_conflicts(merged, obs_set)
            all_conflicts.extend(conflicts)
        
        return all_conflicts, merged
