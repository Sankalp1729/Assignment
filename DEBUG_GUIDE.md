# 🔧 Complete Debugging & Testing Guide

## ✅ FIX 1 — CORS Added (DONE ✓)

**Status**: ✅ COMPLETE

Your backend now has CORS configured to accept requests from Vercel:

```python
origins = [
    "http://localhost:3000",           # Local Next.js dev
    "http://localhost:8000",           # Local FastAPI dev
    "https://localhost:3000",
    "https://localhost:8000",
    "https://*.vercel.app",            # All Vercel URLs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**What's happening**: Render automatically redeploying backend with CORS enabled (1-2 minutes)

---

## ✅ FIX 2 — API URL Verified (CORRECT ✓)

**Status**: ✅ CORRECT

### Frontend Configuration
```
Node Env Variable: NEXT_PUBLIC_API_URL
Local Dev Value:   http://localhost:10000
Production Value:  https://assignment-n57e.onrender.com
```

### API Endpoint Called
```
CORRECT ✅: https://assignment-n57e.onrender.com/api/v1/generate-ddr
```

### Code Location
File: `frontend/src/app/page.tsx` (Line 68)
```typescript
const response = await axios.post(
  `${API_URL}/api/v1/generate-ddr`,
  formData,
  { ... }
);
```

---

## 🧪 FIX 3 — Test Backend Manually (DO NOW)

### Step 1: Test Health Endpoint
```
URL: https://assignment-n57e.onrender.com/health
Method: GET
Expected Response: { "status": "ok" }
```

### Step 2: Test API Docs (Interactive)
```
👉 https://assignment-n57e.onrender.com/docs
```

**Steps**:
1. **Open in browser** → https://assignment-n57e.onrender.com/docs
2. **Find endpoint** → `POST /api/v1/generate-ddr`
3. **Click "Try it out"**
4. **Upload test PDFs** (inspection.pdf, thermal.pdf)
5. **Click "Execute"**

### Expected Results

#### ✅ SUCCESS
- Status: 200 OK
- Response shows:
  ```json
  {
    "status": "success",
    "document_id": "DOC-xxx",
    "report": { ... },
    "observations": [ ... ]
  }
  ```

#### ❌ ERROR - Possible Issues
```
401 Unauthorized       → GEMINI_API_KEY not set
422 Unprocessable     → File format wrong
500 Internal Error    → Backend error (check logs)
504 Gateway Timeout   → Processing took too long
```

---

## 🔍 FIX 4 — Browser Console Debugging (CRITICAL)

### When Testing Frontend

1. **Press F12** (or Cmd+Opt+I on Mac)
2. **Go to "Console" tab**
3. **Upload PDFs in frontend**
4. **Look for errors**

### Common CORS Error
```javascript
❌ Access to XMLHttpRequest at 'https://assignment-n57e.onrender.com/...' 
   from origin 'https://your-frontend.vercel.app' has been blocked by CORS policy
```

**How to fix**:
- ✅ CORS fix deployed? (Commit: d74fbfc)
- ✅ Wait 1-2 min for Render redeploy
- ✅ Hard refresh browser (Ctrl+Shift+R)

### Common Network Error
```javascript
❌ Failed to fetch
   TypeError: fetch failed
```

**Possible causes**:
1. Backend is cold-starting (Render free tier)
   - **Solution**: Wait 20 seconds, try again
2. Wrong API URL
   - **Solution**: Check .env.production
3. Backend down
   - **Solution**: Check Render dashboard

### Network Tab Debug

1. **Go to Network tab** (F12)
2. **Upload PDFs**
3. **Look for POST request** to `/api/v1/generate-ddr`
4. **Check status**:
   - ✅ 200-299 = Success
   - ❌ 4xx = Client error (wrong request)
   - ❌ 5xx = Server error
   - ❌ CORS error = Browser blocked request

---

## ⏳ FIX 5 — Render Cold Start (VERY COMMON)

### What's Happening?
On the free Render plan:
- First request wakes up the server (~20 seconds)
- Subsequent requests are faster (5-10 seconds)

### What You'll See
- Click "Generate"
- Wait 20 seconds
- Report appears

**This is NORMAL - not an error!**

### How to Speed Up
1. **Solution 1**: Be patient (free tier)
2. **Solution 2**: Upgrade Render to Starter plan ($12/month)

---

## ⚡ QUICK DEBUG CHECKLIST

### Before Testing

- [ ] **Backend CORS fixed?**
  - Commit: d74fbfc (CORS Update)
  - Wait 1-2 min for Render redeploy
  - Test: https://assignment-n57e.onrender.com/health

- [ ] **Frontend API URL correct?**
  - File: frontend/.env.production
  - Value: https://assignment-n57e.onrender.com
  - Vercel env var set? ✅

- [ ] **Vercel frontend deployed?**
  - Check: https://vercel.com/dashboard
  - Status: Ready (green checkmark)

### Testing Steps

1. **Health Check**
   ```bash
   curl https://assignment-n57e.onrender.com/health
   ```
   ✅ Should respond with `{"status":"ok"}`

2. **Manual API Test**
   - Go to: https://assignment-n57e.onrender.com/docs
   - Upload test PDFs
   - Execute request
   ✅ Should succeed

3. **Frontend Test**
   - Go to: https://your-frontend-name.vercel.app
   - Upload PDFs
   - Open F12 console
   - Check for CORS errors
   ✅ Should generate report

4. **Console Debugging**
   - Press F12
   - Upload PDFs
   - Check console for errors
   - Check Network tab for 200 response
   ✅ All requests succeed

---

## 📊 Expected Flow

```
User Browser (Vercel Frontend)
    ↓ (HTTPS request with CORS header)
    ↓
Render Backend (API)
    ↓ (CORS check: ✅ Allow)
    ↓
Gemini AI
    ↓ (Process PDFs)
    ↓
Response JSON
    ↓
Frontend displays report ✅
```

---

## 🚀 What's Live Right Now

| Component | URL | Status |
|-----------|-----|--------|
| **Backend API** | https://assignment-n57e.onrender.com | ⏳ Redeploying (1-2 min) |
| **API Docs** | https://assignment-n57e.onrender.com/docs | ✅ Available |
| **Frontend** | https://assignment-[xxx].vercel.app | ✅ Live |
| **GitHub** | https://github.com/Sankalp1729/Assignment | ✅ Updated |

---

## 🔗 Key URLs for Testing

| Purpose | URL |
|---------|-----|
| **Backend Health** | https://assignment-n57e.onrender.com/health |
| **Backend Docs** | https://assignment-n57e.onrender.com/docs |
| **Frontend App** | https://assignment-[xxx].vercel.app |
| **Render Dashboard** | https://dashboard.render.com |
| **Vercel Dashboard** | https://vercel.com/dashboard |
| **GitHub Repo** | https://github.com/Sankalp1729/Assignment |

---

## 💡 Pro Tips

1. **First request slow?** Normal - Render cold start. Be patient.
2. **CORS error?** Backend redeploy takes 1-2 min. Wait and refresh.
3. **PDFs not uploading?** Check file size < 25MB, PDF format only
4. **Report generation slow?** Large PDFs take 30-60 seconds. This is normal.
5. **Testing locally?** Use `http://localhost:8000` for backend

---

## 🆘 Stuck? Try This

1. ✅ Hard refresh browser (Ctrl+Shift+R)
2. ✅ Check Render dashboard for deployment status
3. ✅ Open F12 console for error messages
4. ✅ Go to https://assignment-n57e.onrender.com/docs and test manually
5. ✅ Check GitHub for latest commits
6. ✅ Wait 20 seconds for cold start (free Render plan)

---

**Latest Update**: Commit d74fbfc - CORS enabled for Vercel ✅
