#!/usr/bin/env python3
"""
Proper E2E Test: Run both monolithic and modular through full workflow
"""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import os
import time

REPO_ROOT = Path(__file__).parent

def patch_monolithic_properly():
    """Create patched monolithic that handles args correctly."""
    monolith_path = REPO_ROOT / 'execute_ssot_monolithic.py'
    patched_path = REPO_ROOT / 'execute_ssot_monolithic_fixed.py'
    
    with open(monolith_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    # Find the guard block at the end and replace with proper main() call
    guard_text = '''if __name__ == "__main__":
    print(
        "ERROR: Direct invocation of execute_ssot.py is not supported.\\nUse the entrypoint instead:\\n  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy\\n",
        file=sys.stderr,
    )
    raise SystemExit(2)'''
    
    new_ending = '''if __name__ == "__main__":
    # PATCHED FOR TESTING
    sys.exit(main())'''
    
    if guard_text in code:
        code = code.replace(guard_text, new_ending)
    else:
        # Try simpler replacement
        code = code.replace(
            'raise SystemExit(2)',
            'sys.exit(main())  # PATCHED'
        )
    
    with open(patched_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return patched_path

def run_version(script_path, args, version_name):
    """Run a version and capture output."""
    print(f"\n{'='*70}")
    print(f"Running {version_name}")
    print(f"{'='*70}")
    
    cmd = [sys.executable, str(script_path)] + args
    
    start_time = time.time()
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, 'PYTHONPATH': str(REPO_ROOT)}
    )
    elapsed = time.time() - start_time
    
    print(f"Exit code: {result.returncode}")
    print(f"Time: {elapsed:.2f}s")
    
    # Print last 3000 chars of stdout to see the full execution
    stdout_tail = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
    print(f"\n--- STDOUT (tail) ---")
    print(stdout_tail)
    
    if result.stderr:
        stderr_tail = result.stderr[-1500:] if len(result.stderr) > 1500 else result.stderr
        print(f"\n--- STDERR (tail) ---")
        print(stderr_tail)
    
    return {
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'time': elapsed
    }

def main():
    print("="*70)
    print("E2E WORKFLOW TEST: Monolithic vs Modular")
    print("="*70)
    
    # Create temp test directory
    test_dir = tempfile.mkdtemp(prefix='ssot_e2e_')
    test_file = Path(test_dir) / 'misplaced_file.txt'
    test_file.write_text('# Test file for E2E comparison')
    
    print(f"\nTest directory: {test_dir}")
    print(f"Test file: {test_file}")
    
    # Patch monolithic
    print("\nPatching monolithic...")
    patched_path = patch_monolithic_properly()
    if not patched_path:
        print("Failed to patch")
        return 1
    
    # Run monolithic
    print("\n" + "="*70)
    print("PHASE 1: MONOLITHIC")
    print("="*70)
    monolith_result = run_version(
        patched_path,
        ['--heal', '--targets', test_dir],
        "MONOLITHIC (fixed)"
    )
    
    # Run modular
    print("\n" + "="*70)
    print("PHASE 2: MODULAR")
    print("="*70)
    modular_result = run_version(
        REPO_ROOT / 'agentic_core' / 'L0_routing' / 'scripts' / 'execute_ssot_entrypoint.py',
        ['--heal', '--targets', test_dir],
        "MODULAR"
    )
    
    # Compare phases
    print("\n" + "="*70)
    print("WORKFLOW PHASE COMPARISON")
    print("="*70)
    
    phases = ['Discovery', 'Alignment', 'Validation', 'Healing', 'Reporting']
    
    print("\nMonolithic phases found:")
    for phase in phases:
        found = phase.lower() in monolith_result['stdout'].lower()
        print(f"  {'✓' if found else '✗'} {phase}")
    
    print("\nModular phases found:")
    for phase in phases:
        found = phase.lower() in modular_result['stdout'].lower()
        print(f"  {'✓' if found else '✗'} {phase}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Monolithic: {monolith_result['time']:.2f}s, exit={monolith_result['exit_code']}")
    print(f"Modular:    {modular_result['time']:.2f}s, exit={modular_result['exit_code']}")
    
    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)
    patched_path.unlink(missing_ok=True)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
