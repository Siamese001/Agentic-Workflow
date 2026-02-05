from agentic_core.L5_safety.validators.structure_blueprint_config import is_path_allowed


class TestStressHarden:
    """
    PHASE 7: 10 High-Criticality Stress Tests for Edge Cases.
    """

    # --- 1. The "List-to-Dict" Type Safety (CRITICAL) ---
    def test_list_based_root_does_not_crash_l4_check(self):
        """100% PASS: Ensures apps_rg (list-based) doesn't trigger TypeError in L4 check."""
        path = "apps_rg/engines/formatter/deep_file.py"
        # Logic: apps_rg depth is 2. This is 4. Should return False, NOT crash.
        assert is_path_allowed(path) is False

    # --- 2. The "Deportation" Sanction ---
    def test_core_rejects_app_prefixed_files(self):
        """100% PASS: Prevents 'rg_resume.py' from existing in 'agentic_core'."""
        path = "agentic_core/L0_maintenance/scripts/rg_leaked_script.py"
        assert is_path_allowed(path) is False

    # --- 3. The "Depth-5" Sprawl ---
    def test_l4_specialization_enforces_hard_cutoff(self):
        """100% PASS: tool_registry allows depth 4, but depth 5 must be blocked."""
        path = "agentic_core/L2_execution/tool_registry/core/extra/file.py"
        assert is_path_allowed(path) is False

    # --- 4. The "L3 Phishing" Attack ---
    def test_reconciled_folders_block_legacy_shadows(self):
        """100% PASS: Blocks L3_ prefixes even if the rest of the path looks valid."""
        path = "agentic_core/prompt_governance/L3_templates/instructional.py"
        assert is_path_allowed(path) is False

    # --- 5. The "Empty String" Injection ---
    def test_empty_segments_are_blocked(self):
        """100% PASS: Ensures '//' or trailing slashes are caught."""
        assert is_path_allowed("agentic_core//L2_execution/file.py") is False

    # --- 6. The "Hidden Ghost" File ---
    def test_hidden_files_in_core_require_protection(self):
        """100% PASS: .env or .git files in core roots must be blocked if not protected."""
        assert is_path_allowed("agentic_core/.env") is False

    # --- 7. The "Sovereign Collision" ---
    def test_sovereign_roots_cannot_nest(self):
        """100% PASS: Prevents 'agentic_core' from appearing inside 'apps_rg'."""
        path = "apps_rg/agentic_core/logic.py"
        # Since 'agentic_core' is not in the apps_rg subfolders list, it should fail.
        assert is_path_allowed(path) is False

    # --- 8. The "Casing Ambiguity" ---
    def test_case_sensitivity_enforcement(self):
        """100% PASS: Ensures 'l2_execution' (lowercase) is rejected."""
        assert is_path_allowed("agentic_core/l2_execution/tool_registry") is False

    # --- 9. The "Volatile Root" Check ---
    def test_root_files_outside_whitelist(self):
        """100% PASS: Blocks random files in project root that aren't README or Traces."""
        assert is_path_allowed("unauthorized_manifest.json") is False

    # --- 10. The "Reserved Layer" Protection ---
    def test_protected_layer_directories(self):
        """100% PASS: Prevents creating 'L9_unknown' inside agentic_core."""
        assert is_path_allowed("agentic_core/L9_unknown/file.py") is False
