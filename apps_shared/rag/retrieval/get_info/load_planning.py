"""RAG Retrieval Load Planner - Plans data loading operations for RAG retrieval systems.

This planner manages the loading phase for RAG retrieval operations,
including vector store loading, document chunking, and retrieval optimization.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RetrievalMode(Enum):
    """Types of retrieval modes."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    BM25 = "bm25"
    EXACT_MATCH = "exact_match"
    FUZZY = "fuzzy"


class VectorStoreType(Enum):
    """Types of vector stores."""
    CHROMA = "chroma"
    QDRANT = "qdrant"
    PINECONE = "pinecone"
    FAISS = "faiss"
    MILVUS = "milvus"


class DocumentFormat(Enum):
    """Supported document formats."""
    PDF = "pdf"
    TXT = "txt"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    DOCX = "docx"


class ChunkingStrategy(Enum):
    """Document chunking strategies."""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"
    SLIDING_WINDOW = "sliding_window"


@dataclass
class DocumentSource:
    """Definition of a document source for RAG."""
    id: str
    name: str
    location: str
    format: DocumentFormat
    size_bytes: int = 0
    encoding: str = "utf-8"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkingConfig:
    """Configuration for document chunking."""
    strategy: ChunkingStrategy
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    max_chunk_size: int = 2000
    separators: List[str] = field(default_factory=lambda: ["\n\n", "\n", ".", " "])


@dataclass
class EmbeddingConfig:
    """Configuration for text embedding."""
    model_name: str = "text-embedding-ada-002"
    dimension: int = 1536
    batch_size: int = 100
    normalize: bool = True
    cache_embeddings: bool = True


@dataclass
class RetrievalConfig:
    """Configuration for retrieval parameters."""
    mode: RetrievalMode
    top_k: int = 5
    similarity_threshold: float = 0.7
    include_metadata: bool = True
    rerank: bool = False
    rerank_model: Optional[str] = None


@dataclass
class RAGLoadPlan:
    """Complete plan for RAG data loading."""
    id: str
    name: str
    document_sources: List[DocumentSource]
    vector_store_type: VectorStoreType
    chunking_config: ChunkingConfig
    embedding_config: EmbeddingConfig
    retrieval_config: RetrievalConfig
    collection_name: str = "default"
    persist_directory: Optional[str] = None
    enable_preprocessing: bool = True
    enable_deduplication: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGLoadConfig:
    """Configuration for RAG load planning."""
    enable_chunking: bool = True
    enable_embedding: bool = True
    enable_indexing: bool = True
    max_documents_per_plan: int = 1000
    max_file_size_mb: int = 100
    default_chunk_size: int = 1000
    default_embedding_model: str = "text-embedding-ada-002"
    log_level: str = "INFO"


@dataclass
class RAGLoadResult:
    """Result of RAG load planning."""
    success: bool
    load_plan: Optional[RAGLoadPlan] = None
    estimated_chunks: int = 0
    embedding_count: int = 0
    storage_requirements: Dict[str, int] = field(default_factory=dict)
    processing_time_estimate: int = 0
    cost_estimate: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGLoadPlanner:
    """Planner for RAG data loading operations."""

    def __init__(self, config: Optional[RAGLoadConfig] = None):
        self.config = config or RAGLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> RAGLoadResult:
        """Plan RAG data loading operations.
        
        Args:
            load_request: Dictionary containing load requirements and documents
            
        Returns:
            RAGLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting RAG load planning for: {load_request.get('plan_name', 'unknown')}")
        
        try:
            # Validate input request
            self._validate_request(load_request)
            
            # Parse document sources
            sources = self._parse_document_sources(load_request)
            
            # Parse chunking config
            chunking_config = (
                self._parse_chunking_config(load_request) 
                if self.config.enable_chunking else None
            )
            
            # Parse embedding config
            embedding_config = (
                self._parse_embedding_config(load_request) 
                if self.config.enable_embedding else None
            )
            
            # Parse retrieval config
            retrieval_config = self._parse_retrieval_config(load_request)
            
            # Parse vector store type
            vector_store_type = self._parse_vector_store_type(load_request)
            
            # Create load plan
            load_plan = self._create_load_plan(
                load_request, sources, vector_store_type,
                chunking_config, embedding_config, retrieval_config
            )
            
            # Estimate chunks
            estimated_chunks = self._estimate_chunks(load_plan)
            
            # Calculate storage requirements
            storage_requirements = self._calculate_storage_requirements(load_plan)
            
            # Estimate processing time
            processing_time = self._estimate_processing_time(load_plan)
            
            # Estimate costs
            cost_estimate = self._estimate_costs(load_plan)
            
            result = RAGLoadResult(
                success=True,
                load_plan=load_plan,
                estimated_chunks=estimated_chunks,
                embedding_count=estimated_chunks if self.config.enable_embedding else 0,
                storage_requirements=storage_requirements,
                processing_time_estimate=processing_time,
                cost_estimate=cost_estimate,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "document_count": len(sources),
                    "planner": "RAGLoadPlanner"
                }
            )
            
            self.logger.info(
                f"Successfully planned RAG load: "
                f"{len(sources)} documents, ~{estimated_chunks} chunks"
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
        
        if "documents" not in request:
            raise ValueError("Documents are required in RAG load planning request")

    def _parse_document_sources(self, request: Dict[str, Any]) -> List[DocumentSource]:
        """Parse document sources from request."""
        sources = []
        raw_docs = request.get("documents", [])
        
        for raw_doc in raw_docs:
            if isinstance(raw_doc, dict):
                # Map strings to enums
                format_mapping = {
                    "pdf": DocumentFormat.PDF,
                    "txt": DocumentFormat.TXT,
                    "markdown": DocumentFormat.MARKDOWN,
                    "html": DocumentFormat.HTML,
                    "json": DocumentFormat.JSON,
                    "docx": DocumentFormat.DOCX
                }
                
                source = DocumentSource(
                    id=raw_doc.get("id", f"doc_{len(sources)}"),
                    name=raw_doc.get("name", "unnamed"),
                    location=raw_doc.get("location", ""),
                    format=format_mapping.get(
                        raw_doc.get("format", "txt"),
                        DocumentFormat.TXT
                    ),
                    size_bytes=raw_doc.get("size_bytes", 0),
                    encoding=raw_doc.get("encoding", "utf-8"),
                    metadata=raw_doc.get("metadata", {})
                )
                sources.append(source)
        
        # Validate document count
        if len(sources) > self.config.max_documents_per_plan:
            raise ValueError(
                f"Number of documents ({len(sources)}) exceeds maximum "
                f"({self.config.max_documents_per_plan})"
            )
        
        # Validate file sizes
        max_size_bytes = self.config.max_file_size_mb * 1024 * 1024
        for source in sources:
            if source.size_bytes > max_size_bytes:
                raise ValueError(
                    f"Document {source.name} exceeds maximum file size "
                    f"({self.config.max_file_size_mb}MB)"
                )
        
        return sources

    def _parse_chunking_config(self, request: Dict[str, Any]) -> ChunkingConfig:
        """Parse chunking configuration from request."""
        raw_config = request.get("chunking", {})
        
        # Map strings to enums
        strategy_mapping = {
            "fixed_size": ChunkingStrategy.FIXED_SIZE,
            "semantic": ChunkingStrategy.SEMANTIC,
            "recursive": ChunkingStrategy.RECURSIVE,
            "sliding_window": ChunkingStrategy.SLIDING_WINDOW
        }
        
        return ChunkingConfig(
            strategy=strategy_mapping.get(
                raw_config.get("strategy", "fixed_size"),
                ChunkingStrategy.FIXED_SIZE
            ),
            chunk_size=raw_config.get("chunk_size", self.config.default_chunk_size),
            chunk_overlap=raw_config.get("chunk_overlap", 200),
            min_chunk_size=raw_config.get("min_chunk_size", 100),
            max_chunk_size=raw_config.get("max_chunk_size", 2000),
            separators=raw_config.get("separators", ["\n\n", "\n", ".", " "])
        )

    def _parse_embedding_config(self, request: Dict[str, Any]) -> EmbeddingConfig:
        """Parse embedding configuration from request."""
        raw_config = request.get("embedding", {})
        
        return EmbeddingConfig(
            model_name=raw_config.get("model_name", self.config.default_embedding_model),
            dimension=raw_config.get("dimension", 1536),
            batch_size=raw_config.get("batch_size", 100),
            normalize=raw_config.get("normalize", True),
            cache_embeddings=raw_config.get("cache_embeddings", True)
        )

    def _parse_retrieval_config(self, request: Dict[str, Any]) -> RetrievalConfig:
        """Parse retrieval configuration from request."""
        raw_config = request.get("retrieval", {})
        
        # Map strings to enums
        mode_mapping = {
            "semantic": RetrievalMode.SEMANTIC,
            "hybrid": RetrievalMode.HYBRID,
            "bm25": RetrievalMode.BM25,
            "exact_match": RetrievalMode.EXACT_MATCH,
            "fuzzy": RetrievalMode.FUZZY
        }
        
        return RetrievalConfig(
            mode=mode_mapping.get(
                raw_config.get("mode", "semantic"),
                RetrievalMode.SEMANTIC
            ),
            top_k=raw_config.get("top_k", 5),
            similarity_threshold=raw_config.get("similarity_threshold", 0.7),
            include_metadata=raw_config.get("include_metadata", True),
            rerank=raw_config.get("rerank", False),
            rerank_model=raw_config.get("rerank_model")
        )

    def _parse_vector_store_type(self, request: Dict[str, Any]) -> VectorStoreType:
        """Parse vector store type from request."""
        raw_type = request.get("vector_store", {})
        store_type = raw_type.get("type", "chroma")
        
        # Map strings to enums
        type_mapping = {
            "chroma": VectorStoreType.CHROMA,
            "qdrant": VectorStoreType.QDRANT,
            "pinecone": VectorStoreType.PINECONE,
            "faiss": VectorStoreType.FAISS,
            "milvus": VectorStoreType.MILVUS
        }
        
        return type_mapping.get(store_type, VectorStoreType.CHROMA)

    def _create_load_plan(
        self,
        request: Dict[str, Any],
        sources: List[DocumentSource],
        vector_store_type: VectorStoreType,
        chunking_config: Optional[ChunkingConfig],
        embedding_config: Optional[EmbeddingConfig],
        retrieval_config: RetrievalConfig
    ) -> RAGLoadPlan:
        """Create RAG load plan from parsed components."""
        # Use defaults if configs are disabled
        if not chunking_config:
            chunking_config = ChunkingConfig(strategy=ChunkingStrategy.FIXED_SIZE)
        
        if not embedding_config:
            embedding_config = EmbeddingConfig()
        
        return RAGLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            document_sources=sources,
            vector_store_type=vector_store_type,
            chunking_config=chunking_config,
            embedding_config=embedding_config,
            retrieval_config=retrieval_config,
            collection_name=request.get("collection_name", "default"),
            persist_directory=request.get("persist_directory"),
            enable_preprocessing=request.get("enable_preprocessing", True),
            enable_deduplication=request.get("enable_deduplication", True),
            metadata=request.get("metadata", {})
        )

    def _estimate_chunks(self, plan: RAGLoadPlan) -> int:
        """Estimate total number of chunks from documents."""
        total_chunks = 0
        
        for source in plan.document_sources:
            # Estimate chunks based on document size and chunk configuration
            if source.size_bytes > 0:
                # Assume 1 character = 1 byte for simplicity
                # Average word = 5 characters, average chunk = 200 words
                chunk_size_bytes = plan.chunking_config.chunk_size * 5
                
                # Account for overlap
                effective_size = chunk_size_bytes - plan.chunking_config.chunk_overlap * 5
                
                if effective_size > 0:
                    chunks = source.size_bytes // effective_size
                    if source.size_bytes % effective_size > 0:
                        chunks += 1
                    total_chunks += chunks
            else:
                # Default estimate if size not known
                total_chunks += 10
        
        return total_chunks

    def _calculate_storage_requirements(self, plan: RAGLoadPlan) -> Dict[str, int]:
        """Calculate storage requirements in MB."""
        requirements = {
            "documents_mb": 0,
            "chunks_mb": 0,
            "embeddings_mb": 0,
            "index_mb": 0,
            "total_mb": 0
        }
        
        # Document storage
        total_doc_size = sum(s.size_bytes for s in plan.document_sources)
        requirements["documents_mb"] = total_doc_size // (1024 * 1024)
        
        # Chunk storage (assume chunks are 1.2x original size due to metadata)
        chunk_count = self._estimate_chunks(plan)
        avg_chunk_size = plan.chunking_config.chunk_size * 5  # bytes
        requirements["chunks_mb"] = (chunk_count * avg_chunk_size * 1.2) // (1024 * 1024)
        
        # Embedding storage (dimension * 4 bytes per float)
        if self.config.enable_embedding:
            embedding_size = plan.embedding_config.dimension * 4
            requirements["embeddings_mb"] = (chunk_count * embedding_size) // (1024 * 1024)
        
        # Index storage (varies by vector store type)
        index_multipliers = {
            VectorStoreType.CHROMA: 1.5,
            VectorStoreType.QDRANT: 2.0,
            VectorStoreType.PINECONE: 1.8,
            VectorStoreType.FAISS: 1.2,
            VectorStoreType.MILVUS: 1.6
        }
        requirements["index_mb"] = int(
            requirements["embeddings_mb"] * index_multipliers.get(plan.vector_store_type, 1.5)
        )
        
        requirements["total_mb"] = (
            requirements["documents_mb"] + 
            requirements["chunks_mb"] + 
            requirements["embeddings_mb"] + 
            requirements["index_mb"]
        )
        
        return requirements

    def _estimate_processing_time(self, plan: RAGLoadPlan) -> int:
        """Estimate processing time in seconds."""
        base_time = 10  # Base setup time
        
        # Document processing time
        doc_time = len(plan.document_sources) * 2  # 2 seconds per document
        
        # Chunking time
        chunk_count = self._estimate_chunks(plan)
        chunking_time = chunk_count * 0.01  # 10ms per chunk
        
        # Embedding time
        embedding_time = 0
        if self.config.enable_embedding:
            # Assume 100 embeddings per second
            embedding_time = chunk_count / 100
        
        # Indexing time
        indexing_time = chunk_count * 0.005  # 5ms per chunk for indexing
        
        total_time = base_time + doc_time + chunking_time + embedding_time + indexing_time
        
        return int(total_time)

    def _estimate_costs(self, plan: RAGLoadPlan) -> Dict[str, float]:
        """Estimate costs in USD."""
        costs = {
            "embedding_cost": 0.0,
            "storage_cost": 0.0,
            "total_cost": 0.0
        }
        
        # Embedding costs (OpenAI pricing as reference)
        if self.config.enable_embedding:
            chunk_count = self._estimate_chunks(plan)
            # Assume $0.0001 per 1K tokens, 1 chunk ~ 200 tokens
            costs["embedding_cost"] = (chunk_count * 200 / 1000) * 0.0001
        
        # Storage costs (assume $0.23 per GB/month for Pinecone)
        storage_gb = self._calculate_storage_requirements(plan)["total_mb"] / 1024
        costs["storage_cost"] = storage_gb * 0.23
        
        costs["total_cost"] = costs["embedding_cost"] + costs["storage_cost"]
        
        return costs


# Factory function for easy instantiation
def create_rag_load_planner(
    enable_chunking: bool = True,
    enable_embedding: bool = True,
    enable_indexing: bool = True,
    **kwargs
) -> RAGLoadPlanner:
    """Create a configured RAG load planner."""
    config = RAGLoadConfig(
        enable_chunking=enable_chunking,
        enable_embedding=enable_embedding,
        enable_indexing=enable_indexing,
        **kwargs
    )
    return RAGLoadPlanner(config)


# Convenience function for direct usage
def plan_rag_load(
    plan_name: str,
    documents: List[Dict[str, Any]],
    vector_store: str = "chroma",
    chunking: Optional[Dict[str, Any]] = None,
    embedding: Optional[Dict[str, Any]] = None,
    retrieval: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan RAG data load from simple parameters.
    
    Args:
        plan_name: Name of the load plan
        documents: List of document definitions
        vector_store: Type of vector store to use
        chunking: Optional chunking configuration
        embedding: Optional embedding configuration
        retrieval: Optional retrieval configuration
        config: Optional planner configuration overrides
        
    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "documents": documents,
        "vector_store": {"type": vector_store},
        "chunking": chunking or {},
        "embedding": embedding or {},
        "retrieval": retrieval or {"mode": "semantic"}
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
            "document_sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "location": s.location,
                    "format": s.format.value,
                    "size_bytes": s.size_bytes,
                    "encoding": s.encoding,
                    "metadata": s.metadata
                }
                for s in result.load_plan.document_sources
            ],
            "vector_store_type": result.load_plan.vector_store_type.value,
            "chunking_config": {
                "strategy": result.load_plan.chunking_config.strategy.value,
                "chunk_size": result.load_plan.chunking_config.chunk_size,
                "chunk_overlap": result.load_plan.chunking_config.chunk_overlap,
                "min_chunk_size": result.load_plan.chunking_config.min_chunk_size,
                "max_chunk_size": result.load_plan.chunking_config.max_chunk_size,
                "separators": result.load_plan.chunking_config.separators
            },
            "embedding_config": {
                "model_name": result.load_plan.embedding_config.model_name,
                "dimension": result.load_plan.embedding_config.dimension,
                "batch_size": result.load_plan.embedding_config.batch_size,
                "normalize": result.load_plan.embedding_config.normalize,
                "cache_embeddings": result.load_plan.embedding_config.cache_embeddings
            },
            "retrieval_config": {
                "mode": result.load_plan.retrieval_config.mode.value,
                "top_k": result.load_plan.retrieval_config.top_k,
                "similarity_threshold": result.load_plan.retrieval_config.similarity_threshold,
                "include_metadata": result.load_plan.retrieval_config.include_metadata,
                "rerank": result.load_plan.retrieval_config.rerank,
                "rerank_model": result.load_plan.retrieval_config.rerank_model
            },
            "collection_name": result.load_plan.collection_name,
            "persist_directory": result.load_plan.persist_directory,
            "enable_preprocessing": result.load_plan.enable_preprocessing,
            "enable_deduplication": result.load_plan.enable_deduplication,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "estimated_chunks": result.estimated_chunks,
        "embedding_count": result.embedding_count,
        "storage_requirements": result.storage_requirements,
        "processing_time_estimate": result.processing_time_estimate,
        "cost_estimate": result.cost_estimate,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }