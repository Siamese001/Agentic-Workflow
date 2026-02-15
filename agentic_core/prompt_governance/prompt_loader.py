"""Centralized prompt loading and caching system."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class PromptLoadError(Exception):
    """Raised when prompt file cannot be loaded."""
    pass


class PromptSchemaError(Exception):
    """Raised when prompt file schema is invalid."""
    pass


class PromptLoader:
    """Pure infrastructure component for loading and caching prompts.

    Enforces architectural boundaries:
    - No business logic
    - No domain text formatting
    - No direct apps_* access
    """

    def __init__(self, prompt_dir: Path) -> None:
        """Initialize with injected prompt directory.

        Args:
            prompt_dir: Base directory containing prompt files

        Raises:
            ValueError: If prompt_dir is not a directory
        """
        if not isinstance(prompt_dir, Path):
            raise TypeError("prompt_dir must be a Path object")

        if not prompt_dir.is_dir():
            raise ValueError(f"prompt_dir must be a directory: {prompt_dir}")

        self._prompt_dir = prompt_dir.resolve()
        self._prompt_cache: dict[str, dict[str, Any]] = {}

    def load_prompt(self, domain: str, name: str) -> dict[str, Any]:
        """Load and cache prompt by domain and name.

        Args:
            domain: Prompt domain (e.g., 'executive', 'outreach')
            name: Prompt name without extension

        Returns:
            Loaded prompt data dictionary

        Raises:
            PromptLoadError: If file cannot be loaded
            PromptSchemaError: If schema is invalid
        """
        if not domain or not isinstance(domain, str):
            raise ValueError("domain must be a non-empty string")

        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")

        cache_key = f"{domain}:{name}"

        if cache_key not in self._prompt_cache:
            prompt_file = self._prompt_dir / domain / f"{name}.yaml"

            if not prompt_file.exists():
                raise PromptLoadError(f"Prompt file not found: {prompt_file}")

            if not prompt_file.is_file():
                raise PromptLoadError(f"Path is not a file: {prompt_file}")

            try:
                with open(prompt_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise PromptLoadError(f"Invalid YAML in {prompt_file}: {e}")
            except OSError as e:
                raise PromptLoadError(f"Cannot read {prompt_file}: {e}")

            # Validate minimal schema
            if not isinstance(data, dict):
                raise PromptSchemaError(f"Prompt must be a dict: {prompt_file}")

            if 'template' not in data:
                raise PromptSchemaError(f"Missing required 'template' key: {prompt_file}")

            if not isinstance(data['template'], str):
                raise PromptSchemaError(f"'template' must be a string: {prompt_file}")

            self._prompt_cache[cache_key] = data

        return self._prompt_cache[cache_key]

    def get_template(self, domain: str, name: str, **template_vars: Any) -> str:
        """Get formatted prompt template with variables.

        Args:
            domain: Prompt domain
            name: Prompt name
            **template_vars: Template variables

        Returns:
            Formatted template string

        Raises:
            PromptLoadError: If prompt cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        prompt_data = self.load_prompt(domain, name)
        template = prompt_data["template"]

        # Prepare constraints if present
        constraints = prompt_data.get("constraints", [])
        if constraints:
            if not isinstance(constraints, list):
                raise PromptSchemaError(f"'constraints' must be a list: {domain}:{name}")
            constraints_text = "\n".join(str(c) for c in constraints)
        else:
            constraints_text = ""

        try:
            return template.format(constraints=constraints_text, **template_vars)
        except KeyError as e:
            raise PromptSchemaError(f"Missing template variable {e} in {domain}:{name}")
        except (ValueError, TypeError) as e:
            raise PromptSchemaError(f"Template formatting error in {domain}:{name}: {e}")

    def clear_cache(self) -> None:
        """Clear the internal cache. Useful for testing."""
        self._prompt_cache.clear()

    def cache_info(self) -> dict[str, int]:
        """Get cache statistics for testing and monitoring."""
        return {
            "cached_items": len(self._prompt_cache),
            "cache_keys": list(self._prompt_cache.keys())
        }
