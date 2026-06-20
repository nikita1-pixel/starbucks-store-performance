"""
Data-team script: generates a realistic Starbucks Pune sales extract.
Two periods: Q2 2025 (baseline) and Q2 2026 (the quarter the VP is worried about).
One row = one item sold on one transaction.

(Nikita: you don't need to study this — this is the "data engineer" handing you
your extract. Your job starts when you open the CSV. But it's commented if you're curious.)
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)  # makes the data reproducible — same every run

# --- The 5 Pune stores ---
STORES = [
    "Koregaon Park",
    "Phoenix Marketcity",
    "FC Road",
    "Hinjewadi IT Park",
    "Viman Nagar",
]

# --- Menu: item -> (category, 2025 base price in INR) ---
MENU = {
    "Cappuccino":        ("Beverage", 200),
    "Caffe Latte":       ("Beverage", 220),
    "Cold Brew":         ("Beverage", 250),
    "Frappuccino":       ("Beverage", 300),
    "Filter Coffee":     ("Beverage", 150),
    "Butter Croissant":  ("Food", 180),
    "Chocolate Muffin":  ("Food", 160),
    "Chicken Sandwich":  ("Food", 280),
    "Cookie":            ("Food", 120),
}
ITEMS = list(MENU.keys())

# --- The story baked into the numbers (this is what Nikita has to DISCOVER) ---
# 2026 vs 2025:
#   * Prices +8% across the board   (mild INTERNAL factor)
#   * Hinjewadi IT Park volume -55% (offices went work-from-home -> EXTERNAL footfall crash)
#   * FC Road volume -15%           (a competitor cafe opened nearby -> EXTERNAL)
#   * The other 3 stores +5%        (healthy)
# Net effect: city revenue dips ~4% but UNITS dip ~11% (price hike masks the volume problem),
# and the dip is NOT city-wide — it's concentrated in 2 stores.

VOLUME_2026 = {
    "Koregaon Park":     1.05,
    "Phoenix Marketcity":1.05,
    "FC Road":           0.85,
    "Hinjewadi IT Park": 0.45,
    "Viman Nagar":       1.05,
}
PRICE_BUMP_2026 = 1.08

BASE_TXNS_PER_DAY = 30  # per store per day in 2025


def q2_days(year):
    """Every date in Q2 (Apr 1 - Jun 30) of the given year."""
    d = date(year, 4, 1)
    end = date(year, 6, 30)
    while d <= end:
        yield d
        d += timedelta(days=1)


def make_rows():
    rows = []
    txn_counter = 0
    for year in (2025, 2026):
        for store in STORES:
            # how many transactions this store does per day this year
            multiplier = VOLUME_2026[store] if year == 2026 else 1.0
            txns_per_day = BASE_TXNS_PER_DAY * multiplier
            for day in q2_days(year):
                n_txns = max(0, int(random.gauss(txns_per_day, 4)))
                for _ in range(n_txns):
                    txn_counter += 1
                    txn_id = f"T{txn_counter:07d}"
                    n_items = random.choice([1, 1, 2, 2, 3])  # items per visit
                    for _ in range(n_items):
                        item = random.choice(ITEMS)
                        category, base_price = MENU[item]
                        price = base_price * (PRICE_BUMP_2026 if year == 2026 else 1.0)
                        qty = random.choice([1, 1, 1, 2])
                        rows.append({
                            "transaction_id": txn_id,
                            "date": day.isoformat(),
                            "store": store,
                            "category": category,
                            "item": item,
                            "price": round(price, 2),
                            "quantity": qty,
                        })
    return rows


def main():
    rows = make_rows()
    fields = ["transaction_id", "date", "store", "category", "item", "price", "quantity"]
    with open("starbucks_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows to starbucks_sales.csv")


if __name__ == "__main__":
    main()
