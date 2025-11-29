# graph_store_neo4j.py
# L2-safe Neo4j graph store stub module.

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None

class Neo4jGraphStore:
    """
    Stub graph store class used when Neo4j is not installed.
    Provides import-safe behavior only.
    """

    def __init__(self, uri=None, auth=None):
        if GraphDatabase is None:
            raise ImportError("Neo4j driver not installed")
        self.driver = None

    def write_node(self, *args, **kwargs):
        return {"status": "neo4j_unavailable"}

    def write_relationship(self, *args, **kwargs):
        return {"status": "neo4j_unavailable"}

    def close(self):
        return

__all__ = ["Neo4jGraphStore", "GraphDatabase"]
