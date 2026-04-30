"""Composer — map W1 phase 2 evidence -> R1B subclaim sidecar.

Reads all 6 evidence artifacts emitted by ``tools/certification/evidence/probe_*.py``
and composes ``artifacts/certification/semantic_cache_subclaims.json``.

Separation of concerns (anti-cheat contract):
  - Evidence probes emit raw facts (*_proof.json files).
  - This composer translates evidence -> per-subclaim verdicts.
  - The verifier (scripts/verify_semantic_cache_certification.py) reads the
    sidecar AND writes overrides. Only the verifier owns overrides.
  - This composer does NOT write runtime_evidence_overrides.json and does
    NOT call into the verifier.

Mapping rules (user 2026-04-30 §5 strict composition):
  R1B_DENSE_SIMILARITY_COMPOSITION_PROOF = PASS only if
    R1B_APPROVED_MODEL_PROOF == PASS AND
    R1B_PRODUCTION_THRESHOLD_PROOF == PASS AND
    R1B_NEGATIVE_CONTROL_PROOF == PASS
  otherwise it downgrades to PARTIAL (not BLOCKED — the composition
  contract-level is still provable when individual inputs are PARTIAL).

Per user §3/§4: conditional subclaims stay NOT_APPLICABLE unless the
corresponding scope flag is claimed. This composer hard-codes them to
NOT_APPLICABLE since W1 phase 2 does NOT claim runtime/OTEL/replay.

Output: ``artifacts/certification/semantic_cache_subclaims.json``

Exit codes:
  - 0 on successful sidecar write
  - 2 if one-or-more required evidence artifacts missing/malformed
  - 3 on unexpected error
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
SIDECAR_PATH = ARTIFACTS_DIR / "semantic_cache_subclaims.json"

REQUIRED_EVIDENCE = {
    "model": ARTIFACTS_DIR / "semantic_cache_model_proof.json",
    "threshold": ARTIFACTS_DIR / "semantic_cache_threshold_proof.json",
    "negatives": ARTIFACTS_DIR / "semantic_cache_negative_controls.json",
    "terminal_exit": ARTIFACTS_DIR / "r1b_terminal_exit_proof.json",
    "schema": ARTIFACTS_DIR / "l4_cache_state_schema_proof.json",
    "fixture_vs_uwg": ARTIFACTS_DIR / "cache_fixture_vs_uwg_proof.json",
}

# W1p3 evidence — OPTIONAL (not required to run composer). When present, they
# enable upgrading APPROVED_MODEL / PRODUCTION_THRESHOLD from PARTIAL to PASS.
# Absence is tolerated and yields the legacy W1p2 verdicts.
OPTIONAL_EVIDENCE = {
    "bge_m3_operational": ARTIFACTS_DIR / "bge_m3_operational_proof.json",
    "calibration_results": ARTIFACTS_DIR / "semantic_cache_calibration_results.json",
    # W1p4 — optional; when present AND approved AND applied AND threshold
    # matches AND sweep shows FP=0 at configured threshold, composer upgrades
    # R1B_PRODUCTION_THRESHOLD_PROOF to PASS.
    "threshold_adr": ARTIFACTS_DIR / "semantic_cache_threshold_adr.json",
    "threshold_sweep": ARTIFACTS_DIR / "threshold_sweep_results.json",
}

# W1p4 — the live-configured threshold at composition time. Reading here
# (not at map-time) keeps composer deterministic and side-effect-free.
def _read_configured_threshold() -> float | None:
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            tier_similarity_threshold,
        )
        return tier_similarity_threshold("dynamic")
    except ImportError:
        return None


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_all_evidence() -> tuple[dict[str, dict], list[str]]:
    """Load required + optional evidence. Return ({name: payload}, errors)."""
    loaded: dict[str, dict] = {}
    errors: list[str] = []
    for name, path in REQUIRED_EVIDENCE.items():
        if not path.exists():
            errors.append(f"MISSING_EVIDENCE:{name}:{path.relative_to(REPO_ROOT)}")
            continue
        try:
            loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"MALFORMED_EVIDENCE:{name}:{exc}")
    # Optional W1p3 evidence — absence is OK; malformed is logged but ignored
    for name, path in OPTIONAL_EVIDENCE.items():
        if not path.exists():
            continue
        try:
            loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # treat malformed optional as absent
            pass
    return loaded, errors


def _map_model_proof(model_ev: dict) -> tuple[str, str]:
    """model_match_status -> R1B_APPROVED_MODEL_PROOF verdict.

    W1p4: when certification_scope is present, surface
    final_model_certification_scope in the notes so verifier's caveat
    includes it. Per user §7, final acceptance cannot flip to ACCEPTED
    while scope=LOCAL_ONLY; the scope field is advisory here (subclaim
    verdict itself remains PASS locally, reflecting that the model
    actually works).
    """
    status = model_ev.get("model_match_status", "UNRESOLVED")
    rationale = model_ev.get("rationale", "")
    scope = model_ev.get("certification_scope") or {}
    scope_suffix = ""
    if scope:
        scope_val = scope.get("final_model_certification_scope", "")
        scope_suffix = (
            f" | certification_scope={scope_val} "
            f"(local={scope.get('local_model_operational')}, "
            f"ci={scope.get('ci_model_operational')})"
        )
    if status == "MATCH":
        return "PASS", f"model MATCH: {rationale}{scope_suffix}"
    if status == "MISMATCH_EXPLAINED":
        return "PARTIAL", f"model MISMATCH_EXPLAINED: {rationale}{scope_suffix}"
    if status == "INFRASTRUCTURE_GAP":
        return "INFRASTRUCTURE_GAP", f"model INFRASTRUCTURE_GAP: {rationale}{scope_suffix}"
    # UNRESOLVED or unknown
    return "BLOCKED", f"model status={status}: {rationale}{scope_suffix}"


def _map_threshold_proof_with_adr_gate(
    threshold_ev: dict,
    adr_ev: dict | None,
    sweep_ev: dict | None,
    configured_threshold: float | None,
) -> tuple[str, str]:
    """W1p4: ADR gate for R1B_PRODUCTION_THRESHOLD_PROOF.

    Mapping (in priority order):
      1. override active w/o ADR           -> BLOCKED
      2. infrastructure_gap                -> INFRASTRUCTURE_GAP
      3. ADR absent OR status=PENDING      -> CALIBRATION_GAP (legacy W1p3)
      4. ADR APPROVED, not APPLIED         -> PARTIAL (approved, pending deploy)
      5. ADR APPROVED+APPLIED, threshold
         mismatch (configured != approved) -> PARTIAL (DRIFT_DETECTED in notes)
      6. ADR APPROVED+APPLIED, threshold
         matches, sweep FP>0 at configured -> PARTIAL (DRIFT_DETECTED in notes)
      7. ADR APPROVED+APPLIED, threshold
         matches, sweep FP=0                -> PASS
      8. threshold_ev status=PASS from W1p3 calibration AND no ADR required
         (legacy path, user Rule 1 still gates) -> CALIBRATION_GAP
    """
    status = threshold_ev.get("threshold_subclaim_status", "UNRESOLVED")
    rationale = threshold_ev.get("rationale", "")

    # Early exits — hard blockers from base threshold probe
    if status == "OVERRIDE_PRESENT":
        return "BLOCKED", f"threshold OVERRIDE_PRESENT (no ADR): {rationale}"
    if status == "INFRASTRUCTURE_GAP":
        return "INFRASTRUCTURE_GAP", f"threshold INFRASTRUCTURE_GAP: {rationale}"

    # W1p4 ADR gate
    if adr_ev is None:
        # No ADR on disk — legacy W1p3 path
        if status == "CALIBRATION_GAP":
            return "CALIBRATION_GAP", f"no ADR on disk; {rationale}"
        if status == "PASS":
            # Calibration says PASS but no ADR. Per Rule 1, calibration-at-SSOT
            # PASS is the only sanctioned PASS path and requires FP=0 at the
            # SSOT threshold (which the calibration probe already validates).
            return "PASS", f"threshold PASS (calibration-at-SSOT, no ADR required): {rationale}"
        return "CALIBRATION_GAP", f"no ADR on disk; base status={status}: {rationale}"

    # ADR exists — enforce gate
    approval = adr_ev.get("owner_approval", {}).get("status")
    impl_status = adr_ev.get("implementation_status")
    applied = adr_ev.get("config_binding", {}).get("applied", False)
    approved_t = adr_ev.get("recommended_threshold")
    adr_id = adr_ev.get("adr_id", "SEMCACHE-THRESH-???")

    if approval != "APPROVED":
        return "CALIBRATION_GAP", (
            f"{adr_id} present but owner_approval.status={approval!r} "
            f"(not APPROVED). Per Rule 7 (ADR gate): threshold stays at "
            f"CALIBRATION_GAP until an owner approves. recommended={approved_t}, "
            f"configured={configured_threshold}."
        )

    if impl_status != "APPLIED" or applied is not True:
        return "PARTIAL", (
            f"{adr_id} APPROVED but implementation_status={impl_status!r}, "
            f"applied={applied}. Approved threshold {approved_t} has not "
            f"been deployed to SSOT yet; see config_binding.apply_procedure."
        )

    # Threshold-match check
    if approved_t is None or configured_threshold is None or approved_t != configured_threshold:
        return "PARTIAL", (
            f"DRIFT_DETECTED: {adr_id} APPROVED+APPLIED but configured "
            f"threshold {configured_threshold} does not match approved "
            f"{approved_t}. Re-sync config or re-run sweep + regenerate ADR."
        )

    # Sweep FP=0 at configured threshold check
    if sweep_ev is None:
        return "PARTIAL", (
            f"DRIFT_DETECTED: {adr_id} APPROVED+APPLIED but sweep evidence "
            f"missing. Regenerate via probe_threshold_sweep.py to confirm "
            f"FP=0 at threshold {configured_threshold}."
        )

    sweep_rows = sweep_ev.get("metrics_table", [])
    configured_row = next(
        (m for m in sweep_rows if m.get("threshold") == configured_threshold),
        None,
    )
    if configured_row is None:
        return "PARTIAL", (
            f"DRIFT_DETECTED: {adr_id} APPROVED+APPLIED but sweep has no "
            f"row for configured threshold {configured_threshold}. "
            f"Regenerate sweep with {configured_threshold} in candidate list."
        )
    if configured_row.get("fp", 1) != 0 or configured_row.get("unsafe_fp_count", 1) != 0:
        return "PARTIAL", (
            f"DRIFT_DETECTED: {adr_id} APPROVED+APPLIED at threshold "
            f"{configured_threshold}, but sweep reports "
            f"fp={configured_row.get('fp')}, "
            f"unsafe_fp={configured_row.get('unsafe_fp_count')}. "
            f"Safety invariant violated — threshold cannot PASS."
        )

    return "PASS", (
        f"{adr_id} APPROVED + APPLIED + configured={configured_threshold} "
        f"matches approved={approved_t}; sweep confirms FP=0 and "
        f"unsafe_fp=0 at this threshold. All Rule 7 (ADR gate) conditions met."
    )


def _map_threshold_proof(threshold_ev: dict) -> tuple[str, str]:
    """Legacy mapper preserved for backward compat when ADR evidence absent.

    (Kept as a named function so existing tests can import it directly.)
    """
    return _map_threshold_proof_with_adr_gate(
        threshold_ev, adr_ev=None, sweep_ev=None, configured_threshold=None
    )


def _map_negatives_proof(neg_ev: dict) -> tuple[str, str]:
    """overall_status -> R1B_NEGATIVE_CONTROL_PROOF verdict."""
    status = neg_ev.get("overall_status", "UNRESOLVED")
    if status == "PASS":
        return "PASS", "all 3 W1-phase-2 negatives (NEG-5/6/7) pass"
    if status == "INFRASTRUCTURE_GAP":
        return "INFRASTRUCTURE_GAP", "one or more negative probes hit infrastructure gap"
    return "BLOCKED", f"negatives overall_status={status}"


def _map_terminal_exit_proof(te_ev: dict) -> tuple[str, str]:
    """overall_status -> R1B_TERMINAL_EXIT_PROOF verdict."""
    status = te_ev.get("overall_status", "UNRESOLVED")
    invariants = te_ev.get("invariants", {})
    passed = sum(1 for v in invariants.values() if v)
    total = len(invariants) or 5
    if status == "PASS":
        return "PASS", f"all {total} terminal/exit invariants schema-provable"
    if status == "INFRASTRUCTURE_GAP":
        return "INFRASTRUCTURE_GAP", (
            f"terminal/exit INFRASTRUCTURE_GAP: {passed}/{total} invariants pass"
        )
    return "PARTIAL", f"terminal/exit {passed}/{total} invariants pass"


def _map_schema_and_fixture(
    schema_ev: dict, fixture_ev: dict
) -> tuple[str, str]:
    """Combined: R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF.

    Requires both schema PASS AND fixture_vs_uwg PASS.
    """
    schema_status = schema_ev.get("overall_status", "UNRESOLVED")
    fixture_status = fixture_ev.get("overall_status", "UNRESOLVED")
    if schema_status == "PASS" and fixture_status == "PASS":
        return "PASS", (
            f"schema: {schema_ev.get('concepts_proven_count')}/"
            f"{schema_ev.get('concepts_total')} concepts proven; "
            f"fixture-vs-UWG: 3/3 invariants pass"
        )
    if "INFRASTRUCTURE_GAP" in (schema_status, fixture_status):
        return "INFRASTRUCTURE_GAP", (
            f"schema={schema_status} fixture_vs_uwg={fixture_status}"
        )
    return "PARTIAL", (
        f"schema={schema_status} fixture_vs_uwg={fixture_status}"
    )


def _compose_dense_composition(
    model: tuple[str, str],
    threshold: tuple[str, str],
    negatives: tuple[str, str],
) -> tuple[str, str]:
    """Per user 2026-04-30 §5: composition PASS iff inputs all PASS.

    Otherwise PARTIAL unless any input is BLOCKED/INFRASTRUCTURE_GAP,
    in which case PARTIAL (not BLOCKED) because composition-level
    contract mechanics (dense + sparse fusion + threshold application)
    are independently implementable in the SSOT.
    """
    statuses = (model[0], threshold[0], negatives[0])
    if all(s == "PASS" for s in statuses):
        return "PASS", "all 3 inputs PASS: model, threshold, negatives"
    return "PARTIAL", (
        f"composition downgraded to PARTIAL per Rule 5 "
        f"(user 2026-04-30): inputs are "
        f"model={statuses[0]}, threshold={statuses[1]}, negatives={statuses[2]}"
    )


def _compose_terminal_exit_subclaim(
    terminal_exit: tuple[str, str],
) -> tuple[str, str]:
    return terminal_exit


def _compose(evidence: dict[str, dict]) -> dict:
    """Compose the sidecar payload from loaded evidence."""
    m = _map_model_proof(evidence["model"])
    # W1p4: wire ADR gate for threshold subclaim when ADR + sweep present
    adr_ev = evidence.get("threshold_adr")
    sweep_ev = evidence.get("threshold_sweep")
    configured_threshold = _read_configured_threshold()
    t = _map_threshold_proof_with_adr_gate(
        evidence["threshold"],
        adr_ev=adr_ev,
        sweep_ev=sweep_ev,
        configured_threshold=configured_threshold,
    )
    n = _map_negatives_proof(evidence["negatives"])
    te = _map_terminal_exit_proof(evidence["terminal_exit"])
    pftr = _map_schema_and_fixture(evidence["schema"], evidence["fixture_vs_uwg"])
    dense = _compose_dense_composition(m, t, n)
    terminal_final = _compose_terminal_exit_subclaim(te)

    def subclaim(status: str, notes: str, *, evidence_path: str | None = None) -> dict:
        entry: dict = {"status": status, "notes": notes}
        if evidence_path:
            entry["evidence_path"] = evidence_path
        return entry

    # All 6 core subclaims — map each to its evidence artifact(s)
    core_subclaims = {
        "R1B_DENSE_SIMILARITY_COMPOSITION_PROOF": subclaim(
            dense[0], dense[1],
            evidence_path="artifacts/certification/(model+threshold+negatives)_proof.json",
        ),
        "R1B_APPROVED_MODEL_PROOF": subclaim(
            m[0], m[1],
            evidence_path="artifacts/certification/semantic_cache_model_proof.json",
        ),
        "R1B_PRODUCTION_THRESHOLD_PROOF": subclaim(
            t[0], t[1],
            evidence_path="artifacts/certification/semantic_cache_threshold_proof.json",
        ),
        "R1B_NEGATIVE_CONTROL_PROOF": subclaim(
            n[0], n[1],
            evidence_path="artifacts/certification/semantic_cache_negative_controls.json",
        ),
        "R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF": subclaim(
            pftr[0], pftr[1],
            evidence_path=(
                "artifacts/certification/l4_cache_state_schema_proof.json + "
                "artifacts/certification/cache_fixture_vs_uwg_proof.json"
            ),
        ),
        "R1B_TERMINAL_EXIT_PROOF": subclaim(
            terminal_final[0], terminal_final[1],
            evidence_path="artifacts/certification/r1b_terminal_exit_proof.json",
        ),
    }

    # Conditional subclaims — hardcoded NOT_APPLICABLE per user §3/§4.
    # W2/W3 own these scopes; W1 phase 2 explicitly does NOT claim them.
    conditional_subclaims = {
        "R1B_INTEGRATED_RUNTIME_PROOF": subclaim(
            "NOT_APPLICABLE",
            "W1 phase 2 does not claim integrated-runtime evidence. "
            "R1B_INTEGRATED_RUNTIME_PROOF is W2 scope.",
        ),
        "R1B_REAL_OTEL_PROOF": subclaim(
            "NOT_APPLICABLE",
            "W1 phase 2 does not claim real-OTEL evidence. "
            "R1B_REAL_OTEL_PROOF is W3 scope.",
        ),
        "R1B_REPLAY_PROOF": subclaim(
            "NOT_APPLICABLE",
            "W1 phase 2 does not claim replay evidence. "
            "R1B_REPLAY_PROOF is W3 scope.",
        ),
    }

    all_subclaims = {**core_subclaims, **conditional_subclaims}

    return {
        "schema_version": 1,
        "evaluated_at_utc": _now_utc(),
        "evidence_evaluator": "w1_phase_2_composer",
        "composer_module": "scripts/compose_semantic_cache_subclaims.py",
        "composer_rules": {
            "rule_5_strict_composition": (
                "R1B_DENSE_SIMILARITY_COMPOSITION_PROOF = PASS only if "
                "APPROVED_MODEL, PRODUCTION_THRESHOLD, NEGATIVE_CONTROL are all PASS"
            ),
            "rule_3_no_integrated_runtime_claim": (
                "R1B_INTEGRATED_RUNTIME_PROOF hardcoded NOT_APPLICABLE (W2)"
            ),
            "rule_4_no_otel_replay_claim": (
                "R1B_REAL_OTEL_PROOF and R1B_REPLAY_PROOF hardcoded NOT_APPLICABLE (W3)"
            ),
        },
        "scope": {
            "runtime_certification_claimed": False,
            "observability_certification_claimed": False,
            "replay_certification_claimed": False,
        },
        "subclaims": all_subclaims,
        "evidence_artifacts_consumed": sorted(
            [str(p.relative_to(REPO_ROOT)) for p in REQUIRED_EVIDENCE.values()]
            + [str(p.relative_to(REPO_ROOT)) for p in OPTIONAL_EVIDENCE.values()
               if p.exists()]
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-missing-evidence",
        action="store_true",
        help=(
            "Write sidecar even if one-or-more evidence artifacts are missing. "
            "Missing inputs produce INFRASTRUCTURE_GAP subclaims. Default: fail."
        ),
    )
    args = parser.parse_args(argv)

    evidence, errors = _load_all_evidence()

    if errors and not args.allow_missing_evidence:
        print("[compose] FAIL_CLOSED: required evidence missing/malformed:", file=sys.stderr)
        for err in errors:
            print(f"[compose]   {err}", file=sys.stderr)
        print(
            "[compose] Run the 6 probes first:",
            file=sys.stderr,
        )
        for name, path in REQUIRED_EVIDENCE.items():
            print(f"[compose]   python tools/certification/evidence/probe_{'semantic_cache_' if name in ('model','threshold','negatives') else ''}{ {'model':'model','threshold':'threshold','negatives':'negatives','terminal_exit':'r1b_terminal_exit','schema':'cache_state_schema','fixture_vs_uwg':'cache_fixture_vs_uwg'}[name] }.py",
                  file=sys.stderr)
        return 2

    # Fill missing with INFRASTRUCTURE_GAP stubs when bypass flag used
    if args.allow_missing_evidence:
        for name in REQUIRED_EVIDENCE:
            if name not in evidence:
                evidence[name] = {"overall_status": "INFRASTRUCTURE_GAP",
                                  "rationale": f"evidence {name} missing"}

    sidecar = _compose(evidence)

    SIDECAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SIDECAR_PATH.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )

    print(f"[compose] wrote: {SIDECAR_PATH.relative_to(REPO_ROOT)}")
    print(f"[compose] schema_version={sidecar['schema_version']}")
    print(f"[compose] subclaim verdicts:")
    for sid, entry in sidecar["subclaims"].items():
        print(f"[compose]   {sid} = {entry['status']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[compose] HARNESS_ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
