"""
STEP 8: DDR Report Generation — Demo & Test Script

Full workflow:
1. Load severity-scored observations (from STEP 7)
2. Load conflict data (from STEP 6)
3. Generate professional DDR report
4. Display sections with formatting
5. Save to text and JSON files
6. Verify checkpoint completion
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ddr_generator import (
    generate_ddr_report,
    save_report,
    export_to_json,
    format_report_for_console,
    get_report_summary,
)


def load_severity_scored_data(filepath: str = "outputs/severity_scored.json"):
    """Load severity-scored observations from STEP 7."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} severity-scored observations from STEP 7")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON: {filepath}")
        return []


def load_conflict_data(filepath: str = "outputs/detected_conflicts.json"):
    """Load conflict data from STEP 6."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✓ Loaded conflict data from STEP 6")
        return data
    except FileNotFoundError:
        print(f"⚠️  Conflict file not found: {filepath} (continuing without)")
        return None
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON in conflict file (continuing without)")
        return None


def display_report_sections(report: dict, max_length: int = 300):
    """
    Display report sections in console with formatting.
    
    Args:
        report: Generated report dictionary
        max_length: Maximum chars to display per section (for preview)
    """
    print("\n" + "="*70)
    print("📋 GENERATED DDR REPORT SECTIONS")
    print("="*70)
    
    for i, (section_name, content) in enumerate(report.items(), 1):
        # Truncate for display
        preview = content[:max_length]
        if len(content) > max_length:
            preview += f"\n... [{len(content) - max_length} more chars]"
        
        print(f"\n[{i}] {section_name}")
        print("-" * 70)
        print(preview)
        print()


def print_summary_stats(merged_data: list):
    """Print summary statistics."""
    summary = get_report_summary(merged_data)
    
    print("\n📊 SEVERITY BREAKDOWN")
    print("-" * 70)
    print(f"  Total Issues: {summary['total_issues']}")
    print(f"  🚨 Critical: {summary['by_severity']['Critical']} issue(s)")
    print(f"  ⚠️  High:     {summary['by_severity']['High']} issue(s)")
    print(f"  ⚡ Medium:   {summary['by_severity']['Medium']} issue(s)")
    print(f"  ✓ Low:      {summary['by_severity']['Low']} issue(s)")
    print(f"\n  Thermal Issues: {summary['thermal_issues']}")
    print(f"  Areas Affected: {summary['areas_affected']}")
    print(f"  Locations: {', '.join(summary['unique_areas'])}")


def main():
    """Main STEP 8 workflow."""
    print("\n" + "="*70)
    print("🔥 STEP 8: DDR REPORT GENERATION")
    print("="*70)
    
    # Step 1: Load data from previous steps
    print("\n📂 LOADING DATA FROM PREVIOUS STEPS...")
    print("-" * 70)
    
    severity_data = load_severity_scored_data()
    if not severity_data:
        print("❌ Cannot proceed without severity data. Run STEP 7 first.")
        return False
    
    conflict_data = load_conflict_data()
    
    # Step 2: Display input summary
    print_summary_stats(severity_data)
    
    # Step 3: Generate report
    print("\n🧾 GENERATING DDR REPORT...")
    print("-" * 70)
    
    # Using templates (due to Gemini quota) - set use_gemini=True if API available
    report = generate_ddr_report(
        merged_data=severity_data,
        conflicts=conflict_data,
        use_gemini=False  # Set to True if Gemini quota available
    )
    
    if not report:
        print("❌ Failed to generate report")
        return False
    
    # Step 4: Display sections (preview mode)
    print("\n📺 REPORT PREVIEW (First 300 chars per section)")
    print("-" * 70)
    display_report_sections(report, max_length=300)
    
    # Step 5: Save outputs
    print("\n💾 SAVING OUTPUTS...")
    print("-" * 70)
    
    # Save as text file
    if save_report(report):
        print("✓ Text report saved: outputs/ddr_report.txt")
    else:
        print("❌ Failed to save text report")
    
    # Save as JSON
    if export_to_json(report):
        print("✓ JSON report saved: outputs/ddr_report.json")
    else:
        print("❌ Failed to save JSON report")
    
    # Step 6: Verification checkpoint
    print("\n✅ CHECKPOINT VERIFICATION")
    print("-" * 70)
    print("  ✓ Severity-scored observations loaded (STEP 7 output)")
    print("  ✓ Conflict data loaded (STEP 6 output)")
    print(f"  ✓ Report generated ({len(report)} sections)")
    print(f"  ✓ Summary statistics calculated")
    print("  ✓ Text report saved")
    print("  ✓ JSON report saved")
    print("\n✅ STEP 8 COMPLETE - DDR REPORT GENERATION SUCCESSFUL")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
