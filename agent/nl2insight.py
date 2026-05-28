cat > agent/nl2insight.py << 'EOF'
import csv
from datetime import datetime
from pathlib import Path
from agent.sql_generator import generate_sql
from agent.insight_writer import generate_insight

LOG_PATH = Path(__file__).parent.parent / "logs" / "query_log.csv"

def log_interaction(question, sql, rows, confidence, error):
    try:
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
    except Exception:
        pass

def run_query(question: str) -> dict:
    result = generate_sql(question)
    insight = None
    if result["dataframe"] is not None and len(result["dataframe"]) > 0:
        insight = generate_insight(question, result["dataframe"])
    try:
        log_interaction(
            question   = question,
            sql        = result["sql"],
            rows       = len(result["dataframe"]) if result["dataframe"] is not None else 0,
            confidence = result["confidence"],
            error      = result["error"]
        )
    except Exception:
        pass
    return {
        "sql":        result["sql"],
        "dataframe":  result["dataframe"],
        "insight":    insight,
        "confidence": result["confidence"],
        "error":      result["error"]
    }
EOF