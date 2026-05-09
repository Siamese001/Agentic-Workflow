"""
DS-6: OTEL Span Chain Extensions
Additional span types for C0 RAG, Prompt Assembly, L2 Execution, and UWG State.

These spans extend the core L7RuntimeAuditTrace with granular observability
for deferred scope items from W7.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class SpanOutcome(Enum):
    """Outcome classification for extended spans."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CACHED = "cached"
    BYPASSED = "bypassed"


@dataclass(frozen=True)
class C0GroundingSpan:
    """
    C0 RAG grounding span.
    Captures retrieval attempt and result.
    """
    span_name: str = "c0.grounding.attempt"
    stage_owner: str = "agentic_core.L0_routing.c0_retrieval"
    
    # Grounding parameters
    query_digest: str = ""  # sha256 of the query text
    grounding_source: str = ""  # e.g., "vector_db", "search_api", "cache"
    top_k_requested: int = 5
    
    # Outcome
    outcome: str = ""  # SpanOutcome value
    documents_retrieved: int = 0
    documents_relevant: int = 0
    context_window_tokens: int = 0
    
    # Timing (ms)
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_name": self.span_name,
            "stage_owner": self.stage_owner,
            "query_digest": self.query_digest,
            "grounding_source": self.grounding_source,
            "top_k_requested": self.top_k_requested,
            "outcome": self.outcome,
            "documents_retrieved": self.documents_retrieved,
            "documents_relevant": self.documents_relevant,
            "context_window_tokens": self.context_window_tokens,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class PATemplateSpan:
    """
    Prompt Assembly template resolution span.
    Captures template selection and slot filling.
    """
    span_name: str = "pa.template.resolve"
    stage_owner: str = "agentic_core.L2_execution.prompt_assembly"
    
    # Template resolution
    template_family: str = ""  # e.g., "resume_generation", "company_brief"
    template_variant: str = ""  # e.g., "executive", "technical", "standard"
    template_digest: str = ""  # sha256 of resolved template
    
    # Slot filling
    slots_requested: int = 0
    slots_filled: int = 0
    slots_missing: List[str] = field(default_factory=list)
    
    # Outcome
    outcome: str = ""
    pa_boundary_hits: int = 0  # Number of PA boundary rule applications
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_name": self.span_name,
            "stage_owner": self.stage_owner,
            "template_family": self.template_family,
            "template_variant": self.template_variant,
            "template_digest": self.template_digest,
            "slots_requested": self.slots_requested,
            "slots_filled": self.slots_filled,
            "slots_missing": self.slots_missing,
            "outcome": self.outcome,
            "pa_boundary_hits": self.pa_boundary_hits,
        }


@dataclass(frozen=True)
class L2ExecutionSpan:
    """
    L2 Execution span.
    Captures execution attempt and result.
    """
    span_name: str = "l2.execution.attempt"
    stage_owner: str = "agentic_core.L2_execution"
    
    # Execution parameters
    execution_form: str = ""  # SINGLE_STEP, TERMINAL_SHORTCIRCUIT, MANAGED_WORKFLOW
    l2_contract_digest: str = ""  # SealedL2Artifact digest
    
    # Provider call (if applicable)
    provider_called: Optional[str] = None
    model_requested: Optional[str] = None
    
    # Outcome
    outcome: str = ""
    retry_count: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    
    # Timing (ms)
    latency_ms: float = 0.0
    time_to_first_token_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_name": self.span_name,
            "stage_owner": self.stage_owner,
            "execution_form": self.execution_form,
            "l2_contract_digest": self.l2_contract_digest,
            "provider_called": self.provider_called,
            "model_requested": self.model_requested,
            "outcome": self.outcome,
            "retry_count": self.retry_count,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "latency_ms": self.latency_ms,
            "time_to_first_token_ms": self.time_to_first_token_ms,
        }


@dataclass(frozen=True)
class UWGStateSpan:
    """
    UWG State Write/Read span.
    Captures durable state operations.
    """
    span_name: str = "uwg.state.write"
    stage_owner: str = "agentic_core.L4_state.uwg"
    
    # Operation
    operation: str = "write"  # write, read, update
    key_space: str = ""  # e.g., "request_context", "evaluation_results"
    key_digest: str = ""  # sha256 of key (privacy)
    
    # Data characteristics
    value_size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    
    # Outcome
    outcome: str = ""
    previous_value_existed: bool = False
    
    # Timing (ms)
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_name": self.span_name,
            "stage_owner": self.stage_owner,
            "operation": self.operation,
            "key_space": self.key_space,
            "key_digest": self.key_digest,
            "value_size_bytes": self.value_size_bytes,
            "ttl_seconds": self.ttl_seconds,
            "outcome": self.outcome,
            "previous_value_existed": self.previous_value_existed,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class ExtendedL7AuditTrace:
    """
    Extended L7 audit trace with DS-6 spans.
    This is the container for all extended spans.
    """
    # Core trace reference (from parent plan)
    base_trace_digest: str = ""  # Digest of the base L7RuntimeAuditTrace
    
    # Extended spans (DS-6)
    c0_grounding_spans: List[C0GroundingSpan] = field(default_factory=list)
    pa_template_spans: List[PATemplateSpan] = field(default_factory=list)
    l2_execution_spans: List[L2ExecutionSpan] = field(default_factory=list)
    uwg_state_spans: List[UWGStateSpan] = field(default_factory=list)
    
    # Aggregate metrics
    total_c0_documents_retrieved: int = 0
    total_pa_slots_filled: int = 0
    total_l2_tokens_consumed: int = 0
    total_uwg_bytes_written: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_trace_digest": self.base_trace_digest,
            "c0_grounding_spans": [s.to_dict() for s in self.c0_grounding_spans],
            "pa_template_spans": [s.to_dict() for s in self.pa_template_spans],
            "l2_execution_spans": [s.to_dict() for s in self.l2_execution_spans],
            "uwg_state_spans": [s.to_dict() for s in self.uwg_state_spans],
            "total_c0_documents_retrieved": self.total_c0_documents_retrieved,
            "total_pa_slots_filled": self.total_pa_slots_filled,
            "total_l2_tokens_consumed": self.total_l2_tokens_consumed,
            "total_uwg_bytes_written": self.total_uwg_bytes_written,
        }
