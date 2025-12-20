import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Get the project root directory (where .env is located)
project_root = Path(__file__).parent
env_path = project_root / '.env'

# This pulls your API keys from the existing .env file
load_dotenv(env_path)

# Get the Pinecone API key from environment
pinecone_api_key = os.getenv('PINECONE_API_KEY')

if not pinecone_api_key:
    raise ValueError("PINECONE_API_KEY not found in environment variables")

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Use your existing index
index_name = "canon-memory-l2"

# Check if index exists, if not create it
if not pc.has_index(index_name):
    print(f"Creating new index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=768,  # Matches your existing index
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"  # MUST be us-east-1
        )
    )
else:
    print(f"Using existing index: {index_name}")

# Connect to the index
index = pc.Index(index_name)
print(f"Connected to index: {index_name}")

# Create assistant
assistant = pc.assistant.create_assistant(
    assistant_name="example-assistant",
    instructions="Answer in polite, short sentences. Use American English spelling and vocabulary.",
    timeout=30 # Wait 30 seconds for assistant operation to complete.
)

print(f"Assistant created successfully with ID: {assistant.assistant_id}")