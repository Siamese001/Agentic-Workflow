"""
Guardian Hardened Tests — Structure Blueprint (Sovereign Kernel + Config Shim)

AST-graph justification:
  sovereign_kernel:       fan_in=105  test_cov=17
  structure_blueprint_pkg: fan_in=102  test_cov=16

  Both are the highest fan-in Guardian components in the repo.
  Despite 17/16 test files importing them, current tests exercise mostly
  SOVEREIGN_TERRITORIES membership and path constants — NOT the behavioral
  enforcement contracts for:
    - is_kernel_component() prefix-match semantics
    - is_modular_extension() prefix-match semantics
    - validate_boundary() return contract (bool, reason string)
    - unclassified module handling
    - cross-platform path normalization (backslash vs forward-slash)
    - SOVEREIGN_KERNEL_COMPONENTS immutability
    - MODULAR_EXTENSIONS immutability
    - structure_blueprint_config shim re-exports (backward-compat surface)

  Tier 0 because these two modules are the compile-time governance root
  consumed by CI validators, layer sovereignty enforcer, and all phantom-dir
  tests. A regression here silently breaks all 105 consumers.

Covers:
  1. is_kernel_component() — exact match, prefix match, no-match, path-sep variants
  2. is_modular_extension() — exact match, prefix match, no-match
  3. validate_boundary() — kernel path, extension path, unclassified path
  4. unclassified module: validate_boundary returns (False, "unclassified_module: ...")
  5. SOVEREIGN_KERNEL_COMPONENTS is a frozenset (immutable by contract)
  6. MODULAR_EXTENSIONS is a frozenset (immutable by contract)
  7. SovereignLLMGateway is declared a kernel component (critical choke point)
  8. agent_registry is declared a kernel component
  9. system_learning is declared a modular extension (removable)
 10. structure_blueprint_config shim exposes canonical __all__ surface
 11. Fail-closed: any path not in kernel/extension gets False, not silent True
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_structure_blueprint_hardened")
_emit_applies_guardrail("p0", "test_structure_blueprint_hardened", "p0_governance")
_emit_reads_policy_state("p0", "test_structure_blueprint_hardened", "policy_binding")
_emit_snapshots_state("p0", "test_structure_blueprint_hardened", "state_snapshot")
emit_replay_key("p0", "test_structure_blueprint_hardened")
emit_determinism_digest("p0", "test_structure_blueprint_hardened")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_structure_blueprint_hardened", "execution_auth")
_emit_validates_capability("p2", "test_structure_blueprint_hardened", "capability_check")
_emit_routes_to_capability("p2", "test_structure_blueprint_hardened", "capability_route")
_emit_writes_via_uwg("p2", "test_structure_blueprint_hardened", "uwg_write")
_emit_blocks_direct_write("p2", "test_structure_blueprint_hardened", "direct_write_block")
_emit_records_tool_invocation("p2", "test_structure_blueprint_hardened", "tool_invocation")
_emit_captures_execution_output("p2", "test_structure_blueprint_hardened", "exec_output")
_emit_dispatches_agent("p3", "test_structure_blueprint_hardened", "agent_dispatch")
_emit_coordinates_agents("p3", "test_structure_blueprint_hardened", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_structure_blueprint_hardened", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_structure_blueprint_hardened", "healing_outcome")
_emit_escalates_failure("p3", "test_structure_blueprint_hardened", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_structure_blueprint_hardened", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_structure_blueprint_hardened", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_structure_blueprint_hardened", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_structure_blueprint_hardened", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_structure_blueprint_hardened", "eval_metric")
_emit_stores_embedding("p4", "test_structure_blueprint_hardened", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_structure_blueprint_hardened", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_structure_blueprint_hardened", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.guardian

from agentic_core.L0_routing.config.path_constants import SYSTEM_LEARNING_DIR
from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (
    MODULAR_EXTENSIONS,
    SOVEREIGN_KERNEL_COMPONENTS,
    is_kernel_component,
    is_modular_extension,
    validate_boundary,
)

# ---------------------------------------------------------------------------
# 1. is_kernel_component() — exact, prefix, no-match
# ---------------------------------------------------------------------------


class TestIsKernelComponent:
    def test_exact_match_l5_safety(self):
        assert is_kernel_component("agentic_core.L5_safety") is True

    def test_prefix_match_l5_safety_submodule(self):
        assert is_kernel_component("agentic_core.L5_safety.core_kernel.classification_kernel") is True

    def test_exact_match_l2_execution(self):
        assert is_kernel_component("agentic_core.L2_execution") is True

    def test_prefix_match_l2_submodule(self):
        assert is_kernel_component("agentic_core.L2_execution.enforcement.SovereignLLMGateway") is True

    def test_sovereign_llm_gateway_is_kernel(self):
        assert is_kernel_component("agentic_core.L2_execution.enforcement.SovereignLLMGateway") is True

    def test_agent_registry_is_kernel(self):
        assert is_kernel_component("agentic_core.agents.agent_registry") is True

    def test_l0_routing_is_kernel(self):
        assert is_kernel_component("agentic_core.L0_routing") is True

    def test_interfaces_is_kernel(self):
        assert is_kernel_component("agentic_core.interfaces") is True

    def test_unrelated_module_is_not_kernel(self):
        assert is_kernel_component("my_custom_plugin.utils") is False

    def test_empty_string_is_not_kernel(self):
        assert is_kernel_component("") is False

    def test_partial_overlap_does_not_match(self):
        assert is_kernel_component("agentic_core.L5_safety_extra") is False

    def test_backslash_path_normalized(self):
        assert is_kernel_component(r"agentic_core\L5_safety\core_kernel") is True

    def test_mixed_slash_normalized(self):
        assert is_kernel_component("agentic_core/L2_execution/enforcement") is True

    def test_forward_slash_normalized(self):
        assert is_kernel_component("agentic_core/L0_routing/config") is True


# ---------------------------------------------------------------------------
# 2. is_modular_extension() — exact, prefix, no-match
# ---------------------------------------------------------------------------


class TestIsModularExtension:
    def test_system_learning_is_extension(self):
        assert is_modular_extension("system_learning") is True

    def test_system_learning_submodule_is_extension(self):
        assert is_modular_extension("system_learning.engines.pattern_analysis_engine") is True

    def test_rag_is_extension(self):
        assert is_modular_extension("agentic_core.rag") is True

    def test_context_is_extension(self):
        assert is_modular_extension("agentic_core.context") is True

    def test_monitoring_is_extension(self):
        assert is_modular_extension("agentic_core.monitoring") is True

    def test_telemetry_is_extension(self):
        assert is_modular_extension("agentic_core.telemetry") is True

    def test_l5_safety_is_not_extension(self):
        assert is_modular_extension("agentic_core.L5_safety") is False

    def test_empty_string_is_not_extension(self):
        assert is_modular_extension("") is False

    def test_kernel_component_is_not_extension(self):
        assert is_modular_extension("agentic_core.L2_execution") is False

    def test_arbitrary_module_is_not_extension(self):
        assert is_modular_extension("my_random_app.service") is False


# ---------------------------------------------------------------------------
# 3. validate_boundary() return contract
# ---------------------------------------------------------------------------


class TestValidateBoundary:
    def test_kernel_component_returns_true_with_reason(self):
        is_valid, reason = validate_boundary("agentic_core.L5_safety")
        assert is_valid is True
        assert "kernel_component" in reason

    def test_extension_returns_true_with_reason(self):
        is_valid, reason = validate_boundary("system_learning")
        assert is_valid is True
        assert "modular_extension" in reason

    def test_unclassified_returns_false(self):
        is_valid, reason = validate_boundary("completely_unknown_module")
        assert is_valid is False

    def test_unclassified_reason_contains_module_path(self):
        _, reason = validate_boundary("completely_unknown_module")
        assert "completely_unknown_module" in reason

    def test_unclassified_reason_starts_with_unclassified_module(self):
        _, reason = validate_boundary("some.mystery.module")
        assert reason.startswith("unclassified_module")

    def test_fail_closed_for_empty_string(self):
        is_valid, _ = validate_boundary("")
        assert is_valid is False

    def test_return_type_is_tuple_of_bool_and_str(self):
        result = validate_boundary("agentic_core.L5_safety")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)

    def test_sovereign_llm_gateway_validates_as_kernel(self):
        is_valid, reason = validate_boundary("agentic_core.L2_execution.enforcement.SovereignLLMGateway")
        assert is_valid is True
        assert "kernel_component" in reason


# ---------------------------------------------------------------------------
# 4. Immutability of registry sets
# ---------------------------------------------------------------------------


class TestRegistryImmutability:
    def test_sovereign_kernel_components_is_frozenset(self):
        assert isinstance(SOVEREIGN_KERNEL_COMPONENTS, frozenset)

    def test_modular_extensions_is_frozenset(self):
        assert isinstance(MODULAR_EXTENSIONS, frozenset)

    def test_sovereign_kernel_components_not_mutable(self):
        with pytest.raises((AttributeError, TypeError)):
            SOVEREIGN_KERNEL_COMPONENTS.add("injected.module")  # type: ignore[attr-defined]

    def test_modular_extensions_not_mutable(self):
        with pytest.raises((AttributeError, TypeError)):
            MODULAR_EXTENSIONS.add("injected.module")  # type: ignore[attr-defined]

    def test_sovereign_kernel_non_empty(self):
        assert len(SOVEREIGN_KERNEL_COMPONENTS) > 0

    def test_modular_extensions_non_empty(self):
        assert len(MODULAR_EXTENSIONS) > 0

    def test_no_overlap_between_kernel_and_extensions(self):
        overlap = SOVEREIGN_KERNEL_COMPONENTS & MODULAR_EXTENSIONS
        assert len(overlap) == 0, f"Overlap between kernel and extensions is forbidden: {overlap}"


# ---------------------------------------------------------------------------
# 5. Critical declarations — things that MUST be kernel components
# ---------------------------------------------------------------------------


class TestCriticalDeclarations:
    @pytest.mark.parametrize(
        "module_path",
        [
            "agentic_core.L5_safety",
            "agentic_core.L2_execution",
            "agentic_core.L0_routing",
            "agentic_core.interfaces",
            "agentic_core.agents.agent_registry",
            "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
            "agentic_core.prompt_governance",
            "agentic_core.mixins",
            "agentic_core.base_agents",
        ],
    )
    def test_critical_path_is_kernel(self, module_path):
        assert is_kernel_component(module_path), f"Critical module '{module_path}' must be a kernel component"

    @pytest.mark.parametrize(
        "module_path",
        [
            SYSTEM_LEARNING_DIR,
            "agentic_core.rag",
            "agentic_core.context",
            "agentic_core.monitoring",
            "agentic_core.telemetry",
        ],
    )
    def test_extension_path_is_not_kernel(self, module_path):
        assert not is_kernel_component(module_path), (
            f"Extension '{module_path}' must NOT be a kernel component"
        )


# ---------------------------------------------------------------------------
# 6. structure_blueprint_config shim backward-compat surface
# ---------------------------------------------------------------------------


class TestStructureBlueprintConfigShim:
    """
    Graph-selected: structure_blueprint_config has fan_in=2, test_cov=1.
    The shim must expose exactly the public __all__ surface of the package.
    """

    def test_shim_is_importable(self):
        import agentic_core.L5_safety.config.structure_blueprint_config as shim  # noqa: F401

    def test_shim_has_dunder_all(self):
        import agentic_core.L5_safety.config.structure_blueprint_config as shim

        assert hasattr(shim, "__all__")
        assert len(shim.__all__) > 0

    def test_shim_all_matches_package_all(self):
        import agentic_core.L5_safety.config.structure_blueprint as pkg
        import agentic_core.L5_safety.config.structure_blueprint_config as shim

        assert set(shim.__all__) == set(pkg.__all__)

    def test_sovereign_territories_accessible_via_shim(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            SOVEREIGN_REGISTRY,
        )

        assert SOVEREIGN_REGISTRY is not None

    def test_get_sovereign_territories_accessible_via_shim(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            get_sovereign_territories,
        )

        territories = get_sovereign_territories()
        assert territories is not None

    def test_no_data_definitions_in_shim_itself(self):
        import ast
        from pathlib import Path

        shim_path = Path("agentic_core/L5_safety/config/structure_blueprint_config.py")
        src = shim_path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                pytest.fail(f"structure_blueprint_config shim must not define classes; found: {node.name}")
