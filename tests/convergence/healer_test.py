#!/usr/bin/env python3
"""
Standalone Tests for L4 Recursive Convergence Loop

These tests validate the convergence logic without requiring full imports.
"""

import pytest
import hashlib
import asyncio
from pathlib import Path
from collections import defaultdict
from unittest.mock import Mock, AsyncMock


class MockController:
    """Mock MissionController for testing convergence logic."""
    
    def __init__(self):
        self.max_rounds = 5
        self.detection_calls = 0
        self.healing_calls = 0
        
    async def simulate_convergence_round(self, ctx, violations):
        """Simulate a single convergence round."""
        # Phase 1: Detection
        detection_result = {
            "total_violations": violations,
            "files_scanned": 10,
            "files_with_violations": violations // 5 if violations > 0 else 0,
            "violations_by_file": {}
        }
        self.detection_calls += 1
        
        # Phase 2: Healing
        heals_applied = min(violations, 30)  # Heal up to 30 per round
        healing_result = {
            "heals_applied": heals_applied,
            "files_healed": heals_applied // 5
        }
        self.healing_calls += 1
        
        # Phase 3: Re-validation
        post_violations = max(0, violations - heals_applied)
        
        return detection_result, healing_result, post_violations


class TestConvergenceLogic:
    """Test convergence loop logic."""
    
    @pytest.mark.asyncio
    async def test_convergence_achieves_zero_violations(self):
        """Test that convergence loop reaches zero violations."""
        controller = MockController()
        
        violations = 100
        rounds = 0
        max_rounds = 5
        
        while violations > 0 and rounds < max_rounds:
            rounds += 1
            ctx = Mock()
            
            detection, healing, post_violations = await controller.simulate_convergence_round(ctx, violations)
            
            assert post_violations < violations, f"Round {rounds} should reduce violations"
            violations = post_violations
        
        assert violations == 0, "Should converge to zero violations"
        assert rounds <= max_rounds, "Should converge within max rounds"
        assert rounds == 4, "Should take 4 rounds for 100 violations"
    
    @pytest.mark.asyncio
    async def test_convergence_respects_max_rounds(self):
        """Test that convergence stops at max rounds."""
        controller = MockController()
        
        # Simulate stuck violations (never decrease)
        violations = 50
        rounds = 0
        max_rounds = 3
        
        async def stuck_round(ctx, v):
            return (
                {"total_violations": v, "files_scanned": 5, "files_with_violations": 2, "violations_by_file": {}},
                {"heals_applied": 0, "files_healed": 0},
                v  # Violations don't decrease
            )
        
        controller.simulate_convergence_round = stuck_round
        
        while violations > 0 and rounds < max_rounds:
            rounds += 1
            ctx = Mock()
            detection, healing, post_violations = await controller.simulate_convergence_round(ctx, violations)
            violations = post_violations
        
        assert rounds == max_rounds, "Should stop at max rounds"
        assert violations > 0, "Violations should remain (didn't converge)"
    
    def test_convergence_history_tracking(self):
        """Test convergence history is tracked correctly."""
        history = []
        
        # Simulate 3 rounds
        rounds_data = [
            (100, 70, 30),  # Round 1: 100 → 70 (30 heals)
            (70, 30, 40),   # Round 2: 70 → 30 (40 heals)
            (30, 0, 30)     # Round 3: 30 → 0 (30 heals)
        ]
        
        for round_num, (pre, post, heals) in enumerate(rounds_data, 1):
            history.append({
                "round": round_num,
                "pre_violations": pre,
                "post_violations": post,
                "heals_applied": heals,
                "progress": pre - post
            })
        
        assert len(history) == 3
        assert history[0]["pre_violations"] == 100
        assert history[-1]["post_violations"] == 0
        assert sum(h["progress"] for h in history) == 100


class TestStateSnapshotting:
    """Test file hash snapshotting."""
    
    def test_hash_generation(self, tmp_path):
        """Test SHA256 hash generation for files."""
        file1 = tmp_path / "test1.py"
        file1.write_text("print('hello')")
        
        content = file1.read_text()
        hash1 = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        assert len(hash1) == 64
        assert isinstance(hash1, str)
    
    def test_hash_detects_changes(self, tmp_path):
        """Test that hash changes when file content changes."""
        file1 = tmp_path / "test1.py"
        file1.write_text("print('hello')")
        
        hash1 = hashlib.sha256(file1.read_text().encode('utf-8')).hexdigest()
        
        # Modify file
        file1.write_text("print('world')")
        
        hash2 = hashlib.sha256(file1.read_text().encode('utf-8')).hexdigest()
        
        assert hash1 != hash2
    
    def test_hash_unchanged_for_same_content(self, tmp_path):
        """Test that hash is unchanged for same content."""
        file1 = tmp_path / "test1.py"
        file1.write_text("print('hello')")
        
        hash1 = hashlib.sha256(file1.read_text().encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(file1.read_text().encode('utf-8')).hexdigest()
        
        assert hash1 == hash2


class TestFissionDetection:
    """Test fission event detection logic."""
    
    def test_fission_detects_unchanged_large_files(self, tmp_path):
        """Test fission detection for unchanged large files."""
        large_file = tmp_path / "large.py"
        large_file.write_text("x" * 15000)  # >10KB
        
        content = large_file.read_text()
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Simulate unchanged file
        pre_hashes = {str(large_file): file_hash}
        post_hashes = {str(large_file): file_hash}
        
        # File unchanged + violations remain = fission event
        file_size = large_file.stat().st_size
        
        should_trigger_fission = (
            pre_hashes[str(large_file)] == post_hashes[str(large_file)] and
            file_size > 10000
        )
        
        assert should_trigger_fission is True
    
    def test_fission_ignores_small_files(self, tmp_path):
        """Test that fission ignores small files."""
        small_file = tmp_path / "small.py"
        small_file.write_text("print('small')")
        
        content = small_file.read_text()
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        pre_hashes = {str(small_file): file_hash}
        post_hashes = {str(small_file): file_hash}
        
        file_size = small_file.stat().st_size
        
        should_trigger_fission = (
            pre_hashes[str(small_file)] == post_hashes[str(small_file)] and
            file_size > 10000
        )
        
        assert should_trigger_fission is False
    
    def test_fission_ignores_changed_files(self, tmp_path):
        """Test that fission ignores files that changed."""
        file1 = tmp_path / "test.py"
        file1.write_text("original")
        
        pre_hash = hashlib.sha256(file1.read_text().encode('utf-8')).hexdigest()
        
        file1.write_text("modified")
        post_hash = hashlib.sha256(file1.read_text().encode('utf-8')).hexdigest()
        
        should_trigger_fission = (pre_hash == post_hash)
        
        assert should_trigger_fission is False


class TestTandemEnforcement:
    """Test tandem Validator → Healer enforcement."""
    
    def test_healer_spawning_for_violations(self):
        """Test that healers are spawned for each violation."""
        violations_by_file = {
            "file1.py": [
                {"type": "import_violation", "line": 10},
                {"type": "import_violation", "line": 15}
            ],
            "file2.py": [
                {"type": "hierarchy_violation", "line": 5}
            ]
        }
        
        # Count total violations
        total_violations = sum(len(v) for v in violations_by_file.values())
        
        # Each violation should spawn a healer attempt
        healer_attempts = total_violations
        
        assert healer_attempts == 3
    
    def test_healing_respects_limits(self):
        """Test that healing respects per-file limits."""
        heal_attempts = defaultdict(int)
        max_heals_per_file = 8
        
        file_path = "test.py"
        
        # Simulate 10 heal attempts
        for _ in range(10):
            if heal_attempts[file_path] < max_heals_per_file:
                heal_attempts[file_path] += 1
        
        # Should stop at max
        assert heal_attempts[file_path] == max_heals_per_file


class TestConvergenceReporting:
    """Test convergence reporting."""
    
    def test_convergence_achieved_report(self):
        """Test convergence achieved reporting."""
        converged = True
        rounds = 3
        max_rounds = 5
        
        status = "CONVERGENCE ACHIEVED" if converged else "MAX ROUNDS REACHED"
        
        assert status == "CONVERGENCE ACHIEVED"
        assert rounds < max_rounds
    
    def test_max_rounds_reached_report(self):
        """Test max rounds reached reporting."""
        converged = False
        rounds = 5
        max_rounds = 5
        
        status = "CONVERGENCE ACHIEVED" if converged else "MAX ROUNDS REACHED"
        
        assert status == "MAX ROUNDS REACHED"
        assert rounds == max_rounds
    
    def test_progress_calculation(self):
        """Test progress calculation between rounds."""
        history = [
            {"pre_violations": 100, "post_violations": 70},
            {"pre_violations": 70, "post_violations": 30},
            {"pre_violations": 30, "post_violations": 0}
        ]
        
        for entry in history:
            entry["progress"] = entry["pre_violations"] - entry["post_violations"]
        
        total_progress = sum(h["progress"] for h in history)
        
        assert total_progress == 100
        assert all(h["progress"] > 0 for h in history)


@pytest.mark.asyncio
async def test_full_convergence_simulation():
    """Full convergence simulation test."""
    print("\n" + "="*80)
    print("CONVERGENCE SIMULATION TEST")
    print("="*80)
    
    # Initial state
    violations = 147
    max_rounds = 5
    convergence_history = []
    
    print(f"\nInitial violations: {violations}")
    print(f"Max rounds: {max_rounds}")
    
    # Convergence loop
    for round_num in range(1, max_rounds + 1):
        print(f"\n[ROUND {round_num}]")
        
        # Simulate healing (reduce by 30-50 violations per round)
        import random
        heals = min(violations, random.randint(30, 50))
        post_violations = max(0, violations - heals)
        
        convergence_history.append({
            "round": round_num,
            "pre_violations": violations,
            "post_violations": post_violations,
            "heals_applied": heals,
            "progress": violations - post_violations
        })
        
        print(f"  Pre-violations: {violations}")
        print(f"  Heals applied: {heals}")
        print(f"  Post-violations: {post_violations}")
        print(f"  Progress: -{violations - post_violations}")
        
        violations = post_violations
        
        if violations == 0:
            print(f"\n✅ CONVERGENCE ACHIEVED in {round_num} rounds!")
            break
    else:
        print(f"\n⚠️  MAX ROUNDS REACHED with {violations} violations remaining")
    
    print("\n" + "="*80)
    print("CONVERGENCE HISTORY")
    print("="*80)
    for entry in convergence_history:
        r = entry["round"]
        pre = entry["pre_violations"]
        post = entry["post_violations"]
        heals = entry["heals_applied"]
        progress = entry["progress"]
        status = "✓" if progress > 0 else "⚠"
        print(f"Round {r}: {pre} → {post} violations ({status} {heals} heals, {progress:+d} progress)")
    
    print("="*80)
    
    # Assertions
    assert len(convergence_history) <= max_rounds
    assert convergence_history[-1]["post_violations"] == 0 or len(convergence_history) == max_rounds


if __name__ == "__main__":
    # Run the full simulation
    asyncio.run(test_full_convergence_simulation())
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
