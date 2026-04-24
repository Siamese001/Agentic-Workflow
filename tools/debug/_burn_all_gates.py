"""Run every blocking gate against the latest snapshot."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
print(f"snap: {snap.name}\n")

from tools.generate.validation import (  # noqa: E402
    _check_agentic_antipatterns,
    _check_dead_production_imports,
    _check_p1_ratchet,
    _check_p2_ratchet,
    _check_structural_conformance,
    _check_witness_tier_gates,
)

gates = [
    ("P1 ratchet", lambda: _check_p1_ratchet(sqlite_path=snap)),
    ("P2 ratchet", lambda: _check_p2_ratchet(sqlite_path=snap)),
    ("dead_production_imports", lambda: _check_dead_production_imports(sqlite_path=snap)),
    ("structural_conformance", lambda: _check_structural_conformance(sqlite_path=snap)),
    ("agentic_antipatterns", lambda: _check_agentic_antipatterns(sqlite_path=snap)),
    ("witness_tier_gates", lambda: _check_witness_tier_gates(sqlite_path=snap)),
]

results = []
for name, fn in gates:
    try:
        fn()
        results.append((name, "OK", ""))
    except SystemExit as e:
        results.append((name, f"EXIT={e.code}", ""))
    except (RuntimeError, ValueError, OSError, KeyError) as e:
        results.append((name, "RAISED", f"{type(e).__name__}: {e}"))

print("\n=== SUMMARY ===")
for name, status, note in results:
    marker = "OK " if status == "OK" else "FAIL"
    print(f"  [{marker}] {name:<30} {status} {note}")
