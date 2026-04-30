"""Probe — R1B production threshold proof (W1 phase 2 blocker b).

Anti-cheat rules honored (user 2026-04-30):
  - Rule 1: NEVER silently lower the threshold. Runs with no
    ``SEMANTIC_CACHE_THRESHOLD_DYNAMIC`` override.
  - If a positive-pair run fails, emit ``CALIBRATION_GAP`` — not PASS, not
    silent threshold change.
  - ADR/calibration study path is documented but NOT activated in this pass.

SSOT for thresholds:
  agentic_core/L4_state/utils/memory/semantic_cache_manager.py:
    _TIER_THRESHOLD_DEFAULTS = {"static": 1.0, "dynamic": 0.95}
    _HYBRID_FUSED_THRESHOLD  = 0.88 (via SEMANTIC_CACHE_HYBRID_THRESHOLD env)

What this probe does:
  - Reads the production defaults from the SSOT module.
  - Records whether any override envs are currently set.
  - Records a DECLARED result for each tier: since we do not have a live
    BGE-M3 model in this probe (see probe_semantic_cache_model.py), we
    cannot compute real similarity scores without a model. In that
    scenario we emit ``CALIBRATION_GAP`` honestly.
  - When a model IS live and no override is present, the composer
    integrates with this probe's declared pairs.

Output: ``artifacts/certification/semantic_cache_threshold_proof.json``

Status ladder (probe output -> composer mapping):
  - ``PASS``             -> R1B_PRODUCTION_THRESHOLD_PROOF = PASS
  - ``CALIBRATION_GAP``  -> R1B_PRODUCTION_THRESHOLD_PROOF = CALIBRATION_GAP
  - ``OVERRIDE_PRESENT`` -> R1B_PRODUCTION_THRESHOLD_PROOF = BLOCKED
                           (threshold override without ADR is forbidden)
  - ``INFRASTRUCTURE_GAP`` -> R1B_PRODUCTION_THRESHOLD_PROOF = BLOCKED
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import write_evidence, rel  # noqa: E402

OVERRIDE_ENV_VARS = (
    "SEMANTIC_CACHE_THRESHOLD_DYNAMIC",
    "SEMANTIC_CACHE_THRESHOLD_STATIC",
    "SEMANTIC_CACHE_HYBRID_THRESHOLD",
)


def _read_ssot_defaults() -> dict:
    """Read the SSOT threshold constants from semantic_cache_manager."""
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            _TIER_THRESHOLD_DEFAULTS,
            _HYBRID_FUSED_THRESHOLD,
            tier_similarity_threshold,
        )
    except ImportError as exc:
        return {"error": f"SSOT_IMPORT_FAILED: {exc}"}
    return {
        "tier_defaults": dict(_TIER_THRESHOLD_DEFAULTS),
        "hybrid_fused_default_snapshot": _HYBRID_FUSED_THRESHOLD,
        "dynamic_resolved": tier_similarity_threshold("dynamic"),
        "static_resolved": tier_similarity_threshold("static"),
    }


def _active_overrides() -> dict[str, str | None]:
    return {v: os.environ.get(v) for v in OVERRIDE_ENV_VARS}


def _adr_artifact_present() -> dict:
    """Check whether an ADR-backed calibration artifact exists AND is approved.

    Per user 2026-04-30 W1p4 §6: the ADR being on disk is NOT sufficient to
    unblock an override. Only an APPROVED + APPLIED ADR authorizes a threshold
    override path. PROPOSED_NOT_APPLIED ADRs behave as if absent for this check.
    """
    adr_path = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
    result = {
        "adr_artifact_path": str(adr_path.relative_to(REPO_ROOT)),
        "adr_artifact_exists": adr_path.exists(),
        "adr_approved_and_applied": False,
        "adr_approval_status": None,
        "adr_implementation_status": None,
    }
    if adr_path.exists():
        try:
            import json
            d = json.loads(adr_path.read_text(encoding="utf-8"))
            result["adr_approval_status"] = d.get("owner_approval", {}).get("status")
            result["adr_implementation_status"] = d.get("implementation_status")
            applied = d.get("config_binding", {}).get("applied", False)
            result["adr_approved_and_applied"] = (
                result["adr_approval_status"] == "APPROVED"
                and result["adr_implementation_status"] == "APPLIED"
                and applied is True
            )
        except (json.JSONDecodeError, OSError):
            pass
    return result


def _read_calibration_results() -> dict:
    """W1p3: consume semantic_cache_calibration_results.json when present."""
    art = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_calibration_results.json"
    if not art.exists():
        return {"present": False, "overall_status": None, "aggregate": {}}
    try:
        import json
        d = json.loads(art.read_text(encoding="utf-8"))
        return {
            "present": True,
            "overall_status": d.get("overall_status"),
            "aggregate": d.get("aggregate", {}),
            "dataset_reference": d.get("dataset_reference", {}),
            "threshold_actual": d.get("threshold_actual"),
            "per_pair_count": len(d.get("per_pair_results", [])),
        }
    except (json.JSONDecodeError, OSError):
        return {"present": False, "overall_status": "MALFORMED", "aggregate": {}}


def _classify(ssot: dict, overrides: dict, adr: dict, calibration: dict) -> tuple[str, str]:
    if "error" in ssot:
        return ("INFRASTRUCTURE_GAP",
                f"threshold SSOT not importable: {ssot['error']}")

    # Any override env set without APPROVED+APPLIED ADR -> BLOCKED.
    # A PROPOSED_NOT_APPLIED ADR on disk does NOT authorize an override
    # (user 2026-04-30 W1p4 §6: only APPROVED+APPLIED ADRs permit threshold change).
    active_overrides = {k: v for k, v in overrides.items() if v is not None and v != ""}
    if active_overrides and not adr["adr_approved_and_applied"]:
        return ("OVERRIDE_PRESENT",
                f"threshold override(s) active without APPROVED+APPLIED ADR: "
                f"{active_overrides}. ADR status: "
                f"approval={adr.get('adr_approval_status')}, "
                f"implementation={adr.get('adr_implementation_status')}. "
                f"Rule 1 (user 2026-04-30) forbids silent lowering — only an "
                f"APPROVED+APPLIED ADR at {adr['adr_artifact_path']} authorizes override.")

    # W1p3: if calibration results present, bind their status
    if calibration["present"]:
        cal_status = calibration["overall_status"]
        agg = calibration["aggregate"]
        if cal_status == "PASS":
            return ("PASS",
                    f"calibration PASS at production threshold "
                    f"{calibration['threshold_actual']}: "
                    f"{agg.get('positive_pass_count')}/{agg.get('total_positives')} "
                    f"positives pass, {agg.get('negative_miss_count')}/"
                    f"{agg.get('total_negatives')} negatives miss, FP=0 FN=0.")
        if cal_status == "CALIBRATION_GAP":
            return ("CALIBRATION_GAP",
                    f"calibration results report CALIBRATION_GAP at "
                    f"threshold {calibration['threshold_actual']}: "
                    f"FP={agg.get('false_positive_count')} "
                    f"FN={agg.get('false_negative_count')}. "
                    f"Per Rule 1: threshold stays at SSOT default; no "
                    f"silent lowering. ADR-backed recalibration is the "
                    f"only sanctioned path.")
        if cal_status == "OVERRIDE_PRESENT":
            return ("OVERRIDE_PRESENT",
                    f"calibration probe detected threshold override — "
                    f"calibration results invalid. Clear override and re-run.")
        # INFRASTRUCTURE_GAP, DATASET_MISSING, MALFORMED
        return ("INFRASTRUCTURE_GAP",
                f"calibration probe returned status={cal_status}. "
                f"Infrastructure not operational; re-run after remediation.")

    # No calibration results -> legacy CALIBRATION_GAP (no measurement yet)
    return ("CALIBRATION_GAP",
            "no override env var active; production defaults (static=1.0, "
            "dynamic=0.95, hybrid_fused=0.88) are in force. Calibration "
            "evidence not yet collected (run probe_threshold_calibration.py). "
            "Per Rule 1, this emits CALIBRATION_GAP rather than silently "
            "claiming PASS or lowering the threshold.")


def main() -> int:
    ssot = _read_ssot_defaults()
    overrides = _active_overrides()
    adr = _adr_artifact_present()
    calibration = _read_calibration_results()
    status, rationale = _classify(ssot, overrides, adr, calibration)

    # W1p3: calibration evidence is now authoritative when present.
    declared_positive_pairs: list[dict] = []

    payload = {
        "probe": "semantic_cache_threshold_proof",
        "blocker": "b",
        "subclaim_target": "R1B_PRODUCTION_THRESHOLD_PROOF",
        "ssot_module": "agentic_core.L4_state.utils.memory.semantic_cache_manager",
        "production_threshold_defaults": ssot.get("tier_defaults"),
        "production_threshold_hybrid_fused_default": ssot.get("hybrid_fused_default_snapshot"),
        "threshold_resolved": {
            "dynamic": ssot.get("dynamic_resolved"),
            "static": ssot.get("static_resolved"),
        },
        "override_envs_observed": overrides,
        "override_active": any(v not in (None, "") for v in overrides.values()),
        "adr_calibration_artifact": adr,
        "calibration_evidence": calibration,
        "calibration_evidence_present": calibration["present"],
        "declared_positive_pairs": declared_positive_pairs,
        "all_positive_pairs_pass": False,  # nothing measured; honest
        "threshold_subclaim_status": status,
        "rationale": rationale,
        "anti_cheat_rules_honored": {
            "rule_1_no_silent_threshold_lowering": True,
            "probe_did_not_modify_threshold_env": True,
            "probe_did_not_create_adr": True,
            "probe_did_not_write_sidecar": True,
        },
    }

    path = write_evidence("semantic_cache_threshold_proof.json", payload)
    print(f"[probe_threshold] status={status}")
    print(f"[probe_threshold] tier_defaults={ssot.get('tier_defaults')}")
    print(f"[probe_threshold] override_active={payload['override_active']}")
    print(f"[probe_threshold] adr_exists={adr['adr_artifact_exists']}")
    print(f"[probe_threshold] wrote: {rel(path)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[probe_threshold] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
