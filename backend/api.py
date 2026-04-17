"""
FastAPI Backend for AI DDR Generator
High-performance REST API for property inspection report generation
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import shutil
import os
import tempfile
from pathlib import Path
from datetime import datetime
import json
import sys

# Add backend to path
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

# Import utilities from existing codebase
try:
    from utils.pdf_extractor import extract_text_by_page, PDFExtractor
    from utils.observation_extractor import extract_observations
    from utils.merger import merge_observations, detect_conflicts
    from utils.severity import calculate_severity
    from utils.ddr_generator import generate_ddr_report
except ImportError as e:
    print(f"Warning: Could not import all utilities: {e}")

# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="AI DDR Generator API",
    description="REST API for generating Detailed Diagnostic Reports from property inspection documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS for frontend - Allow all origins (for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory
os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# ============================================================================
# Data Models (Pydantic)
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


class GenerationResponse(BaseModel):
    """Response from DDR generation"""
    success: bool
    document_id: str
    total_observations: int
    merged_observations: int
    conflicts_found: int
    timestamp: str
    report: Optional[Dict[str, Any]] = None
    observations: Optional[List[Dict[str, Any]]] = None
    conflicts: Optional[List[Dict[str, Any]]] = None


class StatusResponse(BaseModel):
    """Status response"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


# ============================================================================
# API Routes
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "AI DDR Generator API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "generate": "/api/v1/generate-ddr"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/generate-ddr", response_model=GenerationResponse, tags=["DDR Generation"])
async def generate_ddr(
    inspection: UploadFile = File(..., description="Inspection report PDF"),
    thermal: UploadFile = File(..., description="Thermal imaging report PDF"),
):
    """
    Generate Detailed Diagnostic Report (DDR) from inspection documents.
    
    This endpoint:
    1. Accepts inspection and thermal PDF files
    2. Extracts text from both documents
    3. Extracts observations from extracted text
    4. Merges observations from both documents
    5. Detects conflicts between observations
    6. Calculates severity levels
    7. Generates comprehensive DDR report
    
    Args:
        inspection: Inspection report PDF file
        thermal: Thermal imaging report PDF file
    
    Returns:
        GenerationResponse with full analysis and report
    
    Raises:
        HTTPException: If file processing fails
    """
    
    # ★★★ STEP 5: FILE OBJECT DEBUG ★★★
    print(f"\n[DEBUG] Files received:")
    print(f"  Inspection filename: {inspection.filename}")
    print(f"  Inspection content_type: {inspection.content_type}")
    print(f"  Thermal filename: {thermal.filename}")
    print(f"  Thermal content_type: {thermal.content_type}")
    
    document_id = f"ddr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create temporary storage
        temp_dir = tempfile.mkdtemp()
        inspection_path = os.path.join(temp_dir, "inspection.pdf")
        thermal_path = os.path.join(temp_dir, "thermal.pdf")
        
        # Save uploaded files
        try:
            with open(inspection_path, "wb") as f:
                content = await inspection.read()
                print(f"[DEBUG] Inspection file size: {len(content)} bytes")
                f.write(content)
            
            with open(thermal_path, "wb") as f:
                content = await thermal.read()
                print(f"[DEBUG] Thermal file size: {len(content)} bytes")
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to save files: {str(e)}")
        
        # ====================================================================
        # STEP 1: Extract Text from PDFs
        # ====================================================================
        try:
            inspection_pages = extract_text_by_page(inspection_path)
            thermal_pages = extract_text_by_page(thermal_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")
        
        # ====================================================================
        # STEP 2: Extract Observations from Text
        # ====================================================================
        inspection_obs = []
        for idx, page in enumerate(inspection_pages):
            try:
                obs = extract_observations(page.get("text", ""))
                # Improved list check
                if isinstance(obs, list) and len(obs) > 0:
                    # Add metadata
                    for o in obs:
                        if isinstance(o, dict):
                            o["source"] = "inspection"
                            o["page"] = page.get("page", idx + 1)
                    inspection_obs.extend(obs)
            except Exception as e:
                print(f"Warning: Error extracting observations from inspection page {idx}: {e}")
        
        thermal_obs = []
        for idx, page in enumerate(thermal_pages):
            try:
                obs = extract_observations(page.get("text", ""))
                # Improved list check
                if isinstance(obs, list) and len(obs) > 0:
                    # Add metadata
                    for o in obs:
                        if isinstance(o, dict):
                            o["source"] = "thermal"
                            o["page"] = page.get("page", idx + 1)
                    thermal_obs.extend(obs)
            except Exception as e:
                print(f"Warning: Error extracting observations from thermal page {idx}: {e}")
        
        # DEBUG: Print all observations
        print(f"\n[DEBUG] INSPECTION OBS ({len(inspection_obs)} observations):")
        print(inspection_obs)
        print(f"\n[DEBUG] THERMAL OBS ({len(thermal_obs)} observations):")
        print(thermal_obs)
        
        total_observations = len(inspection_obs) + len(thermal_obs)
        
        # ====================================================================
        # STEP 3: Merge Observations
        # ====================================================================
        try:
            merged = merge_observations(inspection_obs, thermal_obs)
        except Exception as e:
            merged = inspection_obs + thermal_obs  # Fallback to simple concat
            print(f"Warning: Merge failed, using concatenation: {e}")
        
        # ====================================================================
        # STEP 4: Calculate Severity
        # ====================================================================
        for item in merged:
            try:
                item["severity"] = calculate_severity(item)
            except Exception as e:
                item["severity"] = "UNKNOWN"
                print(f"Warning: Severity calculation failed: {e}")
        
        # ====================================================================
        # STEP 5: Detect Conflicts
        # ====================================================================
        try:
            conflicts = detect_conflicts(merged)
        except Exception as e:
            conflicts = []
            print(f"Warning: Conflict detection failed: {e}")
        
        # ====================================================================
        # STEP 6: Generate DDR Report
        # ====================================================================
        try:
            report = generate_ddr_report(merged, conflicts)
        except Exception as e:
            report = {
                "error": str(e),
                "observations_count": len(merged),
                "conflicts_count": len(conflicts)
            }
        
        # ====================================================================
        # Save Report to Output
        # ====================================================================
        output_path = os.path.join("outputs", f"{document_id}_report.json")
        try:
            with open(output_path, "w") as f:
                json.dump({
                    "document_id": document_id,
                    "timestamp": datetime.now().isoformat(),
                    "report": report,
                    "observations": merged,
                    "conflicts": conflicts,
                    "summary": {
                        "total_observations": total_observations,
                        "merged_observations": len(merged),
                        "conflicts_found": len(conflicts),
                        "severity_distribution": {
                            item.get("severity", "UNKNOWN"): sum(1 for m in merged if m.get("severity") == item.get("severity"))
                            for item in merged
                        }
                    }
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save report: {e}")
        
        # Clean up temp files
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # ====================================================================
        # Return Response
        # ====================================================================
        return {
            "success": True,
            "document_id": document_id,
            "total_observations": total_observations,
            "merged_observations": len(merged),
            "conflicts_found": len(conflicts),
            "timestamp": datetime.now().isoformat(),
            "report": report,
            "observations": merged,
            "conflicts": conflicts
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DDR generation failed: {str(e)}"
        )


@app.get("/api/v1/reports/{document_id}", tags=["Reports"])
async def get_report(document_id: str):
    """
    Retrieve a previously generated report.
    
    Args:
        document_id: The document ID returned from generation
    
    Returns:
        Full report data or 404 if not found
    """
    report_path = os.path.join("outputs", f"{document_id}_report.json")
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Report {document_id} not found")
    
    try:
        with open(report_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read report: {str(e)}")


@app.get("/api/v1/reports", tags=["Reports"])
async def list_reports():
    """List all generated reports"""
    reports = []
    output_dir = "outputs"
    
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith("_report.json"):
                reports.append({
                    "filename": file,
                    "document_id": file.replace("_report.json", ""),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(output_dir, file))
                    ).isoformat()
                })
    
    return {
        "total": len(reports),
        "reports": sorted(reports, key=lambda x: x["modified"], reverse=True)
    }


@app.get("/api/v1/status/{document_id}", tags=["Status"])
async def get_status(document_id: str):
    """Get status of a document"""
    report_path = os.path.join("outputs", f"{document_id}_report.json")
    
    if os.path.exists(report_path):
        return {
            "document_id": document_id,
            "status": "completed",
            "available": True
        }
    else:
        return {
            "document_id": document_id,
            "status": "not_found",
            "available": False
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
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat()
        },
    )


# ============================================================================
# Main - Development Server
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
