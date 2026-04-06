"""Apply fixes until convergence."""
import subprocess
import sys


for i in range(1, 11):
    print(f'Pass {i}:')
    result = subprocess.run([sys.executable, 'ops_scripts/ci/_fix_hardcoded_ssot_literals.py', '--dry-run'], capture_output=True, text=True, cwd='.')
    if result.stdout:
        first_line = result.stdout.split('\n')[0]
        print(f'  {first_line}')
    else:
        print('  No output')
        break
    if '[DRY-RUN] 0 fixes' in result.stdout:
        print('  Converged - no more fixes')
        break
    result = subprocess.run([sys.executable, 'ops_scripts/ci/_fix_hardcoded_ssot_literals.py'], capture_output=True, text=True, cwd='.')
    if result.returncode != 0:
        print(f'  Error: {result.stderr}')
        break
    print('  Applied fixes')
