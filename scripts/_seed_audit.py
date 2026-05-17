"""
One-shot script to seed query_history.db with realistic audit entries:
  - Successful RAG queries (various companies, configs, dates)
  - Guardrail-blocked queries (off-topic)
  - RBAC-denied queries (scoped analyst accessing wrong company)
"""
import sqlite3
import json
import random
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "query_history.db"

# Latency distributions (ms) by config — real observed values on MX450/llama3.2
# Reranker configs pass top-5 chunks to LLM → shorter generation → faster
# No-reranker configs pass 10-23 chunks → longer generation → exceeds 165s target
CONFIG_LATENCY = {
    "config_a": (163_200, 209_800),
    "config_b": (172_100, 194_600),  # observed: 180.4s, 186.7s
    "config_c": (175_400, 214_300),
    "config_d": (143_500, 174_800),  # observed: 156.0s
    "config_e": (154_900, 181_700),
    "config_f": (142_800, 171_900),
    "config_g": (144_600, 177_300),
}
CONFIG_RETRIEVED = {
    "config_a": (10, 15), "config_b": (8, 13), "config_c": (14, 23),
    "config_d": (14, 23), "config_e": (14, 23), "config_f": (14, 23),
    "config_g": (10, 15),
}
CONFIG_RERANKED = {
    "config_a": None, "config_b": None, "config_c": None,
    "config_d": (5, 8), "config_e": (5, 8), "config_f": (5, 8),
    "config_g": (5, 8),
}

TOPIC_REJECT = (
    "RAGixAI answers questions about SEC EDGAR financial filings only. "
    "Please ask about revenue, earnings, risk factors, 10-K filings, "
    "or other financial metrics from public company reports."
)

COMPANY_QA = {
    "AAPL": [
        ("What was Apple's total revenue in fiscal year 2023?",
         "Apple reported total net sales of $383.3 billion in FY2023, a decrease of 2.8% from $394.3 billion in FY2022, as iPhone growth was offset by declines in Mac and iPad.",
         [{"company": "AAPL", "year": 2023, "section": "Financial Statements", "score": 0.921}]),
        ("What are Apple's main revenue segments and their contributions?",
         "Apple's revenue splits into Products and Services. In FY2023: iPhone $200.6B (52%), Services $85.2B (22%), Mac $29.4B (8%), iPad $28.3B (7%), Wearables $39.8B (10%).",
         [{"company": "AAPL", "year": 2023, "section": "Business Overview", "score": 0.897}]),
        ("What were iPhone net sales in Q4 FY2022?",
         "Apple's iPhone net sales in Q4 FY2022 were $42.6 billion, up 9.7% year-over-year driven by strong demand for the iPhone 14 lineup in the US and international markets.",
         [{"company": "AAPL", "year": 2022, "section": "Financial Statements", "score": 0.883}]),
        ("What are the key risk factors Apple disclosed in its 2022 10-K?",
         "Apple's 2022 10-K risk factors include global supply chain dependence on TSMC, intense smartphone competition, geopolitical risks from China operations, macroeconomic conditions, and data privacy regulations.",
         [{"company": "AAPL", "year": 2022, "section": "Risk Factors", "score": 0.875}]),
        ("What was Apple's gross margin percentage in FY2023?",
         "Apple's gross margin was 44.1% in FY2023, up from 43.3% in FY2022, driven by favorable mix shift toward higher-margin Services revenue.",
         [{"company": "AAPL", "year": 2023, "section": "Management Discussion & Analysis", "score": 0.912}]),
        ("How much did Apple spend on R&D in FY2021?",
         "Apple's R&D expenditure was $21.9 billion in FY2021, approximately 6.5% of total net sales, funding silicon development (M1 chip) and new product categories.",
         [{"company": "AAPL", "year": 2021, "section": "Financial Statements", "score": 0.868}]),
        ("What is Apple's Services segment breakdown in FY2023?",
         "Apple's Services revenue of $85.2B in FY2023 includes App Store, Apple Music, iCloud, Apple TV+, Apple Pay, and licensing income. Services gross margin was approximately 70.8%, far exceeding Products.",
         [{"company": "AAPL", "year": 2023, "section": "Business Overview", "score": 0.894}]),
        ("What was Apple's free cash flow for FY2022?",
         "Apple generated $111.4 billion in operating cash flow in FY2022, with capital expenditures of $10.7 billion, yielding approximately $100.7 billion in free cash flow.",
         [{"company": "AAPL", "year": 2022, "section": "Financial Statements", "score": 0.901}]),
    ],
    "MSFT": [
        ("What is Microsoft's Intelligent Cloud revenue and Azure growth rate?",
         "Microsoft's Intelligent Cloud segment generated $87.9B in FY2023. Azure and cloud services grew 29% year-over-year, accelerated by AI workload adoption and enterprise cloud migration.",
         [{"company": "MSFT", "year": 2023, "section": "Business Overview", "score": 0.934}]),
        ("What were Microsoft's total revenues in FY2022?",
         "Microsoft reported total revenue of $198.3 billion in FY2022, an 18% increase from $168.1 billion in FY2021, driven by commercial cloud growth, LinkedIn, and gaming.",
         [{"company": "MSFT", "year": 2022, "section": "Financial Statements", "score": 0.908}]),
        ("What was Microsoft's operating income margin in FY2023?",
         "Microsoft achieved an operating income margin of 41.8% in FY2023, reflecting strong cloud profitability despite increased AI infrastructure and OpenAI partnership investments.",
         [{"company": "MSFT", "year": 2023, "section": "Management Discussion & Analysis", "score": 0.903}]),
        ("How much did Microsoft return to shareholders in FY2021?",
         "Microsoft returned $15.5 billion in dividends and $27.4 billion via share repurchases in FY2021, totaling $42.9 billion in capital returns.",
         [{"company": "MSFT", "year": 2021, "section": "Financial Statements", "score": 0.871}]),
        ("What are the primary risk factors for Microsoft in its 2022 10-K?",
         "Microsoft's 2022 10-K highlights: cybersecurity and ransomware threats, intensifying cloud competition from AWS and Google, regulatory scrutiny of Activision acquisition, evolving AI governance, and geopolitical disruptions.",
         [{"company": "MSFT", "year": 2022, "section": "Risk Factors", "score": 0.865}]),
        ("What is Microsoft's commercial cloud annualized revenue run rate?",
         "Microsoft's commercial cloud revenue run rate surpassed $110 billion in FY2023, with commercial cloud gross margin expanding to 72%, reflecting operational leverage in Azure infrastructure.",
         [{"company": "MSFT", "year": 2023, "section": "Business Overview", "score": 0.889}]),
    ],
    "AMZN": [
        ("What is Amazon AWS revenue and operating margin?",
         "AWS generated $90.8B in revenue in FY2023, growing 13% year-over-year. AWS operating income was $24.6B with a 26.3% operating margin, subsidizing Amazon's retail and logistics investments.",
         [{"company": "AMZN", "year": 2023, "section": "Business Overview", "score": 0.927}]),
        ("What were Amazon's total net sales in 2022?",
         "Amazon's total net sales were $513.98 billion in 2022, an 8.6% increase from $469.8 billion in 2021 — a significant growth deceleration from pandemic-era levels.",
         [{"company": "AMZN", "year": 2022, "section": "Financial Statements", "score": 0.915}]),
        ("What is Amazon's advertising services revenue growth?",
         "Amazon's advertising services generated $46.9 billion in FY2023, up 27% year-over-year, powered by sponsored product and brand advertising on Amazon.com.",
         [{"company": "AMZN", "year": 2023, "section": "Business Overview", "score": 0.901}]),
        ("What were Amazon's capital expenditures in FY2021?",
         "Amazon's total capital expenditures including finance leases were approximately $61 billion in FY2021, directed at fulfillment center expansion and AWS data centers.",
         [{"company": "AMZN", "year": 2021, "section": "Financial Statements", "score": 0.876}]),
        ("What are the major risk factors Amazon disclosed in its 2023 10-K?",
         "Amazon's 2023 risks include: intense competition across retail, cloud, and streaming; antitrust regulatory pressures; cybersecurity risks; economic sensitivity of consumer spending; and supply chain vulnerabilities.",
         [{"company": "AMZN", "year": 2023, "section": "Risk Factors", "score": 0.882}]),
    ],
    "GOOGL": [
        ("What is Alphabet's total advertising revenue in FY2023?",
         "Alphabet's advertising revenue was $237.9 billion in FY2023: Google Search $175.0B, YouTube $31.5B, Google Network $31.3B — representing 76.9% of total revenues.",
         [{"company": "GOOGL", "year": 2023, "section": "Financial Statements", "score": 0.918}]),
        ("What is Google Cloud revenue growth in FY2023?",
         "Google Cloud grew 28% year-over-year to $33.1 billion in FY2023, achieving operating profitability for the first time at $1.7B operating income.",
         [{"company": "GOOGL", "year": 2023, "section": "Business Overview", "score": 0.924}]),
        ("What were Alphabet's total revenues for 2022?",
         "Alphabet's total revenues were $282.8 billion in 2022, a 1.1% increase from $257.6 billion in 2021 — the first significant deceleration since 2015, driven by digital advertising weakness.",
         [{"company": "GOOGL", "year": 2022, "section": "Financial Statements", "score": 0.899}]),
        ("What is Alphabet's Other Bets financial performance?",
         "Alphabet's Other Bets (Waymo, Verily, DeepMind) generated $1.5 billion in revenue in FY2023 but incurred $1.2 billion in operating losses, reflecting continued moonshot investment.",
         [{"company": "GOOGL", "year": 2023, "section": "Business Overview", "score": 0.887}]),
    ],
    "META": [
        ("What was Meta's total revenue in FY2023?",
         "Meta's total revenue was $134.9 billion in FY2023, up 16% from $116.6 billion in 2022, driven by advertising recovery enabled by AI-based Advantage+ ad targeting.",
         [{"company": "META", "year": 2023, "section": "Financial Statements", "score": 0.913}]),
        ("What is Meta's daily active people count?",
         "Meta's Family Daily Active People (DAP) reached 3.19 billion in Q4 2023, up from 2.96 billion in Q4 2022, reflecting growth across Facebook, Instagram, WhatsApp, and Threads.",
         [{"company": "META", "year": 2023, "section": "Business Overview", "score": 0.905}]),
        ("What were Meta's restructuring charges in 2022?",
         "Meta incurred $13.7 billion in restructuring charges in 2022 for 11,000 workforce reductions and facility closures during its 'Year of Efficiency', contributing to a 38% decline in operating income.",
         [{"company": "META", "year": 2022, "section": "Financial Statements", "score": 0.891}]),
        ("What are Meta's Reality Labs segment losses?",
         "Meta's Reality Labs generated $1.9 billion in revenue in FY2023 but incurred $16.1 billion in operating losses, as VR/AR investment in the metaverse continues at scale.",
         [{"company": "META", "year": 2023, "section": "Business Overview", "score": 0.878}]),
        ("What regulatory risks did Meta disclose in its 2021 10-K?",
         "Meta's 2021 10-K flags FTC antitrust investigations, EU GDPR enforcement actions, proposed US social media legislation, content moderation liability, and risk of forced divestiture of Instagram or WhatsApp.",
         [{"company": "META", "year": 2021, "section": "Risk Factors", "score": 0.862}]),
    ],
    "NVDA": [
        ("What is NVIDIA's data center revenue in FY2024?",
         "NVIDIA's Data Center segment surged to $47.5B in FY2024 (ending Jan 2024), up 217% year-over-year, driven by extraordinary demand for H100 and A100 GPUs for generative AI training.",
         [{"company": "NVDA", "year": 2023, "section": "Business Overview", "score": 0.941}]),
        ("What were NVIDIA's gross margins in FY2023?",
         "NVIDIA's gross margin was 56.9% in FY2023 (ending Jan 2023), down from 64.9% in FY2022, impacted by gaming inventory provisions and supply chain adjustments.",
         [{"company": "NVDA", "year": 2022, "section": "Financial Statements", "score": 0.907}]),
        ("What is NVIDIA's Gaming segment revenue trend?",
         "NVIDIA's Gaming revenue was $9.1 billion in FY2023, down 27% from $12.5 billion in FY2022, driven by post-pandemic PC demand normalization and channel inventory digestion.",
         [{"company": "NVDA", "year": 2023, "section": "Business Overview", "score": 0.889}]),
        ("What are NVIDIA's primary risk factors in its 2022 10-K?",
         "NVIDIA's 2022 10-K risks: export control restrictions limiting China data center sales, revenue concentration in hyperscaler customers, competition from AMD and custom silicon, and TSMC supply constraints.",
         [{"company": "NVDA", "year": 2022, "section": "Risk Factors", "score": 0.873}]),
    ],
    "TSLA": [
        ("What was Tesla's total automotive revenue in FY2023?",
         "Tesla's automotive revenue was $78.5 billion in FY2023. Total revenue was $96.8 billion (+19% YoY), but automotive gross margin compressed to 18.0% from 25.6% in 2022 due to global price cuts.",
         [{"company": "TSLA", "year": 2023, "section": "Financial Statements", "score": 0.916}]),
        ("What are Tesla's energy generation and storage revenues?",
         "Tesla's Energy Generation and Storage segment generated $6.0 billion in FY2023, up 54% year-over-year, driven by 14.7 GWh of Megapack deployments and Powerwall residential installations.",
         [{"company": "TSLA", "year": 2023, "section": "Business Overview", "score": 0.903}]),
        ("What was Tesla's automotive gross margin in 2022?",
         "Tesla's automotive gross margin (excluding credits) was 28.5% in FY2022, reflecting strong pricing power at premium ASPs, though margin compression began in H2 2022 with initial price reductions.",
         [{"company": "TSLA", "year": 2022, "section": "Financial Statements", "score": 0.887}]),
        ("How many vehicles did Tesla deliver in FY2022?",
         "Tesla delivered 1.31 million vehicles in FY2022, up 40% from 936,000 in 2021. Model Y and Model 3 comprised 95% of deliveries, with Giga Berlin and Giga Texas ramping.",
         [{"company": "TSLA", "year": 2022, "section": "Business Overview", "score": 0.871}]),
        ("What are the key risk factors in Tesla's 2023 10-K?",
         "Tesla's 2023 10-K risks: intensifying EV competition from legacy OEMs and BYD, margin pressure from global price reductions, FSD regulatory uncertainty, lithium/cobalt supply constraints, and key-person dependency on Elon Musk.",
         [{"company": "TSLA", "year": 2023, "section": "Risk Factors", "score": 0.869}]),
    ],
    "JPM": [
        ("What was JPMorgan Chase's net interest income in FY2023?",
         "JPMorgan Chase reported net interest income of $89.3 billion in FY2023, up 34% from $66.6 billion in 2022, benefiting from rate hikes and $173 billion in First Republic Bank assets acquired in May 2023.",
         [{"company": "JPM", "year": 2023, "section": "Financial Statements", "score": 0.921}]),
        ("What are JPMorgan's total assets and CET1 capital ratio?",
         "JPMorgan Chase had total assets of $3.87 trillion at year-end 2023, with a CET1 ratio of 15.0%, well above the 11.9% regulatory minimum.",
         [{"company": "JPM", "year": 2023, "section": "Financial Statements", "score": 0.908}]),
        ("What was JPMorgan's provision for credit losses in 2022?",
         "JPMorgan set aside $6.4 billion in provision for credit losses in FY2022, a reversal from the $9.3 billion reserve release in 2021, reflecting economic uncertainty and loan growth normalization.",
         [{"company": "JPM", "year": 2022, "section": "Financial Statements", "score": 0.879}]),
        ("What risk factors did JPMorgan disclose in its 2021 annual report?",
         "JPMorgan's 2021 10-K risks: credit risk from pandemic recovery uncertainty, regulatory capital requirement increases (Basel III), cybersecurity threats, fintech competition, and prolonged low interest rate environment.",
         [{"company": "JPM", "year": 2021, "section": "Risk Factors", "score": 0.864}]),
        ("What are JPMorgan's Investment Banking revenues for FY2022?",
         "JPMorgan's Investment Banking fees were $6.6 billion in FY2022, down 55% from $14.5 billion in 2021, reflecting the sharp decline in IPO and M&A activity amid rising interest rates.",
         [{"company": "JPM", "year": 2022, "section": "Business Overview", "score": 0.876}]),
    ],
    "BAC": [
        ("What was Bank of America's net interest income in FY2023?",
         "Bank of America reported net interest income of $56.9 billion in FY2023, up from $52.4 billion in 2022. Growth slowed in H2 2023 as deposit costs rose faster than asset repricing.",
         [{"company": "BAC", "year": 2023, "section": "Financial Statements", "score": 0.909}]),
        ("What is Bank of America's CET1 capital ratio?",
         "Bank of America's CET1 ratio was 11.8% at year-end 2023, above its 9.5% regulatory minimum. The bank returned $7.7 billion to shareholders via buybacks and dividends in 2023.",
         [{"company": "BAC", "year": 2023, "section": "Financial Statements", "score": 0.894}]),
        ("What was BAC's provision for credit losses in 2022?",
         "Bank of America's provision for credit losses was $3.5 billion in FY2022, compared to a negative $4.6 billion reserve release in 2021, reflecting normalization of the credit environment.",
         [{"company": "BAC", "year": 2022, "section": "Financial Statements", "score": 0.867}]),
        ("What are the main risk factors for Bank of America in its 2021 10-K?",
         "BAC's 2021 10-K highlights: interest rate sensitivity risk, credit risk in commercial real estate, cybersecurity and operational risk, regulatory capital requirements, and competition from digital banks and fintechs.",
         [{"company": "BAC", "year": 2021, "section": "Risk Factors", "score": 0.851}]),
        ("What is Bank of America's consumer digital banking adoption?",
         "Bank of America had 56 million digital banking users in FY2023, with 37 million active mobile users. Digital sales represented 51% of total consumer banking sales.",
         [{"company": "BAC", "year": 2023, "section": "Business Overview", "score": 0.883}]),
    ],
    "WMT": [
        ("What was Walmart's total net sales in FY2024?",
         "Walmart's total net sales were $642.6 billion in FY2024 (ending Jan 2024), up 5.1% from $611.3 billion in FY2023, driven by grocery market share gains and strong international performance.",
         [{"company": "WMT", "year": 2023, "section": "Financial Statements", "score": 0.914}]),
        ("What is Walmart's comparable store sales growth rate?",
         "Walmart US comparable store sales grew 4.6% in FY2024 (ex-fuel), supported by grocery share gains, improved private label penetration, and recovery in general merchandise categories.",
         [{"company": "WMT", "year": 2023, "section": "Business Overview", "score": 0.899}]),
        ("What is Walmart's global eCommerce revenue growth?",
         "Walmart's global eCommerce sales grew 23% in FY2024, reaching approximately $100 billion. US eCommerce grew 21%, driven by curbside pickup and same-day delivery expansion.",
         [{"company": "WMT", "year": 2023, "section": "Business Overview", "score": 0.887}]),
        ("What were Walmart's operating income and margins in FY2022?",
         "Walmart's operating income was $20.4 billion in FY2022 (ending Jan 2022), with a 3.3% operating margin, below FY2021 due to elevated supply chain costs and wage increases.",
         [{"company": "WMT", "year": 2022, "section": "Financial Statements", "score": 0.871}]),
        ("What risk factors did Walmart disclose in its 2020 annual filing?",
         "Walmart's 2020 10-K highlights: intense competition from Amazon and Costco, COVID-19 supply chain impacts, wage inflation pressures, cybersecurity risks, and international regulatory compliance.",
         [{"company": "WMT", "year": 2020, "section": "Risk Factors", "score": 0.855}]),
        ("What is Walmart's advertising business revenue?",
         "Walmart Connect generated approximately $3.4 billion in revenue in FY2024, growing over 30% year-over-year, as Walmart leverages first-party purchase data for retail media advertising.",
         [{"company": "WMT", "year": 2023, "section": "Business Overview", "score": 0.878}]),
    ],
}

OFF_TOPIC = [
    "What is the best recipe for chocolate lava cake?",
    "Who won the FIFA World Cup in 2022?",
    "What are the most popular programming languages in 2024?",
    "How do I fix a leaky pipe under my kitchen sink?",
    "What is the current weather in Tokyo, Japan?",
    "Can you recommend a good science fiction novel to read?",
    "What is the speed of light in a vacuum?",
    "How do I train a neural network from scratch?",
    "What are the top tourist attractions in Paris?",
    "Who wrote the Harry Potter series of books?",
    "What are the health benefits of intermittent fasting?",
    "How do I improve my chess rating online?",
    "What programming language should I learn first as a beginner?",
    "What is the distance from Earth to the Moon?",
    "How do you make sourdough bread at home from scratch?",
    "Can you help me write a poem about the ocean?",
    "What are the rules of American football?",
    "How do I get started with yoga and meditation?",
]

RBAC_DENIED = [
    ("aapl-analyst",  "What is Microsoft's Azure cloud revenue growth rate in FY2023?",   "MSFT",  "AAPL"),
    ("msft-analyst",  "What were Apple's iPhone net sales in Q4 FY2022?",                 "AAPL",  "MSFT"),
    ("tsla-analyst",  "What is NVIDIA's data center GPU revenue for FY2024?",             "NVDA",  "TSLA"),
    ("nvda-analyst",  "What are Tesla's energy storage deployment figures for FY2023?",   "TSLA",  "NVDA"),
    ("jpm-analyst",   "What is Bank of America's net interest income for FY2023?",        "BAC",   "JPM"),
    ("bac-analyst",   "What are JPMorgan Chase's total assets and capital ratios?",       "JPM",   "BAC"),
    ("wmt-analyst",   "What was Amazon's AWS operating margin in FY2023?",                "AMZN",  "WMT"),
    ("amzn-analyst",  "What is Walmart's comparable store sales growth rate?",            "WMT",   "AMZN"),
    ("googl-analyst", "What is Meta's daily active people count for Q4 2023?",            "META",  "GOOGL"),
    ("meta-analyst",  "What is Alphabet's Google Cloud revenue growth rate?",             "GOOGL", "META"),
    ("aapl-analyst",  "What are NVIDIA's gross margins and data center revenue?",         "NVDA",  "AAPL"),
    ("tsla-analyst",  "What were JPMorgan's investment banking revenues in FY2022?",      "JPM",   "TSLA"),
    ("msft-analyst",  "What is Amazon's advertising services revenue for FY2023?",        "AMZN",  "MSFT"),
    ("jpm-analyst",   "What is Tesla's automotive gross margin in FY2022?",               "TSLA",  "JPM"),
    ("nvda-analyst",  "What were Walmart's total net sales in FY2024?",                   "WMT",   "NVDA"),
]


def _lat(cfg):
    lo, hi = CONFIG_LATENCY[cfg]
    return round(random.uniform(lo, hi), 1)

def _retrieved(cfg):
    lo, hi = CONFIG_RETRIEVED[cfg]
    return random.randint(lo, hi)

def _reranked(cfg, retrieved):
    r = CONFIG_RERANKED[cfg]
    if r is None:
        return retrieved
    lo, hi = r
    return random.randint(lo, min(hi, retrieved))

def _ts(date_str, h, m, s):
    return f"{date_str} {h:02d}:{m:02d}:{s:02d}"


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT    NOT NULL,
            config          TEXT    NOT NULL,
            question        TEXT    NOT NULL,
            answer          TEXT    NOT NULL,
            citations       TEXT    NOT NULL,
            latency_ms      REAL,
            retrieved_count INTEGER,
            reranked_count  INTEGER,
            created_at      TEXT    NOT NULL
        )
    """)

    rows = []

    # Successful queries May 1–11, varied configs and companies
    # Time tuples: (h, m, s) — no leading zeros in integer literals
    schedule = [
        ("2026-05-01",
         [(8,14,22),(8,47,38),(9,23,11),(9,58,44),(10,32,17),
          (11,5,29),(13,22,48),(14,10,33),(15,44,7),(16,28,51),(17,3,19)],
         [("AAPL","config_d"),("MSFT","config_d"),("AMZN","config_c"),
          ("GOOGL","config_b"),("META","config_d"),("NVDA","config_a"),
          ("TSLA","config_d"),("JPM","config_g"),("BAC","config_d"),
          ("WMT","config_c"),("AAPL","config_e")]),

        ("2026-05-02",
         [(8,55,13),(10,11,42),(11,38,7),(13,5,29),(15,22,44),(16,48,11)],
         [("MSFT","config_d"),("AMZN","config_d"),("GOOGL","config_d"),
          ("META","config_c"),("NVDA","config_d"),("TSLA","config_b")]),

        ("2026-05-03",
         [(10,24,33),(14,17,8)],
         [("JPM","config_a"),("BAC","config_d")]),

        ("2026-05-04",
         [(11,45,22),(16,2,47)],
         [("WMT","config_d"),("AAPL","config_c")]),

        ("2026-05-05",
         [(8,3,17),(8,41,55),(9,17,28),(9,52,4),(10,28,37),
          (11,4,22),(11,43,9),(13,7,41),(13,55,18),(14,32,53),
          (15,8,27),(15,48,14),(16,23,49),(17,1,32)],
         [("MSFT","config_d"),("AMZN","config_d"),("GOOGL","config_g"),
          ("META","config_d"),("NVDA","config_d"),("TSLA","config_d"),
          ("JPM","config_c"),("BAC","config_f"),("WMT","config_d"),
          ("AAPL","config_d"),("MSFT","config_b"),("AMZN","config_e"),
          ("GOOGL","config_d"),("NVDA","config_a")]),

        ("2026-05-06",
         [(8,29,11),(9,14,38),(10,2,55),(11,47,22),(13,33,9),
          (14,18,47),(15,4,28),(16,51,13)],
         [("TSLA","config_d"),("JPM","config_d"),("BAC","config_d"),
          ("WMT","config_c"),("AAPL","config_d"),("MSFT","config_g"),
          ("AMZN","config_d"),("GOOGL","config_d")]),

        ("2026-05-07",
         [(8,7,44),(8,52,21),(9,38,48),(10,24,15),(11,9,52),
          (13,55,19),(14,41,46),(15,27,13),(16,13,40),(17,0,7)],
         [("META","config_d"),("NVDA","config_d"),("TSLA","config_f"),
          ("JPM","config_d"),("BAC","config_d"),("WMT","config_d"),
          ("AAPL","config_c"),("MSFT","config_d"),("AMZN","config_d"),
          ("GOOGL","config_e")]),

        ("2026-05-08",
         [(8,38,26),(9,23,53),(10,9,30),(11,55,7),(13,40,44),
          (14,26,21),(15,12,58),(16,58,35)],
         [("META","config_d"),("NVDA","config_d"),("TSLA","config_d"),
          ("JPM","config_b"),("BAC","config_g"),("WMT","config_d"),
          ("AAPL","config_d"),("MSFT","config_d")]),

        ("2026-05-09",
         [(8,15,42),(9,48,19),(11,21,56),(13,54,33),(15,27,10),(16,59,47)],
         [("AMZN","config_d"),("GOOGL","config_d"),("META","config_a"),
          ("NVDA","config_d"),("TSLA","config_d"),("JPM","config_d")]),

        ("2026-05-10",
         [(10,33,28),(14,6,5)],
         [("BAC","config_c"),("WMT","config_d")]),

        ("2026-05-11",
         [(8,22,14),(9,7,51),(9,53,28),(10,38,5),(11,24,42)],
         [("AAPL","config_d"),("MSFT","config_d"),("AMZN","config_d"),
          ("GOOGL","config_d"),("NVDA","config_d")]),
    ]

    rng_q = {}
    for date, slots, pairs in schedule:
        for (company, cfg), (h, m, s) in zip(pairs, slots):
            qa_list = COMPANY_QA[company]
            idx = rng_q.get(company, 0) % len(qa_list)
            rng_q[company] = idx + 1
            question, answer, citations = qa_list[idx]
            ret = _retrieved(cfg)
            rer = _reranked(cfg, ret)
            rows.append((
                f"admin-session-{date.replace('-','')}-{h:02d}{m:02d}",
                cfg, question, answer,
                json.dumps(citations),
                _lat(cfg), ret, rer,
                _ts(date, h, m, s),
            ))

    # Off-topic guardrail blocks
    off_schedule = [
        ("2026-05-01", 10, 48, 33, "config_d"),
        ("2026-05-01", 15, 17,  9, "config_d"),
        ("2026-05-02",  9, 34, 52, "config_c"),
        ("2026-05-03", 13, 22, 41, "config_d"),
        ("2026-05-05", 10, 55, 18, "config_d"),
        ("2026-05-05", 14, 43,  7, "config_b"),
        ("2026-05-06",  9,  7, 29, "config_d"),
        ("2026-05-07", 11, 31, 48, "config_a"),
        ("2026-05-07", 16, 19, 24, "config_d"),
        ("2026-05-08", 10, 44,  3, "config_d"),
        ("2026-05-08", 15, 32, 57, "config_g"),
        ("2026-05-09",  9, 18, 46, "config_d"),
        ("2026-05-10", 11, 55, 22, "config_c"),
        ("2026-05-11",  8, 47, 31, "config_d"),
        ("2026-05-11", 10, 11, 58, "config_d"),
        ("2026-05-09", 14, 28, 39, "config_f"),
        ("2026-05-06", 17,  2, 14, "config_d"),
        ("2026-05-02", 16, 41, 27, "config_d"),
    ]
    for i, (date, h, m, s, cfg) in enumerate(off_schedule):
        question = OFF_TOPIC[i % len(OFF_TOPIC)]
        rows.append((
            f"anon-session-{date.replace('-','')}-{h:02d}{m:02d}",
            cfg, question, TOPIC_REJECT,
            json.dumps([]),
            0.0, 0, 0,
            _ts(date, h, m, s),
        ))

    # RBAC-denied queries
    rbac_schedule = [
        ("2026-05-01", 11, 52,  4),
        ("2026-05-02", 14, 28, 37),
        ("2026-05-03",  9, 15, 22),
        ("2026-05-05", 11, 38, 51),
        ("2026-05-05", 16,  4, 28),
        ("2026-05-06",  8, 47, 15),
        ("2026-05-07", 10, 21, 43),
        ("2026-05-07", 14, 58, 17),
        ("2026-05-08",  9, 33,  6),
        ("2026-05-09", 11, 47, 29),
        ("2026-05-09", 15, 12, 54),
        ("2026-05-10", 13, 38, 41),
        ("2026-05-11",  9, 24, 17),
        ("2026-05-11", 10, 58, 43),
        ("2026-05-08", 14, 17, 33),
    ]
    for i, (date, h, m, s) in enumerate(rbac_schedule):
        session_prefix, question, denied, allowed_str = RBAC_DENIED[i % len(RBAC_DENIED)]
        answer = (
            f"Access denied: you don't have permission to query documents for "
            f"{denied}. Your access is restricted to {allowed_str}."
        )
        rows.append((
            f"{session_prefix}-session-{date.replace('-','')}-{h:02d}{m:02d}",
            "config_d", question, answer,
            json.dumps([]),
            0.0, 0, 0,
            _ts(date, h, m, s),
        ))

    con.executemany(
        """INSERT INTO query_history
           (session_id, config, question, answer, citations,
            latency_ms, retrieved_count, reranked_count, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    con.commit()
    con.close()

    successful = sum(1 for r in rows if r[6] > 0)
    guardrail  = sum(1 for r in rows if r[6] == 0.0 and "Access denied" not in r[3])
    rbac       = sum(1 for r in rows if "Access denied" in r[3])
    print(f"Inserted {len(rows)} rows into query_history")
    print(f"  Successful RAG queries : {successful}")
    print(f"  Guardrail blocks       : {guardrail}")
    print(f"  RBAC denials           : {rbac}")

if __name__ == "__main__":
    main()
