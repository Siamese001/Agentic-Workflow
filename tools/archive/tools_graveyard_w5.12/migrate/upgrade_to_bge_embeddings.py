#!/usr/bin/env python3
"""
Upgrade ChromaDB collections to use BGE embeddings (recommended)
BGE models are open-source, free, and high-quality
"""

import logging

import chromadb

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_bge_embedding_function():
    """Get BGE embedding function"""

    try:
        # Try to import sentence-transformers
        from sentence_transformers import SentenceTransformer

        # Use BGE-M3 model (multilingual, high performance)
        model_name = "BAAI/bge-m3"
        logger.info(f"Loading BGE model: {model_name}")

        # Load model
        model = SentenceTransformer(model_name)

        class BGEEmbeddingFunction:
            def __init__(self, model):
                self.model = model
                self.dimension = model.get_sentence_embedding_dimension()

            def __call__(self, input_texts):
                """Generate BGE embeddings"""
                # Handle single text or list of texts
                if isinstance(input_texts, str):
                    input_texts = [input_texts]

                embeddings = self.model.encode(
                    input_texts,
                    normalize_embeddings=True,  # Important for cosine similarity
                    batch_size=32,
                    show_progress_bar=False,
                )

                return embeddings.tolist()

        logger.info(f"Successfully loaded BGE model with {BGEEmbeddingFunction(model).dimension} dimensions")
        return BGEEmbeddingFunction(model), "bge"

    except ImportError:
        logger.warning("sentence-transformers not installed")
        logger.info("Install with: pip install sentence-transformers")
        logger.info("Falling back to mock embeddings")

        class MockEmbeddingFunction:
            def __call__(self, input_texts):
                if isinstance(input_texts, str):
                    input_texts = [input_texts]
                return [[0.0] * 1024 for _ in input_texts]  # BGE typically uses 1024 dims

        return MockEmbeddingFunction(), "mock"

    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        logger.error(f"Error loading BGE model: {e}")
        logger.info("Falling back to mock embeddings")

        class MockEmbeddingFunction:
            def __call__(self, input_texts):
                if isinstance(input_texts, str):
                    input_texts = [input_texts]
                return [[0.0] * 1024 for _ in input_texts]

        return MockEmbeddingFunction(), "mock"


def upgrade_collection_embeddings(collection_name):
    """Upgrade a collection to use BGE embeddings"""

    logger.info(f"Upgrading collection: {collection_name}")

    # Get BGE embedding function
    ef_func, ef_type = get_bge_embedding_function()

    # Initialize ChromaDB
    client = chromadb.PersistentClient("artifacts/chromadb")

    try:
        # Get existing collection
        collection = client.get_collection(collection_name)
        count = collection.count()
        logger.info(f"Found collection {collection_name} with {count} items")

        if count == 0:
            logger.warning(f"Collection {collection_name} is empty, skipping")
            return

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

        # Delete old collection and create new one
        logger.info("Recreating collection with new embeddings...")
        client.delete_collection(collection_name)

        # Create new collection
        if ef_type == "bge":
            new_collection = client.create_collection(
                name=collection_name,
                metadata={"description": f"{collection_name} with BGE embeddings"},
            )
        else:
            new_collection = client.create_collection(
                name=collection_name,
                metadata={"description": f"{collection_name} with mock embeddings"},
            )

        # Re-add data with new embeddings (handle batching)
        logger.info("Re-ingesting data with new embeddings...")

        # Process in batches to avoid memory issues
        batch_size = 1000
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

    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        logger.error(f"Error upgrading collection {collection_name}: {e}")


def upgrade_all_collections():
    """Upgrade all ChromaDB collections to BGE embeddings"""

    # Collections to upgrade (skip traces due to size unless needed)
    collections = ["docs", "code", "apps", "adg_artifacts"]

    # Get embedding function info
    _, ef_type = get_bge_embedding_function()

    logger.info(f"Wave 6: Upgrade to {ef_type} embeddings")
    logger.info(f"Collections to upgrade: {collections}")

    if ef_type == "bge":
        logger.info("✅ Using BGE embeddings (open-source, high-quality)")
        logger.info("   Model: BAAI/bge-m3 (multilingual, 1024 dimensions)")
    else:
        logger.warning("⚠️ Using mock embeddings")
        logger.warning("   Install sentence-transformers to use BGE:")
        logger.warning("   pip install sentence-transformers")

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
    logger.info("Wave 6: Upgrade to BGE embeddings")
    logger.info("BGE advantages:")
    logger.info("  - Open source (no API costs)")
    logger.info("  - High quality (competitive with OpenAI)")
    logger.info("  - Self-hosted (data privacy)")
    logger.info("  - Multilingual support")

    upgrade_all_collections()


if __name__ == "__main__":
    main()
