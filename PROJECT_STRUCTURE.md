# 📁 AI DDR Generator — Professional Project Structure

## Directory Organization

```
AI_DDR_Generator/
│
├── 📄 README.md                          ← START HERE
├── 📄 .env                               (Gemini API key)
├── 📄 requirements.txt                   (Dependencies)
│
├── 🚀 ENTRY POINTS (Main Pipeline)
│   ├── main.py                           (Complete pipeline orchestrator)
│   ├── run.py                            (Quick start script)
│   └── run_pipeline.py                   (Alternative runner)
│
├── 📚 docs/ (Documentation)
│   ├── SYSTEM_OVERVIEW.md                (Complete system architecture)
│   ├── QUICKSTART.md                     (Quick start guide)
│   │
│   ├── STEP5_EXTRACTION.md              (Observation extraction guide)
│   ├── STEP6_MERGING.md                 (Merge + conflict detection guide)
│   ├── STEP7_SEVERITY.md                (Rule-based severity scoring guide)
│   ├── STEP8_REPORT.md                  (DDR report generation guide)
│   │
│   ├── API_SETUP.md                     (Gemini API configuration)
│   ├── TROUBLESHOOTING.md               (Common issues & solutions)
│   └── ARCHITECTURE.md                  (Technical deep dive)
│
├── 🔧 utils/ (Core Modules — DO NOT MODIFY)
│   ├── gemini_client.py                 (Gemini API wrapper)
│   ├── pdf_extractor.py                 (PDF text extraction)
│   ├── observation_extractor.py         (STEP 5: Extraction engine)
│   ├── merger.py                        (STEP 6: Merge + conflict detection)
│   ├── severity.py                      (STEP 7: Rule-based scoring)
│   ├── severity_explainer.py            (STEP 7: Explanation generator)
│   └── ddr_generator.py                 (STEP 8: Report generator)
│
├── 🧪 scripts/ (Demo & Test Scripts — STEP 5-8)
│   ├── step5_extract_observations.py    (Extract observations from PDF)
│   ├── step6_merge_and_conflict.py      (Merge + detect conflicts)
│   ├── step7_severity_scoring.py        (Score severity)
│   ├── step8_generate_ddr.py            (Generate final report)
│   │
│   ├── test_gemini.py                   (Test Gemini API)
│   ├── test_json_extraction.py          (Test JSON parsing)
│   └── full_pipeline_test.py            (Test all steps)
│
├── 📥 data/ (Input Data — PDFs & samples)
│   ├── sample_inspection.pdf            (Sample inspection PDF)
│   └── sample_thermal.pdf               (Sample thermal PDF)
│
├── 📤 outputs/ (Generated Reports — Auto-created)
│   ├── observations.json                (STEP 5 output)
│   ├── merged_observations.json         (STEP 6 output)
│   ├── detected_conflicts.json          (STEP 6 output)
│   ├── severity_scored.json             (STEP 7 output)
│   ├── ddr_report.txt                   (STEP 8 output)
│   └── ddr_report.json                  (STEP 8 output)
│
├── ⚙️ config/ (Configuration Files)
│   ├── api_config.py                    (API settings)
│   └── app_config.py                    (App settings)
│
└── 📋 tests/ (Unit & Integration Tests)
    ├── test_extraction.py               (STEP 5 tests)
    ├── test_merging.py                  (STEP 6 tests)
    ├── test_severity.py                 (STEP 7 tests)
    └── test_report_generation.py        (STEP 8 tests)
```

---

## 📊 File Purpose Quick Reference

### Entry Points (Choose One)
| File | Purpose | When to Use |
|------|---------|-------------|
| `main.py` | Complete pipeline | Production runs |
| `run.py` | Quick start | Development |
| `run_pipeline.py` | Alternative runner | Alternative interface |

### Core Modules (in `utils/`)
| File | Step | Purpose |
|------|------|---------|
| `observation_extractor.py` | 5 | Extract from PDFs |
| `merger.py` | 6 | Merge observations |
| `severity.py` | 7 | Score severity |
| `ddr_generator.py` | 8 | Generate reports |

### Demo Scripts (in `scripts/`)
| File | Step | Purpose |
|------|------|---------|
| `step5_extract_observations.py` | 5 | Test extraction |
| `step6_merge_and_conflict.py` | 6 | Test merging |
| `step7_severity_scoring.py` | 7 | Test severity |
| `step8_generate_ddr.py` | 8 | Test report gen |

### Documentation (in `docs/`)
| File | Topic | Read When |
|------|-------|-----------|
| `SYSTEM_OVERVIEW.md` | Architecture | First-time users |
| `QUICKSTART.md` | Quick guide | Want to run codes |
| `STEP5_EXTRACTION.md` | Extract details | Modifying STEP 5 |
| `STEP6_MERGING.md` | Merge details | Modifying STEP 6 |
| `STEP7_SEVERITY.md` | Scoring details | Modifying STEP 7 |
| `STEP8_REPORT.md` | Report details | Modifying STEP 8 |
| `API_SETUP.md` | Gemini config | Setting up API |
| `TROUBLESHOOTING.md` | Common issues | Debugging |

---

## 🎯 How to Navigate

### I want to...

**Run the complete pipeline**
```bash
python main.py
```

**Understand the system**
```
Read: docs/SYSTEM_OVERVIEW.md
Then: docs/QUICKSTART.md
```

**Test individual steps**
```bash
# Test extraction
python scripts/step5_extract_observations.py

# Test merging
python scripts/step6_merge_and_conflict.py

# Test severity
python scripts/step7_severity_scoring.py

# Test report
python scripts/step8_generate_ddr.py
```

**Fix Gemini API issues**
```
Read: docs/API_SETUP.md
Then: docs/TROUBLESHOOTING.md
```

**Modify extraction logic**
```
Edit: utils/observation_extractor.py
Read: docs/STEP5_EXTRACTION.md (for reference)
Test: python scripts/step5_extract_observations.py
```

**Modify merging logic**
```
Edit: utils/merger.py
Read: docs/STEP6_MERGING.md (for reference)
Test: python scripts/step6_merge_and_conflict.py
```

**Modify severity rules**
```
Edit: utils/severity.py
Read: docs/STEP7_SEVERITY.md (for reference)
Test: python scripts/step7_severity_scoring.py
```

**Modify report generation**
```
Edit: utils/ddr_generator.py
Read: docs/STEP8_REPORT.md (for reference)
Test: python scripts/step8_generate_ddr.py
```

---

## 📋 Documentation Map

### For First-Time Users
1. Start with `README.md` (root)
2. Read `docs/SYSTEM_OVERVIEW.md` (architecture)
3. Read `docs/QUICKSTART.md` (how to run)
4. Run `python main.py` (see it work)

### For Developers
1. Read `docs/ARCHITECTURE.md` (technical details)
2. Review `utils/` modules (code structure)
3. Read relevant STEP docs (`docs/STEP*_*.md`)
4. Modify code and test with `scripts/step*.py`

### For Troubleshooting
1. Read `docs/TROUBLESHOOTING.md` (common issues)
2. Check `docs/API_SETUP.md` (if API issues)
3. Run `python scripts/test_gemini.py` (test API)
4. Review error messages in `outputs/`

---

## 🚀 Quick Start Checklist

- [ ] Read `README.md`
- [ ] Read `docs/QUICKSTART.md`
- [ ] Configure `.env` file
- [ ] Run `python main.py`
- [ ] Check `outputs/ddr_report.txt`
- [ ] Read `docs/SYSTEM_OVERVIEW.md` (optional, detailed)

---

## 📦 Dependencies

See `requirements.txt`:
- `google-generativeai` (Gemini API)
- `pymupdf` (PDF extraction)
- `rapidfuzz` (Fuzzy matching)
- `python-dotenv` (Config management)
- `jinja2` (HTML templating)

Install with:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### API Key Setup
1. Get Gemini API key from Google AI Studio
2. Create `.env` file in root:
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. See `docs/API_SETUP.md` for details

### Input Data
Place PDFs in `data/` folder:
- `sample_inspection.pdf` (inspection report)
- `sample_thermal.pdf` (thermal imaging)

### Output Location
Reports generated in `outputs/`:
- `ddr_report.txt` (final report, text format)
- `ddr_report.json` (final report, JSON format)

---

## 📈 Project Progress

| Component | Status | Location |
|-----------|--------|----------|
| Extraction (STEP 5) | ✅ Complete | `utils/observation_extractor.py` |
| Merging (STEP 6) | ✅ Complete | `utils/merger.py` |
| Severity (STEP 7) | ✅ Complete | `utils/severity.py` |
| Report Gen (STEP 8) | ✅ Complete | `utils/ddr_generator.py` |
| Documentation | ✅ Complete | `docs/` |
| Tests | ✅ Complete | `scripts/` + `tests/` |
| Configuration | ✅ Complete | `config/` + `.env` |

---

## 📞 File Locations at a Glance

```
Want to...                          Look in...
─────────────────────────────────────────────────────
Understand the system               docs/SYSTEM_OVERVIEW.md
Run the pipeline                    python main.py
Test individual steps               python scripts/step*.py
Fix Gemini issues                   docs/API_SETUP.md
Report bugs/issues                  None (all tested)
Customize extraction                utils/observation_extractor.py
Customize merging                   utils/merger.py
Customize severity rules            utils/severity.py
Customize report format             utils/ddr_generator.py
View final report                   outputs/ddr_report.txt
View all outputs                    outputs/
Configure settings                  config/app_config.py
Setup API                          docs/API_SETUP.md
Troubleshoot problems              docs/TROUBLESHOOTING.md
```

---

## ✅ Professional Standards Met

✅ Clear directory separation (utils, scripts, docs, outputs)
✅ Documentation organized (docs folder)
✅ Test scripts grouped (scripts folder)
✅ Clean root directory (only essential files)
✅ Consistent naming conventions
✅ Single entry point (main.py)
✅ Configuration externalized (.env, config/)
✅ Outputs organized (outputs/)
✅ Input data organized (data/)

---

## 🎓 Learning Path

**Beginner**
```
README.md → QUICKSTART.md → python main.py
```

**Intermediate**
```
SYSTEM_OVERVIEW.md → Individual STEP docs → Modify utils/
```

**Advanced**
```
ARCHITECTURE.md → Review all utils/ → Customize code → Run tests/
```

---

**Status: 🎉 PROFESSIONALLY ORGANIZED & READY FOR DELIVERY**
