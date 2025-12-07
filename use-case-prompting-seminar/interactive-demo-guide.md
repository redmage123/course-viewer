# Interactive ChatGPT Demo Guide

## Instructor Guide for Live Prompting Demonstration

**Duration:** 10-15 minutes
**Platform:** ChatGPT (chat.openai.com) - works with free or Plus
**Goal:** Show the dramatic difference between basic and optimized prompts

---

## Setup Before the Session

1. Open ChatGPT in a browser tab
2. Have this guide open on a second screen/device
3. Start with a fresh chat (click "New chat")
4. Optional: Have the sample transcript pre-copied

---

## Demo 1: Meeting Summary (5 minutes)

### Sample Meeting Transcript

Use this sample or substitute a real (anonymized) transcript:

```
[Meeting: Q4 Planning - Product Team]
[Attendees: Sarah (PM), Mike (Engineering), Lisa (Design), Tom (Marketing)]

Sarah: Okay, let's go through priorities for Q4. We need to finalize the feature list.

Mike: From engineering, we can realistically ship either the new dashboard OR the API improvements, not both. The dashboard is about 6 weeks, API is 4 weeks.

Lisa: The dashboard redesign has been in the works for months. Users have been asking for it.

Tom: From a marketing perspective, the dashboard is way more "launchable" - we can make a big splash. The API stuff is harder to message.

Sarah: Good point. What if we do dashboard as the main Q4 launch, then API in early Q1?

Mike: That works for us. We'd need final designs by October 15th to hit the December launch.

Lisa: I can commit to that. I'll need the user research summary from last month though.

Sarah: I'll send that over today. Tom, when do you need assets for the launch campaign?

Tom: November 1st at the latest. Earlier is better.

Sarah: Okay, let's lock this in. Dashboard for Q4, API for Q1. Lisa, designs by Oct 15. Tom, assets by Nov 1. Mike, let's sync on technical requirements this week.

Mike: Sounds good. One flag - we might need to bring in a contractor for the frontend work.

Sarah: Put together a proposal and let's discuss async.
```

### Round 1: Basic Prompt

**Type this prompt:**
```
Summarize this meeting transcript.

[paste the transcript]
```

**What to point out:**
- Output is okay but generic
- No clear structure
- Misses some action items
- Doesn't prioritize information

### Round 2: CRAFT-Enhanced Prompt

**Type this prompt:**
```
Context: This is a product team Q4 planning meeting. I need to share notes with the VP of Product who wasn't in attendance.

Role: Act as an experienced executive assistant who creates clear, actionable meeting summaries.

Action: Summarize this meeting transcript focusing on decisions made and commitments.

Format your response as:
## Key Decisions
- [bullet points]

## Action Items
| Owner | Task | Deadline |
|-------|------|----------|
| ... | ... | ... |

## Open Questions
- [any unresolved items]

## Risks & Dependencies
- [anything flagged as a concern]

Tone: Professional and concise. Highlight the most important items.

[paste the transcript]
```

**What to point out:**
- Clear structure makes it scannable
- Action items have owners and deadlines
- Captures the contractor risk flag
- Ready to send to VP as-is

---

## Demo 2: Email Drafting (3 minutes)

### Round 1: Basic Prompt

```
Write a follow-up email after a sales demo.
```

**What to point out:**
- Very generic
- No personalization
- Missing key elements

### Round 2: CRAFT-Enhanced Prompt

```
Context: I just completed a 30-minute product demo with Jennifer Chen, CTO of Acme Corp (mid-size retail company, 500 employees). She was interested in our inventory management features but concerned about implementation time. Her team uses Shopify and needs integration.

Role: Act as a senior enterprise sales rep with 10 years of experience closing B2B SaaS deals.

Action: Write a follow-up email to send within 2 hours of the demo.

Format:
- Subject line that encourages opens
- Brief (under 150 words)
- Reference specific points from our conversation
- Include one resource/case study mention
- Clear next step with specific time proposal

Tone: Professional but warm. Confident but not pushy.
```

**Discussion points:**
- How context transforms output
- Specificity yields relevance
- The "specific time proposal" detail

---

## Demo 3: Chain-of-Thought Reasoning (2 minutes)

### Show the difference with complex analysis

**Basic:**
```
Should we raise prices by 15%?
```

**Chain-of-Thought:**
```
I'm considering a 15% price increase for our SaaS product. Current price is $99/month, we have 500 customers, monthly churn is 3%.

Think through this step-by-step:
1. What's the potential revenue impact?
2. How might this affect churn?
3. What competitive factors should I consider?
4. What are the risks?
5. What's your recommendation and why?
```

**Point out:** The reasoning process, not just the answer

---

## Demo 4: Few-Shot Learning (2 minutes)

### Classification Task

```
Categorize these customer support tickets. Here are examples of how to categorize:

Ticket: "Can't log in, keep getting error 401"
Category: Technical - Authentication

Ticket: "When does my subscription renew?"
Category: Billing - Inquiry

Ticket: "Your product is amazing, love the new features!"
Category: Feedback - Positive

Now categorize these:

Ticket: "The export feature keeps timing out"
Category:

Ticket: "Can I get a refund for last month?"
Category:

Ticket: "How do I add team members to my account?"
Category:
```

---

## Interactive Exercise with Audience

### Prompt: "Let's build one together"

**Scenario:** Draft a LinkedIn post announcing a new hire

**Ask the audience:**
1. What's the context? (company, role, why this hire matters)
2. What role should ChatGPT play?
3. What specific action?
4. What format constraints? (word count, style)
5. What tone? (celebratory, professional, casual?)

**Build the prompt live with their answers.**

---

## Common Questions & Live Answers

### "What if the output isn't what I want?"

Demo the iteration technique:
```
This is good, but:
- Make it shorter (under 100 words)
- Make the opening hook stronger
- Remove the bullet points, use flowing prose instead
```

### "How do I save time on repeated tasks?"

Show creating a template:
```
I frequently need to write [type of content]. Create a reusable prompt template I can fill in with variables in brackets like [company name], [key point], etc.
```

### "Can it handle sensitive information?"

Discuss:
- Don't paste confidential data
- Anonymize when possible
- Use placeholders: "[CUSTOMER NAME]", "[REVENUE FIGURE]"

---

## Closing Points

1. **First prompt is a draft** - Always iterate
2. **Specificity wins** - More context = better output
3. **Save your best prompts** - Build a personal library
4. **Verify facts** - AI can hallucinate, especially with numbers and recent events
5. **Practice daily** - Prompting is a skill that improves with use

---

## Backup Demos (if time permits)

### Data Analysis Prompt
```
Act as a data analyst. I have sales data showing:
- Q1: $1.2M (up 15% YoY)
- Q2: $1.1M (up 8% YoY)
- Q3: $1.4M (up 22% YoY)

Analyze this trend, identify what might explain the Q3 spike, and suggest 3 questions I should investigate further. Present your analysis in a format suitable for a board presentation.
```

### Document Review Prompt
```
Role: Act as a legal operations specialist with experience reviewing vendor contracts.

Task: Review this contract excerpt and identify:
1. Any unusual or potentially risky clauses
2. Missing standard protections
3. Items to negotiate before signing

Format: Bullet points organized by risk level (High/Medium/Low)

[paste contract section]
```

---

## Tips for Live Demo Success

1. **Have a backup plan** - If ChatGPT is slow, have screenshots ready
2. **Embrace imperfection** - If output isn't perfect, use it as a teaching moment about iteration
3. **Engage the audience** - Ask what they noticed between versions
4. **Keep it real** - Use examples relevant to your audience's industry
5. **Time management** - The meeting summary demo is the most impactful; prioritize it

---

*This guide supports the "Use Case Lab & Prompting Foundations" seminar for ITAG Skillnet AI Advantage.*
