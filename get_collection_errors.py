#!/usr/bin/env python3
"""Extract collection errors from pytest run."""
import subprocess
import re
from collections import defaultdict

print("Running pytest to collect errors...")
result = subprocess.run(
    [
        'python', '-m', 'pytest',
        'tests/unit', 'tests/governance', 'tests/system_learning',
        'tests/ci', 'tests/misc', 'tests/performance', 'tests/sovereign_hardening',
        '--ignore=tests/guardian', '--ignore=tests/e2e', '--ignore=tests/architecture',
        '--collect-only', '-q'
    ],
    capture_output=True,
    text=True,
    timeout=120
)

output = result.stdout + result.stderr
lines = output.split('\n')

# Find collection errors
errors = []
current_error = None
error_lines = []

for line in lines:
    if 'ERROR collecting' in line:
        if current_error:
            errors.append({
                'file': current_error,
                'details': '\n'.join(error_lines)
            })
        # Extract file path
        match = re.search(r'ERROR collecting (.+?)(?:\s|$)', line)
        if match:
            current_error = match.group(1)
            error_lines = []
    elif current_error and line.strip():
        if not line.startswith('='):
            error_lines.append(line.strip())
        else:
            errors.append({
                'file': current_error,
                'details': '\n'.join(error_lines)
            })
            current_error = None
            error_lines = []

if current_error:
    errors.append({
        'file': current_error,
        'details': '\n'.join(error_lines)
    })

print(f"\nTotal collection errors: {len(errors)}\n")

# Categorize errors
error_types = defaultdict(list)
for err in errors:
    details = err['details']
    if 'NameError' in details:
        error_types['NameError'].append(err)
    elif 'ImportError' in details or 'ModuleNotFoundError' in details:
        error_types['ImportError'].append(err)
    elif 'AttributeError' in details:
        error_types['AttributeError'].append(err)
    elif 'SyntaxError' in details:
        error_types['SyntaxError'].append(err)
    else:
        error_types['Other'].append(err)

print("Error Type Breakdown:")
for error_type, errs in sorted(error_types.items(), key=lambda x: -len(x[1])):
    print(f"  {error_type}: {len(errs)}")

print("\n" + "="*80)
print("DETAILED ERRORS (First 20)")
print("="*80)

for i, err in enumerate(errors[:20], 1):
    print(f"\n{i}. {err['file']}")
    print(f"   {err['details'][:300]}")
    if len(err['details']) > 300:
        print("   ...")
