"""Full P1/P2/P3 burndown runner.

Invokes every wiring-CI gate script referenced by run_contract_gates.py plus the
class-based P1 gates. For each gate: capture exit code, extract violation count
from stdout (best-effort heuristics), and report gross/net/exempt state.
"""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SNAP = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
print(f"Snapshot: {SNAP.name}")
print(f"Root:     {ROOT}\n")

# ---------------------------------------------------------------------------
# Class-based P1 gates (callable in-process against snapshot)
# ---------------------------------------------------------------------------
CLASS_GATES = [
    ("P1", "G-P1-LIFE", "gate_p1_lifecycle", "LifecycleCoverageGate"),
    ("P1", "G-P1-TRACE", "gate_p1_trace_replay", "TraceReplayEvalGate"),
    ("P1", "G-P1-PROMPT-WIRING", "gate_p1_prompt_wiring", "PromptAssemblyWiringGate"),
    ("P1", "G-P1-ARCH-WITNESS", "gate_p1_architecture_witness", "ArchitectureWitnessGate"),
]

# ---------------------------------------------------------------------------
# Script-based ratchet gates (P2/P3 hygiene via subprocess)
# From run_contract_gates.py WIRING-CI GATE PLANE
# ---------------------------------------------------------------------------
SCRIPT_GATES = [
    # tier, gate_id, script
    ("P2", "J1-pipeline-wiring", "ops_scripts/ci/check_canonical_pipeline_wiring.py"),
    ("P2", "A1-orphan-module", "ops_scripts/ci/check_orphan_module_ratchet.py"),
    ("P2", "A3-dead-symbol", "ops_scripts/ci/check_dead_symbols_ratchet.py"),
    ("P2", "A3b-dead-methods", "ops_scripts/ci/check_dead_methods_ratchet.py"),
    ("P2", "G4-graph-reach", "ops_scripts/ci/check_graph_reach_archival.py"),
    ("P2", "D7-dead-folder", "ops_scripts/ci/check_dead_folder_detector.py"),
    ("P2", "A6-import-cycle", "ops_scripts/ci/check_import_cycles.py"),
    ("P2", "E1-trace-stub", "ops_scripts/ci/check_trace_stub_modules.py"),
    ("P2", "G2-seam-test", "ops_scripts/ci/check_seam_test_export_coherence.py"),
    ("P2", "L1-layer-gravity", "ops_scripts/ci/check_layer_gravity.py"),
    ("P2", "L2-lpg-drift", "ops_scripts/ci/check_lpg_drift_ratchet.py"),
    ("P2", "M1-module-loc", "ops_scripts/ci/check_module_loc_ratchet.py"),
    ("P3", "D1-layer-doc", "ops_scripts/ci/check_layer_doc_binding.py"),
    ("P2", "S1-global-state", "ops_scripts/ci/check_global_state_mutation_ratchet.py"),
    ("P2", "S2-uwg-bypass", "ops_scripts/ci/check_uwg_bypass_ratchet.py"),
    ("P2", "S3-exc-swallow", "ops_scripts/ci/check_exception_swallow_ratchet.py"),
    ("P2", "S4-unused-imports", "ops_scripts/ci/check_unused_imports_ratchet.py"),
    ("P2", "W5-waiver-expiry", "ops_scripts/ci/check_waiver_expiry.py"),
]


def run_script(script: str) -> dict:
    full = ROOT / script
    if not full.exists():
        return {
            "status": "missing",
            "exit": None,
            "gross": None,
            "net": None,
            "exempt": None,
            "note": "script not found",
        }
    result = subprocess.run(
        [sys.executable, str(full)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=ROOT,
        check=False,
    )
    out = (result.stdout or "") + "\n" + (result.stderr or "")
    # Keep HEAD + TAIL of output — first line usually has machine-readable
    # counters like "current=N baseline=M", tail has the per-violation detail.
    head = out[:2000]
    tail = out[-2000:] if len(out) > 4000 else ""
    preserved = head + ("\n...\n" + tail if tail else "")
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "exit": result.returncode,
        "output": preserved,
    }


def parse_counts(output: str) -> dict:
    """Best-effort extraction of gross/net/exempt counts from gate output."""
    gross = net = exempt = None
    # Common patterns:
    # "current=42 ceiling=100"  "violations: 42"  "found 42"  "N violations"
    # "baseline=N current=M"  "exemptions=N"
    m = re.search(r"current[=:\s]+(\d+)", output, re.IGNORECASE)
    if m:
        net = int(m.group(1))
    m = re.search(r"(\d+)\s+violations?\b", output, re.IGNORECASE)
    if m and net is None:
        net = int(m.group(1))
    m = re.search(r"gross[=:\s]+(\d+)", output, re.IGNORECASE)
    if m:
        gross = int(m.group(1))
    m = re.search(r"exempt(?:ions?)?[=:\s]+(\d+)", output, re.IGNORECASE)
    if m:
        exempt = int(m.group(1))
    m = re.search(r"baseline[=:\s]+(\d+)", output, re.IGNORECASE)
    baseline = int(m.group(1)) if m else None
    return {"gross": gross, "net": net, "exempt": exempt, "baseline": baseline}


# ---------------------------------------------------------------------------
# Run class gates
# ---------------------------------------------------------------------------
all_results: list[dict] = []

print("=" * 100)
print("P1 CLASS-BASED GATES")
print("=" * 100)
print(f"{'Tier':<5}{'Gate':<24}{'Status':<10}{'Gross':>8}{'Net':>8}{'Exempt':>8}  Notes")
print("-" * 100)

for tier, gate_id, modname, cls in CLASS_GATES:
    try:
        mod = importlib.import_module(f"ops_scripts.ci.adg_gates.{modname}")
        GateCls = getattr(mod, cls)
        gate = GateCls(sqlite_path=SNAP)
        res = gate.run(emit_artifacts=False)
        net = len(res.violations) if res.violations else 0
        # These gates apply MV-level filters. "Gross" vs "Net" is approximated:
        #   gross = what the raw MV would emit without the gate's filter
        #   net   = what the gate actually emits
        # Without re-querying the MV, we report net only.
        all_results.append(
            {
                "tier": tier,
                "gate_id": gate_id,
                "status": res.status,
                "gross": None,
                "net": net,
                "exempt": None,
                "signal_source": ",".join(GateCls.source_views) if hasattr(GateCls, "source_views") else "",
            }
        )
        print(
            f"{tier:<5}{gate_id:<24}{res.status:<10}{'—':>8}{net:>8}{'—':>8}  {','.join(GateCls.source_views)[:40]}"
        )
    except (ImportError, AttributeError, Exception) as e:  # noqa: BLE001
        all_results.append({"tier": tier, "gate_id": gate_id, "error": f"{type(e).__name__}: {e}"})
        print(
            f"{tier:<5}{gate_id:<24}{'ERROR':<10}{'—':>8}{'—':>8}{'—':>8}  {type(e).__name__}: {str(e)[:40]}"
        )

# ---------------------------------------------------------------------------
# Run script gates
# ---------------------------------------------------------------------------
print("\n" + "=" * 100)
print("P2/P3 SCRIPT-BASED RATCHET GATES")
print("=" * 100)
print(f"{'Tier':<5}{'Gate':<24}{'Status':<10}{'Exit':>5}{'Gross':>8}{'Net':>8}{'Base':>8}  Notes")
print("-" * 100)

for tier, gate_id, script in SCRIPT_GATES:
    info = run_script(script)
    if info["status"] == "missing":
        all_results.append({"tier": tier, "gate_id": gate_id, "status": "missing", "script": script})
        print(f"{tier:<5}{gate_id:<24}{'MISSING':<10}{'—':>5}{'—':>8}{'—':>8}{'—':>8}  {script}")
        continue
    counts = parse_counts(info["output"])
    out_tail = info["output"].strip().splitlines()
    last_line = out_tail[-1][:60] if out_tail else ""
    row = {
        "tier": tier,
        "gate_id": gate_id,
        "status": info["status"],
        "exit": info["exit"],
        **counts,
        "script": script,
        "last_line": last_line,
    }
    all_results.append(row)
    g = counts["gross"] if counts["gross"] is not None else "—"
    n = counts["net"] if counts["net"] is not None else "—"
    b = counts["baseline"] if counts["baseline"] is not None else "—"
    print(
        f"{tier:<5}{gate_id:<24}{info['status']:<10}{info['exit']:>5}{str(g):>8}{str(n):>8}{str(b):>8}  {last_line[:50]}"
    )

# ---------------------------------------------------------------------------
# Violations-table aggregate (anti-pattern burndown — the ratcheted backlog)
# ---------------------------------------------------------------------------
import sqlite3

conn = sqlite3.connect(SNAP)
print("\n" + "=" * 100)
print("ANTI-PATTERN BACKLOG (violations table — source for burndown ratchets)")
print("=" * 100)
print(f"{'Severity':<10}{'Disposition':<20}{'Count':>10}")
print("-" * 100)
total = 0
for r in conn.execute(
    "SELECT severity, disposition, COUNT(*) FROM violations GROUP BY severity, disposition ORDER BY severity, COUNT(*) DESC"
):
    print(f"{str(r[0]):<10}{str(r[1]):<20}{r[2]:>10}")
    total += r[2]
print("-" * 100)
print(f"{'TOTAL':<30}{total:>10}")

# Gross vs Net interpretation for AP burndown:
#   gross  = all rows in violations
#   exempt = rows with disposition in ('exempt', 'waived', 'triaged_exempt')
#   net    = gross - exempt  (what the ratchet gate actually counts)
exempt_ct = conn.execute(
    "SELECT COUNT(*) FROM violations WHERE disposition IN ('exempt','waived','triaged_exempt')"
).fetchone()[0]
print(f"\nGross:  {total}")
print(f"Exempt: {exempt_ct}  (dispositions: exempt / waived / triaged_exempt)")
print(f"Net:    {total - exempt_ct}")

conn.close()

# Write machine-readable report
out = ROOT / "artifacts/ci_gates/p123_burndown_report.json"
out.write_text(
    json.dumps(
        {
            "snapshot": SNAP.name,
            "results": all_results,
            "violations_table": {"gross": total, "exempt": exempt_ct, "net": total - exempt_ct},
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"\nreport: {out.relative_to(ROOT)}")
