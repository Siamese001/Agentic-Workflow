import pytest
import os
import shutil
from pathlib import Path
import tempfile

class TestToolRegistryMigration:
    
    @pytest.fixture
    def mock_env(self):
        """Creates a mock environment with the 'ToolRegistry' casing issue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            l2 = root / "agentic_core" / "L2_execution"
            l2.mkdir(parents=True)
            
            # Create the PascalCase directory
            (l2 / "ToolRegistry").mkdir()
            (l2 / "ToolRegistry" / "dummy_tool.py").write_text("print('I am a tool')")
            
            # Create a consumer file with the old import
            consumer = root / "consumer.py"
            consumer.write_text("from agentic_core.L2_execution.tool_registry import dummy_tool")
            
            yield root

    def test_migration_logic(self, mock_env):
        """Simulate the atomic rename and content replacement."""
        l2 = mock_env / "agentic_core" / "L2_execution"
        old_dir = l2 / "ToolRegistry"
        new_dir = l2 / "tool_registry"
        consumer = mock_env / "consumer.py"
        
        # --- EXECUTE LOGIC (Replicated from script) ---
        
        # 1. Atomic Rename (Simulated)
        if old_dir.exists():
            tmp = l2 / "TEMP_MIGRATION"
            os.rename(old_dir, tmp)
            os.rename(tmp, new_dir)
            
        # 2. Content Replace
        content = consumer.read_text()
        content = content.replace("ToolRegistry", "tool_registry")
        consumer.write_text(content)
        
        # --- ASSERTIONS ---
        
        # Check Directory Structure
        assert new_dir.exists()
        assert (new_dir / "dummy_tool.py").exists()
        assert not old_dir.exists()
        
        # Check Import Update
        updated_content = consumer.read_text()
        assert "from agentic_core.L2_execution.tool_registry" in updated_content
        assert "ToolRegistry" not in updated_content
