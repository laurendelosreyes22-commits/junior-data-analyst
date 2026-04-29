import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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
    df = pd.read_sql(sql, conn)
    df.columns = df.columns.str.lower()
    return df

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

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Interest Score", f"{filtered['interest_value'].mean():.0f}")
    top_state = filtered.groupby("region")["interest_value"].mean().idxmax()
    col2.metric("Top State", top_state)
    top_kw = df.groupby("keyword")["interest_value"].mean().idxmax()
    col3.metric("Top Keyword", top_kw)

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
    event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points")

    if event and event.selection and event.selection.points:
        abbrev_to_state = {v: k for k, v in STATE_ABBREV.items()}
        clicked_code = event.selection.points[0].get("location")
        clicked_state = abbrev_to_state.get(clicked_code)
        if clicked_state:
            st.markdown(f"### {clicked_state} — Keyword Breakdown")
            state_df = (
                filtered[filtered["region"] == clicked_state][["keyword", "category", "interest_value"]]
                .sort_values("interest_value", ascending=False)
                .reset_index(drop=True)
            )
            st.dataframe(state_df, use_container_width=True, hide_index=True)

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
