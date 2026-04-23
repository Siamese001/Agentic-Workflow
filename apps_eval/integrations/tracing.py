"""OpenTelemetry tracing adapter for the apps_eval harness.

Previously, apps_eval relied on `apps_eval._telemetry` — a no-op shim that
returned None for every `_emit_*` call. This module is the replacement:
a thin, dependency-light wrapper around the OpenTelemetry API that:

  * Returns a real `NoOpTracer` (from opentelemetry.trace) when no SDK
    TracerProvider is configured — so calling code never needs to branch.
  * Returns the globally-configured tracer when the host process has
    installed an SDK TracerProvider (e.g., Jaeger / OTLP exporter).
  * Honours the env var `APPS_EVAL_OTEL_ENABLED=1` to attach an in-process
    SDK TracerProvider with a console exporter for local debugging.

Design constraints
------------------
1. **Fail-open**: import must succeed even if the SDK is missing. All
   span creation falls through to NoOpTracer in that case.
2. **No wall-clock used for tracing control flow**: OTel SDK handles
   timestamps internally.
3. **No singletons that hide state**: a module-level helper returns the
   current tracer; callers may also instantiate their own
   ``EvalTracing`` if they want isolated scope.
4. **Back-compat with the legacy `_emit_*` shim**: the legacy no-op
   functions remain importable from ``apps_eval._telemetry`` for any
   code that still references them. New code should use the
   ``eval_span`` context manager exposed here.

Plan reference: `.windsurf/plans/eval-meta-otel-gap-review-ef4a20.md`
Wave W3 (eval-side tracing).
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Iterator

logger = logging.getLogger(__name__)


SPAN_NAMESPACE = "apps_eval.v1"
_ENV_ENABLE_SDK = "APPS_EVAL_OTEL_ENABLED"


def _try_install_sdk_provider() -> bool:
    """Install an SDK TracerProvider with a console exporter if requested.

    Returns True if the SDK provider was installed (or already installed).
    Returns False if the SDK is absent or the env var is unset.

    This function is idempotent: calling it multiple times installs the
    provider only once because `trace.set_tracer_provider` no-ops on an
    already-set provider.
    """
    if os.environ.get(_ENV_ENABLE_SDK, "").strip() not in {"1", "true", "TRUE", "yes"}:
        return False
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )
    except ImportError as exc:  # pragma: no cover - SDK absent in minimal envs
        logger.info("apps_eval tracing: SDK unavailable (%s); using NoOpTracer", exc)
        return False

    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        return True  # already installed
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    logger.info("apps_eval tracing: installed SDK TracerProvider with ConsoleSpanExporter")
    return True


def get_tracer(name: str = SPAN_NAMESPACE) -> Any:
    """Return the current OTel tracer (SDK or NoOp).

    Uses the OTel API's global provider. When no SDK provider is set, the
    API returns a NoOpTracer whose context manager still works — so
    callers can always write::

        with get_tracer().start_as_current_span("eval.scorecard.compute") as span:
            span.set_attribute("eval.suite_count", 12)
            ...

    without branching on whether OTel is configured.
    """
    try:
        from opentelemetry import trace
    except ImportError:  # pragma: no cover - API absent
        # Return a minimal duck-type tracer
        return _FallbackTracer()

    _try_install_sdk_provider()
    return trace.get_tracer(name)


class _FallbackTracer:
    """Last-resort tracer when even the opentelemetry-api package is missing.

    Exposes only ``start_as_current_span`` as a context manager returning a
    no-op span. Used only in environments where the API package itself is
    absent.
    """

    @contextmanager
    def start_as_current_span(
        self,
        name: str,  # noqa: ARG002 - match OTel signature
        attributes: dict[str, Any] | None = None,  # noqa: ARG002
        **_: Any,
    ) -> Iterator["_FallbackSpan"]:
        yield _FallbackSpan()


class _FallbackSpan:
    """No-op span surface matching the subset of OTel span API used here."""

    def set_attribute(self, key: str, value: Any) -> None:  # noqa: ARG002
        return None

    def set_attributes(self, attrs: dict[str, Any]) -> None:  # noqa: ARG002
        return None

    def record_exception(self, exception: BaseException) -> None:  # noqa: ARG002
        return None

    def set_status(self, status: Any) -> None:  # noqa: ARG002
        return None


@contextmanager
def eval_span(
    name: str,
    *,
    attributes: dict[str, Any] | None = None,
    tracer_name: str = SPAN_NAMESPACE,
) -> Iterator[Any]:
    """Context manager that wraps an eval-lab operation in an OTel span.

    Example::

        from apps_eval.integrations.tracing import eval_span

        with eval_span("apps_eval.v1.scorecard.compute",
                       attributes={"eval.suite_count": len(suites)}) as span:
            result = engine.compute(suites)
            span.set_attribute("eval.overall_score", result.overall_score)
    """
    tracer = get_tracer(tracer_name)
    # OTel span API: attributes kw is standard
    with tracer.start_as_current_span(name, attributes=attributes or {}) as span:
        try:
            yield span
        except BaseException as exc:  # re-raise after recording
            try:
                span.record_exception(exc)
            except (
                AttributeError,
                TypeError,
                RuntimeError,
            ):  # guardian: allow-log-and-swallow -- span exception recording is best-effort telemetry
                logger.debug("eval_span: exception recording failed for %s", name)
            raise


__all__ = [
    "SPAN_NAMESPACE",
    "eval_span",
    "get_tracer",
]
