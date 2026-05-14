#!/usr/bin/env python3
"""Run full W1-W5 test suite and report results."""
import subprocess
import sys

test_files = [
    'tests/_apps_contract/test_c0_gate_enforcement.py',
    'tests/_apps_contract/test_apps_rg_dispatch_fec_presence.py',
    'tests/_apps_contract/test_apps_rg_c0_grounding_gate.py',
    'tests/_apps_contract/test_c0_never_writes_l4_or_uwg.py',
    'tests/_apps_contract/test_w2_fact_vectors_foundation.py',
    'tests/_apps_contract/test_w3_briefing_bypass_gate.py',
    'tests/_apps_contract/test_w4_bounded_section_retrieval.py',
    'tests/_apps_contract/test_w5_metadata_filter_and_claim_checker.py',
    'tests/_apps_contract/test_w5_c0_metadata_filter_integration.py',
]

# Run full test suite
result = subprocess.run(
    [sys.executable, '-m', 'pytest'] + test_files + ['-v', '--tb=short'],
    capture_output=True,
    text=True,
    timeout=120
)

print("=== FULL W1-W5 TEST RESULT ===")
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
if result.stderr:
    print("=== STDERR ===")
    print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
print(f"=== RETURN CODE: {result.returncode} ===")

# Save to file
with open('artifacts/w5_full_result.txt', 'w') as f:
    f.write(result.stdout)
    f.write(result.stderr)
    f.write(f"\nReturn code: {result.returncode}\n")
