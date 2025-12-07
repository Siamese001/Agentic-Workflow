"""
format_scripts_context.py - Formatting Module

Domain: utilities
Generated: 2025-12-07T12:07:54.862334
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FormattedOutput:
    """Result of formatting."""
    data: Any
    format_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class FormatScriptsContext:
    """Formatter for utilities domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.output_format = self.config.get("format", "default")
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def format(self, data: Any, target_format: Optional[str] = None) -> FormattedOutput:
        """Format data to target structure."""
        fmt = target_format or self.output_format
        transformed = self._transform(data)
        formatted = self._format_to_target(transformed, fmt)
        
        return FormattedOutput(
            data=formatted,
            format_type=fmt,
            metadata={"original_type": type(data).__name__}
        )
    
    def _transform(self, data: Any) -> Any:
        """Apply transformations."""
        if isinstance(data, str):
            return data.strip()
        return data
    
    def _format_to_target(self, data: Any, fmt: str) -> Any:
        """Format to target."""
        if fmt == "flat" and isinstance(data, dict):
            return self._flatten(data)
        return data
    
    def _flatten(self, data: Dict, prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dict."""
        result = {}
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten(value, new_key))
            else:
                result[new_key] = value
        return result


def format_data(data: Any, config: Optional[Dict] = None) -> FormattedOutput:
    """Convenience function for formatting."""
    return FormatScriptsContext(config).format(data)
