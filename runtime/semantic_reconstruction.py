"""
Semantic Reconstruction for Phase 0.5 Cache Rebuild

Provides query APIs and reconstruction capabilities for the semantic cache,
including semantic similarity search, file signature reconstruction, and
orphan detection for both Resume Engine (RG) and Outreach Engine (LIC) engines.
"""

from __future__ import annotations
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import logging
from collections import defaultdict

# Add schemas to path for imports
sys.path.append(str(Path(__file__).parent.parent / "schemas"))
from semantic_lineage import (
    EngineType, ASTSignature
)


@dataclass
class SimilarityResult:
    """Result of semantic similarity search"""
    file_hash: str
    file_path: Path
    engine: EngineType
    archive_version: str
    similarity_score: float
    match_type: str  # "exact", "semantic", "partial"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_hash": self.file_hash,
            "file_path": str(self.file_path),
            "engine": self.engine.value,
            "archive_version": self.archive_version,
            "similarity_score": self.similarity_score,
            "match_type": self.match_type
        }


@dataclass
class ReconstructionQuery:
    """Query for semantic reconstruction"""
    query_type: str  # "similarity", "signature", "path", "content"
    query_params: Dict[str, Any]
    engine_filter: Optional[EngineType] = None
    version_filter: Optional[str] = None
    max_results: int = 10
    min_similarity: float = 0.5


@dataclass
class OrphanReport:
    """Report on orphaned files and unreferenced artifacts"""
    orphaned_files: List[str]
    unreferenced_hashes: List[str]
    broken_lineage_chains: List[str]
    missing_dependencies: List[str]
    cleanup_recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "orphaned_files": self.orphaned_files,
            "unreferenced_hashes": self.unreferenced_hashes,
            "broken_lineage_chains": self.broken_lineage_chains,
            "missing_dependencies": self.missing_dependencies,
            "cleanup_recommendations": self.cleanup_recommendations
        }


class EmbeddingIndex:
    """In-memory index for fast embedding similarity searches"""
    
    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}  # file_hash -> embedding_vector
        self.metadata: Dict[str, Dict[str, Any]] = {}  # file_hash -> metadata
        self.dimension: int = 0
    
    def add_vector(self, file_hash: str, vector: List[float], metadata: Dict[str, Any]):
        """Add embedding vector to index"""
        if not self.vectors:
            self.dimension = len(vector)
        elif len(vector) != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
        
        self.vectors[file_hash] = vector
        self.metadata[file_hash] = metadata
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def search_similar(self, query_vector: List[float], top_k: int = 10, 
                      min_similarity: float = 0.5) -> List[Tuple[str, float]]:
        """Find most similar vectors to query vector"""
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension mismatch: expected {self.dimension}, got {len(query_vector)}")
        
        similarities = []
        for file_hash, vector in self.vectors.items():
            similarity = self.cosine_similarity(query_vector, vector)
            if similarity >= min_similarity:
                similarities.append((file_hash, similarity))
        
        # Return top-k results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a file hash"""
        return self.metadata.get(file_hash)


class SignatureIndex:
    """Index for fast signature-based searches"""
    
    def __init__(self):
        self.function_signatures: Dict[str, Set[str]] = defaultdict(set)  # function_name -> file_hashes
        self.class_signatures: Dict[str, Set[str]] = defaultdict(set)  # class_name -> file_hashes
        self.import_signatures: Dict[str, Set[str]] = defaultdict(set)  # import_name -> file_hashes
        self.path_index: Dict[str, str] = {}  # relative_path -> file_hash
    
    def add_signature(self, file_hash: str, ast_signature: ASTSignature, file_path: Path):
        """Add AST signature to index"""
        # Index functions
        for func_name in ast_signature.function_signatures.keys():
            self.function_signatures[func_name].add(file_hash)
        
        # Index classes
        for class_name in ast_signature.class_signatures.keys():
            self.class_signatures[class_name].add(file_hash)
        
        # Index imports
        for import_name in ast_signature.import_graph.keys():
            self.import_signatures[import_name].add(file_hash)
        
        # Index path
        relative_path = str(file_path)
        self.path_index[relative_path] = file_hash
    
    def find_by_function(self, function_name: str) -> Set[str]:
        """Find files containing specific function"""
        return self.function_signatures.get(function_name, set())
    
    def find_by_class(self, class_name: str) -> Set[str]:
        """Find files containing specific class"""
        return self.class_signatures.get(class_name, set())
    
    def find_by_import(self, import_name: str) -> Set[str]:
        """Find files importing specific module"""
        return self.import_signatures.get(import_name, set())
    
    def find_by_path(self, file_path: str) -> Optional[str]:
        """Find file hash by path"""
        return self.path_index.get(file_path)


class SemanticReconstructor:
    """Main semantic reconstruction engine"""
    
    def __init__(self, cache_root: Path):
        self.cache_root = cache_root
        self.logger = logging.getLogger("SemanticReconstructor")
        self.embedding_index = EmbeddingIndex()
        self.signature_index = SignatureIndex()
        self.cache_entries: Dict[str, Dict[str, Any]] = {}  # file_hash -> cache_entry_data
        
        self._load_cache_index()
    
    def _load_cache_index(self):
        """Load all cache entries into memory indexes"""
        self.logger.info("Loading semantic cache into memory")
        
        total_files = 0
        
        # Load both engines
        for engine in [EngineType.RESUME_ENGINE, EngineType.OUTREACH_ENGINE]:
            engine_dir = self.cache_root / ("resume_engine" if engine == EngineType.RESUME_ENGINE else "outreach_engine")
            
            if not engine_dir.exists():
                continue
            
            for version_dir in engine_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                
                version_files = self._load_version_index(version_dir, engine, version_dir.name)
                total_files += version_files
        
        self.logger.info(f"Loaded {total_files} cache entries into memory")
        self.logger.info(f"Embedding index: {len(self.embedding_index.vectors)} vectors")
        self.logger.info(f"Signature index: {len(self.signature_index.function_signatures)} functions indexed")
    
    def _load_version_index(self, version_dir: Path, engine: EngineType, version: str) -> int:
        """Load cache entries for a specific version"""
        file_count = 0
        
        for ast_file in version_dir.glob("*.ast"):
            try:
                # Load AST data
                with open(ast_file, 'r', encoding='utf-8') as f:
                    ast_data = json.load(f)
                
                # Load metadata
                meta_file = ast_file.with_suffix(".ast.meta.json")
                if not meta_file.exists():
                    continue
                
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                
                # Load embedding
                embedding_file = ast_file.with_suffix(".embedding")
                embedding_data = {}
                if embedding_file.exists():
                    with open(embedding_file, 'r', encoding='utf-8') as f:
                        embedding_data = json.load(f)
                
                file_hash = meta_data["file_hash"]
                
                # Store in cache entries
                self.cache_entries[file_hash] = {
                    "ast_data": ast_data,
                    "meta_data": meta_data,
                    "embedding_data": embedding_data,
                    "engine": engine,
                    "version": version,
                    "file_path": Path(meta_data["file_path"])
                }
                
                # Index embedding
                if embedding_data and "embedding_data" in embedding_data:
                    self.embedding_index.add_vector(
                        file_hash,
                        embedding_data["embedding_data"],
                        {
                            "engine": engine.value,
                            "version": version,
                            "file_path": str(meta_data["file_path"])
                        }
                    )
                
                # Index signature (simplified AST reconstruction)
                self._index_signature(file_hash, ast_data, Path(meta_data["file_path"]))
                
                file_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to load cache entry from {ast_file}: {e}")
        
        return file_count
    
    def _index_signature(self, file_hash: str, ast_data: Dict[str, Any], file_path: Path):
        """Index AST signature for fast searches"""
        # Create simplified AST signature for indexing
        function_signatures = ast_data.get("function_signatures", {})
        class_signatures = ast_data.get("class_signatures", {})
        import_graph = ast_data.get("import_graph", {})
        
        # Create a mock ASTSignature object for indexing
        mock_signature = ASTSignature(
            signature=None,  # Not needed for indexing
            root_nodes=[],
            import_graph=import_graph,
            function_signatures=function_signatures,
            class_signatures=class_signatures,
            complexity_metrics={}
        )
        
        self.signature_index.add_signature(file_hash, mock_signature, file_path)
    
    def query_semantic_similarity(self, query_text: str, query: ReconstructionQuery) -> List[SimilarityResult]:
        """Query for semantically similar files"""
        self.logger.info(f"Performing semantic similarity query: {query_text}")
        
        # Generate mock embedding for query (in practice, use real embedding service)
        query_embedding = self._generate_query_embedding(query_text)
        
        # Search embedding index
        similar_files = self.embedding_index.search_similar(
            query_embedding,
            top_k=query.max_results,
            min_similarity=query.min_similarity
        )
        
        results = []
        for file_hash, similarity in similar_files:
            metadata = self.embedding_index.get_metadata(file_hash)
            if metadata:
                # Apply filters
                if query.engine_filter and metadata["engine"] != query.engine_filter.value:
                    continue
                
                if query.version_filter and metadata["version"] != query.version_filter:
                    continue
                
                result = SimilarityResult(
                    file_hash=file_hash,
                    file_path=Path(metadata["file_path"]),
                    engine=EngineType(metadata["engine"]),
                    archive_version=metadata["version"],
                    similarity_score=similarity,
                    match_type="semantic"
                )
                results.append(result)
        
        return results
    
    def query_by_signature(self, function_name: Optional[str] = None,
                          class_name: Optional[str] = None,
                          import_name: Optional[str] = None,
                          query: ReconstructionQuery = None) -> List[SimilarityResult]:
        """Query files by function, class, or import signatures"""
        if query is None:
            query = ReconstructionQuery("signature", {})
        
        matching_hashes = set()
        
        if function_name:
            matching_hashes.update(self.signature_index.find_by_function(function_name))
        
        if class_name:
            matching_hashes.update(self.signature_index.find_by_class(class_name))
        
        if import_name:
            matching_hashes.update(self.signature_index.find_by_import(import_name))
        
        results = []
        for file_hash in matching_hashes:
            if file_hash not in self.cache_entries:
                continue
            
            entry_data = self.cache_entries[file_hash]
            
            # Apply filters
            if query.engine_filter and entry_data["engine"] != query.engine_filter:
                continue
            
            if query.version_filter and entry_data["version"] != query.version_filter:
                continue
            
            result = SimilarityResult(
                file_hash=file_hash,
                file_path=entry_data["file_path"],
                engine=entry_data["engine"],
                archive_version=entry_data["version"],
                similarity_score=1.0,  # Exact match
                match_type="exact"
            )
            results.append(result)
        
        # Limit results
        return results[:query.max_results]
    
    def query_by_path(self, file_path: str, query: ReconstructionQuery = None) -> Optional[SimilarityResult]:
        """Query file by exact path"""
        if query is None:
            query = ReconstructionQuery("path", {})
        
        file_hash = self.signature_index.find_by_path(file_path)
        if not file_hash or file_hash not in self.cache_entries:
            return None
        
        entry_data = self.cache_entries[file_hash]
        
        # Apply filters
        if query.engine_filter and entry_data["engine"] != query.engine_filter:
            return None
        
        if query.version_filter and entry_data["version"] != query.version_filter:
            return None
        
        return SimilarityResult(
            file_hash=file_hash,
            file_path=entry_data["file_path"],
            engine=entry_data["engine"],
            archive_version=entry_data["version"],
            similarity_score=1.0,
            match_type="exact"
        )
    
    def reconstruct_file_signature(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Reconstruct complete file signature from cache"""
        if file_hash not in self.cache_entries:
            return None
        
        entry_data = self.cache_entries[file_hash]
        
        # Reconstruct complete signature
        reconstructed = {
            "file_signature": entry_data["meta_data"],
            "ast_signature": entry_data["ast_data"],
            "embedding": entry_data["embedding_data"],
            "reconstruction_timestamp": datetime.now().isoformat(),
            "cache_location": {
                "engine": entry_data["engine"].value,
                "version": entry_data["version"],
                "file_hash": file_hash
            }
        }
        
        return reconstructed
    
    def detect_orphans(self) -> OrphanReport:
        """Detect orphaned files and broken references"""
        self.logger.info("Detecting orphaned files and broken references")
        
        # Check for unreferenced hashes
        all_hash_files = set()
        referenced_hashes = set()
        
        # Scan all cache directories for hash files
        for engine_dir in [self.cache_root / "resume_engine", self.cache_root / "outreach_engine"]:
            if not engine_dir.exists():
                continue
            
            for version_dir in engine_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                
                for hash_file in version_dir.glob("*.json"):
                    if hash_file.stem.endswith(".ast") or hash_file.stem.endswith(".embedding"):
                        # Extract hash from filename
                        hash_part = hash_file.stem.replace(".ast", "").replace(".embedding", "")
                        all_hash_files.add(hash_part)
        
        # Find referenced hashes in metadata
        for entry_data in self.cache_entries.values():
            referenced_hashes.add(entry_data["meta_data"]["file_hash"])
        
        orphaned_files = list(all_hash_files - referenced_hashes)
        unreferenced_hashes = list(referenced_hashes - all_hash_files)
        
        # Check for broken lineage chains
        broken_lineage_chains = []
        # This would require loading lineage data from semantic_lineage_merge results
        
        # Check for missing dependencies
        missing_dependencies = []
        for file_hash, entry_data in self.cache_entries.items():
            ast_data = entry_data["ast_data"]
            import_graph = ast_data.get("import_graph", {})
            
            for import_name in import_graph.keys():
                # Check if imported module exists in cache
                import_matches = self.signature_index.find_by_import(import_name)
                if not import_matches:
                    missing_dependencies.append(f"{file_hash}: imports {import_name}")
        
        # Generate cleanup recommendations
        cleanup_recommendations = []
        if orphaned_files:
            cleanup_recommendations.append(f"Remove {len(orphaned_files)} orphaned hash files")
        if unreferenced_hashes:
            cleanup_recommendations.append(f"Investigate {len(unreferenced_hashes)} unreferenced hashes")
        if missing_dependencies:
            cleanup_recommendations.append(f"Review {len(missing_dependencies)} missing dependencies")
        
        return OrphanReport(
            orphaned_files=orphaned_files,
            unreferenced_hashes=unreferenced_hashes,
            broken_lineage_chains=broken_lineage_chains,
            missing_dependencies=missing_dependencies,
            cleanup_recommendations=cleanup_recommendations
        )
    
    def _generate_query_embedding(self, query_text: str) -> List[float]:
        """Generate embedding for query text (mock implementation)"""
        # In practice, this would use the same embedding service as the scanner
        # For now, generate a deterministic mock embedding
        import hashlib
        
        hash_obj = hashlib.md5(query_text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to float values
        embedding = []
        for i in range(0, min(64, len(hash_hex)), 2):
            byte_val = int(hash_hex[i:i+2], 16)
            embedding.append(byte_val / 255.0)
        
        return embedding
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "total_files": len(self.cache_entries),
            "embedding_index_size": len(self.embedding_index.vectors),
            "signature_index_stats": {
                "functions_indexed": len(self.signature_index.function_signatures),
                "classes_indexed": len(self.signature_index.class_signatures),
                "imports_indexed": len(self.signature_index.import_signatures),
                "paths_indexed": len(self.signature_index.path_index)
            },
            "engine_distribution": defaultdict(int),
            "version_distribution": defaultdict(int),
            "file_type_distribution": defaultdict(int)
        }
        
        for entry_data in self.cache_entries.values():
            stats["engine_distribution"][entry_data["engine"].value] += 1
            stats["version_distribution"][entry_data["version"]] += 1
            
            file_ext = entry_data["file_path"].suffix.lower()
            stats["file_type_distribution"][file_ext] += 1
        
        return stats
    
    def export_cache_manifest(self) -> Dict[str, Any]:
        """Export complete cache manifest for external use"""
        manifest = {
            "export_timestamp": datetime.now().isoformat(),
            "cache_root": str(self.cache_root),
            "statistics": self.get_cache_statistics(),
            "file_manifest": []
        }
        
        for file_hash, entry_data in self.cache_entries.items():
            file_info = {
                "file_hash": file_hash,
                "file_path": str(entry_data["file_path"]),
                "engine": entry_data["engine"].value,
                "version": entry_data["version"],
                "file_size": entry_data["meta_data"]["size_bytes"],
                "last_modified": entry_data["meta_data"]["last_modified"],
                "has_embedding": bool(entry_data["embedding_data"]),
                "function_count": len(entry_data["ast_data"].get("function_signatures", {})),
                "class_count": len(entry_data["ast_data"].get("class_signatures", {}))
            }
            manifest["file_manifest"].append(file_info)
        
        return manifest


def main():
    """Main entry point for semantic reconstruction"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cache_root = Path("data/semantic_cache")
    
    if not cache_root.exists():
        print(f"Error: Semantic cache directory not found: {cache_root}")
        sys.exit(1)
    
    reconstructor = SemanticReconstructor(cache_root)
    
    try:
        # Example queries
        print("Semantic Reconstruction Examples:")
        print("=" * 50)
        
        # Get cache statistics
        stats = reconstructor.get_cache_statistics()
        print("Cache Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Embedding vectors: {stats['embedding_index_size']}")
        print(f"  Engine distribution: {dict(stats['engine_distribution'])}")
        
        # Example semantic similarity query
        query = ReconstructionQuery(
            query_type="similarity",
            query_params={"text": "function that processes data"},
            max_results=5,
            min_similarity=0.3
        )
        
        similarity_results = reconstructor.query_semantic_similarity("data processing function", query)
        print(f"\nSemantic similarity results: {len(similarity_results)} files found")
        for result in similarity_results[:3]:
            print(f"  {result.file_path.name} ({result.engine.value}/{result.archive_version}) - {result.similarity_score:.3f}")
        
        # Example signature query
        signature_results = reconstructor.query_by_signature(function_name="main")
        print(f"\nFiles with 'main' function: {len(signature_results)} found")
        
        # Detect orphans
        orphan_report = reconstructor.detect_orphans()
        print("\nOrphan Detection:")
        print(f"  Orphaned files: {len(orphan_report.orphaned_files)}")
        print(f"  Missing dependencies: {len(orphan_report.missing_dependencies)}")
        
        # Export manifest
        manifest = reconstructor.export_cache_manifest()
        manifest_file = cache_root / "cache_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        print(f"\nCache manifest exported to: {manifest_file}")
        
    except Exception as e:
        logging.error(f"Semantic reconstruction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
