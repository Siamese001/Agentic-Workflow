"""Failure fingerprinting engine for deterministic failure clustering."""

from __future__ import annotations

import re
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

from .types import FailureEvent, FailureFingerprint


class FailureFingerprinter:
    """Deterministic failure fingerprinter for clustering recurring failures."""

    def __init__(self, allow_absolute_paths: bool = False):
        """Initialize fingerprinter with configuration."""
        self.allow_absolute_paths = allow_absolute_paths

    def fingerprint(self, event: FailureEvent) -> FailureFingerprint:
        """Generate deterministic fingerprint for failure event."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FailureFingerprinter.fingerprint")

        if not isinstance(event, FailureEvent):
            raise TypeError(f"Expected FailureEvent, got {type(event).__name__}")
        normalized_event = self._normalize_event(event)
        canonical_bytes = normalized_event.canonical_bytes()
        return FailureFingerprint.from_canonical_bytes(canonical_bytes)

    def _normalize_event(self, event: FailureEvent) -> FailureEvent:
        """Normalize failure event for deterministic fingerprinting."""
        normalized_exc_type = self._normalize_exception_type(event.exc_type)
        normalized_error_code = self._normalize_error_code(event.error_code)
        normalized_component = self._normalize_component(event.component)
        normalized_symbols = self._normalize_symbols(event.symbols)
        normalized_metadata = self._normalize_metadata(event.metadata)
        return FailureEvent(
            exc_type=normalized_exc_type,
            error_code=normalized_error_code,
            component=normalized_component,
            symbols=normalized_symbols,
            metadata=normalized_metadata,
        )

    def _normalize_exception_type(self, exc_type: str) -> str:
        """Normalize exception type to fully qualified name."""
        if not exc_type:
            raise ValueError("Exception type cannot be empty")
        if "." in exc_type:
            return exc_type.split(".")[-1]
        return exc_type

    def _normalize_error_code(self, error_code: str) -> str:
        """Normalize error code to stable string."""
        if not error_code:
            return "UNKNOWN"
        return re.sub("[^A-Z0-9_]", "", error_code.upper())

    def _normalize_component(self, component: str) -> str:
        """Normalize component to stable identifier."""
        if not component:
            return "unknown_component"
        if not self.allow_absolute_paths:
            component = component.replace("\\", "/")
            component = re.sub("^[A-Za-z]:/", "", component)
            component = re.sub("^/", "", component)
            if "/" in component:
                component = component.rsplit("/", 1)[-1]
        component = component.replace("\\", "/").lower()
        for prefix in ["src/", "app/", "lib/", ""]:
            if component.startswith(prefix):
                component = component[len(prefix) :]
                break
        return component or "unknown_component"

    def _normalize_symbols(self, symbols: list[str]) -> list[str]:
        """Normalize symbols to sorted unique list."""
        if not symbols:
            return []
        normalized = []
        for symbol in symbols:
            if not symbol:
                continue
            symbol = re.sub(":\\d+$", "", symbol)
            symbol = re.sub("^.*[\\\\/]", "", symbol)
            symbol = symbol.strip()
            if symbol:
                normalized.append(symbol)
        return sorted(set(normalized))

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, str]:
        """Normalize metadata with allowlist and deterministic stringification."""
        if not metadata:
            return {}
        allowlist = {
            "message",
            "code",
            "status",
            "severity",
            "category",
            "retry_count",
            "timeout",
            "version",
            "phase",
        }
        normalized = {}
        for key, value in metadata.items():
            if key.lower() not in allowlist:
                continue
            if value is None:
                str_value = "null"
            elif isinstance(value, bool):
                str_value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                str_value = str(value)
            else:
                str_value = str(value).strip()
                if key.lower() == "message":
                    str_value = re.sub("\\s+at line \\d+$", "", str_value)
                    str_value = re.sub("\\s+line \\d+$", "", str_value)
            normalized[key] = str_value
        return normalized
