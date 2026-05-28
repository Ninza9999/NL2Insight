# agent/sql_generator.py
#
# WHY THIS EXISTS:
# This is the core AI brain. It takes a plain English question,
# combines it with the DB schema, sends it to the LLM,
# and gets back a SQL query we can actually run.
#
# Flow:
# question (English) → prompt (question + schema) → LLM → SQL → execute → DataFrame

import os
import re
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from pathlib import Path

from agent.schema_extractor import get_schema_string

load_dotenv()

# ─── Database connection ───────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent.parent / "db" / "olist.db"
engine  = create_engine(f"sqlite:///{DB_PATH}")

# ─── LLM Setup (GitHub Models → GPT-4o-mini) ──────────────────────────────────
# GitHub Models uses OpenAI-compatible API, so we use ChatOpenAI
# but point it at GitHub's endpoint instead of OpenAI's
llm = ChatOpenAI(
    model       = "gpt-4o-mini",
    api_key     = os.getenv("GITHUB_TOKEN"),
    base_url    = "https://models.inference.ai.azure.com",
    temperature = 0,        # 0 = deterministic, we want consistent SQL
    max_tokens  = 500,
)

# ─── System Prompt ────────────────────────────────────────────────────────────
# This is the instruction we give the LLM before every question.
# It tells the LLM exactly what role to play and how to respond.
SYSTEM_PROMPT = f"""You are an expert SQL analyst working with a Brazilian e-commerce database.

{get_schema_string()}

RULES:
1. Always return ONLY a valid SQLite SQL query — no explanation, no markdown, no backticks
2. Use exact table and column names from the schema above
3. Always use LIMIT 100 unless the question asks for totals/aggregates
4. For revenue calculations, use order_payments.payment_value
5. For product categories, always JOIN with category_translation to get English names
6. Use STRFTIME('%Y-%m', column) for monthly groupings
7. If the question cannot be answered with the available schema, return: CANNOT_ANSWER
7. For date differences in days, use: JULIANDAY(end_date) - JULIANDAY(start_date)
8. For filtering nulls, use: WHERE column IS NOT NULL
9. If the question cannot be answered with the available schema, return: CANNOT_ANSWER
10. NEVER use reserved words as table aliases — avoid: or, and, in, is, as, by, on
    Use full names instead: order_reviews AS reviews, orders AS ord
"""

def extract_sql(raw_response: str) -> str:
    """
    Cleans up the LLM response to extract pure SQL.
    Sometimes LLMs wrap SQL in markdown like ```sql ... ```
    This function strips all that out.
    """
    # Remove markdown code blocks if present
    cleaned = re.sub(r"```sql|```", "", raw_response).strip()
    return cleaned


def generate_sql(question: str) -> dict:
    """
    Takes a plain English question.
    Returns a dict with:
      - sql:       the generated SQL string
      - dataframe: results as a pandas DataFrame (None if failed)
      - error:     error message if something went wrong (None if success)
      - confidence: how confident the LLM is (1-5 scale)
    """
    # Step 1 — Ask the LLM to generate SQL
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Question: {question}\n\nSQL Query:")
    ]

    try:
        response     = llm.invoke(messages)
        raw_sql      = response.content.strip()
        sql          = extract_sql(raw_sql)

        # Step 2 — Check if LLM said it can't answer
        if sql == "CANNOT_ANSWER":
            return {
                "sql": None,
                "dataframe": None,
                "error": "This question cannot be answered with the available data.",
                "confidence": 0
            }

        # Step 3 — Execute the SQL on olist.db
        df = pd.read_sql(sql, engine)

        # Step 4 — Ask LLM to rate its own confidence (1-5)
        confidence_msg = [
            SystemMessage(content="You are a SQL quality checker. Rate confidence 1-5. Return ONLY a single digit."),
            HumanMessage(content=f"Question: {question}\nSQL: {sql}\nRate confidence (1=low, 5=high):")
        ]
        conf_response = llm.invoke(confidence_msg)
        try:
            confidence = int(conf_response.content.strip()[0])
        except:
            confidence = 3  # default to middle if parsing fails

        return {
            "sql":       sql,
            "dataframe": df,
            "error":     None,
            "confidence": confidence
        }

    except Exception as e:
        return {
            "sql":       sql if 'sql' in locals() else None,
            "dataframe": None,
            "error":     str(e),
            "confidence": 0
        }


if __name__ == "__main__":
    # Quick test — ask 3 questions and see what happens
    test_questions = [
        "What is the total revenue?",
        "Which 5 cities have the most customers?",
        "What is the average delivery time in days?",
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {q}")
        result = generate_sql(q)
        print(f"🔍 SQL:\n{result['sql']}")
        print(f"⭐ Confidence: {result['confidence']}/5")
        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📊 Results ({len(result['dataframe'])} rows):")
            print(result['dataframe'].to_string(index=False))