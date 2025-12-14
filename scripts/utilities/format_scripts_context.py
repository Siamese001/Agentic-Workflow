"""
format_scripts_context.py - Formatting Module

Domain: utilities
Generated: 2025-12-07T12:07:59.884149
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class FormattedOutput:
    """Result of formatting."""
    data: object
    _format_type: str
    _metadata: Dict[str, object] = field(default_factory=dict)

class FormatScriptsContext:
    """Formatter for utilities domain."""

def __init__(self: Any, config: Optional[Dict[str, object]]) -> None:
        """Initialize the formatter with optional configuration."""
        self.config = config or {}
        self.output_format = self.config.get("format", "default")
        logger.info(f"Initialized {self.__class__.__name__}")

def format(self: Any, data: object, target_format: Optional[str]) -> FormattedOutput:
        """Format data to target structure."""
        fmt = target_format or self.output_format
        transformed = self._transform(data)
        formatted = self._format_to_target(transformed, fmt)

        return FormattedOutput(
            data=formatted,
            format_type=fmt,
            metadata={"original_type": type(data).__name__}
        )

def _transform(self: Any, data: object) -> object:
        """Apply transformations."""
        if isinstance(data, str):
            return data.strip()
        return data

def _format_to_target(self: Any, data: object, fmt: str) -> object:
        """Format to target."""
        if fmt == "flat" and isinstance(data, dict):
            return self._flatten(data)
        return data

def _flatten(self: Any, data: Dict, prefix: str) -> Dict[str, object]:
        """Flatten nested dict."""
        result = {}
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten(value, new_key))
            else:
                result[new_key] = value
        return result

def format_data(data: object, config: Optional[Dict] = None) -> FormattedOutput:
    """Convenience function for formatting."""
    return FormatScriptsContext(config).format(data)
