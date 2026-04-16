# Environment Configuration Guide

## Overview

Default environment variables for AI DDR Generator deployment.

## Configuration Methods

### Method 1: .env File (Recommended)
Recommended for local development and single-machine deployment.

```bash
# Copy template
cp .env.example .env

# Edit with your settings
nano .env  # or vi, code, etc.
```

### Method 2: System Environment Variables
For enterprise deployments or containerized environments.

```bash
# Linux/macOS
export GEMINI_API_KEY="your_key_here"
export ENVIRONMENT="production"

# Windows (PowerShell)
$env:GEMINI_API_KEY = "your_key_here"
$env:ENVIRONMENT = "production"

# Windows (Command Prompt)
set GEMINI_API_KEY=your_key_here
```

### Method 3: Docker Environment
Using docker-compose or Docker run with `-e` flags.

```yaml
environment:
  - GEMINI_API_KEY=your_key_here
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO
```

---

## Required Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GEMINI_API_KEY` | String | (required) | Google Gemini API authentication key |

**Get your API key:**
1. Go to [AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Get API Key"
3. Copy the key to `.env`

---

## Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENVIRONMENT` | String | `development` | `production`, `staging`, `development` |
| `LOG_LEVEL` | String | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `PDF_TIMEOUT` | Integer | `60` | PDF extraction timeout (seconds) |
| `API_TIMEOUT` | Integer | `30` | Gemini API timeout (seconds) |
| `API_MAX_RETRIES` | Integer | `3` | API retry attempts on failure |
| `BATCH_SIZE` | Integer | `10` | Observations per batch |
| `FUZZY_MATCH_THRESHOLD` | Integer | `70` | Merge accuracy threshold (%) |
| `ENABLE_GEMINI_FALLBACK` | Boolean | `true` | Enable offline fallback mode |
| `OUTPUT_FORMATS` | String | `txt,json` | Comma-separated: txt, json, html, csv |

---

## Environment Profiles

### Development
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_TIMEOUT=60
API_MAX_RETRIES=5
BATCH_SIZE=5
```

### Staging
```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
API_TIMEOUT=30
API_MAX_RETRIES=3
BATCH_SIZE=10
```

### Production
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
API_TIMEOUT=20
API_MAX_RETRIES=1
BATCH_SIZE=20
ENABLE_GEMINI_FALLBACK=true
```

---

## Configuration File

Create `.env` in project root:

```bash
# === REQUIRED ===
GEMINI_API_KEY=sk_...your_key_here...

# === OPTIONAL ===

# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# Timeouts (seconds)
PDF_TIMEOUT=60
API_TIMEOUT=30

# Resilience
API_MAX_RETRIES=3
ENABLE_GEMINI_FALLBACK=true

# Performance
BATCH_SIZE=10
FUZZY_MATCH_THRESHOLD=70

# Output
OUTPUT_FORMATS=txt,json
```

---

## Security Best Practices

### ✅ DO

- [ ] Store API keys in `.env` (not in code)
- [ ] Add `.env` to `.gitignore`
- [ ] Use environment variables in production
- [ ] Rotate API keys quarterly
- [ ] Use strong, unique keys
- [ ] Restrict key permissions in Google Cloud
- [ ] Monitor API usage regularly

### ❌ DON'T

- [ ] Commit `.env` to version control
- [ ] Share API keys via email or chat
- [ ] Hardcode keys in Python files
- [ ] Store keys in version control
- [ ] Use the same key across environments
- [ ] Log sensitive information

---

## Container Deployment (.env in Docker)

### docker-compose.yml Setup
```yaml
services:
  ai-ddr-generator:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=${ENVIRONMENT}
      - LOG_LEVEL=${LOG_LEVEL}
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
```

### Run with .env
```bash
docker-compose up
```

### Or pass directly
```bash
docker run \
  -e GEMINI_API_KEY="your_key" \
  -e ENVIRONMENT="production" \
  ai-ddr-generator
```

---

## Systemd Service (.service file)

The `.service` file includes:
```ini
EnvironmentFile=/opt/ai-ddr-generator/.env
Environment="LOG_LEVEL=INFO"
```

Place `.env` at: `/opt/ai-ddr-generator/.env`

---

## Validation

Check environment setup:

```bash
# View all settings (masks sensitive data)
python -c "from config.app_config import *; print('Config loaded successfully')"

# Test API connection
python scripts/test_gemini.py

# View active environment
echo $ENVIRONMENT  # or %ENVIRONMENT% on Windows
```

---

## Troubleshooting

### "API key not found"
```bash
# Check .env file exists
cat .env

# Check path
pwd

# Check variable is set
echo $GEMINI_API_KEY
```

### "Invalid API key"
```bash
# Verify key format (should start with "sk_")
# Regenerate from AI Studio
# Check for accidental spaces/newlines in .env
```

### "Timeout errors"
```bash
# Increase timeout
API_TIMEOUT=60

# Check internet connection
ping api.gemini.com  # or appropriate endpoint
```

### "Fallback mode active"
```bash
# This is normal if API quota exceeded
# Check Google AI Studio for usage
# Wait for quota reset or upgrade plan
```

---

## Configuration Override Priority

Higher priority overrides lower:

1. **Runtime Arguments** (highest)
2. **Environment Variables** 
3. **.env File**
4. **config/app_config.py Defaults** (lowest)

---

## Next Steps

1. ✅ Create `.env` file (or use setup.py)
2. ✅ Set `GEMINI_API_KEY`
3. ✅ Verify with `python scripts/test_gemini.py`
4. ✅ Deploy with `python main.py`
5. ✅ Monitor `app.log`

---

**Status: Configuration Guide Complete** ✅
