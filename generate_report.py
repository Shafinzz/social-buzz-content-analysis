# GENERATE THE FINAL PDF REPORT
#
# This script does NOT do any new data analysis -- all the cleaning,
# merging, scoring, and chart-building already happened in
# content_analysis.py (run that first so the charts/ folder exists).
#
# This script's only job is to take everything we found and write it into
# one polished PDF report, structured the same way as "Project 3: Data
# Cleaning and Modelling Project" in the reference academic report
# (Objective -> Tools -> Features -> Challenges -> Methodology ->
# Iterations -> Findings (with charts) -> Conclusion -> Learnings ->
# Recommendations) -- but every number, finding, and chart below is OUR
# own real output, not copied from the reference.
#
# The WORDING in this report is deliberately written in plain, simple
# English -- short sentences, everyday words, technical terms explained
# in parentheses -- so it's easy to read back later, even long after
# the coding details are forgotten.
#
# fpdf2 is a library for building PDF files from Python: you create a
# blank PDF "canvas" and add text/images to it piece by piece, similar in
# spirit to how matplotlib builds a chart piece by piece.
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Same color palette used for the charts in content_analysis.py, so the
# PDF's headings visually match the charts inside it -- one consistent look.
HEADING_BLUE = (42, 120, 214)    # matches PALETTE['blue'] (#2a78d6) -- main headings
ACCENT_ORANGE = (215, 89, 34)    # matches PALETTE['orange'], darkened slightly for text -- sub-headings
INK_PRIMARY = (11, 11, 11)
INK_SECONDARY = (82, 81, 78)

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Try to embed the actual Times New Roman font (Windows ships these 4 files
# by default) for the closest possible match. If they're not found -- e.g.
# running on macOS/Linux, which don't ship this font -- fall back to fpdf2's
# built-in 'Times' core font instead of crashing. The built-in core fonts
# (Helvetica/Times/Courier) need no embedding and render on every PDF viewer.
FONT = 'Times'
try:
    fonts_dir = r'C:\Windows\Fonts'
    pdf.add_font('TimesNewRoman', '', f'{fonts_dir}\\times.ttf')
    pdf.add_font('TimesNewRoman', 'B', f'{fonts_dir}\\timesbd.ttf')
    pdf.add_font('TimesNewRoman', 'I', f'{fonts_dir}\\timesi.ttf')
    pdf.add_font('TimesNewRoman', 'BI', f'{fonts_dir}\\timesbi.ttf')
    FONT = 'TimesNewRoman'
except FileNotFoundError:
    pass  # not on Windows (or fonts missing) -- FONT stays 'Times', fpdf2's built-in core font


# fpdf2 quirk discovered while building this: multi_cell() does NOT reset
# the cursor back to the left margin afterward -- it leaves x wherever the
# text happened to end. Since a width of 0 means "use the space from the
# CURRENT x to the right margin," a second call right after the first can
# end up with zero space left and crash. Fix: explicitly reset x to the
# left margin before every text call, via this one shared helper.
def reset_x():
    pdf.set_x(pdf.l_margin)


def add_heading(text):
    """Adds a bold, colored section heading with a thin accent rule under it
    (e.g. 'Objective', 'Methodology') -- the rule gives each new section a
    clear visual break, like a header band in a modern dashboard."""
    pdf.set_font(FONT, 'B', 18)
    pdf.set_text_color(*HEADING_BLUE)
    pdf.ln(6)
    reset_x()
    pdf.cell(0, 10, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*HEADING_BLUE)
    pdf.set_line_width(0.6)
    reset_x()
    pdf.cell(0, 0, '', border='T', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.set_font(FONT, '', 12)
    pdf.set_text_color(*INK_PRIMARY)


def add_subheading(text):
    """Adds a smaller bold sub-heading within a section, in the accent
    orange -- a second color keeps a long report from feeling monotone,
    while staying inside the same validated palette as the charts."""
    pdf.set_font(FONT, 'B', 14)
    pdf.set_text_color(*ACCENT_ORANGE)
    pdf.ln(3)
    reset_x()
    pdf.cell(0, 9, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(FONT, '', 12)
    pdf.set_text_color(*INK_PRIMARY)


def add_paragraph(text):
    """Adds a regular block of body text, wrapping automatically."""
    reset_x()
    pdf.multi_cell(0, 7, text)
    pdf.ln(1)


def add_bullet(text):
    """Adds one bullet point line, with a colored dash instead of a plain
    hyphen -- a small touch that ties bullets back to the report's palette.
    Uses a temporarily narrowed left margin so wrapped lines line up under
    the bullet TEXT, not back under the dash (a proper hanging indent)."""
    reset_x()
    indent = 8
    pdf.set_text_color(*HEADING_BLUE)
    pdf.set_font(FONT, 'B', 12)
    pdf.cell(indent, 7, '-')
    pdf.set_text_color(*INK_PRIMARY)
    pdf.set_font(FONT, '', 12)
    original_margin = pdf.l_margin
    pdf.set_left_margin(original_margin + indent)
    pdf.multi_cell(0, 7, text)
    pdf.set_left_margin(original_margin)
    reset_x()
    pdf.ln(1)


def add_chart(path, caption, width=170):
    """Embeds a chart image with a small italic caption underneath."""
    reset_x()
    pdf.image(path, w=width)
    pdf.set_font(FONT, 'I', 10)
    pdf.set_text_color(*INK_SECONDARY)
    reset_x()
    pdf.multi_cell(0, 6, caption)
    pdf.set_font(FONT, '', 12)
    pdf.set_text_color(*INK_PRIMARY)
    pdf.ln(1)


def add_summary(text):
    """Adds a one-line 'Key Takeaway' directly under a chart's caption --
    the specific, concrete finding from THAT chart, not just a description
    of what the chart shows."""
    reset_x()
    pdf.set_font(FONT, 'B', 11)
    pdf.set_text_color(*ACCENT_ORANGE)
    pdf.write(6, 'Key Takeaway: ')
    pdf.set_font(FONT, '', 11)
    pdf.set_text_color(*INK_SECONDARY)
    pdf.write(6, text)
    pdf.ln(10)
    pdf.set_text_color(*INK_PRIMARY)
    pdf.set_font(FONT, '', 12)


# ---------------------------------------------------------------------
# TITLE PAGE
# ---------------------------------------------------------------------
pdf.add_page()
pdf.set_font(FONT, 'B', 30)
pdf.set_text_color(*HEADING_BLUE)
pdf.ln(35)
reset_x()
pdf.multi_cell(0, 15, 'Social Buzz Content Analysis', align='C')

# A short colored accent rule, centered under the title -- a small design
# touch borrowed straight from the chart palette, ties the cover page to
# the rest of the report before a single word of body text is read.
pdf.set_draw_color(*ACCENT_ORANGE)
pdf.set_line_width(1)
rule_width = 60
page_center = pdf.w / 2
pdf.line(page_center - rule_width / 2, pdf.get_y() + 2, page_center + rule_width / 2, pdf.get_y() + 2)
pdf.ln(12)

pdf.set_font(FONT, '', 16)
pdf.set_text_color(*INK_PRIMARY)
reset_x()
pdf.multi_cell(0, 9, 'Which content should Social Buzz make more of?', align='C')
pdf.ln(14)
pdf.set_font(FONT, 'I', 12)
pdf.set_text_color(*INK_SECONDARY)
reset_x()
pdf.multi_cell(
    0, 6,
    'A personal portfolio project, inspired by the Accenture "Social Buzz" case '
    'study (a Forage job simulation). Built from scratch in Python -- this is an '
    'independent learning project, not an official Forage submission or certificate.',
    align='C'
)
pdf.set_text_color(*INK_PRIMARY)

# ---------------------------------------------------------------------
# OBJECTIVE
# ---------------------------------------------------------------------
pdf.add_page()
add_heading('Objective')
add_paragraph(
    'Social Buzz is a made-up social media company used for this project. People '
    'post content there, and other people react to it -- not just with a simple '
    '"like," but with over 100 different reaction types (like "love," "scared," or '
    '"cherish"). Every reaction is worth a certain number of points.'
)
add_paragraph(
    'Nobody at Social Buzz had studied this data before. The goal of this project '
    'was simple to state: find out which types of content (like "cooking" or '
    '"science") get the most positive reactions, so the company knows what to '
    'invest more time and money into. To answer that, the raw data had to be '
    'cleaned up, combined into one usable table, added up, and turned into charts '
    'that make the answer obvious at a glance.'
)

# ---------------------------------------------------------------------
# TOOLS AND TECHNIQUES USED
# ---------------------------------------------------------------------
add_heading('Tools and Techniques Used')
add_bullet('Python -- the programming language used for the entire project.')
add_bullet('Pandas -- a tool that lets Python open, clean, and work with spreadsheet-style data (the same kind of data you would see in Excel).')
add_bullet('Matplotlib -- a tool for drawing clean, simple charts.')
add_bullet('Plotly -- a tool for drawing interactive charts you can click and hover over to see exact numbers.')

# ---------------------------------------------------------------------
# FEATURES USED
# ---------------------------------------------------------------------
add_heading('Features Used')
add_paragraph('In plain terms, here is what each tool actually did in this project:')
add_subheading('Pandas')
add_bullet('Opened each CSV file (a simple spreadsheet file) and took a first look at what was inside, including checking for missing information.')
add_bullet('Cleaned up messy text -- made everything lowercase and removed stray quote marks stuck to some category names.')
add_bullet('Removed rows that were missing important information, instead of guessing what they should say.')
add_bullet('Combined separate tables into one, matching rows up by a column they had in common (for example, matching every reaction to the post it belonged to).')
add_bullet('Removed a column that was no longer needed after combining the tables.')
add_bullet('Grouped matching rows together (for example, all "science" posts) and added up their scores.')
add_bullet('Sorted results from highest to lowest, and kept just the top few.')
add_bullet('Counted how many times each value appeared (for example, how many "positive" reactions there were).')
add_bullet('Converted plain text dates into real dates Python could actually understand and do math on.')
add_bullet('Used a small custom function (a mini tool written just for this project) to turn an hour of the day, like 14, into an easy label like "Afternoon."')
add_subheading('Matplotlib')
add_bullet('Drew bar charts and a pie chart, with a consistent, modern color scheme applied throughout.')
add_subheading('Plotly')
add_bullet('Drew interactive bar charts you can hover over for exact numbers, styled to match a professional dashboard.')

# ---------------------------------------------------------------------
# CHALLENGES FACED
# ---------------------------------------------------------------------
add_heading('Challenges Faced')
add_subheading('Missing Information')
add_bullet(
    'Some rows in the reactions file were incomplete -- about 3,000 rows were '
    'missing who reacted, and about 1,000 were missing what type of reaction it '
    'was. These incomplete rows were removed rather than guessed at.'
)
add_subheading('Messy, Inconsistent Text')
add_bullet(
    'Category names (like "science" or "cooking") were written inconsistently -- '
    'sometimes capitalized, sometimes with stray quote marks stuck to the text. '
    'What should have been 16 clean categories showed up as 41 different-looking '
    'versions. This was fixed by lowercasing everything and stripping the stray '
    'quote marks.'
)
add_subheading('Combining the Files Correctly')
add_bullet(
    'Two of the files both had a column called "User ID" -- but they meant '
    'different people in each file (the person who posted vs. the person who '
    'reacted). Combining the files required carefully sorting out this mix-up so '
    'the wrong information never got blended together.'
)
add_subheading('Confusing Date Format')
add_bullet(
    'Dates in the file were written day-first (22-04-2025 means April 22nd), not '
    'the month-first style common in the US. Python had to be told this directly '
    '-- otherwise some dates could have been silently misread with the day and '
    'month swapped, with no error or warning.'
)
add_subheading('A Computer Setting Blocked the Code')
add_bullet(
    "Partway through, a Windows security feature blocked one of the tools from "
    'running at all, with no clear error message at first. This had to be '
    'diagnosed and turned off before the project could continue.'
)

# ---------------------------------------------------------------------
# METHODOLOGY
# ---------------------------------------------------------------------
add_heading('Methodology')
add_subheading('Step 1: Clean the Data')
add_bullet('Opened all three files and checked what was inside each one.')
add_bullet('Fixed the messy category names.')
add_bullet('Removed rows that were missing important information.')
add_subheading('Step 2: Combine the Data')
add_bullet('Joined the reactions file with the scoring file, so every reaction now carried its point value.')
add_bullet('Joined that result with the content file, so every reaction also knew its category and content type.')
add_bullet('Fixed the "User ID" mix-up described above.')
add_subheading('Step 3: Build the Charts')
add_bullet('Added up the total score for each category, reaction type, and sentiment (positive/neutral/negative).')
add_bullet('Turned those totals into both simple charts and interactive, clickable charts.')
add_subheading('Step 4: Look at Time Patterns')
add_bullet('Converted the plain-text dates into real dates.')
add_bullet('Pulled out the year, month, and hour from each date.')
add_bullet('Sorted each hour into a time of day: Morning, Afternoon, Evening, or Night.')
add_bullet('Charted how reactions changed across years, months, and times of day.')

# ---------------------------------------------------------------------
# PROJECT ITERATIONS
# ---------------------------------------------------------------------
add_heading('Project Iterations')
add_subheading('Round 1')
add_bullet(
    'Loaded, cleaned, and combined the three files. Added up the scores and found '
    'the top 5 categories, shown as a first chart.'
)
add_subheading('Round 2')
add_bullet(
    'Added more charts (sentiment, content type, and time patterns), built '
    'interactive versions of the key charts, and gave every chart a consistent, '
    'modern design.'
)

# ---------------------------------------------------------------------
# FINDINGS AND ANALYSIS
# ---------------------------------------------------------------------
pdf.add_page()
add_heading('Findings and Analysis')

add_subheading('Which Categories Win? (Top 5)')
add_paragraph(
    'The 5 categories with the most positive engagement were: animals, science, '
    'healthy eating, technology, and food. Animals came out on top, with 68,624 '
    'total points.'
)
add_paragraph(
    'This same ranking was checked against a completely separate project that '
    'used the exact same underlying data -- and it produced the identical top 5, '
    'in the identical order. That match is a strong sign this result is correct, '
    'not a coincidence or a mistake.'
)
add_paragraph(
    'Looking closer at the numbers shows a useful pattern: the top 5 categories '
    'are tightly clustered together (61,598 to 68,624 points, only about 11% '
    'apart), while the lower half of the list drops off more steeply (down to '
    '45,751 for public speaking, a 33% gap from the top). This suggests the top '
    '5 form a genuinely distinct, higher-performing tier of content -- not just '
    'a handful of categories that happened to score a little higher than the '
    'rest -- which makes them a much stronger, more confident basis for an '
    'investment decision.'
)
add_paragraph(
    'Scale matters here too: together, these 5 categories account for 36% of '
    'ALL engagement earned across the entire platform -- meaningfully more than '
    'the 31% an even split across 16 categories would produce. In plain terms, '
    'roughly a third of everything Social Buzz users respond to positively is '
    'concentrated in just under a third of its content categories.'
)
add_paragraph(
    'It is also worth understanding HOW these categories are winning. The '
    'average score earned per individual reaction is nearly identical across '
    'every category platform-wide -- about 39 to 41 points per reaction, a '
    'spread of under 4%. In other words, a single reaction to an animals post '
    'is not inherently more enthusiastic than a reaction to a public speaking '
    'post. Animals wins because it draws MORE total reactions, not because each '
    'reaction scores higher. Practically, this reframes the opportunity: '
    'growing these categories further is a reach/volume problem (getting more '
    'eyes on the content), not a content-quality problem (making each post more '
    'emotionally compelling) -- the two call for different strategies.'
)
add_chart('charts/top_5_categories.png', 'Figure 1: The top 5 content categories by total engagement score.')
add_summary('Animals leads by about 3,200 points over second-place science -- a clear front-runner, not a marginal one.')
add_chart('charts/sum_score_by_category.png', 'Figure 2: Total engagement score across all 16 categories, ranked highest to lowest.')
add_summary('After the top 5, scores decline gradually -- the bottom 8 categories all sit within about 7,000 points of each other, a much tighter spread than the top tier.')
add_chart('charts/sum_score_by_category_and_year.png', 'Figure 3: Total engagement score by category, comparing 2024 vs. 2025.')
add_summary('The category ranking barely changes between years -- animals and science lead in both 2024 and 2025.')

add_subheading('What Kind of Content Gets Posted?')
add_paragraph(
    'Posts were fairly evenly split across four content types: photo (about 27% '
    'of reactions), video (25%), GIF (25%), and audio (23%). No single type '
    'dominates -- Social Buzz users engage with all four in roughly equal amounts.'
)
add_paragraph(
    'Because engagement barely differs by format, the format of a post (photo, '
    'video, GIF, or audio) does not appear to be a major driver of engagement on '
    'its own. The clear strategic takeaway: Social Buzz should prioritize WHAT '
    'topic to post about (the winning categories above) over WHICH format to '
    'post it in, since format alone shows little influence on the result.'
)
add_paragraph(
    'One nuance worth flagging: WITHIN the top 5 categories specifically, audio '
    'content makes up a noticeably larger share of reactions (27%) than it does '
    'across the rest of the platform (21%), while video and GIF are both '
    'relatively less common there. This is a modest pattern, not a strong '
    'signal on its own -- but it is a reasonable hypothesis worth testing '
    'further before assuming photo or video is always the safer format choice '
    'for high-performing categories.'
)
add_chart('charts/content_type_distribution.png', 'Figure 4: Number of reactions by content type.')
add_summary('Photo leads with about 6,000 reactions, but every content type stays within roughly 900 reactions of the top spot.')
add_chart('charts/content_type_distribution_plotly.png', 'Figure 5: The same breakdown, as an interactive chart.')
add_summary('Same near-even split as Figure 4 -- open the matching .html file in the charts/ folder to hover for exact counts.')

add_subheading('How Do People React?')
add_paragraph(
    'The single reaction type that earned the most total points was "super love" '
    '(104,475 points), followed by "adore" and "want." At the other end, '
    '"disgust" earned almost no points, since it is worth 0 points by design.'
)
add_paragraph(
    'Looking at all reactions together: 56% were positive, 31% were negative, and '
    '12% were neutral. When counting actual points instead of just the number of '
    'reactions, positive reactions pull even further ahead, since positive '
    'reaction types tend to be worth more points each.'
)
add_paragraph(
    'The fact that stronger reactions like "super love" and "adore" earn far '
    'more points than a plain "like" rewards content that inspires genuine '
    'enthusiasm, not just passive approval. It would be reasonable to guess the '
    'top 5 categories win by earning disproportionately MORE of these strong, '
    'positive reactions -- but checking that directly shows otherwise: the '
    'positive/neutral/negative sentiment mix in the top 5 categories (56.5% '
    'positive) is nearly identical to the rest of the platform (56.1% '
    'positive). This confirms the earlier finding -- the top 5 win on volume of '
    'reactions, not on a more positive or enthusiastic mix of reactions. At the '
    'same time, a 31% negative share platform-wide is not negligible: while '
    'overall sentiment is healthy, this is worth monitoring rather than '
    'dismissing outright.'
)
add_chart('charts/sum_score_by_reaction_type.png', 'Figure 6: Total engagement score for each individual reaction type.')
add_summary('The top 3 reaction types alone (super love, adore, want) outscore the bottom 8 reaction types combined.')
add_chart('charts/sentiment_breakdown.png', 'Figure 7: Overall sentiment breakdown -- what share of reactions were positive, neutral, or negative.')
add_summary('Positive reactions outnumber negative ones by nearly 2 to 1 (56.2% vs. 31.2%).')
add_chart('charts/sum_score_by_sentiment.png', 'Figure 8: Total engagement score by sentiment.')
add_summary('Positive reactions account for about 85% of all points earned platform-wide (756,304 of 893,482 total).')
add_chart('charts/sum_score_by_sentiment_and_year.png', 'Figure 9: Total engagement score by sentiment, comparing 2024 vs. 2025.')
add_summary('The positive-dominant pattern holds in both years -- the sentiment mix barely shifted from 2024 to 2025.')

add_subheading('Does Timing Matter?')
add_paragraph(
    'At first glance, 2024 shows noticeably more reactions than 2025 (about '
    '12,200 vs. 10,300). But this needs a closer look before drawing any '
    'conclusion from it: the dataset covers exactly one rolling year (mid-June '
    'to mid-June), not two complete calendar years -- so the 2024 label happens '
    'to cover about one extra month of data compared to 2025. Comparing only '
    'full months, the average reaction count per month is nearly identical '
    'between the two periods (about 1,898 vs. 1,862 per month). In other words, '
    'engagement did not meaningfully change year over year once the uneven date '
    'coverage is accounted for -- a useful reminder that a year-over-year chart '
    'can be misleading on its own without checking what date range each bar '
    'actually represents.'
)
add_paragraph(
    'Month by month, activity stayed fairly steady all year, with May the '
    'busiest month and February the quietest -- no strong seasonal pattern. '
    'Time of day made little difference either, with mornings only slightly '
    'busier than afternoons, evenings, or nights. Practically, this means '
    'Social Buzz does not need to time posts around a specific window; a '
    'simple, consistent publishing schedule captures engagement just as well, '
    'freeing attention to focus on content category and quality instead.'
)
add_chart('charts/reactions_by_year.png', 'Figure 10: Number of reactions by year.')
add_summary('The 2024-vs-2025 gap shown here is a date-range artifact (see the paragraph above), not a real change in engagement.')
add_chart('charts/reactions_by_month.png', 'Figure 11: Number of reactions by month, in calendar order.')
add_summary('Monthly totals stay within about 200 reactions of each other all year -- no clear seasonal pattern.')
add_chart('charts/reactions_by_time_of_day.png', 'Figure 12: Number of reactions by time of day.')
add_summary('All four time windows stay within about 220 reactions of each other -- timing has little effect on engagement.')

# ---------------------------------------------------------------------
# CONCLUSION
# ---------------------------------------------------------------------
pdf.add_page()
add_heading('Conclusion')
add_paragraph(
    'This project took three messy, separate spreadsheets -- 1,000 posts and '
    '25,553 raw reactions -- and turned them into one clean, unified table of '
    '22,534 usable records. Along the way, several real data problems had to be '
    'fixed: missing information, inconsistent text, and a confusing date format.'
)
add_paragraph(
    'The headline result: animals, science, healthy eating, technology, and food '
    'are the 5 content categories Social Buzz should invest in the most, since '
    'they earn the most positive reactions from users. This result was checked '
    'against a completely separate project using the same underlying data, and '
    'it matched exactly -- giving strong confidence that the finding is correct.'
)

# ---------------------------------------------------------------------
# LEARNINGS
# ---------------------------------------------------------------------
add_heading('Learnings')
add_bullet('How to clean up real, messy data: missing values, inconsistent text, and confusing date formats.')
add_bullet('How to combine multiple related spreadsheets into one table, and resolve naming clashes along the way.')
add_bullet('How to build both simple charts and interactive, clickable charts, with a consistent visual design.')
add_bullet('How to work with dates and times in code, including writing a small custom function from scratch.')
add_bullet("How to diagnose and fix a real problem caused by the computer's own settings, not just the code.")

# ---------------------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------------------
add_heading('Recommendations')
add_bullet('Invest more in animals, science, healthy eating, technology, and food content -- these are the categories users respond to most positively, together already earning 36% of all platform engagement.')
add_bullet('Because the top categories win on reaction VOLUME rather than reaction quality (the average score per reaction is nearly flat across every category), growing them further is a reach problem, not a content-quality problem -- prioritize distribution and discoverability (posting frequency, recommendation placement) for these categories over trying to make individual posts more "enthusiasm-worthy."')
add_bullet("Since most reactions (56%) are positive and only 31% are negative, the platform's overall mood is healthy -- but it's still worth keeping an eye on that negative third.")
add_bullet('Since reactions like "super love" and "adore" earn far more points than a plain "like," it may be worth encouraging users toward these stronger, more positive reactions.')
add_bullet("Content type and time of day don't meaningfully affect engagement right now, so no urgent change is needed on either front -- the one exception worth a closer look is the higher audio share within the top 5 categories specifically.")

pdf.output('Social_Buzz_Content_Analysis_Report.pdf')
print('PDF report saved as Social_Buzz_Content_Analysis_Report.pdf')
