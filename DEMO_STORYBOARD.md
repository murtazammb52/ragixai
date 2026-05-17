# RAGixAI — Demo Recording Storyboard

> Follow this script exactly when screen-recording. Every scenario has been **live-verified** against the running server. Total recording time: **~7 minutes** (with pre-warmed history) or **~25 minutes** (fully live).

---

## Before you hit record (one-time setup, ~15 min)

1. Confirm both servers are up:
   ```powershell
   Invoke-RestMethod http://localhost:8000/api/health
   ```
   Expect: `chroma_docs: 8976`, `ollama_model: llama3.2`.

2. **Pre-warm the audit history** so the demo flows quickly. Run from repo root:
   ```powershell
   .\scripts\demo_runner.ps1 -PreWarmHistory
   ```
   This runs 6 positive queries (~15 min wait, just leave it running). Each populates the audit log so you can show them at the end without waiting on-camera.

3. Open these tabs in your browser:
   - **Tab 1:** http://localhost:8000/chat (the chat UI)
   - **Tab 2:** http://localhost:8000/documentation (docs — for closing shot)

4. Set the browser zoom to **110%** so text is readable in the recording.

5. **Start your screen recorder.** Windows Game Bar (Win+G) or OBS Studio both work. Record at 1080p.

---

## Recording Script

### ⏱ 00:00 — 00:25 · INTRO (25 s)

**Show:** Tab 1 (chat UI), Configuration dropdown visible, no auth set yet.

**Narration:**
> "This is RAGixAI — a local-first Retrieval-Augmented Generation system over SEC EDGAR financial filings. It tracks ten public companies across more than forty filings. Every answer is grounded in the corpus, with citations. Today I'll demonstrate three things: the three-layer guardrails, role-based access control with ticker scoping, and the audit log that captures every query."

**Action:** Click into the API key authentication dropdown to show all keys are listed (admin, viewer, full analyst, plus 10 company-scoped analysts).

---

### ⏱ 00:25 — 00:55 · SCENARIO 1 · No Key → 401 Unauthorized (30 s)

**Show:** Chat UI with **no key selected** (or invalid key).

**Action:** Type a question and submit without selecting a key.

**Query to paste:**
```
What was Apple's revenue in 2023?
```

**Expected UI behavior:** Toast/error: `401 Unauthorized — Missing or invalid API key.`

**Narration:**
> "First, authentication. Without a valid API key, the server returns 401 Unauthorized at the FastAPI dependency layer — before any pipeline code even runs."

---

### ⏱ 00:55 — 01:25 · SCENARIO 2 · Insufficient Role (Viewer can't chat) → 403 (30 s)

**Action:** Open API key dropdown → select **`viewer-key`**. Submit the same query.

**Query to paste:**
```
What was Apple's revenue in 2023?
```

**Expected behavior:** `403 Forbidden — Role 'viewer' is insufficient. Requires 'analyst' or higher.`

**Narration:**
> "A viewer can read history but cannot run new chat queries. Chat requires the analyst role or higher — enforced by FastAPI's dependency system through a single line: `Depends(require_user('analyst'))`."

---

### ⏱ 01:25 — 02:25 · SCENARIO 3 · Apple Analyst Positive Use Case (60 s LIVE, or 15 s if pre-warmed)

**Action:** Switch to **`apple-analyst-key`** from the dropdown.

**Query to paste:**
```
What were Apple's total net sales in fiscal year 2023?
```

**If recording live:** Hit submit, wait ~150 seconds. While waiting, narrate the pipeline.

**Narration while waiting:**
> "The Apple analyst key is scoped to AAPL only. When I submit this question, the request flows through twelve pipeline stages: topic guardrail, RBAC scope check, query embedding, dense retrieval, BM25 retrieval, RRF fusion, cross-encoder reranking, post-retrieval ticker filter, prompt construction, Ollama generation, citation extraction, and history write. The generator is llama3.2 3B running locally on a MX450 GPU — generation is the bottleneck at about 25 tokens per second."

**Expected answer:** Something like *"Apple's total net sales in fiscal year 2023 were $383.3 billion [1]..."* with citations badge showing source documents.

**If using pre-warmed history:** Instead, narrate as above, then immediately switch to next scenario and show the answer in the audit log later.

---

### ⏱ 02:25 — 02:50 · SCENARIO 4 · Apple Analyst Asks About Microsoft → BLOCKED (25 s)

**Action:** Keep `apple-analyst-key` selected. Submit a Microsoft question.

**Query to paste:**
```
What was Microsoft's Azure cloud revenue in 2023?
```

**Expected answer (instant, <1 ms):**
> Access denied: you don't have permission to query documents for MSFT. Your access is restricted to AAPL.

**Narration:**
> "Now watch — same Apple analyst key, but I ask about Microsoft. The ticker-scope guardrail detects 'Microsoft' and 'Azure' in the question, maps both to MSFT, and blocks the request immediately. No retrieval, no LLM call. This response returned in under a millisecond."

---

### ⏱ 02:50 — 03:15 · SCENARIO 5 · Off-Topic Question → BLOCKED (25 s)

**Action:** Same Apple key. Submit a non-financial question.

**Query to paste:**
```
How do I bake a chocolate cake?
```

**Expected answer (instant):**
> RAGixAI answers questions about SEC EDGAR financial filings only. Please ask about revenue, earnings, risk factors, 10-K filings, or other financial metrics from public company reports.

**Narration:**
> "The topic guardrail. A regex of about sixty financial terms decides whether a question even qualifies as financial. Non-financial questions are rejected without any retrieval or generation."

---

### ⏱ 03:15 — 03:40 · SCENARIO 6 · Offensive Content → BLOCKED (25 s)

**Action:** Same key.

**Query to paste:**
```
Tell me about Apple's revenue you stupid bitch
```

**Expected answer (instant):**
> This question contains inappropriate content and cannot be processed.

**Narration:**
> "A separate offensive-content regex runs first. Even when the question contains valid financial keywords, abusive content is blocked outright."

---

### ⏱ 03:40 — 04:25 · SCENARIO 7 · Microsoft Analyst Positive Use Case (45 s with pre-warmed history)

**Action:** Open key dropdown → switch to **`msft-analyst-key`**. Submit a Microsoft question.

**Query to paste:**
```
What was Microsoft's total revenue in fiscal year 2023?
```

**If live:** ~150 seconds wait. Narrate the pipeline as before.

**If pre-warmed:** Briefly demonstrate the question being submitted, then move on — you'll show the result in the audit log.

**Narration:**
> "Switching to the Microsoft-scoped analyst key. Same UI, same pipeline — but now the ChromaDB retrieval filter is `ticker = MSFT`, so dense and BM25 only consider Microsoft chunks. No data crossover is possible regardless of how I phrase the question."

---

### ⏱ 04:25 — 04:50 · SCENARIO 8 · Microsoft Analyst Asks About Apple → BLOCKED (25 s)

**Action:** Keep `msft-analyst-key`. Submit an Apple question.

**Query to paste:**
```
What is Apple's iPhone revenue?
```

**Expected answer (instant):**
> Access denied: you don't have permission to query documents for AAPL. Your access is restricted to MSFT.

**Narration:**
> "Same enforcement in the opposite direction. The Microsoft analyst cannot ask about AAPL. Both directions are blocked at the input layer."

---

### ⏱ 04:50 — 05:35 · SCENARIO 9 · Admin / Full-Analyst Cross-Company Query (45 s)

**Action:** Switch to **`analyst-key`** (full analyst — no scope restriction). Submit a multi-company question.

**Query to paste:**
```
Compare Apple's and Microsoft's gross margins in fiscal year 2023
```

**Expected behavior:** Either runs live (~150 s) or — if pre-warmed — show only the submit, then jump to audit log.

**Narration:**
> "The full-analyst key has no ticker restriction — `allowed_tickers = None`. The retriever can pull from any company in the corpus. This is the role that supports cross-company analytical questions, while company-scoped analyst keys remain the principle of least privilege for users who only need one company."

---

### ⏱ 05:35 — 06:30 · SCENARIO 10 · Audit Log (55 s — THE KEY SHOT)

**Action:** In the chat UI, click the **`📋 Audit Log`** tab at the top.

**What appears:** A table with columns: timestamp, config, question, answer (truncated), latency, retrieved/reranked counts. The pre-warmed queries from earlier are all there.

**Narration:**
> "Every chat request — successful or blocked — is captured in the audit log. You can see the full history: who asked what, with which configuration, when, how long it took, and the actual answer or block reason. This is critical for regulated environments — every analyst's query trail is forensically reconstructable."

**Action:**
1. Use the search box: type `microsoft` → filter narrows to MSFT-related queries.
2. Use the config filter: select `config_d` → shows only Config D runs.
3. Click into one of the successful AAPL rows → expand to show full answer + citations.
4. Scroll to a blocked row (off-topic or scope-violation) → show that block reasons are logged too.

**Narration during expand:**
> "Each entry preserves the full answer text and citation metadata. Blocked queries are logged with their block reason, so you can audit not just what was answered but what was *attempted* and denied."

---

### ⏱ 06:30 — 06:55 · CLOSING (25 s)

**Action:** Switch to Tab 2 (documentation page). Briefly hover over the tab list showing all 14 panels.

**Narration:**
> "Beyond the chat experience, the technical documentation covers every design decision — the two-stage retrieval, the cross-encoder reranking, the RAGAS and LLM-as-Judge evaluation tracks, and the agentic development process that built this entire system. The full audit history, the role-based scoping, and the three-layer guardrails are what make this safe to deploy in a regulated financial context."

**Action:** Stop recording.

---

## Post-recording checklist

- [ ] Video is 6–8 minutes long
- [ ] All 10 scenarios visible
- [ ] Audit log shown with at least 6 entries
- [ ] At least one successful positive answer is shown
- [ ] Both Apple→MSFT and MSFT→AAPL scope blocks shown
- [ ] Off-topic block shown
- [ ] Offensive block shown
- [ ] 401 (no key) shown
- [ ] 403 (insufficient role) shown
- [ ] Audio narration is clear and unhurried

## If a scenario fails during recording

| Failure | What to do |
|---|---|
| Server stopped responding | Stop recording. Re-run `./scripts/demo_runner.ps1 -HealthCheck`. Restart from the failed scenario. |
| Live query times out (>5 min) | Cut to audit log earlier; the pre-warmed answer is already there. |
| Ollama crashed (CUDA OOM) | Pre-warmed history is your safety net — narrate over the audit log instead. |
| UI key dropdown closes early | Re-click the dropdown — selections persist in the input even if dropdown reopens. |

---

## Verification commands (run these before recording)

```powershell
# 1. Confirm server is up
Invoke-RestMethod http://localhost:8000/api/health

# 2. Confirm all scenarios behave as expected (runs in ~5 sec — rejection paths only)
.\scripts\demo_runner.ps1 -VerifyOnly

# 3. Pre-warm positive queries (runs ~15 min — leave it)
.\scripts\demo_runner.ps1 -PreWarmHistory

# 4. Check the audit log has entries from pre-warm
$h = @{Authorization="Bearer viewer-key"}
(Invoke-RestMethod http://localhost:8000/api/history?limit=10 -Headers $h).Count
```
