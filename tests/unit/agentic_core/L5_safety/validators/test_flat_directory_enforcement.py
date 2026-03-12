"""
Tests for FLAT_DIRECTORIES enforcement.

Validates that validate_flat_directory() correctly rejects files nested
inside directories that must be flat (no subfolders).

[CREATED 2026-02-08] RCA: mixins/contracts/ was not caught because no
validator enforced the "flat" flag in SOVEREIGN_TERRITORIES.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    FLAT_DIRECTORIES,
    validate_flat_directory,
)


class TestFlatDirectories:
    """FLAT_DIRECTORIES constant is correctly defined."""

    def test_mixins_is_flat(self):
        assert "mixins" in FLAT_DIRECTORIES

    def test_base_agents_is_flat(self):
        assert "base_agents" in FLAT_DIRECTORIES

    def test_interfaces_is_flat(self):
        assert "interfaces" in FLAT_DIRECTORIES


class TestValidateFlatDirectory:
    """validate_flat_directory() catches nested files in flat directories."""

    def test_file_directly_in_mixins_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "meta_learning_mixin.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_mixins_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "contracts", "meta_learning_contract.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "mixins"
        assert result["illegal_child"] == "contracts"
        assert "FLAT VIOLATION" in result["message"]

    def test_file_directly_in_base_agents_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "base_agents", "SovereignBaseAgent.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_base_agents_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "base_agents", "legacy", "OldBase.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "base_agents"
        assert result["illegal_child"] == "legacy"

    def test_file_directly_in_interfaces_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "interfaces", "IOrchestratorProtocol.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_interfaces_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "interfaces", "v2", "INewProtocol.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "interfaces"

    def test_pycache_in_flat_dir_is_allowed(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "__pycache__", "foo.cpython-312.pyc")
        assert validate_flat_directory(parts) is None

    def test_non_flat_directory_is_not_checked(self):
        parts = (AGENTIC_CORE_DIR, "L5_safety", "reasoning", "sub", "file.py")
        assert validate_flat_directory(parts) is None

    def test_deeply_nested_flat_violation(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "a", "b", "file.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["illegal_child"] == "a"
