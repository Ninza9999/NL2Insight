# app/streamlit_app.py

# app/streamlit_app.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Auto-build DB on first run (Streamlit Cloud has no DB file)
DB_FILE = Path(__file__).parent.parent / "db" / "olist.db"
if not DB_FILE.exists():
    from db.setup_db import load_data
    load_data()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from agent.nl2insight import run_query

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NL2Insight — Business Analytics",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080C14 !important;
    color: #E8EDF5 !important;
    font-family: 'DM Mono', monospace !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 20%, #0D1F3C 0%, #080C14 60%) !important;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Hero Header ── */
.hero {
    padding: 3rem 0 2rem 0;
    border-bottom: 1px solid #1A2540;
    margin-bottom: 2.5rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60A5FA;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 2px;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    color: #F0F4FF !important;
    letter-spacing: -0.02em;
    margin: 0.5rem 0 1rem 0;
}
.hero-title span {
    color: #3B82F6;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #4A5568;
    letter-spacing: 0.02em;
    max-width: 500px;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3B82F6;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1A2540;
}

/* ── Example Buttons ── */
div[data-testid="stButton"] > button {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid #1E2D4A !important;
    color: #94A3B8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    padding: 0.6rem 1rem !important;
    border-radius: 4px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
    letter-spacing: 0.01em !important;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(59, 130, 246, 0.08) !important;
    border-color: #3B82F6 !important;
    color: #E2E8F0 !important;
    transform: translateY(-1px) !important;
}

/* Primary run button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #3B82F6 !important;
    border: none !important;
    color: #FFFFFF !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 2rem !important;
    border-radius: 4px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #2563EB !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3) !important;
}

/* ── Input Field ── */
div[data-testid="stTextInput"] > div > div > input {
    background: #0D1525 !important;
    border: 1px solid #1E2D4A !important;
    border-radius: 4px !important;
    color: #E2E8F0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.85rem 1.2rem !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}
div[data-testid="stTextInput"] > div > div > input::placeholder {
    color: #2D3F5E !important;
}

/* ── Result Cards ── */
.result-card {
    background: #0D1525;
    border: 1px solid #1A2540;
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1rem 0;
}
.confidence-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1.2rem;
    background: #0D1525;
    border: 1px solid #1A2540;
    border-left: 3px solid #3B82F6;
    border-radius: 4px;
    margin: 1rem 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #60A5FA;
    letter-spacing: 0.05em;
}
.insight-card {
    background: linear-gradient(135deg, #0D1F3C 0%, #0D1525 100%);
    border: 1px solid #1E3A5F;
    border-left: 3px solid #60A5FA;
    border-radius: 4px;
    padding: 1.5rem 1.8rem;
    margin: 1rem 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    color: #CBD5E1;
    letter-spacing: 0.01em;
}
.metric-card {
    background: #0D1525;
    border: 1px solid #1A2540;
    border-radius: 6px;
    padding: 2rem;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #60A5FA;
    letter-spacing: -0.02em;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4A5568;
    margin-top: 0.5rem;
}
.error-card {
    background: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-left: 3px solid #EF4444;
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #FCA5A5;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0D1525 !important;
    border: 1px solid #1A2540 !important;
    border-radius: 4px !important;
}
[data-testid="stExpander"] summary {
    color: #4A5568 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1A2540 !important;
    border-radius: 4px !important;
}

/* ── Divider ── */
hr { border-color: #1A2540 !important; }

/* ── Footer ── */
.footer {
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1A2540;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #1E2D4A;
    letter-spacing: 0.1em;
    display: flex;
    justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">⬡ AI-Powered Analytics</div>
    <div class="hero-title">NL2<span>Insight</span></div>
    <div class="hero-sub">Type a business question. Get SQL, data, and an expert insight — instantly.</div>
</div>
""", unsafe_allow_html=True)

# ─── Example Prompts ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Quick Queries</div>', unsafe_allow_html=True)

examples = [
    "What is the total revenue?",
    "Which 5 cities have the most customers?",
    "What are the top 5 product categories by revenue?",
    "How many orders were delivered late?",
    "What is the average delivery time in days?",
    "Which payment methods do customers prefer?",
]

cols = st.columns(3)
for i, example in enumerate(examples):
    if cols[i % 3].button(example, key=f"ex_{i}", use_container_width=True):
        st.session_state["question"] = example

# ─── Query Input ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Ask a Question</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    question = st.text_input(
        label="question",
        placeholder="e.g. What is our average order value by state?",
        value=st.session_state.get("question", ""),
        label_visibility="collapsed"
    )
with col_btn:
    run_button = st.button("Run →", type="primary", use_container_width=True)

# ─── Results ──────────────────────────────────────────────────────────────────
if run_button and question:
    with st.spinner(""):
        result = run_query(question)

    if result["error"]:
        st.markdown(f'<div class="error-card">⚠ {result["error"]}</div>', unsafe_allow_html=True)
        if result["sql"]:
            with st.expander("View SQL"):
                st.code(result["sql"], language="sql")
    else:
        df = result["dataframe"]
        conf = result["confidence"]
        conf_label = "HIGH" if conf >= 4 else "MEDIUM" if conf == 3 else "LOW"
        conf_color = "#60A5FA" if conf >= 4 else "#FBBF24" if conf == 3 else "#EF4444"

        # Confidence bar
        st.markdown(f"""
        <div class="confidence-bar">
            <span style="color:{conf_color}">■ CONFIDENCE: {conf_label} ({conf}/5)</span>
            <span style="color:#1E2D4A; margin-left:auto">{len(df)} ROWS RETURNED</span>
        </div>
        """, unsafe_allow_html=True)

        # SQL expander
        with st.expander("⌗ View Generated SQL"):
            st.code(result["sql"], language="sql")

        # Chart / Metric
        st.markdown('<div class="section-label" style="margin-top:1.5rem">Data</div>', unsafe_allow_html=True)

        num_rows, num_cols = df.shape

        plotly_theme = dict(
            paper_bgcolor="#080C14",
            plot_bgcolor="#080C14",
            font=dict(family="DM Mono", color="#4A5568", size=11),
            xaxis=dict(gridcolor="#1A2540", linecolor="#1A2540"),
            yaxis=dict(gridcolor="#1A2540", linecolor="#1A2540"),
            margin=dict(l=20, r=20, t=40, b=20),
        )

        if num_rows == 1 and num_cols == 1:
            val = df.iloc[0, 0]
            label = df.columns[0].replace("_", " ").upper()
            formatted = f"{val:,.2f}" if isinstance(val, float) else str(val)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{formatted}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        elif num_cols >= 2:
            col1, col2 = df.columns[0], df.columns[1]
            is_time = any(k in col1.lower() for k in ["month", "date", "year", "week", "time"])

            if is_time:
                fig = px.line(df, x=col1, y=col2,
                    color_discrete_sequence=["#3B82F6"])
                fig.update_traces(line_width=2, marker=dict(size=5))
            else:
                fig = px.bar(df.head(20), x=col1, y=col2,
                    color_discrete_sequence=["#3B82F6"])
                fig.update_traces(marker_opacity=0.85)

            fig.update_layout(**plotly_theme, title=dict(
                text=question, font=dict(family="Syne", size=13, color="#4A5568")
            ))
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)

        # Insight card
        if result["insight"]:
            st.markdown('<div class="section-label" style="margin-top:1.5rem">AI Insight</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-card">💡 {result["insight"]}</div>', unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <span>NL2INSIGHT — NATURAL LANGUAGE ANALYTICS</span>
    <span>BUILT WITH LANGCHAIN · GPT-4O-MINI · SQLITE · STREAMLIT</span>
</div>
""", unsafe_allow_html=True)