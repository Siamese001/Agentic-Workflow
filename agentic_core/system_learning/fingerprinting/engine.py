"""Failure fingerprinting engine for deterministic failure clustering."""

from __future__ import annotations

import re
from typing import Any

from .types import FailureEvent, FailureFingerprint


class FailureFingerprinter:
    """Deterministic failure fingerprinter for clustering recurring failures."""

    def __init__(self, allow_absolute_paths: bool = False):
        """Initialize fingerprinter with configuration."""
        self.allow_absolute_paths = allow_absolute_paths

    def fingerprint(self, event: FailureEvent) -> FailureFingerprint:
        """Generate deterministic fingerprint for failure event."""
        # Validate input
        if not isinstance(event, FailureEvent):
            raise TypeError(f"Expected FailureEvent, got {type(event).__name__}")

        # Normalize the event
        normalized_event = self._normalize_event(event)

        # Create canonical bytes and fingerprint
        canonical_bytes = normalized_event.canonical_bytes()
        return FailureFingerprint.from_canonical_bytes(canonical_bytes)

    def _normalize_event(self, event: FailureEvent) -> FailureEvent:
        """Normalize failure event for deterministic fingerprinting."""

        # Normalize exception type (fully qualified)
        normalized_exc_type = self._normalize_exception_type(event.exc_type)

        # Normalize error code (stable enum/string)
        normalized_error_code = self._normalize_error_code(event.error_code)

        # Normalize component (stable component id)
        normalized_component = self._normalize_component(event.component)

        # Normalize symbols (sorted unique list)
        normalized_symbols = self._normalize_symbols(event.symbols)

        # Normalize metadata (allowlist, sorted keys, deterministic values)
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

        # Remove any module path variations, keep only class name
        if "." in exc_type:
            # Keep the last part (class name) for stability
            return exc_type.split(".")[-1]

        return exc_type

    def _normalize_error_code(self, error_code: str) -> str:
        """Normalize error code to stable string."""
        if not error_code:
            return "UNKNOWN"

        # Convert to uppercase and remove non-alphanumeric chars
        return re.sub(r"[^A-Z0-9_]", "", error_code.upper())

    def _normalize_component(self, component: str) -> str:
        """Normalize component to stable identifier."""
        if not component:
            return "unknown_component"

        if not self.allow_absolute_paths:
            # Normalise separators first
            component = component.replace("\\", "/")
            # Strip leading drive letter (Windows) or leading slash (Unix)
            component = re.sub(r"^[A-Za-z]:/", "", component)
            component = re.sub(r"^/", "", component)
            # Keep only the base filename stem (strip all parent directories)
            if "/" in component:
                component = component.rsplit("/", 1)[-1]

        # Normalize separators and lowercase
        component = component.replace("\\", "/").lower()

        # Remove common prefixes
        for prefix in ["src/", "app/", "lib/", ""]:
            if component.startswith(prefix):
                component = component[len(prefix) :]
                break

        return component or "unknown_component"

    def _normalize_symbols(self, symbols: list[str]) -> list[str]:
        """Normalize symbols to sorted unique list."""
        if not symbols:
            return []

        # Normalize each symbol
        normalized = []
        for symbol in symbols:
            if not symbol:
                continue

            # Remove line numbers and common prefixes
            symbol = re.sub(r":\d+$", "", symbol)  # Remove line numbers
            symbol = re.sub(r"^.*[\\/]", "", symbol)  # Remove path, keep function name

            # Normalize
            symbol = symbol.strip()
            if symbol:
                normalized.append(symbol)

        # Return sorted unique list
        return sorted(set(normalized))

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, str]:
        """Normalize metadata with allowlist and deterministic stringification."""
        if not metadata:
            return {}

        # Allowlist of metadata keys to include
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
            # Only include allowlisted keys
            if key.lower() not in allowlist:
                continue

            # Convert value to string deterministically
            if value is None:
                str_value = "null"
            elif isinstance(value, bool):
                str_value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                str_value = str(value)
            else:
                str_value = str(value).strip()
                # Strip trailing line number references for stability
                # e.g. "error at line 145" -> "error at line"
                if key.lower() == "message":
                    str_value = re.sub(r"\s+at line \d+$", "", str_value)
                    str_value = re.sub(r"\s+line \d+$", "", str_value)

            normalized[key] = str_value

        return normalized
