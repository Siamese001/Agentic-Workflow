"""Deterministic negative tests for hardening wave.

Each test proves a specific bypass that existed pre-hardening and is now closed.
Tests run matchers directly on synthetic fixture ASTs — no production scan.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    ARTIFACT_CALL_NAMES,
    ARTIFACT_CLASS_NAMES,
    ARTIFACT_DICT_KEYS_STRICT,
    ast_contains_call,
    ast_contains_name,
    find_agent_class,
    find_method,
    is_stub_body,
    is_super_only_delegation,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


# ── Helpers ───────────────────────────────────────────────────────────────────
def _parse(name: str) -> ast.Module:
    fp = FIXTURES_DIR / name
    return ast.parse(fp.read_text(encoding="utf-8"), filename=str(fp))


# ── Bypass 1: super-only delegation ──────────────────────────────────────────
class TestSuperOnlyDelegationBypass:
    """Proves that `return super().execute(**kwargs)` was invisible to
    the old stub check and is now caught."""

    @pytest.fixture(autouse=True)
    def _load(self):
        tree = _parse("fake_super_delegation_agent.py")
        cls = find_agent_class(tree, "FakeSuperDelegationAgent")
        assert cls is not None
        self.execute_body = find_method(cls, "execute").body

    def test_old_matcher_misses_super_delegation(self):
        """Pre-hardening: is_stub_body returns False (bypass existed)."""
        assert is_stub_body(self.execute_body) is False

    def test_new_matcher_catches_super_delegation(self):
        """Post-hardening: is_super_only_delegation returns True."""
        assert is_super_only_delegation(self.execute_body) is True


# ── Bypass 2: trivial dict-key artifact heuristic ────────────────────────────
class TestTrivialOutputDictBypass:
    """Proves that `{"output": None}` passed the old heuristic and is
    now rejected by the strict key set."""

    @pytest.fixture(autouse=True)
    def _load(self):
        tree = _parse("fake_trivial_output_agent.py")
        cls = find_agent_class(tree, "FakeTrivialOutputAgent")
        assert cls is not None
        self.execute_method = find_method(cls, "execute")
        assert self.execute_method is not None

    def _has_artifact_with_keys(self, accepted_keys: frozenset[str]) -> bool:
        """Replicates the dict-key check with a configurable key set."""
        em = self.execute_method
        if ast_contains_call(em, ARTIFACT_CALL_NAMES):
            return True
        if ast_contains_name(em, ARTIFACT_CLASS_NAMES):
            return True
        for child in ast.walk(em):
            if isinstance(child, ast.Dict):
                for key in child.keys:
                    if (
                        isinstance(key, ast.Constant)
                        and isinstance(key.value, str)
                        and key.value in accepted_keys
                    ):
                        return True
        return False

    def test_old_matcher_accepts_trivial_output(self):
        """Pre-hardening: broad key set included 'output' → bypass existed."""
        OLD_KEYS = frozenset({"artifacts", "artifact", "results", "output"})
        assert self._has_artifact_with_keys(OLD_KEYS) is True

    def test_new_matcher_rejects_trivial_output(self):
        """Post-hardening: strict key set excludes 'output' → violation."""
        assert self._has_artifact_with_keys(ARTIFACT_DICT_KEYS_STRICT) is False
