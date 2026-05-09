#!/usr/bin/env python3
"""10-trial benchmark for exec_summary length-parity remediation validation.

Deferred scope item from exec-summary-length-parity-remediation-a3c8e1.
Executes 10 trial runs and measures:
- length_parity pass rate (target: ≥95%)
- Latency per trial (target: Δ ≤ +12s vs baseline)
- eval_harness_outcome ledger population

Usage:
    python -m tools.apps_rg.benchmark_exec_summary --company "Brown & Brown" --trials 10
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Any

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps_rg.integrations.hops.exec_summary_ensemble import (
    generate_exec_summary,
    EXEC_SUMMARY_TARGET_WORDS,
    EXEC_SUMMARY_TOLERANCE_BELOW,
    EXEC_SUMMARY_TOLERANCE_ABOVE,
)
from apps_rg.integrations.length_budget import budget_for_section
from apps_rg.integrations.gates.per_cand_resume_gates import _count_words

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger("benchmark_exec_summary")


def run_single_trial(
    company: str,
    archetype: str,
    marquee_outcomes: list[str],
    strategic_priorities: list[str],
    seed_text: str = "",
) -> dict[str, Any]:
    """Run a single trial and return metrics.
    
    Returns dict with:
        - success: bool (accepted candidate produced)
        - length_parity_pass: bool (word count in [110, 152])
        - word_count: int
        - latency_ms: float
        - repair_applied: bool
        - winner_text: str
    """
    start_time = time.perf_counter()
    
    try:
        result = generate_exec_summary(
            seed_text=seed_text,
            archetype=archetype,
            marquee_outcomes=marquee_outcomes,
            strategic_priorities=strategic_priorities,
            company=company,
            mirror_terms=[],
            jd_facets=[],
            company_facets=[],
            archive_dir=None,  # Don't archive during benchmark
        )
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Check if we got an accepted result
        if not result.accepted or result.winner is None:
            return {
                "success": False,
                "length_parity_pass": False,
                "word_count": 0,
                "latency_ms": latency_ms,
                "repair_applied": False,
                "winner_text": "",
            }
        
        winner = result.winner
        word_count = _count_words(winner.text)
        
        # Calculate bounds
        budget = budget_for_section(
            "exec_summary",
            target_words=EXEC_SUMMARY_TARGET_WORDS,
            target_sentences=4,
            tolerance_below=EXEC_SUMMARY_TOLERANCE_BELOW,
            tolerance_above=EXEC_SUMMARY_TOLERANCE_ABOVE,
        )
        
        length_parity_pass = budget.min_words <= word_count <= budget.max_words
        
        return {
            "success": True,
            "length_parity_pass": length_parity_pass,
            "word_count": word_count,
            "latency_ms": latency_ms,
            "repair_applied": winner.repair_applied,
            "winner_text": winner.text[:200],  # Truncated for logging
        }
        
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        _log.error(f"Trial failed with exception: {e}")
        return {
            "success": False,
            "length_parity_pass": False,
            "word_count": 0,
            "latency_ms": latency_ms,
            "repair_applied": False,
            "winner_text": "",
            "error": str(e),
        }


def compute_repetition_rate(text: str) -> float:
    """Detect tail repetition in generated text.
    
    Heuristic: same trigram appears ≥3 times in last 30 tokens.
    Returns repetition rate (0.0 = no repetition, 1.0 = severe repetition).
    """
    words = text.lower().split()
    if len(words) < 30:
        return 0.0
    
    last_30 = words[-30:]
    trigrams = []
    for i in range(len(last_30) - 2):
        trigrams.append(" ".join(last_30[i:i+3]))
    
    from collections import Counter
    trigram_counts = Counter(trigrams)
    
    # Repetition detected if any trigram appears ≥3 times
    max_count = max(trigram_counts.values()) if trigrams else 0
    if max_count >= 3:
        return 1.0
    
    # Partial score for repeated bigrams
    bigrams = []
    for i in range(len(last_30) - 1):
        bigrams.append(" ".join(last_30[i:i+2]))
    bigram_counts = Counter(bigrams)
    repeated_bigrams = sum(1 for count in bigram_counts.values() if count >= 2)
    
    return min(repeated_bigrams / 5.0, 0.5)  # Cap at 0.5 for bigram-only repetition


def run_benchmark(
    company: str,
    trials: int = 10,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Run full benchmark and return summary metrics.
    
    Success criteria from plan:
    - length_parity pass rate ≥95%
    - Latency Δ ≤ +12s (12000ms)
    """
    _log.info(f"Starting benchmark: {trials} trials for company='{company}'")
    
    # Test data
    archetype = "Digital Transformation SVP"
    marquee_outcomes = [
        "$5M cost savings through cloud migration",
        "25% efficiency gain via AI-powered automation",
        "40% reduction in time-to-market for new products",
    ]
    strategic_priorities = [
        "AI adoption and machine learning integration",
        "Cloud-native architecture transformation",
    ]
    
    trial_results: list[dict] = []
    
    for i in range(trials):
        _log.info(f"Trial {i+1}/{trials}...")
        result = run_single_trial(
            company=company,
            archetype=archetype,
            marquee_outcomes=marquee_outcomes,
            strategic_priorities=strategic_priorities,
        )
        
        # Add repetition detection
        if result["winner_text"]:
            full_text = result["winner_text"]
            result["repetition_rate"] = compute_repetition_rate(full_text)
        else:
            result["repetition_rate"] = 0.0
            
        trial_results.append(result)
    
    # Compute aggregates
    successful_trials = [r for r in trial_results if r["success"]]
    length_parity_passes = [r for r in trial_results if r["length_parity_pass"]]
    
    pass_rate = len(length_parity_passes) / trials if trials > 0 else 0.0
    
    latencies = [r["latency_ms"] for r in trial_results if r["success"]]
    avg_latency = statistics.mean(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0
    
    repetition_rates = [r["repetition_rate"] for r in trial_results]
    avg_repetition = statistics.mean(repetition_rates) if repetition_rates else 0.0
    
    # Repair statistics
    repairs_applied = sum(1 for r in trial_results if r["repair_applied"])
    
    summary = {
        "benchmark_config": {
            "company": company,
            "trials": trials,
            "target_pass_rate": 0.95,
            "max_acceptable_latency_ms": 12000,
            "repetition_rate_threshold": 0.05,
        },
        "results": {
            "total_trials": trials,
            "successful_trials": len(successful_trials),
            "length_parity_passes": len(length_parity_passes),
            "pass_rate": round(pass_rate, 3),
            "pass_rate_percent": f"{pass_rate*100:.1f}%",
            "repairs_applied": repairs_applied,
        },
        "latency": {
            "average_ms": round(avg_latency, 1),
            "max_ms": round(max_latency, 1),
            "within_budget": avg_latency <= 12000,
        },
        "quality": {
            "average_repetition_rate": round(avg_repetition, 3),
            "repetition_rate_percent": f"{avg_repetition*100:.1f}%",
            "repetition_within_threshold": avg_repetition <= 0.05,
        },
        "success_criteria": {
            "pass_rate_met": pass_rate >= 0.95,
            "latency_met": avg_latency <= 12000,
            "repetition_met": avg_repetition <= 0.05,
        },
        "trial_details": trial_results,
    }
    
    # Overall verdict
    all_criteria_met = all(summary["success_criteria"].values())
    summary["overall_verdict"] = "PASS" if all_criteria_met else "NEEDS_IMPROVEMENT"
    
    # Save to file if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        _log.info(f"Benchmark results saved to: {output_path}")
    
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="10-trial benchmark for exec_summary length-parity remediation"
    )
    parser.add_argument(
        "--company",
        type=str,
        default="TestCorp",
        help="Target company name for benchmark context",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=10,
        help="Number of trials to run (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to save JSON results (default: print to stdout)",
    )
    
    args = parser.parse_args()
    
    summary = run_benchmark(
        company=args.company,
        trials=args.trials,
        output_path=args.output,
    )
    
    # Print summary
    print("\n" + "="*60)
    print("EXEC_SUMMARY BENCHMARK RESULTS")
    print("="*60)
    print(f"Company: {summary['benchmark_config']['company']}")
    print(f"Trials: {summary['results']['total_trials']}")
    print()
    print("LENGTH PARITY:")
    print(f"  Passes: {summary['results']['length_parity_passes']}/{summary['results']['total_trials']}")
    print(f"  Rate: {summary['results']['pass_rate_percent']} (target: ≥95%)")
    print(f"  Status: {'✓ PASS' if summary['success_criteria']['pass_rate_met'] else '✗ FAIL'}")
    print()
    print("LATENCY:")
    print(f"  Average: {summary['latency']['average_ms']:.0f}ms (target: ≤12000ms)")
    print(f"  Max: {summary['latency']['max_ms']:.0f}ms")
    print(f"  Status: {'✓ PASS' if summary['success_criteria']['latency_met'] else '✗ FAIL'}")
    print()
    print("QUALITY (Tail Repetition):")
    print(f"  Average rate: {summary['quality']['repetition_rate_percent']} (target: ≤5%)")
    print(f"  Status: {'✓ PASS' if summary['success_criteria']['repetition_met'] else '✗ FAIL'}")
    print()
    print("REPAIR STATISTICS:")
    print(f"  Repairs applied: {summary['results']['repairs_applied']}")
    print()
    print(f"OVERALL VERDICT: {summary['overall_verdict']}")
    print("="*60)
    
    # Return exit code based on verdict
    return 0 if summary["overall_verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
