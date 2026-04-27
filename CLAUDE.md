# CLAUDE.md — Financial Services Keyword Demand Intelligence

## Project Overview

**Student:** Lauren De Los Reyes
**Course:** ISBA 4715 — Analytics Engineering
**Target Role:** Junior Data Analyst at EPCVIP, Inc
**GitHub Repo:** [junior-data-analyst](https://github.com/laurendelosreyes22-commits/junior-data-analyst)

This portfolio project builds an end-to-end analytics pipeline tracking Google Trends search demand for financial product keywords (personal loans, payday loans, credit cards) — the same signals a PPC analyst at EPCVIP monitors to optimize ad spend.

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt |
| Orchestration | GitHub Actions (scheduled) |
| Dashboard | Streamlit (deployed to Streamlit Community Cloud) |
| API Source | pytrends (Google Trends) |
| Web Scrape | Firecrawl or similar |
| AI Development | Claude Code + Superpowers |

## Data Architecture

### Pipeline Flow

```
pytrends API → GitHub Actions → Snowflake Raw → dbt Staging → dbt Mart → Streamlit Dashboard
Web Scrape → GitHub Actions → knowledge/raw/ → Claude Code → knowledge/wiki/
```

### Star Schema (`junior-data-analyst` Snowflake database)

```
fact_search_interest
├── dim_keyword      (keyword name, category, product type)
├── dim_region       (US state/region, region code)
├── dim_date         (date, week, month, year, quarter)
└── dim_category     (financial product category)
```

### Directory Structure

```
├── CLAUDE.md
├── .gitignore
├── docs/
│   ├── job-posting.pdf
│   ├── proposal.pdf
│   └── resume.pdf          (added at final submission)
├── extract/
│   └── load_google_trends.py
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── dbt_project.yml
├── dashboard/
│   └── app.py
├── knowledge/
│   ├── raw/                (15+ scraped sources from 3+ sites)
│   ├── wiki/               (Claude Code-generated synthesis pages)
│   └── index.md
└── .github/
    └── workflows/
```

## Credentials & Secrets

**Never commit credentials to the repo.** All secrets via environment variables:

- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_SCHEMA`
- Stored in `.env` locally (gitignored) and GitHub Actions secrets for CI/CD

## Milestones

| Milestone | Due | Key Deliverables |
|---|---|---|
| Proposal | Apr 13 | `docs/job-posting.pdf`, `docs/proposal.pdf`, repo initialized |
| Milestone 01 | Apr 27 | pytrends extraction, Snowflake raw load, dbt staging + marts, GitHub Actions pipeline, pipeline diagram |
| Milestone 02 | May 4 | Web scrape source, Streamlit dashboard (deployed), knowledge base, README, ERD, slides PDF |
| Final Submission | May 11 | `docs/resume.pdf` committed |

## Knowledge Base

The `knowledge/` folder is a queryable knowledge base about the financial services lead generation industry.

### How to Query the Knowledge Base

When answering questions about EPCVIP, the PPC/lead gen industry, competitor landscape, or financial product trends, Claude Code should:

1. **Start with `knowledge/index.md`** to find which wiki pages are relevant
2. **Read relevant wiki pages** in `knowledge/wiki/` for synthesized insights
3. **Check raw sources** in `knowledge/raw/` for specific quotes, data points, or details not in the wiki
4. **Synthesize across sources** — do not just summarize one document; draw connections across multiple

Example queries you can ask Claude Code:
- "What does my knowledge base say about EPCVIP's business model?"
- "What are the key trends in financial services lead generation?"
- "How do competitors like LendingTree and QuinStreet approach PPC?"

### Knowledge Base Sources

Target sources include:
- EPCVIP website and blog
- LendingTree, QuinStreet, MoneyMutual competitor sites
- Financial services PPC and lead gen industry publications

Minimum: 15 raw sources from 3+ different sites/authors.

## Development Guidelines

- Use the **Superpowers brainstorming skill** before starting any new feature or design decision
- Use the **Superpowers writing-plans skill** before implementing any multi-step task
- Follow **dbt conventions**: staging models clean and rename source columns; mart models implement business logic and star schema
- All Python scripts must load credentials from environment variables — never hardcode
- Commit frequently with meaningful messages that describe *why*, not just *what*
- Use `dbt test` to validate models before committing

## Project Context

This project is designed to transfer across roles:
- Marketing Data Analyst at fintech companies (Chime, SoFi)
- BI Analyst at consumer lending companies (LendingClub)
- Campaign Analytics Analyst at digital marketing agencies serving financial services clients
