"""
Test suite for semantic cache reconstruction and query operations

Tests embedding index, signature index, similarity search, and reconstruction
functionality for both Resume Engine (RG) and Outreach Engine (LIC) engines.
"""

import json
import math
import pytest
import tempfile
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project paths for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "schemas"))
sys.path.append(str(project_root / "runtime"))

from semantic_lineage import (
    EngineType, ASTSignature, FileSignature, FileExtension
)
from semantic_reconstruction import (
    EmbeddingIndex, SignatureIndex, SimilarityResult, ReconstructionQuery,
    SemanticReconstructor, OrphanReport
)


class TestEmbeddingIndex:
    """Test embedding index functionality"""
    
    def test_add_vector(self):
        """Test adding vectors to index"""
        index = EmbeddingIndex()
        
        vector1 = [0.1, 0.2, 0.3, 0.4]
        metadata1 = {"file": "test1.py", "engine": "RG"}
        
        vector2 = [0.5, 0.6, 0.7, 0.8]
        metadata2 = {"file": "test2.py", "engine": "LIC"}
        
        index.add_vector("hash1", vector1, metadata1)
        index.add_vector("hash2", vector2, metadata2)
        
        assert len(index.vectors) == 2
        assert index.dimension == 4
        assert index.vectors["hash1"] == vector1
        assert index.vectors["hash2"] == vector2
        assert index.metadata["hash1"] == metadata1
        assert index.metadata["hash2"] == metadata2
    
    def test_dimension_mismatch(self):
        """Test handling of dimension mismatches"""
        index = EmbeddingIndex()
        
        index.add_vector("hash1", [0.1, 0.2, 0.3], {"file": "test1.py"})
        
        # Adding vector with different dimension should raise error
        with pytest.raises(ValueError):
            index.add_vector("hash2", [0.4, 0.5], {"file": "test2.py"})
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        index = EmbeddingIndex()
        
        # Test identical vectors
        vec1 = [0.1, 0.2, 0.3, 0.4]
        similarity = index.cosine_similarity(vec1, vec1)
        assert math.isclose(similarity, 1.0, rel_tol=1e-9)
        
        # Test orthogonal vectors
        vec2 = [1.0, 0.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0, 0.0]
        similarity = index.cosine_similarity(vec2, vec3)
        assert math.isclose(similarity, 0.0, rel_tol=1e-9)
        
        # Test zero vectors
        vec4 = [0.0, 0.0, 0.0, 0.0]
        similarity = index.cosine_similarity(vec1, vec4)
        assert similarity == 0.0
    
    def test_search_similar(self):
        """Test similarity search"""
        index = EmbeddingIndex()
        
        # Add test vectors
        vectors = {
            "hash1": [0.1, 0.2, 0.3, 0.4],
            "hash2": [0.2, 0.3, 0.4, 0.5],  # Similar to hash1
            "hash3": [0.9, 0.8, 0.7, 0.6],  # Different from hash1
            "hash4": [0.1, 0.2, 0.3, 0.4]   # Identical to hash1
        }
        
        for hash_val, vector in vectors.items():
            index.add_vector(hash_val, vector, {"file": f"{hash_val}.py"})
        
        # Search for similar vectors to hash1
        query_vector = [0.1, 0.2, 0.3, 0.4]
        results = index.search_similar(query_vector, top_k=3, min_similarity=0.5)
        
        assert len(results) <= 3
        assert all(similarity >= 0.5 for _, similarity in results)
        
        # Results should be sorted by similarity (descending)
        similarities = [similarity for _, similarity in results]
        assert similarities == sorted(similarities, reverse=True)
        
        # hash4 should be first (identical), hash1 should be second (identical), hash2 should be third
        assert results[0][0] in ["hash1", "hash4"]  # Identical vectors
        assert results[1][0] in ["hash1", "hash4"]  # Identical vectors
    
    def test_get_metadata(self):
        """Test metadata retrieval"""
        index = EmbeddingIndex()
        
        metadata = {"file": "test.py", "engine": "RG", "version": "v10.7"}
        index.add_vector("test_hash", [0.1, 0.2, 0.3], metadata)
        
        retrieved = index.get_metadata("test_hash")
        assert retrieved == metadata
        
        # Non-existent hash should return None
        assert index.get_metadata("nonexistent") is None


class TestSignatureIndex:
    """Test signature index functionality"""
    
    def test_add_signature(self):
        """Test adding signatures to index"""
        index = SignatureIndex()
        
        # Create mock AST signature
        ast_signature = ASTSignature(
            signature=None,
            root_nodes=[],
            import_graph={"os": ["line_1"], "sys": ["line_2"]},
            function_signatures={"func1": "func1()", "func2": "func2(arg)"},
            class_signatures={"Class1": "class Class1"},
            complexity_metrics={}
        )
        
        file_path = Path("/test/file.py")
        index.add_signature("test_hash", ast_signature, file_path)
        
        # Check function indexing
        assert "test_hash" in index.function_signatures["func1"]
        assert "test_hash" in index.function_signatures["func2"]
        
        # Check class indexing
        assert "test_hash" in index.class_signatures["Class1"]
        
        # Check import indexing
        assert "test_hash" in index.import_signatures["os"]
        assert "test_hash" in index.import_signatures["sys"]
        
        # Check path indexing
        assert index.path_index[str(file_path)] == "test_hash"
    
    def test_find_by_function(self):
        """Test finding files by function name"""
        index = SignatureIndex()
        
        # Add multiple signatures
        for i in range(3):
            ast_signature = ASTSignature(
                signature=None,
                root_nodes=[],
                import_graph={},
                function_signatures={"main": f"main_v{i}()", f"func{i}": f"func{i}()"},
                class_signatures={},
                complexity_metrics={}
            )
            index.add_signature(f"hash{i}", ast_signature, Path(f"/test/file{i}.py"))
        
        # Find files with "main" function
        main_files = index.find_by_function("main")
        assert len(main_files) == 3
        assert all(hash_val.startswith("hash") for hash_val in main_files)
        
        # Find files with specific function
        func1_files = index.find_by_function("func1")
        assert len(func1_files) == 1
        assert "hash1" in func1_files
        
        # Non-existent function should return empty set
        empty_files = index.find_by_function("nonexistent")
        assert len(empty_files) == 0
    
    def test_find_by_class(self):
        """Test finding files by class name"""
        index = SignatureIndex()
        
        # Add signatures with classes
        ast_signature = ASTSignature(
            signature=None,
            root_nodes=[],
            import_graph={},
            function_signatures={},
            class_signatures={"Processor": "class Processor", "Helper": "class Helper"},
            complexity_metrics={}
        )
        index.add_signature("test_hash", ast_signature, Path("/test/file.py"))
        
        processor_files = index.find_by_class("Processor")
        assert len(processor_files) == 1
        assert "test_hash" in processor_files
        
        helper_files = index.find_by_class("Helper")
        assert len(helper_files) == 1
        assert "test_hash" in helper_files
    
    def test_find_by_import(self):
        """Test finding files by import name"""
        index = SignatureIndex()
        
        # Add signatures with imports
        ast_signature = ASTSignature(
            signature=None,
            root_nodes=[],
            import_graph={"os": ["line_1"], "json": ["line_2"], "requests": ["line_3"]},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        index.add_signature("test_hash", ast_signature, Path("/test/file.py"))
        
        os_files = index.find_by_import("os")
        assert len(os_files) == 1
        assert "test_hash" in os_files
        
        json_files = index.find_by_import("json")
        assert len(json_files) == 1
        assert "test_hash" in json_files
    
    def test_find_by_path(self):
        """Test finding files by path"""
        index = SignatureIndex()
        
        file_path = Path("/test/subdir/file.py")
        ast_signature = ASTSignature(
            signature=None,
            root_nodes=[],
            import_graph={},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        index.add_signature("test_hash", ast_signature, file_path)
        
        # Find by exact path
        found_hash = index.find_by_path(str(file_path))
        assert found_hash == "test_hash"
        
        # Non-existent path should return None
        assert index.find_by_path("/nonexistent/path.py") is None


class TestSimilarityResult:
    """Test similarity result functionality"""
    
    def test_similarity_result_creation(self):
        """Test creation of similarity results"""
        result = SimilarityResult(
            file_hash="test_hash",
            file_path=Path("/test/file.py"),
            engine=EngineType.RESUME_ENGINE,
            archive_version="v10.7",
            similarity_score=0.95,
            match_type="semantic"
        )
        
        assert result.file_hash == "test_hash"
        assert result.file_path == Path("/test/file.py")
        assert result.engine == EngineType.RESUME_ENGINE
        assert result.archive_version == "v10.7"
        assert result.similarity_score == 0.95
        assert result.match_type == "semantic"
    
    def test_similarity_result_serialization(self):
        """Test similarity result serialization"""
        result = SimilarityResult(
            file_hash="test_hash",
            file_path=Path("/test/file.py"),
            engine=EngineType.OUTREACH_ENGINE,
            archive_version="Agentic-LIC",
            similarity_score=0.87,
            match_type="exact"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["file_hash"] == "test_hash"
        assert result_dict["file_path"] == "/test/file.py"
        assert result_dict["engine"] == "LIC"
        assert result_dict["archive_version"] == "Agentic-LIC"
        assert result_dict["similarity_score"] == 0.87
        assert result_dict["match_type"] == "exact"


class TestReconstructionQuery:
    """Test reconstruction query functionality"""
    
    def test_query_creation(self):
        """Test creation of reconstruction queries"""
        query = ReconstructionQuery(
            query_type="similarity",
            query_params={"text": "data processing function"},
            engine_filter=EngineType.RESUME_ENGINE,
            version_filter="v10.7",
            max_results=5,
            min_similarity=0.7
        )
        
        assert query.query_type == "similarity"
        assert query.query_params["text"] == "data processing function"
        assert query.engine_filter == EngineType.RESUME_ENGINE
        assert query.version_filter == "v10.7"
        assert query.max_results == 5
        assert query.min_similarity == 0.7


class TestSemanticReconstructor:
    """Test semantic reconstructor functionality"""
    
    def create_mock_cache_structure(self, temp_dir: Path) -> Path:
        """Create mock semantic cache structure"""
        cache_root = temp_dir / "semantic_cache"
        cache_root.mkdir(parents=True)
        
        # Create resume engine structure
        rg_dir = cache_root / "resume_engine"
        rg_dir.mkdir()
        
        # Create version directories
        v10_7_dir = rg_dir / "v10.7"
        v10_7_dir.mkdir()
        
        # Create mock cache files
        self.create_mock_cache_entry(v10_7_dir, "file1_hash", "main.py", EngineType.RESUME_ENGINE)
        self.create_mock_cache_entry(v10_7_dir, "file2_hash", "utils.py", EngineType.RESUME_ENGINE)
        
        return cache_root
    
    def create_mock_cache_entry(self, version_dir: Path, file_hash: str, filename: str, engine: EngineType):
        """Create mock cache entry files"""
        # Create AST file
        ast_data = {
            "signature": {"file_path": str(version_dir / filename)},
            "root_nodes": [],
            "import_graph": {"os": ["line_1"], "json": ["line_2"]},
            "function_signatures": {"main": "main()", "process": "process(data)"},
            "class_signatures": {"Processor": "class Processor"},
            "complexity_metrics": {"cyclomatic_complexity": 3}
        }
        
        ast_file = version_dir / f"{file_hash}.ast"
        with open(ast_file, 'w') as f:
            json.dump(ast_data, f)
        
        # Create metadata file
        meta_data = {
            "file_path": str(version_dir / filename),
            "file_hash": file_hash,
            "size_bytes": 200,
            "last_modified": datetime.now().isoformat(),
            "engine": engine.value,
            "archive_version": version_dir.name,
            "file_extension": ".py"
        }
        
        meta_file = version_dir / f"{file_hash}.ast.meta.json"
        with open(meta_file, 'w') as f:
            json.dump(meta_data, f)
        
        # Create embedding file
        embedding_data = {
            "vector_hash": "embed_hash_" + file_hash,
            "embedding_model": "test_model",
            "vector_dimensions": 64,
            "embedding_data": [0.1 * i for i in range(64)],
            "confidence_score": 0.9,
            "semantic_tags": ["test", "mock"]
        }
        
        embed_file = version_dir / f"{file_hash}.embedding"
        with open(embed_file, 'w') as f:
            json.dump(embedding_data, f)
    
    def test_reconstructor_initialization(self):
        """Test reconstructor initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            assert reconstructor.cache_root == cache_root
            assert len(reconstructor.cache_entries) == 2
            assert len(reconstructor.embedding_index.vectors) == 2
            assert len(reconstructor.signature_index.function_signatures) > 0
    
    def test_query_semantic_similarity(self):
        """Test semantic similarity query"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            query = ReconstructionQuery(
                query_type="similarity",
                query_params={"text": "main function"},
                max_results=5,
                min_similarity=0.1  # Low threshold for testing
            )
            
            results = reconstructor.query_semantic_similarity("main function", query)
            
            assert len(results) <= 5
            assert all(isinstance(result, SimilarityResult) for result in results)
            assert all(result.similarity_score >= query.min_similarity for result in results)
    
    def test_query_by_signature(self):
        """Test signature-based query"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            # Query by function name
            query = ReconstructionQuery("signature", {}, max_results=10)
            results = reconstructor.query_by_signature(function_name="main", query=query)
            
            assert len(results) > 0
            assert all(result.match_type == "exact" for result in results)
            
            # Query by class name
            results = reconstructor.query_by_signature(class_name="Processor", query=query)
            assert len(results) > 0
            
            # Query by import
            results = reconstructor.query_by_signature(import_name="os", query=query)
            assert len(results) > 0
    
    def test_query_by_path(self):
        """Test path-based query"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            # Query by exact path (this would need the exact path from the cache)
            # For testing, we'll use a non-existent path
            query = ReconstructionQuery("path", {})
            result = reconstructor.query_by_path("/nonexistent/path.py", query)
            
            assert result is None
    
    def test_reconstruct_file_signature(self):
        """Test file signature reconstruction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            # Reconstruct signature for known hash
            signature = reconstructor.reconstruct_file_signature("file1_hash")
            
            assert signature is not None
            assert "file_signature" in signature
            assert "ast_signature" in signature
            assert "embedding" in signature
            assert "reconstruction_timestamp" in signature
            
            # Non-existent hash should return None
            signature = reconstructor.reconstruct_file_signature("nonexistent_hash")
            assert signature is None
    
    def test_detect_orphans(self):
        """Test orphan detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            orphan_report = reconstructor.detect_orphans()
            
            assert isinstance(orphan_report, OrphanReport)
            assert isinstance(orphan_report.orphaned_files, list)
            assert isinstance(orphan_report.unreferenced_hashes, list)
            assert isinstance(orphan_report.cleanup_recommendations, list)
    
    def test_get_cache_statistics(self):
        """Test cache statistics generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            stats = reconstructor.get_cache_statistics()
            
            assert "total_files" in stats
            assert "embedding_index_size" in stats
            assert "signature_index_stats" in stats
            assert "engine_distribution" in stats
            assert "version_distribution" in stats
            assert "file_type_distribution" in stats
            
            assert stats["total_files"] == 2
            assert stats["embedding_index_size"] == 2
            assert stats["engine_distribution"]["RG"] == 2
    
    def test_export_cache_manifest(self):
        """Test cache manifest export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = self.create_mock_cache_structure(temp_path)
            
            reconstructor = SemanticReconstructor(cache_root)
            
            manifest = reconstructor.export_cache_manifest()
            
            assert "export_timestamp" in manifest
            assert "cache_root" in manifest
            assert "statistics" in manifest
            assert "file_manifest" in manifest
            
            assert len(manifest["file_manifest"]) == 2
            assert all("file_hash" in file_info for file_info in manifest["file_manifest"])
            assert all("engine" in file_info for file_info in manifest["file_manifest"])


class TestOrphanReport:
    """Test orphan report functionality"""
    
    def test_orphan_report_creation(self):
        """Test creation of orphan reports"""
        report = OrphanReport(
            orphaned_files=["hash1", "hash2"],
            unreferenced_hashes=["hash3"],
            broken_lineage_chains=["file1.py"],
            missing_dependencies=["hash1: imports missing_module"],
            cleanup_recommendations=["Remove orphaned files", "Fix missing dependencies"]
        )
        
        assert len(report.orphaned_files) == 2
        assert len(report.unreferenced_hashes) == 1
        assert len(report.broken_lineage_chains) == 1
        assert len(report.missing_dependencies) == 1
        assert len(report.cleanup_recommendations) == 2
    
    def test_orphan_report_serialization(self):
        """Test orphan report serialization"""
        report = OrphanReport(
            orphaned_files=[],
            unreferenced_hashes=[],
            broken_lineage_chains=[],
            missing_dependencies=[],
            cleanup_recommendations=[]
        )
        
        report_dict = report.to_dict()
        
        assert "orphaned_files" in report_dict
        assert "unreferenced_hashes" in report_dict
        assert "broken_lineage_chains" in report_dict
        assert "missing_dependencies" in report_dict
        assert "cleanup_recommendations" in report_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
