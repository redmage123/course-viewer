# Enterprise AI Adoption - Complete Student Notes

## Table of Contents
1. [Course Overview](#course-overview)
2. [Day 1: Foundations & Mindset Shift](#day-1-foundations--mindset-shift)
3. [Day 2: Mapping & Redesigning Workflows](#day-2-mapping--redesigning-workflows)
4. [Day 3: Governance, Safety & Human-in-the-Loop](#day-3-governance-safety--human-in-the-loop)
5. [Day 4: Building the Internal AI Playbook](#day-4-building-the-internal-ai-playbook)
6. [Day 5: Capstone & Rollout](#day-5-capstone--rollout)
7. [Templates and Frameworks](#templates-and-frameworks)
8. [Quick Reference](#quick-reference)

---

## Course Overview

### The AI Adoption Challenge
> "Start with pain, not platforms. AI strategy begins where work is broken."

**Key Statistics:**
- 70% of AI initiatives fail to deliver expected value
- Primary cause: Technology-first thinking instead of workflow-first design
- Solution: Human-centered AI adoption with clear governance

### Course Structure
| Day | Focus | Key Deliverable |
|-----|-------|-----------------|
| 1 | Foundations & Mindset | AI Design Challenge |
| 2 | Workflow Redesign | Process Blueprint |
| 3 | Governance & Safety | Governance Canvas |
| 4 | Documentation | AI Playbook Draft |
| 5 | Implementation | 30-60-90 Rollout Plan |

---

## Day 1: Foundations & Mindset Shift

### Learning Objectives
By the end of Day 1, you will be able to:
- Distinguish between automation and AI-native design
- Identify workflow friction points in your organization
- Complete an AI Readiness assessment
- Formulate a focused AI Design Challenge

### Automation vs. AI-Native Design

| Aspect | Traditional Automation | AI-Native Design |
|--------|------------------------|------------------|
| **Nature** | Rule-based, deterministic | Probabilistic, adaptive |
| **Function** | Replaces specific tasks | Augments human judgment |
| **Input** | Requires structured data | Handles unstructured data |
| **Learning** | No learning or adaptation | Learns from feedback |
| **Logic** | "If X, then Y" | "Given context, suggest action" |

**Example:**
- **Automation:** Auto-filing emails by sender
- **AI-Native:** Drafting email responses based on context

### The Workflow Autopsy

Before introducing AI, identify where work is broken:

| Friction Type | Symptoms | AI Opportunity |
|---------------|----------|----------------|
| Manual Handoffs | Email chains, waiting for approvals | Route/escalate automatically |
| Duplicate Data Entry | Same info in multiple systems | Auto-populate from source |
| Information Hunting | Searching across tools/docs | Summarize and retrieve |
| Format Translation | Converting between formats | Auto-format/transform |
| Review Bottlenecks | Work queued for expert review | Pre-screen and prioritize |
| Rework Loops | Frequent corrections/revisions | Validate before submission |

### The AI Readiness Canvas

Evaluate your organization across five dimensions (rate 1-5):

1. **Data Access** - Can AI reach the data it needs?
   - Low: Siloed systems, manual exports, no APIs
   - High: Connected systems, real-time access, clean data

2. **Decision Speed** - How fast are decisions made today?
   - Low: Multi-week approvals, committee decisions
   - High: Same-day decisions, delegated authority

3. **Risk Tolerance** - Appetite for AI-assisted decisions?
   - Low: Zero-error culture, heavy regulation
   - High: Experimentation encouraged, learning from failure

4. **Tech Integration** - Can you connect AI to existing tools?
   - Low: Legacy systems, no IT support, vendor lock-in
   - High: Modern APIs, IT partnership, flexible architecture

5. **Employee Readiness** - Are people prepared and willing?
   - Low: Fear of replacement, no training, skepticism
   - High: AI curiosity, growth mindset, training available

### Culture: The Real Bottleneck

> "Culture is the real bottleneck. Fear slows AI adoption more than technology."

**Signs of Fear-Based Culture:**
- "AI will take my job"
- "We've always done it this way"
- "What if it makes a mistake?"
- "I don't trust the outputs"

**Signs of AI-Ready Culture:**
- "How can AI help me do better work?"
- "What if we tried a new approach?"
- "Humans verify, AI accelerates"
- "Let's pilot and learn"

### The AI Design Challenge Template

```
How might we _______________
using AI to achieve _______________
without creating new risks in _______________?
```

**Example:**
> "How might we **reduce proposal review time** using AI to achieve **same-day turnaround for standard requests** without creating new risks in **compliance accuracy or customer data exposure**?"

### Day 1 Deliverables
1. **Workflow Autopsy** - Documented current-state process with friction points
2. **Readiness Canvas** - 5-dimension assessment of your org's readiness
3. **Design Challenge** - Focused problem statement using HMW template

---

## Day 2: Mapping & Redesigning Workflows

### Learning Objectives
By the end of Day 2, you will be able to:
- Apply outcome-backward design to workflow problems
- Create before/after workflow maps
- Identify optimal AI insertion points
- Produce an AI-Augmented Process Blueprint

### Outcome-Backward Design

> "Most broken processes stay broken because we start from the first step and work forward."

**Forward Design (Common):**
1. Receive request
2. Check eligibility
3. Gather information
4. Create draft
5. Review and revise
6. Get approval
7. Deliver output

*Problem: Focuses on existing steps, not outcomes*

**Backward Design (Better):**
1. Define: What does "done" look like?
2. Identify: What decisions are required?
3. Determine: What information is needed?
4. Design: Minimum steps to get there

*Benefit: Focuses on outcomes, eliminates unnecessary steps*

### The Outcome Brief

Before redesigning, define success:

| Element | Question | Example |
|---------|----------|---------|
| **Outcome** | What's the final deliverable? | Approved customer proposal |
| **Time Target** | How fast should it be? | Same-day for standard requests |
| **Quality Standard** | What defines "good enough"? | Zero compliance errors, 90% acceptance |
| **Cost Constraint** | What resources are available? | Max 30 min human time |
| **Risk Boundaries** | What can't go wrong? | No pricing errors, no data leaks |

### Workflow Mapping Legend

Use consistent color coding:

| Tag | Description | Examples |
|-----|-------------|----------|
| **HUMAN** (Blue) | Actions requiring human judgment, creativity, or accountability | Final approval, relationship calls, exceptions |
| **AI/AUTO** (Green) | Tasks AI or automation can handle | Data extraction, draft generation, validation |
| **DECISION** (Yellow) | Branch points where outcomes depend on conditions | Standard vs. custom, approve vs. escalate |

### AI Role Types in Workflows

| AI Role | What It Does | Examples |
|---------|--------------|----------|
| **Analyzer** | Extracts insights from data | Summarize history, flag anomalies |
| **Generator** | Creates draft content | Write proposals, generate options |
| **Recommender** | Suggests actions based on patterns | Recommend pricing, suggest next steps |
| **Validator** | Checks work against rules | Verify compliance, check for errors |
| **Router** | Directs work to right destination | Triage tickets, assign to specialist |

### Identifying AI Insertion Points

**Good Candidates for AI:**
- Repetitive with slight variations
- Time-consuming but low-judgment
- Data gathering and summarization
- First drafts that need human polish
- Pattern matching and classification
- Quality checks against known rules

**Keep Human for Now:**
- Final accountability decisions
- Novel/unprecedented situations
- Relationship-critical moments
- Ethical or legal gray areas
- Creative strategy
- Exception handling

### Before/After Mapping Example

**Before (Current State) - 4-6 hours:**
1. HUMAN: Receive request via email
2. HUMAN: Search for customer history
3. HUMAN: Check eligibility manually
4. HUMAN: Draft proposal from scratch
5. HUMAN: Calculate pricing
6. HUMAN: Send for review
7. DECISION: Approved?
8. HUMAN: Make revisions
9. HUMAN: Send to customer

**After (AI-Augmented) - 30-45 minutes:**
1. AI: Parse request & extract requirements
2. AI: Retrieve & summarize customer history
3. AI: Check eligibility against rules
4. DECISION: Standard or custom?
5. AI: Generate proposal draft
6. AI: Calculate pricing options
7. HUMAN: Review & personalize
8. AI: Validate compliance
9. HUMAN: Final approval & send

### The Process Blueprint Template

| Section | Contents |
|---------|----------|
| **Process Overview** | 1-2 sentence summary |
| **Trigger** | What initiates this workflow? |
| **Inputs** | Data/information required |
| **Outputs** | Deliverable when complete |
| **Workflow Steps** | Numbered steps with Human/AI/Decision tags |
| **Guardrails** | Rules and limits for AI actions |
| **Success Metrics** | How you'll measure improvement |

### Day 2 Deliverables
1. **Outcome Brief** - Clear definition of success with measurable targets
2. **Before/After Map** - Visual workflow comparison with color-coded roles
3. **Process Blueprint** - 1-2 page document ready for review

---

## Day 3: Governance, Safety & Human-in-the-Loop

### Learning Objectives
By the end of Day 3, you will be able to:
- Classify AI risks across five dimensions
- Select appropriate oversight models (HITL/HOTL/HOOTL)
- Design escalation paths and verification steps
- Complete a Governance Canvas for your workflow

> "Governance isn't a blocker — it enables scale."

### The Five AI Risk Dimensions

| Dimension | Risk Types | Key Questions |
|-----------|------------|---------------|
| **Data Risk** | Privacy, exposure, lineage, integrity, retention | What data does AI access? Where does it go? |
| **Model Risk** | Hallucinations, bias, drift, confidence gaps | How might AI outputs be wrong? |
| **Operational Risk** | Workflow failures, poor handoffs, monitoring gaps | What if the AI is unavailable? |
| **Security Risk** | Prompt injection, unauthorized access, data leakage | How could this be exploited? |
| **Reputational Risk** | Harmful outputs, customer confusion, fairness issues | What would the headline be if this fails? |

### Risk Classification Matrix

**Impact Levels:**
- **Low:** Minor inconvenience, easily corrected
- **Medium:** Customer impact, requires intervention
- **High:** Regulatory, legal, or significant financial

**Likelihood Levels:**
- **Rare:** Edge case, unlikely to occur
- **Possible:** May occur occasionally
- **Likely:** Expected to occur regularly

**Priority = Impact × Likelihood**

Focus governance controls on high-priority risks first.

### Three Oversight Archetypes

| Model | How It Works | Best For |
|-------|--------------|----------|
| **Human-in-the-Loop (HITL)** | AI drafts → Human approves every output | Medium-risk decisions, learning phases |
| **Human-on-the-Loop (HOTL)** | AI executes → Human monitors exceptions | High-volume, low-risk tasks |
| **Human-out-of-Loop (HOOTL)** | AI executes autonomously | Structured, rule-based, pre-approved only |

### Choosing the Right Oversight Model

| Factor | HITL | HOTL | HOOTL |
|--------|------|------|-------|
| Decision reversibility | Irreversible | Somewhat | Fully reversible |
| Stakes | High | Medium | Low |
| Volume | Low | Medium-high | Very high |
| Pattern clarity | Novel/unclear | Known + exceptions | Fully defined rules |
| Error tolerance | Near-zero | Some acceptable | Minimal impact |

### Designing Escalation Paths

```
AI Processes Task
        ↓
   [Confidence Check]
        ↓
   ┌────┴────┬────────┐
   ↓         ↓        ↓
High      Medium     Low/Anomaly
   ↓         ↓        ↓
Auto-     Human    Escalate
Complete  Review   to Expert
```

### Verification Steps

Build checkpoints into your workflow:

| Type | What It Checks |
|------|----------------|
| **Format Check** | Output structure correct? |
| **Rule Check** | Business rules followed? |
| **Completeness** | All required fields present? |
| **Consistency** | Data matches across sources? |
| **Confidence** | AI certainty above threshold? |
| **Sampling** | Random human review % |

**Example Verification Schedule:**
- After AI draft: Check pricing within approved ranges
- Before send: Verify customer name/details correct
- Weekly: Sample 10% for quality review
- Monthly: Compare AI vs. human accuracy

### The Governance Canvas

One-page compliance document:

| Section | Contents |
|---------|----------|
| Workflow Name & ID | Name, version, owner |
| Scope & Boundaries | What this does/doesn't cover |
| AI Capabilities Used | Models, tools, integrations |
| Human Roles & Responsibilities | Who does what, when |
| Risk Assessment | Key risks and mitigations |
| Oversight Model | HITL/HOTL/HOOTL and why |
| Logging & Audit Trail | What gets recorded |
| Success Metrics & Review Cadence | KPIs and review schedule |

### Day 3 Deliverables
1. **Risk-Annotated Map** - Workflow with risks color-coded by severity
2. **Oversight Architecture** - Diagram showing checkpoints and escalation paths
3. **Governance Canvas** - Single-page compliance document

---

## Day 4: Building the Internal AI Playbook

### Learning Objectives
By the end of Day 4, you will be able to:
- Write clear, actionable process documentation
- Create effective prompt templates and examples
- Design verification checklists
- Produce a working AI Playbook draft

> "Tools come and go. A well-written playbook survives tools."

### What Makes a Good Playbook?

**Effective Playbooks:**
- Written for someone with no context
- Uses plain language, not jargon
- Shows examples, not just instructions
- Includes "what if" scenarios
- Has clear success criteria
- Tells you when NOT to use it

**Ineffective Playbooks:**
- Assumes reader knows the context
- Full of acronyms and insider terms
- Only describes happy path
- No examples or templates
- Unclear ownership
- Never updated after creation

### Playbook Structure

| Section | Purpose | Length |
|---------|---------|--------|
| **Overview** | What this playbook helps you do | 2-3 sentences |
| **When to Use** | Triggers and conditions | Bullet list |
| **When NOT to Use** | Exceptions and escalations | Bullet list |
| **Step-by-Step Process** | Detailed instructions with AI/Human tags | 1-2 pages |
| **Prompts & Templates** | Copy-paste ready examples | As needed |
| **Verification Checklist** | How to check AI outputs | Checklist format |
| **Troubleshooting** | Common problems and solutions | FAQ format |
| **Contacts & Escalation** | Who to ask for help | Names/roles |

### Writing Effective Prompts

**Prompt Structure:**
```
Role: You are a [role] helping with [task]
Context: Here is the relevant information: [data]
Task: Please [specific action]
Format: Provide your response as [format]
Constraints: Make sure to [rules/limits]
```

**Example:**
```
You are a proposal specialist helping prepare customer quotes.

Context: Customer ABC Corp requested pricing for [PRODUCT].
Their history shows [HISTORY SUMMARY].

Task: Draft a proposal email including pricing options and next steps.

Format: Professional email, 3 paragraphs max.

Constraints: Use only approved pricing from the rate card.
Do not promise delivery dates.
```

### Verification Checklists

Create checklists for humans reviewing AI outputs:

**Example: Proposal Review Checklist**
- [ ] Customer name spelled correctly
- [ ] Pricing matches rate card
- [ ] No unauthorized discounts
- [ ] Terms & conditions included
- [ ] Expiration date set correctly
- [ ] No confidential info exposed
- [ ] Tone appropriate for customer
- [ ] Call-to-action is clear

**Checklist Design Principles:**
- **Binary:** Yes/No questions only
- **Observable:** Can be verified objectively
- **Ordered:** Critical items first
- **Actionable:** Clear what to do if fails
- **Brief:** 5-10 items maximum

### Documenting Handoffs

Be explicit about who does what:

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 1 | AI | Parse request & extract requirements | Structured list |
| 2 | AI | Generate proposal draft | Draft document |
| 3 | HUMAN | Review against checklist | Approved/revised draft |
| 4 | DECISION | Is value > $50K? | Route appropriately |
| 5 | HUMAN | Send with personal note | Sent + logged |

### Troubleshooting Section

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| AI generates nonsense | Input data malformed | Check source format; re-run |
| Wrong customer info | CRM sync delay | Manually verify; wait 10 min |
| Pricing seems wrong | Rate card outdated | Check version; escalate |
| AI tool unavailable | Service outage | Use manual process; check status |
| Data exposure risk | PII in prompt | STOP. Report to security. |

### Day 4 Deliverables
1. **Complete Playbook Draft** - 3-5 pages with all sections
2. **Prompt Templates** - Ready-to-use prompts with placeholders
3. **Verification Checklist** - Binary checklist for reviewing AI outputs

---

## Day 5: Capstone & Rollout

### Learning Objectives
By the end of Day 5, you will be able to:
- Present your AI workflow to stakeholders
- Defend your governance and design decisions
- Create a 30-60-90 day rollout plan
- Establish maintenance and improvement processes

> "AI doesn't replace workflows; it refactors them."

### Capstone Presentation Structure

| Section | Time | Content |
|---------|------|---------|
| **The Problem** | 1 min | Pain points from workflow autopsy |
| **The Solution** | 2 min | Before/After workflow with AI roles |
| **Governance** | 2 min | Risks, oversight model, verification |
| **Demo** | 2 min | Walk through with real/simulated data |
| **Rollout Plan** | 2 min | 30-60-90 implementation plan |
| **Ask** | 1 min | What you need to move forward |

### Common Failure Points

**Technical Failures:**
- Unclear verification steps
- Missing data assumptions
- Poorly defined handoffs
- No fallback for AI unavailability
- Ambiguous prompt templates

**Process Failures:**
- Unclear ownership
- No escalation path
- Missing edge cases
- Untested with real data
- No success metrics defined

### Defending Your Design Decisions

**Common Challenges:**
- "Why does a human need to review this?"
- "Why can't AI do this step too?"
- "What if the AI makes a mistake?"
- "Is this compliant with [regulation]?"
- "How do we know this is working?"

**Strong Answers Include:**
- Reference to risk assessment
- Clear accountability chain
- Specific verification steps
- Measurable success criteria
- Escalation procedures
- Maintenance ownership

### The 30-60-90 Day Rollout Plan

**Days 1-30: Stabilize**
- Focus: Small group pilot (2-3 users)
- Activities: Daily check-ins, log every issue, refine playbook
- Exit Criteria: No critical issues for 1 week

**Days 31-60: Expand**
- Focus: Add teams (10-20 users)
- Activities: Weekly check-ins, train new users, collect feedback
- Exit Criteria: Positive feedback, metrics improving

**Days 61-90: Operationalize**
- Focus: Full integration (all target users)
- Activities: Standard process, upstream/downstream integration
- Exit Criteria: Process is the new normal

### Living Systems Maintenance

> "Treat AI systems as living systems — with owners, updates, and accountability."

**Maintenance Schedule:**
- **Weekly:** Review exception logs
- **Monthly:** Analyze success metrics
- **Quarterly:** Update prompts and playbook
- **As Needed:** Respond to tool changes
- **Annually:** Full governance review

**Ownership Roles:**
- **Process Owner:** Accountable for outcomes
- **Technical Owner:** Maintains integrations
- **Governance Owner:** Ensures compliance
- **Training Owner:** Onboards new users

### Day 5 Deliverables
1. **Capstone Presentation** - 8-10 minutes with demo
2. **Complete Playbook** - Polished, peer-tested documentation
3. **Rollout Plan** - 30-60-90 day plan with owners and metrics

---

## Templates and Frameworks

### AI Design Challenge Template
```
How might we _______________
using AI to achieve _______________
without creating new risks in _______________?
```

### Outcome Brief Template
```
OUTCOME: [Final deliverable]
TIME TARGET: [Speed requirement]
QUALITY STANDARD: [Success criteria]
COST CONSTRAINT: [Resource limits]
RISK BOUNDARIES: [What can't go wrong]
```

### Governance Canvas Template
```
WORKFLOW NAME: _____________ VERSION: _____ OWNER: _____

SCOPE: What this workflow covers/doesn't cover
_________________________________________________

AI CAPABILITIES: Models and tools used
_________________________________________________

HUMAN ROLES: Who does what
_________________________________________________

RISKS & MITIGATIONS:
Risk 1: _____________ Mitigation: _____________
Risk 2: _____________ Mitigation: _____________

OVERSIGHT MODEL: [ ] HITL  [ ] HOTL  [ ] HOOTL
Rationale: _________________________________________________

LOGGING: What gets recorded
_________________________________________________

SUCCESS METRICS: How we measure
_________________________________________________

REVIEW CADENCE: [ ] Weekly  [ ] Monthly  [ ] Quarterly
```

### Rollout Plan Template
| Phase | Timeline | Users | Activities | Metrics | Risks |
|-------|----------|-------|------------|---------|-------|
| Pilot | Days 1-30 | | | | |
| Expand | Days 31-60 | | | | |
| Scale | Days 61-90 | | | | |

---

## Quick Reference

### Key Quotes to Remember
- "Start with pain, not platforms."
- "Culture is the real bottleneck."
- "Governance isn't a blocker — it enables scale."
- "Tools come and go. A well-written playbook survives tools."
- "AI doesn't replace workflows; it refactors them."
- "Organizational change depends on people, not technology alone."

### AI Role Types
| Role | Function |
|------|----------|
| Analyzer | Extract insights |
| Generator | Create content |
| Recommender | Suggest actions |
| Validator | Check against rules |
| Router | Direct to destination |

### Oversight Models
| Model | Pattern |
|-------|---------|
| HITL | AI drafts → Human approves |
| HOTL | AI executes → Human monitors |
| HOOTL | AI fully autonomous |

### Risk Dimensions
1. Data Risk
2. Model Risk
3. Operational Risk
4. Security Risk
5. Reputational Risk

### Course Deliverables Checklist
- [ ] Workflow Autopsy
- [ ] AI Readiness Canvas
- [ ] AI Design Challenge
- [ ] Outcome Brief
- [ ] Before/After Workflow Map
- [ ] Process Blueprint
- [ ] Risk-Annotated Map
- [ ] Oversight Architecture
- [ ] Governance Canvas
- [ ] AI Playbook (3-5 pages)
- [ ] Prompt Templates
- [ ] Verification Checklist
- [ ] Capstone Presentation
- [ ] 30-60-90 Rollout Plan

---

*Remember: The goal is not to implement AI everywhere, but to implement it where it creates genuine value with appropriate governance.*
