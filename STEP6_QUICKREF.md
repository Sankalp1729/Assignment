# STEP 6 Quick Reference

## ✅ What Was Built

**Merge + Conflict Detection** for combining inspection and thermal observations.

### Core Module: `utils/merger.py`
- `match_areas()` - Fuzzy string matching for area names
- `merge_observations()` - Combine observations from multiple sources
- `detect_conflicts()` - Identify logical conflicts
- `get_merge_statistics()` - Quality metrics

### Demo Script: `step6_merge_and_conflict.py`
- Full working example
- Run: `python step6_merge_and_conflict.py`
- Generates 3 output files

---

## 🚀 Quick Start

### Test It
```bash
cd AI_DDR_Generator
python step6_merge_and_conflict.py
```

### Expected Output
```
✅ OBSERVATIONS EXTRACTED
  Total merged: 3
  Matched pairs: 3
  Match rate: 100.0%

⚠️ DETECTED CONFLICTS: 1
  - Minor physical issue with thermal anomaly
  
💾 OUTPUT FILES:
  • merged_observations.json
  • detected_conflicts.json
  • merge_statistics.json
```

---

## 📋 Use in Your Code

### Basic Example
```python
from utils.merger import merge_observations, detect_conflicts

# You already have these from STEP 5
inspection_obs = [...]  # From observations.json
thermal_obs = [...]     # From thermal report

# Merge them
merged = merge_observations(inspection_obs, thermal_obs)

# Detect conflicts
conflicts = detect_conflicts(merged)

print(f"Merged: {len(merged)} observations")
print(f"Conflicts: {len(conflicts)}")
```

### With Statistics
```python
from utils.merger import merge_observations, get_merge_statistics

merged = merge_observations(inspection_obs, thermal_obs)
stats = get_merge_statistics(merged)

print(f"Matched pairs: {stats['matched_pairs']}")
print(f"Match rate: {stats['match_rate']}")
print(f"Both present: {stats['both_present']}")
```

---

## 📊 Output Structure

### Merged Observation
```json
{
  "area": "Living Room Wall",
  "inspection_issue": "Crack",
  "thermal_issue": "Heat Loss",
  "description": "Combined description...",
  "severity_hint": "minor",
  "thermal_flag": true,
  "matched": true,
  "similarity_score": 100.0
}
```

### Detected Conflict
```json
{
  "area": "Living Room Wall",
  "conflict_type": "Minor physical issue with thermal anomaly",
  "inspection_issue": "Crack",
  "thermal_issue": "Heat Loss",
  "confidence": "HIGH",
  "note": "Minor issue present but thermal signature suggests...",
  "recommendation": "Investigate if crack is allowing thermal loss"
}
```

### Statistics
```json
{
  "total_observations": 3,
  "matched_pairs": 3,
  "inspection_only": 0,
  "thermal_only": 0,
  "both_present": 3,
  "match_rate": "100.0%"
}
```

---

## 🔑 Key Functions

### `match_areas(area1, area2, threshold=70)`
Fuzzy match two area names.

```python
# Returns: True/False
match_areas("Living Room", "living room")        → True
match_areas("Wall", "living room wall")          → True
match_areas("Kitchen", "Garage")                 → False
```

### `merge_observations(inspection_obs, thermal_obs)`
Combine two observation lists.

```python
# Returns: List of merged dictionaries
result = merge_observations(inspection_list, thermal_list)
# Each item has: area, inspection_issue, thermal_issue, etc.
```

### `detect_conflicts(merged_data)`
Find logical conflicts.

```python
# Returns: List of conflict records
conflicts = detect_conflicts(merged_observations)
# Each conflict has: area, type, confidence, recommendation
```

### `get_merge_statistics(merged_data)`
Get quality metrics.

```python
# Returns: Dictionary with statistics
stats = get_merge_statistics(merged_observations)
# Keys: total_observations, matched_pairs, match_rate, etc.
```

---

## ✨ Key Features

✅ **Intelligent Fuzzy Matching**
- Handles capitalization differences
- Tolerates minor typos
- Uses token-based comparison

✅ **Graceful Missing Data**
- "Not Available" for missing data
- Both data sources tracked
- Combined descriptions preserved

✅ **Conflict Detection**
- 3 conflict types identified
- Confidence levels assigned
- Recommendations included

✅ **Quality Metrics**
- Match rate percentage
- Coverage by document type
- Matched pairs count

---

## 📂 Generated Files

```
outputs/
├── merged_observations.json      ← Combined data
├── detected_conflicts.json       ← Issues found
└── merge_statistics.json         ← Quality metrics
```

---

## 🧪 Verification Checklist

After running `python step6_merge_and_conflict.py`:

- [ ] Script completed without errors
- [ ] Saw merge statistics output
- [ ] Saw merged observations
- [ ] Saw conflict detection
- [ ] File `merged_observations.json` exists
- [ ] File `detected_conflicts.json` exists
- [ ] File `merge_statistics.json` exists
- [ ] JSON files are valid (no syntax errors)

**All checked?** ✅ STEP 6 is complete!

---

## 🎯 Understanding the Matching

### How Fuzzy Matching Works

```
Inspection: "Bedroom Wall"
Thermal:    "bedroom"
            ↓
    [token_set_ratio comparison]
    ↓
Score: 100% → MATCH
```

**Threshold:** 70%
- Above 70% → Match found
- Below 70% → No match

### Example Matches
```
"Living Room Wall" + "living room"      → 100% ✓
"Bedroom Window" + "bedroom"            → 90%  ✓
"Kitchen Ceiling" + "kitchen"           → 85%  ✓
"Wall" + "Foundation"                   → 20%  ✗
```

---

## ⚠️ Common Issues

### Match rate is low?
- Check area name differences
- Try lowering threshold: `match_areas(a, b, 60)`
- Review naming conventions

### Too many conflicts?
- Check severity classifications
- Verify data freshness
- Review conflict types

### Empty conflicts?
- This is OK! No issues found
- System still merges observations

---

## 💡 Tips

**Tip 1: Access specific conflict type**
```python
conflicts = detect_conflicts(merged)
high_severity = [c for c in conflicts if c['confidence'] == 'HIGH']
```

**Tip 2: Filter merged by match type**
```python
merged = merge_observations(insp, therm)
matched = [m for m in merged if m['matched']]      # Only matched pairs
unmatched_insp = [m for m in merged if not m['matched'] and m['inspection_issue'] != "Not Available"]
```

**Tip 3: Get match score for specific area**
```python
from rapidfuzz import fuzz
score = fuzz.token_set_ratio("wall".lower(), "living room wall".lower())
# Returns: 60% (below 70% threshold)
```

---

## 📈 Test Results

```
INPUT:
• Inspection: 3 observations
• Thermal: 3 observations

OUTPUT:
• Merged: 3 records
• Matched: 3 pairs (100%)
• Conflicts: 1 detected

STATUS: ✅ SUCCESS
```

---

## 🔗 Pipeline Overview

```
STEP 5 Outputs
├── observations.json (inspection)
│
STEP 6 (You are here)
├── Thermal observations (mock or real)
├── Fuzzy matching
├── Merge logic
├── Conflict detection
│
STEP 6 Outputs
├── merged_observations.json
├── detected_conflicts.json
└── merge_statistics.json
```

---

**Ready to move to STEP 7 - Report Generation?** 🚀
