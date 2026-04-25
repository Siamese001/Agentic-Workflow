"""Semantic-convention constants for OpenTelemetry spans emitted by the repo.

Per ADR-062, all retrieval-stage emitters import attribute keys from
``agentic_core.L6_observability.semconv.rag`` rather than using raw string
literals. This package is the single source of truth.
"""

from agentic_core.L6_observability.semconv import rag

__all__ = ["rag"]
