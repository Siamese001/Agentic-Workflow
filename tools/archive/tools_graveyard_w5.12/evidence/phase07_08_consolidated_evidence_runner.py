"""
Phase 7-8 Consolidated Evidence Runner

Generates consolidated evidence for:
- Phase 7: Evidence Contract v2: Scope Isolation + Self-Verification
- Phase 8: CI Enforcement: Evidence Contract Guardrail

Uses Evidence Contract v2 helper for scope isolation and self-verification.
"""
import sys
from pathlib import Path

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent))
from evidence_contract_v2 import EvidenceContractV2

from agentic_core.L5_safety.config.structure_blueprint.ssot import DOCS_REPORTS_PLANS


def main():
    """Generate Phases 7-8 consolidated evidence using Contract v2."""
    args = EvidenceContractV2.parse_args('Generate Phases 7-8 consolidated evidence')
    code_commit = args.code_commit
    evidence_commit = args.evidence_commit
    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / 'docs' / REPORTS_DIR / 'plans' / 'phase_07_08_consolidated.md'
    print(f'Generating Phases 7-8 consolidated evidence: {evidence_file}')
    print(f'CODE_COMMIT: {code_commit}')
    if evidence_commit:
        print(f'EVIDENCE_COMMIT: {evidence_commit}')
    allowed_prefixes = {'apps_shared/', 'apps_lic/', 'apps_rg/', 'agentic_core/', 'ops_scripts/', 'tools/evidence/', 'tests/', 'docs/reports/plans/', '.github/workflows/', 'pytest.ini', 'docs/rules/'}
    contract = EvidenceContractV2(repo_root, allowed_prefixes)
    require_evidence_commit = evidence_commit is not None
    contract.validate_evidence_contract_structure(code_commit, evidence_commit, require_evidence_commit)
    evidence_lines = []
    evidence_lines.append('# Phases 7-8: Evidence Contract v2 + CI Enforcement (Consolidated)')
    evidence_lines.append('')
    evidence_lines.append('## Scope')
    evidence_lines.append('Phase 7: Evidence Contract v2: Scope Isolation + Self-Verification')
    evidence_lines.append('Phase 8: CI Enforcement: Evidence Contract Guardrail')
    evidence_lines.append('')
    inspected = ['tools/evidence/evidence_contract_v2.py', 'tools/evidence/phase05_06_consolidated_evidence_runner.py', 'tools/evidence/phase07_08_consolidated_evidence_runner.py', 'tests/unit_min_deps/test_evidence_contract_v2.py', 'ops_scripts/ci/check_evidence_contract_v2.py', '.github/workflows/spine-determinism-guard.yml']
    sections = contract.build_evidence_sections(code_commit, evidence_commit, inspected)
    evidence_lines.extend(contract.format_evidence_sections(sections))
    commands = [([sys.executable, '-m', 'pytest', '-q', 'tests/unit_min_deps/test_evidence_contract_v2.py'], 'Evidence Contract v2 Unit Tests'), ([sys.executable, '-m', 'pytest', '-q'], 'Full Test Suite'), ([sys.executable, 'ops_scripts/ci/check_evidence_contract_v2.py', '--paths', DOCS_REPORTS_PLANS], 'Evidence Contract v2 Checker')]
    for cmd, title in commands:
        evidence_lines.append(f'## {title}')
        evidence_lines.append('```')
        evidence_lines.append(f"$ {' '.join(cmd)}")
        rc, out, err = contract.run_cmd(cmd)
        evidence_lines.append(out)
        if err:
            evidence_lines.append(f'STDERR: {err}')
        if rc != 0:
            evidence_lines.append(f'EXIT CODE: {rc}')
        evidence_lines.append('```')
        evidence_lines.append('')
    evidence_lines.append('## INSPECTED_FILE_CONTENTS')
    evidence_lines.append('')
    for filepath in sections['INSPECTED_FILES']:
        full_path = repo_root / filepath
        evidence_lines.append(f'### {filepath}')
        evidence_lines.append('```')
        content = EvidenceContractV2.read_file_content(full_path)
        evidence_lines.append(content)
        evidence_lines.append('```')
        evidence_lines.append('')
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
