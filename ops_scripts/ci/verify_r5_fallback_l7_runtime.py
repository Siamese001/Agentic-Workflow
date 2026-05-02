"""R5_FALLBACK family verifier — fail-closed.

Runs against an R5 chain dir. Fail-closes if:

  R5_WRONG_CHAIN_KIND          — manifest.chain_kind != 'R5_FALLBACK'
  R5_WRONG_ROUTE_FAMILY        — route_contract.route_family != 'R5_FALLBACK'
  R5_NO_FALLBACK_DECISION      — safe_fallback_decision.json missing
  R5_FALLBACK_REASON_EMPTY     — safe_fallback_decision.fallback_reason empty
  R5_UNSAFE_EXECUTION_CLAIMED  — safe_fallback_decision asserts unsafe
                                 execution did not occur, but contradicts
                                 chain artifacts
  R5_BAD_X3_DISPOSITION        — actual_x3_disposition not in {X3D (ALLOW),
                                 X3E (SAFE_ABSTAIN)} — V6Disposition.value uses
                                 the X3 packet code, not the enum name
  R5_HOW_TRACE_L2_RAN          — HOW trace L2_EXECUTE.status == RAN (R5 cannot
                                 perform real L2 execution)
  R5_HOW_TRACE_WRONG_KIND      — how_trace.chain_kind != 'R5_FALLBACK'
  R5_FK_NOT_EMITTED            — fortknox_l7_evidence/ missing
  R5_MANIFEST_NO_FALLBACK_REF  — manifest.safe_fallback_decision_ref missing
  R5_SPINE_NO_FALLBACK_REF     — spine.safe_fallback_decision_ref missing
  R5_COVERAGE_NOT_CERTIFIED    — coverage matrix doesn't certify R5
  R5_BORROWED_FROM_R1B         — R5 entrypoint_ref looks like R1B/MW

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1]))

from _w2_verifier_common import (  # noqa: E402
    detect_chain_kind,
    fail,
    passed,
    resolve_artifact_dir,
)


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
    print(f"[verify_r5_fallback_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "R5_FALLBACK":
        return fail(
            "R5_WRONG_CHAIN_KIND",
            f"manifest.chain_kind={kind!r}; expected 'R5_FALLBACK'",
        )

    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "R5_FALLBACK":
        return fail(
            "R5_WRONG_ROUTE_FAMILY",
            f"route_contract.route_family={rc.get('route_family')!r}; expected 'R5_FALLBACK'",
        )

    sf = _read_payload(art, "safe_fallback_decision.json")
    if not sf:
        return fail(
            "R5_NO_FALLBACK_DECISION",
            "safe_fallback_decision.json missing or empty",
        )
    if not str(sf.get("fallback_reason") or "").strip():
        return fail(
            "R5_FALLBACK_REASON_EMPTY",
            "safe_fallback_decision.fallback_reason is empty",
        )
    for assertion in (
        "no_unsafe_execution",
        "no_real_l2_execution",
        "no_real_tool_call",
        "no_real_model_call",
        "no_l4_write_attempted",
    ):
        if not sf.get(assertion):
            return fail(
                "R5_UNSAFE_EXECUTION_CLAIMED",
                f"safe_fallback_decision.{assertion}={sf.get(assertion)!r}; "
                f"R5 fallback path requires all no-execution assertions True",
            )
    # V6Disposition.value uses X3-packet codes: X3D=ALLOW, X3E=SAFE_ABSTAIN.
    actual_x3 = str(sf.get("actual_x3_disposition") or "")
    if actual_x3 not in ("X3D", "X3E"):
        return fail(
            "R5_BAD_X3_DISPOSITION",
            f"actual_x3_disposition={actual_x3!r}; expected X3D (ALLOW) or X3E (SAFE_ABSTAIN)",
        )

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "R5_FALLBACK":
        return fail(
            "R5_HOW_TRACE_WRONG_KIND",
            f"how_trace.chain_kind={ht.get('chain_kind')!r}; expected 'R5_FALLBACK'",
        )
    for stage in ht.get("stages", []) or []:
        if isinstance(stage, dict) and stage.get("stage_id") == "L2_EXECUTE":
            if stage.get("status") == "RAN":
                return fail(
                    "R5_HOW_TRACE_L2_RAN",
                    "R5 chain HOW trace claims L2_EXECUTE.status=RAN — "
                    "fallback may not perform real L2 execution",
                )
            break

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail("R5_FK_NOT_EMITTED", f"fortknox_l7_evidence/ missing at {fk_dir}")

    manifest = _read_payload(art, "integrated_runtime_artifact_manifest.json")
    if not manifest.get("safe_fallback_decision_ref"):
        return fail(
            "R5_MANIFEST_NO_FALLBACK_REF",
            "manifest.safe_fallback_decision_ref missing",
        )
    spine = _read_payload(art, "agentic_core_spine_proof.json")
    if not spine.get("safe_fallback_decision_ref"):
        return fail(
            "R5_SPINE_NO_FALLBACK_REF",
            "spine_proof.safe_fallback_decision_ref missing",
        )

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    families = cov.get("route_families", []) if isinstance(cov, dict) else []
    r5_row = next(
        (f for f in families if isinstance(f, dict) and f.get("route_family") == "R5_FALLBACK"),
        None,
    )
    if not r5_row:
        return fail("R5_COVERAGE_NOT_CERTIFIED", "coverage matrix has no R5_FALLBACK row")
    if r5_row.get("certification_status") != "CERTIFIED" or r5_row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "R5_COVERAGE_NOT_CERTIFIED",
            f"coverage R5.status={r5_row.get('certification_status')!r} "
            f"proof={r5_row.get('proof_class')!r}; expected CERTIFIED/REAL_RUNTIME",
        )
    ep_ref = str(r5_row.get("runtime_entrypoint_ref") or "")
    if "integrated_safe_reuse_run" in ep_ref or "integrated_managed_workflow" in ep_ref:
        return fail(
            "R5_BORROWED_FROM_R1B",
            f"R5.runtime_entrypoint_ref={ep_ref!r} — R5 may not borrow R1B/MW entrypoint",
        )

    return passed(
        f"R5_FALLBACK chain valid (x3={actual_x3}, fallback_reason set, "
        f"no unsafe execution, coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
