#!/usr/bin/env python3
"""
Vector DB MCP Server - Unified vector database interface for ChromaDB and Pinecone
Provides vector operations for semantic search, embeddings, and similarity queries
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import anyio

# Vector database imports
try:
    import chromadb
    import numpy as np
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Vector DB libraries not found: {e}", file=sys.stderr)
    print("Install with: pip install chromadb sentence-transformers numpy", file=sys.stderr)
    sys.exit(1)

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.lowlevel.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging - use stderr to avoid interfering with MCP protocol on stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
CHROMA_PATH = REPO_ROOT / "artifacts" / "chroma"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_RESULTS = 100
MAX_EMBEDDING_BATCH_SIZE = 32

class VectorDBMCPServer:
    def __init__(self):
        self.server = Server("vector-db")
        self.chroma_client = None
        self.embedding_model = None
        self._embedding_model_loading = False
        self._setup_handlers()
        # Fast initialization - defer heavy loading
        self._initialize_chroma_only()

    def _initialize_chroma_only(self):
        """Initialize only ChromaDB for fast startup"""
        try:
            CHROMA_PATH.mkdir(parents=True, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_PATH),
                settings=Settings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB initialized at: {CHROMA_PATH}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

    def _ensure_embedding_model(self):
        """Lazy load embedding model on first use"""
        if self.embedding_model is None and not self._embedding_model_loading:
            self._embedding_model_loading = True
            try:
                logger.info("Loading embedding model (lazy init)...")
                self.embedding_model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
                logger.info(f"Embedding model loaded: {DEFAULT_EMBEDDING_MODEL}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
            finally:
                self._embedding_model_loading = False
        return self.embedding_model is not None

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available vector database tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_collection",
                        description="Create a new vector collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                                "metadata": {
                                    "type": "object",
                                    "description": "Collection metadata",
                                    "additionalProperties": {"type": "string"},
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="list_collections",
                        description="List all vector collections",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                    Tool(
                        name="delete_collection",
                        description="Delete a vector collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="add_documents",
                        description="Add documents to a collection with embeddings",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "collection_name": {
                                    "type": "string",
                                    "description": "Target collection",
                                },
                                "documents": {
                                    "type": "array",
                                    "description": "Documents to add",
                                    "items": {"type": "string"},
                                },
                                "metadatas": {
                                    "type": "array",
                                    "description": "Metadata for each document",
                                    "items": {"type": "object"},
                                },
                                "ids": {
                                    "type": "array",
                                    "description": "Unique IDs for each document",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["collection_name", "documents"],
                        },
                    ),
                    Tool(
                        name="query_collection",
                        description="Query a collection for similar documents",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "collection_name": {
                                    "type": "string",
                                    "description": "Collection to query",
                                },
                                "query_text": {
                                    "type": "string",
                                    "description": "Query text",
                                },
                                "n_results": {
                                    "type": "integer",
                                    "description": "Number of results to return",
                                    "default": 10,
                                    "maximum": 100,
                                },
                                "where": {
                                    "type": "object",
                                    "description": "Filter conditions",
                                },
                                "include": {
                                    "type": "array",
                                    "description": "What to include in results",
                                    "items": {"type": "string", "enum": ["metadatas", "documents", "distances"]},
                                    "default": ["metadatas", "documents", "distances"],
                                },
                            },
                            "required": ["collection_name", "query_text"],
                        },
                    ),
                    Tool(
                        name="get_collection_info",
                        description="Get detailed information about a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Collection name",
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="embed_text",
                        description="Generate embeddings for text",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "texts": {
                                    "type": "array",
                                    "description": "Texts to embed",
                                    "items": {"type": "string"},
                                },
                                "batch_size": {
                                    "type": "integer",
                                    "description": "Batch size for processing",
                                    "default": 32,
                                    "maximum": 32,
                                },
                            },
                            "required": ["texts"],
                        },
                    ),
                    Tool(
                        name="semantic_search",
                        description="Perform semantic search across all collections",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query",
                                },
                                "collections": {
                                    "type": "array",
                                    "description": "Collections to search (empty = all)",
                                    "items": {"type": "string"},
                                },
                                "n_results": {
                                    "type": "integer",
                                    "description": "Results per collection",
                                    "default": 5,
                                    "maximum": 20,
                                },
                            },
                            "required": ["query"],
                        },
                    ),
                    Tool(
                        name="vector_stats",
                        description="Get vector database statistics",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                ],
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "create_collection":
                    return await self._create_collection(arguments)
                elif name == "list_collections":
                    return await self._list_collections(arguments)
                elif name == "delete_collection":
                    return await self._delete_collection(arguments)
                elif name == "add_documents":
                    return await self._add_documents(arguments)
                elif name == "query_collection":
                    return await self._query_collection(arguments)
                elif name == "get_collection_info":
                    return await self._get_collection_info(arguments)
                elif name == "embed_text":
                    return await self._embed_text(arguments)
                elif name == "semantic_search":
                    return await self._semantic_search(arguments)
                elif name == "vector_stats":
                    return await self._vector_stats(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    async def _create_collection(self, args: dict[str, Any]) -> CallToolResult:
        """Create a new vector collection"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        name = args["name"]
        metadata = args.get("metadata", {})

        try:
            # Check if collection already exists
            try:
                existing = self.chroma_client.get_collection(name)
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Collection '{name}' already exists",
                    )],
                    isError=True,
                )
            except Exception:
                pass  # Collection doesn't exist, which is good

            # Create collection
            collection = self.chroma_client.create_collection(
                name=name,
                metadata=metadata,
            )

            result = f"✅ Collection '{name}' created successfully\n"
            result += f"ID: {collection.id}\n"
            if metadata:
                result += f"Metadata: {json.dumps(metadata, indent=2)}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to create collection: {str(e)}")],
                isError=True,
            )

    async def _list_collections(self, args: dict[str, Any]) -> CallToolResult:
        """List all vector collections"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        try:
            collections = self.chroma_client.list_collections()

            result = f"Vector Collections ({len(collections)} total):\n\n"

            for collection in collections:
                result += f"📁 {collection.name}\n"
                result += f"   ID: {collection.id}\n"
                if collection.metadata:
                    result += f"   Metadata: {json.dumps(collection.metadata, indent=6)}\n"
                result += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to list collections: {str(e)}")],
                isError=True,
            )

    async def _delete_collection(self, args: dict[str, Any]) -> CallToolResult:
        """Delete a vector collection"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        name = args["name"]

        try:
            self.chroma_client.delete_collection(name)

            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"✅ Collection '{name}' deleted successfully",
                )],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to delete collection: {str(e)}")],
                isError=True,
            )

    async def _add_documents(self, args: dict[str, Any]) -> CallToolResult:
        """Add documents to a collection with embeddings"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        # Lazy load embedding model
        if not self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        collection_name = args["collection_name"]
        documents = args["documents"]
        metadatas = args.get("metadatas", [])
        ids = args.get("ids", [])

        if len(documents) > MAX_EMBEDDING_BATCH_SIZE:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Too many documents (max {MAX_EMBEDDING_BATCH_SIZE})",
                )],
                isError=True,
            )

        try:
            # Get collection
            collection = self.chroma_client.get_collection(collection_name)

            # Generate embeddings
            start_time = time.time()
            embeddings = self.embedding_model.encode(documents)
            embedding_time = time.time() - start_time

            # Generate IDs if not provided
            if not ids:
                ids = [f"{collection_name}_{int(time.time())}_{i}" for i in range(len(documents))]

            # Add documents
            start_time = time.time()
            collection.add(
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas if metadatas else None,
                ids=ids,
            )
            add_time = time.time() - start_time

            result = f"✅ Added {len(documents)} documents to '{collection_name}'\n"
            result += f"Embedding time: {embedding_time:.2f}s\n"
            result += f"Add time: {add_time:.2f}s\n"
            result += f"Total time: {embedding_time + add_time:.2f}s\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to add documents: {str(e)}")],
                isError=True,
            )

    async def _query_collection(self, args: dict[str, Any]) -> CallToolResult:
        """Query a collection for similar documents"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        # Lazy load embedding model
        if not self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        collection_name = args["collection_name"]
        query_text = args["query_text"]
        n_results = min(args.get("n_results", 10), MAX_RESULTS)
        where = args.get("where", {})
        include = args.get("include", ["metadatas", "documents", "distances"])

        try:
            # Get collection
            collection = self.chroma_client.get_collection(collection_name)

            # Generate query embedding
            start_time = time.time()
            query_embedding = self.embedding_model.encode([query_text])
            embedding_time = time.time() - start_time

            # Query collection
            start_time = time.time()
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where if where else None,
                include=include,
            )
            query_time = time.time() - start_time

            # Format results
            result_text = f"Query Results for '{collection_name}'\n"
            result_text += f"Query: \"{query_text}\"\n"
            result_text += f"Embedding time: {embedding_time:.3f}s\n"
            result_text += f"Query time: {query_time:.3f}s\n"
            result_text += f"Results: {n_results}\n\n"

            if results and "documents" in results and results["documents"]:
                documents = results["documents"][0]
                distances = results.get("distances", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]

                for i, doc in enumerate(documents):
                    result_text += f"Result {i+1}:\n"
                    result_text += f"  Document: {doc[:200]}{'...' if len(doc) > 200 else ''}\n"
                    if i < len(distances):
                        result_text += f"  Distance: {distances[i]:.4f}\n"
                    if i < len(metadatas) and metadatas[i]:
                        result_text += f"  Metadata: {json.dumps(metadatas[i], indent=4)}\n"
                    result_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to query collection: {str(e)}")],
                isError=True,
            )

    async def _get_collection_info(self, args: dict[str, Any]) -> CallToolResult:
        """Get detailed information about a collection"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        name = args["name"]

        try:
            collection = self.chroma_client.get_collection(name)

            # Get basic info
            info = f"Collection Info: '{name}'\n"
            info += f"ID: {collection.id}\n"

            # Get count
            try:
                count = collection.count()
                info += f"Document count: {count}\n"
            except Exception:
                info += "Document count: Unknown\n"

            # Get metadata
            if collection.metadata:
                info += f"Metadata:\n{json.dumps(collection.metadata, indent=2)}\n"

            # Get sample of data
            try:
                sample = collection.get(limit=5, include=["metadatas", "documents"])
                if sample["documents"]:
                    info += "\nSample documents:\n"
                    for i, doc in enumerate(sample["documents"]):
                        info += f"{i+1}. {doc[:100]}{'...' if len(doc) > 100 else ''}\n"
            except Exception as e:
                info += f"\nCould not retrieve sample: {e}\n"

            return CallToolResult(
                content=[TextContent(type="text", text=info)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get collection info: {str(e)}")],
                isError=True,
            )

    async def _embed_text(self, args: dict[str, Any]) -> CallToolResult:
        """Generate embeddings for text"""
        # Lazy load embedding model
        if not self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        texts = args["texts"]
        batch_size = min(args.get("batch_size", 32), MAX_EMBEDDING_BATCH_SIZE)

        if len(texts) > MAX_EMBEDDING_BATCH_SIZE:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Too many texts (max {MAX_EMBEDDING_BATCH_SIZE})",
                )],
                isError=True,
            )

        try:
            start_time = time.time()
            embeddings = self.embedding_model.encode(texts, batch_size=batch_size)
            processing_time = time.time() - start_time

            result = "Embedding Results\n"
            result += f"Texts processed: {len(texts)}\n"
            result += f"Processing time: {processing_time:.2f}s\n"
            result += f"Embedding dimension: {embeddings.shape[1]}\n"
            result += f"Texts per second: {len(texts)/processing_time:.1f}\n\n"

            # Add sample embeddings
            result += "Sample embeddings (first 5 dimensions):\n"
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                result += f"\n{i+1}. \"{text[:50]}{'...' if len(text) > 50 else ''}\"\n"
                result += f"   [{', '.join(f'{x:.4f}' for x in embedding[:5])}, ...]\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to generate embeddings: {str(e)}")],
                isError=True,
            )

    async def _semantic_search(self, args: dict[str, Any]) -> CallToolResult:
        """Perform semantic search across all collections"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        # Lazy load embedding model
        if not self._ensure_embedding_model():
            return CallToolResult(
                content=[TextContent(type="text", text="Failed to load embedding model")],
                isError=True,
            )

        query = args["query"]
        collections = args.get("collections", [])
        n_results = min(args.get("n_results", 5), 20)

        try:
            # Get all collections if none specified
            if not collections:
                all_collections = self.chroma_client.list_collections()
                collections = [col.name for col in all_collections]

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])

            results = {}
            total_time = 0

            for collection_name in collections:
                try:
                    collection = self.chroma_client.get_collection(collection_name)

                    start_time = time.time()
                    search_results = collection.query(
                        query_embeddings=query_embedding.tolist(),
                        n_results=n_results,
                        include=["metadatas", "documents", "distances"],
                    )
                    search_time = time.time() - start_time
                    total_time += search_time

                    results[collection_name] = {
                        "results": search_results,
                        "time": search_time,
                        "count": len(search_results.get("documents", [[]])[0]) if search_results.get("documents") else 0,
                    }

                except Exception as e:
                    results[collection_name] = {"error": str(e)}

            # Format results
            result_text = "Semantic Search Results\n"
            result_text += f"Query: \"{query}\"\n"
            result_text += f"Collections searched: {len(collections)}\n"
            result_text += f"Total search time: {total_time:.3f}s\n\n"

            for collection_name, data in results.items():
                result_text += f"📁 {collection_name}\n"

                if "error" in data:
                    result_text += f"  ❌ Error: {data['error']}\n"
                else:
                    result_text += f"  ⏱️  Time: {data['time']:.3f}s\n"
                    result_text += f"  📊 Results: {data['count']}\n"

                    search_results = data["results"]
                    if search_results.get("documents"):
                        documents = search_results["documents"][0]
                        distances = search_results.get("distances", [[]])[0]

                        for i, (doc, dist) in enumerate(zip(documents, distances)):
                            result_text += f"    {i+1}. (dist: {dist:.4f}) {doc[:100]}{'...' if len(doc) > 100 else ''}\n"

                result_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to perform semantic search: {str(e)}")],
                isError=True,
            )

    async def _vector_stats(self, args: dict[str, Any]) -> CallToolResult:
        """Get vector database statistics"""
        if not self.chroma_client:
            return CallToolResult(
                content=[TextContent(type="text", text="ChromaDB client not initialized")],
                isError=True,
            )

        try:
            collections = self.chroma_client.list_collections()

            stats = "Vector Database Statistics\n"
            stats += f"ChromaDB path: {CHROMA_PATH}\n"
            stats += f"Total collections: {len(collections)}\n"
            stats += f"Embedding model: {DEFAULT_EMBEDDING_MODEL}\n"

            if self.embedding_model:
                stats += f"Embedding dimension: {self.embedding_model.get_sentence_embedding_dimension()}\n"

            stats += "\nCollection Details:\n"

            total_documents = 0
            for collection in collections:
                try:
                    count = collection.count()
                    total_documents += count

                    stats += f"  📁 {collection.name}: {count} documents"
                    if collection.metadata:
                        stats += f" ({json.dumps(collection.metadata)})"
                    stats += "\n"

                except Exception:
                    stats += f"  📁 {collection.name}: Unable to get count\n"

            stats += f"\nTotal documents across all collections: {total_documents}\n"

            # Disk usage
            try:
                import shutil
                size_bytes = shutil.disk_usage(CHROMA_PATH).used
                size_mb = size_bytes / (1024 * 1024)
                stats += f"Disk usage: {size_mb:.1f} MB\n"
            except Exception:
                pass

            return CallToolResult(
                content=[TextContent(type="text", text=stats)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get vector stats: {str(e)}")],
                isError=True,
            )

async def main():
    """Main entry point"""
    server_instance = VectorDBMCPServer()

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vector-db",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Vector DB MCP Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
