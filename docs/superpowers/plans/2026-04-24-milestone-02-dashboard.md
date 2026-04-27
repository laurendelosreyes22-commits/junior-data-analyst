# Milestone 02 Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 3-tab Streamlit dashboard (descriptive + diagnostic + RAG chatbot) connected to Snowflake mart tables, deployed publicly on Streamlit Community Cloud.

**Architecture:** Single `dashboard/app.py` reads from Snowflake `analytics` schema via `snowflake.connector`. RAG logic lives in `dashboard/rag.py` (pure functions, unit-tested). The app reads credentials from `st.secrets` (Streamlit Cloud) falling back to environment variables (local). Deployed via Streamlit Community Cloud connected to the GitHub repo.

**Tech Stack:** streamlit, plotly, anthropic (claude-haiku-4-5-20251001), snowflake-connector-python[pandas], python-dotenv

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Modify | Add streamlit, plotly, anthropic |
| `.streamlit/secrets.toml` | Create (gitignored) | Local credentials for Streamlit |
| `.streamlit/secrets.toml.example` | Create | Template showing required keys |
| `dashboard/__init__.py` | Create | Makes dashboard a package (needed for imports) |
| `dashboard/rag.py` | Create | `retrieve_context()` and `ask_claude()` — pure functions |
| `dashboard/app.py` | Create | Full Streamlit app with 3 tabs |
| `tests/test_rag.py` | Create | Unit tests for RAG retrieval functions |

---

## Task 1: Dependencies + Streamlit Secrets Setup

**Files:**
- Modify: `requirements.txt`
- Create: `.streamlit/secrets.toml` (gitignored)
- Create: `.streamlit/secrets.toml.example`

- [ ] **Step 1: Add new packages to `requirements.txt`**

Replace contents of `requirements.txt` with:

```
pytrends
snowflake-connector-python[pandas]
python-dotenv
requests
pandas
pytest
dbt-core
dbt-snowflake
streamlit
plotly
anthropic
```

- [ ] **Step 2: Install new dependencies**

```bash
pip install streamlit plotly anthropic
```

Expected: installs without errors. Verify:
```bash
streamlit --version
python -c "import plotly; import anthropic; print('ok')"
```

- [ ] **Step 3: Create `.streamlit/` directory**

```bash
mkdir -p /Users/laurendelosreyes/isba-4715/junior-data-analyst/.streamlit
```

- [ ] **Step 4: Create `.streamlit/secrets.toml`**

This file is gitignored. Fill in your actual password and API key:

```toml
SNOWFLAKE_ACCOUNT = "cec86794.us-east-1"
SNOWFLAKE_USER = "laurendlr"
SNOWFLAKE_PASSWORD = "QxqhKMLW9bGjaeq"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_DATABASE = "junior_data_analyst"
SNOWFLAKE_WAREHOUSE = "junior_data_analyst_wh"
SNOWFLAKE_SCHEMA = "raw"
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
```

- [ ] **Step 5: Create `.streamlit/secrets.toml.example`**

```toml
SNOWFLAKE_ACCOUNT = ""
SNOWFLAKE_USER = ""
SNOWFLAKE_PASSWORD = ""
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_DATABASE = "junior_data_analyst"
SNOWFLAKE_WAREHOUSE = "junior_data_analyst_wh"
SNOWFLAKE_SCHEMA = "raw"
ANTHROPIC_API_KEY = ""
```

- [ ] **Step 6: Add `.streamlit/secrets.toml` to `.gitignore`**

Append to `.gitignore`:
```
.streamlit/secrets.toml
```

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .streamlit/secrets.toml.example .gitignore
git commit -m "Add Streamlit + plotly + anthropic dependencies"
```

---

## Task 2: RAG Module + Tests

**Files:**
- Create: `dashboard/__init__.py`
- Create: `dashboard/rag.py`
- Create: `tests/test_rag.py`

- [ ] **Step 1: Create `dashboard/__init__.py`**

Empty file — makes `dashboard` importable as a package:
```python
```

- [ ] **Step 2: Write failing tests in `tests/test_rag.py`**

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from dashboard.rag import retrieve_context, ask_claude


def test_retrieve_context_returns_top_k():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "01-epcvip.md").write_text("EPCVIP personal loans lead generation")
        (Path(tmpdir) / "02-ppc.md").write_text("PPC advertising keywords strategy")
        (Path(tmpdir) / "03-lending.md").write_text("consumer lending market trends")
        result = retrieve_context("EPCVIP loans", tmpdir, top_k=2)
    assert result.count("Source:") == 2


def test_retrieve_context_ranks_by_keyword_overlap():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "a.md").write_text("payday loans cash advance Mississippi")
        (Path(tmpdir) / "b.md").write_text("credit cards unrelated content here")
        result = retrieve_context("payday loans cash advance", tmpdir, top_k=1)
    assert "payday loans" in result


def test_ask_claude_returns_text():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="EPCVIP is a lead gen company.")]
    with patch("dashboard.rag.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = mock_response
        result = ask_claude("What is EPCVIP?", "context text", "fake-key")
    assert result == "EPCVIP is a lead gen company."
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
python -m pytest tests/test_rag.py -v
```

Expected: `ImportError` — `dashboard.rag` does not exist yet.

- [ ] **Step 4: Create `dashboard/rag.py`**

```python
from pathlib import Path
import anthropic


def retrieve_context(question: str, raw_dir: str, top_k: int = 3) -> str:
    """Search knowledge/raw/ markdown files and return top_k most relevant."""
    files = list(Path(raw_dir).glob("*.md"))
    question_words = set(question.lower().split())
    scores = []
    for f in files:
        content = f.read_text(encoding="utf-8")
        score = sum(1 for w in question_words if w in content.lower())
        scores.append((score, f.name, content))
    scores.sort(reverse=True)
    top = scores[:top_k]
    return "\n\n---\n\n".join(
        f"Source: {name}\n{content[:1500]}" for _, name, content in top
    )


def ask_claude(question: str, context: str, api_key: str) -> str:
    """Send question + retrieved context to Claude and return the answer."""
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                f"Based on these industry sources:\n\n{context}\n\n"
                f"Answer this question concisely: {question}"
            ),
        }],
    )
    return message.content[0].text
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
python -m pytest tests/test_rag.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 6: Confirm all 9 tests still pass**

```bash
python -m pytest tests/ -v
```

Expected: 9 passed.

- [ ] **Step 7: Commit**

```bash
git add dashboard/__init__.py dashboard/rag.py tests/test_rag.py
git commit -m "Add RAG retrieval module and unit tests"
```

---

## Task 3: Streamlit App — Skeleton + Tab 1 (Descriptive)

**Files:**
- Create: `dashboard/app.py`

- [ ] **Step 1: Create `dashboard/app.py`** with the full app including Tab 1:

```python
import os
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector

from dashboard.rag import retrieve_context, ask_claude

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Keyword Intelligence",
    page_icon="📊",
    layout="wide",
)

# ── US state name → 2-letter abbreviation ────────────────────────────────────
STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
}

CATEGORY_COLORS = {
    "consumer lending": "#4f46e5",
    "short-term credit": "#7c3aed",
    "revolving credit": "#a855f7",
}

# ── Credentials helper ────────────────────────────────────────────────────────
def get_secret(key: str) -> str:
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

# ── Snowflake connection (cached across sessions) ─────────────────────────────
@st.cache_resource
def get_conn():
    return snowflake.connector.connect(
        account=get_secret("SNOWFLAKE_ACCOUNT"),
        user=get_secret("SNOWFLAKE_USER"),
        password=get_secret("SNOWFLAKE_PASSWORD"),
        role=get_secret("SNOWFLAKE_ROLE"),
        database=get_secret("SNOWFLAKE_DATABASE"),
        warehouse=get_secret("SNOWFLAKE_WAREHOUSE"),
        schema="analytics",
    )

# ── Data loading (cached so Snowflake is only queried once per session) ───────
@st.cache_data
def load_data() -> pd.DataFrame:
    conn = get_conn()
    sql = """
        SELECT k.keyword, k.category, r.region, f.interest_value
        FROM junior_data_analyst.analytics.fact_search_interest f
        JOIN junior_data_analyst.analytics.dim_keyword k ON f.keyword_id = k.keyword_id
        JOIN junior_data_analyst.analytics.dim_region r ON f.region_id = r.region_id
    """
    return pd.read_sql(sql, conn)

# ── App header ────────────────────────────────────────────────────────────────
st.title("📊 Financial Services Keyword Demand Intelligence")
st.caption(
    "Google Trends search interest for financial product keywords across US states — "
    "the same signals a PPC analyst at EPCVIP monitors to optimize ad spend."
)

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()
df["state_code"] = df["region"].map(STATE_ABBREV)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Descriptive", "🔍 Diagnostic", "💬 Ask the Knowledge Base"])

# ── TAB 1: DESCRIPTIVE ────────────────────────────────────────────────────────
with tab1:
    st.subheader("What happened? Search demand by keyword and state")

    keyword_options = ["All"] + sorted(df["keyword"].unique().tolist())
    selected = st.selectbox("Filter by keyword", keyword_options)

    filtered = df if selected == "All" else df[df["keyword"] == selected]

    # KPI cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Interest Score", f"{filtered['interest_value'].mean():.0f}")
    top_state = filtered.groupby("region")["interest_value"].mean().idxmax()
    col2.metric("Top State", top_state)
    top_kw = df.groupby("keyword")["interest_value"].mean().idxmax()
    col3.metric("Top Keyword", top_kw)

    # Choropleth map
    map_df = (
        filtered.groupby(["region", "state_code"])["interest_value"]
        .mean()
        .reset_index()
    )
    fig_map = px.choropleth(
        map_df,
        locations="state_code",
        locationmode="USA-states",
        color="interest_value",
        scope="usa",
        color_continuous_scale="Blues",
        title="Average Search Interest by State",
        labels={"interest_value": "Avg Interest"},
    )
    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

    # Bar chart (only when showing all keywords)
    if selected == "All":
        bar_df = (
            df.groupby(["keyword", "category"])["interest_value"]
            .mean()
            .reset_index()
        )
        fig_bar = px.bar(
            bar_df,
            x="keyword",
            y="interest_value",
            color="category",
            title="Average Search Interest by Keyword",
            labels={"interest_value": "Avg Interest", "keyword": "Keyword"},
            color_discrete_map=CATEGORY_COLORS,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ── TAB 2: DIAGNOSTIC ────────────────────────────────────────────────────────
with tab2:
    st.subheader("Why did it happen? Category and geographic patterns")

    cat_df = df.groupby("category")["interest_value"].mean().reset_index()
    fig_cat = px.bar(
        cat_df,
        x="category",
        y="interest_value",
        color="category",
        title="Average Search Interest by Product Category",
        labels={"interest_value": "Avg Interest", "category": "Category"},
        color_discrete_map=CATEGORY_COLORS,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("**Top state per category**")
    top_states = (
        df.groupby(["category", "region"])["interest_value"]
        .mean()
        .reset_index()
        .sort_values("interest_value", ascending=False)
        .groupby("category")
        .first()
        .reset_index()[["category", "region", "interest_value"]]
        .rename(columns={"region": "Top State", "interest_value": "Avg Interest"})
    )
    top_states["Avg Interest"] = top_states["Avg Interest"].round(1)
    st.dataframe(top_states, use_container_width=True, hide_index=True)

    st.info(
        "**Insight:** Short-term credit keywords (payday loans, cash advance) are "
        "concentrated in Mississippi and Louisiana — states with lower median incomes "
        "and fewer traditional banking options. This signals an underserved market where "
        "EPCVIP's lead generation services have strong demand potential."
    )

# ── TAB 3: CHAT ──────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Ask about the financial services lead gen industry")
    st.caption(
        "Powered by 17 scraped sources on EPCVIP, PPC strategy, and consumer lending trends"
    )

    RAW_DIR = str(Path(__file__).parent.parent / "knowledge" / "raw")

    SUGGESTED = [
        "What is EPCVIP's business model?",
        "How do PPC keywords work in financial services?",
        "Who are EPCVIP's main competitors?",
    ]

    if "question" not in st.session_state:
        st.session_state.question = ""

    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED):
        if cols[i].button(q, use_container_width=True):
            st.session_state.question = q

    question = st.text_input("Or ask your own question:", value=st.session_state.question)

    if question:
        with st.spinner("Searching knowledge base and generating answer..."):
            context = retrieve_context(question, RAW_DIR, top_k=3)
            api_key = get_secret("ANTHROPIC_API_KEY")
            answer = ask_claude(question, context, api_key)
        st.markdown(answer)
```

- [ ] **Step 2: Run the app locally**

```bash
cd /Users/laurendelosreyes/isba-4715/junior-data-analyst
streamlit run dashboard/app.py
```

Expected: browser opens at `http://localhost:8501`. Verify:
- Tab 1 loads with KPI cards, map, and bar chart
- Keyword dropdown filters the map
- Tab 2 shows category bar chart, top states table, and insight box
- Tab 3 shows 3 suggested question buttons and a text input

- [ ] **Step 3: Test the chatbot tab**

Click "What is EPCVIP's business model?" — expected: answer appears within a few seconds referencing EPCVIP content.

Note: if `ANTHROPIC_API_KEY` is not set, the chat tab will error. Make sure `.streamlit/secrets.toml` has your API key filled in.

- [ ] **Step 4: Commit**

```bash
git add dashboard/app.py
git commit -m "Add Streamlit dashboard with 3 tabs: descriptive, diagnostic, RAG chat"
```

---

## Task 4: Deploy to Streamlit Community Cloud

**Files:** None new — deploying existing `dashboard/app.py`

- [ ] **Step 1: Push all changes to GitHub**

```bash
git push origin main
```

- [ ] **Step 2: Sign up / log in to Streamlit Community Cloud**

Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account (`laurendelosreyes22-commits`).

- [ ] **Step 3: Create a new app**

Click **New app** and fill in:
- Repository: `laurendelosreyes22-commits/junior-data-analyst`
- Branch: `main`
- Main file path: `dashboard/app.py`

- [ ] **Step 4: Add secrets in Streamlit Cloud**

Before clicking Deploy, click **Advanced settings** → **Secrets**. Paste:

```toml
SNOWFLAKE_ACCOUNT = "cec86794.us-east-1"
SNOWFLAKE_USER = "laurendlr"
SNOWFLAKE_PASSWORD = "QxqhKMLW9bGjaeq"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_DATABASE = "junior_data_analyst"
SNOWFLAKE_WAREHOUSE = "junior_data_analyst_wh"
SNOWFLAKE_SCHEMA = "raw"
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
```

Replace `ANTHROPIC_API_KEY` with your actual key.

- [ ] **Step 5: Deploy and get public URL**

Click **Deploy**. Wait ~2 minutes for the build. You'll get a public URL like:
```
https://laurendelosreyes22-commits-junior-data-analyst-dashboard-app-xxxxx.streamlit.app
```

- [ ] **Step 6: Verify the deployed app**

Open the public URL. Confirm all 3 tabs work. Take a screenshot for the README.

- [ ] **Step 7: Commit the public URL**

Add the URL to `README.md` under the Live Dashboard section (you'll do this in the README task). For now, just note it down.

---

## Completion Checklist

- [ ] `requirements.txt` includes `streamlit`, `plotly`, `anthropic`
- [ ] `.streamlit/secrets.toml` exists locally (gitignored) with all 8 credentials
- [ ] `dashboard/rag.py` has `retrieve_context()` and `ask_claude()`
- [ ] All 9 Python unit tests pass (`pytest tests/ -v`)
- [ ] `streamlit run dashboard/app.py` runs locally with all 3 tabs working
- [ ] Chatbot returns answers using the `knowledge/raw/` files
- [ ] App deployed to Streamlit Community Cloud with a public URL
- [ ] No credentials committed to the repo
