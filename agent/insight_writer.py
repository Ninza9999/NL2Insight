# agent/insight_writer.py
#
# WHY THIS EXISTS:
# Raw query results are just numbers. Business users want meaning.
# This takes the DataFrame result + the original question
# and asks the LLM to write a short business insight.
#
# Example:
# Input:  "average delivery = 12.5 days"
# Output: "Average delivery time is 12.5 days. São Paulo orders
#          arrive fastest at 10.2 days while rural states average
#          18+ days, suggesting a logistics optimization opportunity."

import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model       = "gpt-4o-mini",
    api_key     = os.getenv("GITHUB_TOKEN"),
    base_url    = "https://models.inference.ai.azure.com",
    temperature = 0.3,   # slight creativity for narrative writing
    max_tokens  = 200,
)

INSIGHT_SYSTEM_PROMPT = """You are a senior business analyst writing insights for executives.
Given a business question and query results, write a concise 2-3 line insight.

RULES:
1. Start with the key number or finding
2. Add one sentence of business context or comparison
3. End with one actionable recommendation or observation
4. Be specific — use the actual numbers from the data
5. Write in plain English, no jargon, no bullet points
"""

def generate_insight(question: str, dataframe: pd.DataFrame) -> str:
    """
    Takes the original question + query results DataFrame.
    Returns a 2-3 line business insight as a string.
    """
    # Convert DataFrame to a clean string for the prompt
    # We limit to 20 rows so we don't overflow the context window
    data_str = dataframe.head(20).to_string(index=False)

    messages = [
        SystemMessage(content=INSIGHT_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Business Question: {question}

Query Results:
{data_str}

Write a 2-3 line business insight:
""")
    ]

    response = llm.invoke(messages)
    return response.content.strip()


if __name__ == "__main__":
    # Test with a sample result
    sample_df = pd.DataFrame({
        "customer_city":   ["sao paulo", "rio de janeiro", "belo horizonte", "brasilia", "curitiba"],
        "customer_count":  [15540, 6882, 2773, 2131, 1521]
    })

    question = "Which 5 cities have the most customers?"
    insight  = generate_insight(question, sample_df)

    print(f"❓ Question: {question}")
    print(f"\n💡 Insight:\n{insight}")