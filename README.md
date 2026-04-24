# Financial Services Keyword Demand Intelligence

Track Google Trends search demand for financial product keywords (personal loans, payday loans, credit cards) — the same signals a PPC analyst at EPCVIP monitors to optimize ad spend.

**Course:** ISBA 4715 — Analytics Engineering | **Student:** Lauren De Los Reyes

## Pipeline

```
pytrends API
     │
     ▼
GitHub Actions (daily 9am UTC)
     │
     ▼
Snowflake: raw.GOOGLE_TRENDS_RAW (255 rows per run)
     │
     ▼
dbt: stg_google_trends_raw (staging view)
     │
     ├── dim_keyword     (5 keywords × category)
     ├── dim_region      (50 US states)
     ├── dim_date        (one row per week)
     └── fact_search_interest  (keyword × region × week)
     │
     ▼
Streamlit Dashboard (Milestone 02)
```

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt |
| Orchestration | GitHub Actions (daily schedule) |
| Dashboard | Streamlit (coming in Milestone 02) |
| API Source | pytrends (Google Trends) |
| Web Scrape | Firecrawl |

## Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy .env.example to .env and fill in your Snowflake credentials
cp .env.example .env

# 3. Pull Google Trends data into Snowflake raw
python extract/load_google_trends.py

# 4. Run dbt to build the star schema
cd dbt && dbt run --profiles-dir .
```

## Run Tests

```bash
# Python unit tests
pytest tests/ -v

# dbt data tests
cd dbt && dbt test --profiles-dir .
```
