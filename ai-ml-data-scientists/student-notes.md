# AI/ML for Data Scientists: Modern Approaches and Deployment
## Student Notes

**Course Duration:** 3 Days
**Target Audience:** Data Scientists, Business Analysts, ML Engineers

---

## Day 1: Foundations & Data Preparation

### The Modern ML Landscape

**Key Statistics:**
- $200B+ Global AI Market in 2025
- 77% of companies using AI
- 10M+ Data Scientists worldwide
- 87% of ML projects never reach production (the deployment gap)

---

### Types of Machine Learning

| Type | Description | Examples |
|------|-------------|----------|
| **Supervised** | Learn from labeled data | Classification, Regression, Ranking |
| **Unsupervised** | Find patterns in unlabeled data | Clustering, Dimensionality Reduction, Anomaly Detection |
| **Reinforcement** | Learn through trial and error | Game AI, Robotics, Recommendations |

---

### The ML Pipeline

```
Data Collection → Data Cleaning → Feature Engineering → Model Training → Evaluation → Deployment → Monitoring
```

**Time Allocation Reality:**
- 80% of time: Data collection, cleaning, feature engineering
- 20% of time: Model training, evaluation, deployment

---

### Data Preprocessing

**Data Cleaning:**
- Missing values: Imputation, deletion, prediction
- Outliers: Detection and handling (IQR, Z-score)
- Duplicates: Identification and removal
- Inconsistencies: Standardization

**Data Transformation:**
- Scaling: MinMax, Standard, Robust
- Encoding: One-hot, Label, Target
- Binning: Equal-width, Equal-frequency
- Log/Power transforms: For skewed distributions

```python
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Handle missing values
imputer = SimpleImputer(strategy='median')
df['age'] = imputer.fit_transform(df[['age']])

# Scale numeric features
scaler = StandardScaler()
df['age_scaled'] = scaler.fit_transform(df[['age']])
```

---

### Feature Engineering

| Category | Techniques |
|----------|------------|
| **Temporal** | Day of week, month, hour, time since event, rolling statistics |
| **Text** | TF-IDF, word embeddings, n-grams, sentiment, named entities |
| **Numeric** | Ratios, differences, aggregations, polynomial features, binning |
| **Categorical** | Target encoding, frequency encoding, embeddings, combinations |

**Pro Tip:** The best features often come from domain knowledge. Collaborate with domain experts.

---

### Model Selection Guide

| Algorithm | Best For | Pros | Cons |
|-----------|----------|------|------|
| Linear/Logistic Regression | Baseline, interpretability | Fast, interpretable | Limited to linear |
| Random Forest | Tabular data, feature importance | Robust, handles non-linear | Memory intensive |
| XGBoost/LightGBM | Competitions, tabular data | State-of-the-art accuracy | Prone to overfitting |
| Neural Networks | Images, text, complex patterns | Learns representations | Data hungry |
| SVMs | Small datasets, high dimensions | Effective in high dims | Doesn't scale |

**Decision Framework:** Start simple → Add complexity as needed → Validate rigorously

---

### Evaluation Metrics

**Classification:**
- **Precision** = TP / (TP + FP) — "Of predicted positives, how many are correct?"
- **Recall** = TP / (TP + FN) — "Of actual positives, how many did we find?"
- **F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)
- **AUC-ROC** — Area under the ROC curve

**Regression:**
- **MAE** — Mean Absolute Error (robust to outliers)
- **MSE/RMSE** — Mean Squared Error (penalizes large errors)
- **R²** — Proportion of variance explained
- **MAPE** — Mean Absolute Percentage Error (scale-independent)

---

### Cross-Validation Strategies

| Strategy | When to Use | Code |
|----------|-------------|------|
| K-Fold CV | General purpose | `cross_val_score(model, X, y, cv=5)` |
| Stratified K-Fold | Imbalanced classes | `StratifiedKFold(n_splits=5)` |
| Time Series Split | Temporal data | `TimeSeriesSplit(n_splits=5)` |

**Warning:** Never use test data for preprocessing decisions. Fit scalers/imputers only on training data!

---

## Day 2: Deep Learning & Modern Architectures

### Neural Networks Fundamentals

**The Artificial Neuron:**
```
y = f(Σ(wᵢxᵢ) + b)
```

- **Inputs (x):** Features from data
- **Weights (w):** Learned parameters
- **Bias (b):** Offset term
- **Activation (f):** Non-linearity
- **Output (y):** Prediction

**Common Activation Functions:**
- **ReLU:** max(0, x) — Most common, fast
- **Sigmoid:** 1/(1+e⁻ˣ) — Output 0-1, binary classification
- **Softmax:** Multi-class probabilities
- **Tanh:** Output -1 to 1, zero-centered

---

### Deep Learning Architectures

| Architecture | Use Cases | Key Concept |
|--------------|-----------|-------------|
| **CNNs** | Image classification, object detection, medical imaging | Convolution, pooling, feature maps |
| **RNNs/LSTMs** | Sequence modeling, time series, speech | Memory cells, hidden states |
| **Transformers** | NLP (BERT, GPT), Vision (ViT), Multimodal | Self-attention, parallelization |

---

### Transformers & Self-Attention

**Self-Attention Mechanism:**
```
Attention(Q,K,V) = softmax(QKᵀ/√dₖ)V
```

- **Query (Q):** What am I looking for?
- **Key (K):** What do I contain?
- **Value (V):** What information do I provide?

**Popular Transformer Models:**
- **BERT:** Bidirectional encoder — classification, NER, Q&A
- **GPT Family:** Autoregressive decoder — text generation, chat
- **T5/BART:** Encoder-decoder — summarization, translation
- **ViT:** Vision Transformer — image classification

**Why Transformers Win:**
- Parallel processing (vs sequential RNNs)
- Long-range dependencies
- Transfer learning ready

---

### Transfer Learning

**Steps:**
1. Load pre-trained model (ImageNet, Wikipedia)
2. Freeze base layers
3. Add custom head for your task
4. Fine-tune on your data

```python
from transformers import AutoModelForSequenceClassification

# Load pre-trained model
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)

# Freeze base layers
for param in model.bert.parameters():
    param.requires_grad = False
```

**Benefits:**
- Less data required
- Faster training
- Better generalization

---

### AutoML & Automated Feature Engineering

**What AutoML Automates:**
- Feature engineering
- Model selection
- Hyperparameter tuning
- Architecture search (NAS)

**Popular Tools:**
- Auto-sklearn, H2O AutoML, Google AutoML, Azure AutoML, TPOT, Optuna

**Note:** AutoML accelerates experimentation but requires human oversight for data quality, business logic, and deployment.

---

### Multimodal AI

Models that understand multiple modalities: Text, Images, Audio, Video

**Key Models:**
- **CLIP:** Text-image understanding, zero-shot classification
- **GPT-4V / Gemini:** Vision + language
- **Stable Diffusion / DALL-E:** Text-to-image generation

---

## Day 3: MLOps & Responsible AI

### MLOps: Machine Learning Operations

**The Problem:** 87% of ML projects never reach production

**MLOps Capabilities:**
- Experiment tracking (log parameters, metrics, artifacts)
- Model registry (version and manage models)
- Model serving (deploy as APIs)
- Monitoring (track performance, data drift)
- Automation (CI/CD for ML)

---

### Experiment Tracking with MLflow

```python
import mlflow

mlflow.set_experiment("customer_churn")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("max_depth", 5)

    model = train_model(X_train, y_train)

    mlflow.log_metric("accuracy", 0.92)
    mlflow.log_metric("f1_score", 0.89)

    mlflow.sklearn.log_model(model, "model")
```

**MLflow Components:**
- Tracking: Log experiments
- Projects: Package ML code
- Model Registry: Version models
- Model Serving: Deploy as REST APIs

---

### Model Deployment Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| **REST API** | Synchronous HTTP endpoints (Flask, FastAPI) | Low latency, interactive apps |
| **Batch Processing** | Process datasets offline (Spark, Airflow) | Reports, bulk scoring |
| **Edge Deployment** | Run on devices (ONNX, TF Lite) | Privacy, offline, low latency |

```python
# FastAPI deployment
from fastapi import FastAPI
import joblib

app = FastAPI()
model = joblib.load("model.pkl")

@app.post("/predict")
async def predict(features: List[float]):
    prediction = model.predict([features])
    return {"prediction": prediction.tolist()}
```

---

### Model Monitoring

**What to Monitor:**
- **Data Drift:** Input distribution changes
- **Concept Drift:** Input-output relationship changes
- **Performance Metrics:** Accuracy, latency, throughput
- **Operational Metrics:** CPU/memory, request volume

**When to Retrain:**
- Performance drops below threshold
- Significant data drift detected
- New labeled data available
- Scheduled retraining
- Business requirements change

**Tools:** Evidently AI, Whylogs, Prometheus + Grafana

---

### Pillars of Responsible AI

| Pillar | Key Practices |
|--------|---------------|
| **Fairness** | Bias detection, equal treatment, demographic parity |
| **Transparency** | Explainable predictions, documentation, traceability |
| **Privacy & Security** | Data protection, differential privacy, access controls |
| **Accountability** | Human oversight, audit trails, governance |

---

### Bias Detection & Mitigation

**Sources of Bias:**
- **Data Bias:** Training data doesn't represent reality
- **Algorithm Bias:** Model amplifies existing patterns
- **Selection Bias:** Feedback loops, self-fulfilling predictions

**Mitigation Strategies:**
- **Pre-processing:** Reweight data, remove sensitive features
- **In-processing:** Fairness constraints, adversarial debiasing
- **Post-processing:** Adjust thresholds, calibration

**Tools:** AI Fairness 360, Fairlearn, What-If Tool

---

### Model Explainability

| Method | Description | Use Case |
|--------|-------------|----------|
| **SHAP** | Shapley values, feature contributions | Any model |
| **LIME** | Local approximations | Instance explanations |
| **Feature Importance** | Permutation importance | Tree models |

```python
import shap
explainer = shap.Explainer(model)
shap_values = explainer(X)
shap.plots.waterfall(shap_values[0])
```

**Global vs Local Explanations:**
- **Global:** Overall model behavior, feature rankings
- **Local:** Why this specific prediction was made

---

### Case Studies

**Success: Fraud Detection**
- Challenge: $10M+ annual fraud losses
- Solution: Ensemble model with real-time scoring
- Result: 60% reduction in fraud, <1% false positives
- Key: Feature engineering, continuous retraining

**Failure: Hiring Algorithm**
- Issue: Model trained on historical hiring data
- Problem: Perpetuated gender bias
- Lesson: Audit for bias before deployment
- Fix: Fairness constraints, diverse training data

---

## Key Takeaways

### Day 1: Foundations
- 80% of time is data preparation
- Feature engineering is an art
- Start simple, add complexity
- Cross-validation is essential
- Avoid data leakage

### Day 2: Modern Techniques
- Deep learning for unstructured data
- Transformers revolutionized NLP
- Transfer learning saves time/data
- AutoML accelerates experimentation
- Multimodal is the future

### Day 3: Production
- MLOps bridges the deployment gap
- Monitor for drift continuously
- Responsible AI is non-negotiable
- Explainability builds trust
- Learn from failures

---

## Essential Tools

| Category | Tools |
|----------|-------|
| **Data** | NumPy, Pandas, Matplotlib, Seaborn |
| **ML** | Scikit-learn, XGBoost, LightGBM |
| **Deep Learning** | PyTorch, TensorFlow, Hugging Face |
| **MLOps** | MLflow, Docker, Kubernetes |
| **Cloud** | AWS SageMaker, Azure ML, GCP Vertex AI |

---

## Your Next Steps

1. Pick a real problem
2. Start with good data practices
3. Experiment rapidly
4. Deploy responsibly
5. Monitor and iterate

---

## Notes Space

### Day 1 Notes:
_________________________________
_________________________________
_________________________________

### Day 2 Notes:
_________________________________
_________________________________
_________________________________

### Day 3 Notes:
_________________________________
_________________________________
_________________________________

---

*AI/ML for Data Scientists: Modern Approaches and Deployment | AI Elevate*
