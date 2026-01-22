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
from typing import Any, Dict, List, Optional

from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.security import safe_execute

try:
    from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
except ImportError:
    class MCPHardenedMixin: pass

Logger = logging.getLogger(__name__)

VALID_AGENT_BASES = {
    "SovereignBaseAgent", "L1CognitionBaseAgent", "L2ExecutionBaseAgent", 
    "L3OrchestrationBaseAgent", "L4StateBaseAgent", "L5SafetyBaseAgent", 
    "L6ObservabilityBaseAgent", "InfrastructureMixin"
}

@dataclass
class CodeViolation:
    file_path: str
    line_number: int
    violation_type: str
    message: str
    severity: str = "HIGH"

class AgentASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[CodeViolation] = []
        self.current_class: Optional[str] = None
        self.in_function: bool = False

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        if node.name.endswith("Agent") and node.name != "SovereignBaseAgent":
            bases = [b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases]
            if not any(base in VALID_AGENT_BASES for base in bases):
                self.violations.append(CodeViolation(str(self.file_path), node.lineno, "MISSING_L0_DNA", f"Agent '{node.name}' does not inherit from SovereignBaseAgent.", "HIGH"))
        
        is_stub = True
        has_heal_method = False
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                is_stub = False
                if item.name == "heal_repository": has_heal_method = True
            elif not isinstance(item, (ast.Pass, ast.Expr)): is_stub = False

        if node.name.endswith("Agent") and is_stub:
            self.violations.append(CodeViolation(str(self.file_path), node.lineno, "STUB_AGENT", f"Agent '{node.name}' is a stub.", "MEDIUM"))
        if node.name.endswith("Agent") and not has_heal_method and not is_stub:
             self.violations.append(CodeViolation(str(self.file_path), node.lineno, "MISSING_HEALING", f"Agent '{node.name}' missing 'heal_repository'.", "MEDIUM"))

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.in_function = True
        self.generic_visit(node)
        self.in_function = False

    def visit_Call(self, node: ast.Call):
        if self.current_class and not self.in_function:
            func_id = getattr(node.func, "id", "")
            if func_id == "super" or (isinstance(node.func, ast.Attribute) and getattr(node.func.value, "id", "") == "super"):
                self.violations.append(CodeViolation(str(self.file_path), node.lineno, "FATAL_SYNTAX", f"Naked super() in '{self.current_class}'.", "CRITICAL"))
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
        if criticals: return {"status": "FATAL", "details": "Naked super() detected."}
        
        fixed = 0
        if execute:
            subprocess.run([sys.executable, "-m", "autoflake", "--in-place", "--remove-all-unused-imports", "--recursive", "."], capture_output=True)
            subprocess.run([sys.executable, "-m", "isort", "."], capture_output=True)
            fixed += 2
        
        return {"status": "SUCCESS", "ast_violations": len(ast_results["violations"]), "fixed": fixed}

    def scan_architecture(self):
        violations = []
        for fp in self.project_root.rglob("*Agent.py"):
            try:
                tree = ast.parse(fp.read_text(encoding="utf-8"), filename=str(fp))
                visitor = AgentASTVisitor(str(fp))
                visitor.visit(tree)
                violations.extend(visitor.violations)
            except SyntaxError as e:
                violations.append(CodeViolation(str(fp), e.lineno or 0, "SYNTAX_ERROR", e.msg, "CRITICAL"))
        return {"violations": violations}
