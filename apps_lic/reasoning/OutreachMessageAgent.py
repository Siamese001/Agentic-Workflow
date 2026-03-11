"""OutreachMessageAgent - Provides outreach message capabilities using prompt governance and markdown templates.

This agent handles:
- YAML-based prompt governance for message body generation (via PromptLoader)
- Markdown template loading for connection requests, cold outreach, and followups
- Simple template substitution with explicit error handling

Domain: outreach
Methods:
- generate_connection_request(payload: dict) -> str
- generate_cold_outreach(payload: dict) -> str
- generate_followup(payload: dict) -> str
- generate_message_body(payload: dict) -> str
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.prompt_governance import PromptLoader


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class OutreachTemplateError(Exception):
    """Raised when an outreach template file cannot be found or read."""

    pass


class OutreachMessageAgent:
    """Agent for generating outreach messages using YAML prompts and MD templates."""

    def __init__(self, prompt_root: Path | None = None) -> None:
        """Initialize with injected prompt directory.

        Args:
            prompt_root: Base directory containing prompt files and templates
        """
        if prompt_root is None:
            prompt_root = Path(__file__).parent.parent.parent / "data" / "prompt_governance"
        self.prompt_root = prompt_root
        self._prompt_loader = PromptLoader(self.prompt_root)

    def generate_connection_request(self, payload: dict[str, Any]) -> str:
        """Generate connection request message from markdown template.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted connection request message

        Raises:
            OutreachTemplateError: If template file cannot be found or read
        """
        template_path = self.prompt_root / "shared" / "connection_request.md"
        return self._load_markdown_template(template_path, payload)

    def generate_cold_outreach(self, payload: dict[str, Any]) -> str:
        """Generate cold outreach message from markdown template.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted cold outreach message

        Raises:
            OutreachTemplateError: If template file cannot be found or read
        """
        template_path = self.prompt_root / "outreach" / "cold_outreach_template.md"
        return self._load_markdown_template(template_path, payload)

    def generate_followup(self, payload: dict[str, Any]) -> str:
        """Generate followup message from markdown template.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted followup message

        Raises:
            OutreachTemplateError: If template file cannot be found or read
        """
        template_path = self.prompt_root / "outreach" / "followup_template.md"
        return self._load_markdown_template(template_path, payload)

    def generate_message_body(self, payload: dict[str, Any]) -> str:
        """Generate message body using YAML prompt governance.

        Args:
            payload: Dictionary of template variables

        Returns:
            Formatted message body from YAML prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded or rendered
        """
        return self._prompt_loader.get_template("outreach", "k3_message_body_agent", **payload)

    def _load_markdown_template(self, template_path: Path, payload: dict[str, Any]) -> str:
        """Load and format a markdown template.

        Args:
            template_path: Path to the markdown template file
            payload: Dictionary of template variables

        Returns:
            Formatted template content

        Raises:
            OutreachTemplateError: If template file cannot be found or read
        """
        try:
            content = template_path.read_text(encoding="utf-8")
            return content.format(**payload)
        except FileNotFoundError:
            raise OutreachTemplateError(f"Template file not found: {template_path}")
        except (OSError, UnicodeDecodeError) as e:
            raise OutreachTemplateError(f"Error reading template file {template_path}: {e}")
        except KeyError as e:
            raise OutreachTemplateError(f"Missing template variable {e} in {template_path}")

    # guardian: allow-type_erasure
    def heal(self, *args, **kwargs) -> dict:
        """heal() not implemented for OutreachMessageAgent."""
        raise NotImplementedError("heal() not implemented for OutreachMessageAgent")

    # guardian: allow-type_erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for OutreachMessageAgent."""
        raise NotImplementedError("heal_repository() not implemented for OutreachMessageAgent")
