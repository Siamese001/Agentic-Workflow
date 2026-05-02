"""R4_SINGLE_ACTION integrated-runtime verifier — fail-closed.

Fail codes: R4_WRONG_CHAIN_KIND, R4_WRONG_ROUTE_FAMILY, R4_SEALED_MISSING,
R4_NOT_INTEGRATED, R4_STRUCTURAL_ONLY_FORGERY (structural_only=True is
forbidden for R4), R4_NO_INVOCATIONS, R4_INVOCATION_NOT_DETERMINISTIC,
R4_AUTH_MISSING, R4_AUTH_DENIED, R4_AUTH_REGISTRY_UNBOUND,
R4_HOW_TRACE_WRONG_KIND, R4_FK_NOT_EMITTED, R4_MANIFEST_NO_SEALED_REF,
R4_SPINE_NO_SEALED_REF, R4_COVERAGE_NOT_CERTIFIED.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1]))

from _w2_verifier_common import detect_chain_kind, fail, passed, resolve_artifact_dir  # noqa: E402


def _read_payload(art: Path, fname: str) -> dict:
    p = art / fname
    if not p.exists():
        return {}
    try:
        env = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    payload = env.get("payload", {}) if isinstance(env, dict) else {}
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str]) -> int:
    art = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art)
    print(f"[verify_r4_single_action_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "R4_SINGLE_ACTION":
        return fail("R4_WRONG_CHAIN_KIND", f"chain_kind={kind!r}; expected 'R4_SINGLE_ACTION'")
    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "R4_SINGLE_ACTION":
        return fail("R4_WRONG_ROUTE_FAMILY", f"route_family={rc.get('route_family')!r}")

    sealed = _read_payload(art, "sealed_l2_artifact.json")
    if not sealed:
        return fail("R4_SEALED_MISSING", "sealed_l2_artifact.json missing or empty")
    if not sealed.get("integrated_runtime_origin"):
        return fail("R4_NOT_INTEGRATED", "sealed_l2.integrated_runtime_origin != True")
    if sealed.get("structural_only") is not False:
        return fail(
            "R4_STRUCTURAL_ONLY_FORGERY",
            f"sealed_l2.structural_only={sealed.get('structural_only')!r}; "
            f"R4 requires structural_only=False (real L2 execution)",
        )
    invs = sealed.get("tool_invocations", [])
    if not invs:
        return fail("R4_NO_INVOCATIONS", "sealed_l2.tool_invocations is empty")
    for inv in invs:
        if not isinstance(inv, dict) or inv.get("deterministic") is not True:
            return fail(
                "R4_INVOCATION_NOT_DETERMINISTIC",
                f"tool_invocation missing deterministic=True: {inv}",
            )

    auth = _read_payload(art, "tool_authorization_receipt.json")
    if not auth:
        return fail("R4_AUTH_MISSING", "tool_authorization_receipt.json missing")
    if auth.get("authorization_status") != "GRANTED":
        return fail(
            "R4_AUTH_DENIED",
            f"authorization_status={auth.get('authorization_status')!r}; expected 'GRANTED'",
        )
    if not auth.get("tool_registry_record_sha256"):
        return fail("R4_AUTH_REGISTRY_UNBOUND", "auth.tool_registry_record_sha256 missing")

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "R4_SINGLE_ACTION":
        return fail("R4_HOW_TRACE_WRONG_KIND", f"how_trace.chain_kind={ht.get('chain_kind')!r}")

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail("R4_FK_NOT_EMITTED", "fortknox_l7_evidence/ missing")

    manifest = _read_payload(art, "integrated_runtime_artifact_manifest.json")
    if not manifest.get("sealed_l2_artifact_ref"):
        return fail("R4_MANIFEST_NO_SEALED_REF", "manifest.sealed_l2_artifact_ref missing")
    spine = _read_payload(art, "agentic_core_spine_proof.json")
    if not spine.get("sealed_l2_artifact_sha256"):
        return fail("R4_SPINE_NO_SEALED_REF", "spine.sealed_l2_artifact_sha256 missing")

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    fams = cov.get("route_families", [])
    row = next((f for f in fams if isinstance(f, dict) and f.get("route_family") == "R4_SINGLE_ACTION"), None)
    if not row or row.get("certification_status") != "CERTIFIED" or row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "R4_COVERAGE_NOT_CERTIFIED",
            f"coverage R4 row={row!r}; expected CERTIFIED/REAL_RUNTIME",
        )

    return passed(
        f"R4_SINGLE_ACTION valid (tool_invocation_count={len(invs)}, "
        f"auth_status=GRANTED, structural_only=False, coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
