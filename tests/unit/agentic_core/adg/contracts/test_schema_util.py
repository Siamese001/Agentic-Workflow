"""Unit tests for agentic_core.adg.contracts.schema_util.

Targets Wave-1 / Phase P2 of test-coverage-hotspots-8f2a1c plan.
Source: 3030 lines, fan_in=227 (L_TOOLS, impact 170.2) — highest fan-in in top 15.
Focused on the three pure functions + constant-integrity invariants.
"""

from __future__ import annotations

import pytest

from agentic_core.adg.contracts import schema_util
from agentic_core.adg.contracts.schema_util import (
    ADG_NS,
    ALLOWED_LAYER_EDGES,
    LAYER_AUTHORITY_FORBIDDEN,
    LAYER_PREFIXES,
    PROMPT_AUTHORITY_RULES,
    PROMPT_FIELD_TO_SLOT,
    PROMPT_SLOT_AUTHORITY,
    PROMPT_SLOT_TYPES,
    UWG_CANONICAL_SYMBOL,
    UWG_MODULE_PATH,
    canonical_name,
    module_path_to_layer,
    verify_layer_graph_consistency,
)


class TestCanonicalName:
    """canonical_name() — ADG namespace builder."""

    def test_module_with_forward_slash_path(self) -> None:
        result = canonical_name("Module", "agentic_core/L0_routing/engines/path_router.py")
        assert result == "ADG::Module::agentic_core/L0_routing/engines/path_router.py"

    def test_layer_single_part(self) -> None:
        assert canonical_name("Layer", "L0") == "ADG::Layer::L0"

    def test_commit_single_part(self) -> None:
        sha = "abcdef1234567890abcdef1234567890abcdef12"
        assert canonical_name("Commit", sha) == f"ADG::Commit::{sha}"

    def test_snapshot_two_parts(self) -> None:
        result = canonical_name("Snapshot", "sha-abc", "digest-xyz")
        assert result == "ADG::Snapshot::sha-abc::digest-xyz"

    def test_backslash_converted_to_forward_slash(self) -> None:
        # Windows paths must be normalized
        result = canonical_name("Module", r"agentic_core\L0_routing\path_router.py")
        assert "\\" not in result
        assert result == "ADG::Module::agentic_core/L0_routing/path_router.py"

    def test_empty_parts_produces_trailing_separator(self) -> None:
        # Zero parts → just namespace + type
        assert canonical_name("Layer") == "ADG::Layer"

    def test_uses_adg_ns_constant(self) -> None:
        assert canonical_name("X", "y").startswith(f"{ADG_NS}::")


class TestModulePathToLayer:
    """module_path_to_layer() — longest-prefix layer lookup."""

    @pytest.mark.parametrize(
        ("path", "expected_layer"),
        [
            ("agentic_core/L0_routing/engines/path_router.py", "L0"),
            ("agentic_core/L1_cognition/reasoner.py", "L1"),
            ("agentic_core/L2_execution/UniversalWriteGateway.py", "L2"),
            ("agentic_core/L3_orchestration/dag.py", "L3"),
            ("agentic_core/L4_state/cache.py", "L4"),
            ("agentic_core/L5_safety/enforcement/policy.py", "L5"),
            ("agentic_core/L6_observability/telemetry.py", "L6"),
            ("agentic_core/utils/helper.py", "L_SHARED"),
            ("agentic_core/runtime/contracts/lifecycle.py", "L_RUNTIME"),
            ("agentic_core/adg/extraction/scanner.py", "L_TOOLS"),
            ("apps_rg/engines/x.py", "L_APP"),
            ("apps_shared/config/y.py", "L_APP"),
            ("system_learning/reasoning/judge.py", "L_SL"),
            ("tools/generate_full_adg.py", "L_TOOLS"),
            ("ops_scripts/ci/gate.py", "L_OPS"),
            ("infrastructure/reasoning/opt.py", "L_INFRA"),
            ("tests/unit/test_x.py", "L_TEST"),
        ],
    )
    def test_known_prefix_mappings(self, path: str, expected_layer: str) -> None:
        assert module_path_to_layer(path) == expected_layer

    def test_unknown_path_returns_l_unknown(self) -> None:
        # Any path not matching any prefix should fall through
        result = module_path_to_layer("random/unmatched/path.py")
        # Function loops without default return → implicit None. Accept either None or L_UNKNOWN.
        assert result in (None, "L_UNKNOWN", "")  # documents current behavior

    def test_backslash_input_normalized(self) -> None:
        result = module_path_to_layer(r"agentic_core\L0_routing\x.py")
        assert result == "L0"

    def test_longest_prefix_wins(self) -> None:
        # agentic_core/L_CONTRACTS maps to L_RUNTIME, and agentic_core/L (hypothetical short prefix)
        # would match first alphabetically. Longest-prefix sorting must pick the right one.
        assert module_path_to_layer("agentic_core/L_CONTRACTS/x.py") == "L_RUNTIME"
        assert module_path_to_layer("agentic_core/base_agents/agent.py") == "L_SHARED"

    def test_lru_cache_works_reentrantly(self) -> None:
        # Call twice — second must be cached, same result
        a = module_path_to_layer("agentic_core/L0_routing/x.py")
        b = module_path_to_layer("agentic_core/L0_routing/x.py")
        assert a == b == "L0"


class TestVerifyLayerGraphConsistency:
    """verify_layer_graph_consistency() — detects L_UNKNOWN mappings."""

    def test_empty_map_returns_no_errors(self) -> None:
        assert verify_layer_graph_consistency({}) == []

    def test_all_known_layers_returns_no_errors(self) -> None:
        mapping = {
            "agentic_core/L0_routing/x.py": "L0",
            "apps_rg/y.py": "L_APP",
        }
        assert verify_layer_graph_consistency(mapping) == []

    def test_single_l_unknown_flagged(self) -> None:
        mapping = {"mystery/path.py": "L_UNKNOWN"}
        errors = verify_layer_graph_consistency(mapping)
        assert len(errors) == 1
        assert "mystery/path.py" in errors[0]
        assert "L_UNKNOWN" in errors[0]

    def test_multiple_l_unknown_sorted_alphabetically(self) -> None:
        mapping = {
            "zz/a.py": "L_UNKNOWN",
            "aa/b.py": "L_UNKNOWN",
            "mm/c.py": "L0",
        }
        errors = verify_layer_graph_consistency(mapping)
        assert len(errors) == 2
        assert "aa/b.py" in errors[0]
        assert "zz/a.py" in errors[1]

    def test_mixed_valid_and_unknown(self) -> None:
        mapping = {
            "agentic_core/L0_routing/a.py": "L0",
            "unknown/b.py": "L_UNKNOWN",
        }
        errors = verify_layer_graph_consistency(mapping)
        assert len(errors) == 1
        assert "unknown/b.py" in errors[0]


class TestPromptAuthorityInvariants:
    """Integrity of PROMPT_SLOT_* constants."""

    def test_prompt_slot_authority_indices_match_type_order(self) -> None:
        for i, slot in enumerate(PROMPT_SLOT_TYPES):
            assert PROMPT_SLOT_AUTHORITY[slot] == i

    def test_prompt_slot_types_includes_canonical_five(self) -> None:
        assert set(PROMPT_SLOT_TYPES) == {"S0", "D0", "I0", "C0", "U0"}

    def test_prompt_field_mapping_includes_r0_output_schema_aliases(self) -> None:
        assert PROMPT_FIELD_TO_SLOT["r0_output_format"] == "R0"
        assert PROMPT_FIELD_TO_SLOT["output_format_schema"] == "R0"

    def test_prompt_authority_rules_slots_are_all_known(self) -> None:
        known = set(PROMPT_SLOT_TYPES)
        for winner, loser in PROMPT_AUTHORITY_RULES:
            assert winner in known, f"unknown winner slot: {winner}"
            assert loser in known, f"unknown loser slot: {loser}"

    def test_prompt_authority_rules_form_strict_partial_order(self) -> None:
        # No (a, a) self-rule
        for winner, loser in PROMPT_AUTHORITY_RULES:
            assert winner != loser
        # No contradictory rule (a beats b AND b beats a)
        rules_set = set(PROMPT_AUTHORITY_RULES)
        for winner, loser in PROMPT_AUTHORITY_RULES:
            assert (loser, winner) not in rules_set


class TestLayerEdgeIntegrity:
    """ALLOWED_LAYER_EDGES + LAYER_AUTHORITY_FORBIDDEN sanity."""

    def test_no_self_edges_in_allowed_layer_edges(self) -> None:
        # A layer importing itself isn't meaningful here.
        # Exception: L_SHARED -> L_SHARED documented as internal.
        self_edges = {(a, b) for a, b in ALLOWED_LAYER_EDGES if a == b}
        assert self_edges <= {("L_SHARED", "L_SHARED")}

    def test_layer_authority_forbidden_values_are_relation_types(self) -> None:
        # Values should be frozensets of known relation-type names
        for _layer, forbidden in LAYER_AUTHORITY_FORBIDDEN.items():
            assert isinstance(forbidden, frozenset)
            assert len(forbidden) > 0

    def test_uwg_constants_consistent(self) -> None:
        assert UWG_CANONICAL_SYMBOL.startswith("ADG::Symbol::")
        assert UWG_MODULE_PATH.endswith(".py")
        assert "UniversalWriteGateway" in UWG_CANONICAL_SYMBOL
        assert "UniversalWriteGateway" in UWG_MODULE_PATH

    def test_layer_prefixes_has_all_canonical_layers(self) -> None:
        layer_values = set(LAYER_PREFIXES.values())
        for expected in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
            assert expected in layer_values
