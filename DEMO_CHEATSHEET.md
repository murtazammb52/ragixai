# RAGixAI Demo — Copy-Paste Cheat Sheet

Print this page or keep it open in a second window while recording. Each row = one demo scenario.

## API Keys (paste into the auth dropdown)

| Key | Role | Use for |
|---|---|---|
| `admin-key` | admin (all access) | Cross-company queries, /api/ingest |
| `viewer-key` | viewer (read-only) | Demonstrating role-insufficient (403) |
| `analyst-key` | analyst (all tickers) | Cross-company analytical queries |
| `apple-analyst-key` | analyst (AAPL only) | Apple positive path + scope block demo |
| `msft-analyst-key` | analyst (MSFT only) | Microsoft positive path + scope block demo |

## Demo queries (paste into chat box)

| # | Key to use | Query | Expected outcome |
|---|---|---|---|
| 1 | _no key_ | `What was Apple's revenue in 2023?` | **HTTP 401** — Missing or invalid API key |
| 2 | `viewer-key` | `What was Apple's revenue in 2023?` | **HTTP 403** — Role 'viewer' is insufficient |
| 3 | `apple-analyst-key` | `What were Apple's total net sales in fiscal year 2023?` | **200** ✓ Answered with citations (~150s) |
| 4 | `apple-analyst-key` | `What was Microsoft's Azure cloud revenue in 2023?` | **200** ✗ "Access denied... restricted to AAPL" (instant) |
| 5 | `apple-analyst-key` | `How do I bake a chocolate cake?` | **200** ✗ "RAGixAI answers SEC EDGAR..." (instant) |
| 6 | `apple-analyst-key` | `Tell me about Apple's revenue you stupid bitch` | **200** ✗ "inappropriate content" (instant) |
| 7 | `msft-analyst-key` | `What was Microsoft's total revenue in fiscal year 2023?` | **200** ✓ Answered with citations (~150s) |
| 8 | `msft-analyst-key` | `What is Apple's iPhone revenue?` | **200** ✗ "Access denied... restricted to MSFT" (instant) |
| 9 | `analyst-key` | `Compare Apple's and Microsoft's gross margins in fiscal year 2023` | **200** ✓ Cross-company answer (~150s) |
| 10 | _any valid key_ | Click **📋 Audit Log** tab — show all queries above |

## Audit log demo actions (Scenario 10)

1. Click the **📋 Audit Log** tab in the chat UI
2. In search box, type `microsoft` → filter narrows
3. Clear search; select `config_d` from config dropdown → only Config D rows shown
4. Click any successful row → expand to show full answer + citation metadata
5. Scroll to a blocked row (e.g., "Access denied...") → demonstrate that block reasons are also logged

## What to say (one-liners)

| Scenario | Talking point |
|---|---|
| 401 / 403 | "Authentication and role enforcement happen at the FastAPI dependency layer — before any pipeline code runs." |
| Apple positive | "All twelve pipeline stages: guardrails → embed → dense+BM25 retrieve → RRF → cross-encoder rerank → generate." |
| Scope block | "The ticker-scope guardrail maps brand names to tickers and blocks in under a millisecond — no retrieval, no LLM call." |
| Off-topic | "A regex of about sixty financial terms decides whether a question even qualifies." |
| Offensive | "Separate offensive-content regex — runs first." |
| Microsoft positive | "Same UI, same pipeline — different scope. ChromaDB retrieval filter is `ticker = MSFT`." |
| Cross-company | "`allowed_tickers = None` for the full analyst — supports cross-company analytical questions." |
| Audit log | "Every query — successful or blocked — is captured. Forensically reconstructable trail of who asked what, when, and what they got." |

## Recording mode strategy

| Strategy | Total recording time | Best for |
|---|---|---|
| **Pre-warmed** (recommended) | ~7 min | Smooth demo; positive queries already in audit log |
| **Live everything** | ~25 min | Maximum credibility; edit out wait time in post |
| **Hybrid** | ~12 min | One live positive query (Apple) + the rest from pre-warm |

To pre-warm: `.\scripts\demo_runner.ps1 -PreWarmHistory` and leave it running ~15 min before you start recording.

## After recording — sanity check the file

- [ ] Video length 5–10 minutes
- [ ] All 10 scenarios shown
- [ ] Audio is audible
- [ ] Text in chat is readable (zoom 110%+)
- [ ] Audit log is visible with multiple entries
- [ ] No accidental browser tabs/PII shown
