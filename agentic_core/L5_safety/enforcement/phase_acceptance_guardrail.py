"""
Phase Acceptance Enforcement Guard
==================================

Enforcement guard to prevent transgressions learned from Phase 2 closeout:
1. Testpaths contract synchronization violations
2. Failure to distinguish pre-existing vs new issues
3. Evidence capture protocol violations
"""

import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


class PhaseAcceptanceGuard:
    """Enforces Phase 2 closeout lessons learned."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def check_testpaths_contract_sync(self) -> None:
        """Rule 46: Testpaths contract must be synchronized with pytest.ini."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PhaseAcceptanceGuard.check_testpaths_contract_sync")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:PhaseAcceptanceGuard.check_testpaths_contract_sync".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        pytest_ini = self.repo_root / "pytest.ini"
        contract_test = self.repo_root / TESTS_DIR / "unit_min_deps" / "test_testpaths_contract.py"
        if not pytest_ini.exists():
            self.errors.append("pytest.ini not found")
            return
        if not contract_test.exists():
            self.errors.append(
                "testpaths contract test not found at tests/unit_min_deps/test_testpaths_contract.py"
            )
            return
        content = pytest_ini.read_text(encoding="utf-8")
        testpaths_match = re.search("^testpaths\\s*=\\s*\\n((?:\\s+.*\\n?)*)", content, re.MULTILINE)
        if not testpaths_match:
            self.errors.append("No testpaths section found in pytest.ini")
            return
        testpaths_lines = testpaths_match.group(1).strip().split("\n")
        actual_testpaths = set()
        for line in testpaths_lines:
            line = line.strip()
            if line and (not line.startswith("#")):
                actual_testpaths.add(line)
        contract_content = contract_test.read_text(encoding="utf-8")
        required_match = re.search("REQUIRED_TESTPATHS\\s*=\\s*{([^}]+)}", contract_content)
        if not required_match:
            self.errors.append("REQUIRED_TESTPATHS not found in contract test")
            return
        required_paths = set()
        for path in required_match.group(1).split(","):
            path = path.strip().strip("'\"")
            if path:
                required_paths.add(path)
        if actual_testpaths != required_paths:
            self.errors.append(
                f"Testpaths contract mismatch:\n  pytest.ini testpaths: {sorted(actual_testpaths)}\n  Contract REQUIRED_TESTPATHS: {sorted(required_paths)}\n  Missing in contract: {sorted(actual_testpaths - required_paths)}\n  Extra in contract: {sorted(required_paths - actual_testpaths)}"
            )

    def check_evidence_files_protocol(self) -> None:
        """Rule 48: Evidence files must contain raw, untruncated outputs."""
        evidence_dir = self.repo_root / "docs" / REPORTS_DIR / "governance"
        if not evidence_dir.exists():
            return
        for evidence_file in evidence_dir.glob("*evidence.md"):
            content = evidence_file.read_text(encoding="utf-8")
            test_blocks = re.findall("```bash\\npytest.*?\\n```", content, re.DOTALL)
            for block in test_blocks:
                if re.search("Full output truncated|lines were truncated", block, re.IGNORECASE):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} contains pytest output truncation"
                    )
                elif re.search("\\.\\.\\.(?!\\n.*```)", block) and "Exit code:" not in block:
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} contains possible pytest output truncation"
                    )
            for block in test_blocks:
                if "Exit code:" not in block and "passed" not in block and ("failed" not in block):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} missing exit code in pytest output block"
                    )
            if (
                "git status" in content
                and "clean working tree" not in content
                and ("nothing to commit" not in content)
            ):
                status_match = re.search("git status.*?\\n```(.*?)```", content, re.DOTALL)
                if status_match and "working tree clean" not in status_match.group(1):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} shows git status but may not prove clean state"
                    )

    def _is_allowed_truncation(self, content: str, pattern: str) -> bool:
        """Check if truncation is allowed in this context."""
        if pattern == "Full output truncated":
            return "==================== test session starts" in content
        if pattern == "\\.\\.\\.":
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "..." in line:
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 3)
                    context = "\n".join(lines[context_start:context_end])
                    if "```" not in context and "Output:" not in context:
                        return True
        return False

    def check_phase_evidence_completeness(self) -> None:
        """Rule 47: Phase evidence must distinguish pre-existing vs new issues."""
        evidence_dir = self.repo_root / "docs" / REPORTS_DIR / "governance"
        for evidence_file in evidence_dir.glob("phase*evidence.md"):
            content = evidence_file.read_text(encoding="utf-8")
            if "failed" in content.lower() and "git --no-pager show" not in content:
                self.warnings.append(
                    f"Evidence file {evidence_file.name} mentions failures but lacks git history analysis"
                )
            if "pytest -q" in content and "Exit code: 1" in content:
                if not re.search("pytest.*tests/governance/test_.*\\.py", content):
                    self.warnings.append(
                        f"Evidence file {evidence_file.name} shows pytest failure but no deterministic command set"
                    )
            if "pre-existing" not in content.lower() and "BLOCKED" in content:
                self.warnings.append(
                    f"Evidence file {evidence_file.name} marked as BLOCKED but lacks pre-existing analysis"
                )

    def validate(self) -> bool:
        """Run all validation checks."""
        self.errors.clear()
        self.warnings.clear()
        self.check_testpaths_contract_sync()
        self.check_evidence_files_protocol()
        self.check_phase_evidence_completeness()
        return len(self.errors) == 0

    def report(self) -> str:
        """Generate validation report."""
        report_lines = []
        if self.errors:
            report_lines.append("ERRORS:")
            for error in self.errors:
                report_lines.append(f"  - {error}")
        if self.warnings:
            report_lines.append("WARNINGS:")
            for warning in self.warnings:
                report_lines.append(f"  - {warning}")
        if not self.errors and (not self.warnings):
            report_lines.append("No enforcement violations detected.")
        return "\n".join(report_lines)


def main():
    """Run phase acceptance enforcement validation."""
    repo_root = Path(__file__).parent.parent.parent
    guard = PhaseAcceptanceGuard(repo_root)
    if guard.validate():
        print("✓ Phase acceptance enforcement validation passed")
        return 0
    else:
        print("✗ Phase acceptance enforcement validation failed")
        print(guard.report())
        return 1


if __name__ == "__main__":
    exit(main())
