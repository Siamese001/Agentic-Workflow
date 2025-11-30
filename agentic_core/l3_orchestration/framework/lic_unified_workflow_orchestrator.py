"""Unified workflow orchestrator for RAG and KG operations."""
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

@dataclass
class RAGConfig:
    """Configuration for RAG operations."""
    retrieval_strategy: str = "semantic_search"
    max_documents: int = 10
    similarity_threshold: float = 0.7
    embedding_model: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KGConfig:
    """Configuration for Knowledge Graph operations."""
    traversal_depth: int = 3
    relationship_types: List[str] = field(default_factory=lambda: ["related_to", "part_of", "works_for"])
    entity_types: List[str] = field(default_factory=lambda: ["person", "company", "skill"])
    reasoning_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UnifiedWorkflowConfig:
    """Configuration for unified RAG+KG workflow."""
    rag: RAGConfig = field(default_factory=RAGConfig)
    kg: KGConfig = field(default_factory=KGConfig)
    integration_strategy: str = "rag_first_kg_enrichment"
    fusion_method: str = "concatenation"
    max_concurrent_operations: int = 5
    timeout_seconds: int = 120
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGResult:
    """Result from RAG operations."""
    query: str = ""
    retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    relevance_scores: List[float] = field(default_factory=list)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class KGResult:
    """Result from Knowledge Graph operations."""
    query: str = ""
    retrieved_entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_paths: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class UnifiedWorkflowResult:
    """Result from unified RAG+KG workflow."""
    query: str = ""
    rag_result: RAGResult = field(default_factory=RAGResult)
    kg_result: KGResult = field(default_factory=KGResult)
    fused_output: Dict[str, Any] = field(default_factory=dict)
    integration_strategy: str = ""
    total_processing_time: float = 0.0
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class UnifiedWorkflowOrchestrator:
    """Unified orchestrator for RAG and Knowledge Graph operations."""
    
    def __init__(self, config: Optional[UnifiedWorkflowConfig] = None):
        """Initialize orchestrator with unified configuration."""
        self.config = config or UnifiedWorkflowConfig()
        self.rag_config = self.config.rag
        self.kg_config = self.config.kg
        self.operation_history = []
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)
    
    async def execute_unified_workflow(self, 
                                      query: str,
                                      context: Dict[str, Any] = None) -> UnifiedWorkflowResult:
        """Execute unified RAG+KG workflow."""
        start_time = datetime.now()
        
        try:
            # Execute based on integration strategy
            if self.config.integration_strategy == "rag_first_kg_enrichment":
                result = await self._execute_rag_first_kg_enrichment(query, context)
            elif self.config.integration_strategy == "kg_first_rag_enrichment":
                result = await self._execute_kg_first_rag_enrichment(query, context)
            elif self.config.integration_strategy == "parallel_execution":
                result = await self._execute_parallel(query, context)
            else:
                result = await self._execute_rag_first_kg_enrichment(query, context)
            
            total_processing_time = (datetime.now() - start_time).total_seconds()
            result.total_processing_time = total_processing_time
            
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            total_processing_time = (datetime.now() - start_time).total_seconds()
            
            error_result = UnifiedWorkflowResult(
                query=query,
                integration_strategy=self.config.integration_strategy,
                total_processing_time=total_processing_time,
                success=False,
                error_message=str(e),
                metadata={"error_occurred": True}
            )
            
            self.operation_history.append(error_result)
            return error_result
    
    async def _execute_rag_first_kg_enrichment(self, 
                                              query: str, 
                                              context: Dict[str, Any] = None) -> UnifiedWorkflowResult:
        """Execute RAG first, then enrich with KG data."""
        async with self.semaphore:
            # Step 1: Execute RAG
            rag_result = await self._execute_rag(query, context)
            
            # Step 2: Extract entities from RAG results for KG lookup
            entities = self._extract_entities_from_rag(rag_result)
            
            # Step 3: Execute KG with extracted entities
            kg_result = await self._execute_kg_with_entities(entities, context)
            
            # Step 4: Fuse results
            fused_output = self._fuse_rag_kg_results(rag_result, kg_result)
            
            return UnifiedWorkflowResult(
                query=query,
                rag_result=rag_result,
                kg_result=kg_result,
                fused_output=fused_output,
                integration_strategy="rag_first_kg_enrichment",
                success=True,
                metadata={"rag_first": True}
            )
    
    async def _execute_kg_first_rag_enrichment(self, 
                                              query: str, 
                                              context: Dict[str, Any] = None) -> UnifiedWorkflowResult:
        """Execute KG first, then enrich with RAG data."""
        async with self.semaphore:
            # Step 1: Extract entities from query
            entities = self._extract_entities_from_query(query)
            
            # Step 2: Execute KG with extracted entities
            kg_result = await self._execute_kg_with_entities(entities, context)
            
            # Step 3: Use KG results to enhance RAG query
            enhanced_query = self._enhance_query_with_kg(query, kg_result)
            
            # Step 4: Execute RAG with enhanced query
            rag_result = await self._execute_rag(enhanced_query, context)
            
            # Step 5: Fuse results
            fused_output = self._fuse_rag_kg_results(rag_result, kg_result)
            
            return UnifiedWorkflowResult(
                query=query,
                rag_result=rag_result,
                kg_result=kg_result,
                fused_output=fused_output,
                integration_strategy="kg_first_rag_enrichment",
                success=True,
                metadata={"kg_first": True}
            )
    
    async def _execute_parallel(self, 
                               query: str, 
                               context: Dict[str, Any] = None) -> UnifiedWorkflowResult:
        """Execute RAG and KG in parallel."""
        async with self.semaphore:
            # Execute RAG and KG concurrently
            rag_task = self._execute_rag(query, context)
            entities = self._extract_entities_from_query(query)
            kg_task = self._execute_kg_with_entities(entities, context)
            
            rag_result, kg_result = await asyncio.gather(rag_task, kg_task)
            
            # Fuse results
            fused_output = self._fuse_rag_kg_results(rag_result, kg_result)
            
            return UnifiedWorkflowResult(
                query=query,
                rag_result=rag_result,
                kg_result=kg_result,
                fused_output=fused_output,
                integration_strategy="parallel_execution",
                success=True,
                metadata={"parallel": True}
            )
    
    async def _execute_rag(self, query: str, context: Dict[str, Any] = None) -> RAGResult:
        """Execute RAG operation."""
        # Mock RAG implementation
        await asyncio.sleep(0.1)
        
        mock_documents = [
            {"content": f"Document about {query}", "source": "knowledge_base", "id": "doc_1"},
            {"content": f"Related information for {query}", "source": "database", "id": "doc_2"},
            {"content": f"Additional context on {query}", "source": "web", "id": "doc_3"}
        ]
        
        # Limit by max_documents
        limited_docs = mock_documents[:self.rag_config.max_documents]
        relevance_scores = [0.9, 0.8, 0.7][:len(limited_docs)]
        
        return RAGResult(
            query=query,
            retrieved_documents=limited_docs,
            relevance_scores=relevance_scores,
            processing_time=0.1,
            metadata={
                "strategy": self.rag_config.retrieval_strategy,
                "model": self.rag_config.embedding_model
            }
        )
    
    async def _execute_kg_with_entities(self, 
                                        entities: List[str], 
                                        context: Dict[str, Any] = None) -> KGResult:
        """Execute KG operation with entities."""
        # Mock KG implementation
        await asyncio.sleep(0.15)
        
        mock_entities = [
            {"name": entity, "type": "person", "properties": {"confidence": 0.8}}
            for entity in entities[:3]
        ]
        
        mock_relationships = [
            {"source": entities[0] if entities else "unknown", "target": "related_entity", "type": "related_to"},
            {"source": entities[1] if len(entities) > 1 else "unknown", "target": "company", "type": "works_for"}
        ]
        
        reasoning_paths = []
        if self.kg_config.reasoning_enabled:
            reasoning_paths = [
                {"path": [entities[0], "related_to", "target"], "confidence": 0.7}
                for entity in entities[:2]
            ]
        
        return KGResult(
            query=",".join(entities),
            retrieved_entities=mock_entities,
            relationships=mock_relationships,
            reasoning_paths=reasoning_paths,
            processing_time=0.15,
            metadata={
                "traversal_depth": self.kg_config.traversal_depth,
                "reasoning_enabled": self.kg_config.reasoning_enabled
            }
        )
    
    def _extract_entities_from_rag(self, rag_result: RAGResult) -> List[str]:
        """Extract entities from RAG results."""
        entities = []
        for doc in rag_result.retrieved_documents:
            # Simple mock entity extraction
            if "person" in doc.get("content", "").lower():
                entities.append("person_entity")
            if "company" in doc.get("content", "").lower():
                entities.append("company_entity")
        return entities[:3]  # Limit entities
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Extract entities from query."""
        # Simple mock entity extraction
        entities = []
        if any(word in query.lower() for word in ["engineer", "developer", "manager"]):
            entities.append("person")
        if any(word in query.lower() for word in ["company", "corporation", "organization"]):
            entities.append("company")
        if any(word in query.lower() for word in ["skill", "technology", "framework"]):
            entities.append("skill")
        return entities[:3]
    
    def _enhance_query_with_kg(self, query: str, kg_result: KGResult) -> str:
        """Enhance query with KG results."""
        # Simple query enhancement
        entity_names = [entity.get("name", "") for entity in kg_result.retrieved_entities]
        enhanced_context = " ".join(entity_names)
        return f"{query} {enhanced_context}"
    
    def _fuse_rag_kg_results(self, rag_result: RAGResult, kg_result: KGResult) -> Dict[str, Any]:
        """Fuse RAG and KG results."""
        if self.config.fusion_method == "concatenation":
            return {
                "documents": rag_result.retrieved_documents,
                "entities": kg_result.retrieved_entities,
                "relationships": kg_result.relationships,
                "reasoning_paths": kg_result.reasoning_paths,
                "fusion_method": "concatenation"
            }
        else:
            # Default fusion
            return {
                "rag_data": rag_result.retrieved_documents,
                "kg_data": {
                    "entities": kg_result.retrieved_entities,
                    "relationships": kg_result.relationships
                },
                "fusion_method": "default"
            }
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        if not self.operation_history:
            return {"total_workflows": 0, "message": "No workflow history available"}
        
        successful_workflows = [w for w in self.operation_history if w.success]
        failed_workflows = [w for w in self.operation_history if not w.success]
        
        avg_processing_time = sum(w.total_processing_time for w in self.operation_history) / len(self.operation_history)
        
        strategy_usage = {}
        for workflow in self.operation_history:
            strategy = workflow.integration_strategy
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
        
        return {
            "total_workflows": len(self.operation_history),
            "successful_workflows": len(successful_workflows),
            "failed_workflows": len(failed_workflows),
            "success_rate": len(successful_workflows) / len(self.operation_history),
            "average_processing_time": avg_processing_time,
            "strategy_usage": strategy_usage,
            "config": {
                "integration_strategy": self.config.integration_strategy,
                "fusion_method": self.config.fusion_method,
                "max_concurrent_operations": self.config.max_concurrent_operations
            }
        }
