# db/test_queries.py
# Runs a few ground truth queries so we can see real results
# This also proves our DB is wired up correctly

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

DB_PATH = Path(__file__).parent / "olist.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

queries = {
    "Total Revenue": "SELECT ROUND(SUM(payment_value), 2) AS total_revenue FROM order_payments",
    "Order Status Breakdown": """
        SELECT order_status, COUNT(*) AS total_orders
        FROM orders GROUP BY order_status ORDER BY total_orders DESC
    """,
    "Top 5 Cities": """
        SELECT customer_city, COUNT(*) AS customers
        FROM customers GROUP BY customer_city ORDER BY customers DESC LIMIT 5
    """,
}

for name, sql in queries.items():
    print(f"\n{'─'*50}")
    print(f"📊 {name}")
    print('─'*50)
    df = pd.read_sql(sql, engine)
    print(df.to_string(index=False))