"""Advisory/fail-closed check that L6 gravity exceptions YAML exists and matches inventory."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
YAML = REPO_ROOT / "config" / "architectural_exceptions.yaml"
INV = REPO_ROOT / "docs" / "reports" / "cursor" / "l6_w6_gravity_edge_inventory_fresh.json"


def main() -> int:
    if os.environ.get("L6_ARCH_EXCEPTIONS_BYPASS") == "1":
        print("[l6_arch_exceptions] BYPASS")
        return 0

    fail_closed = os.environ.get("L6_ARCH_EXCEPTIONS_FAIL_CLOSED") == "1"
    if not YAML.is_file():
        print(f"[l6_arch_exceptions] missing {YAML.relative_to(REPO_ROOT)}")
        return 2 if fail_closed else 0

    text = YAML.read_text(encoding="utf-8")
    if "l6_downstream_exceptions:" not in text:
        print("[l6_arch_exceptions] missing l6_downstream_exceptions section")
        return 2 if fail_closed else 0

    if INV.is_file():
        inv = json.loads(INV.read_text(encoding="utf-8"))
        inv_pairs = set()
        for src, tgts in inv.get("by_source", {}).items():
            seen: set[str] = set()
            for t in tgts:
                if t["target"] in seen:
                    continue
                seen.add(t["target"])
                inv_pairs.add((src, t["target"]))
        yaml_pairs: set[tuple[str, str]] = set()
        src = tgt = None
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("- source:"):
                src = line.split(":", 1)[1].strip()
            elif line.startswith("target:") and src:
                tgt = line.split(":", 1)[1].strip()
                yaml_pairs.add((src, tgt))
                src = tgt = None
        drift = inv_pairs.symmetric_difference(yaml_pairs)
        if drift:
            print(f"[l6_arch_exceptions] inventory/yaml drift: {len(drift)} pair(s)")
            for pair in sorted(drift)[:10]:
                print(f"  {pair[0]} -> {pair[1]}")
            return 2 if fail_closed else 0

    print("[l6_arch_exceptions] OK — YAML present and aligned with inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
