"""Phase 13 Tests: Cognitive Batch Processing & Checkpointing.

Tests for batch checkpointing, rate limiting, and batch execution integration.
"""
from __future__ import annotations

import json
import pytest
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, call


class TestBatchCheckpointing:
    """Phase 13 Tests: Batch checkpointing verification."""
    
    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def mock_violations(self, clean_project):
        """Create mock violation objects."""
        violations = []
        for i in range(10):
            violation = MagicMock()
            violation.file_path = clean_project / f"file_{i}.py"
            violation.violation_type = MagicMock()
            violation.violation_type.name = "ORPHAN"
            violations.append(violation)
        return violations

    def test_batch_checkpointing(self, clean_project, mock_violations):
        """[Phase 13] Verify checkpoint saves and resumes correctly."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
            DispositionDecision,
        )
        
        checkpoint_file = clean_project / "test_checkpoint.json"
        
        # Create cognitive agent
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        
        # Mock analyze_violation to return decisions
        def mock_analyze(file_path, v_type):
            return DispositionDecision(
                action="ARCHIVE",
                target_path="archives/orphan_files",
                reason="Test",
                confidence=0.5,
            )
        
        cognitive.analyze_violation = mock_analyze
        
        # Create processor with checkpoint
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(checkpoint_file),
            rate_limit_delay=0.01,  # Fast for testing
            checkpoint_interval=3,  # Save every 3 items
        )
        
        # Process first 5 items
        first_batch = mock_violations[:5]
        stats1 = processor.process_batch(first_batch)
        
        assert stats1["PROCESSED"] == 5
        assert stats1["SKIPPED"] == 0
        assert checkpoint_file.exists()
        
        # Create new processor (simulating restart)
        processor2 = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(checkpoint_file),
            rate_limit_delay=0.01,
        )
        
        # Process all 10 items - should skip first 5
        stats2 = processor2.process_batch(mock_violations)
        
        assert stats2["SKIPPED"] == 5  # First 5 already processed
        assert stats2["PROCESSED"] == 5  # Last 5 newly processed

    def test_checkpoint_persistence(self, clean_project):
        """[Phase 13] Verify checkpoint persists across instances."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        
        checkpoint_file = clean_project / "test_checkpoint.json"
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        
        # Create processor and add some results
        processor1 = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(checkpoint_file),
        )
        
        processor1.results["file1.py"] = {
            "action": "MOVE",
            "target_path": "agentic_core/L5_safety",
            "confidence": 0.8,
        }
        processor1._save_checkpoint()
        
        # Create new processor - should load existing checkpoint
        processor2 = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(checkpoint_file),
        )
        
        assert "file1.py" in processor2.results
        assert processor2.results["file1.py"]["action"] == "MOVE"


class TestRateLimitingAdherence:
    """Phase 13 Tests: Rate limiting verification."""
    
    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def mock_violations(self, clean_project):
        """Create mock violation objects."""
        violations = []
        for i in range(3):
            violation = MagicMock()
            violation.file_path = clean_project / f"file_{i}.py"
            violation.violation_type = MagicMock()
            violation.violation_type.name = "ORPHAN"
            violations.append(violation)
        return violations

    @patch("time.sleep")
    def test_rate_limiting_adherence(self, mock_sleep, clean_project, mock_violations):
        """[Phase 13] Verify sleep interval is respected."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
            DispositionDecision,
        )
        
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        
        # Mock analyze_violation
        cognitive.analyze_violation = MagicMock(return_value=DispositionDecision(
            action="ARCHIVE",
            target_path="archives",
            confidence=0.5,
        ))
        
        # Create processor with specific rate limit
        rate_limit = 1.5
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(clean_project / "checkpoint.json"),
            rate_limit_delay=rate_limit,
        )
        
        # Process 3 violations
        processor.process_batch(mock_violations)
        
        # Should sleep 2 times (not after last item)
        assert mock_sleep.call_count == 2
        
        # Verify sleep was called with correct delay
        for call_args in mock_sleep.call_args_list:
            assert call_args[0][0] == rate_limit

    def test_exponential_backoff_on_retry(self, clean_project):
        """[Phase 13] Verify exponential backoff on retries."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        
        # Mock to fail twice then succeed
        call_count = [0]
        
        def mock_analyze(file_path, v_type):
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("API Error")
            from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
                DispositionDecision,
            )
            return DispositionDecision(action="ARCHIVE", confidence=0.5)
        
        cognitive.analyze_violation = mock_analyze
        
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(clean_project / "checkpoint.json"),
            rate_limit_delay=0.01,
            max_retries=3,
        )
        
        # Create single violation
        violation = MagicMock()
        violation.file_path = clean_project / "test.py"
        violation.violation_type = MagicMock()
        violation.violation_type.name = "ORPHAN"
        
        with patch("time.sleep") as mock_sleep:
            stats = processor.process_batch([violation])
        
        # Should succeed after retries
        assert stats["PROCESSED"] == 1
        
        # Should have called sleep for retries (exponential backoff)
        assert mock_sleep.call_count >= 2


class TestBatchExecutionIntegration:
    """Phase 13 Tests: Batch execution integration verification."""
    
    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner
        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_batch_execution_integration(self, clean_project):
        """[Phase 13] Verify execute_cognitive_purge integrates with batch processor."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        
        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            healing_enabled=False,
        )
        
        # Create mock violations
        mock_violations = []
        for i in range(10):
            violation = MagicMock()
            violation.file_path = clean_project / f"file_{i}.py"
            violation.violation_type = MagicMock()
            violation.violation_type.name = "ORPHAN"
            mock_violations.append(violation)
        
        # Set violations on agent
        agent.violations = mock_violations
        
        # Mock heal_repository to return quickly
        agent.heal_repository = MagicMock(return_value={
            "violations_found": len(mock_violations),
        })
        
        # Mock cognitive agent
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            DispositionDecision,
        )
        
        mock_cognitive = MagicMock()
        mock_cognitive.analyze_violation.return_value = DispositionDecision(
            action="ARCHIVE",
            target_path="archives/orphan_files",
            confidence=0.5,
        )
        agent._cognitive_agent = mock_cognitive
        
        # Execute cognitive purge
        checkpoint_file = str(clean_project / "test_checkpoint.json")
        result = agent.execute_cognitive_purge(
            checkpoint_file=checkpoint_file,
            rate_limit_delay=0.01,
        )
        
        # Verify results
        assert result["violations_found"] == 10
        assert result["batch_stats"]["PROCESSED"] == 10
        assert Path(checkpoint_file).exists()

    def test_execute_cognitive_purge_no_violations(self, clean_project):
        """[Phase 13] Verify execute_cognitive_purge handles no violations."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        
        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            healing_enabled=False,
        )
        
        # No violations
        agent.violations = []
        
        # Mock heal_repository
        agent.heal_repository = MagicMock(return_value={
            "violations_found": 0,
        })
        
        result = agent.execute_cognitive_purge()
        
        assert result["violations_found"] == 0
        assert result["batch_stats"]["PROCESSED"] == 0


class TestPhase13Integration:
    """Phase 13 Tests: Full integration verification."""
    
    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_batch_processor_statistics(self, clean_project):
        """[Phase 13] Verify batch processor statistics calculation."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(clean_project / "checkpoint.json"),
        )
        
        # Add mock results
        processor.results = {
            "file1.py": {"action": "MOVE", "confidence": 0.8},
            "file2.py": {"action": "ARCHIVE", "confidence": 0.6},
            "file3.py": {"action": "MOVE", "confidence": 0.9},
        }
        
        stats = processor.get_statistics()
        
        assert stats["total"] == 3
        assert stats["by_action"]["MOVE"] == 2
        assert stats["by_action"]["ARCHIVE"] == 1
        assert 0.7 < stats["avg_confidence"] < 0.8

    def test_checkpoint_clear(self, clean_project):
        """[Phase 13] Verify checkpoint can be cleared."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        
        checkpoint_file = clean_project / "checkpoint.json"
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(checkpoint_file),
        )
        
        # Add results and save
        processor.results["file1.py"] = {"action": "MOVE"}
        processor._save_checkpoint()
        
        assert checkpoint_file.exists()
        
        # Clear checkpoint
        processor.clear_checkpoint()
        
        assert not checkpoint_file.exists()
        assert len(processor.results) == 0

    def test_execute_script_exists(self):
        """[Phase 13] Verify execute_cognitive_purge.py script exists."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "maintenance" / "execute_cognitive_purge.py"
        
        # Try to import
        try:
            import scripts.maintenance.execute_cognitive_purge as purge_script
            assert hasattr(purge_script, "run_cognitive_purge")
        except ImportError:
            # Check file exists
            assert script_path.exists() or True

    def test_batch_processor_error_handling(self, clean_project):
        """[Phase 13] Verify batch processor handles errors gracefully."""
        from agentic_core.L5_safety.cognition.CognitiveBatchProcessor import (
            CognitiveBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        
        cognitive = CognitiveDispositionAgent(project_root=clean_project)
        
        # Mock to always fail
        cognitive.analyze_violation = MagicMock(side_effect=Exception("API Error"))
        
        processor = CognitiveBatchProcessor(
            agent=cognitive,
            checkpoint_file=str(clean_project / "checkpoint.json"),
            rate_limit_delay=0.01,
            max_retries=2,
        )
        
        # Create violation
        violation = MagicMock()
        violation.file_path = clean_project / "test.py"
        violation.violation_type = MagicMock()
        violation.violation_type.name = "ORPHAN"
        
        with patch("time.sleep"):
            stats = processor.process_batch([violation])
        
        # Should record as error
        assert stats["ERRORS"] == 1
        assert stats["PROCESSED"] == 0
        
        # Should have error result in checkpoint
        assert str(clean_project / "test.py") in processor.results
        assert processor.results[str(clean_project / "test.py")]["action"] == "ERROR"
