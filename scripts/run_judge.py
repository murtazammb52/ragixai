"""CLI: python scripts/run_judge.py --config config_d --dataset financebench --n 20"""
import os
import argparse
import sys
from pathlib import Path

os.environ.setdefault("RAGAS_DO_NOT_TRACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.evaluation.llm_judge import run_judge_evaluation

THRESHOLD = 0.70


def main():
    parser = argparse.ArgumentParser(description="Run LLM-as-Judge evaluation on a RAG config")
    parser.add_argument("--config", default="config_d",
                        choices=["config_a", "config_b", "config_c", "config_d",
                                 "config_e", "config_f", "config_g"],
                        help="Config to evaluate (default: config_d)")
    parser.add_argument("--dataset", default="financebench",
                        choices=["financebench", "ragas_testset"])
    parser.add_argument("--n", type=int, default=20,
                        help="Number of QA pairs to judge (default: 20)")
    args = parser.parse_args()

    print(f"\nRunning LLM-as-Judge: {args.config} | {args.dataset} | n={args.n}\n")
    result = run_judge_evaluation(
        config=args.config,
        dataset=args.dataset,
        sample_size=args.n,
    )

    def verdict(score: float) -> str:
        return "PASS" if score >= THRESHOLD else "FAIL"

    print(f"\n{'=' * 58}")
    print(f"  LLM-as-Judge Results — {result.config}")
    print(f"{'=' * 58}")
    print(f"  Faithfulness:        {result.faithfulness_mean:.3f}  "
          f"{verdict(result.faithfulness_mean):<4}  (threshold >= {THRESHOLD})")
    print(f"  Completeness:        {result.completeness_mean:.3f}  "
          f"{verdict(result.completeness_mean):<4}  (threshold >= {THRESHOLD})")
    print(f"  Citation Quality:    {result.citation_quality_mean:.3f}  "
          f"{verdict(result.citation_quality_mean):<4}  (threshold >= {THRESHOLD})")
    print(f"  Hallucination-Free:  {result.hallucination_free_mean:.3f}  "
          f"{verdict(result.hallucination_free_mean):<4}  (threshold >= {THRESHOLD})")
    print(f"  ─────────────────────────────────────────────────")
    print(f"  Overall Mean:        {result.overall_mean:.3f}")
    print(f"  Pass Rate:           {result.pass_rate:.1%}")
    print(f"  Sample Size:         {result.sample_size}")
    print(f"  Fallback Count:      {result.fallback_count}")
    print(f"{'=' * 58}\n")


if __name__ == "__main__":
    main()
