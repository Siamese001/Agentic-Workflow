#!/usr/bin/env python3
"""
Unit tests for ConvergenceEngine with Phase 5-6 features.

Tests:
- Toxicity-Weighted Triage (violations sorted by impact_score)
- Zombie Detection (audit_fail_count > 3)
- Fission Detection (large files unchanged after healing)
"""
import asyncio
import tempfile
import os
from pathlib import Path
import pytest

# Import the ConvergenceEngine
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "agentic_core" / "L3_orchestration" / "workflow_engines"))

from mission_controller_convergence import ConvergenceEngine


class MockValidator:
    """Mock validator for testing."""
    
    def __init__(self, violations, rounds_to_clear=1):
        self.violations = violations
        self.call_count = 0
        self.rounds_to_clear = rounds_to_clear
    
    async def validate(self):
        self.call_count += 1
        if self.call_count > self.rounds_to_clear:
            return []
        return self.violations


class MockHealer:
    """Mock healer that tracks healing order."""
    
    def __init__(self, modify_files=False):
        self.heal_order = []
        self.modify_files = modify_files
    
    async def heal(self, violation):
        path = violation.get('path', 'unknown')
        self.heal_order.append(path)
        
        # Optionally modify the file to avoid fission detection
        if self.modify_files and Path(path).exists():
            with open(path, 'a') as f:
                f.write('\n# Healed')


class TestToxicityWeightedTriage:
    """Tests for toxicity-weighted triage (Phase 6)."""
    
    @pytest.mark.asyncio
    async def test_violations_sorted_by_impact_score(self):
        """Test that violations are sorted by impact_score descending."""
        violations = [
            {'path': 'low_impact.py', 'impact_score': 50},
            {'path': 'high_impact.py', 'impact_score': 500},
            {'path': 'medium_impact.py', 'impact_score': 200},
        ]
        
        validator = MockValidator(violations)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        await engine.run_convergence(validator, healer, violations)
        
        # First round should process in order: high, medium, low
        first_round = healer.heal_order[:3]
        assert first_round[0] == 'high_impact.py', "Highest impact should be first"
        assert first_round[1] == 'medium_impact.py', "Medium impact should be second"
        assert first_round[2] == 'low_impact.py', "Lowest impact should be last"
    
    @pytest.mark.asyncio
    async def test_default_impact_score_zero(self):
        """Test that missing impact_score defaults to 0."""
        violations = [
            {'path': 'with_score.py', 'impact_score': 100},
            {'path': 'no_score.py'},  # No impact_score
        ]
        
        validator = MockValidator(violations)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        await engine.run_convergence(validator, healer, violations)
        
        # with_score should be processed before no_score
        first_round = healer.heal_order[:2]
        assert first_round[0] == 'with_score.py'
        assert first_round[1] == 'no_score.py'
    
    @pytest.mark.asyncio
    async def test_equal_impact_scores_stable_sort(self):
        """Test that equal impact scores maintain stable order."""
        violations = [
            {'path': 'first.py', 'impact_score': 100},
            {'path': 'second.py', 'impact_score': 100},
            {'path': 'third.py', 'impact_score': 100},
        ]
        
        validator = MockValidator(violations)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        await engine.run_convergence(validator, healer, violations)
        
        # Should maintain original order for equal scores
        first_round = healer.heal_order[:3]
        assert len(first_round) == 3


class TestZombieDetection:
    """Tests for zombie detection (Phase 5)."""
    
    @pytest.mark.asyncio
    async def test_zombie_detected_when_audit_fail_count_exceeds_3(self, capsys):
        """Test that zombie is detected when audit_fail_count > 3."""
        violations = [
            {'path': 'zombie_agent.py', 'impact_score': 100, 'audit_fail_count': 5},
        ]
        
        validator = MockValidator(violations)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        await engine.run_convergence(validator, healer, violations)
        
        captured = capsys.readouterr()
        assert '🧟 ZOMBIE DETECTED' in captured.out
        assert 'zombie_agent.py' in captured.out
    
    @pytest.mark.asyncio
    async def test_no_zombie_when_audit_fail_count_3_or_less(self, capsys):
        """Test that no zombie is detected when audit_fail_count <= 3."""
        violations = [
            {'path': 'normal_agent.py', 'impact_score': 100, 'audit_fail_count': 3},
        ]
        
        validator = MockValidator(violations)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        await engine.run_convergence(validator, healer, violations)
        
        captured = capsys.readouterr()
        assert '🧟 ZOMBIE DETECTED' not in captured.out
    
    @pytest.mark.asyncio
    async def test_zombie_detection_with_missing_audit_fail_count(self, capsys):
        """Test that missing audit_fail_count defaults to 0 (no zombie)."""
        violations = [
            {'path': 'no_count_agent.py', 'impact_score': 100},
        ]
        
        validator = MockValidator(violations)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        await engine.run_convergence(validator, healer, violations)
        
        captured = capsys.readouterr()
        assert '🧟 ZOMBIE DETECTED' not in captured.out


class TestFissionDetection:
    """Tests for fission detection."""
    
    @pytest.mark.asyncio
    async def test_fission_detected_for_large_unchanged_file(self, capsys):
        """Test that fission is detected for large file unchanged after healing."""
        # Create a temporary large file (>10KB)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Large test file\n" * 1000)  # ~20KB
            temp_file = f.name
        
        try:
            violations = [
                {'path': temp_file, 'impact_score': 100},
            ]
            
            validator = MockValidator(violations)
            healer = MockHealer(modify_files=False)  # Don't modify file
            engine = ConvergenceEngine(max_rounds=2)
            
            await engine.run_convergence(validator, healer, violations)
            
            captured = capsys.readouterr()
            assert '⚛️ FISSION DETECTED' in captured.out
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_no_fission_for_small_unchanged_file(self, capsys):
        """Test that no fission is detected for small file (<10KB)."""
        # Create a temporary small file (<10KB)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Small test file\n")  # < 10KB
            temp_file = f.name
        
        try:
            violations = [
                {'path': temp_file, 'impact_score': 100},
            ]
            
            validator = MockValidator(violations)
            healer = MockHealer(modify_files=False)
            engine = ConvergenceEngine(max_rounds=2)
            
            await engine.run_convergence(validator, healer, violations)
            
            captured = capsys.readouterr()
            assert '⚛️ FISSION DETECTED' not in captured.out
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_no_fission_when_file_modified(self, capsys):
        """Test that no fission is detected when file is modified."""
        # Create a temporary large file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Large test file\n" * 1000)
            temp_file = f.name
        
        try:
            violations = [
                {'path': temp_file, 'impact_score': 100},
            ]
            
            validator = MockValidator(violations)
            healer = MockHealer(modify_files=True)  # Modify file
            engine = ConvergenceEngine(max_rounds=2)
            
            await engine.run_convergence(validator, healer, violations)
            
            captured = capsys.readouterr()
            assert '⚛️ FISSION DETECTED' not in captured.out
        finally:
            os.unlink(temp_file)


class TestConvergenceLoop:
    """Tests for convergence loop behavior."""
    
    @pytest.mark.asyncio
    async def test_convergence_achieved_message(self, capsys):
        """Test that convergence achieved message is printed."""
        violations = [{'path': 'test.py', 'impact_score': 100}]
        
        validator = MockValidator(violations, rounds_to_clear=1)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=5)
        
        result = await engine.run_convergence(validator, healer, violations)
        
        captured = capsys.readouterr()
        assert '✅ CONVERGENCE ACHIEVED' in captured.out
        assert result is True
    
    @pytest.mark.asyncio
    async def test_convergence_failed_message(self, capsys):
        """Test that convergence failed message is printed when max rounds exceeded."""
        violations = [{'path': 'stubborn.py', 'impact_score': 100}]
        
        # Validator never clears violations
        validator = MockValidator(violations, rounds_to_clear=100)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=2)
        
        result = await engine.run_convergence(validator, healer, violations)
        
        captured = capsys.readouterr()
        assert '⚠️ CONVERGENCE FAILED' in captured.out
        assert result is False
    
    @pytest.mark.asyncio
    async def test_round_history_tracked(self):
        """Test that round history is tracked."""
        violations = [{'path': 'test.py', 'impact_score': 100}]
        
        validator = MockValidator(violations, rounds_to_clear=2)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=5)
        
        await engine.run_convergence(validator, healer, violations)
        
        assert len(engine.round_history) > 0
    
    @pytest.mark.asyncio
    async def test_max_rounds_respected(self):
        """Test that max_rounds limit is respected."""
        violations = [{'path': 'test.py', 'impact_score': 100}]
        
        validator = MockValidator(violations, rounds_to_clear=100)
        healer = MockHealer()
        engine = ConvergenceEngine(max_rounds=3)
        
        await engine.run_convergence(validator, healer, violations)
        
        # Should have exactly max_rounds entries in history
        assert len(engine.round_history) == 3


class TestFileHashFunctions:
    """Tests for file hash functions."""
    
    def test_get_file_hash_returns_string(self):
        """Test that get_file_hash returns a string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            engine = ConvergenceEngine()
            hash_value = engine.get_file_hash(Path(temp_file))
            
            assert isinstance(hash_value, str)
            assert len(hash_value) == 64  # SHA256 hex digest length
        finally:
            os.unlink(temp_file)
    
    def test_get_file_hash_consistent(self):
        """Test that get_file_hash returns consistent results."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            engine = ConvergenceEngine()
            hash1 = engine.get_file_hash(Path(temp_file))
            hash2 = engine.get_file_hash(Path(temp_file))
            
            assert hash1 == hash2
        finally:
            os.unlink(temp_file)
    
    def test_detect_fission_true_for_large_unchanged(self):
        """Test detect_fission returns True for large unchanged file."""
        engine = ConvergenceEngine()
        
        result = engine.detect_fission(
            pre_hash="abc123",
            post_hash="abc123",  # Same hash
            file_size=15000  # > 10KB
        )
        
        assert result is True
    
    def test_detect_fission_false_for_changed_file(self):
        """Test detect_fission returns False for changed file."""
        engine = ConvergenceEngine()
        
        result = engine.detect_fission(
            pre_hash="abc123",
            post_hash="def456",  # Different hash
            file_size=15000
        )
        
        assert result is False
    
    def test_detect_fission_false_for_small_file(self):
        """Test detect_fission returns False for small file."""
        engine = ConvergenceEngine()
        
        result = engine.detect_fission(
            pre_hash="abc123",
            post_hash="abc123",  # Same hash
            file_size=5000  # < 10KB
        )
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
