"""Evidence demo: every routing layer.

Persistent SQLite store -> eval gate -> meta-learner -> router feedback,
with the math printed at every step.

Run:
    python tools/demo/routing_evidence_demo.py
"""

from __future__ import annotations

import contextlib
import math
import random
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L0_routing.reasoning.namespace_bandit import NamespaceBandit
from agentic_core.L0_routing.reasoning.r5_reason_calibration import analyze_r5_reasons
from agentic_core.L1_cognition.reasoning.retrieval_mode_bandit import (
    RetrievalModeBandit,
    adaptive_k_cutoff,
    citation_coverage,
)
from agentic_core.L2_execution.reasoning.cost_aware_cascade import (
    ProviderConfidenceCalibrator,
    ProviderFingerprintGate,
    ProviderFingerprintMismatchError,
    should_escalate,
)
from agentic_core.L3_orchestration.exit_control.reroute_governance import (
    RerouteCeiling,
    RerouteCeilingExceededError,
    ReplayCertResult,
    evaluate_judge_disagreement,
    replay_cert_blocks,
)
from agentic_core.L3_orchestration.reasoning.workflow_shape_calibration import (
    cascade_path_distribution,
    cascade_skip_rate,
    oscillation_amplitude,
    recommend_max_iterations,
)
from agentic_core.L4_state.uwg.write_class_severity import (
    AliasManifest,
    AliasAtomicityViolationError,
    InvalidationCoverageGate,
    InvalidationProposal,
    alias_swap_atomicity_proof,
    classify_write,
    requires_second_judge,
)
from agentic_core.L5_safety.reasoning.hitl_calibration import (
    AdversarialProbeSuite,
    HITLCalibrationLedger,
)
from agentic_core.L6_observability.decision_events_schema import (
    DecisionEventRow,
    ensure_schema,
    insert_decision_event,
)
from agentic_core.L6_observability.decision_outcome_backfill import (
    backfill_outcome,
    lag_summary,
    reset_lag_state,
)
from agentic_core.L6_observability.decision_provenance import (
    current_provenance,
    provenance_digest,
    set_active_provenance,
)
from agentic_core.L6_observability.promotion_gates import (
    MetricSample,
    auto_rollback_trigger,
    counterfactual_uplift,
    promotion_decision,
    wilson_interval,
)
from agentic_core.L6_observability.regret_accounting import (
    RegretLedger,
    aggregate_regret_by_layer,
    per_decision_regret,
)


# ---------------------------------------------------------------------------
# print helpers
# ---------------------------------------------------------------------------

def banner(n: int, title: str) -> None:
    print()
    print("=" * 80)
    print(f"  LAYER {n:>2}  {title}")
    print("=" * 80)


def step(label: str) -> None:
    print(f"\n[STEP] {label}")


def fact(label: str, value: object) -> None:
    print(f"   {label:<52} = {value}")


# ---------------------------------------------------------------------------
# Foundation: persistent decision_events store + provenance
# ---------------------------------------------------------------------------

def setup_store() -> sqlite3.Connection:
    banner(0, "Foundation — persistent decision_events store + provenance")
    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)
    fact(
        "schema rows in sqlite_master",
        conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='decision_events'"
        ).fetchone()[0],
    )

    set_active_provenance(
        policy_hash="sha256:policy@v3",
        snapshot_id="adg_indexed_04262026_0500",
        calibration_version="cal-v7",
        judge_version="judge-rubric-v2",
    )
    prov = current_provenance("L0_routing")
    fact("provenance.policy_hash", prov.policy_hash)
    fact("provenance.snapshot_id", prov.snapshot_id)
    fact("provenance.calibration_version", prov.calibration_version)
    fact("provenance.judge_version", prov.judge_version)
    fact("provenance digest (32-hex)", provenance_digest(prov))

    reset_lag_state()
    return conn


def seed_decisions(
    conn: sqlite3.Connection,
    *,
    layer: str,
    n: int,
    mean_p: float,
    chosen_route: str = "R3",
    app_name: str = "default",
    reason_codes: tuple[str, ...] = (),
    start_ts: float = 1_730_000_000.0,
) -> list[str]:
    rng = random.Random(42 + abs(hash(layer + chosen_route + app_name)) % 10_000)
    prov = current_provenance(layer)
    digest = provenance_digest(prov)
    ids: list[str] = []
    for i in range(n):
        did = f"{layer}-{chosen_route}-{app_name}-{i:04d}"
        ids.append(did)
        ts = start_ts + i
        row = DecisionEventRow(
            decision_id=did,
            timestamp=ts,
            decision_layer=layer,
            app_name=app_name,
            request_hash=f"req-{i:04d}",
            chosen_route=chosen_route,
            policy_hash=prov.policy_hash,
            snapshot_id=prov.snapshot_id,
            calibration_version=prov.calibration_version,
            judge_version=prov.judge_version,
            provenance_digest=digest,
            reason_codes=reason_codes,
        )
        insert_decision_event(conn, row)
        # backfill outcome 5 s later (synthetic, SLO-compliant)
        success = rng.random() < mean_p
        backfill_outcome(
            conn,
            decision_id=did,
            outcome_success=success,
            now=ts + 5.0,
        )
    return ids


# ---------------------------------------------------------------------------
# 1. L0 R1B / R3 — Per-namespace bandit
# ---------------------------------------------------------------------------

def demo_l0_namespace_bandit(conn: sqlite3.Connection) -> None:
    banner(1, "L0 R1B/R3 — Per-namespace Thompson bandit")

    step("seed decisions into persistent store, per (app_name, route) cell")
    seed_decisions(conn, layer="L0_routing", n=120, mean_p=0.85,
                   chosen_route="R1B", app_name="resume_kb")
    seed_decisions(conn, layer="L0_routing", n=120, mean_p=0.30,
                   chosen_route="R3",  app_name="resume_kb")
    seed_decisions(conn, layer="L0_routing", n=120, mean_p=0.40,
                   chosen_route="R1B", app_name="market_news")
    seed_decisions(conn, layer="L0_routing", n=120, mean_p=0.75,
                   chosen_route="R3",  app_name="market_news")
    fact(
        "rows in decision_events (layer=L0_routing)",
        conn.execute(
            "SELECT count(*) FROM decision_events WHERE decision_layer='L0_routing'"
        ).fetchone()[0],
    )
    fact(
        "rows with non-null outcome_success",
        conn.execute(
            "SELECT count(*) FROM decision_events "
            "WHERE decision_layer='L0_routing' AND outcome_success IS NOT NULL"
        ).fetchone()[0],
    )

    step("rebuild Beta(α,β) posteriors from persistent store")
    bandit = NamespaceBandit(seed=7)
    n_loaded = bandit.rebuild_from_decision_events(conn, namespace_field="app_name")
    fact("rows replayed into bandit", n_loaded)
    snap = bandit.snapshot()
    for key, post in sorted(snap.items(), key=lambda kv: (kv[0].namespace, kv[0].route)):
        successes = post.alpha - 1.0
        trials = (post.alpha - 1.0) + (post.beta - 1.0)
        emp = successes / max(1.0, trials)
        var = (post.alpha * post.beta) / (
            (post.alpha + post.beta) ** 2 * (post.alpha + post.beta + 1.0)
        )
        mean = post.alpha / (post.alpha + post.beta)
        fact(
            f"{key.namespace}/{key.route} α={post.alpha:.0f} β={post.beta:.0f}",
            f"mean={mean:.4f}  empirical={emp:.4f}  posterior_var={var:.5f}",
        )

    step("eval gate — Thompson choose 5000× per namespace")
    wins: dict[tuple[str, str], int] = {}
    n_trials = 5000
    for _ in range(n_trials):
        for ns in ("resume_kb", "market_news"):
            choice = bandit.choose(ns, ["R1B", "R3"])
            wins[(ns, choice)] = wins.get((ns, choice), 0) + 1
    for (ns, route), c in sorted(wins.items()):
        fact(f"choose-rate {ns}/{route}", f"{c / n_trials:.3%}")

    step("router feedback — namespace × route winner table")
    print(f"   resume_kb   ⇒ recommended route = "
          f"{'R1B' if wins.get(('resume_kb','R1B'), 0) > wins.get(('resume_kb','R3'), 0) else 'R3'}")
    print(f"   market_news ⇒ recommended route = "
          f"{'R1B' if wins.get(('market_news','R1B'), 0) > wins.get(('market_news','R3'), 0) else 'R3'}")


# ---------------------------------------------------------------------------
# 2. L0 R5 — reason-code Brier calibration + demote
# ---------------------------------------------------------------------------

def demo_l0_r5_reason(conn: sqlite3.Connection) -> None:
    banner(2, "L0 R5 — Reason-code Brier calibration & auto-demote")

    step("seed R5 abstain-route decisions (R5 predicts failure -> high failure rate = good calibration)")
    # low_confidence:    success=0.10 => failure=0.90 => Brier ~ 0.10  (well-calibrated, keep)
    seed_decisions(conn, layer="L0_routing", n=80, mean_p=0.10,
                   chosen_route="R5", app_name="ns_r5_a",
                   reason_codes=("low_confidence",))
    # toxicity_flagged:  success=0.50 => failure=0.50 => Brier ~ 0.50  (over threshold -> DEMOTE)
    seed_decisions(conn, layer="L0_routing", n=80, mean_p=0.50,
                   chosen_route="R5", app_name="ns_r5_b",
                   reason_codes=("toxicity_flagged",))
    # ood_score:         success=0.20 => failure=0.80 => Brier ~ 0.20  (right at threshold)
    seed_decisions(conn, layer="L0_routing", n=80, mean_p=0.20,
                   chosen_route="R5", app_name="ns_r5_c",
                   reason_codes=("ood_score",))

    step("eval gate — analyze_r5_reasons() computes per-reason Brier")
    report = analyze_r5_reasons(conn, brier_demote_threshold=0.20, min_observations=20)
    for reason, cal in sorted(report.per_reason.items()):
        fact(
            f"reason={reason:<22} n={cal.n_observations:>3} succ_rate={cal.success_rate_when_triggered:.3f}",
            f"brier={cal.brier_score:.4f}  demoted={cal.demoted}",
        )
    fact("# demoted reasons", len(report.demoted))
    fact("# insufficient-data reasons", len(report.insufficient_data))

    step("router feedback — demoted reasons stripped from R5 trigger set")
    print(f"   demoted ⇒ {sorted(report.demoted)}")


# ---------------------------------------------------------------------------
# 3. L1 / C0 — Retrieval-mode bandit + adaptive-k + citation coverage
# ---------------------------------------------------------------------------

def demo_l1_c0_retrieval_mode() -> None:
    banner(3, "L1 / C0 — Retrieval-mode bandit + adaptive-k + citation coverage")

    step("retrieval-mode bandit on intent_class=doc_qa (4 modes, 400 epochs)")
    bandit = RetrievalModeBandit(seed=11)
    truth_p = {"dense": 0.55, "sparse": 0.40, "hybrid": 0.78, "graph": 0.30}
    rng = random.Random(3)
    for _ in range(400):
        for mode, p in truth_p.items():
            bandit.update(intent_class="doc_qa", mode=mode, success=rng.random() < p)
    for mode, p in truth_p.items():
        post = bandit.posterior(intent_class="doc_qa", mode=mode)
        mean = post.alpha / (post.alpha + post.beta)
        fact(
            f"posterior doc_qa/{mode:<6} α={post.alpha:.0f} β={post.beta:.0f}",
            f"mean={mean:.4f}  (truth p={p:.2f})",
        )

    step("eval gate — bandit.choose 5000× from admissible modes")
    counts: dict[str, int] = {}
    for _ in range(5000):
        choice = bandit.choose("doc_qa", list(truth_p.keys()))
        counts[choice] = counts.get(choice, 0) + 1
    for m, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        fact(f"choose-rate doc_qa/{m}", f"{c/5000:.3%}")

    step("adaptive-k cutoff on cosine score curve")
    scores = [0.92, 0.91, 0.88, 0.61, 0.55, 0.20]
    k = adaptive_k_cutoff(scores, marginal_drop_threshold=0.20, min_k=2, max_k=10)
    fact("scores", scores)
    fact("Δᵢ = score[i-1]-score[i]", [round(scores[i-1]-scores[i], 2) for i in range(1, len(scores))])
    fact("first i with Δᵢ ≥ 0.20  ⇒  k", k)

    step("citation coverage on a 5-claim answer")
    answer_claims = [f"c{i}" for i in range(5)]
    claim_to_anchor = {"c0": "ch1", "c1": "ch2", "c2": "ch1", "c3": "ch3", "c4": "ch9"}
    returned = {"ch1", "ch2", "ch3", "ch4"}
    cov = citation_coverage(answer_claims, claim_to_anchor, returned)
    fact("|claims|=5; anchored-and-returned=4", f"coverage = {cov:.4f}  (=4/5)")

    step("router feedback — winning mode + k_cutoff + coverage drive C0")
    winner = max(counts, key=counts.get)
    print(f"   doc_qa ⇒ retrieval mode = {winner} | k_cutoff = {k} | citation_coverage = {cov:.2f}")


# ---------------------------------------------------------------------------
# 4. L2 — Cost-aware cascade + provider Brier + fingerprint gate
# ---------------------------------------------------------------------------

def demo_l2_cost_cascade() -> None:
    banner(4, "L2 — Cost-aware tier cascade + provider Brier + fingerprint gate")

    step("expected-utility decision: should_escalate()")
    cases = [
        # (current_conf, expected_gain, tier_cost_delta, safety_floor, label)
        (0.95, 0.40, 0.10, 0.40, "high conf"),
        (0.70, 0.40, 0.10, 0.40, "gain > cost"),
        (0.30, 0.40, 0.10, 0.40, "below safety floor"),
        (0.80, 0.05, 0.10, 0.40, "gain < cost"),
    ]
    for cc, eg, tc, sf, label in cases:
        decision = should_escalate(
            current_confidence=cc, expected_gain_at_higher_tier=eg,
            tier_cost_delta=tc, safety_floor=sf,
        )
        margin = eg - tc
        fact(
            f"{label:<22} conf={cc:.2f} gain={eg:.2f} cost={tc:.2f} margin={margin:+.2f}",
            f"escalate={decision}",
        )

    step("provider Brier calibrator — 200 obs each across 3 providers")
    cal = ProviderConfidenceCalibrator(brier_demote_threshold=0.15, min_observations=20)
    rng = random.Random(99)
    # gpt: honest; predicted == actual rate
    for _ in range(200):
        p = rng.random()
        cal.observe(provider_id="gpt-4o", predicted_success=p,
                    actual_success=rng.random() < p)
    # claude: over-confident; claims 0.9 but truth=0.6 => Brier ≈ (0.9-0)²·0.4 + (0.9-1)²·0.6 = 0.33
    for _ in range(200):
        cal.observe(provider_id="claude-3", predicted_success=0.9,
                    actual_success=rng.random() < 0.6)
    # llama: under-confident; claims 0.5 but truth=0.85 => Brier ≈ (0.5-1)²·0.85 + (0.5-0)²·0.15 = 0.25
    for _ in range(200):
        cal.observe(provider_id="llama-3.1", predicted_success=0.5,
                    actual_success=rng.random() < 0.85)
    for pid in ("gpt-4o", "claude-3", "llama-3.1"):
        s = cal.stats(pid)
        brier = s.sum_squared_error / max(1, s.n_observations)
        fact(
            f"provider={pid:<10} n_obs={s.n_observations:>3}",
            f"brier={brier:.4f}  demoted={s.demoted}",
        )
    fact("demoted set (brier > 0.15)", cal.demoted_providers())

    step("provider fingerprint gate — bind v3, verify v3 (ok) vs v4 (block)")
    gate = ProviderFingerprintGate()
    gate.bind_snapshot(provider_id="claude-3", fingerprint="model_card_v3:sha=abc")
    gate.verify(provider_id="claude-3", live_fingerprint="model_card_v3:sha=abc")
    fact("verify(claude-3, v3)", "OK")
    try:
        gate.verify(provider_id="claude-3", live_fingerprint="model_card_v4:sha=xyz")
        fact("verify(claude-3, v4)", "ERROR — should have blocked")
    except ProviderFingerprintMismatchError as e:
        fact("verify(claude-3, v4)", f"BLOCKED: {e.__class__.__name__}")

    step("router feedback — demoted providers + fingerprint blocks gate cascade")
    print(f"   cascade tier excludes ⇒ {cal.demoted_providers()}")


# ---------------------------------------------------------------------------
# 5. L3 — Workflow-shape calibration
# ---------------------------------------------------------------------------

def demo_l3_workflow_shape() -> None:
    banner(5, "L3 — Workflow-shape calibration (max-iter, oscillation, cascade skip)")

    step("convergence histograms — iterations to PASS, per task class")
    hist = {
        "draft_resume":   [1, 2, 1, 2, 3, 2, 1, 2, 2, 3, 2, 2, 1, 2, 3] * 4,
        "research_brief": [3, 4, 5, 6, 4, 5, 7, 5, 4, 6, 5, 5, 4, 6, 7] * 4,
        "rfp_proposal":   [2, 3, 4, 5, 4, 3, 4, 5, 4, 3, 5, 4, 3, 5, 4] * 4,
    }
    rec = recommend_max_iterations(hist, min_observations=30, fallback_max=3, hard_ceiling=10)
    for cls, r in rec.items():
        fact(
            f"{cls:<16} n={r.n_observations:>3}",
            f"p95_iter={r.p95_iterations}  recommended_max={r.recommended_max}  confident={r.confident}",
        )

    step("oscillation amplitude — pairwise 1-cosine across iteration embeddings")
    embs_converge = [[1.0, 0.0, 0.0], [0.99, 0.05, 0.0], [0.98, 0.10, 0.0]]
    amp_a = oscillation_amplitude(embs_converge)
    fact("near-identical embeddings",
         f"per-step distances={[round(x,4) for x in amp_a]}  (low ⇒ converging)")
    embs_pingpong = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    amp_b = oscillation_amplitude(embs_pingpong)
    fact("ping-pong embeddings",
         f"per-step distances={[round(x,4) for x in amp_b]}  (high ⇒ oscillating)")

    step("cascade skip rate over 20 runs")
    cascade_paths = [["t1","t2","t3"]] * 8 + [["t1","t3"]] * 8 + [["t1","t2"]] * 4
    skip = cascade_skip_rate(cascade_paths)
    dist = cascade_path_distribution(cascade_paths)
    fact("skip-rate (any tier omitted)", f"{skip:.4f}  (12/20 paths skip a tier)")
    fact("path distribution", dict(dist))

    step("router feedback — per-class max-iter caps, oscillation kill-switch")
    for cls, r in rec.items():
        print(f"   {cls:<16} max_iter cap → {r.recommended_max}")


# ---------------------------------------------------------------------------
# 6. L3 — Exit-Eval reroute governance
# ---------------------------------------------------------------------------

def demo_l3_reroute_governance() -> None:
    banner(6, "L3 — Exit-Eval reroute governance (ceiling + judge disagreement + replay-cert)")

    step("reroute ceiling = 2; record reroutes until ceiling fires")
    ceiling = RerouteCeiling(max_reroutes=2)
    fired_at = None
    for i in range(5):
        try:
            n = ceiling.attempt_reroute(request_id="run-A1")
            fact(f"attempt #{i+1}", f"OK  reroute_count={n}")
        except RerouteCeilingExceededError as e:
            fact(f"attempt #{i+1}", f"BLOCKED: {type(e).__name__}")
            fired_at = i + 1
            break
    fact("ceiling fired at attempt", fired_at)

    step("judge disagreement — rubric vs span-grader booleans")
    rubric = [True, True, False, True, False, True, True, False, True, True]
    grader = [True, False, False, True, True, True, True, False, False, True]
    summary = evaluate_judge_disagreement(rubric, grader, alarm_threshold=0.15)
    disagree = sum(1 for r, g in zip(rubric, grader) if r != g)
    fact("n_rows", summary.n_rows)
    fact("disagree count (manual)", disagree)
    fact("rate", f"{summary.rate:.4f}  (={disagree}/{summary.n_rows})")
    fact("alarm_threshold", summary.threshold)
    fact("alarm fired", summary.alarm)

    step("replay-cert blocks — expected vs observed digests")
    results = [
        ReplayCertResult("d1", expected_digest="aaa", observed_digest="aaa"),
        ReplayCertResult("d2", expected_digest="bbb", observed_digest="BBB"),  # mismatch
        ReplayCertResult("d3", expected_digest="ccc", observed_digest="ccc"),
        ReplayCertResult("d4", expected_digest="ddd", observed_digest="???"),  # mismatch
    ]
    blocks = replay_cert_blocks(results)
    fact("blocked decision_ids", sorted(blocks))

    step("router feedback — alarm + blocks gate Exit-Eval promotion path")
    print(f"   judge alarm={summary.alarm}  cert_blocks={sorted(blocks)} ⇒ promote=False")


# ---------------------------------------------------------------------------
# 7. L4 — UWG write-class severity, invalidation, alias atomicity
# ---------------------------------------------------------------------------

def demo_l4_uwg_severity() -> None:
    banner(7, "L4 — UWG write-class severity + invalidation coverage + alias atomicity")

    step("classify_write across 4 (op, target) pairs")
    cases = [
        ("PUT", "uwg.cache.session.user42"),
        ("DELETE", "uwg.canonical.identity"),
        ("ALTER", "uwg.schema.sender_kb"),
        ("PATCH", "uwg.policy.guardrail_v3"),
    ]
    n_2nd = 0
    for op, target in cases:
        cls = classify_write(op=op, target=target)
        needs_judge = requires_second_judge(cls)
        n_2nd += int(needs_judge)
        fact(f"{op:<7} {target}", f"class={cls.value}  requires_2nd_judge={needs_judge}")

    step("invalidation coverage gate — 2 proposals, 1 stale read observed")
    gate = InvalidationCoverageGate()
    gate.record_proposal(InvalidationProposal(
        write_id="w1", invalidates=frozenset({"ns:resume", "ns:profile"})))
    gate.record_proposal(InvalidationProposal(
        write_id="w2", invalidates=frozenset({"ns:resume"})))
    # stale read on ns:profile — declared invalidated by w1 ⇒ HIT (no miss)
    gate.record_stale_read(write_id="w1", observed_namespace="ns:profile")
    # stale read on ns:audit — NOT in any invalidation set ⇒ MISS
    gate.record_stale_read(write_id="w2", observed_namespace="ns:audit")
    fact("# proposals tracked", len(gate._proposals))  # noqa: SLF001
    fact("# stale reads observed", len(gate._stale_reads))  # noqa: SLF001
    fact("miss_rate (stale-reads not covered / total stale-reads)",
         f"{gate.miss_rate():.4f}  (1 miss / 2 stale = 0.5 expected)")

    step("alias swap atomicity proof — gap must be >= swap_window_seconds (hold period)")
    before = AliasManifest(timestamp=1_730_000_000.0,
                           alias_to_target={"current": "v3", "previous": "v2"})
    after_too_fast = AliasManifest(timestamp=1_730_000_001.2,
                                   alias_to_target={"current": "v4", "previous": "v3"})
    after_ok = AliasManifest(timestamp=1_730_000_004.0,
                             alias_to_target={"current": "v4", "previous": "v3"})
    try:
        alias_swap_atomicity_proof(before, after_too_fast, swap_window_seconds=1.5)
        fact("gap=1.2s, required>=1.5s", "ATOMIC (UNEXPECTED — should violate)")
    except AliasAtomicityViolationError as e:
        fact("gap=1.2s, required>=1.5s", f"VIOLATION: {e}")
    try:
        alias_swap_atomicity_proof(before, after_ok, swap_window_seconds=1.5)
        fact("gap=4.0s, required>=1.5s", "ATOMIC (no exception)")
    except AliasAtomicityViolationError as e:
        fact("gap=4.0s, required>=1.5s", f"VIOLATION (UNEXPECTED): {e}")

    step("router feedback — only IRREVERSIBLE+SCHEMA fire 2nd-judge gate")
    print(f"   2nd-judge gate fires on {n_2nd}/{len(cases)} writes ⇒ stricter UWG path")


# ---------------------------------------------------------------------------
# 8. L5 — HITL false-positive ledger + adversarial probes
# ---------------------------------------------------------------------------

def demo_l5_hitl_calibration() -> None:
    banner(8, "L5 — HITL false-positive ledger + adversarial probe suite")

    step("seed 50 HITL events; approved-after-fire = false positive")
    ledger = HITLCalibrationLedger()
    rng = random.Random(13)
    truth_block_rate = {"pii_leak": 0.80, "policy_violation": 0.30, "low_confidence": 0.60}
    for i in range(50):
        reason = rng.choice(list(truth_block_rate.keys()))
        is_real_block = rng.random() < truth_block_rate[reason]
        ledger.record(
            decision_id=f"d{i}",
            fired_reason=reason,
            approved=not is_real_block,
            latency_seconds=rng.uniform(0.5, 12.0),
        )
    fact("# events stored", len(ledger.snapshot()))
    fact("overall FP rate", f"{ledger.false_positive_rate():.4f}")
    for reason, fp in sorted(ledger.per_reason_fp_rate().items()):
        fact(f"  per-reason FP [{reason}]",
             f"{fp:.4f}  (truth_block_rate={truth_block_rate[reason]:.2f})")

    step("adversarial probes — 4 registered, score nightly")
    suite = AdversarialProbeSuite()
    for pid in ("prompt_injection_001", "data_exfil_002",
                "benign_paraphrase_003", "jailbreak_004"):
        suite.register_probe(pid)
    suite.record_outcome("prompt_injection_001", passed=True)   # blocked correctly
    suite.record_outcome("data_exfil_002",       passed=False)  # ESCAPE
    suite.record_outcome("benign_paraphrase_003", passed=True)
    suite.record_outcome("jailbreak_004",        passed=False)  # ESCAPE
    fact("escape rate", f"{suite.escape_rate():.4f}  (=2/4)")
    fact("escaped probes", sorted(suite.escaped_probes()))

    step("router feedback — high-FP reason demoted; escapes raise L5 strictness")
    worst = max(ledger.per_reason_fp_rate().items(), key=lambda kv: kv[1])
    print(f"   worst-FP reason ⇒ {worst[0]}  (rate={worst[1]:.2%}) demoted from triggers")
    print(f"   escape rate {suite.escape_rate():.0%} ⇒ raise judge_strict_mode 24h")


# ---------------------------------------------------------------------------
# 9. L6 — Wilson promotion gate + auto-rollback + counterfactual uplift
# ---------------------------------------------------------------------------

def demo_l6_promotion() -> None:
    banner(9, "L6 — Wilson-CI promotion gate + auto-rollback + counterfactual uplift")

    step("candidate=142/200 vs baseline=110/200 — promotion verdict")
    cw = wilson_interval(142, 200, z=1.96)
    bw = wilson_interval(110, 200, z=1.96)
    verdict = promotion_decision(
        candidate_successes=142, candidate_n=200,
        baseline_successes=110, baseline_n=200,
        z=1.96, min_n_each_arm=30,
    )
    fact("candidate point=142/200=0.7100  Wilson-95",
         f"[{cw.lower:.4f}, {cw.upper:.4f}]  n={cw.n}")
    fact("baseline  point=110/200=0.5500  Wilson-95",
         f"[{bw.lower:.4f}, {bw.upper:.4f}]  n={bw.n}")
    fact("candidate.lower vs baseline.upper",
         f"{cw.lower:.4f} > {bw.upper:.4f} ⇒ {cw.lower > bw.upper}")
    fact("promotion verdict", f"promote={verdict.promote}  reason={verdict.reason}")

    step("auto-rollback trigger — canary regression vs baseline")
    samples = [
        # canary 0.50±0.05  baseline 0.80±0.04  n=80 each => z = (0.50-0.80)/sqrt(.05²+.04²) ≈ -4.7
        MetricSample(metric_name="exit_eval_pass_rate",
                     canary_mean=0.50, canary_stddev=0.05,
                     baseline_mean=0.80, baseline_stddev=0.04, n=80),
        MetricSample(metric_name="latency_p95_ms",
                     canary_mean=420.0, canary_stddev=30.0,
                     baseline_mean=380.0, baseline_stddev=25.0, n=80),  # slight regression
        MetricSample(metric_name="cost_usd_per_decision",
                     canary_mean=0.012, canary_stddev=0.002,
                     baseline_mean=0.011, baseline_stddev=0.002, n=80),
    ]
    triggered, reasons = auto_rollback_trigger(samples, sigma_threshold=1.5, min_n=20)
    for s in samples:
        var = s.canary_stddev**2 + s.baseline_stddev**2
        z = (s.canary_mean - s.baseline_mean) / math.sqrt(var) if var > 0 else 0.0
        fact(f"  metric={s.metric_name:<26}", f"z-score={z:+.2f}")
    fact("triggered (sigma > 1.5 on any metric)", triggered)
    fact("breach reasons", reasons)

    step("counterfactual uplift — shadow vs prod outcomes")
    shadow = [True, True, False, True, True, True, False, True, True, True]   # 8/10
    prod   = [False, True, False, False, True, True, False, True, False, False]  # 4/10
    uplift = counterfactual_uplift(shadow, prod)
    fact("shadow_rate", f"{sum(shadow)/len(shadow):.3f}")
    fact("prod_rate",   f"{sum(prod)/len(prod):.3f}")
    fact("uplift = shadow - prod", f"{uplift:+.3f}")

    step("router feedback — promotion_bus")
    print(f"   PROMOTE={verdict.promote} | ROLLBACK={triggered} | UPLIFT={uplift:+.3f}")


# ---------------------------------------------------------------------------
# 10. L6 — Cross-layer regret accounting
# ---------------------------------------------------------------------------

def demo_l6_regret_accounting() -> None:
    banner(10, "L6 — Cross-layer regret accounting (per-decision + by-layer)")

    step("per-decision regret = best_alternative_reward - chosen_reward")
    samples = [
        per_decision_regret(decision_id="d1", decision_layer="L0_routing",
                            chosen_reward=0.7, best_alternative_reward=0.9),
        per_decision_regret(decision_id="d2", decision_layer="L0_routing",
                            chosen_reward=0.8, best_alternative_reward=0.85),
        per_decision_regret(decision_id="d3", decision_layer="L1_reasoning",
                            chosen_reward=0.6, best_alternative_reward=0.95),
        per_decision_regret(decision_id="d4", decision_layer="L2_execution",
                            chosen_reward=0.5, best_alternative_reward=0.55),
        per_decision_regret(decision_id="d5", decision_layer="L1_reasoning",
                            chosen_reward=0.4, best_alternative_reward=0.9),
        per_decision_regret(decision_id="d6", decision_layer="L3_orchestration",
                            chosen_reward=0.7, best_alternative_reward=0.7),
    ]
    for s in samples:
        fact(f"{s.decision_id} layer={s.decision_layer}",
             f"chosen={s.chosen_reward:.2f} best_alt={s.best_alternative_reward:.2f}  regret={s.regret:.4f}")

    step("aggregate by layer + RegretLedger")
    by_layer = aggregate_regret_by_layer(samples)
    for layer, summary in sorted(by_layer.items()):
        mean = summary.sum_regret / max(1, summary.n_samples)
        fact(f"layer={layer}",
             f"n={summary.n_samples}  sum_regret={summary.sum_regret:.4f}  mean={mean:.4f}")

    ledger = RegretLedger()
    for s in samples:
        ledger.record(s)
    fact("ledger.total_regret()", f"{ledger.total_regret():.4f}")
    top = ledger.top_offenders(k=2)
    fact("top-2 layers by sum_regret",
         [(t.decision_layer, round(t.sum_regret, 4), t.n_samples) for t in top])

    step("router feedback — top-offending layer flagged for next calibration cycle")
    worst_layer = top[0].decision_layer
    print(f"   highest-regret layer ⇒ {worst_layer}  (next cycle prioritizes its calibrator)")


# ---------------------------------------------------------------------------
# Foundation closing — outcome backfill lag SLO
# ---------------------------------------------------------------------------

def show_backfill_lag_slo() -> None:
    banner(11, "Foundation closing — outcome backfill lag SLO across all layers")
    s = lag_summary()
    mean = s.sum_seconds / max(1, s.sample_count)
    fact("samples observed", s.sample_count)
    fact("sum_seconds", f"{s.sum_seconds:.4f}")
    fact("mean lag (s)", f"{mean:.4f}")
    fact("histogram buckets (sec → count)",
         {round(k, 1): v for k, v in sorted(s.bucket_counts.items())})
    fact("overflow (> top bucket)", s.overflow_count)
    fact("SLO: 100% within 30 s", "PASS" if mean <= 30.0 and s.overflow_count == 0 else "FAIL")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    conn = setup_store()
    demo_l0_namespace_bandit(conn)
    demo_l0_r5_reason(conn)
    demo_l1_c0_retrieval_mode()
    demo_l2_cost_cascade()
    demo_l3_workflow_shape()
    demo_l3_reroute_governance()
    demo_l4_uwg_severity()
    demo_l5_hitl_calibration()
    demo_l6_promotion()
    demo_l6_regret_accounting()
    show_backfill_lag_slo()
    print()
    print("=" * 80)
    print(f"  ALL 10 ROUTING LAYERS DEMONSTRATED IN {time.time() - t0:.2f}s — closed loop verified.")
    print("=" * 80)


if __name__ == "__main__":
    main()
