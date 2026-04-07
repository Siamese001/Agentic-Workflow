"""
Capture SSOT_cleanup evidence with strict subprocess discipline.
No shell=True, no PowerShell injection, pure Python subprocess.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def run_git_command(args: list[str]) -> tuple[int, str, str]:
    """Run git command with shell=False, capture stdout/stderr."""
    result = subprocess.run(['git'] + args, cwd=REPO_ROOT, capture_output=True, text=True, shell=False)
    return (result.returncode, result.stdout, result.stderr)

def run_precommit_command(args: list[str]) -> tuple[int, str, str]:
    """Run pre-commit command with shell=False, capture stdout/stderr."""
    result = subprocess.run(['pre-commit'] + args, cwd=REPO_ROOT, capture_output=True, text=True, shell=False)
    return (result.returncode, result.stdout, result.stderr)

def check_for_shell_injection(output: str) -> None:
    """Hard stop if output contains PowerShell markers."""
    if 'pwsh' in output.lower() or 'powershell' in output.lower():
        print('ERROR: PowerShell detected in output - shell injection risk', file=sys.stderr)
        sys.exit(1)

def main():
    print('=== Final Evidence Commit Capture ===\n')
    rc, stdout, stderr = run_git_command(['rev-parse', 'HEAD'])
    check_for_shell_injection(stdout + stderr)
    stdout.strip()
    print('[git rev-parse HEAD]')
    print(f'Exit code: {rc}')
    print(f'Output:\n{stdout}')
    if stderr:
        print(f'Stderr:\n{stderr}')
    rc, stdout, stderr = run_git_command(['log', '-1', '--oneline'])
    check_for_shell_injection(stdout + stderr)
    print('\n[git log -1 --oneline]')
    print(f'Exit code: {rc}')
    print(f'Output:\n{stdout}')
    if stderr:
        print(f'Stderr:\n{stderr}')
    rc, stdout, stderr = run_git_command(['show', '--name-only', '--stat', 'HEAD'])
    check_for_shell_injection(stdout + stderr)
    print('\n[git show --name-only --stat HEAD]')
    print(f'Exit code: {rc}')
    print(f'Output:\n{stdout}')
    if stderr:
        print(f'Stderr:\n{stderr}')
    rc, stdout, stderr = run_git_command(['show', 'HEAD', '--', 'docs/evidence/phase_SSOT_cleanup_remediation_dispatcher_docstrings.md'])
    check_for_shell_injection(stdout + stderr)
    print('\n[git show HEAD -- docs/evidence/phase_SSOT_cleanup_remediation_dispatcher_docstrings.md]')
    print(f'Exit code: {rc}')
    print(f'Output (first 50 lines):\n{chr(10).join(stdout.split(chr(10))[:50])}')
    if stderr:
        print(f'Stderr:\n{stderr}')
    rc, stdout, stderr = run_git_command(['status', '--porcelain'])
    check_for_shell_injection(stdout + stderr)
    print('\n[git status --porcelain]')
    print(f'Exit code: {rc}')
    print(f"Output:\n{(stdout if stdout else '(empty - clean working tree)')}")
    if stderr:
        print(f'Stderr:\n{stderr}')
    print('\n=== Wave 2: Pre-commit Provenance ===\n')
    rc, stdout, stderr = run_precommit_command(['--version'])
    check_for_shell_injection(stdout + stderr)
    print('[pre-commit --version]')
    print(f'Exit code: {rc}')
    print(f'Output:\n{stdout}')
    if stderr:
        print(f'Stderr:\n{stderr}')
    rc, stdout, stderr = run_precommit_command(['run', '--all-files'])
    check_for_shell_injection(stdout + stderr)
    print('\n[pre-commit run --all-files]')
    print(f'Exit code: {rc}')
    print(f'Output:\n{stdout}')
    if stderr:
        print(f'Stderr:\n{stderr}')
    rc, stdout, stderr = run_git_command(['status', '--porcelain'])
    check_for_shell_injection(stdout + stderr)
    print('\n[git status --porcelain (after pre-commit)]')
    print(f'Exit code: {rc}')
    print(f"Output:\n{(stdout if stdout else '(empty - clean working tree)')}")
    if stderr:
        print(f'Stderr:\n{stderr}')
    if stdout.strip():
        print('\n[Restoring modified files]')
        rc, stdout, stderr = run_git_command(['restore', '--worktree', '--staged', '.'])
        print(f'git restore exit code: {rc}')
        rc, stdout, stderr = run_git_command(['status', '--porcelain'])
        print('\n[git status --porcelain (after restore)]')
        print(f"Output:\n{(stdout if stdout else '(empty - clean working tree)')}")
    return 0
if __name__ == '__main__':
    sys.exit(main())
