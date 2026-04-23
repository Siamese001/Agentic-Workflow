"""End-to-end W2 proof: run every wiring gate and summarize.

Reports (gate, status, tier, violations, note) for all 6 W1+W2 gates.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GATES = [
    ("J1 canonical pipeline wiring", "check_canonical_pipeline_wiring.py", "B"),
    ("A3 dead-symbol ratchet", "check_dead_symbols_ratchet.py", "R"),
    ("E1 trace-stub ratchet", "check_trace_stub_modules.py", "R"),
    ("G2 seam-test export coherence", "check_seam_test_export_coherence.py", "B"),
    ("L2 L_PG drift ratchet", "check_lpg_drift_ratchet.py", "R"),
    ("M1 module LOC ratchet", "check_module_loc_ratchet.py", "R"),
    ("D1 layer doc binding", "check_layer_doc_binding.py", "W"),
    ("S2 UWG bypass", "check_uwg_bypass_ratchet.py", "R"),
    ("S4 unused imports", "check_unused_imports_ratchet.py", "R"),
    ("W5 waiver expiry", "check_waiver_expiry.py", "B"),
]


def main() -> int:
    print(f"{'GATE':38s} {'TIER':4s} {'EXIT':4s} {'VIOLATIONS':10s}  NOTE")
    print("-" * 100)
    for label, script, tier in GATES:
        path = ROOT / "ops_scripts" / "ci" / script
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        first_line = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
        n_violations = _extract_count(first_line)
        if "baseline=" in proc.stdout:
            note = _extract_baseline_note(proc.stdout)
        elif proc.returncode == 0:
            note = "pass"
        else:
            note = "BLOCK"
        print(f"{label:38s} {tier:4s} {proc.returncode:4d} {n_violations:10d}  {note}")
    return 0


def _extract_count(first_line: str) -> int:
    """Parse 'violations=N' out of the gate's header line."""
    if "violations=" in first_line:
        try:
            return int(first_line.split("violations=")[1].split()[0])
        except (IndexError, ValueError):
            return -1
    return -1


def _extract_baseline_note(stdout: str) -> str:
    for line in stdout.splitlines():
        if "baseline=" in line:
            return line.strip().lstrip("[").rstrip("]")
    return "ratchet"


if __name__ == "__main__":
    sys.exit(main())
