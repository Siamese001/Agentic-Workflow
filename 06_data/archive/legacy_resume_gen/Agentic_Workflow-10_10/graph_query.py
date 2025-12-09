from typing import Any, List, Dict, Optional

try:
    from graph_store_neo4j import Neo4jGraphStore
    _graph: Optional[Neo4jGraphStore] = Neo4jGraphStore()
    _NEO4J_AVAILABLE = True
except ImportError:
    _graph = None
    _NEO4J_AVAILABLE = False

def graph_query(cypher: str, params: Dict[str, Any] | None = None) -> List[Any]:
    """
    Simple helper to run arbitrary Cypher against Neo4j and return the raw records.
    """
    if not _NEO4J_AVAILABLE or _graph is None:
        raise ImportError("Neo4j driver not installed. Install with: pip install neo4j>=5.22.0")
        
    return _graph.run(cypher, params or {})
