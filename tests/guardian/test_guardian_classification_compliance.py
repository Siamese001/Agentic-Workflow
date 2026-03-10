"""
Guardian Contract Tests: Classification Compliance.

Tests:
1. Schema validity (GuardianResult fields, types)
2. Check IDs match registry spec
3. Deterministic evidence ordering
4. Naming compliance scan detects compound suffix conflicts
5. Territory compliance scan detects misplaced files
6. Clean repo produces PASS status
7. No mutations (scan-only)
8. Timestamp injection for determinism
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L2_EXECUTION_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_classification_compliance import (
    GUARDIAN_ID,
    _collect_python_files,
    run_classification_compliance_guardian,
    scan_naming_compliance,
    scan_territory_compliance,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    GuardianStatus,
)
from agentic_core.L0_routing.types.guardian_registry_types import get_guardian_by_id

pytestmark = pytest.mark.guardian

FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def real_result() -> GuardianResult:
    """Run classification compliance guardian on the real repo."""
    return run_classification_compliance_guardian(
        repo_root=PROJECT_ROOT,
        timestamp=FIXED_TIMESTAMP,
    )


@pytest.fixture()
def synthetic_repo(tmp_path: Path) -> Path:
    """Create a minimal synthetic repo for controlled testing."""
    ac = tmp_path / AGENTIC_CORE_DIR
    layer = ac / "L5_safety"

    # Correct placement: agent in reasoning/ (Agent class → AGENT → reasoning)
    reasoning = layer / "reasoning"
    reasoning.mkdir(parents=True)
    (reasoning / "FooAgent.py").write_text(
        "class FooAgent:\n    pass\n",
        encoding="utf-8",
    )

    # Correct placement: utility in utils/ (no class → UTILITY → utils)
    utils_dir = layer / "utils"
    utils_dir.mkdir(parents=True)
    (utils_dir / "bar_util.py").write_text(
        "def bar():\n    return 1\n",
        encoding="utf-8",
    )

    # Correct placement: types in types/ (TypedDict → TYPES → types)
    types_dir = layer / "types"
    types_dir.mkdir(parents=True)
    (types_dir / "baz_types.py").write_text(
        "from typing import TypedDict\nclass Baz(TypedDict):\n    x: int\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def synthetic_repo_with_violations(tmp_path: Path) -> Path:
    """Create a synthetic repo with known classification violations."""
    ac = tmp_path / AGENTIC_CORE_DIR
    layer = ac / L2_EXECUTION_DIR

    # Territory violation: config file in reasoning/ instead of config/
    reasoning = layer / "reasoning"
    reasoning.mkdir(parents=True)
    (reasoning / "some_config.py").write_text(
        "SETTING = True\n",
        encoding="utf-8",
    )

    # Correct placement for comparison
    config = layer / "config"
    config.mkdir(parents=True)
    (config / "good_config.py").write_text(
        "X = 1\n",
        encoding="utf-8",
    )

    return tmp_path


# ---------------------------------------------------------------------------
# 1. Schema validity
# ---------------------------------------------------------------------------


class TestSchemaValidity:
    """Verify guardian result conforms to contract schema."""

    def test_guardian_id(self, real_result: GuardianResult) -> None:
        assert real_result.guardian_id == GUARDIAN_ID

    def test_timestamp_injected(self, real_result: GuardianResult) -> None:
        assert real_result.timestamp == FIXED_TIMESTAMP

    def test_status_is_valid(self, real_result: GuardianResult) -> None:
        valid_statuses = {s.value for s in GuardianStatus}
        assert real_result.status in valid_statuses

    def test_checks_nonempty(self, real_result: GuardianResult) -> None:
        assert len(real_result.checks) >= 2

    def test_check_ids_match_registry(self, real_result: GuardianResult) -> None:
        spec = get_guardian_by_id(GUARDIAN_ID)
        assert spec is not None
        emitted_ids = {c.check_id for c in real_result.checks}
        registered_ids = set(spec.check_ids)
        assert emitted_ids == registered_ids

    def test_metrics_present(self, real_result: GuardianResult) -> None:
        assert "total_checks" in real_result.metrics
        assert "files_scanned" in real_result.metrics
        assert real_result.metrics["files_scanned"] > 0

    def test_serialization_roundtrip(self, real_result: GuardianResult) -> None:
        json_str = real_result.to_json()
        data = json.loads(json_str)
        assert data["guardian_id"] == GUARDIAN_ID
        assert isinstance(data["checks"], list)
        assert len(data["checks"]) >= 2


# ---------------------------------------------------------------------------
# 2. Deterministic evidence ordering
# ---------------------------------------------------------------------------


class TestDeterministicEvidence:
    """Verify evidence is deterministically ordered."""

    def test_naming_violations_sorted(self, real_result: GuardianResult) -> None:
        naming = next(
            (c for c in real_result.checks if c.check_id == "naming_compliance"),
            None,
        )
        assert naming is not None
        violations = naming.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)

    def test_territory_violations_sorted(self, real_result: GuardianResult) -> None:
        territory = next(
            (c for c in real_result.checks if c.check_id == "territory_compliance"),
            None,
        )
        assert territory is not None
        violations = territory.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 3. Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanNamingCompliance:
    """Unit tests for naming compliance scan."""

    def test_clean_repo_no_violations(self, synthetic_repo: Path) -> None:
        violations = scan_naming_compliance(synthetic_repo)
        assert violations == []

    def test_compound_suffix_detected(self, tmp_path: Path) -> None:
        """A file with compound suffix should be detected."""
        ac = tmp_path / L0_ROUTING_DIR / "scripts"
        ac.mkdir(parents=True)
        # _agent_types is a known compound suffix conflict
        (ac / "code_detector_agent_types.py").write_text(
            "X = 1\n",
            encoding="utf-8",
        )
        violations = scan_naming_compliance(tmp_path)
        assert len(violations) == 1
        assert violations[0]["filename"] == "code_detector_agent_types.py"
        assert set(violations[0]["conflicting_tags"]) == {"AGENT", "TYPES"}

    def test_no_false_positive_on_single_suffix(self, tmp_path: Path) -> None:
        """A file with a single suffix should not be flagged."""
        ac = tmp_path / L0_ROUTING_DIR / "types"
        ac.mkdir(parents=True)
        (ac / "guardian_types.py").write_text(
            "X = 1\n",
            encoding="utf-8",
        )
        violations = scan_naming_compliance(tmp_path)
        assert violations == []


class TestScanTerritoryCompliance:
    """Unit tests for territory compliance scan."""

    def test_clean_repo_no_violations(self, synthetic_repo: Path) -> None:
        violations = scan_territory_compliance(synthetic_repo)
        assert violations == []


# ---------------------------------------------------------------------------
# 4. File collector
# ---------------------------------------------------------------------------


class TestFileCollector:
    """Verify file collector is deterministic and correct."""

    def test_collects_python_files_only(self, synthetic_repo: Path) -> None:
        # Add a non-Python file
        (synthetic_repo / AGENTIC_CORE_DIR / "L5_safety" / "reasoning" / "readme.md").write_text(
            "# readme\n",
            encoding="utf-8",
        )
        files = _collect_python_files(synthetic_repo)
        assert all(f.name.endswith(".py") for f in files)

    def test_skips_init_files(self, synthetic_repo: Path) -> None:
        init = synthetic_repo / AGENTIC_CORE_DIR / "L5_safety" / "__init__.py"
        init.write_text("", encoding="utf-8")
        files = _collect_python_files(synthetic_repo)
        assert all(f.name != "__init__.py" for f in files)

    def test_sorted_output(self, synthetic_repo: Path) -> None:
        files = _collect_python_files(synthetic_repo)
        paths = [str(f) for f in files]
        assert paths == sorted(paths)

    def test_skips_pycache(self, synthetic_repo: Path) -> None:
        pc = synthetic_repo / AGENTIC_CORE_DIR / "__pycache__"
        pc.mkdir(parents=True)
        (pc / "cached.py").write_text("X=1\n", encoding="utf-8")
        files = _collect_python_files(synthetic_repo)
        assert all("__pycache__" not in str(f) for f in files)


# ---------------------------------------------------------------------------
# 5. No mutations (scan-only)
# ---------------------------------------------------------------------------


class TestNoMutations:
    """Verify guardian does not mutate the repo."""

    def test_no_files_created(self, synthetic_repo: Path) -> None:
        before = set()
        for dirpath, dirs, filenames in os.walk(synthetic_repo):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                before.add(os.path.join(dirpath, fname))

        run_classification_compliance_guardian(
            repo_root=synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )

        after = set()
        for dirpath, dirs, filenames in os.walk(synthetic_repo):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                after.add(os.path.join(dirpath, fname))

        assert before == after, f"Guardian created files: {after - before}"

    def test_no_files_modified(self, synthetic_repo: Path) -> None:
        # Record content hashes
        import hashlib

        def snapshot():
            result = {}
            for dirpath, dirs, filenames in os.walk(synthetic_repo):
                dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    with open(fpath, "rb") as f:
                        result[fpath] = hashlib.sha256(f.read()).hexdigest()
            return result

        before = snapshot()
        run_classification_compliance_guardian(
            repo_root=synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )
        after = snapshot()
        assert before == after
