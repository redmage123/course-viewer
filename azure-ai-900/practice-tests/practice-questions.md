# Azure AI-900 Practice Questions

## Instructions
These practice questions are designed to help you prepare for the AI-900 exam. Try to answer each question before checking the answer.

---

## Section 1: AI & ML Fundamentals (20-25%)

### Question 1
You need to predict whether an email is spam or not spam based on historical labeled data. Which type of machine learning should you use?

A) Unsupervised learning
B) Reinforcement learning
C) Supervised learning
D) Transfer learning

<details>
<summary>Show Answer</summary>

**Answer: C) Supervised learning**

Explanation: This is a classification problem with labeled data (spam/not spam), which is supervised learning. Classification predicts discrete categories.
</details>

---

### Question 2
Which of the following is NOT one of Microsoft's Responsible AI principles?

A) Fairness
B) Profitability
C) Transparency
D) Accountability

<details>
<summary>Show Answer</summary>

**Answer: B) Profitability**

Explanation: The 6 Responsible AI principles are: Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, and Accountability.
</details>

---

### Question 3
You want to automatically find the best machine learning algorithm for your dataset without writing code. Which Azure ML feature should you use?

A) Azure ML Designer
B) Automated ML
C) Azure AI Vision
D) Azure OpenAI

<details>
<summary>Show Answer</summary>

**Answer: B) Automated ML**

Explanation: Automated ML automatically tests multiple algorithms and hyperparameters to find the best model for your data.
</details>

---

### Question 4
What type of machine learning uses rewards and penalties to learn optimal behavior?

A) Supervised learning
B) Unsupervised learning
C) Reinforcement learning
D) Semi-supervised learning

<details>
<summary>Show Answer</summary>

**Answer: C) Reinforcement learning**

Explanation: Reinforcement learning uses an agent that learns through trial and error, receiving rewards for good actions and penalties for bad ones.
</details>

---

### Question 5
Which machine learning type would you use to group customers into segments without predefined labels?

A) Classification
B) Regression
C) Clustering
D) Anomaly detection

<details>
<summary>Show Answer</summary>

**Answer: C) Clustering**

Explanation: Clustering is an unsupervised learning technique that groups similar items together without predefined labels.
</details>

---

## Section 2: Computer Vision (15-20%)

### Question 6
You need to extract text from scanned documents. Which Azure AI service should you use?

A) Azure AI Language
B) Azure AI Vision
C) Azure AI Speech
D) Azure Machine Learning

<details>
<summary>Show Answer</summary>

**Answer: B) Azure AI Vision**

Explanation: Azure AI Vision includes OCR (Optical Character Recognition) capabilities for extracting text from images and documents.
</details>

---

### Question 7
What is the minimum number of images per tag recommended for Custom Vision?

A) 1
B) 5
C) 15
D) 50

<details>
<summary>Show Answer</summary>

**Answer: B) 5**

Explanation: Custom Vision requires a minimum of 5 images per tag, though 50+ images per tag is recommended for better accuracy.
</details>

---

### Question 8
Which computer vision task draws bounding boxes around detected items?

A) Image classification
B) Object detection
C) Semantic segmentation
D) Image generation

<details>
<summary>Show Answer</summary>

**Answer: B) Object detection**

Explanation: Object detection locates objects in an image and draws bounding boxes around them, also classifying what each object is.
</details>

---

### Question 9
You want to build a model to identify different types of products on store shelves. Which Custom Vision project type should you use?

A) Classification
B) Object Detection
C) Semantic Segmentation
D) Instance Segmentation

<details>
<summary>Show Answer</summary>

**Answer: B) Object Detection**

Explanation: Object detection is needed when you want to locate multiple objects within an image and identify what each one is.
</details>

---

### Question 10
Which Azure service would you use to extract structured data from invoices?

A) Azure AI Vision
B) Azure AI Document Intelligence
C) Azure AI Language
D) Azure OpenAI

<details>
<summary>Show Answer</summary>

**Answer: B) Azure AI Document Intelligence**

Explanation: Azure AI Document Intelligence (formerly Form Recognizer) has pre-built models specifically for invoices, receipts, and other business documents.
</details>

---

## Section 3: Natural Language Processing (15-20%)

### Question 11
Which Azure AI Language feature would you use to determine if a product review is positive or negative?

A) Key phrase extraction
B) Named entity recognition
C) Sentiment analysis
D) Language detection

<details>
<summary>Show Answer</summary>

**Answer: C) Sentiment analysis**

Explanation: Sentiment analysis determines whether text expresses positive, negative, or neutral sentiment.
</details>

---

### Question 12
What replaced LUIS (Language Understanding Intelligent Service) in Azure AI Language?

A) Custom Question Answering
B) Conversational Language Understanding (CLU)
C) Text Analytics
D) Azure OpenAI

<details>
<summary>Show Answer</summary>

**Answer: B) Conversational Language Understanding (CLU)**

Explanation: CLU is the successor to LUIS and is used to identify intents and extract entities from conversational input.
</details>

---

### Question 13
Which feature of Azure AI Speech controls pronunciation, pitch, and pauses?

A) Neural Voice
B) SSML
C) Speaker Diarization
D) Custom Speech

<details>
<summary>Show Answer</summary>

**Answer: B) SSML**

Explanation: SSML (Speech Synthesis Markup Language) is used to control how text-to-speech output is pronounced, including pitch, rate, and pauses.
</details>

---

### Question 14
You need to build a FAQ bot that answers questions from a knowledge base. Which Azure AI Language feature should you use?

A) Sentiment Analysis
B) Key Phrase Extraction
C) Custom Question Answering
D) Named Entity Recognition

<details>
<summary>Show Answer</summary>

**Answer: C) Custom Question Answering**

Explanation: Custom Question Answering (formerly QnA Maker) is designed for building FAQ bots from knowledge bases.
</details>

---

### Question 15
What does NER stand for in NLP?

A) Natural Entity Recognition
B) Named Entity Recognition
C) Neural Entity Retrieval
D) Natural Expression Recognition

<details>
<summary>Show Answer</summary>

**Answer: B) Named Entity Recognition**

Explanation: NER identifies and categorizes named entities in text, such as people, places, organizations, dates, etc.
</details>

---

## Section 4: Generative AI (15-20%)

### Question 16
In Azure OpenAI, what controls the randomness of generated output?

A) Max tokens
B) Top P
C) Temperature
D) Frequency penalty

<details>
<summary>Show Answer</summary>

**Answer: C) Temperature**

Explanation: Temperature controls randomness: 0 is deterministic (same output each time), 1 is more creative/random.
</details>

---

### Question 17
What is RAG in the context of generative AI?

A) Random Access Generation
B) Retrieval-Augmented Generation
C) Real-time AI Grounding
D) Recursive Algorithm Generation

<details>
<summary>Show Answer</summary>

**Answer: B) Retrieval-Augmented Generation**

Explanation: RAG is a pattern that retrieves relevant information from a data source and augments the prompt to ground LLM responses in factual data.
</details>

---

### Question 18
Which prompt engineering technique includes example inputs and outputs?

A) Zero-shot
B) Few-shot
C) Chain of thought
D) Role playing

<details>
<summary>Show Answer</summary>

**Answer: B) Few-shot**

Explanation: Few-shot prompting includes examples of input/output pairs to help the model understand the desired format and behavior.
</details>

---

### Question 19
What type of message in Azure OpenAI sets the behavior and context for the entire conversation?

A) User message
B) Assistant message
C) System message
D) Function message

<details>
<summary>Show Answer</summary>

**Answer: C) System message**

Explanation: The system message establishes the AI's behavior, personality, and context for the conversation.
</details>

---

### Question 20
Which Azure service would you use for enterprise-grade GPT model access with content filtering?

A) OpenAI directly
B) Azure AI Language
C) Azure OpenAI Service
D) Azure Machine Learning

<details>
<summary>Show Answer</summary>

**Answer: C) Azure OpenAI Service**

Explanation: Azure OpenAI Service provides access to OpenAI models with enterprise security, compliance, and built-in content filtering.
</details>

---

## Section 5: Mixed Topics

### Question 21
What is the term for when an AI generates false or inaccurate information?

A) Grounding
B) Hallucination
C) Inference
D) Embedding

<details>
<summary>Show Answer</summary>

**Answer: B) Hallucination**

Explanation: Hallucination refers to AI generating content that sounds plausible but is factually incorrect.
</details>

---

### Question 22
Which Azure AI content safety category includes discrimination and slurs?

A) Violence
B) Sexual
C) Hate
D) Self-harm

<details>
<summary>Show Answer</summary>

**Answer: C) Hate**

Explanation: The Hate category covers content related to discrimination, prejudice, and slurs.
</details>

---

### Question 23
What is the purpose of embeddings in AI?

A) Generate images
B) Represent text as numeric vectors
C) Translate languages
D) Detect faces

<details>
<summary>Show Answer</summary>

**Answer: B) Represent text as numeric vectors**

Explanation: Embeddings convert text into numeric vectors that capture semantic meaning, enabling similarity comparisons and search.
</details>

---

### Question 24
Which Responsible AI principle ensures AI systems work for people with disabilities?

A) Fairness
B) Inclusiveness
C) Transparency
D) Privacy

<details>
<summary>Show Answer</summary>

**Answer: B) Inclusiveness**

Explanation: Inclusiveness ensures AI empowers everyone and engages all people regardless of ability.
</details>

---

### Question 25
You want to convert speech to text in real-time during a meeting. Which Azure service should you use?

A) Azure AI Language
B) Azure AI Speech
C) Azure AI Vision
D) Azure OpenAI

<details>
<summary>Show Answer</summary>

**Answer: B) Azure AI Speech**

Explanation: Azure AI Speech provides real-time speech-to-text transcription capabilities.
</details>

---

## Scoring Guide

- 20-25 correct: Excellent! You're well-prepared for the exam.
- 15-19 correct: Good foundation, review weak areas.
- 10-14 correct: Need more study time, focus on core concepts.
- Below 10: Review all course materials before attempting the exam.

---

## Additional Practice

For more practice questions, visit:
- [Microsoft Learn Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/practice/assessment)
- [Azure AI-900 Exam Page](https://learn.microsoft.com/en-us/credentials/certifications/exams/ai-900/)
