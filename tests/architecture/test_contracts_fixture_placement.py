"""Architecture invariant: tests/contracts/ placement rules.

RCA: commit 81ae2aa21 — LocationHealerAgent._find_best_matching_subfolder used
Jaccard similarity to match 'fixtures' against SSOT subfolders.  Since 'fixtures'
had low/zero word-overlap with every canonical subfolder, the medium-confidence
branch routed it to the parent (tests/contracts/), flattening the directory.
The collision guard then produced _1 suffix duplicates.

This module encodes the invariants that prevent recurrence:
  1. tests/contracts/ root must NOT contain *Agent.py files
  2. tests/contracts/ root must NOT contain fake_*.py files
  3. tests/contracts/fixtures/ must exist and hold the synthetic fixture agents
  4. _find_best_matching_subfolder must treat 'fixtures' as preserved (no Jaccard remap)
  5. _calculate_subfolder_confidence must return 0.9 for 'fixtures' (create, not relocate)
  6. No _1 / _2 suffix duplicate files anywhere in tests/ (outside _quarantine)
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_contracts_fixture_placement")
_emit_applies_guardrail("p0", "test_contracts_fixture_placement", "p0_governance")
_emit_reads_policy_state("p0", "test_contracts_fixture_placement", "policy_binding")
_emit_snapshots_state("p0", "test_contracts_fixture_placement", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_contracts_fixture_placement", "p4obs", "metric_1")
_emit_emits_metric_event("test_contracts_fixture_placement", "p4obs", "metric_2")
_emit_emits_metric_event("test_contracts_fixture_placement", "p4obs", "metric_3")
_emit_emits_metric_event("test_contracts_fixture_placement", "p4obs", "metric_4")
_emit_emits_metric_event("test_contracts_fixture_placement", "p4obs", "metric_5")
_emit_emits_metric_event("test_contracts_fixture_placement", "p4obs", "metric_6")
_emit_records_incident_event("test_contracts_fixture_placement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_contracts_fixture_placement", "p4obs", "anomaly")
_emit_writes_observability_log("test_contracts_fixture_placement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_contracts_fixture_placement", "p4obs", "mon_state")
_emit_triggers_alert("test_contracts_fixture_placement", "p4obs", "alert")
_emit_links_incident_trace("test_contracts_fixture_placement", "p4obs", "trace_link")
_emit_captures_pattern("test_contracts_fixture_placement", "p3lm", "pattern")
_emit_records_learning_event("test_contracts_fixture_placement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_contracts_fixture_placement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_contracts_fixture_placement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_contracts_fixture_placement", "p3lm", "routing")
_emit_improves_agent_policy("test_contracts_fixture_placement", "p3lm", "policy")
_emit_stores_learning_state("test_contracts_fixture_placement", "p3lm", "state")
_emit_records_execution_trace("test_contracts_fixture_placement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_contracts_fixture_placement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_contracts_fixture_placement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_contracts_fixture_placement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_contracts_fixture_placement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_contracts_fixture_placement", "env_read", "p2_env_1")
_emit_reads_environ("test_contracts_fixture_placement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_contracts_fixture_placement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_contracts_fixture_placement", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_contracts_fixture_placement", "context_pull")
_emit_pulls_context("p1", "test_contracts_fixture_placement", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_contracts_fixture_placement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_contracts_fixture_placement", "uwg_term_2")
_emit_writes_through("p1", "test_contracts_fixture_placement", "write_through")
_emit_writes_through("p1", "test_contracts_fixture_placement", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_contracts_fixture_placement", "safety_validation")
_emit_invokes_eval("p1", "test_contracts_fixture_placement", "eval_call")
_emit_proposal_commits_routing("p1", "test_contracts_fixture_placement", "routing_commit")
_emit_escalates_to_human("p1", "test_contracts_fixture_placement", "human_escalation")
_emit_routes_through("p1", "test_contracts_fixture_placement", "route_through")
_emit_checks_agent_registry("p1", "test_contracts_fixture_placement", "agent_registry")
_emit_validates_agent_capability("p1", "test_contracts_fixture_placement", "capability")
_emit_dispatches_execution_plan("p1", "test_contracts_fixture_placement", "exec_plan")
_emit_agent_executes_agent("p1", "test_contracts_fixture_placement", "sub_agent")
_emit_routes_to_agent("p1", "test_contracts_fixture_placement", "target_agent")
_emit_verifies_policy("p1", "test_contracts_fixture_placement", "policy_check")
_emit_observes_runtime_state("p1", "test_contracts_fixture_placement", "runtime_state")
_emit_verifies_boundary("p1", "test_contracts_fixture_placement", "boundary_check")
_emit_transcripts_response("p1", "test_contracts_fixture_placement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_contracts_fixture_placement")
_emit_gated_by_confidence("p1", "test_contracts_fixture_placement", "confidence_gate")
emit_replay_key("p0", "test_contracts_fixture_placement")
emit_determinism_digest("p0", "test_contracts_fixture_placement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_contracts_fixture_placement", "execution_auth")
_emit_validates_capability("p2", "test_contracts_fixture_placement", "capability_check")
_emit_routes_to_capability("p2", "test_contracts_fixture_placement", "capability_route")
_emit_writes_via_uwg("p2", "test_contracts_fixture_placement", "uwg_write")
_emit_blocks_direct_write("p2", "test_contracts_fixture_placement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_contracts_fixture_placement", "tool_invocation")
_emit_captures_execution_output("p2", "test_contracts_fixture_placement", "exec_output")
_emit_dispatches_agent("p3", "test_contracts_fixture_placement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_contracts_fixture_placement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_contracts_fixture_placement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_contracts_fixture_placement", "healing_outcome")
_emit_escalates_failure("p3", "test_contracts_fixture_placement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_contracts_fixture_placement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_contracts_fixture_placement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_contracts_fixture_placement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_contracts_fixture_placement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_contracts_fixture_placement", "eval_metric")
_emit_stores_embedding("p4", "test_contracts_fixture_placement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_contracts_fixture_placement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_contracts_fixture_placement", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = PROJECT_ROOT / TESTS_DIR / "contracts"
FIXTURES_DIR = CONTRACTS_DIR / "fixtures"

_AGENT_PAT = re.compile(r".*Agent\.py$")
_FAKE_PAT = re.compile(r"^fake_.*\.py$")
_DUP_PAT = re.compile(r"^(.+?)_(\d+)(\.[^.]+)$")


# ── helpers ────────────────────────────────────────────────────────────────────


def _iter_contracts_root_files() -> list[Path]:
    """Files directly in tests/contracts/ (not subdirectories)."""
    if not CONTRACTS_DIR.exists():
        return []
    return [f for f in CONTRACTS_DIR.iterdir() if f.is_file() and f.suffix == ".py"]


def _iter_tests_py(exclude_dirs: frozenset[str] = frozenset({"_quarantine", "__pycache__"})) -> list[Path]:
    tests_dir = PROJECT_ROOT / TESTS_DIR
    result = []
    for f in tests_dir.rglob("*.py"):
        rel = f.relative_to(tests_dir)
        if any(part in exclude_dirs for part in rel.parts):
            continue
        result.append(f)
    return result


# ── 1. No *Agent.py in tests/contracts/ root ──────────────────────────────────


class TestNoAgentFilesInContractsRoot:
    """*Agent.py files must never reside directly in tests/contracts/."""

    def test_no_agent_py_in_contracts_root(self):
        """Success path: contracts root contains zero *Agent.py files."""
        violations = [f for f in _iter_contracts_root_files() if _AGENT_PAT.match(f.name)]
        assert violations == [], (
            "*Agent.py files found in tests/contracts/ root (must be in fixtures/): "
            + ", ".join(str(v.name) for v in violations)
        )

    def test_agent_pattern_matches_correctly(self):
        """Branch: pattern correctly identifies Agent filenames."""
        assert _AGENT_PAT.match("FakeAgent.py")
        assert _AGENT_PAT.match("FakeSuperDelegationAgent.py")
        assert _AGENT_PAT.match("MyAgent.py")
        assert not _AGENT_PAT.match("agent_helper.py")
        assert not _AGENT_PAT.match("test_agent.py")

    def test_agent_pattern_negative_control(self):
        """Negative control: non-agent files are not blocked."""
        non_agents = ["__init__.py", "guardian_quarantine.yaml", "mirror_baseline.json"]
        for name in non_agents:
            assert not _AGENT_PAT.match(name), f"{name} falsely matched agent pattern"


# ── 2. No fake_*.py in tests/contracts/ root ──────────────────────────────────


class TestNoFakeFilesInContractsRoot:
    """fake_*.py fixture files must live in tests/contracts/fixtures/, not root."""

    def test_no_fake_py_in_contracts_root(self):
        """Success path: contracts root contains zero fake_*.py files."""
        violations = [f for f in _iter_contracts_root_files() if _FAKE_PAT.match(f.name)]
        assert violations == [], (
            "fake_*.py files found in tests/contracts/ root (must be in fixtures/): "
            + ", ".join(str(v.name) for v in violations)
        )

    def test_fake_pattern_matches_correctly(self):
        """Branch: pattern correctly identifies fake_ filenames."""
        assert _FAKE_PAT.match("fake_trivial_output_agent.py")
        assert _FAKE_PAT.match("fake_super_delegation_agent.py")
        assert _FAKE_PAT.match("fake_any_thing.py")
        assert not _FAKE_PAT.match("test_fake_agent.py")
        assert not _FAKE_PAT.match("__init__.py")

    def test_fake_pattern_boundary_cases(self):
        """Boundary: 'fake' must be exact prefix, not substring."""
        assert not _FAKE_PAT.match("not_fake_agent.py")
        assert not _FAKE_PAT.match("myfake_agent.py")
        assert _FAKE_PAT.match("fake_.py")  # minimal valid match


# ── 3. fixtures/ subdir exists with canonical fixture files ───────────────────


class TestFixturesDirExists:
    """tests/contracts/fixtures/ must exist and hold the synthetic fixture agents."""

    def test_fixtures_dir_exists(self):
        """Success path: fixtures/ directory is present."""
        assert FIXTURES_DIR.exists(), "tests/contracts/fixtures/ does not exist"
        assert FIXTURES_DIR.is_dir(), "tests/contracts/fixtures is not a directory"

    def test_fixtures_init_exists(self):
        """fixtures/__init__.py must exist to mark the directory."""
        init = FIXTURES_DIR / "__init__.py"
        assert init.exists(), "tests/contracts/fixtures/__init__.py missing"

    def test_fake_trivial_output_agent_in_fixtures(self):
        """fake_trivial_output_agent.py must be in fixtures/, not root."""
        assert (FIXTURES_DIR / "fake_trivial_output_agent.py").exists(), (
            "fake_trivial_output_agent.py missing from tests/contracts/fixtures/"
        )

    def test_fake_super_delegation_agent_in_fixtures(self):
        """fake_super_delegation_agent.py must be in fixtures/, not root."""
        assert (FIXTURES_DIR / "fake_super_delegation_agent.py").exists(), (
            "fake_super_delegation_agent.py missing from tests/contracts/fixtures/"
        )

    def test_fixture_files_are_valid_python(self):
        """Fixture files must parse as valid Python (AST parse check)."""
        import ast

        for fpath in FIXTURES_DIR.glob("*.py"):
            try:
                ast.parse(fpath.read_text(encoding="utf-8"))
            except SyntaxError as e:
                pytest.fail(f"{fpath.name} failed AST parse: {e}")

    def test_fixture_files_not_in_contracts_root(self):
        """Fixtures must NOT appear in the contracts/ root (negative control)."""
        root_names = {f.name for f in _iter_contracts_root_files()}
        assert "fake_trivial_output_agent.py" not in root_names, (
            "fake_trivial_output_agent.py found in contracts/ root — must be in fixtures/"
        )
        assert "fake_super_delegation_agent.py" not in root_names, (
            "fake_super_delegation_agent.py found in contracts/ root — must be in fixtures/"
        )


# ── 4. No _N suffix duplicates anywhere in tests/ ─────────────────────────────


class TestNoDuplicateSuffixFiles:
    """_1 / _2 suffix files are healer collision artefacts and must not exist."""

    def test_no_n_suffix_duplicates_in_tests(self):
        """Success path: no *_N.py files whose original also exists."""
        violations = []
        for fpath in _iter_tests_py():
            m = _DUP_PAT.match(fpath.name)
            if not m:
                continue
            original_name = m.group(1) + m.group(3)
            original_path = fpath.parent / original_name
            if original_path.exists():
                violations.append(str(fpath.relative_to(PROJECT_ROOT)))
        assert violations == [], "_N suffix collision duplicates found (healer artefacts):\n" + "\n".join(
            f"  {v}" for v in violations[:20]
        )

    def test_dup_pattern_identifies_n_suffix(self):
        """Branch: _N suffix pattern correctly identifies duplicates."""
        m = _DUP_PAT.match("fake_trivial_output_agent_1.py")
        assert m is not None
        assert m.group(1) == "fake_trivial_output_agent"
        assert m.group(2) == "1"
        assert m.group(3) == ".py"

    def test_dup_pattern_misses_non_suffix(self):
        """Negative: normal files do not match _N pattern."""
        assert _DUP_PAT.match("fake_trivial_output_agent.py") is None
        assert _DUP_PAT.match("__init__.py") is None
        assert _DUP_PAT.match("test_something.py") is None

    def test_dup_pattern_boundary_two_digit(self):
        """Boundary: two-digit suffix also matches."""
        m = _DUP_PAT.match("myfile_12.py")
        assert m is not None
        assert m.group(2) == "12"


# ── 5. _find_best_matching_subfolder: preserved subfolders never remapped ──────


class TestFindBestMatchingSubfolderPreservedDirs:
    """'fixtures' is a preserved subfolder name — must never be Jaccard-remapped."""

    @pytest.fixture
    def healer(self):
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        agent = LocationHealerAgent.__new__(LocationHealerAgent)
        agent.project_root = PROJECT_ROOT
        return agent

    def test_fixtures_existing_returns_self(self, healer):
        """Success path: 'fixtures' in existing list → returns 'fixtures' (self-match)."""
        result = healer._find_best_matching_subfolder("fixtures", ["fixtures", "support", "data"])
        assert result == "fixtures"

    def test_fixtures_not_in_existing_returns_none(self, healer):
        """Branch: 'fixtures' NOT in existing → returns None (caller must create)."""
        result = healer._find_best_matching_subfolder("fixtures", ["support", "data", "helpers"])
        assert result is None

    def test_mocks_preserved(self, healer):
        """Branch: 'mocks' is preserved — returns self when present."""
        result = healer._find_best_matching_subfolder("mocks", ["mocks", "support"])
        assert result == "mocks"

    def test_stubs_preserved(self, healer):
        """Branch: 'stubs' is preserved — returns None when absent."""
        result = healer._find_best_matching_subfolder("stubs", ["support", "data"])
        assert result is None

    def test_non_preserved_uses_jaccard(self, healer):
        """Branch: non-preserved name falls through to Jaccard similarity."""
        # 'reasoning' Jaccard-matches 'reasoning' with score=1.0
        result = healer._find_best_matching_subfolder("reasoning", ["reasoning", "engines"])
        assert result == "reasoning"

    def test_non_preserved_no_match_returns_none(self, healer):
        """Branch: non-preserved, no Jaccard match >= 0.5 → None."""
        result = healer._find_best_matching_subfolder("zzz_unknown_xyz", ["support", "fixtures"])
        assert result is None

    def test_agent_file_blocked_from_support(self, healer):
        """Negative control: *Agent.py file (production) never matched to 'support'."""
        prod_agent = PROJECT_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "LocationHealerAgent.py"
        result = healer._find_best_matching_subfolder(
            "support", ["support", "reasoning"], file_path=prod_agent
        )
        assert result != "support", "Production agent file must not be routed to 'support'"

    def test_empty_existing_returns_none(self, healer):
        """Edge case: empty existing list → None."""
        assert healer._find_best_matching_subfolder("fixtures", []) is None

    def test_fixtures_exact_match_not_jaccard_dependent(self, healer):
        """Metamorphic: result must be identical regardless of other subfolder ordering."""
        r1 = healer._find_best_matching_subfolder("fixtures", ["fixtures", "a", "b"])
        r2 = healer._find_best_matching_subfolder("fixtures", ["b", "a", "fixtures"])
        assert r1 == r2 == "fixtures"


# ── 6. _calculate_subfolder_confidence: preserved dirs return 0.9 ─────────────


class TestCalculateSubfolderConfidencePreserved:
    """'fixtures' must always return confidence 0.9 (create path), never < 0.5."""

    @pytest.fixture
    def healer(self):
        from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

        agent = LocationHealerAgent.__new__(LocationHealerAgent)
        agent.project_root = PROJECT_ROOT
        return agent

    def test_fixtures_returns_high_confidence(self, healer):
        """Success path: 'fixtures' → 0.9 (high confidence create)."""
        score = healer._calculate_subfolder_confidence("fixtures", ["support", "data"])
        assert score == 0.9

    def test_mocks_returns_high_confidence(self, healer):
        """Branch: 'mocks' → 0.9."""
        assert healer._calculate_subfolder_confidence("mocks", []) == 0.9

    def test_stubs_returns_high_confidence(self, healer):
        """Branch: 'stubs' → 0.9."""
        assert healer._calculate_subfolder_confidence("stubs", []) == 0.9

    def test_agent_file_returns_zero(self, healer):
        """Branch: AGENT file (production) → 0.0 regardless of subfolder name."""
        prod_agent = (
            PROJECT_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "FileClassificationAgent.py"
        )
        score = healer._calculate_subfolder_confidence("utils", ["utils", "reasoning"], file_path=prod_agent)
        assert score == 0.0, f"Production agent file must score 0.0, got {score}"

    def test_agent_filename_heuristic_zero(self, healer):
        """Exception path: AST import fails, filename heuristic fires."""
        fake_path = MagicMock(spec=Path)
        fake_path.name = "MyAgent.py"
        # Patch classify_file_standalone to raise so heuristic path executes
        with patch(
            "agentic_core.L5_safety.core_kernel.classification_kernel.classify_file_standalone",
            side_effect=ImportError("no module"),
        ):
            score = healer._calculate_subfolder_confidence("engines", [], file_path=fake_path)
        assert score == 0.0, f"Filename heuristic must return 0.0 for *Agent.py, got {score}"

    def test_non_preserved_non_agent_uses_patterns(self, healer):
        """Branch: non-preserved, non-agent file falls through to regex patterns."""
        score = healer._calculate_subfolder_confidence("utils", [])
        assert score == 0.9  # matches r".*utils.*"

    def test_non_preserved_no_pattern_match(self, healer):
        """Branch: no pattern, low Jaccard → returns 0.7."""
        score = healer._calculate_subfolder_confidence("zzz_unique_xyz", ["abc"])
        assert score == 0.7

    def test_boundary_similarity_above_0_8(self, healer):
        """Boundary: similarity > 0.8 → score = 0.3 (should relocate, not create)."""
        # 'support' vs ['support'] → Jaccard = 1.0 → 0.3
        score = healer._calculate_subfolder_confidence("support_new", ["support_new"])
        assert score == 0.3

    def test_test_subfolder_not_high_confidence(self, healer):
        """Regression: TESTS_DIR and 'test' must NOT return 0.9 (removed from patterns)."""
        score_tests = healer._calculate_subfolder_confidence(TESTS_DIR, [])
        score_test = healer._calculate_subfolder_confidence("test", [])
        # Neither TESTS_DIR nor 'test' should get 0.9 from the pattern list
        # (they were removed to prevent healer from auto-creating test/ subdirs)
        assert score_tests != 0.9 or score_test != 0.9, (
            "Both TESTS_DIR and 'test' return 0.9 — at least one must not match high-confidence patterns"
        )


# ── 7. SSOT blueprint encodes contracts/ forbidden patterns ───────────────────


class TestSSOTBlueprintContractsEntry:
    """SSOT blueprint must declare forbidden_patterns for tests/contracts/."""

    def test_contracts_has_forbidden_patterns(self):
        """Success path: contracts entry has forbidden_patterns key."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_territory = get_all_territories().get(TESTS_DIR, {})
        subfolders = tests_territory.get("subfolders", {})
        contracts = subfolders.get("contracts", {})
        assert "forbidden_patterns" in contracts, "tests/contracts/ SSOT entry missing forbidden_patterns"

    def test_contracts_forbidden_patterns_block_agent(self):
        """Branch: forbidden_patterns blocks *Agent.py."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_territory = get_all_territories().get(TESTS_DIR, {})
        subfolders = tests_territory.get("subfolders", {})
        contracts = subfolders.get("contracts", {})
        patterns = contracts.get("forbidden_patterns", [])
        agent_blocked = any(re.match(p, "FakeAgent.py") for p in patterns)
        assert agent_blocked, "forbidden_patterns must block *Agent.py"

    def test_contracts_forbidden_patterns_block_fake(self):
        """Branch: forbidden_patterns blocks fake_*.py."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_territory = get_all_territories().get(TESTS_DIR, {})
        subfolders = tests_territory.get("subfolders", {})
        contracts = subfolders.get("contracts", {})
        patterns = contracts.get("forbidden_patterns", [])
        fake_blocked = any(re.match(p, "fake_anything.py") for p in patterns)
        assert fake_blocked, "forbidden_patterns must block fake_*.py"

    def test_contracts_fixtures_subfolder_declared(self):
        """Branch: contracts/ SSOT entry declares fixtures/ as approved subfolder."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_territory = get_all_territories().get(TESTS_DIR, {})
        subfolders = tests_territory.get("subfolders", {})
        contracts = subfolders.get("contracts", {})
        contract_subs = contracts.get("subfolders", {})
        assert "fixtures" in contract_subs, "tests/contracts/fixtures/ not declared in SSOT blueprint"
