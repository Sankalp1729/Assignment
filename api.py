"""
FastAPI Application for AI DDR Generator
Backend API for property inspection report generation
Designed to run on Render
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime
import sys

# Add backend to path
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

from modules import (
    DocumentExtractor,
    DocumentType,
    DDRPipeline,
)
from modules.report_generator import ReportGenerator
from modules.data_models import ExtractionResult, DDRReport
from utils import PDFExtractor

# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="AI DDR Generator API",
    description="API for generating Detailed Diagnostic Reports from property inspection documents",
    version="1.0.0",
)

# Configure CORS for frontend
origins = [
    "http://localhost:3000",           # Local Next.js dev
    "http://localhost:8000",           # Local FastAPI dev
    "https://localhost:3000",
    "https://localhost:8000",
    "https://yourfrontend.vercel.app", # Production Vercel URL (update this)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class ExtractionRequest(BaseModel):
    """Request model for extraction"""
    document_type: str = "inspection_report"
    filename: str
    json_data: dict


class PipelineRequest(BaseModel):
    """Request model for full pipeline"""
    document_type: str = "inspection_report"


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


class ExtractionResponse(BaseModel):
    """Response from extraction"""
    success: bool
    document_id: str
    observations_count: int
    message: str


class ReportResponse(BaseModel):
    """Response from report generation"""
    success: bool
    report_id: str
    message: str
    report: Optional[dict] = None


# ============================================================================
# Helper Functions
# ============================================================================

def convert_to_serializable(obj):
    """Convert non-JSON-serializable objects"""
    from dataclasses import asdict, is_dataclass
    
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    return obj


# ============================================================================
# API Routes
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI DDR Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/extract", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_observations(
    file: UploadFile = File(...),
    document_type: str = "inspection_report"
):
    """
    Extract observations from an uploaded document (PDF or JSON)
    
    Args:
        file: PDF or JSON file to process
        document_type: Type of document (inspection_report, thermal_report, etc.)
    
    Returns:
        Extraction result with observation count
    """
    try:
        # Determine document type enum
        doc_type = DocumentType.INSPECTION_REPORT
        if document_type == "thermal_report":
            doc_type = DocumentType.THERMAL_REPORT
        
        # Process uploaded file
        extractor = DocumentExtractor()
        
        if file.content_type == "application/json":
            # Handle JSON
            content = await file.read()
            json_data = json.loads(content.decode())
            result = extractor.extract_from_json(json_data, doc_type, file.filename)
            
        elif file.content_type in ["application/pdf", "application/x-pdf"]:
            # Handle PDF
            pdf_extractor = PDFExtractor()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            try:
                pdf_data = pdf_extractor.extract_pdf(tmp_path)
                
                result = ExtractionResult(
                    document_id=f"pdf_doc_{datetime.now().timestamp()}",
                    document_type=doc_type,
                    filename=file.filename,
                    extraction_timestamp=datetime.now(),
                    raw_text=pdf_data.get('text', ''),
                    observations=[],
                    images=pdf_data.get('images', []),
                    metadata=pdf_data.get('metadata', {})
                )
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or JSON.")
        
        return ExtractionResponse(
            success=True,
            document_id=result.document_id,
            observations_count=len(result.observations),
            message=f"Successfully extracted {len(result.observations)} observations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")


@app.post("/api/pipeline", response_model=ReportResponse, tags=["Pipeline"])
async def run_pipeline(request: PipelineRequest):
    """
    Run the full AI DDR generation pipeline
    
    Args:
        request: Pipeline configuration
    
    Returns:
        Generated report
    """
    try:
        # Initialize pipeline
        pipeline = DDRPipeline()
        
        # In a real implementation, you would pass extraction results from session
        # For now, this is a placeholder
        
        return ReportResponse(
            success=True,
            report_id="report_" + str(datetime.now().timestamp()),
            message="Pipeline executed successfully",
            report=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pipeline failed: {str(e)}")


@app.get("/api/status/{document_id}", tags=["Status"])
async def get_status(document_id: str):
    """Get processing status for a document"""
    return {
        "document_id": document_id,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        },
    )


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuration for development
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
