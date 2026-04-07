"""
otlp_exporter.py - Exporter Module

Domain: tracing
Generated: 2025-12-07T12:07:59.860156
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExportResult:
    """Result of export operation."""

    success: bool
    items_exported: int
    destination: str
    errors: list[str] = None


class BaseExporter(ABC):
    """foundation class for exporters."""

    @abstractmethod
    def export(self, data: object) -> ExportResult:
        """Export data."""
        ...


class OtlpExporter(BaseExporter):
    """Exporter for tracing domain."""

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        self.destination = self.config.get("destination", "stdout")
        logger.info(f"Initialized {self.__class__.__name__}")

    def export(self, data: object) -> ExportResult:
        """Export data to destination."""
        try:
            items = data if isinstance(data, list) else [data]
            if self.destination == "stdout":
                for item in items:
                    logger.debug(json.dumps(item, default=str, indent=2))
            elif self.destination == "file":
                filepath = self.config.get("filepath", "export.json")
                with open(filepath, "w") as f:
                    json.dump(items, f, default=str, indent=2)
            return ExportResult(success=True, items_exported=len(items), destination=self.destination)
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            logger.error(f"Export failed: {e}")
            return ExportResult(
                success=False, items_exported=0, destination=self.destination, errors=[str(e)],
            )


def export_data(data: object, config: dict | None = None) -> ExportResult:
    """Convenience function for export."""
    return OtlpExporter(config).export(data)
