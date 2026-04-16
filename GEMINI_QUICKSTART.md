# Quick Start Guide - Secure Gemini Integration

## TL;DR Setup (2 minutes)

### 1. Get API Key
- Visit: https://aistudio.google.com/app/apikey
- Click "Get API Key"
- Copy the key

### 2. Create `.env` File
In the `AI_DDR_Generator/` folder, create a file named `.env`:

```
GOOGLE_API_KEY=paste_your_key_here
```

### 3. Run Pipeline
```bash
cd AI_DDR_Generator
python main_advanced.py
```

**That's all!** Your API key is:
- ✓ Secure (in `.gitignore`)
- ✓ Not shared (local only)
- ✓ Never logged (only used internally)

## What Each Gemini Module Does

### `gemini_schema_extractor.py`
Safely loads API key from `.env` → Extracts document schema (areas, categories, severity levels)

### `gemini_observation_extractor.py`
Safely loads API key from `.env` → Extracts structured observations from documents

### `gemini_conflict_detector.py`
Safely loads API key from `.env` → Detects conflicts and suggests root causes

## How API Key is Protected

```python
# All 3 Gemini modules use this same pattern:

from dotenv import load_dotenv
import os

# Step 1: Load .env file into environment
load_dotenv(Path(__file__).parent.parent / ".env")

# Step 2: Get key from environment (not from file)
api_key = os.getenv("GOOGLE_API_KEY")

# Step 3: Check key exists
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# Step 4: Configure Gemini (only this SDK sees the key)
genai.configure(api_key=api_key)
```

**Key Points:**
- `.env` file is never parsed/exposed
- API key only loaded into memory
- Never printed or logged
- `.gitignore` prevents accidental commit

## Files You Need

```
AI_DDR_Generator/
├── .env                          ← Create this with your key
├── .env.example                  ← Template (already exists)
├── .gitignore                    ← Already protects .env
├── modules/
│   ├── gemini_schema_extractor.py
│   ├── gemini_observation_extractor.py
│   ├── gemini_conflict_detector.py
│   ├── pymupdf_extractor.py
│   └── html_generator.py
└── main_advanced.py
```

## Testing Your Setup

```python
# Test 1: Check .env file exists
ls -la | grep .env  # Should see .env file

# Test 2: Check API key loads
python -c "
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv(Path('.') / '.env')
print('Key loaded' if os.getenv('GOOGLE_API_KEY') else 'Key missing')
"

# Test 3: Run pipeline
python main_advanced.py
```

## Expected Output

```
============================================================
Advanced DDR Generator - Gemini Integration
============================================================
✓ Gemini API initialized successfully

[STEP 1] Extracting text from inspection.pdf...
  ✓ Extracted 10 pages, 5 images

[STEP 2] Extracting schema...
  ✓ Found 5 areas, 4 categories

[STEP 3] Extracting observations...
  ✓ Inspection: 8 observations
  ✓ Thermal: 6 observations

[STEP 4] Detecting conflicts...
  ✓ Conflicts detected: 1

[STEP 8] Exporting reports...
  ✓ JSON: outputs/ddr_20260416_153022.json
  ✓ Text: outputs/ddr_20260416_153022.txt
  ✓ HTML: outputs/ddr_20260416_153022.html

✓ Pipeline completed successfully!
```

## No API Key? No Problem!

The system automatically falls back to JSON mode:

```
⚠ Gemini initialization failed: GOOGLE_API_KEY not found
  Falling back to standard pipeline...

[Using JSON Fallback Mode]
✓ Inspection: 6 observations
✓ Thermal: 5 observations
```

This provides full functionality without Gemini!

## Frequently Asked Questions

**Q: Is my API key safe?**
A: Yes! It's:
- Never stored in git
- Never logged or printed
- Only used directly by Gemini SDK
- Protected by `.gitignore`

**Q: What if the key leaks?**
A: Delete it from Google AI Studio and create a new one. Update `.env`. Done!

**Q: Can I use without API key?**
A: Yes! JSON fallback mode works perfectly for testing.

**Q: Why use `.env` instead of hardcoding?**
A: Best practice security. Anyone with the code can't access your key.

**Q: Where's my actual key stored?**
A: Nowhere public! Only in:
- Your local `.env` file (not in git)
- RAM when running (temporary)
- Google's servers (as your API quota)

## Need Help?

1. Check [API_KEY_SETUP.md](API_KEY_SETUP.md) for detailed instructions
2. Verify `.env` exists and has correct format
3. Make sure key is from [Google AI Studio](https://aistudio.google.com/app/apikey)
4. Run `python main_advanced.py` - it will show setup errors

Ready to go! 🚀
