# What I'm prepared to defend in the final interview

---

## Pipeline Components

- **API extraction:** `extract/load_google_trends.py` — fetches weekly Google Trends interest (0–100) for 5 keywords (`personal loans`, `payday loans`, `credit cards`, `installment loans`, `cash advance`) across all 51 US regions using pytrends; retries up to 3× with exponential backoff (120s → 240s → 360s) on 429 rate limits
- **Snowflake raw table:** `RAW.GOOGLE_TRENDS_RAW` — columns: `KEYWORD`, `REGION`, `WEEK_START`, `INTEREST_VALUE`, `LOADED_AT`; 2,295 rows total
- **Firecrawl scrape:** `extract/scrape_pipeline.py` → `RAW.FIRECRAWL_RAW` — 65 rows of scraped industry content from EPCVIP, LendingTree, and financial services publications; also writes markdown to `knowledge/raw/`
- **GitHub Actions – daily load:** `.github/workflows/load_google_trends.yml` — cron `0 9 * * *` (9 AM UTC daily); triggers on push to main; runs extraction script with Snowflake secrets from GitHub Actions secrets
- **GitHub Actions – weekly scrape:** `.github/workflows/scrape_pipeline.yml` — cron `0 9 * * 0` (Sundays 9 AM UTC); also supports manual dispatch
- **Secrets handling:** All credentials (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_SCHEMA`) stored in `.env` locally (gitignored) and GitHub Actions secrets in CI/CD — never hardcoded
- **dbt staging model:** `dbt/models/staging/stg_google_trends_raw.sql` — reads from `junior_data_analyst.raw.google_trends_raw`; cleans and renames columns: `keyword`, `region`, `week_start`, `interest_value`, `loaded_at`
- **dbt source definition:** `dbt/models/staging/_sources.yml` — declares source database `junior_data_analyst`, schema `raw`, table `google_trends_raw`
- **dim_keyword:** `dbt/models/marts/dim_keyword.sql` — `keyword_id` (MD5 hash PK), `keyword`, `category` (mapped: consumer lending / short-term credit / revolving credit); tests: unique + not null on keyword_id and keyword
- **dim_region:** `dbt/models/marts/dim_region.sql` — `region_id` (MD5 hash PK), `region` (US state name); 51 rows; tests: unique + not null
- **dim_date:** `dbt/models/marts/dim_date.sql` — `date_id` (MD5 hash PK), `week_start`, `month`, `year`, `quarter`; tests: unique + not null on date_id
- **fact_search_interest:** `dbt/models/marts/fact_search_interest.sql` — grain: 1 row per keyword × region × week; FKs: `keyword_id`, `region_id`, `date_id`; `interest_value` not null; 255 rows in `ANALYTICS` schema
- **dbt tests:** `dbt/models/marts/_schema.yml` — uniqueness and not_null on all dimension PKs and fact FKs
- **Streamlit dashboard:** `dashboard/app.py` — deployed to Streamlit Community Cloud; queries `junior_data_analyst.analytics.fact_search_interest` joined to all 3 dims; tabs: Descriptive (demand by keyword/state), Diagnostic (comparative), Ask the Knowledge Base (RAG Q&A)
- **Knowledge base – raw:** `knowledge/raw/` — 17+ scraped markdown files from EPCVIP site, LendingTree, QuinStreet, financial services PPC publications, FTC lead gen workshop docs, CFPB credit trend reports
- **Knowledge base – wiki:** `knowledge/wiki/` — 4 Claude Code-synthesized pages: `01-epcvip-overview.md`, `02-competitor-landscape.md`, `03-ppc-keyword-strategy.md`, `04-consumer-lending-trends.md`; each cites specific raw source files
- **Knowledge base routing:** `knowledge/index.md` — maps query topics to wiki pages; wiki pages cite raw files by name so any claim can be traced to a source

---

## Star Schema (draw this on whiteboard)

```
fact_search_interest (255 rows)
├── keyword_id  FK → dim_keyword.keyword_id   (5 keywords)
├── region_id   FK → dim_region.region_id     (51 US states)
├── date_id     FK → dim_date.date_id         (1 date record)
└── interest_value  INTEGER  0–100
```

---

## Business Insights (memorize these — be specific)

1. **Credit cards dominate nationally** — avg 2× higher interest than personal loans across all states; signals crowded PPC market, higher CPCs for EPCVIP in this segment
2. **Payday loan / cash advance demand concentrates in the South** — Mississippi and Louisiana show highest relative demand; lower lender saturation = stronger cost-per-lead economics for EPCVIP's regional targeting
3. **Short-term credit keywords spike in lower-median-income states** — geographic pattern that directly maps to EPCVIP's lead gen strategy: bid higher in high-demand, underserved markets

---

## Likely Follow-Up Questions & Answers

**"Why pytrends over a direct Google API?"**
→ Google Trends doesn't offer an official public API. pytrends is the standard Python wrapper that reverse-engineers the Trends UI. Trade-off: unofficial, so rate limits hit fast — handled with exponential backoff.

**"Why MD5 for surrogate keys instead of auto-increment?"**
→ MD5 on the natural key makes the pipeline idempotent — running dbt twice doesn't duplicate rows or break keys. Auto-increment would give different IDs on each run.

**"What breaks at 100× data volume?"**
→ pytrends rate limiting gets worse (already hitting 429s at current scale). The fix: paginate smaller batches or add a proxy layer. Snowflake and dbt scale fine — that's the value of separating ingestion from transformation.

**"What's in knowledge/raw/ vs knowledge/wiki/?"**
→ `raw/` = raw scraped markdown, one file per source (17+ files from 3+ sites). `wiki/` = Claude Code-synthesized summaries that pull from multiple raw files. The wiki is queryable; raw is the citation layer. Example: ask "What's EPCVIP's business model?" → routes to `01-epcvip-overview.md` wiki → cites `01-epcvip-financial-service-lead-provider-and-solutio.md` raw file.

**"What would you change with more time?"**
→ Three things: (1) Deduplicate in staging using `ROW_NUMBER() OVER (PARTITION BY keyword, region, week_start ORDER BY loaded_at DESC)` — right now duplicate pipeline runs create duplicate rows that flow into the fact table. (2) Replace MD5 surrogate keys with integer keys using `ROW_NUMBER() OVER ()` — MD5 has theoretical collision risk and produces opaque 32-char strings. (3) Use actual week dates from the pytrends index instead of `datetime.today()` — right now all historical rows get stamped with today's date, which breaks time-series analysis.

**"What slipped first when time got tight?"**
→ The Firecrawl scrape pipeline — rate limits and API response format changes caused multiple crashes. Prioritized getting the pytrends → Snowflake → dbt → Streamlit path clean first since that was the core deliverable.

---

## "Tell me about yourself" (60 seconds — practice this out loud)

> "I'm a senior at LMU studying Marketing and Information Systems — graduating May 2026.
> This semester I built a full analytics pipeline in ISBA 4715 that tracks Google Trends search demand for financial keywords like personal loans and payday loans across all 50 states — the same signals a PPC analyst at EPCVIP monitors to optimize ad spend.
> I've also interned at Amazon managing operational KPIs for a 60-person team and at Plante Moran doing financial data work in Excel.
> Outside of school I competed in the Effie Collegiate competition and made it to semi-finals nationally.
> I'm drawn to EPCVIP specifically because the role sits at the intersection of data and campaign performance — which is exactly what I built this project to demonstrate."

**Stack words to hit:** SQL, Python, Snowflake, dbt, star schema, GitHub Actions, Google Trends, campaign performance, data pipeline, dashboard

---

## Pipeline Whiteboard Sketch (draw in this order)

```
[pytrends API] ──► [GitHub Actions] ──► [Snowflake RAW.GOOGLE_TRENDS_RAW]
                         │
[Firecrawl] ─────────────┘              │
     │                                  ▼
     ▼                        [dbt stg_google_trends_raw]
[knowledge/raw/]                        │
     │                                  ▼
     ▼                        [dbt mart: dim_keyword]
[Claude Code]                 [dbt mart: dim_region ]  ──► [fact_search_interest]
     │                        [dbt mart: dim_date   ]
     ▼
[knowledge/wiki/]                       │
                                        ▼
                              [Streamlit Dashboard]
                              (Streamlit Community Cloud)
```

Label on whiteboard: database = `junior_data_analyst`, raw schema = `RAW`, mart schema = `ANALYTICS`
