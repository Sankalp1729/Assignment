# ▶️ START HERE — Production Deployment & Go-Live Guide

**Welcome to the AI DDR Generator production deployment guide.**

If you're reading this, you're ready to deploy the system to production.

---

## 🎯 What You Need (5 minutes)

Before you start, make sure you have:

- [ ] **Python 3.11+** installed
- [ ] **Git** installed (optional, but recommended)
- [ ] **2GB+ free disk space**
- [ ] **Internet connection** (for API calls)
- [ ] **Google Gemini API key** (from [AI Studio](https://aistudio.google.com/app/apikeys))
- [ ] **Administrator access** (Windows Task Scheduler needs this)

**No API key yet?**
1. Go to https://aistudio.google.com/app/apikeys
2. Click "Get API Key"
3. Copy the key (starts with `sk_...`)
4. You'll paste this during setup

---

## 📍 Where You Are

Your project structure looks like:
```
AI_DDR_Generator/
├── EVERYTHING READY FOR DEPLOYMENT ✅
├── Choose your deployment method below
└── Follow the steps for your platform
```

---

## 🚀 Choose Your Deployment Path

### Path 1: Windows (Simplest) — 5 minutes ✨

**Visual Step-by-Step:**

```
1. Open Command Prompt
   ↓
2. Run: deployment.bat
   ↓
3. Automatic setup begins
   ↓
4. Enter your API key when prompted
   ↓
5. Done! System ready
```

**Commands:**
```batch
REM Open Command Prompt and run:
deployment.bat

REM Follow all prompts
```

**Next:**
```batch
python main.py
```

---

### Path 2: Linux/macOS — 5 minutes

**Visual Step-by-Step:**

```
1. Open Terminal
   ↓
2. Make script executable
   ↓
3. Run deployment.sh
   ↓
4. Activate virtual environment
   ↓
5. Done! System ready
```

**Commands:**
```bash
# Navigate to project
cd AI_DDR_Generator

# Make executable
chmod +x deployment.sh

# Run setup
./deployment.sh

# Activate environment
source venv/bin/activate

# Run system
python main.py
```

---

### Path 3: Docker (Most Portable) — 3 minutes

**Visual Step-by-Step:**

```
1. Open Terminal
   ↓
2. Build Docker image
   ↓
3. Start with docker-compose
   ↓
4. Check outputs
   ↓
5. Done! Portable & scalable
```

**Commands:**
```bash
# Build image
docker build -t ai-ddr-generator .

# Start container
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop when done
docker-compose down
```

---

### Path 4: Windows PowerShell — 5 minutes

**Commands:**
```powershell
# Set execution policy (one time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run deployment
. .\deployment.ps1 -Action setup

# Deploy
. .\deployment.ps1 -Action deploy

# Start
. .\deployment.ps1 -Action start
```

---

## ✅ Verify Deployment (2 minutes)

After running your chosen deployment method:

### Quick Test
```bash
# Test the system
python deployment_checklist.py

# Should see: ✅ ALL CHECKS PASSED
```

### Full Pipeline Test
```bash
# Run complete pipeline
python main.py

# Check for outputs
ls outputs/ddr_report.*  # or dir outputs on Windows
```

### View Results
```bash
# Display the generated report
cat outputs/ddr_report.txt      # macOS/Linux
type outputs\ddr_report.txt     # Windows
```

---

## 🔄 Set Up Automatic Scheduling

The system can run daily automatically.

### Windows
```batch
REM Run as Administrator
setup_scheduled_task.bat

REM Task will run daily at 2:00 AM
REM Manage in: Task Scheduler GUI
```

### Linux/macOS
```bash
# Set up systemd service
sudo cp ai-ddr-generator.service /etc/systemd/system/
sudo cp ai-ddr-generator.timer /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ai-ddr-generator.timer
sudo systemctl start ai-ddr-generator.timer

# Verify it's working
systemctl status ai-ddr-generator.timer

# View logs
journalctl -u ai-ddr-generator -f
```

---

## 📊 Monitor Your Deployment

### View Logs
```bash
# Real-time logs
tail -f app.log           # macOS/Linux
type app.log              # Windows (one-time view)

# Or open app.log in your editor
```

### Check Output Files
```bash
# Generated files
outputs/ddr_report.txt    # Human-readable report
outputs/ddr_report.json   # Machine-readable data
```

### Verify Health
```bash
python deployment_checklist.py

# Should show: ✅ All systems operational
```

---

## 🔧 Configuration Options

### Edit Settings
Your settings are in: `.env`

**Important Settings:**
```bash
GEMINI_API_KEY=your_key_here    # Required
ENVIRONMENT=production           # Optional
LOG_LEVEL=INFO                   # Optional
```

To change settings:
```bash
# Edit .env file
nano .env          # macOS/Linux
notepad .env       # Windows
code .env          # VS Code (any platform)
```

Save the file and restart the application.

See [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md) for all options.

---

## ⚠️ Troubleshooting Quick Fixes

### "Python not found"
```bash
# Windows: Add Python to PATH
# (Or reinstall Python, check "Add to PATH")

# macOS/Linux: Install Python
brew install python3  # macOS
apt install python3   # Linux
```

### "API key invalid"
```bash
# Go to AI Studio: https://aistudio.google.com/app/apikeys
# Generate new key
# Edit .env and paste new key
# Test: python scripts/test_gemini.py
```

### "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -r requirements.txt

# If that fails, try upgrade
pip install --upgrade -r requirements.txt
```

### "Port already in use" (Docker)
```bash
# Find what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Stop it:
docker ps
docker stop <container_id>
```

**Still stuck?** → See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📋 Pre-Production Checklist

Before your first production run:

- [ ] All 4 test scripts pass (step5, step6, step7, step8)
- [ ] `python main.py` generates reports successfully
- [ ] `app.log` shows no errors
- [ ] `.env` file has valid API key
- [ ] Output files are readable and well-formatted
- [ ] You can view the report: `ddr_report.txt`

---

## 🎉 Deployment Complete!

Your system is now ready for production.

### What Happens Next

1. **Daily Runs**: System runs automatically (if scheduled)
2. **Reports Generated**: New reports in `outputs/` daily
3. **Logs Recorded**: Check `app.log` for any issues
4. **Outputs Saved**: Both `.txt` and `.json` formats

### Your New Workflow

```
Every Day (Automated):
├─ 2:00 AM: System runs automatically
├─ Processes PDFs in data/
├─ Generates ddr_report.txt and ddr_report.json
├─ Stores in outputs/
└─ Logs activity in app.log
```

### Manual Runs (Anytime)

```bash
# Quick test
python main.py

# Production mode with logging
python prod_main.py
```

---

## 📚 Documentation Index

| Need | Location |
|------|----------|
| **Quick start** | This file (START_HERE_PRODUCTION.md) |
| **Full deployment** | [DEPLOYMENT.md](DEPLOYMENT.md) |
| **Verify setup** | [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) |
| **Configuration** | [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md) |
| **Problem solving** | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| **API setup** | [docs/API_SETUP.md](docs/API_SETUP.md) |
| **Overall summary** | [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) |

---

## 🆘 Need Help?

### Step 1: Check Logs
```bash
cat app.log
```

### Step 2: Verify Setup
```bash
python deployment_checklist.py
```

### Step 3: Test Manually
```bash
python scripts/step5_extract_observations.py
python scripts/step6_merge_and_conflict.py
python scripts/step7_severity_scoring.py
python scripts/step8_generate_ddr.py
```

### Step 4: Check Documentation
- See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🏆 Success Metrics

You'll know deployment is successful when:

✅ **Setup completes without errors**
- No error messages during `deployment.bat/sh`
- Virtual environment created and activated
- All dependencies installed

✅ **System runs successfully**
- `python main.py` completes without errors
- Output files appear in `outputs/`
- `app.log` shows progress messages

✅ **Output looks correct**
- `ddr_report.txt` is readable
- `ddr_report.json` is valid JSON
- Reports contain expected content

✅ **Automation works**
- Scheduled tasks appear in Task Scheduler (Windows)
- systemd service status is "active" (Linux)
- Reports regenerate on schedule

---

## 🎯 Next Steps

**Right Now:**
1. Choose your deployment path above
2. Follow the commands for your OS
3. Run `python main.py` to test
4. Check output files

**After Deployment:**
1. Set up automatic scheduling
2. Monitor `app.log` for errors
3. Share outputs with your team
4. Keep API key secure

**Long Term:**
1. Monitor API usage
2. Update dependencies monthly
3. Archive old reports
4. Rotate API keys as needed

---

## ✨ You're All Set!

The AI DDR Generator is now deployed and ready for production use.

**Last Step:**
Run this command to verify everything is working:

```bash
python deployment_checklist.py
```

Watch for: ✅ ALL CHECKS PASSED

**Then deploy:**
```bash
python main.py
```

**Enjoy your new automated property inspection reports!** 🎉

---

**Questions?** Check the [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) or [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

**System Status: ✅ PRODUCTION READY**
