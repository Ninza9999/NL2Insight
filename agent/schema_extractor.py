# agent/schema_extractor.py
#
# WHY THIS EXISTS:
# The LLM has no idea what your database looks like.
# This file reads the DB structure and converts it into
# a clean text description we paste into every prompt.
#
# Example output:
# Table: orders
#   - order_id (TEXT)
#   - customer_id (TEXT)
#   - order_status (TEXT)
#   ...

from sqlalchemy import create_engine, inspect
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "olist.db"

def get_schema_string() -> str:
    """
    Reads every table and column from olist.db
    Returns a clean string description for the LLM prompt
    """
    engine = create_engine(f"sqlite:///{DB_PATH}")
    inspector = inspect(engine)

    schema_parts = []
    schema_parts.append("DATABASE SCHEMA (SQLite):")
    schema_parts.append("=" * 50)

    for table_name in inspector.get_table_names():
        schema_parts.append(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for col in columns:
            schema_parts.append(f"  - {col['name']} ({col['type']})")

    schema_parts.append("\n" + "=" * 50)
    schema_parts.append("\nIMPORTANT RELATIONSHIPS:")
    schema_parts.append("  - orders.customer_id → customers.customer_id")
    schema_parts.append("  - order_items.order_id → orders.order_id")
    schema_parts.append("  - order_items.product_id → products.product_id")
    schema_parts.append("  - order_items.seller_id → sellers.seller_id")
    schema_parts.append("  - order_payments.order_id → orders.order_id")
    schema_parts.append("  - order_reviews.order_id → orders.order_id")
    schema_parts.append("  - products.product_category_name → category_translation.product_category_name")

    return "\n".join(schema_parts)


if __name__ == "__main__":
    # Run this file directly to see what the LLM will see
    print(get_schema_string())