"""RAG Request Understanding Load Planner - Plans loading for RAG request understanding.

This planner manages the loading phase for understanding RAG requests,
including query analysis, context extraction, and retrieval strategy planning.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Types of RAG requests."""
    QUERY = "query"
    SEMANTIC_SEARCH = "semantic_search"
    HYBRID_SEARCH = "hybrid_search"
    FILTERED_RETRIEVAL = "filtered_retrieval"
    CONTEXTUAL_QA = "contextual_qa"
    SUMMARIZATION = "summarization"


class RetrievalStrategy(Enum):
    """Retrieval strategies."""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"
    MULTI_STAGE = "multi_stage"
    RERANK = "rerank"
    ADAPTIVE = "adaptive"


class ProcessingLevel(Enum):
    """Processing levels for requests."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    DEEP = "deep"


@dataclass
class QueryInfo:
    """Information about the query."""
    text: str
    type: RequestType
    intent: str
    entities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextInfo:
    """Information about context requirements."""
    required_domains: List[str] = field(default_factory=list)
    excluded_domains: List[str] = field(default_factory=list)
    time_range: Optional[Dict[str, Any]] = None
    source_types: List[str] = field(default_factory=list)
    metadata_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalConfig:
    """Configuration for retrieval."""
    strategy: RetrievalStrategy
    top_k: int = 10
    similarity_threshold: float = 0.7
    rerank_top_k: Optional[int] = None
    include_metadata: bool = True
    enable_cache: bool = True
    cache_ttl: int = 300


@dataclass
class RAGLoadPlan:
    """Complete plan for RAG request loading."""
    id: str
    name: str
    query_info: QueryInfo
    context_info: ContextInfo
    retrieval_config: RetrievalConfig
    processing_level: ProcessingLevel = ProcessingLevel.STANDARD
    enable_reranking: bool = False
    enable_filtering: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGLoadConfig:
    """Configuration for RAG load planning."""
    enable_query_expansion: bool = True
    enable_intent_detection: bool = True
    enable_entity_extraction: bool = True
    max_query_length: int = 1000
    default_top_k: int = 10
    default_processing_level: str = "standard"
    log_level: str = "INFO"


@dataclass
class RAGLoadResult:
    """Result of RAG load planning."""
    success: bool
    load_plan: Optional[RAGLoadPlan] = None
    query_complexity: str = "medium"
    estimated_retrieval_time: int = 0
    memory_estimate: int = 0
    document_count_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGLoadPlanner:
    """Planner for RAG request loading operations."""

    def __init__(self, config: Optional[RAGLoadConfig] = None):
        self.config = config or RAGLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> RAGLoadResult:
        """Plan RAG request loading operations.
        
        Args:
            load_request: Dictionary containing RAG request requirements
            
        Returns:
            RAGLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting RAG load planning for: {load_request.get('plan_name', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(load_request)
            
            # Parse query info
            query_info = self._parse_query_info(load_request)
            
            # Parse context info
            context_info = self._parse_context_info(load_request)
            
            # Parse retrieval config
            retrieval_config = self._parse_retrieval_config(load_request)
            
            # Parse processing level
            processing_level = self._parse_processing_level(load_request)
            
            # Create load plan
            load_plan = self._create_load_plan(
                load_request, query_info, context_info,
                retrieval_config, processing_level
            )
            
            # Analyze query complexity
            query_complexity = self._analyze_query_complexity(query_info)
            
            # Estimate retrieval time
            retrieval_time = self._estimate_retrieval_time(load_plan)
            
            # Estimate memory usage
            memory_estimate = self._estimate_memory_usage(load_plan)
            
            # Estimate document count
            doc_count = self._estimate_document_count(load_plan)
            
            result = RAGLoadResult(
                success=True,
                load_plan=load_plan,
                query_complexity=query_complexity,
                estimated_retrieval_time=retrieval_time,
                memory_estimate=memory_estimate,
                document_count_estimate=doc_count,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "request_type": query_info.type.value,
                    "planner": "RAGLoadPlanner"
                }
            )
            
            self.logger.info(
                f"Successfully planned RAG load: "
                f"{query_complexity} complexity, {doc_count} documents estimated"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"RAG load planning failed: {str(e)}")
            return RAGLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "RAGLoadPlanner"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate RAG load planning request."""
        if not request:
            raise ValueError("RAG load planning request cannot be empty")
        
        if "plan_name" not in request:
            raise ValueError("Plan name is required in RAG load planning request")
        
        if "query" not in request:
            raise ValueError("Query is required in RAG load planning request")

    def _parse_query_info(self, request: Dict[str, Any]) -> QueryInfo:
        """Parse query information from request."""
        raw_query = request.get("query", {})
        
        # Parse request type
        type_mapping = {
            "query": RequestType.QUERY,
            "semantic_search": RequestType.SEMANTIC_SEARCH,
            "hybrid_search": RequestType.HYBRID_SEARCH,
            "filtered_retrieval": RequestType.FILTERED_RETRIEVAL,
            "contextual_qa": RequestType.CONTEXTUAL_QA,
            "summarization": RequestType.SUMMARIZATION
        }
        
        request_type = type_mapping.get(
            raw_query.get("type", "query"),
            RequestType.QUERY
        )
        
        # Validate query length
        query_text = raw_query.get("text", "")
        if len(query_text) > self.config.max_query_length:
            raise ValueError(
                f"Query length ({len(query_text)}) exceeds maximum "
                f"({self.config.max_query_length})"
            )
        
        return QueryInfo(
            text=query_text,
            type=request_type,
            intent=raw_query.get("intent", "search"),
            entities=raw_query.get("entities", []),
            keywords=raw_query.get("keywords", []),
            embeddings=raw_query.get("embeddings"),
            metadata=raw_query.get("metadata", {})
        )

    def _parse_context_info(self, request: Dict[str, Any]) -> ContextInfo:
        """Parse context information from request."""
        raw_context = request.get("context", {})
        
        return ContextInfo(
            required_domains=raw_context.get("required_domains", []),
            excluded_domains=raw_context.get("excluded_domains", []),
            time_range=raw_context.get("time_range"),
            source_types=raw_context.get("source_types", []),
            metadata_filters=raw_context.get("metadata_filters", {})
        )

    def _parse_retrieval_config(self, request: Dict[str, Any]) -> RetrievalConfig:
        """Parse retrieval configuration from request."""
        raw_config = request.get("retrieval", {})
        
        # Parse strategy
        strategy_mapping = {
            "vector_only": RetrievalStrategy.VECTOR_ONLY,
            "keyword_only": RetrievalStrategy.KEYWORD_ONLY,
            "hybrid": RetrievalStrategy.HYBRID,
            "multi_stage": RetrievalStrategy.MULTI_STAGE,
            "rerank": RetrievalStrategy.RERANK,
            "adaptive": RetrievalStrategy.ADAPTIVE
        }
        
        strategy = strategy_mapping.get(
            raw_config.get("strategy", "hybrid"),
            RetrievalStrategy.HYBRID
        )
        
        return RetrievalConfig(
            strategy=strategy,
            top_k=raw_config.get("top_k", self.config.default_top_k),
            similarity_threshold=raw_config.get("similarity_threshold", 0.7),
            rerank_top_k=raw_config.get("rerank_top_k"),
            include_metadata=raw_config.get("include_metadata", True),
            enable_cache=raw_config.get("enable_cache", True),
            cache_ttl=raw_config.get("cache_ttl", 300)
        )

    def _parse_processing_level(self, request: Dict[str, Any]) -> ProcessingLevel:
        """Parse processing level from request."""
        level_mapping = {
            "basic": ProcessingLevel.BASIC,
            "standard": ProcessingLevel.STANDARD,
            "enhanced": ProcessingLevel.ENHANCED,
            "deep": ProcessingLevel.DEEP
        }
        
        level_str = request.get("processing_level", self.config.default_processing_level)
        return level_mapping.get(level_str, ProcessingLevel.STANDARD)

    def _create_load_plan(
        self,
        request: Dict[str, Any],
        query_info: QueryInfo,
        context_info: ContextInfo,
        retrieval_config: RetrievalConfig,
        processing_level: ProcessingLevel
    ) -> RAGLoadPlan:
        """Create RAG load plan from parsed components."""
        return RAGLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            query_info=query_info,
            context_info=context_info,
            retrieval_config=retrieval_config,
            processing_level=processing_level,
            enable_reranking=request.get("enable_reranking", False),
            enable_filtering=request.get("enable_filtering", True),
            metadata=request.get("metadata", {})
        )

    def _analyze_query_complexity(self, query_info: QueryInfo) -> str:
        """Analyze query complexity."""
        complexity_score = 0
        
        # Length factor
        if len(query_info.text) > 500:
            complexity_score += 2
        elif len(query_info.text) > 200:
            complexity_score += 1
        
        # Entity factor
        complexity_score += min(len(query_info.entities), 3)
        
        # Keyword factor
        complexity_score += min(len(query_info.keywords), 2)
        
        # Type factor
        if query_info.type in [RequestType.HYBRID_SEARCH, RequestType.MULTI_STAGE]:
            complexity_score += 2
        elif query_info.type in [RequestType.SEMANTIC_SEARCH, RequestType.FILTERED_RETRIEVAL]:
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score <= 2:
            return "low"
        elif complexity_score <= 5:
            return "medium"
        else:
            return "high"

    def _estimate_retrieval_time(self, plan: RAGLoadPlan) -> int:
        """Estimate retrieval time in seconds."""
        base_time = 2  # Base setup time
        
        # Time per document retrieved
        retrieval_time = plan.retrieval_config.top_k * 0.05
        
        # Strategy multiplier
        strategy_multiplier = {
            RetrievalStrategy.VECTOR_ONLY: 1.0,
            RetrievalStrategy.KEYWORD_ONLY: 0.8,
            RetrievalStrategy.HYBRID: 1.5,
            RetrievalStrategy.MULTI_STAGE: 2.0,
            RetrievalStrategy.RERANK: 2.5,
            RetrievalStrategy.ADAPTIVE: 1.8
        }
        
        strategy_time = retrieval_time * strategy_multiplier.get(
            plan.retrieval_config.strategy, 1.0
        )
        
        # Processing level multiplier
        level_multiplier = {
            ProcessingLevel.BASIC: 0.5,
            ProcessingLevel.STANDARD: 1.0,
            ProcessingLevel.ENHANCED: 1.5,
            ProcessingLevel.DEEP: 2.0
        }
        
        total_time = (base_time + strategy_time) * level_multiplier.get(
            plan.processing_level, 1.0
        )
        
        if plan.enable_reranking:
            total_time += plan.retrieval_config.top_k * 0.1
        
        return int(total_time)

    def _estimate_memory_usage(self, plan: RAGLoadPlan) -> int:
        """Estimate memory usage in MB."""
        # Base memory usage
        base_memory = 50  # 50MB base for RAG operations
        
        # Memory for retrieved documents (assume average 5KB per document)
        doc_memory = plan.retrieval_config.top_k * 5 * 1024
        
        # Memory for embeddings (if present)
        embedding_memory = 0
        if plan.query_info.embeddings:
            embedding_memory = len(plan.query_info.embeddings) * 4  # 4 bytes per float
        
        # Processing level memory multiplier
        level_multiplier = {
            ProcessingLevel.BASIC: 0.5,
            ProcessingLevel.STANDARD: 1.0,
            ProcessingLevel.ENHANCED: 1.5,
            ProcessingLevel.DEEP: 2.0
        }
        
        total_memory_bytes = (
            base_memory * 1024 * 1024 + 
            doc_memory + embedding_memory
        ) * level_multiplier.get(plan.processing_level, 1.0)
        
        return total_memory_bytes // (1024 * 1024)  # Convert to MB

    def _estimate_document_count(self, plan: RAGLoadPlan) -> int:
        """Estimate number of documents to retrieve."""
        base_count = plan.retrieval_config.top_k
        
        # Adjust based on context requirements
        if plan.context_info.required_domains:
            base_count = min(base_count * 2, base_count + 20)
        
        # Adjust based on strategy
        if plan.retrieval_config.strategy == RetrievalStrategy.MULTI_STAGE:
            base_count = int(base_count * 1.5)
        elif plan.retrieval_config.strategy == RetrievalStrategy.RERANK:
            base_count = int(base_count * 1.3)
        
        return base_count


# Factory function for easy instantiation
def create_rag_load_planner(
    enable_query_expansion: bool = True,
    enable_intent_detection: bool = True,
    enable_entity_extraction: bool = True,
    **kwargs
) -> RAGLoadPlanner:
    """Create a configured RAG load planner."""
    config = RAGLoadConfig(
        enable_query_expansion=enable_query_expansion,
        enable_intent_detection=enable_intent_detection,
        enable_entity_extraction=enable_entity_extraction,
        **kwargs
    )
    return RAGLoadPlanner(config)


# Convenience function for direct usage
def plan_rag_load(
    plan_name: str,
    query_text: str,
    query_type: str = "query",
    intent: str = "search",
    entities: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    retrieval_strategy: str = "hybrid",
    top_k: int = 10,
    processing_level: str = "standard",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan RAG load from simple parameters.
    
    Args:
        plan_name: Name of the load plan
        query_text: The query text
        query_type: Type of RAG request
        intent: Query intent
        entities: Optional list of entities
        keywords: Optional list of keywords
        retrieval_strategy: Strategy for retrieval
        top_k: Number of documents to retrieve
        processing_level: Level of processing
        config: Optional planner configuration overrides
        
    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "query": {
            "text": query_text,
            "type": query_type,
            "intent": intent,
            "entities": entities or [],
            "keywords": keywords or []
        },
        "retrieval": {
            "strategy": retrieval_strategy,
            "top_k": top_k
        },
        "processing_level": processing_level
    }
    
    # Create planner and execute
    planner_config = RAGLoadConfig(**config) if config else None
    planner = RAGLoadPlanner(planner_config)
    result = planner.plan_load(request)
    
    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "query_info": {
                "text": result.load_plan.query_info.text,
                "type": result.load_plan.query_info.type.value,
                "intent": result.load_plan.query_info.intent,
                "entities": result.load_plan.query_info.entities,
                "keywords": result.load_plan.query_info.keywords,
                "metadata": result.load_plan.query_info.metadata
            },
            "context_info": {
                "required_domains": result.load_plan.context_info.required_domains,
                "excluded_domains": result.load_plan.context_info.excluded_domains,
                "time_range": result.load_plan.context_info.time_range,
                "source_types": result.load_plan.context_info.source_types,
                "metadata_filters": result.load_plan.context_info.metadata_filters
            },
            "retrieval_config": {
                "strategy": result.load_plan.retrieval_config.strategy.value,
                "top_k": result.load_plan.retrieval_config.top_k,
                "similarity_threshold": result.load_plan.retrieval_config.similarity_threshold,
                "rerank_top_k": result.load_plan.retrieval_config.rerank_top_k,
                "include_metadata": result.load_plan.retrieval_config.include_metadata,
                "enable_cache": result.load_plan.retrieval_config.enable_cache,
                "cache_ttl": result.load_plan.retrieval_config.cache_ttl
            },
            "processing_level": result.load_plan.processing_level.value,
            "enable_reranking": result.load_plan.enable_reranking,
            "enable_filtering": result.load_plan.enable_filtering,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "query_complexity": result.query_complexity,
        "estimated_retrieval_time": result.estimated_retrieval_time,
        "memory_estimate": result.memory_estimate,
        "document_count_estimate": result.document_count_estimate,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }
