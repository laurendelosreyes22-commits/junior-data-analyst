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
st.title("Financial Keyword Intelligence Dashboard")
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

    with st.expander("ℹ️ How to read this dashboard"):
        st.markdown("""
**Interest Score (0–100):** Pulled from Google Trends. A score of 100 means peak search popularity for that keyword in that location. It's a relative measure — not raw search volume, but how much interest there is compared to the highest point in the data.

**Keyword definitions:**
| Keyword | Category | What it means |
|---|---|---|
| Personal loans | Consumer lending | Fixed-amount loans repaid over months/years — used for big purchases or debt consolidation |
| Installment loans | Consumer lending | Similar to personal loans — repaid in fixed monthly installments |
| Credit cards | Revolving credit | Revolving lines of credit — borrow, repay, borrow again |
| Payday loans | Short-term credit | Small, short-term loans due on your next paycheck — typically high interest |
| Cash advance | Short-term credit | Borrowing against a credit card or paycheck before payday |
        """)

    keyword_options = ["All"] + sorted(df["keyword"].unique().tolist())
    selected = st.selectbox("Filter by keyword", keyword_options)

    filtered = df if selected == "All" else df[df["keyword"] == selected]

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
        title="Average Search Interest by State — click a state to explore",
        labels={"interest_value": "Avg Interest"},
    )
    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points")

    # Determine if a state is clicked
    clicked_state = None
    if event and event.selection and event.selection.points:
        abbrev_to_state = {v: k for k, v in STATE_ABBREV.items()}
        clicked_code = event.selection.points[0].get("location")
        clicked_state = abbrev_to_state.get(clicked_code)

    # KPIs update based on clicked state or overall
    kpi_data = filtered[filtered["region"] == clicked_state] if clicked_state else filtered
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Interest Score", f"{kpi_data['interest_value'].mean():.0f}")
    col2.metric("Selected State" if clicked_state else "Top State",
                clicked_state if clicked_state else filtered.groupby("region")["interest_value"].mean().idxmax())
    col3.metric("Top Keyword", kpi_data.groupby("keyword")["interest_value"].mean().idxmax())

    # Download button for full filtered dataset
    st.download_button(
        label="Download data as CSV",
        data=filtered.to_csv(index=False),
        file_name=f"keyword_interest_{selected.replace(' ', '_')}.csv",
        mime="text/csv",
    )

    if clicked_state:
        st.markdown(f"#### {clicked_state} — Keyword Breakdown")
        state_df = (
            kpi_data[["keyword", "category", "interest_value"]]
            .sort_values("interest_value", ascending=False)
            .reset_index(drop=True)
        )
        st.dataframe(state_df, use_container_width=True, hide_index=True)


# ── TAB 2: DIAGNOSTIC ────────────────────────────────────────────────────────
with tab2:
    st.subheader("Which financial products drive the most search demand?")
    st.caption("Averaged across all US states. Higher score = more Google searches.")

    with st.expander("ℹ️ How to read this tab"):
        st.markdown("""
**What this tab shows:** Instead of individual keywords, this groups them into 3 product categories and compares which category gets the most search interest nationally.

**The 3 categories:**
- **Revolving credit** — Credit cards. People can borrow, repay, and borrow again up to a limit.
- **Short-term credit** — Payday loans and cash advances. Small amounts borrowed for a short time, usually at high interest rates.
- **Consumer lending** — Personal loans and installment loans. Larger amounts repaid in fixed monthly payments over time.

**What the score means:** Same 0–100 Google Trends scale as Tab 1, but averaged across all keywords in that category and all US states. So if revolving credit scores 42, that means credit card searches are at 42% of their peak popularity on average across the country.

**Why this matters:** EPCVIP generates leads for lenders in all three categories. Knowing which category has the highest demand nationally — and which states lead each category — helps decide where to focus ad spend.
        """)


    cat_df = df.groupby("category")["interest_value"].mean().reset_index().sort_values("interest_value", ascending=False)
    cat_df.columns = ["Category", "Avg Interest Score"]
    cat_df["Avg Interest Score"] = cat_df["Avg Interest Score"].round(1)

    fig_cat = px.bar(
        cat_df,
        x="Category",
        y="Avg Interest Score",
        color="Category",
        text="Avg Interest Score",
        color_discrete_map=CATEGORY_COLORS,
    )
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(showlegend=False, xaxis_title="", yaxis_title="Avg Google Trends Score (0–100)")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("#### Which state leads each category?")
    st.caption("The single highest-demand state for each product type.")
    top_states = (
        df.groupby(["category", "region"])["interest_value"]
        .mean()
        .reset_index()
        .sort_values("interest_value", ascending=False)
        .groupby("category")
        .first()
        .reset_index()[["category", "region", "interest_value"]]
        .rename(columns={"category": "Product Category", "region": "Top State", "interest_value": "Avg Interest Score"})
    )
    top_states["Avg Interest Score"] = top_states["Avg Interest Score"].round(1)
    st.dataframe(top_states, use_container_width=True, hide_index=True)

    st.info(
        "**Insight:** Short-term credit keywords (payday loans, cash advance) are "
        "concentrated in Mississippi and Louisiana — states with lower median incomes "
        "and fewer traditional banking options. This signals an underserved market where "
        "EPCVIP's lead generation services have strong demand potential."
    )

# ── TAB 3: CHAT ──────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Ask the Knowledge Base")
    st.caption("Ask anything about EPCVIP, financial services, or the lead gen industry.")

    with st.expander("ℹ️ How this works"):
        st.markdown("""
This knowledge base was built from 17 scraped articles and reports about EPCVIP, PPC advertising, consumer lending trends, and competitor companies (LendingTree, QuinStreet, MoneyMutual).

Click any topic below to read a synthesized summary. These pages were generated by Claude Code from the raw sources — not copy-pasted, but distilled into key insights.
        """)

    WIKI_DIR = Path(__file__).parent.parent / "knowledge" / "wiki"

    WIKI_PAGES = [
        ("01-epcvip-overview.md", "🏢 EPCVIP Overview", "What EPCVIP does, their business model, and key differentiators"),
        ("02-competitor-landscape.md", "⚔️ Competitor Landscape", "LendingTree, QuinStreet, MoneyMutual — how they compare"),
        ("03-ppc-keyword-strategy.md", "🎯 PPC Keyword Strategy", "How PPC advertising works in financial services"),
        ("04-consumer-lending-trends.md", "📈 Consumer Lending Trends", "2025–2026 market trends and geographic demand patterns"),
    ]

    for filename, title, description in WIKI_PAGES:
        filepath = WIKI_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            with st.expander(f"{title} — {description}"):
                st.markdown(content)

    st.divider()
    st.markdown("#### 💬 Ask a question")
    st.caption("Claude will search the knowledge base and answer based on the scraped sources.")

    RAW_DIR = str(Path(__file__).parent.parent / "knowledge" / "raw")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("e.g. What is EPCVIP's business model?"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                context = retrieve_context(prompt, RAW_DIR, top_k=3)
                answer = ask_claude(prompt, context, api_key=get_secret("ANTHROPIC_API_KEY"))
            st.markdown(answer)

        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
