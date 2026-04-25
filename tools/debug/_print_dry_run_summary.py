import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rescore = json.loads((ROOT / "artifacts/notion/_pending_rescore.json").read_text(encoding="utf-8"))
audit = json.loads((ROOT / "artifacts/notion/_pending_audit.json").read_text(encoding="utf-8"))

print("=" * 90)
print("PASS 1 RESCORE — scorable rows (proposed P-Band)")
print("=" * 90)
scored = [r for r in rescore if r["proposed_band"] != "UNSCORABLE"]
scored.sort(key=lambda x: -(x["impact"] or 0))
for r in scored:
    print(
        f"\n[{r['proposed_band']}] impact={r['impact']} layer={r['computed_layer']} fan_in={r['computed_fan_in']} surface={r['computed_surface']}"
    )
    print(f"  {r['wave']}/{r['phase']}: {r['title']}")
    print(f"  paths: {r['candidate_paths'][:3]}")
    print(f"  id={r['id']}")

print()
print("=" * 90)
print("PASS 1 RESCORE — UNSCORABLE summary (no file paths or no ADG match)")
print("=" * 90)
unscorable = [r for r in rescore if r["proposed_band"] == "UNSCORABLE"]
print(f"Total: {len(unscorable)}")
print("Sample (first 5):")
for r in unscorable[:5]:
    print(f"  {r['wave']}/{r['phase']}: {r['title'][:100]}")

print()
print("=" * 90)
print("PASS 2 AUDIT — LANDED candidates (mark Done)")
print("=" * 90)
landed = [r for r in audit if r.get("verdict") == "LANDED"]
for r in landed:
    print(f"\n  {r['wave']}/{r['phase']} [{r['category']}]: {r['title']}")
    print(f"    id={r['id']}")
    extras = {
        k: v for k, v in r.items() if k not in ("id", "url", "wave", "phase", "title", "category", "verdict")
    }
    for k, v in extras.items():
        print(f"    {k}: {v}")

print()
print("=" * 90)
print("PASS 2 AUDIT — PARTIAL (rewrite Blocking Items)")
print("=" * 90)
partial = [r for r in audit if r.get("verdict") == "PARTIAL"]
for r in partial:
    print(f"\n  {r['wave']}/{r['phase']} [{r['category']}]: {r['title']}")
    print(f"    id={r['id']}")
    extras = {
        k: v for k, v in r.items() if k not in ("id", "url", "wave", "phase", "title", "category", "verdict")
    }
    for k, v in extras.items():
        print(f"    {k}: {v}")

print()
print("=" * 90)
print("PASS 2 AUDIT — MISSING (still real work, no action)")
print("=" * 90)
missing = [r for r in audit if r.get("verdict") == "MISSING"]
print(f"Total: {len(missing)}")
for r in missing[:10]:
    print(f"  {r['wave']}/{r['phase']}: {r['title'][:100]}")
if len(missing) > 10:
    print(f"  ... ({len(missing) - 10} more)")
