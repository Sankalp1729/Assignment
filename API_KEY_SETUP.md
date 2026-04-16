# Secure API Key Setup Guide

## Overview

The AI-Based DDR Generator now supports **Gemini API integration** for advanced natural language processing. Your API key is kept secure using environment variables.

## Setup Instructions

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key
4. **Copy the key** (you won't see it again)

### Step 2: Create `.env` File

In the `AI_DDR_Generator/` directory, create a file named `.env` and add:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

**⚠️ IMPORTANT SECURITY NOTES:**

- ✅ `.env` is in `.gitignore` - it will NEVER be committed to git
- ✅ Never share your `.env` file
- ✅ If you accidentally commit it, regenerate the API key immediately
- ✅ The file is local-only and only loaded at runtime

### Step 3: Verify Setup

Run the verification script:

```bash
python -c "
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('.') / '.env')
key = os.getenv('GOOGLE_API_KEY')
if key:
    print(f'✓ API key loaded successfully')
    print(f'  Key length: {len(key)} characters')
    print(f'  First 10 chars: {key[:10]}...')
else:
    print('✗ API key not found in .env')
"
```

### Step 4: Run the Pipeline

```bash
python main_advanced.py
```

The system will automatically:
1. Load your API key from `.env`
2. Initialize Gemini components
3. Process PDFs with advanced AI capabilities
4. Fall back to standard mode if API key is missing

## File Structure Reference

```
AI_DDR_Generator/
├── .env                    ← YOUR API KEY (secured, not in git)
├── .env.example           ← Template (safe to share)
├── .gitignore             ← Prevents .env from being committed
├── modules/
│   ├── gemini_schema_extractor.py       (reads from .env)
│   ├── gemini_observation_extractor.py  (reads from .env)
│   └── gemini_conflict_detector.py      (reads from .env)
├── main_advanced.py                     (coordinates Gemini modules)
└── README.md
```

## How the System Protects Your Key

### Environment Loading
```python
from dotenv import load_dotenv
load_dotenv()  # Only loads into memory, NOT logged

api_key = os.getenv("GOOGLE_API_KEY")  # Retrieved at runtime
genai.configure(api_key=api_key)       # Used immediately
```

### Git Protection
```
.gitignore contains:
.env
.env.local
.env.*.local
```

This ensures `.env` is never accidentally committed.

### Runtime Safety
- API key is never printed to console
- Never logged to files
- Only passed directly to Gemini SDK
- Never appears in error messages

## If Your Key is Compromised

1. **Immediately delete the API key** from Google AI Studio
2. **Create a new API key**
3. **Update your `.env` file** with the new key
4. **Run the system** - it will use the new key

## Troubleshooting

### "GOOGLE_API_KEY not found"
- ✓ Create `.env` file in `AI_DDR_Generator/` directory
- ✓ Add `GOOGLE_API_KEY=your_key`
- ✓ Restart your terminal/Python

### "API key is invalid"
- ✓ Copy the exact key from Google AI Studio (no extra spaces)
- ✓ Check the key hasn't expired
- ✓ Try regenerating a new key

### "Module 'google.generativeai' not found"
- ✓ Install: `pip install google-generativeai`

### Gemini falling back to JSON mode
- ✓ Check that `GOOGLE_API_KEY` is in `.env`
- ✓ Verify the key is valid
- ✓ The system gracefully falls back to JSON processing if Gemini fails

## Alternative: Manual Key Management

If you prefer not to use `.env`:

```python
# In your script:
import os
os.environ["GOOGLE_API_KEY"] = your_key_here
```

But `.env` is recommended because:
- Cleaner code
- Easy to switch environments
- Standard practice
- Cannot accidentally commit the key

## Security Best Practices

1. **Never hardcode API keys** in source code
2. **Use `.env` for local development**
3. **Use environment variables in production** (set via CI/CD platform)
4. **Rotate keys regularly** (monthly recommended)
5. **Monitor API usage** at [Google Cloud Console](https://console.cloud.google.com/)
6. **Set API quotas** to limit unexpected charges

## Questions?

The system uses the battle-tested `python-dotenv` package:
- [python-dotenv Documentation](https://python-dotenv.readthedocs.io/)
- [Google Generative AI SDK](https://github.com/google/generative-ai-python)

Your API key is secure! 🔐
