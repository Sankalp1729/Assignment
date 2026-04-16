# FastAPI Backend for AI DDR Generator

High-performance FastAPI backend running on Render with Gemini AI integration.

## Features

- ⚡ FastAPI - Fast, async Python web framework
- 🚀 Production-ready with Uvicorn
- 🔄 CORS enabled for frontend communication
- 📄 Document processing (PDF, JSON)
- 🤖 Gemini AI integration
- 📊 Complete AI DDR pipeline
- 🔒 Secure environment variable handling

## Tech Stack

- **Framework:** FastAPI 0.104+
- **Server:** Uvicorn (ASGI)
- **AI:** Google Gemini API
- **Document Processing:** PyMuPDF, pdf2image, pdfplumber
- **PDF Generation:** ReportLab
- **Validation:** Pydantic

## Installation

### Prerequisites

- Python 3.9+
- Virtual environment (venv, conda, etc.)
- Google Gemini API key

### Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Add your Gemini API key
# GEMINI_API_KEY=your_key_here
```

## Development

```bash
# Start development server (with auto-reload)
python api.py

# Or use uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# API docs will be at http://localhost:8000/docs
```

## API Endpoints

### Health Check
```
GET /health
```

### Extract Observations
```
POST /api/extract
- file: Upload PDF or JSON
- document_type: inspection_report | thermal_report
```

### Run Full Pipeline
```
POST /api/pipeline
- document_type: inspection_report | thermal_report
```

### Get Document Status
```
GET /api/status/{document_id}
```

## Deployment

### Deploy to Render

```bash
# 1. Push code to GitHub

# 2. Create new Web Service on Render
# - Connect GitHub repository
# - Runtime: Python
# - Build Command: pip install -r requirements.txt
# - Start Command: uvicorn api:app --host 0.0.0.0 --port 8000

# 3. Set Environment Variables in Render
# - GEMINI_API_KEY
# - FRONTEND_URL (for CORS)

# 4. Deploy!
```

### Using render.yaml

```bash
# Deploy with configuration file
# Configuration is in render.yaml

# Push to GitHub and Render will auto-deploy
```

## Project Structure

```
backend/
├── api.py                     # FastAPI application
├── main.py                    # Original CLI entry point
├── modules/                   # Core AI pipeline
│   ├── extraction.py
│   ├── pipeline.py
│   ├── report_generator.py
│   ├── reasoning.py
│   └── data_models.py
├── utils/                     # Utilities
│   ├── pdf_extractor.py
│   ├── image_extractor.py
│   └── gemini_client.py
├── scripts/                   # Deployment scripts
├── config/                    # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

### CORS Configuration

Edit `api.py` to add your frontend URLs:

```python
origins = [
    "http://localhost:3000",
    "https://your-frontend.vercel.app",
]
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=.

# Specific test file
pytest tests/test_api.py
```

## Performance Optimization

### For Production

1. **Use Gunicorn with multiple workers:**
```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Enable caching:**
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

3. **Enable async operations:**
```python
# All I/O operations should be async
```

## Monitoring & Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Troubleshooting

### CORS Errors
- Check frontend URL in CORS configuration
- Verify `FRONTEND_URL` environment variable

### PDF Processing Issues
- Ensure `pymupdf` is installed correctly
- For OCR, install system Tesseract

### Gemini API Errors
- Verify `GEMINI_API_KEY` is set
- Check API quota limits
- Ensure API is enabled in Google Cloud

### Memory Issues
- Increase Render plan resources
- Implement streaming for large files
- Use background tasks for long operations

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test: `pytest`
3. Commit: `git commit -am "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## License

MIT License

## Support

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- GitHub Issues: Your repo URL
