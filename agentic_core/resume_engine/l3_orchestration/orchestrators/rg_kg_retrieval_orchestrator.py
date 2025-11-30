"""KG Retrieval Orchestrator for L3 orchestration layer."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class KGOrchestrationConfig:
    """Configuration for KG retrieval orchestration."""
    max_concurrent_retrievals: int = 5
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    retrieval_timeout_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

class ResumeKGOrchestrator:
    """Orchestrates knowledge graph retrieval for resume processing."""
    
    def __init__(self, config: Optional[KGOrchestrationConfig] = None):
        self.config = config or KGOrchestrationConfig()
        self._cache = {}
    
    def orchestrate_retrieval(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Orchestrate KG retrieval based on query and context."""
        # Mock implementation
        return [
            {
                "id": f"kg_node_{i}",
                "type": "experience",
                "data": f"Experience data {i}",
                "relevance_score": 0.9 - (i * 0.1)
            }
            for i in range(3)
        ]
    
    def get_config(self) -> KGOrchestrationConfig:
        """Get current orchestration config."""
        return self.config
    cache_ttl_seconds: int = 300
    confidence_threshold: float = 0.7
    enable_hybrid_context: bool = True
    timeout_seconds: int = 120
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HybridContext:
    """Hybrid context combining KG and other data sources."""
    context_id: str = ""
    kg_entities: List[Dict[str, Any]] = field(default_factory=list)
    kg_relationships: List[Dict[str, Any]] = field(default_factory=list)
    rag_documents: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_paths: List[Dict[str, Any]] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    fusion_strategy: str = "concatenation"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.context_id:
            self.context_id = f"hybrid_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

@dataclass
class KGOrchestrationResult:
    """Result from KG retrieval orchestration."""
    query: str = ""
    hybrid_context: HybridContext = field(default_factory=HybridContext)
    orchestration_time: float = 0.0
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class KGFirstRetrievalOrchestrator:
    """KG-First Retrieval Orchestrator for knowledge graph operations."""

    def __init__(self, config: Optional[KGOrchestrationConfig] = None):
        """Initialize KG-first retrieval orchestrator with configuration."""
        self.config = config or KGOrchestrationConfig()
        self.orchestration_history = []
        self.context_cache = {}
        self.stats = {
            "total_orchestrations": 0,
            "successful_orchestrations": 0,
            "cache_hits": 0,
            "average_orchestration_time": 0.0,
            "contexts_created": 0
        }

    def orchestrate_kg_first_retrieval(self, query: str, context: Dict[str, Any] = None) -> KGOrchestrationResult:
        """Orchestrate KG-first retrieval with hybrid context generation."""
        start_time = datetime.now()

        try:
            # Check cache first
            cache_key = f"{query}_{str(context or {})}"
            if self.config.enable_caching and cache_key in self.context_cache:
                cached_context = self.context_cache[cache_key]
                self.stats["cache_hits"] += 1

                orchestration_time = (datetime.now() - start_time).total_seconds()

                result = KGOrchestrationResult(
                    query=query,
                    hybrid_context=cached_context,
                    orchestration_time=orchestration_time,
                    success=True,
                    metadata={"cache_hit": True}
                )

                self.orchestration_history.append(result)
                return result

            # Execute KG-first retrieval
            kg_entities = self._retrieve_kg_entities(query, context)
            kg_relationships = self._retrieve_kg_relationships(query, context)
            reasoning_paths = self._generate_reasoning_paths(query, context)

            # Create hybrid context if enabled
            hybrid_context = None
            if self.config.enable_hybrid_context:
                rag_documents = self._retrieve_rag_documents(query, context)
                hybrid_context = create_hybrid_context(
                    kg_entities=kg_entities,
                    kg_relationships=kg_relationships,
                    rag_documents=rag_documents,
                    reasoning_paths=reasoning_paths,
                    fusion_strategy="concatenation"
                )

                # Cache the context
                if self.config.enable_caching:
                    self.context_cache[cache_key] = hybrid_context

            orchestration_time = (datetime.now() - start_time).total_seconds()

            result = KGOrchestrationResult(
                query=query,
                hybrid_context=hybrid_context or HybridContext(),
                orchestration_time=orchestration_time,
                success=True,
                metadata={
                    "kg_first": True,
                    "hybrid_context_enabled": self.config.enable_hybrid_context,
                    "entities_found": len(kg_entities),
                    "relationships_found": len(kg_relationships)
                }
            )

            self._update_stats(result)
            self.orchestration_history.append(result)

            return result

        except Exception as e:
            orchestration_time = (datetime.now() - start_time).total_seconds()

            error_result = KGOrchestrationResult(
                query=query,
                orchestration_time=orchestration_time,
                success=False,
                error_message=str(e),
                metadata={"error_occurred": True}
            )

            self.orchestration_history.append(error_result)
            return error_result

    def _retrieve_kg_entities(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock KG entity retrieval."""
        # Simple mock implementation
        mock_entities = [
            {
                "id": "kg_entity_1",
                "name": query,
                "type": "person",
                "confidence": 0.9,
                "properties": {"source": "kg_retrieval"}
            },
            {
                "id": "kg_entity_2",
                "name": f"related_{query}",
                "type": "organization",
                "confidence": 0.8,
                "properties": {"source": "kg_retrieval"}
            }
        ]

        # Filter by confidence threshold
        return [e for e in mock_entities if e["confidence"] >= self.config.confidence_threshold]

    def _retrieve_kg_relationships(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock KG relationship retrieval."""
        # Simple mock implementation
        mock_relationships = [
            {
                "source": query,
                "target": "related_entity",
                "type": "related_to",
                "confidence": 0.85,
                "properties": {"weight": 0.7}
            },
            {
                "source": query,
                "target": "parent_org",
                "type": "part_of",
                "confidence": 0.75,
                "properties": {"weight": 0.6}
            }
        ]

        # Filter by confidence threshold
        return [r for r in mock_relationships if r["confidence"] >= self.config.confidence_threshold]

    def _generate_reasoning_paths(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock reasoning path generation."""
        # Simple mock implementation
        mock_paths = [
            {
                "path": [query, "related_to", "target"],
                "confidence": 0.8,
                "reasoning": "Direct KG relationship"
            },
            {
                "path": [query, "part_of", "org", "employs", "person"],
                "confidence": 0.6,
                "reasoning": "Multi-hop KG inference"
            }
        ]

        return mock_paths

    def _retrieve_rag_documents(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock RAG document retrieval for hybrid context."""
        # Simple mock implementation
        mock_documents = [
            {
                "content": f"Document about {query}",
                "source": "rag_retrieval",
                "relevance_score": 0.9
            },
            {
                "content": f"Additional information on {query}",
                "source": "rag_retrieval",
                "relevance_score": 0.8
            }
        ]

        return mock_documents

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update orchestrator configuration."""
        if "max_concurrent_retrievals" in new_config:
            self.config.max_concurrent_retrievals = new_config["max_concurrent_retrievals"]
        if "enable_caching" in new_config:
            self.config.enable_caching = new_config["enable_caching"]
        if "cache_ttl_seconds" in new_config:
            self.config.cache_ttl_seconds = new_config["cache_ttl_seconds"]
        if "confidence_threshold" in new_config:
            self.config.confidence_threshold = new_config["confidence_threshold"]
        if "enable_hybrid_context" in new_config:
            self.config.enable_hybrid_context = new_config["enable_hybrid_context"]
        if "timeout_seconds" in new_config:
            self.config.timeout_seconds = new_config["timeout_seconds"]

    def clear_cache(self) -> None:
        """Clear the context cache."""
        self.context_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self.stats,
            "config": {
                "max_concurrent_retrievals": self.config.max_concurrent_retrievals,
                "enable_caching": self.config.enable_caching,
                "cache_ttl_seconds": self.config.cache_ttl_seconds,
                "confidence_threshold": self.config.confidence_threshold,
                "enable_hybrid_context": self.config.enable_hybrid_context
            },
            "cache_size": len(self.context_cache),
            "orchestration_count": len(self.orchestration_history)
        }

    def _update_stats(self, result: KGOrchestrationResult) -> None:
        """Update orchestration statistics."""
        self.stats["total_orchestrations"] += 1

        if result.success:
            self.stats["successful_orchestrations"] += 1
            if result.hybrid_context:
                self.stats["contexts_created"] += 1

        # Update average orchestration time
        total_time = self.stats["average_orchestration_time"] * (self.stats["total_orchestrations"] - 1) + result.orchestration_time
        self.stats["average_orchestration_time"] = total_time / self.stats["total_orchestrations"]

def create_hybrid_context(kg_entities: List[Dict[str, Any]] = None,
                         kg_relationships: List[Dict[str, Any]] = None,
                         rag_documents: List[Dict[str, Any]] = None,
                         reasoning_paths: List[Dict[str, Any]] = None,
                         fusion_strategy: str = "concatenation",
                         query: str = "", user_id: str = "") -> HybridContext:
    """Factory function to create a hybrid context."""
    return HybridContext(
        kg_entities=kg_entities or [],
        kg_relationships=kg_relationships or [],
        rag_documents=rag_documents or [],
        reasoning_paths=reasoning_paths or [],
        fusion_strategy=fusion_strategy,
        confidence_scores=[item.get("confidence", 0.8) for item in (kg_entities or [])],
        metadata={"query": query, "user_id": user_id}
    )
