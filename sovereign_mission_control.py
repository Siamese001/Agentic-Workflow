#!/usr/bin/env python3
"""
Sovereign Mission Control - Eternal Circuit Orchestrator
Sequences: Auditor (v3) -> Validator (v2) -> Final Verification
"""
import subprocess
import sys
import os
from pathlib import Path

def run_mission_step(args: list, stage: str):
    cmd_str = " ".join(str(a) for a in args)
    print(f"\n[ORCHESTRATOR - {stage}] {cmd_str}")
    
    # Use list-based execution for safety and cross-platform path handling
    result = subprocess.run(args, capture_output=False)
    
    if result.returncode != 0:
        print(f"[L6 FAILURE] Stage {stage} failed with code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    root = Path(__file__).parent
    
    # Load environment for global flags
    is_dry_run = os.getenv("MISSION_DRY_RUN", "False").lower() == "true"

    print(f"{'='*60}")
    print(f"[MISSION CONTROL] INITIATING ETERNAL SOVEREIGNTY CIRCUIT")
    if is_dry_run: print("[!] MODE: DRY RUN (Diagnostics only)")
    print(f"{'='*60}")

    python_bin = sys.executable

    # Phase 1: High-level diagnosis (The Supreme Court)
    run_mission_step([python_bin, str(root / 'sovereign_auditor_v3.py')], "DIAGNOSIS")

    # Phase 2: Deep surgical enforcement (The Surgeon)
    if not is_dry_run:
        run_mission_step([python_bin, str(root / 'canon_validator_agentic_v2.py'), "--target", "agentic_core"], "SURGERY")
    else:
        print("\n[SKIP] Stage SURGERY bypassed in Dry Run.")

    # Phase 3: Final verification (The Seal)
    run_mission_step([python_bin, str(root / 'sovereign_auditor_v3.py')], "SEALING")

    print(f"\n{'='*60}\n[CIRCUIT COMPLETE] PERFECTION SEALED AT 100%\n{'='*60}")
