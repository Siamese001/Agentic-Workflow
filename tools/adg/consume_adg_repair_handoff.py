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
    validate_repair_handoff_receipt,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=RECEIPT_PATH)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of key=value lines.")
    args = parser.parse_args(argv)

    receipt, counts, errors = validate_repair_handoff_receipt(args.receipt)
    payload = {
        "ok": not errors,
        "receipt": str(args.receipt.resolve()),
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
        for key in ("P0_FIX", "P1_FIX", "P1_RATCHET_REGRESSION", "P1_RATCHET_FLOOR_BACKLOG"):
            print(f"{key}={counts[key]}")
        for error in errors:
            print(f"error={error}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
