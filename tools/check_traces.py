#!/usr/bin/env python3
"""Check traces collection state"""

import chromadb

client = chromadb.PersistentClient('artifacts/chromadb')
traces = client.get_collection('traces')
print(f'Traces collection: {traces.count()} items')

sample = traces.peek(limit=1)
if sample['metadatas']:
    print(f'Sample metadata keys: {list(sample["metadatas"][0].keys())}')
    print(f'Sample metadata: {sample["metadatas"][0]}')
