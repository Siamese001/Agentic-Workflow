#!/usr/bin/env python3
"""
End-to-End Integration Tests for L4 Recursive Convergence Loop

Tests the complete convergence workflow with simulated violations and healing.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from collections import defaultdict


@pytest.mark.integration
class TestConvergenceE2E:
    """End-to-end tests for convergence loop."""
    
    @pytest.fixture
    def test_repo(self):
        """Create a test repository with violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Create structure
            (repo_path / "agentic_core").mkdir()
            (repo_path / "agentic_core" / "L0_maintenance").mkdir()
            (repo_path / "agentic_core" / "L5_safety").mkdir()
            
            # Create files with violations
            violator1 = repo_path / "agentic_core" / "L0_maintenance" / "bad1.py"
            violator1.write_text("""
# This file has an upward dependency violation
from agentic_core.L5_safety.guardrails import Something

def do_work():
    return Something()
""")
            
            violator2 = repo_path / "agentic_core" / "L0_maintenance" / "bad2.py"
            violator2.write_text("""
# Another violation
from agentic_core.L5_safety.validators import Validator

class MyAgent:
    pass
""")
            
            # Create compliant file
            good = repo_path / "agentic_core" / "L0_maintenance" / "good.py"
            good.write_text("""
# Compliant file
from agentic_core.utils.core_extensions import Helper

def do_work():
    return Helper()
""")
            
            yield repo_path
    
    @pytest.mark.asyncio
    async def test_convergence_with_simulated_healing(self, test_repo):
        """Test convergence loop with simulated healing that fixes violations."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(test_repo)
        
        # Track which round we're on
        detection_calls = [0]
        
        async def mock_detection(ctx):
            """Simulate violations decreasing each round."""
            detection_calls[0] += 1
            round_num = detection_calls[0]
            
            # Round 1: 2 violations
            # Round 2: 1 violation (after healing)
            # Round 3: 0 violations (converged)
            violations_map = {
                1: 2,
                2: 1,
                3: 0
            }
            
            violations = violations_map.get(round_num, 0)
            
            return {
                "total_violations": violations,
                "files_scanned": 3,
                "files_with_violations": violations,
                "violations_by_file": {
                    str(test_repo / "agentic_core" / "L0_maintenance" / "bad1.py"): [
                        {"type": "import_violation", "line": 3}
                    ] if violations >= 1 else [],
                    str(test_repo / "agentic_core" / "L0_maintenance" / "bad2.py"): [
                        {"type": "import_violation", "line": 3}
                    ] if violations >= 2 else []
                },
                "violations_by_type": {"import_violation": violations}
            }
        
        async def mock_healing(ctx, detection_results):
            """Simulate successful healing."""
            return {
                "files_attempted": detection_results["files_with_violations"],
                "files_healed": detection_results["files_with_violations"],
                "heals_applied": detection_results["total_violations"],
                "heals_rejected": 0
            }
        
        # Mock the methods
        controller._run_detection_phase = mock_detection
        controller._run_tandem_healing = mock_healing
        controller._snapshot_file_hashes = AsyncMock(return_value={})
        controller._detect_fission_events = AsyncMock(return_value=False)
        controller._run_postflight_validation = AsyncMock()
        controller._run_sovereign_audit_hook = AsyncMock()
        controller._run_blueprint_reconciliation_hook = AsyncMock()
        controller._initialize_context = AsyncMock(return_value=self._create_mock_context(test_repo))
        controller._discover_python_files = Mock(return_value=[
            str(test_repo / "agentic_core" / "L0_maintenance" / "bad1.py"),
            str(test_repo / "agentic_core" / "L0_maintenance" / "bad2.py"),
            str(test_repo / "agentic_core" / "L0_maintenance" / "good.py")
        ])
        controller._initialize_core_components = AsyncMock()
        controller._run_sovereign_dashboard = AsyncMock()
        controller._record_preflight_metrics = Mock()
        
        # Mock preflight
        with patch('agentic_core.L3_orchestration.workflow_engines.mission_controller.MissionPreflight') as mock_preflight_class:
            mock_preflight = Mock()
            mock_preflight.run_preflight.return_value = {"compliant": True}
            mock_preflight_class.return_value = mock_preflight
            
            # Run mission
            result = await controller.run_mission(target_scope="agentic_core", mode="heal")
        
        # Verify convergence
        assert result["converged"] is True
        assert result["rounds"] == 3
        assert result["final_violations"] == 0
        assert len(result["convergence_history"]) == 3
    
    @pytest.mark.asyncio
    async def test_convergence_max_rounds_reached(self, test_repo):
        """Test convergence loop when max rounds is reached without convergence."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(test_repo)
        
        async def mock_detection(ctx):
            """Always return violations (never converges)."""
            return {
                "total_violations": 5,
                "files_scanned": 3,
                "files_with_violations": 2,
                "violations_by_file": {},
                "violations_by_type": {"import_violation": 5}
            }
        
        async def mock_healing(ctx, detection_results):
            """Simulate healing that doesn't fix anything."""
            return {
                "files_attempted": 2,
                "files_healed": 0,
                "heals_applied": 0,
                "heals_rejected": 2
            }
        
        controller._run_detection_phase = mock_detection
        controller._run_tandem_healing = mock_healing
        controller._snapshot_file_hashes = AsyncMock(return_value={})
        controller._detect_fission_events = AsyncMock(return_value=False)
        controller._run_postflight_validation = AsyncMock()
        controller._run_sovereign_audit_hook = AsyncMock()
        controller._run_blueprint_reconciliation_hook = AsyncMock()
        controller._initialize_context = AsyncMock(return_value=self._create_mock_context(test_repo))
        controller._discover_python_files = Mock(return_value=[])
        controller._initialize_core_components = AsyncMock()
        controller._run_sovereign_dashboard = AsyncMock()
        controller._record_preflight_metrics = Mock()
        
        with patch('agentic_core.L3_orchestration.workflow_engines.mission_controller.MissionPreflight') as mock_preflight_class:
            mock_preflight = Mock()
            mock_preflight.run_preflight.return_value = {"compliant": True}
            mock_preflight_class.return_value = mock_preflight
            
            # Set MAX_CONVERGENCE_ROUNDS to 3
            with patch.dict('os.environ', {'MAX_CONVERGENCE_ROUNDS': '3'}):
                result = await controller.run_mission(target_scope="agentic_core", mode="heal")
        
        # Verify max rounds reached
        assert result["converged"] is False
        assert result["rounds"] == 3
        assert result["final_violations"] == 5
    
    @pytest.mark.asyncio
    async def test_convergence_with_fission_events(self, test_repo):
        """Test convergence loop with fission event detection."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(test_repo)
        
        # Create large file
        large_file = test_repo / "agentic_core" / "L0_maintenance" / "large.py"
        large_file.write_text("x" * 15000)  # >10KB
        
        fission_detected = [False]
        
        async def mock_detection(ctx):
            return {
                "total_violations": 2 if not fission_detected[0] else 0,
                "files_scanned": 1,
                "files_with_violations": 1 if not fission_detected[0] else 0,
                "violations_by_file": {},
                "violations_by_type": {}
            }
        
        async def mock_fission_detection(ctx, pre_hashes, post_hashes, pre_violations, post_violations):
            """Simulate fission event detection."""
            if pre_violations > 0 and post_violations > 0:
                ctx.fission_events.append({
                    "file": str(large_file),
                    "size": 15000,
                    "reason": "Unchanged after healing"
                })
                fission_detected[0] = True
                return True
            return False
        
        controller._run_detection_phase = mock_detection
        controller._run_tandem_healing = AsyncMock(return_value={"heals_applied": 0})
        controller._snapshot_file_hashes = AsyncMock(return_value={str(large_file): "hash123"})
        controller._detect_fission_events = mock_fission_detection
        controller._execute_fission_events = AsyncMock()
        controller._run_postflight_validation = AsyncMock()
        controller._run_sovereign_audit_hook = AsyncMock()
        controller._run_blueprint_reconciliation_hook = AsyncMock()
        controller._initialize_context = AsyncMock(return_value=self._create_mock_context(test_repo))
        controller._discover_python_files = Mock(return_value=[str(large_file)])
        controller._initialize_core_components = AsyncMock()
        controller._run_sovereign_dashboard = AsyncMock()
        controller._record_preflight_metrics = Mock()
        
        with patch('agentic_core.L3_orchestration.workflow_engines.mission_controller.MissionPreflight') as mock_preflight_class:
            mock_preflight = Mock()
            mock_preflight.run_preflight.return_value = {"compliant": True}
            mock_preflight_class.return_value = mock_preflight
            
            with patch.dict('os.environ', {'MAX_CONVERGENCE_ROUNDS': '3'}):
                result = await controller.run_mission(target_scope="agentic_core", mode="heal")
        
        # Verify fission events were detected
        assert result["fission_events"] >= 1
    
    def _create_mock_context(self, repo_path):
        """Create a mock validation context."""
        ctx = Mock()
        ctx.python_files = []
        ctx.report = Mock()
        ctx.report.__iter__ = Mock(return_value=iter([]))
        ctx.results = {}
        ctx.signals = set()
        ctx.successful_traces = []
        ctx.failed_traces = []
        ctx.engine = None
        ctx.safety = None
        ctx.fission = None
        ctx.project_root = repo_path
        ctx.target_scope = "agentic_core"
        ctx.cleaning_crew = []
        ctx.file_heal_history = defaultdict(list)
        ctx.max_heals_per_file = 8
        ctx.max_consecutive_heals = 3
        ctx.heal_attempts = defaultdict(int)
        ctx.convergence_history = []
        ctx.fission_events = []
        ctx.run_hierarchy_healing = True
        ctx.run_sprawl_surgery = True
        return ctx


@pytest.mark.integration
@pytest.mark.performance
class TestConvergencePerformance:
    """Performance tests for convergence loop."""
    
    @pytest.mark.asyncio
    async def test_convergence_performance_with_many_files(self):
        """Test convergence performance with many files."""
        import time
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "agentic_core").mkdir()
            
            # Create many files
            for i in range(100):
                file_path = repo_path / "agentic_core" / f"file_{i}.py"
                file_path.write_text(f"# File {i}\nprint('hello')")
            
            controller = MissionController(repo_path)
            
            # Mock for fast execution
            async def mock_detection(ctx):
                return {
                    "total_violations": 0,
                    "files_scanned": 100,
                    "files_with_violations": 0,
                    "violations_by_file": {},
                    "violations_by_type": {}
                }
            
            controller._run_detection_phase = mock_detection
            controller._snapshot_file_hashes = AsyncMock(return_value={})
            controller._run_tandem_healing = AsyncMock(return_value={"heals_applied": 0})
            controller._detect_fission_events = AsyncMock(return_value=False)
            controller._run_postflight_validation = AsyncMock()
            controller._run_sovereign_audit_hook = AsyncMock()
            controller._run_blueprint_reconciliation_hook = AsyncMock()
            
            # Create minimal mock context
            mock_ctx = Mock()
            mock_ctx.python_files = [str(repo_path / "agentic_core" / f"file_{i}.py") for i in range(100)]
            mock_ctx.convergence_history = []
            mock_ctx.fission_events = []
            mock_ctx.heal_attempts = defaultdict(int)
            
            controller._initialize_context = AsyncMock(return_value=mock_ctx)
            controller._discover_python_files = Mock(return_value=mock_ctx.python_files)
            controller._initialize_core_components = AsyncMock()
            controller._run_sovereign_dashboard = AsyncMock()
            controller._record_preflight_metrics = Mock()
            
            with patch('agentic_core.L3_orchestration.workflow_engines.mission_controller.MissionPreflight') as mock_preflight_class:
                mock_preflight = Mock()
                mock_preflight.run_preflight.return_value = {"compliant": True}
                mock_preflight_class.return_value = mock_preflight
                
                start = time.time()
                result = await controller.run_mission(target_scope="agentic_core", mode="heal")
                duration = time.time() - start
            
            # Should complete quickly (< 5 seconds with mocks)
            assert duration < 5.0
            assert result["converged"] is True


@pytest.mark.integration
class TestConvergenceEdgeCases:
    """Edge case tests for convergence loop."""
    
    @pytest.mark.asyncio
    async def test_convergence_with_no_files(self):
        """Test convergence with no Python files."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "agentic_core").mkdir()
            
            controller = MissionController(repo_path)
            
            mock_ctx = Mock()
            mock_ctx.python_files = []
            mock_ctx.convergence_history = []
            mock_ctx.fission_events = []
            mock_ctx.heal_attempts = defaultdict(int)
            
            controller._initialize_context = AsyncMock(return_value=mock_ctx)
            controller._discover_python_files = Mock(return_value=[])
            controller._initialize_core_components = AsyncMock()
            controller._run_sovereign_dashboard = AsyncMock()
            controller._record_preflight_metrics = Mock()
            controller._run_detection_phase = AsyncMock(return_value={
                "total_violations": 0,
                "files_scanned": 0,
                "files_with_violations": 0,
                "violations_by_file": {},
                "violations_by_type": {}
            })
            controller._snapshot_file_hashes = AsyncMock(return_value={})
            controller._run_postflight_validation = AsyncMock()
            controller._run_sovereign_audit_hook = AsyncMock()
            controller._run_blueprint_reconciliation_hook = AsyncMock()
            
            with patch('agentic_core.L3_orchestration.workflow_engines.mission_controller.MissionPreflight') as mock_preflight_class:
                mock_preflight = Mock()
                mock_preflight.run_preflight.return_value = {"compliant": True}
                mock_preflight_class.return_value = mock_preflight
                
                result = await controller.run_mission(target_scope="agentic_core", mode="heal")
            
            # Should converge immediately with no files
            assert result["converged"] is True
            assert result["rounds"] == 1
    
    @pytest.mark.asyncio
    async def test_convergence_with_validate_only_mode(self):
        """Test that validate_only mode skips convergence loop."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "agentic_core").mkdir()
            
            controller = MissionController(repo_path)
            
            mock_ctx = Mock()
            mock_ctx.python_files = []
            
            controller._initialize_context = AsyncMock(return_value=mock_ctx)
            controller._discover_python_files = Mock(return_value=[])
            controller._initialize_core_components = AsyncMock()
            controller._run_sovereign_dashboard = AsyncMock()
            controller._record_preflight_metrics = Mock()
            controller._run_detection_phase = AsyncMock(return_value={
                "total_violations": 10,
                "files_scanned": 5,
                "files_with_violations": 2,
                "violations_by_file": {},
                "violations_by_type": {}
            })
            
            with patch('agentic_core.L3_orchestration.workflow_engines.mission_controller.MissionPreflight') as mock_preflight_class:
                mock_preflight = Mock()
                mock_preflight.run_preflight.return_value = {"compliant": True}
                mock_preflight_class.return_value = mock_preflight
                
                result = await controller.run_mission(target_scope="agentic_core", mode="validate_only")
            
            # Should not have convergence data
            assert result["phase"] == "validation_complete"
            assert "converged" not in result
            assert "convergence_history" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
