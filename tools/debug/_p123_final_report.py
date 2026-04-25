"""Final P1/P2/P3 burndown — gross / exempt / net per gate.

Primary source: artifacts/windsurf/wiring_gate_violations.jsonl
    Each entry is one gate run record with:
      - gate_id
      - tier
      - violations: list of violation objects
      - summary.raw_count   = gross (pre-exemption count)
      - summary.active_count = net   (what the ratchet counts after exemptions)
      - baseline_count      = ratchet ceiling (fail if active_count > baseline)
      - exempt = raw - active

Secondary: P1 class-based gates (ADG MVs) invoked in-process.
"""

from __future__ import annotations

import importlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SNAP = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
print(f"Snapshot: {SNAP.name}\n")

# ---------------------------------------------------------------------------
# Parse wiring_gate_violations.jsonl — one JSON object per line
# ---------------------------------------------------------------------------
JSONL = ROOT / "artifacts/windsurf/wiring_gate_violations.jsonl"
by_gate: dict[str, list[dict]] = {}
if JSONL.exists():
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        gid = rec.get("gate_id") or rec.get("gate") or "unknown"
        by_gate.setdefault(gid, []).append(rec)

# Keep latest run per gate
latest: dict[str, dict] = {}
for gid, recs in by_gate.items():
    latest[gid] = recs[-1]

# Tier mapping per run_contract_gates.py + empirical
TIER_MAP = {
    "J1_canonical_pipeline_wiring": "P2",
    "A1_orphan_module_ratchet": "P2",
    "A3_dead_public_symbol_ratchet": "P2",
    "A3b_dead_methods_ratchet": "P2",
    "G4_graph_reach_archival": "P2",
    "D_dead_folder_detector": "P2",
    "A6_import_cycles": "P2",
    "E1_trace_stub_modules": "P2",
    "G2_seam_test_export_coherence": "P2",
    "L1_layer_gravity": "P2",
    "L2_lpg_drift_ratchet": "P2",
    "M1_module_loc_ratchet": "P2",
    "D1_layer_doc_binding": "P3",
    "S1_global_state_mutation_ratchet": "P2",
    "S2_uwg_bypass_ratchet": "P2",
    "S3_exception_swallow_ratchet": "P2",
    "S4_unused_imports_ratchet": "P2",
    "W5_waiver_expiry": "P2",
}

# ---------------------------------------------------------------------------
# Class-based P1 gates
# ---------------------------------------------------------------------------
CLASS_GATES = [
    ("P1", "G-P1-LIFE", "gate_p1_lifecycle", "LifecycleCoverageGate"),
    ("P1", "G-P1-TRACE", "gate_p1_trace_replay", "TraceReplayEvalGate"),
    ("P1", "G-P1-PROMPT-WIRING", "gate_p1_prompt_wiring", "PromptAssemblyWiringGate"),
    ("P1", "G-P1-ARCH-WITNESS", "gate_p1_architecture_witness", "ArchitectureWitnessGate"),
]

class_results: list[dict] = []
for tier, gate_id, modname, cls in CLASS_GATES:
    try:
        mod = importlib.import_module(f"ops_scripts.ci.adg_gates.{modname}")
        GateCls = getattr(mod, cls)
        gate = GateCls(sqlite_path=SNAP)
        res = gate.run(emit_artifacts=False)
        net = len(res.violations) if res.violations else 0
        # These gates' MVs already apply exemptions at definition time.
        # gross != net would require re-running MV without exemptions, which we
        # approximate by reading the raw underlying MV row count.
        class_results.append(
            {
                "tier": tier,
                "gate_id": gate_id,
                "status": res.status,
                "gross": None,
                "net": net,
                "exempt": None,
                "source_views": list(GateCls.source_views) if hasattr(GateCls, "source_views") else [],
            }
        )
    except (ImportError, AttributeError, sqlite3.Error, RuntimeError, TypeError) as e:
        class_results.append({"tier": tier, "gate_id": gate_id, "error": f"{type(e).__name__}: {e}"})

# Raw MV row counts for "gross" approximation of P1 gates
conn = sqlite3.connect(SNAP)


def _count(t: str) -> int | None:
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    except sqlite3.Error:
        return None


MV_ROWS = {
    "G-P1-LIFE": ((_count("mv_l2_phase_coverage") or 0) + (_count("mv_exit_disposition_coverage") or 0)),
    "G-P1-TRACE": ((_count("mv_trace_replay_eval_gaps") or 0) + (_count("mv_eval_coverage_by_path") or 0)),
    "G-P1-PROMPT-WIRING": _count("mv_prompt_assembly_wiring_gaps") or 0,
    "G-P1-ARCH-WITNESS": (
        (_count("mv_handoff_witness_tiers") or 0) + (_count("mv_cross_cutting_witness_tiers") or 0)
    ),
}

for r in class_results:
    r["gross"] = MV_ROWS.get(r["gate_id"])
    if r["gross"] is not None and r["net"] is not None:
        r["exempt"] = r["gross"] - r["net"]

# ---------------------------------------------------------------------------
# violations table (P1 SC/AP burndown)
# ---------------------------------------------------------------------------
total_viol = conn.execute("SELECT COUNT(*) FROM violations").fetchone()[0]
exempt_viol = conn.execute(
    "SELECT COUNT(*) FROM violations WHERE disposition IN "
    "('exempt','waived','triaged_exempt','deferred','accepted')"
).fetchone()[0]
high_crit = conn.execute(
    "SELECT COUNT(*) FROM violations WHERE severity IN ('HIGH','CRITICAL') "
    "AND disposition NOT IN ('exempt','waived','triaged_exempt','deferred','accepted')"
).fetchone()[0]
by_sev = {r[0]: r[1] for r in conn.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity")}


# ---------------------------------------------------------------------------
# Render report
# ---------------------------------------------------------------------------
def fmt(v):
    return "—" if v is None else str(v)


def print_table(title: str, rows: list[dict], keys: list[str], headers: list[str]):
    print(f"\n{title}")
    print("-" * 110)
    widths = [
        max(len(headers[i]), max((len(fmt(r.get(k))) for r in rows), default=0)) + 2
        for i, k in enumerate(keys)
    ]
    fmts = "".join(f"{{:<{w}}}" for w in widths)
    print(fmts.format(*headers))
    print("-" * 110)
    for r in rows:
        print(fmts.format(*[fmt(r.get(k)) for k in keys]))


print("=" * 110)
print("P1/P2/P3 BURNDOWN REPORT")
print("=" * 110)

# P1 CLASS GATES
print_table(
    "P1 — STRUCTURAL CONFORMANCE GATES (class-based, ADG SQLite MVs)",
    class_results,
    ["tier", "gate_id", "status", "gross", "exempt", "net"],
    ["Tier", "Gate", "Status", "Gross(MV)", "Exempt", "Net(emit)"],
)

# P2/P3 SCRIPT GATES (from jsonl)
ratchet_rows = []
for gid, rec in sorted(latest.items()):
    tier = TIER_MAP.get(gid, "—")
    s = rec.get("summary", {}) or {}
    gross = s.get("raw_count")
    net = s.get("active_count")
    baseline = rec.get("baseline_count")
    exempt = None
    if gross is not None and net is not None:
        exempt = gross - net
    status = rec.get("status") or ("fail" if (net or 0) > (baseline or 0) else "pass")
    ratchet_rows.append(
        {
            "tier": tier,
            "gate_id": gid,
            "status": status,
            "gross": gross,
            "exempt": exempt,
            "net": net,
            "baseline": baseline,
        }
    )

ratchet_rows.sort(key=lambda r: (r["tier"], r["gate_id"]))
print_table(
    "P2/P3 — HYGIENE RATCHET GATES (from wiring_gate_violations.jsonl)",
    ratchet_rows,
    ["tier", "gate_id", "status", "gross", "exempt", "net", "baseline"],
    ["Tier", "Gate", "Status", "Gross", "Exempt", "Net", "Baseline"],
)

# AP BACKLOG
print("\nANTI-PATTERN BACKLOG (violations table — source for P1 HARDEN ratchet)")
print("-" * 110)
print(f"Gross (all rows):      {total_viol}")
print(f"Exempt (disposition):  {exempt_viol}")
print(f"Net:                   {total_viol - exempt_viol}")
print(f"Net HIGH+CRITICAL:     {high_crit}  (P1 HARDEN ceiling = 0)")
print(f"By severity:           {by_sev}")

# TOTALS
print("\n" + "=" * 110)
print("TOTALS BY TIER")
print("=" * 110)
totals = {"P1": [0, 0, 0], "P2": [0, 0, 0], "P3": [0, 0, 0]}
for r in class_results + ratchet_rows:
    t = r.get("tier")
    if t not in totals:
        continue
    for i, k in enumerate(("gross", "exempt", "net")):
        v = r.get(k)
        if isinstance(v, int):
            totals[t][i] += v
# Fold AP backlog into P1 too (it's the P1 HARDEN gate's input)
totals["P1"][0] += total_viol
totals["P1"][1] += exempt_viol
totals["P1"][2] += total_viol - exempt_viol

print(f"{'Tier':<8}{'Gross':>12}{'Exempt':>12}{'Net':>12}")
print("-" * 44)
for t, (g, e, n) in totals.items():
    print(f"{t:<8}{g:>12}{e:>12}{n:>12}")

# Persist
out = ROOT / "artifacts/ci_gates/p123_burndown_report.json"
out.write_text(
    json.dumps(
        {
            "snapshot": SNAP.name,
            "p1_class_gates": class_results,
            "p2_p3_ratchet_gates": ratchet_rows,
            "violations_table": {
                "gross": total_viol,
                "exempt": exempt_viol,
                "net": total_viol - exempt_viol,
                "high_crit": high_crit,
                "by_severity": by_sev,
            },
            "totals": {t: {"gross": g, "exempt": e, "net": n} for t, (g, e, n) in totals.items()},
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"\nreport written: {out.relative_to(ROOT)}")

conn.close()
