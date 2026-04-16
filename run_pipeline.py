"""
Simple pipeline runner - DDR Generation with Gemini
"""

import sys
import json
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.extraction import DocumentExtractor, DocumentType
from modules.structuring import DataStructurer
from modules.reasoning import ReasoningEngine
from modules.report_generator import ReportGenerator
from modules.html_generator import HTMLReportGenerator


def main():
    """Run pipeline."""
    print("\n" + "="*60)
    print("AI-Based DDR Generator Pipeline")
    print("="*60)
    
    # Paths
    data_dir = Path(__file__).parent / "data"
    outputs_dir = Path(__file__).parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    inspection_json = data_dir / "inspection.pdf.json"
    thermal_json = data_dir / "thermal.pdf.json"
    
    # Check files exist
    if not inspection_json.exists() or not thermal_json.exists():
        print("ERROR: Missing data files")
        print(f"  Looking for: {inspection_json}")
        print(f"               {thermal_json}")
        return 1
    
    print("\nSTEP 1: Loading documents...")
    
    # Load inspection
    with open(inspection_json) as f:
        inspection_data = json.load(f)
    
    extractor = DocumentExtractor()
    inspection_result = extractor.extract_from_json(
        inspection_data,
        DocumentType.INSPECTION_REPORT,
        inspection_json.name
    )
    print(f"  Inspection: {len(inspection_result.observations)} observations")
    
    # Load thermal
    with open(thermal_json) as f:
        thermal_data = json.load(f)
    
    thermal_result = extractor.extract_from_json(
        thermal_data,
        DocumentType.THERMAL_REPORT,
        thermal_json.name
    )
    print(f"  Thermal: {len(thermal_result.observations)} observations")
    
    print("\nSTEP 2: Structuring data...")
    
    structurer = DataStructurer()
    structured_data = structurer.structure_extraction_results(
        [inspection_result, thermal_result]
    )
    print(f"  Areas: {len(structured_data.area_wise_data)}")
    
    print("\nSTEP 3: Running analysis...")
    
    reasoning = ReasoningEngine()
    reasoning_output = reasoning.analyze_structured_data(structured_data)
    print(f"  Conflicts: {len(reasoning_output.conflicts)}")
    print(f"  Missing data: {len(reasoning_output.missing_data)}")
    
    print("\nSTEP 4: Generating report...")
    
    report_gen = ReportGenerator()
    ddr_report = report_gen.generate_ddr_report(
        structured_data,
        reasoning_output
    )
    print(f"  Report ID: {ddr_report.report_id}")
    
    print("\nSTEP 5: Exporting...")
    
    # JSON export
    json_path = outputs_dir / f"{ddr_report.report_id}.json"
    report_gen.export_to_json(ddr_report, str(json_path))
    print(f"  JSON: {json_path.name}")
    
    # Text export
    text_path = outputs_dir / f"{ddr_report.report_id}.txt"
    report_gen.export_to_text(ddr_report, str(text_path))
    print(f"  Text: {text_path.name}")
    
    # HTML export
    html_gen = HTMLReportGenerator()
    html_path = outputs_dir / f"{ddr_report.report_id}.html"
    html_gen.save_html(ddr_report, str(html_path))
    print(f"  HTML: {html_path.name}")
    
    print("\n" + "="*60)
    print("SUCCESS! Pipeline complete")
    print("="*60)
    print(f"\nReports saved to: {outputs_dir}")
    print(f"  - {json_path.name}")
    print(f"  - {text_path.name}")
    print(f"  - {html_path.name}")
    
    return 0


if __name__ == "__main__":
    exit(main())
