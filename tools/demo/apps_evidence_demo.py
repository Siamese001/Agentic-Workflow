"""Evidence demo: apps_* routing/metrics/eval/feedback closed loops.

For each app surface, exercises the live router/eval/feedback APIs with synthetic
inputs and prints the math. Fail-soft: if a section's heavy deps are missing, it
prints SKIP and continues.

Run:
    python tools/demo/apps_evidence_demo.py
"""

from __future__ import annotations

import asyncio
import copy
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def banner(label: str) -> None:
    print()
    print("=" * 80)
    print(f"  {label}")
    print("=" * 80)


def step(msg: str) -> None:
    print(f"\n[STEP] {msg}")


def fact(label: str, value: object) -> None:
    print(f"   {label:<54} = {value}")


def safe_section(name: str, fn) -> None:
    banner(name)
    try:
        fn()
    except Exception as exc:  # guardian: allow-broad-catch -- fail-soft per-section demo
        print(f"   SKIP — {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=2)


# ---------------------------------------------------------------------------
# 1. apps_shared.ModelRouter — tier routing + cost telemetry
# ---------------------------------------------------------------------------
def demo_model_router() -> None:
    from apps_shared.reasoning.core.model_router import ModelRouter, TaskType

    step("get_model_config(task_type, complexity_score) for every TaskType")
    router = ModelRouter()
    for tt in TaskType:
        for cx in (1, 5, 9):
            cfg = router.get_model_config(task_type=tt, complexity_score=cx)
            fact(f"task={tt.value:<10} complexity={cx}", cfg)

    step("record_usage simulates 4 LLM calls; get_stats aggregates cost")
    router.record_usage(model_name="gpt-4o", input_tokens=1200,
                        output_tokens=800, cost=0.012)
    router.record_usage(model_name="gpt-4o", input_tokens=900,
                        output_tokens=600, cost=0.009)
    router.record_usage(model_name="claude-3", input_tokens=2000,
                        output_tokens=1500, cost=0.027)
    router.record_usage(model_name="llama-3.1", input_tokens=3000,
                        output_tokens=2000, cost=0.000)
    stats = router.get_stats()
    fact("aggregate stats", stats)
    spent = stats.get("budget_info", {}).get("spent", 0.0)

    step("router feedback — budget_info.spent feeds the cost-aware cascade in L2")
    print(f"   spent = {spent:.4f}  → cost_aware_cascade should_escalate gate")


# ---------------------------------------------------------------------------
# 2. apps_shared.AdaptiveThresholds — quality-feedback closed loop
# ---------------------------------------------------------------------------
def demo_adaptive_thresholds() -> None:
    from apps_shared.types.feedback_loop_types import AdaptiveThresholds

    step("AdaptiveThresholds.adjust_thresholds — acceptance_rate drives delta")
    base = {"excellent": 0.90, "high": 0.75, "good": 0.60, "marginal": 0.45}
    at = AdaptiveThresholds(initial_thresholds=base)
    fact("initial thresholds", base)

    # Case A: acceptance much LOWER than target -> thresholds should ease
    scores_low = [0.55, 0.50, 0.62, 0.48, 0.58, 0.51, 0.49, 0.60]
    new_a = at.adjust_thresholds(quality_scores=scores_low,
                                 acceptance_rate=0.40, target_acceptance=0.75)
    fact("acceptance=0.40 (target 0.75) → eased thresholds", new_a)

    # Case B: acceptance much HIGHER than target -> thresholds should tighten
    at_b = AdaptiveThresholds(initial_thresholds=base)
    scores_hi = [0.92, 0.95, 0.88, 0.93, 0.94, 0.91, 0.96, 0.93]
    new_b = at_b.adjust_thresholds(quality_scores=scores_hi,
                                   acceptance_rate=0.95, target_acceptance=0.75)
    fact("acceptance=0.95 (target 0.75) → tightened thresholds", new_b)

    step("router feedback — adapted thresholds replace static gate constants")
    print(f"   delta on 'excellent' = {new_a['excellent'] - base['excellent']:+.4f} (eased) "
          f"vs {new_b['excellent'] - base['excellent']:+.4f} (tightened)")


# ---------------------------------------------------------------------------
# 3. apps_shared.FeedbackLoopOrchestrator — regenerate-with-feedback loop
# ---------------------------------------------------------------------------
def demo_feedback_loop_orchestrator() -> None:
    from apps_shared.types.feedback_loop_orchestrator_types import (
        FeedbackLoopOrchestrator,
        ConstraintFailureType,
    )

    step("synthetic generator that fails twice then succeeds; validator scores content length")
    state = {"attempt": 0}

    def generator(context: dict) -> str:
        state["attempt"] += 1
        # Each retry produces a longer draft
        return "x" * (50 * state["attempt"])

    def validator(content: str, context: dict):
        n = len(content)
        passes = n >= 140
        return {
            "passed": passes,
            "score": min(1.0, n / 200.0),
            "failure_type": None if passes
                else ConstraintFailureType.LENGTH_VIOLATION.value
                if hasattr(ConstraintFailureType, "LENGTH_VIOLATION")
                else "length",
            "feedback": f"length={n} need>=140",
        }

    # The orchestrator's API is async; the generator/validator may be sync OR async.
    async def async_generator(context: dict) -> str:
        return generator(context)

    async def async_validator(content: str, context: dict):
        return validator(content, context)

    orch = FeedbackLoopOrchestrator(max_attempts=5, checkpoint_saving=True,
                                    reversion_enabled=True)
    result = asyncio.run(orch.execute_with_feedback(
        generator=async_generator,
        validator=async_validator,
        initial_context={"section": "experience", "target": 140},
        k_node_id="rg.experience.gen",
    ))
    fact("attempts taken", result.attempts)
    fact("success", result.success)
    fact("final content length", len(result.final_content))
    fact("checkpoints recorded", len(result.checkpoints))
    fact("reverted / exhausted", f"{result.reverted} / {result.exhausted}")
    for cp in result.checkpoints:
        fact(f"  checkpoint attempt={cp.attempt}", f"score={cp.score:.3f}  T={cp.temperature}")

    step("router feedback — failure report into healing ledger")
    report = orch.generate_failure_report(result, "rg.experience.gen")
    print(f"   failure_report excerpt:\n{report[:240]}")


# ---------------------------------------------------------------------------
# 4. apps_shared.CircuitBreaker — failure threshold gate
# ---------------------------------------------------------------------------
def demo_circuit_breaker() -> None:
    from apps_shared.enforcement.CircuitbreakerStrategy import (
        CircuitBreaker,
        CircuitBreakerConfig,
        CircuitState,
        CircuitOpenError,
    )

    step("CircuitBreaker config: failure_threshold=3, recovery_timeout=0.5s")
    cb = CircuitBreaker(name="downstream-llm",
                        config=CircuitBreakerConfig(failure_threshold=3,
                                                    recovery_timeout=0.5))

    def flaky():
        raise RuntimeError("synthetic downstream failure")

    def healthy():
        return "OK"

    fact("initial state", cb.get_state())

    async def drive_failures():
        for i in range(4):
            try:
                await cb.call(flaky)
            except (RuntimeError, CircuitOpenError) as e:
                fact(f"call #{i+1} ({flaky.__name__})",
                     f"{type(e).__name__}  state={cb.get_state()}")

    asyncio.run(drive_failures())
    fact("stats after open", cb.get_stats())

    step("wait recovery_timeout, then success closes the circuit")
    time.sleep(0.6)

    async def drive_recovery():
        for i in range(3):
            try:
                r = await cb.call(healthy)
                fact(f"recovery call #{i+1}", f"result={r}  state={cb.get_state()}")
            except CircuitOpenError as e:
                fact(f"recovery call #{i+1}", f"BLOCKED: {e}")

    asyncio.run(drive_recovery())
    fact("stats after recovery", cb.get_stats())

    step("router feedback — OPEN state diverts router to fallback provider")
    print(f"   circuit '{cb.name}' final state = {cb.get_state()}")


# ---------------------------------------------------------------------------
# 5. apps_shared.AdaptiveRetrievalGate — should_retrieve gate
# ---------------------------------------------------------------------------
def demo_adaptive_retrieval_gate() -> None:
    from apps_shared.enforcement.AdaptiveretrievalgateStrategy import (
        AdaptiveRetrievalGate,
    )

    step("classify 7 queries through should_retrieve()")
    gate = AdaptiveRetrievalGate()
    queries = [
        "What is 2 + 2?",
        "Summarize the latest 10-K filing for ACME Corp",
        "Hi",
        "Compare carbon-capture policy across the EU and US in 2024",
        "thx",
        "Find the contract clause about liability caps in our master agreement",
        "ok",
    ]
    decisions = []
    for q in queries:
        d = gate.should_retrieve(query=q, history=[])
        decisions.append(d)
        fact(f"query={q[:40]!r:<44}",
             f"retrieve={d.should_retrieve}  type={d.query_type}  conf={d.confidence:.2f}  "
             f"reason={d.reason[:40]}")

    step("aggregate statistics across decision list")
    stats = gate.get_statistics(decisions)
    fact("statistics", stats)

    step("router feedback — should_retrieve=False short-circuits C0 retrieval plan")
    n_skip = sum(1 for d in decisions if not d.should_retrieve)
    print(f"   {n_skip}/{len(decisions)} queries skip retrieval ⇒ token + latency saved")


# ---------------------------------------------------------------------------
# 6. apps_rg ConfidenceMetrics + EarlyStoppingStrategy + PathPruning
# ---------------------------------------------------------------------------
def demo_apps_rg_confidence() -> None:
    try:
        from apps_rg.reasoning.ConfidencemetricsStrategy import (
            ConfidenceEstimator,
            EarlyStoppingStrategy,
            PathPruningStrategy,
        )
    except ModuleNotFoundError:
        step("apps_rg/reasoning removed — skip confidence demo")
        return

    step("synthetic reasoning chain — 6 steps with rising confidence")
    steps = [
        {"content": "step 1: parse JD", "score": 0.40},
        {"content": "step 2: extract themes", "score": 0.55},
        {"content": "step 3: match achievements", "score": 0.70},
        {"content": "step 4: rank by impact", "score": 0.83},
        {"content": "step 5: write bullets", "score": 0.92},
        {"content": "step 6: polish", "score": 0.97},
    ]
    estimator = ConfidenceEstimator()
    confidences = [estimator.estimate_step_confidence(step=s) for s in steps]
    for s, c in zip(steps, confidences):
        fact(f"step content={s['content'][:24]!r:<26}", f"step_confidence={c:.4f}")

    step("EarlyStoppingStrategy.should_stop_early at each step")
    stopper = EarlyStoppingStrategy(confidence_threshold=0.95,
                                    convergence_threshold=0.90,
                                    min_steps=2, max_steps=8)
    for i, c in enumerate(confidences):
        decision = stopper.should_stop_early(steps=steps[:i+1],
                                             current_confidence=c,
                                             current_step=i+1)
        # Decision may be (bool, reason) tuple
        if isinstance(decision, tuple):
            stop, reason = decision[0], decision[1] if len(decision) > 1 else ""
        else:
            stop, reason = bool(decision), ""
        fact(f"step {i+1} conf={c:.3f}", f"stop_early={stop}  reason={reason}")

    step("PathPruningStrategy.should_prune at min_confidence=0.80")
    pruner = PathPruningStrategy(min_confidence=0.80)
    for c in [0.30, 0.55, 0.70, 0.81, 0.95]:
        fact(f"confidence={c:.2f}", f"prune={pruner.should_prune(confidence=c)}")

    step("router feedback — early-stop + prune compress chain length / token spend")
    print("   early stop on conf>=0.95 ⇒ skip remaining steps; prune cuts low-conf branches")


# ---------------------------------------------------------------------------
# 7. apps_lic OutreachSignalRouterAgent — signal-driven strategy router
# ---------------------------------------------------------------------------
def demo_apps_lic_router() -> None:
    from apps_lic.reasoning.OutreachSignalRouterAgent import (
        OutreachSignalRouterAgent,
        OutreachHealingStrategy,
    )

    step("determine_strategy(cycle, signals, modified_sections) over 5 scenarios")
    scenarios = [
        # cycle, signals, modified_sections
        (0, set(), set()),
        (1, {"low_quality_score"}, {"subject_line"}),
        (2, {"compliance_violation", "pii_leak"}, {"body"}),
        (3, {"low_quality_score", "low_relevance"}, {"subject_line", "body"}),
        (4, {"convergence_signal"}, set()),
    ]
    for cycle, signals, mods in scenarios:
        try:
            strat = OutreachSignalRouterAgent.determine_strategy(
                cycle_number=cycle, signals=signals, modified_sections=mods)
            crit = OutreachSignalRouterAgent.has_critical_signal(signals=signals)
            agents = OutreachSignalRouterAgent.get_agents_for_signals(signals=signals)
            fact(f"cycle={cycle} signals={sorted(signals) or '∅'}",
                 f"strategy={strat.value}  critical={crit}  agents={agents}")
        except Exception as e:  # guardian: allow-broad-catch -- demo fail-soft
            fact(f"cycle={cycle}", f"ERROR {type(e).__name__}: {e}")

    step("router feedback — strategy enum drives next OutreachHealingCycle.execute()")
    print(f"   available strategies: {[s.name for s in OutreachHealingStrategy]}")


# ---------------------------------------------------------------------------
# 8. apps_eval EvalGateValidator — gate over scorecards + regressions
# ---------------------------------------------------------------------------
def demo_apps_eval_gate() -> None:
    from apps_eval.validators.eval_gate_validator import EvalGateValidator
    from apps_eval.types.eval_types import (
        SuiteResult,
        ScorecardRow,
        RegressionRecord,
    )

    step("build synthetic eval inputs — 1 healthy suite + 1 regression")
    suites = [
        SuiteResult(suite_id="rg_quality", display_name="RG Quality Suite",
                    pass_rate=0.92, mean_latency_ms=820.0),
        SuiteResult(suite_id="rg_safety", display_name="RG Safety Suite",
                    pass_rate=0.98, mean_latency_ms=140.0),
    ]
    scorecard = [
        ScorecardRow(dimension_id="relevance", display_name="Relevance",
                     score=0.84, weight=0.4, weighted_score=0.336, verdict="PASS",
                     suite_id="rg_quality"),
        ScorecardRow(dimension_id="clarity", display_name="Clarity",
                     score=0.78, weight=0.3, weighted_score=0.234, verdict="PASS",
                     suite_id="rg_quality"),
        ScorecardRow(dimension_id="completeness", display_name="Completeness",
                     score=0.55, weight=0.3, weighted_score=0.165, verdict="WARN",
                     suite_id="rg_quality"),
    ]
    regressions = [
        RegressionRecord(suite_id="rg_quality", dimension_id="relevance",
                         current_score=0.84, baseline_score=0.86,
                         delta=-0.02, verdict="WARN"),
        RegressionRecord(suite_id="rg_quality", dimension_id="completeness",
                         current_score=0.55, baseline_score=0.78,
                         delta=-0.23, verdict="REGRESSION"),
    ]
    overall = sum(r.weighted_score for r in scorecard)
    fact("overall_score (Σ weighted)", f"{overall:.4f}")

    step("validate(min=0.7, fail_on_regression=True)")
    validator = EvalGateValidator(min_overall_score=0.7,
                                  fail_on_regression=True,
                                  max_timeout_violations=0)
    result = validator.validate(suite_results=suites, scorecard_rows=scorecard,
                                regression_records=regressions,
                                overall_score=overall)
    fact("result.passed", result.passed)
    fact("result.overall_score", f"{result.overall_score:.4f}")
    for v in result.violations:
        fact(f"  violation [{v.severity}]", f"{v.rule_id}: {v.message[:60]}")

    step("router feedback — passed=False blocks promotion in L6 promotion_gates")
    print(f"   eval-gate verdict ⇒ promote={result.passed}; "
          f"REGRESSION dimension routes to repair queue")


# ---------------------------------------------------------------------------
# 9. apps_underwriting_ai IntakeRouter — file-type routing
# ---------------------------------------------------------------------------
def demo_apps_uw_intake() -> None:
    from apps_underwriting_ai.ingestion.intake_router import IntakeRouter

    step("ingest_json(strict=False) on three payloads")
    router = IntakeRouter()
    sample_path = REPO_ROOT / "apps_underwriting_ai" / "examples" / "sample_underwriting_request.json"
    base = json.loads(sample_path.read_text(encoding="utf-8"))
    fact("sample request loaded from", sample_path.name)
    fact("  request_id / amount / term",
         f"{base['request_id']} / {base['requested_amount']} / {base['requested_term_months']}")
    # Variant A: pristine
    pristine = base
    # Variant B: missing required submission_ts
    missing_ts = copy.deepcopy(base)
    missing_ts["submission_ts"] = ""
    # Variant C: out-of-range amount/term
    bad_range = copy.deepcopy(base)
    bad_range["requested_amount"] = 0
    bad_range["requested_term_months"] = 0
    cases = [
        (pristine,    "well-formed"),
        (missing_ts,  "missing submission_ts"),
        (bad_range,   "out-of-range values"),
    ]
    for payload, label in cases:
        result = router.ingest_json(data=payload,
                                    request_id=f"req-{label[:6]}",
                                    strict_mode=False)
        fact(f"payload={label:<22}",
             f"ok={result.success}  warns={len(result.warnings)} errs={len(result.errors)}")
        if result.warnings:
            fact("  warnings[0:2]", result.warnings[:2])
        if result.errors:
            fact("  errors[0:2]", result.errors[:2])

    step("router feedback — provenance dict + errors gate downstream policy_adapter")
    print("   IngestionResult.provenance flows to L4 UWG canonical store")


# ---------------------------------------------------------------------------
# 10. apps_exec / apps_research / apps_rfp — share apps_shared.ModelRouter
# ---------------------------------------------------------------------------
def demo_shared_consumers() -> None:
    from apps_shared.reasoning.core.model_router import ModelRouter, TaskType

    step("the 3 brief-style apps reuse apps_shared.ModelRouter — 1 stats ledger")
    router = ModelRouter()
    # Each app contributes synthetic usage rows
    runs = [
        ("apps_exec/exec_brief",       TaskType.ANALYTICAL, 4, 0.018),
        ("apps_research/brief",        TaskType.COMPLEX,    7, 0.034),
        ("apps_research/brief_redo",   TaskType.COMPLEX,    8, 0.041),
        ("apps_rfp/proposal_section",  TaskType.CREATIVE,   6, 0.027),
        ("apps_rfp/proposal_polish",   TaskType.SIMPLE,     2, 0.004),
    ]
    for app, tt, cx, cost in runs:
        cfg = router.get_model_config(task_type=tt, complexity_score=cx)
        router.record_usage(model_name=cfg["model"], input_tokens=1500,
                            output_tokens=900, cost=cost)
        fact(f"{app:<32} tt={tt.value:<10} cx={cx}", f"cfg={cfg}  cost={cost}")
    stats = router.get_stats()
    fact("aggregate stats across 3 apps", stats)
    spent = stats.get("budget_info", {}).get("spent", 0.0)
    remaining = stats.get("budget_info", {}).get("remaining", 0.0)
    daily = stats.get("budget_info", {}).get("daily_budget", 0.0)

    step("router feedback — shared cost ledger feeds L6 promotion + cost cascade")
    print(f"   spent = {spent:.4f} / daily_budget {daily:.2f}  (remaining = {remaining:.4f})")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

SECTIONS = [
    ("apps_shared.ModelRouter — tier routing + cost telemetry",
     demo_model_router),
    ("apps_shared.AdaptiveThresholds — quality feedback closed loop",
     demo_adaptive_thresholds),
    ("apps_shared.FeedbackLoopOrchestrator — regenerate-with-feedback",
     demo_feedback_loop_orchestrator),
    ("apps_shared.CircuitBreaker — failure threshold gate",
     demo_circuit_breaker),
    ("apps_shared.AdaptiveRetrievalGate — should_retrieve gate",
     demo_adaptive_retrieval_gate),
    ("apps_rg ConfidenceMetrics + EarlyStopping + PathPruning",
     demo_apps_rg_confidence),
    ("apps_lic OutreachSignalRouterAgent — signal-driven strategy",
     demo_apps_lic_router),
    ("apps_eval EvalGateValidator — gate over scorecards + regressions",
     demo_apps_eval_gate),
    ("apps_underwriting_ai IntakeRouter — file-type ingestion",
     demo_apps_uw_intake),
    ("apps_exec/apps_research/apps_rfp — shared ModelRouter consumers",
     demo_shared_consumers),
]


def main() -> None:
    t0 = time.time()
    for label, fn in SECTIONS:
        safe_section(label, fn)
    print()
    print("=" * 80)
    print(f"  {len(SECTIONS)} apps_* surfaces exercised in {time.time() - t0:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
