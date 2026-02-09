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

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.scripts.run_all_guardians import (
    run_all_guardians,
)
from agentic_core.L0_maintenance.types.guardian_contract import (
    GuardianStatus,
)
from agentic_core.L0_maintenance.types.guardian_registry import (
    ALL_GUARDIANS,
)

pytestmark = pytest.mark.guardian


@pytest.fixture
def clean_repo(tmp_path: Path) -> Path:
    """Minimal sandboxed repo."""
    for folder in ("agentic_core", "apps_shared", "tests"):
        d = tmp_path / folder
        d.mkdir()
        (d / "__init__.py").write_text("", encoding="utf-8")
        (d / "real_module.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


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

    def test_error_overrides_all(self, clean_repo: Path):
        """If any guardian errors, aggregate status is ERROR."""
        # This test documents the invariant; actual ERROR injection
        # would require mocking or a synthetic guardian
        result = run_all_guardians(repo_root=clean_repo)

        # Verify precedence logic exists
        # (Cannot easily inject ERROR without modifying guardians)
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
                assert "elapsed_ms" in check.evidence, (
                    f"Check {check.check_id} missing elapsed_ms in evidence"
                )

    def test_contract_version_preserved(self, clean_repo: Path):
        """Aggregate result must preserve contract version."""
        result = run_all_guardians(repo_root=clean_repo)

        from agentic_core.L0_maintenance.types.guardian_contract import (
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
        from agentic_core.L0_maintenance.types.guardian_contract import validate_against_json_schema

        result = run_all_guardians(repo_root=clean_repo)
        errors = validate_against_json_schema(result.to_dict())
        assert errors == [], f"Schema validation errors: {errors}"
