"""Agentic Span Processor - Custom OpenTelemetry span processing for agentic workflows.

Phase 4: Advanced span processors and filtering.
Provides custom span processors that:
1. Filter spans by layer/component for targeted analysis
2. Enrich spans with agentic-specific attributes
3. Correlate spans with Runtime ADG snapshots
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_telemetry_event,
    record_execution_trace,
)

logger = logging.getLogger(__name__)


class AgenticSpanProcessor:
    """Custom span processor for agentic workflow telemetry.

        Filters and enriches OpenTelemetry spans with agentic-specific
    d    context before export to backends.

        Attributes
        ----------
        _filters : list[Callable[[dict[str, Any]], bool]]
            Active span filters
        _enrichers : list[Callable[[dict[str, Any]], dict[str, Any]]]
            Active span enrichers
        _layer_filter : set[str] | None
            Layers to include (None = all layers)
        _component_filter : set[str] | None
            Components to include (None = all components)
    """

    def __init__(
        self,
        layer_filter: set[str] | None = None,
        component_filter: set[str] | None = None,
    ):
        """Initialize agentic span processor.

        Parameters
        ----------
        layer_filter : set[str] | None
            Set of layer names to filter by (e.g., {"L1_Cognition", "L2_Execution"})
        component_filter : set[str] | None
            Set of component names to filter by
        """
        self._filters: list[Callable[[dict[str, Any]], bool]] = []
        self._enrichers: list[Callable[[dict[str, Any]], dict[str, Any]]] = []
        self._layer_filter = layer_filter
        self._component_filter = component_filter

        # Add default filters
        if layer_filter:
            self.add_filter(self._layer_filter_func)
        if component_filter:
            self.add_filter(self._component_filter_func)

        record_execution_trace("agentic_span_processor", "agentic_span_processor_init")

    def add_filter(self, filter_func: Callable[[dict[str, Any]], bool]) -> None:
        """Add a custom span filter.

        Parameters
        ----------
        filter_func : Callable[[dict], bool]
            Function that takes span dict and returns True to keep
        """
        self._filters.append(filter_func)

    def add_enricher(self, enricher_func: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        """Add a custom span enricher.

        Parameters
        ----------
        enricher_func : Callable[[dict], dict]
            Function that takes span dict and returns enriched dict
        """
        self._enrichers.append(enricher_func)

    def _layer_filter_func(self, span: dict[str, Any]) -> bool:
        """Filter spans by layer."""
        if not self._layer_filter:
            return True
        layer = span.get("attributes", {}).get("layer", "")
        return layer in self._layer_filter

    def _component_filter_func(self, span: dict[str, Any]) -> bool:
        """Filter spans by component."""
        if not self._component_filter:
            return True
        component = span.get("attributes", {}).get("component", "")
        return component in self._component_filter

    def process_span(self, span: dict[str, Any]) -> dict[str, Any] | None:
        """Process a single span through filters and enrichers.

        Parameters
        ----------
        span : dict[str, Any]
            OpenTelemetry span dictionary

        Returns
        -------
        dict[str, Any] | None
            Processed span or None if filtered out
        """
        # Apply filters
        for filter_func in self._filters:
            if not filter_func(span):
                return None

        # Apply enrichers
        enriched = span
        for enricher_func in self._enrichers:
            enriched = enricher_func(enriched)

        return enriched

    def process_spans(self, spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process multiple spans.

        Parameters
        ----------
        spans : list[dict[str, Any]]
            List of OpenTelemetry span dictionaries

        Returns
        -------
        list[dict[str, Any]]
            Filtered and enriched spans
        """
        processed = []
        for span in spans:
            result = self.process_span(span)
            if result is not None:
                processed.append(result)

        _emit_records_telemetry_event(
            "agentic_span_processor",
            "L4_STATE",
            "spans_processed",
            input_count=len(spans),
            output_count=len(processed),
        )

        return processed


class RuntimeADGSpanEnricher:
    """Enriches spans with Runtime ADG correlation attributes.

    Adds snapshot IDs and graph correlation to spans for
    Runtime ADG materialization.
    """

    def __init__(self, snapshot_id: str | None = None):
        """Initialize enricher with optional snapshot ID.

        Parameters
        ----------
        snapshot_id : str | None
            Runtime ADG snapshot ID to correlate with
        """
        self._snapshot_id = snapshot_id

    def enrich(self, span: dict[str, Any]) -> dict[str, Any]:
        """Enrich span with Runtime ADG attributes.

        Parameters
        ----------
        span : dict[str, Any]
            Input span dictionary

        Returns
        -------
        dict[str, Any]
            Enriched span dictionary
        """
        if "attributes" not in span:
            span["attributes"] = {}

        # Add Runtime ADG correlation
        if self._snapshot_id:
            span["attributes"]["runtime_adg.snapshot_id"] = self._snapshot_id

        # Add graph node ID from span ID
        span["attributes"]["runtime_adg.node_id"] = f"node_{span.get('span_id', 'unknown')}"

        # Add parent relationship if exists
        parent_id = span.get("parent_span_id")
        if parent_id:
            span["attributes"]["runtime_adg.parent_node_id"] = f"node_{parent_id}"

        return span


def create_layer_filtered_processor(
    layers: set[str],
) -> AgenticSpanProcessor:
    """Factory for layer-filtered span processor.

    Parameters
    ----------
    layers : set[str]
        Layers to include (e.g., {"L1_Cognition", "L3_Orchestration"})

    Returns
    -------
    AgenticSpanProcessor
        Configured processor filtering by layer
    """
    processor = AgenticSpanProcessor(layer_filter=layers)

    # Add Runtime ADG enrichment
    enricher = RuntimeADGSpanEnricher()
    processor.add_enricher(enricher.enrich)

    return processor


def create_cognitive_telemetry_processor() -> AgenticSpanProcessor:
    """Factory for cognitive layer telemetry processor.

    Returns
    -------
    AgenticSpanProcessor
        Processor focused on L1_Cognition telemetry
    """
    return create_layer_filtered_processor({"L1_Cognition"})


def create_execution_telemetry_processor() -> AgenticSpanProcessor:
    """Factory for execution layer telemetry processor.

    Returns
    -------
    AgenticSpanProcessor
        Processor focused on L2_Execution telemetry
    """
    return create_layer_filtered_processor({"L2_Execution"})


def create_orchestration_telemetry_processor() -> AgenticSpanProcessor:
    """Factory for orchestration layer telemetry processor.

    Returns
    -------
    AgenticSpanProcessor
        Processor focused on L3_Orchestration telemetry
    """
    return create_layer_filtered_processor({"L3_Orchestration"})
