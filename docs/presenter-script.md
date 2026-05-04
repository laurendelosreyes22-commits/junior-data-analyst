# Financial Keyword Intelligence — Presenter Script

**Lauren De Los Reyes · ISBA 4715 · EPCVIP Junior Data Analyst Portfolio**

> 🖱️ = click to reveal the next item on that slide

---

## Slide 1 — Hook

"Right now, someone in Mississippi is searching for a payday loan. Does your ad budget know that?"

*Pause. Let it land. Then move forward.*

---

## Slide 2 — The Business Case

"EPCVIP is a lead generation company — they connect people who need loans with lenders, and they make money when leads convert. Leads in high-demand, low-competition markets are worth significantly more. But without geographic demand data, there's no way to know which markets those are. That's the gap this project closes."

---

## Slide 3 — What I Built

"To answer that, I built an end-to-end analytics pipeline. It pulls Google Trends data for financial keywords — personal loans, payday loans, credit cards — across every US state. That data runs through Snowflake and dbt into a live dashboard. It refreshes daily, automatically. No manual work."

---

## Slide 4 — National Average Hides the Real Story 🖱️ click to reveal bars one by one

"Let's look at the national picture. Personal loans lead at 52."

🖱️ click — "Cash advance right behind at 50."

🖱️ click — "Credit cards at 42."

🖱️ click — "Payday loans drop to 27 nationally." *Point at the highlighted amber bar.* "If you stopped here, you'd deprioritize payday loans entirely. That's the wrong call."

🖱️ click — *Point at the map.* "Because look what happens when you break it out by state. Mississippi: 100. The national average is hiding a massive regional signal."

---

## Slide 5 — Diagnostic 🖱️ click to reveal rows one by one

"So why is the South so dark on the map? Let's break it down by category."

🖱️ click — "Short-term credit — payday loans and cash advance — scores 100 out of 100 in Mississippi. Maximum demand."

🖱️ click — "Revolving credit scores 100 in Wyoming."

🖱️ click — "And consumer lending scores 84.5 — also in Mississippi."

🖱️ click — "Mississippi leads two out of three categories. The reason is structural: lower median incomes, fewer traditional banks, higher reliance on alternative credit. That 100 on the right isn't a fluke — it's an underserved market."

---

## Slide 6 — Where to Move the Money 🖱️ click to reveal each bullet

"So here's the recommendation: shift 30–40% of short-term budget to Mississippi, Louisiana, and Wyoming."

🖱️ click — *Point at state names.* "These three states score highest on demand and lowest on national advertiser concentration."

🖱️ click — "That combination means higher-intent leads at lower CPL than you'll get in California, New York, or Texas."

🖱️ click — "And because the pipeline refreshes daily, this isn't a one-time analysis — you rerun it monthly and move budget as the market moves."

---

## Slide 7 — Follow the Data Live

*Switch to browser tab with the dashboard already open before saying anything.*

"Imagine you're a PPC analyst at EPCVIP and you open this Monday morning."

"Step one — what happened? On the Descriptive tab, I click Mississippi. Watch the keyword breakdown update. Payday loan demand spikes well above the national average."

"Step two — why? I go to the Diagnostic tab. It's not a one-week trend — it's consistent across every category. This is structural underbanking, not noise."

"Step three — so what? That's where you move the budget. High-intent audience, lower advertiser competition, lower cost-per-lead. And because this refreshes daily, the answer changes as the market changes."

---

## Slide 8 — Close

"The signal exists. The pipeline captures it. Now act on it."

*Stop there. Don't say "that's it" or "any questions?" — just stop. Let the slide do the work. Then open for Q&A.*
