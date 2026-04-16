"""Configuration for AI-Based DDR Generator"""

# PDF Extraction Configuration
PDF_CONFIG = {
    "dpi": 300,
    "extract_images": True,
    "image_quality": "high",
    "supported_formats": [".pdf", ".pdf.json"],
}

# Image Extraction Configuration
IMAGE_CONFIG = {
    "output_dir": "./images",
    "thumbnail_size": (150, 150),
    "supported_formats": [".png", ".jpg", ".jpeg", ".tiff"],
}

# LLM Configuration (for future enhancement)
LLM_CONFIG = {
    "model": "gpt-4-turbo",
    "temperature": 0.3,  # Low for factual extraction
    "max_tokens": 2000,
    "api_key": "YOUR_OPENAI_KEY_HERE",  # Use env variables in production
}

# Data Validation
SEVERITY_LEVELS = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
    "NOT_AVAILABLE": None,
}

# Output Configuration
OUTPUT_CONFIG = {
    "format": "json",  # Can be json, html, pdf
    "include_images": True,
    "include_raw_data": False,  # Include extracted raw data in output
}

# Section templates for DDR
DDR_SECTIONS = [
    "property_summary",
    "area_wise_observations",
    "root_cause_analysis",
    "severity_assessment",
    "recommended_actions",
    "missing_information",
    "conflicts_noted",
]

# Project Structure
PROJECT_STRUCTURE = {
    "data": "Input PDF/JSON documents",
    "images": "Extracted images from documents",
    "outputs": "Generated DDR reports",
    "modules": "Core processing modules",
    "utils": "PDF and image extraction utilities",
    "config": "Configuration files",
}
