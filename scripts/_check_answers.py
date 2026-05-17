import json

data = json.load(open("data/gold_data.json"))

companies = ["AAPL", "GOOGL", "MSFT", "JPM", "AMZN", "BAC", "META", "WMT", "NVDA", "TSLA"]

for co in companies:
    rows = [e for e in data if e["co"] == co and e.get("d", {}).get("ok") == 1]
    if not rows:
        continue
    e = rows[0]
    print(f"[{co}] {e['q']}")
    print(f"  GOLD: {e['gold']}")
    print(f"  [d]:  {e['d']['s']}")
    print(f"  [e]:  {e['e']['s']}")
    print(f"  [c]:  {e['c']['s']}")
    print(f"  [g]:  {e['g']['s']}")
    print()

print(f"Total records in JSON: {len(data)} questions x 7 configs = {len(data)*7} answers")
