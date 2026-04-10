# Project Proposal

**Name:** Lauren De Los Reyes

**Project Name:** Financial Services Keyword Demand Intelligence

**GitHub Repo:** [marketing-analyst-fintech](https://github.com/laurendelosreyes22-commits/marketing-analyst-fintech)

## Job Posting

- **Role:** Junior Data Analyst
- **Company:** EPCVIP, Inc
- **Link:** https://www.indeed.com/viewjob?jk=d71c3b7f5db99929

**SQL requirement (quote the posting):** "Certifications: Not required, but Google Analytics, SQL, or data visualization certifications are a plus."

## Problem Statement

PPC analysts at financial services companies like EPCVIP need to monitor search demand trends for financial product keywords (personal loans, payday loans, credit cards) to allocate ad spend effectively. Without a structured pipeline, this data lives in one-off Google Trends exports with no history, no regional breakdown, and no way to spot seasonal patterns or benchmark across keywords. This project builds the infrastructure to track, store, and surface that demand signal continuously.

## Proposed Data Sources

- **API (required):** pytrends — Python client for Google Trends. Extracts search interest by keyword, US region, and week. No authentication required. Scheduled via GitHub Actions.
- **Web scrape (required):** EPCVIP website, competitor lead gen sites (LendingTree, QuinStreet, MoneyMutual), and financial services PPC/lead gen industry publications. Feeds the knowledge base. Scraped via Firecrawl or similar, scheduled via GitHub Actions.

## Solution Overview

A pipeline that extracts weekly Google Trends search interest data for financial product keywords, loads it into Snowflake raw, transforms it through dbt staging and mart layers into a star schema (`fact_search_interest`, `dim_keyword`, `dim_region`, `dim_date`), and surfaces it in a deployed Streamlit dashboard answering: which keywords have the highest demand, how demand has shifted over the past 12 months, and which US regions drive the most search interest. A parallel knowledge base pipeline scrapes industry sources and uses Claude Code to synthesize insights into queryable wiki pages.

## Reflection

This Junior Data Analyst role at EPCVIP, Inc is directly relevant to this analytics engineering course because it requires the same core competencies the class builds: SQL, performance dashboards, automated data pipelines, and communicating data-driven insights to stakeholders. Specifically, the posting asks for experience creating and maintaining dashboards and reports, performing ad hoc analysis to support revenue strategy, and ensuring data integrity across reporting systems — all skills developed through dbt, Snowflake, GitHub Actions, and Streamlit in this course. To prove I can do this job, I would build a pipeline that extracts Google Trends search interest data for financial product keywords (personal loans, payday loans, credit cards), loads it into Snowflake, transforms it through a dbt star schema, and surfaces it in a deployed Streamlit dashboard showing demand trends by keyword, region, and time — the same signals a PPC analyst at EPCVIP monitors to optimize ad spend. This project would also transfer to roles like Marketing Data Analyst at a fintech (Chime, SoFi), BI Analyst at a consumer lending company (LendingClub), or Campaign Analytics Analyst at a digital marketing agency serving financial services clients.
