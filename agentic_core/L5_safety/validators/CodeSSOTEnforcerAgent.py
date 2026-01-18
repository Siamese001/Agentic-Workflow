from __future__ import annotations
from dataclasses import dataclass
"""
CodeSSOTEnforcerAgent — CODE-LEVEL SSOT ENFORCEMENT

VERSION 2.0 — 2025-12-31
Enforces that CODE uses SSOT imports instead of hard-coded paths.

Direction: Code → Blueprint (enforcement)
Scans: Python source files for hard-coded path strings
Detects: Violations where code bypasses structure_blueprint.py
Action: Reports violations to validation pipeline

Drastically reduced false positives through:
- AST-based string literal detection (not line scanning)
- Only flags FULL PATH patterns (e.g., "agentic_core/L5_safety")
- Ignores single folder names (too common in legitimate code)
- Context-aware filtering for imports, docstrings, comments
- Whitelist for known safe patterns

Complementary to FilesystemSSOTReconcilerAgent which updates the blueprint
when new folders are created on the filesystem.
"""
import ast
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger = logging.getLogger(__name__)

# Only flag these HIGH-CONFIDENCE patterns (full paths, not single segments)
# These are the ONLY patterns that indicate true SSOT drift
DRIFT_PATTERNS = [
    # Full layer paths - these should use SSOT constants
    r'agentic_core/L\d+_\w+',
    r'agentic_core\\L\d+_\w+',
    # App paths with subfolders
    r'apps_rg/\w+',
    r'apps_lic/\w+', 
    r'apps_shared/\w+',
    # Hardcoded root + subfolder combinations
    r'"agentic_core".*"L\d+_',
    r"'agentic_core'.*'L\d+_",
]

# Compile patterns for performance
DRIFT_REGEX = [re.compile(p) for p in DRIFT_PATTERNS]

# Files/paths to completely skip (SSOT source, tests, configs)
SKIP_PATHS = {
    "structure_blueprint.py",
    "sovereign_config.py",
    "SovereignEnv.py",
    "__pycache__",
    ".git",
    "archives",
    "node_modules",
    ".venv",
    "coverage_html",
    "runtime/audit",
    "runtime/backups",
}

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

@dataclass
class CodeSSOTEnforcerAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Ultra high-signal code-level SSOT enforcer using AST analysis.
    
    Enforces that code uses SSOT imports from structure_blueprint.py
    instead of hard-coded path strings.
    
    Only detects TRUE violations:
    - Hard-coded full paths like "agentic_core/L5_safety/validators"
    - String literals that bypass SSOT imports
    
    Does NOT flag:
    - Single folder names (too common)
    - Dynamic path construction
    - Imports, docstrings, comments
    - Test fixtures and assertions
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        self.project_root = project_root.resolve()
        self.ssot_file = self.project_root / "agentic_core" / "config" / "blueprint_sovereign" / "structure_blueprint.py"

    def _should_skip_file(self, py_file: Path) -> bool:
        """Check if file should be skipped entirely."""
        file_str = str(py_file)
        return any(skip in file_str for skip in SKIP_PATHS)

    def _extract_string_literals(self, content: str) -> List[Tuple[int, str, str]]:
        """
        Use AST to extract only string literals (not comments, docstrings, etc.)
        
        Returns:
            List of (line_number, string_value, context)
        """
        literals = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        for node in ast.walk(tree):
            # Only process string constants
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                # Skip docstrings (first statement in module/class/function)
                if self._is_docstring(node, tree):
                    continue
                
                value = node.value
                lineno = getattr(node, 'lineno', 0)
                
                # Only include if it matches drift patterns
                if self._matches_drift_pattern(value):
                    # Get context line
                    lines = content.splitlines()
                    context = lines[lineno - 1].strip() if lineno <= len(lines) else ""
                    literals.append((lineno, value, context))
        
        return literals

    def _is_docstring(self, node: ast.AST, tree: ast.AST) -> bool:
        """Check if a string constant is a docstring."""
        # Simple heuristic: if it's the first child of a module/class/function body
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = getattr(parent, 'body', [])
                if body and isinstance(body[0], ast.Expr):
                    if isinstance(body[0].value, ast.Constant):
                        if body[0].value is node:
                            return True
        return False

    def _matches_drift_pattern(self, value: str) -> bool:
        """Check if string matches high-confidence drift patterns."""
        for regex in DRIFT_REGEX:
            if regex.search(value):
                return True
        return False

    def _is_legitimate_context(self, context: str) -> bool:
        """
        Filter out legitimate usages based on context.
        """
        ctx_lower = context.lower()
        
        # Allow imports from structure_blueprint
        if "structure_blueprint" in context or "from agentic_core.config" in context:
            return True
        
        # Allow __file__ based paths
        if "__file__" in context:
            return True
        
        # Allow Path() construction with variables
        if "Path(" in context and ("/" not in context or ".parent" in context or ".resolve" in context):
            return True
        
        # Allow logging/print statements (informational)
        if context.strip().startswith(("Logger.", "print(", "logging.")):
            return True
        
        # Allow comments
        if context.strip().startswith("#"):
            return True
        
        # Allow test assertions (test files can reference paths)
        if "assert" in ctx_lower or "test" in ctx_lower:
            return True
        
        # Allow error messages and exceptions
        if "raise " in context or "Error(" in context or "Exception(" in context:
            return True
        
        # Allow docstring-like patterns
        if context.strip().startswith(('"""', "'''")):
            return True
        
        # Allow relative imports
        if "from ." in context or "import " in context:
            return True
        
        return False

    def validate_and_fix_ssot_drift(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Ultra high-signal SSOT validation.
        Only reports true hard-coded path drift.
        """
        violations = []
        files_scanned = 0

        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            files_scanned += 1
            
            try:
                content = py_file.read_text(encoding="utf-8")
            except Exception:
                continue
            
            # Use AST to extract string literals
            literals = self._extract_string_literals(content)
            
            for lineno, value, context in literals:
                # Skip if context indicates legitimate usage
                if self._is_legitimate_context(context):
                    continue
                
                # This is a TRUE Violation - hard-coded path in string literal
                violations.append({
                    "file": str(py_file.relative_to(self.project_root)),
                    "line": lineno,
                    "value": value[:100],  # Truncate long strings
                    "context": context[:150],
                    "Severity": "high",
                    "suggestion": "Replace with SSOT import from structure_blueprint.py"
                })
        
        # Deduplicate by file+line
        seen = set()
        unique_violations = []
        for v in violations:
            key = (v["file"], v["line"])
            if key not in seen:
                seen.add(key)
                unique_violations.append(v)
        
        status = "pure" if not unique_violations else "drift_detected"
        
        return {
            "violations_found": len(unique_violations),
            "files_scanned": files_scanned,
            "violations": unique_violations[:50],  # Limit output
            "status": status,
            "summary": f"SSOT drift scan: {len(unique_violations)} true violations in {files_scanned} files"
        }

    async def detect_violations(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Detection-only interface for MissionController phase separation.
        """
        py_file = Path(file_path)
        if self._should_skip_file(py_file):
            return []
        
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            return []
        
        violations = []
        literals = self._extract_string_literals(content)
        
        for lineno, value, context in literals:
            if self._is_legitimate_context(context):
                continue
            
            violations.append({
                "type": "ssot_drift",
                "line": lineno,
                "value": value[:100],
                "context": context[:150],
            })
        
        return violations

    def execute(self) -> Dict[str, Any]:
        """Orchestrator entrypoint"""
        return self.validate_and_fix_ssot_drift(dry_run=True)

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Autonomous code SSOT enforcement."""
        if _call_path is None:
            _call_path = set()
        if self.__class__.__name__ in _call_path:
            return {"errors": 0, "skipped": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 0, "skipped": 1, "depth_limited": True}
        _call_path.add(self.__class__.__name__)
        
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            
            result = self.validate_and_fix_ssot_drift(dry_run=True)
            violations = result.get("violations_found", 0)
            print(f"[CodeSSOTEnforcer HEAL @ depth {depth}] Found {violations} violations")
            # Code SSOT violations require manual review - informational only
            return {"violations_found": violations, "fixed": 0, "manual_review_required": violations}
        finally:
            _call_path.discard(self.__class__.__name__)


__all__ = ["CodeSSOTEnforcerAgent"]
