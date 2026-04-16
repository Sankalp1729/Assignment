# Deployment Checklist — Final Verification

Complete this checklist before going into production.

---

## ✅ Pre-Deployment (Environment)

- [ ] Python 3.11+ installed
- [ ] Git installed (for version control)
- [ ] Internet connection available (for API)
- [ ] 2GB+ free disk space
- [ ] Sufficient RAM (1GB minimum, 4GB recommended)
- [ ] File permissions correct (755 for scripts)
- [ ] Network access to `api.ai.google.dev`

---

## ✅ Initial Setup

- [ ] `.env` file created with valid GEMINI_API_KEY
- [ ] `.env` added to `.gitignore`
- [ ] `requirements.txt` up-to-date
- [ ] Virtual environment created: `venv/`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] All directories exist: `data/`, `outputs/`, `config/`

---

## ✅ Configuration Validation

- [ ] GEMINI_API_KEY set correctly
- [ ] ENVIRONMENT variable set (production/staging/development)
- [ ] LOG_LEVEL configured appropriately
- [ ] API_TIMEOUT set (30-60 seconds)
- [ ] BATCH_SIZE appropriate for your system
- [ ] FUZZY_MATCH_THRESHOLD at 70% (recommended)

---

## ✅ Code Validation

- [ ] `python -m py_compile utils/*.py` (all syntax valid)
- [ ] `python deployment_checklist.py` (all checks pass)
- [ ] No import errors: `python -c "import utils"`
- [ ] All STEP modules importable
- [ ] PDF extraction working: `python scripts/test_*.py`

---

## ✅ API Connection

- [ ] API key is valid
- [ ] `python scripts/test_gemini.py` passes
- [ ] API quota available (check AI Studio)
- [ ] Network connectivity confirmed
- [ ] Fallback mode tested (works offline)

---

## ✅ Data & Input

- [ ] Sample PDFs in `data/` folder
- [ ] Test PDF readable: `python scripts/step5_extract_observations.py`
- [ ] Output `observations.json` created
- [ ] JSON structure validates successfully

---

## ✅ Individual Component Tests

- [ ] STEP 5 (Extraction): `python scripts/step5_*.py`
  - [ ] observations.json generated
  - [ ] Valid JSON output
  
- [ ] STEP 6 (Merging): `python scripts/step6_*.py`
  - [ ] merged_observations.json generated
  - [ ] detected_conflicts.json created
  
- [ ] STEP 7 (Severity): `python scripts/step7_*.py`
  - [ ] severity_scored.json generated
  - [ ] All observations scored
  
- [ ] STEP 8 (Report): `python scripts/step8_*.py`
  - [ ] ddr_report.txt generated
  - [ ] ddr_report.json created

---

## ✅ Full Pipeline

- [ ] `python main.py` runs without errors
- [ ] All 4 output files created in `outputs/`
- [ ] No warnings in logs
- [ ] Execution completes in reasonable time (<5 min)
- [ ] Reports are readable and well-formatted

---

## ✅ Production Mode

- [ ] `python prod_main.py` starts successfully
- [ ] Logging configured correctly
- [ ] `app.log` file created with entries
- [ ] Error handling works (test with invalid PDF)
- [ ] Recovery from API timeout works

---

## ✅ Deployment Scripts

- [ ] On Windows:
  - [ ] `deployment.bat` runs without errors
  - [ ] venv activates automatically
  - [ ] Dependencies install successfully
  - [ ] setup.py completes

- [ ] On Linux/macOS:
  - [ ] `deployment.sh` executable: `chmod +x deployment.sh`
  - [ ] `./deployment.sh` runs successfully
  - [ ] venv activates in script
  - [ ] setup.py completes

- [ ] PowerShell (Windows):
  - [ ] `deployment.ps1` executable
  - [ ] `. .\deployment.ps1 setup` works
  - [ ] All functions execute

---

## ✅ Scheduled Execution

**Windows Task Scheduler:**
- [ ] Run `setup_scheduled_task.bat` as Administrator
- [ ] Task created in Task Scheduler
- [ ] Task runs at scheduled time (test manually first)
- [ ] Logs created for each run

**Linux systemd:**
- [ ] Copy `.service` file to `/etc/systemd/system/`
- [ ] Run `systemctl daemon-reload`
- [ ] Enable service: `systemctl enable ai-ddr-generator`
- [ ] Test: `systemctl start ai-ddr-generator`
- [ ] Check: `systemctl status ai-ddr-generator`
- [ ] View logs: `journalctl -u ai-ddr-generator`

**Linux cron (alternative):**
- [ ] `crontab -e` to add scheduled job
- [ ] Entry: `0 2 * * * cd /path/to/app && python prod_main.py >> app.log 2>&1`
- [ ] Test with: `Run-Parts /etc/cron.daily`

---

## ✅ Docker Deployment (if applicable)

- [ ] `Dockerfile` builds successfully: `docker build -t ai-ddr .`
- [ ] `docker-compose.yml` configured correctly
- [ ] Volume mounts correct (`data/`, `outputs/`)
- [ ] Environment variables passed correctly
- [ ] Container runs: `docker-compose up`
- [ ] Output files accessible from host

---

## ✅ Documentation

- [ ] README.md is clear and current
- [ ] DEPLOYMENT.md reviewed and applicable
- [ ] API_SETUP.md has correct key instructions
- [ ] TROUBLESHOOTING.md covers known issues
- [ ] QUICKSTART.md is up-to-date
- [ ] All links in docs work

---

## ✅ Security

- [ ] `.env` not committed to git
- [ ] API key rotation documented
- [ ] Log files don't contain sensitive data
- [ ] File permissions are appropriate (600 for .env)
- [ ] Database credentials (if any) secured
- [ ] No hardcoded credentials in code

---

## ✅ Monitoring & Logging

- [ ] Logs directory writable
- [ ] Log rotation configured (if needed)
- [ ] Log levels appropriate for production
- [ ] Error emails/alerts configured (if applicable)
- [ ] Health check script created
- [ ] Monitoring dashboard set up (if applicable)

---

## ✅ Backup & Disaster Recovery

- [ ] Backup plan documented
- [ ] Outputs backed up regularly
- [ ] Configuration backed up
- [ ] Rollback procedure documented
- [ ] Emergency contact list maintained
- [ ] Downtime procedures documented

---

## ✅ Compliance & Approval

- [ ] Security review completed
- [ ] Code review approved
- [ ] Performance acceptable
- [ ] Cost/quota within limits
- [ ] Operational team trained
- [ ] Rollback plan approved

---

## ✅ Final Checks

- [ ] All previous items checked ✓
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled (if applicable)
- [ ] Team available for support
- [ ] Communication channels open
- [ ] Rollback plan in place

---

## 🚀 Deployment Authorization

- **Department**: _________________
- **Date**: _________________
- **Authorized By**: _________________
- **Environment**: [ ] Development  [ ] Staging  [ ] Production
- **Notes**: _________________

---

## Next Steps After Deployment

1. ✅ Monitor first 24 hours closely
2. ✅ Check logs daily for first week
3. ✅ Review outputs for quality
4. ✅ Track API usage and costs
5. ✅ Gather user feedback
6. ✅ Document any issues
7. ✅ Plan optimizations if needed

---

## Support Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| Primary Admin | | | |
| Backup Admin | | | |
| Manager | | | |
| Vendor Support | Google AI | | support@google.com |

---

## Status

**Ready for Deployment**: ✅ YES / ❌ NO

**Sign-off**: _________________     **Date**: _________________

---

**Deployment Checklist Complete** ✅
