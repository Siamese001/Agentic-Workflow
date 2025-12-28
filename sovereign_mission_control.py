#!/usr/bin/env python3
"""
Sovereign Mission Control - Eternal Circuit Orchestrator
Sequences: Auditor (v3) -> Validator (v2) -> Final Verification
"""
import subprocess
import sys
from pathlib import Path

def run_mission_step(cmd: str, stage: str):
    print(f"\n[ORCHESTRATOR - {stage}] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[L6 FAILURE] Stage {stage} failed with code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    root = Path(__file__).parent
    print(f"{'='*60}\n[MISSION CONTROL] INITIATING ETERNAL SOVEREIGNTY CIRCUIT\n{'='*60}")

    # Phase 1: High-level diagnosis (The Supreme Court)
    run_mission_step(f"python {root / 'sovereign_auditor_v3.py'}", "DIAGNOSIS")

    # Phase 2: Deep surgical enforcement (The Surgeon)
    run_mission_step(f"python {root / 'canon_validator_agentic_v2.py'} --target agentic_core", "SURGERY")

    # Phase 3: Final verification (The Seal)
    run_mission_step(f"python {root / 'sovereign_auditor_v3.py'}", "SEALING")

    print(f"\n{'='*60}\n[CIRCUIT COMPLETE] PERFECTION SEALED AT 100%\n{'='*60}")
