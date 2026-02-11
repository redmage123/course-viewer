#!/usr/bin/env python3
"""
Generate PDF from Prompt Engineering Masterclass slides using weasyprint.
This bypasses Reveal.js print-pdf mode issues by creating a flat print-ready HTML.
"""

import re
from pathlib import Path
from weasyprint import HTML

# Configuration
SLIDES_FILE = Path(__file__).parent / "prompt-engineering-slides.html"
OUTPUT_PDF = Path(__file__).parent / "prompt-engineering-slides.pdf"

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
        color: #42affa;
        font-size: 2.2em;
        margin: 0 0 15px 0;
        text-align: center;
    }}

    h2 {{
        color: #42affa;
        font-size: 1.6em;
        margin: 0 0 15px 0;
        border-bottom: 3px solid #1a8ad4;
        padding-bottom: 8px;
    }}

    h3 {{
        color: #94a3b8;
        font-size: 1.3em;
        margin: 8px 0;
    }}

    h4 {{
        color: #42affa;
        font-size: 1.1em;
        margin: 8px 0;
    }}

    h5 {{
        color: #42affa;
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

    .card {{
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px 15px;
        border-left: 4px solid #1a8ad4;
    }}

    .card h4 {{
        color: #42affa;
        margin: 0 0 8px 0;
    }}

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
        background-color: rgba(66, 175, 250, 0.15);
        padding: 10px 15px;
        border-radius: 8px;
        border: 2px solid #42affa;
        margin: 10px 0;
        font-size: 0.85em;
    }}

    .prompt-example {{
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 15px;
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
        margin: 8px 0;
        white-space: pre-wrap;
    }}

    .comparison-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 0.8em;
    }}

    th, td {{
        border: 1px solid #334155;
        padding: 8px 10px;
        text-align: left;
    }}

    th {{
        background: rgba(26, 138, 212, 0.4);
        color: #42affa;
        font-weight: bold;
    }}

    tr:nth-child(even) {{
        background: rgba(30, 41, 59, 0.5);
    }}

    .agenda-item {{
        display: flex;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #333;
        font-size: 0.85em;
    }}

    .agenda-time {{
        color: #42affa;
        font-weight: bold;
        min-width: 70px;
        white-space: nowrap;
        margin-right: 12px;
        flex-shrink: 0;
    }}

    .framework-step {{
        display: flex;
        align-items: center;
        margin: 8px 0;
    }}

    .step-number {{
        background: #1a8ad4;
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

    .craft-circle {{
        height: auto;
        min-height: 300px;
    }}

    .craft-center {{
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #1a8ad4, #42affa);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5em;
        font-weight: bold;
        margin: 0 auto;
    }}

    .craft-item {{
        display: inline-block;
        padding: 8px 15px;
        border: 2px solid #1a8ad4;
        border-radius: 20px;
        margin: 5px;
        font-size: 0.85em;
    }}

    .technique-cards {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }}

    .technique-card {{
        background: rgba(255, 255, 255, 0.08);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #334155;
        width: 130px;
        text-align: center;
        font-size: 0.8em;
    }}

    .technique-card .icon {{
        font-size: 1.5em;
        margin-bottom: 5px;
    }}

    .technique-card h4 {{
        font-size: 0.9em;
        margin: 0 0 5px 0;
    }}

    .context-window {{
        background: rgba(13, 17, 23, 0.8);
        border: 2px solid #1a8ad4;
        border-radius: 12px;
        padding: 15px;
        margin: 10px auto;
    }}

    .context-layer {{
        padding: 10px;
        margin: 8px 0;
        border-radius: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .context-layer:nth-child(1) {{ background: rgba(26, 138, 212, 0.3); border-left: 4px solid #1a8ad4; }}
    .context-layer:nth-child(2) {{ background: rgba(0, 204, 102, 0.2); border-left: 4px solid #00cc66; }}
    .context-layer:nth-child(3) {{ background: rgba(255, 153, 51, 0.2); border-left: 4px solid #ff9933; }}
    .context-layer:nth-child(4) {{ background: rgba(153, 51, 255, 0.2); border-left: 4px solid #9933ff; }}

    .layer-icon {{ font-size: 1.5em; }}
    .layer-content {{ flex: 1; }}
    .layer-content h5 {{ margin: 0 0 3px 0; font-size: 0.9em; }}
    .layer-content p {{ margin: 0; font-size: 0.75em; color: #aaa; }}

    .context-stack {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}

    .stack-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 15px;
        background: rgba(255,255,255,0.05);
        border-radius: 6px;
    }}

    .stack-priority {{
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.8em;
    }}

    .priority-high {{ background: #00cc66; }}
    .priority-med {{ background: #1a8ad4; }}
    .priority-low {{ background: #666; }}

    .flow-diagram {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
    }}

    .flow-box {{
        background: rgba(255,255,255,0.08);
        padding: 10px 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        text-align: center;
    }}

    .flow-arrow {{
        color: #00cc66;
        font-size: 1.3em;
    }}

    .prompt-evolution {{
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}

    .prompt-stage {{
        display: flex;
        align-items: center;
        gap: 15px;
    }}

    .stage-indicator {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2em;
        font-weight: bold;
        flex-shrink: 0;
    }}

    .stage-bad {{ background: linear-gradient(135deg, #660000, #990000); }}
    .stage-ok {{ background: linear-gradient(135deg, #665500, #998800); }}
    .stage-good {{ background: linear-gradient(135deg, #006633, #009944); }}

    .stage-content {{
        flex: 1;
        background: #0d1117;
        padding: 10px;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-size: 0.75em;
    }}

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
        content = content.replace('var(--primary)', '#42affa')
        content = content.replace('var(--primary-dark)', '#1a8ad4')
        content = content.replace('var(--accent-green)', '#00cc66')
        content = content.replace('var(--accent-orange)', '#ff9933')

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
    <title>Prompt Engineering Masterclass - Slides</title>
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
