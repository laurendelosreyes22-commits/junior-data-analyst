# Proposal Design Spec
**Date:** 2026-04-08
**Topic:** Analytics Engineering Portfolio Project Proposal

---

## Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Repo name | `marketing-analyst-fintech` | Professional, descriptive, transfers across fintech/financial services roles |
| Project angle | Keyword Demand Intelligence | Directly mirrors EPCVIP's PPC search monitoring work; real data, clean architecture |
| API source | pytrends (Google Trends) | Free, no auth, financial product keywords by region/time; directly relevant to PPC lead gen |
| Web scrape | EPCVIP + competitor lead gen sites + industry publications | Builds knowledge base about the exact industry in the job posting |
| Star schema center | `fact_search_interest` | Natural grain: one row per keyword × region × week |

## Star Schema

```
fact_search_interest
├── dim_keyword      (keyword name, category, product type)
├── dim_region       (US state/region, region code)
├── dim_date         (date, week, month, year, quarter)
└── dim_category     (financial product category)
```

## Dashboard Business Questions

- **Descriptive:** Which financial product keywords have the highest search demand right now?
- **Descriptive:** How has search interest changed over the past 12 months?
- **Diagnostic:** Which US regions drive the most search interest for personal loans?
- **Diagnostic:** What seasonal patterns exist in financial product search demand?

## Knowledge Base Scope

- EPCVIP website and blog
- Competitor sites: LendingTree, QuinStreet, MoneyMutual
- Financial services PPC/lead gen industry publications
- Minimum 15 raw sources from 3+ sites

## Reflection Paragraph (final)

> This Junior Data Analyst role at EPCVIP, Inc directly targets the skills covered in this analytics engineering course. The role requires SQL proficiency, performance dashboard creation, and the ability to communicate data-driven insights to stakeholders — all core competencies built in this class. The coursework's focus on dimensional modeling (dbt star schema), automated data pipelines (GitHub Actions), and interactive dashboards (Streamlit) maps directly onto EPCVIP's need to monitor campaign KPIs and identify revenue optimization opportunities. By building a pipeline that tracks search demand trends for financial product keywords — the same signals a PPC analyst monitors to allocate ad spend — this project demonstrates both the technical foundation and domain fluency the role requires.

## Transferability

Also targets: fintech analysts (Chime, SoFi), consumer lending (LendingClub), insurance analytics, digital marketing agencies with financial services clients.
