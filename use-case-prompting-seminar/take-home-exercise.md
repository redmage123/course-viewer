# Take-Home Exercise: Prompting, Context Engineering & Use Case Development

## ITAG Skillnet AI Advantage

---

## Before You Begin

**What you'll need:**
- A computer with internet access
- Access to ChatGPT (https://chat.openai.com) - the free version works fine
- About 60-75 minutes of focused time
- A document or note-taking app to save your work

**How to complete this exercise:**
1. Work through each part in order - they build on each other
2. Actually type the prompts into ChatGPT and observe the results
3. Fill in the blanks and tables as you go
4. Save your best prompts - you'll reuse them!

**What you'll learn:**
- How to write effective prompts using the CRAFT framework
- How to manage context for better AI outputs
- How to identify and evaluate AI use cases for your organization

---

# PART 1: Prompt Engineering Practice
**Time: 20 minutes**

In this section, you'll practice five core prompting techniques by typing prompts into ChatGPT and comparing results.

---

## Exercise 1.1: Basic to CRAFT Transformation

**What you'll do:** Compare a basic prompt to a CRAFT-enhanced prompt and see the difference in quality.

**STEP 1: Open ChatGPT** and type this basic prompt exactly as written:
```
Write a project status update email.
```

**STEP 2: Read the output.** Notice how generic it is.

**STEP 3: Now try this improved version.** Replace the text in [brackets] with your own information, then paste into ChatGPT:

```
Context: I'm the project manager for [PROJECT NAME - e.g., "Website Redesign"]. We're in week [NUMBER] of a [DURATION - e.g., "12-week"] project. Current status: [on track/delayed/ahead]. Main stakeholders are [WHO - e.g., "the marketing director and CEO"].

Role: Act as an experienced project manager who writes clear, executive-friendly updates.

Action: Write a weekly status update email covering progress, blockers, and next steps.

Format:
- Subject line
- 3-4 sentence executive summary at top
- Bullet points for: Completed This Week, In Progress, Blockers, Next Week's Priorities
- Keep total length under 200 words

Tone: Professional, confident, transparent about challenges.
```

**STEP 4: Compare the two outputs and answer these questions:**

| Question | Your Answer |
|----------|-------------|
| How did the outputs differ? | |
| What specific improvements did you notice? | |
| Which element of CRAFT had the biggest impact? (Context/Role/Action/Format/Tone) | |

---

## Exercise 1.2: Few-Shot Learning

**What you'll do:** Teach AI a pattern by showing it examples, then have it apply that pattern to new data.

**STEP 1: Copy this entire prompt** (including the examples) and paste it into ChatGPT:

```
Analyze customer feedback and categorize it. Here are examples of how to do this:

EXAMPLE 1:
Feedback: "The new dashboard is confusing and I can't find anything."
Category: Negative - Usability
Action: Route to UX team

EXAMPLE 2:
Feedback: "Love the quick response from support, problem solved in minutes!"
Category: Positive - Support
Action: No action needed, flag for testimonial

EXAMPLE 3:
Feedback: "The product works fine but nothing special."
Category: Neutral - General
Action: No immediate action

---

Now analyze these new pieces of feedback using the same format:

Feedback: "Integration with Salesforce keeps failing every morning."
Category:
Action:

Feedback: "Pricing seems high compared to competitors."
Category:
Action:

Feedback: "The mobile app is fantastic, use it every day!"
Category:
Action:
```

**STEP 2: Review the output.** Did the AI follow your pattern correctly?

**STEP 3: Try your own.** Add 2-3 pieces of feedback relevant to your industry and see if it categorizes them correctly.

---

## Exercise 1.3: Chain-of-Thought Reasoning

**What you'll do:** Force the AI to think step-by-step before giving an answer, which produces better analysis.

**STEP 1: Think of a real decision you're facing at work.** (Examples: Should we hire a contractor? Should we switch vendors? Should we launch this feature?)

**STEP 2: Fill in this template with your situation, then paste into ChatGPT:**

```
I need to decide whether to _________________________________________________.

Current situation:
- [Fact 1: _______________________________________________]
- [Fact 2: _______________________________________________]
- [Fact 3: _______________________________________________]

Constraints:
- Budget: [_______________________________________________]
- Timeline: [_______________________________________________]
- Other: [_______________________________________________]

Think through this step-by-step:
1. First, analyze the pros and cons of each option
2. Then, consider the short-term vs long-term implications
3. Identify the key risks for each path
4. Consider what information I might be missing
5. Finally, provide your recommendation with clear reasoning

Be thorough but concise. Challenge any assumptions you notice.
```

**STEP 3: Answer this question:**

Did the AI surface any considerations you hadn't thought of? Yes / No

If yes, what were they? _______________________________________________

---

## Exercise 1.4: Persona Power

**What you'll do:** Assign an expert identity to AI and see how it changes the advice quality.

**STEP 1: Choose a topic you need help with** (technical, strategic, creative, etc.):

My topic: _______________________________________________

**STEP 2: Fill in this template and paste into ChatGPT:**

```
You are a [JOB TITLE - e.g., "senior marketing strategist"] with [NUMBER] years of experience in [SPECIFIC DOMAIN - e.g., "B2B SaaS marketing"].

You've worked with [RELEVANT EXPERIENCE - e.g., "companies ranging from startups to Fortune 500"].

You're known for [TRAIT - e.g., "giving direct, actionable advice without fluff"].

I'm dealing with this situation: [DESCRIBE YOUR SITUATION IN 2-3 SENTENCES]

Based on your experience, what would you recommend? Focus on practical, actionable advice rather than theory.
```

**STEP 3: Try a different persona** for the same question. How did the advice differ?

Persona 1 advice focused on: _______________________________________________

Persona 2 advice focused on: _______________________________________________

---

## Exercise 1.5: Output Structure Control

**What you'll do:** Request a specific output format (table) to get consistent, usable results.

**STEP 1: Think of 3 options you're comparing** for something at work (tools, vendors, approaches, etc.):

- Option A: _______________________________________________
- Option B: _______________________________________________
- Option C: _______________________________________________

**STEP 2: Fill in and paste this prompt:**

```
Compare these three options for [YOUR PURPOSE - e.g., "project management software for our 20-person team"]:
- Option A: [NAME]
- Option B: [NAME]
- Option C: [NAME]

Present the comparison as a table with these exact columns:
| Criteria | Option A | Option B | Option C |
|----------|----------|----------|----------|

Include these rows:
- Cost (estimated range)
- Implementation time
- Key pros (2-3 bullets)
- Key cons (2-3 bullets)
- Best suited for

After the table, provide a one-paragraph recommendation based on [YOUR PRIORITIES - e.g., "ease of use and budget under $500/month"].
```

**STEP 3: Did you get a properly formatted table?** Yes / No

---

# PART 2: Context Engineering Practice
**Time: 15 minutes**

Context engineering is about strategically managing what information you give to AI. In this section, you'll learn to optimize context for better results.

---

## Exercise 2.1: Context Window Optimization

**What you'll do:** Practice extracting only relevant information instead of dumping everything into AI.

**STEP 1: Think of a long document you work with** (report, contract, policy, etc.):

Document type: _______________________________________________

**STEP 2: Before you paste anything into AI, answer these questions:**

| Question | Your Answer |
|----------|-------------|
| What specific question do I need answered? | |
| Which sections of the document are relevant? | |
| What specific data points do I need? | |
| What can I leave out? | |

**STEP 3: Create an optimized prompt using this structure:**

```
## TASK
[Write your specific question in ONE sentence]

## FOCUS AREAS
[List the 2-3 sections or topics you identified above]

## RELEVANT EXCERPTS
[Paste ONLY the relevant sections - not the whole document]

## OUTPUT REQUIREMENTS
- Format: [bullets / table / paragraph]
- Length: [specific limit - e.g., "5 bullet points" or "under 200 words"]
- Audience: [who will read this]
```

**KEY INSIGHT:** This focused approach will give you better results than pasting a 50-page document and saying "summarize this."

---

## Exercise 2.2: Information Priority Practice

**What you'll do:** Learn to prioritize what information to include in your prompts.

**STEP 1: Rank these information types** from 1 (most essential) to 5 (least essential):

| Information Type | Priority (1-5) | Your Reasoning |
|------------------|----------------|----------------|
| Your specific question/task | | |
| Output format requirements | | |
| Examples of what you want | | |
| Background on your company | | |
| Complete history of the project | | |

**CORRECT ANSWER:**
1. Task (always first!)
2. Output format
3. Examples
4. Background
5. History (often not needed)

**KEY INSIGHT:** Lead with your task, not with background. AI doesn't need to know everything - it needs to know what you want.

---

## Exercise 2.3: Context Layering

**What you'll do:** Build a four-layer prompt for a real task.

**STEP 1: Choose a real task you need to complete this week:**

My task: _______________________________________________

**STEP 2: Fill in each layer:**

**Layer 1 - Role (Who should AI be?):**
```
You are a _______________________________________________
with expertise in _______________________________________________
```

**Layer 2 - Reference Material (Only essential facts):**
```
Key information you need to know:
- _______________________________________________
- _______________________________________________
- _______________________________________________
```

**Layer 3 - Example (What good looks like):**
```
Here's an example of what I'm looking for:
_______________________________________________
```

**Layer 4 - Task (Clear instruction with format):**
```
Now please _______________________________________________
Format the output as _______________________________________________
Keep it under _______________________________________________
```

**STEP 3: Combine all four layers into one prompt and paste into ChatGPT.**

**STEP 4: Rate the output quality (1-5): _____**

---

# PART 3: Use Case Development
**Time: 20 minutes**

Now apply what you've learned to identify a real AI opportunity for your organization.

---

## Exercise 3.1: Discovery

**What you'll do:** Brainstorm potential AI use cases by examining pain points in your work.

**STEP 1: Answer each question with 1-2 specific ideas:**

| Discovery Question | Your Ideas |
|-------------------|------------|
| What tasks take the most time but are fairly repetitive? | |
| What do people complain about doing? | |
| Where do customers wait longest for responses? | |
| What data do we have that's underutilized? | |
| Where do errors or inconsistencies happen most? | |

**STEP 2: List your top 5 potential use cases:**

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________
4. _______________________________________________
5. _______________________________________________

---

## Exercise 3.2: Evaluation

**What you'll do:** Score your top 3 use cases to find the best opportunity.

**STEP 1: Pick your top 3 candidates from the list above.**

**STEP 2: Score each on a 1-5 scale:**

| Criteria | Use Case 1: ________ | Use Case 2: ________ | Use Case 3: ________ |
|----------|---------------------|---------------------|---------------------|
| Data Available (Do we have the data?) | /5 | /5 | /5 |
| Technical Fit (Can AI do this well?) | /5 | /5 | /5 |
| Business Impact (Time/money saved?) | /5 | /5 | /5 |
| Implementation Ease (How hard?) | /5 | /5 | /5 |
| Low Risk (Minimal concerns?) | /5 | /5 | /5 |
| **TOTAL** | /25 | /25 | /25 |

**Scoring Guide:**
- 5 = Excellent, no concerns
- 4 = Good, minor issues
- 3 = Okay, some challenges
- 2 = Difficult, significant hurdles
- 1 = Poor, major blockers

**STEP 3: Identify your winner:**

Highest-scoring use case: _______________________________________________

---

## Exercise 3.3: Use Case Canvas

**What you'll do:** Develop your winning use case into a concrete proposal.

**STEP 1: Complete every field in this canvas for your highest-scoring use case:**

### Use Case Canvas

**Use Case Name:** _______________________________________________

**Problem Statement** (What pain point does this solve? Who feels it?):

_______________________________________________
_______________________________________________

**Current Process** (How is this handled today?):

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Proposed AI Solution** (What specifically would AI do?):

_______________________________________________
_______________________________________________

**Data Requirements:**

| Data Needed | Do We Have It? | Where Is It? |
|-------------|----------------|--------------|
| | Yes / No | |
| | Yes / No | |
| | Yes / No | |

**Success Metrics:**

| Metric | Current State | Target |
|--------|---------------|--------|
| | | |
| | | |

**Risks & Mitigations:**

| Risk | Likelihood | How to Mitigate |
|------|------------|-----------------|
| | High/Med/Low | |
| | High/Med/Low | |

**Immediate Next Step** (What ONE thing will you do this week?):

_______________________________________________

---

# PART 4: Build Your Prompt Library
**Time: 10 minutes**

Create reusable prompts you can use daily.

---

## Exercise 4.1: Create 3 Reusable Prompt Templates

**What you'll do:** Write prompt templates with [VARIABLES] you can fill in each time.

**Template 1 - For your use case from Part 3:**
```
[Write your template here with [VARIABLES] in brackets]




```

**Template 2 - For a task you do frequently at work:**
```
[Write your template here]




```

**Template 3 - For analysis or decision-making:**
```
[Write your template here]




```

---

## Exercise 4.2: Save These Iteration Phrases

**What you'll do:** Copy these phrases somewhere you can access them easily (notes app, bookmark, etc.).

**To make output more specific:**
- "Focus specifically on [X]. Remove information about [Y]."
- "Give me only [type of output], nothing else."

**To adjust length:**
- "Shorten this to under [X] words while keeping the key points."
- "Expand the section on [topic] with more detail."

**To change format:**
- "Convert this to bullet points."
- "Present this as a numbered list."
- "Reorganize this as: [structure]."

**To improve quality:**
- "This is a good start. Now make it more [specific/actionable/concise]."
- "Challenge this analysis. What am I missing?"
- "Give me 3 alternative approaches."

---

# Wrap-Up: Reflection & Next Steps

## What I Learned

**STEP 1: Answer these questions:**

1. The most valuable technique for my work is:
   _______________________________________________

2. The use case I'm most excited about is:
   _______________________________________________

3. One thing I'll do differently with AI starting tomorrow:
   _______________________________________________

---

## 7-Day Challenge

**Commit to using AI with intention this week. Check off each day as you complete it:**

- [ ] **Day 1:** Use CRAFT for one email or document
- [ ] **Day 2:** Try few-shot learning for a classification task
- [ ] **Day 3:** Use chain-of-thought for a decision
- [ ] **Day 4:** Experiment with personas for expertise
- [ ] **Day 5:** Practice iterative refinement (3+ rounds of feedback)
- [ ] **Day 6:** Create one new reusable prompt template
- [ ] **Day 7:** Share one learning with a colleague

---

## Resources for Continued Learning

- **OpenAI's Prompt Engineering Guide:** https://platform.openai.com/docs/guides/prompt-engineering
- **Anthropic's Prompt Library:** https://docs.anthropic.com/claude/prompt-library
- **Learn Prompting (free course):** https://learnprompting.org/

---

## Quick Reference Card

### CRAFT Framework
| Letter | Element | Question to Ask |
|--------|---------|-----------------|
| **C** | Context | What's the situation? |
| **R** | Role | Who should AI be? |
| **A** | Action | What should it do? |
| **F** | Format | How should output look? |
| **T** | Tone | What style/feeling? |

### Context Engineering Priority
1. Task (Essential - always first!)
2. Output requirements (Essential)
3. Key reference data (Important)
4. Examples (Helpful)
5. Background (Optional - often skip)

### Use Case Scoring
Score 1-5 on: Data Available, Technical Fit, Business Impact, Implementation Ease, Low Risk

**Quick Wins = Score 20+ with Low Complexity**

---

*Congratulations on completing the exercise! Keep practicing and building your prompt library.*

*ITAG Skillnet AI Advantage - Use Case Lab & Prompting Foundations*
