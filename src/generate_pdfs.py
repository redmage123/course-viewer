#!/usr/bin/env python3
"""
Generate PDF versions of all course slides.
Uses pyppeteer (headless Chrome) for accurate rendering.
"""
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyppeteer import launch

# Slide files to convert
SLIDES = [
    {
        'html': 'ai-plain-english/ai-plain-english-slides.html',
        'pdf': 'ai-plain-english/ai-plain-english-slides.pdf'
    },
    {
        'html': 'out/mastering-llms-slides.html',
        'pdf': 'out/mastering-llms-slides.pdf'
    },
    {
        'html': 'out/mastering-llms-part1-slides.html',
        'pdf': 'out/mastering-llms-part1-slides.pdf'
    },
    {
        'html': 'python-fundamentals/python-fundamentals-slides.html',
        'pdf': 'python-fundamentals/python-fundamentals-slides.pdf'
    }
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def generate_pdf(browser, html_path, pdf_path):
    """Generate a PDF from an HTML file."""
    full_html_path = os.path.join(BASE_DIR, html_path)
    full_pdf_path = os.path.join(BASE_DIR, pdf_path)

    if not os.path.exists(full_html_path):
        print(f"  Skipping {html_path} - file not found")
        return False

    print(f"  Converting {html_path}...")

    page = await browser.newPage()

    # Set viewport to presentation size
    await page.setViewport({'width': 1920, 'height': 1080})

    # Load the HTML file
    await page.goto(f'file://{full_html_path}', {'waitUntil': 'networkidle0'})

    # Wait for any animations/fonts to load
    await asyncio.sleep(1)

    # Generate PDF with landscape orientation for slides
    await page.pdf({
        'path': full_pdf_path,
        'format': 'A4',
        'landscape': True,
        'printBackground': True,
        'margin': {
            'top': '0.5cm',
            'bottom': '0.5cm',
            'left': '0.5cm',
            'right': '0.5cm'
        }
    })

    await page.close()

    file_size = os.path.getsize(full_pdf_path)
    print(f"  Created {pdf_path} ({file_size // 1024} KB)")
    return True


async def main():
    print("Generating PDF slides...")
    print(f"Base directory: {BASE_DIR}")
    print()

    # Launch browser
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )

    success_count = 0
    for slide in SLIDES:
        try:
            if await generate_pdf(browser, slide['html'], slide['pdf']):
                success_count += 1
        except Exception as e:
            print(f"  Error converting {slide['html']}: {e}")

    await browser.close()

    print()
    print(f"Generated {success_count}/{len(SLIDES)} PDF files")


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
