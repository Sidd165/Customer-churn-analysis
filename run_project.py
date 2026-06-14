"""
run_project.py — Master Setup & Runner Script
=============================================
Run this ONE script to set up and launch the entire project.

Usage:
    python run_project.py
"""

import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def run(cmd, desc):
    print(f"\n{'='*60}")
    print(f"⚙️  {desc}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, cwd=BASE)
    if result.returncode != 0:
        print(f"⚠️  Warning: step may have had issues. Continuing...")
    return result.returncode

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║       Customer Churn Analysis — Project Setup            ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Step 1 — Install dependencies
    run(f"{sys.executable} -m pip install -r requirements.txt -q", "Installing dependencies...")

    # Step 2 — Generate dataset
    run(f"{sys.executable} data/generate_data.py", "Generating synthetic dataset...")

    # Step 3 — Run EDA
    run(f"{sys.executable} notebooks/01_eda.py", "Running EDA & saving charts...")

    # Step 4 — Run Modeling
    run(f"{sys.executable} notebooks/02_modeling.py", "Training ML models...")

    # Step 5 — Run SQL Queries
    run(f"{sys.executable} sql/run_queries.py", "Running SQL business queries...")

    # Step 6 — Launch Dashboard
    print(f"""
{'='*60}
✅ SETUP COMPLETE!

📊 Launching Streamlit Dashboard...
   → Open your browser at: http://localhost:8501
   → Press Ctrl+C to stop the dashboard

{'='*60}
    """)
    subprocess.run(
        f"streamlit run dashboard/app.py",
        shell=True, cwd=BASE
    )

if __name__ == "__main__":
    main()
