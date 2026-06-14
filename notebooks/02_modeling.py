"""
02_modeling.py
--------------
Machine Learning — Customer Churn Prediction
Trains Logistic Regression + Random Forest, evaluates, saves model & feature importance.
"""

# %% [markdown]
# # 🤖 Customer Churn Prediction — Machine Learning Model

# %% — Imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import joblib, os, warnings

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, ConfusionMatrixDisplay
)
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid")
plt.rcParams.update({"figure.dpi": 120})

BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC   = os.path.join(BASE, "data", "processed", "churn_cleaned.csv")
MODELS = os.path.join(BASE, "models")
REPS   = os.path.join(BASE, "reports")

# %% — Load & Encode
df = pd.read_csv(PROC)

# Drop target columns BEFORE encoding to prevent data leakage
DROP = ["Churn", "ChurnBinary"]
df_features = df.drop(columns=[c for c in DROP if c in df.columns])

# One-hot encode categoricals
df_encoded = pd.get_dummies(df_features, drop_first=True)
X = df_encoded
y = df["ChurnBinary"]

print(f"Features: {X.shape[1]}  |  Samples: {len(X):,}")

# Save feature names for dashboard
feature_names = list(X.columns)
pd.Series(feature_names).to_csv(os.path.join(MODELS, "feature_names.csv"), index=False)

# %% — Train / Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {len(X_train):,}  |  Test: {len(X_test):,}")
print(f"Test churn rate: {y_test.mean():.1%}")

# %% — Model 1: Logistic Regression
lr_pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
])
lr_pipe.fit(X_train, y_train)
lr_pred  = lr_pipe.predict(X_test)
lr_proba = lr_pipe.predict_proba(X_test)[:, 1]
lr_auc   = roc_auc_score(y_test, lr_proba)
print(f"\n[Logistic Regression] ROC-AUC: {lr_auc:.4f}")
print(classification_report(y_test, lr_pred, target_names=["Retained", "Churned"]))

# %% — Model 2: Random Forest
rf = RandomForestClassifier(
    n_estimators=200, max_depth=12, min_samples_leaf=5,
    class_weight="balanced", random_state=42, n_jobs=-1
)
rf.fit(X_train, y_train)
rf_pred  = rf.predict(X_test)
rf_proba = rf.predict_proba(X_test)[:, 1]
rf_auc   = roc_auc_score(y_test, rf_proba)
print(f"\n[Random Forest] ROC-AUC: {rf_auc:.4f}")
print(classification_report(y_test, rf_pred, target_names=["Retained", "Churned"]))

# %% — Save Best Model
best_model = rf if rf_auc >= lr_auc else lr_pipe
joblib.dump(best_model, os.path.join(MODELS, "churn_model.pkl"))
joblib.dump(lr_pipe,    os.path.join(MODELS, "logistic_model.pkl"))
joblib.dump(rf,         os.path.join(MODELS, "random_forest.pkl"))
print(f"\n[SAVED] Models saved to {MODELS}/")

# %% — Plot: Confusion Matrices Side by Side
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, model, pred, title in zip(
    axes,
    [lr_pipe, rf],
    [lr_pred, rf_pred],
    ["Logistic Regression", "Random Forest"]
):
    cm = confusion_matrix(y_test, pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=["Retained", "Churned"])
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"{title}\nROC-AUC: {roc_auc_score(y_test, rf_proba if title=='Random Forest' else lr_proba):.3f}",
                 fontsize=13, fontweight="bold")
plt.suptitle("Confusion Matrices — Model Comparison", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(REPS, "08_confusion_matrices.png"), bbox_inches="tight")
plt.close()

# %% — Plot: ROC Curves
fig, ax = plt.subplots(figsize=(8, 6))
for proba, label, color in [
    (lr_proba, f"Logistic Regression (AUC={lr_auc:.3f})", "#3498db"),
    (rf_proba, f"Random Forest      (AUC={rf_auc:.3f})", "#e74c3c"),
]:
    fpr, tpr, _ = roc_curve(y_test, proba)
    ax.plot(fpr, tpr, label=label, linewidth=2.5, color=color)
ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
ax.fill_between(*roc_curve(y_test, rf_proba)[:2], alpha=0.08, color="#e74c3c")
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.set_title("ROC Curves — Model Comparison", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(REPS, "09_roc_curves.png"), bbox_inches="tight")
plt.close()

# %% — Plot: Feature Importance (Top 15)
importances = pd.Series(rf.feature_importances_, index=feature_names)
top15 = importances.nlargest(15).sort_values()

fig, ax = plt.subplots(figsize=(10, 7))
colors = ["#e74c3c" if v > 0.05 else "#3498db" for v in top15.values]
bars = ax.barh(top15.index, top15.values, color=colors, edgecolor="white")
ax.set_title("Top 15 Features Driving Customer Churn\n(Random Forest Importance)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Feature Importance Score")
for bar, val in zip(bars, top15.values):
    ax.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=9)
ax.axvline(0.05, color="orange", linestyle="--", linewidth=1.5, label="High importance threshold")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(REPS, "10_feature_importance.png"), bbox_inches="tight")
plt.close()

# %% — Cross-Validation Scores
cv_scores = cross_val_score(rf, X, y, cv=5, scoring="roc_auc", n_jobs=-1)
print(f"\n5-Fold Cross-Validation ROC-AUC: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

# %% — Final Summary
print("\n" + "="*60)
print("MODEL PERFORMANCE SUMMARY")
print("="*60)
print(f"Logistic Regression  -> ROC-AUC: {lr_auc:.4f}")
print(f"Random Forest        -> ROC-AUC: {rf_auc:.4f}")
print(f"CV Score (5-fold)    -> {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
print(f"\nTop 5 Churn Predictors:")
for feat, score in importances.nlargest(5).items():
    print(f"  {feat:<40} {score:.4f}")
