"""Invoke each P1/P2/P3 gate class directly against current snapshot; capture violations."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SNAP = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"),
              key=lambda p: p.stat().st_mtime)[-1]

print(f"Snapshot: {SNAP.name}\n")

# Gates with class entry points we can call in-process
GATE_CLASSES = [
    # (gate_id, module, class)
    ("G-P1-LIFE",          "ops_scripts.ci.adg_gates.gate_p1_lifecycle",             "LifecycleCoverageGate"),
    ("G-P1-TRACE",         "ops_scripts.ci.adg_gates.gate_p1_trace_replay",          "TraceReplayEvalGate"),
    ("G-P1-PROMPT-WIRING", "ops_scripts.ci.adg_gates.gate_p1_prompt_wiring",         "PromptAssemblyWiringGate"),
    ("G-P1-ARCH-WITNESS",  "ops_scripts.ci.adg_gates.gate_p1_architecture_witness",  "ArchitectureWitnessGate"),
]

import importlib

results: list[dict] = []

for gate_id, modname, cls in GATE_CLASSES:
    print(f"=== {gate_id} : {cls} ===")
    try:
        mod = importlib.import_module(modname)
        GateCls = getattr(mod, cls)
        gate = GateCls(sqlite_path=SNAP)
        res = gate.run(emit_artifacts=False)
        gross = len(res.violations) if res.violations else 0
        # "net" for these gates = gross (no runtime exemption concept — MV-level
        # exclusions are already applied at MV definition)
        summary = res.summary if hasattr(res, "summary") else {}
        print(f"  status={res.status}  violations={gross}")
        if summary:
            for k, v in list(summary.items())[:8]:
                if isinstance(v, (int, float, str, bool)):
                    print(f"    {k}: {v}")
        results.append({
            "gate_id": gate_id, "class": cls, "status": res.status,
            "violations": gross, "summary": {k: v for k, v in summary.items()
                                              if isinstance(v, (int, float, str, bool))},
        })
    except Exception as e:  # noqa: BLE001 -- diag script
        print(f"  ERROR: {type(e).__name__}: {e}")
        results.append({"gate_id": gate_id, "class": cls, "error": f"{type(e).__name__}: {e}"})
    print()

out = ROOT / "artifacts/ci_gates/p1_burndown_probe.json"
out.write_text(json.dumps({"snapshot": SNAP.name, "results": results}, indent=2), encoding="utf-8")
print(f"\nwrote: {out.relative_to(ROOT)}")
