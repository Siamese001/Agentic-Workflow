"""
Phase 7 L6 Vigilance Dispatcher Evidence Generator
Python-only evidence capture for L6 observability modules.
"""
import subprocess
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def get_repo_root() -> Path:
    return get_validated_project_root()

def run_command(cmd: list[str], cwd: Path) -> str:
    """Run command and capture stdout+stderr."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    return result.stdout + result.stderr

def scan_forbidden_tokens(file_path: Path, forbidden_tokens: list[str]) -> list[str]:
    """Scan file for forbidden tokens."""
    try:
        content = file_path.read_text(encoding='utf-8')
        found = []
        for token in forbidden_tokens:
            if token in content:
                found.append(token)
        return found
    except FileNotFoundError:
        return []
    except UnicodeDecodeError:
        return []

def main():
    """Generate Phase 7 L6 Vigilance Dispatcher evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / 'docs' / REPORTS_DIR / 'plans' / 'phase7_l6_vigilance_dispatcher_evidence.md'
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    print(f'Generating Phase 7 evidence at: {evidence_file}')
    sections = []
    print('Collecting git HEAD...')
    sections.append('# Git HEAD\n')
    sections.append('```')
    sections.append(run_command(['git', 'rev-parse', 'HEAD'], repo_root).strip())
    sections.append('```\n\n')
    print('Collecting git status...')
    sections.append('# Git Status\n')
    sections.append('```')
    sections.append(run_command(['git', 'status', '--porcelain'], repo_root).strip())
    sections.append('```\n\n')
    print('Running vigilance dispatcher tests...')
    sections.append('# Vigilance Dispatcher Tests\n')
    sections.append('```')
    sections.append(run_command([sys.executable, '-m', 'pytest', '-q', 'tests/unit/L6_observability/test_vigilance_dispatcher.py', '-m', 'unit'], repo_root))
    sections.append('```\n\n')
    print('Running all L6 observability tests...')
    sections.append('# All L6 Observability Tests\n')
    sections.append('```')
    sections.append(run_command([sys.executable, '-m', 'pytest', '-q', 'tests/unit/L6_observability', '-m', 'unit'], repo_root))
    sections.append('```\n\n')
    print('Scanning for forbidden tokens...')
    dispatcher_file = repo_root / AGENTIC_CORE_DIR / 'L6_observability' / 'engines' / 'vigilance_dispatcher.py'
    wall_clock_tokens = ['datetime.now', 'datetime.utcnow', 'time.time', 'perf_counter', 'monotonic', 'pendulum', 'arrow.']
    forbidden_authority_tokens = ['agentic_core.L4_state', 'agentic_core.L2_execution', 'agentic_core.L5_safety']
    sections.append('# Wall-Clock Token Scan\n')
    sections.append('```')
    wall_clock_found = scan_forbidden_tokens(dispatcher_file, wall_clock_tokens)
    authority_found = scan_forbidden_tokens(dispatcher_file, forbidden_authority_tokens)
    if wall_clock_found:
        sections.append(f'WALL-CLOCK TOKENS FOUND: {wall_clock_found}')
    else:
        sections.append('No wall-clock tokens found')
    if authority_found:
        sections.append(f'FORBIDDEN AUTHORITY TOKENS FOUND: {authority_found}')
    else:
        sections.append('No forbidden L4/L2/L5 imports found')
    sections.append('```\n\n')
    print('Collecting git show --stat...')
    sections.append('# Git Show --stat\n')
    sections.append('```')
    sections.append(run_command(['git', 'show', '--stat'], repo_root))
    sections.append('```\n\n')
    print(f'Writing evidence to {evidence_file}...')
    evidence_content = ''.join(sections)
    evidence_file.write_text(evidence_content, encoding='utf-8')
    print('Phase 7 L6 Vigilance Dispatcher evidence generation complete!')
    return 0
if __name__ == '__main__':
    sys.exit(main())
