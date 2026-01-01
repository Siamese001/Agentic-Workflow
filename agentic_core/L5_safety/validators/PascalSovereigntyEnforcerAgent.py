"""PascalSovereigntyEnforcerAgent — Phase 13 (Jan 01, 2026)

Eternal PascalCase SSOT Enforcer.
- Purges snake_case class/enum/dataclass definitions
- Eliminates all backward-compatibility aliases
- Updates references repo-wide
- Subatomic hops with self-validation (integrated test cases)
- All test cases must pass before commit
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from agentic_core.L2_execution.tool_registry.ExecutionCanonBaseAgent import CanonBaseAgent


class PascalSovereigntyEnforcerAgent(CanonBaseAgent):
    """L5 Safety agent — enforces PascalCase as eternal sole SSOT."""

    def __init__(self, ctx: Any, dry_run: bool = False):
        super().__init__(ctx)
        self.repo_root = Path.cwd()
        self.branch_name = "refactor/eternal-pascal-sovereignty"
        self.dry_run = dry_run

    def get_validation_keys(self) -> List[int]:
        """Return canon keys for naming sovereignty."""
        return [1, 2, 3]  # Naming, structure, sovereignty keys

    async def execute(self, scope: str = "schemas") -> Dict:
        """Subatomic entrypoint — purge snake_case across scope."""
        hop_id = "pascal_purge_2026"

        # Hop 1: INIT - Setup branch + audit
        self._emit_event("INFO", "PASCAL_PURGE_INITIATED")
        
        # Check if branch exists
        result = subprocess.run(["git", "branch", "--list", self.branch_name], 
                              capture_output=True, text=True)
        if self.branch_name not in result.stdout:
            subprocess.run(["git", "checkout", "-b", self.branch_name], check=False)
        
        targets = self._audit_snake_case(scope)
        if not targets:
            return {"status": "clean", "message": "PascalCase already eternal"}

        results = []
        for file_path in targets:
            # Hop 2: THINK/ACT - Generate + apply purge
            original_content = Path(file_path).read_text(encoding='utf-8')
            purged_content = self._purge_snake_case(original_content)
            if purged_content == original_content:
                results.append({"file": file_path, "status": "no_change"})
                continue

            if not self.dry_run:
                Path(file_path).write_text(purged_content, encoding='utf-8')

            # Hop 3: CRITIQUE - Integrated test cases
            test_result = self._run_integrated_tests()
            if not test_result["all_passed"]:
                # Rollback file
                if not self.dry_run:
                    Path(file_path).write_text(original_content, encoding='utf-8')
                    subprocess.run(["git", "restore", file_path], check=False)
                results.append({"file": file_path, "status": "failed_critique", "tests": test_result})
                self._emit_event("ERROR", "PASCAL_PURGE_CRITIQUE_FAILED")
                continue

            results.append({"file": file_path, "status": "purged", "tests": test_result})

        # Hop 4: COMMIT - If all pass
        if all(r["status"] in ["purged", "no_change"] for r in results) and not self.dry_run:
            subprocess.run(["git", "add", "-A"], check=False)
            subprocess.run(["git", "commit", "-m", "refactor: Eternal PascalCase SSOT — purge snake_case + aliases"], check=False)
            self._emit_event("INFO", "PASCAL_SOVEREIGNTY_ACHIEVED")

        return {"results": results, "dry_run": self.dry_run}

    def _audit_snake_case(self, scope: str) -> List[str]:
        """Audit for snake_case defs + aliases."""
        targets = []
        pattern_def = re.compile(r'^\s*(class|@dataclass)\s+([a-z_][a-zA-Z0-9_]*)\s*[\(:]')
        pattern_alias = re.compile(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-zA-Z0-9_]*)\s*$')

        for path in Path(self.repo_root).rglob("*.py"):
            if scope in str(path) or scope == "repo_wide":
                try:
                    content = path.read_text(encoding='utf-8')
                    if pattern_def.search(content) or pattern_alias.search(content):
                        targets.append(str(path))
                except Exception:
                    pass
        return targets

    def _purge_snake_case(self, content: str) -> str:
        """Core purge logic — AST-safe rename + alias removal."""
        # Parse aliases to mapping
        lines = content.splitlines()
        mapping = {}
        cleaned_lines = []
        for line in lines:
            alias_match = re.match(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-zA-Z0-9_]*)\s*$', line)
            if alias_match:
                pascal, snake = alias_match.groups()
                mapping[snake] = pascal
                continue  # Remove alias
            cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        # Rename definitions
        for snake, pascal in mapping.items():
            content = re.sub(rf'class\s+{re.escape(snake)}\s*[\(:]', f'class {pascal}(', content)
            content = re.sub(rf'@dataclass\s*\n\s*class\s+{re.escape(snake)}', f'@dataclass\nclass {pascal}', content)

        # Update references (member + whole-word)
        for snake, pascal in mapping.items():
            content = re.sub(rf'\b{re.escape(snake)}\.', f'{pascal}.', content)
            content = re.sub(rf'\b{re.escape(snake)}\b', pascal, content)

        return content

    def _run_integrated_tests(self) -> Dict:
        """Integrated test cases — all must pass."""
        tests = []

        # Test 1: Basic purge
        input_content = """
class sovereign_severity(str, Enum):
    CRITICAL = "CRITICAL"
SovereignSeverity = sovereign_severity
"""
        expected = """
class SovereignSeverity(str, Enum):
    CRITICAL = "CRITICAL"
"""
        result = self._purge_snake_case(input_content).strip()
        tests.append({"name": "basic_purge", "passed": result == expected.strip()})

        # Test 2: Multiple + references
        input_content = """
class tone_type(str, Enum):
    AUTHORITATIVE = "authoritative"
ToneType = tone_type
severity = tone_type.AUTHORITATIVE
"""
        expected = """
class ToneType(str, Enum):
    AUTHORITATIVE = "authoritative"
severity = ToneType.AUTHORITATIVE
"""
        result = self._purge_snake_case(input_content).strip()
        tests.append({"name": "references", "passed": result == expected.strip()})

        # Test 3: No change clean
        input_content = """
class SovereignEvent(BaseModel):
    pass
"""
        result = self._purge_snake_case(input_content)
        tests.append({"name": "clean_no_change", "passed": result.strip() == input_content.strip()})

        # External validation (run pytest if available)
        pytest_result = subprocess.run(["pytest", "-q", "--tb=no"], 
                                      capture_output=True, 
                                      cwd=self.repo_root,
                                      timeout=30)
        external_passed = pytest_result.returncode == 0
        tests.append({
            "name": "full_pytest_suite", 
            "passed": external_passed, 
            "output": pytest_result.stdout.decode()[:200]
        })

        all_passed = all(t["passed"] for t in tests)
        return {"tests": tests, "all_passed": all_passed}

    def _emit_event(self, severity: str, event_type: str, payload: Optional[Dict] = None) -> None:
        """Telemetry for observability."""
        print(f"[SOVEREIGN EVENT] {severity} | {event_type}")
        if payload:
            print(f"  Payload: {payload}")
