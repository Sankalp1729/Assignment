"""
AI-Based DDR (Detailed Diagnostic Report) Generator
Main Entry Point with PDF Extraction Support
"""

import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    DocumentExtractor,
    DDRPipeline,
    DocumentType,
)
from modules.report_generator import ReportGenerator
from utils import PDFExtractor, ImageExtractor


def load_pdf_data(pdf_path: str, document_type: DocumentType):
    """Load data from PDF (or JSON representation of PDF)"""
    extractor = DocumentExtractor()
    pdf_extractor = PDFExtractor()

    # Try to extract from PDF (will fall back to JSON if available)
    content = pdf_extractor.extract_pdf(pdf_path)

    # Extract observations
    result = extractor.extract_from_json(
        content, document_type, Path(pdf_path).name
    )

    return result


def main():
    """Main DDR generation workflow"""
    print("=" * 80)
    print("AI-BASED DDR (DETAILED DIAGNOSTIC REPORT) GENERATOR")
    print("=" * 80)
    print()

    # Setup paths
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    output_dir = project_root / "outputs"
    images_dir = project_root / "images"

    output_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    # Step 1: Extract images from PDFs
    print("📸 Step 1: Extracting images from documents...")
    print("-" * 80)
    
    image_extractor = ImageExtractor(str(images_dir))
    all_images = image_extractor.batch_extract_images(str(data_dir))
    image_report = image_extractor.generate_image_report(all_images)
    print(f"✅ Extracted {image_report['total_images']} images")
    print(f"   By type: {image_report['by_type']}")
    print()

    # Step 2: Load PDF data
    print("📄 Step 2: Loading and extracting PDF documents...")
    print("-" * 80)

    try:
        # Load inspection report
        inspection_pdf = data_dir / "inspection.pdf"
        inspection_json = data_dir / "inspection.pdf.json"
        
        if inspection_json.exists():
            with open(inspection_json) as f:
                inspection_data = json.load(f)
            inspection_result = DocumentExtractor().extract_from_json(
                inspection_data, DocumentType.INSPECTION_REPORT, inspection_pdf.name
            )
            print(f"✅ Inspection Report: {len(inspection_result.observations)} observations")
        else:
            raise FileNotFoundError(f"No inspection report found at {inspection_json}")

        # Load thermal report
        thermal_pdf = data_dir / "thermal.pdf"
        thermal_json = data_dir / "thermal.pdf.json"
        
        if thermal_json.exists():
            with open(thermal_json) as f:
                thermal_data = json.load(f)
            thermal_result = DocumentExtractor().extract_from_json(
                thermal_data, DocumentType.THERMAL_REPORT, thermal_pdf.name
            )
            print(f"✅ Thermal Report: {len(thermal_result.observations)} observations")
        else:
            raise FileNotFoundError(f"No thermal report found at {thermal_json}")

        print()
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return

    # Step 3: Run pipeline
    print("⚙️  Step 3: Running DDR Generation Pipeline...")
    print("-" * 80)
    try:
        pipeline = DDRPipeline()
        structured_data, reasoning_output, ddr_report = pipeline.process(
            [inspection_result, thermal_result]
        )
        print()
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Export reports
    print("📤 Step 4: Exporting Reports...")
    print("-" * 80)

    report_generator = ReportGenerator()

    # Export JSON
    json_path = output_dir / f"{ddr_report.report_id}.json"
    report_generator.export_to_json(ddr_report, str(json_path))
    print(f"✅ JSON Report: {json_path}")

    # Export Text
    text_path = output_dir / f"{ddr_report.report_id}.txt"
    report_generator.export_to_text(ddr_report, str(text_path))
    print(f"✅ Text Report: {text_path}")

    print()

    # Step 5: Display summary
    print("=" * 80)
    print("📊 REPORT SUMMARY")
    print("=" * 80)
    print(f"Report ID: {ddr_report.report_id}")
    print(f"Status: {ddr_report.property_summary['overall_status']}")
    print()

    print("SEVERITY BREAKDOWN:")
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "not_available"]:
        key = f"{severity.lower()}_count"
        count = ddr_report.property_summary.get(key, 0)
        print(f"  {severity}: {count}")

    print()
    print("AREAS AFFECTED:")
    for area in ddr_report.area_wise_observations:
        count = ddr_report.area_wise_observations[area]["total_issues"]
        print(f"  {area}: {count} issues")

    print()
    print("CONFLICTS NOTED:")
    if ddr_report.conflicts_noted:
        for conflict in ddr_report.conflicts_noted:
            print(f"  ⚠️  {conflict.conflict_id}: {conflict.description}")
    else:
        print("  ✅ No conflicts detected")

    print()
    print("MISSING INFORMATION:")
    if ddr_report.missing_information:
        for missing in ddr_report.missing_information:
            print(f"  ❌ {missing.data_type}: {missing.reason}")
    else:
        print("  ✅ All data available")

    print()
    print("ROOT CAUSES IDENTIFIED:")
    for cause in ddr_report.root_cause_analysis:
        print(f"  • {cause['category']}: {cause['identified_cause']}")

    print()
    print("RECOMMENDATIONS:")
    for action in ddr_report.recommended_actions:
        print(f"  [{action['priority']}] {action['category']}: {action['recommended_action']}")

    print()
    print("=" * 80)
    print("✅ DDR GENERATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"Output files generated in: {output_dir}")
    print(f"Extracted images saved in: {images_dir}")


if __name__ == "__main__":
    main()
