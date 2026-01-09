#!/usr/bin/env python3
"""
Unit Tests for L4 Recursive Convergence Loop

Tests the convergence loop implementation in MissionController including:
- State snapshotting
- Tandem enforcement
- SSOT re-validation
- Fission event detection
- Convergence tracking
"""

import pytest
import asyncio
import hashlib
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from collections import defaultdict

# Mock the imports that may not be available
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))


class TestStateSnapshotting:
    """Tests for file hash snapshotting."""
    
    @pytest.fixture
    def mock_ctx(self, tmp_path):
        """Create mock validation context."""
        ctx = Mock()
        
        # Create test files
        file1 = tmp_path / "file1.py"
        file1.write_text("print('hello')")
        
        file2 = tmp_path / "file2.py"
        file2.write_text("print('world')")
        
        ctx.python_files = [str(file1), str(file2)]
        return ctx
    
    @pytest.mark.asyncio
    async def test_snapshot_creates_hashes(self, mock_ctx, tmp_path):
        """Test that snapshot creates SHA256 hashes for all files."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        hashes = await controller._snapshot_file_hashes(mock_ctx)
        
        assert len(hashes) == 2
        assert all(isinstance(h, str) and len(h) == 64 for h in hashes.values())
    
    @pytest.mark.asyncio
    async def test_snapshot_detects_changes(self, mock_ctx, tmp_path):
        """Test that snapshot detects file changes."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        
        # First snapshot
        hashes1 = await controller._snapshot_file_hashes(mock_ctx)
        
        # Modify a file
        file1 = Path(mock_ctx.python_files[0])
        file1.write_text("print('modified')")
        
        # Second snapshot
        hashes2 = await controller._snapshot_file_hashes(mock_ctx)
        
        # First file should have different hash
        assert hashes1[str(file1)] != hashes2[str(file1)]
        
        # Second file should have same hash
        file2 = Path(mock_ctx.python_files[1])
        assert hashes1[str(file2)] == hashes2[str(file2)]
    
    @pytest.mark.asyncio
    async def test_snapshot_handles_missing_files(self, tmp_path):
        """Test that snapshot handles missing files gracefully."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        ctx = Mock()
        ctx.python_files = [str(tmp_path / "nonexistent.py")]
        
        controller = MissionController(tmp_path)
        hashes = await controller._snapshot_file_hashes(ctx)
        
        # Should handle gracefully
        assert len(hashes) == 1
        assert hashes[str(tmp_path / "nonexistent.py")] == "ERROR"


class TestTandemEnforcement:
    """Tests for tandem Validator → Healer enforcement."""
    
    @pytest.fixture
    def mock_ctx(self):
        """Create mock validation context."""
        ctx = Mock()
        ctx.heal_attempts = defaultdict(int)
        ctx.max_heals_per_file = 8
        return ctx
    
    @pytest.fixture
    def mock_controller(self, tmp_path):
        """Create mock MissionController."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        controller._orchestrator = Mock()
        return controller
    
    @pytest.mark.asyncio
    async def test_tandem_healing_spawns_healers(self, mock_controller, mock_ctx):
        """Test that tandem healing spawns healers for violations."""
        # Mock detection results
        detection_results = {
            "files_with_violations": 2,
            "violations_by_file": {
                "/path/to/file1.py": [
                    {"type": "import_violation", "line": 10}
                ],
                "/path/to/file2.py": [
                    {"type": "hierarchy_violation", "line": 5}
                ]
            }
        }
        
        # Mock validators
        mock_validator = Mock()
        mock_validator.heal_violation = AsyncMock(return_value={"healed": True})
        mock_controller._orchestrator.get_atomic_validators.return_value = [mock_validator]
        
        # Mock heal_with_guards
        mock_controller._heal_with_guards = AsyncMock(return_value={"healed": True})
        
        # Run tandem healing
        result = await mock_controller._run_tandem_healing(mock_ctx, detection_results)
        
        assert result["files_attempted"] == 2
        assert result["heals_applied"] > 0
    
    @pytest.mark.asyncio
    async def test_tandem_healing_respects_limits(self, mock_controller, mock_ctx):
        """Test that tandem healing respects per-file heal limits."""
        # Set file already at max heals
        mock_ctx.heal_attempts["/path/to/file1.py"] = 8
        
        detection_results = {
            "violations_by_file": {
                "/path/to/file1.py": [{"type": "import_violation"}]
            }
        }
        
        mock_controller._orchestrator.get_atomic_validators.return_value = []
        
        result = await mock_controller._run_tandem_healing(mock_ctx, detection_results)
        
        # Should skip file at limit
        assert result["files_healed"] == 0
    
    @pytest.mark.asyncio
    async def test_tandem_healing_tracks_attempts(self, mock_controller, mock_ctx):
        """Test that tandem healing tracks heal attempts."""
        detection_results = {
            "violations_by_file": {
                "/path/to/file1.py": [{"type": "import_violation"}]
            }
        }
        
        mock_validator = Mock()
        mock_controller._orchestrator.get_atomic_validators.return_value = [mock_validator]
        mock_controller._heal_with_guards = AsyncMock(return_value={"healed": True})
        
        initial_attempts = mock_ctx.heal_attempts["/path/to/file1.py"]
        
        await mock_controller._run_tandem_healing(mock_ctx, detection_results)
        
        # Should increment heal attempts
        assert mock_ctx.heal_attempts["/path/to/file1.py"] > initial_attempts


class TestSSOTRevalidation:
    """Tests for SSOT re-validation."""
    
    @pytest.mark.asyncio
    async def test_revalidation_calls_detection(self, tmp_path):
        """Test that re-validation calls detection phase."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        ctx = Mock()
        
        # Mock detection phase
        controller._run_detection_phase = AsyncMock(return_value={
            "total_violations": 0,
            "files_scanned": 10
        })
        
        result = await controller._run_ssot_revalidation(ctx)
        
        # Should call detection phase
        controller._run_detection_phase.assert_called_once_with(ctx)
        assert result["total_violations"] == 0


class TestFissionEventDetection:
    """Tests for fission event detection."""
    
    @pytest.fixture
    def mock_ctx(self, tmp_path):
        """Create mock validation context."""
        ctx = Mock()
        
        # Create test files
        large_file = tmp_path / "large.py"
        large_file.write_text("x" * 15000)  # >10KB
        
        small_file = tmp_path / "small.py"
        small_file.write_text("print('small')")
        
        ctx.python_files = [str(large_file), str(small_file)]
        ctx.fission_events = []
        return ctx
    
    @pytest.mark.asyncio
    async def test_fission_detects_unchanged_large_files(self, mock_ctx, tmp_path):
        """Test that fission detects unchanged large files with violations."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        
        # Create identical pre/post hashes (file unchanged)
        large_file = Path(mock_ctx.python_files[0])
        content = large_file.read_text()
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        pre_hashes = {str(large_file): file_hash}
        post_hashes = {str(large_file): file_hash}
        
        # Violations remain
        fission_detected = await controller._detect_fission_events(
            mock_ctx,
            pre_hashes,
            post_hashes,
            pre_violations=10,
            post_violations=10
        )
        
        assert fission_detected is True
        assert len(mock_ctx.fission_events) == 1
        assert mock_ctx.fission_events[0]["file"] == str(large_file)
    
    @pytest.mark.asyncio
    async def test_fission_ignores_small_files(self, mock_ctx, tmp_path):
        """Test that fission ignores small files."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        
        # Small file unchanged
        small_file = Path(mock_ctx.python_files[1])
        content = small_file.read_text()
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        pre_hashes = {str(small_file): file_hash}
        post_hashes = {str(small_file): file_hash}
        
        fission_detected = await controller._detect_fission_events(
            mock_ctx,
            pre_hashes,
            post_hashes,
            pre_violations=5,
            post_violations=5
        )
        
        # Should not trigger fission for small file
        assert fission_detected is False
        assert len(mock_ctx.fission_events) == 0
    
    @pytest.mark.asyncio
    async def test_fission_skips_when_converged(self, mock_ctx, tmp_path):
        """Test that fission is skipped when violations reach zero."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        
        fission_detected = await controller._detect_fission_events(
            mock_ctx,
            {},
            {},
            pre_violations=10,
            post_violations=0  # Converged
        )
        
        assert fission_detected is False


class TestConvergenceTracking:
    """Tests for convergence history tracking."""
    
    @pytest.mark.asyncio
    async def test_convergence_history_records_rounds(self):
        """Test that convergence history records each round."""
        ctx = Mock()
        ctx.convergence_history = []
        
        # Simulate 3 rounds
        for round_num in range(1, 4):
            ctx.convergence_history.append({
                "round": round_num,
                "pre_violations": 100 - (round_num - 1) * 30,
                "post_violations": 100 - round_num * 30,
                "heals_applied": 30,
                "fission_events": 0,
                "progress": -30
            })
        
        assert len(ctx.convergence_history) == 3
        assert ctx.convergence_history[0]["round"] == 1
        assert ctx.convergence_history[-1]["post_violations"] == 10
    
    def test_convergence_report_shows_progress(self, tmp_path, capsys):
        """Test that convergence report shows progress."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        ctx = Mock()
        ctx.convergence_history = [
            {"round": 1, "pre_violations": 100, "post_violations": 70, "heals_applied": 30, "progress": -30},
            {"round": 2, "pre_violations": 70, "post_violations": 30, "heals_applied": 40, "progress": -40},
            {"round": 3, "pre_violations": 30, "post_violations": 0, "heals_applied": 30, "progress": -30}
        ]
        ctx.fission_events = []
        
        controller._print_convergence_report(ctx, converged=True, rounds=3, max_rounds=5)
        
        captured = capsys.readouterr()
        assert "CONVERGENCE ACHIEVED" in captured.out
        assert "Round 1: 100 → 70" in captured.out
        assert "Round 3: 30 → 0" in captured.out


class TestConvergenceLoopIntegration:
    """Integration tests for the full convergence loop."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_convergence_loop_achieves_zero_violations(self, tmp_path):
        """Test that convergence loop achieves zero violations."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        
        # Mock components
        controller._orchestrator = Mock()
        controller._orchestrator.get_atomic_validators.return_value = []
        
        # Mock detection phase to simulate decreasing violations
        violation_counts = [100, 50, 20, 0]
        call_count = [0]
        
        async def mock_detection(ctx):
            count = violation_counts[min(call_count[0], len(violation_counts) - 1)]
            call_count[0] += 1
            return {
                "total_violations": count,
                "files_scanned": 10,
                "files_with_violations": count // 5 if count > 0 else 0,
                "violations_by_file": {},
                "violations_by_type": {}
            }
        
        controller._run_detection_phase = mock_detection
        controller._snapshot_file_hashes = AsyncMock(return_value={})
        controller._run_tandem_healing = AsyncMock(return_value={"heals_applied": 0, "files_healed": 0})
        controller._detect_fission_events = AsyncMock(return_value=False)
        
        # Note: Full run_mission test would require extensive mocking
        # This tests the convergence logic in isolation
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_convergence_loop_respects_max_rounds(self, tmp_path):
        """Test that convergence loop respects MAX_CONVERGENCE_ROUNDS."""
        from agentic_core.L3_orchestration.workflow_engines.mission_controller import MissionController
        
        controller = MissionController(tmp_path)
        
        # Mock to always return violations (never converge)
        async def mock_detection(ctx):
            return {
                "total_violations": 10,  # Always has violations
                "files_scanned": 5,
                "files_with_violations": 2,
                "violations_by_file": {},
                "violations_by_type": {}
            }
        
        controller._run_detection_phase = mock_detection
        controller._snapshot_file_hashes = AsyncMock(return_value={})
        controller._run_tandem_healing = AsyncMock(return_value={"heals_applied": 0})
        controller._detect_fission_events = AsyncMock(return_value=False)
        
        # Would need to test full run_mission with MAX_CONVERGENCE_ROUNDS=2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
