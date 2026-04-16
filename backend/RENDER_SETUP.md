# 🚀 Render Deployment Setup Guide

## Quick Setup for Backend API

This guide walks you through deploying the AI DDR Backend to Render.

---

## Step 1: Create Render Service

1. Go to [render.com](https://render.com) and sign up / log in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Sankalp1729/Assignment`

---

## Step 2: Configure Web Service

### Basic Settings

| Field | Value |
|-------|-------|
| **Name** | `ai-ddr-backend` |
| **Environment** | `Python 3` |
| **Region** | `US (Oregon)` |
| **Plan** | `Free` (or `Starter` for production) |

### Important: Root Directory (Monorepo Support)

⚠️ **This is crucial for monorepo**: 

```
Root Directory: backend
```

**Why?** Since we have a monorepo with `backend/` and `frontend/` folders, you must set the root directory to `backend` so Render knows where the Python app is located.

---

## Step 3: Build & Start Commands

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
bash start.sh
```

**Or directly:**
```bash
uvicorn api:app --host 0.0.0.0 --port 10000 --workers 4
```

---

## Step 4: Environment Variables

Set these in Render Dashboard under **"Environment"**:

| Key | Value | Notes |
|-----|-------|-------|
| `GEMINI_API_KEY` | `your-key-here` | Get from [Google AI Studio](https://aistudio.google.com) |
| `ENVIRONMENT` | `production` | Set to production mode |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` | Your Vercel frontend URL |
| `PORT` | `10000` | (Optional - Render uses this by default) |

### To Set Environment Variables:

1. In Render dashboard, go to your service
2. Click **"Environment"** tab
3. Add each variable as a Key-Value pair
4. Mark `GEMINI_API_KEY` as **"Secret"** for security

---

## Step 5: Health Check Configuration

The API includes a `/health` endpoint for monitoring:

```
Health Check Path: /health
Check Interval: 30 seconds
Timeout: 5 seconds
```

Render automatically configures this.

---

## Step 6: Disk Configuration

The backend creates report files. Configure persistent disk:

### Disk Settings:
- **Name**: `outputs`
- **Mount Path**: `/app/outputs`
- **Size**: `1 GB` (adjust based on needs)

This ensures generated reports persist across deployments.

---

## Step 7: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone the repository
   - Install dependencies from `requirements.txt`
   - Run `bash start.sh` to start the API
   - Monitor with health checks

3. Wait for deployment (usually 2-3 minutes)
4. Copy your service URL: `https://ai-ddr-backend-xxxxx.onrender.com`

---

## Step 8: Verify Deployment

Test your deployed API:

```bash
# Health check
curl https://ai-ddr-backend-xxxxx.onrender.com/health

# Should return:
# {"status": "ok"}
```

---

## API Endpoints

Once deployed, access these endpoints:

### 1. Health Check
```
GET /health
```

### 2. Generate DDR
```
POST /api/v1/generate-ddr
```

**Request** (multipart/form-data):
- `inspection_pdf`: File (PDF)
- `thermal_pdf`: File (PDF)

**Response**:
```json
{
  "status": "success",
  "report_id": "unique-id-123",
  "document_id": "DOC-123",
  "observations": [...],
  "ddr": "HTML content"
}
```

### 3. Get Report
```
GET /api/v1/reports/{report_id}
```

---

## Troubleshooting

### Issue: "Build failed"
- ✅ Check `requirements.txt` exists in `backend/` folder
- ✅ Verify `Root Directory` is set to `backend`
- ✅ Check all Python packages are pinned to compatible versions

### Issue: "Application failed to start"
- ✅ Verify `GEMINI_API_KEY` is set in Environment
- ✅ Check `start.sh` file exists and is executable
- ✅ Run locally first: `bash backend/start.sh`

### Issue: "504 Gateway Timeout"
- ✅ The API might be processing large PDFs (takes 30-60 seconds)
- ✅ Increase Render's timeout in Settings
- ✅ Consider upgrading from Free to Starter plan

### Issue: "Reports not persisting"
- ✅ Verify disk is mounted at `/app/outputs`
- ✅ Check disk has enough space (1 GB minimum)
- ✅ Ensure `outputs/` folder exists locally

---

## Production Recommendations

### For Production Deployment:

1. **Upgrade Plan**
   - Free → Starter ($12/month)
   - Includes better uptime and performance

2. **Enable Auto-Deploy**
   - ✅ Already configured in `render.yaml`
   - API redeploys on every `git push`

3. **Monitor Logs**
   - Render Dashboard → Logs tab
   - Check for errors or performance issues

4. **Increase Resources**
   - Upgrade to Starter/Standard for more CPU/RAM
   - Faster PDF processing

5. **Add Custom Domain** (Optional)
   - Render → Settings → Custom Domain
   - Map your domain to the service

---

## Monorepo Structure

Your Render service is set up for a **monorepo** with this structure:

```
Assignment/
├── backend/              ← Root Directory = "backend"
│   ├── api.py           ← Main app
│   ├── requirements.txt  ← Dependencies
│   ├── start.sh         ← Start script
│   ├── utils/
│   ├── modules/
│   └── ...
├── frontend/            ← Deployed separately to Vercel
│   ├── package.json
│   ├── src/
│   └── ...
└── README.md
```

Render only deploys the `backend/` folder, while `frontend/` is deployed to Vercel.

---

## Quick Reference

| Setting | Value |
|---------|-------|
| **Service Name** | ai-ddr-backend |
| **Runtime** | Python 3.9 |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `bash start.sh` |
| **Region** | US (Oregon) |
| **Plan** | Free / Starter |
| **Health Endpoint** | `/health` |
| **Output Disk** | `/app/outputs` (1 GB) |

---

## Next Steps

1. ✅ Deploy to Render (this guide)
2. ⬜ Deploy Frontend to Vercel (`frontend/` folder)
3. ⬜ Link Frontend ↔ Backend URLs
4. ⬜ Test full application
5. ⬜ Monitor logs and performance

---

**Need Help?**

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Email Support: support@render.com

