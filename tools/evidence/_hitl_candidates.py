"""HITL gate: list guardian-exempt candidates across all four P2 categories.

Prints teardown + has_reraise sub-categories that may qualify for
# guardian: allow-* exemptions, requiring explicit HITL approval per §8.

Usage:
    python tools/evidence/_hitl_candidates.py
"""
from __future__ import annotations

import json
from pathlib import Path

FILES = [
    ("return_none_swallow",      "w2_return_none_swallow_subcategorized.json"),
    ("log_and_swallow",          "log_and_swallow_subcategorized.json"),
    ("silent_exception_swallow", "silent_exception_swallow_subcategorized.json"),
    ("broad_exception_catch",    "broad_exception_catch_subcategorized.json"),
]

EXEMPT_SUBS = {"teardown", "has_reraise"}


def main() -> None:
    candidates: list[dict] = []

    for kind, fname in FILES:
        path = Path("artifacts/adg_analysis") / fname
        data: list[dict] = json.loads(path.read_text())
        for entry in data:
            if entry.get("sub_category") in EXEMPT_SUBS:
                candidates.append({
                    "kind": kind,
                    "sub_category": entry["sub_category"],
                    "source_file": entry["source_file"],
                    "line_no": entry["line_no"],
                    "func": entry.get("containing_function", ""),
                })

    print(f"Total guardian-exempt candidates: {len(candidates)}")
    print()

    by_sub: dict[str, list[dict]] = {}
    for c in candidates:
        by_sub.setdefault(c["sub_category"], []).append(c)

    for sub in sorted(by_sub.keys()):
        items = by_sub[sub]
        print(f"--- {sub} ({len(items)} entries) ---")
        for item in items[:20]:
            sf = item["source_file"]
            ln = item["line_no"]
            fn = item["func"]
            kd = item["kind"]
            print(f"  [{kd}]  {sf}:{ln}  in {fn}()")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")
        print()

    # Save for HITL review
    out = Path("artifacts/adg_analysis/hitl_guardian_candidates.json")
    out.write_text(json.dumps(candidates, indent=2))
    print(f"Full candidate list: {out}  ({len(candidates)} entries)")


if __name__ == "__main__":
    main()
