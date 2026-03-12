"""
Evidence Contract v2 Helper

Shared helper for consolidated evidence runners that enforces:
- Explicit CODE_COMMIT and EVIDENCE_COMMIT validation
- Hash-loop prevention
- Scope containment with allowed prefixes
- Semantic separation of file sections
- PowerShell detection and rejection
"""
import argparse
import subprocess
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class EvidenceContractV2:
    """Evidence Contract v2 helper for consolidated runners."""
    DEFAULT_ALLOWED_PREFIXES: set[str] = {'apps_shared/', 'apps_lic/', 'apps_rg/', 'agentic_core/', 'ops_scripts/', 'tools/evidence/', 'tests/', 'docs/reports/plans/', '.github/workflows/', 'pytest.ini', 'docs/rules/'}

    def __init__(self, repo_root: Path, allowed_prefixes: set[str] | None=None):
        """Initialize contract helper.

        Args:
            repo_root: Repository root path
            allowed_prefixes: Set of allowed path prefixes for scope containment
        """
        self.repo_root = repo_root
        self.allowed_prefixes = allowed_prefixes or self.DEFAULT_ALLOWED_PREFIXES

    def validate_commit_hash(self, commit_hash: str) -> None:
        """Validate that commit hash is 40-character hex."""
        if len(commit_hash) != 40:
            raise ValueError(f'Commit hash must be 40 characters: {commit_hash}')
        if not all((c in '0123456789abcdefABCDEF' for c in commit_hash)):
            raise ValueError(f'Commit hash must be hex: {commit_hash}')

    def run_cmd(self, args: list[str], cwd: Path | None=None) -> tuple[int, str, str]:
        """Execute command with PowerShell detection and return (rc, stdout, stderr)."""
        argv0_lower = str(args[0]).lower()
        if 'pwsh' in argv0_lower or 'powershell' in argv0_lower:
            raise ValueError(f"PowerShell usage detected in command: {' '.join(args)}")
        work_dir = cwd or self.repo_root
        result = subprocess.run(args, cwd=work_dir, capture_output=True, text=True, shell=False, encoding='utf-8', errors='replace')
        return (result.returncode, result.stdout, result.stderr)

    def get_current_head(self) -> str:
        """Get current HEAD commit hash."""
        rc, out, err = self.run_cmd(['git', 'rev-parse', 'HEAD'])
        if rc != 0:
            raise RuntimeError(f'git rev-parse failed: {err}')
        return out.strip()

    def validate_commit_exists(self, commit_hash: str) -> None:
        """Validate that commit exists in repository."""
        rc, out, err = self.run_cmd(['git', 'cat-file', '-e', commit_hash])
        if rc != 0:
            raise ValueError(f'Commit does not exist: {commit_hash}')

    def validate_hash_loop_prevention(self, code_commit: str) -> None:
        """Enforce CODE_COMMIT != current HEAD (hash-loop prevention)."""
        current_head = self.get_current_head()
        if code_commit == current_head:
            raise ValueError(f'CODE_COMMIT ({code_commit}) == current HEAD ({current_head}). This would create a hash loop. Use a commit from before the evidence changes.')

    def get_changed_files(self, commit_hash: str) -> list[str]:
        """Get list of changed files for a commit."""
        rc, out, err = self.run_cmd(['git', 'show', '--name-only', '--pretty=format:', commit_hash])
        if rc != 0:
            raise RuntimeError(f'git show failed for {commit_hash}: {err}')
        files = [f.strip() for f in out.strip().splitlines() if f.strip()]
        return files

    def validate_scope_containment(self, files: list[str], phase_name: str) -> None:
        """Validate that all changed files are within allowed prefixes."""
        violations = []
        for file_path in files:
            if not any((file_path.startswith(prefix) for prefix in self.allowed_prefixes)):
                violations.append(file_path)
        if violations:
            raise ValueError(f'Scope violation in {phase_name}: Files outside allowed prefixes detected:\n' + '\n'.join((f'  - {v}' for v in violations)) + f'\nAllowed prefixes: {sorted(self.allowed_prefixes)}')

    def validate_evidence_contract_structure(self, code_commit: str, evidence_commit: str | None=None, require_evidence_commit: bool=False) -> None:
        """Validate evidence contract structure and requirements."""
        self.validate_commit_hash(code_commit)
        self.validate_commit_exists(code_commit)
        if evidence_commit:
            self.validate_hash_loop_prevention(code_commit)
        if require_evidence_commit:
            if not evidence_commit:
                raise ValueError('EVIDENCE_COMMIT is required')
            self.validate_commit_hash(evidence_commit)
            self.validate_commit_exists(evidence_commit)

    def build_evidence_sections(self, code_commit: str, evidence_commit: str | None=None, inspected_files: list[str] | None=None) -> dict:
        """Build evidence contract sections."""
        files_changed_code = self.get_changed_files(code_commit)
        self.validate_scope_containment(files_changed_code, 'CODE_COMMIT')
        files_changed_evidence = []
        if evidence_commit:
            files_changed_evidence = self.get_changed_files(evidence_commit)
        if not inspected_files:
            inspected_files = []
        return {'CODE_COMMIT': code_commit, 'EVIDENCE_COMMIT': evidence_commit or 'PENDING', 'FILES_CHANGED_CODE': files_changed_code, 'FILES_CHANGED_EVIDENCE': files_changed_evidence, 'INSPECTED_FILES': inspected_files}

    def format_evidence_sections(self, sections: dict) -> list[str]:
        """Format evidence sections as markdown lines."""
        lines = []
        lines.append('## CODE_COMMIT')
        lines.append(sections['CODE_COMMIT'])
        lines.append('')
        lines.append('## EVIDENCE_COMMIT')
        lines.append(sections['EVIDENCE_COMMIT'])
        lines.append('')
        lines.append('## FILES_CHANGED_CODE')
        lines.append('```')
        for f in sections['FILES_CHANGED_CODE']:
            lines.append(f)
        lines.append('```')
        lines.append('')
        lines.append('## FILES_CHANGED_EVIDENCE')
        lines.append('```')
        if sections['FILES_CHANGED_EVIDENCE']:
            for f in sections['FILES_CHANGED_EVIDENCE']:
                lines.append(f)
        else:
            lines.append('PENDING (will be filled after commit)')
        lines.append('```')
        lines.append('')
        lines.append('## INSPECTED_FILES')
        lines.append('```')
        for f in sections['INSPECTED_FILES']:
            lines.append(f)
        lines.append('```')
        lines.append('')
        return lines

    @staticmethod
    def parse_args(description: str) -> argparse.Namespace:
        """Parse common evidence runner arguments."""
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('--code-commit', required=True, help='40-hex commit hash for CODE_COMMIT')
        parser.add_argument('--evidence-commit', help='40-hex commit hash for EVIDENCE_COMMIT (optional)')
        return parser.parse_args()

    @staticmethod
    def read_file_content(filepath: Path) -> str:
        """Read file content with error handling."""
        try:
            return filepath.read_text(encoding='utf-8')
        # guardian: allow-silent-swallow
        except Exception as e:
            return f'ERROR: Could not read {filepath}: {e}'
