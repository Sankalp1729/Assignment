# Quick Start — 5-Minute Setup

## 📋 Prerequisites
- Python 3.11+
- Gemini API key (free)
- ~5 minutes

## 🚀 Setup Steps

### 1. Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key (2 min)
1. Visit: https://ai.google.dev/
2. Click "Get API Key"
3. Copy your API key

### 3. Configure .env (1 min)
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

### 4. Run System (1 min)
```bash
python main.py
```

### 5. View Report (instant)
```bash
cat outputs/ddr_report.txt
```

## ✅ Done!

Your professional diagnostic report is ready in `outputs/ddr_report.txt`

---

## 🧪 Test Individual Steps

```bash
# Test extraction (STEP 5)
python scripts/step5_extract_observations.py

# Test merging (STEP 6)
python scripts/step6_merge_and_conflict.py

# Test severity (STEP 7)
python scripts/step7_severity_scoring.py

# Test report (STEP 8)
python scripts/step8_generate_ddr.py
```

---

## 📂 Where to Find Things

| What | Where |
|------|-------|
| Final report | `outputs/ddr_report.txt` |
| Input PDFs | `data/` |
| Documentation | `docs/` |
| Source code | `utils/` |
| Test scripts | `scripts/` |
| Configuration | `.env` |

---

## 🆘 Stuck?

- **API issue?** → Read `docs/API_SETUP.md`
- **Error?** → Check `docs/TROUBLESHOOTING.md`
- **Want details?** → Read `docs/SYSTEM_OVERVIEW.md`
- **Understand architecture?** → Check `PROJECT_STRUCTURE.md`

---

**Next:** Read `docs/SYSTEM_OVERVIEW.md` for complete architecture details.
