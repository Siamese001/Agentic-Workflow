"""Single runtime-safe tracing bootstrap seam for the shared run path.

This is a thin, status-returning wrapper over
:func:`agentic_core.tracing.provider_bootstrap.ensure_tracer_provider_from_env`.
Its job is to give the live runtime (the integrated single-action spine, the
Exit-eval factory) **one** call to make early — before any emitter resolves its
tracer or any span sink is constructed — that:

1. Installs a recording OTEL ``TracerProvider`` **iff** the operator opted in via
   the standard ``OTEL_*`` environment variables (external export stays env-gated
   and default-OFF), and
2. Reports, in a small structured status, what happened — so receipts and tests
   can assert the bootstrap ran without scraping logs.

Local, deterministic span *records* (the dict-shaped spans appended by
``L6_system_learning.runtime_adg.runtime_span_emitter`` and consumed by the L6
shadow-exhaust adapter) do **not** depend on this bootstrap or on an external
OTLP collector — they are always available. ``local_capture_enabled`` records
that invariant. External OTLP export is the only thing gated by env here.

Contract: :func:`bootstrap_runtime_tracing` is idempotent (delegating to the
once-per-process guard in ``provider_bootstrap``), env-gated, and **fail-soft**
— it never raises. It contains no app-specific literals; per-app service
identity flows only through ``OTEL_SERVICE_NAME`` inside ``provider_bootstrap``.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from agentic_core.tracing import provider_bootstrap

_LOGGER = logging.getLogger(__name__)

__all__ = ["RuntimeTracingStatus", "bootstrap_runtime_tracing"]


@dataclass(frozen=True, slots=True)
class RuntimeTracingStatus:
    """Structured result of one :func:`bootstrap_runtime_tracing` call.

    Attributes:
        external_otel_activation: ``"disabled"`` or ``"enabled:<kind>"`` —
            the opt-in state read from ``OTEL_TRACES_EXPORTER`` *before*
            provider installation was attempted.
        provider_bootstrap_status: the raw status string returned by
            ``ensure_tracer_provider_from_env`` (e.g. ``disabled_env_unset``,
            ``console_installed``, ``provider_already_installed``,
            ``sdk_unavailable``, ``bootstrap_failed:<ExcType>``).
        local_capture_enabled: always ``True`` — local deterministic runtime
            span *records* are produced by the runtime adapters regardless of
            external OTEL export, and are the source L6 shadow ingest reads.
        collector_export_mode: ``"none"`` when external export is disabled;
            otherwise the selected exporter kind (``"otlp"``, ``"console"``,
            or ``"unknown:<kind>"``). The collector inbox only receives spans
            for ``"otlp"`` runs.
        collector_endpoint: OTLP endpoint selected by the environment, when
            applicable. Empty when export is disabled or non-OTLP.
        l6_observability_role: stable label documenting that L6 consumes local
            span records/raw exhaust as runtime evidence; it does not own
            provider bootstrap or collector transport.
    """

    external_otel_activation: str
    provider_bootstrap_status: str
    collector_export_mode: str
    collector_endpoint: str
    local_capture_enabled: bool = True
    l6_observability_role: str = "consume_local_span_records"

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable operator-facing status mapping."""
        return {
            "external_otel_activation": self.external_otel_activation,
            "provider_bootstrap_status": self.provider_bootstrap_status,
            "collector_export_mode": self.collector_export_mode,
            "collector_endpoint": self.collector_endpoint,
            "local_capture_enabled": self.local_capture_enabled,
            "l6_observability_role": self.l6_observability_role,
        }


def _collector_export_mode() -> tuple[str, str]:
    """Return ``(mode, endpoint)`` for the current external export env."""
    kind = os.environ.get("OTEL_TRACES_EXPORTER", "").strip().lower()
    if not kind:
        return "none", ""
    if kind == "otlp":
        endpoint = (
            os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "").strip()
            or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
        )
        return "otlp", endpoint
    if kind == "console":
        return "console", ""
    return f"unknown:{kind}", ""


def bootstrap_runtime_tracing() -> RuntimeTracingStatus:
    """Ensure the OTEL provider is installed (env-gated) and report status.

    The single runtime-level bootstrap seam. Call it once, early, on the shared
    run path before any emitter resolves its tracer or any span sink is built.

    External OTEL export remains env-gated (no-op unless ``OTEL_TRACES_EXPORTER``
    is set). Local deterministic span capture is always enabled by the runtime
    adapters. Never raises.
    """
    # Resolve through the module (late binding) so a monkeypatched
    # ``provider_bootstrap.ensure_tracer_provider_from_env`` is honored, and no
    # stale function reference is frozen into this module's namespace (which
    # would otherwise leak test-injected spies across cases).
    before = provider_bootstrap.otel_activation_status()
    collector_export_mode, collector_endpoint = _collector_export_mode()
    try:
        status = provider_bootstrap.ensure_tracer_provider_from_env()
    except Exception as exc:  # guardian: allow-broad-exception -- tracing bootstrap is best-effort; must never break the run path
        # ensure_tracer_provider_from_env is already fail-soft, but this seam
        # guarantees the runtime contract ("never raises") even if that changes.
        _LOGGER.warning("runtime_tracing_bootstrap_failed: %r", exc)
        status = f"bootstrap_failed:{type(exc).__name__}"
    return RuntimeTracingStatus(
        external_otel_activation=before,
        provider_bootstrap_status=status,
        collector_export_mode=collector_export_mode,
        collector_endpoint=collector_endpoint,
        local_capture_enabled=True,
    )
