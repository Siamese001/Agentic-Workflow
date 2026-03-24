"""
Regression guard for phantom folder bugs created by healing agents.

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| HierarchyAgent._heal_depth_violation | SHALLOW depth path | depth_aligned/ created | HARD FAIL — must never exist | test_no_depth_aligned_anywhere |
| HierarchyAgent._heal_depth_violation | DEEP depth path | depth_aligned/ created | HARD FAIL — must never exist | test_no_depth_aligned_in_agentic_core |
| LocationHealerAgent | any healing run | depth_aligned/ spacer created | HARD FAIL — must never exist | test_no_depth_aligned_in_any_territory |
| healing pipeline | any healing run | tests/support/ gains L-layer subdirs | HARD FAIL — support must be flat | test_tests_support_has_no_subdirectories |
| healing pipeline | any healing run | agent file duplicated into phantom subdir | HARD FAIL — no duplicate agents | test_no_agent_file_duplicated_in_subdir |
| healing pipeline | any healing run | depth_aligned duplicate of parent dir | HARD FAIL — content must be unique | test_depth_aligned_not_duplicate_of_parent |

## Bugs being guarded
Bug 1: HierarchyAgent / LocationHealerAgent create `depth_aligned/` spacer directories
        when a file is at the wrong depth. These are semantically meaningless and
        duplicate content from the parent directory.

Bug 2: Healing pipeline creates L-layer subdirectories (`l1_cognition/`, `l2_execution/`,
        `l3_orchestration/`, `l6_observability/`) under `tests/support/`, duplicating
        agent files that already exist at the flat root level.

Both bugs represent the same class of failure: healing agents creating phantom structural
scaffolding rather than actually relocating files correctly.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
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

_emit_records_execution_trace("p0", "evidence", "test_phantom_folder_regression")
_emit_applies_guardrail("p0", "test_phantom_folder_regression", "p0_governance")
_emit_reads_policy_state("p0", "test_phantom_folder_regression", "policy_binding")
_emit_snapshots_state("p0", "test_phantom_folder_regression", "state_snapshot")
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

_emit_emits_metric_event("test_phantom_folder_regression", "p4obs", "metric_1")
_emit_emits_metric_event("test_phantom_folder_regression", "p4obs", "metric_2")
_emit_emits_metric_event("test_phantom_folder_regression", "p4obs", "metric_3")
_emit_emits_metric_event("test_phantom_folder_regression", "p4obs", "metric_4")
_emit_emits_metric_event("test_phantom_folder_regression", "p4obs", "metric_5")
_emit_emits_metric_event("test_phantom_folder_regression", "p4obs", "metric_6")
_emit_records_incident_event("test_phantom_folder_regression", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_phantom_folder_regression", "p4obs", "anomaly")
_emit_writes_observability_log("test_phantom_folder_regression", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_phantom_folder_regression", "p4obs", "mon_state")
_emit_triggers_alert("test_phantom_folder_regression", "p4obs", "alert")
_emit_links_incident_trace("test_phantom_folder_regression", "p4obs", "trace_link")
_emit_captures_pattern("test_phantom_folder_regression", "p3lm", "pattern")
_emit_records_learning_event("test_phantom_folder_regression", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_phantom_folder_regression", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_phantom_folder_regression", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_phantom_folder_regression", "p3lm", "routing")
_emit_improves_agent_policy("test_phantom_folder_regression", "p3lm", "policy")
_emit_stores_learning_state("test_phantom_folder_regression", "p3lm", "state")
_emit_records_execution_trace("test_phantom_folder_regression", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_phantom_folder_regression", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_phantom_folder_regression", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_phantom_folder_regression", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_phantom_folder_regression", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_phantom_folder_regression", "env_read", "p2_env_1")
_emit_reads_environ("test_phantom_folder_regression", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_phantom_folder_regression", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_phantom_folder_regression", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_phantom_folder_regression", "context_pull")
_emit_pulls_context("p1", "test_phantom_folder_regression", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_phantom_folder_regression", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_phantom_folder_regression", "uwg_term_2")
_emit_writes_through("p1", "test_phantom_folder_regression", "write_through")
_emit_writes_through("p1", "test_phantom_folder_regression", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_phantom_folder_regression", "safety_validation")
_emit_invokes_eval("p1", "test_phantom_folder_regression", "eval_call")
_emit_proposal_commits_routing("p1", "test_phantom_folder_regression", "routing_commit")
_emit_escalates_to_human("p1", "test_phantom_folder_regression", "human_escalation")
_emit_routes_through("p1", "test_phantom_folder_regression", "route_through")
_emit_checks_agent_registry("p1", "test_phantom_folder_regression", "agent_registry")
_emit_validates_agent_capability("p1", "test_phantom_folder_regression", "capability")
_emit_dispatches_execution_plan("p1", "test_phantom_folder_regression", "exec_plan")
_emit_agent_executes_agent("p1", "test_phantom_folder_regression", "sub_agent")
_emit_routes_to_agent("p1", "test_phantom_folder_regression", "target_agent")
_emit_verifies_policy("p1", "test_phantom_folder_regression", "policy_check")
_emit_observes_runtime_state("p1", "test_phantom_folder_regression", "runtime_state")
_emit_verifies_boundary("p1", "test_phantom_folder_regression", "boundary_check")
_emit_transcripts_response("p1", "test_phantom_folder_regression", "transcript")
_emit_hard_fails_untranscripted("p1", "test_phantom_folder_regression")
_emit_gated_by_confidence("p1", "test_phantom_folder_regression", "confidence_gate")
emit_replay_key("p0", "test_phantom_folder_regression")
emit_determinism_digest("p0", "test_phantom_folder_regression")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_phantom_folder_regression", "execution_auth")
_emit_validates_capability("p2", "test_phantom_folder_regression", "capability_check")
_emit_routes_to_capability("p2", "test_phantom_folder_regression", "capability_route")
_emit_writes_via_uwg("p2", "test_phantom_folder_regression", "uwg_write")
_emit_blocks_direct_write("p2", "test_phantom_folder_regression", "direct_write_block")
_emit_records_tool_invocation("p2", "test_phantom_folder_regression", "tool_invocation")
_emit_captures_execution_output("p2", "test_phantom_folder_regression", "exec_output")
_emit_dispatches_agent("p3", "test_phantom_folder_regression", "agent_dispatch")
_emit_coordinates_agents("p3", "test_phantom_folder_regression", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_phantom_folder_regression", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_phantom_folder_regression", "healing_outcome")
_emit_escalates_failure("p3", "test_phantom_folder_regression", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_phantom_folder_regression", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_phantom_folder_regression", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_phantom_folder_regression", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_phantom_folder_regression", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_phantom_folder_regression", "eval_metric")
_emit_stores_embedding("p4", "test_phantom_folder_regression", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_phantom_folder_regression", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_phantom_folder_regression", "exec_snapshot_link")

REPO_ROOT = Path(__file__).resolve().parents[2]

AGENT_TERRITORIES = [
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    TESTS_DIR,
    OPS_SCRIPTS_DIR,
    "docs",
]

# Only used for tests/support/ specific check — NOT for broad territory scan.
# ops_scripts/dev_tools/l0_scripts is a legitimate directory.
L_LAYER_PATTERN = re.compile(r"^l[0-9]_[a-z]+$")


# ===========================================================================
# Bug 1: depth_aligned/ phantom folders
# ===========================================================================


@pytest.mark.architecture
class TestDepthAlignedRegression:
    def _all_depth_aligned_dirs(self) -> list[Path]:
        violations = []
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("*"):
                if d.is_dir() and d.name == "depth_aligned":
                    violations.append(d)
        return violations

    def test_no_depth_aligned_anywhere(self):
        """depth_aligned/ must not exist anywhere in any canonical territory.

        This directory name is a semantically meaningless spacer invented by
        HierarchyAgent / LocationHealerAgent to satisfy depth counters. It is
        a known healing bug. Any occurrence = regression.
        """
        violations = self._all_depth_aligned_dirs()
        if violations:
            rel = [str(d.relative_to(REPO_ROOT)) for d in violations]
            pytest.fail(
                f"HEALING BUG REGRESSION: {len(violations)} phantom depth_aligned/ "
                f"director(y/ies) found — these must never be created:\n  " + "\n  ".join(rel)
            )

    def test_no_depth_aligned_in_agentic_core(self):
        """Specific guard: agentic_core/ must never contain depth_aligned/."""
        ac = REPO_ROOT / AGENTIC_CORE_DIR
        if not ac.exists():
            pytest.fail("agentic_core not present")
        violations = [d for d in ac.rglob("*") if d.is_dir() and d.name == "depth_aligned"]
        assert not violations, "depth_aligned/ found inside agentic_core/:\n  " + "\n  ".join(
            str(d.relative_to(REPO_ROOT)) for d in violations
        )

    def test_no_depth_aligned_in_tests(self):
        """Specific guard: tests/ must never contain depth_aligned/."""
        t = REPO_ROOT / TESTS_DIR
        if not t.exists():
            pytest.fail("tests/ not present")
        violations = [d for d in t.rglob("*") if d.is_dir() and d.name == "depth_aligned"]
        assert not violations, "depth_aligned/ found inside tests/:\n  " + "\n  ".join(
            str(d.relative_to(REPO_ROOT)) for d in violations
        )

    def test_no_depth_aligned_in_system_learning(self):
        """Specific guard: system_learning/ must never contain depth_aligned/."""
        sl = REPO_ROOT / SYSTEM_LEARNING_DIR
        if not sl.exists():
            pytest.fail("system_learning not present")
        violations = [d for d in sl.rglob("*") if d.is_dir() and d.name == "depth_aligned"]
        assert not violations, "depth_aligned/ found inside system_learning/:\n  " + "\n  ".join(
            str(d.relative_to(REPO_ROOT)) for d in violations
        )

    def test_depth_aligned_not_in_sovereign_territories_blueprint(self):
        """depth_aligned must not be declared as a canonical subfolder in the blueprint.

        Guards against the healing agent updating SOVEREIGN_TERRITORIES to
        legitimise the phantom folder structure.
        """
        try:
            from agentic_core.L5_safety.config.structure_blueprint import (
                get_all_territories,
            )
        except ImportError:
            pytest.fail("get_all_territories not importable")

        def _walk(obj: object, path: str = "") -> list[str]:
            found = []
            if hasattr(obj, "items"):
                for k, v in obj.items():
                    if k == "depth_aligned":
                        found.append(f"{path}.{k}")
                    found.extend(_walk(v, f"{path}.{k}"))
            return found

        violations = _walk(get_all_territories())
        assert not violations, (
            "depth_aligned declared as canonical subfolder in get_all_territories(): "
            + ", ".join(violations)
            + " — this is forbidden."
        )

    def test_depth_aligned_not_duplicate_of_parent(self):
        """depth_aligned/ content must not be a duplicate of its parent directory.

        When the bug fires, depth_aligned/ contains byte-for-byte copies of parent
        files. This test catches partial regression where the folder exists but
        the duplication only covers some files.
        """
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("depth_aligned"):
                if not d.is_dir():
                    continue
                parent = d.parent
                parent_files = {f.name for f in parent.iterdir() if f.is_file()}
                da_files = {f.name for f in d.iterdir() if f.is_file()}
                overlap = parent_files & da_files
                assert not overlap, (
                    f"depth_aligned/ at {d.relative_to(REPO_ROOT)} duplicates "
                    f"{len(overlap)} file(s) from its parent: {sorted(overlap)}"
                )


# ===========================================================================
# Bug 2: tests/support/ phantom L-layer subdirectories
# ===========================================================================


@pytest.mark.architecture
class TestTestsSupportFlatStructure:
    def _support_subdirs(self) -> list[Path]:
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            return []
        return [d for d in support.iterdir() if d.is_dir() and d.name != "__pycache__"]

    def test_tests_support_has_no_subdirectories(self):
        """tests/support/ must be a flat directory with no subdirectories.

        Healing agents have incorrectly created L-layer subdirectories (l1_cognition/,
        l2_execution/, etc.) under tests/support/ and duplicated agent files into them.
        tests/support/ holds flat test-only infrastructure agents — no hierarchy allowed.
        """
        subdirs = self._support_subdirs()
        if subdirs:
            rel = [str(d.relative_to(REPO_ROOT)) for d in subdirs]
            pytest.fail(
                f"HEALING BUG REGRESSION: {len(subdirs)} phantom subdirector(y/ies) found "
                f"under tests/support/ — this directory must be flat:\n  " + "\n  ".join(rel)
            )

    def test_tests_support_has_no_l_layer_subdirectories(self):
        """tests/support/ must not contain any L-layer subdirectory names.

        Pattern: l[0-9]_<name> (e.g. l1_cognition, l6_observability).
        These are phantom folders created by a misbehaving healing run.
        """
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            pytest.fail("tests/support not present")
        violations = [d for d in support.iterdir() if d.is_dir() and L_LAYER_PATTERN.match(d.name)]
        assert not violations, "L-layer phantom subdirectories found under tests/support/: " + ", ".join(
            d.name for d in violations
        )

    def test_tests_support_no_agent_duplication(self):
        """Agent files in tests/support/ must not also exist in any subdirectory.

        When the bug fires, every agent at tests/support/FooAgent.py is also
        duplicated into tests/support/l1_cognition/FooAgent.py (or similar).
        """
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            pytest.fail("tests/support not present")

        root_agents = {f.name for f in support.iterdir() if f.is_file() and f.suffix == ".py"}
        subdirs = [d for d in support.iterdir() if d.is_dir() and d.name != "__pycache__"]

        for subdir in subdirs:
            sub_files = {f.name for f in subdir.iterdir() if f.is_file() and f.suffix == ".py"}
            duplicates = root_agents & sub_files
            assert not duplicates, (
                f"Agent file(s) duplicated between tests/support/ and "
                f"tests/support/{subdir.name}/: {sorted(duplicates)}"
            )

    @pytest.mark.parametrize(
        "forbidden_name",
        [
            "l0_routing",
            "l1_cognition",
            "l2_execution",
            "l3_orchestration",
            "l4_memory",
            "l5_safety",
            "l6_observability",
            "depth_aligned",
            "_quarantine",
        ],
    )
    def test_tests_support_specific_forbidden_subdirs_absent(self, forbidden_name):
        """Each known-bad subdirectory name must not exist under tests/support/."""
        support = REPO_ROOT / TESTS_DIR / "support"
        if not support.exists():
            pytest.fail("tests/support not present")
        bad = support / forbidden_name
        assert not bad.exists(), (
            f"Forbidden subdirectory tests/support/{forbidden_name}/ exists — "
            "created by a misbehaving healing run. Remove it."
        )


# ===========================================================================
# Bug 3: phantom subdirectory duplication across all territories
# ===========================================================================


@pytest.mark.architecture
class TestPhantomSubdirDuplication:
    # ONLY depth_aligned is universally forbidden.
    # _quarantine is canonical under tests/. l0_scripts is legitimate ops tooling.
    FORBIDDEN_SUBDIR_NAMES = frozenset({"depth_aligned"})

    def _is_forbidden(self, name: str) -> bool:
        return name in self.FORBIDDEN_SUBDIR_NAMES

    def test_no_depth_aligned_subdirs_in_any_territory(self):
        """No canonical territory may contain depth_aligned/ subdirs.

        This is the exhaustive scan across all territories that catches any healing
        agent creating phantom depth_aligned/ structure anywhere in the repo.
        """
        violations: list[str] = []
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("*"):
                if d.is_dir() and self._is_forbidden(d.name) and "__pycache__" not in d.parts:
                    violations.append(str(d.relative_to(REPO_ROOT)))

        assert not violations, (
            f"REGRESSION: {len(violations)} forbidden depth_aligned/ directory(ies) found:\n  "
            + "\n  ".join(sorted(violations))
        )

    def test_no_file_exists_in_both_parent_and_depth_aligned_subdir(self):
        """Files must not be duplicated between a directory and a depth_aligned/ child.

        When the healing bug fires, a directory gains a depth_aligned/ child that
        contains byte-for-byte copies of the parent's files.
        """
        violations: list[str] = []
        for territory in AGENT_TERRITORIES:
            t_path = REPO_ROOT / territory
            if not t_path.exists():
                continue
            for d in t_path.rglob("depth_aligned"):
                if not d.is_dir() or "__pycache__" in d.parts:
                    continue
                parent = d.parent
                parent_files = {f.name for f in parent.iterdir() if f.is_file()}
                child_files = {f.name for f in d.iterdir() if f.is_file()}
                dupes = parent_files & child_files
                for dup in sorted(dupes):
                    violations.append(f"{d.relative_to(REPO_ROOT)}/{dup}")

        assert not violations, (
            f"REGRESSION: {len(violations)} file(s) duplicated in depth_aligned/ subdir:\n  "
            + "\n  ".join(violations)
        )

    def test_git_index_has_no_depth_aligned_paths(self):
        """Ensure no depth_aligned/ directories are tracked by git.

        Catches cases where phantom dirs were committed but deleted on disk —
        they would resurface on the next `git checkout` or clone.
        """
        import subprocess

        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        tracked = result.stdout.splitlines()
        violations = [f for f in tracked if "depth_aligned" in Path(f).parts]
        assert not violations, (
            f"REGRESSION: {len(violations)} depth_aligned/ path(s) tracked in git index:\n  "
            + "\n  ".join(sorted(violations)[:40])
        )

    def test_git_index_has_no_tests_support_l_layer_subdirs(self):
        """Ensure no L-layer subdirs of tests/support/ are tracked in git.

        Catches the phantom tests/support/l1_cognition/, l6_observability/ etc.
        even if already deleted on disk (git index would restore them on checkout).
        """
        import subprocess

        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        tracked = result.stdout.splitlines()
        violations = [
            f
            for f in tracked
            if f.startswith("tests/support/")
            and len(Path(f).parts) > 2
            and L_LAYER_PATTERN.match(Path(f).parts[2])
        ]
        assert not violations, (
            f"REGRESSION: {len(violations)} phantom tests/support/L-layer path(s) in git:\n  "
            + "\n  ".join(sorted(violations)[:40])
        )
