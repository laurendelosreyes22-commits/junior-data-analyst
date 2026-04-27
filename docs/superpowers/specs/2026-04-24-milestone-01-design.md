# Milestone 01 Design Spec
**Date:** 2026-04-24
**Topic:** Extract & Load — pytrends + Firecrawl → Snowflake Raw

---

## Overview

Two independent Python scripts that extract data from two different source types and load results into Snowflake's raw schema. No transformation, orchestration, or dashboard required at this milestone.

**Due:** April 27 at 9:55 AM
**Points:** 20 (10 pts per deliverable)

---

## Approach

Two separate scripts following the lesson patterns from mp03 (API pipeline) and mp04 (scrape pipeline):
- `extract/load_google_trends.py` — pytrends → Snowflake (Deliverable 4)
- `extract/scrape_pipeline.py` — Firecrawl search → `knowledge/raw/` markdown files + Snowflake metadata (Deliverable 5)

Snowflake loading uses `write_pandas` (bulk via COPY INTO) as demonstrated in mp02, not row-by-row inserts.

---

## Snowflake Setup

**Account identifier:** `cec86794.us-east-1`
**Database:** `junior_data_analyst` (hyphens not allowed in Snowflake identifiers)
**Schema:** `junior_data_analyst.raw`
**Warehouse:** `junior_data_analyst_wh` (X-Small, auto-suspend 60s)

Setup SQL lives in `setup/snowflake_setup.sql` and is run once manually before the scripts.

### Raw Tables

```sql
CREATE TABLE IF NOT EXISTS google_trends_raw (
  keyword        VARCHAR,
  region         VARCHAR,
  week_start     DATE,
  interest_value INTEGER,
  loaded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firecrawl_raw (
  source_url       VARCHAR,
  page_title       VARCHAR,
  description      VARCHAR,
  local_file_path  VARCHAR,
  scraped_at       TIMESTAMP,
  loaded_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Note: `firecrawl_raw` stores metadata only — full markdown content lives in `knowledge/raw/` files.

---

## Deliverable 4 — pytrends Extraction (`extract/load_google_trends.py`)

**Pattern:** Follows mp03 API pipeline pattern — extract data, build DataFrame, load to Snowflake via `write_pandas`.

**Source:** pytrends Python client (Google Trends, no auth required)

**Keywords tracked:**
- `personal loans`
- `payday loans`
- `credit cards`
- `installment loans`
- `cash advance`

**Pull:** `interest_by_region` at US state resolution, `timeframe='today 12-m'`

**Output:** ~250 rows per run (50 states × 5 keywords). Loaded to `raw.GOOGLE_TRENDS_RAW` via `write_pandas`.

**Credentials:** `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_SCHEMA` — loaded from `.env` via `python-dotenv`.

---

## Deliverable 5 — Firecrawl Scrape (`extract/scrape_pipeline.py`)

**Pattern:** Follows mp04 scrape pipeline pattern — raw `requests` library, Firecrawl v2/search endpoint, save as numbered markdown files in `knowledge/raw/`.

**Source:** Firecrawl v2 search API (`POST https://api.firecrawl.dev/v2/search`)

**Searches (3 queries × 5 results = 15 files):**
1. `"EPCVIP personal loans payday loans lead generation"` — limit 5
2. `"financial services PPC advertising keywords strategy"` — limit 5
3. `"consumer lending market trends personal loans credit cards"` — limit 5

**File storage:** `knowledge/raw/01-slug.md` through `15-slug.md`
Each file has the source URL header + scraped markdown content.

**Snowflake load:** Metadata (url, title, description, local file path, scraped_at) loaded to `raw.FIRECRAWL_RAW` via `write_pandas`. Satisfies milestone "loads to Snowflake raw schema" requirement.

**Credentials:** `FIRECRAWL_API_KEY` + Snowflake vars — loaded from `.env` via `python-dotenv`.

---

## File Structure

```
├── setup/
│   └── snowflake_setup.sql
├── extract/
│   ├── load_google_trends.py
│   └── scrape_pipeline.py
├── tests/
│   ├── test_load_google_trends.py
│   └── test_scrape_pipeline.py
├── knowledge/
│   └── raw/                   (15 markdown files created by scrape_pipeline.py)
├── .env                       (gitignored)
└── requirements.txt
```

---

## Environment Variables (`.env`)

```
SNOWFLAKE_ACCOUNT=cec86794.us-east-1
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_DATABASE=junior_data_analyst
SNOWFLAKE_WAREHOUSE=junior_data_analyst_wh
SNOWFLAKE_SCHEMA=raw
FIRECRAWL_API_KEY=
```

---

## Dependencies (`requirements.txt`)

```
pytrends
snowflake-connector-python
python-dotenv
requests
pandas
pytest
```

Note: Uses raw `requests` for Firecrawl (not the `firecrawl-py` SDK), matching the mp04 lesson pattern.

---

## Success Criteria

- [ ] Snowflake database, schema, warehouse, and tables created
- [ ] `load_google_trends.py` runs locally and rows appear in `raw.GOOGLE_TRENDS_RAW`
- [ ] `scrape_pipeline.py` runs locally and creates 15 markdown files in `knowledge/raw/`
- [ ] `scrape_pipeline.py` loads metadata rows to `raw.FIRECRAWL_RAW`
- [ ] No credentials committed to the repo
- [ ] `.env` is in `.gitignore`
- [ ] All unit tests pass
