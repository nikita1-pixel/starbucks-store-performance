-- ============================================================
-- Starbucks Pune Store Performance — SQL Analysis
-- Business question: "Pune store sales dipped last quarter — why, and what do we do?"
-- Data: starbucks_sales.csv loaded into table `sales`
--       (transaction_id, date, store, category, item, price, quantity)
-- Periods compared: Q2 2025 (baseline) vs Q2 2026 (the worrying quarter)
-- revenue = price * quantity  |  a "visit" = one distinct transaction_id
-- ============================================================


-- ------------------------------------------------------------
-- Q1. Is the dip city-wide, and how big is it? (top-line health check)
--     Splits the top line into 3 signals: revenue, units, visits.
-- ------------------------------------------------------------
SELECT
    strftime('%Y', date)              AS year,
    ROUND(SUM(price * quantity), 0)   AS revenue,
    SUM(quantity)                     AS units_sold,
    COUNT(DISTINCT transaction_id)    AS visits
FROM sales
GROUP BY year
ORDER BY year;
--  RESULT: revenue -5.1%, units -12.2%, visits -11.8%  →  the -5.1% headline HIDES a ~12% footfall crash.


-- ------------------------------------------------------------
-- Q2. Is it a PRICE problem or a TRAFFIC problem?
--     Average price per unit, 2025 vs 2026.
-- ------------------------------------------------------------
SELECT
    strftime('%Y', date)                       AS year,
    ROUND(SUM(price * quantity) * 1.0
          / SUM(quantity), 2)                  AS avg_price_per_unit
FROM sales
GROUP BY year
ORDER BY year;
--  RESULT: avg price rose ~8%  →  price went UP while volume fell. The price hike propped up revenue.


-- ------------------------------------------------------------
-- Q3. WHICH stores are dragging the average down? (revenue YoY by store)
--     This is the key query — proves the dip is NOT city-wide.
-- ------------------------------------------------------------
SELECT
    store,
    ROUND(SUM(CASE WHEN strftime('%Y', date) = '2025' THEN price * quantity END), 0) AS rev_2025,
    ROUND(SUM(CASE WHEN strftime('%Y', date) = '2026' THEN price * quantity END), 0) AS rev_2026,
    ROUND(
        100.0 * (SUM(CASE WHEN strftime('%Y', date) = '2026' THEN price * quantity END)
               - SUM(CASE WHEN strftime('%Y', date) = '2025' THEN price * quantity END))
              / SUM(CASE WHEN strftime('%Y', date) = '2025' THEN price * quantity END), 1
    ) AS revenue_yoy_pct
FROM sales
GROUP BY store
ORDER BY revenue_yoy_pct;
--  RESULT: Hinjewadi IT Park ~-51%, FC Road ~-13%; the other 3 stores +11–14%.
--          Only 2 of 5 stores are the problem.


-- ------------------------------------------------------------
-- Q4. Confirm the diagnosis with a SECOND, independent metric: visits YoY by store.
--     If BOTH revenue and visits point to the same 2 stores, the diagnosis is trustworthy.
-- ------------------------------------------------------------
SELECT
    store,
    COUNT(DISTINCT CASE WHEN strftime('%Y', date) = '2025' THEN transaction_id END) AS visits_2025,
    COUNT(DISTINCT CASE WHEN strftime('%Y', date) = '2026' THEN transaction_id END) AS visits_2026,
    ROUND(
        100.0 * (COUNT(DISTINCT CASE WHEN strftime('%Y', date) = '2026' THEN transaction_id END)
               - COUNT(DISTINCT CASE WHEN strftime('%Y', date) = '2025' THEN transaction_id END))
              / COUNT(DISTINCT CASE WHEN strftime('%Y', date) = '2025' THEN transaction_id END), 1
    ) AS visits_yoy_pct
FROM sales
GROUP BY store
ORDER BY visits_yoy_pct;
--  RESULT: same 2 stores collapse on footfall too → revenue drop is a REAL traffic problem, not a data fluke.
