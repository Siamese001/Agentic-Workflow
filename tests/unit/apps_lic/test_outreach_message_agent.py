"""Unit tests for OutreachMessageAgent.

Tests cover:
- YAML prompt loading via PromptLoader (domain: outreach, name: k3_message_body_agent)
- Markdown template loading and formatting
- Error handling for missing templates and missing variables
- Exception propagation from PromptLoader
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.prompt_governance import PromptLoader, PromptLoadError
from apps_lic.engines.OutreachMessageAgent import OutreachMessageAgent, OutreachTemplateError


class TestOutreachMessageAgent:
    """Test suite for OutreachMessageAgent."""

    def test_generate_connection_request_success(self, tmp_path: Path) -> None:
        """Test successful connection request generation from markdown template."""
        # Create shared directory and template
        (tmp_path / "shared").mkdir()
        template_content = "Hello {name}, I'd like to connect with you."
        (tmp_path / "shared" / "connection_request.md").write_text(template_content)

        agent = OutreachMessageAgent(prompt_root=tmp_path)
        result = agent.generate_connection_request({"name": "John"})

        assert result == "Hello John, I'd like to connect with you."

    def test_generate_cold_outreach_success(self, tmp_path: Path) -> None:
        """Test successful cold outreach generation from markdown template."""
        # Create outreach directory and template
        (tmp_path / "outreach").mkdir()
        template_content = "Hi {first_name}, I'm reaching out about {topic}."
        (tmp_path / "outreach" / "cold_outreach_template.md").write_text(template_content)

        agent = OutreachMessageAgent(prompt_root=tmp_path)
        result = agent.generate_cold_outreach({"first_name": "Sarah", "topic": "collaboration"})

        assert result == "Hi Sarah, I'm reaching out about collaboration."

    def test_generate_followup_success(self, tmp_path: Path) -> None:
        """Test successful followup generation from markdown template."""
        # Create outreach directory and template
        (tmp_path / "outreach").mkdir()
        template_content = "Following up on our discussion about {subject}."
        (tmp_path / "outreach" / "followup_template.md").write_text(template_content)

        agent = OutreachMessageAgent(prompt_root=tmp_path)
        result = agent.generate_followup({"subject": "the project"})

        assert result == "Following up on our discussion about the project."

    def test_generate_message_body_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test successful message body generation via PromptLoader."""
        # Create outreach directory
        (tmp_path / "outreach").mkdir()

        # Mock PromptLoader methods
        def mock_get_template(self, domain: str, name: str, **kwargs):
            assert domain == "outreach"
            assert name == "k3_message_body_agent"
            assert kwargs["recipient"] == "Alex"
            assert kwargs["context"] == "job opportunity"
            return "Dear Alex, regarding job opportunity..."

        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = OutreachMessageAgent(prompt_root=tmp_path)
        result = agent.generate_message_body({"recipient": "Alex", "context": "job opportunity"})

        assert result == "Dear Alex, regarding job opportunity..."

    def test_missing_markdown_template_raises_error(self, tmp_path: Path) -> None:
        """Test that missing markdown template raises OutreachTemplateError."""
        agent = OutreachMessageAgent(prompt_root=tmp_path)

        with pytest.raises(OutreachTemplateError) as exc_info:
            agent.generate_connection_request({"name": "John"})

        assert "Template file not found" in str(exc_info.value)
        assert "connection_request.md" in str(exc_info.value)

    def test_missing_template_variable_raises_error(self, tmp_path: Path) -> None:
        """Test that missing template variable raises OutreachTemplateError."""
        # Create shared directory and template with missing variable
        (tmp_path / "shared").mkdir()
        template_content = "Hello {missing_var}, this won't work."
        (tmp_path / "shared" / "connection_request.md").write_text(template_content)

        agent = OutreachMessageAgent(prompt_root=tmp_path)

        with pytest.raises(OutreachTemplateError) as exc_info:
            agent.generate_connection_request({"name": "John"})

        assert "Missing template variable" in str(exc_info.value)
        assert "missing_var" in str(exc_info.value)

    def test_prompt_loader_exception_propagates(self, tmp_path: Path, monkeypatch) -> None:
        """Test that PromptLoader exceptions propagate unchanged for YAML method."""
        # Create outreach directory
        (tmp_path / "outreach").mkdir()

        # Mock PromptLoader to raise PromptLoadError
        def mock_get_template(self, domain: str, name: str, **kwargs):
            raise PromptLoadError("Prompt file not found")

        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = OutreachMessageAgent(prompt_root=tmp_path)

        with pytest.raises(PromptLoadError) as exc_info:
            agent.generate_message_body({"test": "data"})

        assert str(exc_info.value) == "Prompt file not found"

    def test_template_read_error_raises_outreach_template_error(self, tmp_path: Path, monkeypatch) -> None:
        """Test that file read errors raise OutreachTemplateError."""
        # Create shared directory
        (tmp_path / "shared").mkdir()
        template_path = tmp_path / "shared" / "connection_request.md"
        template_path.write_text("test content")

        # Mock Path.read_text to raise OSError
        def mock_read_text(self, encoding="utf-8"):
            raise OSError("Permission denied")

        monkeypatch.setattr(type(template_path), "read_text", mock_read_text)

        agent = OutreachMessageAgent(prompt_root=tmp_path)

        with pytest.raises(OutreachTemplateError) as exc_info:
            agent.generate_connection_request({"name": "John"})

        assert "Error reading template file" in str(exc_info.value)
        assert "Permission denied" in str(exc_info.value)

    def test_correct_domain_and_name_requested(self, tmp_path: Path, monkeypatch) -> None:
        """Test that generate_message_body requests correct domain and name."""
        # Create outreach directory
        (tmp_path / "outreach").mkdir()

        calls = []

        def mock_get_template(self, domain: str, name: str, **kwargs):
            calls.append((domain, name))
            return "Mock template"

        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = OutreachMessageAgent(prompt_root=tmp_path)
        agent.generate_message_body({"test": "data"})

        assert len(calls) == 1
        assert calls[0] == ("outreach", "k3_message_body_agent")

    def test_markdown_template_formatting_with_multiple_variables(self, tmp_path: Path) -> None:
        """Test markdown template formatting with multiple variables."""
        # Create outreach directory and template
        (tmp_path / "outreach").mkdir()
        template_content = "Dear {title} {last_name},\n\nI hope you're well. I'm reaching out about {topic}. Let's connect at {event}.\n\nBest regards,\n{sender}"
        (tmp_path / "outreach" / "cold_outreach_template.md").write_text(template_content)

        payload = {
            "title": "Dr.",
            "last_name": "Smith",
            "topic": "research collaboration",
            "event": "the conference",
            "sender": "Jane Doe",
        }

        agent = OutreachMessageAgent(prompt_root=tmp_path)
        result = agent.generate_cold_outreach(payload)

        expected = "Dear Dr. Smith,\n\nI hope you're well. I'm reaching out about research collaboration. Let's connect at the conference.\n\nBest regards,\nJane Doe"
        assert result == expected
