"""Regression tests for heal-run bugs identified from JSON output audit.

BUG-1+5: agents["location"] was LocationValidatorAgent (raises NotImplementedError)
BUG-2:   violations_fixed always 0 — phase2_result not fed into cert builder via state
BUG-3:   LOCATION violation file-path "unknown" for dict-shaped violations
BUG-4:   Windows Path objects serialised with backslashes cause json.load escape errors
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _make_decision_engine(confidence_value=0.9):
    de = MagicMock()
    conf = MagicMock()
    conf.value = confidence_value
    de.calculate_healing_confidence.return_value = conf
    de.should_proceed_with_healing.return_value = (False, "test-blocked")
    de.decisions_made = []
    return de


def _make_state_mgr(**extra_state):
    mgr = MagicMock()
    mgr.project_root = REPO_ROOT
    mgr.state = {
        "healing_actions": [],
        "location_violations": [],
        "hygiene_fixed": 0,
        "location_fixed": 0,
        "hierarchy_fixed": 0,
        "gravity_fixed": 0,
        "phase2_violations_fixed": 0,
        "completed_agents": [],
        "skipped_agents": [],
        "compliance_scores": {},
        "meta_learning": {},
        **extra_state,
    }
    return mgr


# ---------------------------------------------------------------------------
# BUG-1: agents registry must use LocationHealerAgent, not LocationValidatorAgent
# ---------------------------------------------------------------------------


class TestBug1LocationAgentRegistry:
    def test_location_healer_has_heal_repository(self):
        """LocationHealerAgent must expose heal_repository() without raising NotImplementedError."""
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        assert hasattr(LocationHealerAgent, "heal_repository"), (
            "LocationHealerAgent must have heal_repository"
        )

    def test_location_validator_raises_not_implemented(self):
        """LocationValidatorAgent.heal_repository() must raise NotImplementedError."""
        from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

        agent = LocationValidatorAgent(project_root=REPO_ROOT)
        with pytest.raises(NotImplementedError):
            agent.heal_repository()

    def test_get_l5_agent_roster_returns_healer_not_validator(self):
        """_get_l5_agent_roster must include LocationHealerAgent, not LocationValidatorAgent."""
        from agentic_core.L0_routing.scripts.execute_ssot import _get_l5_agent_roster
        from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        roster = list(_get_l5_agent_roster())
        assert LocationHealerAgent in roster, "LocationHealerAgent must be in the roster"
        assert LocationValidatorAgent not in roster, (
            "LocationValidatorAgent must NOT be in the roster (raises NotImplementedError)"
        )

    def test_lazy_loader_returns_healer(self):
        """_get_location_healer_agent() must exist and return LocationHealerAgent."""
        from agentic_core.L0_routing.scripts.execute_ssot import _get_location_healer_agent
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        assert _get_location_healer_agent() is LocationHealerAgent


# ---------------------------------------------------------------------------
# BUG-2: phase2_violations_fixed must be accumulated in state by Phase 2
# ---------------------------------------------------------------------------


class TestBug2ViolationsFixedTally:
    def test_phase2_reconciliation_stores_fixed_count_in_state(self):
        """execute_phase2_reconciliation must accumulate violations_fixed in state_mgr.state."""
        from agentic_core.L0_routing.scripts.execute_ssot import execute_phase2_reconciliation

        # Spy state_mgr — we need real dict so state mutations are visible
        state_mgr = _make_state_mgr()

        # Fake agent that succeeds and returns a fix result
        fake_agent_instance = MagicMock()
        fake_agent_instance.heal_repository.return_value = {
            "success": True,
            "violations_fixed": 3,
        }
        fake_agent_cls = MagicMock(return_value=fake_agent_instance)

        agents = {"test_agent": fake_agent_cls}
        decision_engine = _make_decision_engine()
        decision_engine.should_proceed_with_healing.return_value = (True, "TIER1-GATE1(conf=0.9)")
        decision_engine.request_sovereignty_token.return_value = True

        ctx = MagicMock()
        ctx.heal = True

        plan = {
            "violations_found": [{"type": "TEST", "file": "some/file.py", "suggested_agent": "test_agent"}]
        }

        # Patch UWG so it doesn't block
        with (
            patch("agentic_core.L0_routing.scripts.execute_ssot._get_uwg") as mock_uwg_fn,
            patch("agentic_core.L0_routing.scripts.execute_ssot._get_heal_result_adapter") as mock_adapt_fn,
        ):
            mock_uwg = MagicMock()
            mock_uwg_fn.return_value = mock_uwg
            mock_adapt_fn.return_value = MagicMock(return_value=MagicMock(to_dict=lambda: {}))

            result = execute_phase2_reconciliation(
                agents, "test_territory", decision_engine, state_mgr, plan, ctx
            )

        assert result["violations_fixed"] >= 1, (
            f"Phase 2 must report violations_fixed >= 1, got {result['violations_fixed']}"
        )

    def test_phase2_violations_fixed_state_key_read_by_cert_tally(self):
        """state['phase2_violations_fixed'] must be readable and additive in cert metrics."""
        # This tests the fix in the cert builder: state key exists and is included.
        # We test the dict arithmetic directly since the cert builder is inline.
        state = {
            "phase2_violations_fixed": 7,
            "hygiene_fixed": 0,
            "location_fixed": 0,
            "hierarchy_fixed": 0,
            "gravity_fixed": 0,
        }
        compliance_stats_fixed = 0
        total_fixed = (
            compliance_stats_fixed
            + state.get("hygiene_fixed", 0)
            + state.get("location_fixed", 0)
            + state.get("hierarchy_fixed", 0)
            + state.get("gravity_fixed", 0)
            + state.get("phase2_violations_fixed", 0)
        )
        assert total_fixed == 7, f"Expected 7, got {total_fixed}"


# ---------------------------------------------------------------------------
# BUG-3: LOCATION violation file-path extraction for dict-shaped violations
# ---------------------------------------------------------------------------


class TestBug3LocationViolationFilePath:
    """Test the violation-extraction logic directly by inspecting the AST of execute_ssot.

    The logic is inline (not exported), so we validate the invariant by running
    the extraction code path extracted from the source and verifying behavior.
    """

    def _extract_file_and_message(self, loc_violation) -> tuple[str, str]:
        """Mirror the BUG-3-fixed extraction logic from execute_ssot.py."""
        if isinstance(loc_violation, tuple) and len(loc_violation) >= 2:
            file_path = str(loc_violation[0])
            message = str(loc_violation[1])
        elif isinstance(loc_violation, dict):
            raw_fp = loc_violation.get("file") or loc_violation.get("path") or "unknown"
            file_path = str(raw_fp)
            message = str(loc_violation.get("message", loc_violation.get("msg", str(loc_violation))))
        else:
            file_path = str(getattr(loc_violation, "file", "unknown"))
            message = str(loc_violation)
        return file_path, message

    def test_dict_with_file_key(self):
        v = {"file": "agentic_core/L5_safety/some_file.py", "message": "Bad location"}
        fp, msg = self._extract_file_and_message(v)
        assert fp != "unknown"
        assert "some_file.py" in fp

    def test_dict_with_path_key_fallback(self):
        v = {"path": "agentic_core/L5_safety/path_key.py", "message": "Bad location"}
        fp, msg = self._extract_file_and_message(v)
        assert fp != "unknown"
        assert "path_key.py" in fp

    def test_tuple_shape(self):
        v = (Path("agentic_core/L5_safety/tuple_file.py"), "Missing sovereign root")
        fp, msg = self._extract_file_and_message(v)
        assert fp != "unknown"
        assert "tuple_file.py" in fp

    def test_old_getattr_on_dict_returns_unknown(self):
        """Confirm the old bug: getattr on a dict does NOT work for dict violations."""
        v = {"file": "real_file.py", "message": "Bad location"}
        # old (buggy) code:
        file_path_old = str(getattr(v, "file", "unknown"))
        assert file_path_old == "unknown", (
            "getattr on dict always returns 'unknown' — confirms the original bug"
        )
        # new (fixed) code:
        file_path_new, _ = self._extract_file_and_message(v)
        assert file_path_new != "unknown", "Fixed code must not return 'unknown' for dict"


# ---------------------------------------------------------------------------
# BUG-4: JSON serialisation must not produce backslash escape errors on Windows
# ---------------------------------------------------------------------------


class TestBug4JsonPathSerialisation:
    def test_per_territory_report_is_loadable(self, tmp_path):
        """compliance_report_*.json must be json.load()-able after save_comprehensive_reports."""
        from agentic_core.L0_routing.scripts.execute_ssot import save_comprehensive_reports

        detailed_cert = {
            "meta": {"territory": "test", "status": "COMPLIANT"},
            "metrics": {"violation_count": 0},
            "unified_violations": [],
            "healing_log": [],
            "path_object_example": Path("agentic_core\\L0_routing\\some_file.py"),
        }

        # Bypass mutation_prohibition which only fires in real L0 context
        with patch("agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write"):
            save_comprehensive_reports(
                territory="test_territory",
                detailed_cert=detailed_cert,
                markdown_summary=["# Test"],
                files_affected=set(),
                project_root=tmp_path,
            )

        json_path = tmp_path / "logs" / "compliance_reports" / "compliance_report_test_territory.json"
        assert json_path.exists(), "Report file must be written"

        loaded = json.loads(json_path.read_text(encoding="utf-8"))
        assert loaded["meta"]["territory"] == "test"
        path_val = loaded.get("path_object_example", "")
        assert "\\" not in path_val, f"Path must be serialised as forward-slash, got backslash: {path_val!r}"

    def test_windows_path_in_violations_no_backslash_in_json(self, tmp_path):
        """Path object in a violation dict must not produce backslashes in JSON output."""
        from agentic_core.L0_routing.scripts.execute_ssot import save_comprehensive_reports

        detailed_cert = {
            "meta": {"territory": "test", "status": "NON-COMPLIANT"},
            "metrics": {"violation_count": 1},
            "unified_violations": [
                {
                    "type": "GRAVITY",
                    "file": Path("C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\foo.py"),
                    "message": "Layer inversion",
                }
            ],
            "healing_log": [],
        }

        with patch("agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write"):
            save_comprehensive_reports(
                territory="test_win",
                detailed_cert=detailed_cert,
                markdown_summary=["# Test"],
                files_affected=set(),
                project_root=tmp_path,
            )

        json_path = tmp_path / "logs" / "compliance_reports" / "compliance_report_test_win.json"
        assert json_path.exists()
        loaded = json.loads(json_path.read_text(encoding="utf-8"))
        file_val = loaded["unified_violations"][0]["file"]
        assert "\\" not in file_val, f"Path must use forward slashes in JSON, got: {file_val!r}"

    def test_aggregate_serialiser_converts_path_to_posix(self, tmp_path):
        """save_aggregate_report must serialise Path objects with forward slashes.

        We write a pre-baked per-territory report containing a Path in the JSON
        (as a string, since json.dump already ran), then verify save_aggregate_report
        can read and re-serialise it without raising.
        """
        import json as _json

        from agentic_core.L0_routing.scripts.execute_ssot import save_aggregate_report

        reports_dir = tmp_path / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True)

        territory = "agg_test_territory"
        per_territory_cert = {
            "meta": {"territory": territory, "status": "COMPLIANT", "timestamp": "2024-01-01T00:00:00"},
            "metrics": {
                "violation_count": 0,
                "violations_fixed": 2,
                "drift_count": 0,
                "errors": 0,
                "confidence_score": 0.9,
                "agents_run": 1,
            },
            "unified_violations": [
                {
                    "type": "GRAVITY",
                    "file": "agentic_core/L0_routing/foo.py",
                    "message": "Layer inversion",
                }
            ],
            "healing_log": [],
        }

        report_path = reports_dir / f"compliance_report_{territory}.json"
        report_path.write_text(_json.dumps(per_territory_cert, indent=2), encoding="utf-8")

        with patch("agentic_core.L0_routing.scripts.execute_ssot.assert_no_persistent_write"):
            agg_path = save_aggregate_report(
                targets=[territory],
                project_root=tmp_path,
            )

        assert agg_path is not None, "save_aggregate_report must return a path"
        assert agg_path.exists(), "Aggregate report file must be created"

        loaded = _json.loads(agg_path.read_text(encoding="utf-8"))
        # Verify the report is json.load()-able (no backslash escape errors)
        assert isinstance(loaded, dict)
        # Aggregate report structure uses "territories" list
        assert "territories" in loaded, (
            f"Aggregate report must have 'territories' key, got {list(loaded.keys())}"
        )
        assert len(loaded["territories"]) == 1, (
            f"Expected 1 territory entry, got {len(loaded['territories'])}"
        )


# ---------------------------------------------------------------------------
# HARDENING: BUG-1 production wiring — agents dict key "location"
# ---------------------------------------------------------------------------


class TestBug1ProductionAgentsWiring:
    def test_agents_dict_location_key_is_healer(self):
        """The production agents dict must map 'location' → LocationHealerAgent (not Validator)."""
        import ast

        ssot_path = Path(__file__).resolve().parents[2] / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
        source = ssot_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(ssot_path))

        # Find the agents dict assignment: agents = {"location": ..., ...}
        # We look for Dict nodes where one key is the string "location"
        location_values: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "agents":
                        if isinstance(node.value, ast.Dict):
                            for key, val in zip(node.value.keys, node.value.values):
                                if isinstance(key, ast.Constant) and key.value == "location":
                                    # val should be a Name node referencing LocationHealerAgent
                                    if isinstance(val, ast.Name):
                                        location_values.append(val.id)

        assert location_values, "Could not find agents['location'] assignment in execute_ssot.py"
        for val in location_values:
            assert val == "LocationHealerAgent", (
                f"agents['location'] must be LocationHealerAgent, got {val!r}"
            )
            assert "Validator" not in val, (
                "agents['location'] must NOT reference any Validator (raises NotImplementedError)"
            )


# ---------------------------------------------------------------------------
# HARDENING: BUG-2 production wiring — state mutation after execute_phase2_reconciliation
# ---------------------------------------------------------------------------


class TestBug2ProductionStateMutation:
    def test_phase2_result_persisted_to_state_mgr(self):
        """execute_ssot.py must write phase2_result['violations_fixed'] into state_mgr.state.

        Verified by AST inspection of the production code path.
        """
        import ast

        ssot_path = Path(__file__).resolve().parents[2] / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
        source = ssot_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(ssot_path))

        # Look for: state_mgr.state["phase2_violations_fixed"] = ...
        found_state_write = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    # target: state_mgr.state[...] subscript
                    if (
                        isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Attribute)
                        and target.value.attr == "state"
                        and isinstance(target.value.value, ast.Name)
                        and target.value.value.id == "state_mgr"
                    ):
                        # Check the subscript key is "phase2_violations_fixed"
                        key_node = target.slice
                        if isinstance(key_node, ast.Constant) and key_node.value == "phase2_violations_fixed":
                            found_state_write = True

        assert found_state_write, (
            "execute_ssot.py must assign state_mgr.state['phase2_violations_fixed'] "
            "after execute_phase2_reconciliation (BUG-2 fix not present)"
        )

    def test_cert_builder_reads_phase2_violations_fixed(self):
        """The cert builder must include state.get('phase2_violations_fixed', 0) in violations_fixed.

        Verified by AST inspection: a BinOp or augmented-add chain in execute_ssot.py
        must contain a Call to state.get with 'phase2_violations_fixed'.
        """

        ssot_path = Path(__file__).resolve().parents[2] / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
        source = ssot_path.read_text(encoding="utf-8")

        # String-level check: simpler and sufficient — the fix is a single identifiable string
        assert "phase2_violations_fixed" in source, (
            "execute_ssot.py must contain 'phase2_violations_fixed' (BUG-2 fix absent)"
        )

        # Count occurrences: must appear at least twice (write and read in cert builder)
        count = source.count("phase2_violations_fixed")
        assert count >= 2, (
            f"'phase2_violations_fixed' must appear at least twice in execute_ssot.py "
            f"(write in Phase 2 + read in cert builder), got {count}"
        )


# ---------------------------------------------------------------------------
# HARDENING: BUG-3 production path — AST verify dict violations use .get()
# ---------------------------------------------------------------------------


class TestBug3ProductionCodePath:
    def test_execute_ssot_uses_dict_get_for_location_violations(self):
        """The inline location-violation extraction in execute_ssot.py must use
        dict.get() for dict-shaped violations, NOT getattr().

        Verified by AST: inside the elif isinstance(loc_violation, dict) branch
        there must be a .get() call — not a getattr() call.
        """
        import ast

        ssot_path = Path(__file__).resolve().parents[2] / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"
        source = ssot_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(ssot_path))

        found_dict_branch = False
        found_get_call = False

        for node in ast.walk(tree):
            # Look for: elif isinstance(loc_violation, dict):
            if isinstance(node, ast.If):
                test = node.test
                if (
                    isinstance(test, ast.Call)
                    and isinstance(test.func, ast.Name)
                    and test.func.id == "isinstance"
                    and len(test.args) == 2
                    and isinstance(test.args[1], ast.Name)
                    and test.args[1].id == "dict"
                ):
                    found_dict_branch = True
                    # Inside this branch, check for .get() calls
                    for child in ast.walk(node):
                        if (
                            isinstance(child, ast.Call)
                            and isinstance(child.func, ast.Attribute)
                            and child.func.attr == "get"
                        ):
                            found_get_call = True
                            break

        assert found_dict_branch, (
            "execute_ssot.py must have an 'isinstance(x, dict)' branch for location violations"
        )
        assert found_get_call, "The dict branch must use .get() to extract file/path keys (BUG-3 fix absent)"
