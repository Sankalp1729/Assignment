"""Main pipeline orchestration"""

from typing import List
from datetime import datetime
from .extraction import DocumentExtractor
from .structuring import DataStructurer
from .reasoning import ReasoningEngine
from .report_generator import ReportGenerator
from .data_models import (
    ExtractionResult,
    StructuredData,
    ReasoningOutput,
    DDRReport,
    DocumentType,
)


class DDRPipeline:
    """Main orchestrator for DDR generation pipeline"""

    def __init__(self):
        self.extractor = DocumentExtractor()
        self.structurer = DataStructurer()
        self.reasoning_engine = ReasoningEngine()
        self.report_generator = ReportGenerator()

    def process(
        self,
        extraction_results: List[ExtractionResult],
    ) -> tuple[StructuredData, ReasoningOutput, DDRReport]:
        """
        Run complete DDR generation pipeline.
        
        Steps:
        1. Structure the extraction results
        2. Perform reasoning
        3. Generate report
        """
        print("[Pipeline] Starting DDR generation...")
        print(f"[Pipeline] Processing {len(extraction_results)} documents")

        # Step 1: Structuring
        print("[Pipeline] Step 1: Structuring data...")
        structured_data = self.structurer.structure_extraction_results(
            extraction_results
        )
        struct_validation = self.structurer.validate_structure(structured_data)
        print(f"[Pipeline] Structured data: {struct_validation['stats']}")
        if struct_validation["warnings"]:
            for warning in struct_validation["warnings"]:
                print(f"  ⚠️  {warning}")

        # Step 2: Reasoning
        print("[Pipeline] Step 2: Performing reasoning...")
        reasoning_output = self.reasoning_engine.analyze_structured_data(
            structured_data
        )
        print(f"[Pipeline] Found {len(reasoning_output.conflicts)} conflicts")
        print(f"[Pipeline] Found {len(reasoning_output.missing_data)} missing data points")
        print(f"[Pipeline] Generated {len(reasoning_output.cross_doc_insights)} insights")

        # Step 3: Report Generation
        print("[Pipeline] Step 3: Generating DDR report...")
        ddr_report = self.report_generator.generate_ddr_report(
            structured_data, reasoning_output
        )
        print(f"[Pipeline] Report generated: {ddr_report.report_id}")
        print(f"[Pipeline] Status: {ddr_report.property_summary['overall_status']}")

        print("[Pipeline] ✅ Pipeline complete!")

        return structured_data, reasoning_output, ddr_report
