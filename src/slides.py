#!../.venv/bin/python3.12
# slides.py
# Generates LinkedIn carousel PDF
# Produces:
#   out/AI-Elevate_LinkedIn_Carousel.pdf  (ready to upload to LinkedIn)
#   out/slide_01.png through out/slide_07.png  (individual slides)
#
# Usage:
#   pip install pillow reportlab
#   python slides.py --profile linkedin --logo /path/to/logo.png
#
# Notes:
# - Optimized for LinkedIn carousel format (max 10 slides)
# - Square format (1080x1080) for best LinkedIn compatibility
# - Upload the PDF to LinkedIn - it automatically converts to carousel!

import os, math, argparse, re, gc
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# PDF generation for LinkedIn carousel
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

# PDF post-processing to add NewWindow flags
try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DictionaryObject, BooleanObject
    PYPDF_OK = True
except Exception:
    PYPDF_OK = False

# Progress bars
try:
    from tqdm import tqdm
except Exception:
    class tqdm:
        def __init__(self, iterable=None, total=None, desc="", unit="", leave=True, bar_format=None):
            self.iterable = iterable if iterable is not None else range(total or 0)
            self.total = total
            print(f"[...] {desc}")
        def __iter__(self):
            for x in self.iterable: yield x
        def update(self, n=1): pass
        def set_description(self, desc): print(f"[STATUS] {desc}")
        def write(self, msg): print(msg)
        def close(self): pass

# ---------------- Profiles ----------------
# LinkedIn carousel optimized dimensions
PROFILES = {
    "linkedin":  {"W":1080,"H":1080, "mesh_cols":9, "mesh_rows":9, "blur":1},  # Square (recommended)
    "portrait":  {"W":1080,"H":1350, "mesh_cols":9, "mesh_rows":11, "blur":1}, # Portrait
    "landscape": {"W":1080,"H":566,  "mesh_cols":9, "mesh_rows":5, "blur":1},  # Landscape
}

# --------------- Colors & Strings ---------------
# Professional LinkedIn-ready gradient background (lighter, modern)
BG_TOP    = (15, 20, 35)     # Dark blue/black
BG_BOTTOM = (25, 35, 55)     # Slightly lighter dark blue
ACCENT    = (37,99,235)      # Professional blue
ACCENT_DARK = (29,78,216)    # Darker blue for contrast
ACCENT_LIGHT = (147,197,253) # Lighter blue for accents
WHITE     = (255,255,255)
TEXT_DARK = (15,23,42)       # Dark text for readability
TEXT_MID  = (51,65,85)       # Medium dark text
GREY_LIGHT = (148,163,184)   # Light grey for subtle elements

TITLE     = "26% PRODUCTIVITY INCREASE"
SUBTITLE  = "IN JUST 3 HOURS"
TITLE_ATTRIBUTION = "Microsoft/MIT Study, 2024"
TAGLINE   = "The enterprise prompt engineering training"
TAGLINE2  = "your competitors are already using"
QUOTE     = '"AI doesn\'t replace people - it amplifies them."'
QUOTE_ATTR = "AI Elevate Philosophy"

# Unified footer for all slides - brand phrase
FOOTER_ALL_SLIDES = "Join the AI Elevation Movement"
FOOTER_SLIDE_1 = FOOTER_ALL_SLIDES
FOOTER_SLIDE_2_3 = FOOTER_ALL_SLIDES
FOOTER_SLIDE_4_5 = FOOTER_ALL_SLIDES
FOOTER_SLIDE_6 = FOOTER_ALL_SLIDES
FOOTER_SLIDE_7_8 = FOOTER_ALL_SLIDES

# Slide titles - benefit-driven
SLIDE_2_TITLE = "Why 80% See No Impact from AI"
SLIDE_2_SUBTITLE = "(McKinsey, 2024)"
SLIDE_3_TITLE = "Is This Training Right for You?"
SLIDE_4_TITLE = "The 4 Skills That Separate Experts"
SLIDE_4_SUBTITLE = "from Everyone Else"
SLIDE_5_TITLE = "3 Hours That Feel Like 40"
SLIDE_6_TITLE = "The Results (Backed by Data)"
SLIDE_7_TITLE = "Proven Track Record"
SLIDE_8_TITLE = "Download Your Free Resource"

# New CTA with lower barrier
CTA_SUBTITLE = '"The 10 Enterprise Prompts That Save 10 Hours/Week"'
CTA_LINES = [
    "✓ Tested frameworks used by Fortune 500s",
    "✓ Real examples from 500+ trained teams",
    "✓ Ready to use in your business tomorrow",
    "✓ Plus: Free 15-min AI Readiness Call",
]
CTA_BUTTON_TEXT = "GET FREE GUIDE + CONSULTATION →"
CTA_URL = "https://ai-elevate.ai"

# --------------- Helpers ---------------
def sanitize(s: str) -> str:
    """Sanitize text but keep useful symbols like checkmarks and emojis"""
    repl = {
        "\u2014":"-","\u2013":"-","\u2018":"'", "\u2019":"'",
        "\u201C":'"', "\u201D":'"', "\u2022":"-","\u2026":"...",
        "\u00A0":" "
    }
    for k,v in repl.items(): s = s.replace(k,v)
    # Don't strip emojis and useful symbols - only remove problematic characters
    # Keep: ✓ ✗ and emojis (U+2713, U+2717, U+1F300-U+1F9FF)
    return s  # Return without stripping non-ASCII

def load_font(size: int, bold=False, italic=False, serif=False) -> ImageFont.ImageFont:
    # Try multiple common font paths for better cross-platform compatibility
    paths=[]
    if serif:
        # Use Liberation Serif for elegant, stylish text (quotes, etc.)
        if bold and italic:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
                "/System/Library/Fonts/Times.ttc",
                "C:\\Windows\\Fonts\\timesbi.ttf",
            ]
        elif bold:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                "/System/Library/Fonts/Times.ttc",
                "C:\\Windows\\Fonts\\timesbd.ttf",
            ]
        elif italic:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
                "/System/Library/Fonts/Times.ttc",
                "C:\\Windows\\Fonts\\timesi.ttf",
            ]
        else:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/System/Library/Fonts/Times.ttc",
                "C:\\Windows\\Fonts\\times.ttf",
            ]
    else:
        # Use Liberation Sans (modern, clean) instead of blocky DejaVu
        if bold and italic:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "C:\\Windows\\Fonts\\arialbi.ttf",
            ]
        elif bold:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "C:\\Windows\\Fonts\\arialbd.ttf",
            ]
        elif italic:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "C:\\Windows\\Fonts\\ariali.ttf",
            ]
        else:
            paths=[
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "C:\\Windows\\Fonts\\arial.ttf",
            ]

    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue

    # Fallback to default font
    try:
        return ImageFont.load_default()
    except Exception:
        # Ultimate fallback for newer PIL versions
        return ImageFont.load_default(size=size)

def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int,int]:
    text = sanitize(text)
    if hasattr(draw,"textbbox"):
        x0,y0,x1,y1=draw.textbbox((0,0),text,font=font)
        return (x1-x0,y1-y0)
    try:
        return font.getsize(text)
    except Exception:
        return (max(6,font.size//2)*len(text), font.size)

def load_background_image(w, h, bg_path=None):
    """Load and prepare background image from file"""
    # Auto-detect background image
    if bg_path is None:
        candidates = [
            "Screenshot from 2025-11-02 10-23-58.png",
            "bg_neural.png",
            "bg_neural.webp",
            "background.png"
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                bg_path = candidate
                break

    try:
        # Load the background image
        bg = Image.open(bg_path).convert("RGB")

        # Resize to cover the entire slide (crop to fit)
        bg_ratio = bg.width / bg.height
        slide_ratio = w / h

        if bg_ratio > slide_ratio:
            # Background is wider - fit height
            new_h = h
            new_w = int(h * bg_ratio)
        else:
            # Background is taller - fit width
            new_w = w
            new_h = int(w / bg_ratio)

        bg = bg.resize((new_w, new_h), Image.LANCZOS)

        # Center crop to exact dimensions
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        bg = bg.crop((left, top, left + w, top + h))

        # Add semi-transparent overlay for text readability
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 180))  # Darker overlay for better text contrast
        bg = bg.convert("RGBA")
        bg = Image.alpha_composite(bg, overlay)

        return bg.convert("RGB")
    except Exception as e:
        print(f"[WARN] Could not load background image {bg_path}: {e}")
        # Fallback to gradient with visual accents
        img = Image.new("RGB",(w,h),BG_TOP)
        dr = ImageDraw.Draw(img)
        for y in range(h):
            t = y/(h-1)
            r = int(BG_TOP[0]*(1-t)+BG_BOTTOM[0]*t)
            g = int(BG_TOP[1]*(1-t)+BG_BOTTOM[1]*t)
            b = int(BG_TOP[2]*(1-t)+BG_BOTTOM[2]*t)
            dr.line([(0,y),(w,y)], fill=(r,g,b))
        # Add visual interest with abstract shapes
        img = add_background_accents(img)
        return img

def add_background_accents(img):
    """Abstract tech-inspired art - like circuit patterns and quantum visualizations"""
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay, "RGBA")
    W, H = img.size

    # Large organic flowing shapes - top right
    d.ellipse([int(W*0.6), -int(H*0.35), int(W*1.3), int(H*0.35)],
              fill=ACCENT_LIGHT + (100,))

    # Bottom left flowing blob
    d.ellipse([-int(W*0.3), int(H*0.6), int(W*0.4), int(H*1.3)],
              fill=ACCENT + (90,))

    # Overlapping organic circles creating wave pattern
    d.ellipse([int(W*0.5), int(H*0.15), int(W*1.0), int(H*0.65)],
              fill=ACCENT_LIGHT + (70,))
    d.ellipse([int(W*0.4), int(H*0.3), int(W*0.8), int(H*0.7)],
              fill=(147,197,253,60))
    d.ellipse([int(W*0.55), int(H*0.4), int(W*0.85), int(H*0.8)],
              fill=ACCENT_LIGHT + (50,))

    # Abstract corner accents
    # Top left curved triangle
    triangle_points = [(0, 0), (int(W*0.25), 0), (0, int(H*0.25))]
    d.polygon(triangle_points, fill=ACCENT + (70,))

    # Bottom right organic triangle
    triangle_points = [(W, H), (int(W*0.75), H), (W, int(H*0.75))]
    d.polygon(triangle_points, fill=ACCENT_DARK + (80,))

    # Flowing diagonal waves
    wave1 = [
        (int(W*0.3), 0),
        (int(W*0.42), 0),
        (int(W*0.15), H),
        (0, H),
        (0, int(H*0.85))
    ]
    d.polygon(wave1, fill=ACCENT_LIGHT + (45,))

    wave2 = [
        (W, int(H*0.2)),
        (W, int(H*0.35)),
        (int(W*0.65), H),
        (int(W*0.5), H)
    ]
    d.polygon(wave2, fill=ACCENT_DARK + (50,))

    # Abstract rectangular accents (circuit-inspired)
    d.rectangle([int(W*0.015), int(H*0.12), int(W*0.095), int(H*0.28)],
                fill=ACCENT + (100,))
    d.rectangle([int(W*0.91), int(H*0.58), int(W*0.985), int(H*0.78)],
                fill=ACCENT_DARK + (100,))

    # Small accent dots (particle effect)
    for i in range(8):
        x = int(W * (0.1 + i * 0.12))
        y = int(H * (0.15 + (i % 3) * 0.25))
        d.ellipse([(x-6, y-6), (x+6, y+6)], fill=ACCENT_LIGHT + (80,))

    base = img.convert("RGBA")
    result = Image.alpha_composite(base, overlay)
    return result.convert("RGB")

def blur_glow(img: Image.Image, sigma: float) -> Image.Image:
    """Light 'glow' blend using Gaussian blur."""
    if sigma <= 0:
        return img
    return Image.blend(img, img.filter(ImageFilter.GaussianBlur(sigma)), 0.20)

def draw_neural_mesh(base_img, cols, rows):
    """Draw a subtle neural network mesh overlay - accent, not dominating"""
    img = base_img.copy()
    d = ImageDraw.Draw(img,"RGBA")
    W,H = img.size
    margin_x, margin_y = min(120, W//10), min(120, H//10)

    nodes=[]
    for r in range(rows):
        row=[]
        for c in range(cols):
            x = margin_x + c * ((W-2*margin_x)/(cols-1))
            y = margin_y + r * ((H-2*margin_y)/(rows-1))
            y += 12 * math.sin(c*0.8) * math.cos(r*0.6)
            row.append((x,y))
        nodes.append(row)

    # Draw horizontal lines - MORE subtle, let geometric shapes shine
    for r in range(rows):
        for c in range(cols-1):
            opacity = 35 + int(15 * (1 - r/rows))  # Much more subtle
            d.line([nodes[r][c], nodes[r][c+1]],
                   fill=(ACCENT[0],ACCENT[1],ACCENT[2],opacity), width=1)

    # Draw vertical lines - very subtle
    for c in range(cols):
        for r in range(rows-1):
            opacity = 30 + int(10 * (1 - c/cols))
            d.line([nodes[r][c], nodes[r+1][c]],
                   fill=(ACCENT[0],ACCENT[1],ACCENT[2],opacity), width=1)

    # Draw nodes - small and subtle
    for r in range(rows):
        for c in range(cols):
            x,y = nodes[r][c]
            # Very subtle dot
            d.ellipse([(x-2,y-2),(x+2,y+2)], fill=(ACCENT[0],ACCENT[1],ACCENT[2],100))

    return img.convert("RGB")

def wrap_text(draw, text, font, max_width):
    text = sanitize(text)
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        tw,_ = measure_text(draw,test,font)
        if tw<=max_width: line=test
        else:
            if line: lines.append(line)
            line=w
    if line: lines.append(line)
    return lines

def logo_bar(img, logo_path=None):
    """Place AI Elevate branding in upper right corner - clean and minimal"""
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img,"RGBA")
    W,H = img.size
    pad = int(min(W,H)*0.032)

    # Place logo and text in upper right as unified lockup with dynamic rocket
    if logo_path and os.path.exists(logo_path):
        try:
            logo_original = Image.open(logo_path).convert("RGBA")
            # Logo size - keep prominent
            target_h = int(H*0.08)  # Slightly larger for impact
            logo_original.thumbnail((int(W*0.20), target_h), Image.LANCZOS)

            # Rotate rocket -40 degrees (upward to the right, ascending)
            logo_rotated = logo_original.rotate(-40, expand=True, resample=Image.BICUBIC)

            # "AI ELEVATE" text - smaller, tighter in upper right
            brand_font = load_font(max(24, int(H*0.032)), bold=True)
            brand_text = "AI ELEVATE"
            tw, th = measure_text(d, brand_text, brand_font)

            # More negative spacing to eliminate gap from rotated image padding
            logo_text_spacing = -25

            # Calculate total width including rotated logo
            total_width = logo_rotated.width + logo_text_spacing + tw

            # Position the entire unit closer to the right edge
            unit_x = W - total_width - int(pad*0.7)

            # Position rotated logo higher and more to the right
            logo_x = unit_x
            logo_y = int(pad*0.6)

            # Paste the rocket - clean and simple, no air flow effects
            img.paste(logo_rotated, (logo_x, logo_y), logo_rotated)

            # Position text - vertically centered with logo center
            text_x = logo_x + logo_rotated.width + logo_text_spacing
            text_y = logo_y + (logo_rotated.height - th) // 2
            d.text((text_x, text_y), sanitize(brand_text), fill=WHITE, font=brand_font)

            logo_original.close()
            logo_rotated.close()
        except Exception as e:
            print(f"[WARN] Failed to load logo from {logo_path}: {e}")
            # Fallback to text only
            brand_font = load_font(max(32, int(H*0.042)), bold=True)
            brand_text = "AI ELEVATE"
            tw, th = measure_text(d, brand_text, brand_font)
            text_x = W - tw - pad
            text_y = pad
            d.text((text_x, text_y), sanitize(brand_text), fill=WHITE, font=brand_font)
    else:
        # Text only fallback - make it prominent
        brand_font = load_font(max(32, int(H*0.042)), bold=True)
        brand_text = "AI ELEVATE"
        tw, th = measure_text(d, brand_text, brand_font)
        text_x = W - tw - pad
        text_y = pad
        d.text((text_x, text_y), sanitize(brand_text), fill=WHITE, font=brand_font)

    return img.convert("RGB")

def add_footer(img, text):
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img,"RGBA")
    W,H = img.size
    font = load_font(max(28,int(H*0.035)), bold=True)
    text = sanitize(text)
    tw,_ = measure_text(d,text,font)
    # Center footer with consistent bottom margin matching slide number area
    footer_y = H - int(H*0.065)
    d.text(((W-tw)//2, footer_y), text, fill=WHITE+(220,), font=font)
    return img.convert("RGB")

def draw_text_with_shadow(draw, pos, text, font, fill, shadow_color=(0,0,0,180)):
    """Draw text with shadow for better readability"""
    x, y = pos
    # Draw shadow (offset by 2px)
    draw.text((x+2, y+2), sanitize(text), fill=shadow_color, font=font)
    # Draw main text
    draw.text((x, y), sanitize(text), fill=fill, font=font)

def add_slide_number(img, current, total):
    """Add slide number indicator in bottom right"""
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    font = load_font(max(18, int(H*0.022)))
    text = f"{current}/{total}"
    tw, th = measure_text(d, text, font)
    # Bottom right corner with padding
    x = W - tw - 30
    y = H - th - 30
    # Add subtle background
    padding = 8
    d.rectangle([(x-padding, y-padding), (x+tw+padding, y+th+padding)],
                fill=(0,0,0,120))
    d.text((x, y), text, fill=WHITE+(220,), font=font)
    return img.convert("RGB")

def add_swipe_indicator(img, text="SWIPE →"):
    """Add swipe indicator for engagement"""
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    font = load_font(max(20, int(H*0.028)), bold=True)
    text = sanitize(text)
    tw, th = measure_text(d, text, font)
    # Bottom right, above slide number
    x = W - tw - 35
    y = H - th - 70
    # Draw with emphasis
    draw_text_with_shadow(d, (x, y), text, font, ACCENT_LIGHT+(255,))
    return img.convert("RGB")

# --------------- PDF for LinkedIn Carousel ---------------
def build_linkedin_pdf(slide_paths: List[str], pdf_path: str, W: int, H: int, progress):
    """PDF generation for LinkedIn carousel with auto-transitions and interactive links"""
    if not REPORTLAB_OK:
        progress.write("[WARN] reportlab not available; skipping PDF generation.")
        progress.write("[INFO] Install with: pip install reportlab")
        return False

    try:
        c = canvas.Canvas(pdf_path, pagesize=(W, H))
        c.setTitle("AI-Elevate Prompt Engineering")
        c.setAuthor("AI-Elevate")

        progress.set_description("Creating LinkedIn PDF")
        for idx, p in enumerate(slide_paths, start=1):
            img = ImageReader(p)
            c.drawImage(img, 0, 0, width=W, height=H, mask='auto')

            # Add auto-transition: 5 seconds per slide
            # This makes the PDF auto-advance but viewers can pause/play
            c.setPageDuration(5)

            # Add subtle fade transition between slides
            c.setPageTransition("Dissolve", duration=0.5)

            # Add clickable link to logo/company name in upper right corner (all slides)
            # Logo area is approximately 20% of width in upper right
            logo_area_w = int(W*0.22)  # Width of logo + "AI ELEVATE" text
            logo_area_h = int(H*0.10)  # Height of logo area
            logo_area_x = W - logo_area_w - int(W*0.02)  # Right edge
            logo_area_y_pil = int(H*0.015)  # Top in PIL coordinates
            logo_area_y_pdf = H - logo_area_y_pil - logo_area_h  # Convert to PDF coordinates

            # Add clickable link to logo area
            c.linkURL(CTA_URL, (logo_area_x, logo_area_y_pdf, logo_area_x + logo_area_w, logo_area_y_pdf + logo_area_h), relative=0)

            # Add clickable footer link to all slides
            # Footer is at bottom center - calculate approximate position
            footer_h = int(H*0.05)  # Approximate footer height
            footer_w = int(W*0.50)  # Approximate width for footer text
            footer_x = int(W*0.25)  # Center the footer link
            footer_y = 0  # At the very bottom

            # Add clickable link to footer
            c.linkURL(CTA_URL, (footer_x, footer_y, footer_x + footer_w, footer_y + footer_h), relative=0)

            # Add clickable link on the last slide (CTA slide button and URL)
            if idx == len(slide_paths):
                # Calculate button position (matching cta_slide layout)
                y_approx = int(H*0.204) + int(H*0.065) + int(H*0.027) + len(CTA_LINES) * int(H*0.055) + int(H*0.028)
                btn_x = int(W*0.052)
                btn_h = int(H*0.078)
                btn_w = int(W*0.60)  # Generous width to cover the full button

                # Convert PIL coordinates (top-left origin) to PDF coordinates (bottom-left origin)
                pdf_y = H - y_approx - btn_h

                # Add clickable link rectangle for the button
                c.linkURL(CTA_URL, (btn_x, pdf_y, btn_x + btn_w, pdf_y + btn_h), relative=0)

                # Add clickable link for URL text below button
                url_text_w = int(W*0.35)  # Width of "https://ai-elevate.ai" text
                url_text_h = int(H*0.04)  # Height of URL text
                url_text_x = int((W - url_text_w) / 2)  # Centered horizontally
                url_y_approx = y_approx + btn_h + int(H*0.022)  # Below button
                url_pdf_y = H - url_y_approx - url_text_h

                # Add clickable link rectangle for the URL text
                c.linkURL(CTA_URL, (url_text_x, url_pdf_y, url_text_x + url_text_w, url_pdf_y + url_text_h), relative=0)

            c.showPage()
            progress.set_description(f"PDF page {idx}/{len(slide_paths)}")
            progress.update(1)

        c.save()
        progress.write(f"[OK] LinkedIn carousel PDF saved: {pdf_path}")
        progress.write(f"[INFO] PDF features: Auto-transitions (5s/slide), Clickable links, Fade effects")
        progress.write(f"[TIP] Use PDF viewer controls to pause/play auto-transitions")
        return True
    except Exception as e:
        progress.write(f"[ERROR] PDF generation failed: {e}")
        return False

def add_newwindow_flags(pdf_path: str, progress) -> bool:
    """Post-process PDF to make all URL links open in new browser windows/tabs"""
    if not PYPDF_OK:
        return False

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        progress.write("[INFO] Adding NewWindow flags to links...")

        for page_num, page in enumerate(reader.pages):
            # Copy the page
            writer.add_page(page)

            # Check if page has annotations
            if "/Annots" in page:
                annotations = page["/Annots"]
                for annot in annotations:
                    annot_obj = annot.get_object()
                    # Check if it's a Link annotation with a URI action
                    if annot_obj.get("/Subtype") == "/Link":
                        if "/A" in annot_obj:
                            action = annot_obj["/A"]
                            # If it's a URI action, add NewWindow flag
                            if action.get("/S") == "/URI":
                                # Add NewWindow = true to make link open in new window
                                action.update({"/NewWindow": BooleanObject(True)})

        # Write the modified PDF
        with open(pdf_path, "wb") as output_file:
            writer.write(output_file)

        progress.write("[OK] Links configured to open in new windows")
        return True
    except Exception as e:
        progress.write(f"[WARN] Could not add NewWindow flags: {e}")
        return False

# --------------- Slide renderers ---------------
def render_title_slide(W,H, cols, rows, blur_sigma, logo):
    """Slide 1 - Bold hook with pattern interrupt"""
    base = load_background_image(W, H)
    img = blur_glow(base, sigma=float(max(0, blur_sigma)))
    d = ImageDraw.Draw(img, "RGBA")

    # Stat box - increased height to accommodate wrapped title and attribution
    stat_box_w = int(W*0.896)
    stat_box_h = int(H*0.235)
    stat_box_x = int(W*0.052)
    stat_box_y = int(H*0.14)

    # Draw stat box with solid background
    if hasattr(d, "rounded_rectangle"):
        d.rounded_rectangle([stat_box_x, stat_box_y, stat_box_x+stat_box_w, stat_box_y+stat_box_h],
                          radius=15, fill=ACCENT+(240,), outline=ACCENT_LIGHT+(255,), width=4)
    else:
        d.rectangle([stat_box_x, stat_box_y, stat_box_x+stat_box_w, stat_box_y+stat_box_h],
                   fill=ACCENT+(240,), outline=ACCENT_LIGHT+(255,), width=4)

    # Title in stat box - wrap text to prevent overflow
    title_font = load_font(max(38,int(H*0.056)), bold=True)
    title_y = stat_box_y + 26
    # Wrap title if it's too long to fit in the box
    max_title_width = stat_box_w - 60  # Account for padding on both sides
    title_lines = wrap_text(d, TITLE, title_font, max_width=max_title_width)
    for line in title_lines:
        d.text((stat_box_x + 30, title_y), line, fill=WHITE, font=title_font)
        title_y += int(H*0.058)

    # Subtitle in stat box - aligned below title
    subtitle_font = load_font(max(34,int(H*0.050)), bold=True)
    subtitle_y = title_y + int(H*0.015)
    d.text((stat_box_x + 30, subtitle_y), SUBTITLE, fill=ACCENT_LIGHT, font=subtitle_font)

    # Attribution in stat box - small text below subtitle
    attribution_font = load_font(max(16,int(H*0.024)))
    attribution_y = subtitle_y + int(H*0.054)
    d.text((stat_box_x + 30, attribution_y), TITLE_ATTRIBUTION, fill=WHITE+(200,), font=attribution_font)

    # Tagline below box - wrap to prevent overflow
    tagline_font = load_font(max(22,int(H*0.032)))
    tagline_y = stat_box_y + stat_box_h + int(H*0.035)
    tagline_lines = wrap_text(d, TAGLINE, tagline_font, max_width=int(W*0.88))
    for line in tagline_lines:
        d.text((int(W*0.052), tagline_y), line, fill=WHITE, font=tagline_font)
        tagline_y += int(H*0.038)
    tagline2_lines = wrap_text(d, TAGLINE2, tagline_font, max_width=int(W*0.88))
    for line in tagline2_lines:
        d.text((int(W*0.052), tagline_y), line, fill=WHITE, font=tagline_font)
        tagline_y += int(H*0.038)

    # Add quote - centered at bottom, large and readable
    quote_font = load_font(max(40,int(H*0.056)), italic=True)
    attr_font = load_font(max(32,int(H*0.046)))

    quote_y = int(H*0.64)
    quote_lines = wrap_text(d, QUOTE, quote_font, max_width=int(W*0.85))
    for line in quote_lines:
        qw,_ = measure_text(d, line, quote_font)
        d.text(((W-qw)//2, quote_y), line, fill=WHITE+(255,), font=quote_font)
        quote_y += int(H*0.052)

    # Attribution - same color as quote for consistency
    aw,_ = measure_text(d, QUOTE_ATTR, attr_font)
    d.text(((W-aw)//2, quote_y + int(H*0.015)), QUOTE_ATTR, fill=WHITE+(255,), font=attr_font)

    # Add logo, footer, slide number, and swipe indicator
    img = img.convert("RGB")
    img = logo_bar(img, logo_path=logo)
    img = add_footer(img, FOOTER_SLIDE_1)
    img = add_slide_number(img, 1, 8)
    img = add_swipe_indicator(img, "SWIPE →")
    return img

def content_slide(W,H, cols, rows, blur_sigma, logo, title, bullets, slide_num=2, total_slides=8,
                  subtitle=None, footer=None, curiosity_gap=None, subtitle_color=None):
    """Generic content slide with variable formatting"""
    base = load_background_image(W, H)
    img = blur_glow(base, sigma=float(max(0, blur_sigma-1)))
    d = ImageDraw.Draw(img)
    title_font = load_font(max(40,int(H*0.056)), bold=True)
    subtitle_font = load_font(max(26,int(H*0.038)), italic=True)
    body_font  = load_font(max(24,int(H*0.035)))

    title_x = int(W*0.052)
    title_y = int(H*0.10)

    # Main title - wrap if too long
    title_lines = wrap_text(d, title, title_font, max_width=int(W*0.896))
    current_y = title_y
    for line in title_lines:
        d.text((title_x, current_y), line, fill=WHITE, font=title_font)
        current_y += int(H*0.058)

    # Subtitle if provided - wrap if needed
    if subtitle:
        subtitle_lines = wrap_text(d, subtitle, subtitle_font, max_width=int(W*0.896))
        sub_color = subtitle_color if subtitle_color else ACCENT_LIGHT
        for line in subtitle_lines:
            d.text((title_x, current_y), line, fill=sub_color, font=subtitle_font)
            current_y += int(H*0.035)

    # Measure FIRST line of title for underline width
    first_title_line = title_lines[0] if title_lines else title
    title_width, _ = measure_text(d, first_title_line, title_font)
    line_end_x = title_x + title_width
    line_y = current_y + int(H*0.015)
    d.line([(title_x, line_y), (line_end_x, line_y)], fill=ACCENT_LIGHT, width=6)

    # Content bullets - increased spacing from underline
    y = line_y + int(H*0.055)
    for b in bullets:
        lines = wrap_text(d, b, body_font, max_width=int(W*0.85))
        for li in lines:
            d.text((int(W*0.073), y), li, fill=WHITE, font=body_font)
            y += int(H*0.046)
        y += int(H*0.012)

    # Curiosity gap at bottom - fixed position for alignment across all slides
    if curiosity_gap:
        gap_font = load_font(max(24,int(H*0.035)), bold=True)
        gap_y = H - int(H*0.13)  # Fixed at 13% from bottom for consistency
        # Center the curiosity gap for better visibility
        gw,_ = measure_text(d, curiosity_gap, gap_font)
        d.text(((W-gw)//2, gap_y), curiosity_gap, fill=ACCENT_LIGHT+(255,), font=gap_font)

    # Add logo, footer, and slide number
    img = img.convert("RGB")
    img = logo_bar(img, logo_path=logo)
    img = add_footer(img, footer or FOOTER_SLIDE_2_3)
    img = add_slide_number(img, slide_num, total_slides)
    return img

def social_proof_slide(W,H, cols, rows, blur_sigma, logo):
    """Slide 7 - Social Proof with testimonials"""
    base = load_background_image(W, H)
    img = blur_glow(base, sigma=float(max(0, blur_sigma)))
    d = ImageDraw.Draw(img)

    title_font = load_font(max(44,int(H*0.062)), bold=True)
    quote_font = load_font(max(20,int(H*0.030)), italic=True)
    attr_font = load_font(max(18,int(H*0.026)), bold=True)
    stat_font = load_font(max(22,int(H*0.032)), bold=True)

    # Title
    title_x = int(W*0.052)
    d.text((title_x, int(H*0.10)), sanitize(SLIDE_7_TITLE), fill=WHITE, font=title_font)

    # Underline
    title_width, _ = measure_text(d, sanitize(SLIDE_7_TITLE), title_font)
    d.line([(title_x, int(H*0.17)), (title_x + title_width, int(H*0.17))], fill=ACCENT_LIGHT, width=6)

    # Real results section (no fake testimonials)
    y = int(H*0.22)

    results_title_font = load_font(max(28,int(H*0.042)), bold=True)
    d.text((int(W*0.073), y), "PROVEN RESULTS:", fill=ACCENT_LIGHT, font=results_title_font)
    y += int(H*0.070)

    # Stats box - real, verifiable metrics with attributions
    stats = [
        "✓ 26% productivity increase",
        "   (Microsoft/MIT Study, 2024)",
        "✓ 4+ hours saved per worker weekly",
        "   (Gartner Survey, 2024)",
        "✓ 55% faster task completion",
        "   (Microsoft Research, 2023)",
        "✓ 500+ teams trained worldwide",
        "✓ Industries: Tech, Finance, Healthcare, Retail"
    ]

    for stat in stats:
        d.text((int(W*0.073), y), stat, fill=WHITE, font=stat_font)
        y += int(H*0.042)

    # Curiosity gap - fixed position for alignment across all slides
    gap_text = "Ready to join them? →"
    gap_font = load_font(max(24,int(H*0.035)), bold=True)
    gap_y = H - int(H*0.13)  # Fixed at 13% from bottom for consistency
    gw,_ = measure_text(d, gap_text, gap_font)
    d.text(((W-gw)//2, gap_y), gap_text, fill=ACCENT_LIGHT+(255,), font=gap_font)

    img = img.convert("RGB")
    img = logo_bar(img, logo_path=logo)
    img = add_footer(img, FOOTER_SLIDE_7_8)
    img = add_slide_number(img, 7, 8)
    return img

def cta_slide(W,H, cols, rows, blur_sigma, logo):
    """Slide 8 - Low-barrier CTA with free resource"""
    base = load_background_image(W, H)
    img = blur_glow(base, sigma=float(max(0, blur_sigma)))
    d = ImageDraw.Draw(img)

    title_font = load_font(max(44,int(H*0.062)), bold=True)
    subtitle_font = load_font(max(26,int(H*0.038)), italic=True, serif=True)
    body_font  = load_font(max(22,int(H*0.032)))
    button_font = load_font(max(20,int(H*0.030)), bold=True)

    # Title - wrap to prevent truncation
    title_x = int(W*0.052)
    y_title = int(H*0.15)
    title_lines = wrap_text(d, SLIDE_8_TITLE, title_font, max_width=int(W*0.88))
    current_y = y_title
    for line in title_lines:
        d.text((title_x, current_y), sanitize(line), fill=WHITE, font=title_font)
        current_y += int(H*0.065)

    # Subtitle
    y_subtitle = current_y + int(H*0.010)
    subtitle_lines = wrap_text(d, CTA_SUBTITLE, subtitle_font, max_width=int(W*0.88))
    for line in subtitle_lines:
        sw, _ = measure_text(d, line, subtitle_font)
        d.text(((W-sw)//2, y_subtitle), sanitize(line), fill=ACCENT_LIGHT, font=subtitle_font)
        y_subtitle += int(H*0.048)

    # Bullets
    y = y_subtitle + int(H*0.035)
    for line in CTA_LINES:
        d.text((int(W*0.073), y), sanitize(line), fill=WHITE, font=body_font)
        y += int(H*0.048)

    # Large CTA button
    btn_h = int(H*0.09)
    btn_w = int(W*0.80)
    bx = (W - btn_w) // 2
    by = y + int(H*0.035)

    if hasattr(d,"rounded_rectangle"):
        d.rounded_rectangle([bx,by,bx+btn_w,by+btn_h], radius=20, fill=ACCENT, outline=ACCENT_LIGHT, width=4)
    else:
        d.rectangle([bx,by,bx+btn_w,by+btn_h], fill=ACCENT, outline=ACCENT_LIGHT, width=4)

    # Center button text
    btw, bth = measure_text(d, sanitize(CTA_BUTTON_TEXT), button_font)
    text_x = bx + (btn_w - btw) // 2
    text_y = by + (btn_h - bth) // 2
    d.text((text_x, text_y), sanitize(CTA_BUTTON_TEXT), fill=WHITE, font=button_font)

    # Add URL below button
    url_font = load_font(max(18,int(H*0.026)))
    url_text = "https://ai-elevate.ai"
    url_w, url_h = measure_text(d, url_text, url_font)
    url_x = (W - url_w) // 2
    url_y = by + btn_h + int(H*0.022)
    d.text((url_x, url_y), url_text, fill=ACCENT_LIGHT+(230,), font=url_font)

    img = img.convert("RGB")
    img = logo_bar(img, logo_path=logo)
    img = add_footer(img, FOOTER_SLIDE_7_8)
    img = add_slide_number(img, 8, 8)
    return img

# --------------- Main ---------------
def main():
    ap = argparse.ArgumentParser(description="Generate LinkedIn carousel images for AI-Elevate.")
    ap.add_argument("--outdir", default="out", help="Output directory (default: out)")
    ap.add_argument("--logo", default=None, help="Path to logo image (e.g., ai-elevate-s-wbg.png)")
    ap.add_argument("--profile", choices=list(PROFILES.keys()), default="linkedin", help="Image format: linkedin|portrait|landscape (default: linkedin)")
    args = ap.parse_args()

    # Auto-detect logo if not specified
    if args.logo is None:
        common_logo_names = ["ai-elevate-s-wbg.png", "logo.png", "AI-Elevate-logo.png"]
        for logo_name in common_logo_names:
            if os.path.exists(logo_name):
                args.logo = logo_name
                print(f"[INFO] Auto-detected logo: {args.logo}")
                break

    os.makedirs(args.outdir, exist_ok=True)
    prof = PROFILES[args.profile]
    W,H       = prof["W"], prof["H"]
    mesh_cols = prof["mesh_cols"]
    mesh_rows = prof["mesh_rows"]
    blur      = prof["blur"]

    # Display configuration
    print(f"\n{'='*60}")
    print(f"AI-Elevate LinkedIn Carousel Generator")
    print(f"{'='*60}")
    print(f"Profile: {args.profile} ({W}x{H})")
    print(f"Output: {os.path.abspath(args.outdir)}")
    if args.logo and os.path.exists(args.logo):
        print(f"Logo: {args.logo}")
    elif args.logo:
        print(f"[WARN] Logo file not found: {args.logo}")
    else:
        print(f"Logo: Using default text branding")
    print(f"Format: PNG (optimized for LinkedIn)")
    print(f"{'='*60}\n")

    # Phase 1: Render slides
    steps = 8
    bar = tqdm(total=steps, desc=f"Rendering slides ({args.profile})", unit="slide")
    slides=[]

    bar.set_description("Slide 1 (hook)")
    slides.append(render_title_slide(W,H,mesh_cols,mesh_rows,blur,args.logo)); bar.update(1)

    bar.set_description("Slide 2 (why)")
    slides.append(content_slide(W,H,mesh_cols,mesh_rows,blur,args.logo,
        SLIDE_2_TITLE,
        [
            "✗ Generic prompts = generic results",
            "✓ Learn the framework Fortune 500s use",
            "",
            "✗ Copy-paste templates that don't work",
            "✓ Build custom prompts for YOUR business",
            "",
            "✗ One-off AI experiments",
            "✓ Repeatable workflows that scale"
        ],
        slide_num=2,
        subtitle=SLIDE_2_SUBTITLE,
        footer=FOOTER_SLIDE_2_3,
        curiosity_gap="But here's who this ISN'T for... →"
    )); bar.update(1)

    bar.set_description("Slide 3 (audience)")
    slides.append(content_slide(W,H,mesh_cols,mesh_rows,blur,args.logo,
        SLIDE_3_TITLE,
        [
            "PERFECT FOR:",
            "✓ Business analysts seeking AI leverage",
            "✓ Developers building AI workflows",
            "✓ Project managers coordinating adoption",
            "✓ AI champions driving transformation",
            "",
            "NOT FOR:",
            "✗ Data scientists (too basic)",
            "✗ Companies not ready for change"
        ],
        slide_num=3,
        footer=FOOTER_SLIDE_2_3,
        curiosity_gap="Here's what 97% of courses get wrong →"
    )); bar.update(1)

    bar.set_description("Slide 4 (learning)")
    slides.append(content_slide(W,H,mesh_cols,mesh_rows,blur,args.logo,
        SLIDE_4_TITLE,
        [
            "✓ Structured Prompting Frameworks",
            "   (A-C-E & ReAct methodologies)",
            "",
            "✓ Prompt Optimization & Testing",
            "   (Iterative refinement strategies)",
            "",
            "✓ Enterprise AI Workflow Design",
            "   (Copilots, chains, and automation)",
            "",
            "✓ Responsible AI Practices",
            "   (Guardrails, ethics, and compliance)"
        ],
        slide_num=4,
        subtitle=SLIDE_4_SUBTITLE,
        subtitle_color=WHITE,
        footer=FOOTER_SLIDE_4_5,
        curiosity_gap="The format that makes this stick →"
    )); bar.update(1)

    bar.set_description("Slide 5 (format)")
    slides.append(content_slide(W,H,mesh_cols,mesh_rows,blur,args.logo,
        SLIDE_5_TITLE,
        [
            "✓ In-company delivery",
            "✓ Hands-on sessions (not lectures)",
            "✓ Customizable to your industry",
            "",
            "MODULE BREAKDOWN:",
            "1. Intro to Generative AI (30 min)",
            "2. Prompt Design & Iteration (1 hr)",
            "3. Use Cases & Labs (90 min)",
            "4. Team Prompt Challenge (30 min)"
        ],
        slide_num=5,
        footer=FOOTER_SLIDE_4_5,
        curiosity_gap="The results speak for themselves →"
    )); bar.update(1)

    bar.set_description("Slide 6 (outcomes)")
    slides.append(content_slide(W,H,mesh_cols,mesh_rows,blur,args.logo,
        SLIDE_6_TITLE,
        [
            "→ 20-30% productivity uplift",
            "   (Measured on routine tasks)",
            "",
            "→ Teams ship AI workflows faster",
            "   (Shared prompts & frameworks)",
            "",
            "→ Better decisions with AI assistance",
            "   (Data analysis & insights)",
            "",
            "→ Enterprise-grade AI compliance",
            "   (Safe, responsible LLM usage)"
        ],
        slide_num=6,
        footer=FOOTER_SLIDE_6,
        curiosity_gap="See our proven track record →"
    )); bar.update(1)

    bar.set_description("Slide 7 (social proof)")
    slides.append(social_proof_slide(W,H,mesh_cols,mesh_rows,blur,args.logo)); bar.update(1)

    bar.set_description("Slide 8 (CTA)")
    slides.append(cta_slide(W,H,mesh_cols,mesh_rows,blur,args.logo)); bar.update(1); bar.close()

    # Save slides as PNGs
    slide_paths=[]
    sv = tqdm(total=len(slides), desc="Saving slides", unit="img")
    for i,im in enumerate(slides, start=1):
        p = os.path.join(args.outdir, f"slide_{i:02d}.png")
        im.save(p, "PNG", optimize=True)
        slide_paths.append(p)
        sv.set_description(f"Saving slide {i}/{len(slides)}")
        sv.update(1)
        im.close()
    sv.close()
    slides.clear(); gc.collect()

    # Generate PDF for LinkedIn carousel
    pdf_path = os.path.join(args.outdir, "AI-Elevate_LinkedIn_Carousel.pdf")
    pdf_bar = tqdm(total=len(slide_paths), desc="Creating PDF", unit="page")
    pdf_ok = build_linkedin_pdf(slide_paths, pdf_path, W, H, pdf_bar)
    pdf_bar.close()

    # Post-process PDF to make links open in new windows
    if pdf_ok and PYPDF_OK:
        add_newwindow_flags(pdf_path, pdf_bar)

    print(f"\n{'='*60}")
    print(f"[DONE] LinkedIn Carousel Generated!")
    print(f"{'='*60}")
    if pdf_ok:
        print(f"PDF: {os.path.abspath(pdf_path)}")
        print(f"\n[TIP] Upload to LinkedIn:")
        print(f"  1. Create a new post")
        print(f"  2. Click 'Add Media' > 'Document'")
        print(f"  3. Upload the PDF file")
        print(f"  4. LinkedIn will automatically convert it to a carousel!")
    else:
        print(f"PNG images: {os.path.abspath(args.outdir)}")
        print(f"\n[NOTE] PDF generation skipped (reportlab not installed)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

