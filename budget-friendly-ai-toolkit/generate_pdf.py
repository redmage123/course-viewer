#!/usr/bin/env python3
"""
PDF Generator for Budget-Friendly AI Toolkit Slides
Uses WeasyPrint to convert HTML slides to a printable PDF format.
"""

import os
import re
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
SLIDES_FILE = SCRIPT_DIR / "budget-friendly-ai-toolkit-slides.html"
OUTPUT_PDF = SCRIPT_DIR / "budget-friendly-ai-toolkit-slides.pdf"

def extract_slides(html_content):
    """Extract individual slides from the reveal.js HTML."""
    # Find all <section> tags (each is a slide)
    pattern = r'<section>(.*?)</section>'
    slides = re.findall(pattern, html_content, re.DOTALL)
    return slides

def create_print_html(slides, original_html):
    """Create a print-friendly HTML document."""
    # Extract the style section from original HTML
    style_match = re.search(r'<style>(.*?)</style>', original_html, re.DOTALL)
    original_styles = style_match.group(1) if style_match else ""

    print_styles = """
    @page {
        size: A4 landscape;
        margin: 0.5cm;
    }

    body {
        margin: 0;
        padding: 0;
        background: #1a1a2e;
        color: #e6edf3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .slide-page {
        width: 100%;
        height: 100%;
        page-break-after: always;
        page-break-inside: avoid;
        padding: 20px;
        box-sizing: border-box;
        background: #1a1a2e;
        position: relative;
        display: flex;
        flex-direction: column;
    }

    .slide-page:last-child {
        page-break-after: auto;
    }

    .slide-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        overflow: hidden;
        padding: 10px;
    }

    .slide-number {
        position: absolute;
        bottom: 10px;
        right: 20px;
        font-size: 12px;
        color: #666;
    }

    h1, h2, h3, h4 {
        color: #4da6ff;
        margin-top: 0;
    }

    h1 { font-size: 2em; }
    h2 {
        font-size: 1.5em;
        border-bottom: 2px solid #0066cc;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    h3 { font-size: 1.2em; }
    h4 { font-size: 1em; }

    ul, ol {
        margin: 10px 0;
        padding-left: 25px;
    }

    li {
        margin: 5px 0;
        font-size: 0.9em;
    }

    p {
        margin: 8px 0;
        font-size: 0.9em;
    }

    .two-column {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }

    .three-column {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 15px;
    }

    .four-column {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 12px;
    }

    .card, .tool-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #0066cc;
        font-size: 0.85em;
    }

    .tool-card.recommended {
        border-color: #ffd700;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    }

    .tip-box {
        background: linear-gradient(135deg, #0d3320 0%, #1a4d30 100%);
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #00cc66;
        margin: 10px 0;
        font-size: 0.85em;
    }

    .warning-box {
        background: linear-gradient(135deg, #4d2600 0%, #663300 100%);
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #ff9933;
        margin: 10px 0;
        font-size: 0.85em;
    }

    .danger-box {
        background: linear-gradient(135deg, #4d1a1a 0%, #661a1a 100%);
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #ff4444;
        margin: 10px 0;
        font-size: 0.85em;
    }

    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.75em;
        margin: 10px 0;
    }

    .comparison-table th {
        background: #0066cc;
        color: white;
        padding: 8px;
        text-align: left;
    }

    .comparison-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #333;
    }

    .comparison-table tr:nth-child(even) {
        background: rgba(0, 102, 204, 0.1);
    }

    .stat-box {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 8px;
    }

    .stat-number {
        font-size: 2em;
        font-weight: bold;
        color: #4da6ff;
    }

    .stat-label {
        font-size: 0.8em;
        color: #888;
    }

    .value-framework {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .value-letter {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 6px;
        border-left: 3px solid #ffd700;
        font-size: 0.85em;
    }

    .value-letter .letter {
        font-size: 1.2em;
        font-weight: bold;
        color: #ffd700;
        min-width: 25px;
    }

    .agenda-item {
        display: flex;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #333;
        font-size: 0.9em;
    }

    .agenda-time {
        color: #4da6ff;
        font-weight: bold;
        min-width: 60px;
        margin-right: 15px;
    }

    .price-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75em;
        font-weight: bold;
    }

    .price-free { background: #1a4d30; color: #00cc66; }
    .price-budget { background: #1a3d4d; color: #4da6ff; }

    .tool-name {
        font-weight: bold;
        color: #4da6ff;
    }

    .tool-price {
        font-size: 1.2em;
        font-weight: bold;
        margin: 8px 0;
    }

    .fullscreen-btn, .reveal-viewport, script, .controls, .progress {
        display: none !important;
    }
    """

    html_parts = ['<!DOCTYPE html><html><head><meta charset="UTF-8">']
    html_parts.append(f'<style>{original_styles}\n{print_styles}</style>')
    html_parts.append('</head><body>')

    for i, slide in enumerate(slides, 1):
        html_parts.append(f'''
        <div class="slide-page">
            <div class="slide-content">
                {slide}
            </div>
            <div class="slide-number">{i} / {len(slides)}</div>
        </div>
        ''')

    html_parts.append('</body></html>')
    return ''.join(html_parts)

def main():
    print(f"Reading slides from: {SLIDES_FILE}")

    with open(SLIDES_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    slides = extract_slides(html_content)
    print(f"Extracted {len(slides)} slides")

    print_html = create_print_html(slides, html_content)

    # Save debug HTML
    debug_file = SCRIPT_DIR / "print-debug.html"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(print_html)
    print(f"Debug HTML saved to: {debug_file}")

    # Generate PDF using WeasyPrint
    try:
        from weasyprint import HTML, CSS

        print(f"Generating PDF: {OUTPUT_PDF}")
        HTML(string=print_html, base_url=str(SCRIPT_DIR)).write_pdf(
            OUTPUT_PDF,
            stylesheets=[CSS(string='@page { size: A4 landscape; margin: 0.5cm; }')]
        )
        print(f"PDF generated successfully: {OUTPUT_PDF}")
        print(f"File size: {os.path.getsize(OUTPUT_PDF) / 1024:.1f} KB")

    except ImportError:
        print("WeasyPrint not installed. Install with: pip install weasyprint")
        print("Debug HTML has been saved - you can open it in a browser and print to PDF.")

if __name__ == "__main__":
    main()
