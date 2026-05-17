"""Extract all 150 gold QA rows with Config D answers for judge evaluation."""
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
src = (ROOT / "frontend" / "static" / "gold_data.js").read_text(encoding="utf-8", errors="replace")

# Extract the JS array — handles window.GOLD_DATA = [...]
m = re.search(r'window\.GOLD_DATA\s*=\s*(\[[\s\S]*?\])\s*;', src)
if not m:
    m = re.search(r'(?:const\s+)?(?:goldData|GOLD_DATA)\s*=\s*(\[[\s\S]*?\])\s*;', src)
if not m:
    print("ERROR: could not find GOLD_DATA array", file=sys.stderr)
    sys.exit(1)

raw = m.group(1)
raw = re.sub(r',\s*([\]}])', r'\1', raw)
data = json.loads(raw)

# Inspect first item keys
if data:
    print("Keys in first item:", list(data[0].keys()))

rows = []
for i, item in enumerate(data):
    q = item.get("q", item.get("question", ""))
    gt = item.get("gold", item.get("ground_truth", item.get("answer", "")))
    company = item.get("co", item.get("company", item.get("ticker", "")))
    # Config D answer is item['d']['s']
    d_obj = item.get("d", {})
    d_ans = d_obj.get("s", "") if isinstance(d_obj, dict) else str(d_obj)
    rows.append({
        "id": i + 1,
        "company": company,
        "question": q,
        "ground_truth": gt,
        "config_d_answer": d_ans,
    })

out = ROOT / "scripts" / "_all_rows.json"
out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Extracted {len(rows)} rows -> {out}")
# Also print first row as sanity check
if rows:
    r = rows[0]
    print(f"\nRow 1 sample:")
    print(f"  Q: {r['question'][:80]}")
    print(f"  GT: {r['ground_truth'][:80]}")
    print(f"  D: {r['config_d_answer'][:80]}")
