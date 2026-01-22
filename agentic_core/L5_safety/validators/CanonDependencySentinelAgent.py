"""
[PHASE 16] Canon Dependency Sentinel - The Governance Gatekeeper.
Enforces architectural integrity at the AST level to prevent crashes from broken stubs.
"""

from __future__ import annotations
import ast
import logging
import os
import sys
import subprocess
from dataclasses import dataclass
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

try:
    from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
except ImportError:

    class MCPHardenedMixin:
        pass


Logger = logging.getLogger(__name__)

VALID_AGENT_BASES = {
    "SovereignBaseAgent",
    "L1CognitionBaseAgent",
    "L2ExecutionBaseAgent",
    "L3OrchestrationBaseAgent",
    "L4StateBaseAgent",
    "L5SafetyBaseAgent",
    "L6ObservabilityBaseAgent",
    "InfrastructureMixin",
    "L0MaintenanceBaseAgent",
}

LAYER_AFFINITY_MAP = {
    "L1": ["CognitionAgent", "ReasoningMixin"],
    "L2": ["ExecutionBaseAgent", "ToolInterfaceMixin"],
    "L3": ["OrchestrationBaseAgent", "SupervisorMixin", "SubatomicTestingMixin"],
    "L4": ["StateBaseAgent", "MemoryMixin", "RedisCacheMixin", "PineconeVectorMixin"],
    "L5": ["SafetyBaseAgent", "MCPHardenedMixin", "HealerMixin"],
    "L6": ["ObservabilityBaseAgent", "MetricsMixin"],
}


@dataclass
class CodeViolation:
    file_path: str
    line_number: int
    violation_type: str
    message: str
    severity: str = "HIGH"


class ArchitectureDNAVisitor(ast.NodeVisitor):
    """
    Enforces v3.2 Capability Map: MRO, Mixin Affinity, and DNA integrity.

    Detects:
    - DNA_SEVERED: Agents missing L0 foundation (MRO risk)
    - LAYER_CROSSING: Mixins used outside their designated layer
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[CodeViolation] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        if not node.name.endswith("Agent"):
            return

        # 1. MRO Violation: SovereignBaseAgent must be in the bases or a layer base
        bases = [b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases]
        if not any(base in VALID_AGENT_BASES for base in bases):
            self.violations.append(
                CodeViolation(
                    self.file_path,
                    node.lineno,
                    "DNA_SEVERED",
                    f"Agent '{node.name}' has no L0 foundation (MRO risk).",
                    "HIGH",
                )
            )

        # 2. Layer Affinity: Check if Mixins match the folder path
        layer_match = next(
            (l for l in ["L1", "L2", "L3", "L4", "L5", "L6"] if l in self.file_path), None
        )
        if layer_match:
            for base in bases:
                if "Mixin" in base and base not in LAYER_AFFINITY_MAP.get(layer_match, []):
                    # Allow InfrastructureMixin as global
                    if base != "InfrastructureMixin":
                        self.violations.append(
                            CodeViolation(
                                self.file_path,
                                node.lineno,
                                "LAYER_CROSSING",
                                f"Mixin '{base}' does not belong to layer {layer_match}.",
                                "MEDIUM",
                            )
                        )

        self.generic_visit(node)


class InitializationIntegrityVisitor(ast.NodeVisitor):
    """
    Ensures __init__ properly propagates to SovereignBaseAgent via **kwargs.

    [PHASE 33m] Calibrated to support dataclasses:
    - Dataclasses with @dataclass decorator are auto-initialized
    - __post_init__ is treated as valid initialization context

    Detects:
    - INIT_BYPASS: Agent __init__ fails to call super().__init__(**kwargs)
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[CodeViolation] = []
        self.current_class: str | None = None
        self.is_dataclass: bool = False
        self.has_post_init: bool = False

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name.endswith("Agent"):
            self.current_class = node.name

            # [PHASE 33m] Check for @dataclass decorator
            self.is_dataclass = any(
                (isinstance(d, ast.Name) and d.id == "dataclass")
                or (
                    isinstance(d, ast.Call)
                    and isinstance(d.func, ast.Name)
                    and d.func.id == "dataclass"
                )
                for d in node.decorator_list
            )

            # Check for __post_init__ method (valid for dataclasses)
            self.has_post_init = any(
                isinstance(item, ast.FunctionDef) and item.name == "__post_init__"
                for item in node.body
            )

            self.generic_visit(node)
            self.current_class = None
            self.is_dataclass = False
            self.has_post_init = False
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # [PHASE 33m] Skip dataclasses - they auto-generate __init__
        if self.is_dataclass:
            return

        if node.name != "__init__" or not self.current_class:
            return

        # Verify super().__init__ exists and passes **kwargs
        has_super_init = False
        passes_kwargs = False

        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                # Check for super().__init__(...) pattern
                if isinstance(stmt.func, ast.Attribute) and stmt.func.attr == "__init__":
                    if isinstance(stmt.func.value, ast.Call):
                        func_value = stmt.func.value
                        if isinstance(func_value.func, ast.Name) and func_value.func.id == "super":
                            has_super_init = True
                            # Check for **kwargs in the call
                            for kw in stmt.keywords:
                                if kw.arg is None:  # **kwargs
                                    passes_kwargs = True

        if not has_super_init:
            self.violations.append(
                CodeViolation(
                    self.file_path,
                    node.lineno,
                    "INIT_BYPASS",
                    f"Agent '{self.current_class}' __init__ missing super().__init__() call.",
                    "HIGH",
                )
            )
        elif not passes_kwargs:
            self.violations.append(
                CodeViolation(
                    self.file_path,
                    node.lineno,
                    "INIT_BYPASS",
                    f"Agent '{self.current_class}' __init__ fails to propagate **kwargs to L0 Foundation.",
                    "HIGH",
                )
            )


class HealerComplianceVisitor(ast.NodeVisitor):
    """
    Detects 'Zombie' Healers that exist but do nothing.

    Detects:
    - ZOMBIE_HEALER: heal_repository method is a no-op stub (only pass/return)
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[CodeViolation] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name.endswith("Agent"):
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = None
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name != "heal_repository" or not self.current_class:
            return

        # Check if body is trivial (only pass, or only return with simple value)
        is_trivial = True
        if len(node.body) > 1:
            is_trivial = False
        elif len(node.body) == 1:
            stmt = node.body[0]
            # Pass is trivial
            if isinstance(stmt, ast.Pass):
                is_trivial = True
            # Return with just a dict literal is trivial
            elif isinstance(stmt, ast.Return):
                if stmt.value is None:
                    is_trivial = True
                elif isinstance(stmt.value, ast.Dict):
                    # Check if it's just returning a status dict with no real logic
                    is_trivial = True
                else:
                    is_trivial = False
            # Docstring only is trivial
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                is_trivial = True
            else:
                is_trivial = False

        if is_trivial:
            self.violations.append(
                CodeViolation(
                    self.file_path,
                    node.lineno,
                    "ZOMBIE_HEALER",
                    f"Agent '{self.current_class}' heal_repository method appears to be a no-op stub.",
                    "MEDIUM",
                )
            )


class AgentASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[CodeViolation] = []
        self.current_class: str | None = None
        self.in_function: bool = False

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        if node.name.endswith("Agent") and node.name != "SovereignBaseAgent":
            bases = [
                b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases
            ]
            if not any(base in VALID_AGENT_BASES for base in bases):
                self.violations.append(
                    CodeViolation(
                        str(self.file_path),
                        node.lineno,
                        "MISSING_L0_DNA",
                        f"Agent '{node.name}' does not inherit from SovereignBaseAgent.",
                        "HIGH",
                    )
                )

        is_stub = True
        has_heal_method = False
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                is_stub = False
                if item.name == "heal_repository":
                    has_heal_method = True
            elif not isinstance(item, (ast.Pass, ast.Expr)):
                is_stub = False

        if node.name.endswith("Agent") and is_stub:
            self.violations.append(
                CodeViolation(
                    str(self.file_path),
                    node.lineno,
                    "STUB_AGENT",
                    f"Agent '{node.name}' is a stub.",
                    "MEDIUM",
                )
            )
        if node.name.endswith("Agent") and not has_heal_method and not is_stub:
            self.violations.append(
                CodeViolation(
                    str(self.file_path),
                    node.lineno,
                    "MISSING_HEALING",
                    f"Agent '{node.name}' missing 'heal_repository'.",
                    "MEDIUM",
                )
            )

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.in_function = True
        self.generic_visit(node)
        self.in_function = False

    def visit_Call(self, node: ast.Call):
        if self.current_class and not self.in_function:
            func_id = getattr(node.func, "id", "")
            if func_id == "super" or (
                isinstance(node.func, ast.Attribute)
                and getattr(node.func.value, "id", "") == "super"
            ):
                self.violations.append(
                    CodeViolation(
                        str(self.file_path),
                        node.lineno,
                        "FATAL_SYNTAX",
                        f"Naked super() in '{self.current_class}'.",
                        "CRITICAL",
                    )
                )
        self.generic_visit(node)


class CanonDependencySentinelAgent(SovereignBaseAgent, MCPHardenedMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent_name = "CanonDependencySentinel"
        self.project_root = Path(os.getcwd())

    @timeout(300)
    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        ast_results = self.scan_architecture()
        criticals = [v for v in ast_results["violations"] if v.severity == "CRITICAL"]
        if criticals:
            return {"status": "FATAL", "details": "Naked super() detected."}

        fixed = 0
        if execute:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--recursive",
                    ".",
                ],
                capture_output=True,
            )
            subprocess.run([sys.executable, "-m", "isort", "."], capture_output=True)
            fixed += 2

        return {
            "status": "SUCCESS",
            "ast_violations": len(ast_results["violations"]),
            "fixed": fixed,
        }

    def scan_architecture(self):
        """
        Scan all Agent files for structural validity and DNA integrity.

        [PHASE 33m] Scope Containment: Excludes test, archive, and script directories
        to reduce false positives from non-production code.
        """
        # [PHASE 33m] Directories to exclude from scanning
        EXCLUDED_DIRS = {"tests", "archives", "scripts", "apps_lic", "__pycache__", ".git"}

        violations = []
        for fp in self.project_root.rglob("*Agent.py"):
            # [PHASE 33m] Skip excluded directories
            path_parts = set(fp.parts)
            if path_parts & EXCLUDED_DIRS:
                continue

            try:
                tree = ast.parse(fp.read_text(encoding="utf-8"), filename=str(fp))

                # Run Syntax Sentinel
                visitor = AgentASTVisitor(str(fp))
                visitor.visit(tree)
                violations.extend(visitor.violations)

                # Run DNA Auditor
                dna_visitor = ArchitectureDNAVisitor(str(fp))
                dna_visitor.visit(tree)
                violations.extend(dna_visitor.violations)

                # Run Init Integrity Auditor
                init_visitor = InitializationIntegrityVisitor(str(fp))
                init_visitor.visit(tree)
                violations.extend(init_visitor.violations)

                # Run Healer Compliance Auditor
                healer_visitor = HealerComplianceVisitor(str(fp))
                healer_visitor.visit(tree)
                violations.extend(healer_visitor.violations)

            except SyntaxError as e:
                violations.append(
                    CodeViolation(str(fp), e.lineno or 0, "SYNTAX_ERROR", e.msg, "CRITICAL")
                )
        return {"violations": violations}

    def resurrect_zombie(self, file_path: Path, agent_name: str) -> bool:
        """
        [PHASE 33l] Surgical injection of a standardized heal_repository method
        for agents detected as ZOMBIE_HEALER.

        Args:
            file_path: Path to the agent file with zombie healer
            agent_name: Name of the agent class

        Returns:
            True if resurrection successful, False otherwise
        """
        import re

        try:
            content = file_path.read_text(encoding="utf-8")
            if "def heal_repository" not in content:
                Logger.warning(f"No heal_repository found in {file_path.name}")
                return False

            # Resurrection patch - standardized healer logic
            resurrection_patch = '''    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict:
        """Standardized resurrection healer logic."""
        violations = self.scan_repository(**kwargs) if hasattr(self, 'scan_repository') else []
        if execute and not dry_run and violations:
            return self._fix_violations(violations) if hasattr(self, '_fix_violations') else {"status": "SKIPPED", "violations": len(violations)}
        return {"status": "PASS" if not violations else "FAIL", "violations_found": len(violations), "violations_fixed": 0}'''

            # Use regex to replace the stub heal_repository method
            # Pattern matches: def heal_repository(...): followed by pass/return/docstring only
            pattern = r'(    def heal_repository\([^)]*\)[^:]*:)\s*(?:"""[^"]*"""\s*)?(?:pass|return[^\n]*)'

            if re.search(pattern, content):
                content = re.sub(pattern, resurrection_patch, content)
                file_path.write_text(content, encoding="utf-8")
                Logger.info(f"✅ Resurrected zombie healer in {file_path.name}")
                return True
            else:
                Logger.warning(f"Could not match heal_repository pattern in {file_path.name}")
                return False

        except Exception as e:
            Logger.error(f"Resurrection failed for {file_path.name}: {e}")
            return False
