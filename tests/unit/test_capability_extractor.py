"""
Unit tests for CapabilityExtractor primitive.
Phase 9: Autonomous Evolution - L0 Primitive Test Coverage
"""
import pytest
import ast
from agentic_core.L0_maintenance.primitives.capability_extractor import CapabilityExtractor


class TestCapabilityExtractor:
    """Comprehensive test suite for CapabilityExtractor."""
    
    def test_initialization(self):
        """Test CapabilityExtractor initializes correctly."""
        extractor = CapabilityExtractor()
        
        assert hasattr(extractor, 'COMMON_METHODS')
        assert hasattr(extractor, 'SEMANTIC_KEYWORDS')
        assert hasattr(extractor, 'PATTERN_KEYWORDS')
    
    def test_common_methods_defined(self):
        """Test COMMON_METHODS contains expected baseline methods."""
        extractor = CapabilityExtractor()
        
        assert '__init__' in extractor.COMMON_METHODS
        assert 'heal_violation' in extractor.COMMON_METHODS
        assert 'execute' in extractor.COMMON_METHODS
        assert 'run' in extractor.COMMON_METHODS
        assert 'validate' in extractor.COMMON_METHODS
        assert 'monitor' in extractor.COMMON_METHODS
    
    def test_extract_capabilities_empty_class(self):
        """Test extracting capabilities from empty class."""
        code = """
class EmptyAgent:
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert caps['semantic_tags'] == set()
        assert caps['unique_methods'] == set()
        assert caps['patterns'] == set()
        assert caps['valuable_methods'] == []
    
    def test_extract_capabilities_with_common_methods(self):
        """Test that common methods are not marked as unique."""
        code = """
class TestAgent:
    def __init__(self):
        pass
    
    def execute(self):
        pass
    
    def validate(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        # Common methods should not be in unique_methods
        assert '__init__' not in caps['unique_methods']
        assert 'execute' not in caps['unique_methods']
        assert 'validate' not in caps['unique_methods']
    
    def test_extract_capabilities_with_unique_methods(self):
        """Test that unique methods are identified."""
        code = """
class TestAgent:
    def custom_analyze(self):
        pass
    
    def special_transform(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'custom_analyze' in caps['unique_methods']
        assert 'special_transform' in caps['unique_methods']
        assert len(caps['valuable_methods']) == 2
    
    def test_semantic_tagging_healing(self):
        """Test semantic tagging for healing-related methods."""
        code = """
class HealerAgent:
    def heal_violation(self):
        pass
    
    def fix_error(self):
        pass
    
    def repair_structure(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'healing' in caps['semantic_tags']
    
    def test_semantic_tagging_validation(self):
        """Test semantic tagging for validation-related methods."""
        code = """
class ValidatorAgent:
    def validate_structure(self):
        pass
    
    def check_compliance(self):
        pass
    
    def enforce_rules(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'validation' in caps['semantic_tags']
    
    def test_semantic_tagging_detection(self):
        """Test semantic tagging for detection-related methods."""
        code = """
class DetectorAgent:
    def detect_anomalies(self):
        pass
    
    def find_violations(self):
        pass
    
    def scan_codebase(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'detection' in caps['semantic_tags']
    
    def test_semantic_tagging_pruning(self):
        """Test semantic tagging for pruning-related methods."""
        code = """
class PrunerAgent:
    def prune_dead_code(self):
        pass
    
    def clean_imports(self):
        pass
    
    def remove_unused(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'pruning' in caps['semantic_tags']
    
    def test_semantic_tagging_mapping(self):
        """Test semantic tagging for mapping-related methods."""
        code = """
class MapperAgent:
    def map_dependencies(self):
        pass
    
    def analyze_territory(self):
        pass
    
    def build_structure(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'mapping' in caps['semantic_tags']
    
    def test_semantic_tagging_monitoring(self):
        """Test semantic tagging for monitoring-related methods."""
        code = """
class MonitorAgent:
    def watch_changes(self):
        pass
    
    def monitor_health(self):
        pass
    
    def observe_metrics(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'monitoring' in caps['semantic_tags']
    
    def test_semantic_tagging_git_integration(self):
        """Test semantic tagging for git-related methods."""
        code = """
class GitAgent:
    def git_commit(self):
        pass
    
    def git_push(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'git_integration' in caps['semantic_tags']
    
    def test_pattern_detection_git_operations(self):
        """Test pattern detection for git operations."""
        code = """
class GitAgent:
    def run_git_command(self):
        import subprocess
        subprocess.run(['git', 'status'])
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'git_operations' in caps['patterns']
    
    def test_pattern_detection_dead_code_analysis(self):
        """Test pattern detection for dead code analysis."""
        code = """
class AnalyzerAgent:
    def analyze(self):
        # Check for dead code
        if has_dead_code():
            remove_unused()
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'dead_code_analysis' in caps['patterns']
    
    def test_pattern_detection_filesystem_introspection(self):
        """Test pattern detection for filesystem operations."""
        code = """
class FileAgent:
    def check_files(self):
        from pathlib import Path
        if Path('file.txt').exists():
            process()
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'filesystem_introspection' in caps['patterns']
    
    def test_pattern_detection_redis_integration(self):
        """Test pattern detection for Redis operations."""
        code = """
class CacheAgent:
    def cache_data(self):
        import redis
        client = redis.Redis()
        client.set('key', 'value')
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'redis_integration' in caps['patterns']
    
    def test_get_all_capabilities(self):
        """Test getting unified set of all capabilities."""
        code = """
class ComplexAgent:
    def heal_violation(self):
        pass
    
    def git_commit(self):
        import subprocess
        subprocess.run(['git', 'commit'])
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        all_caps = extractor.get_all_capabilities(caps)
        
        assert 'healing' in all_caps
        assert 'git_integration' in all_caps
        assert 'git_operations' in all_caps
        assert isinstance(all_caps, set)
    
    def test_filter_unique_methods(self):
        """Test filtering out common methods."""
        extractor = CapabilityExtractor()
        
        methods = {'__init__', 'execute', 'custom_method', 'validate', 'special_func'}
        unique = extractor.filter_unique_methods(methods)
        
        assert 'custom_method' in unique
        assert 'special_func' in unique
        assert '__init__' not in unique
        assert 'execute' not in unique
        assert 'validate' not in unique
    
    def test_valuable_methods_tracking(self):
        """Test that valuable methods are tracked with metadata."""
        code = """
class TestAgent:
    def unique_capability(self):
        pass
    
    def another_unique(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert len(caps['valuable_methods']) == 2
        
        # Check structure of valuable_methods
        for method_name, line_no, description in caps['valuable_methods']:
            assert isinstance(method_name, str)
            assert isinstance(line_no, int)
            assert isinstance(description, str)
    
    def test_async_method_handling(self):
        """Test that async methods are handled correctly."""
        code = """
class AsyncAgent:
    async def async_execute(self):
        pass
    
    async def async_validate(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'async_execute' in caps['unique_methods']
        assert 'async_validate' in caps['unique_methods']
    
    def test_multiple_semantic_tags(self):
        """Test that methods can trigger multiple semantic tags."""
        code = """
class MultiAgent:
    def heal_and_validate(self):
        pass
    
    def detect_and_fix(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        # Should have both healing and validation tags
        assert 'healing' in caps['semantic_tags']
        assert 'validation' in caps['semantic_tags']
        assert 'detection' in caps['semantic_tags']
    
    def test_case_insensitive_tagging(self):
        """Test that semantic tagging is case-insensitive."""
        code = """
class CaseAgent:
    def HEAL_VIOLATION(self):
        pass
    
    def ValidateStructure(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        extractor = CapabilityExtractor()
        caps = extractor.extract_capabilities(class_node)
        
        assert 'healing' in caps['semantic_tags']
        assert 'validation' in caps['semantic_tags']
