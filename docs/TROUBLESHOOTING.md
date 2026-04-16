# Troubleshooting Guide

## Common Issues & Solutions

### 🔴 API & Configuration Issues

#### Problem: "ModuleNotFoundError: google.generativeai"
**Symptoms:** Import error when running script
**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import google.generativeai; print('✓ OK')"
```

#### Problem: "GEMINI_API_KEY not found"
**Symptoms:** Error saying API key missing
**Solution:**
1. Create `.env` file in root directory
2. Add line: `GEMINI_API_KEY=your_actual_key`
3. Get key from: https://ai.google.dev/
4. Restart Python process

#### Problem: "Invalid API key"
**Symptoms:** "401 Unauthorized" error
**Solution:**
1. Get fresh API key from Google AI Studio
2. Verify no extra spaces in `.env`
3. Update `.env` file
4. Test with: `python scripts/test_gemini.py`

#### Problem: "API quota exceeded"
**Symptoms:** Gemini API calls fail (blue error)
**Solution:** ✅ **NO ACTION NEEDED**
- System automatically uses template-based fallback
- Report still generated successfully
- Same professional output quality

### 🔧 Data & File Issues

#### Problem: "PDF file not found"
**Symptoms:** "FileNotFoundError" when extracting
**Solution:**
1. Place PDFs in `data/` folder
2. Name them: `sample_inspection.pdf`, `sample_thermal.pdf`
3. Verify files exist: `ls data/`
4. Run STEP 5: `python scripts/step5_extract_observations.py`

#### Problem: "outputs folder doesn't exist"
**Symptoms:** "No such directory" error
**Solution:**
```bash
# Create outputs folder
mkdir -p outputs

# Or run main.py (creates automatically)
python main.py
```

#### Problem: "Permission denied" on outputs
**Symptoms:** Can't write to outputs folder
**Solution:**
```bash
# Fix permissions
chmod -R 755 outputs/

# Or delete and recreate
rm -rf outputs/
mkdir outputs/
```

### 📊 Data Processing Issues

#### Problem: "No observations extracted"
**Symptoms:** `observations.json` is empty or has 0 items
**Possible Causes:**
1. PDF has no text (scanned image only)
2. PDF format not recognized
3. Text extraction failed

**Solutions:**
- Ensure PDFs have extractable text
- Try with sample PDFs first
- Check STEP 5 output: `cat outputs/observations.json`

#### Problem: "Merge match rate is 0%"
**Symptoms:** No observations matched in STEP 6
**Causes:**
1. Area names too different
2. Fuzzy match threshold too high

**Solutions:**
1. Lower threshold in `utils/merger.py`:
   ```python
   MATCH_THRESHOLD = 60  # Was 70
   ```
2. Verify observation format
3. Check similarity scores in output

#### Problem: "All observations are MEDIUM severity"
**Symptoms:** Severity scoring not working correctly
**Causes:**
1. Keywords not matching inspection_issue field
2. thermal_flag not being set

**Solutions:**
1. Verify `merged_observations.json` has correct fields
2. Check keywords in `utils/severity.py`
3. Run STEP 7 debug mode

### 🖨️ Report Generation Issues

#### Problem: "Report file is empty"
**Symptoms:** `ddr_report.txt` exists but has no content
**Solutions:**
1. Verify `severity_scored.json` has data
2. Run STEP 8 again: `python scripts/step8_generate_ddr.py`
3. Check for errors in console

#### Problem: "JSON parsing error"
**Symptoms:** JSON output files are invalid
**Causes:**
1. Gemini returned invalid JSON
2. Fallback template failed

**Solutions:**
1. Verify with: `python -m json.tool outputs/ddr_report.json`
2. Regenerate report
3. Check `severity_scored.json` is valid JSON

### 🔄 Pipeline Issues

#### Problem: "Main script hangs"
**Symptoms:** `python main.py` never completes
**Possible Causes:**
1. Gemini API call timeout
2. Large PDF processing
3. Network issue

**Solutions:**
1. Increase timeout in config
2. Break into steps (test individually)
3. Check internet connection
4. Try smaller PDF first

#### Problem: "Partial pipeline failure"
**Symptoms:** Some steps work, others fail
**Solutions:**
1. Test individual steps:
   ```bash
   python scripts/step5_extract_observations.py  # Test STEP 5
   python scripts/step6_merge_and_conflict.py   # Test STEP 6
   python scripts/step7_severity_scoring.py     # Test STEP 7
   python scripts/step8_generate_ddr.py         # Test STEP 8
   ```
2. Fix failing step
3. Run complete pipeline again

### 🐍 Python Issues

#### Problem: "Python version too old"
**Symptoms:** "SyntaxError" or module compatibility errors
**Solution:**
```bash
# Check Python version
python --version

# Need Python 3.11+
# Install from: https://www.python.org/
```

#### Problem: "Virtual environment conflicts"
**Symptoms:** Import errors despite installing packages
**Solutions:**
```bash
# Create fresh virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Problem: "pip install fails"
**Symptoms:** "Could not find a version that satisfies"
**Solutions:**
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Try installing packages one-by-one:
   ```bash
   pip install google-generativeai
   pip install pymupdf
   pip install rapidfuzz
   pip install python-dotenv
   ```
3. Check internet connection

### 💾 Output/Storage Issues

#### Problem: "Disk space error"
**Symptoms:** "No space left on device" error
**Solution:**
```bash
# Check disk space
df -h

# Clean up old reports
rm outputs/ddr_*.txt
rm outputs/ddr_*.json
```

#### Problem: "File copy/move failed"
**Symptoms:** Can't copy PDFs or outputs
**Solution:**
```bash
# Ensure source file exists
ls data/sample_inspection.pdf

# Check permissions
chmod 644 data/sample_inspection.pdf

# Try again
```

---

## 🆘 Still Having Issues?

### Debugging Steps

1. **Check Error Message**
   - Read full error traceback
   - Note line number and function name

2. **Test API Connection**
   ```bash
   python scripts/test_gemini.py
   ```

3. **Test Individual Steps**
   ```bash
   # Test each step separately
   python scripts/step5_extract_observations.py
   python scripts/step6_merge_and_conflict.py
   python scripts/step7_severity_scoring.py
   python scripts/step8_generate_ddr.py
   ```

4. **Check Intermediate Files**
   ```bash
   # Verify output files exist and have content
   ls -la outputs/
   wc -l outputs/*.json
   ```

5. **Review Configuration**
   ```bash
   # Verify .env file
   cat .env
   # Should show: GEMINI_API_KEY=...
   ```

### Enable Debug Mode

Edit script and add:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Get Detailed Error Info

```bash
# Run with verbose output
python -u main.py 2>&1 | tee debug.log

# Review log file
cat debug.log
```

---

## 📞 Support Resources

| Resource | URL/Location |
|----------|---|
| Gemini API Docs | https://ai.google.dev/ |
| Python Docs | https://docs.python.org/ |
| Project Docs | `docs/` folder |
| Example Code | `scripts/` folder |

---

## ✅ Quick Health Check

Run this to verify everything is working:

```bash
#!/bin/bash

echo "🔍 System Health Check"
echo "========================"

# Check Python
echo -n "Python 3.11+: "
python --version

# Check dependencies
echo -n "google-generativeai: "
python -c "import google.generativeai; print('✓')" || echo "✗"

echo -n "pymupdf: "
python -c "import fitz; print('✓')" || echo "✗"

echo -n "rapidfuzz: "
python -c "import rapidfuzz; print('✓')" || echo "✗"

# Check files
echo -n ".env file: "
[ -f .env ] && echo "✓" || echo "✗"

echo -n "data/ folder: "
[ -d data ] && echo "✓" || echo "✗"

echo -n "outputs/ folder: "
[ -d outputs ] && echo "✓" || echo "✗"

# Test API
echo -n "Gemini API: "
python scripts/test_gemini.py 2>&1 | grep -q "✓" && echo "✓" || echo "✗"

echo "========================"
echo "✅ All OK" || echo "❌ Some issues found - see above"
```

---

**Still stuck? Check the main documentation files in `docs/` folder.**

