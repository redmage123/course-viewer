# Data Discovery: Harnessing AI, AGI & Vector Databases
## Student Notes

**Course Duration:** 2 Days
**Target Audience:** Data engineers, data scientists, compliance professionals, and IT architects

---

## Day 1: Discovery & Classification

### What is Data Discovery?

Data discovery is the process of finding, understanding, and cataloguing data assets across an organisation to unlock value and ensure compliance.

**Three Pillars:**
- **Identify** — Locate data assets across silos, databases, file shares, cloud storage, and SaaS platforms
- **Classify** — Categorise data by type, sensitivity, ownership, and business relevance using AI
- **Catalogue** — Build a searchable inventory with metadata, lineage, and access controls

**Key Insight:** Data discovery transforms dark data into actionable intelligence. Without discovery, organisations cannot govern what they do not know exists.

---

### The Data Discovery Landscape

**Key Statistics:**
- 175 ZB of global data by 2025
- 68% of enterprise data goes unused
- $3.92M average cost of a data breach
- 73% of analysts' time is spent finding data

---

### Structured vs Unstructured Data

| Aspect | Structured Data | Unstructured Data |
|--------|----------------|-------------------|
| **Format** | Tables, rows, columns | Text, images, audio, video |
| **Storage** | RDBMS, data warehouses | Data lakes, object stores |
| **Discovery** | Schema inspection, profiling | NLP, computer vision, embeddings |
| **Classification** | Rule-based + ML | Deep learning, transformers |
| **Volume** | ~20% of enterprise data | ~80% of enterprise data |

**Key Fact:** 80% of enterprise data is unstructured and growing 55-65% annually.

---

### Traditional vs AI-Driven Discovery

| Aspect | Traditional | AI-Driven |
|--------|-----------|-----------|
| **Method** | Manual inventories, spreadsheets | Automated scanning & profiling |
| **Search** | Keyword-based | Semantic search with embeddings |
| **Classification** | Regex, rule-based | ML (supervised + unsupervised) |
| **Catalogue** | Static, manual updates | Dynamic, self-updating |
| **Frequency** | Periodic audits | Continuous real-time monitoring |

---

### How AI Enhances Data Discovery

**Pipeline:**
```
Ingest → NLP / Embeddings → Classify → Catalogue → Search
```

**AI Techniques:**
- **NLP:** Named Entity Recognition, topic modelling, text classification
- **Machine Learning:** TF-IDF + RandomForest (supervised), KMeans (unsupervised)
- **Embeddings:** Sentence transformers for semantic similarity search and duplicate detection

---

### ML for Data Classification

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Vectorise text descriptions
tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
X = tfidf.fit_transform(df['description'])
y = df['category']

# Train / test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train a RandomForest classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
print(classification_report(y_test, clf.predict(X_test)))
```

**Why TF-IDF + RandomForest?** Simple, interpretable, works well on tabular metadata. For larger corpora, consider fine-tuned transformers.

---

### Text Classification Approaches

| Method | Technique | Accuracy | Speed | Best For |
|--------|-----------|----------|-------|----------|
| **Regex / Rules** | Pattern matching | Low-Med | Very Fast | Known patterns (SSN, emails) |
| **TF-IDF + ML** | Bag-of-words + classifier | Med-High | Fast | Document categorisation |
| **Word Embeddings** | Word2Vec / GloVe + ML | High | Medium | Semantic understanding |
| **Transformers** | BERT / RoBERTa fine-tuned | Very High | Slow | Complex / nuanced text |
| **LLM Zero-Shot** | GPT-4 / Claude prompting | High | Slow | Rapid prototyping |

**Practical Advice:** Start with TF-IDF + RandomForest. Upgrade to transformers only when accuracy demands it.

---

### Automated Metadata Extraction

| Type | Examples |
|------|---------|
| **Technical Metadata** | Schema, data types, row counts, file sizes, source system |
| **Business Metadata** | Business domain, owner, key terms, classification labels, quality score |
| **Operational Metadata** | Lineage, access patterns, pipeline dependencies, freshness, compliance flags |

**AI Techniques:** NER for entity extraction, regex for structural patterns, LLMs for description generation, embeddings for similarity tagging.

---

### Vector Databases for Data Discovery

Vector databases store high-dimensional embeddings, enabling semantic search — finding data by *meaning*, not just keywords.

```python
from sentence_transformers import SentenceTransformer
import chromadb

# Create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(descriptions)

# Store in ChromaDB
client = chromadb.Client()
collection = client.create_collection("data_catalogue")
collection.add(
    embeddings=embeddings.tolist(),
    documents=descriptions,
    ids=[f"asset_{i}" for i in range(len(descriptions))]
)

# Semantic search
results = collection.query(
    query_texts=["customer financial transactions"],
    n_results=5
)
```

**Why Vectors?** A search for "customer financial transactions" finds "payment processing records" even though no keywords match.

---

### Vector Database Options

| Database | Type | Scale | Best For |
|----------|------|-------|----------|
| **ChromaDB** | Embedded / local | Small-Medium | Prototyping, dev |
| **Pinecone** | Managed cloud | Large | Production SaaS |
| **Weaviate** | Open-source / cloud | Large | Hybrid search, multi-modal |
| **pgvector** | PostgreSQL extension | Medium | Existing Postgres stacks |
| **Milvus** | Open-source / cloud | Very Large | Billion-scale vector search |

**Tip:** Start with ChromaDB for prototyping. Migrate to Pinecone or Weaviate for production.

---

### Unsupervised Discovery with Clustering

```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Cluster TF-IDF vectors
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(X_tfidf)

# Reduce to 2D for visualisation
pca = PCA(n_components=2)
coords = pca.fit_transform(X_tfidf.toarray())

# Plot clusters
plt.scatter(coords[:, 0], coords[:, 1], c=clusters, cmap='viridis')
plt.title("Data Asset Clusters")
plt.show()
```

**Workflow:** Cluster first, then review clusters to assign labels, then train a supervised classifier.

---

## Day 2: Compliance, Governance & Ethics

### Detecting Sensitive Data with AI

**PII Categories:**
- **Personal (PII):** Names, SSNs, emails, phone numbers, date of birth
- **Financial:** Credit card numbers, bank accounts, transaction records, income data
- **Health (PHI):** Medical record numbers, diagnoses, prescriptions, insurance IDs

**Risk:** A single undetected PII field can trigger GDPR fines of up to EUR 20M or 4% of global turnover.

---

### Hybrid Detection: Regex + ML

```python
import re

patterns = {
    'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    'credit_card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
    'email': re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.]+\b'),
    'phone': re.compile(r'\b\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'),
}

def scan_text(text):
    findings = {}
    for name, pat in patterns.items():
        matches = pat.findall(text)
        if matches:
            findings[name] = matches
    return findings
```

**Hybrid Strategy:**
1. **Layer 1:** Regex for known formats (SSN, CC, email)
2. **Layer 2:** NER for names, organisations, locations
3. **Layer 3:** ML classifier for contextual sensitivity
4. **Layer 4:** LLM review for ambiguous cases

---

### NER for PII Detection

```python
import spacy

nlp = spacy.load("en_core_web_sm")

text = """John Smith from Acme Corp submitted a claim
on 15 March 2024. Contact: john.smith@acme.com,
SSN: 123-45-6789. Based in New York."""

doc = nlp(text)

for ent in doc.ents:
    print(f"{ent.text:20} {ent.label_:10}")

# Output:
# John Smith           PERSON
# Acme Corp            ORG
# 15 March 2024        DATE
# New York             GPE
```

**Hybrid Approach:** Combine spaCy NER (for PERSON, ORG, GPE) with regex (for SSN, email) for comprehensive PII detection.

---

### Compliance Risk Assessment

| Regulation | Scope | Key Data Types | Max Penalty |
|-----------|-------|---------------|-------------|
| **GDPR** | EU personal data | PII, consent, profiling | EUR 20M / 4% revenue |
| **HIPAA** | US healthcare | PHI, medical records | $1.5M per violation |
| **PCI-DSS** | Payment cards | Card numbers, CVV, PINs | $100K/month |
| **CCPA** | California consumers | PII, purchase history | $7,500 per violation |
| **SOX** | US public companies | Financial records, audit trails | $5M + imprisonment |

---

### Automated Risk Scoring

**Formula:**
```
Risk = Sensitivity x Exposure x Regulatory Weight
```

**Risk Tiers:**
| Tier | Score | Action |
|------|-------|--------|
| **Critical** | 76-100 | Immediate remediation |
| **High** | 51-75 | Remediation within 30 days |
| **Medium** | 26-50 | Monitor and plan |
| **Low** | 0-25 | Acceptable risk |

---

### Data Governance Integration

**Three Pillars:**
- **Policy:** Classification policies, retention rules, access control standards, encryption requirements
- **Process:** Discovery workflows, risk assessment, incident response, continuous monitoring
- **People:** Data stewards, privacy officers (DPO), compliance teams, training

**Key Principle:** Discovery without governance is just inventory. Governance without discovery is guesswork.

---

### Continuous Data Monitoring

**Pipeline:**
```
Classify → Check Policy → Alert → Remediate
```

**What to Monitor:**
- New data sources appearing
- Classification drift (data changing category)
- Sensitivity escalation (new PII fields)
- Access pattern anomalies
- Policy violations

**Tools:** Great Expectations, Monte Carlo, Soda, custom ML anomaly detection, SIEM integration.

---

### Data Lineage & Provenance

**Pipeline:**
```
Source → Transform → Aggregate → Destination
```

**Why Lineage Matters:**
- GDPR Art. 30: Must document processing activities
- Impact Analysis: Understand downstream effects of changes
- Root Cause: Trace data quality issues to their source
- Audit Trail: Prove compliance to regulators

**Tools:** OpenLineage, Apache Atlas, DataHub, dbt

---

### Ethics, Privacy & Bias

| Concern | Key Issues | Mitigation |
|---------|-----------|------------|
| **Privacy** | Discovery systems access sensitive data | Least-privilege access, encryption, data minimisation |
| **Bias** | ML classifiers can inherit training bias | Regular audits, diverse validation datasets |
| **Transparency** | Explainable classification decisions | Human-in-the-loop, document limitations |

---

### Operational Challenges

| Challenge | Mitigation |
|-----------|-----------|
| **Scale** | Incremental scanning, prioritise high-risk sources |
| **Accuracy** | Hybrid detection, human review for edge cases |
| **Integration** | Connector frameworks, open standards |
| **Change Management** | Executive sponsorship, demonstrate quick wins |
| **Cost** | Start small, lightweight models, scale on ROI |

**Success Formula:** Start with one high-value use case (e.g., GDPR PII detection), prove value, then expand scope incrementally.

---

*Data Discovery: Harnessing AI, AGI & Vector Databases | AI Elevate*
