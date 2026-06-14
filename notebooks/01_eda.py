"""
01_eda.py  (Run as Jupyter notebook cells using VS Code "# %%" or plain Python)
---------------------------------------------------------------------------------
Exploratory Data Analysis — Customer Churn Dataset
"""

# %% [markdown]
# # Customer Churn Analysis - Exploratory Data Analysis
# **Goal**: Understand the data, find patterns, and identify key drivers of churn.

# %% — Imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — saves charts without opening windows
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os, warnings

warnings.filterwarnings("ignore")

# Style
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({"figure.figsize": (10, 5), "figure.dpi": 120,
                     "font.family": "DejaVu Sans"})
CHURN_PALETTE = {"Yes": "#e74c3c", "No": "#2ecc71"}

# %% — Load Data
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, "data", "raw", "telco_churn.csv")
PROC = os.path.join(BASE, "data", "processed", "churn_cleaned.csv")

df = pd.read_csv(RAW)
print(f"Shape: {df.shape}")
print(f"\nColumn dtypes:\n{df.dtypes}")
df.head()

# %% — Basic Stats
print("=== Missing Values ===")
print(df.isnull().sum())
print("\n=== Duplicates:", df.duplicated().sum())
print("\n=== Churn Distribution:\n", df["Churn"].value_counts())

# %% — Data Cleaning
# Fix TotalCharges (may be string with spaces in real Kaggle data)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)

# Encode churn as binary
df["ChurnBinary"] = (df["Churn"] == "Yes").astype(int)

# Drop customerID
df_clean = df.drop(columns=["customerID"])

df_clean.to_csv(PROC, index=False)
print(f"[SAVED] Cleaned data saved -> {PROC}")

# %% — Plot 1: Churn Distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
churn_counts = df["Churn"].value_counts()

axes[0].pie(churn_counts, labels=churn_counts.index,
            autopct="%1.1f%%", colors=["#2ecc71", "#e74c3c"],
            startangle=90, wedgeprops=dict(width=0.6))
axes[0].set_title("Overall Churn Rate", fontsize=14, fontweight="bold")

sns.countplot(data=df, x="Churn", palette=CHURN_PALETTE, ax=axes[1])
axes[1].set_title("Churned vs Retained Customers", fontsize=14, fontweight="bold")
axes[1].set_xlabel("Churn")
axes[1].set_ylabel("Number of Customers")
for p in axes[1].patches:
    axes[1].annotate(f'{int(p.get_height()):,}',
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "01_churn_distribution.png"), bbox_inches="tight")
plt.show()

# %% — Plot 2: Churn by Contract Type
fig, ax = plt.subplots(figsize=(10, 5))
contract_churn = df.groupby("Contract")["ChurnBinary"].mean().sort_values(ascending=False) * 100
bars = ax.bar(contract_churn.index, contract_churn.values,
              color=["#e74c3c", "#f39c12", "#2ecc71"], edgecolor="white", linewidth=1.5)
ax.set_title("Churn Rate by Contract Type", fontsize=14, fontweight="bold")
ax.set_ylabel("Churn Rate (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for bar, val in zip(bars, contract_churn.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "02_churn_by_contract.png"), bbox_inches="tight")
plt.close()
print(contract_churn.to_string())

# %% — Plot 3: Tenure Distribution by Churn
fig, ax = plt.subplots(figsize=(12, 5))
for churn_val, color in CHURN_PALETTE.items():
    subset = df[df["Churn"] == churn_val]["tenure"]
    ax.hist(subset, bins=30, alpha=0.7, label=f"Churn={churn_val}",
            color=color, edgecolor="white")
ax.set_title("Customer Tenure Distribution by Churn Status", fontsize=14, fontweight="bold")
ax.set_xlabel("Tenure (months)")
ax.set_ylabel("Count")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "03_tenure_distribution.png"), bbox_inches="tight")
plt.close()

# %% — Plot 4: Monthly Charges Boxplot
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="Churn", y="MonthlyCharges", palette=CHURN_PALETTE, ax=ax)
ax.set_title("Monthly Charges: Churned vs Retained", fontsize=14, fontweight="bold")
ax.set_xlabel("Churn")
ax.set_ylabel("Monthly Charges ($)")
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "04_monthly_charges_box.png"), bbox_inches="tight")
plt.close()

# %% — Plot 5: Churn by Internet Service
fig, ax = plt.subplots(figsize=(10, 5))
internet_churn = df.groupby("InternetService")["ChurnBinary"].mean().sort_values(ascending=False) * 100
bars = ax.bar(internet_churn.index, internet_churn.values,
              color=["#e74c3c", "#f39c12", "#3498db"], edgecolor="white")
ax.set_title("Churn Rate by Internet Service Type", fontsize=14, fontweight="bold")
ax.set_ylabel("Churn Rate (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for bar, val in zip(bars, internet_churn.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val:.1f}%", ha="center", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "05_churn_by_internet.png"), bbox_inches="tight")
plt.close()

# %% — Plot 6: Churn by Payment Method
fig, ax = plt.subplots(figsize=(11, 5))
pay_churn = df.groupby("PaymentMethod")["ChurnBinary"].mean().sort_values(ascending=False) * 100
bars = ax.barh(pay_churn.index, pay_churn.values,
               color=["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71"])
ax.set_title("Churn Rate by Payment Method", fontsize=14, fontweight="bold")
ax.set_xlabel("Churn Rate (%)")
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
for bar, val in zip(bars, pay_churn.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "06_churn_by_payment.png"), bbox_inches="tight")
plt.close()

# %% — Plot 7: Correlation Heatmap
numeric_df = df_clean.select_dtypes(include=[np.number])
fig, ax = plt.subplots(figsize=(10, 7))
mask = np.triu(np.ones_like(numeric_df.corr(), dtype=bool))
sns.heatmap(numeric_df.corr(), mask=mask, annot=True, fmt=".2f",
            cmap="RdYlGn", center=0, ax=ax, linewidths=0.5)
ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(BASE, "reports", "07_correlation_heatmap.png"), bbox_inches="tight")
plt.close()

# %% — Summary Statistics
print("\n" + "="*60)
print("KEY EDA FINDINGS")
print("="*60)
churn_rate = df["ChurnBinary"].mean() * 100
month_churn = df[df["Contract"]=="Month-to-month"]["ChurnBinary"].mean()*100
fiber_churn = df[df["InternetService"]=="Fiber optic"]["ChurnBinary"].mean()*100
elec_churn  = df[df["PaymentMethod"]=="Electronic check"]["ChurnBinary"].mean()*100
new_cust_churn = df[df["tenure"]<6]["ChurnBinary"].mean()*100
print(f"1. Overall churn rate:                     {churn_rate:.1f}%")
print(f"2. Month-to-month contract churn rate:     {month_churn:.1f}%")
print(f"3. Fiber optic internet churn rate:        {fiber_churn:.1f}%")
print(f"4. Electronic check payment churn rate:    {elec_churn:.1f}%")
print(f"5. New customers (<6 months) churn rate:   {new_cust_churn:.1f}%")
rev_at_risk = df[df["Churn"]=="Yes"]["MonthlyCharges"].sum()
print(f"6. Monthly revenue at risk from churners:  ${rev_at_risk:,.0f}")
