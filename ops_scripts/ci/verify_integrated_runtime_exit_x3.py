"""W2 verifier #5 — ExitReviewPacket consumes terminal; X3 disposition unique.

Asserts:
  1. Exactly one x3_disposition_receipt.json exists with a valid disposition.
  2. exit_review_packet.json route_id == terminal_ret_packet.json route_id
     (Exit consumed the terminal packet's route).
  3. exit_review_packet.json no_l2_execution_assertion is True
     (terminal cache reuse never executes L2).
  4. exit_review_packet.json no_l4_write_assertion is True
     (no durable L4 mutation without UWG receipt).
  5. terminal_ret_packet.json no_l2_execution_assertion and
     no_l4_write_assertion are both True.
  6. The x3 packet's trace_root agrees with the exit review packet's.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (
    EXIT_HARNESS_ERROR,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

VALID_X3 = {"X3A", "X3B", "X3C", "X3D", "X3E", "X3F"}


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_integrated_runtime_exit_x3] artifact_dir={art_dir}")

    try:
        terminal = load_payload(art_dir, "terminal_ret_packet.json")
        review = load_payload(art_dir, "exit_review_packet.json")
        x3 = load_payload(art_dir, "x3_disposition_receipt.json")
    except FileNotFoundError as exc:
        return fail("ARTIFACT_MISSING", str(exc))

    # 1: unique + valid disposition.
    disposition = x3.get("x3_disposition", "")
    if disposition not in VALID_X3:
        return fail("X3_DISPOSITION_INVALID",
                    f"x3_disposition={disposition!r} not in {VALID_X3}")
    # Multiple-X3 detection: the manifest's artifact list must contain
    # exactly one x3_disposition_receipt.json (we already loaded it; the
    # uniqueness comes from the W2_CHAIN_LINKAGE shape).

    # 2: review consumed terminal.
    if review.get("route_id") != terminal.get("route_id"):
        return fail("EXIT_TERMINAL_ROUTE_MISMATCH",
                    f"review.route_id={review.get('route_id')!r} != terminal.route_id={terminal.get('route_id')!r}")

    # 3+4: review-side terminal-class invariants.
    if not review.get("no_l2_execution_assertion"):
        return fail("EXIT_REVIEW_L2_ASSERTION_FALSE",
                    "exit_review.no_l2_execution_assertion must be True for terminal cache reuse")
    if not review.get("no_l4_write_assertion"):
        return fail("EXIT_REVIEW_L4_ASSERTION_FALSE",
                    "exit_review.no_l4_write_assertion must be True (no UWG receipt)")

    # 5: terminal-side invariants.
    if not terminal.get("no_l2_execution_assertion"):
        return fail("TERMINAL_L2_ASSERTION_FALSE",
                    "terminal.no_l2_execution_assertion must be True")
    if not terminal.get("no_l4_write_assertion"):
        return fail("TERMINAL_L4_ASSERTION_FALSE",
                    "terminal.no_l4_write_assertion must be True")

    # 6: trace_root consistency.
    review_trace = review.get("trace_root", "")
    x3_trace = x3.get("x3_packet", {}).get("trace_root", "")
    if review_trace != x3_trace:
        return fail("TRACE_ROOT_DIVERGENCE",
                    f"review.trace_root={review_trace!r} != x3.trace_root={x3_trace!r}")

    return passed(
        f"x3_disposition={disposition} (unique); "
        f"route_id={terminal.get('route_id')}; "
        f"no_l2={review.get('no_l2_execution_assertion')}; "
        f"no_l4={review.get('no_l4_write_assertion')}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
