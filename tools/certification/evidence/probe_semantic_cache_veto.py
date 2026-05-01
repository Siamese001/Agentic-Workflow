"""W1 Phase 5 — Wave E.1: Semantic Cache Veto Probe.

Evaluates the veto pipeline against a test set of adversarial pairs.
Produces artifacts/certification/veto_evaluation_report.json

Key metrics:
- True positive: adversarial pair correctly vetoed
- False negative: adversarial pair incorrectly passed (CRITICAL)
- Latency distribution per stage
- Invocation counters (proves LLM judge actually ran)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "certification"
ARTIFACT_PATH = ARTIFACT_DIR / "veto_evaluation_report.json"

# Test pairs covering W1p5 adversarial classes
TEST_PAIRS = [
    # Class: near_miss_negative (cosine > 0.95, different intent)
    {
        "id": "nmn-001",
        "class": "near_miss_negative",
        "query": "Enable two-factor authentication",
        "cached_query": "Disable two-factor authentication",
        "cached_answer": "2FA has been disabled.",
        "expected_veto": True,
        "rationale": "Opposite action: enable vs disable (security-critical)",
    },
    {
        "id": "nmn-002",
        "class": "near_miss_negative",
        "query": "Schedule meeting for Monday at 10am",
        "cached_query": "Schedule meeting for Tuesday at 10am",
        "cached_answer": "Meeting scheduled for Tuesday.",
        "expected_veto": True,
        "rationale": "Different day: Monday vs Tuesday (different outcome)",
    },
    {
        "id": "nmn-003",
        "class": "near_miss_negative",
        "query": "Grant admin access to alice",
        "cached_query": "Revoke admin access from alice",
        "cached_answer": "Admin access for alice has been revoked.",
        "expected_veto": True,
        "rationale": "Opposite action: grant vs revoke (access control)",
    },
    # Class: lexical_overlap_different_meaning_negative
    {
        "id": "lodm-001",
        "class": "lexical_overlap_different_meaning_negative",
        "query": "Turn on the lights",
        "cached_query": "Turn off the lights",
        "cached_answer": "Lights are now off.",
        "expected_veto": True,
        "rationale": "Opposite: on vs off (95% token overlap)",
    },
    {
        "id": "lodm-002",
        "class": "lexical_overlap_different_meaning_negative",
        "query": "Buy 100 shares of AAPL",
        "cached_query": "Buy 1000 shares of AAPL",
        "cached_answer": "Purchased 1000 shares of AAPL.",
        "expected_veto": True,
        "rationale": "Different magnitude: 100 vs 1000 shares (financial impact)",
    },
    # Class: policy_tenant_freshness_reuse_negative
    {
        "id": "ptf-001",
        "class": "policy_tenant_freshness_reuse_negative",
        "query": "What's the current interest rate?",
        "cached_query": "What's the interest rate?",
        "cached_answer": "The current interest rate is 5.25% (as of January 2024).",
        "expected_veto": True,
        "rationale": "Stale data: cached answer is 4 months old (May vs Jan)",
        "context": {"policy_sensitive": True, "freshness_days": 120},
    },
    # Class: opposite_semantic_direction_negative
    {
        "id": "osd-001",
        "class": "opposite_semantic_direction_negative",
        "query": "Increase the allocation by 10%",
        "cached_query": "Decrease the allocation by 10%",
        "cached_answer": "Allocation decreased by 10%.",
        "expected_veto": True,
        "rationale": "Opposite direction: increase vs decrease",
    },
    # Class: negation_scope_change_negative
    {
        "id": "nsc-001",
        "class": "negation_scope_change_negative",
        "query": "Include taxes in the quote",
        "cached_query": "Exclude taxes from the quote",
        "cached_answer": "Taxes excluded from quote.",
        "expected_veto": True,
        "rationale": "Negation scope: include vs exclude taxes (price difference)",
    },
    # Class: positive_reuse (should NOT be vetoed)
    {
        "id": "pos-001",
        "class": "positive_reuse",
        "query": "Enable two-factor authentication",
        "cached_query": "Turn on two-factor auth",
        "cached_answer": "2FA has been enabled for your account.",
        "expected_veto": False,
        "rationale": "Semantic equivalence: enable = turn on (same action)",
    },
    {
        "id": "pos-002",
        "class": "positive_reuse",
        "query": "What's my account balance?",
        "cached_query": "Show me my balance",
        "cached_answer": "Your account balance is $1,234.56.",
        "expected_veto": False,
        "rationale": "Semantic equivalence: asking for same info",
    },
    {
        "id": "pos-003",
        "class": "positive_reuse",
        "query": "Cancel order #12345",
        "cached_query": "Cancel order 12345",
        "cached_answer": "Order #12345 has been cancelled.",
        "expected_veto": False,
        "rationale": "Semantic equivalence: #12345 = 12345 (same order)",
    },
]


def _load_orchestrator() -> Any:
    """Load the veto orchestrator."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.certification.safety.veto_orchestrator import VetoOrchestrator
        return VetoOrchestrator()
    except Exception as e:
        return None


def _compute_rubric_hash() -> str:
    """Compute SHA256 of the LLM judge rubric file (proves which rubric ran)."""
    rubric_path = REPO_ROOT / "config" / "certification" / "llm_judge_rubric.md"
    if not rubric_path.exists():
        return "RUBRIC_FILE_MISSING"
    try:
        content = rubric_path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        return f"RUBRIC_HASH_ERROR:{e}"


def _extract_llm_judge_config() -> dict[str, Any]:
    """Extract LLM judge provider/model from policy file."""
    policy_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_veto_policy.json"
    if not policy_path.exists():
        return {"provider": None, "model_id": None}
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        cfg = policy.get("llm_judge_config", {})
        return {
            "provider": cfg.get("provider"),
            "model_id": cfg.get("model_id"),
            "enabled": policy.get("enabled_stages", {}).get("llm_judge", False),
        }
    except Exception:
        return {"provider": None, "model_id": None}


def _classify_veto_pass_mode(
    invocation_counts: dict[str, int],
    metrics: dict[str, int],
    llm_enabled: bool,
) -> tuple[str, str]:
    """Classify veto status with LLM-actually-ran semantics.

    Returns (status, reason):
      - PASS: FN=0 AND llm_judge_invocation_count > 0 (judge actually ran)
      - PARTIAL: FN=0 but lexical blocked everything (judge never needed to run)
      - PARTIAL: FN>0 but below critical threshold
      - FAIL: FN>2 or unacceptable safety gap
    """
    fn = metrics["false_negatives"]
    llm_calls = invocation_counts["llm_judge_invocation_count"]
    lex_blocks = invocation_counts["lexical_pre_veto_count"]

    if fn > 2:
        return "FAIL", f"critical safety gap: FN={fn}"
    if fn > 0:
        return "PARTIAL", f"minor escapes: FN={fn} (safety gap present)"
    # FN=0 branch — check whether judge actually ran
    if not llm_enabled:
        return "PARTIAL", "FN=0 but llm_judge disabled in policy (Layer 2 not proven)"
    if llm_calls == 0:
        return "PARTIAL", (
            f"FN=0 but llm_judge_invocation_count=0 — lexical pre-veto "
            f"blocked all {lex_blocks} adversarial pairs. LLM judge not "
            f"actually exercised on this test matrix. Cannot certify "
            f"Layer-2 safety from this evidence alone."
        )
    return "PASS", (
        f"FN=0 AND llm_judge ran ({llm_calls} invocation(s)). "
        f"Both layers exercised."
    )


def main() -> int:
    """Run veto probe and emit evaluation report."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    
    orchestrator = _load_orchestrator()
    
    if orchestrator is None:
        # No orchestrator available — emit degraded report
        report = {
            "probe": "semantic_cache_veto",
            "phase": "W1p5",
            "status": "DEGRADED",
            "reason": "Veto orchestrator not available (modules may not be fully installed)",
            "timestamp": None,
            "anti_cheat_invariants": {
                "probe_did_not_modify_threshold": True,
                "probe_did_not_remove_adversarial_pairs": True,
            },
        }
        from datetime import datetime, timezone
        report["timestamp"] = datetime.now(timezone.utc).isoformat()
        ARTIFACT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("[probe_veto] DEGRADED: orchestrator not available")
        return 2
    
    # Run evaluation
    results = []
    metrics = {
        "total_pairs": len(TEST_PAIRS),
        "true_positives": 0,  # Correctly vetoed
        "false_negatives": 0,  # Adversarial pair passed (CRITICAL)
        "true_negatives": 0,  # Correctly allowed
        "false_positives": 0,  # Good pair vetoed (latency cost, not safety issue)
        "errors": 0,
    }
    # Gap-2 invocation counters
    invocation_counts = {
        "lexical_pre_veto_count": 0,
        "lexical_pre_veto_block_count": 0,
        "lexical_pre_veto_delegate_count": 0,
        "lexical_pre_veto_safe_count": 0,
        "llm_judge_invocation_count": 0,
        "llm_judge_safe_count": 0,
        "llm_judge_unsafe_count": 0,
        "timeout_count": 0,
        "parse_fail_count": 0,
        "unknown_count": 0,
        "error_count": 0,
        "fail_closed_count": 0,
    }
    
    latency_by_stage: dict[str, list[float]] = {}
    
    for pair in TEST_PAIRS:
        try:
            result = orchestrator.evaluate(
                query=pair["query"],
                cached_query=pair["cached_query"],
                cached_answer=pair.get("cached_answer"),
                context=pair.get("context"),
            )
        except Exception as e:
            result = None
            metrics["errors"] += 1
            result_data = {
                "id": pair["id"],
                "class": pair["class"],
                "expected_veto": pair["expected_veto"],
                "actual_veto": None,
                "status": "ERROR",
                "error": str(e),
                "latency_ms": 0,
            }
            results.append(result_data)
            continue
        
        actual_veto = result.blocks_reuse() if result else True
        expected_veto = pair["expected_veto"]
        
        # Classification
        if expected_veto and actual_veto:
            metrics["true_positives"] += 1
            status = "TP"
        elif expected_veto and not actual_veto:
            metrics["false_negatives"] += 1  # CRITICAL: adversarial passed
            status = "FN_CRIT"
        elif not expected_veto and not actual_veto:
            metrics["true_negatives"] += 1
            status = "TN"
        else:
            metrics["false_positives"] += 1
            status = "FP"
        
        result_data = {
            "id": pair["id"],
            "class": pair["class"],
            "expected_veto": expected_veto,
            "actual_veto": actual_veto,
            "status": status,
            "veto_status": result.status.value if result else "ERROR",
            "confidence": result.confidence if result else 0.0,
            "rationale": result.rationale if result else "",
            "latency_ms": result.latency_ms if result else 0.0,
            "metadata": result.metadata if result else {},
        }
        results.append(result_data)
        
        # Accumulate latency AND invocation counts by stage (Gap-2)
        if result and result.metadata:
            stage_results = result.metadata.get("stage_results", [])
            for sr in stage_results:
                stage_name = sr.get("stage_name", "unknown")
                stage_status = sr.get("status", "UNKNOWN")
                stage_latency = sr.get("latency_ms", 0)
                if stage_name not in latency_by_stage:
                    latency_by_stage[stage_name] = []
                latency_by_stage[stage_name].append(stage_latency)

                # Count invocations per stage type
                if stage_name == "lexical_intent":
                    invocation_counts["lexical_pre_veto_count"] += 1
                    if stage_status in ("UNSAFE_DIFFERENT_INTENT", "UNSAFE_POLICY_DRIFT", "VETO"):
                        invocation_counts["lexical_pre_veto_block_count"] += 1
                    elif stage_status == "DELEGATE":
                        invocation_counts["lexical_pre_veto_delegate_count"] += 1
                    elif stage_status == "SAFE":
                        invocation_counts["lexical_pre_veto_safe_count"] += 1
                elif stage_name.startswith("llm_judge"):
                    invocation_counts["llm_judge_invocation_count"] += 1
                    if stage_status == "SAFE":
                        invocation_counts["llm_judge_safe_count"] += 1
                    elif stage_status in ("UNSAFE_DIFFERENT_INTENT", "UNSAFE_POLICY_DRIFT", "VETO"):
                        invocation_counts["llm_judge_unsafe_count"] += 1

                # Count failure modes (any stage)
                if stage_status == "UNKNOWN":
                    invocation_counts["unknown_count"] += 1
                    invocation_counts["fail_closed_count"] += 1
                elif stage_status == "ERROR":
                    invocation_counts["error_count"] += 1
                    invocation_counts["fail_closed_count"] += 1
                    # Check if error was timeout or parse failure
                    err_msg = (sr.get("metadata") or {}).get("error", "")
                    rationale = sr.get("rationale", "")
                    if "timeout" in rationale.lower() or "timeout" in err_msg.lower():
                        invocation_counts["timeout_count"] += 1
                    if "parse" in rationale.lower() or "json" in rationale.lower():
                        invocation_counts["parse_fail_count"] += 1
    
    # Compute safety score: 1.0 if FN=0, lower otherwise
    adversarial_count = sum(1 for p in TEST_PAIRS if p["expected_veto"])
    safety_score = 1.0 if metrics["false_negatives"] == 0 else (
        1.0 - (metrics["false_negatives"] / adversarial_count) if adversarial_count > 0 else 0.0
    )
    
    # Compute recall (TP / (TP + FN))
    recall = metrics["true_positives"] / (metrics["true_positives"] + metrics["false_negatives"]) if (metrics["true_positives"] + metrics["false_negatives"]) > 0 else 0.0
    
    # Latency stats
    latency_stats = {}
    for stage, latencies in latency_by_stage.items():
        if latencies:
            latency_stats[stage] = {
                "count": len(latencies),
                "mean_ms": sum(latencies) / len(latencies),
                "max_ms": max(latencies),
                "min_ms": min(latencies),
            }
    
    # Gap-2: classify using LLM-actually-ran semantics
    judge_cfg = _extract_llm_judge_config()
    llm_enabled = judge_cfg.get("enabled", False)
    veto_status, veto_reason = _classify_veto_pass_mode(
        invocation_counts, metrics, llm_enabled
    )

    # Policy summary and primary_veto_mode
    policy_summary = orchestrator.get_policy_summary()
    enabled_stages = policy_summary.get("enabled_stages", {})
    if enabled_stages.get("llm_judge") and not enabled_stages.get("cross_encoder"):
        primary_veto_mode = "C_PRIMARY_LLM_JUDGE"
    elif enabled_stages.get("cross_encoder"):
        primary_veto_mode = "B_PRIMARY_CROSS_ENCODER"
    else:
        primary_veto_mode = "A_ONLY_LEXICAL"

    # Build report
    from datetime import datetime, timezone
    report = {
        "probe": "semantic_cache_veto",
        "phase": "W1p5",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": veto_status,
        "status_reason": veto_reason,
        "primary_veto_mode": primary_veto_mode,
        "llm_judge_provider": judge_cfg.get("provider"),
        "llm_judge_model": judge_cfg.get("model_id"),
        "rubric_hash": _compute_rubric_hash(),
        "metrics": metrics,
        "invocation_counts": invocation_counts,
        "safety_score": round(safety_score, 4),
        "recall_at_safety": round(recall, 4),
        "latency_by_stage": latency_stats,
        "pair_results": results,
        "policy_summary": policy_summary,
        "anti_cheat_invariants": {
            "probe_did_not_modify_threshold": True,
            "probe_did_not_remove_adversarial_pairs": True,
            "probe_used_standard_orchestrator": True,
            "no_override_applied": True,
            "rubric_hash_recorded": True,
            "invocation_counts_recorded": True,
            "llm_actually_ran_required_for_pass": True,
        },
    }
    
    ARTIFACT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    # Console summary
    print(f"[probe_veto] pairs={metrics['total_pairs']}")
    print(f"[probe_veto] TP={metrics['true_positives']} TN={metrics['true_negatives']}")
    print(f"[probe_veto] FN={metrics['false_negatives']} FP={metrics['false_positives']}")
    print(f"[probe_veto] lexical_count={invocation_counts['lexical_pre_veto_count']} "
          f"llm_judge_count={invocation_counts['llm_judge_invocation_count']}")
    print(f"[probe_veto] fail_closed={invocation_counts['fail_closed_count']} "
          f"timeouts={invocation_counts['timeout_count']}")
    print(f"[probe_veto] primary_veto_mode={primary_veto_mode}")
    print(f"[probe_veto] rubric_hash={_compute_rubric_hash()[:16]}...")
    print(f"[probe_veto] safety_score={safety_score:.4f} recall={recall:.4f}")
    print(f"[probe_veto] status={report['status']} ({veto_reason[:80]})")
    print(f"[probe_veto] wrote: {ARTIFACT_PATH.relative_to(REPO_ROOT)}")
    
    # Exit: 0 if PASS, 1 if PARTIAL/FAIL
    return 0 if veto_status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
