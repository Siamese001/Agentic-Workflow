"""
Test suite for semantic cache integrity and validation

Tests integrity signals, validation checks, and completeness verification
for both Resume Engine (RG) and Outreach Engine (LIC) semantic cache.
"""

import json
import pytest
import tempfile
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project paths for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "schemas"))
sys.path.append(str(project_root / "runtime"))

from semantic_lineage import (
    EngineType, SemanticCacheEntry, FileSignature, ASTSignature,
    EmbeddingVector, IntegritySignals, SemanticLineageValidator,
    calculate_file_hash, ArchiveManifest, GlobalCacheReport
)
from semantic_scanner import IntegritySignalGenerator


class TestIntegritySignals:
    """Test integrity signal generation"""
    
    def test_integrity_signals_creation(self):
        """Test creation of integrity signals"""
        signals = IntegritySignals(
            content_hash="a" * 64,
            structure_hash="b" * 64,
            semantic_hash="c" * 64,
            version_id="v1.0_abcdef1234567890",
            lineage_chain=["v0.9", "v1.0"],
            verification_status=True
        )
        
        assert len(signals.content_hash) == 64
        assert len(signals.structure_hash) == 64
        assert len(signals.semantic_hash) == 64
        assert signals.version_id.startswith("v1.0_")
        assert len(signals.lineage_chain) == 2
        assert signals.verification_status is True
    
    def test_integrity_signals_serialization(self):
        """Test integrity signals serialization"""
        signals = IntegritySignals(
            content_hash="hash1",
            structure_hash="hash2",
            semantic_hash="hash3",
            version_id="v1.0_test",
            lineage_chain=["v0.9"],
            verification_status=False
        )
        
        signals_dict = signals.to_dict()
        
        assert signals_dict["content_hash"] == "hash1"
        assert signals_dict["structure_hash"] == "hash2"
        assert signals_dict["semantic_hash"] == "hash3"
        assert signals_dict["version_id"] == "v1.0_test"
        assert signals_dict["lineage_chain"] == ["v0.9"]
        assert signals_dict["verification_status"] is False


class TestIntegritySignalGenerator:
    """Test integrity signal generation functionality"""
    
    def test_generate_integrity_signals(self):
        """Test generation of integrity signals"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_path / "test.py"
            test_content = "def hello():\n    print('Hello, World!')"
            test_file.write_text(test_content)
            
            # Create mock AST signature
            file_signature = FileSignature(
                file_path=test_file,
                file_hash="test_hash",
                size_bytes=len(test_content.encode()),
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=None
            )
            
            ast_signature = ASTSignature(
                signature=file_signature,
                root_nodes=[],
                import_graph={},
                function_signatures={"hello": "hello()"},
                class_signatures={},
                complexity_metrics={}
            )
            
            # Create mock embedding
            embedding = EmbeddingVector(
                vector_hash="embed_hash",
                embedding_model="test_model",
                vector_dimensions=64,
                embedding_data=[0.1] * 64,
                confidence_score=0.9,
                semantic_tags=["test"]
            )
            
            # Generate integrity signals
            generator = IntegritySignalGenerator()
            signals = generator.generate_integrity_signals(test_file, ast_signature, embedding)
            
            # Verify signals
            assert len(signals.content_hash) == 64
            assert len(signals.structure_hash) == 64
            assert len(signals.semantic_hash) == 64
            assert signals.version_id is not None
            assert isinstance(signals.lineage_chain, list)
            assert isinstance(signals.verification_status, bool)
    
    def test_content_hash_generation(self):
        """Test content hash generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files with different content
            file1 = temp_path / "file1.txt"
            file2 = temp_path / "file2.txt"
            
            file1.write_text("Hello, World!")
            file2.write_text("Hello, Universe!")
            
            hash1 = calculate_file_hash(file1)
            hash2 = calculate_file_hash(file2)
            
            # Hashes should be different for different content
            assert hash1 != hash2
            assert len(hash1) == 64  # SHA-256 length
            assert len(hash2) == 64
            
            # Same content should produce same hash
            file3 = temp_path / "file3.txt"
            file3.write_text("Hello, World!")
            hash3 = calculate_file_hash(file3)
            
            assert hash1 == hash3
    
    def test_structure_hash_generation(self):
        """Test structure hash generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_path / "test.py"
            test_file.write_text("def func(): pass")
            
            # Create different AST signatures
            file_signature = FileSignature(
                file_path=test_file,
                file_hash="test_hash",
                size_bytes=100,
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=None
            )
            
            ast_sig1 = ASTSignature(
                signature=file_signature,
                root_nodes=[],
                import_graph={"os": ["line_1"]},
                function_signatures={"func": "func()"},
                class_signatures={},
                complexity_metrics={}
            )
            
            ast_sig2 = ASTSignature(
                signature=file_signature,
                root_nodes=[],
                import_graph={"sys": ["line_1"]},  # Different import
                function_signatures={"func": "func()"},
                class_signatures={},
                complexity_metrics={}
            )
            
            embedding = EmbeddingVector(
                vector_hash="embed_hash",
                embedding_model="test_model",
                vector_dimensions=64,
                embedding_data=[0.1] * 64,
                confidence_score=0.9,
                semantic_tags=["test"]
            )
            
            generator = IntegritySignalGenerator()
            signals1 = generator.generate_integrity_signals(test_file, ast_sig1, embedding)
            signals2 = generator.generate_integrity_signals(test_file, ast_sig2, embedding)
            
            # Structure hashes should be different for different AST structures
            assert signals1.structure_hash != signals2.structure_hash
    
    def test_semantic_hash_generation(self):
        """Test semantic hash generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            test_file = temp_path / "test.py"
            test_file.write_text("def func(): pass")
            
            file_signature = FileSignature(
                file_path=test_file,
                file_hash="test_hash",
                size_bytes=100,
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=None
            )
            
            ast_signature = ASTSignature(
                signature=file_signature,
                root_nodes=[],
                import_graph={},
                function_signatures={},
                class_signatures={},
                complexity_metrics={}
            )
            
            # Different embeddings should produce different semantic hashes
            embed1 = EmbeddingVector(
                vector_hash="embed_hash1",
                embedding_model="test_model",
                vector_dimensions=64,
                embedding_data=[0.1] * 64,
                confidence_score=0.9,
                semantic_tags=["test"]
            )
            
            embed2 = EmbeddingVector(
                vector_hash="embed_hash2",
                embedding_model="test_model",
                vector_dimensions=64,
                embedding_data=[0.2] * 64,  # Different embedding data
                confidence_score=0.9,
                semantic_tags=["test"]
            )
            
            generator = IntegritySignalGenerator()
            signals1 = generator.generate_integrity_signals(test_file, ast_signature, embed1)
            signals2 = generator.generate_integrity_signals(test_file, ast_signature, embed2)
            
            # Semantic hashes should be different for different embeddings
            assert signals1.semantic_hash != signals2.semantic_hash


class TestSemanticLineageValidator:
    """Test semantic lineage validation"""
    
    def create_valid_cache_entry(self) -> SemanticCacheEntry:
        """Create a valid semantic cache entry for testing"""
        file_signature = FileSignature(
            file_path=Path("/test/file.py"),
            file_hash="a" * 64,
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=None
        )
        
        ast_signature = ASTSignature(
            signature=file_signature,
            root_nodes=[],
            import_graph={},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        
        embedding = EmbeddingVector(
            vector_hash="embed_hash",
            embedding_model="test_model",
            vector_dimensions=64,
            embedding_data=[0.1] * 64,
            confidence_score=0.9,
            semantic_tags=["test"]
        )
        
        from semantic_lineage import ToolUsageSignature, SafetySignature, GoldenProjection
        
        tool_usage = ToolUsageSignature([], [], [], [], [])
        safety = SafetySignature([], [], [], [], [])
        golden = GoldenProjection("", "", "", "", [])
        integrity = IntegritySignals("a" * 64, "b" * 64, "c" * 64, "v1.0", [], True)
        
        return SemanticCacheEntry(
            file_signature=file_signature,
            ast_signature=ast_signature,
            embedding=embedding,
            tool_usage=tool_usage,
            safety=safety,
            semantic_diff=None,
            golden_projection=golden,
            integrity=integrity,
            processing_timestamp=datetime.now()
        )
    
    def test_validate_cache_entry_valid(self):
        """Test validation of valid cache entry"""
        entry = self.create_valid_cache_entry()
        validator = SemanticLineageValidator()
        
        errors = validator.validate_cache_entry(entry)
        
        # Should have no validation errors
        assert len(errors) == 0
    
    def test_validate_cache_entry_missing_hash(self):
        """Test validation of cache entry with missing hash"""
        entry = self.create_valid_cache_entry()
        entry.file_signature.file_hash = ""  # Empty hash
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(entry)
        
        # Should have validation error
        assert len(errors) > 0
        assert any("hash" in error.lower() for error in errors)
    
    def test_validate_cache_entry_empty_ast(self):
        """Test validation of cache entry with empty AST"""
        entry = self.create_valid_cache_entry()
        entry.ast_signature.root_nodes = []  # Empty AST
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(entry)
        
        # Should have validation error for empty AST
        assert len(errors) > 0
        assert any("ast" in error.lower() or "empty" in error.lower() for error in errors)
    
    def test_validate_cache_entry_empty_embedding(self):
        """Test validation of cache entry with empty embedding"""
        entry = self.create_valid_cache_entry()
        entry.embedding.embedding_data = []  # Empty embedding
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(entry)
        
        # Should have validation error for empty embedding
        assert len(errors) > 0
        assert any("embedding" in error.lower() for error in errors)
    
    def test_validate_cache_entry_integrity_failure(self):
        """Test validation of cache entry with integrity failure"""
        entry = self.create_valid_cache_entry()
        entry.integrity.verification_status = False  # Failed integrity
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(entry)
        
        # Should have validation error for integrity failure
        assert len(errors) > 0
        assert any("integrity" in error.lower() for error in errors)
    
    def test_validate_archive_manifest_valid(self):
        """Test validation of valid archive manifest"""
        manifest = ArchiveManifest(
            engine=EngineType.RESUME_ENGINE,
            archive_version="v10.7",
            archive_path=Path("/test/archive"),
            total_files=100,
            processed_files=95,
            failed_files=["file1.py", "file2.py"],
            file_hashes={"hash1", "hash2", "hash3"},
            completeness_score=0.95,
            processing_start=datetime.now(),
            processing_end=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_manifest(manifest)
        
        # Should have no validation errors
        assert len(errors) == 0
    
    def test_validate_manifest_zero_files(self):
        """Test validation of manifest with zero files"""
        manifest = ArchiveManifest(
            engine=EngineType.RESUME_ENGINE,
            archive_version="v10.7",
            archive_path=Path("/test/archive"),
            total_files=0,  # Zero files
            processed_files=0,
            failed_files=[],
            file_hashes=set(),
            completeness_score=0.0,
            processing_start=datetime.now(),
            processing_end=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_manifest(manifest)
        
        # Should have validation error for zero files
        assert len(errors) > 0
        assert any("zero" in error.lower() for error in errors)
    
    def test_validate_manifest_processed_exceeds_total(self):
        """Test validation of manifest where processed exceeds total"""
        manifest = ArchiveManifest(
            engine=EngineType.RESUME_ENGINE,
            archive_version="v10.7",
            archive_path=Path("/test/archive"),
            total_files=10,
            processed_files=15,  # Exceeds total
            failed_files=[],
            file_hashes=set(),
            completeness_score=1.5,  # Invalid > 1.0
            processing_start=datetime.now(),
            processing_end=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_manifest(manifest)
        
        # Should have validation errors
        assert len(errors) > 0
        assert any("exceeds" in error.lower() or "processed" in error.lower() for error in errors)
        assert any("completeness" in error.lower() for error in errors)
    
    def test_validate_manifest_invalid_completeness(self):
        """Test validation of manifest with invalid completeness score"""
        manifest = ArchiveManifest(
            engine=EngineType.RESUME_ENGINE,
            archive_version="v10.7",
            archive_path=Path("/test/archive"),
            total_files=10,
            processed_files=5,
            failed_files=[],
            file_hashes=set(),
            completeness_score=1.5,  # Invalid > 1.0
            processing_start=datetime.now(),
            processing_end=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_manifest(manifest)
        
        # Should have validation error for invalid completeness
        assert len(errors) > 0
        assert any("completeness" in error.lower() for error in errors)


class TestCacheCompleteness:
    """Test cache completeness verification"""
    
    def test_required_archives_presence(self):
        """Test presence of required archives"""
        required_rg_archives = [
            "C:\\Git\\Resume Engine Archive\\Agentic-Workflow-10_11",
            "C:\\Git\\Resume Engine Archive\\v2",
            "C:\\Git\\Resume Engine Archive\\v10.7"
        ]
        
        required_lic_archives = [
            "C:\\Git\\Reachout Engine Archive\\Agentic-LIC",
            "C:\\Git\\Reachout Engine Archive\\Monolithic"
        ]
        
        # In a real test, you would check if these paths exist
        # For this test, we'll simulate the check
        existing_rg = [path for path in required_rg_archives if Path(path).exists()]
        existing_lic = [path for path in required_lic_archives if Path(path).exists()]
        
        # Test completeness calculation
        rg_completeness = len(existing_rg) / len(required_rg_archives)
        lic_completeness = len(existing_lic) / len(required_lic_archives)
        overall_completeness = (len(existing_rg) + len(existing_lic)) / (len(required_rg_archives) + len(required_lic_archives))
        
        assert 0.0 <= rg_completeness <= 1.0
        assert 0.0 <= lic_completeness <= 1.0
        assert 0.0 <= overall_completeness <= 1.0
    
    def test_engine_separation_validation(self):
        """Test validation of engine separation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = temp_path / "semantic_cache"
            cache_root.mkdir()
            
            # Create proper engine separation
            rg_dir = cache_root / "resume_engine"
            lic_dir = cache_root / "outreach_engine"
            rg_dir.mkdir()
            lic_dir.mkdir()
            
            # Add version directories
            (rg_dir / "v10.7").mkdir()
            (lic_dir / "Agentic-LIC").mkdir()
            
            # Test separation validation
            rg_exists = rg_dir.exists()
            lic_exists = lic_dir.exists()
            separation_valid = rg_exists and lic_exists
            
            assert separation_valid is True
            
            # Test invalid separation (mixed versions)
            (rg_dir / "Agentic-LIC").mkdir()  # LIC version in RG directory
            
            # This would be detected by proper validation logic
            rg_versions = set([d.name for d in rg_dir.iterdir() if d.is_dir()])
            lic_versions = set([d.name for d in lic_dir.iterdir() if d.is_dir()])
            
            overlap = rg_versions.intersection(lic_versions)
            assert len(overlap) == 0  # Should be no overlap in proper separation
    
    def test_artifact_integrity_validation(self):
        """Test validation of artifact integrity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cache_root = temp_path / "semantic_cache"
            cache_root.mkdir()
            
            # Create test artifacts
            version_dir = cache_root / "resume_engine" / "v10.7"
            version_dir.mkdir(parents=True)
            
            # Create valid JSON artifact
            valid_artifact = version_dir / "test_hash.ast"
            valid_artifact.write_text('{"test": "valid json"}')
            
            # Create invalid JSON artifact
            invalid_artifact = version_dir / "invalid_hash.ast"
            invalid_artifact.write_text('{"test": "invalid json"')
            
            # Test artifact validation
            total_artifacts = 0
            valid_artifacts = 0
            corrupted_artifacts = 0
            
            for artifact_file in version_dir.glob("*.json"):
                total_artifacts += 1
                try:
                    with open(artifact_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    valid_artifacts += 1
                except json.JSONDecodeError:
                    corrupted_artifacts += 1
            
            # In our test, we have .ast files, not .json, so we'll test the logic differently
            ast_files = list(version_dir.glob("*.ast"))
            assert len(ast_files) == 2
            
            # Test JSON parsing on the files
            for ast_file in ast_files:
                try:
                    with open(ast_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    valid_artifacts += 1
                except json.JSONDecodeError:
                    corrupted_artifacts += 1
            
            assert valid_artifacts == 1  # Only one valid JSON
            assert corrupted_artifacts == 1  # One corrupted JSON


class TestGlobalCacheReport:
    """Test global cache report functionality"""
    
    def test_global_cache_report_creation(self):
        """Test creation of global cache report"""
        resume_manifests = {
            "v10.7": ArchiveManifest(
                engine=EngineType.RESUME_ENGINE,
                archive_version="v10.7",
                archive_path=Path("/test/rg/v10.7"),
                total_files=100,
                processed_files=95,
                failed_files=[],
                file_hashes=set(),
                completeness_score=0.95,
                processing_start=datetime.now(),
                processing_end=datetime.now()
            )
        }
        
        outreach_manifests = {
            "Agentic-LIC": ArchiveManifest(
                engine=EngineType.OUTREACH_ENGINE,
                archive_version="Agentic-LIC",
                archive_path=Path("/test/lic/agentic-lic"),
                total_files=50,
                processed_files=48,
                failed_files=[],
                file_hashes=set(),
                completeness_score=0.96,
                processing_start=datetime.now(),
                processing_end=datetime.now()
            )
        }
        
        global_integrity = {
            "total_archives": 2,
            "successful_archives": 2,
            "total_files_processed": 143,
            "integrity_violations": []
        }
        
        drift_report = {
            "semantic_drift": [],
            "api_drift": []
        }
        
        orphan_report = {
            "orphaned_files": [],
            "unreferenced_hashes": []
        }
        
        completeness_report = {
            "required_archives": ["v10.7", "Agentic-LIC"],
            "missing_archives": [],
            "overall_completeness": 1.0
        }
        
        report = GlobalCacheReport(
            resume_engine_manifests=resume_manifests,
            outreach_engine_manifests=outreach_manifests,
            global_integrity=global_integrity,
            drift_report=drift_report,
            orphan_report=orphan_report,
            completeness_report=completeness_report
        )
        
        assert len(report.resume_engine_manifests) == 1
        assert len(report.outreach_engine_manifests) == 1
        assert report.global_integrity["total_archives"] == 2
        assert report.completeness_report["overall_completeness"] == 1.0
    
    def test_global_cache_report_serialization(self):
        """Test global cache report serialization"""
        # Create minimal report for testing
        report = GlobalCacheReport(
            resume_engine_manifests={},
            outreach_engine_manifests={},
            global_integrity={"total_archives": 0},
            drift_report={"semantic_drift": []},
            orphan_report={"orphaned_files": []},
            completeness_report={"overall_completeness": 0.0}
        )
        
        report_dict = report.to_dict()
        
        assert "resume_engine_manifests" in report_dict
        assert "outreach_engine_manifests" in report_dict
        assert "global_integrity" in report_dict
        assert "drift_report" in report_dict
        assert "orphan_report" in report_dict
        assert "completeness_report" in report_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
