# Milestone 01 Pipeline Design Spec
**Date:** 2026-04-24
**Topic:** GitHub Actions + dbt Star Schema + README

---

## Overview

Three deliverables needed to complete Milestone 01 submission:
1. GitHub Actions workflow scheduling the pytrends extraction daily
2. dbt project transforming raw Snowflake data into a star schema
3. README with data pipeline diagram

**Due:** April 27 at 9:55 AM

---

## Part 1: GitHub Actions Workflow

**File:** `.github/workflows/load_google_trends.yml`

**Triggers:**
- Scheduled daily at 9am UTC (`cron: '0 9 * * *'`)
- On push to `main` (so it can be tested by pushing)

**Steps:**
1. Checkout repo
2. Set up Python 3.11
3. `pip install -r requirements.txt`
4. Run `python extract/load_google_trends.py`

**Credentials:** All 7 Snowflake env vars stored as GitHub repository secrets (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_SCHEMA`). Injected into the runner environment via `env:` block — never hardcoded.

---

## Part 2: dbt Project

Follows the mp02 tutorial pattern exactly. Project name: `junior_data_analyst`.

### Directory Structure

```
dbt/
├── dbt_project.yml
├── profiles.yml          (committed with env_var() — no secrets)
├── models/
│   ├── staging/
│   │   ├── _sources.yml
│   │   └── stg_google_trends_raw.sql
│   └── marts/
│       ├── _schema.yml
│       ├── dim_keyword.sql
│       ├── dim_region.sql
│       ├── dim_date.sql
│       └── fact_search_interest.sql
```

### Staging Layer

`stg_google_trends_raw.sql` — one model per raw table, no joins, no filters:
- Reads from `{{ source('raw', 'google_trends_raw') }}`
- Renames columns to snake_case, casts types
- Outputs: `keyword`, `region`, `week_start`, `interest_value`, `loaded_at`

`_sources.yml` declares the upstream raw table in Snowflake.

### Marts Layer — Star Schema

All mart models use `{{ config(materialized='table') }}` and reference staging via `{{ ref() }}`.

**`dim_keyword`** — one row per unique keyword:
- `keyword_id` (surrogate key via `row_number()`)
- `keyword` (e.g. "personal loans")
- `category` (derived: "consumer lending" / "credit" / "cash")

**`dim_region`** — one row per US state:
- `region_id` (surrogate key)
- `region` (state name)

**`dim_date`** — one row per unique date:
- `date_id` (surrogate key)
- `week_start`
- `month`, `year`, `quarter` (extracted)

**`fact_search_interest`** — grain: one row per keyword × region × week:
- `keyword_id`, `region_id`, `date_id` (foreign keys)
- `interest_value`

### profiles.yml

Stored at `dbt/profiles.yml` (committed — safe because it uses `env_var()`):

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

---

## Part 3: README

**File:** `README.md` at repo root.

**Sections:**
1. Project title + one-line description
2. Pipeline diagram (ASCII)
3. Tech stack table
4. How to run locally (3 commands)

**Pipeline diagram:**
```
pytrends API
     │
     ▼
GitHub Actions (daily 9am UTC)
     │
     ▼
Snowflake: raw.GOOGLE_TRENDS_RAW
     │
     ▼
dbt: stg_google_trends_raw
     │
     ▼
dbt: fact_search_interest ── dim_keyword
                          ── dim_region
                          ── dim_date
     │
     ▼
Streamlit Dashboard (Milestone 02)
```

---

## Snowflake Setup Addition

dbt writes to a new schema `analytics` (separate from `raw`). Need to add to `setup/snowflake_setup.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS junior_data_analyst.analytics;
```

---

## Success Criteria

- [ ] `.github/workflows/load_google_trends.yml` committed and visible in Actions tab
- [ ] dbt models run cleanly (`dbt run` with 0 errors)
- [ ] `dbt test` passes for all models
- [ ] Star schema tables exist in `junior_data_analyst.analytics`
- [ ] `README.md` committed with pipeline diagram
- [ ] All 6 unit tests still pass
