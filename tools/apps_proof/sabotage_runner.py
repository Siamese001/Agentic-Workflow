"""W4 — Anti-cheat sabotage runner.

Mutates a known-passing proof run and re-verifies, asserting the verifier
catches each tamper with the exact ``fail_code`` from the user's spec.

CLI:

    python -m tools.apps_proof.sabotage_runner \
        --proof-dir artifacts/apps_proof/<app>/<run_id> \
        --out artifacts/apps_proof/sabotage_results.json

The 9 sabotage cases (T13–T21) cover every anti-cheat invariant:

    T13 — remove C0 evidence contract    → FAIL_MISSING_C0_CONTRACT
    T14 — remove an L2 span from trace   → FAIL_SPAN_COVERAGE_GAP
    T15 — mutate route_digest            → FAIL_TAMPERED_PROOF
    T16 — final output without Exit      → FAIL_OUTPUT_WITHOUT_EXIT
    T17 — L6 timestamp before boundary   → FAIL_L6_PRE_EXIT_MUTATION_RISK
    T18 — UWG bypass (durable, no recpt) → FAIL_UWG_BYPASS
    T19 — unsupported underwriting claim → FAIL_UNSUPPORTED_MATERIAL_CLAIM
    T20 — provider fallback no recert    → FAIL_UNCERTIFIED_PROVIDER_FALLBACK
    T21 — fake proof_verdict PASS        → FAIL_TAMPERED_PROOF

Each case (a) clones the proof dir, (b) applies the mutation, (c) runs the
verifier against the clone, (d) asserts the expected fail_code is in
``failed_checks``, (e) records SABOTAGE_OK / SABOTAGE_NOT_CAUGHT.

A SABOTAGE_NOT_CAUGHT result means the verifier has a detection gap —
this IS itself a constitutional failure of the harness.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.apps_proof.verify_app_proof import verify, write_verdict  # noqa: E402


@dataclass
class SabotageResult:
    """Outcome of one tamper test."""

    case_id: str
    description: str
    expected_fail_code: str
    caught: bool
    actual_fail_codes: list[str] = field(default_factory=list)
    proof_dir: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "expected_fail_code": self.expected_fail_code,
            "caught": self.caught,
            "actual_fail_codes": list(self.actual_fail_codes),
            "proof_dir": self.proof_dir,
        }


# ---------------------------------------------------------------------------
# Mutators — each takes a cloned proof dir and applies one tamper.
# ---------------------------------------------------------------------------


def _t13_remove_c0(d: Path) -> None:
    p = d / "contracts" / "c0_final_evidence_contract.json"
    if p.exists():
        p.unlink()


def _t14_remove_l2_span(d: Path) -> None:
    p = d / "trace" / "otel_trace.json"
    if not p.exists():
        return
    spans = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(spans, list):
        return
    spans = [s for s in spans if not (isinstance(s, dict) and s.get("layer") == "L2")]
    p.write_text(json.dumps(spans, indent=2, sort_keys=True), encoding="utf-8")


def _t15_mutate_route_digest(d: Path) -> None:
    p = d / "contracts" / "l0_route_contract.json"
    if not p.exists():
        return
    body = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(body, dict):
        # Mutate the wrapper-level route_id (an immutable identifier per run).
        body["route_id"] = "TAMPERED_ROUTE_ID"
        if isinstance(body.get("payload"), dict):
            body["payload"]["deterministic_route_digest"] = "TAMPERED_DIGEST"
    p.write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")


def _t16_remove_exit(d: Path) -> None:
    p = d / "contracts" / "exit_disposition.json"
    if p.exists():
        p.unlink()


def _t17_l6_pre_boundary(d: Path) -> None:
    """Inject an L6 span timestamped before runtime_boundary_ts."""
    trace = d / "trace" / "otel_trace.json"
    manifest = d / "run_manifest.json"
    if not trace.exists() or not manifest.exists():
        return
    spans = json.loads(trace.read_text(encoding="utf-8"))
    body = json.loads(manifest.read_text(encoding="utf-8"))
    boundary = body.get("runtime_boundary_ts") or "9999-12-31T23:59:59.000000Z"
    if not isinstance(spans, list):
        return
    spans.append({
        "trace_id": body.get("trace_id"),
        "span_id": "tampered_l6_pre",
        "parent_span_id": None,
        "layer": "L6",
        "name": "l6.tampered",
        "started_at": "2000-01-01T00:00:00.000000Z",  # before boundary
        "ended_at": "2000-01-01T00:00:01.000000Z",
        "status": "PASS",
        "run_id": body.get("run_id"),
        "request_id": body.get("request_id"),
        "app_id": body.get("app_name"),
        "scenario_id": body.get("scenario_id"),
        "contract_digest": None,
        "gate_id": None,
        "reason_codes": [],
        "latency_ms": None,
        "artifact_refs": [],
        "attrs": {"injected": "T17"},
    })
    trace.write_text(json.dumps(spans, indent=2, sort_keys=True), encoding="utf-8")


def _t18_uwg_bypass(d: Path) -> None:
    """Inject a durable artifact without a UWG receipt."""
    p = d / "contracts" / "uwg_commit_request.json"
    body = {
        "kind": "UWGCommitRequest",
        "run_id": "tampered_run",
        "trace_id": "tampered_trace",
        "request_id": "tampered_req",
        "policy_hash": "ph",
        "blueprint_hash": "bp",
        "replay_key": "rrk",
        "contract_digest": None,
        "payload": {"classification": "UWG_DURABLE", "durable": True, "tampered": True},
    }
    p.write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")
    receipt = d / "contracts" / "uwg_commit_receipt.json"
    if receipt.exists():
        receipt.unlink()


def _t19_unsupported_claim(d: Path) -> None:
    """Inject a key_risks claim entirely absent from evidence_register."""
    p = d / "contracts" / "decision_packet.json"
    if not p.exists():
        return
    body = json.loads(p.read_text(encoding="utf-8"))
    payload = body.get("payload", body)
    if isinstance(payload, dict):
        risks = list(payload.get("key_risks") or [])
        risks.append("xyzqqq fictional unverifiable allegation no support whatsoever zorblax")
        payload["key_risks"] = risks
    p.write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")


def _t20_provider_fallback(d: Path) -> None:
    """Inject provider_fallback into a contract without recertification."""
    p = d / "contracts" / "l2_sealed_artifact.json"
    if not p.exists():
        return
    body = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(body, dict):
        body.setdefault("payload", {})
        if isinstance(body["payload"], dict):
            body["payload"]["provider_fallback"] = "anthropic_fallback_provider_3rd_party"
    p.write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")


def _t21_fake_pass_verdict(d: Path) -> None:
    """Hand-edit run_manifest to break the proof_manifest_hash chain.

    Even though we then write a fake PASS verdict, the verifier recomputes
    the hash from on-disk content and catches the tamper as
    FAIL_TAMPERED_PROOF.
    """
    manifest_path = d / "run_manifest.json"
    if not manifest_path.exists():
        return
    body = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(body, dict):
        # Break a hashed field but DO NOT re-stamp proof_manifest_hash.
        body["app_name"] = "TAMPERED_APP"
    manifest_path.write_text(
        json.dumps(body, indent=2, sort_keys=True), encoding="utf-8"
    )
    # Also overwrite proof_verdict.json to claim PASS — the verifier
    # ignores it and rebuilds from sources.
    verdict_path = d / "verifier" / "proof_verdict.json"
    verdict_path.parent.mkdir(parents=True, exist_ok=True)
    verdict_path.write_text(
        json.dumps(
            {"final_status": "PASS", "tampered": True, "no_trace_links": True},
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


# Applicability predicates — ``applies_when(app, manifest, proof_dir) -> bool``.
# Cases that don't apply to a run are marked NOT_APPLICABLE rather than MISSED.


def _grounded(_app: str | None, manifest: dict, _pd: Path) -> bool:
    return bool(manifest.get("grounding_required", False))


def _has_sealed_with_dict_payload(_app: str | None, _m: dict, pd: Path) -> bool:
    """T20 needs a sealed artifact where ``payload`` is a dict the mutator
    can extend. Some non-grounded apps emit sealed artifacts with a
    non-dict payload (or none) — the mutator no-ops there."""
    p = pd / "contracts" / "l2_sealed_artifact.json"
    if not p.exists():
        return False
    try:
        body = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(body, dict):
        return False
    payload = body.get("payload")
    return isinstance(payload, dict)


def _has_sealed_and_exit(_app: str | None, _m: dict, pd: Path) -> bool:
    """T16 ('output without Exit') only applies when both sealed AND exit
    are present in a passing baseline — the mutator removes the exit."""
    sealed = pd / "contracts" / "l2_sealed_artifact.json"
    exit_d = pd / "contracts" / "exit_disposition.json"
    return sealed.exists() and exit_d.exists()


def _is_underwriting(app: str | None, _m: dict, _pd: Path) -> bool:
    return app == "apps_underwriting_ai"


# (case_id, description, expected_fail_code, mutator, applies_when_predicate)
SABOTAGE_CASES: list[
    tuple[str, str, str, Callable[[Path], None], Callable[[str | None, dict, Path], bool] | None]
] = [
    ("T13", "Remove C0 final evidence contract", "FAIL_MISSING_C0_CONTRACT", _t13_remove_c0, _grounded),
    ("T14", "Remove all L2 spans from OTEL trace", "FAIL_SPAN_COVERAGE_GAP", _t14_remove_l2_span, None),
    ("T15", "Mutate route_digest in l0_route_contract", "FAIL_TAMPERED_PROOF", _t15_mutate_route_digest, None),
    ("T16", "Final output (sealed) without ExitDisposition", "FAIL_OUTPUT_WITHOUT_EXIT", _t16_remove_exit, _has_sealed_and_exit),
    ("T17", "L6 span timestamped before runtime boundary", "FAIL_L6_PRE_EXIT_MUTATION_RISK", _t17_l6_pre_boundary, None),
    ("T18", "UWG durable artifact without commit receipt", "FAIL_UWG_BYPASS", _t18_uwg_bypass, None),
    ("T19", "Unsupported claim in decision_packet", "FAIL_UNSUPPORTED_MATERIAL_CLAIM", _t19_unsupported_claim, _is_underwriting),
    ("T20", "Provider fallback without recertification", "FAIL_UNCERTIFIED_PROVIDER_FALLBACK", _t20_provider_fallback, _has_sealed_with_dict_payload),
    ("T21", "Hand-edit manifest + fake PASS verdict", "FAIL_TAMPERED_PROOF", _t21_fake_pass_verdict, None),
]


def _clone_proof_dir(src: Path, dest_root: Path, case_id: str) -> Path:
    dest = dest_root / f"sabotage_{case_id}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest


def run_sabotage(proof_dir: Path) -> dict[str, Any]:
    """Run all 9 sabotage cases against a passing run dir.

    Cases with an ``applicable_apps`` filter are skipped (marked
    NOT_APPLICABLE) when the run's app is not in the filter set. NA cases
    do NOT count toward ``missed`` — they are tracked separately so the
    overall sabotage status is interpretable.
    """
    if not proof_dir.exists():
        raise FileNotFoundError(f"proof_dir missing: {proof_dir}")
    sabotage_root = proof_dir.parent / f"_sabotage_{proof_dir.name}"
    sabotage_root.mkdir(parents=True, exist_ok=True)

    # Resolve current run's app and manifest from run_manifest.json.
    current_app: str | None = None
    manifest: dict = {}
    manifest_path = proof_dir / "run_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(manifest, dict):
                current_app = manifest.get("app_name")
            else:
                manifest = {}
        except (OSError, json.JSONDecodeError):
            manifest = {}

    results: list[SabotageResult] = []
    not_applicable_count = 0
    for case_id, description, expected, mutator, applies_when in SABOTAGE_CASES:
        if applies_when is not None and not applies_when(current_app, manifest, proof_dir):
            results.append(
                SabotageResult(
                    case_id=case_id,
                    description=description + " [NOT_APPLICABLE]",
                    expected_fail_code=expected,
                    caught=True,  # NA counts as caught for summary purposes
                    actual_fail_codes=["NOT_APPLICABLE"],
                    proof_dir="",
                )
            )
            not_applicable_count += 1
            continue
        clone = _clone_proof_dir(proof_dir, sabotage_root, case_id)
        try:
            mutator(clone)
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            results.append(
                SabotageResult(
                    case_id=case_id,
                    description=description,
                    expected_fail_code=expected,
                    caught=False,
                    actual_fail_codes=[f"MUTATOR_ERROR:{exc}"],
                    proof_dir=str(clone),
                )
            )
            continue
        verdict = verify(clone)
        write_verdict(verdict, clone)
        actual_codes = [
            fc.get("fail_code") for fc in verdict.get("failed_checks", [])
            if fc.get("fail_code")
        ]
        caught = expected in actual_codes
        results.append(
            SabotageResult(
                case_id=case_id,
                description=description,
                expected_fail_code=expected,
                caught=caught,
                actual_fail_codes=[c for c in actual_codes if c],
                proof_dir=str(clone),
            )
        )

    summary = {
        "proof_dir": str(proof_dir),
        "current_app": current_app,
        "sabotage_root": str(sabotage_root),
        "total": len(results),
        "applicable": len(results) - not_applicable_count,
        "not_applicable": not_applicable_count,
        "caught": sum(
            1 for r in results
            if r.caught and "NOT_APPLICABLE" not in r.actual_fail_codes
        ),
        "missed": sum(1 for r in results if not r.caught),
        "results": [r.to_dict() for r in results],
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.apps_proof.sabotage_runner",
        description="W4 anti-cheat sabotage harness — proves verifier catches every tamper.",
    )
    parser.add_argument("--proof-dir", required=True, type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (default: <proof_dir>/verifier/sabotage_results.json)",
    )
    args = parser.parse_args(argv)
    out = args.out or (args.proof_dir / "verifier" / "sabotage_results.json")

    summary = run_sabotage(args.proof_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print(
        f"sabotage: {summary['caught']}/{summary['applicable']} caught "
        f"(applicable), {summary['not_applicable']} N/A, "
        f"{summary['missed']} missed"
    )
    for r in summary["results"]:
        if "NOT_APPLICABLE" in r["actual_fail_codes"]:
            marker = "N/A"
        elif r["caught"]:
            marker = "OK"
        else:
            marker = "MISSED"
        print(f"  [{marker}] {r['case_id']} {r['description']}")
        if marker == "MISSED":
            print(f"           expected={r['expected_fail_code']} got={r['actual_fail_codes']}")

    return 0 if summary["missed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
