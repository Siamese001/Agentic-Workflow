"""
Test suite for semantic cache lineage and merge operations

Tests lineage chain building, semantic diff generation, and cross-version analysis
for both Resume Engine (RG) and Outreach Engine (LIC) engines.
"""

import json
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
    EngineType, SemanticDiff, ASTSignature, FileSignature, FileExtension
)
from semantic_lineage_merge import (
    VersionInfo, SemanticDiffer, LineageChain, LineageMergeProcessor
)


class TestVersionInfo:
    """Test version parsing and ordering"""
    
    def test_numeric_version_parsing(self):
        """Test parsing of numeric versions"""
        test_cases = [
            ("v2", 2.0),
            ("v6.0", 6.0),
            ("v10.7", 10.7),
            ("v123.456", 123.456),
        ]
        
        for version_str, expected_number in test_cases:
            version_info = VersionInfo.from_string(version_str)
            assert version_info.version_string == version_str
            assert version_info.version_number == expected_number
            assert version_info.version_type == "numeric"
            assert version_info.sort_key[0] == 0  # Numeric versions have priority 0
    
    def test_semantic_version_parsing(self):
        """Test parsing of semantic versions"""
        test_cases = [
            ("10_11", 10.11),
            ("10_10", 10.10),
            ("9_0", 9.0),
            ("1_0", 1.0),
        ]
        
        for version_str, expected_number in test_cases:
            version_info = VersionInfo.from_string(version_str)
            assert version_info.version_string == version_str
            assert version_info.version_number == expected_number
            assert version_info.version_type == "semantic"
            assert version_info.sort_key[0] == 1  # Semantic versions have priority 1
    
    def test_named_version_parsing(self):
        """Test parsing of named versions"""
        test_cases = [
            ("Monolithic", 1),
            ("Monolith", 2),
            ("Agentic-Workflow-10_11", 9),
            ("Agentic LIC", 12),
        ]
        
        for version_str, expected_priority in test_cases:
            version_info = VersionInfo.from_string(version_str)
            assert version_info.version_string == version_str
            assert version_info.version_type == "named"
            assert version_info.sort_key[0] == 2  # Named versions have priority 2
            assert version_info.sort_key[1] == expected_priority
    
    def test_version_sorting(self):
        """Test chronological version sorting"""
        version_strings = [
            "v10.7", "v2", "Monolithic", "10_11", "v6.0", "Agentic-Workflow-10_11"
        ]
        
        version_infos = [VersionInfo.from_string(v) for v in version_strings]
        version_infos.sort(key=lambda v: v.sort_key)
        
        expected_order = ["v2", "v6.0", "v10.7", "10_11", "Monolithic", "Agentic-Workflow-10_11"]
        actual_order = [v.version_string for v in version_infos]
        
        assert actual_order == expected_order


class TestSemanticDiffer:
    """Test semantic diff generation"""
    
    def create_test_signature(self, functions: List[str], classes: List[str], imports: List[str]) -> ASTSignature:
        """Create test AST signature"""
        file_signature = FileSignature(
            file_path=Path("/test.py"),
            file_hash="test_hash",
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=FileExtension.PYTHON
        )
        
        return ASTSignature(
            signature=file_signature,
            root_nodes=[],
            import_graph={imp: ["line_1"] for imp in imports},
            function_signatures={func: f"{func}()" for func in functions},
            class_signatures={cls: f"class {cls}" for cls in classes},
            complexity_metrics={"cyclomatic_complexity": 1}
        )
    
    def test_function_addition_detection(self):
        """Test detection of added functions"""
        old_sig = self.create_test_signature(["func1"], [], [])
        new_sig = self.create_test_signature(["func1", "func2"], [], [])
        
        diff = SemanticDiffer.compare_ast_signatures(old_sig, new_sig)
        
        assert "func2" in diff.added_functions
        assert "func1" not in diff.added_functions
        assert len(diff.removed_functions) == 0
        assert len(diff.modified_functions) == 0
    
    def test_function_removal_detection(self):
        """Test detection of removed functions"""
        old_sig = self.create_test_signature(["func1", "func2"], [], [])
        new_sig = self.create_test_signature(["func1"], [], [])
        
        diff = SemanticDiffer.compare_ast_signatures(old_sig, new_sig)
        
        assert "func2" in diff.removed_functions
        assert "func1" not in diff.removed_functions
        assert len(diff.added_functions) == 0
        assert len(diff.modified_functions) == 0
    
    def test_function_modification_detection(self):
        """Test detection of modified functions"""
        old_sig = self.create_test_signature(["func1"], [], [])
        # Simulate function signature change
        new_sig = self.create_test_signature(["func1"], [], [])
        new_sig.function_signatures["func1"] = "func1(arg1)"  # Different signature
        
        diff = SemanticDiffer.compare_ast_signatures(old_sig, new_sig)
        
        assert "func1" in diff.modified_functions
        assert len(diff.added_functions) == 0
        assert len(diff.removed_functions) == 0
        assert "func1" in diff.signature_changes
    
    def test_import_change_detection(self):
        """Test detection of import changes"""
        old_sig = self.create_test_signature([], [], ["os", "sys"])
        new_sig = self.create_test_signature([], [], ["os", "json"])
        
        diff = SemanticDiffer.compare_ast_signatures(old_sig, new_sig)
        
        assert len(diff.behavior_changes) > 0
        assert any("import" in change.lower() for change in diff.behavior_changes)
    
    def test_api_drift_detection(self):
        """Test API drift detection"""
        old_sig = self.create_test_signature(["public_func", "_private_func"], [], [])
        new_sig = self.create_test_signature(["_private_func"], [], [])  # Removed public API
        
        api_drifts = SemanticDiffer.detect_api_drift(old_sig, new_sig)
        
        assert len(api_drifts) > 0
        assert any("public_func" in drift for drift in api_drifts)
        assert any("removed" in drift.lower() for drift in api_drifts)


class TestLineageChain:
    """Test lineage chain functionality"""
    
    def test_lineage_chain_creation(self):
        """Test creation of lineage chains"""
        versions = [("v2", "hash1"), ("v6.0", "hash2"), ("v10.7", "hash3")]
        
        chain = LineageChain(
            file_key="test_file.py",
            engine=EngineType.RESUME_ENGINE,
            versions=versions,
            completeness=1.0,
            gaps=[],
            current_hash="hash3"
        )
        
        assert chain.file_key == "test_file.py"
        assert chain.engine == EngineType.RESUME_ENGINE
        assert len(chain.versions) == 3
        assert chain.completeness == 1.0
        assert chain.current_hash == "hash3"
    
    def test_lineage_chain_with_gaps(self):
        """Test lineage chain with missing versions"""
        versions = [("v2", "hash1"), ("v10.7", "hash2")]  # Missing v6.0
        
        chain = LineageChain(
            file_key="test_file.py",
            engine=EngineType.RESUME_ENGINE,
            versions=versions,
            completeness=0.67,  # 2/3 versions present
            gaps=["v6.0"],
            current_hash="hash2"
        )
        
        assert chain.completeness == 0.67
        assert "v6.0" in chain.gaps
        assert len(chain.versions) == 2
    
    def test_lineage_chain_serialization(self):
        """Test lineage chain serialization to dict"""
        versions = [("v2", "hash1"), ("v6.0", "hash2")]
        
        chain = LineageChain(
            file_key="test_file.py",
            engine=EngineType.RESUME_ENGINE,
            versions=versions,
            completeness=1.0,
            gaps=[],
            current_hash="hash2"
        )
        
        chain_dict = chain.to_dict()
        
        assert chain_dict["file_key"] == "test_file.py"
        assert chain_dict["engine"] == "RG"
        assert chain_dict["versions"] == versions
        assert chain_dict["completeness"] == 1.0
        assert chain_dict["current_hash"] == "hash2"


class TestLineageMergeProcessor:
    """Test lineage merge processor functionality"""
    
    def create_mock_cache_structure(self, temp_dir: Path) -> Dict[str, Any]:
        """Create mock semantic cache structure for testing"""
        cache_root = temp_dir / "semantic_cache"
        cache_root.mkdir(parents=True)
        
        # Create resume engine structure
        rg_dir = cache_root / "resume_engine"
        rg_dir.mkdir()
        
        # Create version directories
        v2_dir = rg_dir / "v2"
        v2_dir.mkdir()
        
        v6_dir = rg_dir / "v6.0"
        v6_dir.mkdir()
        
        # Create mock cache files
        self.create_mock_cache_file(v2_dir, "file1_hash", "file1.py")
        self.create_mock_cache_file(v6_dir, "file2_hash", "file1.py")  # Same file, different version
        
        return {"cache_root": cache_root, "rg_dir": rg_dir}
    
    def create_mock_cache_file(self, version_dir: Path, file_hash: str, filename: str):
        """Create mock cache file"""
        # Create AST file
        ast_data = {
            "signature": {"file_path": str(version_dir / filename)},
            "root_nodes": [],
            "import_graph": {"os": ["line_1"]},
            "function_signatures": {"main": "main()"},
            "class_signatures": {},
            "complexity_metrics": {"cyclomatic_complexity": 1}
        }
        
        ast_file = version_dir / f"{file_hash}.ast"
        with open(ast_file, 'w') as f:
            json.dump(ast_data, f)
        
        # Create metadata file
        meta_data = {
            "file_path": str(version_dir / filename),
            "file_hash": file_hash,
            "size_bytes": 100,
            "last_modified": datetime.now().isoformat(),
            "engine": "RG",
            "archive_version": version_dir.name,
            "file_extension": ".py"
        }
        
        meta_file = version_dir / f"{file_hash}.ast.meta.json"
        with open(meta_file, 'w') as f:
            json.dump(meta_data, f)
        
        # Create embedding file
        embedding_data = {
            "vector_hash": "embed_hash",
            "embedding_model": "test_model",
            "vector_dimensions": 64,
            "embedding_data": [0.1] * 64,
            "confidence_score": 0.9,
            "semantic_tags": ["test"]
        }
        
        embed_file = version_dir / f"{file_hash}.embedding"
        with open(embed_file, 'w') as f:
            json.dump(embedding_data, f)
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_structure = self.create_mock_cache_structure(temp_path)
            
            processor = LineageMergeProcessor(mock_structure["cache_root"])
            
            assert processor.cache_root == mock_structure["cache_root"]
            assert processor.differ is not None
            assert processor.dependency_analyzer is not None
    
    def test_load_version_entries(self):
        """Test loading version entries"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_structure = self.create_mock_cache_structure(temp_path)
            
            processor = LineageMergeProcessor(mock_structure["cache_root"])
            
            v2_dir = mock_structure["rg_dir"] / "v2"
            entries = processor._load_version_entries(v2_dir)
            
            assert len(entries) == 1
            assert "file1_hash" in entries
            assert entries["file1_hash"]["file_signature"].file_hash == "file1_hash"
    
    def test_build_lineage_chains(self):
        """Test building lineage chains"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_structure = self.create_mock_cache_structure(temp_path)
            
            processor = LineageMergeProcessor(mock_structure["cache_root"])
            
            # Create version entries with valid FileSignature objects
            from semantic_lineage import FileSignature, EngineType, FileExtension
            from datetime import datetime
            
            version_entries = {
                "v2": {
                    "file1_hash": {
                        "file_signature": FileSignature(
                            file_path=Path("/test/file1.py"),
                            file_hash="file1_hash",
                            size_bytes=100,
                            last_modified=datetime.now(),
                            engine=EngineType.RESUME_ENGINE,
                            archive_version="v2",
                            file_extension=FileExtension.PYTHON
                        ),
                        "ast_data": {},
                        "embedding_data": {}
                    }
                },
                "v6.0": {
                    "file2_hash": {
                        "file_signature": FileSignature(
                            file_path=Path("/test/file1.py"),  # Same file path for lineage tracking
                            file_hash="file2_hash",
                            size_bytes=200,
                            last_modified=datetime.now(),
                            engine=EngineType.RESUME_ENGINE,
                            archive_version="v6.0",
                            file_extension=FileExtension.PYTHON
                        ),
                        "ast_data": {},
                        "embedding_data": {}
                    }
                }
            }
            
            chains = processor._build_lineage_chains(version_entries, EngineType.RESUME_ENGINE)
            
            assert len(chains) == 1
            chain = chains[0]
            assert chain.engine == EngineType.RESUME_ENGINE
            assert len(chain.versions) == 2
    
    def test_generate_semantic_diffs(self):
        """Test semantic diff generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_structure = self.create_mock_cache_structure(temp_path)
            
            processor = LineageMergeProcessor(mock_structure["cache_root"])
            
            # Create version entries with different content
            version_entries = {
                "v2": {"file1_hash": {"file_signature": None, "ast_data": {}, "embedding_data": {}}},
                "v6.0": {"file2_hash": {"file_signature": None, "ast_data": {}, "embedding_data": {}}}
            }
            
            diffs = processor._generate_semantic_diffs(version_entries, EngineType.RESUME_ENGINE)
            
            assert "v2_to_v6.0" in diffs
            assert "summary" in diffs["v2_to_v6.0"]
    
    def test_save_lineage_results(self):
        """Test saving lineage results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_structure = self.create_mock_cache_structure(temp_path)
            
            processor = LineageMergeProcessor(mock_structure["cache_root"])
            
            results = {
                "resume_engine": {"test": "data"},
                "outreach_engine": {"test": "data"},
                "processing_timestamp": datetime.now().isoformat()
            }
            
            output_file = processor.save_lineage_results(results)
            
            assert output_file.exists()
            assert output_file.parent.name == "lineage_results"
            
            # Verify saved content
            with open(output_file, 'r') as f:
                saved_data = json.load(f)
            
            assert "resume_engine" in saved_data
            assert "outreach_engine" in saved_data


class TestDependencyAnalyzer:
    """Test dependency analysis functionality"""
    
    def test_build_dependency_graph(self):
        """Test building dependency graph"""
        from semantic_lineage_merge import DependencyAnalyzer
        
        # Create mock signatures
        signatures = {
            "file1.py": ASTSignature(
                signature=None,
                root_nodes=[],
                import_graph={"os": ["line_1"], "sys": ["line_2"]},
                function_signatures={},
                class_signatures={},
                complexity_metrics={}
            ),
            "file2.py": ASTSignature(
                signature=None,
                root_nodes=[],
                import_graph={"json": ["line_1"], "os": ["line_3"]},
                function_signatures={},
                class_signatures={},
                complexity_metrics={}
            )
        }
        
        graph = DependencyAnalyzer.build_dependency_graph(signatures)
        
        assert "file1.py" in graph
        assert "file2.py" in graph
        assert "os" in graph["file1.py"]
        assert "sys" in graph["file1.py"]
        assert "json" in graph["file2.py"]
        assert "os" in graph["file2.py"]
    
    def test_detect_dependency_changes(self):
        """Test detection of dependency changes"""
        from semantic_lineage_merge import DependencyAnalyzer
        
        old_graph = {
            "file1.py": {"os", "sys"},
            "file2.py": {"json"}
        }
        
        new_graph = {
            "file1.py": {"os", "requests"},  # sys removed, requests added
            "file2.py": {"json", "yaml"}      # yaml added
        }
        
        changes = DependencyAnalyzer.detect_dependency_changes(old_graph, new_graph)
        
        assert len(changes) > 0
        assert any("sys" in change and "removed" in change for change in changes)
        assert any("requests" in change and "added" in change for change in changes)
        assert any("yaml" in change and "added" in change for change in changes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
