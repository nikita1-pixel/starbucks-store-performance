

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


SELECT
    strftime('%Y', date)                       AS year,
    ROUND(SUM(price * quantity) * 1.0
          / SUM(quantity), 2)                  AS avg_price_per_unit
FROM sales
GROUP BY year
ORDER BY year;
--  RESULT: avg price rose ~8%  →  price went UP while volume fell. The price hike propped up revenue.


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
