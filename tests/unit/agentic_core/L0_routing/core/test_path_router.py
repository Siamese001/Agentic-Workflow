"""Runtime-hardened tests for deterministic L0 path routing."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def routing_symbols():
    path_router_module = pytest.importorskip("agentic_core.L0_routing.reasoning.path_router")
    assembly_module = pytest.importorskip("agentic_core.L0_routing.reasoning.assembly_stage")
    return {
        "Path": path_router_module.Path,
        "PathRouter": path_router_module.PathRouter,
        "AirlockAssembler": assembly_module.AirlockAssembler,
    }


@pytest.fixture(scope="module")
def seam_module():
    return pytest.importorskip("agentic_core.L0_routing.utils.elevator_shaft_seam")


@pytest.fixture()
def make_payload(routing_symbols):
    def _make_payload(user_prompt: str = "Simple prompt"):
        assembler = routing_symbols["AirlockAssembler"]
        return assembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=user_prompt,
        )

    return _make_payload


class TestPathRouter:
    def test_path_enum_values(self, routing_symbols):
        path_enum = routing_symbols["Path"]

        assert path_enum.A.value == "A"
        assert path_enum.B.value == "B"
        assert path_enum.C.value == "C"
        assert path_enum.D.value == "D"

    def test_empty_check_ids_selects_path_a(self, routing_symbols, make_payload):
        payload = make_payload()
        payload.check_ids = []

        selected = routing_symbols["PathRouter"]().select_path(payload)

        assert selected == routing_symbols["Path"].A

    def test_sanitized_payload_selects_path_b(self, routing_symbols, make_payload):
        payload = make_payload("Prompt with [ADMIN] marker")

        assert payload.sanitized is True
        assert payload.check_ids

        selected = routing_symbols["PathRouter"]().select_path(payload)

        assert selected == routing_symbols["Path"].B

    def test_single_check_id_selects_path_c(self, routing_symbols, make_payload):
        payload = make_payload()
        payload.check_ids = ["check1"]
        payload.sanitized = False

        selected = routing_symbols["PathRouter"]().select_path(payload)

        assert selected == routing_symbols["Path"].C

    def test_multiple_check_ids_selects_path_d(self, routing_symbols, make_payload):
        payload = make_payload()
        payload.check_ids = ["check1", "check2"]
        payload.sanitized = False

        selected = routing_symbols["PathRouter"]().select_path(payload)

        assert selected == routing_symbols["Path"].D

    def test_deterministic_selection_identical_payloads(self, routing_symbols, make_payload):
        router = routing_symbols["PathRouter"]()
        payload1 = make_payload("Test prompt")
        payload2 = make_payload("Test prompt")

        assert router.select_path(payload1) == router.select_path(payload2)

    def test_priority_order_empty_check_ids_overrides_sanitized(self, routing_symbols, make_payload):
        payload = make_payload("Prompt with [ADMIN] marker")
        payload.check_ids = []

        selected = routing_symbols["PathRouter"]().select_path(payload)

        assert selected == routing_symbols["Path"].A

    def test_priority_order_sanitized_over_single_check_id(self, routing_symbols, make_payload):
        payload = make_payload("Prompt with [ADMIN] marker")
        payload.check_ids = ["check1"]

        selected = routing_symbols["PathRouter"]().select_path(payload)

        assert selected == routing_symbols["Path"].B


class TestElevatorShaftSeam:
    def test_load_context_jit_returns_empty_dict(self, seam_module):
        result = seam_module.load_context_jit("test_trace_id", "test_intent")

        assert result == {}
        assert isinstance(result, dict)

    def test_seam_has_no_forbidden_imports(self, seam_module):
        seam_path = Path(seam_module.__file__)
        tree = ast.parse(seam_path.read_text(encoding="utf-8"))

        forbidden_import_terms = ("L2_", "L5_", "datetime", "time")
        found_forbidden: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(term in alias.name for term in forbidden_import_terms):
                        found_forbidden.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                if any(term in module_name for term in forbidden_import_terms):
                    found_forbidden.append(f"from {module_name}")

        assert not found_forbidden, f"Forbidden imports found: {found_forbidden}"

    def test_seam_has_no_routing_logic_in_load_context_jit(self, seam_module):
        seam_path = Path(seam_module.__file__)
        tree = ast.parse(seam_path.read_text(encoding="utf-8"))
        target_function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "load_context_jit"
        )

        forbidden_nodes = (ast.If, ast.For, ast.While, ast.Try)
        found_nodes = [
            type(node).__name__ for node in ast.walk(target_function) if isinstance(node, forbidden_nodes)
        ]

        assert not found_nodes, f"Control-flow statements found in load_context_jit: {found_nodes}"
