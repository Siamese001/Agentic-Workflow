"""
Integration Tests for Phase 16H: Sovereignty Auditor
Validates comprehensive MCP compliance scanning.
"""
import asyncio
import pytest
import tempfile
from pathlib import Path
from agentic_core.utils.guardian.sovereignty_auditor import SovereigntyAuditor, run_sovereignty_audit


class TestSovereigntyAuditor:
    """Test suite for Sovereignty Auditor."""
    
    @pytest.mark.asyncio
    async def test_auditor_initialization(self):
        """Test auditor initializes correctly."""
        auditor = SovereigntyAuditor(root_dir="agentic_core")
        assert auditor.root_dir == "agentic_core"
        assert auditor.violations == []
        assert auditor.stats["files_scanned"] == 0
    
    @pytest.mark.asyncio
    async def test_depth_calculation(self):
        """Test path depth calculation."""
        auditor = SovereigntyAuditor(root_dir="agentic_core")
        
        # Test various depths
        assert auditor._calculate_depth("agentic_core") == 0
        assert auditor._calculate_depth("agentic_core/L1_cognition") == 1
        assert auditor._calculate_depth("agentic_core/L1_cognition/thought_engine") == 2
        assert auditor._calculate_depth("agentic_core/L1_cognition/thought_engine/agent_logic") == 3
    
    @pytest.mark.asyncio
    async def test_detects_redis_import(self):
        """Test auditor detects direct Redis imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import redis\nclient = redis.Redis()")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            assert auditor.stats["import_violations"] > 0
            assert any("Redis" in v["message"] for v in auditor.violations)
    
    @pytest.mark.asyncio
    async def test_detects_requests_import(self):
        """Test auditor detects direct requests imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import requests\nresponse = requests.get('url')")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            assert auditor.stats["import_violations"] > 0
            assert any("HTTP" in v["message"] for v in auditor.violations)
    
    @pytest.mark.asyncio
    async def test_detects_pinecone_import(self):
        """Test auditor detects direct Pinecone imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("from pinecone import Pinecone\npc = Pinecone()")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            assert auditor.stats["import_violations"] > 0
            assert any("Vector" in v["message"] for v in auditor.violations)
    
    @pytest.mark.asyncio
    async def test_detects_legacy_path(self):
        """Test auditor detects legacy 'tools/' path usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("from agentic_core.tools.guardian import check")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            assert auditor.stats["path_violations"] > 0
            assert any("PATH_BREACH" in v["type"] for v in auditor.violations)
    
    @pytest.mark.asyncio
    async def test_ignores_mcp_client_files(self):
        """Test auditor ignores MCP client files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "redis_mcp_client.py"
            test_file.write_text("import redis\n# This is the MCP client itself")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            # Should not flag MCP client files
            assert auditor.stats["import_violations"] == 0
    
    @pytest.mark.asyncio
    async def test_detects_depth_violations(self):
        """Test auditor detects path depth violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deep directory structure
            deep_path = Path(tmpdir) / "level1" / "level2" / "level3" / "level4" / "level5"
            deep_path.mkdir(parents=True)
            test_file = deep_path / "test.py"
            test_file.write_text("# Deep file")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            assert auditor.stats["depth_violations"] > 0
            assert any("DEPTH_BREACH" in v["type"] for v in auditor.violations)
    
    @pytest.mark.asyncio
    async def test_clean_codebase_passes(self):
        """Test auditor passes on clean codebase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("from agentic_core.L4_state.caching.redis_mcp_client import get_redis_client")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            result = await auditor.run_audit()
            
            assert result is True
            assert auditor.stats["violations_found"] == 0


class TestGuardianLockdown:
    """Test guardian lockdown enforcement."""
    
    def test_guardian_blocks_subprocess_call(self):
        """Verify guardian blocks subprocess.call()."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import subprocess\n")
            f.write("subprocess.call(['ls', '-la'])\n")
            temp_path = Path(f.name)
        
        try:
            result = check_file(temp_path)
            assert result is False, "Guardian should block subprocess.call()"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_os_popen(self):
        """Verify guardian blocks os.popen()."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import os\n")
            f.write("os.popen('ls -la')\n")
            temp_path = Path(f.name)
        
        try:
            result = check_file(temp_path)
            assert result is False, "Guardian should block os.popen()"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_legacy_tools_path(self):
        """Verify guardian blocks legacy 'tools/' path."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from agentic_core.tools.guardian import check\n")
            temp_path = Path(f.name)
        
        try:
            result = check_file(temp_path)
            assert result is False, "Guardian should block legacy 'tools/' path"
        finally:
            temp_path.unlink()
    
    def test_guardian_allows_utils_path(self):
        """Verify guardian allows 'utils/' path."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from agentic_core.utils.guardian import SovereigntyAuditor\n")
            temp_path = Path(f.name)
        
        try:
            result = check_file(temp_path)
            assert result is True, "Guardian should allow 'utils/' path"
        finally:
            temp_path.unlink()


class TestAuditorReporting:
    """Test auditor reporting functionality."""
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test auditor statistics retrieval."""
        auditor = SovereigntyAuditor(root_dir="agentic_core")
        stats = auditor.get_stats()
        
        assert "files_scanned" in stats
        assert "violations_found" in stats
        assert "depth_violations" in stats
        assert "import_violations" in stats
        assert "path_violations" in stats
    
    @pytest.mark.asyncio
    async def test_get_violations(self):
        """Test auditor violations retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import redis")
            
            auditor = SovereigntyAuditor(root_dir=tmpdir)
            await auditor.run_audit()
            
            violations = auditor.get_violations()
            assert isinstance(violations, list)
            assert len(violations) > 0
            assert all("type" in v for v in violations)
            assert all("message" in v for v in violations)
            assert all("file" in v for v in violations)


class TestAuditorIntegration:
    """Test auditor integration with codebase."""
    
    @pytest.mark.asyncio
    async def test_run_sovereignty_audit_function(self):
        """Test standalone audit function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# Clean file")
            
            result = await run_sovereignty_audit(root_dir=tmpdir)
            assert isinstance(result, bool)


def run_tests():
    """Run all sovereignty auditor tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
