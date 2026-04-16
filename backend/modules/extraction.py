"""Document extraction module - Extract text, images, and metadata from PDFs"""

import json
from typing import List, Dict, Any
from datetime import datetime
from .data_models import (
    ExtractionResult,
    Observation,
    DocumentType,
    ImageReference,
    SeverityLevel,
)


class DocumentExtractor:
    """Extracts observations and metadata from documents"""

    def __init__(self):
        pass

    def extract_from_pdf(
        self, filename: str, document_type: DocumentType
    ) -> ExtractionResult:
        """
        Extract observations, images, and metadata from a PDF.
        
        In production, this would use:
        - PyPDF2 or pdfplumber for text extraction
        - Tesseract OCR for image text
        - LLM for semantic understanding
        
        For now, we'll use a structured format.
        """
        # This is a stub - in production would process actual PDF
        result = ExtractionResult(
            document_id=f"doc_{datetime.now().timestamp()}",
            document_type=document_type,
            filename=filename,
            extraction_timestamp=datetime.now(),
            observations=[],
            images=[],
            metadata={},
            raw_text="",
        )
        return result

    def extract_from_json(
        self, data: Dict[str, Any], document_type: DocumentType, source_filename: str
    ) -> ExtractionResult:
        """
        Extract observations from structured JSON data.
        This is useful for testing and when data is already pre-processed.
        
        Expected JSON structure:
        {
            "metadata": {...},
            "observations": [
                {
                    "area": "Terrace",
                    "category": "Structural",
                    "description": "...",
                    "severity": "HIGH",
                    "page": 1,
                    "images": ["image_id_1"]
                }
            ],
            "images": [
                {
                    "id": "image_id_1",
                    "filename": "thermal_1.png",
                    "page": 1,
                    "description": "..."
                }
            ]
        }
        """
        document_id = f"doc_{datetime.now().timestamp()}"

        # Extract metadata
        metadata = data.get("metadata", {})

        # Extract observations
        observations = []
        for idx, obs_data in enumerate(data.get("observations", [])):
            severity_str = obs_data.get("severity", "NOT_AVAILABLE").upper()
            severity = (
                SeverityLevel[severity_str]
                if severity_str in SeverityLevel.__members__
                else SeverityLevel.NOT_AVAILABLE
            )

            observation = Observation(
                observation_id=f"{document_id}_obs_{idx}",
                document_type=document_type,
                area=obs_data.get("area", "Not Specified"),
                category=obs_data.get("category", "Other"),
                description=obs_data.get("description", ""),
                severity=severity,
                confidence=obs_data.get("confidence", 0.0),
                image_references=obs_data.get("images", []),
                raw_text=obs_data.get("raw_text", ""),
                source_page=obs_data.get("page", 0),
            )
            observations.append(observation)

        # Extract images
        images = []
        for img_data in data.get("images", []):
            image = ImageReference(
                image_id=img_data.get("id", ""),
                filename=img_data.get("filename", ""),
                source_document=source_filename,
                page_number=img_data.get("page", 0),
                description=img_data.get("description", ""),
                related_observations=img_data.get("related_observations", []),
            )
            images.append(image)

        result = ExtractionResult(
            document_id=document_id,
            document_type=document_type,
            filename=source_filename,
            extraction_timestamp=datetime.now(),
            observations=observations,
            images=images,
            metadata=metadata,
            raw_text=data.get("raw_text", ""),
        )

        return result

    def validate_extraction(self, result: ExtractionResult) -> Dict[str, Any]:
        """
        Validate extraction result for quality and completeness.
        
        Checks:
        - Required fields present
        - No empty observations
        - Image references valid
        """
        validation_report = {
            "valid": True,
            "warnings": [],
            "errors": [],
        }

        # Check observations
        if not result.observations:
            validation_report["warnings"].append(
                f"No observations extracted from {result.filename}"
            )

        # Check for missing required fields
        for obs in result.observations:
            if not obs.description:
                validation_report["errors"].append(
                    f"Observation {obs.observation_id} has empty description"
                )
            if obs.area == "Not Specified":
                validation_report["warnings"].append(
                    f"Observation {obs.observation_id} has unspecified area"
                )

        # Check image references
        image_ids = {img.image_id for img in result.images}
        for obs in result.observations:
            for img_ref in obs.image_references:
                if img_ref not in image_ids:
                    validation_report["warnings"].append(
                        f"Observation {obs.observation_id} references missing image {img_ref}"
                    )

        validation_report["valid"] = len(validation_report["errors"]) == 0

        return validation_report
