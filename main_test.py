"""
Main pipeline test - Clean Gemini integration.

Steps:
1. Extract PDF text
2. Extract schema from text
3. Extract observations from text
4. Display results
"""

import sys
from pathlib import Path
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.gemini_client import init_gemini, get_gemini_client
from utils.schema_extractor import extract_schema, extract_observations
from utils.pdf_extractor import PDFExtractor


def main():
    """Main pipeline."""
    print(r"""
╔═══════════════════════════════════════════════════════════╗
║     AI-Based DDR Generator                               ║
║     Gemini-Powered Inspection Analysis                   ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Setup paths
    data_dir = Path(__file__).parent / "data"
    outputs_dir = Path(__file__).parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    inspection_pdf = data_dir / "inspection.pdf"
    thermal_pdf = data_dir / "thermal.pdf"
    
    # Check for sample data
    inspection_json = data_dir / "inspection.pdf.json"
    thermal_json = data_dir / "thermal.pdf.json"
    
    print("\n" + "="*60)
    print("STEP 1: Initialize Gemini")
    print("="*60)
    
    if not init_gemini():
        print("⚠ Gemini not available - will use JSON fallback for testing")
        use_gemini = False
    else:
        print("✓ Gemini API initialized")
        use_gemini = True
    
    # Try to use PDF if available
    if inspection_pdf.exists():
        print(f"\n📄 Found PDF: {inspection_pdf.name}")
        print("\n" + "="*60)
        print("STEP 2: Extract text from PDF")
        print("="*60)
        
        extractor = PDFExtractor()
        result = extractor.extract_pdf(str(inspection_pdf))
        
        if result and result.get("text"):
            inspection_text = result["text"]
            print(f"✓ Extracted {len(inspection_text)} characters")
        else:
            print("⚠ PDF extraction failed, using JSON fallback")
            use_gemini = False
            with open(inspection_json) as f:
                data = json.load(f)
                inspection_text = data.get("text", "")[:2000]
    else:
        print("ℹ No PDF found, using JSON sample data...")
        if inspection_json.exists():
            with open(inspection_json) as f:
                data = json.load(f)
                inspection_text = data.get("text", "")[:2000]
        else:
            print("❌ No inspection data available")
            return 1
    
    if use_gemini and inspection_text:
        print("\n" + "="*60)
        print("STEP 3: Extract schema using Gemini")
        print("="*60)
        
        schema = extract_schema(inspection_text)
        
        if "error" in schema:
            print(f"❌ Error: {schema['error']}")
            return 1
        
        print(f"\n✓ Schema extracted successfully!")
        print(f"\nAreas ({len(schema['areas'])}):")
        for area in schema['areas'][:5]:
            print(f"  - {area}")
        if len(schema['areas']) > 5:
            print(f"  ... and {len(schema['areas'])-5} more")
        
        print(f"\nIssue Types ({len(schema['issue_types'])}):")
        for issue in schema['issue_types'][:5]:
            print(f"  - {issue}")
        if len(schema['issue_types']) > 5:
            print(f"  ... and {len(schema['issue_types'])-5} more")
        
        print(f"\nMeasurement Units ({len(schema['units'])}):")
        for unit in schema['units']:
            print(f"  - {unit}")
        
        print("\n" + "="*60)
        print("STEP 4: Extract observations using Gemini")
        print("="*60)
        
        result = extract_observations(inspection_text, schema, doc_type="inspection")
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return 1
        
        observations = result.get("observations", [])
        print(f"\n✓ Extracted {len(observations)} observations!\n")
        
        for i, obs in enumerate(observations[:10], 1):
            print(f"   [{i}] {obs['area'].title()} - {obs['issue_type'].title()}")
            print(f"       Severity: {obs['severity'].upper()}")
            print(f"       {obs['description'][:80]}...")
            print()
        
        if len(observations) > 10:
            print(f"   ... and {len(observations)-10} more observations")
        
        # Save results
        print("\n" + "="*60)
        print("STEP 5: Save results")
        print("="*60)
        
        output_file = outputs_dir / "gemini_extraction_result.json"
        output_data = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "schema": schema,
            "observations": observations,
            "observation_count": len(observations)
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✓ Saved to {output_file}")
    else:
        print("⚠ Gemini extraction skipped")
    
    print("\n" + "="*60)
    print("✅ Pipeline Test Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review results in outputs/gemini_extraction_result.json")
    print("2. Run full pipeline: python main_advanced.py")
    print("3. Check AI_DDR_Generator/GEMINI_QUICKSTART.md for setup")
    
    return 0


if __name__ == "__main__":
    exit(main())
