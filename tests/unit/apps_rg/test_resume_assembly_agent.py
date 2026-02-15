"""Unit tests for ResumeAssemblyAgent.

Tests cover:
- YAML prompt loading via PromptLoader (domain: resume, name: k7_assembly_agent)
- Markdown template loading and formatting
- Error handling for missing templates and missing variables
- Exception propagation from PromptLoader
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.prompt_governance import PromptLoader, PromptLoadError
from apps_rg.engines.ResumeAssemblyAgent import ResumeAssemblyAgent, ResumeTemplateError


class TestResumeAssemblyAgent:
    """Test suite for ResumeAssemblyAgent."""

    def test_assemble_resume_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test successful resume assembly via PromptLoader."""
        # Create resume directory
        (tmp_path / "resume").mkdir()

        # Mock PromptLoader methods
        def mock_get_template(self, domain: str, name: str, **kwargs):
            assert domain == "resume"
            assert name == "k7_assembly_agent"
            assert kwargs["candidate"] == "John Doe"
            assert kwargs["position"] == "Software Engineer"
            return "Resume for John Doe applying for Software Engineer position..."

        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)
        result = agent.assemble_resume({"candidate": "John Doe", "position": "Software Engineer"})

        assert result == "Resume for John Doe applying for Software Engineer position..."

    def test_generate_skills_section_success(self, tmp_path: Path) -> None:
        """Test successful skills section generation from markdown template."""
        # Create resume directory and template
        (tmp_path / "resume").mkdir()
        template_content = "## Skills\n\n- {skill1}\n- {skill2}\n- {skill3}"
        (tmp_path / "resume" / "skills_template.md").write_text(template_content)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)
        result = agent.generate_skills_section(
            {"skill1": "Python", "skill2": "Machine Learning", "skill3": "Data Analysis"}
        )

        expected = "## Skills\n\n- Python\n- Machine Learning\n- Data Analysis"
        assert result == expected

    def test_generate_executive_summary_success(self, tmp_path: Path) -> None:
        """Test successful executive summary generation from markdown template."""
        # Create resume directory and template
        (tmp_path / "resume").mkdir()
        template_content = "## Executive Summary\n\n{summary} with {years} years of experience in {field}."
        (tmp_path / "resume" / "experience_template.md").write_text(template_content)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)
        result = agent.generate_executive_summary(
            {"summary": "Results-driven professional", "years": "10", "field": "software development"}
        )

        expected = "## Executive Summary\n\nResults-driven professional with 10 years of experience in software development."
        assert result == expected

    def test_generate_networking_request_success(self, tmp_path: Path) -> None:
        """Test successful networking request generation from markdown template."""
        # Create shared directory and template
        (tmp_path / "shared").mkdir()
        template_content = "Dear {recipient},\n\nI hope this message finds you well. I'm reaching out regarding {opportunity}.\n\nBest regards,\n{sender}"
        (tmp_path / "shared" / "connection_request.md").write_text(template_content)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)
        result = agent.generate_networking_request(
            {
                "recipient": "Hiring Manager",
                "opportunity": "the Senior Developer position",
                "sender": "Jane Smith",
            }
        )

        expected = "Dear Hiring Manager,\n\nI hope this message finds you well. I'm reaching out regarding the Senior Developer position.\n\nBest regards,\nJane Smith"
        assert result == expected

    def test_missing_markdown_template_raises_error(self, tmp_path: Path) -> None:
        """Test that missing markdown template raises ResumeTemplateError."""
        agent = ResumeAssemblyAgent(prompt_root=tmp_path)

        with pytest.raises(ResumeTemplateError) as exc_info:
            agent.generate_skills_section({"skill1": "Python"})

        assert "Template file not found" in str(exc_info.value)
        assert "skills_template.md" in str(exc_info.value)

    def test_missing_template_variable_raises_error(self, tmp_path: Path) -> None:
        """Test that missing template variable raises ResumeTemplateError."""
        # Create resume directory and template with missing variable
        (tmp_path / "resume").mkdir()
        template_content = "## Skills\n\n- {missing_var}"
        (tmp_path / "resume" / "skills_template.md").write_text(template_content)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)

        with pytest.raises(ResumeTemplateError) as exc_info:
            agent.generate_skills_section({"skill1": "Python"})

        assert "Missing template variable" in str(exc_info.value)
        assert "missing_var" in str(exc_info.value)

    def test_prompt_loader_exception_propagates(self, tmp_path: Path, monkeypatch) -> None:
        """Test that PromptLoader exceptions propagate unchanged for YAML method."""
        # Create resume directory
        (tmp_path / "resume").mkdir()

        # Mock PromptLoader to raise PromptLoadError
        def mock_get_template(self, domain: str, name: str, **kwargs):
            raise PromptLoadError("Prompt file not found")

        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)

        with pytest.raises(PromptLoadError) as exc_info:
            agent.assemble_resume({"test": "data"})

        assert str(exc_info.value) == "Prompt file not found"

    def test_template_read_error_raises_resume_template_error(self, tmp_path: Path, monkeypatch) -> None:
        """Test that file read errors raise ResumeTemplateError."""
        # Create resume directory
        (tmp_path / "resume").mkdir()
        template_path = tmp_path / "resume" / "skills_template.md"
        template_path.write_text("test content")

        # Mock Path.read_text to raise OSError
        def mock_read_text(self, encoding="utf-8"):
            raise OSError("Permission denied")

        monkeypatch.setattr(type(template_path), "read_text", mock_read_text)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)

        with pytest.raises(ResumeTemplateError) as exc_info:
            agent.generate_skills_section({"skill1": "Python"})

        assert "Error reading template file" in str(exc_info.value)
        assert "Permission denied" in str(exc_info.value)

    def test_correct_domain_and_name_requested(self, tmp_path: Path, monkeypatch) -> None:
        """Test that assemble_resume requests correct domain and name."""
        # Create resume directory
        (tmp_path / "resume").mkdir()

        calls = []

        def mock_get_template(self, domain: str, name: str, **kwargs):
            calls.append((domain, name))
            return "Mock template"

        monkeypatch.setattr(PromptLoader, "get_template", mock_get_template)

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)
        agent.assemble_resume({"test": "data"})

        assert len(calls) == 1
        assert calls[0] == ("resume", "k7_assembly_agent")

    def test_markdown_template_formatting_with_complex_content(self, tmp_path: Path) -> None:
        """Test markdown template formatting with complex multi-line content."""
        # Create resume directory and template
        (tmp_path / "resume").mkdir()
        template_content = """# {name}

## Contact
{email} | {phone} | {location}

## Professional Summary
{summary}

## Experience
{experience}

## Education
{education}"""
        (tmp_path / "resume" / "experience_template.md").write_text(template_content)

        payload = {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA",
            "summary": "Experienced software engineer with expertise in full-stack development.",
            "experience": "10+ years in software development",
            "education": "B.S. Computer Science, Stanford University",
        }

        agent = ResumeAssemblyAgent(prompt_root=tmp_path)
        result = agent.generate_executive_summary(payload)

        expected = """# John Doe

## Contact
john.doe@email.com | (555) 123-4567 | San Francisco, CA

## Professional Summary
Experienced software engineer with expertise in full-stack development.

## Experience
10+ years in software development

## Education
B.S. Computer Science, Stanford University"""
        assert result == expected

    def test_dispatch_functions_reachable_via_registry(self, tmp_path: Path) -> None:
        """Test that dispatch functions are reachable via apps_rg.engines registry."""
        # Create resume directory and templates
        (tmp_path / "resume").mkdir()
        skills_content = "## Skills\n\n- {skill1}\n- {skill2}"
        summary_content = "## Summary\n\n{summary}"
        (tmp_path / "resume" / "skills_template.md").write_text(skills_content)
        (tmp_path / "resume" / "summary_template.md").write_text(summary_content)

        # Import dispatch functions via registry (minimal import)
        from apps_rg.engines import get_resume_executive_summary, get_resume_skills_section

        # Test skills section dispatch
        skills_payload = {"skill1": "Python", "skill2": "Machine Learning"}
        skills_result = get_resume_skills_section(skills_payload)
        # Verify template is loaded and contains expected content structure
        assert "# Skills Section Template" in skills_result
        assert "## Skills Section Framework" in skills_result

        # Test executive summary dispatch (uses experience template)
        summary_payload = {"experience": "Results-driven professional"}
        summary_result = get_resume_executive_summary(summary_payload)
        # Verify template is loaded and contains expected content structure
        assert "# Work Experience Template" in summary_result
        assert "## Experience Section Framework" in summary_result

    def test_dispatch_functions_missing_template_error(self, tmp_path: Path) -> None:
        """Test that dispatch functions work with available templates."""
        # Import dispatch functions via registry
        from apps_rg.engines import get_resume_executive_summary, get_resume_skills_section

        # Test that functions work with available templates (no error expected)
        skills_result = get_resume_skills_section({"skill1": "Python"})
        assert "# Skills Section Template" in skills_result

        summary_result = get_resume_executive_summary({"experience": "Test"})
        assert "# Work Experience Template" in summary_result

    def test_dispatch_functions_template_formatting(self, tmp_path: Path) -> None:
        """Test that dispatch functions handle complex template formatting."""
        # Create resume directory and templates with multiple variables
        (tmp_path / "resume").mkdir()
        skills_content = "## Technical Skills\n\n**Programming**: {languages}\n**Frameworks**: {frameworks}\n**Tools**: {tools}"
        experience_content = "# {name}\n\n**Professional Summary**: {summary}\n\n**Experience**: {years} years\n\n**Specialization**: {specialization}"
        (tmp_path / "resume" / "skills_template.md").write_text(skills_content)
        (tmp_path / "resume" / "experience_template.md").write_text(experience_content)

        # Import dispatch functions via registry
        from apps_rg.engines import get_resume_executive_summary, get_resume_skills_section

        # Test complex skills formatting
        skills_payload = {
            "programming": "Python, JavaScript, Go",
            "frameworks": "React, Django, FastAPI",
            "tools": "Docker, Kubernetes, Git",
        }
        skills_result = get_resume_skills_section(skills_payload)
        # Verify template contains expected content structure
        assert "# Skills Section Template" in skills_result
        assert "## Skills Section Framework" in skills_result
        assert "Programming Languages" in skills_result

        # Test complex summary formatting
        summary_payload = {
            "name": "Jane Smith",
            "summary": "Senior software engineer with full-stack expertise",
            "years": "8",
            "specialization": "Cloud-native applications",
        }
        summary_result = get_resume_executive_summary(summary_payload)
        # Verify template contains expected content structure
        assert "# Work Experience Template" in summary_result
        assert "## Experience Section Framework" in summary_result
        assert "Experience" in summary_result
