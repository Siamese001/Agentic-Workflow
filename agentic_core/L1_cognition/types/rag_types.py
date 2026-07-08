"""RAG Pipeline Types.

Defines the data structures for Retrieval-Augmented Generation pipeline
including context assembly, prompt templates, and generation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("rag_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rag_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rag_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rag_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rag_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rag_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rag_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rag_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rag_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rag_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rag_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rag_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rag_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rag_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rag_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rag_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rag_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rag_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rag_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("rag_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rag_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rag_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rag_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rag_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rag_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rag_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rag_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rag_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rag_types", "context_pull")
trace_contract._emit_pulls_context("p1", "rag_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rag_types", "write_through")
trace_contract._emit_writes_through("p1", "rag_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rag_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rag_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rag_types", "routing_commit")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_dispatch_entry")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_dispatch_exit")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_tool_invoke")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_tool_complete")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_agent_entry")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_agent_exit")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_uwg_write")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_trace_sign")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_guardrail_check")
trace_contract.emit_determinism_digest("trace_rag_types", "rag_types_policy_verify")


@dataclass
class RAGQuery:
    """Represents a RAG pipeline query with context requirements."""

    query_text: str
    query_type: str = "qa"  # "qa", "summarization", "explanation", "analysis"

    # Context requirements
    max_context_length: int = 4000  # Maximum context tokens
    min_context_items: int = 3
    max_context_items: int = 10

    # Search strategy
    search_mode: str = "fusion"  # "local", "global", "drift", "fusion"
    search_filters: dict[str, Any] = field(default_factory=dict)

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    top_k: int = 40

    # Context assembly
    include_sources: bool = True
    include_relationships: bool = True
    include_communities: bool = True
    context_format: str = "structured"  # "structured", "narrative", "bullet"

    # Metadata
    query_id: str = field(default_factory=lambda: f"rag_query_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize query text."""
        self.query_text = self.query_text.strip()
        if not self.query_text:
            raise ValueError("Query text cannot be empty")


@dataclass
class ContextItem:
    """Represents a single context item for RAG."""

    item_id: str
    content: str
    item_type: str  # "entity", "relationship", "community", "document"
    title: str
    relevance_score: float

    # Source information
    source_file: str | None = None
    line_number: int | None = None
    confidence: float = 1.0

    # Context metadata
    context_type: str = "primary"  # "primary", "supporting", "background"
    hierarchy_level: int | None = None
    surrounding_context: str | None = None

    # Formatting
    formatted_content: str | None = None

    def format_for_context(self, format_type: str = "structured") -> str:
        """Format the context item for inclusion in prompt."""
        if self.formatted_content and format_type == self.context_format:
            return self.formatted_content

        if format_type == "structured":
            parts = [
                f"Type: {self.item_type}",
                f"Title: {self.title}",
                f"Content: {self.content}",
                f"Relevance: {self.relevance_score:.2f}",
            ]
            if self.source_file:
                parts.append(f"Source: {self.source_file}")
            return "\n".join(parts)

        elif format_type == "narrative":
            return f"{self.title}: {self.content}"

        elif format_type == "bullet":
            return f"• {self.title}: {self.content}"

        else:
            return self.content


@dataclass
class RAGContext:
    """Represents the assembled context for RAG generation."""

    query: RAGQuery
    items: list[ContextItem]

    # Context statistics
    total_items: int
    total_length: int  # Character count
    token_estimate: int

    # Quality metrics
    avg_relevance_score: float
    max_relevance_score: float
    min_relevance_score: float

    # Diversity metrics
    item_type_distribution: dict[str, int]
    source_distribution: dict[str, int]

    # Assembly metadata
    assembly_time_ms: float
    assembly_method: str
    truncation_applied: bool = False
    warnings: list[str] = field(default_factory=list)

    def get_formatted_context(self, format_type: str | None = None) -> str:
        """Get the formatted context as a string."""
        fmt = format_type or self.query.context_format

        if fmt == "structured":
            sections = []
            for item in self.items:
                sections.append(item.format_for_context(fmt))
                sections.append("---")
            return "\n".join(sections)

        elif fmt == "narrative":
            parts = []
            for item in self.items:
                parts.append(item.format_for_context(fmt))
            return " ".join(parts)

        elif fmt == "bullet":
            bullets = []
            for item in self.items:
                bullets.append(item.format_for_context(fmt))
            return "\n".join(bullets)

        else:
            # Default: concatenate with newlines
            return "\n\n".join(item.content for item in self.items)

    def get_sources(self) -> list[str]:
        """Get unique sources from context items."""
        sources = set()
        for item in self.items:
            if item.source_file:
                sources.add(item.source_file)
        return sorted(list(sources))


@dataclass
class PromptTemplate:
    """Represents a prompt template for RAG generation."""

    template_id: str
    name: str
    description: str

    # Template content
    system_prompt: str
    user_prompt_template: str

    # Placeholders
    required_placeholders: list[str] = field(default_factory=list)
    optional_placeholders: list[str] = field(default_factory=list)

    # Template metadata
    template_type: str = "qa"  # "qa", "summarization", "explanation", "analysis"
    target_llm: str = "generic"
    version: str = "1.0"

    # Usage statistics
    usage_count: int = 0
    last_used: datetime | None = None
    avg_success_score: float = 0.0

    def render(
        self,
        context: RAGContext,
        query: RAGQuery,
        additional_data: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Render the template with context and query."""
        # Prepare placeholder values
        placeholders = {
            "context": context.get_formatted_context(),
            "query": query.query_text,
            "query_type": query.query_type,
            "sources": "\n".join(context.get_sources()),
            "item_count": str(context.total_items),
            "avg_relevance": f"{context.avg_relevance_score:.2f}",
        }

        # Add additional data
        if additional_data:
            placeholders.update(additional_data)

        # Check required placeholders
        missing = [p for p in self.required_placeholders if p not in placeholders]
        if missing:
            raise ValueError(f"Missing required placeholders: {missing}")

        # Render prompts
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt_template

        for placeholder, value in placeholders.items():
            system_prompt = system_prompt.replace(f"{{{placeholder}}}", str(value))
            user_prompt = user_prompt.replace(f"{{{placeholder}}}", str(value))

        return system_prompt, user_prompt


@dataclass
class GenerationRequest:
    """Represents a request to the LLM for generation."""

    request_id: str
    query: RAGQuery
    context: RAGContext
    template: PromptTemplate

    # Rendered prompts
    system_prompt: str
    user_prompt: str

    # Generation parameters
    temperature: float
    max_tokens: int
    top_p: float
    top_k: int

    # Request metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Represents the result from LLM generation."""

    request_id: str
    generated_text: str

    # Generation metadata
    model_used: str
    tokens_generated: int
    tokens_prompt: int
    tokens_total: int
    generation_time_ms: float

    # Quality metrics
    coherence_score: float
    relevance_score: float
    completeness_score: float

    # Source attribution
    source_citations: list[str] = field(default_factory=list)
    attribution_confidence: float = 0.0

    # Errors and warnings
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RAGResponse:
    """Represents a complete RAG pipeline response."""

    query: RAGQuery
    context: RAGContext
    template: PromptTemplate
    generation: GenerationResult

    # Pipeline statistics
    total_time_ms: float
    search_time_ms: float
    context_assembly_time_ms: float
    generation_time_ms: float

    # Quality metrics
    overall_quality_score: float
    context_quality_score: float
    generation_quality_score: float

    # Feedback
    user_rating: int | None = None  # 1-5
    user_feedback: str | None = None

    # Errors and warnings
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the RAG response."""
        return {
            "query": self.query.query_text,
            "response_length": len(self.generation.generated_text),
            "context_items": self.context.total_items,
            "sources": len(self.context.get_sources()),
            "total_time_ms": self.total_time_ms,
            "quality_scores": {
                "overall": self.overall_quality_score,
                "context": self.context_quality_score,
                "generation": self.generation_quality_score,
            },
            "has_errors": len(self.errors) > 0,
            "has_warnings": len(self.warnings) > 0,
        }


@dataclass
class RAGConfig:
    """Configuration for the RAG pipeline."""

    # Search configuration
    search_mode: str = "fusion"
    max_context_items: int = 10
    min_relevance_threshold: float = 0.3

    # Context assembly
    context_format: str = "structured"
    max_context_length: int = 4000
    include_sources: bool = True

    # Generation
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    default_top_p: float = 0.9

    # Templates
    default_template_id: str = "qa_default"
    template_cache_size: int = 100

    # Quality control
    min_coherence_score: float = 0.5
    min_relevance_score: float = 0.5
    enable_source_attribution: bool = True

    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_concurrent_requests: int = 5


@dataclass
class RAGMetrics:
    """Metrics for RAG pipeline performance."""

    # Performance metrics
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float

    # Quality metrics
    avg_quality_score: float
    avg_context_relevance: float
    avg_generation_coherence: float

    # Usage metrics
    total_requests: int
    successful_requests: int
    error_rate: float

    # Context metrics
    avg_context_items: float
    avg_context_length: float
    truncation_rate: float

    # Template usage
    template_usage: dict[str, int]

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Export all types
__all__ = [
    "RAGQuery",
    "ContextItem",
    "RAGContext",
    "PromptTemplate",
    "GenerationRequest",
    "GenerationResult",
    "RAGResponse",
    "RAGConfig",
    "RAGMetrics",
]
