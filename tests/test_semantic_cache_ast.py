"""
Test suite for semantic cache AST extraction and validation

Tests AST extraction, signature generation, and validation components
for both Resume Engine (RG) and Outreach Engine (LIC) semantic processing.
"""

import ast
import json
import pytest
import tempfile
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project paths for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "schemas"))
sys.path.append(str(project_root / "runtime"))

from semantic_lineage import (
    EngineType, ResponsibilityLevel, FileExtension, FileSignature,
    ASTNode, ASTSignature, SemanticCacheEntry, SemanticLineageValidator
)
from semantic_scanner import ASTExtractor


class TestASTExtractor:
    """Test AST extraction functionality"""
    
    def test_extract_simple_function_signature(self):
        """Test extraction of simple function signature"""
        python_code = '''
def hello_world():
    """Simple hello function"""
    print("Hello, World!")
    return "done"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = Path(f.name)
        
        try:
            file_signature = FileSignature(
                file_path=temp_path,
                file_hash="test_hash",
                size_bytes=len(python_code.encode()),
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=FileExtension.PYTHON
            )
            
            ast_signature = ASTExtractor.extract_ast_signature(temp_path, file_signature)
            
            assert ast_signature.signature == file_signature
            assert len(ast_signature.function_signatures) == 1
            assert "hello_world" in ast_signature.function_signatures
            assert len(ast_signature.root_nodes) == 1
            
            # Check function node
            func_node = ast_signature.root_nodes[0]
            assert func_node.node_type == "function"
            assert func_node.name == "hello_world"
            assert func_node.docstring == "Simple hello function"
            assert func_node.responsibility_level == ResponsibilityLevel.L5_UTILITY
            
        finally:
            temp_path.unlink()
    
    def test_extract_class_signature(self):
        """Test extraction of class signature"""
        python_code = '''
class DataProcessor:
    """Processes data efficiently"""
    
    def __init__(self, config):
        self.config = config
    
    def process(self, data):
        return self.transform(data)
    
    def transform(self, data):
        return data.upper()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = Path(f.name)
        
        try:
            file_signature = FileSignature(
                file_path=temp_path,
                file_hash="test_hash",
                size_bytes=len(python_code.encode()),
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=FileExtension.PYTHON
            )
            
            ast_signature = ASTExtractor.extract_ast_signature(temp_path, file_signature)
            
            assert len(ast_signature.class_signatures) == 1
            assert "DataProcessor" in ast_signature.class_signatures
            assert len(ast_signature.function_signatures) == 3  # __init__, process, transform
            
            # Check class node
            class_node = None
            for node in ast_signature.root_nodes:
                if node.node_type == "class" and node.name == "DataProcessor":
                    class_node = node
                    break
            
            assert class_node is not None
            assert class_node.docstring == "Processes data efficiently"
            assert class_node.responsibility_level == ResponsibilityLevel.L2_COMPONENT
            
        finally:
            temp_path.unlink()
    
    def test_extract_import_graph(self):
        """Test extraction of import graph"""
        python_code = '''
import os
import sys
from pathlib import Path
from typing import Dict, List
import requests
from collections import defaultdict

def main():
    path = Path("/tmp")
    return os.listdir(path)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = Path(f.name)
        
        try:
            file_signature = FileSignature(
                file_path=temp_path,
                file_hash="test_hash",
                size_bytes=len(python_code.encode()),
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=FileExtension.PYTHON
            )
            
            ast_signature = ASTExtractor.extract_ast_signature(temp_path, file_signature)
            
            # Check import graph
            assert "os" in ast_signature.import_graph
            assert "sys" in ast_signature.import_graph
            assert "pathlib" in ast_signature.import_graph
            assert "typing" in ast_signature.import_graph
            assert "requests" in ast_signature.import_graph
            assert "collections" in ast_signature.import_graph
            
        finally:
            temp_path.unlink()
    
    def test_calculate_complexity_metrics(self):
        """Test complexity calculation"""
        python_code = '''
def complex_function(data):
    if data:
        for item in data:
            if item > 0:
                try:
                    result = process_item(item)
                    if result:
                        return result
                except Exception:
                    pass
    return None

def process_item(item):
    return item * 2
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = Path(f.name)
        
        try:
            file_signature = FileSignature(
                file_path=temp_path,
                file_hash="test_hash",
                size_bytes=len(python_code.encode()),
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=FileExtension.PYTHON
            )
            
            ast_signature = ASTExtractor.extract_ast_signature(temp_path, file_signature)
            
            complexity = ast_signature.complexity_metrics
            assert "cyclomatic_complexity" in complexity
            assert "cognitive_complexity" in complexity
            assert complexity["cyclomatic_complexity"] > 1  # Should be > 1 due to if/for/try
            
        finally:
            temp_path.unlink()
    
    def test_responsibility_level_detection(self):
        """Test responsibility level detection"""
        test_cases = [
            ("core_engine", ResponsibilityLevel.L1_CORE),
            ("MainComponent", ResponsibilityLevel.L1_CORE),
            ("data_service", ResponsibilityLevel.L2_COMPONENT),
            ("api_handler", ResponsibilityLevel.L3_INTERFACE),
            ("data_processor_impl", ResponsibilityLevel.L4_IMPLEMENTATION),
            ("helper_function", ResponsibilityLevel.L5_UTILITY),
            ("random_name", ResponsibilityLevel.L5_UTILITY),
        ]
        
        python_template = '''
def {}():
    pass
'''
        
        for func_name, expected_level in test_cases:
            python_code = python_template.format(func_name)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(python_code)
                temp_path = Path(f.name)
            
            try:
                file_signature = FileSignature(
                    file_path=temp_path,
                    file_hash="test_hash",
                    size_bytes=len(python_code.encode()),
                    last_modified=datetime.now(),
                    engine=EngineType.RESUME_ENGINE,
                    archive_version="test_version",
                    file_extension=FileExtension.PYTHON
                )
                
                ast_signature = ASTExtractor.extract_ast_signature(temp_path, file_signature)
                
                if ast_signature.root_nodes:
                    func_node = ast_signature.root_nodes[0]
                    assert func_node.responsibility_level == expected_level, f"Failed for {func_name}"
                
            finally:
                temp_path.unlink()
    
    def test_handle_syntax_error(self):
        """Test handling of syntax errors"""
        invalid_python = '''
def broken_function(
    # Missing closing parenthesis
    print("This will cause syntax error")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(invalid_python)
            temp_path = Path(f.name)
        
        try:
            file_signature = FileSignature(
                file_path=temp_path,
                file_hash="test_hash",
                size_bytes=len(invalid_python.encode()),
                last_modified=datetime.now(),
                engine=EngineType.RESUME_ENGINE,
                archive_version="test_version",
                file_extension=FileExtension.PYTHON
            )
            
            ast_signature = ASTExtractor.extract_ast_signature(temp_path, file_signature)
            
            # Should handle syntax error gracefully
            assert ast_signature.signature == file_signature
            assert len(ast_signature.root_nodes) == 0
            assert "error" in ast_signature.complexity_metrics
            assert ast_signature.complexity_metrics["error"] == "syntax_error"
            
        finally:
            temp_path.unlink()


class TestASTSignatureValidation:
    """Test AST signature validation"""
    
    def test_valid_ast_signature(self):
        """Test validation of valid AST signature"""
        file_signature = FileSignature(
            file_path=Path("/test/path.py"),
            file_hash="a" * 64,  # Valid SHA-256 hash
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=FileExtension.PYTHON
        )
        
        ast_signature = ASTSignature(
            signature=file_signature,
            root_nodes=[
                ASTNode(
                    node_type="function",
                    name="test_func",
                    line_number=1,
                    docstring="Test function",
                    imports=[],
                    dependencies=[],
                    responsibility_level=ResponsibilityLevel.L5_UTILITY,
                    children=[]
                )
            ],
            import_graph={"os": ["line_1"]},
            function_signatures={"test_func": "test_func()"},
            class_signatures={},
            complexity_metrics={"cyclomatic_complexity": 1}
        )
        
        from semantic_lineage import ToolUsageSignature, SafetySignature, GoldenProjection, IntegritySignals
        
        # Create a complete cache entry for validation
        tool_usage = ToolUsageSignature([], [], [], [], [])
        safety = SafetySignature([], [], [], [], [])
        golden = GoldenProjection("", "", "", "", [])
        integrity = IntegritySignals("a" * 64, "b" * 64, "c" * 64, "v1.0", [], True)
        
        cache_entry = SemanticCacheEntry(
            file_signature=file_signature,
            ast_signature=ast_signature,
            embedding=None,  # Not needed for this test
            tool_usage=tool_usage,
            safety=safety,
            semantic_diff=None,
            golden_projection=golden,
            integrity=integrity,
            processing_timestamp=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(cache_entry)
        
        # Should have no validation errors
        assert len(errors) == 0
    
    def test_invalid_ast_signature_missing_hash(self):
        """Test validation of AST signature with missing hash"""
        file_signature = FileSignature(
            file_path=Path("/test/path.py"),
            file_hash="",  # Empty hash - invalid
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=FileExtension.PYTHON
        )
        
        ast_signature = ASTSignature(
            signature=file_signature,
            root_nodes=[],
            import_graph={},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        
        from semantic_lineage import ToolUsageSignature, SafetySignature, GoldenProjection, IntegritySignals
        
        # Create a complete cache entry for validation
        tool_usage = ToolUsageSignature([], [], [], [], [])
        safety = SafetySignature([], [], [], [], [])
        golden = GoldenProjection("", "", "", "", [])
        integrity = IntegritySignals("a" * 64, "b" * 64, "c" * 64, "v1.0", [], True)
        
        cache_entry = SemanticCacheEntry(
            file_signature=file_signature,
            ast_signature=ast_signature,
            embedding=None,
            tool_usage=tool_usage,
            safety=safety,
            semantic_diff=None,
            golden_projection=golden,
            integrity=integrity,
            processing_timestamp=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(cache_entry)
        
        # Should have validation error for missing hash
        assert len(errors) > 0
        assert any("hash" in error.lower() for error in errors)


class TestFileSignatureValidation:
    """Test file signature validation"""
    
    def test_valid_file_signature(self):
        """Test validation of valid file signature"""
        file_signature = FileSignature(
            file_path=Path("/test/path.py"),
            file_hash="a" * 64,  # Valid SHA-256 hash
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=FileExtension.PYTHON
        )
        
        # File signature validation is part of cache entry validation
        from semantic_lineage import ToolUsageSignature, SafetySignature, GoldenProjection, IntegritySignals, ASTSignature
        
        ast_signature = ASTSignature(
            signature=file_signature,
            root_nodes=["class_def", "function_def"],  # Valid AST with nodes
            import_graph={},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        
        # Create a complete cache entry for validation
        tool_usage = ToolUsageSignature([], [], [], [], [])
        safety = SafetySignature([], [], [], [], [])
        golden = GoldenProjection("", "", "", "", [])
        integrity = IntegritySignals("a" * 64, "b" * 64, "c" * 64, "v1.0", [], True)
        
        cache_entry = SemanticCacheEntry(
            file_signature=file_signature,
            ast_signature=ast_signature,
            embedding=None,
            tool_usage=tool_usage,
            safety=safety,
            semantic_diff=None,
            golden_projection=golden,
            integrity=integrity,
            processing_timestamp=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(cache_entry)
        
        # Should have no validation errors
        assert len(errors) == 0
    
    def test_invalid_file_signature_hash(self):
        """Test validation of file signature with invalid hash"""
        file_signature = FileSignature(
            file_path=Path("/test/path.py"),
            file_hash="short_hash",  # Too short for SHA-256
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=FileExtension.PYTHON
        )
        
        from semantic_lineage import ToolUsageSignature, SafetySignature, GoldenProjection, IntegritySignals, ASTSignature
        
        ast_signature = ASTSignature(
            signature=file_signature,
            root_nodes=[],
            import_graph={},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        
        # Create a complete cache entry for validation
        tool_usage = ToolUsageSignature([], [], [], [], [])
        safety = SafetySignature([], [], [], [], [])
        golden = GoldenProjection("", "", "", "", [])
        integrity = IntegritySignals("a" * 64, "b" * 64, "c" * 64, "v1.0", [], True)
        
        cache_entry = SemanticCacheEntry(
            file_signature=file_signature,
            ast_signature=ast_signature,
            embedding=None,
            tool_usage=tool_usage,
            safety=safety,
            semantic_diff=None,
            golden_projection=golden,
            integrity=integrity,
            processing_timestamp=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(cache_entry)
        
        # Should have validation error for invalid hash
        assert len(errors) > 0
        assert any("hash" in error.lower() for error in errors)
    
    def test_invalid_file_extension(self):
        """Test validation of file signature with invalid extension"""
        file_signature = FileSignature(
            file_path=Path("/test/path.xyz"),  # Invalid extension
            file_hash="a" * 64,
            size_bytes=100,
            last_modified=datetime.now(),
            engine=EngineType.RESUME_ENGINE,
            archive_version="test_version",
            file_extension=FileExtension.PYTHON  # Mismatch with actual file path
        )
        
        from semantic_lineage import ToolUsageSignature, SafetySignature, GoldenProjection, IntegritySignals, ASTSignature
        
        ast_signature = ASTSignature(
            signature=file_signature,
            root_nodes=[],
            import_graph={},
            function_signatures={},
            class_signatures={},
            complexity_metrics={}
        )
        
        # Create a complete cache entry for validation
        tool_usage = ToolUsageSignature([], [], [], [], [])
        safety = SafetySignature([], [], [], [], [])
        golden = GoldenProjection("", "", "", "", [])
        integrity = IntegritySignals("a" * 64, "b" * 64, "c" * 64, "v1.0", [], True)
        
        cache_entry = SemanticCacheEntry(
            file_signature=file_signature,
            ast_signature=ast_signature,
            embedding=None,
            tool_usage=tool_usage,
            safety=safety,
            semantic_diff=None,
            golden_projection=golden,
            integrity=integrity,
            processing_timestamp=datetime.now()
        )
        
        validator = SemanticLineageValidator()
        errors = validator.validate_cache_entry(cache_entry)
        
        # Should have validation error for extension mismatch
        assert len(errors) > 0


class TestEngineTypeDetection:
    """Test engine type detection from paths"""
    
    def test_resume_engine_detection(self):
        """Test detection of resume engine paths"""
        from semantic_lineage import determine_engine_from_path
        
        test_paths = [
            Path("C:/Git/Resume Engine Archive/v10.7/main.py"),
            Path("C:/Git/Resume Engine Archive/Agentic-Workflow-10_11/core.py"),
            Path("C:/Git/Resume Engine Archive/v2/data.py")
        ]
        
        for test_path in test_paths:
            engine = determine_engine_from_path(test_path)
            assert engine == EngineType.RESUME_ENGINE
    
    def test_outreach_engine_detection(self):
        """Test detection of outreach engine paths"""
        from semantic_lineage import determine_engine_from_path
        
        test_paths = [
            Path("C:/Git/Reachout Engine Archive/Agentic-LIC/main.py"),
            Path("C:/Git/Reachout Engine Archive/Monolithic/core.py"),
            Path("C:/Git/Reachout Engine Archive/Agentic LIC/data.py")
        ]
        
        for test_path in test_paths:
            engine = determine_engine_from_path(test_path)
            assert engine == EngineType.OUTREACH_ENGINE
    
    def test_invalid_engine_path(self):
        """Test handling of invalid engine paths"""
        from semantic_lineage import determine_engine_from_path
        
        test_paths = [
            Path("C:/Git/Other Archive/v10.7/main.py"),
            Path("C:/random/path/core.py"),
        ]
        
        for test_path in test_paths:
            with pytest.raises(ValueError):
                determine_engine_from_path(test_path)


class TestFileExtensionValidation:
    """Test file extension validation"""
    
    def test_valid_extensions(self):
        """Test validation of supported file extensions"""
        from semantic_lineage import validate_file_extension
        
        test_cases = [
            ("test.py", FileExtension.PYTHON),
            ("test.json", FileExtension.JSON),
            ("test.md", FileExtension.MARKDOWN),
            ("test.txt", FileExtension.TEXT),
            ("test.yaml", FileExtension.YAML),
            ("test.cfg", FileExtension.CONFIG),
        ]
        
        for filename, expected_ext in test_cases:
            result = validate_file_extension(Path(filename))
            assert result == expected_ext
    
    def test_invalid_extensions(self):
        """Test validation of unsupported file extensions"""
        from semantic_lineage import validate_file_extension
        
        invalid_files = [
            "test.exe",
            "test.dll",
            "test.jpg",
            "test.mp4",
            "test.zip"
        ]
        
        for filename in invalid_files:
            result = validate_file_extension(Path(filename))
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
