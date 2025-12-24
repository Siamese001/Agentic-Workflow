"""
This script initializes the Pinecone client, ensures a specific index exists,
and connects to it. It also includes a placeholder for AI assistant creation,
noting that this functionality is not part of the standard Pinecone client library.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


# --- Configuration Constants ---
# Define constants for better readability and maintainability
INDEX_NAME = "canon-memory-l2"
INDEX_DIMENSION = 768  # Matches your existing index's dimension
INDEX_METRIC = "cosine"
CLOUD_PROVIDER = "aws"
CLOUD_REGION = "us-east-1"  # IMPORTANT: Must be us-east-1 for ServerlessSpec


# --- Environment Setup ---
# Get the project root directory (where .env is located)
# This ensures the .env file is found regardless of the current working directory.
project_root = Path(__file__).parent
env_path = project_root / '.env'

# Load environment variables from the .env file
load_dotenv(env_path)

# Get the Pinecone API key from environment variables
pinecone_api_key = os.getenv('PINECONE_API_KEY')

# Validate that the API key is present
if not pinecone_api_key:
    raise ValueError("PINECONE_API_KEY not found in environment variables. "
                     "Please ensure it's set in your .env file or environment.")


# --- Pinecone Client Initialization ---
# Initialize the Pinecone client with the API key
pc = Pinecone(api_key=pinecone_api_key)
print("Pinecone client initialized.")


# --- Pinecone Index Management ---
# Check if the specified index exists, if not, create it
if not pc.has_index(INDEX_NAME):
    print(f"Creating new index: '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=INDEX_DIMENSION,
        metric=INDEX_METRIC,
        spec=ServerlessSpec(
            cloud=CLOUD_PROVIDER,
            region=CLOUD_REGION
        )
    )
    print(f"Index '{INDEX_NAME}' created successfully.")
else:
    print(f"Using existing index: '{INDEX_NAME}'.")

# Connect to the Pinecone index
index = pc.Index(INDEX_NAME)
# Split long print statement for better readability and PEP 8 compliance
print(f"Connected to index: '{index.name}'.")
print(f"Index description: {index.describe_index_stats()}")


# --- AI Assistant Creation (Placeholder/Note) ---
# IMPORTANT NOTE:
# The `pc.assistant.create_assistant` method is NOT part of the standard
# `pinecone-client` library (as of v3.x). This functionality might be
# specific to a higher-level framework (e.g., LangChain, LlamaIndex),
# a custom wrapper, or a beta feature not exposed directly through the
# core client.
#
# If you intend to create an AI assistant that uses Pinecone as a vector store,
# you would typically integrate Pinecone with an LLM framework (like LangChain
# or LlamaIndex) and define your assistant's logic there.
#
# The following code is commented out because it will cause an AttributeError
# with the standard Pinecone client.

# try:
#     # Create assistant (This functionality is not standard in pinecone-client)
#     assistant = pc.assistant.create_assistant(
#         assistant_name="example-assistant",
#         instructions="Answer in polite, short sentences. Use American English spelling and vocabulary.",
#         timeout=30  # Wait 30 seconds for assistant operation to complete.
#     )
#     print(f"Assistant created successfully with ID: {assistant.assistant_id}")
# except AttributeError:
#     print("\nWARNING: `pc.assistant.create_assistant` is not a standard method "
#           "of the Pinecone client library (v3.x).")

print("\nScript execution complete.")