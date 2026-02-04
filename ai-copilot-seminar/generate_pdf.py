#!/usr/bin/env python3
"""
Generate PDF from AI Copilot Seminar slides using weasyprint.
This bypasses Reveal.js print-pdf mode issues by creating a flat print-ready HTML.
"""

import re
from pathlib import Path
from weasyprint import HTML

# Configuration
SLIDES_FILE = Path(__file__).parent / "ai-copilot-slides.html"
OUTPUT_PDF = Path(__file__).parent / "ai-copilot-slides.pdf"

# Page dimensions (A4 landscape)
PAGE_WIDTH = "297mm"
PAGE_HEIGHT = "210mm"

def extract_slides(html_content: str) -> list[str]:
    """Extract individual slides from the Reveal.js HTML."""
    # Find the slides container - more flexible pattern
    slides_match = re.search(r'<div class="slides">(.*)</div>\s*</div>\s*<button',
                            html_content, re.DOTALL)
    if not slides_match:
        # Try alternative pattern
        slides_match = re.search(r'<div class="slides">(.*?)</div>\s*</div>\s*<script',
                                html_content, re.DOTALL)
    if not slides_match:
        raise ValueError("Could not find slides container")

    slides_content = slides_match.group(1)

    # Parse sections - handle nested sections (vertical slides)
    slides = []

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

def create_print_html(slides: list[str]) -> str:
    """Create a print-ready HTML document."""

    # Custom print CSS optimized for AI Copilot slides
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
        font-size: 12pt;
    }}

    .slide:last-child {{
        page-break-after: auto;
    }}

    /* Center class for title slides */
    .slide.center {{
        justify-content: center;
        align-items: center;
        text-align: center;
    }}

    h1 {{
        color: #4da6ff;
        font-size: 2.4em;
        margin: 0 0 20px 0;
        text-align: center;
    }}

    h2 {{
        color: #4da6ff;
        font-size: 1.8em;
        margin: 0 0 20px 0;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 10px;
    }}

    h3 {{
        color: #94a3b8;
        font-size: 1.4em;
        margin: 10px 0;
    }}

    h4 {{
        color: #4da6ff;
        font-size: 1.2em;
        margin: 10px 0;
    }}

    p {{
        margin: 10px 0;
        line-height: 1.5;
        font-size: 1em;
    }}

    ul, ol {{
        margin: 10px 0;
        padding-left: 25px;
    }}

    li {{
        margin: 6px 0;
        line-height: 1.4;
        font-size: 0.95em;
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
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #0066cc;
    }}

    .card h4 {{
        color: #4da6ff;
        margin: 0 0 10px 0;
    }}

    /* Tip and warning boxes */
    .tip-box {{
        background-color: rgba(0, 204, 102, 0.15);
        padding: 15px 20px;
        border-radius: 5px;
        border-left: 4px solid #00cc66;
        margin: 15px 0;
    }}

    .warning-box {{
        background-color: rgba(255, 153, 51, 0.15);
        padding: 15px 20px;
        border-radius: 5px;
        border-left: 4px solid #ff9933;
        margin: 15px 0;
    }}

    .exercise-box {{
        background-color: rgba(77, 166, 255, 0.15);
        padding: 15px 20px;
        border-radius: 8px;
        border: 2px solid #4da6ff;
        margin: 15px 0;
    }}

    /* Code blocks */
    pre {{
        background: #0d1117;
        border: 2px solid #0066cc;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.75em;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 10px 0;
    }}

    .prompt-example {{
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.8em;
        margin: 10px 0;
    }}

    /* Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.85em;
    }}

    .comparison-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    th, td {{
        border: 1px solid #334155;
        padding: 10px 12px;
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

    /* Agenda items */
    .agenda-item {{
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #333;
    }}

    .agenda-time {{
        color: #4da6ff;
        font-weight: bold;
        width: 70px;
        flex-shrink: 0;
    }}

    /* Framework steps */
    .framework-step {{
        display: flex;
        align-items: center;
        margin: 12px 0;
    }}

    .step-number {{
        background: #0066cc;
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 12px;
        flex-shrink: 0;
    }}

    /* RAG Pipeline */
    .rag-pipeline {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        padding: 20px;
    }}

    .pipeline-stage {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 15px 12px;
        border-radius: 10px;
        border: 2px solid #0066cc;
        text-align: center;
        width: 110px;
    }}

    .pipeline-stage .icon {{
        font-size: 1.8em;
        margin-bottom: 8px;
    }}

    .pipeline-stage h4 {{
        margin: 0 0 5px 0;
        font-size: 0.85em;
    }}

    .pipeline-stage p {{
        margin: 0;
        font-size: 0.7em;
        color: #aaa;
    }}

    .pipeline-arrow {{
        font-size: 1.3em;
        color: #00cc66;
    }}

    /* Copilot Architecture */
    .copilot-arch {{
        display: flex;
        flex-direction: column;
        gap: 15px;
        max-width: 650px;
        margin: 0 auto;
    }}

    .arch-layer {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px;
        border-radius: 10px;
    }}

    .arch-layer:nth-child(1) {{ background: linear-gradient(135deg, #1a4d30, #2d7a4d); }}
    .arch-layer:nth-child(2) {{ background: linear-gradient(135deg, #0d3366, #1a5599); }}
    .arch-layer:nth-child(3) {{ background: linear-gradient(135deg, #4d1a66, #7a2d99); }}
    .arch-layer:nth-child(4) {{ background: linear-gradient(135deg, #664d00, #997300); }}

    .arch-layer .icon {{
        font-size: 2em;
    }}

    .arch-layer h4 {{
        margin: 0 0 5px 0;
        font-size: 1em;
    }}

    .arch-layer p {{
        margin: 0;
        font-size: 0.85em;
        opacity: 0.9;
    }}

    /* Document flow */
    .doc-flow {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        padding: 15px;
    }}

    .doc-step {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }}

    .doc-step:nth-child(1) {{ border-left: 4px solid #ff6b6b; }}
    .doc-step:nth-child(2) {{ border-left: 4px solid #ffd93d; }}
    .doc-step:nth-child(3) {{ border-left: 4px solid #4da6ff; }}
    .doc-step:nth-child(4) {{ border-left: 4px solid #00cc66; }}

    .doc-step .icon {{
        font-size: 1.8em;
        margin-bottom: 8px;
    }}

    .doc-step h4 {{
        margin: 0 0 5px 0;
        font-size: 0.9em;
    }}

    .doc-step p {{
        margin: 0;
        font-size: 0.75em;
        color: #aaa;
    }}

    /* Knowledge base visual */
    .kb-visual {{
        display: grid;
        grid-template-columns: 1fr 60px 1fr;
        align-items: center;
        gap: 10px;
        padding: 15px;
    }}

    .kb-sources {{
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}

    .kb-source {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 10px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .kb-source .icon {{
        font-size: 1.2em;
    }}

    .kb-source span {{
        font-size: 0.8em;
    }}

    .kb-arrows {{
        display: flex;
        flex-direction: column;
        gap: 5px;
        align-items: center;
    }}

    .kb-arrow {{
        color: #00cc66;
        font-size: 1em;
    }}

    .kb-database {{
        background: linear-gradient(135deg, #0066cc, #4da6ff);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }}

    .kb-database .icon {{
        font-size: 2.5em;
        margin-bottom: 8px;
    }}

    .kb-database h4 {{
        margin: 0;
        font-size: 1em;
    }}

    /* Tool cards */
    .tool-cards {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        padding: 15px;
    }}

    .tool-card {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 18px;
        border-radius: 12px;
        border: 2px solid #0066cc;
        text-align: center;
    }}

    .tool-card .icon {{
        font-size: 2em;
        margin-bottom: 10px;
    }}

    .tool-card h4 {{
        margin: 0 0 8px 0;
        font-size: 0.95em;
    }}

    .tool-card p {{
        font-size: 0.75em;
        color: #aaa;
        margin: 0 0 8px 0;
    }}

    .tool-card .tag {{
        display: inline-block;
        background: #0066cc;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7em;
    }}

    /* Use case matrix */
    .usecase-matrix {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        padding: 15px;
    }}

    .usecase-card {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 18px;
        border-radius: 12px;
    }}

    .usecase-card:nth-child(1) {{ border-top: 4px solid #00cc66; }}
    .usecase-card:nth-child(2) {{ border-top: 4px solid #4da6ff; }}
    .usecase-card:nth-child(3) {{ border-top: 4px solid #ff9933; }}
    .usecase-card:nth-child(4) {{ border-top: 4px solid #9933ff; }}

    .usecase-card .icon {{
        font-size: 1.5em;
        margin-bottom: 8px;
    }}

    .usecase-card h4 {{
        margin: 0 0 8px 0;
        font-size: 1em;
    }}

    .usecase-card p {{
        margin: 0 0 8px 0;
        font-size: 0.8em;
        color: #aaa;
    }}

    .usecase-card ul {{
        margin: 0;
        padding-left: 18px;
        font-size: 0.75em;
    }}

    .usecase-card li {{
        margin: 4px 0;
    }}

    /* Chunk visual */
    .chunk-visual {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}

    .chunk-doc {{
        background: #0d1117;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #30363d;
    }}

    .chunk-doc h4 {{
        margin: 0 0 10px 0;
    }}

    .chunk-row {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }}

    .chunk {{
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.75em;
        border-left: 3px solid #0066cc;
    }}

    .chunk:nth-child(1) {{ border-left-color: #ff6b6b; }}
    .chunk:nth-child(2) {{ border-left-color: #ffd93d; }}
    .chunk:nth-child(3) {{ border-left-color: #4da6ff; }}
    .chunk:nth-child(4) {{ border-left-color: #00cc66; }}
    .chunk:nth-child(5) {{ border-left-color: #9933ff; }}

    /* Slide number */
    .slide-number {{
        position: absolute;
        bottom: 12px;
        right: 25px;
        font-size: 0.9em;
        color: #64748b;
    }}

    /* Hide animations for print */
    * {{
        animation: none !important;
        transition: none !important;
    }}

    /* ITAG logo */
    .itag-logo {{
        position: absolute;
        bottom: 10px;
        left: 20px;
        font-size: 0.7em;
        color: #64748b;
    }}
    """

    # Build the HTML document
    slides_html = ""
    for i, slide_content in enumerate(slides, 1):
        # Clean up the slide content
        content = slide_content.strip()
        if not content:
            continue

        # Check if this is a center slide
        is_center = 'style="text-align: center' in content or content.startswith('<div class="slide-content" style="text-align: center')

        # Remove animation styles from content
        content = re.sub(r'style="[^"]*animation[^"]*"', '', content)

        # Add slide wrapper with number
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
    <title>Build Your Own AI Copilot - Course Slides</title>
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

    # Create print-ready HTML
    print_html = create_print_html(slides)

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
