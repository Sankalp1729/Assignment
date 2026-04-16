"""
Test Gemini integration step by step.
Run this to verify Gemini is working before running full pipeline.
"""

import sys
from pathlib import Path
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.gemini_client import init_gemini, ask_gemini_json
from utils.schema_extractor import extract_schema, extract_observations
from utils.pdf_extractor import PDFExtractor


def test_gemini_connection():
    """Test if Gemini API is accessible."""
    print("\n" + "="*60)
    print("TEST 1: Gemini API Connection")
    print("="*60)
    
    if not init_gemini():
        print("❌ Gemini API not available")
        print("   Make sure GOOGLE_API_KEY is set in .env file")
        return False
    
    print("✓ Gemini API connected successfully")
    return True


def test_schema_extraction():
    """Test schema extraction from sample text."""
    print("\n" + "="*60)
    print("TEST 2: Schema Extraction")
    print("="*60)
    
    # Sample inspection text
    sample_text = """
    Property Inspection Report
    
    Date: 2026-04-16
    
    The terrace shows signs of water damage with visible cracks in the concrete surface.
    The south wall exhibits moisture issues and heat loss through the outer layer.
    
    Temperature measurements show the exterior wall is 15°C cooler than interior (22°C),
    indicating insulation failure. Relative humidity in the cellar is 85% RH.
    
    East wall foundation shows minor cracks (2mm width) and some deterioration.
    Thermal imaging revealed heat loss patterns consistent with poor insulation.
    """
    
    print("📄 Sample text length:", len(sample_text), "characters")
    print("\n🧠 Extracting schema...")
    
    schema = extract_schema(sample_text)
    
    if "error" in schema:
        print(f"❌ Error: {schema['error']}")
        return False
    
    print("✓ Schema extracted successfully!")
    print(f"\n  Areas found ({len(schema['areas'])}): {', '.join(schema['areas'])}")
    print(f"  Issue types ({len(schema['issue_types'])}): {', '.join(schema['issue_types'])}")
    print(f"  Units ({len(schema['units'])}): {', '.join(schema['units'])}")
    
    return True, schema


def test_observation_extraction():
    """Test observation extraction from sample text."""
    print("\n" + "="*60)
    print("TEST 3: Observation Extraction")
    print("="*60)
    
    # Sample text
    sample_text = """
    Property Inspection Report
    
    Terrace: The terrace surface shows significant water damage with multiple cracks.
    The concrete appears to have settled in the center area.
    
    South Wall: Moisture detected on the lower portion. Paint is peeling and there
    is visible mold growth in corners where humidity is high.
    
    Foundation: Minor structural cracks observed, approximately 2-3mm in width.
    No active water seepage currently visible.
    """
    
    print("📄 Sample text length:", len(sample_text), "characters")
    
    # First extract schema
    print("\n1️⃣ Extracting schema...")
    schema = extract_schema(sample_text)
    print(f"   ✓ Found {len(schema['areas'])} areas")
    
    # Then extract observations
    print("2️⃣ Extracting observations...")
    result = extract_observations(sample_text, schema, doc_type="inspection")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    observations = result.get("observations", [])
    print(f"✓ Extracted {len(observations)} observations!\n")
    
    for i, obs in enumerate(observations, 1):
        print(f"   Observation {i}:")
        print(f"     Area: {obs['area']}")
        print(f"     Issue: {obs['issue_type']}")
        print(f"     Description: {obs['description']}")
        print(f"     Severity: {obs['severity']} (confidence: {obs['confidence']})")
    
    return True, observations


def test_pdf_extraction():
    """Test PDF extraction."""
    print("\n" + "="*60)
    print("TEST 4: PDF Extraction")
    print("="*60)
    
    data_dir = Path(__file__).parent / "data"
    pdf_path = data_dir / "inspection.pdf"
    
    if not pdf_path.exists():
        print(f"ℹ PDF not found at {pdf_path}")
        print("   This is OK if you haven't added PDFs yet")
        return None
    
    print(f"📄 Extracting from {pdf_path.name}...")
    
    extractor = PDFExtractor()
    result = extractor.extract_pdf(str(pdf_path))
    
    if result is None:
        print("❌ PDF extraction failed")
        return False
    
    text = result.get("text", "")
    print(f"✓ Extracted {len(text)} characters")
    print(f"  First 200 chars: {text[:200]}...")
    
    return True, text[:2000]  # Return first 2000 chars for next steps


def main():
    """Run all tests."""
    print(r"""
    
╔════════════════════════════════════════════════════════════╗
║         Gemini Integration Test Suite                      ║
║                                                            ║
║  Testing: API → Schema → Observations → PDF               ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Connection
    if not test_gemini_connection():
        print("\n❌ Setup failed. Check your .env file:")
        print("   1. File should be: AI_DDR_Generator/.env")
        print("   2. Content should be: GOOGLE_API_KEY=your_key")
        return 1
    
    # Test 2: Schema extraction
    result = test_schema_extraction()
    if not result:
        return 1
    _, schema = result
    
    # Test 3: Observation extraction
    result = test_observation_extraction()
    if not result:
        return 1
    
    # Test 4: PDF extraction (optional)
    test_pdf_extraction()
    
    # Success summary
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYou're ready to run: python main.py")
    print("Or: python main_advanced.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
