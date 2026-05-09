"""CLI: python scripts/run_evaluate.py --config config_d --dataset financebench --n 50"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.evaluation.ragas_eval import run_evaluation


def main():
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation on a RAG configuration")
    parser.add_argument("--config", default="config_d", help="Config to evaluate (default: config_d)")
    parser.add_argument("--dataset", default="financebench", choices=["financebench", "ragas_testset"])
    parser.add_argument("--n", type=int, default=50, help="Number of QA pairs to evaluate")
    args = parser.parse_args()

    print(f"\nEvaluating {args.config} on {args.dataset} ({args.n} samples)...\n")
    result = run_evaluation(config=args.config, dataset=args.dataset, sample_size=args.n)

    print(f"\n{'='*50}")
    print(f"RAGAS Results — {result.config}")
    print(f"{'='*50}")
    print(f"  Faithfulness:       {result.faithfulness:.3f}  (target ≥ 0.89)")
    print(f"  Answer Relevancy:   {result.answer_relevancy:.3f}  (target ≥ 0.87)")
    print(f"  Context Precision:  {result.context_precision:.3f}  (target ≥ 0.84)")
    print(f"  Context Recall:     {result.context_recall:.3f}  (target ≥ 0.84)")
    print(f"  Answer Correctness: {result.answer_correctness:.3f}  (target ≥ 0.82)")
    print(f"  p95 Latency:        {result.response_latency_p95_ms:.0f}ms  (target < 3000ms)")
    print(f"  Sample size:        {result.sample_size}")


if __name__ == "__main__":
    main()
