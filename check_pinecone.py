#!/usr/bin/env python3
"""Check what's in the Pinecone index."""

import os
from connection_manager import ConnectionFactory

try:
    pinecone = ConnectionFactory.get_pinecone_index()
    index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
    index = pinecone.Index(index_name)
    
    # Get index stats
    stats = index.describe_index_stats()
    print(f"Index stats: {stats}")
    
    # List all vectors
    vectors = index.list()
    print(f"Vector IDs: {vectors}")
    
    # Query for all vectors
    import numpy as np
    dummy_vector = np.random.rand(384).tolist()
    results = index.query(vector=dummy_vector, top_k=10, include_metadata=True)
    
    print(f"\nFound {len(results['matches'])} matches:")
    for match in results['matches']:
        print(f"- ID: {match['id']}, Score: {match['score']}")
        
except Exception as e:
    print(f"Error: {e}")
