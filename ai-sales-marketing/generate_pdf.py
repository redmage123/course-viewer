#!/usr/bin/env python3
"""
Generate PDF from AI for Sales and Marketing slides using weasyprint.
This creates a flat print-ready HTML from the custom slide system.
"""

import re
from pathlib import Path
from weasyprint import HTML

# Configuration
SLIDES_FILE = Path(__file__).parent / "ai-sales-marketing-slides.html"
OUTPUT_PDF = Path(__file__).parent / "ai-sales-marketing-slides.pdf"

# Page dimensions (A4 landscape)
PAGE_WIDTH = "297mm"
PAGE_HEIGHT = "210mm"

def extract_slides(html_content: str) -> list[str]:
    """Extract individual slides from the custom HTML."""
    slides = []

    # Find all slide div positions
    slide_starts = []
    for match in re.finditer(r'<div class="slide[^"]*"[^>]*id="slide(\d+)"[^>]*>', html_content):
        slide_starts.append((int(match.group(1)), match.start(), match.end()))

    # Sort by slide number
    slide_starts.sort(key=lambda x: x[0])

    # Find the navigation div as the end marker
    nav_match = re.search(r'<!-- Navigation -->', html_content)
    end_pos = nav_match.start() if nav_match else len(html_content)

    # Extract each slide's content
    for i, (slide_num, start, content_start) in enumerate(slide_starts):
        # Determine end position
        if i + 1 < len(slide_starts):
            end = slide_starts[i + 1][1]
        else:
            end = end_pos

        # Extract the slide HTML
        slide_html = html_content[start:end]

        # Find matching closing div - count depth
        depth = 0
        pos = 0
        content_end = None
        while pos < len(slide_html):
            if slide_html[pos:pos+4] == '<div':
                depth += 1
                pos += 4
            elif slide_html[pos:pos+6] == '</div>':
                depth -= 1
                if depth == 0:
                    content_end = pos
                    break
                pos += 6
            else:
                pos += 1

        if content_end:
            # Extract inner content (after opening tag, before closing tag)
            opening_end = slide_html.find('>')
            inner_content = slide_html[opening_end + 1:content_end].strip()
            slides.append(inner_content)

    return slides

def extract_styles(html_content: str) -> str:
    """Extract CSS styles from the HTML."""
    style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
    return style_match.group(1) if style_match else ""

def create_print_html(slides: list[str], original_styles: str) -> str:
    """Create a print-ready HTML document."""

    # Custom print CSS
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
        background: #1a1a2e;
        color: #ffffff;
    }}

    .slide {{
        width: {PAGE_WIDTH};
        height: {PAGE_HEIGHT};
        padding: 30px 40px;
        page-break-after: always;
        page-break-inside: avoid;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}

    .slide:last-child {{
        page-break-after: auto;
    }}

    /* Title slides */
    .slide.title-slide {{
        justify-content: center;
        align-items: center;
        text-align: center;
    }}

    .slide.section-divider {{
        justify-content: center;
        align-items: center;
        text-align: center;
    }}

    h1 {{
        font-size: 2.2em;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #667eea;
    }}

    h2 {{
        font-size: 1.8em;
        margin-bottom: 18px;
        color: #a5b4fc;
    }}

    h3 {{
        font-size: 1.4em;
        margin-bottom: 15px;
        color: #c4b5fd;
    }}

    h4 {{
        font-size: 1.2em;
        margin-bottom: 12px;
        color: #ddd6fe;
    }}

    p {{
        font-size: 1em;
        line-height: 1.6;
        margin-bottom: 15px;
        color: #e2e8f0;
    }}

    ul, ol {{
        font-size: 0.95em;
        line-height: 1.8;
        margin-left: 25px;
        color: #e2e8f0;
    }}

    li {{
        margin-bottom: 8px;
    }}

    .subtitle {{
        font-size: 1.4em;
        color: #a5b4fc;
        margin-bottom: 20px;
    }}

    .course-info {{
        font-size: 1em;
        color: #94a3b8;
    }}

    /* Two-column layout */
    .two-column {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        flex: 1;
    }}

    .three-column {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        flex: 1;
    }}

    .four-column {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 15px;
        flex: 1;
    }}

    /* Card styles */
    .card {{
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 18px;
    }}

    /* Highlight boxes */
    .highlight-box {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-left: 4px solid #8b5cf6;
        padding: 18px 22px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    .warning-box {{
        background: rgba(245, 158, 11, 0.2);
        border-left: 4px solid #f59e0b;
        padding: 18px 22px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    .success-box {{
        background: rgba(34, 197, 94, 0.2);
        border-left: 4px solid #22c55e;
        padding: 18px 22px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    /* Day badge */
    .day-badge {{
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }}

    /* Section icon */
    .section-icon {{
        font-size: 4em;
        margin-bottom: 20px;
    }}

    /* Stat cards */
    .stat-card {{
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }}

    .stat-value {{
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #667eea;
    }}

    .stat-label {{
        font-size: 0.9em;
        color: #a5b4fc;
        margin-top: 8px;
    }}

    /* Tool cards */
    .tool-card {{
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }}

    .tool-icon {{
        font-size: 2.5em;
        margin-bottom: 10px;
    }}

    .tool-name {{
        font-weight: bold;
        color: #a5b4fc;
        margin-bottom: 5px;
    }}

    .tool-desc {{
        font-size: 0.85em;
        color: #94a3b8;
    }}

    /* Process flow */
    .process-flow {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin: 20px 0;
        gap: 10px;
    }}

    .process-step {{
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
    }}

    .process-icon {{
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5em;
        margin-bottom: 10px;
    }}

    .process-arrow {{
        font-size: 1.5em;
        color: #6366f1;
        margin-top: 25px;
    }}

    .process-label {{
        font-size: 0.85em;
        color: #a5b4fc;
    }}

    /* AI Wheel - simplified for print */
    .ai-wheel-container {{
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }}

    .ai-wheel {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        max-width: 500px;
    }}

    .wheel-center {{
        grid-column: 2;
        grid-row: 2;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 50%;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1em;
        font-weight: bold;
        text-align: center;
        margin: auto;
    }}

    .wheel-segment {{
        background: rgba(99, 102, 241, 0.2);
        border: 2px solid rgba(139, 92, 246, 0.5);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }}

    .wheel-segment .icon {{
        font-size: 1.5em;
        margin-bottom: 5px;
    }}

    .wheel-segment .label {{
        font-size: 0.8em;
        color: #a5b4fc;
    }}

    /* Score meter - simplified for print */
    .score-container {{
        margin: 20px 0;
    }}

    .score-meter {{
        width: 100%;
        height: 30px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        overflow: hidden;
    }}

    .score-fill {{
        height: 100%;
        border-radius: 15px;
    }}

    .score-fill.low {{ background: linear-gradient(90deg, #ef4444, #f97316); width: 30%; }}
    .score-fill.medium {{ background: linear-gradient(90deg, #f59e0b, #eab308); width: 60%; }}
    .score-fill.high {{ background: linear-gradient(90deg, #22c55e, #10b981); width: 85%; }}

    .score-labels {{
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
        font-size: 0.8em;
        color: #94a3b8;
    }}

    /* Customer journey */
    .customer-journey {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 20px 0;
        gap: 8px;
    }}

    .journey-step {{
        text-align: center;
        flex: 1;
    }}

    .journey-icon {{
        font-size: 1.5em;
        margin-bottom: 5px;
    }}

    .journey-label {{
        font-size: 0.75em;
        color: #a5b4fc;
    }}

    .journey-arrow {{
        font-size: 1.2em;
        color: #6366f1;
    }}

    /* Comparison table */
    .comparison-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.85em;
    }}

    .comparison-table th,
    .comparison-table td {{
        border: 1px solid rgba(139, 92, 246, 0.3);
        padding: 10px 12px;
        text-align: left;
    }}

    .comparison-table th {{
        background: rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        font-weight: bold;
    }}

    .comparison-table tr:nth-child(even) {{
        background: rgba(99, 102, 241, 0.1);
    }}

    /* Framework boxes */
    .framework-box {{
        background: rgba(99, 102, 241, 0.1);
        border: 2px solid rgba(139, 92, 246, 0.4);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }}

    .framework-letter {{
        font-size: 1.8em;
        font-weight: bold;
        color: #8b5cf6;
        margin-right: 12px;
    }}

    /* Tip box */
    .tip-box {{
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
        border-left: 4px solid #22c55e;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
    }}

    /* Code/prompt examples */
    .prompt-example {{
        background: #0f172a;
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 8px;
        padding: 15px;
        font-family: 'Consolas', monospace;
        font-size: 0.85em;
        white-space: pre-wrap;
        margin: 10px 0;
    }}

    /* Checklist */
    .checklist {{
        list-style: none;
        padding-left: 0;
    }}

    .checklist li {{
        padding-left: 28px;
        position: relative;
        margin-bottom: 10px;
    }}

    .checklist li:before {{
        content: "✓";
        position: absolute;
        left: 0;
        color: #22c55e;
        font-weight: bold;
    }}

    /* Slide number */
    .slide-number {{
        position: absolute;
        bottom: 15px;
        right: 30px;
        font-size: 0.9em;
        color: #64748b;
    }}

    /* Remove animations for print */
    * {{
        animation: none !important;
        transition: none !important;
    }}

    .animated-list li {{
        opacity: 1 !important;
    }}
    """

    # Build the HTML document
    slides_html = ""
    for i, slide_content in enumerate(slides, 1):
        content = slide_content.strip()
        if not content:
            continue

        # Determine slide class
        slide_class = "slide"
        if 'title-slide' in content or (i == 1):
            slide_class = "slide title-slide"
        elif 'section-divider' in content:
            slide_class = "slide section-divider"

        slides_html += f'''
        <div class="{slide_class}">
            {content}
            <div class="slide-number">{i}</div>
        </div>
        '''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Introduction to AI for Sales and Marketing</title>
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

    # Extract original styles for reference
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
