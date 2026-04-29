"""Semantic-convention constants for OpenTelemetry spans emitted by the repo.

Per ADR-062, all retrieval-stage emitters import attribute keys from
``agentic_core.L6_observability.semconv.rag`` rather than using raw string
literals. Per ADR-074 (2026-04-29), all GenAI agent/workflow/tool/model
spans align with the OpenTelemetry GenAI SIG semconv via the ``gen_ai``
sub-module — see ``agentic_core/L6_observability/semconv/gen_ai.py``.

This package is the single source of truth for OTel span attribute names.
"""

from agentic_core.L6_observability.semconv import gen_ai, rag

__all__ = ["gen_ai", "rag"]
