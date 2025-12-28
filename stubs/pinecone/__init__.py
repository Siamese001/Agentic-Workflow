"""
Pinecone Stub Package - External Client Integration

PURPOSE:
    Provides stub implementations for Pinecone vector database operations.
    Enables testing of vector search and RAG functionality without live Pinecone connection.

STATUS: Active - Used for testing L4 State layer
INTEGRATION: Connected via PINECONE_API_KEY in .env

CLASSES:
    - Index: Stub for Pinecone index operations (upsert, query)
    - GRPCIndex: GRPC-based index stub (inherits from Index)

FUNCTIONS:
    - init: Stub initialization (no-op)
"""
from .core import Index, init, GRPCIndex
__all__ = ["init", "Index", "GRPCIndex"]
