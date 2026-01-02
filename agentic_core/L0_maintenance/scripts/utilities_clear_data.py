from __future__ import annotations
"""Clear all data from Redis and Pinecone for clean simulation."""
import os
from connection_manager import ConnectionFactory
from typing import Any
try:
    redis_conn: Any = ConnectionFactory.get_redis_connection()
    redis_conn.flushall()
except Exception:
    pass
try:
    if os.getenv('PINECONE_API_KEY'):
        pinecone: Any = ConnectionFactory.get_pinecone_index()
        index_name: Any = os.getenv('PINECONE_INDEX_NAME', 'canon-memory-l2')
        index: Any = pinecone.Index(index_name)
        index.delete(delete_all=True)
    else:
        pass
except Exception:
    pass
