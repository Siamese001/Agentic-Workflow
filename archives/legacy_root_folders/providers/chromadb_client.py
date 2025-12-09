"""
ChromaDB client provider for vector storage operations.

Isolates ChromaDB SDK dependencies to the providers layer
and provides a clean interface for vector store operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

try:
    import chromadb  # type: ignore
except ImportError as exc:
    raise ImportError("chromadb package not installed. Install with: pip install chromadb") from exc


class ChromaClient:
    """Provider client for ChromaDB operations."""
    
    def __init__(self, host: str = "localhost", port: int = 8000,
                 path: Optional[str] = None, settings: Optional[Dict] = None):
        """Initialize ChromaDB client with connection parameters."""
        if path:
            # Use persistent storage
            self.client = chromadb.PersistentClient(path=path, settings=settings)
        else:
            # Use in-memory or remote client
            self.client = chromadb.HttpClient(host=host, port=port, settings=settings)
    
    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> Any:
        """Create a new collection in ChromaDB."""
        return self.client.create_collection(name=name, metadata=metadata)
    
    def get_collection(self, name: str) -> Any:
        """Get an existing collection from ChromaDB."""
        return self.client.get_collection(name=name)
    
    def delete_collection(self, name: str) -> None:
        """Delete a collection from ChromaDB."""
        self.client.delete_collection(name=name)
    
    def list_collections(self) -> List[Any]:
        """List all collections in ChromaDB."""
        return self.client.list_collections()
    
    def heartbeat(self) -> Dict[str, Any]:
        """Check ChromaDB server heartbeat."""
        return self.client.heartbeat()
    
    def get_version(self) -> str:
        """Get ChromaDB version."""
        return self.client.get_version()


@dataclass
class ChromaConfig:
    """Configuration for ChromaDB client."""
    host: str = "localhost"
    port: int = 8000
    path: Optional[str] = None
    settings: Optional[Dict] = None


def init_chroma_client(config: Optional[ChromaConfig] = None) -> ChromaClient:
    """Initialize a ChromaDB client from configuration."""
    if config is None:
        config = ChromaConfig()
    
    return ChromaClient(
        host=config.host,
        port=config.port,
        path=config.path,
        settings=config.settings
    )
