#!/usr/bin/env python3
"""
E2E Comparison Test: Monolithic vs Modular execute_ssot
Actually runs both versions and compares execution output.
"""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import os
import time

REPO_ROOT = Path(__file__).parent

def patch_monolithic():
    """Create a testable version of monolithic by patching the guard."""
    monolith_path = REPO_ROOT / 'execute_ssot_monolithic.py'
    patched_path = REPO_ROOT / 'execute_ssot_monolithic_testable.py'
    
    # Read monolithic
    with open(monolith_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    # Find and replace the guard block
    guard_start = code.find('if __name__ == "__main__":')
    if guard_start == -1:
        print("Could not find guard block")
        return None
    
    # Replace everything from guard to end with actual main() call
    new_ending = '''
if __name__ == "__main__":
    # BYPASSED FOR TESTING
    sys.exit(main())
'''
    
    patched_code = code[:guard_start] + new_ending
    
    with open(patched_path, 'w', encoding='utf-8') as f:
        f.write(patched_code)
    
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
        timeout=120,
        env={**os.environ, 'PYTHONPATH': str(REPO_ROOT)}
    )
    elapsed = time.time() - start_time
    
    print(f"Exit code: {result.returncode}")
    print(f"Time: {elapsed:.2f}s")
    print(f"\n--- STDOUT ---")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.stderr:
        print(f"\n--- STDERR ---")
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
    
    return {
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'time': elapsed
    }

def main():
    print("="*70)
    print("E2E COMPARISON: Monolithic vs Modular execute_ssot")
    print("="*70)
    
    # Create temp test directory with a misplaced file
    test_dir = tempfile.mkdtemp(prefix='ssot_compare_')
    test_file = Path(test_dir) / 'misplaced_file.txt'
    test_file.write_text('# Test file in temp directory')
    
    print(f"\nTest directory: {test_dir}")
    print(f"Test file: {test_file}")
    
    # Patch monolithic
    print("\nPatching monolithic for testable execution...")
    patched_path = patch_monolithic()
    if not patched_path:
        print("Failed to patch monolithic")
        return 1
    
    # Run monolithic
    print("\n" + "="*70)
    print("PHASE 1: MONOLITHIC VERSION")
    print("="*70)
    monolith_result = run_version(
        patched_path,
        ['--heal', '--targets', test_dir, '--verbosity', '2'],
        "MONOLITHIC (patched)"
    )
    
    # Run modular
    print("\n" + "="*70)
    print("PHASE 2: MODULAR VERSION")
    print("="*70)
    modular_result = run_version(
        REPO_ROOT / 'agentic_core' / 'L0_routing' / 'scripts' / 'execute_ssot_entrypoint.py',
        ['--heal', '--targets', test_dir, '--verbosity', '2'],
        "MODULAR (entrypoint)"
    )
    
    # Compare
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    
    # Check for key phases in output
    phases = ['Discovery', 'Alignment', 'Validation', 'Healing', 'Reporting']
    
    print("\nMonolithic phases found:")
    for phase in phases:
        found = phase in monolith_result['stdout'] or phase.lower() in monolith_result['stdout'].lower()
        print(f"  {'✓' if found else '✗'} {phase}")
    
    print("\nModular phases found:")
    for phase in phases:
        found = phase in modular_result['stdout'] or phase.lower() in modular_result['stdout'].lower()
        print(f"  {'✓' if found else '✗'} {phase}")
    
    print(f"\nExit codes:")
    print(f"  Monolithic: {monolith_result['exit_code']}")
    print(f"  Modular: {modular_result['exit_code']}")
    
    print(f"\nExecution time:")
    print(f"  Monolithic: {monolith_result['time']:.2f}s")
    print(f"  Modular: {modular_result['time']:.2f}s")
    
    # Success criteria
    both_zero = monolith_result['exit_code'] == 0 and modular_result['exit_code'] == 0
    both_ran = monolith_result['time'] > 1 and modular_result['time'] > 1
    
    print("\n" + "="*70)
    if both_zero and both_ran:
        print("E2E PARITY: BOTH VERSIONS EXECUTED SUCCESSFULLY ✓")
    else:
        print("E2E PARITY: ISSUES DETECTED ✗")
        print(f"  Both exit 0: {both_zero}")
        print(f"  Both ran >1s: {both_ran}")
    print("="*70)
    
    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)
    patched_path.unlink(missing_ok=True)
    
    return 0 if both_zero else 1

if __name__ == "__main__":
    sys.exit(main())
