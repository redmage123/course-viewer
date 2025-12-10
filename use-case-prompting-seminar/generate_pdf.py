#!/usr/bin/env python3
"""
Generate PDF from Use Case Prompting Seminar slides using weasyprint.
This bypasses Reveal.js print-pdf mode issues by creating a flat print-ready HTML.
"""

import re
from pathlib import Path
from weasyprint import HTML, CSS

# Configuration
SLIDES_FILE = Path(__file__).parent / "use-case-prompting-slides.html"
OUTPUT_PDF = Path(__file__).parent / "use-case-prompting-slides.pdf"

# Page dimensions (A4 landscape)
PAGE_WIDTH = "297mm"
PAGE_HEIGHT = "210mm"

def extract_slides(html_content: str) -> list[str]:
    """Extract individual slides from the Reveal.js HTML."""
    # Find the slides container
    slides_match = re.search(r'<div class="slides">(.*?)</div>\s*</div>\s*<script',
                            html_content, re.DOTALL)
    if not slides_match:
        raise ValueError("Could not find slides container")

    slides_content = slides_match.group(1)

    # Parse sections - handle nested sections (vertical slides)
    slides = []

    # Find all top-level sections
    section_pattern = r'<section[^>]*>(.*?)</section>'

    def process_section(content: str, depth: int = 0) -> list[str]:
        """Recursively process sections, flattening nested ones."""
        results = []
        # Check if this section contains nested sections
        nested = re.findall(r'<section[^>]*>(.*?)</section>', content, re.DOTALL)

        if nested and depth == 0:
            # This is a vertical stack - process each nested section
            for nested_content in nested:
                results.extend(process_section(nested_content, depth + 1))
        else:
            # This is a leaf section - add it
            if content.strip():
                results.append(content)

        return results

    # Find all top-level sections
    pos = 0
    while True:
        # Find next section start
        start = slides_content.find('<section', pos)
        if start == -1:
            break

        # Find matching closing tag (handle nesting)
        depth = 0
        i = start
        while i < len(slides_content):
            if slides_content[i:i+8] == '<section':
                depth += 1
                i += 8
            elif slides_content[i:i+10] == '</section>':
                depth -= 1
                if depth == 0:
                    # Found matching close
                    section_html = slides_content[start:i+10]
                    # Extract inner content
                    inner = re.match(r'<section[^>]*>(.*)</section>', section_html, re.DOTALL)
                    if inner:
                        processed = process_section(inner.group(1), 0)
                        slides.extend(processed)
                    pos = i + 10
                    break
                i += 10
            else:
                i += 1
        else:
            break

    return slides

def extract_styles(html_content: str) -> str:
    """Extract CSS styles from the HTML."""
    style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
    return style_match.group(1) if style_match else ""

def create_print_html(slides: list[str], original_styles: str) -> str:
    """Create a print-ready HTML document."""

    # Custom print CSS that overrides problematic styles
    print_css = f"""
    @page {{
        size: {PAGE_WIDTH} {PAGE_HEIGHT};
        margin: 0;
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: #0f172a;
        color: #f1f5f9;
    }}

    .slide {{
        width: {PAGE_WIDTH};
        height: {PAGE_HEIGHT};
        padding: 25px 35px;
        page-break-after: always;
        page-break-inside: avoid;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        font-size: 14pt;
    }}

    .slide:last-child {{
        page-break-after: auto;
    }}

    h1 {{
        color: #4da6ff;
        font-size: 2.8em;
        margin: 0 0 25px 0;
        text-align: center;
    }}

    h2 {{
        color: #4da6ff;
        font-size: 2.2em;
        margin: 0 0 25px 0;
        text-align: center;
    }}

    h3 {{
        color: #94a3b8;
        font-size: 1.6em;
        margin: 12px 0;
    }}

    h4 {{
        color: #4da6ff;
        font-size: 1.4em;
        margin: 12px 0;
    }}

    p {{
        margin: 12px 0;
        line-height: 1.6;
        font-size: 1.1em;
    }}

    /* Override inline small font sizes to be readable */
    p[style*="font-size: 0.7em"],
    p[style*="font-size:0.7em"],
    span[style*="font-size: 0.7em"],
    span[style*="font-size:0.7em"] {{
        font-size: 1.2em !important;
    }}

    /* Override dark grey text to be more visible */
    p[style*="color: #666"],
    p[style*="color:#666"],
    span[style*="color: #666"],
    span[style*="color:#666"] {{
        color: #94a3b8 !important;
    }}

    ul, ol {{
        margin: 12px 0;
        padding-left: 30px;
    }}

    li {{
        margin: 8px 0;
        line-height: 1.5;
        font-size: 1.1em;
    }}

    /* Two-column layout */
    .two-column {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        flex: 1;
    }}

    .three-column {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 15px;
        flex: 1;
    }}

    /* Card styles */
    .card {{
        background: rgba(30, 41, 59, 0.8);
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #334155;
        font-size: 1.1em;
    }}

    /* Tip and warning boxes */
    .tip-box {{
        background: linear-gradient(135deg, #0d3320 0%, #1a4d30 100%);
        border-left: 5px solid #00cc66;
        padding: 18px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 1.1em;
    }}

    .warning-box {{
        background: linear-gradient(135deg, #3d2814 0%, #4d3318 100%);
        border-left: 5px solid #ff9933;
        padding: 18px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 1.1em;
    }}

    .exercise-box {{
        background: linear-gradient(135deg, #1a1a3d 0%, #2d2d5c 100%);
        border-left: 5px solid #9966ff;
        padding: 18px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 1.1em;
    }}

    /* Prompt example box */
    .prompt-example {{
        background: #1a1a2e;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 18px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 1em;
        white-space: pre-wrap;
        line-height: 1.6;
    }}

    /* CRAFT diagram - simplified for print */
    .craft-circle {{
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 30px;
        max-width: 800px;
        margin: 20px auto;
    }}

    .craft-center {{
        width: 140px;
        height: 140px;
        background: linear-gradient(135deg, #0066cc, #4da6ff);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2em;
        font-weight: bold;
        color: white;
        order: 3;
    }}

    .craft-item {{
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 2px solid #4da6ff;
        border-radius: 10px;
        padding: 15px 25px;
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 120px;
        position: static !important;
        transform: none !important;
        top: auto !important;
        left: auto !important;
        right: auto !important;
        bottom: auto !important;
    }}

    .craft-item span:first-child {{
        font-size: 1.8em;
        font-weight: bold;
        color: #4da6ff;
    }}

    .craft-item span:last-child {{
        font-size: 1.1em;
        color: #94a3b8;
    }}

    /* Technique cards */
    .technique-cards {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-top: 20px;
    }}

    .technique-card {{
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }}

    .technique-card .icon {{
        font-size: 2.5em;
        margin-bottom: 12px;
    }}

    .technique-card h4 {{
        margin: 8px 0;
        font-size: 1.2em;
    }}

    .technique-card p {{
        font-size: 1em;
        color: #94a3b8;
        margin: 8px 0;
    }}

    /* Agenda items */
    .agenda-item {{
        display: flex;
        align-items: center;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        padding: 14px 20px;
        margin: 10px 0;
        border-left: 4px solid #4da6ff;
        font-size: 1.1em;
    }}

    .agenda-time {{
        color: #4da6ff;
        font-weight: bold;
        min-width: 70px;
        margin-right: 20px;
        font-size: 1.1em;
    }}

    /* Framework steps */
    .framework-step {{
        display: flex;
        align-items: flex-start;
        gap: 18px;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        padding: 15px 20px;
        margin: 12px 0;
        font-size: 1.1em;
    }}

    .step-number {{
        background: linear-gradient(135deg, #0066cc, #4da6ff);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        flex-shrink: 0;
        font-size: 1.1em;
    }}

    /* Matrix for prioritization */
    .matrix-animated {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto;
        gap: 15px;
        flex: 1;
    }}

    .matrix-cell {{
        background: rgba(30, 41, 59, 0.8);
        border-radius: 8px;
        padding: 18px;
        border: 1px solid #334155;
    }}

    .matrix-cell h4 {{
        margin: 0 0 10px 0;
        font-size: 1.3em;
    }}

    .matrix-cell p {{
        margin: 6px 0;
        font-size: 1em;
    }}

    /* Prompt stages */
    .prompt-stages {{
        display: flex;
        flex-direction: column;
        gap: 15px;
    }}

    .prompt-stage {{
        display: flex;
        align-items: flex-start;
        gap: 15px;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        padding: 15px 20px;
        font-size: 1.1em;
    }}

    .stage-indicator {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 1.1em;
    }}

    .stage-bad {{
        background: #ff4444;
    }}

    .stage-medium {{
        background: #ff9933;
    }}

    .stage-good {{
        background: #00cc66;
    }}

    .stage-label {{
        font-weight: bold;
        color: #94a3b8;
        font-size: 1em;
        margin-bottom: 6px;
    }}

    /* Context layers */
    .context-layers {{
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}

    .context-layer {{
        background: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #4da6ff;
        padding: 15px 20px;
        border-radius: 0 8px 8px 0;
        font-size: 1.1em;
    }}

    /* Stack items */
    .context-stack {{
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}

    .stack-item {{
        display: flex;
        align-items: center;
        gap: 15px;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        padding: 14px 20px;
        font-size: 1.1em;
    }}

    /* Flow diagram */
    .flow-diagram {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
        margin: 20px 0;
    }}

    .flow-box {{
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 1px solid #4da6ff;
        border-radius: 8px;
        padding: 15px 20px;
        text-align: center;
        font-size: 1.1em;
    }}

    .flow-arrow {{
        color: #4da6ff;
        font-size: 1.8em;
    }}

    /* Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 1.1em;
    }}

    th, td {{
        border: 1px solid #334155;
        padding: 12px 16px;
        text-align: left;
    }}

    th {{
        background: rgba(0, 102, 204, 0.3);
        color: #4da6ff;
        font-size: 1.1em;
    }}

    tr:nth-child(even) {{
        background: rgba(30, 41, 59, 0.5);
    }}

    /* Footer */
    .itag-footer {{
        position: absolute;
        bottom: 12px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 0.9em;
        color: #64748b;
    }}

    /* Slide number */
    .slide-number {{
        position: absolute;
        bottom: 12px;
        right: 25px;
        font-size: 1em;
        color: #64748b;
    }}

    /* Code blocks */
    pre, code {{
        background: #0f172a;
        border-radius: 4px;
        padding: 3px 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 1em;
    }}

    pre {{
        padding: 15px 20px;
        overflow-x: auto;
        font-size: 1em;
    }}

    /* Hide animations and fragments */
    .fragment {{
        opacity: 1 !important;
        visibility: visible !important;
    }}
    """

    # Build the HTML document
    slides_html = ""
    for i, slide_content in enumerate(slides, 1):
        # Clean up the slide content
        content = slide_content.strip()
        if not content:
            continue

        # Add slide wrapper with number
        slides_html += f'''
        <div class="slide">
            {content}
            <div class="slide-number">{i}</div>
        </div>
        '''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Use Case Lab & Prompting Foundations - ITAG Skillnet</title>
    <style>
    {print_css}
    </style>
</head>
<body>
{slides_html}
</body>
</html>
"""
    return html

def main():
    print(f"Reading slides from: {SLIDES_FILE}")

    # Read the original HTML
    html_content = SLIDES_FILE.read_text(encoding='utf-8')

    # Extract slides
    slides = extract_slides(html_content)
    print(f"Extracted {len(slides)} slides")

    # Extract styles
    original_styles = extract_styles(html_content)

    # Create print-ready HTML
    print_html = create_print_html(slides, original_styles)

    # Save intermediate HTML for debugging
    debug_html = Path(__file__).parent / "print-debug.html"
    debug_html.write_text(print_html, encoding='utf-8')
    print(f"Debug HTML saved to: {debug_html}")

    # Generate PDF
    print(f"Generating PDF: {OUTPUT_PDF}")
    HTML(string=print_html).write_pdf(OUTPUT_PDF)

    print(f"PDF generated successfully: {OUTPUT_PDF}")
    print(f"File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
