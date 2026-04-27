# Interview Study Guide — Financial Services Keyword Demand Intelligence

**Format:** One-on-one professor Q&A  
**Project:** End-to-end analytics pipeline tracking Google Trends search demand for financial keywords  
**Last updated:** 2026-04-27

> **How to use this guide:** Read each section's explanation until you can say it in your own words. Then practice answering the sample questions out loud — not by reading the answer, but by recalling it. Update this file as you build Milestone 2.

---

## Section 1: Elevator Pitch

**What to be able to say in 2 minutes:**

> "I built an end-to-end analytics pipeline that tracks Google Trends search demand for financial keywords — things like personal loans, payday loans, and credit cards. These are the exact signals a PPC analyst at a company like EPCVIP would monitor to decide where to spend ad budget.
>
> Data flows from the pytrends API into Snowflake through a GitHub Actions job that runs every day automatically. From there, dbt transforms the raw data into a star schema — dimension tables for keywords, regions, and dates, with a fact table for search interest scores. The final output is a Streamlit dashboard that visualizes demand trends across US states and keywords over time.
>
> I also built a knowledge base by scraping 17 industry sources using Firecrawl, so I could understand the business context behind the data — how lead generation works, what drives search demand, and how companies like EPCVIP compete in the market."

**Practice tip:** Say this without looking. Time yourself. Aim for under 2 minutes.

---

## Section 2: Business Context

**The explanation:**

EPCVIP is a financial services lead generation company. They connect consumers searching for personal loans, payday loans, or credit cards with lenders willing to pay for those leads. Their revenue depends on capturing high-intent search traffic at the right moment.

A PPC analyst at EPCVIP monitors Google search demand to know when to bid more aggressively on keywords, which regions are heating up, and which financial products are trending. Your pipeline automates that signal — instead of manually checking Google Trends, the data lands in Snowflake every morning ready to query.

**Sample questions:**

- *"Why does search interest data matter for a company like EPCVIP?"*
  > Search volume predicts consumer intent. If "personal loans" searches spike in Texas, a PPC analyst knows to increase bids for that region before competitors do. Your pipeline makes that signal queryable and historical.

- *"Why these five keywords specifically?"*
  > They map directly to EPCVIP's core financial products — personal loans, payday loans, credit cards, installment loans, cash advance. These are the terms consumers type when they're ready to borrow, which is exactly when EPCVIP wants to show an ad.

- *"What does lead generation actually mean?"*
  > A consumer searches for a personal loan, clicks an ad, fills out a form. EPCVIP sells that filled-out form (the "lead") to a lender. The lender pays per lead. EPCVIP's margin is the difference between what they pay for the click and what they charge for the lead.

---

## Section 3: Pipeline & Architecture

**The explanation:**

```
pytrends API → GitHub Actions (daily 9am UTC) → Snowflake raw → dbt → Streamlit
Firecrawl → knowledge/raw/ (17 markdown files)
```

Each layer has a job:
- **pytrends** — Python client that queries Google Trends. No API key needed. Returns interest scores 0-100 by US state.
- **GitHub Actions** — runs `load_google_trends.py` on a cron schedule (`0 9 * * *` = 9am UTC daily). Credentials stored as GitHub Secrets, never in code.
- **Snowflake** — cloud data warehouse. Raw data lands in `raw.GOOGLE_TRENDS_RAW`. Chosen because it's industry standard for analytics engineering.
- **dbt** — transforms raw into a star schema. Staging cleans and renames columns. Marts implement business logic.
- **Streamlit** — Python-based dashboard framework. Simple to deploy, connects directly to Snowflake.

**Sample questions:**

- *"Walk me through what happens when the pipeline runs."*
  > At 9am UTC, GitHub Actions spins up a Linux runner, installs dependencies, and runs `load_google_trends.py`. That script calls pytrends for each of the 5 keywords across all US states (5 × 51 = 255 rows), then uses `write_pandas` to load them into `GOOGLE_TRENDS_RAW` in Snowflake. dbt runs separately to refresh the star schema models on top of that raw data.

- *"Why Snowflake instead of Postgres or SQLite?"*
  > Snowflake separates compute from storage, scales automatically, and is what analytics teams actually use in industry. It also integrates directly with dbt and Streamlit. For a portfolio project targeting a data analyst role, it's the right choice to demonstrate.

- *"What are GitHub Secrets and why do you use them?"*
  > Secrets are encrypted environment variables stored in GitHub, injected into the workflow at runtime. This means Snowflake credentials never appear in the code or git history — a basic security requirement. Locally, the same variables live in a `.env` file that's gitignored.

---

## Section 4: dbt & Star Schema

**The explanation:**

dbt brings software engineering discipline to SQL transformations. Instead of one-off scripts, every transformation is a versioned `.sql` file with tests, documentation, and automatic dependency ordering.

Your star schema:
- **`stg_google_trends_raw`** — staging view that cleans column names from the raw table
- **`dim_keyword`** — 5 rows, one per keyword, with a surrogate key
- **`dim_region`** — 50 rows, one per US state
- **`dim_date`** — one row per unique week_start date
- **`fact_search_interest`** — grain: one row per keyword × region × week. Joins to all three dimensions via foreign keys. Contains `interest_value` (0-100).

Why star schema? Dashboards query it with simple joins. A BI tool or Streamlit app can ask "what was the interest in personal loans in California last month?" with one straightforward SQL query.

**Sample questions:**

- *"What does dbt actually do that you couldn't do with plain SQL?"*
  > Plain SQL in Snowflake works fine, but dbt adds: version control for transforms, `ref()` so models declare their own dependencies, built-in testing (`dbt test`), and a data catalog (`dbt docs`). It treats your data pipeline like software — testable, reviewable, deployable.

- *"What is the grain of your fact table?"*
  > One row per keyword × region × week. So for a given week, there are 5 keywords × 51 regions = 255 rows. `interest_value` is the Google Trends score (0-100) for that combination.

- *"What tests do you run with dbt?"*
  > Schema tests defined in `_schema.yml`: `unique` and `not_null` on all primary keys, `not_null` on all foreign keys in the fact table. Run with `dbt test`. If a key is duplicated or missing, the test fails before bad data reaches the dashboard.

- *"Why staging models? Why not just build marts directly from raw?"*
  > Staging isolates raw source details from business logic. If the source API changes a column name, you fix it in one staging model — not in every mart. It's the same reason you don't write business logic directly in a database controller.

---

## Section 5: GitHub Actions

**The explanation:**

GitHub Actions is the orchestration layer — it's what makes the pipeline run automatically without you touching it. Your workflow file (`.github/workflows/load_google_trends.yml`) defines:

- **Trigger:** `schedule: cron: '0 9 * * *'` (daily at 9am UTC) + on every push to main
- **Runner:** `ubuntu-latest` (a fresh Linux VM spun up by GitHub)
- **Steps:** checkout code → set up Python 3.11 → install `requirements.txt` → run `load_google_trends.py`
- **Secrets:** all Snowflake credentials injected from GitHub Secrets as environment variables

**Sample questions:**

- *"Why automate this? Couldn't you just run the script manually?"*
  > Manual runs get forgotten. A daily cron means the data is always fresh without human intervention — the same reason production pipelines use schedulers like Airflow or GitHub Actions. It also demonstrates that the pipeline is reliable, not just a one-time script.

- *"What happens if the pipeline fails?"*
  > GitHub Actions sends an email notification on failure. The raw table doesn't get new rows for that day, but historical data is preserved. You'd check the Actions log to see the error, fix it, and re-run.

- *"How do you make sure credentials don't end up in the code?"*
  > Two layers: locally, a `.env` file loaded by `python-dotenv` that's listed in `.gitignore`. In GitHub Actions, secrets are stored encrypted in the repo settings and injected as environment variables at runtime — they never appear in logs or code.

---

## Section 6: Knowledge Base (Firecrawl)

**The explanation:**

The `knowledge/` folder is a queryable library of 17 scraped industry sources. `extract/scrape_pipeline.py` uses the Firecrawl API to search for and scrape pages, saving each as a markdown file in `knowledge/raw/`. Sources cover:

- EPCVIP's business model and product offerings
- Financial services PPC strategy (keyword selection, bid management)
- Consumer lending trends (personal loan demand, credit card usage)
- Competitor approaches (LendingTree, QuinStreet, MoneyMutual)

This gives the project business context — the pipeline isn't just a technical exercise, it tracks signals that matter for real decisions.

**Sample questions:**

- *"Why scrape industry articles? What does that add to the project?"*
  > The pipeline produces numbers, but the knowledge base explains what those numbers mean. If personal loan searches spike, the scraped sources tell you whether that's seasonal, driven by rate cuts, or a market trend. It connects the data to business judgment.

- *"What is Firecrawl?"*
  > A web scraping API that handles JavaScript rendering, rate limiting, and markdown conversion. You send it a search query and a target number of results, it returns scraped pages as clean markdown. Much simpler than building a scraper from scratch with BeautifulSoup.

- *"How many sources and from how many different sites?"*
  > 17 sources from at least 3 different sites — EPCVIP's own site, PPC/marketing publications, consumer lending industry reports, and competitor sites like LendingTree.

---

## Section 7: dbt Docs

**The explanation:**

dbt has a built-in documentation system. Two commands:

- `dbt docs generate` — reads your model `.sql` files and `_schema.yml` descriptions, generates a static JSON catalog
- `dbt docs serve` — spins up a local web server at `localhost:8080` with a browsable data catalog

The catalog shows every model, its description, column names and types, tests, and the full lineage graph (a DAG showing which models depend on which). It's the difference between a pipeline that exists and a pipeline that a team can actually understand and maintain.

**Sample questions:**

- *"What is a data catalog and why does it matter?"*
  > A catalog is documentation attached to the data itself — not a separate wiki that goes stale. When a new analyst joins the team, they open the catalog and can see what every table contains, what it means, and where it came from. In dbt, it's generated automatically from your code and schema descriptions.

- *"What does the dbt lineage graph show?"*
  > A DAG (directed acyclic graph) of your models — arrows show dependencies. You can see that `fact_search_interest` depends on `dim_keyword`, `dim_region`, and `dim_date`, which all depend on `stg_google_trends_raw`, which reads from `raw.google_trends_raw`. It makes the pipeline's structure visual and auditable.

- *"Why is documentation part of the pipeline, not separate?"*
  > Because separate documentation always goes stale. When your code changes, dbt docs regenerate automatically — the catalog reflects the actual current state of the models. That's a software engineering principle: make the artifact generate its own documentation.

---

## Section 8: Natural Language & AI

**The explanation:**

Natural language interfaces to data let non-technical users ask questions in plain English and get SQL results back. Tools like Claude, ChatGPT, or purpose-built BI tools (Tableau Pulse, Looker's AI features) sit on top of a data warehouse and translate questions into queries.

Your project connects to this in two ways:
1. **Development:** You used Claude Code to assist with building the pipeline — writing scripts, designing the schema, debugging GitHub Actions, generating this study guide.
2. **Future direction:** A well-documented star schema (clear table names, column descriptions, dbt docs) is exactly what an LLM needs to generate accurate SQL. The better your data model is documented, the more reliably an AI can query it.

**Sample questions:**

- *"How did you use AI in this project?"*
  > Claude Code assisted throughout — brainstorming the architecture, writing and debugging Python scripts, designing the dbt schema, and generating documentation. It's like pair programming with a senior engineer. I still made all the design decisions and reviewed everything, but it accelerated the implementation significantly.

- *"What is natural language querying of a data warehouse?"*
  > Instead of writing SQL, a user types "which state had the highest interest in personal loans last month?" and an LLM translates that into a SQL query against the star schema. Tools like Snowflake Cortex, BigQuery Duet AI, and standalone tools like Vanna.ai do this. It requires a well-structured, well-documented data model to work reliably.

- *"Why does schema design matter for AI querying?"*
  > An LLM generates better SQL when table and column names are clear and consistent. `fact_search_interest.interest_value` is easier to reason about than `raw.val`. Your star schema — with descriptive names and dbt docs descriptions — is well-suited for natural language querying on top.

---

## Section 9: Tough Questions

These are the questions designed to probe whether you actually understand what you built.

**"What would you do differently if you built this again?"**
> I'd add a `dim_category` dimension to group keywords by product type (short-term credit vs. revolving credit). I'd also add a proper incremental dbt model so the fact table appends new rows instead of rebuilding from scratch each run. And I'd set up `dbt docs` in the GitHub Actions pipeline so the catalog deploys automatically.

**"What are the limitations of pytrends data?"**
> Google Trends scores are relative (0-100), not absolute search volumes. The number 75 doesn't mean 75,000 searches — it means 75% of peak interest for that term in that period. You can compare trends over time and across regions, but you can't derive absolute traffic estimates. It's directional, not precise.

**"How does this pipeline handle failure?"**
> GitHub Actions emails on failure. The raw table preserves all historical rows even if a day's run fails. dbt tests would catch if malformed data made it through. What's missing: alerting, a retry mechanism, and idempotent loads (right now a failed mid-run could partially load a day's data).

**"Is this production-ready?"**
> Not fully. It works reliably for a portfolio project, but a production pipeline would need: idempotent loads (deduplicate on keyword + region + week), monitoring/alerting beyond email, dbt run in the Actions workflow (not just extract), and a staging environment separate from production Snowflake.

**"Why Streamlit instead of Tableau or Power BI?"**
> Streamlit is Python-native — the same language as the rest of the pipeline. It deploys for free on Streamlit Community Cloud and connects directly to Snowflake. For a portfolio project, it shows Python and SQL skills together. In a real company, Tableau or Looker would be the choice because they're self-serve for non-technical users.

**"What does the data actually show?"**
> Answer this with what you observe in your own dashboard. Practice describing one real insight: which keyword has the highest interest, which region leads, whether there's seasonality. The professor will respect "here's what I actually found in the data" more than a generic answer.

---

## How to Study

1. **Day before:** Read each section explanation out loud. Don't memorize — understand.
2. **Night before:** Cover the answers and answer each sample question out loud from memory.
3. **Morning of:** Run through the elevator pitch twice. Open your dashboard and note one real insight from the data.
4. **In the interview:** If you don't know something, say "I'd have to look that up, but my understanding is..." — honesty is better than guessing.

---

*Update this file as Milestone 2 (dashboard, knowledge base wiki) is completed.*
