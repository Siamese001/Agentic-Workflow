import json, sys

data = json.load(open("artifacts/notion/open_by_wave.json", encoding="utf-8"))
waves = data["waves"]
prefix = sys.argv[1] if len(sys.argv) > 1 else ""
include = sys.argv[2] if len(sys.argv) > 2 else ""
names = [w for w in waves if (prefix and w.startswith(prefix)) or (include and w in include.split(","))]
names.sort()
for w in names:
    items = waves[w]
    items.sort(key=lambda x: -(x.get("impact") or 0))
    for it in items:
        band = it["band"]
        imp = it.get("impact")
        imp_s = f"{imp:.0f}" if imp else "-"
        phase = (it["phase"] or "").strip()
        title = (it["title"] or "").strip()
        if title.startswith(f"[{band}]"):
            title = title[len(f"[{band}]") :].strip()
        print(f"{w}|{band}|{imp_s}|{phase}|{title}")
