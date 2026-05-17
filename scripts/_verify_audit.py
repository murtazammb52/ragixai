import sqlite3
con = sqlite3.connect(r"D:\code\ragixai\data\query_history.db")
total = con.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
successful = con.execute("SELECT COUNT(*) FROM query_history WHERE latency_ms > 0").fetchone()[0]
guardrail  = con.execute("SELECT COUNT(*) FROM query_history WHERE latency_ms = 0 AND answer LIKE 'RAGixAI%'").fetchone()[0]
rbac       = con.execute("SELECT COUNT(*) FROM query_history WHERE answer LIKE 'Access denied%'").fetchone()[0]
print(f"Total rows      : {total}")
print(f"Successful RAG  : {successful}")
print(f"Guardrail blocks: {guardrail}")
print(f"RBAC denials    : {rbac}")
print()
dates = con.execute("SELECT MIN(created_at), MAX(created_at) FROM query_history").fetchone()
print(f"Date range: {dates[0]}  ->  {dates[1]}")
print()
print("Sample successful rows:")
for r in con.execute("SELECT config, latency_ms, retrieved_count, reranked_count, created_at, question FROM query_history WHERE latency_ms > 0 LIMIT 4").fetchall():
    print(f"  [{r[4]}] {r[0]}  lat={r[1]}ms  ret={r[2]}  rer={r[3]}  Q: {r[5][:60]}")
print()
print("Sample guardrail rows:")
for r in con.execute("SELECT config, created_at, question FROM query_history WHERE answer LIKE 'RAGixAI%' LIMIT 3").fetchall():
    print(f"  [{r[1]}] {r[0]}  Q: {r[2][:60]}")
print()
print("Sample RBAC rows:")
for r in con.execute("SELECT session_id, created_at, question FROM query_history WHERE answer LIKE 'Access denied%' LIMIT 3").fetchall():
    print(f"  [{r[1]}] {r[0][:30]}  Q: {r[2][:55]}")
