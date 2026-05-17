"""Write all 150 judge scores to llm_judge_output.json."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

# (id, faith, comp, cit, hall, reasoning_faith, reasoning_comp, reasoning_cit, reasoning_hall)
SCORES = [
    (1,  5,4,5,5, "Core revenue and YoY figures directly match filing data","Missing 'driven by iPhone and Services' context from ground truth","[1] placed correctly after the key facts","No external knowledge introduced"),
    (2,  5,5,5,5, "All three data points ($205.5B, 52%, 6.6%) are accurate","Question fully addressed including revenue, share, and growth rate","[1] correctly anchors the financial fact","Answer stays within retrieved corpus"),
    (3,  5,3,5,5, "Revenue and growth rate are accurate","Missing the ~19.8% share of total net sales from ground truth","[1] placed correctly","No hallucination"),
    (4,  5,4,5,5, "43.3% and 41.8% comparison are accurate","Missing driver explanation about Services mix and pricing","[1] correctly placed","No external knowledge"),
    (5,  5,3,5,5, "Net income figures are accurate","Missing diluted EPS of $6.15 from ground truth","[1] placed correctly","No hallucination"),
    (6,  5,3,5,5, "R&D figure of $26.3B is accurate","Missing percentage of net sales (6.7%) and prior year ($21.9B)","[1] placed correctly","No external knowledge introduced"),
    (7,  5,2,5,5, "Mac revenue $40.2B is accurate","Missing growth rate, prior year comparison, and M1 driver context","[1] placed correctly","No hallucination"),
    (8,  2,1,2,5, "Answer truncated to just 'Apple's Wearables' — no actual data provided","Question completely unanswered; no revenue figure given","[1] present but answer is effectively empty","No fabricated numbers, but answer is useless"),
    (9,  5,4,5,5, "Total net sales and decline percentage are accurate","Missing explanation of which segments drove the decline","[1] correctly placed","No hallucination"),
    (10, 5,4,5,5, "iPhone revenue and YoY decline are accurate","Missing macro headwinds context from ground truth","[1] placed correctly","No external knowledge"),
    (11, 5,4,5,5, "Services revenue and growth rate are accurate","Missing 'all-time record' designation and App Store/TV+ drivers","[1] correctly placed","No hallucination"),
    (12, 5,4,5,5, "Gross margin expansion figures are accurate","Missing Services mix-shift driver explanation","[1] placed correctly","No external knowledge"),
    (13, 5,4,5,5, "FY2021 net sales and growth rate are accurate","Missing 'broad-based recovery' context","[1] correctly placed","No hallucination"),
    (14, 5,5,5,5, "Americas revenue, share, and YoY growth all accurate","All three components of the question fully addressed","[1] correctly placed","No external knowledge"),
    (15, 5,3,5,5, "Long-term debt figure is accurate","Missing debt financing strategy and capital returns context","[1] placed correctly","No hallucination"),
    (16, 5,4,5,5, "Employee count is accurate (minor formatting comma in '164, 000')","Core answer complete; missing investment context","[1] correctly placed","No external knowledge"),
    (17, 5,3,5,5, "Correctly states Apple does not report segment operating income","Missing the consolidated operating income figure of $108.9B","[1] placed correctly","No hallucination"),
    (18, 5,5,3,5, "Correctly identifies answer as not found in corpus","Appropriate response for an unavailable data point","No citation needed for not-found response","No hallucination — correctly declined"),
    (19, 5,4,5,5, "Total revenue figure and growth rate are accurate","Missing 'significant deceleration' context and prior year absolute","[1] correctly placed","No external knowledge"),
    (20, 5,4,5,5, "Search revenue and YoY growth are accurate","Missing 'largest component of advertising' context","[1] correctly placed","No hallucination"),
    (21, 5,4,5,5, "YouTube revenue and comparison are accurate","Missing brand advertising softening context","[1] correctly placed","No external knowledge"),
    (22, 5,4,5,5, "Cloud revenue and growth rate are accurate","Missing prior year absolute ($19.2B) and driver context","[1] correctly placed","No hallucination"),
    (23, 5,5,5,5, "Net income and prior year both accurate","Both current and prior year figures fully addressed","[1] correctly placed","No external knowledge"),
    (24, 5,3,5,5, "Operating income figure is accurate","Missing operating margin of ~30.6%","[1] correctly placed","No hallucination"),
    (25, 5,3,5,5, "CapEx figure is accurate","Missing prior year ($24.3B) and infrastructure purpose context","[1] correctly placed","No external knowledge"),
    (26, 5,4,5,5, "Employee count accurate (minor formatting comma)","Missing January 2023 layoff announcement context","[1] correctly placed","No hallucination"),
    (27, 5,5,5,5, "US revenue and percentage share both accurate","Both the dollar figure and the percentage share fully addressed","[1] correctly placed","No external knowledge"),
    (28, 2,1,2,5, "Answer truncated to 'Alphabet's Europe, Middle East' — no data provided","Question completely unanswered; no revenue figure given","[1] present but answer is useless","No fabricated numbers"),
    (29, 5,5,5,5, "Growth rate, absolute figures, and context all accurate","Full answer including rate, base, and advertising recovery narrative","[1] correctly placed","No external knowledge"),
    (30, 5,5,5,5, "Operating income and margin both accurate","Both components of the question fully addressed","[1] correctly placed","No hallucination"),
    (31, 5,3,5,5, "Net income figure is accurate","Missing decline from $76.0B and primary reasons","[1] correctly placed","No external knowledge"),
    (32, 4,1,3,5, "Search revenue is correct but YouTube and Cloud are missing","Only one of three requested segments answered","Partial citation — fact given has [1] but answer is severely incomplete","No incorrect facts, but critically incomplete"),
    (33, 5,3,5,5, "Effective tax rate is accurate","Missing the two primary drivers (stock comp, foreign earnings)","[1] correctly placed","No hallucination"),
    (34, 5,5,3,5, "Correctly identifies quarterly breakdown as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (35, 5,5,3,5, "Correctly identifies holding-level gains as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (36, 5,4,5,5, "Revenue and growth rate are accurate","Missing drivers (commercial cloud, LinkedIn, gaming)","[1] correctly placed","No external knowledge"),
    (37, 5,4,5,5, "Intelligent Cloud revenue and growth rate accurate","Missing the Azure ~40% sub-segment detail","[1] correctly placed","No hallucination"),
    (38, 5,4,5,5, "Productivity segment revenue and growth accurate","Missing specific drivers (Office 365, LinkedIn)","[1] correctly placed","No external knowledge"),
    (39, 5,5,5,5, "Gross margin and drivers both accurate","Complete answer matching ground truth","[1] correctly placed","No hallucination"),
    (40, 5,5,5,5, "Operating income and margin both accurate","Both figures fully addressed","[1] correctly placed","No external knowledge"),
    (41, 5,5,5,5, "Net income and diluted EPS both accurate","Complete answer","[1] correctly placed","No hallucination"),
    (42, 5,4,5,5, "R&D spend and percentage of revenue accurate","Missing 'supporting cloud infrastructure and AI' context","[1] correctly placed","No external knowledge"),
    (43, 5,4,5,5, "Revenue and growth rate accurate","Missing commercial cloud >$70B detail","[1] correctly placed","No hallucination"),
    (44, 5,5,5,5, "Net income and diluted EPS both accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (45, 5,3,5,5, "Total revenue figure accurate","Missing growth rate, prior year, and Azure detail","[1] correctly placed","No hallucination"),
    (46, 5,4,5,5, "Gross margin and prior year comparison accurate","Missing driver context (IC mix shift and Azure)","[1] correctly placed","No external knowledge"),
    (47, 5,5,5,5, "Operating income and margin both accurate","Complete answer","[1] correctly placed","No hallucination"),
    (48, 5,4,5,5, "CapEx figure and trend accurate","Missing specific Azure/AI data center buildout context","[1] correctly placed","No external knowledge"),
    (49, 5,4,5,5, "Employee count accurate (comma formatting issue)","Core answer present; missing year '2022' from the date","[1] correctly placed","No hallucination"),
    (50, 5,4,5,5, "Correctly notes Azure not disclosed standalone","Missing the $60.1B IC figure and +50% Azure growth","[1] correctly placed","No external knowledge"),
    (51, 5,5,3,5, "Correctly identifies country-level data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (52, 5,3,5,5, "Managed net revenue figure accurate","Missing prior year and NII driver context","[1] correctly placed","No external knowledge"),
    (53, 5,4,5,5, "NII and prior year comparison accurate","Mentions prior year; missing Fed rate hike context","[1] correctly placed","No hallucination"),
    (54, 5,3,5,5, "Provision figure accurate","Missing 2021 comparison and economic uncertainty context","[1] correctly placed","No external knowledge"),
    (55, 5,4,5,5, "Net income and diluted EPS accurate","Missing decline context versus 2021","[1] correctly placed","No hallucination"),
    (56, 5,5,5,5, "CET1 ratio and regulatory context both accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (57, 5,3,5,5, "Total assets figure accurate","Missing largest-US-bank context and prior year $3.39T","[1] correctly placed","No hallucination"),
    (58, 5,5,5,5, "Loan balance and growth context both accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (59, 2,4,5,3, "States deposits increased from $2.46T to $2.39T — direction is wrong; it was a decrease","Key numbers present but directional error undermines reliability","[1] placed correctly","Incorrect direction likely from training memory bias — external knowledge error"),
    (60, 5,3,5,5, "Net income figure accurate","Missing diluted EPS $15.36 and reserve release context","[1] correctly placed","No external knowledge"),
    (61, 5,5,5,5, "Revenue and business drivers both accurate","Complete answer including IB fees and C&CB context","[1] correctly placed","No hallucination"),
    (62, 2,1,2,5, "Answer truncated to 'approximately 293' — number cut off","Question unanswered; no full headcount given","[1] present but answer is unusable","No fabricated data, just truncated"),
    (63, 5,5,5,5, "Provision figures for 2020 and 2019 both accurate","Complete answer with comparison","[1] correctly placed","No external knowledge"),
    (64, 5,3,5,5, "IB fees figure accurate","Missing decline from $14.5B and IPO/M&A volume context","[1] correctly placed","No hallucination"),
    (65, 5,1,2,5, "Honest not-found response even though corpus has relevant tech risk disclosures","Retrieval failure — ground truth shows relevant content exists in 2021 10-K","Not applicable for not-found response","No hallucination"),
    (66, 5,5,3,5, "Correctly identifies charge-off breakdown as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (67, 5,5,3,5, "Correctly identifies loan-level impairment data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (68, 5,5,5,5, "Total net sales and growth rate both accurate","Complete answer with current and prior year","[1] correctly placed","No external knowledge"),
    (69, 5,3,5,5, "AWS revenue and growth rate accurate","Missing operating income $18.5B and 29.8% margin","[1] correctly placed","No hallucination"),
    (70, 5,4,5,5, "North America revenue and growth rate accurate","Missing segment operating income $7.3B","[1] correctly placed","No external knowledge"),
    (71, 5,4,5,5, "Advertising revenue and growth rate accurate","Missing prior year absolute figure ($19.8B)","[1] correctly placed","No hallucination"),
    (72, 5,3,5,5, "Net income figure accurate","Missing material Rivian valuation gain context ($11.8B)","[1] correctly placed","No external knowledge"),
    (73, 5,3,5,5, "Total operating income accurate","Missing segment breakdown (AWS, NA, International) which was the question's intent","[1] correctly placed","No hallucination"),
    (74, 5,3,5,5, "Total net sales accurate","Missing growth rate and prior year comparison","[1] correctly placed","No external knowledge"),
    (75, 5,4,5,5, "AWS revenue and growth rate accurate","Missing prior year absolute ($62.2B)","[1] correctly placed","No hallucination"),
    (76, 5,4,5,5, "Advertising revenue and growth rate accurate","Missing prior year absolute ($31.2B)","[1] correctly placed","No external knowledge"),
    (77, 5,3,5,5, "Net loss figure correct","Missing Rivian -$12.7B valuation context and prior year comparison","[1] correctly placed","No hallucination"),
    (78, 5,4,5,5, "Operating income and prior year comparison accurate","Missing segment contribution breakdown","[1] correctly placed","No external knowledge"),
    (79, 5,5,5,5, "Employee count and context accurate","Complete answer","[1] correctly placed","No hallucination"),
    (80, 5,3,5,5, "Total revenue figure accurate","Missing growth rate (+37.6%) and prior year ($280.5B)","[1] correctly placed","No external knowledge"),
    (81, 5,4,5,5, "Correctly notes per-unit metric not disclosed","Missing the $84.3B total fulfillment cost figure","[1] correctly placed","No hallucination"),
    (82, 5,5,3,5, "Correctly identifies Prime subscriber/ARPU data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (83, 5,4,5,5, "Net revenue and prior year comparison accurate","Missing rate hike driver context","[1] correctly placed","No external knowledge"),
    (84, 5,4,5,5, "NII and prior year comparison accurate","Missing Fed rate hike attribution","[1] correctly placed","No hallucination"),
    (85, 5,3,5,5, "Consumer Banking NII accurate","Missing deposit rate mechanism context","[1] correctly placed","No external knowledge"),
    (86, 5,4,5,5, "Net income and EPS accurate","Missing decline from $31.9B context","[1] correctly placed","No hallucination"),
    (87, 5,4,5,5, "CET1 ratio accurate (minor: missing year)","Missing year '2022' and 'above regulatory minimum' qualifier","[1] correctly placed","No external knowledge"),
    (88, 5,5,5,5, "Loan balance and growth context accurate","Complete answer including growth drivers","[1] correctly placed","No hallucination"),
    (89, 5,5,5,5, "Deposit figure and direction (decrease) both accurate","Complete answer correctly noting pandemic liquidity normalization","[1] correctly placed","No external knowledge"),
    (90, 5,5,5,5, "Employee count accurate (minor comma formatting)","Complete answer","[1] correctly placed","No hallucination"),
    (91, 2,1,2,5, "Answer truncated to 'Bank of America operated 4' — number cut off","Question unanswered; no financial center count given","[1] present but answer is unusable","No fabricated data"),
    (92, 5,5,5,5, "Global Markets revenue and market context accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (93, 5,3,5,5, "Net income figure accurate","Missing diluted EPS and credit reserve release context","[1] correctly placed","No hallucination"),
    (94, 5,5,5,5, "Revenue, context, and constraints all accurate","Complete answer matching ground truth narrative","[1] correctly placed","No external knowledge"),
    (95, 5,4,5,5, "Net income and prior year comparison accurate","Missing $11.3B provision and COVID attribution","[1] correctly placed","No hallucination"),
    (96, 5,4,5,5, "Charge-off rate and historical context accurate","Missing 2021 trough comparison (1.0%)","[1] correctly placed","No external knowledge"),
    (97, 5,5,3,5, "Correctly identifies branch-level data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (98, 5,5,5,5, "Revenue and prior year comparison accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (99, 4,2,4,5, "Revenue figure correct but operating loss entirely omitted","Missing the -$13.7B operating loss which was half the question","[1] present but answer critically incomplete","No hallucination — just truncated"),
    (100,5,5,5,5, "Operating income and prior year comparison accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (101,5,5,5,5, "Net income and prior year comparison accurate","Complete answer","[1] correctly placed","No hallucination"),
    (102,5,5,5,5, "MAU figure and prior period comparison accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (103,5,3,5,5, "Revenue figure accurate","Missing growth rate (+37.2%), prior year ($86.0B), and drivers","[1] correctly placed","No hallucination"),
    (104,5,5,5,5, "Operating income and margin accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (105,5,5,5,5, "Net income and diluted EPS accurate","Complete answer","[1] correctly placed","No hallucination"),
    (106,5,5,5,5, "Worldwide ARPU and regional breakdown all accurate","Complete answer with all geographic segments","[1] correctly placed","No external knowledge"),
    (107,5,3,5,5, "CapEx figure accurate","Missing purpose breakdown (data centers, network, VR/AR hardware)","[1] correctly placed","No hallucination"),
    (108,5,3,5,5, "CapEx figure accurate","Missing prior year comparison and investment purpose","[1] correctly placed","No external knowledge"),
    (109,5,4,5,5, "Revenue and growth rate accurate","Missing prior year absolute ($70.7B)","[1] correctly placed","No hallucination"),
    (110,3,2,4,4, "Headcount present but '11' truncated — cannot confirm 11,000 vs other","Key layoff quantity '11,000' cut off; missing 13% and November 2022 details","[1] present but answer is incomplete","Partial answer — truncation creates ambiguity"),
    (111,5,5,3,5, "Correctly identifies engagement time data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (112,5,3,5,5, "Total net sales accurate","Missing growth rate (+2.4%) and prior year ($555.2B)","[1] correctly placed","No external knowledge"),
    (113,5,5,5,5, "Comp sales growth and primary driver accurate","Complete answer","[1] correctly placed","No hallucination"),
    (114,5,4,5,5, "Operating income and prior year comparison accurate","Missing supply chain and wage cost headwind context","[1] correctly placed","No external knowledge"),
    (115,5,4,5,5, "Net income and EPS accurate","Missing supply chain inflation context","[1] correctly placed","No hallucination"),
    (116,5,3,5,5, "Sam's Club net sales accurate","Missing growth from $58.8B and membership driver context","[1] correctly placed","No external knowledge"),
    (117,5,5,5,5, "Total assets and date accurate","Complete answer","[1] correctly placed","No hallucination"),
    (118,5,5,5,5, "Employee count and date accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (119,5,3,5,5, "Total net sales accurate","Missing growth rate (+6.7%) and prior year ($519.9B)","[1] correctly placed","No hallucination"),
    (120,5,5,5,5, "Comp sales growth and pandemic driver context accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (121,5,4,5,5, "Operating income accurate","Mentions comparable sales but misses favorable mix and cost discipline","[1] correctly placed","No hallucination"),
    (122,5,5,5,5, "Gross margin and headwind context accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (123,2,1,2,5, "Answer truncated to 'Walmart's advertising business, Walmart Connect' — no figure","Question completely unanswered; no revenue figure given","[1] present but answer is useless","No fabricated numbers"),
    (124,5,3,5,5, "CapEx figure accurate","Missing e-commerce fulfillment and tech modernization priorities","[1] correctly placed","No hallucination"),
    (125,5,5,3,5, "Correctly identifies store-level labor data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (126,5,3,5,5, "Total revenue figure accurate","Missing growth rate (+61.4%) and prior year ($16.7B)","[1] correctly placed","No external knowledge"),
    (127,5,4,5,5, "Data Center revenue and growth rate accurate","Missing A100 GPU adoption context","[1] correctly placed","No hallucination"),
    (128,5,3,5,5, "Gaming revenue accurate","Missing growth rate (+61.3%) and RTX/mining demand context","[1] correctly placed","No external knowledge"),
    (129,5,5,5,5, "Gross margin and product mix context accurate","Complete answer","[1] correctly placed","No hallucination"),
    (130,5,5,5,5, "Net income and adjusted EPS accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (131,5,5,5,5, "Revenue, comparison, and segment narrative accurate","Complete answer","[1] correctly placed","No hallucination"),
    (132,5,4,5,5, "Data Center revenue and growth rate accurate","Missing H100 GPU context","[1] correctly placed","No external knowledge"),
    (133,5,3,5,5, "Gaming revenue accurate","Missing decline rate and demand normalization context","[1] correctly placed","No hallucination"),
    (134,5,4,5,5, "Gross margin and prior year comparison accurate","Missing inventory provision ($1.4B) context","[1] correctly placed","No external knowledge"),
    (135,5,4,5,5, "R&D figure and growth rate accurate","Missing Hopper GPU architecture investment context","[1] correctly placed","No hallucination"),
    (136,5,3,5,5, "Operating income accurate","Missing decline from $10.04B in FY2022","[1] correctly placed","No external knowledge"),
    (137,5,4,5,5, "Correctly notes Mellanox not separately disclosed","Missing the $10.6B total and segment structure note","[1] correctly placed","No hallucination"),
    (138,5,5,3,5, "Correctly identifies hyperscaler concentration data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
    (139,5,4,5,5, "Revenue and growth rate accurate","Missing prior year absolute ($31.5B) and deliveries/energy context","[1] correctly placed","No external knowledge"),
    (140,5,3,5,5, "Automotive revenue accurate","Missing +72% growth rate and factory ramp context","[1] correctly placed","No hallucination"),
    (141,5,4,5,5, "Net income and profitability milestone accurate","Missing prior year $721M for 2020 comparison","[1] correctly placed","No external knowledge"),
    (142,2,1,2,5, "Answer truncated to 'Tesla delivered 936' — number cut off","Question completely unanswered; no delivery count given","[1] present but answer is useless","No fabricated data"),
    (143,5,3,5,5, "Total revenue accurate","Missing growth rate (+51.4%) and deliveries milestone","[1] correctly placed","No hallucination"),
    (144,1,3,5,2, "States margin was 'a 29.3% increase from 2021' — factually wrong; it decreased from 29.3% to 28.5%","Current figure present but directional claim is incorrect","[1] correctly placed","Incorrect directional relationship likely from training memory"),
    (145,5,5,5,5, "Operating income and margin both accurate","Complete answer","[1] correctly placed","No external knowledge"),
    (146,5,4,5,5, "Net income and profitability milestone accurate","Missing diluted EPS $3.62","[1] correctly placed","No hallucination"),
    (147,2,1,2,5, "Answer truncated to 'Tesla delivered 1, 313' — number cut off","Question completely unanswered; full delivery count unavailable","[1] present but answer is useless","No fabricated data"),
    (148,5,5,5,5, "Cash balance and date accurate","Complete answer","[1] correctly placed","No hallucination"),
    (149,4,2,2,5, "Honest about limited disclosure, but misses qualitative negative-margin context","Ground truth notes near-zero margins from Megapack ramp; answer omits this","Not applicable — should have cited corpus context about Megapack costs","No hallucination"),
    (150,5,5,3,5, "Correctly identifies battery cost data as not in corpus","Appropriate not-found response","No citation needed for not-found","No hallucination"),
]

results = []
for row in SCORES:
    id_, f, c, cq, h, rf, rc, rcq, rh = row
    results.append({
        "id": id_,
        "faithfulness":      {"score": f,  "reasoning": rf},
        "completeness":      {"score": c,  "reasoning": rc},
        "citation_quality":  {"score": cq, "reasoning": rcq},
        "hallucination_free":{"score": h,  "reasoning": rh},
    })

out = ROOT / "llm_judge_output.json"
out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(results)} rows -> {out}")

# Aggregate
n = len(results)
def mean_norm(dim):
    return round(sum(r[dim]["score"] for r in results) / (n * 5), 4)

faith = mean_norm("faithfulness")
comp  = mean_norm("completeness")
cit   = mean_norm("citation_quality")
hall  = mean_norm("hallucination_free")
overall = round((faith + comp + cit + hall) / 4, 4)

def passes(r):
    dims = ["faithfulness","completeness","citation_quality","hallucination_free"]
    avg = sum(r[d]["score"] for d in dims) / 4
    return (avg / 5) >= 0.70

pass_count = sum(1 for r in results if passes(r))
pass_rate = round(pass_count / n, 4)

print(f"\n{'='*52}")
print(f"  LLM-as-Judge  (Claude Sonnet 4.6, n={n}, Config D)")
print(f"{'='*52}")
print(f"  Faithfulness:       {faith:.3f}  {'PASS' if faith>=0.70 else 'FAIL'}")
print(f"  Completeness:       {comp:.3f}  {'PASS' if comp>=0.70 else 'FAIL'}")
print(f"  Citation Quality:   {cit:.3f}  {'PASS' if cit>=0.70 else 'FAIL'}")
print(f"  Hallucination-Free: {hall:.3f}  {'PASS' if hall>=0.70 else 'FAIL'}")
print(f"  {'─'*40}")
print(f"  Overall Mean:       {overall:.3f}")
print(f"  Pass Rate:          {pass_rate:.1%}  ({pass_count}/{n})")
print(f"{'='*52}")
