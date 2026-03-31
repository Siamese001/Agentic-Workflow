"""
Phase 10C-11-12 Consolidated Evidence Runner

Generates consolidated evidence for:
- Phase 10C: Phase 09-10 Evidence Canonicalization
- Phase 11: apps_* Refactor Contract Alignment
- Phase 12: CI Ordering + Hard-Fail Wiring

Uses Evidence Contract v2 helper for scope isolation and self-verification.
All command outputs are stripped of ANSI escape sequences before embedding.
Runner hard-fails if any required command exits non-zero.
"""
import re
import sys
from pathlib import Path

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent))
from evidence_contract_v2 import EvidenceContractV2

from agentic_core.L5_safety.config.structure_blueprint.ssot import DOCS_REPORTS_PLANS

_ANSI_RE = re.compile('\\x1b\\[[0-9;]*[mABCDEFGHJKSTfhilmnprsu]')

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences and replace remaining non-ASCII with '?'."""
    text = _ANSI_RE.sub('', text)
    return ''.join(c if ord(c) < 128 else '?' for c in text)

def main():
    """Generate Phases 10C-11-12 consolidated evidence using Contract v2."""
    args = EvidenceContractV2.parse_args('Generate Phases 10C-11-12 consolidated evidence')
    code_commit = args.code_commit
    evidence_commit = args.evidence_commit
    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / 'docs' / REPORTS_DIR / 'plans' / 'phase_10c_11_12_consolidated.md'
    print(f'Generating Phases 10C-11-12 consolidated evidence: {evidence_file}')
    print(f'CODE_COMMIT: {code_commit}')
    if evidence_commit:
        print(f'EVIDENCE_COMMIT: {evidence_commit}')
    allowed_prefixes = {'apps_shared/', 'apps_lic/', 'apps_rg/', 'agentic_core/', 'ops_scripts/', 'tools/evidence/', 'tests/', 'docs/reports/plans/', '.github/workflows/', 'pytest.ini', 'docs/rules/'}
    contract = EvidenceContractV2(repo_root, allowed_prefixes)
    require_evidence_commit = evidence_commit is not None
    contract.validate_evidence_contract_structure(code_commit, evidence_commit, require_evidence_commit)
    evidence_lines = []
    evidence_lines.append('# Phases 10C-11-12: Evidence Canonicalization + Apps Boundary + CI Hardening (Consolidated)')
    evidence_lines.append('')
    evidence_lines.append('## Scope')
    evidence_lines.append('Phase 10C: Phase 09-10 Evidence Canonicalization (single-source-of-truth)')
    evidence_lines.append('Phase 11: apps_* Refactor Contract Alignment (minimal, enforcement-first)')
    evidence_lines.append('Phase 12: CI Ordering + Hard-Fail Wiring (repo-wide, deterministic)')
    evidence_lines.append('')
    inspected = ['ops_scripts/ci/check_evidence_contract_v2.py', 'ops_scripts/ci/check_tooling_apps_boundary.py', 'ops_scripts/ci/run_contract_gates.py', 'tests/unit_min_deps/test_tooling_apps_boundary.py', 'tests/unit_min_deps/test_contract_gates.py', 'tools/evidence/phase_10c_11_12_consolidated_evidence_runner.py', '.github/workflows/spine-determinism-guard.yml']
    sections = contract.build_evidence_sections(code_commit, evidence_commit, inspected)
    evidence_lines.extend(contract.format_evidence_sections(sections))
    commands = [([sys.executable, '-m', 'pytest', '-q', '--color=no'], 'Full Test Suite'), ([sys.executable, 'ops_scripts/ci/check_evidence_contract_v2.py', '--paths', DOCS_REPORTS_PLANS], 'Evidence Contract v2 Checker'), ([sys.executable, 'ops_scripts/ci/check_tooling_apps_boundary.py'], 'Tooling/Apps Boundary Guard'), ([sys.executable, 'ops_scripts/ci/run_contract_gates.py'], 'Contract Gates Runner')]
    failed_commands = []
    for cmd, title in commands:
        evidence_lines.append(f'## {title}')
        evidence_lines.append('```')
        evidence_lines.append(f"$ {' '.join(cmd)}")
        rc, out, err = contract.run_cmd(cmd)
        out_clean = strip_ansi(out)
        err_clean = strip_ansi(err)
        evidence_lines.append(out_clean)
        if err_clean.strip():
            evidence_lines.append(f'STDERR: {err_clean}')
        if rc != 0:
            evidence_lines.append(f'EXIT CODE: {rc}')
            failed_commands.append((title, rc))
        evidence_lines.append('```')
        evidence_lines.append('')
    if failed_commands:
        print('ERROR: The following required commands failed:')
        for title, rc in failed_commands:
            print(f'  - {title}: exit {rc}')
        sys.exit(1)
    evidence_content = '\n'.join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding='utf-8', newline='\n')
    content_start = evidence_file.read_text(encoding='utf-8')[:200]
    if content_start.strip().startswith('#!/usr/bin/env python') or 'def main()' in content_start[:200]:
        print('ERROR: Evidence file appears to contain Python code instead of markdown')
        print('This indicates the runner content was written to the evidence file.')
        sys.exit(1)
    print(f'Evidence generated successfully: {evidence_file}')
    print(f'CODE_COMMIT: {code_commit}')
    print(f"EVIDENCE_COMMIT: {sections['EVIDENCE_COMMIT']}")
    print(f'Current HEAD: {contract.get_current_head()}')
    if not evidence_commit:
        print('\nTo complete the evidence contract:')
        print('1. Commit this evidence file')
        print('2. Re-run with --evidence-commit <new_commit_hash>')
        print('3. The runner will update the sealed evidence file')
if __name__ == '__main__':
    main()
