"""
Run the Starbucks SQL analysis end-to-end.

Loads starbucks_sales.csv into an in-memory SQLite database, then runs each
query from sql/starbucks_analysis.sql and prints the results. This proves the
dashboard's numbers come from real, reproducible SQL.

Run it:  python run_sql_analysis.py
"""

import sqlite3
import pandas as pd

# 1. Load the raw extract and push it into a SQLite table called `sales`.
df = pd.read_csv("starbucks_sales.csv")
conn = sqlite3.connect(":memory:")          # a throwaway database in RAM
df.to_sql("sales", conn, index=False, if_exists="replace")


def run(title, query):
    """Run one SQL query and print it as a tidy table."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(pd.read_sql_query(query, conn).to_string(index=False))


# Q1 — top-line health: revenue vs units vs visits
run("Q1. Top line — revenue, units, visits (2025 vs 2026)", """
    SELECT strftime('%Y', date)           AS year,
           ROUND(SUM(price * quantity), 0) AS revenue,
           SUM(quantity)                   AS units_sold,
           COUNT(DISTINCT transaction_id)  AS visits
    FROM sales
    GROUP BY year
    ORDER BY year;
""")

# Q2 — price vs traffic: average price per unit
run("Q2. Average price per unit (2025 vs 2026)", """
    SELECT strftime('%Y', date)                       AS year,
           ROUND(SUM(price * quantity) * 1.0 / SUM(quantity), 2) AS avg_price_per_unit
    FROM sales
    GROUP BY year
    ORDER BY year;
""")

# Q3 — which stores drag the average: revenue YoY by store
run("Q3. Revenue YoY by store (the culprits)", """
    SELECT store,
           ROUND(SUM(CASE WHEN strftime('%Y', date)='2025' THEN price*quantity END), 0) AS rev_2025,
           ROUND(SUM(CASE WHEN strftime('%Y', date)='2026' THEN price*quantity END), 0) AS rev_2026,
           ROUND(100.0 * (SUM(CASE WHEN strftime('%Y', date)='2026' THEN price*quantity END)
                        - SUM(CASE WHEN strftime('%Y', date)='2025' THEN price*quantity END))
                       / SUM(CASE WHEN strftime('%Y', date)='2025' THEN price*quantity END), 1) AS revenue_yoy_pct
    FROM sales
    GROUP BY store
    ORDER BY revenue_yoy_pct;
""")

# Q4 — confirm with a second metric: visits YoY by store
run("Q4. Visits YoY by store (independent confirmation)", """
    SELECT store,
           COUNT(DISTINCT CASE WHEN strftime('%Y', date)='2025' THEN transaction_id END) AS visits_2025,
           COUNT(DISTINCT CASE WHEN strftime('%Y', date)='2026' THEN transaction_id END) AS visits_2026,
           ROUND(100.0 * (COUNT(DISTINCT CASE WHEN strftime('%Y', date)='2026' THEN transaction_id END)
                        - COUNT(DISTINCT CASE WHEN strftime('%Y', date)='2025' THEN transaction_id END))
                       / COUNT(DISTINCT CASE WHEN strftime('%Y', date)='2025' THEN transaction_id END), 1) AS visits_yoy_pct
    FROM sales
    GROUP BY store
    ORDER BY visits_yoy_pct;
""")

conn.close()
