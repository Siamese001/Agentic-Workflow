"""
Memory Architect Sync - L4 State Synchronization

Updates Pinecone vector database after atomic fission to prevent stale embeddings.
Ensures RAG (Retrieval-Augmented Generation) queries return accurate code snippets.

Strategy:
- Purge old monolith embeddings
- Generate new embeddings for sub-modules
- Cross-link with parent_monolith metadata
- Maintain L4 State consistency
"""
from typing import Any, Optional, Protocol, Dict, List
import re


import logging
import os
from typing import Dict, List, Optional

try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    Pinecone = None

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MemoryArchitectSync:
    """
    L4 State Sync: Updates Pinecone to reflect new modular architecture.
    
    Process:
    1. Purge old monolith from vector database
    2. Embed and upsert new sub-modules
    3. Cross-link with parent_monolith metadata
    4. Ensure RAG consistency
    
    Prevents:
    - Stale embeddings pointing to non-existent code
    - Hallucinated code snippets during RAG queries
    - L4 State / L1 Cognition desynchronization
    """
    
    def __init__(self):
        """Initialize Memory Architect Sync."""
        self.pinecone_available = PINECONE_AVAILABLE
        self.genai_available = GENAI_AVAILABLE
        
        # Initialize Pinecone
        if PINECONE_AVAILABLE:
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX_NAME", "canon-memory-l2")
            
            if api_key:
                try:
                    self.pc = Pinecone(api_key=api_key)
                    self.index = self.pc.Index(index_name)
                    logger.info(f"[OK] Memory Architect connected to Pinecone: {index_name}")
                except Exception as e:
                    logger.warning(f"[!]  Could not connect to Pinecone: {e}")
                    self.pinecone_available = False
            else:
                logger.warning("[!]  PINECONE_API_KEY not found")
                self.pinecone_available = False
        
        # Initialize Gemini for embeddings
        if GENAI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    self.genai_client = genai.Client(api_key=api_key)
                    logger.info("[OK] Memory Architect connected to Gemini for embeddings")
                except Exception as e:
                    logger.warning(f"[!]  Could not connect to Gemini: {e}")
                    self.genai_available = False
            else:
                self.genai_available = False
    
    def sync_fission_state(self, monolith_path: str, new_files: List[str]) -> bool:
        """
        L4 State Sync: Updates Pinecone to reflect the new modular architecture.
        
        Args:
            monolith_path: Path to original monolithic file
            new_files: List of new sub-module file paths
            
        Returns:
            True if successful, False otherwise
        """
        if not self.pinecone_available:
            logger.warning("[!]  Pinecone not available, skipping L4 State sync")
            return False
        
        try:
            # 1. Purge the old Monolith from Memory
            logger.info(f"  [Memory] Purging stale embeddings for {monolith_path}...")
            self._purge_monolith(monolith_path)
            
            # 2. Embed and Upsert the new Sub-modules
            for file_path in new_files:
                logger.info(f"  [Memory] Indexing new L4 State: {file_path}")
                self._index_file(file_path, parent_monolith=monolith_path)
            
            logger.info(f"  [OK] L4 State sync complete: {len(new_files)} files indexed")
            return True
        
        except Exception as e:
            logger.error(f"  [X] L4 State sync failed: {e}")
            return False
    
    def _purge_monolith(self, monolith_path: str):
        """
        Purge old monolith embeddings from Pinecone.
        
        Args:
            monolith_path: Path to monolithic file
        """
        try:
            # Delete vectors with matching file_path metadata
            self.index.delete(filter={"file_path": {"$eq": monolith_path}})
            logger.info(f"    [OK] Purged embeddings for {monolith_path}")
        except Exception as e:
            logger.warning(f"    [!]  Could not purge embeddings: {e}")
    
    def _index_file(self, file_path: str, parent_monolith: Optional[str] = None):
        """
        Index a file in Pinecone with embeddings.
        
        Args:
            file_path: Path to file to index
            parent_monolith: Optional parent monolith path for cross-linking
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate embedding
            vector = self._generate_embedding(content)
            
            if vector is None:
                logger.warning(f"    [!]  Could not generate embedding for {file_path}")
                return
            
            # Prepare metadata
            metadata = {
                "file_path": file_path,
                "layer": "L4_STATE",
                "line_count": len(content.splitlines()),
                "char_count": len(content)
            }
            
            if parent_monolith:
                metadata["parent_monolith"] = parent_monolith
            
            # Upsert to Pinecone
            # Create vector ID by replacing path separators
            clean_path = file_path.replace('/', '_').replace('\\', '_')
            vector_id = f"vec_{clean_path}"
            self.index.upsert(vectors=[(vector_id, vector, metadata)])
            
            logger.info(f"    [OK] Indexed {file_path} ({len(content.splitlines())} lines)")
        
        except Exception as e:
            logger.error(f"    [X] Failed to index {file_path}: {e}")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.genai_available:
            logger.warning("    [!]  Gemini not available for embeddings")
            return None
        
        try:
            # Use Gemini embedding model
            result = self.genai_client.models.embed_content(
                model='models/text-embedding-004',
                content=text
            )
            
            if result and hasattr(result, 'embedding'):
                return result.embedding
            
            logger.warning("    [!]  No embedding returned from Gemini")
            return None
        
        except Exception as e:
            logger.error(f"    [X] Embedding generation failed: {e}")
            return None
    
    def verify_sync(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Verify files are properly indexed in Pinecone.
        
        Args:
            file_paths: List of file paths to verify
            
        Returns:
            Dictionary mapping file paths to verification status
        """
        if not self.pinecone_available:
            return {path: False for path in file_paths}
        
        results = {}
        
        for file_path in file_paths:
            try:
                # Query for file
                clean_path = file_path.replace('/', '_').replace('\\', '_')
                vector_id = f"vec_{clean_path}"
                fetch_result = self.index.fetch(ids=[vector_id])
                
                results[file_path] = vector_id in fetch_result.vectors
                
                if results[file_path]:
                    logger.info(f"  [OK] Verified: {file_path}")
                else:
                    logger.warning(f"  [!]  Not found: {file_path}")
            
            except Exception as e:
                logger.error(f"  [X] Verification failed for {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def query_related_files(self, file_path: str, top_k: int = 5) -> List[Dict]:
        """
        Query Pinecone for files related to given file.
        
        Args:
            file_path: File path to find related files for
            top_k: Number of related files to return
            
        Returns:
            List of related file metadata
        """
        if not self.pinecone_available or not self.genai_available:
            return []
        
        try:
            # Read file and generate embedding
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vector = self._generate_embedding(content)
            
            if vector is None:
                return []
            
            # Query Pinecone
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )
            
            related_files = []
            for match in results.matches:
                related_files.append({
                    "file_path": match.metadata.get("file_path"),
                    "score": match.score,
                    "parent_monolith": match.metadata.get("parent_monolith")
                })
            
            return related_files
        
        except Exception as e:
            logger.error(f"  [X] Query failed: {e}")
            return []


def get_memory_architect_sync() -> MemoryArchitectSync:
    """
    Factory function to create MemoryArchitectSync instance.
    
    Returns:
        MemoryArchitectSync instance
    """
    return MemoryArchitectSync()


# Integration Example for orchestrator_main.py:
"""
from .pinecone_sync import MemoryArchitectSync

# Initialize sync manager
memory_sync = MemoryArchitectSync()

# After successful fission:
if fission_result.success:
    # Write decomposed files
    fission_manager.write_decomposed_files(fission_result)
    
    # Sync L4 State (Pinecone)
    new_file_paths = list(fission_result.new_files.keys())
    memory_sync.sync_fission_state(
        monolith_path=fission_result.original_file,
        new_files=new_file_paths
    )
    
    # Verify sync
    verification = memory_sync.verify_sync(new_file_paths)
    if all(verification.values()):
        logger.info("[OK] L4 State fully synchronized")
    else:
        logger.warning("[!]  Some files not indexed in Pinecone")
"""
