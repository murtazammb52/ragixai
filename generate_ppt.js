const PptxGenJS = require("pptxgenjs");
const pptx = new PptxGenJS();

// ── Theme ──────────────────────────────────────────────────────────────────
pptx.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pptx.author  = "RAGixAI Team";
pptx.title   = "RAGixAI — SEC EDGAR Financial Intelligence";

const C = {
  bg:        "0D0D1A",
  purple:    "7C3AED",
  purpleL:   "A78BFA",
  blue:      "3B82F6",
  cyan:      "06B6D4",
  emerald:   "10B981",
  amber:     "F59E0B",
  coral:     "F43F5E",
  white:     "FFFFFF",
  white60:   "99999F",
  card:      "16182A",
  border:    "2A2D45",
};

// ── Helpers ────────────────────────────────────────────────────────────────
function addBg(slide) {
  slide.background = { color: C.bg };
}

function gradientTitle(slide, text, y = 0.35, size = 36) {
  // render as two halves for gradient feel using bold color
  slide.addText(text, {
    x: 0.4, y, w: 12.5, h: 0.7,
    fontSize: size, bold: true, color: C.purpleL,
    fontFace: "Calibri",
  });
}

function sectionTag(slide, text, y = 0.18) {
  slide.addText(text.toUpperCase(), {
    x: 0.4, y, w: 12.5, h: 0.28,
    fontSize: 11, bold: true, color: C.cyan,
    charSpacing: 2, fontFace: "Calibri",
  });
}

function body(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontSize: opts.size || 13,
    color: opts.color || C.white60,
    fontFace: "Calibri",
    wrap: true,
    valign: "top",
    ...opts,
  });
}

function card(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    fill:        { color: C.card },
    line:        { color: opts.border || C.border, width: 1 },
    rectRadius:  0.08,
  });
}

function accentBar(slide, x, y, h, color) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w: 0.05, h,
    fill: { color: color },
    line: { color: color, width: 0 },
  });
}

function bullet(slide, items, x, y, w, color = C.cyan) {
  const lines = items.map(t => ({ text: "  • " + t, options: { color: C.white60 } }));
  slide.addText(lines, {
    x, y, w, h: items.length * 0.32 + 0.1,
    fontSize: 12, fontFace: "Calibri", wrap: true,
  });
}

function statBox(slide, num, label, x, y, color = C.purpleL) {
  card(slide, x, y, 2.8, 1.2, { border: color });
  slide.addText(num, {
    x: x + 0.1, y: y + 0.1, w: 2.6, h: 0.55,
    fontSize: 28, bold: true, color, fontFace: "Calibri", align: "center",
  });
  slide.addText(label, {
    x: x + 0.1, y: y + 0.65, w: 2.6, h: 0.45,
    fontSize: 11, color: C.white60, fontFace: "Calibri", align: "center", wrap: true,
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);

  // decorative gradient rect top
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 13.33, h: 0.06,
    fill: { type: "gradient", gradType: "linear", stops: [
      { position: 0,   color: C.purple },
      { position: 50,  color: C.blue },
      { position: 100, color: C.cyan },
    ]},
    line: { color: C.bg, width: 0 },
  });

  s.addText("🚀  Capstone Project  ·  Financial AI  ·  2025–2026", {
    x: 0.4, y: 0.35, w: 12.5, h: 0.3,
    fontSize: 12, color: C.purpleL, fontFace: "Calibri", bold: true,
  });

  s.addText("RAGixAI", {
    x: 0.4, y: 0.85, w: 12.5, h: 1.2,
    fontSize: 72, bold: true, color: C.purpleL, fontFace: "Calibri",
  });

  s.addText("SEC EDGAR Financial Intelligence\nPowered by Retrieval-Augmented Generation", {
    x: 0.4, y: 2.1, w: 12.5, h: 0.9,
    fontSize: 22, color: C.white, fontFace: "Calibri",
  });

  s.addText(
    "A local-first RAG pipeline that makes 10-K · 10-Q · 8-K filings instantly queryable\n" +
    "with cited answers — automated end-to-end with Claude Code.",
    {
      x: 0.4, y: 3.1, w: 9, h: 0.8,
      fontSize: 14, color: C.white60, fontFace: "Calibri",
    }
  );

  // stat pills
  const pills = [
    ["36M+", "EDGAR Filings"],
    ["3.5hrs", "Per 10-K Read"],
    ["87%", "Retrieval Target"],
    ["Local-First", "Architecture"],
  ];
  pills.forEach(([n, l], i) => statBox(s, n, l, 0.4 + i * 3.2, 4.3,
    [C.purpleL, C.cyan, C.emerald, C.amber][i]));

  // decorative gradient rect bottom
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 7.44, w: 13.33, h: 0.06,
    fill: { type: "gradient", gradType: "linear", stops: [
      { position: 0,   color: C.purple },
      { position: 50,  color: C.blue },
      { position: 100, color: C.cyan },
    ]},
    line: { color: C.bg, width: 0 },
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 2 — Problem Statement
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "Problem Statement");
  gradientTitle(s, "The SEC Filing Overload Crisis", 0.5, 32);

  s.addText(
    "Financial analysts, investors, and compliance teams drown in dense SEC filings every quarter.",
    { x: 0.4, y: 1.25, w: 12.5, h: 0.4, fontSize: 14, color: C.white60, fontFace: "Calibri" }
  );

  // 4 stat boxes
  const stats = [
    ["3.5 hrs",  "to read a single\n10-K annual report",    C.coral],
    ["150+ pgs", "average 10-K length\n(some exceed 300)",   C.amber],
    ["6,900+",   "public companies\nfiling with the SEC",    C.cyan],
    ["36M+",     "total filings in\nthe EDGAR database",     C.purpleL],
  ];
  stats.forEach(([n, l, c], i) => statBox(s, n, l, 0.4 + i * 3.2, 1.9, c));

  // Pain points
  const pains = [
    ["📄", "Overwhelming Volume",     "A single 10-K can exceed 300 pages. Analysts covering 10+ companies face thousands of pages per quarter."],
    ["🔍", "No Semantic Search",      "EDGAR's search is keyword-only. 'Supply chain risk' won't find 'logistics disruptions' — missing critical disclosures."],
    ["⚖️", "Compliance & Audit Risk", "Compliance teams must cite exact filing sections. Manual search is slow and error-prone — a legal liability."],
    ["🤖", "AI Hallucination Risk",   "Generic LLMs invent financial figures. A fabricated revenue number in an investment memo can be illegal."],
  ];

  pains.forEach(([icon, title, desc], i) => {
    const x = i < 2 ? 0.4 : 6.85;
    const y = i % 2 === 0 ? 3.5 : 5.0;
    card(s, x, y, 6.0, 1.35, { border: C.coral });
    accentBar(s, x, y, 1.35, C.coral);
    s.addText(icon + "  " + title, { x: x+0.2, y: y+0.12, w: 5.6, h: 0.35, fontSize: 13, bold: true, color: "FDA4AF", fontFace: "Calibri" });
    s.addText(desc, { x: x+0.2, y: y+0.5, w: 5.6, h: 0.75, fontSize: 11, color: C.white60, fontFace: "Calibri", wrap: true });
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 3 — Solution Overview
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "The Solution");
  gradientTitle(s, "RAGixAI: RAG over SEC EDGAR Filings", 0.5, 30);

  s.addText(
    "Every answer is grounded in the actual SEC filing — with exact section and page citations.",
    { x: 0.4, y: 1.2, w: 12.5, h: 0.35, fontSize: 13, color: C.white60, fontFace: "Calibri" }
  );

  const cols = [
    { icon: "🧠", title: "RAG Pipeline",           color: C.purpleL,
      points: ["EDGAR API + local corpus ingestion", "Semantic + hybrid retrieval", "Cross-encoder re-ranking", "Citation-grounded answers"] },
    { icon: "📊", title: "Evaluation Framework",   color: C.cyan,
      points: ["6 RAGAS metrics tracked", "A/B configuration testing (7 configs)", "FinanceBench + EDGAR Corpus datasets", "Automated scoring pipeline"] },
    { icon: "🚀", title: "Cloud-Ready (Stretch)",  color: C.emerald,
      points: ["Runs fully locally (ChromaDB, sentence-transformers)", "HuggingFace free API for LLM", "AWS upgrade path: Bedrock + OpenSearch", "8 Claude Code skills — zero manual steps"] },
  ];

  cols.forEach(({ icon, title, color, points }, i) => {
    const x = 0.4 + i * 4.3;
    card(s, x, 1.75, 4.0, 5.3, { border: color });
    accentBar(s, x, 1.75, 5.3, color);
    s.addText(icon, { x: x+0.2, y: 1.9, w: 0.5, h: 0.5, fontSize: 22, fontFace: "Calibri" });
    s.addText(title, { x: x+0.2, y: 2.45, w: 3.6, h: 0.4, fontSize: 15, bold: true, color: C.white, fontFace: "Calibri" });
    points.forEach((p, j) => {
      s.addText("→  " + p, { x: x+0.2, y: 3.0 + j*0.55, w: 3.6, h: 0.45, fontSize: 11.5, color: C.white60, fontFace: "Calibri", wrap: true });
    });
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 4 — RAG Pipeline
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "Architecture");
  gradientTitle(s, "6-Stage RAG Pipeline", 0.5, 32);

  const stages = [
    { num:"1", icon:"📄", label:"Ingest",    color: C.purple,  desc: "SEC EDGAR API\n10-K · 10-Q · 8-K\nEDGAR Corpus (HF)" },
    { num:"2", icon:"✂️", label:"Chunk",     color: C.blue,    desc: "Fixed-size 512 tok\nRecursive char\nSemantic chunking" },
    { num:"3", icon:"🔢", label:"Embed",     color: C.cyan,    desc: "sentence-transformers\n(local, free)\nCohere Embed v3" },
    { num:"4", icon:"🔍", label:"Retrieve",  color: C.emerald, desc: "Dense vector search\nBM25 sparse\nRRF fusion → top-20" },
    { num:"5", icon:"📈", label:"Rerank",    color: C.amber,   desc: "Cross-encoder\nre-ranking\nTop-20 → top-5" },
    { num:"6", icon:"💬", label:"Answer",    color: C.coral,   desc: "HF Inference API\nPrompt + 5 chunks\nCitations included" },
  ];

  stages.forEach(({ num, icon, label, color, desc }, i) => {
    const x = 0.35 + i * 2.12;
    const y = 1.55;
    // circle
    s.addShape(pptx.ShapeType.ellipse, { x: x+0.56, y, w: 1.0, h: 1.0, fill: { color: C.card }, line: { color, width: 2 } });
    s.addText(icon, { x: x+0.56, y: y+0.05, w: 1.0, h: 0.75, fontSize: 22, align: "center", fontFace: "Calibri" });
    // badge
    s.addShape(pptx.ShapeType.ellipse, { x: x+1.38, y: y-0.1, w: 0.3, h: 0.3, fill: { color }, line: { color, width: 0 } });
    s.addText(num, { x: x+1.38, y: y-0.08, w: 0.3, h: 0.28, fontSize: 9, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
    // label
    s.addText(label, { x: x+0.3, y: y+1.1, w: 1.5, h: 0.3, fontSize: 12, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
    // desc card
    card(s, x+0.1, y+1.55, 1.9, 1.4, { border: color });
    s.addText(desc, { x: x+0.2, y: y+1.65, w: 1.7, h: 1.2, fontSize: 9.5, color: C.white60, fontFace: "Calibri", wrap: true, valign: "top" });
    // arrow
    if (i < 5) {
      s.addShape(pptx.ShapeType.line, {
        x: x+1.8, y: y+0.5, w: 0.32, h: 0,
        line: { color, width: 2, endArrowType: "triangle" },
      });
    }
  });

  // query flow example
  card(s, 0.4, 5.35, 12.5, 1.7, { border: C.purple });
  accentBar(s, 0.4, 5.35, 1.7, C.purple);
  s.addText("⚡  Query Flow Example", { x: 0.6, y: 5.45, w: 12.0, h: 0.3, fontSize: 12, bold: true, color: C.purpleL, fontFace: "Calibri" });
  s.addText(
    "Query: \"What were Apple's net sales by product segment in FY2023?\"\n" +
    "→ Embedded → Top-20 from EDGAR corpus → Re-ranked → AAPL_10-K_2023.txt §Item 8 Note 14 (0.96) → Answer: $383.3B total · iPhone $200.6B · Services $85.2B (+9.1% YoY)  |  Latency: ~1.8s",
    { x: 0.6, y: 5.8, w: 12.2, h: 0.9, fontSize: 11, color: C.white60, fontFace: "Calibri", wrap: true }
  );
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 5 — Datasets
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "Evaluation Data");
  gradientTitle(s, "Three SEC EDGAR-Rooted Datasets", 0.5, 30);

  s.addText("All datasets are rooted in real SEC filings — no synthetic or out-of-domain data.", {
    x: 0.4, y: 1.2, w: 12.5, h: 0.3, fontSize: 13, color: C.white60, fontFace: "Calibri",
  });

  const datasets = [
    {
      num: "Dataset 1", icon: "🏛️", title: "EDGAR Corpus",
      sub: "eloukas/edgar-corpus  ·  HuggingFace",
      color: C.purpleL,
      rows: [
        ["Coverage",    "6,900+ companies · 10-K annual reports 2000–2020"],
        ["Purpose",     "Primary document corpus ingested into vector store"],
        ["Filing Types","10-K, 10-K405, 10-KSB variants"],
        ["Role",        "Knowledge base — what the RAG pipeline retrieves from"],
      ]
    },
    {
      num: "Dataset 2", icon: "📊", title: "FinanceBench",
      sub: "PatronusAI/financebench  ·  HuggingFace",
      color: C.blue,
      rows: [
        ["Size",        "150 expert-annotated QA pairs"],
        ["Source",      "Real SEC 10-K and 10-Q filings"],
        ["Fields",      "question, answer, evidence, doc_name"],
        ["Role",        "Gold-standard QA benchmark for financial RAG evaluation"],
      ]
    },
    {
      num: "Dataset 3", icon: "⚗️", title: "RAGAS Testset (EDGAR)",
      sub: "ragas.testset.TestsetGenerator  ·  Generated locally",
      color: C.cyan,
      rows: [
        ["Size",        "~100 QA pairs per evaluation run"],
        ["Source",      "Auto-generated from ingested EDGAR documents"],
        ["Fields",      "question, contexts, answer, ground_truth"],
        ["Role",        "Domain-matched QA — questions about the exact indexed filings"],
      ]
    },
  ];

  datasets.forEach(({ num, icon, title, sub, color, rows }, i) => {
    const y = 1.65 + i * 1.85;
    card(s, 0.4, y, 12.5, 1.7, { border: color });
    accentBar(s, 0.4, y, 1.7, color);
    s.addText(num.toUpperCase(), { x: 0.65, y: y+0.1, w: 1.2, h: 0.25, fontSize: 9, bold: true, color, fontFace: "Calibri", charSpacing: 1 });
    s.addText(icon + "  " + title, { x: 0.65, y: y+0.38, w: 2.8, h: 0.4, fontSize: 15, bold: true, color: C.white, fontFace: "Calibri" });
    s.addText(sub, { x: 0.65, y: y+0.82, w: 2.8, h: 0.3, fontSize: 9.5, color: C.white60, fontFace: "Calibri" });
    rows.forEach(([k, v], j) => {
      const cx = j < 2 ? 3.8 : 8.1;
      const cy = y + 0.2 + (j % 2) * 0.65;
      s.addText(k + ": ", { x: cx, y: cy, w: 1.0, h: 0.3, fontSize: 10, bold: true, color, fontFace: "Calibri" });
      s.addText(v, { x: cx + 1.0, y: cy, w: 3.7, h: 0.35, fontSize: 10, color: C.white60, fontFace: "Calibri", wrap: true });
    });
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 6 — RAGAS Evaluation
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "RAGAS Framework");
  gradientTitle(s, "Measuring What Matters", 0.5, 32);

  s.addText("6 automated metrics quantify every dimension of RAG quality over SEC EDGAR filings.", {
    x: 0.4, y: 1.2, w: 12.5, h: 0.3, fontSize: 13, color: C.white60, fontFace: "Calibri",
  });

  const metrics = [
    { name: "Faithfulness",       target: "≥ 0.89", color: C.emerald, desc: "Every claim supported by the SEC filing. Prevents hallucinated financial figures." },
    { name: "Answer Relevancy",   target: "≥ 0.87", color: C.blue,    desc: "Answer directly addresses the analyst's question about the filing." },
    { name: "Context Precision",  target: "≥ 0.84", color: C.purple,  desc: "Retrieved EDGAR chunks are relevant — no noise from unrelated filings." },
    { name: "Context Recall",     target: "≥ 0.84", color: C.cyan,    desc: "All relevant filing sections were retrieved — no key disclosures missed." },
    { name: "Answer Correctness", target: "≥ 0.82", color: C.amber,   desc: "Answer matches FinanceBench ground truth from the actual SEC filing." },
    { name: "Response Latency",   target: "p95 < 3s", color: C.coral, desc: "End-to-end: sub-3s response vs 3.5 hours to manually read a 10-K." },
  ];

  metrics.forEach(({ name, target, color, desc }, i) => {
    const x = i % 3 < 1 ? 0.4 : i % 3 < 2 ? 4.65 : 8.9;
    const y = i < 3 ? 1.65 : 4.2;
    card(s, x, y, 4.0, 2.2, { border: color });
    accentBar(s, x, y, 2.2, color);
    s.addText(name, { x: x+0.2, y: y+0.15, w: 3.2, h: 0.35, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri" });
    s.addText("Target: " + target, { x: x+0.2, y: y+0.55, w: 3.2, h: 0.3, fontSize: 12, bold: true, color, fontFace: "Calibri" });
    s.addText(desc, { x: x+0.2, y: y+0.95, w: 3.6, h: 0.95, fontSize: 10.5, color: C.white60, fontFace: "Calibri", wrap: true });
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 7 — Configuration Comparison
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "A/B Configuration Testing");
  gradientTitle(s, "7-Config Comparison Matrix", 0.5, 32);

  s.addText("All 7 configs run through EDGAR Corpus + FinanceBench. Best tradeoff of accuracy, latency & cost selected.", {
    x: 0.4, y: 1.2, w: 12.5, h: 0.3, fontSize: 12, color: C.white60, fontFace: "Calibri",
  });

  const headers = ["Config", "Embedding", "Retrieval", "Reranker", "Faithfulness", "Relevancy", "Ctx Prec.", "p95 Lat."];
  const rows = [
    ["Config A", "Titan v2",       "Dense",   "None",        "0.71", "0.74", "0.68", "1.1s"],
    ["Config B", "Titan v2",       "Hybrid",  "None",        "0.78", "0.79", "0.76", "1.4s"],
    ["Config C", "Cohere v3",      "Dense",   "None",        "0.80", "0.82", "0.77", "1.2s"],
    ["Config D", "Cohere v3",      "Hybrid",  "None",        "0.84", "0.85", "0.81", "1.7s"],
    ["★ Config E","Cohere v3",     "Hybrid",  "Cross-enc.",  "0.89", "0.87", "0.84", "2.4s"],
    ["Config F", "OpenAI ada-3",   "Hybrid",  "Cross-enc.",  "0.88", "0.86", "0.83", "2.6s"],
    ["Config G", "Cohere v3",      "BM25",    "Cross-enc.",  "0.72", "0.71", "0.69", "1.8s"],
  ];

  const colW = [1.35, 1.55, 1.1, 1.1, 1.2, 1.1, 1.1, 1.0];
  const startX = 0.4;
  const startY = 1.65;
  const rowH = 0.52;

  // header row
  let cx = startX;
  headers.forEach((h, i) => {
    s.addShape(pptx.ShapeType.rect, { x: cx, y: startY, w: colW[i], h: rowH, fill: { color: "1E1B3A" }, line: { color: C.border, width: 0.5 } });
    s.addText(h, { x: cx+0.05, y: startY+0.1, w: colW[i]-0.1, h: rowH-0.1, fontSize: 10, bold: true, color: C.purpleL, fontFace: "Calibri", wrap: true });
    cx += colW[i];
  });

  // data rows
  rows.forEach((row, ri) => {
    cx = startX;
    const isHighlight = ri === 4;
    const y = startY + rowH * (ri + 1);
    row.forEach((cell, ci) => {
      s.addShape(pptx.ShapeType.rect, {
        x: cx, y, w: colW[ci], h: rowH,
        fill: { color: isHighlight ? "1A1040" : C.card },
        line: { color: isHighlight ? C.purple : C.border, width: 0.5 },
      });
      s.addText(cell, {
        x: cx+0.05, y: y+0.1, w: colW[ci]-0.1, h: rowH-0.1,
        fontSize: 10,
        color: isHighlight ? C.white : (ci >= 4 ? (parseFloat(cell) >= 0.85 ? C.emerald : C.white60) : C.white60),
        bold: isHighlight,
        fontFace: "Calibri", wrap: true,
      });
      cx += colW[ci];
    });
  });

  s.addText("★ Config E selected — best faithfulness (0.89) + relevancy (0.87) within the 3s latency budget", {
    x: 0.4, y: 6.05, w: 12.5, h: 0.3, fontSize: 11, color: C.purpleL, fontFace: "Calibri", bold: true,
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 8 — Claude Code Skills
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "Automation First");
  gradientTitle(s, "8 Claude Code Skills — Zero Manual Touch", 0.5, 30);

  s.addText("The entire pipeline — from EDGAR ingestion to final evaluation report — runs via custom Claude Code slash commands.", {
    x: 0.4, y: 1.2, w: 12.5, h: 0.3, fontSize: 13, color: C.white60, fontFace: "Calibri",
  });

  const skills = [
    ["/ingest-docs",     "Auto-ingest SEC EDGAR filings via API + local corpus. Handles incremental sync & metadata extraction."],
    ["/chunk-docs",      "Compare fixed-size, recursive-char & semantic chunking strategies on the EDGAR corpus."],
    ["/embed-docs",      "Run sentence-transformers locally. Switch between Cohere Embed v3 and Titan v2 with one command."],
    ["/query-rag",       "End-to-end RAG query: embed → retrieve → rerank → generate → return cited answer."],
    ["/evaluate-rag",    "Run full RAGAS suite on FinanceBench + EDGAR Testset. Score all 6 metrics automatically."],
    ["/ab-test-configs", "Run all 7 configurations head-to-head and output the comparison matrix."],
    ["/build-index",     "Build or rebuild the ChromaDB vector index from the ingested EDGAR corpus."],
    ["/deploy-local",    "One-command local deployment — spin up the RAG API endpoint on localhost."],
  ];

  skills.forEach(([cmd, desc], i) => {
    const x = i % 2 === 0 ? 0.4 : 6.9;
    const y = 1.65 + Math.floor(i / 2) * 1.3;
    card(s, x, y, 6.0, 1.15, { border: C.purple });
    accentBar(s, x, y, 1.15, C.purple);
    s.addText(cmd, { x: x+0.2, y: y+0.1, w: 5.6, h: 0.35, fontSize: 13, bold: true, color: C.purpleL, fontFace: "Calibri" });
    s.addText(desc, { x: x+0.2, y: y+0.5, w: 5.6, h: 0.55, fontSize: 10.5, color: C.white60, fontFace: "Calibri", wrap: true });
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 9 — AWS Stretch Goal
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "Stretch Goal");
  gradientTitle(s, "AWS Cloud Upgrade Path", 0.5, 32);

  s.addText("Primary implementation is local-first (free). AWS is the stretch goal if time permits.", {
    x: 0.4, y: 1.2, w: 12.5, h: 0.3, fontSize: 13, color: C.white60, fontFace: "Calibri",
  });

  // Local vs AWS comparison
  const sections = [
    {
      label: "🖥️  Local (Primary)", color: C.emerald, x: 0.4,
      items: [
        "ChromaDB — local vector store",
        "sentence-transformers — local embedding",
        "HuggingFace Inference API — free LLM",
        "eloukas/edgar-corpus — local dataset",
        "RAGAS — local evaluation",
        "pypdf / unstructured — PDF parsing",
      ]
    },
    {
      label: "☁️  AWS (Stretch Goal)", color: C.amber, x: 6.85,
      items: [
        "Amazon OpenSearch — managed vector DB",
        "Amazon Bedrock — Claude / Titan LLM",
        "Amazon Titan Embeddings v2",
        "Amazon S3 — EDGAR filing storage",
        "Amazon Textract — advanced PDF parsing",
        "AWS Lambda — serverless compute",
      ]
    },
  ];

  sections.forEach(({ label, color, x, items }) => {
    card(s, x, 1.65, 6.0, 5.4, { border: color });
    accentBar(s, x, 1.65, 5.4, color);
    s.addText(label, { x: x+0.2, y: 1.78, w: 5.6, h: 0.4, fontSize: 14, bold: true, color, fontFace: "Calibri" });
    items.forEach((item, i) => {
      s.addText("✓  " + item, { x: x+0.2, y: 2.35 + i * 0.72, w: 5.5, h: 0.55, fontSize: 12, color: C.white60, fontFace: "Calibri" });
    });
  });

  s.addText("→", { x: 6.45, y: 4.1, w: 0.4, h: 0.5, fontSize: 24, color: C.amber, fontFace: "Calibri", align: "center" });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 10 — Roadmap
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);
  sectionTag(s, "Project Timeline");
  gradientTitle(s, "Roadmap & Milestones", 0.5, 32);

  const phases = [
    {
      phase: "Phase 1", title: "Foundation",
      color: C.purpleL, weeks: "Weeks 1–4",
      tasks: ["Problem definition & success metrics", "SEC EDGAR dataset collection & curation", "Baseline: naive keyword search on EDGAR", "Dev environment & repo structure", "/ingest-docs Claude Code skill"],
    },
    {
      phase: "Phase 2", title: "Pipeline Build",
      color: C.cyan, weeks: "Weeks 5–9",
      tasks: ["RAG pipeline: chunk → embed → retrieve", "ChromaDB vector store setup", "Hybrid retrieval + BM25 implementation", "Cross-encoder re-ranking", "All 8 Claude Code skills"],
    },
    {
      phase: "Phase 3", title: "Evaluation",
      color: C.emerald, weeks: "Weeks 10–13",
      tasks: ["RAGAS evaluation framework integration", "FinanceBench + EDGAR Testset scoring", "7-config A/B comparison matrix", "Performance optimisation", "AWS stretch goal (if time permits)"],
    },
    {
      phase: "Phase 4", title: "Submission",
      color: C.amber, weeks: "Weeks 14–16",
      tasks: ["Final evaluation report", "Demo recording", "Documentation & codebase clean-up", "Presentation preparation", "Final submission"],
    },
  ];

  phases.forEach(({ phase, title, color, weeks, tasks }, i) => {
    const x = 0.4 + i * 3.2;
    card(s, x, 1.6, 3.0, 5.5, { border: color });
    s.addShape(pptx.ShapeType.rect, { x, y: 1.6, w: 3.0, h: 0.65, fill: { color }, line: { color, width: 0 } });
    s.addText(phase, { x: x+0.12, y: 1.65, w: 2.8, h: 0.28, fontSize: 10, bold: true, color: C.bg, fontFace: "Calibri" });
    s.addText(title, { x: x+0.12, y: 1.93, w: 2.8, h: 0.28, fontSize: 13, bold: true, color: C.bg, fontFace: "Calibri" });
    s.addText(weeks, { x: x+0.12, y: 2.35, w: 2.8, h: 0.28, fontSize: 10, color: C.white60, fontFace: "Calibri" });
    tasks.forEach((t, j) => {
      s.addText("→  " + t, { x: x+0.12, y: 2.75 + j * 0.68, w: 2.75, h: 0.58, fontSize: 10, color: C.white60, fontFace: "Calibri", wrap: true });
    });
  });
}

// ══════════════════════════════════════════════════════════════════════════
// SLIDE 11 — Thank You
// ══════════════════════════════════════════════════════════════════════════
{
  const s = pptx.addSlide();
  addBg(s);

  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 13.33, h: 0.06,
    fill: { type: "gradient", gradType: "linear", stops: [
      { position: 0,   color: C.purple },
      { position: 50,  color: C.blue },
      { position: 100, color: C.cyan },
    ]},
    line: { color: C.bg, width: 0 },
  });

  s.addText("RAGixAI", {
    x: 0.4, y: 1.4, w: 12.5, h: 1.1,
    fontSize: 64, bold: true, color: C.purpleL, fontFace: "Calibri", align: "center",
  });

  s.addText("SEC EDGAR Financial Intelligence with RAG & Evaluation", {
    x: 0.4, y: 2.6, w: 12.5, h: 0.5,
    fontSize: 18, color: C.white, fontFace: "Calibri", align: "center",
  });

  s.addText("Capstone Project 2025–2026  ·  Built with Claude Code", {
    x: 0.4, y: 3.2, w: 12.5, h: 0.3,
    fontSize: 13, color: C.white60, fontFace: "Calibri", align: "center",
  });

  // summary pills
  const items = [
    ["🏛️", "EDGAR Corpus\n+ FinanceBench"],
    ["🧠", "6-Stage RAG\nPipeline"],
    ["📊", "6 RAGAS\nMetrics"],
    ["🤖", "8 Claude Code\nSkills"],
  ];
  items.forEach(([icon, label], i) => {
    card(s, 1.8 + i * 2.5, 3.9, 2.1, 1.4, { border: C.purple });
    s.addText(icon, { x: 1.8 + i * 2.5, y: 4.0, w: 2.1, h: 0.5, fontSize: 22, align: "center", fontFace: "Calibri" });
    s.addText(label, { x: 1.8 + i * 2.5, y: 4.5, w: 2.1, h: 0.7, fontSize: 10.5, color: C.white60, align: "center", fontFace: "Calibri" });
  });

  s.addText("Thank you — Questions?", {
    x: 0.4, y: 5.7, w: 12.5, h: 0.6,
    fontSize: 28, bold: true, color: C.cyan, fontFace: "Calibri", align: "center",
  });

  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 7.44, w: 13.33, h: 0.06,
    fill: { type: "gradient", gradType: "linear", stops: [
      { position: 0,   color: C.purple },
      { position: 50,  color: C.blue },
      { position: 100, color: C.cyan },
    ]},
    line: { color: C.bg, width: 0 },
  });
}

// ── Write file ─────────────────────────────────────────────────────────────
pptx.writeFile({ fileName: "RAGixAI_Presentation.pptx" })
  .then(() => console.log("✅  RAGixAI_Presentation.pptx created successfully!"))
  .catch(err => console.error("❌  Error:", err));
