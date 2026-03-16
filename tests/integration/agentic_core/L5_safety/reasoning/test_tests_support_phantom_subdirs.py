"""
Regression tests for phantom L-layer subdirectory creation under tests/support/.

Bug 1 root cause: Healing agents created l1_cognition/, l2_execution/, etc. inside
tests/support/ and duplicated agent files there. These tests enforce multi-layer protection:

  Layer 1 — Blueprint invariant: get_all_territories()[TESTS_DIR]['subfolders']['support']
             has no declared subfolders → healing agents can never create canonical subdirs.
  Layer 2 — Enforcement gap (documented): _enforce_tests_structure checks only
             rel.parts[0] against the approved set. Files inside tests/support/l1_cognition/
             have rel.parts[0] == 'support' (approved) → the phantom subdir is NOT detected.
  Layer 3 — Filesystem scan: test_phantom_folder_regression.py (and the architecture
             invariant suite) catches phantom dirs actually present on disk.

These tests verify:
  - Layer 1 holds (blueprint has no phantom subfolders declared for support/)
  - Layer 2 gap is demonstrable (and therefore the Layer 3 guard is load-bearing)
  - create_missing_structure never creates subdirs inside support/
  - SOVEREIGN_TERRITORIES has no L-layer names anywhere under tests/ subfolders
  - Stress: 50 phantom files in support subdirs are ALL silently skipped

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"]["support"] | no subfolders key | support stays flat | test_support_has_no_declared_subfolders_in_blueprint |
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"] | "support" key exists | support is approved | test_support_is_approved_tests_subfolder |
| _constants.py | get_all_territories()[TESTS_DIR]["subfolders"] | no l*_* top-level keys | no l-layer approved | test_no_l_layer_names_approved_at_tests_top_level |
| _constants.py | SOVEREIGN_TERRITORIES | all required_subfolders | no l*_* names | test_no_l_layer_in_any_required_subfolders |
| HierarchyAgent.py | _enforce_tests_structure | tests/support/l1_cognition/Agent.py | SKIPPED (gap: parts[0]='support') | test_phantom_l1_cognition_under_support_not_detected |
| HierarchyAgent.py | _enforce_tests_structure | tests/support/l2_execution/Agent.py | SKIPPED (gap) | test_phantom_l2_execution_under_support_not_detected |
| HierarchyAgent.py | _enforce_tests_structure | tests/support/depth_aligned/f.py | SKIPPED (gap) | test_phantom_depth_aligned_under_support_not_detected |
| HierarchyAgent.py | _enforce_tests_structure | tests/support/l1_cognition/ non-test file | SKIPPED (gap) | test_non_test_file_in_phantom_support_subdir_not_detected |
| HierarchyAgent.py | _enforce_tests_structure | tests/support/ root files | violations_found=0 | test_real_support_files_not_reported |
| HierarchyAgent.py | _enforce_tests_structure | stress: 50 phantom files | violations_found=0 | test_stress_50_phantom_support_files_all_skipped |
| HierarchyAgent.py | _enforce_tests_structure | real + phantom mix | only real violations counted | test_real_violations_plus_phantom_support_mix |
| HierarchyAgent.py | _create_territory_structure | support empty subfolders | no subdirs created | test_create_territory_structure_support_no_subdirs |
| HierarchyAgent.py | _create_territory_structure | support subfolders={} | no dirs attempted | test_create_territory_structure_empty_subfolders_no_create |
| HierarchyAgent.py | create_missing_structure | live SSOT for tests territory | no l*_* dirs created under tests/support/ | test_create_missing_structure_no_l_layer_under_support |
| HierarchyAgent.py | _enforce_tests_structure | duplicate agent files in phantom subdirs | ALL silently skipped (gap) | test_duplicate_agent_files_in_phantom_subdirs_skipped |
| HierarchyAgent.py | _heal_depth_violation | tests/support/l1_cognition/f.py at correct depth | depth==expected → 0, no gk (bypass) | test_phantom_support_file_correct_depth_bypasses_heal |
| HierarchyAgent.py | _heal_depth_violation | tests/support/l1_cognition/f.py too deep | DEEP: gk called | test_phantom_support_file_too_deep_healed |
"""

from __future__ import annotations

import re
from pathlib import Path
from types import MappingProxyType
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_tests_support_phantom_subdirs")
_emit_applies_guardrail("p0", "test_tests_support_phantom_subdirs", "p0_governance")
_emit_reads_policy_state("p0", "test_tests_support_phantom_subdirs", "policy_binding")
_emit_snapshots_state("p0", "test_tests_support_phantom_subdirs", "state_snapshot")
emit_replay_key("p0", "test_tests_support_phantom_subdirs")
emit_determinism_digest("p0", "test_tests_support_phantom_subdirs")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_Mapping = (dict, MappingProxyType)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agent(healing_enabled: bool = False):
    """Construct a minimal HierarchyAgent without triggering __init__ chain."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = Path("/fake/root")
    agent.agent_name = "HierarchyAgent"
    agent.healing_enabled = healing_enabled
    gk = MagicMock()
    gk.safe_move.return_value = MagicMock(success=True, error=None)
    agent.gatekeeper = gk
    agent._legacy_archive_depth_violation = MagicMock(return_value=0)
    return agent


def _patch_approved(approved: frozenset):
    return patch(
        "agentic_core.L5_safety.reasoning.hierarchy_healer.HierarchyAgent._get_approved_tests_subfolders",
        return_value=approved,
    )


def _patch_whitelist(whitelist: frozenset | None = None):
    wl = whitelist if whitelist is not None else frozenset({"conftest.py", "__init__.py"})
    return patch(
        "agentic_core.L5_safety.config.structure_blueprint_config.TESTS_ROOT_FILE_WHITELIST",
        wl,
        create=True,
    )


APPROVED = frozenset(
    {
        "unit",
        "integration",
        "support",
        "fixtures",
        "e2e",
        "_config",
        "architecture",
        "governance",
        "behavioral",
        "stress",
    }
)


def _run_enforce(agent, tmp_path, files: list[tuple[str, str]]) -> dict:
    """Write files and run _enforce_tests_structure; return results dict."""
    for rel, content in files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    results = {"violations_found": 0, "files_relocated": 0}
    agent._enforce_tests_structure(tmp_path, results)
    return results


# ---------------------------------------------------------------------------
# Layer 1: Blueprint invariants
# ---------------------------------------------------------------------------


@pytest.mark.architecture
class TestBlueprintInvariants:
    """SOVEREIGN_TERRITORIES must not declare any subfolders for tests/support/."""

    def test_support_has_no_declared_subfolders_in_blueprint(self):
        """
        HARD INVARIANT: get_all_territories()[TESTS_DIR]['subfolders']['support']
        must have no 'subfolders' key (or an empty one).

        Any declared subfolders would give healing agents permission to create
        L-layer subdirectories inside tests/support/.
        """
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_subs = get_all_territories().get(TESTS_DIR, {}).get("subfolders", {})
        support_cfg = tests_subs.get("support", {}) if isinstance(tests_subs, _Mapping) else {}
        declared = support_cfg.get("subfolders", None) if isinstance(support_cfg, _Mapping) else None
        assert declared is None or len(declared) == 0, (
            f"tests/support/ has declared subfolders in get_all_territories(): {declared}. "
            "Healing agents would create these as canonical subdirectories."
        )

    def test_support_is_approved_tests_subfolder(self):
        """support must exist in get_all_territories()[TESTS_DIR]['subfolders'] as a canonical dir."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_subs = get_all_territories().get(TESTS_DIR, {}).get("subfolders", {})
        assert isinstance(tests_subs, _Mapping), "tests.subfolders must be a dict or MappingProxyType"
        assert "support" in tests_subs, (
            "'support' not found in get_all_territories()[TESTS_DIR]['subfolders']. "
            "This would cause healing agents to report all tests/support/ files as violations."
        )

    def test_no_l_layer_names_approved_at_tests_top_level(self):
        """No l[0-9]_* names in get_all_territories()[TESTS_DIR]['subfolders'] at top level."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        l_pattern = re.compile(r"^l[0-9]_[a-z]+$")
        tests_subs = get_all_territories().get(TESTS_DIR, {}).get("subfolders", {})
        if not isinstance(tests_subs, _Mapping):
            return
        violations = [k for k in tests_subs if l_pattern.match(k)]
        assert not violations, (
            f"L-layer names approved at tests/ top level: {violations}. "
            "This would allow healing agents to create L-layer directories directly under tests/."
        )

    def test_no_l_layer_in_any_required_subfolders(self):
        """No l[0-9]_* names in required_subfolders of ANY territory."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        l_pattern = re.compile(r"^l[0-9]_[a-z]+$")
        violations: dict[str, list[str]] = {}
        for name, cfg in get_all_territories().items():
            if not isinstance(cfg, dict):
                continue
            required = cfg.get("required_subfolders", [])
            bad = [s for s in required if l_pattern.match(s)]
            if bad:
                violations[name] = bad
        assert not violations, (
            f"L-layer names in required_subfolders: {violations}. "
            "These would be created by create_missing_structure as canonical directories."
        )

    def test_no_depth_aligned_in_tests_subfolders(self):
        """'depth_aligned' must not appear anywhere in get_all_territories()[TESTS_DIR]['subfolders']."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_subs = get_all_territories().get(TESTS_DIR, {}).get("subfolders", {})
        assert isinstance(tests_subs, _Mapping), "tests.subfolders must be a Mapping"
        assert "depth_aligned" not in tests_subs, (
            "'depth_aligned' found in get_all_territories()[TESTS_DIR]['subfolders']. "
            "This would make files inside depth_aligned/ compliant with enforcement rules."
        )

    def test_support_cfg_has_purpose_key(self):
        """Sanity check: support entry is a non-empty Mapping with a purpose."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        tests_subs = get_all_territories().get(TESTS_DIR, {}).get("subfolders", {})
        support_cfg = tests_subs.get("support", None)
        assert support_cfg is not None, "support entry missing from tests subfolders"
        assert isinstance(support_cfg, _Mapping), "support entry must be a dict or MappingProxyType"
        assert "purpose" in support_cfg, "support entry must have a 'purpose' key"


# ---------------------------------------------------------------------------
# Layer 2: Enforcement gap documentation
# The key finding: _enforce_tests_structure uses only rel.parts[0] for the
# approved-subfolder check, so phantom subdirs INSIDE approved dirs are invisible.
# ---------------------------------------------------------------------------


class TestEnforcementGapDocumentation:
    """
    [FIX-1 APPLIED] The enforcement gap is now closed.

    Previously, _enforce_tests_structure used an unconditional `continue` for any file
    whose rel.parts[0] was in the approved set, silently accepting *Agent.py files placed
    inside tests/support/l1_cognition/ etc.

    After Fix 1, the approved-subfolder branch runs the infra-exemption and test_ prefix
    checks BEFORE continuing, so non-test files (including *Agent.py) inside approved
    subfolders ARE now detected as violations.

    The Layer 3 filesystem invariant (test_phantom_folder_regression.py) remains
    load-bearing for files that exist on disk outside any scan.
    """

    def test_phantom_l1_cognition_under_support_not_detected(self, tmp_path):
        """
        [FIX-1] tests/support/l1_cognition/SomeAgent.py must now be detected.
        rel.parts[0] = 'support' → approved, but no test_ prefix → violation logged.
        """
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("support/l1_cognition/SomeAgent.py", "class SomeAgent: pass"),
                ],
            )
        assert results["violations_found"] >= 1, (
            "FIX-1: tests/support/l1_cognition/SomeAgent.py must now be detected "
            "by _enforce_tests_structure (gap closed)."
        )

    def test_phantom_l2_execution_under_support_not_detected(self, tmp_path):
        """[FIX-1] tests/support/l2_execution/ *Agent.py files are now detected."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("support/l2_execution/ExecutorAgent.py", "class ExecutorAgent: pass"),
                    ("support/l2_execution/SubAgent.py", "class SubAgent: pass"),
                ],
            )
        assert results["violations_found"] == 2

    def test_phantom_depth_aligned_under_support_not_detected(self, tmp_path):
        """[FIX-1] Non-test file in tests/support/depth_aligned/ is now detected."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("support/depth_aligned/schema_cache.py", "# phantom"),
                ],
            )
        assert results["violations_found"] == 1

    def test_non_test_file_in_phantom_support_subdir_not_detected(self, tmp_path):
        """
        [FIX-1] A non-test_ file inside tests/support/l1_cognition/ is now detected
        (same rule as placing it directly at tests/ root).
        """
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("support/l1_cognition/AgentWithNoTestPrefix.py", "class Agent: pass"),
                ],
            )
        assert results["violations_found"] == 1

    def test_stress_50_phantom_support_files_all_skipped(self, tmp_path):
        """
        [FIX-1] Stress: 50 non-test_ files across phantom l*_* subdirs under tests/support/
        are ALL now detected (one violation per file).
        """
        agent = _make_agent()
        phantom_subdirs = [
            "l0_routing",
            "l1_cognition",
            "l2_execution",
            "l3_orchestration",
            "l4_state",
            "l5_safety",
            "depth_aligned",
            "phantom_dir",
            "old_agents",
            "legacy",
        ]
        files = []
        for i, subdir in enumerate(phantom_subdirs):
            for j in range(5):
                files.append(
                    (
                        f"support/{subdir}/Agent_{i}_{j}.py",
                        f"class Agent_{i}_{j}: pass",
                    )
                )

        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(agent, tmp_path, files)

        assert results["violations_found"] == 50, (
            f"[FIX-1] Expected 50 violations (one per phantom support file), "
            f"but got {results['violations_found']}."
        )

    def test_real_support_files_not_reported(self, tmp_path):
        """
        [FIX-1] Direct non-test files in tests/support/ ARE now reported (gap closed).
        Infra files (conftest, __init__) and test_-prefixed files remain exempt.
        """
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("support/BaseHealingTestCase.py", "class BaseHealingTestCase: pass"),
                    ("support/test_helpers.py", "def helper(): pass"),
                    ("support/conftest.py", "import pytest"),
                ],
            )
        # BaseHealingTestCase.py has no test_ prefix and is not infra → 1 violation
        # test_helpers.py has test_ prefix → clean
        # conftest.py is infra → exempt
        assert results["violations_found"] == 1

    def test_real_violations_not_masked_by_phantom_support_files(self, tmp_path):
        """
        [FIX-1] Matrix: both BadAgent.py at root AND PhantomAgent.py in support/l1_cognition/
        are now detected (2 violations total).
        """
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("BadAgent.py", "class BadAgent: pass"),
                    ("support/l1_cognition/PhantomAgent.py", "class PhantomAgent: pass"),
                    ("unit/test_ok.py", "def test_ok(): pass"),
                ],
            )
        assert results["violations_found"] == 2, (
            "[FIX-1] Both BadAgent.py at root and PhantomAgent.py in support/l1_cognition/ "
            "must now be detected."
        )

    def test_duplicate_agent_files_in_phantom_support_subdirs_all_skipped(self, tmp_path):
        """
        [FIX-1] Bug 1 exact scenario: agent files duplicated into tests/support/l*_* during
        healing are now ALL detected by _enforce_tests_structure (gap closed).
        """
        agent = _make_agent()
        # Simulates the exact files that appeared in the bug report
        duplicated_agents = [
            "support/l1_cognition/AutonomicMonitorAgent.py",
            "support/l1_cognition/PilotOrchestrator.py",
            "support/l2_execution/InfrastructureOrchestrator.py",
            "support/l5_safety/HierarchyAgent.py",
            "support/l5_safety/LocationHealerAgent.py",
        ]
        files = [(f, "class Agent: pass") for f in duplicated_agents]
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(agent, tmp_path, files)

        assert results["violations_found"] == 5, (
            "[FIX-1] All 5 duplicated agent files in tests/support/l*_* subdirs must "
            "now be detected by _enforce_tests_structure."
        )

    def test_gatekeeper_never_called_for_phantom_support_files(self, tmp_path):
        """
        Side-effect safety: even if phantom support files are present,
        gatekeeper.safe_move is NEVER called (report-only behavior).
        """
        agent = _make_agent(healing_enabled=True)
        with _patch_approved(APPROVED), _patch_whitelist():
            _run_enforce(
                agent,
                tmp_path,
                [
                    ("support/l1_cognition/SomeAgent.py", "class SomeAgent: pass"),
                    ("support/depth_aligned/__init__.py", ""),
                ],
            )
        agent.gatekeeper.safe_move.assert_not_called()


# ---------------------------------------------------------------------------
# create_missing_structure: support stays flat
# ---------------------------------------------------------------------------


class TestCreateMissingStructureSupportFlat:
    """Verify that create_missing_structure never creates subdirectories inside support/."""

    def test_create_territory_structure_support_empty_config_no_subdirs(self, tmp_path):
        """
        support subfolders config is {purpose: '...'} with no subfolders key
        → _create_territory_structure creates NO child directories.
        """
        agent = _make_agent(healing_enabled=True)
        created_labels: list[str] = []

        def _fake_create(path, results, label):
            created_labels.append(label)

        agent._create_dir_with_init = _fake_create

        territory_path = tmp_path / TESTS_DIR / "support"
        territory_path.mkdir(parents=True, exist_ok=True)
        support_config = {"purpose": "Shared test infrastructure"}
        results = {"violations_found": 0, "created": [], "errors": []}

        agent._create_territory_structure("tests/support", territory_path, support_config, results)

        assert created_labels == [], (
            f"create_territory_structure unexpectedly tried to create: {created_labels}. "
            "tests/support/ must remain flat — no subdirs."
        )
        assert results["violations_found"] == 0

    def test_create_territory_structure_no_required_subfolders_no_dirs(self, tmp_path):
        """
        If required_subfolders is absent from support config, no dirs are created.
        """
        agent = _make_agent(healing_enabled=True)
        created_labels: list[str] = []

        def _fake_create(path, results, label):
            created_labels.append(label)

        agent._create_dir_with_init = _fake_create

        territory_path = tmp_path / TESTS_DIR / "support"
        territory_path.mkdir(parents=True)
        results = {"violations_found": 0, "created": [], "errors": []}

        agent._create_territory_structure("tests/support", territory_path, {}, results)

        assert created_labels == []

    def test_create_missing_structure_no_l_layer_under_tests_support(self, tmp_path):
        """
        End-to-end: create_missing_structure with controlled SOVEREIGN_TERRITORIES
        including a real-world 'support' entry (no subfolders).
        ensure_dir is never called with a path that looks like tests/support/l*_*.
        """
        agent = _make_agent(healing_enabled=True)
        agent.project_root = tmp_path

        ensure_dir_calls: list[str] = []

        def _track(path):
            ensure_dir_calls.append(str(path))

        l_pattern = re.compile(r"^l[0-9]_[a-z]+$")
        clean_st = {
            TESTS_DIR: {
                "required_subfolders": [],
                "subfolders": {
                    "unit": {"purpose": "unit tests"},
                    "support": {"purpose": "shared test infrastructure"},
                },
            },
        }
        with (
            patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg") as mock_wg,
            patch(
                "agentic_core.L5_safety.reasoning.hierarchy_healer.SOVEREIGN_TERRITORIES",
                clean_st,
            ),
            patch(
                "agentic_core.L5_safety.reasoning.hierarchy_healer.ENFORCED_TERRITORIES",
                frozenset({TESTS_DIR}),
            ),
        ):
            mock_wg.ensure_dir.side_effect = _track
            mock_wg.touch_file = MagicMock()
            agent.create_missing_structure()

        violations = [
            p
            for p in ensure_dir_calls
            if "support" in p and any(l_pattern.match(part) for part in Path(p).parts)
        ]
        assert not violations, (
            f"create_missing_structure tried to create L-layer dirs under tests/support/: {violations}"
        )


# ---------------------------------------------------------------------------
# Depth enforcement on files inside tests/support/l*_*
# ---------------------------------------------------------------------------


class TestDepthEnforcementPhantomSupportFiles:
    """
    Verify that depth enforcement also has the same bypass for files inside
    phantom support subdirs, and that no new phantom dirs are created.
    """

    def _make_heal_agent(self, project_root: Path):
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        agent = object.__new__(HierarchyAgent)
        agent.project_root = project_root
        agent.agent_name = "HierarchyAgent"
        agent.healing_enabled = True
        gk = MagicMock()
        gk.safe_move.return_value = MagicMock(success=True, error=None)
        agent.gatekeeper = gk
        agent._legacy_archive_depth_violation = MagicMock(return_value=0)
        return agent

    def _call(self, agent, file_path, rel, depth, expected):
        with patch("agentic_core.L5_safety.reasoning.hierarchy_healer._wg") as mock_wg:
            mock_wg.ensure_dir = MagicMock()
            return agent._heal_depth_violation(file_path, rel, depth, expected)

    def test_phantom_support_file_correct_depth_bypasses_heal(self, tmp_path):
        """
        tests/support/l1_cognition/SomeAgent.py at depth 2 (expected 2).
        _heal_depth_violation returns 0 → phantom subdir NOT healed by depth enforcement.
        """
        agent = self._make_heal_agent(tmp_path)
        rel = Path("tests/support/l1_cognition/SomeAgent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = self._call(agent, file_path, rel, depth=3, expected=3)

        assert result == 0
        agent.gatekeeper.safe_move.assert_not_called()

    def test_phantom_support_file_too_deep_is_healed_out(self, tmp_path):
        """
        tests/support/l1_cognition/sub/SomeAgent.py at depth 4 > expected 3.
        DEEP path → gk.safe_move called, file flattened.
        """
        agent = self._make_heal_agent(tmp_path)
        rel = Path("tests/support/l1_cognition/sub/SomeAgent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        result = self._call(agent, file_path, rel, depth=4, expected=3)

        agent.gatekeeper.safe_move.assert_called_once()
        assert result == 1

    def test_phantom_support_heal_never_creates_depth_aligned(self, tmp_path):
        """
        DEEP heal of phantom support file never creates a new depth_aligned directory.
        """
        agent = self._make_heal_agent(tmp_path)
        rel = Path("tests/support/l1_cognition/sub/SomeAgent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        self._call(agent, file_path, rel, depth=4, expected=3)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        assert "depth_aligned" not in str(target)

    def test_phantom_support_deep_heal_drops_sub_component(self, tmp_path):
        """
        DEEP heal: tests/support/l1_cognition/sub/SomeAgent.py → depth=4, expected=3.
        Flattened target: parts[:3] + (name,) drops 'sub'.
        """
        agent = self._make_heal_agent(tmp_path)
        rel = Path("tests/support/l1_cognition/sub/SomeAgent.py")
        file_path = tmp_path / rel
        file_path.parent.mkdir(parents=True)
        file_path.write_text("")

        self._call(agent, file_path, rel, depth=4, expected=3)

        target = agent.gatekeeper.safe_move.call_args[0][1]
        assert "sub" not in str(target.relative_to(tmp_path))
        assert target.name == "SomeAgent.py"
