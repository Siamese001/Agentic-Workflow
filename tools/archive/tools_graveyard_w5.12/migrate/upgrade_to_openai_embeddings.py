#!/usr/bin/env python3
"""
Upgrade ChromaDB collections to use OpenAI embeddings (optional)
Falls back to mock embeddings if OPENAI_API_KEY is not available
"""

import logging
import os

import chromadb
from chromadb.utils import embedding_functions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_embedding_function():
    """Get embedding function - OpenAI if available, otherwise mock"""

    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        logger.info("Using OpenAI embeddings")
        try:
            # Use OpenAI embedding function
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-3-small",  # Cost-effective model
            )
            return openai_ef, "openai"
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
            logger.info("Falling back to mock embeddings")

    # Use mock embeddings
    logger.info("Using mock embeddings (OPENAI_API_KEY not set)")

    class MockEmbeddingFunction:
        def __call__(self, input_texts):
            """Generate mock embeddings"""
            return [[0.0] * 1536 for _ in input_texts]

    return MockEmbeddingFunction(), "mock"


def upgrade_collection_embeddings(collection_name):
    """Upgrade a collection to use new embeddings"""

    logger.info(f"Upgrading collection: {collection_name}")

    # Get embedding function
    ef_func, ef_type = get_embedding_function()

    # Initialize ChromaDB
    client = chromadb.PersistentClient("artifacts/chromadb")

    try:
        # Get existing collection
        collection = client.get_collection(collection_name)
        logger.info(f"Found collection {collection_name} with {collection.count()} items")

        # Get all data
        logger.info("Retrieving existing data...")
        all_data = collection.get()

        if not all_data["ids"]:
            logger.warning(f"No data found in collection {collection_name}")
            return

        logger.info(f"Processing {len(all_data['ids'])} items...")

        # Generate new embeddings
        logger.info(f"Generating {ef_type} embeddings...")
        new_embeddings = ef_func(all_data["documents"])
        logger.info(f"Generated {len(new_embeddings)} embeddings")

        # Delete old collection and create new one with updated embedding function
        logger.info("Recreating collection with new embeddings...")
        client.delete_collection(collection_name)

        # Create new collection with proper embedding function
        if ef_type == "openai":
            new_collection = client.create_collection(
                name=collection_name,
                embedding_function=ef_func,
                metadata={"description": f"{collection_name} with OpenAI embeddings"},
            )
        else:
            new_collection = client.create_collection(
                name=collection_name,
                metadata={"description": f"{collection_name} with mock embeddings"},
            )

        # Re-add data with new embeddings (handle batching)
        logger.info("Re-ingesting data with new embeddings...")

        # Process in batches to avoid size limits
        batch_size = 5000
        total_items = len(all_data["ids"])

        for i in range(0, total_items, batch_size):
            end_idx = min(i + batch_size, total_items)

            batch_ids = all_data["ids"][i:end_idx]
            batch_docs = all_data["documents"][i:end_idx]
            batch_metas = all_data["metadatas"][i:end_idx]
            batch_embeddings = new_embeddings[i:end_idx]

            new_collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=batch_embeddings,
            )

            logger.info(
                f"  Ingested batch {i // batch_size + 1}/{(total_items - 1) // batch_size + 1} ({end_idx - i} items)"
            )

        logger.info(f"Successfully upgraded {collection_name} to {ef_type} embeddings")

    except Exception as e:
        logger.error(f"Error upgrading collection {collection_name}: {e}")


def upgrade_all_collections():
    """Upgrade all ChromaDB collections"""

    # Collections to upgrade (skip traces for now due to size)
    collections = ["docs", "code", "apps", "adg_artifacts"]

    # Get embedding function info
    _, ef_type = get_embedding_function()

    logger.info(f"Starting Wave 6: Upgrade to {ef_type} embeddings")
    logger.info(f"Collections to upgrade: {collections}")

    # Check if OpenAI is available
    if ef_type == "mock":
        logger.warning("Wave 6: Using mock embeddings (OPENAI_API_KEY not set)")
        logger.warning("To use OpenAI embeddings, set OPENAI_API_KEY environment variable")
    else:
        logger.info("Wave 6: Using OpenAI embeddings")
        logger.warning("Note: This will consume OpenAI API credits")

    # Upgrade each collection
    for collection_name in collections:
        upgrade_collection_embeddings(collection_name)

    # Get final stats
    client = chromadb.PersistentClient("artifacts/chromadb")
    logger.info("\nWave 6 Complete - Final Collection Stats:")

    all_collections = client.list_collections()
    for col in all_collections:
        count = col.count()
        logger.info(f"  {col.name}: {count} items")


def main():
    """Main function"""
    logger.info("Wave 6: Upgrade embeddings starting...")
    logger.info(f"OPENAI_API_KEY available: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

    upgrade_all_collections()


if __name__ == "__main__":
    main()
