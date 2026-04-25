"""Tests for structure_blueprint_data.py module.

This module contains only literal constants (no functions or classes).
Tests verify that the constants exist and have expected types.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.config.structure_blueprint_data import (
    # Folder purity rules
    FOLDER_PURITY_RULES,
    # Layer keyword affinity
    LAYER_KEYWORD_AFFINITY,
    # App domain prefixes
    APP_DOMAIN_PREFIXES,
    # Suffix to folder mapping
    SUFFIX_TO_FOLDER,
    # AST placement signals
    AST_PLACEMENT_SIGNALS,
    # Forensic discovery
    FORENSIC_DISCOVERY_SCRIPT,
    FORENSIC_DISCOVERY_INTEGRITY_HASH,
    # Layer prefix pattern
    LAYER_PREFIX_PATTERN,
    # Interface pattern
    INTERFACE_FILENAME_PATTERN,
    # Global interfaces folder
    GLOBAL_INTERFACES_FOLDER,
    # Canonical location priority
    CANONICAL_LOCATION_PRIORITY,
    # Compound suffix conflicts
    COMPOUND_SUFFIX_CONFLICTS,
    # Filetype to folder
    FILETYPE_TO_FOLDER,
    # Forbidden ephemeral patterns
    FORBIDDEN_EPHEMERAL_PATTERNS,
    # Ephemeral pattern exemptions
    EPHEMERAL_PATTERN_EXEMPTIONS,
    # Duplicate detection exempt
    DUPLICATE_DETECTION_EXEMPT,
    # L5 subprocess allowlist
    L5_SUBPROCESS_ALLOWLIST,
    # L6 hybrid allowlist
    L6_HYBRID_ALLOWLIST,
    # Scripts forbidden patterns
    SCRIPTS_FORBIDDEN_PATTERNS,
)


class TestFolderPurityRules:
    """Tests for FOLDER_PURITY_RULES constant."""

    def test_folder_purity_rules_exists(self):
        """Test that FOLDER_PURITY_RULES constant exists."""
        assert FOLDER_PURITY_RULES is not None

    def test_folder_purity_rules_is_dict(self):
        """Test that FOLDER_PURITY_RULES is a dict."""
        assert isinstance(FOLDER_PURITY_RULES, dict)

    def test_folder_purity_rules_has_expected_keys(self):
        """Test that FOLDER_PURITY_RULES has expected structure."""
        # Should contain keys for different folder types
        for key in FOLDER_PURITY_RULES:
            assert isinstance(key, str)
            assert isinstance(FOLDER_PURITY_RULES[key], (str, list, dict))


class TestAppDomainPrefixes:
    """Tests for APP_DOMAIN_PREFIXES constant."""

    def test_app_domain_prefixes_exists(self):
        """Test that APP_DOMAIN_PREFIXES constant exists."""
        assert APP_DOMAIN_PREFIXES is not None

    def test_app_domain_prefixes_is_sequence(self):
        """Test that APP_DOMAIN_PREFIXES is a sequence."""
        assert isinstance(APP_DOMAIN_PREFIXES, (list, tuple))

    def test_app_domain_prefixes_has_strings(self):
        """Test that APP_DOMAIN_PREFIXES contains strings."""
        for prefix in APP_DOMAIN_PREFIXES:
            assert isinstance(prefix, str)


class TestLayerKeywordAffinity:
    """Tests for LAYER_KEYWORD_AFFINITY constant."""

    def test_layer_keyword_affinity_exists(self):
        """Test that LAYER_KEYWORD_AFFINITY constant exists."""
        assert LAYER_KEYWORD_AFFINITY is not None

    def test_layer_keyword_affinity_is_mapping(self):
        """Test that LAYER_KEYWORD_AFFINITY is a mapping."""
        assert isinstance(LAYER_KEYWORD_AFFINITY, dict)

    def test_layer_keyword_affinity_has_layer_keys(self):
        """Test that LAYER_KEYWORD_AFFINITY has layer keys."""
        for key in LAYER_KEYWORD_AFFINITY:
            assert isinstance(key, str)
            # Keys should be layer identifiers (L0_routing, L1_cognition, etc.)
            assert key.startswith("L")


class TestSuffixToFolder:
    """Tests for SUFFIX_TO_FOLDER constant."""

    def test_suffix_to_folder_exists(self):
        """Test that SUFFIX_TO_FOLDER constant exists."""
        assert SUFFIX_TO_FOLDER is not None

    def test_suffix_to_folder_is_mapping(self):
        """Test that SUFFIX_TO_FOLDER is a mapping."""
        assert isinstance(SUFFIX_TO_FOLDER, dict)

    def test_suffix_to_folder_has_string_values(self):
        """Test that SUFFIX_TO_FOLDER has string values."""
        for suffix, folder in SUFFIX_TO_FOLDER.items():
            assert isinstance(suffix, str)
            assert isinstance(folder, str)


class TestASTPlacementSignals:
    """Tests for AST_PLACEMENT_SIGNALS constant."""

    def test_ast_placement_signals_exists(self):
        """Test that AST_PLACEMENT_SIGNALS constant exists."""
        assert AST_PLACEMENT_SIGNALS is not None

    def test_ast_placement_signals_is_sequence(self):
        """Test that AST_PLACEMENT_SIGNALS is a sequence."""
        assert isinstance(AST_PLACEMENT_SIGNALS, (list, tuple))

    def test_ast_placement_signals_has_strings(self):
        """Test that AST_PLACEMENT_SIGNALS contains strings."""
        for signal in AST_PLACEMENT_SIGNALS:
            assert isinstance(signal, str)


class TestForensicDiscovery:
    """Tests for forensic discovery constants."""

    def test_forensic_discovery_script_exists(self):
        """Test that FORENSIC_DISCOVERY_SCRIPT constant exists."""
        assert FORENSIC_DISCOVERY_SCRIPT is not None

    def test_forensic_discovery_script_is_string(self):
        """Test that FORENSIC_DISCOVERY_SCRIPT is a string."""
        assert isinstance(FORENSIC_DISCOVERY_SCRIPT, str)

    def test_forensic_discovery_integrity_hash_exists(self):
        """Test that FORENSIC_DISCOVERY_INTEGRITY_HASH constant exists."""
        assert FORENSIC_DISCOVERY_INTEGRITY_HASH is not None

    def test_forensic_discovery_integrity_hash_is_string(self):
        """Test that FORENSIC_DISCOVERY_INTEGRITY_HASH is a string."""
        assert isinstance(FORENSIC_DISCOVERY_INTEGRITY_HASH, str)
        # Should be a hex string
        assert len(FORENSIC_DISCOVERY_INTEGRITY_HASH) == 64  # SHA256 hex length


class TestLayerPrefixPattern:
    """Tests for LAYER_PREFIX_PATTERN constant."""

    def test_layer_prefix_pattern_exists(self):
        """Test that LAYER_PREFIX_PATTERN constant exists."""
        assert LAYER_PREFIX_PATTERN is not None

    def test_layer_prefix_pattern_is_string(self):
        """Test that LAYER_PREFIX_PATTERN is a string."""
        assert isinstance(LAYER_PREFIX_PATTERN, str)


class TestInterfacePattern:
    """Tests for interface pattern constants."""

    def test_interface_filename_pattern_exists(self):
        """Test that INTERFACE_FILENAME_PATTERN constant exists."""
        assert INTERFACE_FILENAME_PATTERN is not None

    def test_interface_filename_pattern_is_string(self):
        """Test that INTERFACE_FILENAME_PATTERN is a string."""
        assert isinstance(INTERFACE_FILENAME_PATTERN, str)

    def test_global_interfaces_folder_exists(self):
        """Test that GLOBAL_INTERFACES_FOLDER constant exists."""
        assert GLOBAL_INTERFACES_FOLDER is not None

    def test_global_interfaces_folder_is_string(self):
        """Test that GLOBAL_INTERFACES_FOLDER is a string."""
        assert isinstance(GLOBAL_INTERFACES_FOLDER, str)


class TestCanonicalLocationPriority:
    """Tests for CANONICAL_LOCATION_PRIORITY constant."""

    def test_canonical_location_priority_exists(self):
        """Test that CANONICAL_LOCATION_PRIORITY constant exists."""
        assert CANONICAL_LOCATION_PRIORITY is not None

    def test_canonical_location_priority_is_sequence(self):
        """Test that CANONICAL_LOCATION_PRIORITY is a sequence."""
        assert isinstance(CANONICAL_LOCATION_PRIORITY, (list, tuple))


class TestEphemeralPatterns:
    """Tests for ephemeral pattern constants."""

    def test_forbidden_ephemeral_patterns_exists(self):
        """Test that FORBIDDEN_EPHEMERAL_PATTERNS constant exists."""
        assert FORBIDDEN_EPHEMERAL_PATTERNS is not None

    def test_forbidden_ephemeral_patterns_is_sequence(self):
        """Test that FORBIDDEN_EPHEMERAL_PATTERNS is a sequence."""
        assert isinstance(FORBIDDEN_EPHEMERAL_PATTERNS, (list, tuple))

    def test_ephemeral_pattern_exemptions_exists(self):
        """Test that EPHEMERAL_PATTERN_EXEMPTIONS constant exists."""
        assert EPHEMERAL_PATTERN_EXEMPTIONS is not None

    def test_ephemeral_pattern_exemptions_is_sequence(self):
        """Test that EPHEMERAL_PATTERN_EXEMPTIONS is a sequence."""
        assert isinstance(EPHEMERAL_PATTERN_EXEMPTIONS, (list, tuple))


class TestCompoundSuffixConflicts:
    """Tests for COMPOUND_SUFFIX_CONFLICTS constant."""

    def test_compound_suffix_conflicts_exists(self):
        """Test that COMPOUND_SUFFIX_CONFLICTS constant exists."""
        assert COMPOUND_SUFFIX_CONFLICTS is not None

    def test_compound_suffix_conflicts_is_sequence(self):
        """Test that COMPOUND_SUFFIX_CONFLICTS is a sequence."""
        assert isinstance(COMPOUND_SUFFIX_CONFLICTS, (list, tuple))

    def test_compound_suffix_conflicts_has_tuples(self):
        """Test that COMPOUND_SUFFIX_CONFLICTS contains tuples."""
        for conflict in COMPOUND_SUFFIX_CONFLICTS:
            assert isinstance(conflict, tuple)
            assert len(conflict) == 4


class TestFiletypeToFolder:
    """Tests for FILETYPE_TO_FOLDER constant."""

    def test_filetype_to_folder_exists(self):
        """Test that FILETYPE_TO_FOLDER constant exists."""
        assert FILETYPE_TO_FOLDER is not None

    def test_filetype_to_folder_is_mapping(self):
        """Test that FILETYPE_TO_FOLDER is a mapping."""
        assert isinstance(FILETYPE_TO_FOLDER, dict)


class TestDuplicateDetectionExempt:
    """Tests for DUPLICATE_DETECTION_EXEMPT constant."""

    def test_duplicate_detection_exempt_exists(self):
        """Test that DUPLICATE_DETECTION_EXEMPT constant exists."""
        assert DUPLICATE_DETECTION_EXEMPT is not None

    def test_duplicate_detection_exempt_is_sequence(self):
        """Test that DUPLICATE_DETECTION_EXEMPT is a sequence."""
        assert isinstance(DUPLICATE_DETECTION_EXEMPT, (list, tuple))


class TestAllowlistConstants:
    """Tests for allowlist constants."""

    def test_l5_subprocess_allowlist_exists(self):
        """Test that L5_SUBPROCESS_ALLOWLIST constant exists."""
        assert L5_SUBPROCESS_ALLOWLIST is not None

    def test_l5_subprocess_allowlist_is_sequence(self):
        """Test that L5_SUBPROCESS_ALLOWLIST is a sequence."""
        assert isinstance(L5_SUBPROCESS_ALLOWLIST, (list, tuple))

    def test_l6_hybrid_allowlist_exists(self):
        """Test that L6_HYBRID_ALLOWLIST constant exists."""
        assert L6_HYBRID_ALLOWLIST is not None

    def test_l6_hybrid_allowlist_is_sequence(self):
        """Test that L6_HYBRID_ALLOWLIST is a sequence."""
        assert isinstance(L6_HYBRID_ALLOWLIST, (list, tuple))


class TestScriptsForbiddenPatterns:
    """Tests for SCRIPTS_FORBIDDEN_PATTERNS constant."""

    def test_scripts_forbidden_patterns_exists(self):
        """Test that SCRIPTS_FORBIDDEN_PATTERNS constant exists."""
        assert SCRIPTS_FORBIDDEN_PATTERNS is not None

    def test_scripts_forbidden_patterns_is_sequence(self):
        """Test that SCRIPTS_FORBIDDEN_PATTERNS is a sequence."""
        assert isinstance(SCRIPTS_FORBIDDEN_PATTERNS, (list, tuple))


class TestConstantImmutability:
    """Tests for constant immutability."""

    def test_constants_are_immutable_strings(self):
        """Test that string constants are immutable."""
        # String constants are inherently immutable in Python
        assert isinstance(FORENSIC_DISCOVERY_SCRIPT, str)
        assert isinstance(LAYER_PREFIX_PATTERN, str)

    def test_constants_are_immutable_dicts(self):
        """Test that dict constants can be read but modification is discouraged."""
        # While dicts are mutable in Python, these constants should be treated as read-only
        original_rules = FOLDER_PURITY_RULES.copy()
        assert FOLDER_PURITY_RULES == original_rules
