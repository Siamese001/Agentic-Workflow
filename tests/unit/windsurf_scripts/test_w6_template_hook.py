"""W6.P6 tests: Template authorization section and hook registration verification."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure repo root is on path for imports
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestTemplateScopeExpansionAuthorization:
    """Test that execution-plan-template.md contains required authorization section."""

    @pytest.fixture
    def template_content(self) -> str:
        """Read the execution plan template."""
        template_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "templates" / "execution-plan-template.md"
        if not template_path.exists():
            pytest.skip("Template file not found")
        return template_path.read_text(encoding="utf-8")

    def test_contains_authorization_section(self, template_content: str) -> None:
        """Template has '## Scope Expansion Authorization' heading."""
        assert "## Scope Expansion Authorization" in template_content

    def test_contains_four_step_protocol(self, template_content: str) -> None:
        """Template documents the four-step protocol."""
        # Step 1
        assert "DISCOVERED_SCOPE marker" in template_content
        # Step 2
        assert "AUTHORIZATION_DECISION marker" in template_content
        # Step 3
        assert "Plan file updates" in template_content
        # Step 4
        assert "SCOPE_EXPANSION marker" in template_content

    def test_contains_all_marker_names(self, template_content: str) -> None:
        """Template references all three marker types."""
        markers = ["DISCOVERED_SCOPE", "AUTHORIZATION_DECISION", "SCOPE_EXPANSION"]
        for marker in markers:
            assert marker in template_content, f"Missing marker: {marker}"

    def test_contains_all_decision_values(self, template_content: str) -> None:
        """Template lists all four decision vocabulary values."""
        decisions = ["ACCEPTED", "DEFERRED", "SPLIT_TO_NEW_PLAN", "REJECTED"]
        for decision in decisions:
            assert decision in template_content, f"Missing decision: {decision}"

    def test_contains_required_updates_checklist(self, template_content: str) -> None:
        """Template includes the required update checklist."""
        checklist_items = [
            "Refresh `last_updated`",
            "Add/modify Wave Structure row",
            "Add/modify Phase-Level Summary row",
            "Add/modify Gap Register row",
            "Add/modify DoD criterion",
            "Append to Scope Expansion Authorization Log",
        ]
        for item in checklist_items:
            assert item in template_content, f"Missing checklist item: {item}"

    def test_contains_retroactive_authorization_warning(self, template_content: str) -> None:
        """Template mentions RETROACTIVE_AUTHORIZATION_DETECTED."""
        assert "RETROACTIVE_AUTHORIZATION_DETECTED" in template_content

    def test_contains_negative_control_language(self, template_content: str) -> None:
        """Template has documentation-does-not-equal-authorization warning."""
        assert "Documentation ≠ Authorization" in template_content

    def test_contains_marker_grammar_examples(self, template_content: str) -> None:
        """Template provides example marker formats."""
        assert "DISCOVERED_SCOPE: plan=" in template_content
        assert "AUTHORIZATION_DECISION: plan=" in template_content
        assert "SCOPE_EXPANSION: plan=" in template_content


class TestHooksJsonRegistration:
    """Test that hooks.json registers the plan scope audit hook."""

    @pytest.fixture
    def hooks_config(self) -> dict[str, Any]:
        """Read and parse hooks.json."""
        hooks_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"
        if not hooks_path.exists():
            pytest.skip("hooks.json not found")
        content = hooks_path.read_text(encoding="utf-8")
        return json.loads(content)

    def test_post_agent_plan_scope_audit_registered(
        self, hooks_config: dict[str, Any]
    ) -> None:
        """Hook post_agent_plan_scope_audit.py is in post_agent_response list."""
        post_cascade = hooks_config.get("hooks", {}).get("post_agent_response", [])
        commands = [h.get("command", "") for h in post_cascade]
        
        audit_hooks = [c for c in commands if "post_agent_plan_scope_audit.py" in c]
        assert len(audit_hooks) >= 1, "post_agent_plan_scope_audit.py not registered"

    def test_hook_is_advisory_not_strict(self, hooks_config: dict[str, Any]) -> None:
        """Hook runs in advisory mode (show_output=true, no strict flag)."""
        post_cascade = hooks_config.get("hooks", {}).get("post_agent_response", [])
        
        for hook in post_cascade:
            if "post_agent_plan_scope_audit.py" in hook.get("command", ""):
                # Default advisory: show_output=true for visibility
                assert hook.get("show_output") is True
                # No strict enforcement by default
                command = hook.get("command", "")
                assert "--strict" not in command
                assert "PLAN_SCOPE_AUDIT_STRICT" not in command
                break
        else:
            pytest.fail("post_agent_plan_scope_audit.py hook not found")

    def test_hook_has_correct_working_directory(
        self, hooks_config: dict[str, Any]
    ) -> None:
        """Hook uses {repo_root} as working directory."""
        post_cascade = hooks_config.get("hooks", {}).get("post_agent_response", [])
        
        for hook in post_cascade:
            if "post_agent_plan_scope_audit.py" in hook.get("command", ""):
                assert hook.get("working_directory") == "{repo_root}"
                break
        else:
            pytest.fail("post_agent_plan_scope_audit.py hook not found")


class TestW6Integration:
    """Integration tests verifying W6 components work together."""

    def test_w2_helper_exists(self) -> None:
        """W2 helper exists and is importable."""
        helper_path = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "_plan_scope_expansion_check.py"
        assert helper_path.exists(), "W2 helper not found"

    def test_w3_hook_exists(self) -> None:
        """W3 hook exists and is runnable."""
        hook_path = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "post_agent_plan_scope_audit.py"
        assert hook_path.exists(), "W3 hook not found"

    def test_template_exists(self) -> None:
        """Execution plan template exists."""
        template_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "templates" / "execution-plan-template.md"
        assert template_path.exists(), "Template not found"

    def test_hooks_json_valid_json(self) -> None:
        """hooks.json is valid JSON."""
        hooks_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"
        content = hooks_path.read_text(encoding="utf-8")
        config = json.loads(content)
        assert "hooks" in config
        assert "post_agent_response" in config["hooks"]
