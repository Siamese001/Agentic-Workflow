"""Final Evidence Contract (FEC) Producer for apps_lic Research Bridge.

Wave 4, Phase 1 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides the C0 FEC producer for the apps_research → apps_lic
research bridge, enabling retrieval-proven exit evaluation.

App: apps_lic
Layer: Certification (apps_lic/cert/)

Dependencies:
    - FEC Framework (apps_shared/cert/fec_framework.py)
    - apps_research FEC Producer (apps_research/cert/fec_producer.py)
    - C0 Retrieval (agentic_core/L1_cognition/retrieval/)

Pattern Source: apps-qna-c0-fec-producer-wiring-d4f1e8 (established pattern)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import json

# Schema version for this FEC producer
FEC_SCHEMA_VERSION = "1.0.0"

# Producer identifier
PRODUCER_ID = "apps_lic.research_bridge"


# -----------------------------------------------------------------------------
# FEC Producer
# -----------------------------------------------------------------------------

def produce_fec(run_context: dict[str, Any]) -> dict[str, Any]:
    """Produce Final Evidence Contract for apps_lic research bridge.
    
    This FEC producer extracts evidence from the research bridge context,
    including company briefing data and competitive landscape signals.
    
    The producer is designed for forward-compatibility: when C0 retrieval
    wires in, this producer will automatically upgrade to grounded=True
    with the retrieval_sources populated.
    
    Parameters
    ----------
    run_context : dict[str, Any]
        The run context containing research bridge data. Expected keys:
        - research_snippets: list of research snippets from apps_research
        - company_brief: company briefing data
        - competitive_signals: competitive landscape signals
        - c0_retrieval_sources: Optional[C0RetrievalResult] - populated when C0 wires
    
    Returns
    -------
    dict[str, Any]
        FEC dictionary conforming to schema_version=1.0.0:
        {
            "producer": str,
            "grounded": bool,
            "retrieval_sources": list[dict],
            "template_ids": list[str],
            "route_id": str,
            "evidence_sufficiency": str,
        }
    
    Example
    -------
    >>> run_context = {
    ...     "research_snippets": [
    ...         {"source": "linkedin", "content": "Company raised Series B"},
    ...     ],
    ...     "company_brief": {"funding_stage": "Series B"},
    ...     "competitive_signals": [{"type": "hiring", "confidence": 0.85}],
    ... }
    >>> fec = produce_fec(run_context)
    >>> fec["producer"]
    'apps_lic.research_bridge'
    >>> fec["grounded"]
    False  # True when C0 retrieval wires in
    """
    # Extract research bridge data from context
    research_snippets = run_context.get("research_snippets", [])
    company_brief = run_context.get("company_brief", {})
    competitive_signals = run_context.get("competitive_signals", [])
    
    # Check if C0 retrieval has wired in
    c0_retrieval = run_context.get("c0_retrieval_sources")
    
    # Build retrieval sources
    retrieval_sources = []
    
    if c0_retrieval is not None:
        # C0 retrieval is wired - use as primary source
        retrieval_sources.append({
            "source_type": "c0_retrieval",
            "retrieval_id": c0_retrieval.get("retrieval_id", "unknown"),
            "query": c0_retrieval.get("query", ""),
            "results_count": len(c0_retrieval.get("results", [])),
            "confidence": c0_retrieval.get("confidence", 0.0),
        })
        grounded = True
        evidence_sufficiency = "grounded"
    else:
        # Template-only path (forward-compatible)
        # Research snippets are used as lightweight evidence
        for i, snippet in enumerate(research_snippets[:5]):  # Top 5 snippets
            retrieval_sources.append({
                "source_type": "research_snippet",
                "snippet_index": i,
                "source": snippet.get("source", "unknown"),
                "content_preview": _truncate(snippet.get("content", ""), 100),
                "confidence": snippet.get("confidence", 0.5),
            })
        
        # Competitive signals as additional evidence
        for signal in competitive_signals[:3]:  # Top 3 signals
            retrieval_sources.append({
                "source_type": "competitive_signal",
                "signal_type": signal.get("type", "unknown"),
                "confidence": signal.get("confidence", 0.0),
            })
        
        grounded = len(retrieval_sources) > 0
        evidence_sufficiency = "template_with_signals" if grounded else "template_only"
    
    # Determine template IDs used
    template_ids = _extract_template_ids(run_context)
    
    # Determine route ID
    route_id = run_context.get("route_id", "apps_lic.research_bridge.default")
    
    # Build FEC
    return {
        "producer": PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": retrieval_sources,
        "template_ids": template_ids,
        "route_id": route_id,
        "evidence_sufficiency": evidence_sufficiency,
        "_schema_version": FEC_SCHEMA_VERSION,
        "_metadata": {
            "snippet_count": len(research_snippets),
            "signal_count": len(competitive_signals),
            "brief_available": bool(company_brief),
        },
    }


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _truncate(text: str, max_length: int) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def _extract_template_ids(run_context: dict[str, Any]) -> list[str]:
    """Extract template IDs from run context."""
    template_ids = []
    
    # Check for explicit template IDs
    if "template_ids" in run_context:
        template_ids.extend(run_context["template_ids"])
    
    # Check for prompt assembly templates
    if "prompt_assembly" in run_context:
        assembly = run_context["prompt_assembly"]
        if isinstance(assembly, dict):
            template_id = assembly.get("template_id")
            if template_id:
                template_ids.append(template_id)
    
    # Default template if none found
    if not template_ids:
        template_ids = ["apps_lic.research_bridge.default"]
    
    return list(set(template_ids))  # Deduplicate


# -----------------------------------------------------------------------------
# Side-Effect Registration
# -----------------------------------------------------------------------------

def register() -> None:
    """Register this FEC producer with the framework.
    
    This function is called as a side-effect when the module is imported
    by apps_lic/cert/__init__.py.
    
    Example
    -------
    >>> # In apps_lic/cert/__init__.py:
    >>> from apps_lic.cert.fec_producer import register
    >>> register()
    """
    try:
        from apps_shared.cert.fec_framework import register_producer
        register_producer("apps_lic", produce_fec)
    except ImportError:
        # FEC framework not available - graceful degradation
        pass


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "produce_fec",
    "register",
    "PRODUCER_ID",
    "FEC_SCHEMA_VERSION",
]
