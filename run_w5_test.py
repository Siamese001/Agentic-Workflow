#!/usr/bin/env python3
"""Run W5 narrow test and report results."""
import subprocess
import sys

# Run narrow test
result = subprocess.run(
    [sys.executable, '-m', 'pytest',
     'tests/_apps_contract/test_c0_gate_enforcement.py::test_actual_fec_from_c0_retrieve_has_gate_verdicts_or_explicit_non_passing',
     'tests/_apps_contract/test_apps_rg_c0_grounding_gate.py::test_grounding_required_true_allows_c0_file_only',
     '-v', '--tb=short'],
    capture_output=True,
    text=True,
    timeout=60
)

print("=== NARROW TEST RESULT ===")
print(result.stdout)
if result.stderr:
    print("=== STDERR ===")
    print(result.stderr)
print(f"=== RETURN CODE: {result.returncode} ===")

# Save to file
with open('artifacts/w5_narrow_result.txt', 'w') as f:
    f.write(result.stdout)
    f.write(result.stderr)
    f.write(f"\nReturn code: {result.returncode}\n")
