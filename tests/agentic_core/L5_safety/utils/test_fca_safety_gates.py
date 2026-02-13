"""
Tests for FCA Safety Gates: collision prevention, blast radius limiting,
mass action guards, AST-based agent detection, observability hardening,
nested LCD policy, deterministic plan output, and wave execution API.

Covers: WAVE 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2
"""

from __future__ import annotations

import json
import textwrap

from agentic_core.L5_safety.utils._fca_safety_gates import (
    MAX_ACTIONS_DEFAULT,
    NestedLCDPolicy,
    PlannedAction,
    WaveConfig,
    build_execution_plan,
    build_import_graph,
    check_import_impact,
    check_init_reexports,
    check_mass_action,
    check_nested_lcd_with_policy,
    check_observability_violation,
    check_rename_collisions,
    detect_agent_lineage,
    filter_actions_for_wave,
    run_all_safety_gates,
)

# ============================================================================
# WAVE 1.1 — Rename Collision Gate
# ============================================================================


class TestRenameCollisionGate:
    """WAVE 1.1: Collision-prevention gate for renames."""

    def test_no_collisions_clean_map(self):
        """Clean rename map produces no collisions."""
        rename_map = {
            "agentic_core/foo.py": "agentic_core/foo_util.py",
            "agentic_core/bar.py": "agentic_core/bar_types.py",
        }
        existing = {"agentic_core/foo.py", "agentic_core/bar.py", "agentic_core/baz.py"}
        collisions = check_rename_collisions(rename_map, existing, case_sensitive=False)
        assert collisions == []

    def test_two_files_same_destination(self):
        """Two source files mapping to the same proposed destination."""
        rename_map = {
            "a/config_loader.py": "a/config_loader_util.py",
            "b/config_loader.py": "a/config_loader_util.py",
        }
        existing = {"a/config_loader.py", "b/config_loader.py"}
        collisions = check_rename_collisions(rename_map, existing, case_sensitive=False)
        assert len(collisions) >= 1
        types = {c["type"] for c in collisions}
        assert "DST_COLLISION" in types

    def test_destination_already_exists(self):
        """Destination file already present on disk."""
        rename_map = {
            "agentic_core/old_name.py": "agentic_core/existing_target.py",
        }
        existing = {"agentic_core/old_name.py", "agentic_core/existing_target.py"}
        collisions = check_rename_collisions(rename_map, existing, case_sensitive=False)
        assert len(collisions) >= 1
        types = {c["type"] for c in collisions}
        assert "DST_EXISTS" in types

    def test_casing_only_conflict_case_insensitive(self):
        """Case-insensitive FS: FooAgent.py vs fooagent.py detected."""
        rename_map = {
            "agentic_core/old.py": "agentic_core/FooAgent.py",
        }
        existing = {"agentic_core/old.py", "agentic_core/fooagent.py"}
        collisions = check_rename_collisions(rename_map, existing, case_sensitive=False)
        assert len(collisions) >= 1
        types = {c["type"] for c in collisions}
        assert "CASING_CONFLICT" in types or "DST_EXISTS" in types

    def test_casing_conflict_not_on_case_sensitive_fs(self):
        """Case-sensitive FS: FooAgent.py vs fooagent.py is NOT a conflict."""
        rename_map = {
            "agentic_core/old.py": "agentic_core/FooAgent.py",
        }
        existing = {"agentic_core/old.py", "agentic_core/fooagent.py"}
        collisions = check_rename_collisions(rename_map, existing, case_sensitive=True)
        # No CASING_CONFLICT on case-sensitive FS
        casing = [c for c in collisions if c["type"] == "CASING_CONFLICT"]
        assert len(casing) == 0

    def test_self_rename_not_collision(self):
        """Renaming a file to itself (no-op) is not a collision."""
        rename_map = {
            "agentic_core/foo.py": "agentic_core/foo.py",
        }
        existing = {"agentic_core/foo.py"}
        collisions = check_rename_collisions(rename_map, existing, case_sensitive=False)
        assert collisions == []


# ============================================================================
# WAVE 1.2 — Import Impact Gate
# ============================================================================


class TestImportImpactGate:
    """WAVE 1.2: Blast radius limiter via import graph."""

    def test_low_impact_passes(self, tmp_path):
        """Module with few importers passes the gate."""
        # Create a simple module graph
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "b.py").write_text("import a\n")
        (tmp_path / "c.py").write_text("import a\n")

        files = list(tmp_path.glob("*.py"))
        counts = build_import_graph(files, tmp_path)

        rename_map = {"a.py": "a_util.py"}
        blocked = check_import_impact(
            rename_map,
            counts,
            files,
            tmp_path,
            max_import_impact=25,
        )
        assert len(blocked) == 0

    def test_high_impact_blocks(self, tmp_path):
        """Module imported by many files is blocked."""
        # Create a heavily-imported module
        (tmp_path / "core.py").write_text("x = 1\n")
        for i in range(30):
            (tmp_path / f"consumer_{i}.py").write_text("import core\n")

        files = list(tmp_path.glob("*.py"))
        counts = build_import_graph(files, tmp_path)

        rename_map = {"core.py": "core_util.py"}
        blocked = check_import_impact(
            rename_map,
            counts,
            files,
            tmp_path,
            max_import_impact=25,
        )
        assert len(blocked) == 1
        assert blocked[0]["type"] == "BLOCKED_HIGH_IMPACT"
        assert blocked[0]["total_impact"] > 25

    def test_init_reexport_bonus(self, tmp_path):
        """__init__.py re-export adds +10 impact."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "module.py").write_text("class Foo: pass\n")
        (pkg / "__init__.py").write_text("from .module import Foo\n")

        bonus = check_init_reexports(pkg / "module.py")
        assert bonus == 10

    def test_no_init_reexport(self, tmp_path):
        """No __init__.py re-export means 0 bonus."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "module.py").write_text("class Foo: pass\n")
        (pkg / "__init__.py").write_text("# empty\n")

        bonus = check_init_reexports(pkg / "module.py")
        assert bonus == 0


# ============================================================================
# WAVE 1.3 — Mass Action Guard
# ============================================================================


class TestMassActionGuard:
    """WAVE 1.3: No mass action guardrail."""

    def test_under_threshold_passes(self):
        """Actions under threshold pass."""
        result = check_mass_action(30, max_actions=50)
        assert result is None

    def test_at_threshold_passes(self):
        """Exactly at threshold passes."""
        result = check_mass_action(50, max_actions=50)
        assert result is None

    def test_over_threshold_blocks(self):
        """51 actions without force blocks."""
        result = check_mass_action(51, max_actions=50)
        assert result is not None
        assert result["type"] == "ABORTED_MASS_ACTION"

    def test_force_without_wave_id_blocks(self):
        """force=True but no wave_id still blocks."""
        result = check_mass_action(51, max_actions=50, force=True, wave_id=None)
        assert result is not None
        assert "wave_id" in result["reason"]

    def test_force_with_wave_id_passes(self):
        """force=True + wave_id allows override."""
        result = check_mass_action(
            100,
            max_actions=50,
            force=True,
            wave_id="wave-001-renames",
        )
        assert result is None

    def test_default_threshold(self):
        """Default threshold is 50."""
        assert MAX_ACTIONS_DEFAULT == 50


# ============================================================================
# WAVE 2.1 — AST-based Agent Lineage Detection
# ============================================================================


class TestAgentLineageDetection:
    """WAVE 2.1: Agent detection uses AST lineage, not just name."""

    def test_confirmed_agent_with_base(self, tmp_path):
        """class Foo(SovereignBaseAgent) => AGENT."""
        p = tmp_path / "FooAgent.py"
        p.write_text(
            textwrap.dedent("""\
            class FooAgent(SovereignBaseAgent):
                pass
        """),
        )
        assert detect_agent_lineage(p) == "AGENT"

    def test_confirmed_agent_with_suffix_base(self, tmp_path):
        """class Foo(SomeBaseAgent) => AGENT (suffix match)."""
        p = tmp_path / "BarAgent.py"
        p.write_text(
            textwrap.dedent("""\
            class BarAgent(SomeBaseAgent):
                pass
        """),
        )
        assert detect_agent_lineage(p) == "AGENT"

    def test_agent_name_no_lineage_is_uncertain(self, tmp_path):
        """class FooAgent(Thing) where Thing is not a known base => UNCERTAIN."""
        p = tmp_path / "FooAgent.py"
        p.write_text(
            textwrap.dedent("""\
            class FooAgent(SomeRandomMixin):
                pass
        """),
        )
        assert detect_agent_lineage(p) == "AGENT_DETECTION_UNCERTAIN"

    def test_non_agent_file(self, tmp_path):
        """Regular utility class => NOT_AGENT."""
        p = tmp_path / "helper_util.py"
        p.write_text(
            textwrap.dedent("""\
            class HelperUtil:
                pass
        """),
        )
        assert detect_agent_lineage(p) == "NOT_AGENT"

    def test_orchestrator_detection(self, tmp_path):
        """class FooOrchestrator(...) => ORCHESTRATOR."""
        p = tmp_path / "FooOrchestrator.py"
        p.write_text(
            textwrap.dedent("""\
            class FooOrchestrator:
                pass
        """),
        )
        assert detect_agent_lineage(p) == "ORCHESTRATOR"

    def test_executor_detection(self, tmp_path):
        """class BarExecutor(...) => EXECUTOR."""
        p = tmp_path / "BarExecutor.py"
        p.write_text(
            textwrap.dedent("""\
            class BarExecutor:
                pass
        """),
        )
        assert detect_agent_lineage(p) == "EXECUTOR"

    def test_agent_inheriting_from_agent(self, tmp_path):
        """class SubAgent(ParentAgent) => AGENT (transitive)."""
        p = tmp_path / "SubAgent.py"
        p.write_text(
            textwrap.dedent("""\
            class SubAgent(ParentAgent):
                pass
        """),
        )
        assert detect_agent_lineage(p) == "AGENT"

    def test_syntax_error_returns_not_agent(self, tmp_path):
        """File with syntax error => NOT_AGENT (graceful)."""
        p = tmp_path / "broken.py"
        p.write_text("class Broken(\n")
        assert detect_agent_lineage(p) == "NOT_AGENT"


# ============================================================================
# WAVE 2.2 — Observability Detection (Import-based)
# ============================================================================


class TestObservabilityDetection:
    """WAVE 2.2: Observability detection not keyword-only."""

    def test_l0_dashboard_script_not_flagged(self, tmp_path):
        """L0 maintenance script with 'dashboard' in name but no obs imports => NOT flagged."""
        p = tmp_path / "audit_dashboard_util.py"
        p.write_text("import json\nprint('audit')\n")
        parts = ("agentic_core", "L0_routing", "scripts", "audit_dashboard_util.py")
        result = check_observability_violation(p, parts=parts)
        assert result is None

    def test_non_l6_with_obs_import_flagged(self, tmp_path):
        """Non-L6 module importing prometheus_client => flagged."""
        p = tmp_path / "metric_reporter.py"
        p.write_text("import prometheus_client\nclass Reporter: pass\n")
        parts = ("agentic_core", "L2_execution", "utils", "metric_reporter.py")
        result = check_observability_violation(p, parts=parts)
        assert result is not None
        assert result["violation"] == "OBSERVABILITY_OUTSIDE_L6"
        assert "prometheus_client" in result["imports"]

    def test_l6_module_not_flagged(self, tmp_path):
        """Module inside L6_observability is never flagged."""
        p = tmp_path / "dashboard_util.py"
        p.write_text("import prometheus_client\n")
        parts = ("agentic_core", "L6_observability", "utils", "dashboard_util.py")
        result = check_observability_violation(p, parts=parts)
        assert result is None

    def test_no_obs_import_not_flagged(self, tmp_path):
        """Non-L6 module with no observability imports => NOT flagged."""
        p = tmp_path / "telemetry_util.py"
        p.write_text("import json\nclass Telemetry: pass\n")
        parts = ("agentic_core", "L4_state", "utils", "telemetry_util.py")
        result = check_observability_violation(p, parts=parts)
        assert result is None


# ============================================================================
# WAVE 2.3 — Nested LCD Subtree Policy
# ============================================================================


class TestNestedLCDPolicy:
    """WAVE 2.3: Configurable nested LCD subtree detection."""

    @staticmethod
    def _mock_validate(parts):
        """Mock validate_no_nested_lcd that flags 'runtime/config' as nested."""
        if "runtime" in parts and "config" in parts:
            return {
                "violation": "NESTED_LCD_SUBTREE",
                "domain": "runtime",
                "subfolder": "config",
                "message": "Leaf domain 'runtime' must not sprout LCD subfolder 'config/'.",
            }
        return None

    def test_strict_false_produces_warning(self):
        """strict=False => severity=WARN, executable=False."""
        parts = ("agentic_core", "runtime", "config", "foo_config.py")
        policy = NestedLCDPolicy(strict_lcd_roots_only=False)
        result = check_nested_lcd_with_policy(parts, self._mock_validate, policy)
        assert result is not None
        assert result["severity"] == "WARN"
        assert result["executable"] is False

    def test_strict_true_produces_violation(self):
        """strict=True => severity=VIOLATION, executable=True."""
        parts = ("agentic_core", "runtime", "config", "foo_config.py")
        policy = NestedLCDPolicy(strict_lcd_roots_only=True)
        result = check_nested_lcd_with_policy(parts, self._mock_validate, policy)
        assert result is not None
        assert result["severity"] == "VIOLATION"
        assert result["executable"] is True

    def test_no_violation_returns_none(self):
        """No nested LCD => None regardless of policy."""
        parts = ("agentic_core", "L5_safety", "config", "foo_config.py")
        policy = NestedLCDPolicy(strict_lcd_roots_only=True)
        result = check_nested_lcd_with_policy(parts, self._mock_validate, policy)
        assert result is None


# ============================================================================
# WAVE 3.1 — Deterministic Staged Plan Output
# ============================================================================


class TestDeterministicPlanOutput:
    """WAVE 3.1: Stable, machine-readable plan output."""

    def test_plan_is_sorted(self):
        """Actions are sorted by (action_type, src)."""
        actions = [
            PlannedAction("TERRITORY_MOVE", "z/foo.py", "z/utils/foo.py", "TERRITORY"),
            PlannedAction("DETECT_RENAME", "a/bar.py", "a/bar_util.py", "NAMING"),
            PlannedAction("DETECT_RENAME", "a/aaa.py", "a/aaa_util.py", "NAMING"),
        ]
        plan = build_execution_plan(actions)
        srcs = [a["src"] for a in plan["planned_actions"]]
        assert srcs == ["a/aaa.py", "a/bar.py", "z/foo.py"]

    def test_plan_counts_blocked(self):
        """Blocked actions counted correctly."""
        actions = [
            PlannedAction("RENAME", "a.py", "b.py", "NAMING", blocked_reason=None),
            PlannedAction("RENAME", "c.py", "d.py", "NAMING", blocked_reason="COLLISION"),
            PlannedAction("RENAME", "e.py", "f.py", "NAMING", blocked_reason="HIGH_IMPACT"),
        ]
        plan = build_execution_plan(actions)
        assert plan["total"] == 3
        assert plan["blocked"] == 2
        assert plan["executable"] == 1

    def test_plan_is_json_serializable(self):
        """Plan output can be serialized to JSON."""
        actions = [
            PlannedAction("RENAME", "a.py", "b.py", "NAMING", impact_score=5),
        ]
        plan = build_execution_plan(actions)
        json_str = json.dumps(plan)
        parsed = json.loads(json_str)
        assert parsed["total"] == 1

    def test_empty_plan(self):
        """Empty action list produces valid plan."""
        plan = build_execution_plan([])
        assert plan["total"] == 0
        assert plan["blocked"] == 0
        assert plan["executable"] == 0


# ============================================================================
# WAVE 3.2 — Wave Execution API
# ============================================================================


class TestWaveExecutionAPI:
    """WAVE 3.2: Scoped wave execution with type filtering and limits."""

    def test_filters_by_action_type(self):
        """Only allowed action types are included."""
        actions = [
            PlannedAction("FORBIDDEN_RENAME", "a.py", "b.py", "R1"),
            PlannedAction("CONFIG_SUFFIX_RENAME", "c.py", "d.py", "R2"),
            PlannedAction("TERRITORY_MOVE", "e.py", "f.py", "R3"),
        ]
        wave = WaveConfig(
            wave_id="wave-001",
            allow_action_types={"FORBIDDEN_RENAME", "CONFIG_SUFFIX_RENAME"},
        )
        result = filter_actions_for_wave(actions, wave)
        types = {a.action_type for a in result}
        assert "TERRITORY_MOVE" not in types
        assert len(result) == 2

    def test_max_actions_per_wave_enforced(self):
        """Wave stops at max_actions_per_wave."""
        actions = [PlannedAction("RENAME", f"f{i}.py", f"g{i}.py", "R") for i in range(20)]
        wave = WaveConfig(
            wave_id="wave-002",
            allow_action_types={"RENAME"},
            max_actions_per_wave=5,
        )
        result = filter_actions_for_wave(actions, wave)
        assert len(result) == 5

    def test_blocked_actions_excluded(self):
        """Blocked actions are not included in wave."""
        actions = [
            PlannedAction("RENAME", "a.py", "b.py", "R", blocked_reason="COLLISION"),
            PlannedAction("RENAME", "c.py", "d.py", "R", blocked_reason=None),
        ]
        wave = WaveConfig(wave_id="wave-003", allow_action_types={"RENAME"})
        result = filter_actions_for_wave(actions, wave)
        assert len(result) == 1
        assert result[0].src == "c.py"

    def test_empty_wave(self):
        """No matching actions produces empty list."""
        actions = [
            PlannedAction("RENAME", "a.py", "b.py", "R"),
        ]
        wave = WaveConfig(
            wave_id="wave-004",
            allow_action_types={"TERRITORY_MOVE"},
        )
        result = filter_actions_for_wave(actions, wave)
        assert result == []


# ============================================================================
# Integration: Unified Preflight
# ============================================================================


class TestUnifiedPreflight:
    """Integration test for run_all_safety_gates."""

    def test_clean_small_rename_set(self, tmp_path):
        """Small clean rename set passes all gates."""
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "b.py").write_text("import a\n")
        files = list(tmp_path.glob("*.py"))

        rename_map = {"a.py": "a_util.py"}
        existing = {"a.py", "b.py"}

        result = run_all_safety_gates(
            rename_map,
            existing,
            files,
            tmp_path,
            max_actions=50,
        )
        assert result.collision_count == 0
        assert result.high_impact_count == 0
        assert result.mass_action_abort is False
        assert result.blocked_count == 0

    def test_collision_blocks_action(self, tmp_path):
        """Collision in rename map blocks the involved action."""
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "target.py").write_text("y = 2\n")
        files = list(tmp_path.glob("*.py"))

        rename_map = {"a.py": "target.py"}
        existing = {"a.py", "target.py"}

        result = run_all_safety_gates(
            rename_map,
            existing,
            files,
            tmp_path,
            max_actions=50,
        )
        assert result.collision_count >= 1
        assert result.blocked_count >= 1
        blocked_actions = [a for a in result.actions if a.blocked_reason]
        assert any("COLLISION" in (a.blocked_reason or "") for a in blocked_actions)
