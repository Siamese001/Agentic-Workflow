#!/usr/bin/env python3
"""Gate W5.1 — waiver expiry gate.

Fails CI when any waiver in `config/wiring_gate_waivers.yaml` has a
`expires_on` date in the past. Prevents the waiver file from quietly
accumulating stale suppressions indefinitely.

Tier: B (blocking).

Validation rules per waiver entry:
    - Required fields: gate, scope, reason, owner, expires_on
    - expires_on must be YYYY-MM-DD and >= today (UTC)
    - reason non-empty; owner non-empty
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

WAIVER_FILE = REPO_ROOT / "config" / "wiring_gate_waivers.yaml"
REQUIRED_FIELDS = ("gate", "scope", "reason", "owner", "expires_on")


class WaiverExpiryGate(WiringGate):
    gate_id = "W5_waiver_expiry"
    tier = "B"

    def run(self, conn) -> list[Violation]:  # conn unused
        _ = conn
        if not WAIVER_FILE.exists():
            return []
        try:
            data = yaml.safe_load(WAIVER_FILE.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            return [
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=WAIVER_FILE.name,
                    rule="waiver_yaml_parse_error",
                    detail=str(exc),
                )
            ]

        waivers = data.get("waivers") or []
        if not isinstance(waivers, list):
            return [
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=WAIVER_FILE.name,
                    rule="waivers_key_must_be_list",
                    detail=f"top-level 'waivers:' must be a list, got {type(waivers).__name__}",
                )
            ]

        today = datetime.now(timezone.utc).date()
        violations: list[Violation] = []
        for idx, entry in enumerate(waivers):
            if not isinstance(entry, dict):
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"waivers[{idx}]",
                        rule="waiver_entry_not_mapping",
                        detail=f"entry must be a dict, got {type(entry).__name__}",
                    )
                )
                continue

            missing = [f for f in REQUIRED_FIELDS if not entry.get(f)]
            if missing:
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"waivers[{idx}]:{entry.get('gate', '?')}:{entry.get('scope', '?')}",
                        rule="waiver_missing_required_fields",
                        detail=f"missing fields: {missing}",
                    )
                )
                continue

            expires = str(entry["expires_on"])
            try:
                exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
            except ValueError:
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"{entry['gate']}:{entry['scope']}",
                        rule="waiver_invalid_expires_on_format",
                        detail=f"expires_on={expires!r} is not YYYY-MM-DD",
                    )
                )
                continue

            if exp_date < today:
                days_overdue = (today - exp_date).days
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"{entry['gate']}:{entry['scope']}",
                        rule="waiver_expired",
                        detail=(
                            f"expires_on={expires} is {days_overdue} day(s) ago; "
                            f"remove, renew (with fresh ADR/owner review), "
                            f"or fix the underlying violation"
                        ),
                        extra={
                            "gate": entry["gate"],
                            "scope": entry["scope"],
                            "owner": entry.get("owner"),
                            "days_overdue": days_overdue,
                        },
                    )
                )
        return violations


def main() -> int:
    return cli_exit(WaiverExpiryGate().execute())


if __name__ == "__main__":
    sys.exit(main())
