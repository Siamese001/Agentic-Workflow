"""MW_REAL (MANAGED_WORKFLOW_REAL_EXECUTION) integrated-runtime verifier.

Fail codes: MWR_WRONG_CHAIN_KIND, MWR_WRONG_ROUTE_FAMILY,
MWR_RECEIPT_MISSING, MWR_NOT_INTEGRATED, MWR_NOT_CERTIFIED (receipt
says managed_workflow_certified=False), MWR_WRONG_GATE_COUNT (must be
exactly 29), MWR_GATE_FAILURES (any gate verdict=FAIL),
MWR_MISSING_SUBSTRATE_REFS, MWR_HOW_TRACE_WRONG_KIND, MWR_FK_NOT_EMITTED,
MWR_COVERAGE_NOT_CERTIFIED.
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
    print(f"[verify_mw_real_execution_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "MANAGED_WORKFLOW_REAL_EXECUTION":
        return fail("MWR_WRONG_CHAIN_KIND", f"chain_kind={kind!r}; expected 'MANAGED_WORKFLOW_REAL_EXECUTION'")
    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "MANAGED_WORKFLOW_REAL_EXECUTION":
        return fail("MWR_WRONG_ROUTE_FAMILY", f"route_family={rc.get('route_family')!r}")

    mwr = _read_payload(art, "managed_workflow_real_execution_receipt.json")
    if not mwr:
        return fail("MWR_RECEIPT_MISSING", "managed_workflow_real_execution_receipt.json missing")
    if not mwr.get("integrated_runtime_origin"):
        return fail("MWR_NOT_INTEGRATED", "mwr.integrated_runtime_origin != True")
    if not mwr.get("managed_workflow_certified"):
        return fail(
            "MWR_NOT_CERTIFIED",
            f"managed_workflow_certified={mwr.get('managed_workflow_certified')}; expected True",
        )
    gates = mwr.get("gate_verdicts", [])
    if len(gates) != 29:
        return fail("MWR_WRONG_GATE_COUNT", f"gate count={len(gates)}; expected 29")
    failed = [g for g in gates if isinstance(g, dict) and g.get("verdict") != "PASS"]
    if failed:
        return fail(
            "MWR_GATE_FAILURES",
            f"{len(failed)} gates with non-PASS verdict: "
            f"{[g.get('gate_id') for g in failed[:5]]}",
        )
    substrates = mwr.get("composed_substrates", {})
    missing = []
    for key in ("r3_grounded_read", "r4_single_action", "uwg_commit"):
        if not isinstance(substrates.get(key), dict) or not substrates[key]:
            missing.append(key)
    if missing:
        return fail("MWR_MISSING_SUBSTRATE_REFS", f"composed_substrates missing: {missing}")

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "MANAGED_WORKFLOW_REAL_EXECUTION":
        return fail("MWR_HOW_TRACE_WRONG_KIND", f"how_trace.chain_kind={ht.get('chain_kind')!r}")

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail("MWR_FK_NOT_EMITTED", "fortknox_l7_evidence/ missing")

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    fams = cov.get("route_families", [])
    row = next((f for f in fams if isinstance(f, dict) and f.get("route_family") == "MANAGED_WORKFLOW_REAL_EXECUTION"), None)
    if not row or row.get("certification_status") != "CERTIFIED" or row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "MWR_COVERAGE_NOT_CERTIFIED",
            f"coverage MW_REAL row={row!r}; expected CERTIFIED/REAL_RUNTIME",
        )

    return passed(
        f"MANAGED_WORKFLOW_REAL_EXECUTION valid "
        f"(gates={len(gates)}/29 PASS, certified=True, coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
