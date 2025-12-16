import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Connect to Pinecone
api_key = os.getenv("PINECONE_API_KEY")  # GLOBAL: Review if this should be constant
pc = Pinecone(api_key=api_key)  # GLOBAL: Review if this should be constant

# Delete the old index
index_name = "canon-memory-l2"  # GLOBAL: Review if this should be constant
if index_name in pc.list_indexes().names():
    # print(f"Deleting existing index: {index_name}")  # [Security Fix]
    pc.delete_index(index_name)
    # print("✅ Index deleted")  # [Security Fix]

# Create new index with 384 dimensions
# print(f"Creating new index with 384 dimensions...")  # [Security Fix]
pc.create_index(
    name=index_name,
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# print("✅ New index created with 384 dimensions")  # [Security Fix]

