import json

data = json.load(open("artifacts/notion/open_by_wave.json", encoding="utf-8"))
waves = data["waves"]
order = sorted(waves, key=lambda w: (-len(waves[w]), w))
for w in order:
    items = waves[w]
    items.sort(key=lambda x: -(x.get("impact") or 0))
    print(f"### {w} ({len(items)})")
    for it in items:
        band = it["band"]
        imp = it.get("impact")
        imp_s = f"{imp:.0f}" if imp else "  -"
        phase = (it["phase"] or "").strip()
        title = (it["title"] or "").strip()
        if title.startswith(f"[{band}]"):
            title = title[len(f"[{band}]"):].strip()
        title = title[:90]
        print(f"  [{band:<8}] {imp_s:>4}  {phase:<20} {title}")
    print()
