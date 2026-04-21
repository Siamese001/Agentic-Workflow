"""
Environment Validator Service — apps_shared

Service for validating environment configuration.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Iterable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_reads_environ,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

_log = logging.getLogger(__name__)


class EnvironmentValidatorService:
    """Service for validating environment configuration."""

    REQUIRED_VARS = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the environment validator service."""
        self.config = config or {}
        self.required_vars = self._build_required_vars()

        # Lifecycle trace emission
        emit_replay_key("env_validator", "init")
        emit_determinism_digest("env_validator", "init")
        _emit_applies_guardrail("p0", "env_validator", "service_init")
        _emit_snapshots_state("p0", "env_validator", "service_state")

    def _build_required_vars(self) -> tuple[str, ...]:
        configured = self.config.get("required_vars", self.REQUIRED_VARS)
        if isinstance(configured, str):
            configured = [configured]
        cleaned = []
        seen: set[str] = set()
        for item in configured:
            name = str(item).strip()
            if name and name not in seen:
                cleaned.append(name)
                seen.add(name)
        return tuple(cleaned)

    def validate_environment(self) -> dict[str, Any]:
        """Validate required environment variables."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "EnvironmentValidatorService.validate_environment",
        )
        _emit_reads_environ("p2", "env_validator", "env_read")
        _emit_validates_capability("p2", "env_validator", "validation")
        _emit_records_telemetry_event("p4", "env_validator", "validation_start")

        missing: list[str] = []
        present: list[str] = []

        for var in self.required_vars:
            if self.is_var_set(var):
                present.append(var)
            else:
                missing.append(var)

        result = {
            "valid": len(missing) == 0,
            "present": present,
            "missing": missing,
            "total_required": len(self.required_vars),
        }

        if missing:
            _log.warning("Missing environment variables: %s", missing)
            _emit_applies_guardrail("p0", "env_validator", "missing_env_vars")

        _emit_records_telemetry_event(
            "p4",
            "env_validator",
            f"validation_complete:{'valid' if result['valid'] else 'invalid'}",
        )

        return result

    def get_env_var(self, var_name: str, default: str | None = None) -> str | None:
        """Get environment variable with optional default."""
        value = os.environ.get(var_name)
        if value is None or value.strip() == "":
            return default
        return value

    def is_var_set(self, var_name: str) -> bool:
        """Check if an environment variable is set and non-empty."""
        return self.get_env_var(var_name) is not None

    def redact_env_snapshot(self, names: Iterable[str] | None = None) -> dict[str, str]:
        """Return a redacted snapshot suitable for logs or telemetry."""
        result: dict[str, str] = {}
        for name in names or self.required_vars:
            value = self.get_env_var(name)
            result[name] = "<set>" if value is not None else "<missing>"
        return result
