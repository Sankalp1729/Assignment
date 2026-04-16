"""
Advanced DDR Generator Pipeline with Gemini Integration.
Securely handles API keys through environment variables.

Pipeline:
1. PDF Extraction (PyMuPDF)
2. Schema Extraction (Gemini)
3. Observation Extraction (Gemini)
4. Conflict Detection (Gemini)
5. Report Generation (Jinja2 HTML)
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables early
load_dotenv(Path(__file__).parent / ".env")

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.pymupdf_extractor import PyMuPDFExtractor
from modules.gemini_schema_extractor import GeminiSchemaExtractor
from modules.gemini_observation_extractor import GeminiObservationExtractor
from modules.gemini_conflict_detector import GeminiConflictDetector
from modules.data_models import DocumentType, Observation, ExtractionResult, SeverityLevel
from modules.extraction import DocumentExtractor
from modules.structuring import DataStructurer
from modules.reasoning import ReasoningEngine
from modules.report_generator import ReportGenerator
from modules.html_generator import HTMLReportGenerator


class AdvancedDDRPipeline:
    """Advanced DDR pipeline with Gemini integration."""
    Coordinates all stages from PDF input to HTML output.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the generator with API keys and components."""
        self.gemini_api_key = gemini_api_key or os.environ.get("GOOGLE_API_KEY")
        
        # Initialize components
        self.pdf_processor = PDFProcessor(output_dir=Path("./images"))
        self.schema_extractor = GeminiSchemaExtractor(api_key=self.gemini_api_key)
        self.obs_extractor = GeminiObservationExtractor(api_key=self.gemini_api_key)
        self.conflict_resolver = GeminiConflictResolver(api_key=self.gemini_api_key)
        self.html_generator = HTMLReportGenerator()
        self.legacy_pipeline = DDRPipeline()  # Fallback pipeline
        self.legacy_report_gen = ReportGenerator()
        
        logger.info("Advanced DDR Generator initialized")

    def process_pdfs(self, pdf_paths: List[str]) -> Dict:
        """
        Process multiple PDFs through the entire pipeline.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            Dictionary with all processing results
        """
        logger.info(f"Processing {len(pdf_paths)} PDF(s)...")
        
        results = {
            "pdfs_extracted": [],
            "schemas_extracted": [],
            "observations_extracted": [],
            "conflicts_detected": [],
            "merged_observations": [],
            "ddr_report": None,
            "html_report_path": None,
            "json_report_path": None,
            "text_report_path": None,
            "processing_timestamp": datetime.now().isoformat()
        }
        
        try:
            # STAGE 1: PDF Extraction
            logger.info("=== STAGE 1: PDF Text & Image Extraction ===")
            pdf_docs = []
            for pdf_path in pdf_paths:
                try:
                    if not Path(pdf_path).exists():
                        logger.warning(f"PDF not found: {pdf_path}")
                        continue
                    
                    pdf_doc = self.pdf_processor.extract_pdf(pdf_path)
                    pdf_docs.append(pdf_doc)
                    results["pdfs_extracted"].append({
                        "filename": pdf_doc.filename,
                        "pages": pdf_doc.total_pages,
                        "images_found": sum(len(p.images) for p in pdf_doc.pages),
                        "document_type": pdf_doc.document_type
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to extract PDF {pdf_path}: {e}")
            
            if not pdf_docs:
                logger.error("No PDFs successfully extracted")
                return results
            
            # STAGE 2: Schema Extraction
            logger.info("=== STAGE 2: Schema Extraction with Gemini ===")
            schemas = []
            documents_data = []
            
            for pdf_doc in pdf_docs:
                # Combine text from all pages
                full_text = "\n".join(page.text for page in pdf_doc.pages)
                
                # Extract images as bytes (simplified for demo)
                images = []  # Would extract actual image bytes
                
                # Extract schema
                schema = self.schema_extractor.extract_schema(
                    text=full_text,
                    schema_type=SchemaType[pdf_doc.document_type.upper().replace("_REPORT", "_SCHEMA")] if pdf_doc.document_type else None,
                    images=images,
                    context=f"Document: {pdf_doc.filename}"
                )
                
                schemas.append(schema)
                documents_data.append({
                    "text": full_text,
                    "images": images,
                    "context": pdf_doc.document_type
                })
                
                results["schemas_extracted"].append({
                    "document": pdf_doc.filename,
                    "schema_confidence": schema.get("_extraction_metadata", {}).get("confidence_overall", 0)
                })
            
            # STAGE 3: Observation Extraction
            logger.info("=== STAGE 3: Structured Observation Extraction ===")
            all_observations = []
            observation_batches = []
            
            for idx, schema in enumerate(schemas):
                pdf_doc = pdf_docs[idx]
                
                # Create extraction context
                context = ExtractionContext(
                    document_type=pdf_doc.document_type,
                    source_filename=pdf_doc.filename,
                    extraction_method="gemini"
                )
                
                # Extract observations
                obs_list, metadata = self.obs_extractor.extract_observations(
                    schema_data=schema,
                    context=context,
                    images=None
                )
                
                observation_batches.append(obs_list)
                all_observations.extend(obs_list)
                
                results["observations_extracted"].append({
                    "document": pdf_doc.filename,
                    "observations_count": len(obs_list),
                    "avg_confidence": metadata.get("avg_confidence", 0),
                    "extraction_errors": len(metadata.get("extraction_errors", []))
                })
                
                logger.info(f"Extracted {len(obs_list)} observations from {pdf_doc.filename}")
            
            # STAGE 4: Conflict Detection & Merging
            logger.info("=== STAGE 4: Conflict Detection & Merging ===")
            if len(observation_batches) > 1:
                conflicts, merged = self.conflict_resolver.batch_detect_conflicts(observation_batches)
                results["conflicts_detected"] = [
                    {
                        "conflict_id": c.conflict_id,
                        "severity_discrepancy": c.severity_discrepancy,
                        "likely_cause": c.likely_cause,
                        "confidence": c.confidence
                    }
                    for c in conflicts
                ]
                results["merged_observations"] = merged
                logger.info(f"Detected {len(conflicts)} conflicts, merged to {len(merged)} observations")
            else:
                results["merged_observations"] = all_observations
                logger.info(f"No conflict detection needed, using {len(all_observations)} observations")
            
            # STAGE 5-6: DDR Report Generation
            logger.info("=== STAGE 5-6: DDR Report Generation ===")
            final_observations = results["merged_observations"]
            
            # Use legacy pipeline for compatibility
            ddr_report = self.legacy_report_gen.generate_ddr_report(final_observations)
            results["ddr_report"] = ddr_report
            
            logger.info(f"Generated DDR Report: {ddr_report.report_id}")
            
            # STAGE 7: HTML Report Generation
            logger.info("=== STAGE 7: HTML Report Generation ===")
            html_content = self.html_generator.generate_html_report(ddr_report, final_observations)
            
            # Save reports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("./outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save HTML
            html_path = output_dir / f"ddr_{timestamp}.html"
            self.html_generator.save_html_report(html_content, str(html_path))
            results["html_report_path"] = str(html_path)
            
            # Save JSON (legacy format)
            json_path = output_dir / f"ddr_{timestamp}.json"
            self.legacy_report_gen.export_to_json(ddr_report, str(json_path))
            results["json_report_path"] = str(json_path)
            
            # Save text (legacy format)
            text_path = output_dir / f"ddr_{timestamp}.txt"
            self.legacy_report_gen.export_to_text(ddr_report, str(text_path))
            results["text_report_path"] = str(text_path)
            
            logger.info(f"✅ DDR Generation Complete")
            logger.info(f"   HTML: {html_path}")
            logger.info(f"   JSON: {json_path}")
            logger.info(f"   TXT: {text_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            results["error"] = str(e)
            return results

    def process_json_fallback(self, json_paths: List[str]) -> Dict:
        """
        Fallback processor for JSON inputs (used when PDFs not available).
        Maintains backward compatibility with existing test data.
        """
        logger.info(f"Processing {len(json_paths)} JSON file(s) as fallback...")
        
        results = {
            "json_documents_loaded": [],
            "observations_extracted": 0,
            "ddr_report": None,
            "html_report_path": None
        }
        
        try:
            all_extraction_results = []
            
            for json_path in json_paths:
                json_file = Path(json_path)
                if not json_file.exists():
                    logger.warning(f"JSON not found: {json_path}")
                    continue
                
                with open(json_file) as f:
                    data = json.load(f)
                
                # Import extraction module for JSON parsing
                from modules.extraction import DocumentExtractor, DocumentType
                
                # Determine document type from filename
                if "thermal" in json_file.name.lower():
                    doc_type = DocumentType.THERMAL_REPORT
                else:
                    doc_type = DocumentType.INSPECTION_REPORT
                
                # Extract observations using legacy extractor
                extractor = DocumentExtractor()
                result = extractor.extract_from_json(data, doc_type, json_file.name)
                
                # Result should be ExtractionResult
                all_extraction_results.append(result)
                
                results["json_documents_loaded"].append(json_file.name)
            
            # Gather all observations for counting
            all_observations = []
            for result in all_extraction_results:
                if hasattr(result, 'observations'):
                    all_observations.extend(result.observations)
            
            results["observations_extracted"] = len(all_observations)
            
            # Generate DDR report using pipeline for proper processing
            if all_extraction_results:
                structured, reasoning, ddr_report = self.legacy_pipeline.process(all_extraction_results)
                results["ddr_report"] = ddr_report
                
                # Generate HTML report
                html_content = self.html_generator.generate_html_report(ddr_report, all_observations)
                
                # Save HTML
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path("./outputs")
                output_dir.mkdir(parents=True, exist_ok=True)
                html_path = output_dir / f"ddr_{timestamp}_fallback.html"
                self.html_generator.save_html_report(html_content, str(html_path))
                results["html_report_path"] = str(html_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Fallback processing error: {e}", exc_info=True)
            results["error"] = str(e)
            return results


def main():
    """Main entry point."""
    print("""
=============================================================
  Advanced AI-DDR Generator with Gemini Integration
  
  Pipeline: PDF -> Schema -> Observations -> Reports
=============================================================
    """)
    
    # Configure paths
    data_dir = Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    generator = AdvancedDDRGenerator()
    
    # Check for PDF files
    pdf_files = list(data_dir.glob("*.pdf"))
    json_files = list(data_dir.glob("*.json"))
    
    if not pdf_files and not json_files:
        logger.info("No PDF or JSON files found in ./data directory")
        logger.info("Creating sample PDFs for demonstration...")
        
        try:
            from utils.pdf_generator import create_sample_pdfs
            sample_pdfs = create_sample_pdfs(data_dir)
            if sample_pdfs["inspection"]:
                pdf_files.append(Path(sample_pdfs["inspection"]))
            if sample_pdfs["thermal"]:
                pdf_files.append(Path(sample_pdfs["thermal"]))
            logger.info(f"Created sample PDFs: {pdf_files}")
        except Exception as e:
            logger.error(f"Failed to create sample PDFs: {e}")
            logger.warning("Falling back to JSON files...")
    
    # Process PDFs if available
    if pdf_files:
        logger.info(f"\n🔍 Found {len(pdf_files)} PDF file(s)")
        pdf_paths = [str(f) for f in pdf_files]
        
        # Check for Gemini API key
        if not os.environ.get("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY not set. Schema extraction will fail.")
            logger.warning("Set: export GOOGLE_API_KEY=<your-key>")
        
        results = generator.process_pdfs(pdf_paths)
        
        # Print summary
        print(f"\n📊 Processing Results:")
        print(f"   PDFs Extracted: {len(results['pdfs_extracted'])}")
        print(f"   Observations Found: {len(results['merged_observations'])}")
        print(f"   Conflicts Detected: {len(results['conflicts_detected'])}")
        print(f"   HTML Report: {results.get('html_report_path', 'N/A')}")
        print(f"   JSON Report: {results.get('json_report_path', 'N/A')}")
        
    # Fallback to JSON if no PDFs or if PDF processing failed
    elif json_files:
        logger.info(f"\n🔄 Using JSON fallback: {len(json_files)} file(s)")
        results = generator.process_json_fallback([str(f) for f in json_files])
        
        print(f"\n📊 Processing Results (Fallback):")
        print(f"   JSON Documents: {len(results['json_documents_loaded'])}")
        print(f"   Observations Extracted: {results['observations_extracted']}")
        print(f"   HTML Report: {results.get('html_report_path', 'N/A')}")
    
    else:
        logger.error("No PDF or JSON files available for processing")


if __name__ == "__main__":
    main()
