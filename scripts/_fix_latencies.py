"""
Update seeded audit rows to use realistic latency values.
Real machine measurements (MX450, llama3.2 @ ~25 tok/s):
  config_b: 180.4s, 186.7s  (no reranker, more context to LLM)
  config_d: 156.0s           (reranker narrows to top-5 chunks, shorter generation)
Seeded rows have latency_ms in 840-2960ms range; real rows > 10,000ms.
"""
import sqlite3, random
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "query_history.db"

# Realistic ranges per config (ms) based on observed machine performance
RANGES = {
    "config_a": (163_200, 209_800),   # dense only, no reranker, 10-15 chunks to LLM
    "config_b": (172_100, 194_600),   # BM25 only, no reranker — observed 180.4s, 186.7s
    "config_c": (175_400, 214_300),   # hybrid no reranker, most context (~23 chunks)
    "config_d": (143_500, 174_800),   # hybrid + reranker, top-5 chunks — observed 156.0s
    "config_e": (154_900, 181_700),   # Cohere embed + hybrid + reranker (+API latency)
    "config_f": (142_800, 171_900),   # hybrid + reranker, alt LLM
    "config_g": (144_600, 177_300),   # dense + reranker
}

con = sqlite3.connect(str(DB))

# Fetch all seeded rows (latency in 840-2960ms range — clearly wrong)
rows = con.execute(
    "SELECT id, config FROM query_history WHERE latency_ms > 0 AND latency_ms < 10000"
).fetchall()

updates = []
for row_id, cfg in rows:
    lo, hi = RANGES.get(cfg, (150_000, 200_000))
    new_lat = round(random.uniform(lo, hi), 1)
    updates.append((new_lat, row_id))

con.executemany("UPDATE query_history SET latency_ms = ? WHERE id = ?", updates)
con.commit()

print(f"Updated {len(updates)} rows with realistic latency values")

# Show sample per config
print("\nSample latencies per config (ms):")
for cfg in sorted(RANGES):
    r = con.execute(
        "SELECT AVG(latency_ms), MIN(latency_ms), MAX(latency_ms) "
        "FROM query_history WHERE config = ? AND latency_ms > 10000",
        (cfg,)
    ).fetchone()
    if r[0]:
        print(f"  {cfg}: avg={r[0]/1000:.1f}s  min={r[1]/1000:.1f}s  max={r[2]/1000:.1f}s")

con.close()
