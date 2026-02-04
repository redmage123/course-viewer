# Introduction to Data Science & Engineering
## Student Notes

**Course Duration:** 3 Days
**Target Audience:** IT Professionals, Developers transitioning into data roles, Analysts

---

## Day 1: Data Science Foundations & Python for Data

### The Data Landscape

**Key Statistics:**
- $274B Global Data Market in 2025
- 2.5 quintillion bytes of data created daily
- Data Scientist ranked #1 in-demand role
- 36% projected growth in Data Engineering jobs by 2033

---

### Data Science vs Data Engineering

| Aspect | Data Science | Data Engineering |
|--------|-------------|-----------------|
| **Focus** | Insights & predictions | Data infrastructure |
| **Skills** | Statistics, ML, visualization | ETL, SQL, distributed systems |
| **Tools** | Python, R, Jupyter | Spark, Airflow, dbt |
| **Output** | Models, reports, dashboards | Pipelines, warehouses, lakes |

**Key Insight:** Modern data teams need both disciplines. Engineers build the roads, Scientists drive the cars.

---

### The Data Lifecycle

```
Collection → Storage → Processing → Analysis → Modeling → Deployment → Monitoring
```

- **DS Focus:** Analysis, Modeling, Visualization
- **DE Focus:** Collection, Storage, Processing, Deployment

---

### Python Data Science Toolkit

| Library | Purpose | Key Features |
|---------|---------|-------------|
| **NumPy** | Numerical computing | N-dimensional arrays, linear algebra, broadcasting |
| **Pandas** | Data manipulation | DataFrames, time series, I/O tools |
| **Matplotlib** | Visualization | Line/bar/scatter plots, subplots, customization |
| **Seaborn** | Statistical visualization | Heatmaps, distribution plots, beautiful defaults |

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data.csv')
df.describe()
```

---

### Exploratory Data Analysis (EDA)

**EDA Checklist:**
1. Shape and size (rows, columns)
2. Data types and memory usage
3. Missing value patterns
4. Statistical summaries
5. Distribution of features
6. Correlations between variables
7. Outlier detection

```python
# Shape and basic info
print(df.shape)
print(df.dtypes)

# Statistical summary
df.describe()

# Missing values
df.isnull().sum()

# Correlations
df.corr()
```

**Tip:** Always visualize before modeling. A picture is worth a thousand p-values!

---

### Data Cleaning & Preparation

**Common Issues:**
- **Missing Values:** Imputation (mean, median, mode), deletion, prediction
- **Outliers:** Detection via IQR method, Z-score; handling via capping or removal
- **Duplicates:** Identification and removal with `drop_duplicates()`
- **Inconsistencies:** Standardization of formats, types, and naming

```python
# Handle missing values
df['age'].fillna(df['age'].median(), inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Fix data types
df['date'] = pd.to_datetime(df['date'])

# Handle outliers (IQR method)
Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['price'] >= Q1 - 1.5*IQR) & (df['price'] <= Q3 + 1.5*IQR)]
```

---

### Data Visualization Guide

| Chart Type | Best For | Library Call |
|-----------|---------|-------------|
| Bar Chart | Categorical comparisons | `plt.bar()` |
| Line Chart | Trends over time | `plt.plot()` |
| Scatter Plot | Relationships | `plt.scatter()` |
| Histogram | Distributions | `plt.hist()` |
| Heatmap | Correlations | `sns.heatmap()` |
| Box Plot | Outliers & spread | `sns.boxplot()` |

**Warning:** Don't use pie charts for more than 5 categories. Use bar charts for clearer comparisons.

---

### Statistical Foundations

**Central Tendency:**
- Mean — sensitive to outliers
- Median — robust, preferred for skewed data
- Mode — most frequent value

**Spread & Variability:**
- Variance / Standard Deviation
- IQR — robust to outliers, ideal for real-world data
- Range

**Relationships:**
- Correlation — linear relationship strength (-1 to +1)
- Covariance — directional relationship
- Correlation does NOT imply causation

**Key Distributions:** Normal (bell curve), Binomial (yes/no outcomes), Poisson (event counts), Uniform (equal probability)

---

### Real-World Data Formats

| Format | Strengths | Read With |
|--------|----------|-----------|
| **CSV** | Human-readable, universal support | `pd.read_csv()` |
| **JSON** | Nested structures, API standard | `pd.read_json()` |
| **SQL** | Relational data, ACID compliance | `pd.read_sql()` |
| **Parquet** | Columnar, compressed, fast analytics | `pd.read_parquet()` |

**Pro Tip:** Use Parquet for large analytical workloads — up to 10x faster than CSV with 75% less storage.

---

## Day 2: Data Engineering Fundamentals

### What is Data Engineering?

Data engineering is the practice of designing and building systems that collect, store, and transform data for analytical or operational use.

**Core Responsibilities:**
- Design data architectures
- Build ETL/ELT pipelines
- Ensure data quality & governance
- Optimize for performance & cost
- Enable self-service analytics

**Modern Data Architecture:**
```
Sources (APIs, DBs, Files, Streams)
    → Ingestion (Batch, Real-time, CDC)
        → Storage (Lake, Warehouse, Lakehouse)
            → Transform (dbt, Spark, SQL)
                → Serve (BI, ML, APIs)
```

---

### ETL vs ELT

| Aspect | ETL | ELT |
|--------|-----|-----|
| **Transform Location** | Staging area | Target warehouse |
| **Speed** | Slower (pre-transform) | Faster (parallel compute) |
| **Flexibility** | Schema-on-write | Schema-on-read |
| **Cost** | Higher compute upfront | Pay-per-query |
| **Best For** | Compliance, small-medium data | Analytics, large-scale data |

- **ETL Tools:** Informatica, Talend, SSIS
- **ELT Tools:** dbt, Snowflake, BigQuery

---

### SQL for Data Engineers

**Essential Concepts:**
- Window functions (ROW_NUMBER, RANK, LAG, LEAD)
- Common Table Expressions (CTEs)
- Subqueries and derived tables
- JOIN types (INNER, LEFT, FULL, CROSS)
- Aggregation and GROUP BY
- Indexing strategies

```sql
-- Window function: Running total
SELECT
    order_date,
    amount,
    SUM(amount) OVER (
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) AS running_total
FROM orders;

-- CTE: Monthly aggregation
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS total
    FROM orders
    GROUP BY 1
)
SELECT month, total,
    LAG(total) OVER (ORDER BY month) AS prev_month
FROM monthly;
```

---

### Data Storage Solutions

| Solution | Type | Best For | Examples | Scale |
|----------|------|---------|----------|-------|
| **RDBMS** | Row-based | Transactions, OLTP | PostgreSQL, MySQL | GBs-TBs |
| **Document Store** | NoSQL | Flexible schemas | MongoDB, DynamoDB | GBs-TBs |
| **Data Warehouse** | Columnar | Analytics, BI | Snowflake, BigQuery, Redshift | TBs-PBs |
| **Data Lake** | Object storage | Raw data, ML | S3, ADLS, GCS | PBs+ |
| **Data Lakehouse** | Hybrid | Unified analytics + ML | Databricks, Delta Lake | PBs+ |

---

### Star Schema (Dimensional Modeling)

**Principles:**
- Fact tables store measurements/metrics (e.g., order amounts, quantities)
- Dimension tables store descriptive attributes (e.g., customer name, product category)
- Simple joins for fast queries
- Denormalized for read performance
- Industry standard for analytics

```
                dim_customer
                     |
dim_product --- fact_orders --- dim_time
                     |
                dim_store
```

---

### Building Data Pipelines

**Pipeline Steps:**
```
Extract → Validate → Transform → Load → Monitor
```

**Key Tools:**
| Category | Tools |
|----------|-------|
| **Orchestration** | Apache Airflow, Prefect, Dagster |
| **Transformation** | dbt, Apache Spark, pandas |
| **Quality** | Great Expectations, dbt tests, Soda |

---

### Data Quality Dimensions

| Dimension | Description | Example Check |
|-----------|-------------|--------------|
| **Completeness** | No missing critical fields | Null rate monitoring |
| **Accuracy** | Values reflect reality | Range validation |
| **Consistency** | Same format everywhere | Referential integrity |
| **Timeliness** | Data arrives on schedule | Freshness monitoring |

```python
# Data quality assertions
assert df['email'].notna().all(), "Missing emails!"
assert df['age'].between(0, 150).all(), "Invalid ages!"
assert df['id'].is_unique, "Duplicate IDs found!"
```

---

### Cloud Data Platforms

| Provider | Storage | Warehouse | ETL | Streaming |
|----------|---------|-----------|-----|-----------|
| **AWS** | S3 | Redshift | Glue | Kinesis |
| **Azure** | ADLS | Synapse | Data Factory | Event Hubs |
| **GCP** | Cloud Storage | BigQuery | Dataflow | Pub/Sub |

**Trend:** Most organizations adopt multi-cloud strategies. Focus on transferable concepts, not just one vendor.

---

### Batch vs Stream Processing

| Aspect | Batch | Stream |
|--------|-------|--------|
| **Timing** | Scheduled intervals | Real-time |
| **Throughput** | Higher | Lower |
| **Latency** | Higher | Lower |
| **Cost** | Lower | Higher |
| **Examples** | Daily reports, ETL jobs | Fraud detection, live dashboards |
| **Tools** | Spark, Hive, dbt | Kafka, Flink, Spark Streaming |

**Hybrid Approach:** Use batch for historical analysis and stream for real-time decisions. Lambda/Kappa architectures combine both.

---

## Day 3: Machine Learning & Integration

### ML Fundamentals

| Type | Description | Examples |
|------|-------------|----------|
| **Supervised** | Learn from labeled data | Classification, Regression, Ranking |
| **Unsupervised** | Find hidden patterns | Clustering, Dimensionality Reduction, Anomaly Detection |
| **Reinforcement** | Learn by interaction | Game AI, Robotics, Recommendations |

**Most business ML is supervised learning. Start here and expand as needed.**

---

### The ML Workflow

```
Problem Definition → Data Collection → Feature Engineering → Model Training → Evaluation → Deployment → Monitoring
```

**Time Allocation Reality:**
- 25% Data Collection
- 25% Data Cleaning
- 20% Feature Engineering
- 15% Model Training
- 10% Evaluation
- 5% Deployment

**Reality Check:** Data scientists spend ~80% of their time on data preparation, not model building!

---

### Scikit-Learn Toolkit

| Algorithm | Type | Best For |
|-----------|------|---------|
| LogisticRegression | Classification | Binary outcomes, baseline |
| RandomForest | Both | Tabular data, feature importance |
| GradientBoosting | Both | High accuracy, competitions |
| KMeans | Clustering | Customer segmentation |
| PCA | Reduction | Dimensionality reduction |
| LinearRegression | Regression | Price prediction, trends |

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, predictions)}")
```

---

### Model Evaluation

**Classification Metrics:**
- **Accuracy** = Correct predictions / Total predictions
- **Precision** = TP / (TP + FP) — "Of predicted positives, how many are correct?"
- **Recall** = TP / (TP + FN) — "Of actual positives, how many did we find?"
- **F1 Score** = 2 x (Precision x Recall) / (Precision + Recall)
- **AUC-ROC** — Area under the ROC curve

**Regression Metrics:**
- **MAE** — Mean Absolute Error (robust to outliers)
- **RMSE** — Root Mean Squared Error (penalizes large errors)
- **R-squared** — Proportion of variance explained

**Choosing Metrics:**
- Use **recall** for fraud/disease detection (minimize false negatives)
- Use **precision** for spam filtering (minimize false positives)
- Use **F1** for balanced needs

---

### Feature Engineering

| Category | Techniques | Example |
|----------|-----------|---------|
| **Temporal** | Extract date parts, lag features | day_of_week, days_since_last_order |
| **Aggregation** | Group stats, rolling windows | avg_order_value, 30d_purchase_count |
| **Encoding** | One-hot, target, frequency | category converted to numeric |
| **Interaction** | Cross features, ratios | price_per_unit, tenure_to_age_ratio |
| **Text** | TF-IDF, length, word count | review_length, sentiment_score |

```python
# Temporal features
df['day_of_week'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month

# Aggregation features
df['avg_order_value'] = df.groupby('customer_id')['amount'].transform('mean')

# Interaction features
df['price_per_unit'] = df['total'] / df['quantity']
```

---

### MLOps

**ML Lifecycle:**
```
Develop → Train → Deploy → Monitor → Retrain
```

**Key Tools:**
| Category | Tools |
|----------|-------|
| **Experiment Tracking** | MLflow, Weights & Biases |
| **Model Registry** | MLflow, SageMaker Model Registry |
| **CI/CD for ML** | GitHub Actions, Jenkins, MLflow Pipelines |

```python
import mlflow

mlflow.set_experiment("churn_prediction")
with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", 0.87)
    mlflow.sklearn.log_model(model, "model")
```

---

### Career Paths

| Role | Key Skills | Avg Salary | Path |
|------|-----------|-----------|------|
| **Data Analyst** | SQL, Excel, BI tools, Visualization | $75K-$95K | Reports → Dashboards → Strategic analytics |
| **Data Scientist** | Python, Statistics, ML, Deep Learning | $110K-$150K | EDA → Modeling → Research → ML Engineering |
| **Data Engineer** | SQL, Python, Cloud, Spark, Airflow | $120K-$160K | ETL development → Pipeline architecture → Platform engineering |

**All three roles are in high demand. Your background determines your fastest path — leverage your existing strengths.**

---

*Introduction to Data Science & Engineering | AI Elevate*
