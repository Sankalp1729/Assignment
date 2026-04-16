"""
HTML report generation using Jinja2 templates.
Converts DDR data to professional HTML reports.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Template
from .data_models import DDRReport


class HTMLReportGenerator:
    """Generate professional HTML reports from DDR data."""
    
    # HTML template with embedded CSS for professional styling
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DDR Report - {{ report_id }}</title>
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
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header {
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 32px;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .report-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        
        .meta-item h3 {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .meta-item p {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            font-size: 20px;
            color: #2c3e50;
            border-left: 4px solid #3498db;
            padding-left: 12px;
            margin-bottom: 15px;
            margin-top: 25px;
        }
        
        .severity-summary {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .severity-card {
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            color: white;
        }
        
        .severity-critical {
            background: #e74c3c;
        }
        
        .severity-high {
            background: #f39c12;
        }
        
        .severity-medium {
            background: #f1c40f;
            color: #333;
        }
        
        .severity-low {
            background: #27ae60;
        }
        
        .severity-card h3 {
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .severity-card p {
            font-size: 24px;
            font-weight: bold;
        }
        
        .area-section {
            background: #fafafa;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
        }
        
        .area-section h3 {
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }
        
        .area-issues {
            list-style: none;
        }
        
        .area-issues li {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .area-issues li:last-child {
            border-bottom: none;
        }
        
        .observation {
            padding: 12px;
            border-left: 3px solid #3498db;
            margin-bottom: 10px;
        }
        
        .obs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .obs-category {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .obs-severity {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }
        
        .severity-CRITICAL { background: #e74c3c; }
        .severity-HIGH { background: #f39c12; }
        .severity-MEDIUM { background: #f1c40f; color: #333; }
        .severity-LOW { background: #27ae60; }
        
        .obs-description {
            color: #555;
            font-size: 14px;
            margin: 8px 0;
        }
        
        .obs-meta {
            font-size: 12px;
            color: #999;
        }
        
        .root-causes {
            background: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #3498db;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        
        .root-causes h4 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .root-causes ul {
            margin-left: 20px;
        }
        
        .root-causes li {
            margin-bottom: 5px;
            color: #555;
        }
        
        .recommendations {
            background: #f0f8e8;
            padding: 15px;
            border-left: 4px solid #27ae60;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        
        .recommendations h4 {
            color: #27ae60;
            margin-bottom: 10px;
        }
        
        .recommendations ol {
            margin-left: 20px;
        }
        
        .recommendations li {
            margin-bottom: 8px;
            color: #555;
        }
        
        .missing-data {
            background: #fef5e7;
            padding: 15px;
            border-left: 4px solid #f39c12;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        
        .missing-data h4 {
            color: #f39c12;
            margin-bottom: 10px;
        }
        
        .missing-data ul {
            margin-left: 20px;
        }
        
        .missing-data li {
            margin-bottom: 5px;
            color: #555;
            font-size: 14px;
        }
        
        .footer {
            border-top: 1px solid #eee;
            margin-top: 40px;
            padding-top: 20px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .status-critical {
            background: #e74c3c;
            color: white;
        }
        
        .status-high {
            background: #f39c12;
            color: white;
        }
        
        .status-medium {
            background: #f1c40f;
            color: #333;
        }
        
        .status-low {
            background: #27ae60;
            color: white;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #f5f5f5;
            font-weight: 600;
            color: #2c3e50;
        }
        
        tr:hover {
            background: #f9f9f9;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .container {
                box-shadow: none;
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Detailed Diagnostic Report (DDR)</h1>
            <p>Property Inspection & Analysis Summary</p>
        </div>
        
        <!-- Report Metadata -->
        <div class="report-meta">
            <div class="meta-item">
                <h3>Report ID</h3>
                <p>{{ report_id }}</p>
            </div>
            <div class="meta-item">
                <h3>Generation Date</h3>
                <p>{{ generation_date }}</p>
            </div>
            <div class="meta-item">
                <h3>Overall Status</h3>
                <p class="status-badge status-{{ overall_status | lower }}">{{ overall_status }}</p>
            </div>
            <div class="meta-item">
                <h3>Total Issues</h3>
                <p>{{ total_issues }}</p>
            </div>
        </div>
        
        <!-- Property Summary Section -->
        <div class="section">
            <h2>Property Summary</h2>
            
            {% if property_summary %}
            <div class="severity-summary">
                <div class="severity-card severity-critical">
                    <h3>Critical</h3>
                    <p>{{ property_summary.critical_count | default(0) }}</p>
                </div>
                <div class="severity-card severity-high">
                    <h3>High</h3>
                    <p>{{ property_summary.high_count | default(0) }}</p>
                </div>
                <div class="severity-card severity-medium">
                    <h3>Medium</h3>
                    <p>{{ property_summary.medium_count | default(0) }}</p>
                </div>
                <div class="severity-card severity-low">
                    <h3>Low</h3>
                    <p>{{ property_summary.low_count | default(0) }}</p>
                </div>
            </div>
            
            {% if property_summary.overall_assessment %}
            <p><strong>Assessment:</strong> {{ property_summary.overall_assessment }}</p>
            {% endif %}
            {% endif %}
        </div>
        
        <!-- Area-wise Observations Section -->
        <div class="section">
            <h2>Area-Wise Analysis</h2>
            
            {% if area_wise_observations %}
                {% for area, details in area_wise_observations.items() %}
                <div class="area-section">
                    <h3>
                        {{ area }}
                        <span class="obs-severity severity-{{ details.max_severity | default('LOW') }}">
                            {{ details.max_severity | default('LOW') }}
                        </span>
                    </h3>
                    
                    <div class="area-issues">
                        {% for issue in details.issues %}
                        <li>
                            <div class="observation">
                                <div class="obs-header">
                                    <span class="obs-category">{{ issue.category | default('General') }}</span>
                                    <span class="obs-severity severity-{{ issue.severity | default('LOW') }}">
                                        {{ issue.severity | default('LOW') }}
                                    </span>
                                </div>
                                <div class="obs-description">{{ issue.description }}</div>
                                <div class="obs-meta">
                                    Confidence: {{ ((issue.confidence | string | float(0.5)) * 100) | round(0) }}% | 
                                    Source: {{ issue.source | default('Analysis') }}
                                </div>
                            </div>
                        </li>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        </div>
        
        <!-- Root Cause Analysis Section -->
        {% if root_causes %}
        <div class="section">
            <h2>Root Cause Analysis</h2>
            
            {% for cause in root_causes %}
            <div class="root-causes">
                <h4>{{ cause.category }} Issues in {{ cause.area }}</h4>
                <p><strong>Primary Cause:</strong> {{ cause.root_cause }}</p>
                
                {% if cause.contributing_factors %}
                <p><strong>Contributing Factors:</strong></p>
                <ul>
                    {% for factor in cause.contributing_factors %}
                    <li>{{ factor }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                {% if cause.confidence %}
                <p><strong>Confidence Level:</strong> {{ ((cause.confidence | string | float(0.5)) * 100) | round(0) }}%</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- Recommended Actions Section -->
        {% if recommended_actions %}
        <div class="section">
            <h2>Recommended Actions</h2>
            
            <div class="recommendations">
                <h4>Priority Actions Required</h4>
                <ol>
                    {% for action in recommended_actions %}
                    <li><strong>{{ action.priority | default('ACTION') }}:</strong> {{ action.description }}</li>
                    {% endfor %}
                </ol>
            </div>
        </div>
        {% endif %}
        
        <!-- Missing Information Section -->
        {% if missing_information %}
        <div class="section">
            <h2>Missing Information</h2>
            
            <div class="missing-data">
                <h4>Data Gaps Identified</h4>
                <ul>
                    {% for item in missing_information %}
                    <li><strong>{{ item.data_type }}:</strong> {{ item.reason }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}
        
        <!-- Conflicts Section -->
        {% if conflicts %}
        <div class="section">
            <h2>Data Conflicts Detected</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Area</th>
                        <th>Category</th>
                        <th>Conflict Type</th>
                        <th>Resolution</th>
                    </tr>
                </thead>
                <tbody>
                    {% for conflict in conflicts %}
                    <tr>
                        <td>{{ conflict.area }}</td>
                        <td>{{ conflict.category }}</td>
                        <td>{{ conflict.conflict_type }}</td>
                        <td>{{ conflict.resolution | default('Requires review') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        <!-- Footer -->
        <div class="footer">
            <p>This report was automatically generated by the AI-Based DDR Generator system.</p>
            <p>For questions or clarifications, please contact the inspection team.</p>
            <p>Generated: {{ generation_date }}</p>
        </div>
    </div>
</body>
</html>
"""
    
    def __init__(self):
        """Initialize HTML report generator."""
        self.template = Template(self.HTML_TEMPLATE)
    
    def generate(self, ddr_report: DDRReport) -> str:
        """
        Generate HTML report from DDR data.
        
        Args:
            ddr_report: DDRReport object with all data
            
        Returns:
            HTML string
        """
        # Prepare data for template
        # Handle property_summary which might be dict or object
        ps = ddr_report.property_summary
        if isinstance(ps, dict):
            overall_status = ps.get("overall_status", "PENDING")
        else:
            overall_status = getattr(ps, "overall_status", "PENDING") if ps else "PENDING"
        
        context = {
            "report_id": ddr_report.report_id,
            "generation_date": ddr_report.generation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": overall_status,
            "property_summary": ddr_report.property_summary,
            "area_wise_observations": ddr_report.area_wise_observations,
            "root_causes": ddr_report.root_cause_analysis,
            "recommended_actions": ddr_report.recommended_actions if hasattr(ddr_report, 'recommended_actions') else [],
            "missing_information": ddr_report.missing_information,
            "conflicts": ddr_report.conflicts_noted if ddr_report.conflicts_noted else [],
            "total_issues": len([obs for details in ddr_report.area_wise_observations.values() for obs in details.get("issues", [])])
        }
        
        return self.template.render(**context)
    
    def save_html(self, ddr_report: DDRReport, output_path: str) -> str:
        """
        Generate and save HTML report to file.
        
        Args:
            ddr_report: DDRReport object
            output_path: Path to save HTML file
            
        Returns:
            Path to saved file
        """
        html_content = self.generate(ddr_report)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def generate_with_images(
        self,
        ddr_report: DDRReport,
        image_paths: Dict[str, str] = None
    ) -> str:
        """
        Generate HTML with embedded images.
        
        Args:
            ddr_report: DDRReport object
            image_paths: Dictionary mapping image identifiers to paths
            
        Returns:
            HTML string with embedded images
        """
        html = self.generate(ddr_report)
        
        # Images can be embedded as base64 if needed
        # For now, return standard HTML with image references
        return html
