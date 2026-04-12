"""
Unit tests for L0 Path Router - deterministic path selection.
"""

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


@pytest.mark.unit
class TestPathRouter:
    """Test deterministic PathRouter implementation."""

    def test_path_enum_values(self):
        """Test Path enum has correct values."""
        from agentic_core.L0_routing.reasoning.path_router import Path

        assert Path.A.value == "A"
        assert Path.B.value == "B"
        assert Path.C.value == "C"
        assert Path.D.value == "D"

    def test_empty_check_ids_selects_path_a(self):
        """Test empty check_ids selects Path.A."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Simple prompt",
        )

        # Ensure empty check_ids
        payload.check_ids = []

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.A

    def test_sanitized_payload_selects_path_b(self):
        """Test sanitized payload selects Path.B."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with [ADMIN] marker",
        )

        # Verify payload is sanitized
        assert payload.sanitized is True
        assert payload.check_ids  # Non-empty to avoid Path.A

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.B

    def test_single_check_id_selects_path_c(self):
        """Test single check_id selects Path.C."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Simple prompt",
        )

        # Set single check_id and ensure not sanitized
        payload.check_ids = ["check1"]
        payload.sanitized = False

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.C

    def test_multiple_check_ids_selects_path_d(self):
        """Test multiple check_ids selects Path.D."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Simple prompt",
        )

        # Set multiple check_ids and ensure not sanitized
        payload.check_ids = ["check1", "check2"]
        payload.sanitized = False

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.D

    def test_deterministic_selection_identical_payloads(self):
        """Test identical payloads produce identical path selection."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import PathRouter

        payload_args = {
            "s0_system": "System",
            "i0_instructional": "Instructions",
            "c0_context": "Context",
            "u0_user_prompt": "Test prompt",
        }

        payload1 = AirlockAssembler.assemble(**payload_args)
        payload2 = AirlockAssembler.assemble(**payload_args)

        router = PathRouter()
        path1 = router.select_path(payload1)
        path2 = router.select_path(payload2)

        assert path1 == path2

    def test_priority_order_empty_check_ids_overrides_sanitized(self):
        """Test priority: empty check_ids overrides sanitized."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with [ADMIN] marker",
        )

        # Force empty check_ids even though sanitized
        payload.check_ids = []

        router = PathRouter()
        selected = router.select_path(payload)

        # Should be Path.A due to empty check_ids, not Path.B
        assert selected == Path.A

    def test_priority_order_sanitized_over_single_check_id(self):
        """Test priority: sanitized overrides single check_id."""
        from agentic_core.L0_routing.reasoning.assembly_stage import AirlockAssembler
        from agentic_core.L0_routing.reasoning.path_router import Path, PathRouter

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with [ADMIN] marker",
        )

        # Ensure single check_id but sanitized
        payload.check_ids = ["check1"]

        router = PathRouter()
        selected = router.select_path(payload)

        # Should be Path.B due to sanitized flag, not Path.C
        assert selected == Path.B


@pytest.mark.unit
class TestElevatorShaftSeam:
    """Test Elevator Shaft seam contains no business logic."""

    def test_load_context_jit_returns_empty_dict(self):
        """Test seam returns deterministic empty dict."""
        from agentic_core.L0_routing.utils.elevator_shaft_seam import load_context_jit

        result = load_context_jit("test_trace_id", "test_intent")

        assert result == {}
        assert isinstance(result, dict)

    def test_seam_has_no_forbidden_imports(self):
        """Test seam contains no forbidden imports."""
        import ast

        seam_file = "agentic_core/L0_routing/utils/elevator_shaft_seam.py"

        # Read and parse the seam file
        with open(seam_file, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Check for forbidden imports
        forbidden_imports = ["L2_", "L5_", "datetime", "time"]
        found_forbidden = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(forbidden in alias.name for forbidden in forbidden_imports):
                        found_forbidden.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(forbidden in node.module for forbidden in forbidden_imports):
                    found_forbidden.append(f"from {node.module}")

        assert not found_forbidden, f"Forbidden imports found: {found_forbidden}"

    def test_seam_has_no_routing_logic(self):
        """Test seam contains no routing decision logic."""
        import ast

        seam_file = "agentic_core/L0_routing/utils/elevator_shaft_seam.py"

        with open(seam_file, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Check for control flow statements (routing logic)
        forbidden_nodes = (ast.If, ast.For, ast.While, ast.Try)
        found_nodes = []

        for node in ast.walk(tree):
            if isinstance(node, forbidden_nodes):
                found_nodes.append(type(node).__name__)

        assert not found_nodes, f"Control flow statements found: {found_nodes}"
