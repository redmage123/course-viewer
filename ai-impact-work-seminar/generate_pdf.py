#!/usr/bin/env python3
"""
Generate PDF from AI Impact on Work seminar slides using weasyprint.
This bypasses Reveal.js print-pdf mode issues by creating a flat print-ready HTML.
"""

import re
from pathlib import Path
from weasyprint import HTML

# Configuration
SLIDES_FILE = Path(__file__).parent / "ai-impact-work-slides.html"
OUTPUT_PDF = Path(__file__).parent / "ai-impact-work-slides.pdf"

# Page dimensions (A4 landscape)
PAGE_WIDTH = "297mm"
PAGE_HEIGHT = "210mm"

def extract_slides(html_content: str) -> list[str]:
    """Extract individual slides from the Reveal.js HTML."""
    slides_match = re.search(r'<div class="slides">(.*)</div>\s*</div>\s*<button',
                            html_content, re.DOTALL)
    if not slides_match:
        slides_match = re.search(r'<div class="slides">(.*?)</div>\s*</div>\s*<script',
                                html_content, re.DOTALL)
    if not slides_match:
        raise ValueError("Could not find slides container")

    slides_content = slides_match.group(1)

    slides = []

    def process_section(content: str, depth: int = 0) -> list[str]:
        """Recursively process sections, flattening nested ones."""
        results = []
        nested = re.findall(r'<section[^>]*>(.*?)</section>', content, re.DOTALL)

        if nested and depth == 0:
            for nested_content in nested:
                results.extend(process_section(nested_content, depth + 1))
        else:
            if content.strip():
                results.append(content)

        return results

    pos = 0
    while True:
        start = slides_content.find('<section', pos)
        if start == -1:
            break

        depth = 0
        i = start
        while i < len(slides_content):
            if slides_content[i:i+8] == '<section':
                depth += 1
                i += 8
            elif slides_content[i:i+10] == '</section>':
                depth -= 1
                if depth == 0:
                    section_html = slides_content[start:i+10]
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

def create_print_html(slides: list[str]) -> str:
    """Create a print-ready HTML document."""

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
        background: #0a0a1a;
        color: #f1f5f9;
    }}

    .slide {{
        width: {PAGE_WIDTH};
        height: {PAGE_HEIGHT};
        padding: 25px 35px;
        page-break-after: always;
        page-break-inside: avoid;
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        font-size: 12pt;
    }}

    .slide:last-child {{
        page-break-after: auto;
    }}

    .slide.center {{
        justify-content: center;
        align-items: center;
        text-align: center;
    }}

    h1 {{
        color: #4da6ff;
        font-size: 2.2em;
        margin: 0 0 15px 0;
        text-align: center;
    }}

    h2 {{
        color: #4da6ff;
        font-size: 1.6em;
        margin: 0 0 15px 0;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 8px;
    }}

    h3 {{
        color: #94a3b8;
        font-size: 1.3em;
        margin: 8px 0;
    }}

    h4 {{
        color: #4da6ff;
        font-size: 1.1em;
        margin: 8px 0;
    }}

    h5 {{
        color: #4da6ff;
        font-size: 1em;
        margin: 6px 0;
    }}

    p {{
        margin: 8px 0;
        line-height: 1.5;
        font-size: 0.9em;
    }}

    ul, ol {{
        margin: 8px 0;
        padding-left: 25px;
    }}

    li {{
        margin: 5px 0;
        line-height: 1.4;
        font-size: 0.9em;
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
        gap: 12px;
        flex: 1;
        font-size: 0.85em;
    }}

    /* Card styles */
    .card {{
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px 15px;
        border-left: 4px solid #0066cc;
    }}

    .card h4 {{
        color: #4da6ff;
        margin: 0 0 8px 0;
    }}

    /* Stat cards */
    .stat-card {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 15px 12px;
        text-align: center;
        border: 1px solid #334155;
    }}

    .stat-number {{
        font-size: 1.6em;
        font-weight: 800;
        color: #4da6ff;
        margin-bottom: 5px;
    }}

    .stat-label {{
        font-size: 0.75em;
        color: #94a3b8;
        line-height: 1.3;
    }}

    .stat-source {{
        font-size: 0.55em;
        color: #666;
        margin-top: 5px;
    }}

    /* Tip and warning boxes */
    .tip-box {{
        background-color: rgba(0, 204, 102, 0.15);
        padding: 10px 15px;
        border-radius: 5px;
        border-left: 4px solid #00cc66;
        margin: 10px 0;
        font-size: 0.85em;
    }}

    .warning-box {{
        background-color: rgba(255, 153, 51, 0.15);
        padding: 10px 15px;
        border-radius: 5px;
        border-left: 4px solid #ff9933;
        margin: 10px 0;
        font-size: 0.85em;
    }}

    .exercise-box {{
        background-color: rgba(77, 166, 255, 0.15);
        padding: 10px 15px;
        border-radius: 8px;
        border: 2px solid #4da6ff;
        margin: 10px 0;
        font-size: 0.85em;
    }}

    /* Case study */
    .case-study {{
        background: linear-gradient(135deg, rgba(0,102,204,0.15), rgba(0,204,102,0.1));
        border-radius: 8px;
        padding: 10px 15px;
        border-left: 4px solid #0066cc;
        margin: 10px 0;
    }}

    /* Agenda items */
    .agenda-item {{
        display: flex;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #333;
        font-size: 0.85em;
    }}

    .agenda-time {{
        color: #4da6ff;
        font-weight: bold;
        min-width: 70px;
        white-space: nowrap;
        margin-right: 12px;
        flex-shrink: 0;
    }}

    /* Framework steps */
    .framework-step {{
        display: flex;
        align-items: center;
        margin: 8px 0;
    }}

    .step-number {{
        background: #0066cc;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
        flex-shrink: 0;
        font-size: 0.85em;
    }}

    /* LAUNCH grid */
    .launch-grid {{
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 8px;
        margin: 10px auto;
        max-width: 700px;
    }}

    .launch-grid-item {{
        text-align: center;
        padding: 10px 5px;
        border-radius: 10px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-top: 3px solid #0066cc;
    }}

    .launch-grid-letter {{
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #0066cc, #4da6ff);
        border-radius: 50%;
        font-size: 1.3em;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 6px;
        color: white;
    }}

    .launch-grid-label {{
        font-size: 0.65em;
        color: #ccc;
    }}

    .launch-letter {{
        color: #4da6ff;
        font-weight: bold;
    }}

    /* Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 0.8em;
    }}

    .comparison-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    th, td {{
        border: 1px solid #334155;
        padding: 8px 10px;
        text-align: left;
    }}

    th {{
        background: rgba(0, 102, 204, 0.4);
        color: #4da6ff;
        font-weight: bold;
    }}

    tr:nth-child(even) {{
        background: rgba(30, 41, 59, 0.5);
    }}

    /* Pilot scoring table */
    .pilot-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .score-low {{
        color: #ff6666;
    }}

    .score-high {{
        color: #00cc66;
    }}

    /* Timeline */
    .timeline {{
        margin: 10px 0;
    }}

    .timeline-item {{
        display: flex;
        margin-bottom: 8px;
        padding: 8px;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        border-left: 3px solid #0066cc;
    }}

    .timeline-week {{
        color: #4da6ff;
        font-weight: bold;
        min-width: 80px;
        flex-shrink: 0;
        font-size: 0.85em;
    }}

    .timeline-content {{
        flex: 1;
        font-size: 0.85em;
    }}

    /* Readiness radar */
    .readiness-radar {{
        margin: 10px 0;
    }}

    .radar-dimension {{
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }}

    .radar-label {{
        width: 120px;
        font-size: 0.85em;
        flex-shrink: 0;
    }}

    .radar-bar-bg {{
        flex: 1;
        height: 20px;
        background: #1a1a2e;
        border-radius: 10px;
        margin: 0 10px;
        overflow: hidden;
    }}

    .radar-bar-fill {{
        height: 100%;
        width: var(--fill-width, 50%);
        border-radius: 10px;
    }}

    .radar-score {{
        font-weight: bold;
        font-size: 0.9em;
        width: 40px;
        text-align: right;
    }}

    /* ROI metrics grid */
    .roi-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }}

    /* Slide number */
    .slide-number {{
        position: absolute;
        bottom: 12px;
        right: 25px;
        font-size: 0.9em;
        color: #64748b;
    }}

    /* ITAG branding */
    .itag-logo {{
        position: absolute;
        bottom: 10px;
        left: 20px;
        font-size: 0.7em;
        color: #64748b;
    }}

    /* Hide animations for print */
    * {{
        animation: none !important;
        transition: none !important;
    }}

    /* Ensure elements with opacity:0 from animations are visible */
    [style*="opacity: 0"] {{
        opacity: 1 !important;
    }}
    """

    # Build the HTML document
    slides_html = ""
    for i, slide_content in enumerate(slides, 1):
        content = slide_content.strip()
        if not content:
            continue

        is_center = 'style="text-align: center' in content
        # Remove animation styles
        content = re.sub(r'opacity:\s*0;\s*animation:[^;"]*;?', '', content)
        content = re.sub(r'animation:[^;"]*;?', '', content)
        # Replace CSS var references with actual values
        content = content.replace('var(--itag-blue)', '#0066cc')
        content = content.replace('var(--itag-light)', '#4da6ff')
        content = content.replace('var(--accent-green)', '#00cc66')
        content = content.replace('var(--accent-orange)', '#ff9933')
        content = content.replace('var(--accent-red)', '#ff4444')

        center_class = " center" if is_center else ""
        slides_html += f'''
        <div class="slide{center_class}">
            {content}
            <div class="slide-number">{i}</div>
        </div>
        '''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI's Impact on Work & Rolling Out AI Successfully - Slides</title>
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

    html_content = SLIDES_FILE.read_text(encoding='utf-8')

    slides = extract_slides(html_content)
    print(f"Extracted {len(slides)} slides")

    print_html = create_print_html(slides)

    print(f"Generating PDF: {OUTPUT_PDF}")
    HTML(string=print_html).write_pdf(OUTPUT_PDF)

    print(f"PDF generated successfully: {OUTPUT_PDF}")
    print(f"File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
