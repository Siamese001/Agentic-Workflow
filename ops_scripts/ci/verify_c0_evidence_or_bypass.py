"""Spine verifier — C0 ran OR C0 was lawfully bypassed.

Asserts exactly one of these holds for the run:

    A) ``route_contract.grounding_required == True`` AND a
       ``final_evidence_contract.json`` exists.

    B) ``route_contract.grounding_required == False`` AND a
       ``c0_bypass_receipt.json`` exists with ``c0_required=False``
       and a permitted bypass reason.

The R1B terminal-shortcircuit path always lands on Branch B because the
cache reuses prior evidence rather than performing fresh retrieval.

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

from agentic_core.runtime.contracts.c0_bypass_receipt import (  # noqa: E402
    ALLOWED_C0_BYPASS_REASONS,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_c0_evidence_or_bypass] artifact_dir={art_dir}")

    try:
        rc = load_payload(art_dir, "route_contract.json")
    except FileNotFoundError as exc:
        return fail("ROUTE_CONTRACT_MISSING", str(exc))

    grounding_required = bool(rc.get("grounding_required", False))

    if grounding_required:
        # Branch A.
        fec_path = art_dir / "final_evidence_contract.json"
        if not fec_path.exists():
            return fail(
                "FINAL_EVIDENCE_CONTRACT_MISSING",
                "route_contract.grounding_required=True but "
                "final_evidence_contract.json is absent.",
            )
        return passed("grounding_required=True; FinalEvidenceContract present")

    # Branch B — bypass required.
    try:
        bypass = load_payload(art_dir, "c0_bypass_receipt.json")
    except FileNotFoundError as exc:
        return fail(
            "C0_BYPASS_RECEIPT_MISSING",
            f"grounding_required=False but c0_bypass_receipt.json "
            f"is absent: {exc}",
        )

    if bypass.get("grounding_required") is not False:
        return fail(
            "C0_BYPASS_GROUNDING_REQUIRED_TRUE",
            f"c0_bypass_receipt.grounding_required="
            f"{bypass.get('grounding_required')!r}; must be False",
        )
    if bypass.get("c0_required") is not False:
        return fail(
            "C0_BYPASS_C0_REQUIRED_TRUE",
            f"c0_bypass_receipt.c0_required={bypass.get('c0_required')!r}; "
            f"must be False",
        )
    reason = bypass.get("c0_bypass_reason", "")
    if reason not in ALLOWED_C0_BYPASS_REASONS:
        return fail(
            "C0_BYPASS_REASON_INVALID",
            f"c0_bypass_reason={reason!r} not in {sorted(ALLOWED_C0_BYPASS_REASONS)}",
        )

    return passed(f"C0 lawfully bypassed: reason={reason!r}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
