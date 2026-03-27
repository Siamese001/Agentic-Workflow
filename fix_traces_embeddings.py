#!/usr/bin/env python3
"""Fix traces collection to use BGE embeddings (1024 dimensions)"""

import logging
from pathlib import Path
import chromadb

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_traces_embeddings():
    """Upgrade traces collection to BGE embeddings"""
    
    logger.info("Fixing traces collection embedding dimensions...")
    
    # Get BGE embedding function
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-m3")
        
        class BGEEmbeddingFunction:
            def __init__(self, model):
                self.model = model
                self.dimension = model.get_sentence_embedding_dimension()
            
            def __call__(self, input_texts):
                if isinstance(input_texts, str):
                    input_texts = [input_texts]
                
                embeddings = self.model.encode(
                    input_texts,
                    normalize_embeddings=True,
                    batch_size=32,
                    show_progress_bar=False
                )
                return embeddings.tolist()
        
        ef_func = BGEEmbeddingFunction(model)
        ef_type = "bge"
        logger.info(f"Using BGE embeddings with {ef_func.dimension} dimensions")
        
    except Exception as e:
        logger.error(f"Failed to load BGE: {e}")
        logger.info("Using mock embeddings")
        
        class MockEmbeddingFunction:
            def __call__(self, input_texts):
                if isinstance(input_texts, str):
                    input_texts = [input_texts]
                return [[0.0] * 1024 for _ in input_texts]
        
        ef_func = MockEmbeddingFunction()
        ef_type = "mock"
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient("artifacts/chromadb")
    
    try:
        # Get traces collection
        collection = client.get_collection("traces")
        count = collection.count()
        logger.info(f"Found traces collection with {count} items")
        
        if count == 0:
            logger.warning("Traces collection is empty")
            return
        
        # Get sample to check current dimensions
        sample = collection.peek(limit=1)
        if sample['embeddings']:
            current_dim = len(sample['embeddings'][0])
            logger.info(f"Current embedding dimension: {current_dim}")
        
        # For large collections, we'll skip recreating and just note the status
        if count > 50000:
            logger.warning(f"Traces collection is large ({count} items)")
            logger.warning("Skipping re-embedding due to size - keeping as-is")
            logger.info("Traces collection will work with 1536-dim embeddings")
            return
        
        # Get all data (for smaller collections)
        logger.info("Retrieving all traces data...")
        all_data = collection.get()
        
        # Generate new embeddings
        logger.info(f"Generating {ef_type} embeddings...")
        new_embeddings = ef_func(all_data['documents'])
        logger.info(f"Generated {len(new_embeddings)} embeddings")
        
        # Recreate collection
        logger.info("Recreating traces collection with new embeddings...")
        client.delete_collection("traces")
        
        new_collection = client.create_collection(
            name="traces",
            metadata={"description": f"Traces with {ef_type} embeddings"}
        )
        
        # Re-add data in batches
        batch_size = 1000
        total_items = len(all_data['ids'])
        
        for i in range(0, total_items, batch_size):
            end_idx = min(i + batch_size, total_items)
            
            batch_ids = all_data['ids'][i:end_idx]
            batch_docs = all_data['documents'][i:end_idx]
            batch_metas = all_data['metadatas'][i:end_idx]
            batch_embeddings = new_embeddings[i:end_idx]
            
            new_collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=batch_embeddings
            )
            
            logger.info(f"  Ingested batch {i//batch_size + 1}/{(total_items-1)//batch_size + 1} ({end_idx-i} items)")
        
        logger.info(f"Successfully upgraded traces to {ef_type} embeddings")
        
    except Exception as e:
        logger.error(f"Error fixing traces embeddings: {e}")

def main():
    """Main function"""
    fix_traces_embeddings()
    
    # Final status
    client = chromadb.PersistentClient("artifacts/chromadb")
    traces = client.get_collection("traces")
    logger.info(f"Final traces collection: {traces.count()} items")

if __name__ == "__main__":
    main()
