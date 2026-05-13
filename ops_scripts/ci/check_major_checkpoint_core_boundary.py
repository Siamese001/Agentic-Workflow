"""Major Checkpoint Core Leakage Validator

Runs agentic_core leakage detection at every major checkpoint:
- Before/after each wave completion
- Before commit
- Before merge to main
- After any agentic_core modification

Ensures zero apps_* leakage into core at all critical points.

Usage:
  python check_major_checkpoint_core_boundary.py --checkpoint <name> [--wave <W#>]

Checkpoints:
  pre-wave        Before starting a wave
  post-wave       After completing a wave
  pre-commit      Before git commit
  pre-merge       Before merge to main
  post-core-edit  After any agentic_core modification
  full-suite      Run all core boundary checks

Exit codes:
  0 = All checks passed
  1 = Leakage detected — BLOCK
  2 = Tool error
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent.parent
CHECKPOINT_LOG = REPO_ROOT / "artifacts" / "ci" / "checkpoint_core_boundary_log.jsonl"


def log_checkpoint(checkpoint_name: str, wave: str | None, result: dict[str, Any]) -> None:
    """Log checkpoint result for audit trail."""
    CHECKPOINT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checkpoint": checkpoint_name,
        "wave": wave,
        "result": result,
    }
    
    with open(CHECKPOINT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def run_core_leakage_gate() -> dict[str, Any]:
    """Run the core leakage detection gate."""
    gate_script = Path(__file__).parent / "check_agentic_core_leakage.py"
    
    try:
        # Always fail-closed at checkpoints
        env = os.environ.copy()
        env["CORE_LEAKAGE_GATE_FAIL_CLOSED"] = "1"
        
        result = subprocess.run(
            [sys.executable, str(gate_script)],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "passed": result.returncode == 0,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "exit_code": 2,
            "error": "Timeout after 60s",
            "passed": False,
        }
    except Exception as e:
        return {
            "exit_code": 2,
            "error": str(e),
            "passed": False,
        }


def check_git_status() -> dict[str, Any]:
    """Check if there are agentic_core changes staged."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "agentic_core/"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30,
        )
        
        changed_files = [f for f in result.stdout.strip().split("\n") if f]
        
        return {
            "has_core_changes": len(changed_files) > 0,
            "changed_files": changed_files,
        }
        
    except Exception as e:
        return {
            "has_core_changes": False,
            "error": str(e),
        }


def checkpoint_pre_wave(wave: str | None) -> dict[str, Any]:
    """Pre-wave checkpoint: Verify core is clean before starting work."""
    print(f"=" * 70)
    print(f"CHECKPOINT: pre-wave {wave or 'unknown'}")
    print(f"=" * 70)
    print()
    
    # Check core leakage
    leakage_result = run_core_leakage_gate()
    
    if not leakage_result["passed"]:
        print(f"[BLOCK] Core leakage detected — cannot start {wave}")
        print(f"Fix core boundary violations before proceeding.")
        return {
            "status": "blocked",
            "reason": "core_leakage",
            "leakage_result": leakage_result,
        }
    
    # Check git status
    git_status = check_git_status()
    
    if git_status.get("has_core_changes"):
        print(f"[WARN] Staged agentic_core changes detected:")
        for f in git_status["changed_files"]:
            print(f"  - {f}")
        print()
        print(f"Ensure these changes do not introduce apps_* leakage.")
    
    print(f"[PASS] Pre-wave checkpoint passed — {wave} may proceed")
    
    return {
        "status": "passed",
        "leakage_result": leakage_result,
        "git_status": git_status,
    }


def checkpoint_post_wave(wave: str | None) -> dict[str, Any]:
    """Post-wave checkpoint: Verify no leakage introduced during wave."""
    print(f"=" * 70)
    print(f"CHECKPOINT: post-wave {wave or 'unknown'}")
    print(f"=" * 70)
    print()
    
    # Check core leakage
    leakage_result = run_core_leakage_gate()
    
    if not leakage_result["passed"]:
        print(f"[BLOCK] Core leakage detected after {wave}")
        print(f"Wave introduced apps_* code into agentic_core — REVERT REQUIRED")
        return {
            "status": "blocked",
            "reason": "core_leakage_introduced",
            "leakage_result": leakage_result,
        }
    
    # Check for any core modifications during this wave
    git_status = check_git_status()
    
    if git_status.get("has_core_changes"):
        print(f"[INFO] agentic_core files modified during {wave}:")
        for f in git_status["changed_files"]:
            print(f"  - {f}")
        print()
        print(f"[VERIFY] No apps_* leakage in modified files — PASSED")
    
    print(f"[PASS] Post-wave checkpoint passed — {wave} complete, core boundary intact")
    
    return {
        "status": "passed",
        "leakage_result": leakage_result,
        "git_status": git_status,
    }


def checkpoint_pre_commit() -> dict[str, Any]:
    """Pre-commit checkpoint: Block commit if core leakage detected."""
    print(f"=" * 70)
    print(f"CHECKPOINT: pre-commit")
    print(f"=" * 70)
    print()
    
    # Check for core changes in staging
    git_status = check_git_status()
    
    if not git_status.get("has_core_changes"):
        print(f"[PASS] No agentic_core changes staged — commit allowed")
        return {
            "status": "passed",
            "reason": "no_core_changes",
        }
    
    print(f"[INFO] agentic_core changes detected in staging:")
    for f in git_status["changed_files"]:
        print(f"  - {f}")
    print()
    
    # Run leakage check
    leakage_result = run_core_leakage_gate()
    
    if not leakage_result["passed"]:
        print(f"[BLOCK] COMMIT BLOCKED: Core leakage detected")
        print()
        print(f"Fix the following before committing:")
        print(leakage_result.get("stdout", "")[-1500:])
        print()
        print(f"Commands to fix:")
        print(f"  1. Edit files to remove apps_* references from agentic_core")
        print(f"  2. git add <fixed-files>")
        print(f"  3. Re-run this checkpoint")
        return {
            "status": "blocked",
            "reason": "core_leakage_in_staging",
            "leakage_result": leakage_result,
            "git_status": git_status,
        }
    
    print(f"[PASS] Core boundary intact — commit allowed")
    
    return {
        "status": "passed",
        "leakage_result": leakage_result,
        "git_status": git_status,
    }


def checkpoint_pre_merge() -> dict[str, Any]:
    """Pre-merge checkpoint: Comprehensive check before merge to main."""
    print(f"=" * 70)
    print(f"CHECKPOINT: pre-merge")
    print(f"=" * 70)
    print()
    
    # Full leakage scan
    leakage_result = run_core_leakage_gate()
    
    if not leakage_result["passed"]:
        print(f"[BLOCK] MERGE BLOCKED: Core leakage detected")
        print(f"Cannot merge to main with apps_* code in agentic_core")
        return {
            "status": "blocked",
            "reason": "core_leakage",
            "leakage_result": leakage_result,
        }
    
    # Check for uncommitted core changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "agentic_core/"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=30,
        )
        
        uncommitted = [l for l in result.stdout.strip().split("\n") if l]
        
        if uncommitted:
            print(f"[WARN] Uncommitted agentic_core changes:")
            for line in uncommitted:
                print(f"  {line}")
            print()
            print(f"[BLOCK] Commit or stash before merge")
            return {
                "status": "blocked",
                "reason": "uncommitted_core_changes",
                "uncommitted_files": uncommitted,
            }
            
    except Exception as e:
        print(f"[WARN] Could not check git status: {e}")
    
    print(f"[PASS] Pre-merge checkpoint passed — merge to main allowed")
    
    return {
        "status": "passed",
        "leakage_result": leakage_result,
    }


def checkpoint_post_core_edit() -> dict[str, Any]:
    """Post-core-edit checkpoint: Immediate check after any agentic_core modification."""
    print(f"=" * 70)
    print(f"CHECKPOINT: post-core-edit")
    print(f"=" * 70)
    print()
    
    print(f"[INFO] Running immediate leakage check after agentic_core modification...")
    
    leakage_result = run_core_leakage_gate()
    
    if not leakage_result["passed"]:
        print(f"[ALERT] Core leakage introduced!")
        print()
        print(f"Immediate action required:")
        print(f"  git checkout -- agentic_core/  # Revert if unintentional")
        print(f"  # OR fix the leakage")
        print()
        print(leakage_result.get("stdout", "")[-1500:])
        
        return {
            "status": "alert",
            "reason": "leakage_introduced",
            "requires_action": True,
            "leakage_result": leakage_result,
        }
    
    print(f"[PASS] Core edit checkpoint passed — no leakage detected")
    
    return {
        "status": "passed",
        "leakage_result": leakage_result,
    }


def checkpoint_full_suite() -> dict[str, Any]:
    """Full checkpoint suite — run all checks."""
    print(f"=" * 70)
    print(f"CHECKPOINT: full-suite")
    print(f"=" * 70)
    print()
    
    results = {}
    all_passed = True
    
    for name, func in [
        ("core-leakage", run_core_leakage_gate),
        ("pre-commit", checkpoint_pre_commit),
    ]:
        print(f"Running: {name}")
        print("-" * 40)
        result = func()
        results[name] = result
        if not result.get("status", "").startswith("pass"):
            all_passed = False
        print()
    
    summary = {
        "status": "passed" if all_passed else "blocked",
        "checks": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if all_passed:
        print(f"[PASS] Full suite passed")
    else:
        print(f"[FAIL] Full suite failed — see details above")
    
    return summary


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Major Checkpoint Core Boundary Validator"
    )
    parser.add_argument(
        "--checkpoint", "-c",
        required=True,
        choices=["pre-wave", "post-wave", "pre-commit", "pre-merge", "post-core-edit", "full-suite"],
        help="Checkpoint to run"
    )
    parser.add_argument(
        "--wave", "-w",
        help="Wave identifier (e.g., W1, W2)"
    )
    
    args = parser.parse_args()
    
    # Run checkpoint
    checkpoint_map = {
        "pre-wave": lambda: checkpoint_pre_wave(args.wave),
        "post-wave": lambda: checkpoint_post_wave(args.wave),
        "pre-commit": checkpoint_pre_commit,
        "pre-merge": checkpoint_pre_merge,
        "post-core-edit": checkpoint_post_core_edit,
        "full-suite": checkpoint_full_suite,
    }
    
    result = checkpoint_map[args.checkpoint]()
    
    # Log result
    log_checkpoint(args.checkpoint, args.wave, result)
    
    # Determine exit code
    status = result.get("status", "unknown")
    
    if status in ("blocked", "alert"):
        return 1
    elif status == "error":
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
