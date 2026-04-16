# Application Configuration

"""
App configuration settings for AI DDR Generator
"""

# API Settings
API_PROVIDER = "gemini"
API_VERSION = "2.0-flash"

# Processing Settings
FUZZY_MATCH_THRESHOLD = 70  # For area name matching (0-100)
BATCH_SIZE = 10  # Items to process at once
TIMEOUT_SECONDS = 30  # API call timeout

# Output Settings
OUTPUT_FORMAT = "both"  # "text", "json", or "both"
OUTPUT_DIRECTORY = "outputs"
REPORT_ENCODING = "utf-8"

# Logging Settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = True
LOG_FILE = "app.log"

# PDF Settings
PDF_MAX_PAGES = None  # None = unlimited
EXTRACT_IMAGES = False
PAGE_BY_PAGE_PROCESSING = True

# Severity Settings (STEP 7)
CRITICAL_COLOR = "#d32f2f"
HIGH_COLOR = "#f57c00"
MEDIUM_COLOR = "#fbc02d"
LOW_COLOR = "#4caf50"

# Report Settings (STEP 8)
REPORT_SECTIONS = [
    "Property Issue Summary",
    "Area-wise Observations",
    "Probable Root Cause",
    "Severity Assessment",
    "Recommended Actions",
    "Additional Notes",
    "Missing Information",
]

INCLUDE_EXPLANATIONS = True
INCLUDE_IMAGES = False  # Future enhancement

# Feature Flags
ENABLE_GEMINI_FALLBACK = True  # Use templates if API fails
ENABLE_CONFLICT_DETECTION = True
ENABLE_SEVERITY_EXPLANATIONS = True
ENABLE_REPORT_FORMATTING = True
