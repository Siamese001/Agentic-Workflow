"""Inspect latest gate dispatcher results and P0 two-pass runner."""

import json
import pathlib

adg = pathlib.Path("artifacts/adg")

gate_files = sorted(adg.glob("adg_gate_results_*.json"))
if gate_files:
    p = gate_files[-1]
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"=== {p.name} ===")
    print("schema keys:", list(d.keys())[:8])
    for key in ("gates", "results", "gate_results"):
        if key in d:
            for g in d[key]:
                st = g.get("status", "?")
                name = g.get("name") or g.get("gate_family") or g.get("gate") or "?"
                n = g.get("violation_count") or len(g.get("violations", []) or [])
                if st not in ("PASS", "ok", "passed", "clean"):
                    msgs = g.get("violations", [])
                    print(f"  FAIL  {name:30}  status={st}  count={n}")
                    for m in (msgs or [])[:3]:
                        txt = m.get("message") if isinstance(m, dict) else str(m)
                        print(f"        - {txt[:140] if txt else m}")
                else:
                    print(f"  ok    {name:30}  status={st}  count={n}")

print()

p0 = sorted(pathlib.Path("artifacts/ci_gates").glob("p0_runner_full_*.json"))
if p0:
    p = p0[-1]
    d = json.loads(p.read_text(encoding="utf-8"))
    print(f"=== {p.name} ===")
    for r in d.get("results", []):
        st = r.get("status", "?")
        name = r.get("gate_family", "?")
        vs = r.get("violations", []) or []
        print(f"  {st:<9} {name:<28} violations={len(vs)}")
        if st != "passed":
            for v in vs[:5]:
                msg = v.get("message", str(v))
                print(f"    - {msg[:140]}")
