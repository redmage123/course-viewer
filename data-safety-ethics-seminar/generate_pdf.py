#!/usr/bin/env python3
"""
PDF Generator for Data Safety & Ethics Slides
Converts Reveal.js HTML slides to a printable PDF format.
"""

import re
from pathlib import Path
from weasyprint import HTML, CSS


def extract_slides(html_content: str) -> list[str]:
    """Extract individual slides from the Reveal.js HTML."""
    # Find the slides container - handle various closing patterns
    slides_match = re.search(r'<div class="slides">(.*?)</div>\s*</div>\s*(?:<button|<script)',
                            html_content, re.DOTALL)
    if not slides_match:
        # Try alternative pattern
        slides_match = re.search(r'<div class="slides">(.*?)</div>\s*</div>',
                                html_content, re.DOTALL)
    if not slides_match:
        raise ValueError("Could not find slides container")

    slides_content = slides_match.group(1)

    # Split by section tags
    sections = re.findall(r'<section[^>]*>(.*?)</section>', slides_content, re.DOTALL)

    return sections


def create_print_html(slides: list[str], original_html: str) -> str:
    """Create a print-friendly HTML document."""

    # Extract the style section from original
    style_match = re.search(r'<style>(.*?)</style>', original_html, re.DOTALL)
    original_styles = style_match.group(1) if style_match else ""

    print_styles = """
        @page {
            size: A4 landscape;
            margin: 0.5cm;
        }

        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #f0f0f0;
            margin: 0;
            padding: 0;
        }

        .slide-page {
            width: 297mm;
            height: 210mm;
            padding: 15mm;
            box-sizing: border-box;
            page-break-after: always;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .slide-page:last-child {
            page-break-after: auto;
        }

        .slide-content {
            width: 100%;
            height: 100%;
            overflow: hidden;
            padding: 10px;
        }

        h1 {
            font-size: 2.2em;
            color: #4da6ff;
            margin-bottom: 20px;
        }

        h2 {
            font-size: 1.6em;
            color: #4da6ff;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        h3, h4 {
            color: #4da6ff;
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
            gap: 10px;
        }

        .card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
        }

        .tip-box {
            background: linear-gradient(135deg, #0d3320 0%, #1a4d30 100%);
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #00cc66;
            margin: 10px 0;
        }

        .warning-box {
            background: linear-gradient(135deg, #4d2600 0%, #663300 100%);
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #ff9933;
            margin: 10px 0;
        }

        .danger-box {
            background: linear-gradient(135deg, #4d1a1a 0%, #661a1a 100%);
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #ff4444;
            margin: 10px 0;
        }

        .exercise-box {
            background: linear-gradient(135deg, #1a1a4d 0%, #2d2d66 100%);
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #4da6ff;
            margin: 10px 0;
        }

        .shield-framework {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .shield-letter {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 6px;
            border-left: 4px solid #0066cc;
            font-size: 0.9em;
        }

        .shield-letter .letter {
            font-size: 1.2em;
            font-weight: bold;
            color: #4da6ff;
            min-width: 25px;
        }

        .risk-example {
            background: linear-gradient(135deg, #2d1a1a 0%, #3d2020 100%);
            border: 2px solid #ff4444;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }

        .safe-example {
            background: linear-gradient(135deg, #1a2d1a 0%, #203d20 100%);
            border: 2px solid #00cc66;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
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
            color: #aaa;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.75em;
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
            background: rgba(0,102,204,0.1);
        }

        .framework-step {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }

        .step-number {
            background: #0066cc;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 12px;
            flex-shrink: 0;
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

        .prompt-example {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 10px;
            font-family: monospace;
            font-size: 0.75em;
            white-space: pre-wrap;
        }

        .regulation-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 3px;
        }

        .gdpr { background: #1a4d80; color: #4da6ff; }
        .ai-act { background: #4d1a80; color: #b366ff; }
        .ccpa { background: #804d1a; color: #ffb366; }

        .highlight { color: #00cc66; font-weight: bold; }
        .highlight-orange { color: #ff9933; font-weight: bold; }
        .highlight-red { color: #ff4444; font-weight: bold; }
        .highlight-purple { color: #9966ff; font-weight: bold; }

        ul, ol {
            margin-left: 20px;
        }

        li {
            margin: 6px 0;
        }

        .slide-number {
            position: absolute;
            bottom: 8mm;
            right: 10mm;
            font-size: 0.8em;
            color: #666;
        }
    """

    slides_html = ""
    for i, slide in enumerate(slides, 1):
        slides_html += f'''
        <div class="slide-page">
            <div class="slide-content">
                {slide}
            </div>
            <div class="slide-number">{i} / {len(slides)}</div>
        </div>
        '''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            {original_styles}
            {print_styles}
        </style>
    </head>
    <body>
        {slides_html}
    </body>
    </html>
    """


def main():
    # Setup paths
    script_dir = Path(__file__).parent
    slides_path = script_dir / "data-safety-ethics-slides.html"
    output_path = script_dir / "data-safety-ethics-slides.pdf"
    debug_path = script_dir / "print-debug.html"

    print(f"Reading slides from: {slides_path}")

    # Read the HTML file
    with open(slides_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract slides
    slides = extract_slides(html_content)
    print(f"Extracted {len(slides)} slides")

    # Create print HTML
    print_html = create_print_html(slides, html_content)

    # Save debug HTML
    with open(debug_path, 'w', encoding='utf-8') as f:
        f.write(print_html)
    print(f"Debug HTML saved to: {debug_path}")

    # Generate PDF
    print(f"Generating PDF: {output_path}")
    HTML(string=print_html, base_url=str(script_dir)).write_pdf(output_path)

    print(f"PDF generated successfully: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
