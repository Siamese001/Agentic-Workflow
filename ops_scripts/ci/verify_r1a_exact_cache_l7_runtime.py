"""R1A_EXACT_CACHE family verifier — fail-closed.

Runs against an R1A chain dir. Fail-closes if:

  R1A_WRONG_CHAIN_KIND        — manifest.chain_kind != 'R1A_EXACT_CACHE'
  R1A_WRONG_ROUTE_FAMILY      — route_contract.payload.route_family != 'R1A_EXACT_CACHE'
  R1A_NOT_EXACT_MATCH         — runtime_gate_verdict_bundle.d1_outcome != HIT
                                (R1A requires the D1 exact-cache gate to hit;
                                 D2 semantic similarity is NOT exact)
  R1A_NO_CACHE_HIT            — terminal_ret_packet missing cached_answer_ref
                                or reason_codes does not include 'd1_exact_hit'
  R1A_BORROWED_FROM_R1B       — coverage matrix marks R1A CERTIFIED but
                                runtime_entrypoint_ref is the R1B entrypoint
                                (i.e. matrix is overclaiming)
  R1A_HOW_TRACE_WRONG_KIND    — agentic_core_how_trace.payload.chain_kind != 'R1A_EXACT_CACHE'
  R1A_FK_NOT_EMITTED          — fortknox_l7_evidence/ directory missing
  R1A_COVERAGE_NOT_CERTIFIED  — coverage matrix does not mark R1A CERTIFIED/REAL_RUNTIME

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
    print(f"[verify_r1a_exact_cache_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "R1A_EXACT_CACHE":
        return fail(
            "R1A_WRONG_CHAIN_KIND",
            f"manifest.chain_kind={kind!r}; expected 'R1A_EXACT_CACHE'",
        )

    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "R1A_EXACT_CACHE":
        return fail(
            "R1A_WRONG_ROUTE_FAMILY",
            f"route_contract.route_family={rc.get('route_family')!r}; expected 'R1A_EXACT_CACHE'",
        )

    gvb = _read_payload(art, "runtime_gate_verdict_bundle.json")
    d1_outcome = str(gvb.get("d1_outcome") or "")
    reason_codes = list(gvb.get("reason_codes", []) or [])
    if d1_outcome != "HIT" or "d1_exact_hit" not in reason_codes:
        return fail(
            "R1A_NOT_EXACT_MATCH",
            f"runtime_gate_verdict_bundle.d1_outcome={d1_outcome!r}, "
            f"reason_codes={reason_codes!r}; R1A requires D1=HIT and "
            f"reason_codes containing 'd1_exact_hit'",
        )

    terminal = _read_payload(art, "terminal_ret_packet.json")
    cached_answer_ref = str(terminal.get("cached_answer_ref") or "")
    terminal_reasons = list(terminal.get("reason_codes", []) or [])
    if not cached_answer_ref or "d1_exact_hit" not in terminal_reasons:
        return fail(
            "R1A_NO_CACHE_HIT",
            f"terminal_ret_packet.cached_answer_ref={cached_answer_ref!r}, "
            f"reason_codes={terminal_reasons!r}; R1A requires non-empty "
            f"cached_answer_ref and reason_codes containing 'd1_exact_hit'",
        )

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "R1A_EXACT_CACHE":
        return fail(
            "R1A_HOW_TRACE_WRONG_KIND",
            f"how_trace.chain_kind={ht.get('chain_kind')!r}; expected 'R1A_EXACT_CACHE'",
        )

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail(
            "R1A_FK_NOT_EMITTED",
            f"fortknox_l7_evidence/ missing or empty at {fk_dir}",
        )

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    families = cov.get("route_families", []) if isinstance(cov, dict) else []
    r1a_row = None
    for f in families:
        if isinstance(f, dict) and f.get("route_family") == "R1A_EXACT_CACHE":
            r1a_row = f
            break
    if not r1a_row:
        return fail(
            "R1A_COVERAGE_NOT_CERTIFIED", "coverage matrix has no R1A_EXACT_CACHE row"
        )
    if r1a_row.get("certification_status") != "CERTIFIED":
        return fail(
            "R1A_COVERAGE_NOT_CERTIFIED",
            f"coverage R1A.certification_status={r1a_row.get('certification_status')!r}; "
            f"expected 'CERTIFIED'",
        )
    if r1a_row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "R1A_COVERAGE_NOT_CERTIFIED",
            f"coverage R1A.proof_class={r1a_row.get('proof_class')!r}; expected 'REAL_RUNTIME'",
        )
    ep_ref = str(r1a_row.get("runtime_entrypoint_ref") or "")
    if "integrated_safe_reuse_run" in ep_ref or "integrated_managed_workflow" in ep_ref:
        return fail(
            "R1A_BORROWED_FROM_R1B",
            f"R1A.runtime_entrypoint_ref={ep_ref!r} — R1A may not borrow R1B/MW entrypoint",
        )

    return passed(
        f"R1A_EXACT_CACHE chain valid (d1_outcome=HIT, "
        f"reason_codes={reason_codes}, cached_answer_ref set, "
        f"how_trace.chain_kind=R1A_EXACT_CACHE, coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
