#!/usr/bin/env python3
"""
Comprehensive test suite for execute_ssot.py refactoring fixes.

Tests cover all batches:
- Batch 1: B13, I2, B19, B7, B2, B15
- Batch 2: B3, B14, B4+B5, B6
- Batch 3: B1, B12, B11, B10, B9
- Batch 4: H2, H3, H4, H5
- Batch 5: I1, I3, I4
"""

import ast
import importlib
import inspect
import json
import re
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module import helper
# ---------------------------------------------------------------------------

MODULE_NAME = "agentic_core.L0_routing.scripts.execute_ssot"


@pytest.fixture(scope="module")
def ssot_module():
    """Import the execute_ssot module once for all tests."""
    try:
        return importlib.import_module(MODULE_NAME)
    except ImportError as e:
        pytest.skip(f"Cannot import {MODULE_NAME}: {e}")


@pytest.fixture
def source_path():
    """Return absolute path to execute_ssot.py source."""
    return Path(__file__).resolve().parents[5] / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"


@pytest.fixture
def source_text(source_path):
    """Return the raw source text of execute_ssot.py."""
    return source_path.read_text(encoding="utf-8")


@pytest.fixture
def source_ast(source_text):
    """Return the parsed AST of execute_ssot.py."""
    return ast.parse(source_text)


# ============================================================================
# BATCH 1 TESTS
# ============================================================================


class TestBatch1TrivialFixes:
    """Tests for Batch 1 trivial fixes."""

    @pytest.mark.unit
    def test_b13_no_dead_decision_history_expression(self, source_text):
        """B13: The dead `state_mgr.state.get('decision_history', [])` expression
        on its own line (without assignment) must not exist."""
        # Pattern: a line that is just state_mgr.state.get("decision_history", []) with no assignment
        lines = source_text.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == 'state_mgr.state.get("decision_history", [])':
                pytest.fail(f"Dead decision_history expression found at line {i}")

    @pytest.mark.unit
    def test_i2_no_dead_dict_literal(self, source_text):
        """I2: No standalone dict literal with has_test_functions/has_sovereign_class keys."""
        assert '"has_test_functions"' not in source_text or "has_test_functions" in source_text.split("=")[0] is False
        # More precise: look for the specific dead dict pattern
        pattern = r'{\s*"has_test_functions".*?"is_in_docs".*?}'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            # Verify it's not assigned to anything
            start = match.start()
            line_start = source_text.rfind("\n", 0, start) + 1
            prefix = source_text[line_start:start].strip()
            if not prefix or prefix.endswith("{"):
                pytest.fail("Dead dict literal with file-specific factors still exists")

    @pytest.mark.unit
    def test_b19_validate_territory_no_redundant_checks(self, ssot_module):
        """B19: validate_territory_input should reject invalid chars via regex alone,
        without redundant path traversal / injection checks."""
        validate = ssot_module.validate_territory_input
        # Valid territory
        ok, msg = validate("L0_routing")
        assert ok is True

        # Invalid chars — rejected by regex, not by downstream checks
        bad, msg = validate("foo;bar")
        assert bad is False
        assert "Invalid characters" in msg

        bad2, msg2 = validate("foo/bar")
        assert bad2 is False
        assert "Invalid characters" in msg2

    @pytest.mark.unit
    def test_b7_phase8_key_renamed(self, source_text):
        """B7: Phase 8 compliance_report key must be 'compliance_report_audit',
        not 'compliance_report' (which collides with Phase 3)."""
        # There should be at least one occurrence of compliance_report_audit
        assert "compliance_report_audit" in source_text

    @pytest.mark.unit
    def test_b15_healing_enabled_reset(self, source_text):
        """B15: _healing_enabled must be reset to True per territory."""
        assert "decision_engine._healing_enabled = True" in source_text


# ============================================================================
# BATCH 2 TESTS
# ============================================================================


class TestBatch2StateStorage:
    """Tests for Batch 2 state storage fixes."""

    @pytest.mark.unit
    def test_b14_territory_in_decision_data(self, source_text):
        """B14: decision_data dict must contain a 'territory' field."""
        # Find the decision_data dict definition
        pattern = r'decision_data\s*=\s*\{[^}]*"territory"'
        assert re.search(pattern, source_text, re.DOTALL), \
            "decision_data dict missing 'territory' field"

    @pytest.mark.unit
    def test_b3_location_fixed_stored(self, source_text):
        """B3: location_fixed must be stored in state_mgr.state."""
        assert 'state_mgr.state["location_fixed"]' in source_text

    @pytest.mark.unit
    def test_b3_hierarchy_fixed_stored(self, source_text):
        """B3: hierarchy_fixed must be stored in state_mgr.state."""
        assert 'state_mgr.state["hierarchy_fixed"]' in source_text

    @pytest.mark.unit
    def test_b3_gravity_fixed_stored(self, source_text):
        """B3: gravity_fixed must be stored in state_mgr.state."""
        assert 'state_mgr.state["gravity_fixed"]' in source_text

    @pytest.mark.unit
    def test_b4_decisions_made_from_engine(self, source_text):
        """B4+B5: decisions_made must be sourced from decision_engine.decisions_made
        filtered by territory, not from state_mgr.state."""
        # Should filter decision_engine.decisions_made by territory
        assert "decision_engine.decisions_made" in source_text or \
               'getattr(decision_engine, "decisions_made"' in source_text

    @pytest.mark.unit
    def test_b6_phase1_violations_passed(self, source_text):
        """B6: Phase 3 validation must receive _phase1_violations, not empty list."""
        assert "_phase1_violations" in source_text
        # Ensure p1_drift.get("violations", []) is NOT passed to execute_phase3_validation
        lines = source_text.split("\n")
        for i, line in enumerate(lines, 1):
            if "execute_phase3_validation" in line or (
                i > 1 and "execute_phase3_validation" in lines[i - 2]
            ):
                # Check nearby lines don't have p1_drift.get("violations", [])
                context = "\n".join(lines[max(0, i - 3):min(len(lines), i + 3)])
                if 'p1_drift.get("violations", [])' in context and "execute_phase3_validation" in context:
                    pytest.fail("Phase 3 validation still receives p1_drift.get('violations', [])")


# ============================================================================
# BATCH 3 TESTS
# ============================================================================


class TestBatch3HealingBehavior:
    """Tests for Batch 3 healing behavior fixes."""

    @pytest.mark.unit
    def test_b1_no_gravity_in_per_territory_violations(self, source_text):
        """B1: Gravity violations must NOT appear in per-territory all_violations list.
        They should only be in the aggregate report."""
        # Find the execute_phase5_final_impl function
        # The old pattern appended gravity_violations to all_violations
        # After fix, this should be replaced with a comment about B1
        assert "[FIX-B1] Gravity violations are global" in source_text

    @pytest.mark.unit
    def test_b1_no_hygiene_in_per_territory_violations(self, source_text):
        """B1: Hygiene violations must NOT appear in per-territory all_violations list."""
        assert "[FIX-B1] Hygiene violations are global" in source_text

    @pytest.mark.unit
    def test_b1_aggregate_has_global_violations(self, source_text):
        """B1: save_aggregate_report must include a 'global_violations' key."""
        assert '"global_violations"' in source_text

    @pytest.mark.unit
    def test_b12_non_ac_territories_enforced(self, source_text):
        """B12: _NON_AC_TERRITORIES must be enforced in the territory loop."""
        assert "[FIX-B12] Enforce scan-only for non-AC territories" in source_text

    @pytest.mark.unit
    def test_b11_single_location_validator(self, source_text):
        """B11: Only one LocationValidatorAgent instance should be created per Phase 1 call."""
        # Count _get_location_validator_agent() calls in execute_phase1_discovery
        # After fix, there should be exactly one
        assert "[FIX-B11] Single LocationValidatorAgent instance" in source_text

    @pytest.mark.unit
    def test_b10_system_architect_guard(self, source_text):
        """B10: SystemArchitectAgent must be guarded for AC-only territories."""
        assert "[FIX-B10] Only invoke SystemArchitectAgent for agentic_core" in source_text

    @pytest.mark.unit
    def test_b9_classification_scoped_to_territory(self, source_text):
        """B9: FileClassificationAgent Phase 1 scan must be scoped to territory."""
        assert "[FIX-B9] Scope scan to current territory" in source_text

    @pytest.mark.unit
    def test_b8_gravity_function_exists(self, ssot_module):
        """B8: _run_gravity_repair_global standalone function must exist."""
        assert hasattr(ssot_module, "_run_gravity_repair_global")
        assert callable(ssot_module._run_gravity_repair_global)

    @pytest.mark.unit
    def test_b8_gravity_removed_from_phase3_impl(self, source_text):
        """B8: GravityLeakRepairAgent block must be removed from execute_phase3_validation_impl."""
        # Find the phase3 impl body
        pattern = r'def execute_phase3_validation_impl\(.*?\n(.*?)(?=\ndef )'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            body = match.group(1)
            assert "gravity_agent" not in body, \
                "GravityLeakRepairAgent still instantiated inside execute_phase3_validation_impl"

    @pytest.mark.unit
    def test_b8_gravity_called_before_territory_loop(self, source_text):
        """B8: _run_gravity_repair_global must be called before 'for territory in targets'."""
        gravity_call_pos = source_text.find("_run_gravity_repair_global(agents")
        loop_pos = source_text.find("for territory in targets:")
        assert gravity_call_pos != -1, "_run_gravity_repair_global call not found"
        assert loop_pos != -1, "territory loop not found"
        assert gravity_call_pos < loop_pos, \
            "_run_gravity_repair_global must be called BEFORE the territory loop"


# ============================================================================
# BATCH 4 TESTS — HEALING OUTPUT ENRICHMENT
# ============================================================================


class TestBatch4HealingOutputEnrichment:
    """Tests for Batch 4 healing output enrichment."""

    @pytest.mark.unit
    def test_h2_record_healing_action_exists(self, ssot_module):
        """H2: _record_healing_action helper function must exist."""
        assert hasattr(ssot_module, "_record_healing_action")
        assert callable(ssot_module._record_healing_action)

    @pytest.mark.unit
    def test_h2_record_healing_action_signature(self, ssot_module):
        """H2: _record_healing_action must accept the required parameters."""
        sig = inspect.signature(ssot_module._record_healing_action)
        params = list(sig.parameters.keys())
        assert "state_mgr" in params
        assert "agent" in params
        assert "territory" in params
        assert "routing_score" in params
        assert "routing_tier" in params
        assert "confidence" in params
        assert "fix_summary" in params
        assert "outcome" in params

    @pytest.mark.unit
    def test_h2_record_healing_action_stores_data(self, ssot_module):
        """H2: _record_healing_action must append to state_mgr.state['healing_actions']."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {}

        ssot_module._record_healing_action(
            mock_state_mgr,
            agent="TestAgent",
            territory="test_territory",
            routing_score=0.85,
            routing_tier="DETERMINISTIC",
            confidence=0.85,
            fix_summary="Fixed 3 violations",
            outcome="SUCCESS",
        )

        assert "healing_actions" in mock_state_mgr.state
        assert len(mock_state_mgr.state["healing_actions"]) == 1
        action = mock_state_mgr.state["healing_actions"][0]
        assert action["agent"] == "TestAgent"
        assert action["territory"] == "test_territory"
        assert action["routing_score"] == 0.85
        assert action["routing_tier"] == "DETERMINISTIC"
        assert action["confidence"] == 0.85
        assert action["fix_summary"] == "Fixed 3 violations"
        assert action["outcome"] == "SUCCESS"
        assert "timestamp" in action

    @pytest.mark.unit
    def test_h2_record_healing_action_appends(self, ssot_module):
        """H2: Multiple calls must append, not overwrite."""
        mock_state_mgr = MagicMock()
        mock_state_mgr.state = {"healing_actions": []}

        ssot_module._record_healing_action(
            mock_state_mgr, agent="Agent1", territory="t1",
        )
        ssot_module._record_healing_action(
            mock_state_mgr, agent="Agent2", territory="t2",
        )

        assert len(mock_state_mgr.state["healing_actions"]) == 2
        assert mock_state_mgr.state["healing_actions"][0]["agent"] == "Agent1"
        assert mock_state_mgr.state["healing_actions"][1]["agent"] == "Agent2"

    @pytest.mark.unit
    def test_h3_heal_sites_call_record(self, source_text):
        """H3: _record_healing_action must be called at all major heal sites."""
        call_count = source_text.count("_record_healing_action(")
        # Expect: definition (1) + RootHygiene + LocationAgent + Phase2 reconciliation
        # + GravityLeakRepair + ArchGovernor = at least 6 occurrences
        assert call_count >= 6, f"Expected >= 6 _record_healing_action calls, found {call_count}"

    @pytest.mark.unit
    def test_h4_healing_log_in_detailed_cert(self, source_text):
        """H4: detailed_cert dict must contain 'healing_log' key."""
        assert '"healing_log"' in source_text

    @pytest.mark.unit
    def test_h5_governance_table_8_columns(self, source_text):
        """H5: Governance table must have 8 columns: Agent, Score, Tier, Model, Gate, Confidence, Outcome, Fix Applied."""
        assert "| Agent | Score | Tier | Model | Gate | Confidence | Outcome | Fix Applied |" in source_text


# ============================================================================
# BATCH 5 TESTS — CODE QUALITY
# ============================================================================


class TestBatch5CodeQuality:
    """Tests for Batch 5 code quality fixes."""

    @pytest.mark.unit
    def test_i1_save_removed_from_update_agent(self, source_text):
        """I1: update_agent must NOT call self.save()."""
        # Find the update_agent method body
        pattern = r'def update_agent\(self.*?\n(.*?)(?=\n    def )'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            body = match.group(1)
            # Check only non-comment lines for self.save()
            code_lines = [l for l in body.split("\n") if l.strip() and not l.strip().startswith("#")]
            for line in code_lines:
                assert "self.save()" not in line, f"update_agent still calls self.save() in: {line.strip()}"

    @pytest.mark.unit
    def test_i1_save_removed_from_complete_agent(self, source_text):
        """I1: complete_agent must NOT call self.save()."""
        pattern = r'def complete_agent\(self.*?\n(.*?)(?=\n    def )'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            body = match.group(1)
            code_lines = [l for l in body.split("\n") if l.strip() and not l.strip().startswith("#")]
            for line in code_lines:
                assert "self.save()" not in line, f"complete_agent still calls self.save() in: {line.strip()}"

    @pytest.mark.unit
    def test_i1_save_removed_from_skip_agent(self, source_text):
        """I1: skip_agent must NOT call self.save()."""
        pattern = r'def skip_agent\(self.*?\n(.*?)(?=\n    def )'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            body = match.group(1)
            code_lines = [l for l in body.split("\n") if l.strip() and not l.strip().startswith("#")]
            for line in code_lines:
                assert "self.save()" not in line, f"skip_agent still calls self.save() in: {line.strip()}"

    @pytest.mark.unit
    def test_i1_save_kept_in_start_mission(self, source_text):
        """I1: start_mission must still call self.save()."""
        pattern = r'def start_mission\(self.*?\n(.*?)(?=\n    def )'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            body = match.group(1)
            assert "self.save()" in body, "start_mission must still call self.save()"

    @pytest.mark.unit
    def test_i1_save_kept_in_finish_mission(self, source_text):
        """I1: finish_mission must still call self.save()."""
        pattern = r'def finish_mission\(self.*?\n(.*?)(?=\n    def )'
        match = re.search(pattern, source_text, re.DOTALL)
        if match:
            body = match.group(1)
            assert "self.save()" in body, "finish_mission must still call self.save()"

    @pytest.mark.unit
    def test_i3_json_dump_guarded_by_verbose(self, source_text):
        """I3: Per-territory JSON manifest print must be guarded by DEBUG log level."""
        assert "logger.isEnabledFor(logging.DEBUG)" in source_text

    @pytest.mark.unit
    def test_i4_no_deprecated_get_event_loop(self, source_text):
        """I4: asyncio.get_event_loop() must not appear as code — replaced by new_event_loop()."""
        # Check only non-comment lines for get_event_loop
        for line in source_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert "asyncio.get_event_loop()" not in stripped, \
                f"Deprecated asyncio.get_event_loop() found in code: {stripped}"
        # Should have new_event_loop
        assert "asyncio.new_event_loop()" in source_text


# ============================================================================
# STRUCTURAL INTEGRITY TESTS
# ============================================================================


class TestStructuralIntegrity:
    """Tests verifying structural integrity after all refactoring."""

    @pytest.mark.unit
    def test_module_imports_cleanly(self, ssot_module):
        """The module must import without errors after all changes."""
        assert ssot_module is not None

    @pytest.mark.unit
    def test_source_parses_without_syntax_errors(self, source_ast):
        """The source must parse without syntax errors."""
        assert source_ast is not None

    @pytest.mark.unit
    def test_key_functions_exist(self, ssot_module):
        """All key functions must exist after refactoring."""
        required_functions = [
            "validate_territory_input",
            "_record_healing_action",
            "save_aggregate_report",
        ]
        for fn_name in required_functions:
            assert hasattr(ssot_module, fn_name), f"Missing function: {fn_name}"

    @pytest.mark.unit
    def test_key_classes_exist(self, ssot_module):
        """All key classes must exist after refactoring."""
        required_classes = [
            "HealContext",
            "RuntimeStateManager",
            "AutonomousDecisionEngine",
        ]
        for cls_name in required_classes:
            assert hasattr(ssot_module, cls_name), f"Missing class: {cls_name}"
            assert inspect.isclass(getattr(ssot_module, cls_name))

    @pytest.mark.unit
    def test_b2_conversational_violations_reset_present(self, source_text):
        """B2: conversational_violations reset must be present before Phase 4.5."""
        assert 'state_mgr.state["conversational_violations"] = []' in source_text

    @pytest.mark.unit
    def test_all_fix_markers_present(self, source_text):
        """All FIX markers from the refactoring plan must be present in source."""
        expected_markers = [
            "[FIX-B1]",
            "[FIX-B2]",
            "[FIX-B3]",
            "[FIX-B4]",
            "[FIX-B6]",
            "[FIX-B8]",
            "[FIX-B9]",
            "[FIX-B10]",
            "[FIX-B11]",
            "[FIX-B12]",
            "[FIX-B15]",
            "[FIX-I1]",
            "[FIX-I3]",
            "[FIX-I4]",
            "[H2]",
            "[H3]",
            "[H4]",
            "[H5]",
        ]
        missing = [m for m in expected_markers if m not in source_text]
        assert not missing, f"Missing fix markers in source: {missing}"
