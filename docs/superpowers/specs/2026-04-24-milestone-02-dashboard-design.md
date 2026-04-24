# Milestone 02 Dashboard Design Spec
**Date:** 2026-04-24
**Topic:** Streamlit Dashboard + RAG Chatbot

---

## Overview

A 3-tab Streamlit dashboard connected to Snowflake mart tables, deployed publicly on Streamlit Community Cloud. Includes a RAG chatbot powered by the `knowledge/raw/` scraped files and the Claude API.

**Due:** May 4 at 9:55 AM
**Points:** 15 pts (dashboard) + partial credit toward knowledge base demo

---

## Architecture

```
Snowflake analytics schema (mart tables)
    └── dashboard/app.py (Streamlit)
            ├── Tab 1: Descriptive (plotly map + bar chart)
            ├── Tab 2: Diagnostic (category breakdown + insight)
            └── Tab 3: Chat (RAG via knowledge/raw/ + Claude API)
                    └── knowledge/raw/*.md (17 scraped files)
```

**Credentials needed:**
- All 7 Snowflake env vars (already in `.env`)
- `ANTHROPIC_API_KEY` (new — needed for Claude API in chatbot)

---

## File Structure

```
dashboard/
└── app.py          # Single-file Streamlit app
.streamlit/
└── secrets.toml    # Streamlit Cloud credential format (gitignored)
requirements.txt    # Add: streamlit, plotly, anthropic
```

---

## Tab 1 — Descriptive: "What happened?"

**Purpose:** Show the overall search demand landscape across keywords and US states.

**Layout (top to bottom):**

1. **Keyword filter** — `st.selectbox` with options: All, personal loans, payday loans, credit cards, installment loans, cash advance. Filters all charts below.

2. **3 KPI cards** — `st.columns(3)` with `st.metric()`:
   - Avg Interest Score (mean of `interest_value` for selected keyword)
   - Top State (state with highest interest for selected keyword)
   - Top Keyword (keyword with highest avg interest, shown when filter = All)

3. **US Choropleth Map** — `plotly.express.choropleth`:
   - Color scale: white → dark blue
   - Location mode: `USA-states` (uses 2-letter state codes — need a state name → abbreviation mapping)
   - Title: "Search Interest by State"
   - Updates when keyword filter changes

4. **Bar chart** — `plotly.express.bar`:
   - X: keyword, Y: avg interest_value
   - Color by category (consumer lending = blue, short-term credit = purple, revolving credit = green)
   - Title: "Average Search Interest by Keyword"
   - Hidden when a specific keyword is selected (shows all 5 keywords when filter = All)

**Data query:**
```sql
SELECT k.keyword, k.category, r.region, f.interest_value
FROM analytics.fact_search_interest f
JOIN analytics.dim_keyword k ON f.keyword_id = k.keyword_id
JOIN analytics.dim_region r ON f.region_id = r.region_id
```

---

## Tab 2 — Diagnostic: "Why did it happen?"

**Purpose:** Explain the geographic concentration pattern — why certain states show high demand for certain keyword categories.

**Layout (top to bottom):**

1. **Section header:** "Which product categories drive demand in each region?"

2. **Stacked bar chart** — `plotly.express.bar` with `barmode='group'`:
   - X: category (consumer lending, short-term credit, revolving credit)
   - Y: avg interest_value
   - Color: category
   - Title: "Average Search Interest by Product Category"

3. **Top states per category table** — `st.dataframe`:
   - Columns: Category | Top State | Interest Score
   - 3 rows (one per category)
   - Shows the single highest-interest state for each category

4. **Insight callout box** — `st.info()` or styled `st.markdown()`:
   > "Short-term credit keywords (payday loans, cash advance) are concentrated in Mississippi and Louisiana — states with lower median incomes and fewer traditional banking options. This signals an underserved market where EPCVIP's lead generation services have strong demand potential."

**Data query:**
```sql
SELECT k.category, r.region, AVG(f.interest_value) as avg_interest
FROM analytics.fact_search_interest f
JOIN analytics.dim_keyword k ON f.keyword_id = k.keyword_id
JOIN analytics.dim_region r ON f.region_id = r.region_id
GROUP BY k.category, r.region
ORDER BY avg_interest DESC
```

---

## Tab 3 — Chat: "Ask the Knowledge Base"

**Purpose:** Let users query the 17 scraped industry articles using natural language. Demonstrates RAG pipeline.

**Layout:**

1. **Section header:** "Ask about the financial services lead gen industry"
2. **Subtitle:** "Powered by 17 scraped sources on EPCVIP, PPC strategy, and consumer lending trends"

3. **Suggested questions** — 3 `st.button()` elements that pre-fill the input:
   - "What is EPCVIP's business model?"
   - "How do PPC keywords work in financial services?"
   - "Who are EPCVIP's main competitors?"

4. **Text input** — `st.text_input()` for custom questions

5. **Answer display** — `st.markdown()` showing Claude's response after submit

**RAG logic (`dashboard/app.py`):**
```python
def retrieve_context(question: str, raw_dir: str, top_k: int = 3) -> str:
    """Simple keyword-based retrieval from knowledge/raw/ markdown files."""
    files = Path(raw_dir).glob("*.md")
    scores = []
    question_words = set(question.lower().split())
    for f in files:
        content = f.read_text()
        word_count = sum(1 for w in question_words if w in content.lower())
        scores.append((word_count, f.name, content))
    scores.sort(reverse=True)
    top = scores[:top_k]
    return "\n\n---\n\n".join(f"Source: {name}\n{content[:1500]}" for _, name, content in top)

def ask_claude(question: str, context: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"Based on these industry sources:\n\n{context}\n\nAnswer this question: {question}"
        }]
    )
    return message.content[0].text
```

**Notes:**
- Uses keyword overlap for retrieval (no embeddings needed — simple and fast)
- Uses `claude-haiku-4-5-20251001` (cheapest Claude model — keeps costs low)
- `knowledge/raw/` path is relative to repo root; use `Path(__file__).parent.parent / "knowledge" / "raw"`
- `ANTHROPIC_API_KEY` stored in `.env` locally and `.streamlit/secrets.toml` on Streamlit Cloud

---

## Streamlit Cloud Deployment

**Steps:**
1. Push `dashboard/app.py` to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → connect repo
3. Set main file: `dashboard/app.py`
4. Add secrets in Streamlit Cloud UI (all 7 Snowflake vars + `ANTHROPIC_API_KEY`)
5. Deploy → get public URL

**`.streamlit/secrets.toml` format** (gitignored, for local Streamlit testing):
```toml
SNOWFLAKE_ACCOUNT = "cec86794.us-east-1"
SNOWFLAKE_USER = "laurendlr"
SNOWFLAKE_PASSWORD = "..."
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_DATABASE = "junior_data_analyst"
SNOWFLAKE_WAREHOUSE = "junior_data_analyst_wh"
SNOWFLAKE_SCHEMA = "raw"
ANTHROPIC_API_KEY = "..."
```

In `app.py`, read credentials with:
```python
import streamlit as st
import os

# Works both locally (from .env) and on Streamlit Cloud (from secrets.toml)
SNOWFLAKE_ACCOUNT = st.secrets.get("SNOWFLAKE_ACCOUNT", os.environ.get("SNOWFLAKE_ACCOUNT"))
```

---

## Dependencies to Add to requirements.txt

```
streamlit
plotly
anthropic
```

(`snowflake-connector-python[pandas]` already present)

---

## Success Criteria

- [ ] `streamlit run dashboard/app.py` runs locally without errors
- [ ] Tab 1: map renders with state-level color, bar chart shows all 5 keywords
- [ ] Tab 2: category breakdown + insight callout visible
- [ ] Tab 3: suggested questions work, Claude returns an answer
- [ ] Deployed to Streamlit Community Cloud with public URL
- [ ] All Snowflake + Anthropic credentials in Streamlit Cloud secrets (not committed)
