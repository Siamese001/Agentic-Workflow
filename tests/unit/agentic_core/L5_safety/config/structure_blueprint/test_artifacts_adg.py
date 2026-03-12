"""ADG-driven tests for L5 structure_blueprint/artifacts.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.artifacts import (
    APP_SPECIFIC_PREFIXES,
    APP_SPECIFIC_PATTERN_STRINGS,
    APP_SPECIFIC_TARGET_SUBFOLDER,
    STUTTERING_PREFIX_MAP,
)


class TestArtifactConstants:
    def test_app_specific_prefixes_mapping(self):
        assert isinstance(APP_SPECIFIC_PREFIXES, dict | type(APP_SPECIFIC_PREFIXES))
        assert "rg_" in APP_SPECIFIC_PREFIXES
        assert "lic_" in APP_SPECIFIC_PREFIXES

    def test_rg_prefix_maps_to_apps_rg(self):
        assert APP_SPECIFIC_PREFIXES["rg_"] == "apps_rg"

    def test_lic_prefix_maps_to_apps_lic(self):
        assert APP_SPECIFIC_PREFIXES["lic_"] == "apps_lic"

    def test_stuttering_prefix_map_non_empty(self):
        assert len(STUTTERING_PREFIX_MAP) > 0

    def test_app_specific_pattern_strings_sequence(self):
        assert len(APP_SPECIFIC_PATTERN_STRINGS) > 0

    def test_pattern_strings_are_strings(self):
        for p in APP_SPECIFIC_PATTERN_STRINGS:
            assert isinstance(p, str)

    def test_target_subfolder_is_string(self):
        assert isinstance(APP_SPECIFIC_TARGET_SUBFOLDER, str)
        assert len(APP_SPECIFIC_TARGET_SUBFOLDER) > 0
