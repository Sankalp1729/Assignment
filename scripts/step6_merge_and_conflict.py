"""
STEP 6 - Merge Observations + Conflict Detection
Combine inspection and thermal observations, detect conflicts
"""

import json
from pathlib import Path
from utils.merger import merge_observations, detect_conflicts, get_merge_statistics


# Mock thermal observations for demonstration
MOCK_THERMAL_OBSERVATIONS = [
    {
        "area": "Living Room",
        "issue": "Heat Loss",
        "description": "Significant thermal anomaly detected near wall junction",
        "severity_hint": "major"
    },
    {
        "area": "Bedroom Window",
        "issue": "Thermal Bridge",
        "description": "Infrared signature shows cold spots at window frame",
        "severity_hint": "major"
    },
    {
        "area": "Foundation Area",
        "issue": "Moisture and Thermal Loss",
        "description": "Basement thermal scan shows temperature differential",
        "severity_hint": "major"
    },
]


def load_inspection_observations(filepath: str):
    """Load inspection observations from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON: {filepath}")
        return []


def main():
    """Main STEP 6 workflow"""
    
    print("\n" + "=" * 80)
    print("STEP 6 - MERGE OBSERVATIONS + CONFLICT DETECTION")
    print("=" * 80)
    print()
    
    # Setup paths
    project_root = Path(__file__).parent
    inspection_file = project_root / "outputs" / "observations.json"
    
    # Load inspection observations from STEP 5
    print("📋 Loading observations from STEP 5...")
    inspection_obs = load_inspection_observations(str(inspection_file))
    
    if not inspection_obs:
        print("❌ No inspection observations found")
        print("   Please run STEP 5 first: python step5_extract_observations.py")
        return
    
    print(f"✓ Loaded {len(inspection_obs)} inspection observations")
    
    # Thermal observations (would come from real thermal report in production)
    print("\n🌡️  Loading thermal observations...")
    thermal_obs = MOCK_THERMAL_OBSERVATIONS
    print(f"✓ Loaded {len(thermal_obs)} thermal observations (mock data)")
    
    # Merge observations
    print("\n🔀 Merging observations...")
    merged = merge_observations(inspection_obs, thermal_obs)
    print(f"✓ Merged into {len(merged)} combined records")
    
    # Detect conflicts
    print("\n⚠️  Detecting conflicts...")
    conflicts = detect_conflicts(merged)
    print(f"✓ Found {len(conflicts)} potential conflicts")
    
    # Calculate statistics
    stats = get_merge_statistics(merged)
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 MERGE STATISTICS")
    print("=" * 80)
    print(f"  Total merged observations: {stats['total_observations']}")
    print(f"  Matched pairs (inspection + thermal): {stats['matched_pairs']}")
    print(f"  Inspection-only: {stats['inspection_only']}")
    print(f"  Thermal-only: {stats['thermal_only']}")
    print(f"  Both data present: {stats['both_present']}")
    print(f"  Match rate: {stats['match_rate']}")
    
    # Display merged observations
    print("\n" + "=" * 80)
    print("📋 MERGED OBSERVATIONS (First 5)")
    print("=" * 80)
    
    for i, item in enumerate(merged[:5], 1):
        print(f"\n[{i}] AREA: {item['area']}")
        print(f"    Inspection: {item['inspection_issue']}")
        print(f"    Thermal: {item['thermal_issue']}")
        print(f"    Severity: {item['severity_hint'].upper()}")
        print(f"    Thermal Match: {'✓ Yes' if item['thermal_flag'] else '✗ No'}")
        if item['matched']:
            print(f"    Match Confidence: {item['similarity_score']:.0f}%")
    
    if len(merged) > 5:
        print(f"\n... and {len(merged) - 5} more observations")
    
    # Display conflicts
    if conflicts:
        print("\n" + "=" * 80)
        print("⚠️  DETECTED CONFLICTS (First 5)")
        print("=" * 80)
        
        for i, conflict in enumerate(conflicts[:5], 1):
            print(f"\n[{i}] AREA: {conflict['area']}")
            print(f"    Type: {conflict['conflict_type']}")
            print(f"    Confidence: {conflict['confidence']}")
            print(f"    Inspection: {conflict.get('inspection_issue', 'N/A')}")
            print(f"    Thermal: {conflict.get('thermal_issue', 'N/A')}")
            print(f"    Note: {conflict['note']}")
            print(f"    Recommendation: {conflict['recommendation']}")
        
        if len(conflicts) > 5:
            print(f"\n... and {len(conflicts) - 5} more conflicts")
    else:
        print("\n✅ No conflicts detected - observations are consistent!")
    
    # Save results
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Save merged data
    merged_file = output_dir / "merged_observations.json"
    with open(merged_file, 'w') as f:
        json.dump(merged, f, indent=2)
    print(f"\n💾 Merged observations saved: {merged_file}")
    
    # Save conflicts
    if conflicts:
        conflicts_file = output_dir / "detected_conflicts.json"
        with open(conflicts_file, 'w') as f:
            json.dump(conflicts, f, indent=2)
        print(f"💾 Detected conflicts saved: {conflicts_file}")
    
    # Save statistics
    stats_file = output_dir / "merge_statistics.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"💾 Merge statistics saved: {stats_file}")
    
    # Final checkpoint
    print("\n" + "=" * 80)
    print("🎯 STEP 6 CHECKPOINT - All Requirements Met")
    print("=" * 80)
    print("✓ Combined inspection + thermal observations")
    print("✓ Intelligently matched areas using fuzzy matching")
    print("✓ Handled missing information gracefully")
    print("✓ Detected logical conflicts")
    print("✓ Generated merge statistics")
    print("✓ Saved all output files")
    print()
    print("📊 OUTPUT FILES GENERATED:")
    print(f"  • {merged_file.name}")
    print(f"  • {stats_file.name}")
    if conflicts:
        print(f"  • {conflicts_file.name}")
    print()


if __name__ == "__main__":
    main()
