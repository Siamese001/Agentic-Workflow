"""
PrepareResumeContext.py - Formatting Module

Domain: resume
Generated: 2025-12-07T13:28:54.194597
"""

import logging
from typing import Union, Dict, Optional
from shared.result_types import FormatResult

Logger = logging.getLogger(__name__)





class PrepareResumeContext:
    """Formatter for resume domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        self.config = config or {}
        self.format_type = self.config.get("format", "default")
        Logger.info(f"Initialized {self.__class__.__name__}")

    def format(self, data: Union[str, Dict], target: Optional[str] = None) -> FormatResult:
        """Format input data into the required output structure."""
        fmt = target or self.format_type
        transformed = self._transform(data)
        return FormatResult(data=transformed, format_type=fmt)

    def _transform(self, data: Union[str, Dict]) -> object:
        """Transform data."""
        if isinstance(data, str):
            return data.strip()
        return data


def FormatData(data: Union[str, Dict], config: Optional[Dict] = None) -> FormatResult:
    """Format input data into the required output structure."""
    return PrepareResumeContext(config).format(data)
