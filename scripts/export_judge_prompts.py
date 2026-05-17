"""
Generate LLM-as-Judge prompts from gold_data.js for external judge evaluation.

Parses the 150 Config D QA pairs and writes a markdown file with
ready-to-paste batched prompts. Each batch = 10 rows per judge message.
Results are saved to llm_judge_output.json and aggregated here.

Usage:
    python scripts/export_judge_prompts.py
    python scripts/export_judge_prompts.py --n 30 --batch 10
    python scripts/export_judge_prompts.py --config e   # use Config E answers
    python scripts/export_judge_prompts.py --aggregate llm_judge_output.json

Output: llm_judge_output.json (judge replies saved here, then pass to --aggregate)
"""
import re, json, argparse, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def load_gold_data():
    js = (ROOT / "frontend" / "static" / "gold_data.js").read_text(encoding="utf-8")
    match = re.search(r"window\.GOLD_DATA\s*=\s*(\[.*\])\s*;?\s*$", js, re.DOTALL)
    if not match:
        sys.exit("Could not parse gold_data.js")
    return json.loads(match.group(1))


SYSTEM_PROMPT = """You are an expert financial RAG (Retrieval-Augmented Generation) evaluator.

I will give you a batch of QA rows. For EACH row, score the Generated Answer on exactly 4 dimensions using an INTEGER from 1 to 5:

1. faithfulness       — every factual claim in the generated answer matches the ground truth and would be traceable to a real SEC filing
   (1 = fabricates facts / wrong numbers, 5 = fully grounded and accurate)

2. completeness       — the generated answer fully addresses all parts of the question
   (1 = major gaps / partial answer, 5 = thorough and complete)

3. citation_quality   — the answer includes [N] citation markers placed next to specific facts
   (1 = no citations at all, 5 = every key fact cited inline)

4. hallucination_free — the answer avoids adding information not present in the ground truth or SEC filings
   (1 = adds external/made-up data, 5 = purely corpus-grounded)

Return ONLY a JSON array — one object per row, in the same order. No other text before or after.

Format:
[
  {
    "id": <row_id>,
    "faithfulness":       {"score": <1-5>, "reasoning": "<one sentence>"},
    "completeness":       {"score": <1-5>, "reasoning": "<one sentence>"},
    "citation_quality":   {"score": <1-5>, "reasoning": "<one sentence>"},
    "hallucination_free": {"score": <1-5>, "reasoning": "<one sentence>"}
  },
  ...
]"""


def build_batch_prompt(rows: list[dict], config_key: str) -> str:
    lines = [SYSTEM_PROMPT, "", "---", ""]
    for i, row in enumerate(rows, 1):
        ans_obj = row.get(config_key, {})
        generated = ans_obj.get("s", "Answer not found in Corpus")
        if not ans_obj.get("ok", 0):
            generated = "Answer not found in Corpus"

        lines += [
            f"### Row {i} of {len(rows)}  (ID: {row['id']} | {row['co']} {row['yr']})",
            f"**Question:** {row['q']}",
            f"**Ground Truth Answer:** {row['gold']}",
            f"**Generated Answer (Config {config_key.upper()}):** {generated}",
            "",
        ]
    lines += ["---", "", "Now return the JSON array scoring all rows above."]
    return "\n".join(lines)


def aggregate_note(n_batches: int, config: str) -> str:
    return f"""
---

## How to aggregate results

After ChatGPT responds to all {n_batches} prompts, collect the JSON arrays and paste them here:

```json
// Paste each ChatGPT JSON array below, one per line
// Then run: python scripts/export_judge_prompts.py --aggregate results.json
```

Or save each ChatGPT reply into a file called `chatgpt_judge_results.json` as a JSON array of arrays, then run:

```
python scripts/export_judge_prompts.py --aggregate chatgpt_judge_results.json --config {config}
```

This will compute per-dimension means, pass rates, and print the final table.
"""


def aggregate_results(results_file: str, config: str, n: int):
    data = json.loads(Path(results_file).read_text(encoding="utf-8"))
    # data can be: list of lists (one per batch) or flat list
    if data and isinstance(data[0], list):
        rows = [r for batch in data for r in batch]
    else:
        rows = data

    rows = rows[:n]
    dims = ["faithfulness", "completeness", "citation_quality", "hallucination_free"]
    PASS = 0.70

    totals = {d: [] for d in dims}
    for row in rows:
        for d in dims:
            score = row.get(d, {}).get("score", 0)
            totals[d].append(score / 5.0)

    print(f"\n{'='*62}")
    print(f"  LLM-as-Judge Results (GPT-4o via ChatGPT)")
    print(f"  Config: {config.upper()}   n={len(rows)}")
    print(f"{'='*62}")
    for d in dims:
        mean = sum(totals[d]) / len(totals[d]) if totals[d] else 0
        verdict = "PASS" if mean >= PASS else "FAIL"
        label = d.replace("_", " ").title()
        print(f"  {label:<22} {mean:.3f}  {verdict}  (threshold >= {PASS})")
    overall = sum(sum(totals[d]) for d in dims) / (4 * len(rows)) if rows else 0
    pass_rows = sum(
        1 for row in rows
        if all(row.get(d, {}).get("score", 0) / 5.0 >= PASS for d in dims)
    )
    print(f"  {'-'*46}")
    print(f"  Overall Mean:        {overall:.3f}")
    print(f"  Pass Rate:           {pass_rows/len(rows):.1%}")
    print(f"  Sample Size:         {len(rows)}")
    print(f"{'='*62}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20,
                        help="Number of QA pairs to export (default: 20, max: 150)")
    parser.add_argument("--batch", type=int, default=10,
                        help="Rows per ChatGPT prompt (default: 10)")
    parser.add_argument("--config", default="d",
                        choices=["a","b","c","d","e","f","g"],
                        help="Which config's generated answers to judge (default: d)")
    parser.add_argument("--aggregate", default=None,
                        help="Path to JSON file with ChatGPT replies to aggregate")
    args = parser.parse_args()

    if args.aggregate:
        aggregate_results(args.aggregate, args.config, args.n)
        return

    data = load_gold_data()
    rows = data[:args.n]
    batches = [rows[i:i+args.batch] for i in range(0, len(rows), args.batch)]

    out_path = ROOT / "chatgpt_judge_prompts.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# ChatGPT LLM-as-Judge Prompts\n\n")
        f.write(f"**Config:** {args.config.upper()}  |  **Rows:** {len(rows)}  |  "
                f"**Batches:** {len(batches)} (x{args.batch} rows each)\n\n")
        f.write("Paste each section below into a **new ChatGPT conversation** (use GPT-4o). "
                "Copy the JSON array it returns.\n\n---\n\n")

        for bi, batch in enumerate(batches, 1):
            f.write(f"## Prompt {bi} of {len(batches)} "
                    f"(rows {batch[0]['id']}–{batch[-1]['id']})\n\n")
            f.write("```\n")
            f.write(build_batch_prompt(batch, args.config))
            f.write("\n```\n\n")
            f.write(f"**Paste ChatGPT reply for Prompt {bi} here:**\n\n")
            f.write("```json\n// [ChatGPT JSON array goes here]\n```\n\n---\n\n")

        f.write(aggregate_note(len(batches), args.config))

    print(f"Written: {out_path}")
    print(f"  {len(rows)} QA pairs  |  {len(batches)} ChatGPT prompts  "
          f"(~{args.batch} rows each)  |  Config {args.config.upper()}")
    print(f"\nNext steps:")
    print(f"  1. Open {out_path}")
    print(f"  2. Paste each numbered prompt block into a new ChatGPT GPT-4o conversation")
    print(f"  3. Copy the JSON array response back into the file")
    print(f"  4. Save all replies to a file and run:")
    print(f"     python scripts/export_judge_prompts.py --aggregate <replies_file.json> --n {len(rows)}")


if __name__ == "__main__":
    main()
