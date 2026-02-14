"""Tests for meta-control config bridge — Wave 7.0.18.

Validates:
  T1) load returns {} when store missing (tmp_path store root)
  T2) render deterministic for same payload regardless of key order
  T3) rejects invalid component (fail-closed)
  T4) AST scan: no imports/calls of apply seam (meta_apply*, apply_*)
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.meta_control.config_store import write_next_version
from agentic_core.L0_routing.meta_control.config_store_types import canonical_json
from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from apps_shared.scripts.meta_control_config_bridge import (
    load_app_component_config,
    render_app_component_config,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


class TestLoadMissing:
    def test_returns_empty_dict_when_store_missing(self, tmp_path: Path) -> None:
        result = load_app_component_config(
            "apps_rg",
            "routing_thresholds",
            store_root=tmp_path,
        )
        assert result == {}

    def test_returns_payload_when_store_exists(self, tmp_path: Path) -> None:
        payload = {"threshold": 0.42, "nested": {"a": 1}}
        write_next_version(tmp_path, "apps_rg", "routing_thresholds", payload, _CLOCK)
        result = load_app_component_config(
            "apps_rg",
            "routing_thresholds",
            store_root=tmp_path,
        )
        expected = json.loads(canonical_json(payload))
        assert result == expected


class TestRenderDeterminism:
    def test_render_deterministic_for_same_payload(self, tmp_path: Path) -> None:
        write_next_version(
            tmp_path,
            "apps_rg",
            "routing_thresholds",
            {"z": 1, "a": 2, "m": {"b": 3, "a": 4}},
            _CLOCK,
        )
        r1 = render_app_component_config(
            "apps_rg",
            "routing_thresholds",
            store_root=tmp_path,
        )
        r2 = render_app_component_config(
            "apps_rg",
            "routing_thresholds",
            store_root=tmp_path,
        )
        assert r1 == r2
        parsed = json.loads(r1)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_render_returns_empty_object_when_missing(self, tmp_path: Path) -> None:
        result = render_app_component_config(
            "apps_rg",
            "routing_thresholds",
            store_root=tmp_path,
        )
        assert result == "{}"


class TestFailClosed:
    def test_load_rejects_invalid_component(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="COMPONENT_NOT_MUTABLE"):
            load_app_component_config(
                "apps_rg",
                "guardian_contract",
                store_root=tmp_path,
            )

    def test_render_rejects_invalid_component(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="COMPONENT_NOT_MUTABLE"):
            render_app_component_config(
                "apps_rg",
                "guardian_contract",
                store_root=tmp_path,
            )


_BRIDGE_FILE = (
    Path(__file__).resolve().parents[3] / "apps_shared" / "scripts" / "meta_control_config_bridge.py"
)
_FORBIDDEN_MODULES = {"meta_apply", "meta_apply_ops"}
_FORBIDDEN_NAMES = {"apply_meta_learning_rollout", "apply_with_invariants"}


class TestNoApplyImports:
    def test_source_has_no_apply_imports_or_calls(self) -> None:
        """AST scan: bridge must not import or call any apply seam."""
        source = _BRIDGE_FILE.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(_BRIDGE_FILE))

        violations: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    module_parts = node.module.split(".")
                    for part in module_parts:
                        if part in _FORBIDDEN_MODULES:
                            violations.append(f"line {node.lineno}: imports from forbidden module {part!r}")
                    if node.names:
                        for alias in node.names:
                            if alias.name in _FORBIDDEN_NAMES:
                                violations.append(
                                    f"line {node.lineno}: imports forbidden name {alias.name!r}"
                                )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        parts = alias.name.split(".")
                        for part in parts:
                            if part in _FORBIDDEN_MODULES:
                                violations.append(f"line {node.lineno}: imports forbidden module {part!r}")

            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in _FORBIDDEN_NAMES:
                    violations.append(f"line {node.lineno}: calls forbidden function {func.id!r}")
                elif isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_NAMES:
                    violations.append(f"line {node.lineno}: calls forbidden method {func.attr!r}")

        assert not violations, "Bridge has forbidden apply-seam references:\n" + "\n".join(
            f"  - {v}" for v in violations
        )
