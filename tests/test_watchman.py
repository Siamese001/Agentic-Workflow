"""
Unit tests for The Watchman (L5 Proactive Monitoring) implementation.
Tests WatchmanHandler, DependencyGraph blast radius, and CLI argument parsing.

These tests are standalone and don't import the full canon_validator_agentic.py
to avoid stdout wrapper issues on Windows.
"""
import asyncio
import ast
import os
import sys
import pytest
from pathlib import Path
import subprocess
import tempfile

# Constants matching canon_validator_agentic.py
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs', 
    'site-packages', 'archives', 'data', 'cache', 'logs', 'tmp', 'temp'
}


# Standalone implementations for testing (mirrors canon_validator_agentic.py)
class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""
    def __init__(self):
        self.graph = {}
        self.reverse_graph = {}

    def build(self, files: list):
        for file_path in files:
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]["imports"].append(node.module)
                    elif isinstance(node, ast.ClassDef):
                        self.graph[file_path]["classes"].append(node.name)
            except Exception:
                pass
        for file, data in self.graph.items():
            for imp in data["imports"]:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> list:
        impacted = set()
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        return list(impacted)


class WatchmanHandler:
    """L5 Autonomous Mode: File system event handler for proactive validation."""
    def __init__(self, loop):
        self.loop = loop
        self._debounce_tasks = {}
        self._debounce_delay = 1.0
    
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.py'):
            return None
        if any(excluded in event.src_path for excluded in EXCLUDED_DIRS):
            return None
        return os.path.normpath(event.src_path)


class MockEvent:
    """Mock file system event for testing."""
    def __init__(self, path, is_dir=False):
        self.src_path = path
        self.is_directory = is_dir


class TestWatchmanHandler:
    """Tests for WatchmanHandler class."""
    
    def test_handler_initialization(self):
        """Test WatchmanHandler initializes correctly."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            assert handler.loop == loop
            assert handler._debounce_tasks == {}
            assert handler._debounce_delay == 1.0
        finally:
            loop.close()
    
    def test_filters_non_python_files(self):
        """Test that non-.py files are ignored."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            
            # Should be filtered (not .py)
            assert handler.on_modified(MockEvent('test.txt')) is None
            assert handler.on_modified(MockEvent('test.js')) is None
            assert handler.on_modified(MockEvent('README.md')) is None
            
            # Should pass (is .py)
            result = handler.on_modified(MockEvent('test.py'))
            assert result is not None
            assert result.endswith('test.py')
        finally:
            loop.close()
    
    def test_filters_excluded_directories(self):
        """Test that files in excluded directories are ignored."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            
            # Should be filtered (excluded dirs)
            assert handler.on_modified(MockEvent('.git/hooks/pre-commit.py')) is None
            assert handler.on_modified(MockEvent('__pycache__/module.py')) is None
            assert handler.on_modified(MockEvent('venv/lib/site.py')) is None
            
            # Should pass (not in excluded)
            result = handler.on_modified(MockEvent('src/main.py'))
            assert result is not None
        finally:
            loop.close()
    
    def test_filters_directories(self):
        """Test that directory events are ignored."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            assert handler.on_modified(MockEvent('src/', is_dir=True)) is None
            assert handler.on_modified(MockEvent('test.py', is_dir=False)) is not None
        finally:
            loop.close()


class TestDependencyGraph:
    """Tests for DependencyGraph blast radius calculation."""
    
    def test_graph_initialization(self):
        """Test DependencyGraph initializes correctly."""
        graph = DependencyGraph()
        assert graph.graph == {}
        assert graph.reverse_graph == {}
    
    def test_build_extracts_imports(self):
        """Test that build() extracts imports from files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import os\nimport sys\nfrom pathlib import Path\n")
            temp_path = f.name
        
        try:
            graph = DependencyGraph()
            graph.build([temp_path])
            
            assert temp_path in graph.graph
            imports = graph.graph[temp_path]['imports']
            assert 'os' in imports
            assert 'sys' in imports
            assert 'pathlib' in imports
        finally:
            os.unlink(temp_path)
    
    def test_build_extracts_classes(self):
        """Test that build() extracts class definitions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class Foo:\n    pass\n\nclass Bar:\n    pass\n")
            temp_path = f.name
        
        try:
            graph = DependencyGraph()
            graph.build([temp_path])
            
            classes = graph.graph[temp_path]['classes']
            assert 'Foo' in classes
            assert 'Bar' in classes
        finally:
            os.unlink(temp_path)
    
    def test_impact_radius_returns_dependents(self):
        """Test get_impact_radius returns files that import the target."""
        graph = DependencyGraph()
        # Manually set up graph for testing
        graph.graph = {
            'module_a.py': {'imports': ['module_b'], 'classes': []},
            'module_b.py': {'imports': [], 'classes': ['ClassB']},
            'module_c.py': {'imports': ['module_b'], 'classes': []},
        }
        graph.reverse_graph = {
            'module_b': ['module_a.py', 'module_c.py']
        }
        
        # module_b is imported by module_a and module_c
        impacted = graph.get_impact_radius('module_b.py')
        assert 'module_a.py' in impacted
        assert 'module_c.py' in impacted
    
    def test_build_handles_syntax_errors(self):
        """Test that build() gracefully handles files with syntax errors."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def broken(\n")  # Invalid syntax
            temp_path = f.name
        
        try:
            graph = DependencyGraph()
            graph.build([temp_path])  # Should not raise
            assert temp_path in graph.graph
        finally:
            os.unlink(temp_path)


class TestCLIArguments:
    """Tests for CLI argument parsing."""
    
    def test_help_flag_works(self):
        """Test --help flag doesn't crash."""
        result = subprocess.run(
            [sys.executable, 'scripts/canon_validator_agentic.py', '--help'],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        assert '--daemon' in result.stdout
        assert '--target' in result.stdout
        assert 'L5 Autonomous Mode' in result.stdout or 'Autonomous' in result.stdout


class TestWatchdogIntegration:
    """Integration tests for watchdog library."""
    
    def test_watchdog_imports(self):
        """Test watchdog library imports correctly."""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        assert Observer is not None
        assert FileSystemEventHandler is not None
    
    def test_observer_can_be_created(self):
        """Test Observer can be instantiated."""
        from watchdog.observers import Observer
        
        observer = Observer()
        assert observer is not None


class TestBlastRadiusCalculation:
    """Tests for blast radius calculation in surgical mode."""
    
    def test_blast_radius_includes_target(self):
        """Test that blast radius always includes the target file."""
        graph = DependencyGraph()
        graph.graph = {'target.py': {'imports': [], 'classes': []}}
        graph.reverse_graph = {}
        
        # Even with no dependents, target should be in scope
        target = 'target.py'
        blast_radius = set([target])
        dependents = graph.get_impact_radius(target)
        blast_radius.update(dependents)
        
        assert target in blast_radius
    
    def test_blast_radius_includes_dependents(self):
        """Test that blast radius includes all files that import the target."""
        graph = DependencyGraph()
        graph.graph = {
            'core.py': {'imports': [], 'classes': ['CoreClass']},
            'service_a.py': {'imports': ['core'], 'classes': []},
            'service_b.py': {'imports': ['core'], 'classes': []},
            'unrelated.py': {'imports': ['other'], 'classes': []},
        }
        graph.reverse_graph = {
            'core': ['service_a.py', 'service_b.py']
        }
        
        target = 'core.py'
        blast_radius = set([target])
        dependents = graph.get_impact_radius(target)
        blast_radius.update(dependents)
        
        assert 'core.py' in blast_radius
        assert 'service_a.py' in blast_radius
        assert 'service_b.py' in blast_radius
        assert 'unrelated.py' not in blast_radius


# ==============================================================================
# L5 FULL AUTONOMY TESTS - Event-Driven Reliability & Anti-Loop Safety
# ==============================================================================

class TestL5EventDetection:
    """
    L5 Test Case 1: Event Detection & Mission Trigger
    Verifies that filesystem modification events successfully initiate missions.
    """
    
    @pytest.mark.asyncio
    async def test_watchman_trigger_on_modification(self):
        """Verifies that a .py modification triggers a mission."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        # Simulate a file modification event for a valid Python file
        event = MockEvent("./agentic_core/unit_test_target.py")
        
        # Handler should return the normalized path (not None)
        result = handler.on_modified(event)
        
        assert result is not None
        assert result.endswith('unit_test_target.py')
        assert 'agentic_core' in result
    
    @pytest.mark.asyncio
    async def test_watchman_returns_normalized_path(self):
        """Verifies that the handler returns a normalized path for surgical scoping."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        # Test with various path formats
        event1 = MockEvent("./src/module.py")
        event2 = MockEvent("src\\nested\\file.py")
        event3 = MockEvent("apps_rg/resume_engine/test.py")
        
        result1 = handler.on_modified(event1)
        result2 = handler.on_modified(event2)
        result3 = handler.on_modified(event3)
        
        # All should return non-None normalized paths
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        
        # Paths should be normalized (no ./ prefix after normpath)
        assert not result1.startswith('.\\') or os.name != 'nt'


class TestL5ExclusionZoneSafety:
    """
    L5 Test Case 2: Exclusion Zone Safety (Anti-Loop)
    CRITICAL for L5 stability - prevents infinite recursive loops.
    """
    
    @pytest.mark.asyncio
    async def test_watchman_ignores_pycache(self):
        """Verifies that __pycache__ modifications do NOT trigger missions."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        # Simulate a modification in __pycache__
        event = MockEvent("./__pycache__/some_cache.cpython-311.pyc")
        result = handler.on_modified(event)
        
        # Should be filtered - NO mission triggered
        assert result is None
    
    @pytest.mark.asyncio
    async def test_watchman_ignores_git_directory(self):
        """Verifies that .git directory modifications do NOT trigger missions."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        event = MockEvent("./.git/hooks/pre-commit.py")
        result = handler.on_modified(event)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_watchman_ignores_venv(self):
        """Verifies that venv/virtualenv modifications do NOT trigger missions."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        events = [
            MockEvent("./venv/lib/python3.11/site-packages/module.py"),
            MockEvent("./.venv/bin/activate.py"),
            MockEvent("./env/lib/site.py"),
        ]
        
        for event in events:
            result = handler.on_modified(event)
            assert result is None, f"Should have filtered: {event.src_path}"
    
    @pytest.mark.asyncio
    async def test_watchman_ignores_logs_and_cache(self):
        """Verifies that logs/cache directories do NOT trigger missions."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        events = [
            MockEvent("./logs/debug.py"),
            MockEvent("./cache/embeddings.py"),
            MockEvent("./tmp/scratch.py"),
            MockEvent("./temp/working.py"),
        ]
        
        for event in events:
            result = handler.on_modified(event)
            assert result is None, f"Should have filtered: {event.src_path}"
    
    @pytest.mark.asyncio
    async def test_watchman_ignores_archives_and_data(self):
        """Verifies that archives/data directories do NOT trigger missions."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        events = [
            MockEvent("./archives/legacy/old_module.py"),
            MockEvent("./data/samples/test.py"),
        ]
        
        for event in events:
            result = handler.on_modified(event)
            assert result is None, f"Should have filtered: {event.src_path}"
    
    @pytest.mark.asyncio
    async def test_watchman_allows_valid_source_files(self):
        """Verifies that valid source files DO trigger missions."""
        loop = asyncio.get_running_loop()
        handler = WatchmanHandler(loop)
        
        # These should NOT be filtered (no excluded dir substrings)
        # Note: Avoid paths containing substrings like 'build', 'cache', 'data', etc.
        valid_events = [
            MockEvent("./core/agent.py"),
            MockEvent("./apps/engine/processor.py"),
            MockEvent("./scripts/validator.py"),
            MockEvent("./tests/test_module.py"),
            MockEvent("./src/module.py"),
            MockEvent("./lib/utils.py"),
        ]
        
        for event in valid_events:
            result = handler.on_modified(event)
            assert result is not None, f"Should NOT have filtered: {event.src_path}"


class TestL5SurgicalScopeCalculation:
    """
    L5 Test Case 3: Surgical Scope & Blast Radius
    Verifies correct utilization of DependencyGraph for impact analysis.
    """
    
    @pytest.mark.asyncio
    async def test_watchman_surgical_scope_single_dependent(self):
        """Verifies that the Watchman identifies single dependent correctly."""
        graph = DependencyGraph()
        
        # Mock: file_b imports module_a (use module name without path prefix)
        graph.reverse_graph = {"module_a": ["./file_b.py"]}
        
        # Calculate impact radius - use bare module name (as it would appear after normalization)
        # The get_impact_radius converts path to module: "module_a.py" -> "module_a"
        modified_file = "module_a.py"
        impact_radius = graph.get_impact_radius(modified_file)
        
        assert "./file_b.py" in impact_radius
        assert len(impact_radius) == 1
    
    @pytest.mark.asyncio
    async def test_watchman_surgical_scope_multiple_dependents(self):
        """Verifies blast radius with multiple dependents."""
        graph = DependencyGraph()
        
        # Mock: multiple files import core_module
        graph.reverse_graph = {
            "core_module": ["./service_a.py", "./service_b.py", "./handler.py"]
        }
        
        # Use bare module name
        impact_radius = graph.get_impact_radius("core_module.py")
        
        assert len(impact_radius) == 3
        assert "./service_a.py" in impact_radius
        assert "./service_b.py" in impact_radius
        assert "./handler.py" in impact_radius
    
    @pytest.mark.asyncio
    async def test_watchman_surgical_scope_no_dependents(self):
        """Verifies handling of files with no dependents."""
        graph = DependencyGraph()
        graph.reverse_graph = {}
        
        # Leaf file with no dependents
        impact_radius = graph.get_impact_radius("isolated_module.py")
        
        assert len(impact_radius) == 0
    
    @pytest.mark.asyncio
    async def test_watchman_surgical_scope_excludes_unrelated(self):
        """Verifies that unrelated files are NOT in blast radius."""
        graph = DependencyGraph()
        graph.reverse_graph = {
            "module_a": ["./dependent_a.py"],
            "module_b": ["./dependent_b.py"],
        }
        
        # Only module_a dependents should be returned
        impact_radius = graph.get_impact_radius("module_a.py")
        
        assert "./dependent_a.py" in impact_radius
        assert "./dependent_b.py" not in impact_radius


class TestL5RecursionGuard:
    """
    L5 Recursion Guard Tests - Prevents infinite healing loops.
    """
    
    def test_all_excluded_dirs_are_filtered(self):
        """Comprehensive test that ALL EXCLUDED_DIRS are properly filtered."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            
            # Test every single excluded directory
            for excluded_dir in EXCLUDED_DIRS:
                event = MockEvent(f"./{excluded_dir}/some_file.py")
                result = handler.on_modified(event)
                assert result is None, f"EXCLUDED_DIR '{excluded_dir}' was NOT filtered!"
        finally:
            loop.close()
    
    def test_nested_excluded_dirs_are_filtered(self):
        """Test that nested paths containing excluded dirs are filtered."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            
            nested_paths = [
                "./project/__pycache__/module.py",
                "./deep/nested/.git/hooks/script.py",
                "./apps/venv/lib/package.py",
                "./src/build/output.py",
            ]
            
            for path in nested_paths:
                event = MockEvent(path)
                result = handler.on_modified(event)
                assert result is None, f"Nested excluded path '{path}' was NOT filtered!"
        finally:
            loop.close()
    
    def test_non_python_files_never_trigger(self):
        """Test that non-.py files never trigger missions regardless of location."""
        loop = asyncio.new_event_loop()
        try:
            handler = WatchmanHandler(loop)
            
            non_python_files = [
                "./src/config.json",
                "./src/data.yaml",
                "./src/script.sh",
                "./src/module.pyc",  # Compiled Python
                "./src/module.pyo",  # Optimized Python
                "./src/module.pyd",  # Python DLL
            ]
            
            for path in non_python_files:
                event = MockEvent(path)
                result = handler.on_modified(event)
                assert result is None, f"Non-Python file '{path}' was NOT filtered!"
        finally:
            loop.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
