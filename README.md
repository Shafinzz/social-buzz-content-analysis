# Social Buzz Content Analysis

**Skill:** Data cleaning, merging, and visualization (pandas, Matplotlib, Plotly), applied data-viz design principles (validated color palette, consistent styling, plain-English reporting)

**Status:** Completed

An independent portfolio project inspired by the Accenture "Social Buzz" case study (Forage Data Analytics and Visualization Job Simulation). Built entirely in Python, not Excel/Power BI — same business question, different tool, matching the skillset from this project's own 7-project data science roadmap (Project 2: clean + merge + visualize).

Social Buzz is a fictional social media company that wanted to know: **which content categories earn the most positive engagement, so leadership knows where to invest?**

## Files

- `Content.csv`, `Reactions.csv`, `ReactionTypes.csv` — the 3 raw starting datasets (verified authentic, unedited)
- `content_analysis.py` — the full analysis script (cleaning → merging → scoring → visualization → temporal analysis). Comments are concise but complete: what each pandas/matplotlib/Plotly tool does (for anyone new to them), why any non-obvious decision was made, and the real outcome/finding at each step
- `generate_report.py` — builds the final PDF report from the charts and findings produced by `content_analysis.py`
- `requirements.txt` — Python dependencies (`pip install -r requirements.txt`)
- `charts/` — every generated chart, both static (`.png`) and interactive (`.html`, open in any browser)
- `Social_Buzz_Content_Analysis_Report.pdf` — the final polished report (17 pages, written in plain/simple English: Objective, Tools, Features, Challenges, Methodology, Iterations, Findings with embedded charts + a "Key Takeaway" under each, Conclusion, Learnings, Recommendations)

## How to run

```
pip install -r requirements.txt
python content_analysis.py    # cleans the data, builds all 18 charts into charts/
python generate_report.py     # builds the PDF report from those charts (run second)
```

## Key findings

**Top 5 content categories by total engagement score:**
1. animals — 68,624
2. science — 65,405
3. healthy eating — 63,138
4. technology — 63,035
5. food — 61,598

This ranking was independently cross-checked against a separately completed reference project using the same underlying dataset, which produced the **identical top-5 ranking in the identical order** — strong validation that the cleaning and merging logic was correct.

**Scale:** the top 5 categories together account for **36% of all engagement earned platform-wide** — meaningfully more than the 31% an even split across 16 categories would produce.

**Volume, not quality:** the average score per individual reaction is nearly identical across every category platform-wide (~39–41 points, under 4% spread). The top categories win because they draw more total reactions, not because each reaction is more enthusiastic — a real distinction for how to grow them further (reach/distribution, not "make each post more compelling").

**Sentiment:** 56.2% of all reactions were positive, 31.2% negative, 12.5% neutral (by count). By total score, positive reactions dominate even further (756K vs. 78K neutral vs. 59K negative), since positive reaction types tend to carry higher point values. This sentiment mix is nearly identical between the top 5 categories and the rest of the platform — reinforcing that the top 5 win on volume, not on a more positive reaction mix.

**Content type:** Fairly even split platform-wide — photo (26.8%), video (25.4%), GIF (24.8%), audio (23.0%). Within the top 5 categories specifically, audio over-indexes somewhat (27% vs. 21% elsewhere).

**Reaction types:** "Super love" was the single highest-scoring reaction type (104,475 total points); "disgust" scored lowest (~0, by design — it's worth 0 points).

**Temporal patterns:** the raw year-over-year chart shows 2024 with more reactions than 2025 (~12,200 vs. ~10,300) — but the dataset actually spans one rolling year (mid-June to mid-June), not two full calendar years, so the 2024 label covers about one extra month of data. Once that's accounted for, average reactions per full month are nearly identical (1,898 vs. 1,862) — no real year-over-year change. Reactions were otherwise fairly evenly spread across months (May highest, February lowest) and across time of day (Morning highest, Afternoon lowest) — no dramatic spikes.

## Data cleaning notes

- `Content.csv`'s `Category` column had 41 different-looking values for what was really only 16 categories, caused by inconsistent capitalization and stray quote marks baked into the text — fixed with `.str.strip('"').str.lower()`.
- `Reactions.csv` had 3,019 rows missing a `User ID` and 980 rows missing a `Reaction_Type` — fully overlapping (every row missing a Reaction_Type was also missing a User ID). Removed with `.dropna()`, leaving 22,534 clean rows (from 25,553).
- Merging `Content` and `Reactions` caused a naming collision (`User ID` existed in both, meaning different things) — resolved by dropping both auto-suffixed copies, since neither was needed for the analysis.
- `Datetime` was written `DD-MM-YYYY`, requiring `dayfirst=True` in `pd.to_datetime()` to avoid silently misreading ambiguous dates.
