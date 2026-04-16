"""
Gemini-based structured observation extraction.
Safely loads API key from environment variables.
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class ExtractedObservation:
    """Structured observation from Gemini extraction."""
    area: str
    category: str
    description: str
    severity: str
    confidence: float
    source_document: str


class GeminiObservationExtractor:
    """Extract and structure observations from inspection text using Gemini."""
    
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
    
    def extract_observations(
        self, 
        text: str, 
        doc_type: str,
        schema: Dict[str, Any]
    ) -> List[ExtractedObservation]:
        """
        Extract structured observations from inspection text.
        
        Args:
            text: Raw text from PDF
            doc_type: "inspection" or "thermal"
            schema: Extracted schema with valid areas/categories
            
        Returns:
            List of ExtractedObservation objects
        """
        doc_description = "inspection report" if doc_type == "inspection" else "thermal analysis"
        areas_str = ", ".join(schema.get("areas", []))
        categories_str = ", ".join(schema.get("categories", []))
        
        prompt = f"""Extract all observations from this {doc_description}.

Valid areas: {areas_str}
Valid categories: {categories_str}
Severity levels: Critical, High, Medium, Low

For EACH observation identified, extract:
1. area: which area (must match valid areas exactly)
2. category: type of issue (must match valid categories exactly)
3. description: specific observation found
4. severity: Critical/High/Medium/Low based on urgency
5. confidence: 0.0-1.0 confidence in assessment

Return as JSON array:
[
  {{"area": "...", "category": "...", "description": "...", "severity": "...", "confidence": 0.X}}
]

Return ONLY the JSON array, no markdown or explanation:

{doc_description} text:
{text}"""
        
        try:
            response = self.model.generate_content(prompt)
            obs_text = response.text
            
            # Clean markdown if present
            if "```json" in obs_text:
                obs_text = obs_text.split("```json")[1].split("```")[0]
            elif "```" in obs_text:
                obs_text = obs_text.split("```")[1].split("```")[0]
            
            obs_list = json.loads(obs_text.strip())
            
            # Convert to ExtractedObservation objects
            observations = []
            for obs in obs_list:
                observations.append(ExtractedObservation(
                    area=obs.get("area", "Unknown"),
                    category=obs.get("category", "Unknown"),
                    description=obs.get("description", ""),
                    severity=obs.get("severity", "Low"),
                    confidence=float(obs.get("confidence", 0.5)),
                    source_document=doc_type
                ))
            return observations
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Gemini extraction error: {e}. Returning empty list.")
            return []
    
    def extract_with_context(
        self,
        text: str,
        doc_type: str,
        schema: Dict[str, Any],
        existing_observations: List[ExtractedObservation] = None
    ) -> List[ExtractedObservation]:
        """
        Extract observations with context from other documents.
        
        Args:
            text: Raw text from PDF
            doc_type: "inspection" or "thermal"
            schema: Extracted schema
            existing_observations: Observations from other documents for context
            
        Returns:
            Contextually-aware list of ExtractedObservation objects
        """
        context = ""
        if existing_observations:
            context = "\nObservations from other document for reference:\n"
            for obs in existing_observations[:5]:  # Limit to avoid token overload
                context += f"- {obs.area} ({obs.category}): {obs.description}\n"
        
        prompt = f"""Extract observations from this document, considering context from related documents:
{context}

Use the same area/category structure where applicable for consistency.

Valid areas: {", ".join(schema.get("areas", []))}
Valid categories: {", ".join(schema.get("categories", []))}

Return JSON array only:
[{{"area": "...", "category": "...", "description": "...", "severity": "...", "confidence": 0.X}}]

{text}"""
        
        try:
            response = self.model.generate_content(prompt)
            obs_text = response.text
            
            if "```json" in obs_text:
                obs_text = obs_text.split("```json")[1].split("```")[0]
            elif "```" in obs_text:
                obs_text = obs_text.split("```")[1].split("```")[0]
            
            obs_list = json.loads(obs_text.strip())
            return [
                ExtractedObservation(
                    area=obs.get("area", "Unknown"),
                    category=obs.get("category", "Unknown"),
                    description=obs.get("description", ""),
                    severity=obs.get("severity", "Low"),
                    confidence=float(obs.get("confidence", 0.5)),
                    source_document=doc_type
                )
                for obs in obs_list
            ]
        except Exception as e:
            print(f"Context-aware extraction error: {e}")
            return self.extract_observations(text, doc_type, schema)
