-- ============================================================
-- business_queries.sql
-- Customer Churn Analysis — SQL Business Questions
-- Database: churn.db (SQLite)
-- Run via: python sql/run_queries.py
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- Q1. What is the overall churn rate?
-- ─────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                     AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS total_churned,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                            AS churn_rate_pct
FROM customers;


-- ─────────────────────────────────────────────────────────────
-- Q2. Churn rate by contract type (ranked)
-- ─────────────────────────────────────────────────────────────
SELECT
    Contract,
    COUNT(*)                                             AS total,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)      AS churned,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- Q3. Average monthly charges & tenure: churned vs retained
-- ─────────────────────────────────────────────────────────────
SELECT
    Churn                                     AS status,
    ROUND(AVG(MonthlyCharges), 2)             AS avg_monthly_charges,
    ROUND(AVG(TotalCharges), 2)               AS avg_total_charges,
    ROUND(AVG(tenure), 1)                     AS avg_tenure_months,
    COUNT(*)                                  AS customer_count
FROM customers
GROUP BY Churn;


-- ─────────────────────────────────────────────────────────────
-- Q4. Monthly revenue at risk (from active churners)
-- ─────────────────────────────────────────────────────────────
SELECT
    ROUND(SUM(MonthlyCharges), 2)   AS monthly_revenue_at_risk,
    ROUND(SUM(TotalCharges), 2)     AS total_historical_revenue_lost,
    COUNT(*)                        AS churned_customers
FROM customers
WHERE Churn = 'Yes';


-- ─────────────────────────────────────────────────────────────
-- Q5. Churn rate by internet service type
-- ─────────────────────────────────────────────────────────────
SELECT
    InternetService,
    COUNT(*)                                        AS total,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- Q6. Churn rate by payment method
-- ─────────────────────────────────────────────────────────────
SELECT
    PaymentMethod,
    COUNT(*)                                        AS total,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- Q7. High-risk customer segment (most likely to churn)
--     Month-to-month, Fiber optic, Electronic check, tenure < 12
-- ─────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                        AS high_risk_customers,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                   AS avg_monthly_charges
FROM customers
WHERE Contract        = 'Month-to-month'
  AND InternetService = 'Fiber optic'
  AND PaymentMethod   = 'Electronic check'
  AND tenure          < 12;


-- ─────────────────────────────────────────────────────────────
-- Q8. Senior citizens churn vs non-senior
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE WHEN SeniorCitizen = 1 THEN 'Senior' ELSE 'Non-Senior' END AS segment,
    COUNT(*)                                        AS total,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers
GROUP BY SeniorCitizen;


-- ─────────────────────────────────────────────────────────────
-- Q9. Top 5 service combos with highest churn
-- ─────────────────────────────────────────────────────────────
SELECT
    Contract,
    InternetService,
    PaymentMethod,
    COUNT(*)                                        AS total,
    SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END)    AS churned,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 1) AS churn_rate_pct
FROM customers
GROUP BY Contract, InternetService, PaymentMethod
HAVING total >= 50
ORDER BY churn_rate_pct DESC
LIMIT 5;


-- ─────────────────────────────────────────────────────────────
-- Q10. Cohort analysis — churn by tenure bucket
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN tenure BETWEEN 0  AND 11 THEN '0-11 months (New)'
        WHEN tenure BETWEEN 12 AND 23 THEN '12-23 months'
        WHEN tenure BETWEEN 24 AND 35 THEN '24-35 months'
        WHEN tenure BETWEEN 36 AND 47 THEN '36-47 months'
        WHEN tenure BETWEEN 48 AND 59 THEN '48-59 months'
        ELSE '60+ months (Loyal)'
    END AS tenure_cohort,
    COUNT(*)                                        AS total,
    ROUND(100.0 * AVG(CASE WHEN Churn='Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers
GROUP BY tenure_cohort
ORDER BY MIN(tenure);
