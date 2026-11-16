"""Segment content taken from the client report "IF - Real Livelihoods Project Segmentation Report - V1"
(Nov 2026): segment overview slides, the youth segments overview table, pathway slides and opportunity
areas. This is the single source for the written content in both dashboards; scripts/export_nextjs_data.py
copies it into the Next.js data bundle.

Keys are the ANALYSIS segment codes used in every data file (precomputed/*.json and the self-assessment
model). The report numbers the segments differently, so the mapping is:

    code  report  name
     1      1     Survival Workers
     4      2     Stability Seekers
     2      3     Income Pragmatists
     3      4     Skill Investors
     5      5     Credentialed Aspirants
     6      6     Career Pursuers

Figures are rounded on purpose (feedback of 16.11.2026): people-counts to one decimal of a million,
percentages to whole numbers. Exact figures and the method notes live on the Methodology page.
"""

from __future__ import annotations

# Display order everywhere = the report's order.
ORDER = ["1", "4", "2", "3", "5", "6"]

NAMES = {
    "1": "Survival Workers",
    "4": "Stability Seekers",
    "2": "Income Pragmatists",
    "3": "Skill Investors",
    "5": "Credentialed Aspirants",
    "6": "Career Pursuers",
}

# Comparison rows for the "All segments" view (report: Youth segments overview table).
COMPARE_ROWS = [
    ("share", "Share of Kenyan youth (16-30), estimated"),
    ("population", "Young people, estimated"),
    ("rural", "Live in rural areas, estimated"),
    ("median_age", "Median age"),
    ("women", "Women"),
    ("median_income", "Median monthly income"),
    ("education", "Education route"),
    ("found_work", "How they found their current work"),
    ("work_meaning", "What work means to them"),
    ("stands_out", "Stands out on"),
]

PATHWAY_STAGE_KEYS = [
    ("education", "Educational preparation"),
    ("access", "Opportunity access"),
    ("establishment", "Livelihood establishment"),
    ("investment", "Upward investment"),
    ("advancement", "Livelihood advancement"),
]

SEGMENTS: dict[str, dict] = {
    "1": {
        "number": 1,
        "image": "Survival workers.png",
        "slug": "survival-workers",
        "traits": ["Resource-constrained", "Reactive", "Survival-oriented"],
        "tagline": "Prioritising immediate income to make ends meet over future progression",
        "insight": (
            "4.3M young people in Kenya are Survival Workers, the largest segment. They are the youngest group and "
            "most often left school early to earn. Almost all of them find work only through family and friends, "
            "so their options stop at whatever casual work people nearby can offer."
        ),
        "narrative": [
            "Survival Workers are mostly rural young people with little schooling, and most of them are women. Many "
            "entered work early to meet immediate financial and childcare needs, often leaving school before "
            "finishing secondary. Most rely on irregular, low-paid casual work in domestic work, micro-retail and "
            "manual labour, and switch jobs often to make ends meet.",
            "With unpredictable earnings, few side incomes and little savings, they struggle to cover basic needs, "
            "let alone invest in their futures. Many hope for more stable work, but caregiving and money pressures "
            "make progress hard. Seeing work mainly as a way to survive, they often accept harsh conditions, because "
            "even difficult work is better than no income.",
        ],
        "quote": ("I reached Class 4... I didn't go to any college to learn how to wash clothes or haul water. You "
                  "just start doing it... Sometimes you pull water carts the whole day and get nothing."),
        "enablers": ["Willingness to take on many kinds of work to earn"],
        "barriers": ["Low education, limited training and unaffordable upskilling",
                     "Seasonal, financial and employment shocks", "Little reliable childcare"],
        "stats": {"share": "32%", "population": "4.3M", "rural": "69%", "median_age": "21", "women": "62%",
                  "median_income": "KES 5K"},
        "compare": {
            "education": "Most left school early (about a third finished secondary)",
            "found_work": "Family and friends (97%)",
            "work_meaning": "A means to an end (97%)",
            "stands_out": "Lowest saving (25%) and fewest side incomes (9%); most likely to live with family (55%)",
        },
        "pathway_summary": (
            "Survival Workers often leave school early to earn, entering low-paid domestic work, micro-retail or "
            "manual labour through family and friends. They take whatever work is available and move between jobs "
            "when pay falls short, work dries up or mistreatment becomes intolerable. With close to half not "
            "earning at the moment and most unable to cover basic needs, they have little room to search widely or "
            "invest in skills."
        ),
        "aspirations": {
            "education": "Plans to continue education have been left behind",
            "access": "Find casual work through people they know, to support themselves and their family and save a little",
            "establishment": "Need support to make their livelihood more stable",
        },
        "opportunities": [
            ("Education & upskilling", "Practical paid training",
             "Short vocational courses and paid apprenticeships in accessible trades, so they can build skills "
             "without giving up the income their households depend on."),
            ("Work access", "Childcare support near work",
             "Affordable, flexible childcare near markets, farms and training sites, including emergency cover, so "
             "parents can take shifts and training."),
            ("Work access", "Extend trusted local work referrals",
             "Build on word-of-mouth networks through community organisations, local employers and SMS alerts to "
             "reach verified, recurring work beyond close family."),
            ("Work access", "Reduce job-search costs",
             "Transport support for interviews, employer visits and work travel, so they can look beyond nearby "
             "casual jobs."),
            ("Income generation", "Group-based local income activities",
             "Shared enterprises in locally relevant activities such as poultry, horticulture or food processing, "
             "spreading learning and risk across members."),
            ("Income generation", "Strengthen existing micro-businesses",
             "Business skills and micro-loans for youth already running small shops, food vending or services."),
            ("Shock resilience", "Saving on low, irregular incomes",
             "Savings groups, flexible small-deposit accounts and money coaching to set money aside in better weeks."),
            ("Shock resilience", "One-to-one mental health support",
             "Confidential support through trusted community facilitators for those who feel isolated."),
        ],
    },
    "4": {
        "number": 2,
        "image": "Stability Seekers.png",
        "slug": "stability-seekers",
        "traits": ["Relationship-dependent", "Asset-aspiring", "Autonomy-oriented"],
        "tagline": "Piecing together locally available, hands-on work, without a fixed occupational path",
        "insight": (
            "1.3M young people in Kenya are Stability Seekers. Nearly all of them learned their skills as informal "
            "apprentices, on the job, from people they know. They combine several kinds of hands-on local work "
            "(farm labour, building, trades, small business) to keep earning, and most are men."
        ),
        "narrative": [
            "Stability Seekers are largely rural, mostly young men, many with limited secondary education, who rely "
            "on practical skills learned through apprenticeships and on-the-job training. Many live independently, "
            "head their own households and send money to relatives, so a steady income is essential. They move "
            "between casual labour, trades, farming and small businesses, often combining seasonal work.",
            "They lean on family and friends for both work and training, and learn by doing rather than through "
            "formal courses. Many want to build assets or grow a business, but irregular earnings and little savings "
            "make progress difficult. They believe hard work can improve their lives, yet often lack a clear path to "
            "more secure livelihoods.",
        ],
        "quote": ("I do farm labor for others, I grow my own vegetables at home, I do tailoring, and I used to sell "
                  "second-hand clothes and cook samosas... But when students went away on break, I decided to do "
                  "stone quarry mining."),
        "enablers": ["Trusted networks that offer work and learning",
                     "Practical skills gained through apprenticeships and hands-on work"],
        "barriers": ["Irregular earnings and little savings to manage shortfalls",
                     "Unclear progression paths and limited access to assets"],
        "stats": {"share": "10%", "population": "1.3M", "rural": "65%", "median_age": "23", "women": "38%",
                  "median_income": "KES 7.5K"},
        "compare": {
            "education": "Informal apprenticeship (96%)",
            "found_work": "Family and friends (95%)",
            "work_meaning": "A means to an end (99%)",
            "stands_out": "Learn on the job; mostly men (62%)",
        },
        "pathway_summary": (
            "With limited access to further education, Stability Seekers enter work through family and friends who "
            "offer jobs or teach them a trade. They often move between casual labour, farming and artisan work after "
            "a few months, as work dries up or better-paid work appears through their networks. This keeps them "
            "earning, but they may move on before building deep expertise in one trade."
        ),
        "aspirations": {
            "education": "Earlier hopes of vocational training and certification have lapsed",
            "access": "Build personal relationships to reach work",
            "establishment": "Secure consistent work with fair treatment and pay",
            "investment": "Need support to see a growth path and build skills",
            "advancement": "Need support to build personal and business assets, such as livestock",
        },
        "opportunities": [
            ("Education & upskilling", "Upgrade and certify trade skills",
             "Help experienced workers deepen skills in mechanics, welding, plumbing and construction, and use "
             "existing recognition-of-prior-learning (RPL) trade tests to gain recognised credentials."),
            ("Education & upskilling", "Create trade progression pathways",
             "Link informal apprentices to advanced tasks and independent contracts, with clearer routes to "
             "becoming master craft workers or employers."),
            ("Work access", "Secure regular work and contracts",
             "Connect artisans and casual workers with contractors, SMEs and county projects for repeat and "
             "longer-term work."),
            ("Work access", "Coordinate seasonal work",
             "Coordinate labour demand across farming, construction and local services so earnings continue between "
             "seasons."),
            ("Income generation", "Finance productive trade assets",
             "Affordable loans or lease-to-own options for tools, equipment and livestock."),
            ("Income generation", "Strengthen small rural businesses",
             "Practical help with pricing, stock, record-keeping and registration."),
            ("Income generation", "Expand women's market access",
             "Bring market information, buyers and shared transport closer to women who face mobility limits."),
            ("Shock resilience", "Safer emergency finance",
             "Responsible, affordable emergency credit and savings so households avoid cutting meals in lean "
             "seasons."),
            ("Shock resilience", "Health support for manual workers",
             "Guidance on managing physical strain, recognising health risks and seeking care."),
        ],
    },
    "2": {
        "number": 3,
        "image": "Income Pragmatists.png",
        "slug": "income-pragmatists",
        "traits": ["Practical", "Adaptive", "Lifestyle-oriented"],
        "tagline": "Moving selectively between opportunities in search of better pay and conditions",
        "insight": (
            "2.7M young people in Kenya are Income Pragmatists. Most finished secondary school, and they judge any "
            "job or course by what it pays. They are the most likely to save and the most likely to take short "
            "formal courses outside university, and they will switch work quickly when the pay or conditions are "
            "better elsewhere."
        ),
        "narrative": [
            "Income Pragmatists are secondary-educated young adults across Kenya who put earning potential ahead of "
            "a particular career. Most live independently and many support parents, relatives or children, so "
            "reliable income is essential. They gravitate to self-employment, micro-retail and skilled trades, often "
            "combining several income streams to manage seasonal swings.",
            "Rather than stay in poorly paid roles, they look for better opportunities through personal networks "
            "and invest in TVET and job-linked training when it promises higher earnings. Although nearly half "
            "struggle to meet basic needs, many save regularly and are optimistic about the future.",
        ],
        "quote": ("I washed my hands of wage employment... when payday comes, the salary doesn't change... But with "
                  "self-employment, it depends on your own effort: my hard work is what brings in higher earnings."),
        "enablers": ["Active use of personal and digital networks to find opportunities",
                     "Savings and extra income streams"],
        "barriers": ["Seasonal earnings that do not cover basic needs",
                     "Poor working conditions leading to losing or leaving work"],
        "stats": {"share": "20%", "population": "2.7M", "rural": "57%", "median_age": "24", "women": "52%",
                  "median_income": "KES 10K"},
        "compare": {
            "education": "Secondary (87%) and TVET (40%)",
            "found_work": "Family and friends (96%)",
            "work_meaning": "A means to an end (100%)",
            "stands_out": "Most formal upskilling outside university (38%); most likely to save (61%)",
        },
        "pathway_summary": (
            "Income Pragmatists may take vocational training to raise their earnings, but find that qualifications "
            "alone do not guarantee work. They use family, friends, digital tools and contacts to find better-paid "
            "work, and switch or combine activities when earnings fall short. Some invest in short, job-linked "
            "training when they expect it to pay off. Many want to become self-employed, but raising capital is hard."
        ),
        "aspirations": {
            "education": "Gain a certificate through vocational education and training",
            "access": "Build a local professional network to reach better-paid work",
            "establishment": "Reach financial stability with room to save",
            "investment": "Invest in on-the-job training that unlocks better-paid work",
            "advancement": "Need support to set up a small business",
        },
        "opportunities": [
            ("Education & upskilling", "Link TVET to paid work",
             "Work with employers and TVET providers to shape courses around real vacancies and hiring needs."),
            ("Education & upskilling", "Free training for higher-return work",
             "Short (under three months), free training in digital services and skilled trades with proven earning "
             "potential."),
            ("Work access", "Connect to emerging work",
             "Employer and sector partnerships into better-paid work in technology, hospitality, transport and "
             "growing services."),
            ("Work access", "Widen access beyond personal networks",
             "Verified vacancies through digital matching and county employment channels, shared on WhatsApp and "
             "other familiar channels."),
            ("Income generation", "Find higher-return business opportunities",
             "Market information and business assessment to compare margins, demand and investment needs before "
             "switching ventures."),
            ("Income generation", "Finance micro-retail growth",
             "Affordable working capital for stock, equipment or premises, instead of costly mobile loans."),
            ("Shock resilience", "Turn savings into financial security",
             "Help regular savers build emergency buffers and choose suitable investments."),
            ("Shock resilience", "Reliable mental health support",
             "Use familiar digital channels to point young people to credible, free helplines and professional "
             "services."),
        ],
    },
    "3": {
        "number": 4,
        "image": "Skill Investors.png",
        "slug": "skill-investors",
        "traits": ["Curious", "Self-driven", "Vocation-oriented"],
        "tagline": "Investing in skills and a trade as a route to better opportunities",
        "insight": (
            "2.7M young people in Kenya are Skill Investors. What sets them apart is that their trade is part of "
            "who they are, not just a way to earn. They keep learning from mentors, peers and online videos, but "
            "without recognised certificates their skills often do not turn into steady, better-paid work."
        ),
        "narrative": [
            "Skill Investors are largely rural young people who build their livelihoods around practical trades "
            "rather than formal qualifications. Many finished secondary school, and family occupations, informal "
            "apprenticeships and TVET give them hands-on routes into work. They identify strongly with their "
            "vocation and keep learning through mentors, peers, practice and digital self-study.",
            "Their trade brings moderate, irregular earnings, so many top up with casual labour or seasonal side "
            "work. They rely on personal networks for work and hope that showing their skills will open better "
            "doors. They want to master their trade, but struggle to see a clear path from skill to financial "
            "security.",
        ],
        "quote": ("I was once called for a job doing door joinery in apartment blocks, but because I lacked "
                  "certification papers, the opportunity slipped away."),
        "enablers": ["Self-directed learning and continuous skill building",
                     "Practical family support for training and finding work"],
        "barriers": ["Skills are not recognised without formal credentials",
                     "Reliance on trusted personal networks rather than wider professional contacts"],
        "stats": {"share": "21%", "population": "2.7M", "rural": "66%", "median_age": "23", "women": "53%",
                  "median_income": "KES 7.5K"},
        "compare": {
            "education": "Secondary (63%), with a mix of apprenticeship and TVET",
            "found_work": "Family and friends (97%)",
            "work_meaning": "Part of their identity (100%)",
            "stands_out": "Strong trade identity; learn informally or through apprenticeships",
        },
        "pathway_summary": (
            "Skill Investors enter trades through family occupations, apprenticeships or TVET, and put practical "
            "mastery ahead of formal qualifications. They deepen their skills through experience, mentors and "
            "online learning, and look for customers and employers through personal networks. Irregular earnings "
            "push many into casual or seasonal work, while missing credentials and connections keep better-paid "
            "work out of reach."
        ),
        "aspirations": {
            "education": "Gain skills and certificates through tertiary education or on-the-job training",
            "access": "Need support to win good work with leading employers",
            "establishment": "Gain industry experience in safe, supportive workplaces",
            "investment": "Master their trade and build real expertise",
            "advancement": "Need support to find stable employment or start a business in their trade",
        },
        "opportunities": [
            ("Education & upskilling", "Raise awareness of skills recognition",
             "Explain existing recognition-of-prior-learning (RPL) trade tests: who is eligible, how to apply and "
             "how to get a recognised credential for experience."),
            ("Education & upskilling", "Curate practical digital learning",
             "Local YouTube and TikTok learning paths for trades, paired with mentor feedback."),
            ("Education & upskilling", "Build business skills",
             "Trade-specific learning in pricing, bookkeeping, customer service and marketing."),
            ("Work access", "Connect trades to larger contracts",
             "Broker links between local artisans and contractors on housing, infrastructure and value-chain "
             "projects."),
            ("Work access", "Prepare for formal work",
             "Help with documents, work histories and simple digital profiles needed for contracts and jobs."),
            ("Income generation", "Grow trade-related side businesses",
             "Coaching and capital to turn seasonal side work into services linked to their main trade."),
            ("Income generation", "Finance tools for trade growth",
             "Affordable loans or shared access to trade tools and materials."),
            ("Shock resilience", "Reduce dependence on mobile loans",
             "Responsible small-scale credit and borrowing guidance for seasonal income gaps."),
            ("Shock resilience", "Extend mentorship to wellbeing",
             "Equip trusted trade mentors to support young people through stress and setbacks."),
        ],
    },
    "5": {
        "number": 5,
        "image": "Credentialed Aspirants.png",
        "slug": "credentialed-aspirants",
        "traits": ["Aspirational", "Persistent", "Stability-oriented"],
        "tagline": "Looking for work that matches their qualifications while juggling informal work to stay afloat",
        "insight": (
            "About half a million young people in Kenya are Credentialed Aspirants, the smallest segment. All of "
            "them hold a university degree and they are the most active users of AI for learning. Yet many still "
            "take informal or lower-status work, sometimes hiding it, while they search for jobs that match their "
            "education."
        ),
        "narrative": [
            "Credentialed Aspirants are university-educated young men and women, mostly in urban Kenya, who expected "
            "their education to open doors to stable, respected careers. Many head their own households and support "
            "their families. They aim for formal employment, digital work and business ownership, and look for "
            "opportunities through job portals, mentors and professional networks.",
            "Their qualifications bring both pride and pressure: they want work that reflects their education and "
            "the progress their families expected. Some hide manual or lower-status work from their communities "
            "even as they take it to meet their needs. They stay optimistic, but are frustrated by hiring that often "
            "seems to favour connections over qualifications.",
        ],
        "quote": ("I'm a registered nurse with a degree, but I'm currently unemployed and rely on occasional "
                  "shifts... It can be discouraging, but I believe I'm on the right career path and hope to "
                  "specialize."),
        "enablers": ["University degrees and professional qualifications",
                     "Continued upskilling, freelancing and digital skills", "Regular saving"],
        "barriers": ["Hiring seen to favour connections over qualifications",
                     "Family financial obligations and high living costs"],
        "stats": {"share": "4%", "population": "0.5M", "rural": "39%", "median_age": "25", "women": "49%",
                  "median_income": "KES 18K"},
        "compare": {
            "education": "University degree (100%)",
            "found_work": "Half through formal channels (49%), half through family and friends",
            "work_meaning": "Mostly a means to an end (83%)",
            "stands_out": "Highest AI use for learning (59%); most willing to take work others look down on (45%)",
        },
        "pathway_summary": (
            "Credentialed Aspirants pursue degrees expecting stable, respected careers. After graduating they apply "
            "for formal roles; those who approach mentors often find jobs sooner. To cover costs, most turn to "
            "personal connections for digital gigs and side hustles while they keep applying and build their CVs "
            "through internships and courses."
        ),
        "aspirations": {
            "education": "Earn a degree or diploma for social recognition",
            "access": "Need support to secure institutional work that matches their qualifications",
            "establishment": "Reach a stable livelihood and financial stability",
            "investment": "Add formal credentials to progress in their careers",
            "advancement": "Need support to progress in a salaried profession or start their own business",
        },
        "opportunities": [
            ("Education & upskilling", "Workplace-readiness curriculum",
             "Build CV writing, interviewing and employer expectations into university programmes."),
            ("Education & upskilling", "Advanced digital capabilities",
             "Market-linked training in data, AI and other advanced digital skills."),
            ("Work access", "Expand graduate placements",
             "Structured partnerships between universities, colleges and employers for entry-level roles."),
            ("Work access", "Widen access through professional mentors",
             "Connect graduates without industry contacts to mentors who can guide and introduce them."),
            ("Work access", "Explain how to get into the job market",
             "Make public- and private-sector recruitment processes and entry routes clear."),
            ("Work access", "Connect graduates to incubators",
             "Raise awareness of existing incubators and enterprise support and how to join them."),
            ("Income generation", "Finance graduate-led small businesses",
             "Suitably structured finance for equipment, working capital and expansion."),
            ("Income generation", "Connect freelancers with verified clients",
             "Link digital freelancers to vetted clients and trusted platforms."),
            ("Shock resilience", "Mental health support in institutions",
             "Confidential counselling in universities and institutions, and awareness of reliable help."),
        ],
    },
    "6": {
        "number": 6,
        "image": "Carer Pursuers.png",
        "slug": "career-pursuers",
        "traits": ["Self-starters", "Network-engaged", "Progression-oriented"],
        "tagline": "Shaping their own progress by drawing on credentials, professional contacts and work experience",
        "insight": (
            "1.8M young people in Kenya are Career Pursuers. Their key difference: they get work through job "
            "applications, mentors and professional contacts, and hardly ever through family and friends. They are "
            "also the most likely of all segments to say their education or training was worth it."
        ),
        "narrative": [
            "Career Pursuers are young men and women across Kenya with moderate education who live independently "
            "and want more secure livelihoods. Most finished secondary school, and nearly half have taken vocational "
            "qualifications or apprenticeships. They work across wage jobs, casual labour, retail and skilled "
            "trades, and often earn more than peers without degrees.",
            "They actively seek opportunities through mentors, professional networks and formal applications. Many "
            "save and feel able to handle financial shocks, but earnings don't always cover basic needs and family "
            "contributions, so they lean on family and side work. They see education and training as investments "
            "and are optimistic that initiative and continued learning will pay off.",
        ],
        "quote": ("You know connections are everything... I stay in this job because I want to observe how my boss "
                  "runs his business and deals with customers, so that later I can also set up my own small "
                  "hardware shop."),
        "enablers": ["Mentors, professional networks and proactive job searching",
                     "Savings and several income streams"],
        "barriers": ["Late wages and seasonal work create financial uncertainty",
                     "Unclear hiring processes for institutional jobs"],
        "stats": {"share": "14%", "population": "1.8M", "rural": "57%", "median_age": "24", "women": "51%",
                  "median_income": "KES 9.5K"},
        "compare": {
            "education": "Secondary (76%) and TVET (27%)",
            "found_work": "Job applications, mentors and professional contacts (100%)",
            "work_meaning": "Mostly a means to an end (76%); part of their identity for 24%",
            "stands_out": "Most likely to value their education or training (66%); strongest sense of agency (94%)",
        },
        "pathway_summary": (
            "Career Pursuers enter work through family trades or vocational training, using mentors, professional "
            "networks and direct applications to get early opportunities. They choose roles that build experience "
            "and add TVET qualifications, workshops and on-the-job learning. When pay is late or work is seasonal, "
            "they draw on family, savings and side work rather than give up their main livelihood."
        ),
        "aspirations": {
            "education": "Learn on the job alongside education or training, to build skills and contacts",
            "access": "Secure an entry-level role in the occupation they want",
            "establishment": "Gain relevant industry experience",
            "investment": "Secure formal, stable employment or start a business in their chosen career",
            "advancement": "Need support to serve their community through services and leadership",
        },
        "opportunities": [
            ("Education & upskilling", "Flexible TVET for working youth",
             "Modular, evening and blended TVET so they can earn recognised qualifications without losing income."),
            ("Education & upskilling", "Skills for livelihood growth",
             "Practical learning in business management, finding customers and navigating the workplace."),
            ("Work access", "From casual work to contracts",
             "Partner with employers to create routes from casual work into longer contracts with predictable pay."),
            ("Work access", "Widen access to professional networks",
             "Peer and mentor networks that share vacancies, industry knowledge and introductions."),
            ("Work access", "Open trades to more women",
             "Work with trade associations and women practitioners to widen young women's access to male-dominated "
             "trades."),
            ("Income generation", "Reach markets in other counties",
             "Link skilled workers and small traders to customers and projects in neighbouring counties."),
            ("Income generation", "Grow side businesses",
             "Coaching, growth capital and customer links to turn skills and side activities into extra income."),
            ("Shock resilience", "Build emergency financial buffers",
             "Savings groups and responsible emergency finance for income gaps."),
            ("Shock resilience", "Strengthen peer support",
             "Facilitated peer groups to talk through career uncertainty, setbacks and money pressure."),
        ],
    },
}

# Study context for the Overview and Methodology pages (report: Project overview).
STUDY = {
    "why": [
        ("Learning to earning is not a straight line",
         "Kenyan youth learn and earn at the same time and move between formal and informal work. Existing data "
         "misses many of these transitions."),
        ("Programmes lag reality",
         "Most models assume formal jobs and step-by-step progress, and track proxies such as enrolment rather than "
         "what drives a stable income."),
        ("A job is not a livelihood",
         "Being employed does not guarantee a decent or rising income. The question is what helps young people "
         "earn, grow and support others."),
    ],
    "what": (
        "Imaginable Futures is developing a multi-year Kenya strategy on education and the move into sustainable, "
        "rewarding livelihoods. This study grounds that strategy in evidence on the routes young people actually "
        "take. It combined in-depth conversations with 51 young people in four locations with a survey of 1,221 "
        "young people in nine counties (August to September 2026), and grouped them into six "
        "segments that share circumstances, behaviours and mindsets."
    ),
}
