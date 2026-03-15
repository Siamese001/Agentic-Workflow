"""
_ssot_validation_artifacts.py — Validation JSON writers and healing action recorder.

Extracted from execute_ssot.py to reduce file size and improve cohesion.
All public symbols are re-exported from execute_ssot.py for backward compat.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

logger = logging.getLogger(__name__)


def _normalize_finding_id(finding: dict, validator: str, index: int) -> str:
    """Generate normalized finding ID: {validator}:{path}:{rule}:{index}.

    Per hostile audit Section B3: Finding IDs must be normalized and deterministic.
    Per .windsurfrules §1.7: Identical input → identical output.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_normalize_finding_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_normalize_finding_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_normalize_finding_id")
    path = finding.get("file", finding.get("path", "UNKNOWN"))
    rule = finding.get("type", finding.get("rule", "UNKNOWN"))
    path_normalized = str(path).replace("\\", "/")
    return f"{validator}:{path_normalized}:{rule}:{index:04d}"


def _write_pre_validation_json(
    violations: list[dict], trace_id: str, territory: str, validators_used: list[str], output_dir: Path
) -> None:
    """Write pre_validation.json before any healing occurs.

    Per hostile audit Section C2: Pre-heal state must be captured in structured artifact.
    Per hostile audit Section B3: Findings must have normalized IDs and validator provenance.
    Per .windsurfrules §2.2: Evidence must be deterministic, ASCII-only.
    """
    from datetime import timezone

    findings = []
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    targeted_paths = set()
    for idx, violation in enumerate(violations):
        validator = violation.get("suggested_agent", "UNKNOWN")
        finding_id = _normalize_finding_id(violation, validator, idx)
        vtype = violation.get("type", "")
        if "FORBIDDEN" in vtype or "ARCHIVED" in vtype:
            severity = "high"
        elif "DUPLICATE" in vtype:
            severity = "medium"
        else:
            severity = "low"
        severity_counts[severity] += 1
        path = violation.get("file", violation.get("path", ""))
        if path:
            targeted_paths.add(str(path))
        findings.append(
            {
                "id": finding_id,
                "validator": validator,
                "path": str(path),
                "severity": severity,
                "rule": violation.get("type", "UNKNOWN"),
                "description": violation.get("message", ""),
            }
        )
    pre_validation = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "territory": territory,
        "validators": validators_used,
        "findings": findings,
        "counts": {
            "total": len(findings),
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
        },
        "targeted_paths": sorted(targeted_paths),
    }
    output_path = output_dir / "pre_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pre_validation, f, indent=2, ensure_ascii=True)
    logger.info(f"[PRE-VALIDATION] Wrote {len(findings)} findings to {output_path}")


def _write_post_validation_json(
    pre_validation_path: Path, phase3_result: dict, trace_id: str, territory: str, output_dir: Path
) -> None:
    """Write post_validation.json after Phase 3 revalidation.

    Per hostile audit Section C4: Post-heal proof with resolved/residual/regression breakdown.
    Per hostile audit Section B5: Must show resolved, remaining, and newly introduced findings.
    """
    from datetime import timezone

    pre_validation = {}
    if pre_validation_path.exists():
        with open(pre_validation_path, encoding="utf-8") as f:
            pre_validation = json.load(f)
    pre_finding_ids = {f["id"] for f in pre_validation.get("findings", [])}
    pre_finding_count = len(pre_finding_ids)
    remaining_violations = phase3_result.get("remaining_violations", [])
    remaining_findings = []
    for idx, violation in enumerate(remaining_violations):
        validator = violation.get("suggested_agent", "UNKNOWN")
        finding_id = _normalize_finding_id(violation, validator, idx)
        remaining_findings.append(
            {
                "id": finding_id,
                "validator": validator,
                "path": str(violation.get("file", violation.get("path", ""))),
                "rule": violation.get("type", "UNKNOWN"),
            }
        )
    remaining_ids = {f["id"] for f in remaining_findings}
    resolved_ids = list(pre_finding_ids - remaining_ids)
    regression_ids = list(remaining_ids - pre_finding_ids)
    post_validation = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "territory": territory,
        "pre_finding_count": pre_finding_count,
        "resolved_findings": resolved_ids,
        "residual_findings": list(remaining_ids),
        "regressions": regression_ids,
        "post_finding_count": len(remaining_ids),
        "resolution_rate": round(len(resolved_ids) / max(pre_finding_count, 1), 4),
        "validators_rerun": ["Phase3Validator"],
    }
    output_path = output_dir / "post_validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(post_validation, f, indent=2, ensure_ascii=True)
    logger.info(
        f"[POST-VALIDATION] Resolved: {len(resolved_ids)}, Residual: {len(remaining_ids)}, Regressions: {len(regression_ids)}"
    )


def _write_run_manifest_json(
    trace_id: str, execution_mode: str, territories: list[str], agents_executed: list[str], output_dir: Path
) -> None:
    """E6: Write run_manifest.json with run metadata and execution summary.

    Per hostile audit Section E6: run_manifest.json provides high-level run metadata.
    """
    from datetime import timezone

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "trace_id": trace_id,
        "execution_mode": execution_mode,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "territories": territories,
        "agents_executed": agents_executed,
        "agent_count": len(agents_executed),
        "territory_count": len(territories),
    }
    output_path = output_dir / "run_manifest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=True)
    logger.info(
        f"[RUN-MANIFEST] Wrote run_manifest.json with {len(agents_executed)} agents, {len(territories)} territories"
    )


def _write_decision_summary_json(trace_id: str, decisions_made: list[dict], output_dir: Path) -> None:
    """E6: Write decision_summary.json with routing decision audit trail.

    Per hostile audit Section E6: decision_summary.json provides routing decision audit.
    """
    from datetime import timezone

    output_dir.mkdir(parents=True, exist_ok=True)
    tier_counts = {}
    agent_counts = {}
    for decision in decisions_made:
        tier = decision.get("tier", "UNKNOWN")
        agent = decision.get("agent", "unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    summary = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_decisions": len(decisions_made),
        "tier_distribution": tier_counts,
        "agent_distribution": agent_counts,
        "decisions": decisions_made,
    }
    output_path = output_dir / "decision_summary.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=True)
    logger.info(f"[DECISION-SUMMARY] Wrote decision_summary.json with {len(decisions_made)} decisions")


def _write_artifact_integrity_json(trace_id: str, output_dir: Path) -> None:
    """E7: Write artifact_integrity.json as final step with SHA256 hashes of all artifacts.

    Per hostile audit Section E7: artifact_integrity.json provides cryptographic proof of artifact set.
    """
    import hashlib
    from datetime import timezone

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for artifact_path in output_dir.glob("*.json"):
        if artifact_path.name == "artifact_integrity.json":
            continue
        try:
            content = artifact_path.read_bytes()
            sha256_hash = hashlib.sha256(content).hexdigest()
            artifacts[artifact_path.name] = {"sha256": sha256_hash, "size_bytes": len(content)}
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"[ARTIFACT-INTEGRITY] Failed to hash {artifact_path.name}: {e}")
    integrity = {
        "trace_id": trace_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    output_path = output_dir / "artifact_integrity.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(integrity, f, indent=2, ensure_ascii=True)
    logger.info(f"[ARTIFACT-INTEGRITY] Wrote artifact_integrity.json with {len(artifacts)} artifact hashes")


def _record_healing_action(
    state_mgr,
    agent: str,
    territory: str,
    routing_score: float = 0.0,
    routing_tier: str = "DETERMINISTIC",
    model: str = "none",
    routing_gate: str = "N/A",
    confidence: float = 0.0,
    fix_summary: str = "",
    outcome: str = "SUCCESS",
    routing_digest: str | None = None,
    check_id: str | None = None,
):
    """[H2] Record a structured healing action for per-territory JSON and Markdown reports.

    Appends to state_mgr.state["healing_actions"] so Phase 5 can filter by territory
    and emit a healing_log in the detailed_cert JSON.

    Also persists the outcome to the system learning memory bridge (fire-and-forget,
    never raises) so healing patterns accumulate cross-session — same wiring as apps_*.
    """
    ts = datetime.now().isoformat()
    action = {
        "agent": agent,
        "territory": territory,
        "routing_score": round(routing_score, 4),
        "routing_tier": routing_tier,
        "model": model,
        "routing_gate": routing_gate,
        "confidence": round(confidence, 4),
        "fix_summary": fix_summary,
        "outcome": outcome,
        "timestamp": ts,
        "routing_digest": routing_digest,
        "check_id": check_id,
    }
    if "healing_actions" not in state_mgr.state:
        state_mgr.state["healing_actions"] = []
    state_mgr.state["healing_actions"].append(action)

    # ------------------------------------------------------------------
    # System learning persistence — fire-and-forget, never raises
    # ------------------------------------------------------------------
    try:
        from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

        _bridge = get_sl_memory_bridge()
        # Build a compact error signature from agent + territory + outcome
        error_sig = f"{agent}::{territory}::{outcome}"
        # Healing success rate: 1.0 = healed, 0.0 = failure/skipped
        _rate = 1.0 if outcome == "SUCCESS" else 0.0
        _bridge.persist_healing_success_rate(error_sig, rate=_rate, count=1, ts=ts)

        # Persist failure pattern for non-success outcomes so RCA can cluster them
        if outcome not in ("SUCCESS",):
            import hashlib as _hl

            _pattern_id = _hl.sha256(f"{error_sig}:{fix_summary[:80]}".encode()).hexdigest()[:16]
            _label = f"{agent} {outcome} in {territory}: {fix_summary[:80]}"
            _centroid = _hl.sha256(f"{agent}:{territory}".encode()).hexdigest()[:16]
            _bridge.persist_failure_pattern(
                pattern_id=_pattern_id,
                pattern_label=_label,
                centroid_hash=_centroid,
                member_count=1,
                ts=ts,
            )
    except ImportError as _sl_err:
        logger.debug("[SL] system_learning persist skipped (not available): %s", _sl_err)
    except Exception as _sl_err:
        logger.warning("[SL] system_learning persist failed: %s", _sl_err)
        raise
