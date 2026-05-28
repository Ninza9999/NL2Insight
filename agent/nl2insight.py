# agent/nl2insight.py
#
# WHY THIS EXISTS:
# This is the master orchestrator. The Streamlit UI will call
# just one function: run_query(question) and get everything back.
# It also logs every interaction to logs/query_log.csv

import csv
import os
from datetime import datetime
from pathlib import Path
from agent.sql_generator import generate_sql
from agent.insight_writer import generate_insight

LOG_PATH = Path(__file__).parent.parent / "logs" / "query_log.csv"

def log_interaction(question, sql, rows, confidence, error):
    """Appends every query to a CSV log file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True) 
    file_exists = LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "question", "sql", "rows_returned", "confidence", "error"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp":     datetime.now().isoformat(),
            "question":      question,
            "sql":           sql,
            "rows_returned": rows,
            "confidence":    confidence,
            "error":         error or ""
        })

def run_query(question: str) -> dict:
    """
    Master function — call this from the UI.
    Input:  plain English question (string)
    Output: dict with sql, dataframe, insight, confidence, error
    """
    # Step 1 — Generate SQL and execute it
    result = generate_sql(question)

    insight = None
    if result["dataframe"] is not None and len(result["dataframe"]) > 0:
        # Step 2 — Generate business insight from results
        insight = generate_insight(question, result["dataframe"])

    # Step 3 — Log everything
    try:
        log_interaction(
            question   = question,
            sql        = result["sql"],
            rows       = len(result["dataframe"]) if result["dataframe"] is not None else 0,
            confidence = result["confidence"],
            error      = result["error"]
        )
    except Exception:
        pass  # Logging is optional — don't crash the app if it fails

    return {
        "sql":        result["sql"],
        "dataframe":  result["dataframe"],
        "insight":    insight,
        "confidence": result["confidence"],
        "error":      result["error"]
    }


if __name__ == "__main__":
    questions = [
        "What is the total revenue?",
        "Which product categories have the best ratings?",
        "How many orders were delivered late?",
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"❓ {q}")
        result = run_query(q)
        print(f"🔍 SQL: {result['sql']}")
        print(f"⭐ Confidence: {result['confidence']}/5")
        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📊 {len(result['dataframe'])} rows returned")
            print(result['dataframe'].head(5).to_string(index=False))
            print(f"\n💡 Insight: {result['insight']}")