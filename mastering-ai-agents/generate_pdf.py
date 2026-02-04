#!/usr/bin/env python3
"""
Generate PDF from Mastering AI Agents slides using weasyprint.
This bypasses Reveal.js print-pdf mode issues by creating a flat print-ready HTML.
"""

import re
from pathlib import Path
from weasyprint import HTML

# Configuration
SLIDES_FILE = Path(__file__).parent / "mastering-ai-agents-slides.html"
OUTPUT_PDF = Path(__file__).parent / "mastering-ai-agents-slides.pdf"

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

    # Custom print CSS optimized for AI Agents course
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
        color: #f1f5f9;
    }}

    .slide {{
        width: {PAGE_WIDTH};
        height: {PAGE_HEIGHT};
        padding: 25px 35px;
        page-break-after: always;
        page-break-inside: avoid;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
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
        color: #42affa;
        font-size: 2.4em;
        margin: 0 0 20px 0;
        text-align: center;
    }}

    h2 {{
        color: #42affa;
        font-size: 1.8em;
        margin: 0 0 20px 0;
    }}

    h3 {{
        color: #94a3b8;
        font-size: 1.4em;
        margin: 10px 0;
    }}

    h4 {{
        color: #42affa;
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
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .card h4 {{
        color: #42affa;
        margin: 0 0 10px 0;
    }}

    /* Highlight boxes */
    .highlight-box {{
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px 20px;
        border-radius: 5px;
        border-left: 4px solid #42affa;
        margin: 15px 0;
    }}

    .warning-box {{
        background-color: rgba(255, 152, 0, 0.2);
        padding: 15px 20px;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
        margin: 15px 0;
    }}

    .success-box {{
        background-color: rgba(76, 175, 80, 0.2);
        padding: 15px 20px;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
        margin: 15px 0;
    }}

    /* Code blocks */
    pre {{
        background: #0d1117;
        border: 2px solid #42affa;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.75em;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 10px 0;
        max-height: none;
    }}

    pre code {{
        background: none;
        padding: 0;
        font-size: inherit;
    }}

    code {{
        background: rgba(66, 175, 250, 0.2);
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9em;
    }}

    /* Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.85em;
    }}

    th, td {{
        border: 1px solid #334155;
        padding: 10px 12px;
        text-align: left;
    }}

    th {{
        background: rgba(66, 175, 250, 0.3);
        color: #42affa;
        font-weight: bold;
    }}

    tr:nth-child(even) {{
        background: rgba(30, 41, 59, 0.5);
    }}

    /* Diagram container - hide SVG animations for print */
    .diagram-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }}

    .diagram-container svg {{
        max-width: 100%;
        height: auto;
    }}

    /* Hide animated elements that don't work in print */
    .agent-visual,
    .swarm-container,
    .protocol-visual {{
        display: none;
    }}

    /* Slide number */
    .slide-number {{
        position: absolute;
        bottom: 12px;
        right: 25px;
        font-size: 0.9em;
        color: #64748b;
    }}

    /* Hide inline animation styles */
    [style*="animation"] {{
        animation: none !important;
    }}

    /* Remove animation delays and effects */
    * {{
        animation: none !important;
        transition: none !important;
    }}

    /* SVG animations - make static */
    svg animate {{
        display: none;
    }}

    /* Make all SVG elements visible */
    svg rect, svg circle, svg path, svg text {{
        opacity: 1 !important;
    }}

    /* Agent visual - simple static version for print */
    .agent-node {{
        display: none;
    }}

    /* Flow boxes for diagrams */
    .flow-box {{
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 1px solid #42affa;
        border-radius: 8px;
        padding: 12px 18px;
        text-align: center;
    }}

    .flow-arrow {{
        color: #42affa;
        font-size: 1.5em;
    }}

    /* Protocol agents */
    .protocol-agent {{
        text-align: center;
        padding: 10px;
    }}

    .agent-icon {{
        font-size: 2em;
    }}

    /* BDI and neural visuals */
    .bdi-stack, .neural-visual {{
        display: flex;
        flex-direction: column;
        gap: 10px;
        align-items: center;
    }}

    .bdi-layer {{
        padding: 15px 30px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        min-width: 150px;
    }}

    .bdi-layer.beliefs {{
        background: linear-gradient(135deg, #42affa, #2196f3);
    }}

    .bdi-layer.desires {{
        background: linear-gradient(135deg, #50c878, #4caf50);
    }}

    .bdi-layer.intentions {{
        background: linear-gradient(135deg, #ff6b6b, #f44336);
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
        is_center = 'class="center"' in content or content.startswith('<h1')

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
    <title>Mastering AI Agents - Course Slides</title>
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
