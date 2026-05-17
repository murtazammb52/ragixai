import sqlite3
con = sqlite3.connect(r"D:\code\ragixai\data\query_history.db")
print("Per-config latency (realistic rows > 100s):")
for r in con.execute("""SELECT config, COUNT(*), ROUND(AVG(latency_ms)/1000,1), ROUND(MIN(latency_ms)/1000,1), ROUND(MAX(latency_ms)/1000,1)
    FROM query_history WHERE latency_ms > 100000 GROUP BY config ORDER BY config""").fetchall():
    print(f"  {r[0]}: n={r[1]}  avg={r[2]}s  min={r[3]}s  max={r[4]}s")
print()
total = con.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
block_g = con.execute("SELECT COUNT(*) FROM query_history WHERE answer LIKE 'RAGixAI%'").fetchone()[0]
block_r = con.execute("SELECT COUNT(*) FROM query_history WHERE answer LIKE 'Access denied%'").fetchone()[0]
ok = con.execute("SELECT COUNT(*) FROM query_history WHERE latency_ms > 100000").fetchone()[0]
print(f"Total rows       : {total}")
print(f"Successful (>100s): {ok}")
print(f"Guardrail blocks : {block_g}")
print(f"RBAC denials     : {block_r}")
print()
print("Date spread:")
for r in con.execute("SELECT DATE(created_at), COUNT(*) FROM query_history GROUP BY DATE(created_at) ORDER BY 1").fetchall():
    print(f"  {r[0]}: {r[1]} rows")
