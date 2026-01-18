import os
import threading
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class KnowledgeNamespace(Enum):
    AGENTS = "agents"
    MIXINS = "mixins"
    DOCS = "architecture-docs"
    HEALING = "healing-patterns"
    CONTRACTS = "api-contracts"
    CONFIGS = "config-blueprints"
    WORKFLOW = "agentic-workflow"


@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class SemanticKnowledgeClient:
    _instance: Optional["SemanticKnowledgeClient"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "SemanticKnowledgeClient":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        try:
            from pinecone import Pinecone
        except ImportError as e:
            raise ImportError("pinecone-client not installed. Run: pip install pinecone-client") from e

        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "agentic-semantic-search")

        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set")

        self._pc = Pinecone(api_key=self.api_key)
        self._index = self._pc.Index(self.index_name)
        self._initialized = True

    @property
    def is_available(self) -> bool:
        return self._index is not None

    def search(
        self,
        query: str,
        namespace: Union[KnowledgeNamespace, str],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        ns_value = namespace.value if isinstance(namespace, KnowledgeNamespace) else namespace

        try:
            q: Dict[str, Any] = {
                "inputs": {"text": query},
                "top_k": top_k,
            }
            if filter_dict:
                q["filter"] = filter_dict

            response = self._index.search_records(namespace=ns_value, query=q)

            hits = response.get("result", {}).get("hits", [])
            results: List[SearchResult] = []
            for hit in hits:
                fields = hit.get("fields", {})
                results.append(
                    SearchResult(
                        id=hit.get("_id", ""),
                        content=fields.get("content", ""),
                        score=hit.get("_score", 0.0),
                        metadata={k: v for k, v in fields.items() if k != "content"},
                    )
                )
            return results
        except Exception as e:
            logger.error(f"Error querying namespace {ns_value}: {e}")
            return []

    def search_all(
        self,
        query: str,
        top_k: int = 2,
        namespaces: Optional[List[KnowledgeNamespace]] = None,
    ) -> Dict[str, List[SearchResult]]:
        if namespaces is None:
            namespaces = list(KnowledgeNamespace)

        results: Dict[str, List[SearchResult]] = {}
        for ns in namespaces:
            results[ns.value] = self.search(query, ns, top_k=top_k)
        return results

    def find_agent_for_task(self, task_description: str) -> List[SearchResult]:
        return self.search(task_description, KnowledgeNamespace.AGENTS, top_k=3)

    def find_healing_pattern(self, error_context: str) -> List[SearchResult]:
        return self.search(error_context, KnowledgeNamespace.HEALING, top_k=3)

    def get_api_contract(self, class_method_name: str) -> List[SearchResult]:
        return self.search(class_method_name, KnowledgeNamespace.CONTRACTS, top_k=3)

    def find_mixin(self, capability: str) -> List[SearchResult]:
        return self.search(capability, KnowledgeNamespace.MIXINS, top_k=3)

    def find_documentation(self, topic: str) -> List[SearchResult]:
        return self.search(topic, KnowledgeNamespace.DOCS, top_k=3)

    def find_config(self, config_query: str) -> List[SearchResult]:
        return self.search(config_query, KnowledgeNamespace.CONFIGS, top_k=3)

    def get_stats(self) -> Dict[str, Any]:
        if not self.is_available:
            return {"error": "Pinecone index not available"}

        try:
            stats = self._index.describe_index_stats()

            namespaces: Dict[str, int] = {}
            total_records: int = 0
            dimension: int = 0

            if isinstance(stats, dict):
                dimension = int(stats.get("dimension") or 0)
                total_records = int(stats.get("totalRecordCount") or 0)
                for ns, info in (stats.get("namespaces") or {}).items():
                    if isinstance(info, dict):
                        namespaces[ns] = int(info.get("recordCount") or 0)
            else:
                dimension = int(getattr(stats, "dimension", 0) or 0)
                total_records = int(getattr(stats, "total_record_count", 0) or 0)
                stats_namespaces = getattr(stats, "namespaces", {}) or {}
                for ns, info in stats_namespaces.items():
                    namespaces[ns] = int(getattr(info, "record_count", 0) or 0)

            return {
                "namespaces": namespaces,
                "total_records": total_records,
                "dimension": dimension,
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}
