# AI Workflow System Design: UrbanRoof DDR Generator

This document outlines the architecture and logic of the AI system designed to automate the generation of Detailed Diagnostic Reports (DDR) from technical inspection and thermal data.

## 1. System Architecture
The system follows a multi-stage pipeline designed for accuracy, reliability, and hallucination control.

### Phase 1: Multimodal Data Extraction
- **Input:** PDF Inspection Report & PDF Thermal Report.
- **Process:** The system uses OCR and Vision-Language Models (VLMs) to extract:
  - Textual observations from summary tables and checklists.
  - Temperature data (Hotspots/Coldspots) from thermal report panels.
  - Spatial mapping (linking Photo IDs in the inspection report to Thermal Image IDs).

### Phase 2: Logical Data Merging
- **Core Logic:** The system correlates the physical observations (e.g., "Hall Skirting Dampness") with the corresponding thermal evidence (e.g., "Coldspot 23.4°C").
- **Conflict Handling:** If the inspection report notes dampness but the thermal image shows no temperature anomaly, the system flags this as a "Conflict" for manual review.
- **Missing Data:** If a section is required but not found in the source, the system is hard-coded to output "Not Available" rather than inferring facts.

### Phase 3: Diagnostic Reasoning
- **Root Cause Analysis:** Using a knowledge base of civil engineering and waterproofing principles, the AI analyzes the merged data to identify probable causes (e.g., capillary action vs. direct leakage).
- **Severity Assessment:** The system calculates severity based on the spread of issues (number of rooms affected) and the depth of damage (e.g., presence of efflorescence or structural cracks).

### Phase 4: Structured Report Generation
- **Output:** A professional Markdown/PDF deliverable following the UrbanRoof standard structure.
- **Image Integration:** Relevant images are embedded directly under their respective observations to provide visual proof for the client.

## 2. Key Features & Guardrails
- **Hallucination Control:** Strict adherence to source documents. No inventing of facts.
- **Client-Friendly Language:** Complex technical findings (like emissivity or reflected temperature) are translated into actionable insights for the property owner.
- **Scalability:** The workflow is designed to handle different report formats by focusing on key data markers (Skirting, Dampness, Coldspot, etc.) rather than fixed layouts.

## 3. Limitations & Future Improvements
- **Current Limitation:** Manual mapping of photo IDs to thermal IDs if the reports use inconsistent naming conventions.
- **Future Improvement:** Implement an automated image-matching algorithm that uses visual similarity to pair site photos with thermal overlays automatically.
- **Future Improvement:** Integration with a mobile app for real-time DDR generation during the site visit.
