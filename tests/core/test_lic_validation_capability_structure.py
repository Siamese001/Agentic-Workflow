"""
Structural invariant tests for LICEngineValidationCapability (Cluster 5 extraction).

Validates:
1. Capability exists and has the correct protocol (SIGNAL_NAME, VALIDATION_LABEL, _validate, run_validation)
2. CampaignBalanceAgent and DeliverabilityAgent inherit LICEngineValidationCapability
3. Both agents declare SIGNAL_NAME and VALIDATION_LABEL as non-empty ClassVars
4. Both agents override _validate() with domain-specific logic
5. Neither agent contains inline scaffold logic (add_signal/record_result/print ❌/✅ in execute)

All checks are AST-based — zero runtime imports required.

[CREATED 2026-02-08] Cluster 5 structural enforcement.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_file(rel_path: str) -> ast.Module:
    """Parse a Python file relative to PROJECT_ROOT and return the AST."""
    full = PROJECT_ROOT / rel_path
    assert full.exists(), f"File not found: {full}"
    return ast.parse(full.read_text(encoding="utf-8"))


def _get_class(tree: ast.Module, class_name: str) -> ast.ClassDef | None:
    """Find a top-level ClassDef by name."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _get_method(cls: ast.ClassDef, method_name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Find a method (sync or async) inside a ClassDef by name."""
    for node in ast.iter_child_nodes(cls):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            return node
    return None


def _get_base_names(cls: ast.ClassDef) -> list[str]:
    """Return simple base-class names for a ClassDef."""
    names = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _class_var_value(cls: ast.ClassDef, var_name: str) -> str | None:
    """Return the string value of a ClassVar assignment, or None if absent."""
    for node in ast.iter_child_nodes(cls):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id == var_name:
                    val = node.value if isinstance(node, ast.Assign) else node.value
                    if isinstance(val, ast.Constant) and isinstance(val.value, str):
                        return val.value
    return None


# ---------------------------------------------------------------------------
# 1. Capability protocol
# ---------------------------------------------------------------------------


class TestCapabilityProtocol:
    """LICEngineValidationCapability has the required protocol surface."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.tree = _parse_file("apps_lic/utils/lic_engine_validation_capability.py")
        self.cls = _get_class(self.tree, "LICEngineValidationCapability")
        assert self.cls is not None, "LICEngineValidationCapability class not found"

    def test_has_signal_name_classvar(self):
        assert _class_var_value(self.cls, "SIGNAL_NAME") is not None

    def test_has_validation_label_classvar(self):
        assert _class_var_value(self.cls, "VALIDATION_LABEL") is not None

    def test_has_validate_method(self):
        m = _get_method(self.cls, "_validate")
        assert m is not None, "_validate() method missing"

    def test_has_run_validation_method(self):
        m = _get_method(self.cls, "run_validation")
        assert m is not None, "run_validation() method missing"

    def test_validate_raises_not_implemented(self):
        """_validate() in the base capability must raise NotImplementedError."""
        m = _get_method(self.cls, "_validate")
        assert m is not None
        source = ast.dump(m)
        assert "NotImplementedError" in source

    def test_no_domain_logic_in_capability(self):
        """Capability must not reference campaign, deliverability, spam, etc."""
        source = Path(
            PROJECT_ROOT / "apps_lic/utils/lic_engine_validation_capability.py",
        ).read_text(encoding="utf-8")
        forbidden = ["campaign", "deliverability", "spam", "leads", "messages"]
        for word in forbidden:
            assert word not in source.lower(), (
                f"Capability contains domain word '{word}' — pure harness violated"
            )


# ---------------------------------------------------------------------------
# 2. Agent inheritance
# ---------------------------------------------------------------------------

AGENTS = [
    ("apps_lic/engines/CampaignBalanceAgent.py", "CampaignBalanceAgent"),
    ("apps_lic/engines/DeliverabilityAgent.py", "DeliverabilityAgent"),
]


class TestAgentInheritance:
    """Both agents inherit LICEngineValidationCapability."""

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_inherits_capability(self, path, class_name):
        tree = _parse_file(path)
        cls = _get_class(tree, class_name)
        assert cls is not None, f"{class_name} not found"
        bases = _get_base_names(cls)
        assert "LICEngineValidationCapability" in bases, (
            f"{class_name} does not inherit LICEngineValidationCapability (bases: {bases})"
        )


# ---------------------------------------------------------------------------
# 3. ClassVar declarations
# ---------------------------------------------------------------------------


class TestAgentClassVars:
    """Both agents declare non-empty SIGNAL_NAME and VALIDATION_LABEL."""

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_signal_name_non_empty(self, path, class_name):
        cls = _get_class(_parse_file(path), class_name)
        val = _class_var_value(cls, "SIGNAL_NAME")
        assert val and len(val) > 0, f"{class_name}.SIGNAL_NAME is empty or missing"

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_validation_label_non_empty(self, path, class_name):
        cls = _get_class(_parse_file(path), class_name)
        val = _class_var_value(cls, "VALIDATION_LABEL")
        assert val and len(val) > 0, f"{class_name}.VALIDATION_LABEL is empty or missing"


# ---------------------------------------------------------------------------
# 4. _validate override
# ---------------------------------------------------------------------------


class TestAgentValidateOverride:
    """Both agents override _validate() with domain-specific logic."""

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_has_validate_method(self, path, class_name):
        cls = _get_class(_parse_file(path), class_name)
        m = _get_method(cls, "_validate")
        assert m is not None, f"{class_name} does not override _validate()"

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_validate_returns_list(self, path, class_name):
        """_validate must contain a return statement (returns issues list)."""
        cls = _get_class(_parse_file(path), class_name)
        m = _get_method(cls, "_validate")
        assert m is not None
        returns = [n for n in ast.walk(m) if isinstance(n, ast.Return)]
        assert len(returns) > 0, f"{class_name}._validate() has no return statement"


# ---------------------------------------------------------------------------
# 5. No inline scaffold in execute()
# ---------------------------------------------------------------------------


class TestNoInlineScaffold:
    """execute() must NOT contain scaffold logic (that's the capability's job)."""

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_execute_has_no_add_signal(self, path, class_name):
        """execute() should delegate to run_validation(), not call add_signal directly."""
        cls = _get_class(_parse_file(path), class_name)
        m = _get_method(cls, "execute")
        assert m is not None
        source = ast.dump(m)
        assert "add_signal" not in source, (
            f"{class_name}.execute() still calls add_signal() — use run_validation()"
        )

    @pytest.mark.parametrize("path,class_name", AGENTS)
    def test_execute_has_no_record_result(self, path, class_name):
        """execute() should not call record_result directly (except for early-return guards)."""
        cls = _get_class(_parse_file(path), class_name)
        m = _get_method(cls, "execute")
        assert m is not None
        # Count record_result calls — allow at most 1 for early-return guard
        calls = [
            n
            for n in ast.walk(m)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "record_result"
        ]
        assert len(calls) <= 1, (
            f"{class_name}.execute() has {len(calls)} record_result() calls — scaffold leaked"
        )
