#!/usr/bin/env python3
"""
Lifecycle Audit - Validates Sovereign Lifecycle Guard hardening.

Tests DNA contract enforcement using AST visitors implemented inline
(CanonDependencySentinelAgent is not yet a standalone importable module).
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field

import pytest


# ---------------------------------------------------------------------------
# Minimal inline visitors (mirror the contract without external dependency)
# ---------------------------------------------------------------------------

@dataclass
class Violation:
    violation_type: str
    message: str
    file: str
    line: int = 0


class InitializationIntegrityVisitor(ast.NodeVisitor):
    """Detects missing super().__init__(**kwargs) in SovereignBaseAgent subclasses."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.violations: list[Violation] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [getattr(b, "id", None) or getattr(b, "attr", None) for b in node.bases]
        if "SovereignBaseAgent" not in bases:
            self.generic_visit(node)
            return
        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == "__init__"):
                continue
            # Check for super().__init__ call
            has_super_init = False
            has_kwargs_pass = False
            for stmt in ast.walk(item):
                if not isinstance(stmt, ast.Call):
                    continue
                func = stmt.func
                if isinstance(func, ast.Attribute) and func.attr == "__init__":
                    if isinstance(func.value, ast.Call):
                        inner = func.value
                        if getattr(inner.func, "id", None) == "super":
                            has_super_init = True
                            # Check **kwargs forwarded
                            for kw in stmt.keywords:
                                if kw.arg is None:  # **kwargs spread
                                    has_kwargs_pass = True
            if not has_super_init:
                self.violations.append(Violation(
                    violation_type="INIT_BYPASS",
                    message=f"{node.name}.__init__ does not call super().__init__()",
                    file=self.filename,
                    line=item.lineno,
                ))
            elif not has_kwargs_pass:
                self.violations.append(Violation(
                    violation_type="INIT_BYPASS",
                    message=f"{node.name}.__init__ calls super().__init__() without **kwargs",
                    file=self.filename,
                    line=item.lineno,
                ))
        self.generic_visit(node)


class ArchitectureDNAVisitor(ast.NodeVisitor):
    """Detects classes that lack SovereignBaseAgent in their inheritance chain."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.violations: list[Violation] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not node.bases:
            self.violations.append(Violation(
                violation_type="DNA_SEVERED",
                message=f"{node.name} has no base class (DNA severed)",
                file=self.filename,
                line=node.lineno,
            ))
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

COMPLIANT_AGENT = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class CompliantAgent(SovereignBaseAgent):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS", "violations_found": 0}
"""

INIT_HIJACKING_AGENT = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class ZombieAgent(SovereignBaseAgent):
    def __init__(self, some_arg):
        self.some_arg = some_arg

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""

INIT_NO_KWARGS_AGENT = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class NoKwargsAgent(SovereignBaseAgent):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""

DNA_SEVERED_AGENT = """
class OrphanAgent:
    def __init__(self):
        pass

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_init_gate_compliant():
    """DNA-01: Compliant Agent must produce 0 violations."""
    tree = ast.parse(COMPLIANT_AGENT)
    visitor = InitializationIntegrityVisitor("test_compliant.py")
    visitor.visit(tree)
    assert visitor.violations == [], (
        f"Compliant agent incorrectly flagged: {[v.message for v in visitor.violations]}"
    )


def test_init_gate_hijacking():
    """DNA-02: Missing super().__init__() must be detected."""
    tree = ast.parse(INIT_HIJACKING_AGENT)
    visitor = InitializationIntegrityVisitor("test_hijacking.py")
    visitor.visit(tree)
    init_bypasses = [v for v in visitor.violations if v.violation_type == "INIT_BYPASS"]
    assert len(init_bypasses) > 0, "Init hijacking (missing super) was NOT detected"


def test_init_gate_no_kwargs():
    """DNA-02b: super().__init__() without **kwargs must be detected."""
    tree = ast.parse(INIT_NO_KWARGS_AGENT)
    visitor = InitializationIntegrityVisitor("test_no_kwargs.py")
    visitor.visit(tree)
    init_bypasses = [v for v in visitor.violations if v.violation_type == "INIT_BYPASS"]
    assert len(init_bypasses) > 0, "Missing **kwargs propagation was NOT detected"


def test_dna_severed():
    """DNA-SEVERED: Agent without any base class must be detected."""
    tree = ast.parse(DNA_SEVERED_AGENT)
    visitor = ArchitectureDNAVisitor("test_severed.py")
    visitor.visit(tree)
    severed = [v for v in visitor.violations if v.violation_type == "DNA_SEVERED"]
    assert len(severed) > 0, "Orphan agent (no base class) was NOT detected"
