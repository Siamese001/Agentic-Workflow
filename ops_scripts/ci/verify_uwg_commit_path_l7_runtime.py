"""UWG_COMMIT_PATH integrated-runtime verifier — fail-closed.

Asserts that the UWG_COMMIT_PATH chain at <artifact_dir> represents a
real integrated-runtime run that drove a SUCCESSFUL commit through
DurableWriteGateway.commit() from the Exit surface.

Fail-closes if:
  UWGCMT_WRONG_CHAIN_KIND        — chain_kind != UWG_COMMIT_PATH
  UWGCMT_WRONG_ROUTE_FAMILY      — route_contract.route_family != UWG_COMMIT_PATH
  UWGCMT_RECEIPT_MISSING         — uwg_commit_receipt.json missing
  UWGCMT_NOT_INTEGRATED          — receipt.integrated_runtime_origin != True
  UWGCMT_NOT_COMMITTED           — receipt.commit_status != COMMITTED
  UWGCMT_NO_SNAPSHOT             — snapshot_before == snapshot_after (no state change)
  UWGCMT_NO_AUDIT_APPEND         — audit_append_receipt_ref missing
  UWGCMT_NO_COMMIT_REQUEST       — commit_request.json missing
  UWGCMT_WRONG_SOURCE_SURFACE    — commit_request.source_surface != Exit
  UWGCMT_FK_NOT_EMITTED          — fortknox_l7_evidence/ missing
  UWGCMT_MANIFEST_NO_RECEIPT_REF — manifest.uwg_commit_receipt_ref missing
  UWGCMT_SPINE_NO_COMMIT_REF     — spine.uwg_commit_or_block_ref missing
  UWGCMT_COVERAGE_NOT_CERTIFIED  — coverage doesn't mark UWG_COMMIT CERTIFIED

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
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
    print(f"[verify_uwg_commit_path_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "UWG_COMMIT_PATH":
        return fail("UWGCMT_WRONG_CHAIN_KIND", f"chain_kind={kind!r}; expected 'UWG_COMMIT_PATH'")

    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "UWG_COMMIT_PATH":
        return fail(
            "UWGCMT_WRONG_ROUTE_FAMILY",
            f"route_contract.route_family={rc.get('route_family')!r}; expected 'UWG_COMMIT_PATH'",
        )

    rcpt = _read_payload(art, "uwg_commit_receipt.json")
    if not rcpt:
        return fail("UWGCMT_RECEIPT_MISSING", "uwg_commit_receipt.json missing or empty")
    if not rcpt.get("integrated_runtime_origin"):
        return fail("UWGCMT_NOT_INTEGRATED", "uwg_commit_receipt.integrated_runtime_origin != True")
    if rcpt.get("commit_status") != "COMMITTED":
        return fail(
            "UWGCMT_NOT_COMMITTED",
            f"uwg_commit_receipt.commit_status={rcpt.get('commit_status')!r}; expected 'COMMITTED'",
        )
    sb = rcpt.get("snapshot_before", "")
    sa = rcpt.get("snapshot_after", "")
    if not sb or not sa or sb == sa:
        return fail(
            "UWGCMT_NO_SNAPSHOT",
            f"snapshot_before={sb!r}, snapshot_after={sa!r}; must differ",
        )
    if not rcpt.get("audit_append_receipt_ref"):
        return fail("UWGCMT_NO_AUDIT_APPEND", "audit_append_receipt_ref missing")

    cr = _read_payload(art, "commit_request.json")
    if not cr:
        return fail("UWGCMT_NO_COMMIT_REQUEST", "commit_request.json missing or empty")
    if cr.get("source_surface") != "Exit":
        return fail(
            "UWGCMT_WRONG_SOURCE_SURFACE",
            f"commit_request.source_surface={cr.get('source_surface')!r}; expected 'Exit'",
        )

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "UWG_COMMIT_PATH":
        return fail(
            "UWGCMT_HOW_TRACE_WRONG_KIND",
            f"how_trace.chain_kind={ht.get('chain_kind')!r}; expected 'UWG_COMMIT_PATH'",
        )

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail("UWGCMT_FK_NOT_EMITTED", f"fortknox_l7_evidence/ missing at {fk_dir}")

    manifest = _read_payload(art, "integrated_runtime_artifact_manifest.json")
    if not manifest.get("uwg_commit_receipt_ref"):
        return fail("UWGCMT_MANIFEST_NO_RECEIPT_REF", "manifest.uwg_commit_receipt_ref missing")
    spine = _read_payload(art, "agentic_core_spine_proof.json")
    if not spine.get("uwg_commit_or_block_ref"):
        return fail("UWGCMT_SPINE_NO_COMMIT_REF", "spine.uwg_commit_or_block_ref missing")

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    fams = cov.get("route_families", []) if isinstance(cov, dict) else []
    row = next((f for f in fams if isinstance(f, dict) and f.get("route_family") == "UWG_COMMIT_PATH"), None)
    if not row or row.get("certification_status") != "CERTIFIED" or row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "UWGCMT_COVERAGE_NOT_CERTIFIED",
            f"coverage UWG_COMMIT_PATH row={row!r}; expected CERTIFIED/REAL_RUNTIME",
        )

    return passed(
        f"UWG_COMMIT_PATH valid (commit_status=COMMITTED, snapshot {sb}->{sa}, "
        f"source_surface=Exit, coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
