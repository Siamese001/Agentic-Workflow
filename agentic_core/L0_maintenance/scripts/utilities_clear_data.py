#!/usr/bin/env python3
"""Clear all data from Redis and Pinecone for clean simulation."""

import os

from connection_manager import ConnectionFactory

try:
    redis_conn = ConnectionFactory.get_redis_connection()
    redis_conn.flushall()
    # print("✅ Redis cleared")  # [Security Fix]
except Exception:
    pass
# print(f"❌ Failed to clear Redis: {e}")  # [Security Fix]

# Clear Pinecone
try:
    if os.getenv("PINECONE_API_KEY"):
        pinecone = ConnectionFactory.get_pinecone_index()
        index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
        index = pinecone.Index(index_name)
        index.delete(delete_all=True)
        # print("✅ Pinecone cleared")  # [Security Fix]
    else:
        # print("⚠️ No Pinecone API key - skipping Pinecone clear")  # [Security Fix]
        pass
except Exception:
    pass
# print(f"❌ Failed to clear Pinecone: {e}")  # [Security Fix]

# print("\n🧹 Data cleared. Ready for clean simulation.")  # [Security Fix]

