"""
Generate sample PDF test data for demonstration.
Creates realistic building inspection and thermal report PDFs.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    logging.warning("ReportLab not installed. Install with: pip install reportlab")


logger = logging.getLogger(__name__)


def create_sample_inspection_pdf(output_path: str) -> str:
    """Create a sample building inspection report PDF."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Building Inspection Report", title_style))
        
        # Metadata
        meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        story.append(Paragraph("<b>Property:</b> 123 Oak Street, Springfield, USA", meta_style))
        story.append(Paragraph("<b>Inspection Date:</b> April 15, 2026", meta_style))
        story.append(Paragraph("<b>Inspector:</b> John Smith, Licensed Inspector #2426", meta_style))
        story.append(Spacer(1, 12))
        
        # Findings
        story.append(Paragraph("Structural Findings", styles['Heading2']))
        story.append(Paragraph(
            "<b>Terrace - Concrete Cracking:</b> Significant cracks observed in terrace concrete surface, "
            "approximately 1/4 inch width. Cracks appear to be active with some fresh spalling. "
            "Recommend professional structural assessment. Severity: HIGH",
            styles['BodyText']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "<b>Terrace - Water Seepage:</b> Evidence of water ingress through terrace. Active seepage noted "
            "during inspection. Water stains and efflorescence visible. Waterproofing membrane failure suspected. "
            "Severity: HIGH",
            styles['BodyText']
        ))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Exterior Issues", styles['Heading2']))
        story.append(Paragraph(
            "<b>South Wall - Mortar Deterioration:</b> Mortar deterioration in brick joints visible on south facade. "
            "Missing mortar in several locations creating water infiltration risk. Tuckpointing recommended. "
            "Severity: MEDIUM",
            styles['BodyText']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "<b>East Wall - Small Cracks:</b> Minor hairline cracks in render, non-structural. "
            "Monitoring recommended. Severity: LOW",
            styles['BodyText']
        ))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Foundation", styles['Heading2']))
        story.append(Paragraph(
            "<b>Foundation - Settlement Indicators:</b> Minor differential settlement visible in foundation area. "
            "Doors and windows show slight misalignment. Further monitoring needed. Severity: LOW",
            styles['BodyText']
        ))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Recommendations", styles['Heading2']))
        story.append(Paragraph(
            "1. <b>URGENT:</b> Address terrace cracking and water seepage - structural integrity concern<br/>"
            "2. Obtain structural engineer assessment for settlement monitoring<br/>"
            "3. Plan mortar repointing for south wall within 12 months<br/>"
            "4. Continue monitoring of east wall cracks",
            styles['BodyText']
        ))
        
        doc.build(story)
        logger.info(f"Sample inspection PDF created: {output_path}")
        return str(output_path)
        
    except ImportError:
        logger.error("ReportLab required. Install with: pip install reportlab")
        return None


def create_sample_thermal_pdf(output_path: str) -> str:
    """Create a sample thermal analysis report PDF."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#ff9800'),
            spaceAfter=6,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Thermal Analysis Report", title_style))
        
        # Metadata
        meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        story.append(Paragraph("<b>Property:</b> 123 Oak Street, Springfield, USA", meta_style))
        story.append(Paragraph("<b>Scan Date:</b> April 15, 2026", meta_style))
        story.append(Paragraph("<b>Equipment:</b> FLIR E8 Thermal Camera", meta_style))
        story.append(Paragraph("<b>External Temperature:</b> 52°F (11°C)", meta_style))
        story.append(Spacer(1, 12))
        
        # Thermal Findings
        story.append(Paragraph("Thermal Anomalies Detected", styles['Heading2']))
        
        story.append(Paragraph(
            "<b>Terrace - Insulation Loss:</b> Significant thermal bridging detected over terrace area. "
            "Temperature differential of 15°F (8°C) compared to adjacent areas indicates insulation degradation or gaps. "
            "Severity: HIGH",
            styles['BodyText']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "<b>Terrace - Heat Loss Pattern:</b> Additional thermal anomaly showing consistent heat loss pattern. "
            "Suggests possible structural crack or air infiltration correlating with visual inspection findings. "
            "Severity: HIGH",
            styles['BodyText']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "<b>South Wall - Moderate Heat Loss:</b> Thermal imaging shows moderate heat loss on south facade. "
            "Temperature variation of 8°F (4°C) correlates with mortar deterioration areas. "
            "Severity: MEDIUM",
            styles['BodyText']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "<b>South Wall - Additional Thermal Pattern:</b> Secondary thermal anomaly detected on south wall. "
            "Pattern suggests air leakage around window area. Minor adjustments to weatherstripping recommended. "
            "Severity: MEDIUM",
            styles['BodyText']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "<b>East Wall - Minor Thermal Variation:</b> Small thermal variations detected on east wall facade. "
            "Temperature differential of 3°F (1.5°C). Within normal parameters for time of day. "
            "Severity: LOW",
            styles['BodyText']
        ))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Assessment", styles['Heading2']))
        story.append(Paragraph(
            "Property shows significant thermal envelope issues concentrated on the terrace and south-facing side. "
            "Thermal imaging corroborates visual inspection findings of structural damage and mortar deterioration. "
            "Recommend immediate attention to highest priority items to improve energy efficiency and prevent further damage.",
            styles['BodyText']
        ))
        
        doc.build(story)
        logger.info(f"Sample thermal PDF created: {output_path}")
        return str(output_path)
        
    except ImportError:
        logger.error("ReportLab required. Install with: pip install reportlab")
        return None


def create_sample_pdfs(data_dir: Path = None) -> dict:
    """Create both sample PDFs."""
    if data_dir is None:
        data_dir = Path("./data")
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    inspection_path = create_sample_inspection_pdf(str(data_dir / "sample_inspection.pdf"))
    thermal_path = create_sample_thermal_pdf(str(data_dir / "sample_thermal.pdf"))
    
    return {
        "inspection": inspection_path,
        "thermal": thermal_path
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    paths = create_sample_pdfs()
    print(f"Created: {paths}")
