"""Validate the ADG audit repair handoff before burndown edits.

The burndown automation should call this first and stop on any non-zero exit.
It deliberately consumes only the digest-bound receipt, not latest files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.run_full_adg_audit import (  # noqa: E402
    RECEIPT_PATH,
    validate_repair_handoff_pointer,
    validate_repair_handoff_receipt,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--receipt", type=Path, default=RECEIPT_PATH)
    source.add_argument("--handoff-pointer", type=Path)
    parser.add_argument("--expected-adg-run-id")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of key=value lines.")
    args = parser.parse_args(argv)

    if args.handoff_pointer:
        receipt, counts, errors = validate_repair_handoff_pointer(
            args.handoff_pointer,
            expected_adg_run_id=args.expected_adg_run_id,
        )
        source_path = args.handoff_pointer
        source_key = "handoff_pointer"
    else:
        receipt, counts, errors = validate_repair_handoff_receipt(
            args.receipt,
            expected_adg_run_id=args.expected_adg_run_id,
        )
        source_path = args.receipt
        source_key = "receipt"
    payload = {
        "ok": not errors,
        source_key: str(source_path.resolve()),
        "artifact_status": receipt.get("artifact_status") if receipt else None,
        "adg_run_id": receipt.get("adg_run_id") if receipt else None,
        "counts": counts,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"ok={str(payload['ok']).lower()}")
        print(f"artifact_status={payload['artifact_status']}")
        print(f"adg_run_id={payload['adg_run_id']}")
        for key in (
            "P0_FIX",
            "P0_WAVE",
            "P0_TRACKED_BACKLOG",
            "P1_FIX",
            "P1_RATCHET_REGRESSION",
            "P1_RATCHET_FLOOR_BACKLOG",
        ):
            print(f"{key}={counts[key]}")
        for error in errors:
            print(f"error={error}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
