"""
Phase 4: Aggregator Invariants Lock (Contract of Contracts).

Enforces that aggregator behavior is deterministic and contract-compliant:
1. Deterministic ordering (registry order)
2. Correlation ID propagation
3. Rollup precedence locked (ERROR > FAIL > PASS)
4. Per-guardian metadata preserved
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_all_guardians import (
    run_all_guardians,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    AGGREGATE_GUARDIAN_ID,
    CONTRACT_VERSION,
    GuardianResult,
    GuardianStatus,
)
from agentic_core.L0_routing.types.guardian_registry_types import (
    ALL_GUARDIANS,
)

pytestmark = pytest.mark.guardian


@pytest.fixture
def clean_repo(robust_tmp_path: Path) -> Path:
    """Minimal sandboxed repo with full SOVEREIGN_TERRITORIES structure."""
    from agentic_core.L0_routing.scripts.run_guardian_hierarchy_compliance import (
        _get_l3_subfolders,
    )
    from agentic_core.L5_safety.config.structure_blueprint_config import (
        SOVEREIGN_TERRITORIES,
    )

    # Build complete hierarchy from SOVEREIGN_TERRITORIES.
    # Each dir gets __init__.py + README.md to avoid init_only_folders
    # without triggering classification/location violations from .py stubs.
    for root_name, root_def in SOVEREIGN_TERRITORIES.items():
        root_dir = robust_tmp_path / root_name
        root_dir.mkdir(exist_ok=True)
        (root_dir / "__init__.py").write_text("", encoding="utf-8")
        (root_dir / "README.md").write_text("stub", encoding="utf-8")

        if not hasattr(root_def, "get"):
            continue
        l2_subs = root_def.get("subfolders", {})
        if not hasattr(l2_subs, "keys"):
            continue
        for l2_name in l2_subs.keys():
            l2_dir = root_dir / l2_name
            l2_dir.mkdir(exist_ok=True)
            (l2_dir / "__init__.py").write_text("", encoding="utf-8")
            (l2_dir / "README.md").write_text("stub", encoding="utf-8")
            l2_def = l2_subs.get(l2_name, {})
            for l3_name in _get_l3_subfolders(l2_def):
                l3_dir = l2_dir / l3_name
                l3_dir.mkdir(exist_ok=True)
                (l3_dir / "__init__.py").write_text("", encoding="utf-8")
                (l3_dir / "README.md").write_text("stub", encoding="utf-8")
    return robust_tmp_path


class TestDeterministicOrdering:
    """Aggregator must execute guardians in registry order."""

    def test_execution_order_matches_registry(self, clean_repo: Path):
        """Guardian execution order must match ALL_GUARDIANS order."""
        result = run_all_guardians(repo_root=clean_repo)

        # Extract guardian_ids from checks (format: "guardian_{id}")
        executed_ids = []
        for check in result.checks:
            if check.check_id.startswith("guardian_"):
                gid = check.check_id.replace("guardian_", "")
                if gid not in executed_ids:
                    executed_ids.append(gid)

        # Registry order (enabled only)
        registry_order = [spec.guardian_id for spec in ALL_GUARDIANS if spec.enabled_by_default]

        assert executed_ids == registry_order, (
            f"Execution order mismatch. Expected: {registry_order}, Got: {executed_ids}"
        )

    def test_ordering_is_stable_across_runs(self, clean_repo: Path):
        """Multiple runs must produce identical ordering."""
        r1 = run_all_guardians(repo_root=clean_repo)
        r2 = run_all_guardians(repo_root=clean_repo)

        ids1 = [c.check_id for c in r1.checks]
        ids2 = [c.check_id for c in r2.checks]

        assert ids1 == ids2, "Ordering must be stable across runs"


class TestCorrelationIdPropagation:
    """Correlation ID must propagate to aggregate result."""

    def test_correlation_id_in_aggregate(self, clean_repo: Path):
        """Aggregate result must include correlation_id."""
        result = run_all_guardians(
            repo_root=clean_repo,
            correlation_id="test-run-123",
        )
        assert result.correlation_id == "test-run-123"

    def test_correlation_id_in_serialized(self, clean_repo: Path):
        """Serialized aggregate must include correlation_id."""
        result = run_all_guardians(
            repo_root=clean_repo,
            correlation_id="test-run-123",
        )
        d = result.to_dict()
        assert d["correlation_id"] == "test-run-123"

    def test_no_correlation_id_when_absent(self, clean_repo: Path):
        """Aggregate without correlation_id must not include it."""
        result = run_all_guardians(repo_root=clean_repo)
        assert result.correlation_id is None
        d = result.to_dict()
        assert "correlation_id" not in d


class TestRollupPrecedence:
    """Global rollup precedence: ERROR > FAIL > PASS."""

    def test_error_overrides_pass_in_rollup(self, clean_repo: Path):
        """Injecting ERROR into any sub-guardian forces aggregate to ERROR."""
        call_count = 0

        def _synthetic(spec, repo_root, artifact_dir, timestamp, correlation_id):
            nonlocal call_count
            call_count += 1
            # First guardian PASS, remaining ERROR — proves ERROR overrides PASS
            status = GuardianStatus.PASS.value if call_count == 1 else GuardianStatus.ERROR.value
            r = GuardianResult(
                guardian_id=spec.guardian_id,
                version=CONTRACT_VERSION,
                status=status,
                summary=f"synthetic {status}",
                correlation_id=correlation_id,
            )
            return r

        with patch(
            "agentic_core.L0_routing.scripts.run_all_guardians._run_single_guardian",
            side_effect=_synthetic,
        ):
            result = run_all_guardians(repo_root=clean_repo)

        assert result.status == GuardianStatus.ERROR.value, (
            f"ERROR must override PASS in rollup, got {result.status}"
        )

    def test_aggregate_status_is_valid_enum_member(self, clean_repo: Path):
        """Aggregate status must be a member of GuardianStatus enum."""
        result = run_all_guardians(repo_root=clean_repo)
        assert result.status in {
            GuardianStatus.PASS.value,
            GuardianStatus.FAIL.value,
            GuardianStatus.ERROR.value,
        }

    def test_fail_overrides_pass(self, clean_repo: Path):
        """If any guardian fails (and none error), aggregate status is FAIL."""
        # Create a violation in an allowed root to trigger FAIL
        (clean_repo / "agentic_core" / "temp.tmp").write_text("temp", encoding="utf-8")

        result = run_all_guardians(repo_root=clean_repo)

        # Should be FAIL due to hygiene guardian detecting temp file
        assert result.status == GuardianStatus.FAIL.value

    def test_all_pass_yields_pass(self, clean_repo: Path):
        """If all guardians pass, aggregate status is PASS."""
        result = run_all_guardians(repo_root=clean_repo)

        # Clean repo should yield PASS
        assert result.status == GuardianStatus.PASS.value


class TestPerGuardianMetadata:
    """Aggregator must preserve per-guardian metadata."""

    def test_per_guardian_checks_present(self, clean_repo: Path):
        """Each enabled guardian must have a check in aggregate."""
        result = run_all_guardians(repo_root=clean_repo)

        enabled_ids = {spec.guardian_id for spec in ALL_GUARDIANS if spec.enabled_by_default}

        check_ids = {
            c.check_id.replace("guardian_", "") for c in result.checks if c.check_id.startswith("guardian_")
        }

        assert check_ids == enabled_ids, f"Missing guardian checks. Expected: {enabled_ids}, Got: {check_ids}"

    def test_guardian_metadata_in_evidence(self, clean_repo: Path):
        """Each guardian check must have metadata in evidence."""
        result = run_all_guardians(repo_root=clean_repo)

        for check in result.checks:
            if check.check_id.startswith("guardian_"):
                assert "guardian_id" in check.evidence, (
                    f"Check {check.check_id} missing guardian_id in evidence"
                )

    def test_contract_version_preserved(self, clean_repo: Path):
        """Aggregate result must preserve contract version."""
        result = run_all_guardians(repo_root=clean_repo)

        from agentic_core.L0_routing.types.guardian_contract_types import (
            CONTRACT_VERSION,
        )

        assert result.version == CONTRACT_VERSION


class TestAggregateArtifactContract:
    """Aggregate artifacts must follow AGGREGATE pattern."""

    def test_aggregate_artifact_uses_correct_pattern(self, clean_repo: Path):
        """Aggregate artifact filename must match AGGREGATE pattern."""
        artifact_dir = clean_repo / "docs" / "reports" / "verification" / "guardian"
        artifact_dir.mkdir(parents=True)

        result = run_all_guardians(
            repo_root=clean_repo,
            write_artifacts_dir=str(artifact_dir.relative_to(clean_repo)),
            correlation_id="test-123",
        )

        # Check artifacts list
        aggregate_artifacts = [a for a in result.artifacts if "combined_guardian" in a.path]

        assert len(aggregate_artifacts) > 0, "No aggregate artifact found"

        # Verify pattern
        for artifact in aggregate_artifacts:
            assert "combined_guardian" in artifact.path
            assert artifact.path.endswith(".json")

    def test_aggregate_without_correlation_uses_fallback(self, clean_repo: Path):
        """Aggregate without correlation_id uses fallback pattern."""
        artifact_dir = clean_repo / "docs" / "reports" / "verification" / "guardian"
        artifact_dir.mkdir(parents=True)

        result = run_all_guardians(
            repo_root=clean_repo,
            write_artifacts_dir=str(artifact_dir.relative_to(clean_repo)),
        )

        aggregate_artifacts = [a for a in result.artifacts if "combined_guardian" in a.path]

        if aggregate_artifacts:
            # Should use fallback pattern (no correlation_id in filename)
            for artifact in aggregate_artifacts:
                assert "combined_guardian_result.json" in artifact.path


class TestArtifactIndex:
    """Aggregate must include index as a first-class field (not in metrics)."""

    def test_index_is_first_class_field(self, clean_repo: Path):
        """Index must be a top-level field on GuardianResult, not in metrics."""
        result = run_all_guardians(repo_root=clean_repo)
        assert hasattr(result, "index"), "GuardianResult must have 'index' field"
        assert isinstance(result.index, dict)
        assert "index" not in result.metrics, "Index must NOT live in metrics"

    def test_index_in_serialized_output(self, clean_repo: Path):
        """Serialized aggregate must include 'index' at top level."""
        result = run_all_guardians(repo_root=clean_repo)
        d = result.to_dict()
        assert "index" in d, "Serialized aggregate must include 'index'"
        assert "index" not in d.get("metrics", {}), "Index must NOT be in metrics"

    def test_index_covers_all_enabled_guardians(self, clean_repo: Path):
        """Index must have an entry for every enabled guardian."""
        result = run_all_guardians(repo_root=clean_repo)
        enabled_ids = {spec.guardian_id for spec in ALL_GUARDIANS if spec.enabled_by_default}
        assert set(result.index.keys()) == enabled_ids, (
            f"Index keys {set(result.index.keys())} != enabled guardians {enabled_ids}"
        )

    def test_index_entries_have_required_fields(self, clean_repo: Path):
        """Each index entry must have 'status' and 'artifacts' fields."""
        result = run_all_guardians(repo_root=clean_repo)
        for gid, entry in result.index.items():
            assert "status" in entry, f"Index[{gid}] missing 'status'"
            assert "artifacts" in entry, f"Index[{gid}] missing 'artifacts'"
            assert isinstance(entry["artifacts"], list), f"Index[{gid}].artifacts must be a list"

    def test_index_status_matches_check_status(self, clean_repo: Path):
        """Index status for each guardian must match the check evidence."""
        result = run_all_guardians(repo_root=clean_repo)
        for check in result.checks:
            if check.check_id.startswith("guardian_"):
                gid = check.check_id.replace("guardian_", "")
                if gid in result.index:
                    assert result.index[gid]["status"] == check.evidence.get("status"), (
                        f"Index[{gid}].status != check evidence status"
                    )

    def test_index_artifact_paths_are_posix(self, clean_repo: Path):
        """All artifact paths in index must be POSIX (no backslashes)."""
        artifact_dir = clean_repo / "docs" / "reports" / "verification" / "guardian"
        artifact_dir.mkdir(parents=True)
        result = run_all_guardians(
            repo_root=clean_repo,
            write_artifacts_dir=str(artifact_dir.relative_to(clean_repo)),
        )
        for gid, entry in result.index.items():
            for path in entry["artifacts"]:
                assert "\\" not in path, f"Index[{gid}] has non-POSIX path: {path}"
                assert not path.startswith("/"), f"Index[{gid}] has absolute path: {path}"

    def test_index_schema_validates(self, clean_repo: Path):
        """Aggregate with index must pass JSON schema validation."""
        from agentic_core.L0_routing.types.guardian_contract_types import validate_against_json_schema

        result = run_all_guardians(repo_root=clean_repo)
        errors = validate_against_json_schema(result.to_dict())
        assert errors == [], f"Schema validation errors: {errors}"


class TestDisabledGuardianExclusion:
    """Disabled guardians must be excluded from aggregate index and checks."""

    def test_index_excludes_disabled_guardians(self, clean_repo: Path):
        """Disabled guardians must NOT appear in combined.index."""
        result = run_all_guardians(repo_root=clean_repo)
        disabled_ids = {spec.guardian_id for spec in ALL_GUARDIANS if not spec.enabled_by_default}
        for gid in disabled_ids:
            assert gid not in result.index, f"Disabled guardian '{gid}' must NOT appear in aggregate index"

    def test_index_keys_are_strict_subset_of_enabled(self, clean_repo: Path):
        """Index keys must be exactly the enabled guardian set — no extras."""
        result = run_all_guardians(repo_root=clean_repo)
        enabled_ids = {spec.guardian_id for spec in ALL_GUARDIANS if spec.enabled_by_default}
        extra = set(result.index.keys()) - enabled_ids
        assert extra == set(), f"Index contains non-enabled guardian IDs: {extra}"

    def test_aggregate_uses_ssot_guardian_id(self, clean_repo: Path):
        """Aggregate result must use AGGREGATE_GUARDIAN_ID from SSOT."""
        result = run_all_guardians(repo_root=clean_repo)
        assert result.guardian_id == AGGREGATE_GUARDIAN_ID, (
            f"Aggregate guardian_id '{result.guardian_id}' != SSOT '{AGGREGATE_GUARDIAN_ID}'"
        )

    def test_disabled_guardians_not_in_checks(self, clean_repo: Path):
        """Disabled guardians must not have check entries in the aggregate."""
        result = run_all_guardians(repo_root=clean_repo)
        disabled_ids = {spec.guardian_id for spec in ALL_GUARDIANS if not spec.enabled_by_default}
        check_guardian_ids = set()
        for check in result.checks:
            if check.check_id.startswith("guardian_"):
                check_guardian_ids.add(check.check_id.replace("guardian_", ""))
        for gid in disabled_ids:
            assert gid not in check_guardian_ids, f"Disabled guardian '{gid}' has a check entry in aggregate"
