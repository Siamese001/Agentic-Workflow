from __future__ import annotations
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
import logging
import os
import re
from typing import Any, Dict, List, Optional, Protocol
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE: Any = True
except ImportError:
    PINECONE_AVAILABLE: Any = False
    Pinecone: Any = None
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE: Any = True
except ImportError:
    GENAI_AVAILABLE: Any = False
    genai: Any = None
    types: Any = None
from dotenv import load_dotenv

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from archives.location_violations.file_utils import safe_read_file, safe_write_file

load_dotenv()
Logger: Any = logging.getLogger(__name__)

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
        if PINECONE_AVAILABLE:
            api_key = os.getenv('PINECONE_API_KEY')
            index_name = os.getenv('PINECONE_INDEX_NAME', 'canon-memory-l2')
            if api_key:
                try:
                    self.pc = Pinecone(api_key=api_key)
                    self.index = self.pc.Index(index_name)
                    Logger.info(f'[OK] Memory Architect connected to Pinecone: {index_name}')
                except Exception as e:
                    Logger.warning(f'[!]  Could not connect to Pinecone: {e}')
                    self.pinecone_available = False
            else:
                Logger.warning('[!]  PINECONE_API_KEY not found')
                self.pinecone_available = False
        if GENAI_AVAILABLE:
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if api_key:
                try:
                    self.genai_client = genai.Client(api_key=api_key)
                    Logger.info('[OK] Memory Architect connected to Gemini for embeddings')
                except Exception as e:
                    Logger.warning(f'[!]  Could not connect to Gemini: {e}')
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
            Logger.warning('[!]  Pinecone not available, skipping L4 State sync')
            return False
        try:
            Logger.info(f'  [Memory] Purging stale embeddings for {monolith_path}...')
            self._purge_monolith(monolith_path)
            for file_path in new_files:
                Logger.info(f'  [Memory] Indexing new L4 State: {file_path}')
                self._index_file(file_path, parent_monolith=monolith_path)
            Logger.info(f'  [OK] L4 State sync complete: {len(new_files)} files indexed')
            return True
        except Exception as e:
            Logger.error(f'  [X] L4 State sync failed: {e}')
            return False

    def _purge_monolith(self, monolith_path: str):
        """
        Purge old monolith embeddings from Pinecone.
        
        Args:
            monolith_path: Path to monolithic file
        """
        try:
            self.index.delete(filter={'file_path': {'$eq': monolith_path}})
            Logger.info(f'    [OK] Purged embeddings for {monolith_path}')
        except Exception as e:
            Logger.warning(f'    [!]  Could not purge embeddings: {e}')

    def _index_file(self, file_path: str, parent_monolith: Optional[str]=None):
        """
        Index a file in Pinecone with embeddings.
        
        Args:
            file_path: Path to file to index
            parent_monolith: Optional parent monolith path for cross-linking
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            vector = self._generate_embedding(content)
            if vector is None:
                Logger.warning(f'    [!]  Could not generate embedding for {file_path}')
                return
            metadata = {'file_path': file_path, 'layer': 'L4_STATE', 'line_count': len(content.splitlines()), 'char_count': len(content)}
            if parent_monolith:
                metadata['parent_monolith'] = parent_monolith
            clean_path = file_path.replace('/', '_').replace('\\', '_')
            vector_id = f'vec_{clean_path}'
            self.index.upsert(vectors=[(vector_id, vector, metadata)])
            Logger.info(f'    [OK] Indexed {file_path} ({len(content.splitlines())} lines)')
        except Exception as e:
            Logger.error(f'    [X] Failed to index {file_path}: {e}')

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.genai_available:
            Logger.warning('    [!]  Gemini not available for embeddings')
            return None
        try:
            result = self.genai_client.models.embed_content(model='models/text-embedding-004', content=text)
            if result and hasattr(result, 'embedding'):
                return result.embedding
            Logger.warning('    [!]  No embedding returned from Gemini')
            return None
        except Exception as e:
            Logger.error(f'    [X] Embedding generation failed: {e}')
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
        results: Any = {}
        for file_path in file_paths:
            try:
                clean_path: Any = file_path.replace('/', '_').replace('\\', '_')
                vector_id: Any = f'vec_{clean_path}'
                fetch_result: Any = self.index.fetch(ids=[vector_id])
                results[file_path] = vector_id in fetch_result.vectors
                if results[file_path]:
                    Logger.info(f'  [OK] Verified: {file_path}')
                else:
                    Logger.warning(f'  [!]  Not found: {file_path}')
            except Exception as e:
                Logger.error(f'  [X] Verification failed for {file_path}: {e}')
                results[file_path] = False
        return results

    def query_related_files(self, file_path: str, top_k: int=5) -> List[Dict]:
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
            with open(file_path, 'r', encoding='utf-8') as f:
                content: Any = f.read()
            vector: Any = self._generate_embedding(content)
            if vector is None:
                return []
            results: Any = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
            related_files: Any = []
            for match in results.matches:
                related_files.append({'file_path': match.metadata.get('file_path'), 'score': match.score, 'parent_monolith': match.metadata.get('parent_monolith')})
            return related_files
        except Exception as e:
            Logger.error(f'  [X] Query failed: {e}')
            return []

def get_memory_architect_sync() -> MemoryArchitectSync:
    """
    Factory function to create MemoryArchitectSync instance.
    
    Returns:
        MemoryArchitectSync instance
    """
    return MemoryArchitectSync()
'\nfrom agentic_core.pinecone_sync import MemoryArchitectSync\n\n# Initialize sync manager\nmemory_sync = MemoryArchitectSync()\n\n# After successful fission:\nif FissionResult.success:\n    # Write decomposed files\n    FissionManagerAgent.write_decomposed_files(FissionResult)\n    \n    # Sync L4 State (Pinecone)\n    new_file_paths = list(FissionResult.new_files.keys())\n    memory_sync.sync_fission_state(\n        monolith_path=FissionResult.original_file,\n        new_files=new_file_paths\n    )\n    \n    # Verify sync\n    verification = memory_sync.verify_sync(new_file_paths)\n    if all(verification.values()):\n        Logger.info("[OK] L4 State fully synchronized")\n    else:\n        Logger.warning("[!]  Some files not indexed in Pinecone")\n'
