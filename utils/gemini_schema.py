"""
Gemini-based schema extraction module.
Extracts structured information from unstructured PDF text using Gemini vision.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai


logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Types of schemas to extract."""
    INSPECTION_SCHEMA = "inspection"
    THERMAL_SCHEMA = "thermal"
    MOISTURE_SCHEMA = "moisture"
    GENERIC_SCHEMA = "generic"


@dataclass
class SchemaField:
    """Represents a field in the extracted schema."""
    name: str
    value: Any
    confidence: float  # 0-1 confidence score
    source_text: Optional[str] = None


class GeminiSchemaExtractor:
    """
    Uses Gemini API to extract structured schema from PDF text and images.
    Handles document type detection and schema-specific extraction.
    """

    # Predefined schema prompts for different document types
    SCHEMA_PROMPTS = {
        SchemaType.INSPECTION_SCHEMA: """
You are a building inspection expert. Extract the following structured information from the inspection report text:

1. Property Details:
   - Property address
   - Inspector name
   - Inspection date
   - Property type (residential/commercial)

2. Identified Issues (list each):
   - Location (area of building)
   - Category (structural/electrical/plumbing/roofing/etc)
   - Severity (CRITICAL/HIGH/MEDIUM/LOW)
   - Description of issue
   - Recommended action

3. Photos/Images:
   - Count of photos
   - Areas covered

4. Overall Property Condition:
   - General assessment
   - Urgency level

Return as JSON with exact keys. Be precise. If information is missing, use null.
""",

        SchemaType.THERMAL_SCHEMA: """
You are a thermal imaging expert. Extract the following structured information from the thermal report text:

1. Document Metadata:
   - Report date
   - Equipment used
   - Locations scanned
   - Weather conditions

2. Thermal Anomalies (list each):
   - Location (area of building)
   - Temperature differential (°C or °F)
   - Severity (CRITICAL/HIGH/MEDIUM/LOW based on delta)
   - Likely cause (insulation/airflow/thermal bridge/etc)
   - Affected area size

3. Recommendations:
   - Priority actions
   - Estimated remediation cost if mentioned

4. Overall Assessment:
   - Building envelope integrity
   - Risk level

Return as JSON with exact keys. If information is missing, use null.
""",

        SchemaType.MOISTURE_SCHEMA: """
You are a moisture/mold inspection expert. Extract the following structured information:

1. Moisture Reading Locations:
   - Location
   - Moisture content (%)
   - Status (CRITICAL/HIGH/MEDIUM/LOW)
   - Surface type

2. Mold/Fungal Growth:
   - Location
   - Type (if identifiable)
   - Extent
   - Health risk level

3. Water Damage History:
   - Location
   - Age of damage
   - Source of moisture
   - Current status

4. Remediation Recommendations:
   - Priority
   - Estimated timeline

Return as JSON with exact keys. If unknown, use null.
""",

        SchemaType.GENERIC_SCHEMA: """
Extract the following structured information from the provided text:

1. Document Type: What type of report is this?
2. Date: When was this report created?
3. Main Findings: List key observations (5-10 items)
4. Severity: Overall severity (CRITICAL/HIGH/MEDIUM/LOW)
5. Locations/Areas: Geographic areas covered
6. Recommendations: Key action items

Return as JSON. If information is missing, use null.
"""
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini schema extractor.
        
        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
        """
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Will use GOOGLE_API_KEY environment variable
            try:
                genai.configure()
            except Exception as e:
                logger.warning(f"Gemini not configured: {e}. Schema extraction will fail.")
        
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def extract_schema(
        self,
        text: str,
        schema_type: Optional[SchemaType] = None,
        images: Optional[List[bytes]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured schema from text and images using Gemini.
        
        Args:
            text: Extracted PDF text
            schema_type: Type of schema to extract
            images: Optional list of image bytes
            context: Optional additional context/instructions
            
        Returns:
            Dictionary with extracted schema
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to schema extraction")
            return {}
        
        # Auto-detect schema type if not provided
        if schema_type is None:
            schema_type = self._detect_schema_type(text)
        
        # Get the appropriate prompt
        base_prompt = self.SCHEMA_PROMPTS.get(schema_type, self.SCHEMA_PROMPTS[SchemaType.GENERIC_SCHEMA])
        
        # Add context if provided
        if context:
            base_prompt += f"\n\nAdditional context: {context}"
        
        # Build the full prompt
        full_prompt = f"""{base_prompt}

---DOCUMENT TEXT---
{text[:3000]}  # Limit to 3000 chars to avoid token overload
---END TEXT---

Extract and return ONLY valid JSON, no markdown, no explanations."""
        
        try:
            # Prepare content parts (text + images)
            content_parts = [full_prompt]
            
            if images:
                logger.info(f"Including {len(images)} images in schema extraction")
                for idx, img_bytes in enumerate(images[:3]):  # Limit to 3 images
                    content_parts.append({
                        "mime_type": "image/png",
                        "data": img_bytes
                    })
            
            # Call Gemini API
            response = self.model.generate_content(content_parts)
            response_text = response.text
            
            # Parse JSON response
            schema = self._parse_json_response(response_text)
            
            # Add metadata
            schema["_extraction_metadata"] = {
                "schema_type": schema_type.value,
                "confidence_overall": self._calculate_confidence(schema),
                "images_processed": len(images) if images else 0,
                "text_length": len(text)
            }
            
            logger.info(f"Schema extraction successful ({schema_type.value})")
            return schema
            
        except Exception as e:
            logger.error(f"Failed to extract schema: {e}")
            return {"_error": str(e), "schema_type": schema_type.value}

    def _detect_schema_type(self, text: str) -> SchemaType:
        """Auto-detect document type from text content."""
        text_lower = text.lower()
        
        if "thermal" in text_lower or "temperature" in text_lower or "infrared" in text_lower:
            return SchemaType.THERMAL_SCHEMA
        elif "moisture" in text_lower or "mold" in text_lower or "humidity" in text_lower:
            return SchemaType.MOISTURE_SCHEMA
        elif "inspection" in text_lower or "property" in text_lower:
            return SchemaType.INSPECTION_SCHEMA
        else:
            return SchemaType.GENERIC_SCHEMA

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response, handling markdown code blocks."""
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON object from response
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            
            logger.warning(f"Failed to parse JSON response: {response_text[:200]}")
            return {"_raw_response": response_text[:500]}

    def _calculate_confidence(self, schema: Dict[str, Any]) -> float:
        """Calculate overall extraction confidence (0-1)."""
        if not schema:
            return 0.0
        
        # Count non-null fields
        total_fields = 0
        filled_fields = 0
        
        def count_fields(obj):
            nonlocal total_fields, filled_fields
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if not k.startswith("_"):
                        total_fields += 1
                        if v is not None and v != "":
                            filled_fields += 1
                        if isinstance(v, (dict, list)):
                            count_fields(v)
            elif isinstance(obj, list):
                for item in obj:
                    count_fields(item)
        
        count_fields(schema)
        
        if total_fields == 0:
            return 0.0
        
        return min(1.0, filled_fields / total_fields)

    def extract_multiple_schemas(
        self,
        documents: List[dict],
        schema_types: Optional[List[SchemaType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract schemas from multiple documents.
        
        Args:
            documents: List of {text, images} dicts
            schema_types: Optional list of schema types per document
            
        Returns:
            List of extracted schemas
        """
        schemas = []
        
        for idx, doc in enumerate(documents):
            schema_type = schema_types[idx] if schema_types and idx < len(schema_types) else None
            schema = self.extract_schema(
                text=doc.get("text", ""),
                schema_type=schema_type,
                images=doc.get("images"),
                context=doc.get("context")
            )
            schemas.append(schema)
        
        return schemas

    def validate_schema(self, schema: Dict[str, Any], required_fields: Optional[List[str]] = None) -> bool:
        """Validate extracted schema has required fields."""
        if not schema or "_error" in schema:
            return False
        
        if required_fields:
            for field in required_fields:
                if field not in schema or schema[field] is None:
                    return False
        
        return True
