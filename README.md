# 📉 Customer Churn Analysis

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange?style=flat-square&logo=scikit-learn)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey?style=flat-square&logo=sqlite)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)

> **An end-to-end Data Analytics project** — from raw data exploration to a live, interactive machine learning dashboard.

---

## 🔗 Live Dashboard

[👉 **[View Live Demo →](https://your-app-name.streamlit.app)** *(replace with your Streamlit Cloud URL)*](https://customer-churn-analysis-adduezyczwgquyixfcxnzw.streamlit.app/)

---

## 📌 Problem Statement

Customer churn is one of the most expensive problems in business. Acquiring a new customer costs **5–25x more** than retaining an existing one. This project analyzes a telecom company's customer data to:

1. **Identify** which customers are most likely to churn
2. **Understand** the key drivers of churn
3. **Quantify** the revenue at risk
4. **Predict** churn probability for individual customers using ML

---

## 🎯 Key Findings

| # | Finding | Business Impact |
|---|---------|----------------|
| 1 | **Month-to-month** customers churn at **~42%** vs 11% for annual contracts | Push customers to long-term contracts |
| 2 | **Fiber optic** internet users have the highest churn rate (~42%) | Improve fiber service quality |
| 3 | **Electronic check** payers churn more (~45%) | Incentivize auto-pay enrollment |
| 4 | **New customers** (< 6 months) are the highest-risk segment (~50% churn) | Invest in early onboarding programs |
| 5 | Monthly revenue at risk from churners: **~$139,000/month** | Targeted retention can save millions |

---

## 🤖 Model Performance

| Model | ROC-AUC | Precision | Recall | F1 |
|-------|---------|-----------|--------|----|
| Logistic Regression | 0.84 | 0.67 | 0.79 | 0.72 |
| **Random Forest** | **0.87** | **0.72** | **0.81** | **0.76** |

**Top 5 Churn Predictors** (from Random Forest feature importance):
1. `tenure` — How long the customer has been with the company
2. `MonthlyCharges` — Higher charges → higher churn risk
3. `TotalCharges` — Correlated with tenure
4. `Contract_Two year` — Long contracts drastically reduce churn
5. `InternetService_Fiber optic` — Fiber users churn disproportionately

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Language** | Python 3.11 |
| **Data Analysis** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn, Plotly |
| **Machine Learning** | Scikit-learn (Random Forest, Logistic Regression) |
| **Dashboard** | Streamlit |
| **Database** | SQLite (10 business SQL queries) |
| **Version Control** | Git + GitHub |

---

## 🗂️ Project Structure

```
Customer_Churn_Analysis/
├── data/
│   ├── generate_data.py        # Synthetic data generator
│   ├── raw/
│   │   └── telco_churn.csv     # Raw dataset
│   └── processed/
│       └── churn_cleaned.csv   # Cleaned & feature-engineered data
│
├── notebooks/
│   ├── 01_eda.py               # Exploratory Data Analysis (7 charts)
│   └── 02_modeling.py          # ML Training + Evaluation (4 charts)
│
├── sql/
│   ├── business_queries.sql    # 10 SQL business questions
│   └── run_queries.py          # SQLite runner
│
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
│
├── models/
│   ├── churn_model.pkl         # Best trained model
│   ├── random_forest.pkl       # Random Forest model
│   └── feature_names.csv       # Feature names for prediction
│
├── reports/
│   └── *.png                   # All generated charts
│
├── run_project.py              # ⚡ One-click setup & launch
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run Locally

### Option 1 — One Command (Recommended)
```bash
python run_project.py
```
This installs dependencies, generates data, trains the model, and launches the dashboard.

### Option 2 — Step by Step
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate dataset
python data/generate_data.py

# 3. Run EDA
python notebooks/01_eda.py

# 4. Train ML model
python notebooks/02_modeling.py

# 5. Run SQL queries
python sql/run_queries.py

# 6. Launch dashboard
streamlit run dashboard/app.py
```

---

## 📊 Dashboard Features

The interactive dashboard has **4 sections**:

| Page | Description |
|------|-------------|
| 🏠 **Overview** | KPI cards, churn pie chart, contract-type comparison, key insights |
| 📊 **EDA** | 6 interactive charts — tenure, charges, internet service, payment method, cohort analysis |
| 🤖 **Model** | ROC curve, confusion matrix, feature importance visualization |
| 🔮 **Predict** | Real-time churn prediction for a custom customer profile with risk gauge |

---

## 📧 About

**Built by**: [Your Name]  
**LinkedIn**: [your-linkedin-url]  
**GitHub**: [your-github-url]

---

*This project demonstrates end-to-end data analytics skills: data wrangling, EDA, SQL, machine learning, and dashboard deployment.*
