#!/usr/bin/env python3
"""
Generate PDF from take-home exercise markdown using weasyprint.
"""

import markdown
from pathlib import Path
from weasyprint import HTML

# Configuration
MARKDOWN_FILE = Path(__file__).parent / "take-home-exercise.md"
OUTPUT_PDF = Path(__file__).parent / "take-home-exercise.pdf"

def create_html_from_markdown(md_content: str) -> str:
    """Convert markdown to styled HTML for PDF generation."""

    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    html_content = md.convert(md_content)

    css = """
    @page {
        size: A4;
        margin: 20mm 15mm;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #1a1a2e;
        max-width: 100%;
    }

    h1 {
        color: #0066cc;
        font-size: 22pt;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 10px;
        margin-top: 30px;
        page-break-after: avoid;
    }

    h2 {
        color: #16213e;
        font-size: 16pt;
        margin-top: 25px;
        border-bottom: 2px solid #4da6ff;
        padding-bottom: 5px;
        page-break-after: avoid;
    }

    h3 {
        color: #0066cc;
        font-size: 13pt;
        margin-top: 20px;
        page-break-after: avoid;
    }

    h4 {
        color: #16213e;
        font-size: 11pt;
        margin-top: 15px;
        page-break-after: avoid;
    }

    p { margin: 10px 0; }

    ul, ol {
        margin: 10px 0;
        padding-left: 25px;
    }

    li { margin: 5px 0; }

    hr {
        border: none;
        border-top: 1px solid #ccc;
        margin: 20px 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }

    th, td {
        border: 1px solid #dee2e6;
        padding: 8px 10px;
        text-align: left;
    }

    th {
        background: #0066cc;
        color: white;
        font-weight: bold;
    }

    tr:nth-child(even) {
        background: #f8f9fa;
    }

    h1, h2 { page-break-after: avoid; }
    pre, table { page-break-inside: avoid; }

    body::before {
        content: "ITAG Skillnet AI Advantage";
        display: block;
        text-align: right;
        font-size: 9pt;
        color: #666;
        margin-bottom: 20px;
    }
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Take-Home Exercise: AI's Impact on Work &amp; Rolling Out AI Successfully</title>
    <style>
    {css}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    return html

def main():
    print(f"Reading markdown from: {MARKDOWN_FILE}")
    md_content = MARKDOWN_FILE.read_text(encoding='utf-8')
    html = create_html_from_markdown(md_content)

    print(f"Generating PDF: {OUTPUT_PDF}")
    HTML(string=html).write_pdf(OUTPUT_PDF)

    print(f"PDF generated successfully: {OUTPUT_PDF}")
    print(f"File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
