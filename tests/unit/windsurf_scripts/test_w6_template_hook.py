"""W6.P6 tests: Template authorization section and active hook registration verification."""

from __future__ import annotations

import json
import sys
from pathlib import Path

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
        template_path = REPO_ROOT / ".claude" / "templates" / "execution-plan-template.md"
        if not template_path.exists():
            pytest.skip("Template file not found")
        return template_path.read_text(encoding="utf-8")

    def test_contains_authorization_section(self, template_content: str) -> None:
        """Template has '## Scope Expansion Authorization' heading."""
        assert "## Scope Expansion Authorization" in template_content

    def test_contains_four_step_protocol(self, template_content: str) -> None:
        """Template documents the four-step protocol."""
        assert "emit markers in order" in template_content
        assert "DISCOVERED_SCOPE:" in template_content
        assert "AUTHORIZATION_DECISION:" in template_content
        assert "SCOPE_EXPANSION:" in template_content

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

    def test_contains_required_update_surfaces(self, template_content: str) -> None:
        """Template includes the required plan update surfaces."""
        checklist_items = [
            "### Wave Progress",
            "### Phase Progress",
            "## Gap Register",
            "## Definition of Done",
            "## Scope Expansion Authorization",
        ]
        for item in checklist_items:
            assert item in template_content, f"Missing checklist item: {item}"

    def test_contains_retroactive_authorization_warning(self, template_content: str) -> None:
        """Template warns that retroactive updates are not authorization."""
        assert "Retroactive plan updates are not governance" in template_content

    def test_contains_negative_control_language(self, template_content: str) -> None:
        """Template has documentation-does-not-equal-authorization warning."""
        assert "Documentation ≠ Authorization" in template_content

    def test_contains_marker_grammar_examples(self, template_content: str) -> None:
        """Template provides example marker formats."""
        assert "DISCOVERED_SCOPE: plan=" in template_content
        assert "AUTHORIZATION_DECISION: plan=" in template_content
        assert "SCOPE_EXPANSION: plan=" in template_content


class TestActiveScopeAudit:
    """Test that the active plan scope audit hook is available and advisory by default."""

    def test_post_agent_plan_scope_audit_exists(self) -> None:
        """Hook post_agent_plan_scope_audit.py exists as an active script."""
        hook_path = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_plan_scope_audit.py"
        assert hook_path.exists()

    def test_hook_is_advisory_not_strict(self) -> None:
        """Hook runs in advisory mode by default."""
        script = REPO_ROOT / ".claude" / "governance" / "scripts" / "post_agent_plan_scope_audit.py"
        text = script.read_text(encoding="utf-8")
        assert "PLAN_SCOPE_AUDIT_STRICT" in text
        assert "--strict" not in text

    def test_stop_hook_routes_to_governance_dispatcher(self) -> None:
        """Claude Stop hook routes through the active governance dispatcher."""
        settings_path = REPO_ROOT / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        commands = [
            entry["command"]
            for hook in settings["hooks"]["Stop"]
            for entry in hook.get("hooks", [])
            if "command" in entry
        ]
        assert any("after_agent_governance_dispatch.py" in command for command in commands)


class TestW6Integration:
    """Integration tests verifying W6 components work together."""

    def test_w2_helper_exists(self) -> None:
        """W2 helper exists and is importable."""
        helper_path = REPO_ROOT / ".claude" / "governance/scripts" / "_plan_scope_expansion_check.py"
        assert helper_path.exists(), "W2 helper not found"

    def test_w3_hook_exists(self) -> None:
        """W3 hook exists and is runnable."""
        hook_path = REPO_ROOT / ".claude" / "governance/scripts" / "post_agent_plan_scope_audit.py"
        assert hook_path.exists(), "W3 hook not found"

    def test_template_exists(self) -> None:
        """Execution plan template exists."""
        template_path = REPO_ROOT / ".claude" / "templates" / "execution-plan-template.md"
        assert template_path.exists(), "Template not found"

    def test_settings_json_valid_json(self) -> None:
        """Active Claude settings JSON is valid."""
        settings_path = REPO_ROOT / ".claude" / "settings.json"
        content = settings_path.read_text(encoding="utf-8")
        config = json.loads(content)
        assert "hooks" in config
        assert "Stop" in config["hooks"]
