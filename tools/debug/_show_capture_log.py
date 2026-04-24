import json, pathlib
p = pathlib.Path("artifacts/windsurf/deferred_scope_capture.jsonl")
if not p.exists():
    print("NO LOG FILE at", p)
    raise SystemExit
lines = p.read_text(encoding="utf-8").splitlines()
print(f"total lines in log: {len(lines)}")
for ln in lines[-20:]:
    try:
        r = json.loads(ln)
        m = r.get("marker") or {}
        ts = r.get("timestamp", "")[:19]
        kind = r.get("kind", "?")
        band = r.get("band", "-")
        plan = (m.get("plan") or "-")[:50]
        phase = m.get("phase", "-")
        impact = r.get("impact_score", "-")
        notion_url = r.get("notion_url") or r.get("reason") or "-"
        print(f"  {ts} kind={kind:30s} band={band} impact={impact} plan={plan} phase={phase}")
        if notion_url != "-":
            print(f"      -> {notion_url}")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print("  parse-err:", ln[:100])
