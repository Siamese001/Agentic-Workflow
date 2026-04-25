import json

r = json.load(open("docs/reports/plans/mixin_audit.json", encoding="utf-8"))
print("== UNUSED MIXINS (defined but never subclassed) ==")
for n in r["mixins_unused_as_base"]:
    print(" ", n)
print()
print("== STEM CLUSTERS (multi-member) ==")
for k, v in sorted(r["stem_clusters_multi"].items()):
    print(f"  {k}: {v}")
print()
print("== TOP-USED MIXINS ==")
for n, c in r["mixin_usage_top"][:30]:
    print(f"  {c:3d}  {n}")
print()
print("== DEEPEST CONSUMERS ==")
for c in r["deepest_consumers"][:15]:
    mb = ", ".join(c["mixin_bases"])
    print(f"  {c['mixin_count']:2d}  {c['class']} ({c['file']})")
    print(f"        bases: {mb}")
print()
print("== TOP-FANIN MIXIN FILES (importers) ==")
for m in sorted(r["mixins"], key=lambda x: -x["importers"])[:20]:
    print(
        f"  imp={m['importers']:3d}  sub={m['subclassers']:2d}  body={m['body_size']:3d}  {m['name']:40s}  {m['path']}"
    )
print()
print("== TINY MIXINS (body_size <= 3, possible delete candidates) ==")
tiny = [m for m in r["mixins"] if m["body_size"] <= 3]
for m in sorted(tiny, key=lambda x: x["body_size"]):
    print(
        f"  body={m['body_size']}  sub={m['subclassers']}  imp={m['importers']}  {m['name']}  ({m['path']})"
    )
