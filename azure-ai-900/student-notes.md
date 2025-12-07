# Azure AI-900: AI Fundamentals - Student Notes

## Course Overview

This 3-day certification prep course covers all domains tested on the Microsoft Azure AI Fundamentals (AI-900) exam.

**Exam Details:**
- Cost: $165 USD
- Questions: 40-60
- Passing Score: 700/1000
- Duration: ~60 minutes

---

## Day 1: AI & Machine Learning Fundamentals

### What is Artificial Intelligence?

AI is software that imitates human behaviors and capabilities:
- **Machine Learning** - Learning from data
- **Computer Vision** - Interpreting visual information
- **Natural Language Processing** - Understanding text/speech
- **Document Intelligence** - Extracting information from documents

**Key Hierarchy:**
```
Artificial Intelligence (broadest)
    └── Machine Learning
            └── Deep Learning (neural networks)
```

### Types of Machine Learning

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Supervised** | Training with labeled data | Classification, Regression |
| **Unsupervised** | Finding patterns without labels | Clustering, Anomaly Detection |
| **Reinforcement** | Learning through trial and error | Game AI, Robotics |

**Classification vs Regression:**
- Classification: Predict categories (spam/not spam)
- Regression: Predict numeric values (house prices)

### ML Model Training Process

1. **Data Collection & Preparation** - Gather, clean, split data
2. **Feature Engineering** - Select relevant features
3. **Model Training** - Algorithm learns patterns
4. **Model Evaluation** - Test with validation data
5. **Deployment & Inference** - Use model for predictions

### Azure AI Services Overview

Pre-built AI capabilities accessed via REST APIs:

| Service | Capabilities |
|---------|-------------|
| **Azure AI Vision** | Image analysis, Face detection, OCR |
| **Azure AI Language** | Text analytics, Question answering, Translation |
| **Azure AI Speech** | Speech-to-text, Text-to-speech, Translation |
| **Azure OpenAI** | GPT models, DALL-E, Embeddings |

**Provisioning:** Create resource in Azure portal → Get endpoint URL + API key

### Azure Machine Learning

Platform for building custom ML models:

- **Azure ML Designer** - Drag-and-drop visual ML building
- **Automated ML** - Automatically finds best algorithm and hyperparameters

**Workspace Components:**
- Compute: VMs and clusters for training
- Datastores: Connect to data sources
- Datasets: Versioned data references
- Pipelines: Automated workflows
- Models: Trained model registry
- Endpoints: Deploy models as APIs

### Responsible AI Principles (Memorize All 6!)

1. **Fairness** - Treat all people fairly without bias
2. **Reliability & Safety** - Perform reliably under various conditions
3. **Privacy & Security** - Protect user data
4. **Inclusiveness** - Empower everyone regardless of ability
5. **Transparency** - Systems should be understandable
6. **Accountability** - People accountable for AI systems

---

## Day 2: Computer Vision & NLP

### Computer Vision Workloads

| Workload | Description |
|----------|-------------|
| **Image Classification** | Categorize entire images |
| **Object Detection** | Locate objects with bounding boxes |
| **Semantic Segmentation** | Pixel-level classification |
| **Face Detection** | Detect and analyze faces |
| **OCR** | Extract text from images |

### Azure AI Vision Service

**Image Analysis 4.0 Features:**
- Tags: Content labels
- Captions: Natural language descriptions
- Objects: Detected with bounding boxes
- People: Detection and positioning
- Smart Crops: Intelligent thumbnails

**Face Service:**
- Face detection & attributes
- Face verification (1:1)
- Face identification (1:many)
- *Note: Limited access policy for identification*

### Custom Vision Service

Train your own vision models with minimal data.

**Requirements:**
- Minimum 5 images per tag
- Recommended: 50+ images per tag

**Project Types:**
- Classification: Categorize whole images
- Object Detection: Locate and classify objects

**Workflow:**
1. Create project → 2. Upload images → 3. Tag images → 4. Train model → 5. Evaluate & Publish

### Natural Language Processing

| Feature | Description |
|---------|-------------|
| **Sentiment Analysis** | Positive/Negative/Neutral + score |
| **Key Phrase Extraction** | Main talking points |
| **Named Entity Recognition** | People, places, organizations |
| **Entity Linking** | Wikipedia connections |
| **PII Detection** | Personal data identification |

### Azure AI Language Service

**Pre-configured Features:**
- Sentiment analysis
- Key phrase extraction
- Named entity recognition
- Language detection

**Customizable Features:**
- Custom text classification
- Custom NER
- Conversational Language Understanding (CLU) - *replaced LUIS*
- Custom question answering

**Language Studio:** Web portal for building and testing without code

### Azure AI Speech Service

| Feature | Description |
|---------|-------------|
| **Speech-to-Text** | Real-time and batch transcription |
| **Text-to-Speech** | Neural voices (natural sounding) |
| **Speech Translation** | 30+ source, 60+ target languages |
| **Speaker Recognition** | Verification (1:1) and Identification (1:many) |

**SSML (Speech Synthesis Markup Language):** Controls pronunciation, pitch, rate, and pauses

### Azure AI Document Intelligence

Formerly Form Recognizer - specialized OCR for structured documents.

**Pre-built Models:**
- Invoice, Receipt, ID Document, Business Card, W-2, Health Insurance

**Capabilities:**
- Layout: Tables, text structure
- General Document: Key-value pairs
- Read: OCR with language detection
- Custom Models: Train for unique forms

---

## Day 3: Generative AI & Exam Prep

### Generative AI Fundamentals

AI that creates new, original content:
- Text generation
- Image generation
- Code generation
- Audio generation

**Key Concepts:**

| Term | Definition |
|------|------------|
| **Tokens** | Units of text processed by LLM |
| **Prompts** | Input text guiding the model |
| **Completions** | Generated output |
| **Temperature** | Controls randomness (0=deterministic, 1=creative) |

### Azure OpenAI Service

Enterprise-grade generative AI with same models as OpenAI:

| Model | Use Case |
|-------|----------|
| **GPT-4, GPT-4 Turbo** | Text/code generation, conversation |
| **GPT-3.5 Turbo** | Faster, cost-effective text generation |
| **DALL-E** | Image generation from text |
| **Embeddings** | Semantic search, similarity |

**Azure OpenAI vs OpenAI:**
- Same models, Microsoft-hosted
- Enterprise security & compliance
- Private networking support
- Built-in content filtering

### Prompt Engineering

**Prompt Components:**
- System Message: Sets behavior and context
- User Message: The actual request
- Assistant Message: Model's response
- Examples: Few-shot learning samples

**Techniques:**

| Technique | Description |
|-----------|-------------|
| Zero-shot | No examples provided |
| Few-shot | Include example inputs/outputs |
| Chain of Thought | Ask model to explain reasoning |
| Role Playing | Assign persona to model |

### Microsoft Copilot

AI assistants across Microsoft products:

- **Microsoft 365 Copilot:** Word, Excel, PowerPoint, Outlook, Teams
- **GitHub Copilot:** Code completion and generation
- **Security Copilot:** Threat analysis, incident response

**How Copilots Work:** LLMs + Your Data + App Context + Grounding

### Azure AI Foundry (formerly AI Studio)

Unified platform for building AI applications:

1. **Explore** - Browse model catalog
2. **Build** - Create with prompt flow
3. **Customize** - Fine-tune models
4. **Evaluate** - Test quality and safety
5. **Deploy** - Production endpoints

### Content Safety

**Content Categories:**
- Hate (discrimination, slurs)
- Sexual (explicit content)
- Violence (graphic violence)
- Self-Harm

**Severity Levels:** Safe (0), Low (2), Medium (4), High (6)

**Azure OpenAI Content Filtering:**
- Default filters applied automatically
- Cannot be completely disabled
- Configurable severity thresholds
- Jailbreak attempt detection

### RAG (Retrieval-Augmented Generation)

Pattern combining retrieval with generation:

1. **Retrieval** - Find relevant documents (Azure AI Search)
2. **Augmentation** - Add to prompt context
3. **Generation** - LLM creates grounded response

**Benefits:**
- Access current information
- Cite sources
- Reduce hallucinations
- Domain-specific responses

---

## Key Terms Quick Reference

| Term | Definition |
|------|------------|
| Token | Unit of text processed by LLM |
| Embedding | Numeric vector representing text |
| Grounding | Connecting AI to factual data |
| Hallucination | AI generating false information |
| Fine-tuning | Additional training on custom data |
| Inference | Using trained model for predictions |
| Intent | User's goal in conversation |
| Entity | Specific data extracted from text |
| Utterance | User input in conversational AI |
| NER | Named Entity Recognition |
| OCR | Optical Character Recognition |
| SSML | Speech Synthesis Markup Language |
| CLU | Conversational Language Understanding |
| RAG | Retrieval-Augmented Generation |

---

## Exam Tips

1. **Know when to use each service:**
   - Image analysis → Azure AI Vision
   - Form extraction → Document Intelligence
   - Sentiment → Azure AI Language
   - Custom ML model → Azure Machine Learning
   - Text generation → Azure OpenAI

2. **Memorize the 6 Responsible AI principles**

3. **Understand the difference:**
   - Azure AI Services = Pre-built models
   - Azure Machine Learning = Build custom models

4. **Practice with Azure portal and AI Studio**

5. **Focus on scenarios:** Questions often describe a business problem and ask which service solves it

---

## Additional Resources

- [Microsoft Learn AI-900 Learning Path](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/)
- [AI-900 Study Guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-900)
- [Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/practice/assessment)
- [Azure AI Services Documentation](https://learn.microsoft.com/en-us/azure/ai-services/)
