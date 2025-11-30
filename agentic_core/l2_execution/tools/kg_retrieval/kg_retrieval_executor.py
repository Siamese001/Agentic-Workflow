"""KG Retrieval Executor for L2 execution layer."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

# Import KGQueryPlan from L1 module
from agentic_core.l1_planning.planners.lic_kg_retrieval_planning import KGQueryPlan

@dataclass
class KGRetrievalConfig:
    """Configuration for KG retrieval operations."""
    max_depth: int = 3
    max_entities: int = 50
    confidence_threshold: float = 0.7
    enable_reasoning: bool = True
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KGRetrievalResult:
    """Result from KG retrieval operations."""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_paths: List[Dict[str, Any]] = field(default_factory=list)
    query_time: float = 0.0
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class KGRetrievalExecutor:
    """KG Retrieval Executor for knowledge graph operations."""
    
    def __init__(self, config: Optional[KGRetrievalConfig] = None):
        """Initialize KG retrieval executor with configuration."""
        self.config = config or KGRetrievalConfig()
        self.execution_history = []
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "average_query_time": 0.0,
            "entities_retrieved": 0,
            "relationships_found": 0
        }
    
    def execute_retrieval(self, query: str, context: Dict[str, Any] = None) -> KGRetrievalResult:
        """Execute KG retrieval query."""
        start_time = datetime.now()
        
        try:
            # Mock KG retrieval implementation
            entities = self._retrieve_entities(query, context)
            relationships = self._retrieve_relationships(query, context)
            reasoning_paths = self._generate_reasoning_paths(query, context) if self.config.enable_reasoning else []
            
            query_time = (datetime.now() - start_time).total_seconds()
            
            result = KGRetrievalResult(
                entities=entities,
                relationships=relationships,
                reasoning_paths=reasoning_paths,
                query_time=query_time,
                success=True,
                metadata={
                    "query": query,
                    "max_depth": self.config.max_depth,
                    "reasoning_enabled": self.config.enable_reasoning
                }
            )
            
            self._update_stats(result)
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            query_time = (datetime.now() - start_time).total_seconds()
            
            error_result = KGRetrievalResult(
                query_time=query_time,
                success=False,
                error_message=str(e),
                metadata={"error_occurred": True}
            )
            
            self.execution_history.append(error_result)
            return error_result
    
    def execute(self, plan: KGQueryPlan) -> KGRetrievalResult:
        """Execute a KG query plan."""
        return self.execute_retrieval(
            query=plan.primary_entity,
            context=plan.constraints
        )
    
    def _retrieve_entities(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock entity retrieval from KG."""
        # Simple mock implementation
        mock_entities = [
            {
                "id": "entity_1",
                "name": query,
                "type": "person",
                "confidence": 0.9,
                "properties": {"source": "knowledge_graph"}
            },
            {
                "id": "entity_2", 
                "name": f"related_to_{query}",
                "type": "organization",
                "confidence": 0.8,
                "properties": {"source": "knowledge_graph"}
            }
        ]
        
        # Limit by max_entities
        return mock_entities[:self.config.max_entities]
    
    def _retrieve_relationships(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock relationship retrieval from KG."""
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
                "target": "parent_organization", 
                "type": "part_of",
                "confidence": 0.75,
                "properties": {"weight": 0.6}
            }
        ]
        
        return mock_relationships
    
    def _generate_reasoning_paths(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock reasoning path generation."""
        # Simple mock implementation
        mock_paths = [
            {
                "path": [query, "related_to", "target_entity"],
                "confidence": 0.8,
                "reasoning": "Direct relationship found"
            },
            {
                "path": [query, "part_of", "organization", "employs", "person"],
                "confidence": 0.6,
                "reasoning": "Multi-hop relationship inferred"
            }
        ]
        
        return mock_paths
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update executor configuration."""
        if "max_depth" in new_config:
            self.config.max_depth = new_config["max_depth"]
        if "max_entities" in new_config:
            self.config.max_entities = new_config["max_entities"]
        if "confidence_threshold" in new_config:
            self.config.confidence_threshold = new_config["confidence_threshold"]
        if "enable_reasoning" in new_config:
            self.config.enable_reasoning = new_config["enable_reasoning"]
        if "timeout_seconds" in new_config:
            self.config.timeout_seconds = new_config["timeout_seconds"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics."""
        return {
            **self.stats,
            "config": {
                "max_depth": self.config.max_depth,
                "max_entities": self.config.max_entities,
                "confidence_threshold": self.config.confidence_threshold,
                "enable_reasoning": self.config.enable_reasoning
            },
            "execution_count": len(self.execution_history)
        }
    
    def _update_stats(self, result: KGRetrievalResult) -> None:
        """Update execution statistics."""
        self.stats["total_queries"] += 1
        
        if result.success:
            self.stats["successful_queries"] += 1
            self.stats["entities_retrieved"] += len(result.entities)
            self.stats["relationships_found"] += len(result.relationships)
        
        # Update average query time
        total_time = self.stats["average_query_time"] * (self.stats["total_queries"] - 1) + result.query_time
        self.stats["average_query_time"] = total_time / self.stats["total_queries"]
