"""
Gemini-enhanced conflict detection and analysis.
Safely loads API key from environment variables.
"""

import os
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class ConflictAnalysis:
    """Analysis of conflicts between observations."""
    has_conflict: bool
    severity_mismatch: bool
    confidence_mismatch: bool
    reasoning: str
    recommendation: str


class GeminiConflictDetector:
    """Detect and analyze conflicts between observations using Gemini."""
    
    def __init__(self):
        """Initialize with API key from environment variables."""
        load_dotenv(Path(__file__).parent.parent / ".env")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please create a .env file with your API key."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def analyze_conflict(
        self,
        area: str,
        category: str,
        obs1: Dict[str, Any],
        obs2: Dict[str, Any]
    ) -> ConflictAnalysis:
        """
        Analyze if two observations create a conflict.
        
        Args:
            area: Property area (e.g., "Terrace")
            category: Issue category (e.g., "Structural")
            obs1: First observation (e.g., from inspection)
            obs2: Second observation (e.g., from thermal)
            
        Returns:
            ConflictAnalysis with reasoning
        """
        prompt = f"""Analyze if these two observations of the same area/category conflict:

Area: {area}
Category: {category}

Observation 1 (Inspection):
- Description: {obs1.get('description', 'N/A')}
- Severity: {obs1.get('severity', 'Unknown')}
- Confidence: {obs1.get('confidence', 0)}

Observation 2 (Thermal):
- Description: {obs2.get('description', 'N/A')}
- Severity: {obs2.get('severity', 'Unknown')}
- Confidence: {obs2.get('confidence', 0)}

Determine:
1. Is there a conflict? (severity mismatch of 2+ levels = conflict)
2. Are descriptions incompatible?
3. What should be recommended?

Respond as JSON:
{{
  "has_conflict": true/false,
  "severity_mismatch": true/false,
  "confidence_mismatch": true/false,
  "reasoning": "explanation of conflict or consistency",
  "recommendation": "how to handle this"
}}

Return ONLY JSON, no explanation."""
        
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Clean markdown
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0]
            
            data = json.loads(analysis_text.strip())
            return ConflictAnalysis(
                has_conflict=data.get("has_conflict", False),
                severity_mismatch=data.get("severity_mismatch", False),
                confidence_mismatch=data.get("confidence_mismatch", False),
                reasoning=data.get("reasoning", "Unable to determine"),
                recommendation=data.get("recommendation", "Further investigation needed")
            )
        except Exception as e:
            print(f"Conflict analysis error: {e}")
            return ConflictAnalysis(
                has_conflict=False,
                severity_mismatch=False,
                confidence_mismatch=False,
                reasoning=f"Analysis failed: {str(e)}",
                recommendation="Manual review required"
            )
    
    def detect_conflicts_batch(
        self,
        paired_observations: List[Tuple[Dict, Dict]]
    ) -> Dict[str, Any]:
        """
        Detect all conflicts in a batch of paired observations.
        
        Args:
            paired_observations: List of (inspection_obs, thermal_obs) tuples
            
        Returns:
            Dictionary with conflict summary and details
        """
        conflicts = []
        consistencies = []
        
        for obs1, obs2 in paired_observations:
            analysis = self.analyze_conflict(
                area=obs1.get("area", "Unknown"),
                category=obs1.get("category", "Unknown"),
                obs1=obs1,
                obs2=obs2
            )
            
            if analysis.has_conflict:
                conflicts.append({
                    "area": obs1.get("area"),
                    "category": obs1.get("category"),
                    "conflict_type": "severity_mismatch" if analysis.severity_mismatch else "description_mismatch",
                    "reasoning": analysis.reasoning,
                    "recommendation": analysis.recommendation
                })
            else:
                consistencies.append({
                    "area": obs1.get("area"),
                    "category": obs1.get("category"),
                    "reasoning": analysis.reasoning
                })
        
        return {
            "total_pairs": len(paired_observations),
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "consistent_pairs": len(consistencies),
            "summary": f"Found {len(conflicts)} conflicts in {len(paired_observations)} observations"
        }
    
    def suggest_root_causes(
        self,
        area: str,
        category: str,
        observations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use Gemini to suggest root causes from multiple observations.
        
        Args:
            area: Property area
            category: Issue category
            observations: List of related observations
            
        Returns:
            Root cause analysis with confidence
        """
        obs_text = "\n".join([
            f"- {obs.get('description')} (Severity: {obs.get('severity')}, "
            f"Source: {obs.get('source_document', 'Unknown')})"
            for obs in observations
        ])
        
        prompt = f"""Based on these observations, determine the likely root cause:

Area: {area}
Category: {category}

Observations:
{obs_text}

Provide:
1. Most likely root cause
2. Contributing factors
3. Confidence level (0-1)
4. Evidence from observations

Return as JSON:
{{
  "root_cause": "primary cause",
  "contributing_factors": ["factor1", "factor2"],
  "confidence": 0.X,
  "evidence_summary": "brief evidence summary"
}}

Return ONLY JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            cause_text = response.text
            
            if "```json" in cause_text:
                cause_text = cause_text.split("```json")[1].split("```")[0]
            elif "```" in cause_text:
                cause_text = cause_text.split("```")[1].split("```")[0]
            
            return json.loads(cause_text.strip())
        except Exception as e:
            return {
                "root_cause": "Unable to determine - requires further investigation",
                "contributing_factors": [],
                "confidence": 0.0,
                "evidence_summary": f"Analysis failed: {str(e)}"
            }
