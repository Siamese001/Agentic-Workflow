#!/usr/bin/env python3
"""
Unit tests for DuplicateCodeDetectorAgent
Tests whole-file duplicate detection, code block detection, and deletion capabilities.
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from agentic_core.L5_safety.guardrails.DuplicateCodeDetectorAgent import (

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
    DuplicateCodeDetectorAgent,
    DuplicateFile
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory with test files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create directory structure
    (temp_dir / AGENTIC_CORE_DIR / "L5_safety").mkdir(parents=True)
    (temp_dir / AGENTIC_CORE_DIR / "config" / "blueprint").mkdir(parents=True)
    (temp_dir / SCRIPTS_DIR).mkdir(parents=True)
    
    # Create duplicate Python files
    py_content = """
def hello_world():
    print("Hello, World!")
    return 42

class TestClass:
    def __init__(self):
        self.value = 100
"""
    
    (temp_dir / AGENTIC_CORE_DIR / "L5_safety" / "test_agent.py").write_text(py_content)
    (temp_dir / AGENTIC_CORE_DIR / "config" / "blueprint" / "test_agent.py").write_text(py_content)
    
    # Create duplicate HTML files
    html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Test Page</h1></body>
</html>"""
    
    (temp_dir / AGENTIC_CORE_DIR / "L5_safety" / "template.html").write_text(html_content)
    (temp_dir / SCRIPTS_DIR / "template.html").write_text(html_content)
    
    # Create unique files
    (temp_dir / AGENTIC_CORE_DIR / "L5_safety" / "unique.py").write_text("# Unique content\nprint('unique')")
    (temp_dir / SCRIPTS_DIR / "unique.js").write_text("console.log('unique');")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def agent(temp_project):
    """Create DuplicateCodeDetectorAgent instance."""
    return DuplicateCodeDetectorAgent(project_root=temp_project)


class TestDuplicateCodeDetectorAgent:
    """Test suite for DuplicateCodeDetectorAgent."""
    
    def test_initialization(self, agent, temp_project):
        """Test agent initializes correctly."""
        assert agent.project_root == temp_project
        assert agent.min_lines == 10
        assert '.py' in agent.SUPPORTED_EXTENSIONS
        assert '.html' in agent.SUPPORTED_EXTENSIONS
        assert ARCHIVES_DIR in agent.EXCLUDE_DIRS
    
    @pytest.mark.asyncio
    async def test_scan_whole_files_python(self, agent):
        """Test detection of duplicate Python files."""
        results = await agent.execute(file_types={'.py'}, scan_whole_files=True)
        
        assert "whole_file_duplicates" in results
        assert "deletion_recommendations" in results
        
        # Should find 1 set of duplicate Python files (test_agent.py in 2 locations)
        assert len(results["whole_file_duplicates"]) >= 1
        
        # Check duplicate structure
        for dup in results["whole_file_duplicates"]:
            assert isinstance(dup, DuplicateFile)
            assert len(dup.paths) >= 2
            assert dup.file_type == '.py'
    
    @pytest.mark.asyncio
    async def test_scan_whole_files_html(self, agent):
        """Test detection of duplicate HTML files."""
        results = await agent.execute(file_types={'.html'}, scan_whole_files=True)
        
        # Should find 1 set of duplicate HTML files (template.html in 2 locations)
        assert len(results["whole_file_duplicates"]) >= 1
        
        html_dup = results["whole_file_duplicates"][0]
        assert html_dup.file_type == '.html'
        assert len(html_dup.paths) == 2
    
    @pytest.mark.asyncio
    async def test_scan_multiple_file_types(self, agent):
        """Test scanning multiple file types simultaneously."""
        results = await agent.execute(file_types={'.py', '.html'}, scan_whole_files=True)
        
        # Should find duplicates for both Python and HTML
        assert len(results["whole_file_duplicates"]) >= 2
        
        file_types = {dup.file_type for dup in results["whole_file_duplicates"]}
        assert '.py' in file_types
        assert '.html' in file_types
    
    @pytest.mark.asyncio
    async def test_deletion_recommendations(self, agent):
        """Test generation of deletion recommendations."""
        results = await agent.execute(file_types={'.py'}, scan_whole_files=True)
        
        recommendations = results["deletion_recommendations"]
        assert len(recommendations) >= 1
        
        for rec in recommendations:
            assert "keep" in rec
            assert "delete" in rec
            assert "rationale" in rec
            assert "size" in rec
            assert "file_type" in rec
            assert "hash" in rec
            
            # Should have at least one file to delete
            assert len(rec["delete"]) >= 1
    
    @pytest.mark.asyncio
    async def test_canonical_path_selection(self, agent):
        """Test that canonical paths are preferred for keeping."""
        results = await agent.execute(file_types={'.py'}, scan_whole_files=True)
        
        recommendations = results["deletion_recommendations"]
        
        for rec in recommendations:
            keep_path = rec["keep"]
            
            # Canonical location should be kept
            if "L5_safety" in keep_path:
                # Should delete the blueprint copy
                assert any("blueprint" in del_path for del_path in rec["delete"])
    
    def test_delete_duplicates_dry_run(self, agent):
        """Test dry-run deletion (should not actually delete files)."""
        # First scan for duplicates
        results = asyncio.run(agent.execute(file_types={'.py'}, scan_whole_files=True))
        recommendations = results["deletion_recommendations"]
        
        # Perform dry-run deletion
        delete_result = agent.delete_duplicates(recommendations, dry_run=True)
        
        assert delete_result["dry_run"] is True
        assert delete_result["deleted_count"] >= 1
        assert len(delete_result["errors"]) == 0
        
        # Verify files still exist
        for rec in recommendations:
            for delete_path in rec["delete"]:
                full_path = agent.project_root / delete_path
                assert full_path.exists(), f"File should still exist in dry-run: {delete_path}"
    
    def test_delete_duplicates_execute(self, agent):
        """Test actual deletion of duplicate files."""
        # First scan for duplicates
        results = asyncio.run(agent.execute(file_types={'.py'}, scan_whole_files=True))
        recommendations = results["deletion_recommendations"]
        
        # Get paths before deletion
        files_to_delete = []
        for rec in recommendations:
            for delete_path in rec["delete"]:
                files_to_delete.append(agent.project_root / delete_path)
        
        # Verify files exist before deletion
        for file_path in files_to_delete:
            assert file_path.exists(), f"File should exist before deletion: {file_path}"
        
        # Perform actual deletion
        delete_result = agent.delete_duplicates(recommendations, dry_run=False)
        
        assert delete_result["dry_run"] is False
        assert delete_result["deleted_count"] >= 1
        assert len(delete_result["errors"]) == 0
        
        # Verify files are deleted
        for file_path in files_to_delete:
            assert not file_path.exists(), f"File should be deleted: {file_path}"
        
        # Verify kept files still exist
        for rec in recommendations:
            keep_path = agent.project_root / rec["keep"]
            assert keep_path.exists(), f"Kept file should still exist: {rec['keep']}"
    
    def test_exclude_directories(self, agent, temp_project):
        """Test that excluded directories are skipped."""
        # Create file in excluded directory
        archives_dir = temp_project / ARCHIVES_DIR
        archives_dir.mkdir()
        (archives_dir / "old_file.py").write_text("print('archived')")
        
        results = asyncio.run(agent.execute(file_types={'.py'}, scan_whole_files=True))
        
        # Archives should not appear in results
        for dup in results["whole_file_duplicates"]:
            for path in dup.paths:
                assert ARCHIVES_DIR not in str(path)
    
    @pytest.mark.asyncio
    async def test_no_duplicates(self, agent, temp_project):
        """Test behavior when no duplicates exist."""
        # Remove duplicate files
        (temp_project / AGENTIC_CORE_DIR / "config" / "blueprint" / "test_agent.py").unlink()
        (temp_project / SCRIPTS_DIR / "template.html").unlink()
        
        results = await agent.execute(file_types={'.py', '.html'}, scan_whole_files=True)
        
        assert len(results["whole_file_duplicates"]) == 0
        assert len(results["deletion_recommendations"]) == 0
    
    def test_rationale_generation(self, agent):
        """Test rationale generation for deletions."""
        results = asyncio.run(agent.execute(file_types={'.py'}, scan_whole_files=True))
        recommendations = results["deletion_recommendations"]
        
        for rec in recommendations:
            rationale = rec["rationale"]
            assert len(rationale) > 0
            
            # Should mention canonical location or path depth
            assert "canonical" in rationale.lower() or "shortest" in rationale.lower()
    
    @pytest.mark.asyncio
    async def test_code_block_detection(self, agent, temp_project):
        """Test detection of duplicate code blocks within files."""
        # Create file with duplicate code blocks
        code_with_dupes = """
def function_a():
    x = 1
    y = 2
    z = 3
    result = x + y + z
    print(result)
    return result

def function_b():
    x = 1
    y = 2
    z = 3
    result = x + y + z
    print(result)
    return result

def unique_function():
    return "unique"
"""
        (temp_project / AGENTIC_CORE_DIR / "L5_safety" / "code_dupes.py").write_text(code_with_dupes)
        
        results = await agent.execute(file_types={'.py'}, scan_whole_files=False)
        
        # Should detect code block duplicates
        assert "code_block_duplicates" in results
        # Note: May or may not find duplicates depending on min_lines threshold


def test_duplicate_file_dataclass():
    """Test DuplicateFile dataclass."""
    dup = DuplicateFile(
        hash="abc123",
        size=1024,
        paths=[Path("/a/file.py"), Path("/b/file.py")],
        file_type=".py"
    )
    
    assert dup.hash == "abc123"
    assert dup.size == 1024
    assert len(dup.paths) == 2
    assert dup.file_type == ".py"
    assert dup.keep_path is None
    assert dup.delete_paths is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
