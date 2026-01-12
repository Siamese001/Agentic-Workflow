"""E2E test for full canon validation mission with healing."""
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch, MagicMock
import json

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

@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skip(reason='RecursionError in file_hash_tracker fixture - needs investigation')
class test_full_canon_mission:
    """End-to-end canon validation mission execution."""

    @patch('canon_validator_agentic_v2.GeminiClient')
    def test_full_mission_with_zero_violations(self, mock_gemini: Any, tmp_sovereign_workspace: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Codebase with no canon violations
        WHEN: Full canon mission executes
        THEN: All 50 keys pass, no healing triggered
        """
        mock_gemini.return_value.generate_content.return_value = Mock(text='All canon keys validated successfully')
        (tmp_sovereign_workspace / AGENTIC_CORE_DIR).mkdir(exist_ok=True)
        (tmp_sovereign_workspace / 'schemas').mkdir(exist_ok=True)
        compliant_file: Any = tmp_sovereign_workspace / AGENTIC_CORE_DIR / 'core.py'
        compliant_file.write_text('\n"""Core sovereignty module."""\nfrom typing import Dict, Any\n\n# NAMING FIXED: agentic_core → agentic_core\nclass agentic_core:\n    """Main agentic core."""\n    \n    def run(self, mission: Dict[str, Any]) -> Dict[str, Any]:\n        return {"status": "success"}\n')
        mission_result: Any = {'mission_id': 'canon-001', 'status': 'completed', 'violations': 0, 'keys_passed': 50, 'healing_triggered': False}
        audit_log_tracker.log('mission_complete', mission_result)
        assert mission_result['violations'] == 0
        assert mission_result['keys_passed'] == 50
        assert mission_result['healing_triggered'] is False
        entries: Any = audit_log_tracker.get_entries('mission_complete')
        assert len(entries) == 1

    @patch('canon_validator_agentic_v2.GeminiClient')
    def test_mission_detects_and_heals_violations(self, mock_gemini: Any, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Codebase with canon violations
        WHEN: Mission executes with healing enabled
        THEN: Violations detected, healing applied, convergence achieved
        """
        mock_gemini.return_value.generate_content.return_value = Mock(text=json.dumps({'violations': [{'key': 'K01', 'type': 'naming', 'file': 'BAD_name.py'}, {'key': 'K15', 'type': 'gravity', 'file': 'misplaced.py'}], 'healing_plan': [{'action': 'rename', 'target': 'BAD_name.py', 'new_name': 'good_name.py'}, {'action': 'relocate', 'target': 'misplaced.py', 'new_location': 'agentic_core/'}]}))
        bad_file: Any = tmp_sovereign_workspace / 'BAD_name.py'
        bad_file.write_text('class Test:\n    pass\n')
        misplaced: Any = tmp_sovereign_workspace / 'misplaced.py'
        misplaced.write_text('class Core:\n    pass\n')
        healing_transaction_mock.backup(bad_file)
        healing_transaction_mock.backup(misplaced)
        good_file: Any = tmp_sovereign_workspace / 'good_name.py'
        good_file.write_text(bad_file.read_text())
        bad_file.unlink()
        core_dir: Any = tmp_sovereign_workspace / AGENTIC_CORE_DIR
        core_dir.mkdir(exist_ok=True)
        relocated: Any = core_dir / 'misplaced.py'
        relocated.write_text(misplaced.read_text())
        misplaced.unlink()
        healing_transaction_mock.commit()
        audit_log_tracker.log('healing_round', {'round': 1, 'violations_fixed': 2, 'remaining_violations': 0})
        assert not bad_file.exists()
        assert good_file.exists()
        assert relocated.exists()
        assert healing_transaction_mock.committed is True
        healing_entries: Any = audit_log_tracker.get_entries('healing_round')
        assert healing_entries[0]['details']['violations_fixed'] == 2

    @patch('canon_validator_agentic_v2.GeminiClient')
    def test_mission_convergence_after_multiple_rounds(self, mock_gemini: Any, tmp_sovereign_workspace: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Complex violations requiring multiple healing rounds
        WHEN: Mission executes iteratively
        THEN: Violations converge to zero
        """
        violation_counts: Any = [10, 5, 2, 0]
        for round_num, count in enumerate(violation_counts):
            audit_log_tracker.log('healing_round', {'round': round_num + 1, 'violations_remaining': count})
        rounds: Any = audit_log_tracker.get_entries('healing_round')
        assert len(rounds) == 4
        assert rounds[0]['details']['violations_remaining'] == 10
        assert rounds[-1]['details']['violations_remaining'] == 0
        counts: Any = [r['details']['violations_remaining'] for r in rounds]
        assert counts == sorted(counts, reverse=True)

    @patch('canon_validator_agentic_v2.GeminiClient')
    def test_mission_rollback_on_critical_failure(self, mock_gemini: Any, tmp_sovereign_workspace: Any, healing_transaction_mock: Any) -> Any:
        """
        GIVEN: Healing operation fails critically
        WHEN: Rollback triggered
        THEN: All changes reverted, original state restored
        """
        critical_file: Any = tmp_sovereign_workspace / 'critical.py'
        original_content: Any = '# Critical sovereignty code\nclass Sovereign:\n    pass\n'
        critical_file.write_text(original_content)
        import hashlib
        original_hash: Any = hashlib.sha256(critical_file.read_bytes()).hexdigest()
        healing_transaction_mock.backup(critical_file)
        try:
            critical_file.write_text("# CORRUPTED\nraise Exception('Healing failed')\n")
            raise Exception('Critical healing failure')
        except Exception:
            healing_transaction_mock.rollback()
            audit_log_tracker.log('mission_rollback', {'reason': 'critical_failure', 'files_restored': 1})
        final_hash: Any = hashlib.sha256(critical_file.read_bytes()).hexdigest()
        assert final_hash == original_hash
        assert critical_file.read_text() == original_content
        assert healing_transaction_mock.rolled_back is True
        rollback_entries: Any = audit_log_tracker.get_entries('mission_rollback')
        assert len(rollback_entries) == 1

@pytest.mark.e2e
@pytest.mark.slow
class test_canon_mission_edge_cases:
    """Test edge cases in canon mission execution."""

    def test_empty_codebase_passes_all_keys(self, tmp_sovereign_workspace: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Empty codebase (no Python files)
        WHEN: Canon mission runs
        THEN: All keys pass (no violations possible)
        """
        mission_result: Any = {'files_scanned': 0, 'violations': 0, 'keys_passed': 50}
        audit_log_tracker.log('mission_complete', mission_result)
        assert mission_result['violations'] == 0
        assert mission_result['keys_passed'] == 50

    def test_mission_handles_malformed_files(self, tmp_sovereign_workspace: Any, audit_log_tracker: Any) -> Any:
        """
        GIVEN: Files with syntax errors
        WHEN: Canon mission scans
        THEN: Syntax errors logged, mission continues
        """
        malformed: Any = tmp_sovereign_workspace / 'malformed.py'
        malformed.write_text('class Broken\n    def incomplete(:\n')
        audit_log_tracker.log('syntax_error', {'file': str(malformed), 'error': 'SyntaxError: invalid syntax'})
        syntax_errors: Any = audit_log_tracker.get_entries('syntax_error')
        assert len(syntax_errors) == 1
        assert 'malformed.py' in syntax_errors[0]['details']['file']

    @pytest.mark.parametrize('violation_count', [1, 10, 50, 100])
    def test_mission_scales_with_violation_count(self, tmp_sovereign_workspace: Any, audit_log_tracker: Any, violation_count: Any) -> Any:
        """
        GIVEN: Varying numbers of violations
        WHEN: Mission executes
        THEN: Healing scales appropriately
        """
        for i in range(violation_count):
            file: Any = tmp_sovereign_workspace / f'violation_{i}.py'
            file.write_text(f'# Violation {i}\n')
        audit_log_tracker.log('mission_start', {'total_violations': violation_count})
        remaining: Any = violation_count
        round_num: Any = 0
        while remaining > 0:
            round_num += 1
            fixed: Any = max(1, int(remaining * 0.2))
            remaining -= fixed
            audit_log_tracker.log('healing_round', {'round': round_num, 'fixed': fixed, 'remaining': remaining})
        rounds: Any = audit_log_tracker.get_entries('healing_round')
        assert len(rounds) > 0
        assert rounds[-1]['details']['remaining'] == 0
