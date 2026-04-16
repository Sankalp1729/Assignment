# Advanced DDR Generator - Architecture & Pipeline Documentation

## System Overview

The Advanced DDR (Detailed Diagnostic Report) Generator is a sophisticated AI-powered system for automated property inspection report analysis and merging. It integrates PyMuPDF for document processing, Google&apos;s Gemini API for intelligent extraction and reasoning, and Jinja2 templating for professional HTML report generation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ADVANCED DDR PIPELINE ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  INPUT STAGE                 PROCESSING STAGE        OUTPUT STAGE       │
│  ───────────                 ────────────────        ────────────       │
│                                                                         │
│  PDF Files  ──┐                                                         │
│               │                                                         │
│  Images     ──┼─→ [1] PDF Extraction   ──→ [2] Schema    ──→ [3]       │
│               │      (PyMuPDF)               Extraction      Observation│
│               │      • Text extraction       (Gemini)        Extraction │
│               │      • Image extraction      • Auto-detect   (Gemini)   │
│               │      • OCR support           • 3 schemas     • Smart     │
│               │                              • Confidence    categorize  │
│               │                                             • Severity  │
│  JSON Data  ──┘                                           assessment   │
│  (Fallback)                                                           │
│                                                                         │
│                          ↓                   ↓                ↓         │
│                                                                         │
│                    [4] Conflict Detection & Merging                     │
│                         (Python + Gemini)                              │
│                         • Detect discrepancies                         │
│                         • Gemini analysis                              │
│                         • Intelligent resolution                       │
│                                                                         │
│                          ↓                                             │
│                                                                         │
│                    [5] Rule-Based Severity Scoring                     │
│                                                                         │
│                          ↓                                             │
│                                                                         │
│                    [6] DDR Section Generation                          │
│                         (Modular Organization)                        │
│                                                                         │
│                          ↓                                             │
│                                                                         │
│              ┌─────────────────────────────────┐                       │
│              │  [7] HTML Report Generation     │                       │
│              │      (Jinja2 Templates)         │                       │
│              │      • Professional styling     │                       │
│              │      • Embedded images          │                       │
│              │      • Responsive layout        │                       │
│              └─────────────────────────────────┘                       │
│                          ↓                                             │
│              ┌─────────────────────────────────┐                       │
│              │      Final Outputs              │                       │
│              ├─────────────────────────────────┤                       │
│              │  • HTML Report (print-ready)    │                       │
│              │  • JSON (machine-readable)      │                       │
│              │  • Text (human-readable)        │                       │
│              │  • Extracted Images            │                       │
│              └─────────────────────────────────┘                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. **PDF Processor** (`utils/pdf_processor.py`)

**Purpose**: Extract text and images from PDF documents using PyMuPDF

**Key Classes**:
- `PDFProcessor`: Main processor class
- `PDFPage`: Single page representation
- `PDFDocument`: Complete document structure

**Key Methods**:
```python
extract_pdf(pdf_path)              # Extract all content
extract_text_only(pdf_path)        # Text-only extraction (fast)
extract_images_only(pdf_path)      # Image extraction
batch_extract(input_dir)           # Process entire directory
validate_pdf(pdf_path)             # Quality validation
to_json()                          # Convert to JSON format
```

**Features**:
- PyMuPDF (fitz) for reliable PDF processing
- Handles CMYK and RGB color spaces
- Page-level metadata extraction
- Base64 image encoding for JSON storage
- Automatic document type inference

**Example Usage**:
```python
processor = PDFProcessor(output_dir=Path("./images"))
pdf_doc = processor.extract_pdf("inspection.pdf")
print(f"Pages: {pdf_doc.total_pages}, Images: {sum(len(p.images) for p in pdf_doc.pages)}")
```

---

### 2. **Gemini Schema Extractor** (`utils/gemini_schema.py`)

**Purpose**: Use Google Gemini to intelligently extract structured schemas from unstructured text

**Key Classes**:
- `SchemaType`: Enum for document types
- `SchemaField`: Individual field representation
- `GeminiSchemaExtractor`: Main extractor

**Supported Schema Types**:
- `INSPECTION_SCHEMA`: Building inspection reports
- `THERMAL_SCHEMA`: Thermal analysis reports
- `MOISTURE_SCHEMA`: Moisture/mold reports
- `GENERIC_SCHEMA`: Fallback for unknown types

**Key Methods**:
```python
extract_schema(text, schema_type, images, context)  # Main extraction
_detect_schema_type(text)                            # Auto-detection
_parse_json_response(response_text)                  # JSON parsing
_calculate_confidence(schema)                        # Confidence scoring
extract_multiple_schemas(documents, schema_types)    # Batch processing
validate_schema(schema, required_fields)             # Validation
```

**Gemini Prompts**:
Each schema type has a specialized prompt that instructs Gemini to extract:
- Document metadata (date, location, equipment)
- Identified issues/anomalies
- Severity indicators
- Photographic evidence
- Recommendations

**Example Usage**:
```python
extractor = GeminiSchemaExtractor(api_key="your-key")
schema = extractor.extract_schema(
    text=pdf_text,
    schema_type=SchemaType.INSPECTION_SCHEMA
)
print(f"Confidence: {schema['_extraction_metadata']['confidence_overall']}")
```

---

### 3. **Gemini Observation Extractor** (`utils/gemini_observations.py`)

**Purpose**: Convert schema data into standardized Observation objects with intelligent categorization

**Key Classes**:
- `ConfidenceLevel`: Enum for confidence assessment
- `ExtractionContext`: Context metadata
- `GeminiObservationExtractor`: Main extractor

**Category Mapping**:
- Structural
- Thermal
- Electrical
- Plumbing
- Roofing
- Moisture
- Finishing
- Insulation
- HVAC
- Exterior

**Key Methods**:
```python
extract_observations(schema_data, context, images)    # Main extraction
_determine_category(issue, images)                    # Smart categorization
_determine_severity(issue, category)                  # Severity assessment
_calculate_observation_confidence(issue, category, severity)
_generate_observation_id(context, index)
_map_document_type(doc_type_str)
batch_extract_observations(schemas, contexts, images_list)
merge_observations(observation_batches)               # Deduplication
```

**Confidence Calculation Factors**:
1. Description completeness (0-0.15)
2. Location specificity (0-0.10)
3. Recommended action presence (0-0.10)
4. Image references (0-0.10)
5. Severity level confidence (0-0.05)
6. Base score (0.50)

**Example Usage**:
```python
extractor = GeminiObservationExtractor(api_key="your-key")
obs_list, metadata = extractor.extract_observations(
    schema_data=schema,
    context=ExtractionContext(
        document_type="inspection_report",
        source_filename="inspection.pdf"
    )
)
print(f"Extracted {len(obs_list)} observations")
```

---

### 4. **Gemini Conflict Resolver** (`utils/gemini_conflict.py`)

**Purpose**: Detect and intelligently resolve discrepancies between observations from different documents

**Key Classes**:
- `ConflictAnalysis`: Analysis result
- `GeminiConflictResolver`: Main resolver

**Conflict Detection Strategy**:
1. Match observations by area + category
2. Compare severity levels
3. Flag if discrepancy ≥ threshold (2 levels)
4. Use Gemini for intelligent analysis

**Key Methods**:
```python
detect_conflicts(obs_batch1, obs_batch2, severity_threshold)  # Detection
_find_matching_observation(obs, candidates)                  # Matching
_analyze_conflict_with_gemini(obs1, obs2, discrepancy)      # Analysis
_merge_observations(obs1, obs2, resolved_severity)           # Merging
create_conflict_records(analyses)                            # Record creation
batch_detect_conflicts(observation_sets)                     # Batch processing
```

**Conflict Resolution Process**:
1. Gemini analyzes source documents
2. Assesses which observation is more reliable
3. Provides likely cause of discrepancy
4. Recommends resolution severity level
5. Merges observations with confidence score

**Example Usage**:
```python
resolver = GeminiConflictResolver(api_key="your-key")
conflicts, merged = resolver.detect_conflicts(
    inspection_obs,
    thermal_obs,
    severity_threshold=2
)
print(f"Found {len(conflicts)} conflicts, merged to {len(merged)} observations")
```

---

### 5. **HTML Report Generator** (`utils/html_generator.py`)

**Purpose**: Generate professional, print-ready HTML reports from DDR data using Jinja2

**Key Classes**:
- `HTMLReportGenerator`: Main generator

**Features**:
- Professional CSS styling
- Responsive design
- Print-optimized layout
- Severity color coding
- Summary statistics cards
- Area-wise organization
- Interactive elements

**HTML Sections**:
1. **Header**: Report metadata, property info, status badge
2. **Executive Summary**: Severity counts, overall status
3. **Detailed Findings**: Area-by-area observations with images
4. **Root Cause Analysis**: Categorized causes with confidence
5. **Recommendations**: Priority actions with descriptions
6. **Information Gaps**: Missing data explanations
7. **Assessment Discrepancies**: Conflict documentation
8. **Footer**: Generation timestamp, disclaimer

**Key Methods**:
```python
generate_html_report(ddr_report, observations, custom_css)  # Main generation
_calculate_summary(observations)                             # Statistics
save_html_report(html_content, output_path)                 # Save to file
generate_and_save(ddr_report, observations, output_path)    # One-step
render_template(template_name, context)                     # Custom template
```

**CSS Features**:
- Status badge colors (CRITICAL, HIGH, MEDIUM, LOW)
- Area section styling with left border
- Observation cards with severity highlighting
- Print media queries for optimized output
- Mobile-responsive grid layouts

**Example Usage**:
```python
generator = HTMLReportGenerator()
html = generator.generate_html_report(ddr_report, observations)
generator.save_html_report(html, "output.html")
```

---

### 6. **PDF Generator for Testing** (`utils/pdf_generator.py`)

**Purpose**: Create sample PDF documents for testing and demonstration

**Key Functions**:
```python
create_sample_inspection_pdf(output_path)   # Create inspection PDF
create_sample_thermal_pdf(output_path)      # Create thermal PDF
create_sample_pdfs(data_dir)                # Create both
```

**Generated Content**:
- Building inspection report with structural findings
- Thermal analysis report with anomalies
- Realistic property details and measurements
- Professional formatting with sections

---

### 7. **Advanced Main Entry Point** (`main_advanced.py`)

**Purpose**: Orchestrate the complete pipeline

**Class**: `AdvancedDDRGenerator`

**Key Methods**:
```python
process_pdfs(pdf_paths)           # Process real PDFs with Gemini
process_json_fallback(json_paths) # Fallback to JSON data
```

**Pipeline Flow**:
1. **Stage 1**: PDF Text & Image Extraction (PyMuPDF)
2. **Stage 2**: Schema Extraction with Gemini
3. **Stage 3**: Structured Observation Extraction
4. **Stage 4**: Conflict Detection & Merging
5. **Stage 5-6**: DDR Report Generation
6. **Stage 7**: HTML Report Generation

**Example Usage**:
```python
generator = AdvancedDDRGenerator(gemini_api_key="your-key")
results = generator.process_pdfs(["inspection.pdf", "thermal.pdf"])
print(f"Report: {results['html_report_path']}")
```

---

## Data Flow & Models

### Core Data Models (modules/data_models.py)

```python
SeverityLevel(Enum)
├── CRITICAL = "CRITICAL"
├── HIGH = "HIGH"
├── MEDIUM = "MEDIUM"
├── LOW = "LOW"
└── NOT_AVAILABLE = "NOT_AVAILABLE"

DocumentType(Enum)
├── INSPECTION_REPORT = "inspection_report"
├── THERMAL_REPORT = "thermal_report"
└── OTHER = "other"

Observation(@dataclass)
├── observation_id: str
├── document_type: DocumentType
├── area: str                    # "Terrace", "South Wall", etc.
├── category: str                # "Structural", "Thermal", etc.
├── description: str
├── severity: SeverityLevel
├── confidence: float (0-1)
├── image_references: List[str]
└── raw_data: Dict

DDRReport(@dataclass)
├── report_id: str
├── generation_date: datetime
├── property_summary: Dict
├── area_wise_observations: Dict
├── root_cause_analysis: List
├── severity_assessment: Dict
├── recommended_actions: List
├── missing_information: List
└── conflicts_noted: List
```

---

## API Configuration

### Google Gemini API Setup

**Required**: Set `GOOGLE_API_KEY` environment variable

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Gemini Models Used**:
- `gemini-1.5-pro`: For all extraction and reasoning tasks
  - Schema extraction
  - Observation extraction
  - Conflict resolution
  - Severity assessment

**Rate Limits** (as per Google's defaults):
- 60 requests/minute (free tier)
- Higher limits available with billing

---

## Processing Example

### Input: Two PDF Files
```
inspection.pdf → 20 pages, 15 observations
thermal.pdf → 12 pages, 18 observations
```

### Processing Steps

**Stage 1: PDF Extraction**
```
inspection.pdf
├─ 20 pages extracted
├─ 82 images found & extracted
└─ 45KB text content

thermal.pdf
├─ 12 pages extracted
├─ 36 images found
└─ 28KB text content
```

**Stage 2: Schema Extraction (Gemini)**
```
inspection.pdf → Schema (confidence: 0.92)
├─ Property Details ✓
├─ 15 Issues identified ✓
├─ Severity levels assigned ✓
└─ Recommendations ✓

thermal.pdf → Thermal Schema (confidence: 0.88)
├─ Scan parameters ✓
├─ 18 anomalies ✓
├─ Temperature deltas ✓
└─ Affected areas ✓
```

**Stage 3: Observations (Gemini)**
```
inspection.pdf
├─ 15 Observation objects created
├─ Categories: Structural(8), Moisture(4), Electrical(3)
├─ Avg confidence: 0.84
└─ 0 extraction errors

thermal.pdf
├─ 18 Observation objects created
├─ Categories: Thermal(12), Structural(6)
├─ Avg confidence: 0.81
└─ 1 extraction error (resolved)
```

**Stage 4: Conflict Detection (Gemini)**
```
Matching observations:
├─ Terrace Structural + Thermal = Conflict detected
│  └─ Severity: HIGH vs HIGH = No discrepancy
├─ South Wall Moisture vs Thermal = Conflict detected
│  └─ Severity: MEDIUM vs MEDIUM = Resolved
└─ Foundation Structural (only in inspection)
   └─ No conflict = Added to merged

Result: 33 merged observations, 2 conflicts analyzed
```

**Stage 5-7: Report Generation**
```
DDRReport(id=ddr_20260416_191557)
├─ Property Summary
│  ├─ Total Issues: 33
│  ├─ Areas: 4
│  ├─ Severity: Critical(0) + High(8) + Medium(12) + Low(13)
│  └─ Status: HIGH PRIORITY
├─ Area-wise Observations: 4 areas
├─ Root Causes: 3 identified
├─ Recommendations: 5 actions
└─ Missing Info: 1 item (Foundation thermal)

HTML Report Generated
├─ File: outputs/ddr_20260416_191557_fallback.html
├─ Size: 145KB
├─ Including images: Yes
└─ Print-ready: Yes
```

---

## Error Handling

### Graceful Degradation

1. **PDF Processing Fails**
   - Fallback to JSON data if available
   - Log error and continue

2. **Gemini API Unavailable**
   - Use rule-based extraction
   - Reduce confidence scores
   - Fall back to legacy pipeline

3. **Missing Images**
   - Continue processing without images
   - Note in metadata
   - Generate reports anyway

4. **Invalid Schema**
   - Log warning
   - Skip problematic fields
   - Use defaults for missing data

---

## Performance Metrics

**Typical Processing Time** (for 2 documents):
- PDF Extraction: 0.5-1.0s
- Schema Extraction (Gemini): 2-4s
- Observation Extraction: 3-5s
- Conflict Detection: 1-2s
- Report Generation: 0.5s
- **Total: 7-13 seconds**

**Output Sizes** (typical):
- HTML Report: 100-200KB
- JSON Report: 50-100KB
- Text Report: 20-50KB
- Extracted Images: 5-50MB

---

## Dependencies

### Python Packages

```
pymupdf==1.24.8              # PDF processing
google-generativeai==0.3.0   # Gemini API
jinja2==3.1.2                # HTML templating
pydantic==2.0.0              # Data validation
pillow==10.0.0               # Image processing
pdf2image==1.16.3            # Alternative PDF handling
reportlab==4.0.8             # Sample PDF generation
```

### System Requirements

- Python 3.8+
- 4GB RAM (recommended)
- Internet connection (for Gemini API)
- 100MB disk space (for outputs)

---

## Configuration

### Environment Variables

```bash
GOOGLE_API_KEY          # Required for Gemini features
GEMINI_MODEL            # Optional: default is "gemini-1.5-pro"
OUTPUT_DIR              # Optional: output directory path
LOG_LEVEL               # Optional: DEBUG, INFO, WARNING, ERROR
```

### Input Configuration

**data/** directory structure:
```
data/
├─ inspection.pdf              # Real PDF or
├─ inspection.pdf.json         # JSON fallback
├─ thermal.pdf                 # Real PDF or
├─ thermal.pdf.json            # JSON fallback
├─ moisture.pdf                # Optional
└─ moisture.pdf.json           # Optional
```

---

## Future Enhancements

1. **Database Integration**
   - PostgreSQL persistence
   - Historical report comparison
   - Trend analysis

2. **REST API**
   - FastAPI endpoints
   - Batch processing
   - Web dashboard

3. **Advanced LLM Features**
   - Multi-model comparison (GPT-4, Claude)
   - Fine-tuned models
   - Custom prompts

4. **Real Estate Integration**
   - MLS data enrichment
   - Property valuation impact
   - Insurance premium estimation

5. **Mobile App**
   - On-site report generation
   - Image annotation
   - Voice notes

---

## Troubleshooting

### Common Issues

**"GOOGLE_API_KEY not set"**
```bash
# Set the environment variable
export GOOGLE_API_KEY="your-key"
python main_advanced.py
```

**"No module named 'pymupdf'"**
```bash
pip install pymupdf
```

**"Gemini API rate limited"**
- Wait 1 minute and retry
- Upgrade to paid tier for higher limits
- Batch requests more efficiently

**"PDF extraction failing"**
- Ensure PDF is valid and readable
- Try JSON fallback mode
- Check file permissions

---

## Command Line Usage

```bash
# Process PDFs with Gemini
export GOOGLE_API_KEY="your-key"
python main_advanced.py

# Process with JSON fallback (no API key needed)
python main_advanced.py

# Access generated HTML report
open outputs/ddr_*.html
```

---

## Testing

### Unit Tests (example)

```python
# Test PDF extraction
def test_pdf_processor():
    processor = PDFProcessor()
    doc = processor.extract_pdf("test_inspection.pdf")
    assert doc.total_pages > 0
    assert len(doc.pages) == doc.total_pages

# Test observation extraction
def test_observation_extraction():
    extractor = GeminiObservationExtractor()
    obs, meta = extractor.extract_observations(schema, context)
    assert len(obs) > 0
    assert all(o.severity in SeverityLevel for o in obs)

# Test conflict detection
def test_conflict_detection():
    resolver = GeminiConflictResolver()
    conflicts, merged = resolver.detect_conflicts(obs1, obs2)
    assert len(merged) <= len(obs1) + len(obs2)
```

---

## License

This project implements building inspection automation using AI. Follow your local laws and regulations regarding property inspection and reporting.

---

**Last Updated**: April 16, 2026  
**Version**: 2.0 (Advanced Gemini Integration)
