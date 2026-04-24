# Milestone 01 Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions scheduling, a dbt star schema, and a README to complete the Milestone 01 submission.

**Architecture:** GitHub Actions runs the pytrends script daily and loads raw data to Snowflake. dbt reads from `raw.google_trends_raw`, builds a staging view, then materializes four tables (three dims + one fact) in the `analytics` schema. README documents the pipeline with an ASCII diagram.

**Tech Stack:** dbt-core, dbt-snowflake, GitHub Actions, Snowflake, Python 3.11

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Modify | Add `dbt-core` and `dbt-snowflake` |
| `setup/snowflake_setup.sql` | Modify | Add `CREATE SCHEMA analytics` |
| `.github/workflows/load_google_trends.yml` | Create | Scheduled daily extraction |
| `dbt/dbt_project.yml` | Create | dbt project config |
| `dbt/profiles.yml` | Create | Snowflake connection via env vars (safe to commit) |
| `dbt/models/staging/_sources.yml` | Create | Declare `raw.google_trends_raw` as dbt source |
| `dbt/models/staging/stg_google_trends_raw.sql` | Create | Clean raw data — no joins, no filters |
| `dbt/models/marts/dim_keyword.sql` | Create | One row per keyword with category |
| `dbt/models/marts/dim_region.sql` | Create | One row per US state |
| `dbt/models/marts/dim_date.sql` | Create | One row per week_start date |
| `dbt/models/marts/fact_search_interest.sql` | Create | Grain: keyword × region × week |
| `dbt/models/marts/_schema.yml` | Create | dbt tests for mart models |
| `README.md` | Create | Pipeline diagram + how to run |

---

## Task 1: Add dbt Dependencies + Analytics Schema

**Files:**
- Modify: `requirements.txt`
- Modify: `setup/snowflake_setup.sql`

- [ ] **Step 1: Add dbt packages to `requirements.txt`**

Replace the contents of `requirements.txt` with:

```
pytrends
snowflake-connector-python
python-dotenv
requests
pandas
pytest
dbt-core
dbt-snowflake
```

- [ ] **Step 2: Install updated dependencies**

```bash
pip install -r requirements.txt
```

Expected: installs `dbt-core` and `dbt-snowflake` without errors. You should see `dbt` available:

```bash
dbt --version
```

Expected output contains: `Core: 1.x.x`

- [ ] **Step 3: Add analytics schema to Snowflake setup SQL**

Open `setup/snowflake_setup.sql` and append at the bottom:

```sql
-- Analytics schema (dbt writes here)
CREATE SCHEMA IF NOT EXISTS junior_data_analyst.analytics;
```

- [ ] **Step 4: Run the analytics schema creation in Snowflake**

Go to [app.snowflake.com](https://app.snowflake.com/us-east-1/cec86794/#/homepage) → Worksheets. Run:

```sql
CREATE SCHEMA IF NOT EXISTS junior_data_analyst.analytics;
```

Expected: no error. You should see `ANALYTICS` under `junior_data_analyst` in the left sidebar.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt setup/snowflake_setup.sql
git commit -m "Add dbt dependencies and analytics schema"
```

---

## Task 2: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/load_google_trends.yml`

- [ ] **Step 1: Create the workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create `.github/workflows/load_google_trends.yml`**

```yaml
name: Load Google Trends to Snowflake

on:
  schedule:
    - cron: '0 9 * * *'
  push:
    branches: [main]

jobs:
  load:
    runs-on: ubuntu-latest

    env:
      SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
      SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
      SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
      SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
      SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
      SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
      SNOWFLAKE_SCHEMA: ${{ secrets.SNOWFLAKE_SCHEMA }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run extraction
        run: python extract/load_google_trends.py
```

- [ ] **Step 3: Add GitHub Secrets**

Go to your repo on GitHub → Settings → Secrets and variables → Actions → New repository secret.

Add each of these (copy values from your `.env` file):

| Secret Name | Value from .env |
|---|---|
| `SNOWFLAKE_ACCOUNT` | `cec86794.us-east-1` |
| `SNOWFLAKE_USER` | your username |
| `SNOWFLAKE_PASSWORD` | your password |
| `SNOWFLAKE_ROLE` | `ACCOUNTADMIN` |
| `SNOWFLAKE_DATABASE` | `junior_data_analyst` |
| `SNOWFLAKE_WAREHOUSE` | `junior_data_analyst_wh` |
| `SNOWFLAKE_SCHEMA` | `raw` |

- [ ] **Step 4: Commit and push**

```bash
git add .github/workflows/load_google_trends.yml
git commit -m "Add GitHub Actions workflow for daily Google Trends extraction"
git push origin main
```

- [ ] **Step 5: Verify the workflow ran**

Go to your repo on GitHub → Actions tab. You should see a workflow run triggered by the push to main. Click it and confirm the `Run extraction` step shows:

```
Extracted 255 rows
Loaded 255 rows to GOOGLE_TRENDS_RAW
```

---

## Task 3: dbt Project Setup

**Files:**
- Create: `dbt/dbt_project.yml`
- Create: `dbt/profiles.yml`
- Create: `dbt/models/staging/` (directory)
- Create: `dbt/models/marts/` (directory)

- [ ] **Step 1: Create the dbt directory structure**

```bash
mkdir -p dbt/models/staging dbt/models/marts
```

- [ ] **Step 2: Create `dbt/dbt_project.yml`**

```yaml
name: 'junior_data_analyst'
version: '1.0.0'
config-version: 2

profile: 'junior_data_analyst'

model-paths: ["models"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  junior_data_analyst:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

- [ ] **Step 3: Create `dbt/profiles.yml`**

This file uses `env_var()` — no actual credentials. Safe to commit.

```yaml
junior_data_analyst:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('SNOWFLAKE_ROLE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      schema: analytics
      threads: 4
```

- [ ] **Step 4: Test the connection**

```bash
cd dbt
dbt debug --profiles-dir .
```

Expected: all checks show `OK`. The last line should be:
```
All checks passed!
```

If you see a connection error, double-check your `.env` values match Snowflake.

- [ ] **Step 5: Commit**

```bash
cd ..
git add dbt/dbt_project.yml dbt/profiles.yml
git commit -m "Add dbt project config and Snowflake profiles"
```

---

## Task 4: dbt Staging Model

**Files:**
- Create: `dbt/models/staging/_sources.yml`
- Create: `dbt/models/staging/stg_google_trends_raw.sql`

- [ ] **Step 1: Create `dbt/models/staging/_sources.yml`**

This tells dbt where the raw data lives in Snowflake.

```yaml
version: 2

sources:
  - name: raw
    database: junior_data_analyst
    schema: raw
    tables:
      - name: google_trends_raw
```

- [ ] **Step 2: Create `dbt/models/staging/stg_google_trends_raw.sql`**

One staging model per raw table. No joins, no filters, no aggregations — just clean column names and correct types.

```sql
select
    keyword,
    region,
    week_start::date   as week_start,
    interest_value::integer as interest_value,
    loaded_at
from {{ source('raw', 'google_trends_raw') }}
```

- [ ] **Step 3: Run the staging model**

```bash
cd dbt
dbt run --select stg_google_trends_raw --profiles-dir .
```

Expected:
```
1 of 1 START sql view model analytics.stg_google_trends_raw ........ [RUN]
1 of 1 OK created sql view model analytics.stg_google_trends_raw ... [SUCCESS]
```

- [ ] **Step 4: Verify the view exists in Snowflake**

In the Snowflake worksheet:
```sql
SELECT * FROM junior_data_analyst.analytics.stg_google_trends_raw LIMIT 5;
```

Expected: 5 rows with `keyword`, `region`, `week_start`, `interest_value` columns.

- [ ] **Step 5: Commit**

```bash
cd ..
git add dbt/models/staging/
git commit -m "Add dbt staging model for google_trends_raw"
```

---

## Task 5: dbt Dimension Models

**Files:**
- Create: `dbt/models/marts/dim_keyword.sql`
- Create: `dbt/models/marts/dim_region.sql`
- Create: `dbt/models/marts/dim_date.sql`

- [ ] **Step 1: Create `dbt/models/marts/dim_keyword.sql`**

One row per keyword. Surrogate key via `md5()`. Category derived from keyword name.

```sql
{{ config(materialized='table') }}

select
    md5(keyword)  as keyword_id,
    keyword,
    case keyword
        when 'personal loans'    then 'consumer lending'
        when 'installment loans' then 'consumer lending'
        when 'payday loans'      then 'short-term credit'
        when 'cash advance'      then 'short-term credit'
        when 'credit cards'      then 'revolving credit'
        else 'other'
    end as category
from (
    select distinct keyword
    from {{ ref('stg_google_trends_raw') }}
)
```

- [ ] **Step 2: Create `dbt/models/marts/dim_region.sql`**

One row per US state.

```sql
{{ config(materialized='table') }}

select
    md5(region) as region_id,
    region
from (
    select distinct region
    from {{ ref('stg_google_trends_raw') }}
)
```

- [ ] **Step 3: Create `dbt/models/marts/dim_date.sql`**

One row per unique week_start date, with calendar attributes.

```sql
{{ config(materialized='table') }}

select
    md5(cast(week_start as varchar)) as date_id,
    week_start,
    month(week_start)    as month,
    year(week_start)     as year,
    quarter(week_start)  as quarter
from (
    select distinct week_start
    from {{ ref('stg_google_trends_raw') }}
)
```

- [ ] **Step 4: Run the dimension models**

```bash
cd dbt
dbt run --select dim_keyword dim_region dim_date --profiles-dir .
```

Expected:
```
3 of 3 OK ...
```

- [ ] **Step 5: Spot-check in Snowflake**

```sql
SELECT * FROM junior_data_analyst.analytics.dim_keyword;
```

Expected: 5 rows — one per keyword — with `keyword_id`, `keyword`, `category` columns.

```sql
SELECT * FROM junior_data_analyst.analytics.dim_date;
```

Expected: 1 row (all 255 raw rows share today's date as `week_start`).

- [ ] **Step 6: Commit**

```bash
cd ..
git add dbt/models/marts/dim_keyword.sql dbt/models/marts/dim_region.sql dbt/models/marts/dim_date.sql
git commit -m "Add dbt dimension models: dim_keyword, dim_region, dim_date"
```

---

## Task 6: dbt Fact Model + Schema Tests

**Files:**
- Create: `dbt/models/marts/fact_search_interest.sql`
- Create: `dbt/models/marts/_schema.yml`

- [ ] **Step 1: Create `dbt/models/marts/fact_search_interest.sql`**

Grain: one row per keyword × region × week. Joins all three dims on natural keys.

```sql
{{ config(materialized='table') }}

select
    dk.keyword_id,
    dr.region_id,
    dd.date_id,
    s.interest_value
from {{ ref('stg_google_trends_raw') }}   s
join {{ ref('dim_keyword') }}             dk on s.keyword    = dk.keyword
join {{ ref('dim_region') }}              dr on s.region     = dr.region
join {{ ref('dim_date') }}                dd on s.week_start = dd.week_start
```

- [ ] **Step 2: Run the fact model**

```bash
cd dbt
dbt run --select fact_search_interest --profiles-dir .
```

Expected:
```
1 of 1 OK created sql table model analytics.fact_search_interest ... [SUCCESS]
```

- [ ] **Step 3: Verify row count in Snowflake**

```sql
SELECT count(*) FROM junior_data_analyst.analytics.fact_search_interest;
```

Expected: 255 (same row count as raw table).

- [ ] **Step 4: Create `dbt/models/marts/_schema.yml`**

Declares tests that dbt runs with `dbt test`.

```yaml
version: 2

models:
  - name: dim_keyword
    description: "One row per tracked financial keyword."
    columns:
      - name: keyword_id
        tests:
          - unique
          - not_null
      - name: keyword
        tests:
          - unique
          - not_null

  - name: dim_region
    description: "One row per US state."
    columns:
      - name: region_id
        tests:
          - unique
          - not_null
      - name: region
        tests:
          - unique
          - not_null

  - name: dim_date
    description: "One row per unique week_start date."
    columns:
      - name: date_id
        tests:
          - unique
          - not_null

  - name: fact_search_interest
    description: "One row per keyword x region x week. Grain: search interest score."
    columns:
      - name: keyword_id
        tests:
          - not_null
      - name: region_id
        tests:
          - not_null
      - name: date_id
        tests:
          - not_null
      - name: interest_value
        tests:
          - not_null
```

- [ ] **Step 5: Run dbt test**

```bash
dbt test --profiles-dir .
```

Expected:
```
All N tests passed.
```

- [ ] **Step 6: Run the full dbt pipeline from scratch to confirm end-to-end**

```bash
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Both should complete with 0 errors.

- [ ] **Step 7: Commit**

```bash
cd ..
git add dbt/models/marts/fact_search_interest.sql dbt/models/marts/_schema.yml
git commit -m "Add fact_search_interest and dbt schema tests"
```

---

## Task 7: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md` at the repo root**

```markdown
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
```

- [ ] **Step 2: Commit and push everything**

```bash
git add README.md
git commit -m "Add README with pipeline diagram"
git push origin main
```

---

## Milestone 01 Completion Checklist

- [ ] `requirements.txt` includes `dbt-core` and `dbt-snowflake`
- [ ] `.github/workflows/load_google_trends.yml` committed and visible in Actions tab
- [ ] GitHub Secrets set for all 7 Snowflake environment variables
- [ ] Actions run shows successful extraction on push to main
- [ ] `dbt/dbt_project.yml` and `dbt/profiles.yml` committed
- [ ] `dbt run --profiles-dir .` completes with 0 errors (run from `dbt/` directory)
- [ ] `dbt test --profiles-dir .` passes all tests
- [ ] 4 tables exist in `junior_data_analyst.analytics`: `stg_google_trends_raw` (view), `dim_keyword`, `dim_region`, `dim_date`, `fact_search_interest`
- [ ] `README.md` committed with ASCII pipeline diagram
- [ ] All 6 Python unit tests still pass (`pytest tests/ -v`)
- [ ] Changes pushed to `main` on GitHub
