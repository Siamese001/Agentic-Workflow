"""UWG_BLOCK_PATH integrated-runtime verifier — fail-closed.

Asserts that the UWG_BLOCK_PATH chain at <artifact_dir> represents a real
integrated-runtime run that drove a blocked commit through
DurableWriteGateway.reject_direct_write — NOT just a fixture test.

Fail-closes if:

  UWGBLK_WRONG_CHAIN_KIND        — manifest.chain_kind != 'UWG_BLOCK_PATH'
  UWGBLK_WRONG_ROUTE_FAMILY      — route_contract.route_family != 'UWG_BLOCK_PATH'
  UWGBLK_RECEIPT_MISSING         — uwg_blocked_commit_receipt.json missing
  UWGBLK_NOT_INTEGRATED          — receipt.integrated_runtime_origin != True
                                   (i.e. fixture-only forgery attempt)
  UWGBLK_NO_BLOCK_REASON         — receipt.blocked_reason_codes empty
  UWGBLK_FAILED_RULE_MISSING     — receipt.failed_rule_ids does not include
                                   UWG_AUTHORITY_REQUIRED
  UWGBLK_AUTHORIZED_SURFACE      — attempting_surface looks UWG-authorized
                                   (Exit). Block path requires NON-UWG
                                   surface.
  UWGBLK_NO_COMMIT_REQUEST       — commit_request.json missing
  UWGBLK_HOW_TRACE_WRONG_KIND    — how_trace.chain_kind != 'UWG_BLOCK_PATH'
  UWGBLK_HOW_TRACE_L2_RAN        — HOW trace L2_EXECUTE RAN (block path
                                   may not perform real L2 execution)
  UWGBLK_FK_NOT_EMITTED          — fortknox_l7_evidence/ missing
  UWGBLK_MANIFEST_NO_RECEIPT_REF — manifest.uwg_blocked_commit_receipt_ref missing
  UWGBLK_SPINE_NO_BLOCK_REF      — spine.uwg_commit_or_block_ref missing
  UWGBLK_COVERAGE_NOT_CERTIFIED  — coverage doesn't mark UWG_BLOCK certified
  UWGBLK_FIXTURE_ONLY_OVERCLAIM  — coverage marks proof_class FIXTURE_ONLY
                                   but certification_status CERTIFIED

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


# Surfaces that may legitimately issue commits via UWG. Any of these
# attempting a "blocked" path means the block is not authority-driven.
_UWG_AUTHORIZED_SURFACES = {"Exit", "UWG"}


def main(argv: list[str]) -> int:
    art = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art)
    print(f"[verify_uwg_block_path_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "UWG_BLOCK_PATH":
        return fail(
            "UWGBLK_WRONG_CHAIN_KIND",
            f"manifest.chain_kind={kind!r}; expected 'UWG_BLOCK_PATH'",
        )

    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "UWG_BLOCK_PATH":
        return fail(
            "UWGBLK_WRONG_ROUTE_FAMILY",
            f"route_contract.route_family={rc.get('route_family')!r}; expected 'UWG_BLOCK_PATH'",
        )

    rcpt = _read_payload(art, "uwg_blocked_commit_receipt.json")
    if not rcpt:
        return fail(
            "UWGBLK_RECEIPT_MISSING",
            "uwg_blocked_commit_receipt.json missing or empty",
        )
    if not rcpt.get("integrated_runtime_origin"):
        return fail(
            "UWGBLK_NOT_INTEGRATED",
            "uwg_blocked_commit_receipt.integrated_runtime_origin != True — "
            "block path requires integrated runtime evidence, not fixture-only",
        )
    rcs = list(rcpt.get("blocked_reason_codes", []) or [])
    if not rcs:
        return fail(
            "UWGBLK_NO_BLOCK_REASON",
            "uwg_blocked_commit_receipt.blocked_reason_codes is empty",
        )
    rules = list(rcpt.get("failed_rule_ids", []) or [])
    if "UWG_AUTHORITY_REQUIRED" not in rules:
        return fail(
            "UWGBLK_FAILED_RULE_MISSING",
            f"failed_rule_ids={rules!r} missing UWG_AUTHORITY_REQUIRED",
        )
    attempting = str(rcpt.get("attempting_surface") or "")
    if attempting in _UWG_AUTHORIZED_SURFACES:
        return fail(
            "UWGBLK_AUTHORIZED_SURFACE",
            f"attempting_surface={attempting!r} is UWG-authorized; "
            f"block path requires non-UWG surface",
        )

    cr = _read_payload(art, "commit_request.json")
    if not cr:
        return fail(
            "UWGBLK_NO_COMMIT_REQUEST",
            "commit_request.json missing or empty",
        )

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "UWG_BLOCK_PATH":
        return fail(
            "UWGBLK_HOW_TRACE_WRONG_KIND",
            f"how_trace.chain_kind={ht.get('chain_kind')!r}; expected 'UWG_BLOCK_PATH'",
        )
    for stage in ht.get("stages", []) or []:
        if isinstance(stage, dict) and stage.get("stage_id") == "L2_EXECUTE":
            if stage.get("status") == "RAN":
                return fail(
                    "UWGBLK_HOW_TRACE_L2_RAN",
                    "UWG_BLOCK chain HOW trace claims L2_EXECUTE.status=RAN — "
                    "block path may not perform real L2 execution",
                )
            break

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail("UWGBLK_FK_NOT_EMITTED", f"fortknox_l7_evidence/ missing at {fk_dir}")

    manifest = _read_payload(art, "integrated_runtime_artifact_manifest.json")
    if not manifest.get("uwg_blocked_commit_receipt_ref"):
        return fail(
            "UWGBLK_MANIFEST_NO_RECEIPT_REF",
            "manifest.uwg_blocked_commit_receipt_ref missing",
        )
    spine = _read_payload(art, "agentic_core_spine_proof.json")
    if not spine.get("uwg_commit_or_block_ref"):
        return fail(
            "UWGBLK_SPINE_NO_BLOCK_REF",
            "spine_proof.uwg_commit_or_block_ref missing",
        )

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    families = cov.get("route_families", []) if isinstance(cov, dict) else []
    uwg_row = next(
        (
            f for f in families
            if isinstance(f, dict) and f.get("route_family") == "UWG_BLOCK_PATH"
        ),
        None,
    )
    if not uwg_row:
        return fail(
            "UWGBLK_COVERAGE_NOT_CERTIFIED",
            "coverage matrix has no UWG_BLOCK_PATH row",
        )
    if uwg_row.get("certification_status") != "CERTIFIED":
        return fail(
            "UWGBLK_COVERAGE_NOT_CERTIFIED",
            f"coverage UWG_BLOCK.certification_status="
            f"{uwg_row.get('certification_status')!r}; expected 'CERTIFIED'",
        )
    if uwg_row.get("proof_class") == "FIXTURE_ONLY":
        return fail(
            "UWGBLK_FIXTURE_ONLY_OVERCLAIM",
            "coverage marks UWG_BLOCK CERTIFIED with proof_class=FIXTURE_ONLY — "
            "integrated runtime evidence required for CERTIFIED status",
        )
    if uwg_row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "UWGBLK_COVERAGE_NOT_CERTIFIED",
            f"coverage UWG_BLOCK.proof_class={uwg_row.get('proof_class')!r}; "
            f"expected 'REAL_RUNTIME'",
        )

    return passed(
        f"UWG_BLOCK_PATH chain valid (attempting={attempting}, "
        f"integrated_runtime_origin=True, blocked_reason_codes={rcs}, "
        f"coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
