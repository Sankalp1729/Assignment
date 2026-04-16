# API Setup — Gemini Configuration Guide

## 🔑 Getting Your API Key

### Step 1: Visit Google AI Studio
- Go to: https://ai.google.dev/
- Click "Get API Key"
- Choose your Google account

### Step 2: Create Project
- Google will create a default project
- Your API key is automatically generated

### Step 3: Copy API Key
- Copy the key from the dashboard
- Keep it private and secure

## 🔧 Configure .env File

### Method 1: Automatic (If .env template exists)
```bash
cp .env.example .env
# Edit .env and paste your API key
```

### Method 2: Manual
```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_actual_key_here
EOF
```

## ✅ Verify Setup

```bash
# Test API connection
python scripts/test_gemini.py

# Expected output:
# ✓ Gemini API connection successful
```

## 🚨 Troubleshooting

### Issue: "API key not found"
**Solution:**
1. Verify `.env` file exists in root directory
2. Check `GEMINI_API_KEY=` has correct key (no spaces)
3. Restart Python process

### Issue: "API quota exceeded"
**Solution:**ystem automatically falls back to template-based generation
- No interruption to pipeline
- Same professional output quality
- No action needed

### Issue: "Invalid API key"
**Solution:**
1. Check key is copied completely
2. Verify no extra spaces or quotes
3. Get new key from Google AI Studio
4. Update `.env` file

## 📋 Requirements

- Google account
- Internet connection
- Free Gemini API access (generous limits)
- Python 3.11+

## 🔐 Security Best Practices

✅ **DO:**
- Store API key in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables
- Rotate keys periodically

❌ **DON'T:**
- Commit `.env` to git
- Hardcode API key in code
- Share API key
- Use in client-side JavaScript

## 📖 More Information

See: [Gemini API Docs](https://ai.google.dev/tutorials)

