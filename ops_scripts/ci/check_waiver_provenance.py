#!/usr/bin/env python3
"""Gate W6_WAIVER_PROVENANCE — every wiring-CI waiver must cite a real ADR or plan.

Extends `W5_waiver_expiry` (which only checks expiration dates) with a
provenance rule:

    Every entry in config/wiring_gate_waivers.yaml MUST include one of:
      * adr:  docs/architecture/adr/ADR-NNN-*.md      (file must exist)
      * plan: .cursor/plans/<slug>-<6hex>.md        (file must exist)

And must always include:
      * gate, scope, reason, owner, expires_on (pre-existing required fields)

Rationale
    Ungrounded waivers are how debt freezes in amber. Requiring a pointer
    to either an architectural decision record OR an explicit plan means:
      * Every waiver can be audited.
      * Waivers survive ownership churn.
      * The `reason` field stops being a one-line escape hatch.

Tier
    B (blocking). Any malformed or unreferenced waiver fails CI immediately.
    There's no baseline — this gate must converge to zero violations.
"""

from __future__ import annotations

import fnmatch
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)
from agentic_core.L0_routing.config.path_constants import (
    ADR_DIR,
    WINDSURF_PLANS_DIR,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


GATE_ID = "W6_waiver_provenance"
WAIVER_FILE = REPO_ROOT / "config" / "wiring_gate_waivers.yaml"

REQUIRED_FIELDS = ("gate", "scope", "reason", "owner", "expires_on")
PROVENANCE_KEYS = ("adr", "plan")

ADR_GLOB = f"{ADR_DIR}/ADR-*.md"
PLAN_GLOB = f"{WINDSURF_PLANS_DIR}/*-*.md"


def _load_waivers(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or yaml is None:
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    if not isinstance(data, dict):
        return []
    entries = data.get("waivers", []) or []
    return [e for e in entries if isinstance(e, dict)]


def _provenance_path_exists(value: str, glob_pattern: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    # Accept either a direct path or a filename that fnmatches the glob.
    p = REPO_ROOT / value
    if p.exists():
        return True
    # Also permit bare basename match (e.g. "ADR-023.md" or the slug only).
    base = (REPO_ROOT / glob_pattern).parent
    if base.exists():
        for candidate in base.glob("*"):
            if candidate.name == value or fnmatch.fnmatch(candidate.name, f"*{value}*"):
                return True
    return False


def validate_entry(entry: dict[str, Any], *, now: datetime | None = None) -> list[str]:
    """Return list of reasons an entry is invalid; empty list means ok."""
    now = now or datetime.now(timezone.utc)
    problems: list[str] = []
    for field in REQUIRED_FIELDS:
        value = entry.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            problems.append(f"missing required field: {field}")
    # Provenance — at least one of adr/plan, file must exist.
    prov = {k: entry.get(k) for k in PROVENANCE_KEYS if entry.get(k)}
    if not prov:
        problems.append("missing provenance — must cite one of: " + ", ".join(PROVENANCE_KEYS))
    else:
        if "adr" in prov and not _provenance_path_exists(str(prov["adr"]), ADR_GLOB):
            problems.append(f"adr provenance {prov['adr']!r} does not match any file in {ADR_GLOB}")
        if "plan" in prov and not _provenance_path_exists(str(prov["plan"]), PLAN_GLOB):
            problems.append(f"plan provenance {prov['plan']!r} does not match any file in {PLAN_GLOB}")
    # expires_on parseable
    exp = entry.get("expires_on")
    if isinstance(exp, str):
        try:
            datetime.strptime(exp, "%Y-%m-%d")
        except ValueError:
            problems.append(f"expires_on not YYYY-MM-DD: {exp!r}")
    return problems


class WaiverProvenanceGate(WiringGate):
    gate_id = GATE_ID
    tier = "B"
    baseline_filename = None

    def run(self, conn) -> list[Violation]:  # noqa: ARG002
        entries = _load_waivers(WAIVER_FILE)
        violations: list[Violation] = []
        for idx, entry in enumerate(entries):
            problems = validate_entry(entry)
            if not problems:
                continue
            subject = f"{entry.get('gate', '?')}::{entry.get('scope', '?')}"
            violations.append(
                Violation(
                    gate_id=GATE_ID,
                    tier="B",
                    subject=subject,
                    rule="waiver_missing_provenance_or_invalid",
                    detail="; ".join(problems),
                    extra={"index": idx, "entry": entry},
                )
            )
        return violations


def main() -> int:
    result = WaiverProvenanceGate().execute()
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
