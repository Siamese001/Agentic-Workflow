"""OpenTelemetry-backed sink for ``IngressMetrics``.

Closes deferred gap W7.2 from plan ``request-intake-w7-deferred-4c8e1f``.
This module bridges the transport-agnostic :class:`IngressMetricsSink`
protocol to OpenTelemetry's ``Counter`` and ``Histogram`` primitives.

Design notes:

* OTEL is an optional dependency. If ``opentelemetry.metrics`` is unavailable,
  ``OtelMetricsSink`` raises ``ImportError`` on construction so deployments
  that depend on it fail fast instead of silently no-op'ing.
* Counters and histograms are created lazily, one per ``(metric_name, label-key
  tuple)`` combination. This matches the contract in ``ingress_telemetry`` and
  keeps cardinality under the caller's control.
* A ``StubMeter`` is provided so tests can verify forwarding behaviour without
  depending on the OTEL SDK.

Layer authority: L6 (observability — counters and histograms), invoked through
the L5 :class:`IngressMetrics` façade.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable


@runtime_checkable
class _MeterCounter(Protocol):
    def add(self, value: int | float, attributes: dict[str, str] | None = None) -> None: ...


@runtime_checkable
class _MeterHistogram(Protocol):
    def record(self, value: int | float, attributes: dict[str, str] | None = None) -> None: ...


@runtime_checkable
class Meter(Protocol):
    """Minimal subset of the OTEL Meter surface we actually use."""

    def create_counter(self, name: str, *, description: str = "", unit: str = "") -> _MeterCounter: ...

    def create_histogram(self, name: str, *, description: str = "", unit: str = "") -> _MeterHistogram: ...


class OtelMetricsSink:
    """:class:`IngressMetricsSink` that forwards to an OTEL :class:`Meter`.

    ``meter`` may be any object satisfying the :class:`Meter` protocol. In
    production it is typically the result of
    ``opentelemetry.metrics.get_meter(__name__)``; in tests it may be a
    :class:`StubMeter` instance for determinism.
    """

    _COUNTER_DESCRIPTIONS = {
        "ingress_requests_total": "Total ingress requests by outcome.",
        "ingress_rejections_total": "Total ingress rejections by reason_code + gate_stage.",
        "ingress_clarifications_total": "Total ingress clarifications by reason.",
    }
    _HISTOGRAM_DESCRIPTIONS = {
        "ingress_latency_ms": "Ingress gate latency, milliseconds, by outcome.",
    }

    def __init__(self, meter: Meter | None = None) -> None:
        if meter is None:
            meter = self._load_default_meter()
        self._meter: Meter = meter
        self._counters: dict[str, _MeterCounter] = {}
        self._histograms: dict[str, _MeterHistogram] = {}

    @staticmethod
    def _load_default_meter() -> Meter:
        try:
            from opentelemetry import metrics  # type: ignore[import-not-found]
        except ImportError as exc:  # guardian: allow-import-fail -- OTEL is optional at runtime; surface a clear error by re-raising with an install hint
            raise ImportError(
                "opentelemetry.metrics is not installed; install opentelemetry-api to use OtelMetricsSink."
            ) from exc
        return metrics.get_meter("agentic_core.ingress")

    # ------------------------------------------------------------------ Sink protocol
    def incr(self, metric: str, *, labels: dict[str, str] | None = None) -> None:
        counter = self._counters.get(metric)
        if counter is None:
            counter = self._meter.create_counter(
                metric,
                description=self._COUNTER_DESCRIPTIONS.get(metric, ""),
                unit="1",
            )
            self._counters[metric] = counter
        counter.add(1, labels or None)

    def observe(self, metric: str, value: float, *, labels: dict[str, str] | None = None) -> None:
        hist = self._histograms.get(metric)
        if hist is None:
            hist = self._meter.create_histogram(
                metric,
                description=self._HISTOGRAM_DESCRIPTIONS.get(metric, ""),
                unit="ms" if metric.endswith("_ms") else "1",
            )
            self._histograms[metric] = hist
        hist.record(value, labels or None)


# ---------------------------------------------------------------------------
# Stub meter for unit tests — no OTEL dependency.
# ---------------------------------------------------------------------------


class _StubCounter:
    def __init__(self, name: str) -> None:
        self.name = name
        self.events: list[tuple[int | float, dict[str, str] | None]] = []

    def add(self, value: int | float, attributes: dict[str, str] | None = None) -> None:
        self.events.append((value, attributes))


class _StubHistogram:
    def __init__(self, name: str) -> None:
        self.name = name
        self.events: list[tuple[int | float, dict[str, str] | None]] = []

    def record(self, value: int | float, attributes: dict[str, str] | None = None) -> None:
        self.events.append((value, attributes))


class StubMeter:
    """Deterministic in-memory meter for tests.

    Usage::

        meter = StubMeter()
        sink = OtelMetricsSink(meter)
        ...
        assert meter.counters["ingress_requests_total"].events == [...]
    """

    def __init__(self) -> None:
        self.counters: dict[str, _StubCounter] = {}
        self.histograms: dict[str, _StubHistogram] = {}

    def create_counter(
        self,
        name: str,
        *,
        description: str = "",
        unit: str = "",  # noqa: ARG002
    ) -> _StubCounter:
        if name not in self.counters:
            self.counters[name] = _StubCounter(name)
        return self.counters[name]

    def create_histogram(
        self,
        name: str,
        *,
        description: str = "",
        unit: str = "",  # noqa: ARG002
    ) -> _StubHistogram:
        if name not in self.histograms:
            self.histograms[name] = _StubHistogram(name)
        return self.histograms[name]


# ---------------------------------------------------------------------------
# Wiring helper for process-start code.
# ---------------------------------------------------------------------------


def install_otel_sink(
    meter_factory: Callable[[], Meter] | None = None,
) -> OtelMetricsSink:
    """Install an ``OtelMetricsSink`` as the default ingress metrics sink.

    ``meter_factory`` is an optional callable returning a :class:`Meter`
    instance. When None, OTEL's ``get_meter`` is used (requires
    ``opentelemetry-api`` to be installed).

    Returns the installed sink so the caller can retain a reference.
    """

    from agentic_core.L5_safety.enforcement.ingress_telemetry import set_default_sink

    meter = meter_factory() if meter_factory is not None else None
    sink = OtelMetricsSink(meter) if meter is not None else OtelMetricsSink()
    set_default_sink(sink)
    return sink


__all__ = [
    "Meter",
    "OtelMetricsSink",
    "StubMeter",
    "install_otel_sink",
]


# Silence a harmless "unused import for Any" warning when the static analyzer
# inlines protocols — keep the Any symbol re-exported for introspection tests.
_ = Any
