"""
Gemini-based schema extraction from PDF text.
Safely loads API key from environment variables.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv


class GeminiSchemaExtractor:
    """Extract structured schema from unstructured PDF text using Gemini."""
    
    def __init__(self):
        """Initialize with API key from environment variables."""
        # Load environment variables from .env file
        load_dotenv(Path(__file__).parent.parent / ".env")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please create a .env file with your API key. "
                "See .env.example for the format."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def extract_schema(self, text: str) -> Dict[str, Any]:
        """
        Extract schema structure from inspection report text.
        
        Args:
            text: Raw text from PDF extraction
            
        Returns:
            Dictionary with identified areas, categories, patterns
        """
        prompt = """Analyze this property inspection report and extract:
1. Physical areas mentioned (e.g., Terrace, South Wall, Foundation, Roof, etc.)
2. Issue categories (e.g., Structural, Thermal, Moisture, Electrical, etc.)
3. Severity indicators (e.g., "critical", "urgent", "high priority")
4. Measurement units mentioned (e.g., mm, °C, RH%)

Return as JSON with keys: areas, categories, severity_indicators, units

Report text:
{text}

Return ONLY valid JSON, no markdown or explanation."""
        
        try:
            response = self.model.generate_content(prompt)
            schema_text = response.text
            
            # Clean markdown if present
            if "```json" in schema_text:
                schema_text = schema_text.split("```json")[1].split("```")[0]
            elif "```" in schema_text:
                schema_text = schema_text.split("```")[1].split("```")[0]
            
            return json.loads(schema_text.strip())
        except json.JSONDecodeError:
            # Fallback schema if parsing fails
            return {
                "areas": ["Terrace", "South Wall", "East Wall", "West Wall", "Foundation", "Roof"],
                "categories": ["Structural", "Thermal", "Moisture", "Electrical", "Plumbing"],
                "severity_indicators": ["Critical", "High", "Medium", "Low"],
                "units": ["mm", "°C", "RH%", "W/m²"]
            }
    
    def extract_observations_structure(self, text: str, schema: Dict) -> Dict[str, Any]:
        """
        Extract observations that match the identified schema.
        
        Args:
            text: Raw PDF text
            schema: Extracted schema structure
            
        Returns:
            Structured observations matching schema
        """
        areas_str = ", ".join(schema.get("areas", []))
        categories_str = ", ".join(schema.get("categories", []))
        
        prompt = f"""From this inspection report, extract all observations that match:
Areas: {areas_str}
Categories: {categories_str}

For each observation, structure as JSON with:
- area: specific area (must be from above)
- category: issue category (must be from above)
- description: what was observed
- severity: estimated severity (Critical/High/Medium/Low)
- confidence: confidence score (0-1)

Return as JSON array of observations only, no markdown.

Report text:
{text}"""
        
        try:
            response = self.model.generate_content(prompt)
            obs_text = response.text
            
            # Clean markdown
            if "```json" in obs_text:
                obs_text = obs_text.split("```json")[1].split("```")[0]
            elif "```" in obs_text:
                obs_text = obs_text.split("```")[1].split("```")[0]
            
            return {"observations": json.loads(obs_text.strip())}
        except (json.JSONDecodeError, Exception):
            return {"observations": []}
