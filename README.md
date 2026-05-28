# 📊 NL2Insight — Natural Language Business Analytics Agent

> Type a business question in plain English → get SQL, data, and an AI-generated insight instantly.

🔗 **[Live Demo](https://nl2insight-3npzpqdfixoykbtaqdmugx.streamlit.app/)** | Built with LangChain · GPT-4o-mini · SQLite · Streamlit

---

## What it does

NL2Insight is an end-to-end agentic AI system that lets non-technical users query a 100K+ row e-commerce database using plain English — no SQL knowledge required.

**Ask:** *"Which product categories have the best ratings?"*
**Get:** The SQL, a bar chart, a data table, and a 3-line business insight — all in seconds.

---

## Architecture
User Question (English)
↓
Schema Extractor → feeds DB structure to LLM
↓
SQL Generator (GPT-4o-mini via LangChain)
↓
SQLite Execution (Olist E-Commerce DB)
↓
Insight Writer (GPT-4o-mini)
↓
Streamlit UI (chart + table + insight card)

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangChain](https://img.shields.io/badge/LangChain-latest-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![GPT-4o-mini](https://img.shields.io/badge/GPT--4o--mini-GitHub%20Models-black)

| Layer | Technology |
|-------|-----------|
| Data | SQLite + Olist Brazilian E-Commerce (100K+ orders) |
| AI | LangChain + GPT-4o-mini (GitHub Models) |
| Backend | Python — sql_generator, insight_writer, orchestrator |
| Frontend | Streamlit + Plotly |
| Deployment | Streamlit Cloud |

---

## Example Queries

| Question | Result |
|----------|--------|
| "What is the total revenue?" | $16,008,872 |
| "Which 5 cities have the most customers?" | São Paulo leads with 15,540 |
| "How many orders were delivered late?" | 7,827 orders (8.1%) |
| "What is the average delivery time?" | 12.5 days |
| "Which payment methods do customers prefer?" | Credit card at 73% |

---

## Project Structure
NL2Insight/
├── agent/
│   ├── schema_extractor.py   # Reads DB structure for LLM context
│   ├── sql_generator.py      # English → SQL → DataFrame
│   ├── insight_writer.py     # DataFrame → business narrative
│   └── nl2insight.py         # Master orchestrator
├── app/
│   └── streamlit_app.py      # Full UI
├── db/
│   └── setup_db.py           # Loads CSVs into SQLite
├── tests/
│   └── ground_truth_queries.sql  # 16 verified queries
└── data/raw/                 # Olist CSV files

---

## Run Locally

```bash
git clone https://github.com/Ninza9999/NL2Insight.git
cd NL2Insight
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python db/setup_db.py
streamlit run app/streamlit_app.py
```


---

## Key Engineering Decisions

- **SQLite over PostgreSQL** — zero config, file-based, perfect for deployment
- **Schema injection** — DB structure sent in every prompt so LLM writes accurate SQL
- **Prompt engineering** — 10 explicit rules prevent common SQL errors (reserved word aliases, missing date functions, NULL handling)
- **Auto chart selection** — time series → line chart, categorical → bar chart, single value → metric card
- **Graceful error handling** — agent explains failures in plain English instead of crashing

---

Built by **Nikhil Dalal** — [GitHub](https://github.com/Ninza9999) | [LinkedIn](linkedin.com/in/ nikhil-dalal-3544bb231)