"""
generate_data.py
----------------
Generates a realistic synthetic Telco Customer Churn dataset (~7,000 rows).
Run this if you don't have the Kaggle dataset.
Output: data/raw/telco_churn.csv
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
n = 7043

# Demographics
customer_ids = [f"CUST-{str(i).zfill(5)}" for i in range(1, n + 1)]
genders = np.random.choice(["Male", "Female"], n)
senior = np.random.choice([0, 1], n, p=[0.84, 0.16])
partners = np.random.choice(["Yes", "No"], n)
dependents = np.random.choice(["Yes", "No"], n, p=[0.3, 0.7])

# Tenure and contract
contract = np.random.choice(
    ["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.21, 0.24]
)
tenure = np.where(
    contract == "Month-to-month",
    np.random.exponential(scale=15, size=n).clip(1, 72).astype(int),
    np.where(
        contract == "One year",
        np.random.exponential(scale=30, size=n).clip(1, 72).astype(int),
        np.random.exponential(scale=50, size=n).clip(1, 72).astype(int),
    ),
)

# Services
phone_service = np.random.choice(["Yes", "No"], n, p=[0.9, 0.1])
multiple_lines = np.where(
    phone_service == "No",
    "No phone service",
    np.random.choice(["Yes", "No"], n),
)
internet_service = np.random.choice(
    ["DSL", "Fiber optic", "No"], n, p=[0.34, 0.44, 0.22]
)

def internet_addon(internet_service, yes_p=0.5):
    result = []
    for svc in internet_service:
        if svc == "No":
            result.append("No internet service")
        else:
            result.append(np.random.choice(["Yes", "No"], p=[yes_p, 1 - yes_p]))
    return result

online_security    = internet_addon(internet_service, 0.29)
online_backup      = internet_addon(internet_service, 0.34)
device_protection  = internet_addon(internet_service, 0.34)
tech_support       = internet_addon(internet_service, 0.29)
streaming_tv       = internet_addon(internet_service, 0.38)
streaming_movies   = internet_addon(internet_service, 0.39)

# Billing
paperless_billing = np.random.choice(["Yes", "No"], n, p=[0.59, 0.41])
payment_method = np.random.choice(
    [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
    n,
    p=[0.34, 0.23, 0.22, 0.21],
)

# Monthly charges based on services
base_charge = np.where(internet_service == "No", 20, np.where(internet_service == "DSL", 45, 70))
addon_charge = (
    (np.array(online_security) == "Yes").astype(int) * 5
    + (np.array(online_backup) == "Yes").astype(int) * 5
    + (np.array(device_protection) == "Yes").astype(int) * 5
    + (np.array(tech_support) == "Yes").astype(int) * 5
    + (np.array(streaming_tv) == "Yes").astype(int) * 5
    + (np.array(streaming_movies) == "Yes").astype(int) * 5
    + (np.array(multiple_lines) == "Yes").astype(int) * 10
)
monthly_charges = (base_charge + addon_charge + np.random.normal(0, 3, n)).round(2)
total_charges = (monthly_charges * tenure + np.random.normal(0, 10, n)).clip(0).round(2)

# Churn probability (realistic logic)
churn_prob = (
    0.05
    + 0.25 * (contract == "Month-to-month")
    + 0.10 * (internet_service == "Fiber optic")
    + 0.08 * (payment_method == "Electronic check")
    + 0.12 * (tenure < 6)
    - 0.10 * (tenure > 36)
    - 0.08 * (np.array(online_security) == "Yes")
    - 0.08 * (np.array(tech_support) == "Yes")
    + 0.05 * (paperless_billing == "Yes")
    + 0.03 * senior
).clip(0.02, 0.95)

churn = (np.random.random(n) < churn_prob).astype(int)
churn_label = np.where(churn == 1, "Yes", "No")

df = pd.DataFrame({
    "customerID":       customer_ids,
    "gender":           genders,
    "SeniorCitizen":    senior,
    "Partner":          partners,
    "Dependents":       dependents,
    "tenure":           tenure,
    "PhoneService":     phone_service,
    "MultipleLines":    multiple_lines,
    "InternetService":  internet_service,
    "OnlineSecurity":   online_security,
    "OnlineBackup":     online_backup,
    "DeviceProtection": device_protection,
    "TechSupport":      tech_support,
    "StreamingTV":      streaming_tv,
    "StreamingMovies":  streaming_movies,
    "Contract":         contract,
    "PaperlessBilling": paperless_billing,
    "PaymentMethod":    payment_method,
    "MonthlyCharges":   monthly_charges,
    "TotalCharges":     total_charges,
    "Churn":            churn_label,
})

out_path = os.path.join(os.path.dirname(__file__), "raw", "telco_churn.csv")
df.to_csv(out_path, index=False)
print(f"[OK] Dataset generated: {out_path}")
print(f"   Rows: {len(df):,}  |  Churn rate: {df['Churn'].eq('Yes').mean():.1%}")
