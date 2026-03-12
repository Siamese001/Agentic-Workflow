"""
Phase 2 Assembly Stage Evidence Generator
Python-only evidence capture for deterministic Assembly Stage implementation.
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

def main():
    """Generate Phase 2 Assembly Stage evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / 'docs' / REPORTS_DIR / 'plans' / 'phase2_assembly_stage_evidence.md'
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    print(f'Generating Phase 2 evidence at: {evidence_file}')
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
    print('Running assembly stage tests...')
    sections.append('# Assembly Stage Tests\n')
    sections.append('```')
    sections.append(run_command([sys.executable, '-m', 'pytest', '-q', 'tests/unit/L0_routing/test_assembly_stage.py', '-m', 'unit'], repo_root))
    sections.append('```\n\n')
    print('Running all L0_routing tests...')
    sections.append('# All L0 Routing Tests\n')
    sections.append('```')
    sections.append(run_command([sys.executable, '-m', 'pytest', '-q', 'tests/unit/L0_routing', '-m', 'unit'], repo_root))
    sections.append('```\n\n')
    print('Scanning for wall-clock tokens...')
    assembly_file = repo_root / AGENTIC_CORE_DIR / 'L0_routing' / 'engines' / 'assembly_stage.py'
    forbidden_tokens = ['datetime.now', 'datetime.utcnow', 'time.time', 'perf_counter', 'monotonic', 'pendulum', 'arrow.']
    sections.append('# Wall-Clock Token Scan\n')
    sections.append('```')
    content = assembly_file.read_text(encoding='utf-8')
    found_tokens = []
    for token in forbidden_tokens:
        if token in content:
            found_tokens.append(token)
    if found_tokens:
        sections.append(f'FORBIDDEN TOKENS FOUND: {found_tokens}')
    else:
        sections.append('No forbidden wall-clock tokens found')
    sections.append('```\n\n')
    print('Collecting git show --stat...')
    sections.append('# Git Show --stat\n')
    sections.append('```')
    sections.append(run_command(['git', 'show', '--stat'], repo_root))
    sections.append('```\n\n')
    print(f'Writing evidence to {evidence_file}...')
    evidence_content = ''.join(sections)
    evidence_file.write_text(evidence_content, encoding='utf-8')
    print('Phase 2 Assembly Stage evidence generation complete!')
    return 0
if __name__ == '__main__':
    sys.exit(main())
