#!/usr/bin/env python3
"""
Sovereign Mission Control - Eternal Circuit Orchestrator
Sequences: Auditor (v3) -> Validator (v2) -> Final Verification
"""
import subprocess
import sys
import os
from pathlib import Path

# [CONSTITUTIONAL ARMING] Key 2 Compliance ✓
try:
    from agentic_core.config.P1_core.structure_blueprint import ACTIVE_CANON_KEYS
    print(f"   [OK] SSOT Physics Loaded: {len(ACTIVE_CANON_KEYS)} keys active.") # Should show 19
except ImportError:
    print("[!] [L6 FAILURE] CRITICAL GRAVITY LOSS: SSOT Blueprint missing.")
    sys.exit(1)

def run_mission_step(args: list, stage: str):
    """Executes a mission stage with process isolation and return-code enforcement."""
    cmd_preview = " ".join(map(str, args))
    print(f"\n[ORCHESTRATOR - {stage}] {cmd_preview}")
    
    result = subprocess.run(args, capture_output=False, check=False)
    
    if result.returncode != 0:
        print(f"[L6 FAILURE] Stage {stage} failed with code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    root = Path(__file__).parent.resolve()
    python_exe = sys.executable 
    
    # [CONSTITUTION RULE 7] MANDATORY NEURAL LINK CHECK
    env_path = root.parent / ".env"
    if not env_path.exists():
        print(f"\n[!] [PHYSICS FAILURE] Neural Link Missing: {env_path}")
        print("    Stop. Do not attempt mission without valid .env")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"[MISSION CONTROL] INITIATING ETERNAL SOVEREIGNTY CIRCUIT")
    print(f"Neural Link: ACTIVE | Target: {root.parent.name}")
    print(f"{'='*60}")
    
    # Load environment for global flags
    is_dry_run = os.getenv("MISSION_DRY_RUN", "False").lower() == "true"
    if is_dry_run: print("[!] MODE: DRY RUN (Diagnostics only)")

    # Phase 1: High-level diagnosis (The Supreme Court)
    run_mission_step([python_exe, str(root / 'sovereign_auditor_v3.py')], "DIAGNOSIS")

    # Phase 2: Deep surgical enforcement (The Surgeon)
    if not is_dry_run:
        run_mission_step([python_exe, str(root / 'canon_validator_agentic_v2.py'), "--target", "agentic_core"], "SURGERY")
    else:
        print("\n[SKIP] Stage SURGERY bypassed in Dry Run.")

    # Phase 3: Final verification (The Seal)
    run_mission_step([python_exe, str(root / 'sovereign_auditor_v3.py')], "SEALING")

    print(f"\n{'='*60}\n[CIRCUIT COMPLETE] PERFECTION SEALED AT 100%\n{'='*60}")
