from __future__ import annotations

"""
This script initializes the Pinecone client, ensures a specific index exists,
and connects to it. It also includes a placeholder for AI assistant creation,
noting that this functionality is not part of the standard Pinecone client library.
"""
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

index_name: Any = "canon-memory-l2"
index_dimension: Any = 768
index_metric: Any = "cosine"
cloud_provider: Any = "aws"
cloud_region: Any = "us-east-1"
project_root: Any = Path(__file__).parent
env_path: Any = project_root / ".env"
load_dotenv(env_path)
pinecone_api_key: Any = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    raise ValueError(
        "PINECONE_API_KEY not found in environment variables. Please ensure it's set in your .env file or environment."
    )
pc: Any = Pinecone(api_key=pinecone_api_key)
print("Pinecone client initialized.")
if not pc.has_index(INDEX_NAME):
    print(f"Creating new index: '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=INDEX_DIMENSION,
        Metric=INDEX_METRIC,
        spec=ServerlessSpec(cloud=CLOUD_PROVIDER, region=CLOUD_REGION),
    )
    print(f"Index '{INDEX_NAME}' created successfully.")
else:
    print(f"Using existing index: '{INDEX_NAME}'.")
index: Any = pc.Index(INDEX_NAME)
print(f"Connected to index: '{index.name}'.")
print(f"Index description: {index.describe_index_stats()}")
print("\nScript execution complete.")
