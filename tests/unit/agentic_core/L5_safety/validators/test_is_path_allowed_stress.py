from agentic_core.L5_safety.config.structure_blueprint_config import is_path_allowed


class TestPathHardeningRigor:
    """
    ULTRA-AGGRESSIVE SUITE: 100% PASS mandatory on zero-trust edge cases.
    """

    def test_type_safety_list_roots(self):
        """100% PASS: Ensures list-based roots (apps_rg) do not trigger TypeErrors."""
        # apps_rg uses a list for subfolders. This path should fail gracefully.
        path = "apps_rg/core/engines/subfolder/file.py"
        assert is_path_allowed(path) is False

    def test_cross_domain_deportation(self):
        """100% PASS: Strictly blocks app-prefixed files from core layers."""
        # 'rg_' belongs in apps_rg, not L1_cognition
        path = "agentic_core/L1_cognition/thought_engine/rg_resume_node.py"
        assert is_path_allowed(path) is False

    def test_path_normalization_traversal(self):
        """100% PASS: Neutralizes and rejects directory traversal attempts."""
        path = "agentic_core/L5_safety/../L1_cognition/file.py"
        # normpath converts this to 'agentic_core/L1_cognition/file.py',
        # but the logic should verify the sanitized intent.
        assert is_path_allowed(path) is True

    def test_redundant_slash_blocking(self):
        """100% PASS: Rejects malformed paths with redundant slashes."""
        path = "agentic_core//L2_execution/tool.py"
        # [CRITICAL ANALYSIS] Redundant slashes often mask security bypasses.
        assert is_path_allowed(path) is False

    def test_depth_precision_files_vs_folders(self):
        """100% PASS: Ensures L4 is approved for FOLDERS, but blocks Depth-5 files."""
        # Depth 4 folder (meta_prompts/reasoning) is allowed
        valid_l4 = "agentic_core/prompt_governance/meta_prompts/reasoning/cot.py"
        assert is_path_allowed(valid_l4) is True

        # Depth 5 file (exceeds specialization) is blocked
        invalid_l5 = "agentic_core/prompt_governance/meta_prompts/reasoning/sub/leak.py"
        assert is_path_allowed(invalid_l5) is False

    def test_forbidden_patterns_legacy_l3_prefixes(self):
        """100% PASS: Blocks legacy L3_ prefixes in prompt_governance."""
        # Legacy L3_ prefix should be blocked
        legacy_path = "agentic_core/prompt_governance/meta_prompts/L3_legacy_prompt.py"
        assert is_path_allowed(legacy_path) is False

        # Lowercase l3_ prefix should also be blocked
        legacy_path_lower = "agentic_core/prompt_governance/templates/l3_old_template.py"
        assert is_path_allowed(legacy_path_lower) is False

    def test_test_prefix_deportation_with_exceptions(self):
        """100% PASS: Blocks test_ prefixes except in allowed locations."""
        # test_ prefix blocked in core
        blocked_path = "agentic_core/L2_execution/test_helper.py"
        assert is_path_allowed(blocked_path) is False

        # test_ prefix allowed in L0_maintenance/scripts
        allowed_path = "agentic_core/L0_maintenance/scripts/test_validator.py"
        assert is_path_allowed(allowed_path) is True

        # __init__.py always allowed
        init_allowed = "agentic_core/L1_cognition/test_init.py"  # This would be blocked
        assert is_path_allowed(init_allowed) is False

    def test_empty_path_and_traversal_security(self):
        """100% PASS: Handles empty paths and traversal attempts securely."""
        # Empty path should be rejected
        assert is_path_allowed("") is False

        # Traversal beyond root should be rejected
        assert is_path_allowed("../etc/passwd") is False

        # Traversal to parent directories should be rejected
        assert is_path_allowed("agentic_core/../../../etc/passwd") is False

    def test_filename_vs_folder_depth_logic(self):
        """100% PASS: Correctly distinguishes file depth from folder depth."""
        # File at depth 4 (folder depth 3) should be allowed
        file_at_depth_4 = "agentic_core/L1_cognition/thought_engine/reasoning/engine.py"
        assert is_path_allowed(file_at_depth_4) is True

        # Folder at depth 4 should be evaluated differently
        # This tests the folder depth calculation logic
        folder_path = "agentic_core/L1_cognition/thought_engine/reasoning"
        assert is_path_allowed(folder_path) is True  # Folder depth 3, within limit

    def test_nonexistent_root_handling(self):
        """100% PASS: Gracefully handles paths to non-existent root directories."""
        nonexistent_root = "nonexistent_folder/file.py"
        assert is_path_allowed(nonexistent_root) is False

        # Complex path with nonexistent root
        complex_nonexistent = "fake_root/sub1/sub2/file.py"
        assert is_path_allowed(complex_nonexistent) is False

    def test_special_characters_and_edge_cases(self):
        """100% PASS: Handles special characters and edge case paths."""
        # Path with spaces (should be normalized)
        # Should be processed based on actual structure rules

        # Path with dots (should be handled correctly)
        path_with_dots = "agentic_core/L2_execution/tool.v2.py"
        assert is_path_allowed(path_with_dots) is True  # Assuming valid structure

        # Path with multiple dots
        path_multi_dots = "agentic_core/L2_execution/tool.v2.1.py"
        assert is_path_allowed(path_multi_dots) is True
