# Course Viewer Project

## Overview
Educational course platform with HTML slides and Jupyter notebook labs for Python and AI/ML training. Built for AI Elevate training programs.

## Project Structure
```
course-viewer/
├── python-fundamentals/        # Basic Python (1 day)
├── python-intermediate/        # Intermediate Python (2 days)
├── ai-plain-english/           # AI concepts for non-technical audiences
├── ai-sales-marketing/         # AI for Sales & Marketing (2 days)
├── enterprise-ai-adoption/     # Enterprise AI strategy (2 days)
├── mastering-ai-agents/        # AI Agents, Swarms, A2A (3 days)
├── use-case-prompting-seminar/ # Prompting & Use Cases (90 min)
├── ai-ml-data-scientists/      # AI/ML for Data Scientists (3 days)
├── out/                        # Mastering AI course outputs
└── src/                        # Flask app, workspaces
```

## Courses

### Python Fundamentals (1 day)
- **Slides:** `python-fundamentals/python-fundamentals-slides.html`
- **Topics:** Variables, data types, strings, lists, dictionaries, control flow, functions, error handling, files, modules, tuples, sets, boolean logic, loop control, enumerate/zip, sorting, nested data, JSON, PEP 8

### Python Intermediate (2 days)
- **Slides:** `python-intermediate/python-intermediate-slides.html`
- **Topics:** OOP (classes, inheritance, polymorphism), properties, pattern matching, functional programming (lambda, map, filter, reduce), closures, decorators, generators, partial functions, currying, lazy evaluation, testing (unittest, pytest)

### AI for Sales and Marketing (2 days)
- **Slides:** `ai-sales-marketing/ai-sales-marketing-slides.html` (33 slides)
- **Topics:** Content generation, prompt engineering (CRAFT), lead scoring, campaign analytics, customer engagement, personalization, A/B testing, implementation strategy
- **Materials:** Student notes, lab exercises, prompt library templates

### Enterprise AI Adoption (2 days)
- **Slides:** `enterprise-ai-adoption/enterprise-ai-adoption-slides.html`
- **Topics:** AI strategy, governance, implementation roadmaps, change management, risk assessment
- **Materials:** Case studies, facilitator guide, CSV templates (readiness canvas, governance, stakeholder analysis)

### Mastering AI Agents (3 days)
- **Slides:** `mastering-ai-agents/mastering-ai-agents-slides.html`
- **Topics:** Reactive vs deliberative agents, agent architectures, swarm intelligence, Google A2A protocol
- **Labs:** Jupyter notebooks for agent types demo, reactive agents, swarm intelligence

### Use Case Lab & Prompting Foundations (90 min seminar)
- **Slides:** `use-case-prompting-seminar/use-case-prompting-slides.html`
- **Topics:** CRAFT framework, context engineering, use case identification, prompt engineering techniques
- **Materials:** Interactive demo guide (instructor), take-home exercise PDF
- **Client:** ITAG Skillnet AI Advantage

### AI/ML for Data Scientists (3 days)
- **Slides:** `ai-ml-data-scientists/ai-ml-data-scientists-slides.html` (32 slides)
- **Topics:**
  - Day 1: ML foundations, data preprocessing, feature engineering, model selection, evaluation metrics
  - Day 2: Deep learning, CNNs, RNNs, Transformers, transfer learning, AutoML, multimodal AI
  - Day 3: MLOps, model deployment, monitoring, responsible AI, explainability
- **Labs:** Data preprocessing (scikit-learn), Deep learning (PyTorch)

### Mastering AI / LLMs (multi-day)
- **Slides:** `out/mastering-ai-slides.html`, `out/mastering-ai-part1-slides.html`
- **Topics:** ML foundations, neural networks, NLP, transformers, LLMs, RAG, agents
- **Labs:** Python data science, ML with PyTorch, NLP, generative AI with Ollama

## Slide HTML Format
- Custom reveal.js-style with `<div class="slide" id="slideX">`
- CSS classes: `.two-column`, `.three-column`, `.four-column`, `.card`, `.code-block`, `.tip-box`, `.warning-box`, `.highlight-box`, `.success-box`, `.comparison-table`
- Animations: `fadeInUp`, `pulse`, `glow`, `float`, `slideInLeft`, `slideInRight`
- Navigation script at bottom with `totalSlides` variable
- PDF versions generated with weasyprint

## Lab Notebook Format
- Jupyter notebooks with markdown instruction cells and code cells
- Code cells use `# YOUR CODE HERE` placeholders
- Solutions in separate `-solution.ipynb` files

## Commands
- Virtual env: `.venv/bin/python`
- Tests: `.venv/bin/pytest`
- PDF generation: `.venv/bin/python` with weasyprint

## App Registration
All courses registered in `src/app.py` in the `COURSES` dictionary with sections for slides, materials, labs, templates.

## Git
- Branch: master
- Remote: github.com:redmage123/course-viewer.git
