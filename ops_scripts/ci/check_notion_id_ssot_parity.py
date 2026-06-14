#!/usr/bin/env python3
"""NP-IDSSOT — Notion-ID SSOT parity gate.

Guards the consolidation in plan ``notion-id-ssot-consolidation``: the single
source of truth for Notion database/data-source IDs is
``config/notion_databases.yaml``; ``.claude/governance/scripts/_notion_constants.py``
*derives* its constants from that YAML and keeps the literals only as a fail-soft
fallback.

This gate asserts the three views can never silently diverge:

  1. YAML SSOT  ==  ``_notion_constants`` derived module constants
  2. YAML SSOT  ==  ``_notion_constants._FALLBACK_*`` literals (so the fail-soft
     fallback can't drift from the SSOT it shadows)
  3. ``WAVE_PHASE_*`` deprecated aliases  ==  Backlog Items canonical constants

Fail-closed by default (exit 1 on any mismatch) — a divergence here is a real
correctness bug, not advisory drift. Bypass: ``NOTION_ID_SSOT_PARITY_BYPASS=1``.

Usage:
    python ops_scripts/ci/check_notion_id_ssot_parity.py [--json]

Exit codes:
    0 = all three views agree (or bypassed)
    1 = at least one mismatch
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_GOV_SCRIPTS = REPO_ROOT / ".claude" / "governance" / "scripts"
_YAML_PATH = REPO_ROOT / "config" / "notion_databases.yaml"

# YAML row key -> (database_id attr, data_source_id attr) on _notion_constants.
KEY_TO_ATTRS: dict[str, tuple[str, str]] = {
    "backlog_items": ("BACKLOG_ITEMS_DB_ID", "BACKLOG_ITEMS_DATA_SOURCE_ID"),
    "plans": ("PLANS_DB_ID", "PLANS_DATA_SOURCE_ID"),
    "adr_registry": ("ADR_REGISTRY_DB_ID", "ADR_REGISTRY_DS_ID"),
    "author_gate_ledger": ("AUTHOR_GATE_LEDGER_DB_ID", "AUTHOR_GATE_LEDGER_DS_ID"),
    "sc_ap_violation_backlog": ("SCAP_BACKLOG_DB_ID", "SCAP_BACKLOG_DS_ID"),
    "mcp_registry": ("MCP_REGISTRY_DB_ID", "MCP_REGISTRY_DS_ID"),
    "antipattern_burndown": ("AP_BURNDOWN_DB_ID", "AP_BURNDOWN_DS_ID"),
}


def _load_yaml() -> dict[str, object]:
    import yaml

    return yaml.safe_load(_YAML_PATH.read_text(encoding="utf-8"))


def _import_constants():
    if str(_GOV_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_GOV_SCRIPTS))
    import _notion_constants  # type: ignore[import-not-found]

    return _notion_constants


def check() -> list[str]:
    """Return a list of mismatch messages (empty == parity holds)."""
    problems: list[str] = []

    if not _YAML_PATH.is_file():
        return [f"SSOT YAML missing: {_YAML_PATH}"]

    raw = _load_yaml()
    if not isinstance(raw, dict):
        return [f"SSOT YAML did not parse to a mapping: {_YAML_PATH}"]

    n = _import_constants()

    # --- 1 + 2: API surface (derived + fallback) vs YAML ---
    api = raw.get("api") or {}
    api_expect = {
        "NOTION_API_VERSION": str(api.get("version")),
        "NOTION_BASE": str(api.get("base")),
        "NOTION_HTTP_TIMEOUT_S": float(api.get("http_timeout_s")),
    }
    for attr, want in api_expect.items():
        got = getattr(n, attr, None)
        if got != want:
            problems.append(f"derived {attr}={got!r} != YAML {want!r}")
    fb_api = {
        "_FALLBACK_NOTION_API_VERSION": str(api.get("version")),
        "_FALLBACK_NOTION_BASE": str(api.get("base")),
        "_FALLBACK_NOTION_HTTP_TIMEOUT_S": float(api.get("http_timeout_s")),
    }
    for attr, want in fb_api.items():
        got = getattr(n, attr, None)
        if got != want:
            problems.append(f"fallback {attr}={got!r} != YAML {want!r}")

    # --- 1 + 2: per-database IDs (derived + fallback) vs YAML ---
    rows = {r["key"]: r for r in (raw.get("databases") or []) if isinstance(r, dict) and r.get("key")}
    fb_db = getattr(n, "_FALLBACK_DB", {})
    for key, (db_attr, ds_attr) in KEY_TO_ATTRS.items():
        row = rows.get(key)
        if row is None:
            problems.append(f"YAML missing database key '{key}'")
            continue
        want_db = str(row.get("database_id"))
        want_ds = str(row.get("id"))
        if getattr(n, db_attr, None) != want_db:
            problems.append(f"derived {db_attr}={getattr(n, db_attr, None)!r} != YAML database_id {want_db!r}")
        if getattr(n, ds_attr, None) != want_ds:
            problems.append(f"derived {ds_attr}={getattr(n, ds_attr, None)!r} != YAML id {want_ds!r}")
        if fb_db.get(key) != (want_db, want_ds):
            problems.append(f"_FALLBACK_DB[{key!r}]={fb_db.get(key)!r} != YAML ({want_db!r}, {want_ds!r})")

    # --- 3: WAVE_PHASE_* aliases must equal Backlog Items canonical ---
    if getattr(n, "WAVE_PHASE_DB_ID", None) != getattr(n, "BACKLOG_ITEMS_DB_ID", object()):
        problems.append("WAVE_PHASE_DB_ID alias != BACKLOG_ITEMS_DB_ID")
    if getattr(n, "WAVE_PHASE_DATA_SOURCE_ID", None) != getattr(n, "BACKLOG_ITEMS_DATA_SOURCE_ID", object()):
        problems.append("WAVE_PHASE_DATA_SOURCE_ID alias != BACKLOG_ITEMS_DATA_SOURCE_ID")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Notion-ID SSOT parity gate")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    args = parser.parse_args(argv)

    if os.getenv("NOTION_ID_SSOT_PARITY_BYPASS") == "1":
        msg = "NP-IDSSOT bypassed (NOTION_ID_SSOT_PARITY_BYPASS=1)"
        print(json.dumps({"status": "bypassed"}) if args.json else f"WARNING: {msg}")
        return 0

    problems = check()
    if args.json:
        print(json.dumps({"status": "ok" if not problems else "fail", "problems": problems}, indent=2))
    elif problems:
        print("NP-IDSSOT FAIL — Notion-ID SSOT parity violations:")
        for p in problems:
            print(f"  - {p}")
        print(
            "\nFix: edit config/notion_databases.yaml (SSOT) and keep the matching "
            "_FALLBACK_* literal in .claude/governance/scripts/_notion_constants.py in sync."
        )
    else:
        print("NP-IDSSOT OK — YAML SSOT == derived constants == fallback literals.")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
