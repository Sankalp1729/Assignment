"""
HTML report generator with Jinja2 templates.
Produces professional, image-rich DDR reports in HTML format.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64

from jinja2 import Environment, FileSystemLoader, Template
import json

# Import core models
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.data_models import DDRReport, Observation, SeverityLevel, DocumentType


logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """
    Generates professional HTML DDR reports with Jinja2 templating.
    Supports embedded images, dynamic styling, and modular sections.
    """

    DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.property_summary.property_address or 'DDR Report' }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .header {
            border-bottom: 3px solid #0066cc;
            margin-bottom: 30px;
            padding-bottom: 20px;
        }
        
        .header h1 {
            color: #0066cc;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .report-meta {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            font-size: 14px;
            color: #666;
        }
        
        .meta-item {
            padding: 10px 0;
        }
        
        .meta-label {
            font-weight: bold;
            color: #333;
        }
        
        section {
            margin: 30px 0;
        }
        
        section h2 {
            color: #0066cc;
            font-size: 22px;
            border-left: 4px solid #0066cc;
            padding-left: 15px;
            margin-bottom: 20px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }
        
        .status-critical { background: #ff4444; color: white; }
        .status-high { background: #ff9800; color: white; }
        .status-medium { background: #ffb300; color: white; }
        .status-low { background: #4caf50; color: white; }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .summary-card {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border: 1px solid #ddd;
        }
        
        .summary-card h3 {
            color: #0066cc;
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .summary-card p {
            color: #666;
            font-size: 12px;
        }
        
        .area-section {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #0066cc;
        }
        
        .area-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .observation {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 3px solid #ddd;
            border-radius: 3px;
        }
        
        .observation.critical {
            border-left-color: #ff4444;
            background: #fff5f5;
        }
        
        .observation.high {
            border-left-color: #ff9800;
            background: #fff8f0;
        }
        
        .observation.medium {
            border-left-color: #ffb300;
            background: #fffbf0;
        }
        
        .observation.low {
            border-left-color: #4caf50;
            background: #f9f9f9;
        }
        
        .obs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .obs-category {
            display: inline-block;
            background: #e0e0e0;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .obs-description {
            color: #555;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        
        .obs-confidence {
            font-size: 12px;
            color: #999;
            margin-top: 10px;
        }
        
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .image-item {
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            background: #f9f9f9;
        }
        
        .image-item img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        
        .image-caption {
            padding: 10px;
            font-size: 12px;
            color: #666;
            text-align: center;
            background: #f0f0f0;
        }
        
        .root-cause-item {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        
        .root-cause-item h4 {
            color: #0066cc;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .recommendation {
            background: #f0f8ff;
            padding: 15px;
            border-left: 4px solid #0066cc;
            margin-bottom: 15px;
            border-radius: 3px;
        }
        
        .recommendation h4 {
            color: #0066cc;
            margin-bottom: 8px;
        }
        
        .footer {
            border-top: 1px solid #ddd;
            margin-top: 40px;
            padding-top: 20px;
            font-size: 12px;
            color: #999;
            text-align: center;
        }
        
        @media print {
            body { background: white; padding: 0; }
            .container { max-width: 100%; margin: 0; padding: 0; box-shadow: none; }
            section { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Detailed Diagnostic Report (DDR)</h1>
            <div class="report-meta">
                <div class="meta-item">
                    <span class="meta-label">Report ID:</span> {{ report.report_id }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Generated:</span> {{ report.generation_date|default('N/A') }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Property:</span> {{ report.property_summary.property_address|default('Residential') }}
                </div>
                <div class="meta-item">
                    <span class="meta-label">Overall Status:</span> 
                    <span class="status-badge status-{{ report.property_summary.overall_status|lower|replace(' ', '-') }}">
                        {{ report.property_summary.overall_status|upper }}
                    </span>
                </div>
            </div>
        </div>

        <!-- Executive Summary -->
        <section>
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>{{ summary.critical|default(0) }}</h3>
                    <p>Critical Issues</p>
                </div>
                <div class="summary-card">
                    <h3>{{ summary.high|default(0) }}</h3>
                    <p>High Priority</p>
                </div>
                <div class="summary-card">
                    <h3>{{ summary.medium|default(0) }}</h3>
                    <p>Medium Priority</p>
                </div>
                <div class="summary-card">
                    <h3>{{ summary.low|default(0) }}</h3>
                    <p>Low Priority</p>
                </div>
            </div>
            <p>{{ report.property_summary.property_description|default('Property assessment complete.') }}</p>
        </section>

        <!-- Area-wise Observations -->
        {% if report.area_wise_observations %}
        <section>
            <h2>Detailed Findings by Area</h2>
            {% for area_name, area_data in report.area_wise_observations.items() %}
            <div class="area-section">
                <div class="area-title">
                    {{ area_name }}
                    <span class="status-badge status-{{ area_data.issues_by_severity.keys()|first|lower|default('low') }}">
                        HIGH
                    </span>
                </div>
                
                {% if area_data.issues_by_severity %}
                    {% for severity_level, obs_list in area_data.issues_by_severity.items() %}
                        {% for obs in obs_list %}
                        <div class="observation {{ severity_level|lower }}">
                            <div class="obs-header">
                                <div>
                                    <span class="obs-category">{{ obs.category|upper }}</span>
                                    <span class="status-badge status-{{ severity_level|lower }}">{{ severity_level }}</span>
                                </div>
                            </div>
                            <div class="obs-description">{{ obs.description }}</div>
                            <div class="obs-confidence">Confidence: {{ (obs.confidence * 100)|int }}%</div>
                        </div>
                        {% endfor %}
                    {% endfor %}
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Root Cause Analysis -->
        {% if report.root_cause_analysis %}
        <section>
            <h2>Root Cause Analysis</h2>
            {% for item in report.root_cause_analysis %}
                {% if item %}
                <div class="root-cause-item">
                    <h4>{{ item.category|default('Issue Category') }}</h4>
                    <p>{{ item.identified_cause|default('Investigation recommended to determine exact cause.') }}</p>
                </div>
                {% endif %}
            {% endfor %}
        </section>
        {% endif %}

        <!-- Recommended Actions -->
        {% if report.recommended_actions %}
        <section>
            <h2>Recommended Actions</h2>
            {% for item in report.recommended_actions %}
            <div class="recommendation">
                <h4>{{ item.action|default(item.category|default('Action Required')) }}</h4>
                <p>{{ item.description|default('Further investigation recommended.') }}</p>
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Missing Information -->
        {% if report.missing_information %}
        <section>
            <h2>Information Gaps</h2>
            <p style="margin-bottom: 15px; color: #666;">The following information could not be determined from available documents:</p>
            <ul style="margin-left: 20px; color: #555;">
                {% for item in report.missing_information %}
                <li style="margin-bottom: 8px;">
                    <strong>{{ item.data_type|default('Unknown Field') }}:</strong> 
                    {{ item.reason|default('Data not available.') }}
                </li>
                {% endfor %}
            </ul>
        </section>
        {% endif %}

        <!-- Conflicts Detected -->
        {% if report.conflicts_noted %}
        <section>
            <h2>Assessment Discrepancies</h2>
            <p style="margin-bottom: 15px; color: #666;">The following discrepancies were found between source documents:</p>
            {% for conflict in report.conflicts_noted %}
            <div class="root-cause-item" style="border-left: 3px solid #ff9800;">
                <h4>{{ conflict.severity_discrepancy|default('Conflict') }}: {{ conflict.conflict_id }}</h4>
                <p><strong>Likely Cause:</strong> {{ conflict.likely_cause|default('Assessment differences') }}</p>
                <p><strong>Resolution:</strong> {{ conflict.recommendation|default('Merged assessment') }}</p>
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Footer -->
        <div class="footer">
            <p>This report was automatically generated using AI-based analysis on {{ report.generation_date|default('the indicated date') }}.</p>
            <p>For questions or clarifications, please contact the inspection provider.</p>
        </div>
    </div>
</body>
</html>
"""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize HTML report generator.
        
        Args:
            template_dir: Optional directory with custom Jinja2 templates
        """
        self.template_dir = template_dir
        
        if template_dir and template_dir.exists():
            self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            # Use inline default template
            self.env = Environment()

    def generate_html_report(
        self,
        ddr_report: DDRReport,
        observations: List[Observation],
        custom_css: Optional[str] = None,
        include_images: bool = False
    ) -> str:
        """
        Generate HTML report from DDR data.
        
        Args:
            ddr_report: DDRReport object
            observations: List of Observation objects
            custom_css: Optional custom CSS to inject
            include_images: Whether to embed images in HTML
            
        Returns:
            HTML report string
        """
        # Calculate summary statistics
        summary = self._calculate_summary(observations)
        
        # Prepare template context
        context = {
            "report": ddr_report,
            "observations": observations,
            "summary": summary,
            "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "custom_css": custom_css or ""
        }
        
        # Render template
        template = self.env.from_string(self.DEFAULT_TEMPLATE)
        html = template.render(**context)
        
        logger.info("HTML report generated")
        return html

    def _calculate_summary(self, observations: List[Observation]) -> Dict[str, int]:
        """Calculate severity summary statistics."""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "total": len(observations)
        }
        
        for obs in observations:
            if obs.severity == SeverityLevel.CRITICAL:
                summary["critical"] += 1
            elif obs.severity == SeverityLevel.HIGH:
                summary["high"] += 1
            elif obs.severity == SeverityLevel.MEDIUM:
                summary["medium"] += 1
            elif obs.severity == SeverityLevel.LOW:
                summary["low"] += 1
        
        return summary

    def save_html_report(self, html_content: str, output_path: str):
        """Save HTML report to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to: {output_path}")

    def generate_and_save(
        self,
        ddr_report: DDRReport,
        observations: List[Observation],
        output_path: str,
        custom_css: Optional[str] = None
    ):
        """Generate and save HTML report in one step."""
        html = self.generate_html_report(ddr_report, observations, custom_css)
        self.save_html_report(html, output_path)
        return output_path

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render custom template from template directory."""
        if not self.template_dir:
            raise ValueError("No template directory configured")
        
        template = self.env.get_template(template_name)
        return template.render(**context)
