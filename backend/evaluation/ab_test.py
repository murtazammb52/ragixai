"""
7-configuration A/B test orchestrator.
Runs RAGAS evaluation for each config and prints comparison matrix.
"""
from __future__ import annotations

from loguru import logger

from backend.models.schemas import EvalResult, ABTestResponse, JudgeAggregateResult
from backend.evaluation.ragas_eval import run_evaluation

ALL_CONFIGS = ["config_a", "config_b", "config_c", "config_d", "config_e", "config_f", "config_g"]


def run_ab_test(
    configs: list[str] | None = None,
    dataset: str = "financebench",
    sample_size: int = 20,
    run_judge: bool = False,
) -> ABTestResponse:
    configs_to_run = configs or ALL_CONFIGS
    results: list[EvalResult] = []

    for cfg in configs_to_run:
        logger.info(f"\n{'='*50}\nRunning {cfg}...\n{'='*50}")
        try:
            result = run_evaluation(config=cfg, dataset=dataset, sample_size=sample_size)
            results.append(result)
            _print_result(result)
        except Exception as e:
            logger.error(f"Config {cfg} failed: {e}")
            results.append(EvalResult(
                config=cfg, faithfulness=0.0, answer_relevancy=0.0,
                context_precision=0.0, context_recall=0.0,
                answer_correctness=0.0, response_latency_p95_ms=0.0,
                sample_size=0,
            ))

    # Optional LLM-as-Judge pass
    judge_results: dict[str, JudgeAggregateResult] = {}
    if run_judge:
        from backend.evaluation.llm_judge import run_judge_evaluation
        for cfg in configs_to_run:
            logger.info(f"Running LLM judge for {cfg}...")
            try:
                judge_results[cfg] = run_judge_evaluation(
                    config=cfg, dataset=dataset, sample_size=sample_size
                )
            except Exception as e:
                logger.error(f"Judge failed for {cfg}: {e}")

    # Winner: composite score when judge available, RAGAS-only otherwise
    if judge_results:
        winner = max(
            results,
            key=lambda r: (
                r.faithfulness + r.answer_relevancy
                + judge_results[r.config].overall_mean * 2
                if r.config in judge_results else r.faithfulness + r.answer_relevancy
            ),
        ).config if results else "config_d"
    else:
        winner = max(results, key=lambda r: r.faithfulness + r.answer_relevancy).config if results else "config_d"

    comparison_table = []
    for r in results:
        row: dict = {
            "config": r.config,
            "faithfulness": round(r.faithfulness, 3),
            "answer_relevancy": round(r.answer_relevancy, 3),
            "context_precision": round(r.context_precision, 3),
            "context_recall": round(r.context_recall, 3),
            "answer_correctness": round(r.answer_correctness, 3),
            "p95_latency_ms": round(r.response_latency_p95_ms, 0),
            "winner": r.config == winner,
        }
        if r.config in judge_results:
            jr = judge_results[r.config]
            row.update({
                "judge_faithfulness": round(jr.faithfulness_mean, 3),
                "judge_completeness": round(jr.completeness_mean, 3),
                "judge_citation_quality": round(jr.citation_quality_mean, 3),
                "judge_hallucination_free": round(jr.hallucination_free_mean, 3),
                "judge_overall": round(jr.overall_mean, 3),
                "judge_pass_rate": round(jr.pass_rate, 3),
            })
        comparison_table.append(row)

    _print_table(comparison_table)
    return ABTestResponse(results=results, winner=winner, comparison_table=comparison_table)


def _print_result(r: EvalResult):
    logger.info(
        f"{r.config}: faithfulness={r.faithfulness:.3f}  "
        f"relevancy={r.answer_relevancy:.3f}  "
        f"precision={r.context_precision:.3f}  "
        f"p95={r.response_latency_p95_ms:.0f}ms"
    )


def _print_table(table: list[dict]):
    header = f"{'Config':<12} {'Faith':>7} {'Relev':>7} {'Prec':>7} {'Recall':>7} {'Correct':>8} {'p95(ms)':>8} {'Winner':>7}"
    logger.info("\n" + "="*70)
    logger.info(header)
    logger.info("-"*70)
    for row in table:
        star = "★" if row["winner"] else ""
        logger.info(
            f"{row['config']:<12} {row['faithfulness']:>7.3f} {row['answer_relevancy']:>7.3f} "
            f"{row['context_precision']:>7.3f} {row['context_recall']:>7.3f} "
            f"{row['answer_correctness']:>8.3f} {row['p95_latency_ms']:>8.0f} {star:>7}"
        )
    logger.info("="*70)
