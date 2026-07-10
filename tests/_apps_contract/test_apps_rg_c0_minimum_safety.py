"""apps-test-model: MIGRATION.

Regression coverage for the live C0 minimum-safety predicate after the slim-runtime migration.
The profile-driven aggregate checker is historical; section C0 metrics consume only
``is_c0_minimum_safe``.
"""

from __future__ import annotations

import ast
import inspect

import pytest

import apps_rg.runtime.bindings.c0_minimum_safety as safety


@pytest.mark.parametrize("support_status", ["PASS", "WEAK_WITH_CAVEATS"])
def test_live_minimum_safety_accepts_supported_statuses(support_status: str) -> None:
    assert safety.is_c0_minimum_safe(support_status) is True


@pytest.mark.parametrize(
    "support_status",
    ["PARTIAL", "WEAK", "CONFLICTED", "EMPTY", "BLOCKED", "UNKNOWN", "", "pass"],
)
def test_live_minimum_safety_rejects_non_sendable_statuses(support_status: str) -> None:
    assert safety.is_c0_minimum_safe(support_status) is False


def test_live_predicate_does_not_load_deleted_legacy_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(safety, "_DEFAULT_PROFILE", None)
    monkeypatch.setattr(safety, "_PROFILE_PATH", safety._PROFILE_PATH.with_name("missing.json"))

    assert safety.is_c0_minimum_safe("PASS") is True


def test_live_module_keeps_provider_and_core_boundaries() -> None:
    tree = ast.parse(inspect.getsource(safety))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    forbidden = {"agentic_core", "anthropic", "httpx", "openai", "requests"}
    imported_roots = {name.split(".", 1)[0] for name in imports}
    assert not imported_roots & forbidden


def test_live_predicate_is_exported() -> None:
    assert "is_c0_minimum_safe" in safety.__all__
