#!/usr/bin/env python3
"""
Generate the "10 Enterprise Prompts That Save 10 Hours/Week" lead magnet PDF
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
import os

# AI Elevate brand colors
ACCENT = colors.HexColor('#3B82F6')
ACCENT_LIGHT = colors.HexColor('#93C5FD')
DARK = colors.HexColor('#1E293B')

def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()

    # Header - Brand
    canvas.setFillColor(DARK)
    canvas.setFont('Helvetica-Bold', 14)
    canvas.drawString(0.75*inch, 10.5*inch, "AI Elevate")

    # Footer
    canvas.setFillColor(colors.grey)
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(4.25*inch, 0.5*inch,
                            "© AI Elevate | training@ai-elevate.ai | ai-elevate.ai")
    canvas.restoreState()

def generate_lead_magnet():
    """Generate the lead magnet PDF"""

    output_file = "out/10_Enterprise_Prompts_Lead_Magnet.pdf"
    os.makedirs("out", exist_ok=True)

    # Create PDF
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=DARK,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.grey,
        spaceAfter=24,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )

    prompt_title_style = ParagraphStyle(
        'PromptTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=ACCENT,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        leftIndent=0
    )

    prompt_category_style = ParagraphStyle(
        'PromptCategory',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=8,
        fontName='Helvetica-Oblique'
    )

    prompt_text_style = ParagraphStyle(
        'PromptText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK,
        spaceAfter=6,
        leftIndent=12,
        fontName='Courier',
        backColor=colors.HexColor('#F1F5F9'),
        borderPadding=8
    )

    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK,
        spaceAfter=12,
        fontName='Helvetica'
    )

    usage_style = ParagraphStyle(
        'Usage',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=20,
        leftIndent=12,
        fontName='Helvetica'
    )

    # Build content
    story = []

    # Title page
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("10 Enterprise Prompts", title_style))
    story.append(Paragraph("That Save 10 Hours Per Week", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Tested frameworks from Fortune 500 companies", subtitle_style))
    story.append(Spacer(1, 0.5*inch))

    # Introduction
    intro_text = """
    <b>Welcome to enterprise-grade prompt engineering.</b><br/><br/>
    These 10 prompts are the result of training 500+ teams worldwide. Each prompt uses proven
    frameworks (A-C-E, ReAct, Chain-of-Thought) that Fortune 500 companies rely on daily.<br/><br/>
    <b>How to use this guide:</b><br/>
    • Copy the prompt exactly as written<br/>
    • Replace [bracketed] sections with your specific information<br/>
    • Iterate based on results - prompting is a conversation<br/>
    • Customize for your industry and use case<br/><br/>
    Ready to 10x your productivity? Let's begin.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(PageBreak())

    # Prompts
    prompts = [
        {
            "title": "1. Executive Summary Generator",
            "category": "TIME SAVED: 45 minutes per report",
            "description": "<b>What it is:</b> An automated executive summary generator that distills complex documents into decision-ready briefings.<br/><b>Problems it solves:</b> Eliminates the time sink of reading 50+ page reports, prevents important details from getting lost in lengthy documents, and ensures executives have the key information they need to make fast decisions.",
            "prompt": """You are an executive summary expert. Analyze the following document and create a concise executive summary following this structure:

[PASTE YOUR DOCUMENT HERE]

Please provide:
1. Key takeaways (3-5 bullet points)
2. Critical metrics or data points
3. Recommended actions
4. Risk factors or concerns

Format: Executive-ready, max 300 words.""",
            "usage": "<b>Use for:</b> Board reports, client updates, project summaries, quarterly reviews"
        },
        {
            "title": "2. Meeting Minutes & Action Items",
            "category": "TIME SAVED: 30 minutes per meeting",
            "description": "<b>What it is:</b> An intelligent meeting minutes extractor that converts messy notes or transcripts into structured action items with clear ownership.<br/><b>Problems it solves:</b> Stops action items from falling through the cracks, eliminates the 30-minute post-meeting admin work, and prevents the 'who was supposed to do that?' confusion that derails projects.",
            "prompt": """You are a professional meeting coordinator. Based on this meeting transcript/notes, extract:

[PASTE MEETING NOTES/TRANSCRIPT HERE]

Provide:
• Meeting summary (2-3 sentences)
• Key decisions made
• Action items with owner assignments
• Open questions or blockers
• Follow-up dates

Format as a professional meeting summary ready to distribute.""",
            "usage": "<b>Use for:</b> Team meetings, client calls, sprint planning, stakeholder updates"
        },
        {
            "title": "3. Email Response Drafter (A-C-E Method)",
            "category": "TIME SAVED: 1 hour per day",
            "description": "<b>What it is:</b> A professional email response drafter using the proven A-C-E framework (Acknowledge, Clarify, Execute) to handle complex communications.<br/><b>Problems it solves:</b> Ends the endless back-and-forth from unclear emails, prevents the stress of crafting difficult responses, and ensures you address every point without sounding defensive or missing key details.",
            "prompt": """You are a professional communication expert. Help me draft a response to this email using the A-C-E framework (Acknowledge, Clarify, Execute).

ORIGINAL EMAIL:
[PASTE EMAIL HERE]

CONTEXT:
[Add relevant background: relationship, urgency, constraints]

Draft a response that:
• Acknowledges their points professionally
• Clarifies any ambiguities or requests
• Executes with clear next steps

Tone: [Professional/Friendly/Formal]""",
            "usage": "<b>Use for:</b> Client emails, vendor communications, internal stakeholder updates"
        },
        {
            "title": "4. Code Review & Documentation",
            "category": "TIME SAVED: 1.5 hours per review",
            "description": "<b>What it is:</b> A senior-level code reviewer that analyzes code for quality, security vulnerabilities, performance issues, and documentation gaps.<br/><b>Problems it solves:</b> Catches bugs before they reach production, identifies security holes that could cost millions, speeds up PR reviews when teams are bottlenecked, and provides mentorship-quality feedback for junior developers.",
            "prompt": """You are a senior software engineer conducting a thorough code review.

CODE:
[PASTE CODE HERE]

CONTEXT: [Programming language, purpose, requirements]

Analyze and provide:
1. Code quality assessment (readability, maintainability, performance)
2. Potential bugs or edge cases
3. Security concerns
4. Optimization opportunities
5. Documentation suggestions
6. Test coverage recommendations

Be specific with line references and provide concrete examples.""",
            "usage": "<b>Use for:</b> Pull requests, legacy code analysis, architecture reviews, onboarding"
        },
        {
            "title": "5. Data Analysis & Insights",
            "category": "TIME SAVED: 2 hours per analysis",
            "description": "<b>What it is:</b> A data analysis engine that finds patterns, trends, and anomalies in your datasets and translates them into business recommendations.<br/><b>Problems it solves:</b> Eliminates 'analysis paralysis' from staring at spreadsheets, uncovers hidden opportunities in your data that manual review misses, and gives non-technical leaders data-driven insights without needing a data science team.",
            "prompt": """You are a senior data analyst. Analyze this dataset and provide actionable insights.

DATA:
[PASTE DATA OR DESCRIBE DATASET]

BUSINESS QUESTION:
[What decision needs to be made?]

Provide:
• Key patterns and trends
• Statistical significance
• Anomalies or outliers
• Business implications
• Recommended actions with confidence levels
• Suggested follow-up analyses

Use clear visualizations concepts and explain reasoning.""",
            "usage": "<b>Use for:</b> Sales data, customer behavior, operational metrics, A/B test results"
        },
        {
            "title": "6. Project Plan Generator",
            "category": "TIME SAVED: 3 hours per project",
            "description": "<b>What it is:</b> A comprehensive project planning system that generates phases, milestones, resource allocation, risk assessments, and communication plans.<br/><b>Problems it solves:</b> Prevents projects from starting without clear roadmaps, eliminates the 3-hour slog of building plans from scratch, ensures nothing critical is forgotten in the planning phase, and creates stakeholder-ready documentation instantly.",
            "prompt": """You are an experienced project manager. Create a comprehensive project plan for:

PROJECT: [Project name and objective]
TIMELINE: [Duration]
TEAM SIZE: [Number of people]
CONSTRAINTS: [Budget, resources, dependencies]

Provide:
1. Project phases with milestones
2. Task breakdown with time estimates
3. Resource allocation
4. Risk assessment and mitigation
5. Success metrics
6. Communication plan

Format as a professional project plan ready for stakeholder review.""",
            "usage": "<b>Use for:</b> Product launches, infrastructure projects, org initiatives, campaigns"
        },
        {
            "title": "7. Customer Support Response (ReAct Method)",
            "category": "TIME SAVED: 45 minutes per day",
            "description": "<b>What it is:</b> A customer support response system using the ReAct method (Reason + Act) that analyzes root causes before crafting empathetic solutions.<br/><b>Problems it solves:</b> Stops customers from getting generic copy-paste responses, reduces multi-round ticket exchanges that frustrate users, maintains consistent brand voice across support teams, and turns upset customers into advocates through thoughtful problem-solving.",
            "prompt": """You are a customer support expert using the ReAct method (Reason + Act).

CUSTOMER ISSUE:
[PASTE CUSTOMER MESSAGE]

CONTEXT:
• Account type: [Free/Paid/Enterprise]
• History: [New/Long-term customer]
• Urgency: [Low/Medium/High]

REASONING: First, analyze the root cause and customer emotion.
ACTION: Then draft a response that:
• Empathizes with their situation
• Provides clear solution steps
• Offers alternatives if applicable
• Sets expectations for resolution
• Maintains brand voice

Include both your reasoning and the final response.""",
            "usage": "<b>Use for:</b> Support tickets, escalations, product issues, billing inquiries"
        },
        {
            "title": "8. Competitive Analysis",
            "category": "TIME SAVED: 2 hours per competitor",
            "description": "<b>What it is:</b> A competitive intelligence analyzer that researches competitors' strengths, weaknesses, pricing strategies, and market positioning to identify strategic gaps.<br/><b>Problems it solves:</b> Eliminates hours of manual competitor research across multiple sources, prevents 'flying blind' when competitors launch new features, identifies market opportunities you're missing, and arms sales teams with battle cards in minutes instead of days.",
            "prompt": """You are a competitive intelligence analyst. Research and analyze:

COMPETITOR: [Company name]
OUR PRODUCT: [Your product/service]
FOCUS AREAS: [Pricing/Features/Marketing/Tech stack]

Provide:
1. Competitor strengths and weaknesses
2. Feature comparison matrix
3. Pricing strategy analysis
4. Market positioning
5. Gaps and opportunities for us
6. Recommended competitive responses

Be specific and cite sources where possible.""",
            "usage": "<b>Use for:</b> Product strategy, sales enablement, market positioning, investor updates"
        },
        {
            "title": "9. Training Material Creator",
            "category": "TIME SAVED: 4 hours per module",
            "description": "<b>What it is:</b> An instructional design system that creates complete training modules with learning objectives, interactive exercises, assessments, and resource lists.<br/><b>Problems it solves:</b> Ends the 4-hour struggle of creating training from scratch, prevents dry, ineffective training that employees forget immediately, ensures learning objectives are measurable and achievable, and scales training creation without hiring instructional designers.",
            "prompt": """You are an instructional designer. Create training materials for:

TOPIC: [Subject matter]
AUDIENCE: [Role, experience level, learning goals]
DURATION: [Target time]
FORMAT: [Presentation/Video/Workshop/Self-paced]

Create:
1. Learning objectives (specific and measurable)
2. Module outline with time allocations
3. Key concepts to cover
4. Interactive exercises or examples
5. Assessment questions
6. Resources and references

Make it engaging and practical.""",
            "usage": "<b>Use for:</b> Employee onboarding, product training, compliance training, skill development"
        },
        {
            "title": "10. Strategic Decision Framework",
            "category": "TIME SAVED: 2 hours per decision",
            "description": "<b>What it is:</b> A strategic decision framework that evaluates complex business choices through structured analysis of pros/cons, risks, resources, and stakeholder impacts.<br/><b>Problems it solves:</b> Breaks the cycle of decision paralysis when multiple good options exist, prevents costly decisions made on gut feel alone, ensures all stakeholders and risks are considered before committing, and creates documentation that justifies decisions to executives and boards.",
            "prompt": """You are a strategic advisor helping with complex decisions. Use structured analysis for:

DECISION: [What needs to be decided?]
OPTIONS: [List 2-4 options]
CONSTRAINTS: [Time, budget, resources, risks]
STAKEHOLDERS: [Who's affected?]

Analyze using:
1. Pros and cons for each option
2. Risk assessment (likelihood × impact)
3. Resource requirements
4. Timeline implications
5. Stakeholder impact
6. Recommended approach with rationale
7. Key assumptions and dependencies

Think step-by-step and show your reasoning.""",
            "usage": "<b>Use for:</b> Business strategy, vendor selection, hiring decisions, product roadmap"
        }
    ]

    for i, p in enumerate(prompts):
        if i > 0:
            story.append(PageBreak())

        story.append(Paragraph(p["title"], prompt_title_style))
        story.append(Paragraph(p["category"], prompt_category_style))
        story.append(Spacer(1, 0.05*inch))

        # Description of what the prompt does
        story.append(Paragraph(p["description"], description_style))
        story.append(Spacer(1, 0.1*inch))

        # Prompt text in box
        prompt_para = Paragraph(p["prompt"].replace('\n', '<br/>'), prompt_text_style)
        story.append(prompt_para)
        story.append(Spacer(1, 0.1*inch))

        story.append(Paragraph(p["usage"], usage_style))

    # Closing page
    story.append(PageBreak())
    story.append(Spacer(1, 1*inch))

    closing_title = ParagraphStyle(
        'ClosingTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=ACCENT,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    story.append(Paragraph("Ready to Master Enterprise AI?", closing_title))

    closing_text = """
    <b>These 10 prompts are just the beginning.</b><br/><br/>

    In our 3-hour enterprise training, you'll learn:<br/>
    • The A-C-E and ReAct frameworks Fortune 500s use<br/>
    • How to build custom prompts for YOUR specific business<br/>
    • Enterprise AI workflow design (copilots, chains, automation)<br/>
    • Responsible AI practices (guardrails, ethics, compliance)<br/><br/>

    <b>87% of our teams report 20%+ productivity gains.</b><br/><br/>

    Industries we've trained: Tech, Finance, Healthcare, Retail, Manufacturing<br/>
    Companies trained: 500+ teams worldwide<br/>
    Training delivered: 10,000+ hours<br/><br/>

    <b>Book your free 15-minute AI Readiness Call:</b><br/>
    training@ai-elevate.ai<br/><br/>

    <i>Let's elevate your business with AI.</i><br/><br/>

    - The AI Elevate Team<br/>
    ai-elevate.ai
    """

    story.append(Paragraph(closing_text, styles['Normal']))

    # Build PDF
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)

    print(f"[OK] Lead magnet PDF generated: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_lead_magnet()
