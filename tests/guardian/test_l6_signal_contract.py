"""
Phase D: L6 Signal Contract Tests.

Verifies:
1. GUARDIAN_ARTIFACT_DIR constant matches contract doc
2. GUARDIAN_ARTIFACT_PATTERN produces valid filenames
3. Artifact paths written by guardians match the L6 contract
4. Correlation ID propagates through aggregation
5. Contract doc exists
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_all_guardians import (
    run_all_guardians,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    GUARDIAN_ARTIFACT_DIR,
    GUARDIAN_ARTIFACT_PATTERN,
    ArtifactClass,
    get_artifact_filename,
)
from agentic_core.L0_routing.types.guardian_registry_types import (
    ALL_GUARDIANS,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_repo(tmp_path: Path) -> Path:
    for folder in ("agentic_core", "apps_shared", "tests"):
        d = tmp_path / folder
        d.mkdir()
        (d / "__init__.py").write_text("", encoding="utf-8")
        (d / "real_module.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Constants
# ---------------------------------------------------------------------------


class TestL6Constants:
    def test_artifact_dir_is_posix(self):
        assert "\\" not in GUARDIAN_ARTIFACT_DIR
        assert not GUARDIAN_ARTIFACT_DIR.startswith("/")

    def test_artifact_dir_value(self):
        assert GUARDIAN_ARTIFACT_DIR == "docs/reports/verification/guardian"

    def test_artifact_pattern_has_placeholder(self):
        assert "{guardian_id}" in GUARDIAN_ARTIFACT_PATTERN

    def test_artifact_pattern_produces_valid_name(self):
        name = GUARDIAN_ARTIFACT_PATTERN.format(guardian_id="hygiene")
        assert name == "guardian_hygiene.json"
        assert re.match(r"^guardian_[a-z_]+\.json$", name)


# ---------------------------------------------------------------------------
# 2. Artifact paths match contract
# ---------------------------------------------------------------------------


class TestArtifactPathContract:
    def test_written_artifacts_in_contract_dir(self, clean_repo: Path):
        result = run_all_guardians(
            repo_root=clean_repo,
            write_artifacts_dir=GUARDIAN_ARTIFACT_DIR,
        )
        for artifact in result.artifacts:
            assert artifact.path.startswith(GUARDIAN_ARTIFACT_DIR), (
                f"Artifact path '{artifact.path}' not under '{GUARDIAN_ARTIFACT_DIR}'"
            )

    def test_artifact_filenames_match_pattern(self, clean_repo: Path):
        result = run_all_guardians(
            repo_root=clean_repo,
            write_artifacts_dir=GUARDIAN_ARTIFACT_DIR,
        )
        valid_prefixes = ("guardian_", "combined_guardian_")
        for artifact in result.artifacts:
            filename = artifact.path.split("/")[-1]
            assert filename.startswith(valid_prefixes), (
                f"Artifact filename '{filename}' does not match pattern (expected prefix: {valid_prefixes})"
            )
            assert filename.endswith(".json"), f"Artifact filename '{filename}' is not .json"


# ---------------------------------------------------------------------------
# 3. Correlation ID propagation
# ---------------------------------------------------------------------------


class TestCorrelationId:
    def test_correlation_id_in_combined(self, clean_repo: Path):
        result = run_all_guardians(
            repo_root=clean_repo,
            correlation_id="ci-run-abc-123",
        )
        assert result.correlation_id == "ci-run-abc-123"

    def test_correlation_id_in_serialized(self, clean_repo: Path):
        result = run_all_guardians(
            repo_root=clean_repo,
            correlation_id="ci-run-abc-123",
        )
        d = result.to_dict()
        assert d["correlation_id"] == "ci-run-abc-123"

    def test_no_correlation_id_when_absent(self, clean_repo: Path):
        result = run_all_guardians(repo_root=clean_repo)
        assert result.correlation_id is None
        d = result.to_dict()
        assert "correlation_id" not in d


# ---------------------------------------------------------------------------
# 4. Contract document exists
# ---------------------------------------------------------------------------


class TestContractDoc:
    def test_guardian_to_l6_doc_exists(self):
        doc = PROJECT_ROOT / "docs" / "contracts" / "guardian_to_L6.md"
        assert doc.exists(), "L6 ingestion contract document missing"

    def test_contract_module_exists(self):
        mod = PROJECT_ROOT / "agentic_core" / "L0_routing" / "types" / "guardian_contract.py"
        assert mod.exists()


# ---------------------------------------------------------------------------
# 5. Artifact class (Phase 4: Individual vs Aggregate)
# ---------------------------------------------------------------------------


class TestArtifactClass:
    """Test artifact classification and filename generation."""

    def test_artifact_class_enum_values(self):
        assert ArtifactClass.INDIVIDUAL.value == "individual"
        assert ArtifactClass.AGGREGATE.value == "aggregate"

    def test_individual_artifact_pattern(self):
        filename = get_artifact_filename("hygiene", "abc-123", ArtifactClass.INDIVIDUAL)
        assert filename == "guardian_hygiene_abc-123.json"

    def test_individual_artifact_no_correlation(self):
        filename = get_artifact_filename("hygiene", None, ArtifactClass.INDIVIDUAL)
        assert filename == "guardian_hygiene_result.json"

    def test_aggregate_artifact_pattern(self):
        filename = get_artifact_filename(None, "abc-123", ArtifactClass.AGGREGATE)
        assert filename == "combined_guardian_abc-123.json"

    def test_aggregate_artifact_no_correlation(self):
        filename = get_artifact_filename(None, None, ArtifactClass.AGGREGATE)
        assert filename == "combined_guardian_result.json"

    def test_individual_requires_guardian_id(self):
        with pytest.raises(ValueError, match="guardian_id required"):
            get_artifact_filename(None, "abc-123", ArtifactClass.INDIVIDUAL)

    def test_registry_guardians_produce_valid_filenames(self):
        for spec in ALL_GUARDIANS:
            filename = get_artifact_filename(spec.guardian_id, "corr-123", ArtifactClass.INDIVIDUAL)
            assert filename.startswith("guardian_")
            assert filename.endswith(".json")
            assert spec.guardian_id in filename
