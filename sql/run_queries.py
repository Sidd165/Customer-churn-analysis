"""
run_queries.py
--------------
Loads the cleaned churn data into a SQLite database and runs all business SQL queries.
Prints results as formatted tables.
"""

import pandas as pd
import sqlite3
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV  = os.path.join(BASE, "data", "processed", "churn_cleaned.csv")
DB   = os.path.join(BASE, "sql", "churn.db")

# Load data into SQLite
df   = pd.read_csv(CSV)
conn = sqlite3.connect(DB)
df.to_sql("customers", conn, if_exists="replace", index=False)
print(f"[OK] Loaded {len(df):,} rows into {DB}\n")

queries = {
    "Q1 — Overall Churn Rate": """
        SELECT COUNT(*) AS total_customers,
               SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS total_churned,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct
        FROM customers
    """,
    "Q2 — Churn by Contract Type": """
        SELECT Contract,
               COUNT(*) AS total,
               SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS churned,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct
        FROM customers GROUP BY Contract ORDER BY churn_rate_pct DESC
    """,
    "Q3 — Avg Charges: Churned vs Retained": """
        SELECT Churn AS status,
               ROUND(AVG(MonthlyCharges),2) AS avg_monthly_charges,
               ROUND(AVG(tenure),1)         AS avg_tenure_months,
               COUNT(*)                     AS count
        FROM customers GROUP BY Churn
    """,
    "Q4 — Monthly Revenue at Risk": """
        SELECT ROUND(SUM(MonthlyCharges),2) AS monthly_revenue_at_risk,
               COUNT(*)                     AS churned_customers
        FROM customers WHERE Churn='Yes'
    """,
    "Q5 — Churn by Internet Service": """
        SELECT InternetService, COUNT(*) AS total,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct
        FROM customers GROUP BY InternetService ORDER BY churn_rate_pct DESC
    """,
    "Q6 — Churn by Payment Method": """
        SELECT PaymentMethod, COUNT(*) AS total,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct
        FROM customers GROUP BY PaymentMethod ORDER BY churn_rate_pct DESC
    """,
    "Q7 — High-Risk Segment": """
        SELECT COUNT(*) AS high_risk_customers,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct,
               ROUND(AVG(MonthlyCharges),2) AS avg_monthly_charges
        FROM customers
        WHERE Contract='Month-to-month' AND InternetService='Fiber optic'
          AND PaymentMethod='Electronic check' AND tenure<12
    """,
    "Q8 — Senior vs Non-Senior Churn": """
        SELECT CASE WHEN SeniorCitizen=1 THEN 'Senior' ELSE 'Non-Senior' END AS segment,
               COUNT(*) AS total,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct
        FROM customers GROUP BY SeniorCitizen
    """,
    "Q9 — Top 5 Churn Combos": """
        SELECT Contract, InternetService, PaymentMethod,
               COUNT(*) AS total,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),1) AS churn_rate_pct
        FROM customers
        GROUP BY Contract, InternetService, PaymentMethod
        HAVING total>=50 ORDER BY churn_rate_pct DESC LIMIT 5
    """,
    "Q10 — Churn by Tenure Cohort": """
        SELECT CASE
                 WHEN tenure BETWEEN 0  AND 11 THEN '0-11 months (New)'
                 WHEN tenure BETWEEN 12 AND 23 THEN '12-23 months'
                 WHEN tenure BETWEEN 24 AND 35 THEN '24-35 months'
                 WHEN tenure BETWEEN 36 AND 47 THEN '36-47 months'
                 WHEN tenure BETWEEN 48 AND 59 THEN '48-59 months'
                 ELSE '60+ months (Loyal)'
               END AS tenure_cohort,
               COUNT(*) AS total,
               ROUND(100.0*AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END),2) AS churn_rate_pct
        FROM customers GROUP BY tenure_cohort ORDER BY MIN(tenure)
    """,
}

for title, sql in queries.items():
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))

conn.close()
print("\n[DONE] All queries complete.")
