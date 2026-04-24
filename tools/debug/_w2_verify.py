"""Verify the ratchet gate produces zero violations against seeded baseline."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

p = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}")
n = c.execute("SELECT COUNT(*) FROM mv_trace_replay_eval_gaps WHERE gap_type != 'ok'").fetchone()[0]
print(f"mv_trace_replay_eval_gaps where gap_type != 'ok': {n}")

import importlib

mod = importlib.import_module("ops_scripts.ci.adg_gates.gate_p1_trace_replay")
g = mod.TraceReplayEvalGate(sqlite_path=p)
r = g.run(emit_artifacts=False)
print(f"gate status: {r.status}")
print(f"gate violations: {len(r.violations)}")
