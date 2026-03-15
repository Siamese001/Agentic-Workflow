"""ResumeAssemblyAgent - Provides resume assembly capabilities using prompt governance and markdown templates.

This agent handles:
- YAML-based prompt governance for resume assembly (via PromptLoader)
- Markdown template loading for skills sections, executive summaries, and networking requests
- Simple template substitution with explicit error handling

Domain: resume
Methods:
- assemble_resume(payload: dict) -> str
- generate_skills_section(payload: dict) -> str
- generate_executive_summary(payload: dict) -> str
- generate_networking_request(payload: dict) -> str
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.prompt_governance import PromptLoader
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ResumeTemplateError(Exception):
    """Raised when a resume template file cannot be found or read."""

    pass


class ResumeAssemblyAgent:
    """Agent for assembling resumes using YAML prompts and MD templates."""

    _TEMPLATE_REFERENCES = {
        "skills_template.md",
        "experience_template.md",
        "summary_template.md",
        "cold_outreach_template.md",
        "followup_template.md",
        "connection_request.md",
    }

    def __init__(self, prompt_root: Path | None = None) -> None:
        """Initialize with injected prompt directory.

        Args:
            prompt_root: Base directory containing prompt files and templates
        """
        if prompt_root is None:
            prompt_root = Path(__file__).parent.parent.parent / "data" / "prompt_governance"
        self.prompt_root = prompt_root
        self._prompt_loader = PromptLoader(self.prompt_root)

    def assemble_resume(self, payload: dict[str, Any]) -> str:
        """Assemble resume using YAML prompt governance.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted resume assembly from YAML prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded or rendered
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ResumeAssemblyAgent.assemble_resume")
        return self._prompt_loader.get_template("resume", "k7_assembly_agent", **payload)

    def generate_skills_section(self, payload: dict[str, Any]) -> str:
        """Generate skills section from markdown template.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted skills section

        Raises:
            ResumeTemplateError: If template file cannot be found or read
        """
        template_path = self.prompt_root / "resume" / "skills_template.md"
        return self._load_markdown_template(template_path, payload)

    def generate_executive_summary(self, payload: dict[str, Any]) -> str:
        """Generate executive summary from markdown template.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted executive summary

        Raises:
            ResumeTemplateError: If template file cannot be found or read
        """
        template_path = self.prompt_root / "resume" / "experience_template.md"
        return self._load_markdown_template(template_path, payload)

    def generate_networking_request(self, payload: dict[str, Any]) -> str:
        """Generate networking request from markdown template.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted networking request

        Raises:
            ResumeTemplateError: If template file cannot be found or read
        """
        template_path = self.prompt_root / "shared" / "connection_request.md"
        return self._load_markdown_template(template_path, payload)

    def _load_markdown_template(self, template_path: Path, payload: dict[str, Any]) -> str:
        """Load and format a markdown template.

        Args:
            template_path: Path to the markdown template file
            payload: Dictionary of template variables

        Returns:
            Formatted template content

        Raises:
            ResumeTemplateError: If template file cannot be found or read
        """
        try:
            content = template_path.read_text(encoding="utf-8")
            return content.format(**payload)
        except FileNotFoundError:
            raise ResumeTemplateError(f"Template file not found: {template_path}")
        except (OSError, UnicodeDecodeError) as e:
            raise ResumeTemplateError(f"Error reading template file {template_path}: {e}")
        except KeyError as e:
            raise ResumeTemplateError(f"Missing template variable {e} in {template_path}")

    # guardian: allow-type-erasure
    def heal(self, *args, **kwargs) -> dict:
        """heal() not implemented for ResumeAssemblyAgent."""
        raise NotImplementedError("heal() not implemented for ResumeAssemblyAgent")

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for ResumeAssemblyAgent."""
        raise NotImplementedError("heal_repository() not implemented for ResumeAssemblyAgent")


def get_resume_skills_section(payload: dict[str, Any]) -> str:
    """Dispatch function for generating resume skills section.

    Args:
        payload: Dictionary of template variables

    Returns:
        Formatted skills section
    """
    agent = ResumeAssemblyAgent()
    return agent.generate_skills_section(payload)


def get_resume_executive_summary(payload: dict[str, Any]) -> str:
    """Dispatch function for generating resume executive summary.

    Args:
        payload: Dictionary of template variables

    Returns:
        Formatted executive summary
    """
    agent = ResumeAssemblyAgent()
    return agent.generate_executive_summary(payload)
