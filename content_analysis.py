"""
Social Buzz Content Analysis

Cleans and merges three raw datasets (posts, reactions, reaction scores) to
identify the top 5 content categories by total engagement score, with
supporting analysis of sentiment, content type, and temporal patterns.

Input:  Content.csv, Reactions.csv, ReactionTypes.csv
Output: charts/ (12 PNG + 6 interactive HTML charts)
"""

import os
import pandas as pd            # loads/cleans/merges the CSV data (spreadsheet-style tables)
import matplotlib.pyplot as plt  # draws the static (image) charts
import plotly.express as px      # draws the interactive (hover/click) charts

CHARTS_DIR = 'charts'
os.makedirs(CHARTS_DIR, exist_ok=True)  # creates the charts/ folder if it doesn't exist yet

# --- Chart style -----------------------------------------------------------
# A small, fixed set of colors reused across every chart -- a validated,
# colorblind-safe categorical palette -- so the whole report looks like one
# consistent system instead of each chart picking its own random colors.
# STATUS is reserved for good/neutral/bad data specifically (e.g. sentiment).
PALETTE = {
    'blue': '#2a78d6', 'orange': '#eb6834', 'aqua': '#1baf7a', 'yellow': '#eda100',
    'magenta': '#e87ba4', 'green': '#008300', 'violet': '#4a3aa7', 'red': '#e34948',
}
STATUS = {'good': '#0ca30c', 'neutral': '#898781', 'critical': '#d03b3b'}
INK_PRIMARY = '#0b0b0b'      # main text color
INK_SECONDARY = '#52514e'    # axis label / caption color
INK_MUTED = '#898781'        # tick label color
GRID_COLOR = '#e1e0d9'       # faint gridline color
SURFACE = '#fcfcfb'          # near-white chart background

# One hue (blue), light-to-dark. Used only on charts where the bars are
# already sorted by value, so the gradient visually reinforces "this is a
# ranking" instead of being pure decoration.
SEQUENTIAL_BLUE = [
    '#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7',
    '#3987e5', '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b',
]


def ranked_colors(n):
    """Return n colors sampled light-to-dark from SEQUENTIAL_BLUE, for bars
    already sorted smallest-to-largest (index 0 = lightest, index n-1 = darkest)."""
    step = (len(SEQUENTIAL_BLUE) - 1) / max(n - 1, 1)
    return [SEQUENTIAL_BLUE[round(i * step)] for i in range(n)]


# rcParams sets matplotlib's DEFAULTS globally -- every chart drawn after
# this point automatically picks up this look (no boxed border, light
# gridlines, muted tick labels, one consistent font) without repeating it.
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'axes.edgecolor': GRID_COLOR,
    'axes.labelcolor': INK_SECONDARY,
    'axes.titlecolor': INK_PRIMARY,
    'axes.titleweight': 'bold',
    'axes.titlesize': 13,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'axes.axisbelow': True,
    'grid.color': GRID_COLOR,
    'grid.linewidth': 0.8,
    'xtick.color': INK_MUTED,
    'ytick.color': INK_MUTED,
    'text.color': INK_PRIMARY,
})

# The Plotly equivalent of rcParams above: a dict of shared settings handed
# to every Plotly chart via fig.update_layout(**PLOTLY_LAYOUT, ...) below,
# so the interactive charts match the static ones.
PLOTLY_LAYOUT = dict(
    template='plotly_white',
    font=dict(family='Segoe UI, Arial, sans-serif', color=INK_PRIMARY, size=13),
    title_font=dict(size=16, color=INK_PRIMARY),
    plot_bgcolor=SURFACE,
    paper_bgcolor=SURFACE,
    margin=dict(l=80, r=40, t=60, b=50),
)

# --- Load --------------------------------------------------------------
# pd.read_csv() reads a CSV file (a plain-text spreadsheet) into a pandas
# DataFrame -- a table you can filter, sort, and calculate on in Python.
# Content: 1,000 posts. Reactions: 25,553 raw reactions. ReactionTypes: 16
# reaction types mapped to a sentiment and a point score.
content = pd.read_csv('Content.csv')
reactions = pd.read_csv('Reactions.csv')
reaction_types = pd.read_csv('ReactionTypes.csv')

# --- Clean -----------------------------------------------------------------
# .str unlocks text operations applied to every row in a column at once.
# .strip('"') removes stray quote marks from each value's edges; .lower()
# makes everything lowercase. Outcome: 41 raw variants (e.g. "Science" vs.
# science vs. "science") collapse to the correct 16 clean categories.
content['Category'] = content['Category'].str.strip('"').str.lower()

# .dropna() removes any row with a missing value in ANY column -- here, rows
# missing a User ID or Reaction_Type. Outcome: 25,553 -> 22,534 rows.
reactions = reactions.dropna()

# --- Merge -------------------------------------------------------------
# .merge() joins two tables into one, matching rows by a shared column --
# similar to an Excel VLOOKUP, but for the whole table at once.
# how='inner' keeps only rows that found a match in BOTH tables.
reactions_scored = reactions.merge(reaction_types, on='Reaction_Type', how='inner')
final_data = reactions_scored.merge(content, on='Content ID', how='inner')

# Both source files had a "User ID" column with different meanings (reactor
# vs. poster); pandas auto-suffixed them to User ID_x/_y on merge to avoid a
# name clash. .drop(columns=...) removes columns we don't need downstream.
final_data = final_data.drop(columns=['User ID_x', 'User ID_y'])
# Outcome: final_data is 22,534 rows x 7 columns, one row per reaction.

# --- Score and rank categories ---------------------------------------------
# .groupby('Category') splits all rows into one group per category;
# ['Reaction_Score'].sum() adds up the score within each group.
category_scores = final_data.groupby('Category')['Reaction_Score'].sum()
# .sort_values(ascending=False) orders scores highest-to-lowest; .head(5)
# keeps just the first 5 rows -- now that it's sorted, the actual top 5.
top_5 = category_scores.sort_values(ascending=False).head(5)

# Outcome (the headline answer): animals (68,624), science (65,405),
# healthy eating (63,138), technology (63,035), food (61,598).
print('Top 5 Content Categories by Total Engagement Score:')
print(top_5)

# Extra context: what SHARE of the whole platform's score do these 5
# account for? (16 categories total, so an even split would be 31.25%.)
top_5_share = top_5.sum() / category_scores.sum() * 100
print(f'Top 5 share of total platform engagement: {top_5_share:.1f}%')

# --- Chart: top 5 categories ---------------------------------------------
# plt.subplots() creates a blank figure (the whole image) and axes (the
# actual plotting area) to draw on.
fig, ax = plt.subplots(figsize=(7, 5))
colors = ranked_colors(len(top_5))[::-1]  # reversed: darkest first, matching top_5's biggest-first order
bars = ax.bar(top_5.index, top_5.values, color=colors, width=0.6)
# bar_label() prints each bar's exact value above it; the list comprehension
# formats each number with a comma separator (e.g. 68,624).
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in top_5.values], padding=3, color=INK_SECONDARY, fontsize=9)
# fig.suptitle() is the bold main title; ax.set_title() (smaller, muted) sits
# just above the plot as a subtitle -- matplotlib has no built-in subtitle,
# this two-title trick is the standard way to add one.
fig.suptitle('Top 5 Content Categories by Total Engagement Score', fontsize=13, fontweight='bold', color=INK_PRIMARY, y=0.98)
ax.set_title(f'Together, these 5 categories account for {top_5_share:.0f}% of all engagement platform-wide', fontsize=9.5, color=INK_SECONDARY, fontweight='normal', pad=10)
ax.set_xlabel('Category')
ax.set_ylabel('Total Reaction Score')
ax.grid(axis='x', visible=False)  # only horizontal gridlines, cleaner for a bar chart
plt.xticks(rotation=30, ha='right')
plt.tight_layout(rect=[0, 0, 1, 0.94])  # leaves room at the top for suptitle + subtitle
plt.savefig(f'{CHARTS_DIR}/top_5_categories.png', dpi=150)

# --- Chart: sentiment breakdown -------------------------------------------
# .value_counts() counts how many rows have each distinct value, sorted
# from most common to least. Outcome: 56.2% positive, 31.2% negative, 12.5% neutral.
sentiment_counts = final_data['Sentiment'].value_counts()
# A dict + list comprehension maps each sentiment to a FIXED color (not by
# rank), so "positive" is always green regardless of chart order.
sentiment_color_map = {'positive': STATUS['good'], 'neutral': STATUS['neutral'], 'negative': STATUS['critical']}
pie_colors = [sentiment_color_map[s] for s in sentiment_counts.index]

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',  # autopct prints each slice's %
    colors=pie_colors, startangle=90,
    wedgeprops={'edgecolor': SURFACE, 'linewidth': 2},  # thin gap between slices, not a heavy border
    textprops={'color': INK_PRIMARY, 'fontsize': 11},
)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax.set_title('Overall Sentiment Breakdown of Reactions')
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/sentiment_breakdown.png', dpi=150)

# --- Chart: content type distribution -------------------------------------
# Fixed color per content type (not by rank), so "photo" is always the same
# color regardless of sort order. Outcome: fairly even split -- photo ~27%,
# video ~25%, GIF ~25%, audio ~23%.
content_type_counts = final_data['Content_Type'].value_counts()
content_type_color_map = {'photo': PALETTE['blue'], 'video': PALETTE['orange'], 'GIF': PALETTE['aqua'], 'audio': PALETTE['yellow']}
bar_colors = [content_type_color_map[c] for c in content_type_counts.index]

fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(content_type_counts.index, content_type_counts.values, color=bar_colors, width=0.6)
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in content_type_counts.values], padding=3, color=INK_SECONDARY, fontsize=9)
ax.set_title('Reactions by Content Type')
ax.set_xlabel('Content Type')
ax.set_ylabel('Number of Reactions')
ax.grid(axis='x', visible=False)
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/content_type_distribution.png', dpi=150)

# --- Temporal features -----------------------------------------------------
# pd.to_datetime() converts plain text (e.g. '22-04-2025 15:17') into a real
# date/time value pandas can extract year/month/hour from. dayfirst=True
# tells pandas the dates are written DD-MM-YYYY (not the American MM-DD-YYYY)
# -- without it, some dates could be silently misread with day/month swapped.
final_data['Datetime'] = pd.to_datetime(final_data['Datetime'], dayfirst=True)

# Shifted +4 years for presentation freshness (source data is synthetic
# simulation data; the offset preserves every relative pattern used below).
final_data['Datetime'] = final_data['Datetime'] + pd.DateOffset(years=4)

# .dt unlocks date/time-specific extraction, the same way .str unlocks text
# operations -- here pulling out the year, month name, and hour as new columns.
final_data['Year'] = final_data['Datetime'].dt.year
final_data['Month'] = final_data['Datetime'].dt.month_name()
final_data['Hour'] = final_data['Datetime'].dt.hour


def get_time_of_day(hour):
    """Bucket an hour (0-23) into Night / Morning / Afternoon / Evening."""
    if hour < 6:
        return 'Night'
    elif hour < 12:
        return 'Morning'
    elif hour < 18:
        return 'Afternoon'
    return 'Evening'


# .apply() runs get_time_of_day() once per row of Hour and collects the
# returned labels into a new column.
final_data['Time_of_Day'] = final_data['Hour'].apply(get_time_of_day)

# --- Chart: reactions by year ---------------------------------------------
# NOTE: the source data spans one rolling year (mid-June to mid-June), not
# two full calendar years, so the 2024 label covers ~1 extra month vs. 2025.
# Average reactions per full month are nearly identical (1,898 vs. 1,862) --
# the gap shown here is a date-range artifact, not a real decline.
year_counts = final_data['Year'].value_counts().sort_index()
year_color_map = {2024: PALETTE['blue'], 2025: PALETTE['orange']}
bar_colors = [year_color_map[y] for y in year_counts.index]
fig, ax = plt.subplots(figsize=(5, 5))
bars = ax.bar(year_counts.index.astype(str), year_counts.values, color=bar_colors, width=0.5)
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in year_counts.values], padding=3, color=INK_SECONDARY, fontsize=9)
ax.set_title('Reactions by Year')
ax.set_xlabel('Year')
ax.set_ylabel('Number of Reactions')
ax.grid(axis='x', visible=False)
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/reactions_by_year.png', dpi=150)

# --- Chart: reactions by month (calendar order) -----------------------
# .reindex(month_order) forces the calendar order (Jan->Dec) instead of
# value_counts()'s default "sorted by count" order, since a flowing calendar
# sequence reads more naturally than a shuffled one. Outcome: fairly flat all
# year -- May busiest, February quietest.
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
               'August', 'September', 'October', 'November', 'December']
month_counts = final_data['Month'].value_counts().reindex(month_order)
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(month_counts.index, month_counts.values, color=PALETTE['blue'], width=0.6)
ax.set_title('Reactions by Month')
ax.set_xlabel('Month')
ax.set_ylabel('Number of Reactions')
ax.grid(axis='x', visible=False)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/reactions_by_month.png', dpi=150)

# --- Chart: reactions by time of day (natural order) -----------------------
# Outcome: fairly flat -- Morning slightly busiest, Afternoon slightly quietest.
time_of_day_order = ['Morning', 'Afternoon', 'Evening', 'Night']
time_of_day_counts = final_data['Time_of_Day'].value_counts().reindex(time_of_day_order)
fig, ax = plt.subplots(figsize=(6, 5))
bars = ax.bar(time_of_day_counts.index, time_of_day_counts.values, color=PALETTE['blue'], width=0.55)
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in time_of_day_counts.values], padding=3, color=INK_SECONDARY, fontsize=9)
ax.set_title('Reactions by Time of Day')
ax.set_xlabel('Time of Day')
ax.set_ylabel('Number of Reactions')
ax.grid(axis='x', visible=False)
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/reactions_by_time_of_day.png', dpi=150)

# --- Interactive Plotly charts ---------------------------------------------
# px.bar() builds a Plotly figure object (fig) rather than drawing directly,
# unlike matplotlib. orientation='h' makes the bars horizontal; text_auto
# prints each bar's value automatically. fig.write_image() saves a static
# PNG (needs the 'kaleido' package); fig.write_html() saves the fully
# interactive version -- open it in a browser to hover for exact values.
sorted_scores = category_scores.sort_values(ascending=True)
fig = px.bar(x=sorted_scores.values, y=sorted_scores.index, orientation='h', text_auto='.2s')
fig.update_traces(marker_color=ranked_colors(len(sorted_scores)), marker_line_width=0)
fig.update_layout(**PLOTLY_LAYOUT, title='Sum of Score by Category', xaxis_title='Total Reaction Score', yaxis_title='')
fig.update_xaxes(gridcolor=GRID_COLOR)
fig.write_image(f'{CHARTS_DIR}/sum_score_by_category.png', scale=2)
fig.write_html(f'{CHARTS_DIR}/sum_score_by_category.html')

# Outcome: "super love" scores highest (104,475 points); "disgust" scores
# lowest (~0, worth 0 points by design).
reaction_type_scores = final_data.groupby('Reaction_Type')['Reaction_Score'].sum().sort_values(ascending=True)
fig = px.bar(x=reaction_type_scores.values, y=reaction_type_scores.index, orientation='h', text_auto='.2s')
fig.update_traces(marker_color=ranked_colors(len(reaction_type_scores)), marker_line_width=0)
fig.update_layout(**PLOTLY_LAYOUT, title='Sum of Score by Reaction Type', xaxis_title='Total Reaction Score', yaxis_title='')
fig.update_xaxes(gridcolor=GRID_COLOR)
fig.write_image(f'{CHARTS_DIR}/sum_score_by_reaction_type.png', scale=2)
fig.write_html(f'{CHARTS_DIR}/sum_score_by_reaction_type.html')

# Sentiment uses STATUS colors (not the ranking gradient) since sentiment
# specifically means good/bad, matching the sentiment pie chart above.
sentiment_scores = final_data.groupby('Sentiment')['Reaction_Score'].sum().sort_values(ascending=True)
sentiment_bar_colors = [sentiment_color_map[s] for s in sentiment_scores.index]
fig = px.bar(x=sentiment_scores.values, y=sentiment_scores.index, orientation='h', text_auto='.2s')
fig.update_traces(marker_color=sentiment_bar_colors, marker_line_width=0)
fig.update_layout(**PLOTLY_LAYOUT, title='Sum of Score by Sentiment', xaxis_title='Total Reaction Score', yaxis_title='')
fig.update_xaxes(gridcolor=GRID_COLOR)
fig.write_image(f'{CHARTS_DIR}/sum_score_by_sentiment.png', scale=2)
fig.write_html(f'{CHARTS_DIR}/sum_score_by_sentiment.html')

# Year-split comparisons. groupby() on TWO columns + reset_index() turns the
# grouped result back into a flat table (Category, Year, Reaction_Score as
# separate columns) so Plotly can use Year as the color grouping.
# color_discrete_map fixes identity colors (2024=blue, 2025=orange), so 2024
# is the same blue everywhere in the report, not just here.
category_year_scores = final_data.groupby(['Category', 'Year'])['Reaction_Score'].sum().reset_index()
category_year_scores['Year'] = category_year_scores['Year'].astype(str)  # text, not a number, so Plotly treats it as 2 distinct colors, not a gradient
fig = px.bar(
    category_year_scores, x='Reaction_Score', y='Category', color='Year', orientation='h', barmode='group',
    text_auto='.2s', color_discrete_map={'2024': PALETTE['blue'], '2025': PALETTE['orange']},
)
# Labels moved outside the bars: 16 categories x 2 years = 32 bars is too
# dense for in-bar labels to stay readable.
fig.update_traces(marker_line_width=0, textposition='outside', textfont_size=10)
fig.update_layout(**PLOTLY_LAYOUT, title='Sum of Score by Category and Year', xaxis_title='Total Reaction Score', yaxis_title='', height=700)
fig.update_xaxes(gridcolor=GRID_COLOR)
fig.update_yaxes(categoryorder='total ascending')
fig.write_image(f'{CHARTS_DIR}/sum_score_by_category_and_year.png', scale=2)
fig.write_html(f'{CHARTS_DIR}/sum_score_by_category_and_year.html')

sentiment_year_scores = final_data.groupby(['Sentiment', 'Year'])['Reaction_Score'].sum().reset_index()
sentiment_year_scores['Year'] = sentiment_year_scores['Year'].astype(str)
fig = px.bar(
    sentiment_year_scores, x='Reaction_Score', y='Sentiment', color='Year', orientation='h', barmode='group',
    text_auto='.2s', color_discrete_map={'2024': PALETTE['blue'], '2025': PALETTE['orange']},
)
fig.update_traces(marker_line_width=0, textposition='outside', textfont_size=11)
fig.update_layout(**PLOTLY_LAYOUT, title='Sum of Score by Sentiment and Year', xaxis_title='Total Reaction Score', yaxis_title='')
fig.update_xaxes(gridcolor=GRID_COLOR)
fig.update_yaxes(categoryorder='total ascending')
fig.write_image(f'{CHARTS_DIR}/sum_score_by_sentiment_and_year.png', scale=2)
fig.write_html(f'{CHARTS_DIR}/sum_score_by_sentiment_and_year.html')

# Bar chart, not pie: the 4 content-type shares are too close (23-27%) for a
# pie chart to compare accurately (slice angles that close are hard to judge by eye).
content_type_counts_for_bar = final_data['Content_Type'].value_counts().reset_index()
content_type_counts_for_bar.columns = ['Content_Type', 'Count']  # reset_index() names the count column '0' by default; rename for clarity
bar_colors = [content_type_color_map[c] for c in content_type_counts_for_bar['Content_Type']]
fig = px.bar(content_type_counts_for_bar, x='Content_Type', y='Count', text_auto=True)
fig.update_traces(marker_color=bar_colors, marker_line_width=0)
fig.update_layout(**PLOTLY_LAYOUT, title='Content Type Distribution (Interactive)', xaxis_title='', yaxis_title='Number of Reactions')
fig.update_yaxes(gridcolor=GRID_COLOR)
fig.write_image(f'{CHARTS_DIR}/content_type_distribution_plotly.png', scale=2)
fig.write_html(f'{CHARTS_DIR}/content_type_distribution_plotly.html')
