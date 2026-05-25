"""Drift test for ``system_learning.v6_contract_map``.

Asserts every module dotted-path named in the V6 contract map is importable
in the current repo. This catches:

- engines renamed without updating the map
- engines moved between layers without updating the map
- typos in the map itself
"""

from __future__ import annotations

import importlib.util

import pytest

from agentic_core.L6_system_learning.v6_contract_map import (
    V6_CONTRACT_MAP,
    V6PhaseContract,
    all_modules,
    phase_for_module,
)

EXPECTED_PHASE_IDS = (
    "S1A", "S1B", "S1C",
    "S2A", "S2B", "S2C", "S2D",
    "S3A", "S3B", "S3C",
    "S4A", "S4B", "S4C", "S4D",
)


class TestContractMapShape:
    def test_all_14_phases_present(self):
        assert tuple(V6_CONTRACT_MAP.keys()) == EXPECTED_PHASE_IDS

    def test_each_row_is_v6phasecontract(self):
        for row in V6_CONTRACT_MAP.values():
            assert isinstance(row, V6PhaseContract)
            assert row.phase_id and row.title and row.contract_description
            assert isinstance(row.modules, tuple)
            assert len(row.modules) >= 1

    def test_no_empty_module_lists(self):
        empty = [pid for pid, row in V6_CONTRACT_MAP.items() if not row.modules]
        assert empty == [], f"phases with empty module list: {empty}"

    def test_map_is_frozen(self):
        with pytest.raises(TypeError):
            V6_CONTRACT_MAP["X"] = None  # type: ignore[index]


class TestContractMapDrift:
    @pytest.mark.parametrize("dotted", list(all_modules()))
    def test_module_importable(self, dotted: str):
        spec = importlib.util.find_spec(dotted)
        assert spec is not None, (
            f"v6 contract names {dotted!r} but it is not importable. "
            f"Either restore the module or update v6_contract_map.py."
        )


class TestPhaseForModule:
    def test_known_module_resolves_to_correct_phase(self):
        phases = phase_for_module("agentic_core.L6_system_learning.engines.rca_engine")
        assert "S3B" in phases

    def test_shared_module_appears_in_multiple_phases(self):
        # meta_learning_replay_binding is named in both S1B (lineage binder)
        # and S4D (replay binding).
        phases = phase_for_module(
            "agentic_core.L6_system_learning.engines.meta_learning_replay_binding"
        )
        assert "S1B" in phases
        assert "S4D" in phases

    def test_unknown_module_returns_empty(self):
        assert phase_for_module("agentic_core.L6_system_learning.engines.does_not_exist") == ()
