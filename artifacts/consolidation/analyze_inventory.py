"""Analyze agent inventory to identify consolidation targets."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INV_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "agent_inventory.json"


def main():
    inv = json.loads(INV_PATH.read_text(encoding="utf-8"))
    agents = inv["agents"]

    print("=" * 80)
    print("HIGH BOILERPLATE (>70%)")
    print("=" * 80)
    for a in agents:
        if a.get("boilerplate_ratio", 0) > 0.7:
            print(
                f"  {a['class_name']:45s} ratio={a['boilerplate_ratio']} total={a['total_loc']} domain={a['domain_logic_loc']} layer={a['layer']}"
            )

    print()
    print("=" * 80)
    print("LOW DOMAIN LOC (<5 lines)")
    print("=" * 80)
    for a in agents:
        if a.get("domain_logic_loc", 999) < 5:
            print(
                f"  {a['class_name']:45s} domain={a['domain_logic_loc']} total={a['total_loc']} bases={a.get('all_bases', [])} layer={a['layer']}"
            )

    print()
    print("=" * 80)
    print("HIGH BLAST RADIUS (>=20)")
    print("=" * 80)
    for a in agents:
        if a.get("blast_radius", 0) >= 20:
            print(f"  {a['class_name']:45s} blast={a['blast_radius']} layer={a['layer']}")

    print()
    print("=" * 80)
    print("BASE CLASS DISTRIBUTION")
    print("=" * 80)
    base_counter = Counter()
    for a in agents:
        for b in a.get("all_bases", []):
            base_counter[b] += 1
    for name, count in base_counter.most_common(20):
        print(f"  {name:45s} {count}")

    print()
    print("=" * 80)
    print("CAPABILITY MIXIN DISTRIBUTION")
    print("=" * 80)
    mixin_counter = Counter()
    for a in agents:
        for m in a.get("capability_mixins", []):
            mixin_counter[m] += 1
    for name, count in mixin_counter.most_common(20):
        print(f"  {name:45s} {count}")

    print()
    print("=" * 80)
    print("AGENTS BY BASE CLASS GROUP (for consolidation targeting)")
    print("=" * 80)
    # Group agents by their base class signature
    base_groups: dict[str, list] = {}
    for a in agents:
        key = "+".join(sorted(a.get("all_bases", [])))
        if not key:
            key = "(no bases)"
        base_groups.setdefault(key, []).append(a)

    for key, group in sorted(base_groups.items(), key=lambda x: -len(x[1])):
        if len(group) >= 3:
            print(f"\n  [{key}] ({len(group)} agents)")
            for a in group:
                print(
                    f"    {a['class_name']:42s} domain={a['domain_logic_loc']:3d} total={a['total_loc']:3d} bp={a['boilerplate_ratio']:.2f} layer={a['layer']} methods={a.get('domain_methods', [])}"
                )

    # Find agents with ZERO entrypoints
    print()
    print("=" * 80)
    print("AGENTS WITH NO ENTRYPOINTS (stub candidates)")
    print("=" * 80)
    for a in agents:
        if not a.get("entrypoints"):
            print(
                f"  {a['class_name']:45s} domain={a['domain_logic_loc']} total={a['total_loc']} layer={a['layer']} methods={a.get('domain_methods', [])}"
            )

    # Summary counts
    print()
    print("=" * 80)
    print("CONSOLIDATION OPPORTUNITY SUMMARY")
    print("=" * 80)
    high_bp = [a for a in agents if a.get("boilerplate_ratio", 0) > 0.5]
    low_domain = [a for a in agents if a.get("domain_logic_loc", 999) < 10]
    no_entry = [a for a in agents if not a.get("entrypoints")]
    stubs = [a for a in agents if a.get("domain_logic_loc", 999) < 5 and not a.get("entrypoints")]
    print(f"  Boilerplate >50%: {len(high_bp)}")
    print(f"  Domain LOC <10:   {len(low_domain)}")
    print(f"  No entrypoints:   {len(no_entry)}")
    print(f"  Stub agents:      {len(stubs)} (low domain + no entrypoints)")


if __name__ == "__main__":
    main()
