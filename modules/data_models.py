"""Data models and schemas for DDR Generator"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class SeverityLevel(Enum):
    """Severity levels for issues"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NOT_AVAILABLE = "NOT_AVAILABLE"

class DocumentType(Enum):
    """Types of input documents"""
    INSPECTION_REPORT = "inspection_report"
    THERMAL_REPORT = "thermal_report"
    OTHER = "other"

@dataclass
class ImageReference:
    """Reference to an image with metadata"""
    image_id: str
    filename: str
    source_document: str
    page_number: int
    description: str = ""
    related_observations: List[str] = field(default_factory=list)

@dataclass
class Observation:
    """Single observation from a document"""
    observation_id: str
    document_type: DocumentType
    area: str  # e.g., "Terrace", "South Wall"
    category: str  # e.g., "Structural", "Thermal", "Moisture"
    description: str
    severity: SeverityLevel = SeverityLevel.NOT_AVAILABLE
    confidence: float = 0.0  # 0-1 scale
    image_references: List[str] = field(default_factory=list)
    raw_text: str = ""  # Original text from document
    source_page: int = 0

@dataclass
class ConflictRecord:
    """Record of conflicting observations"""
    conflict_id: str
    observations: List[Observation]
    description: str
    resolution_status: str = "UNRESOLVED"  # RESOLVED, UNRESOLVED, FLAGGED
    notes: str = ""

@dataclass
class MissingData:
    """Record of missing information"""
    data_type: str  # e.g., "thermal_readings_west_wall"
    expected_source: str  # e.g., "THERMAL_REPORT"
    reason: str  # e.g., "Page not provided", "Data corrupted"

@dataclass
class ExtractionResult:
    """Result of document extraction"""
    document_id: str
    document_type: DocumentType
    filename: str
    extraction_timestamp: datetime
    observations: List[Observation] = field(default_factory=list)
    images: List[ImageReference] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""

@dataclass
class StructuredData:
    """Structured intermediate data"""
    area_wise_data: Dict[str, List[Observation]]  # { "Terrace": [...], "South Wall": [...] }
    category_wise_data: Dict[str, List[Observation]]  # { "Structural": [...], "Thermal": [...] }
    all_observations: List[Observation]
    all_images: List[ImageReference]
    extraction_results: List[ExtractionResult]

@dataclass
class ReasoningOutput:
    """Output from reasoning module"""
    conflicts: List[ConflictRecord]
    missing_data: List[MissingData]
    root_causes: Dict[str, str]  # { "issue_id": "root_cause_description" }
    cross_doc_insights: List[str]  # Insights from multiple documents

@dataclass
class DDRReport:
    """Final Detailed Diagnostic Report"""
    report_id: str
    generation_date: datetime
    property_summary: Dict[str, Any]
    area_wise_observations: Dict[str, Any]
    root_cause_analysis: List[Dict[str, Any]]
    severity_assessment: Dict[str, Any]
    recommended_actions: List[Dict[str, Any]]
    missing_information: List[MissingData]
    conflicts_noted: List[ConflictRecord]
    image_mappings: Dict[str, List[str]]  # { "observation_id": ["image_ids"] }
    metadata: Dict[str, Any] = field(default_factory=dict)
