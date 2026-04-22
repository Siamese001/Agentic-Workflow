"""Behavioral tests for ``agentic_core.L5_safety.config.structure_blueprint.derived``.

Covers the derived registries that are computed lazily from SOVEREIGN_TERRITORIES:
- DEPTH_RULES: dict[territory → int], non-empty, every value is a positive int.
- CORE_SUBFOLDER_MAP: populated with L0..L6 layer keys and their subfolder lists.
- SUBFOLDER_METADATA: every key carries purpose/content_types/execution_allowed/notes.
- APPS_{RG,LIC,SHARED,EVAL,EXEC,RESEARCH,RFP}_SUBFOLDER_MAP: all are Mappings.
- agentic_core_registry is the same object as CORE_SUBFOLDER_MAP.
- L4_SUBFOLDER_MAP: known keys present (dashboards, reasoning, enforcement, …).
- L4_APPROVED_FOLDERS is frozenset containing L5 safety folders.
- SCRIPTS_PLACEMENT_RULES: root_ops_scripts forbids agentic_core imports.
- TESTS_SUBFOLDER_MAP equals TESTS_L2_SUBFOLDER_MAP.
- verify_derived_registries returns a list[str] (empty on healthy state).
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from agentic_core.L5_safety.config.structure_blueprint import derived as mod
from agentic_core.L5_safety.config.structure_blueprint.derived import (
    APPS_EVAL_SUBFOLDER_MAP,
    APPS_EXEC_SUBFOLDER_MAP,
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RESEARCH_SUBFOLDER_MAP,
    APPS_RFP_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    DEPTH_RULES,
    L4_APPROVED_FOLDERS,
    L4_SUBFOLDER_MAP,
    SCRIPTS_PLACEMENT_RULES,
    SUBFOLDER_METADATA,
    TESTS_L2_SUBFOLDER_MAP,
    TESTS_SUBFOLDER_MAP,
    agentic_core_registry,
    verify_derived_registries,
)


# ---- DEPTH_RULES -------------------------------------------------------

class TestDepthRules:
    def test_all_values_non_negative_int(self) -> None:
        """Depth rules are non-negative integers (0 = root, >0 = nested)."""
        for name, depth in DEPTH_RULES.items():
            assert isinstance(depth, int), f"{name} depth is {type(depth).__name__}"
            assert depth >= 0, f"{name} depth is {depth}"

    def test_is_mapping(self) -> None:
        assert isinstance(DEPTH_RULES, Mapping)


# ---- CORE_SUBFOLDER_MAP ------------------------------------------------

class TestCoreSubfolderMap:
    def test_is_mapping(self) -> None:
        assert isinstance(CORE_SUBFOLDER_MAP, Mapping)

    def test_values_are_sequences(self) -> None:
        for layer, subs in CORE_SUBFOLDER_MAP.items():
            assert hasattr(subs, "__iter__"), f"{layer} subfolders not iterable"


# ---- SUBFOLDER_METADATA ------------------------------------------------

class TestSubfolderMetadata:
    def test_is_mapping(self) -> None:
        assert isinstance(SUBFOLDER_METADATA, Mapping)

    def test_every_entry_has_full_record(self) -> None:
        """If a metadata entry exists it MUST have the full record shape."""
        for key, meta in SUBFOLDER_METADATA.items():
            assert "purpose" in meta, f"{key} missing 'purpose'"
            assert "content_types" in meta, f"{key} missing 'content_types'"
            assert "execution_allowed" in meta, f"{key} missing 'execution_allowed'"
            assert "notes" in meta, f"{key} missing 'notes'"

    def test_execution_allowed_is_bool(self) -> None:
        for key, meta in SUBFOLDER_METADATA.items():
            assert isinstance(meta["execution_allowed"], bool), (
                f"{key} execution_allowed is {type(meta['execution_allowed']).__name__}"
            )


# ---- Apps subfolder maps -----------------------------------------------

class TestAppsSubfolderMaps:
    @pytest.mark.parametrize("reg", [
        APPS_RG_SUBFOLDER_MAP, APPS_LIC_SUBFOLDER_MAP, APPS_SHARED_SUBFOLDER_MAP,
        APPS_EVAL_SUBFOLDER_MAP, APPS_EXEC_SUBFOLDER_MAP,
        APPS_RESEARCH_SUBFOLDER_MAP, APPS_RFP_SUBFOLDER_MAP,
    ])
    def test_is_mapping(self, reg: object) -> None:
        assert isinstance(reg, Mapping)


# ---- agentic_core_registry alias --------------------------------------

class TestRegistryAlias:
    def test_is_same_object(self) -> None:
        assert agentic_core_registry is CORE_SUBFOLDER_MAP


# ---- L4_SUBFOLDER_MAP --------------------------------------------------

class TestL4SubfolderMap:
    @pytest.mark.parametrize("key", [
        "dashboards", "reasoning", "scripts", "enforcement",
        "L1_reasoning", "L2_reasoning", "L3_reasoning",
        "L5_enforcement", "L6_dashboards",
        "prompt_governance",
    ])
    def test_key_present(self, key: str) -> None:
        assert key in L4_SUBFOLDER_MAP

    def test_dashboards_has_expected_subkeys(self) -> None:
        d = L4_SUBFOLDER_MAP["dashboards"]
        assert "generators" in d
        assert "templates" in d
        assert "tests" in d


# ---- L4_APPROVED_FOLDERS ----------------------------------------------

class TestL4ApprovedFolders:
    def test_is_frozenset(self) -> None:
        assert isinstance(L4_APPROVED_FOLDERS, frozenset)

    def test_contains_core_safety_paths(self) -> None:
        assert "agentic_core/L5_safety/enforcement" in L4_APPROVED_FOLDERS
        assert "agentic_core/L5_safety/validators" in L4_APPROVED_FOLDERS

    def test_contains_l4_state_memory(self) -> None:
        # Referenced by external callers — don't accidentally remove.
        assert "agentic_core/L4_state/memory" in L4_APPROVED_FOLDERS


# ---- SCRIPTS_PLACEMENT_RULES ------------------------------------------

class TestScriptsPlacementRules:
    def test_root_ops_scripts_forbids_agentic_core(self) -> None:
        r = SCRIPTS_PLACEMENT_RULES["root_ops_scripts"]
        assert "agentic_core" in r["forbidden_imports"]
        assert r["allowed_depth"] == 1

    def test_l0_maintenance_scripts_has_core_access(self) -> None:
        r = SCRIPTS_PLACEMENT_RULES["l0_maintenance_scripts"]
        assert "core_access" in r["required_capabilities"]


# ---- TESTS subfolder maps ---------------------------------------------

class TestTestsSubfolderMaps:
    def test_alias_identity(self) -> None:
        assert TESTS_SUBFOLDER_MAP is TESTS_L2_SUBFOLDER_MAP

    def test_is_mapping(self) -> None:
        assert isinstance(TESTS_SUBFOLDER_MAP, Mapping)


# ---- verify_derived_registries ---------------------------------------

class TestVerifyDerivedRegistries:
    def test_returns_list(self) -> None:
        result = verify_derived_registries()
        assert isinstance(result, list)

    def test_entries_are_strings(self) -> None:
        result = verify_derived_registries()
        for entry in result:
            assert isinstance(entry, str)


# ---- Derivation functions (private) ----------------------------------

class TestDerivationFunctions:
    def test_derive_depth_rules_matches_registry(self) -> None:
        assert mod._derive_depth_rules() == dict(DEPTH_RULES)

    def test_derive_core_subfolder_map_matches_registry(self) -> None:
        # Cast Sequence values to list for equality
        result = mod._derive_core_subfolder_map()
        assert set(result.keys()) == set(CORE_SUBFOLDER_MAP.keys())

    def test_derive_apps_subfolder_map_unknown_territory_empty(self) -> None:
        assert mod._derive_apps_subfolder_map("no-such-territory") == {}
