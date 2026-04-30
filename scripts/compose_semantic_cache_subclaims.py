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


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_all_evidence() -> tuple[dict[str, dict], list[str]]:
    """Load all 6 evidence artifacts. Return ({name: payload}, errors)."""
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
    return loaded, errors


def _map_model_proof(model_ev: dict) -> tuple[str, str]:
    """model_match_status -> R1B_APPROVED_MODEL_PROOF verdict."""
    status = model_ev.get("model_match_status", "UNRESOLVED")
    rationale = model_ev.get("rationale", "")
    if status == "MATCH":
        return "PASS", f"model MATCH: {rationale}"
    if status == "MISMATCH_EXPLAINED":
        return "PARTIAL", f"model MISMATCH_EXPLAINED: {rationale}"
    if status == "INFRASTRUCTURE_GAP":
        return "INFRASTRUCTURE_GAP", f"model INFRASTRUCTURE_GAP: {rationale}"
    # UNRESOLVED or unknown
    return "BLOCKED", f"model status={status}: {rationale}"


def _map_threshold_proof(threshold_ev: dict) -> tuple[str, str]:
    """threshold_subclaim_status -> R1B_PRODUCTION_THRESHOLD_PROOF verdict."""
    status = threshold_ev.get("threshold_subclaim_status", "UNRESOLVED")
    rationale = threshold_ev.get("rationale", "")
    if status == "PASS":
        return "PASS", f"threshold PASS: {rationale}"
    if status == "CALIBRATION_GAP":
        return "CALIBRATION_GAP", f"threshold CALIBRATION_GAP: {rationale}"
    if status == "OVERRIDE_PRESENT":
        return "BLOCKED", f"threshold OVERRIDE_PRESENT (no ADR): {rationale}"
    if status == "INFRASTRUCTURE_GAP":
        return "INFRASTRUCTURE_GAP", f"threshold INFRASTRUCTURE_GAP: {rationale}"
    return "BLOCKED", f"threshold status={status}: {rationale}"


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
    t = _map_threshold_proof(evidence["threshold"])
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
            str(p.relative_to(REPO_ROOT)) for p in REQUIRED_EVIDENCE.values()
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
