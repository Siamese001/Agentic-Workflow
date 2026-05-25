#!/usr/bin/env python3
"""Emit L0 v12 fan-in inventory JSON (plan l0-routing-v15-only-cutover W1.1)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_OUT = _REPO / "artifacts" / "governance" / "l0_v12_fanin_inventory.json"
_MODULES = (
    "v12_route_selector",
    "route_contract_v12_extensions",
    "route_contract_v15_bridge",
    "fallback_chains_loader",
)
_L0 = _REPO / "agentic_core" / "L0_routing"


def _grep_imports(module_stem: str) -> list[str]:
    hits: list[str] = []
    pat = re.compile(rf"\b{re.escape(module_stem)}\b")
    for py in _REPO.rglob("*.py"):
        if ".venv" in py.parts or "node_modules" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if pat.search(text):
            hits.append(py.relative_to(_REPO).as_posix())
    return sorted(set(hits))[:200]


def main() -> int:
    doc = {
        "schema_version": "l0_v12_fanin_inventory_v1",
        "snapshot_hint": "05212026_0548",
        "modules": {},
    }
    for stem in _MODULES:
        if stem == "v12_route_selector":
            path = _L0 / "_archive" / "v12" / "reasoning" / f"{stem}.py"
        elif stem == "fallback_chains_loader":
            path = _L0 / "_archive" / "v12" / "config" / f"{stem}.py"
        else:
            path = _L0 / f"{stem}.py"
        doc["modules"][stem] = {
            "path": path.relative_to(_REPO).as_posix() if path.is_file() else None,
            "exists": path.is_file(),
            "import_sites": _grep_imports(stem),
        }
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"OK wrote {_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
