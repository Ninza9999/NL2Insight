# db/setup_db.py

# What's happening here:
# pandas  → reads CSV files into DataFrames (like in-memory tables)
# sqlalchemy → creates the SQLite database and handles the connection
# pathlib → handles file paths cleanly across Mac/Windows

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
# Path(__file__) = this file's location (db/setup_db.py)
# .parent        = the db/ folder
# .parent        = the project root (NL2Insight/)
BASE_DIR = Path(__file__).parent.parent
RAW_DATA = BASE_DIR / "data" / "raw"
DB_PATH  = BASE_DIR / "db" / "olist.db"

# ─── Map: table name → CSV filename ───────────────────────────────────────────
# Each key becomes a table name in your database
# Each value is the CSV file it reads from
TABLES = {
    "customers":    "olist_customers_dataset.csv",
    "orders":       "olist_orders_dataset.csv",
    "order_items":  "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products":     "olist_products_dataset.csv",
    "sellers":      "olist_sellers_dataset.csv",
    "geolocation":  "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

def load_data():
    # create_engine sets up the connection to SQLite
    # sqlite:/// means "file-based database"
    # The DB file gets created automatically if it doesn't exist
    engine = create_engine(f"sqlite:///{DB_PATH}")

    print("🚀 Loading Olist data into SQLite...\n")

    for table_name, csv_file in TABLES.items():
        csv_path = RAW_DATA / csv_file

        # Read CSV into a pandas DataFrame
        df = pd.read_csv(csv_path)

        # Write DataFrame into the SQLite database as a table
        # if_exists="replace" → drops & recreates the table each time you run this
        df.to_sql(table_name, engine, if_exists="replace", index=False)

        print(f"  ✅ {table_name:25s} → {len(df):,} rows loaded")

    # Quick sanity check — list all tables now in the DB
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]

    print(f"\n✅ Database created at: {DB_PATH}")
    print(f"📦 Tables in DB: {tables}")

if __name__ == "__main__":
    load_data()