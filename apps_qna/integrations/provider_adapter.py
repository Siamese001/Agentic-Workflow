"""Provider SDK integration adapter — D4.2.

Wraps the canonical agentic_core ClockProvider / WallClock injection layer
and exposes a thin apps_qna-specific provider surface for optional model
execution. apps_qna is a build-time compiler — it does NOT call a model
provider at pack-build time. This adapter is reserved for the future
R4_SINGLE_ACTION live-interview route where a provider call may be needed.

Surfaces:
  - QnaProviderContext: injectable clock + run metadata for provider calls
  - build_provider_context(): construct a QnaProviderContext from run params
  - get_timestamp(): thin wrapper over ClockProvider.now_iso() for tracing

The adapter is fail-open — if the canonical clock import fails, it falls
back to stdlib datetime. All provider calls are stubbed (no network I/O).

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D4.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QnaProviderContext:
    """Injectable context for apps_qna provider interactions.

    Attributes:
        request_id: Correlation id for this provider call.
        run_id: Run identifier.
        interview_slug: Interview slug for tracing.
        route_id: Selected route id.
        clock: Canonical ClockProvider instance (or None for wall-clock default).
        model_id: Target model identifier (empty = no model call).
        max_tokens: Maximum output tokens for a model call.
        temperature: Sampling temperature (0.0 = deterministic).
        extra: App-specific extra context for future extension.
    """

    request_id: str = ""
    run_id: str = ""
    interview_slug: str = ""
    route_id: str = ""
    clock: Any = None
    model_id: str = ""
    max_tokens: int = 0
    temperature: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    def now_iso(self) -> str:
        """Return current time as ISO-8601 string via injected clock or stdlib fallback."""
        if self.clock is not None and hasattr(self.clock, "now_iso"):
            try:
                return self.clock.now_iso()
            except Exception:
                pass
        try:
            from datetime import datetime, timezone
            return datetime.now(tz=timezone.utc).isoformat()
        except Exception:
            return "1970-01-01T00:00:00+00:00"

    def has_model(self) -> bool:
        """Return True if a model_id is configured for provider calls."""
        return bool(self.model_id)


def build_provider_context(
    *,
    request_id: str = "",
    run_id: str = "",
    interview_slug: str = "",
    route_id: str = "",
    model_id: str = "",
    max_tokens: int = 0,
    temperature: float = 0.0,
    inject_clock: Any = None,
    extra: dict[str, Any] | None = None,
) -> QnaProviderContext:
    """Construct a QnaProviderContext with canonical clock injection.

    Attempts to acquire the process-level ClockProvider from
    agentic_core.utils.runners.providers. Falls back to None (stdlib)
    if the import fails. The caller may also supply their own clock
    via inject_clock for test determinism.

    Args:
        request_id: Correlation id.
        run_id: Run id.
        interview_slug: Pack slug.
        route_id: Route id.
        model_id: Model identifier (leave empty for no-model context).
        max_tokens: Max output tokens.
        temperature: Sampling temperature.
        inject_clock: Optional ClockProvider override (e.g. FrozenClock).
        extra: App-specific extra dict.

    Returns:
        QnaProviderContext ready for use.
    """
    clock = inject_clock
    if clock is None:
        try:
            from agentic_core.utils.runners.providers import get_clock
            clock = get_clock()
        except Exception:
            clock = None

    return QnaProviderContext(
        request_id=request_id,
        run_id=run_id,
        interview_slug=interview_slug,
        route_id=route_id,
        clock=clock,
        model_id=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        extra=dict(extra) if extra else {},
    )


def get_timestamp(ctx: QnaProviderContext | None = None) -> str:
    """Return current ISO-8601 timestamp via context clock or stdlib.

    Args:
        ctx: Optional QnaProviderContext (uses its clock if provided).

    Returns:
        ISO-8601 timestamp string.
    """
    if ctx is not None:
        return ctx.now_iso()
    try:
        from agentic_core.utils.runners.providers import get_clock
        return get_clock().now_iso()
    except Exception:
        from datetime import datetime, timezone
        return datetime.now(tz=timezone.utc).isoformat()


__all__ = [
    "QnaProviderContext",
    "build_provider_context",
    "get_timestamp",
]
