"""
Guardian Contract Tests: Architecture Governance.

Tests:
1. Schema validity (GuardianResult fields, types)
2. Check IDs match registry spec
3. Deterministic evidence ordering
4. Import compliance scan detects upward dependencies
5. Layer gravity scan detects misplaced agents
6. Clean synthetic repo produces PASS
7. No mutations (scan-only)
8. Timestamp injection for determinism
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_architecture_governance import (
    GUARDIAN_ID,
    _collect_python_files,
    run_architecture_governance_guardian,
    scan_import_compliance,
)
from agentic_core.L0_routing.types.guardian_contract import (
    GuardianResult,
    GuardianStatus,
)
from agentic_core.L0_routing.types.guardian_registry import get_guardian_by_id

pytestmark = pytest.mark.guardian

FIXED_TIMESTAMP = "2000-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def real_result() -> GuardianResult:
    """Run architecture governance guardian on the real repo."""
    return run_architecture_governance_guardian(
        repo_root=PROJECT_ROOT,
        timestamp=FIXED_TIMESTAMP,
    )


@pytest.fixture()
def clean_synthetic_repo(tmp_path: Path) -> Path:
    """Create a synthetic repo with no import violations."""
    ac = tmp_path / "agentic_core"

    # L0 file importing from L0 only (no upward)
    l0 = ac / "L0_routing" / "scripts"
    l0.mkdir(parents=True)
    (l0 / "helper.py").write_text(
        "from agentic_core.L0_routing.types import foo\n",
        encoding="utf-8",
    )

    # L5 file importing from L0 (downward — allowed)
    l5 = ac / "L5_safety" / "reasoning"
    l5.mkdir(parents=True)
    (l5 / "SafetyAgent.py").write_text(
        "from agentic_core.L0_routing.types import bar\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def violating_synthetic_repo(tmp_path: Path) -> Path:
    """Create a synthetic repo with a known upward import violation."""
    ac = tmp_path / "agentic_core"

    # L0 file importing from L5 (upward — violation!)
    l0 = ac / "L0_routing" / "scripts"
    l0.mkdir(parents=True)
    (l0 / "bad_import.py").write_text(
        "from agentic_core.L5_safety.reasoning import SomeAgent\n",
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

    def test_import_violations_sorted(self, real_result: GuardianResult) -> None:
        check = next(
            (c for c in real_result.checks if c.check_id == "import_compliance"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        keys = [(v["path"], v["line_number"]) for v in violations]
        assert keys == sorted(keys)

    def test_gravity_violations_sorted(self, real_result: GuardianResult) -> None:
        check = next(
            (c for c in real_result.checks if c.check_id == "layer_gravity"),
            None,
        )
        assert check is not None
        violations = check.evidence.get("violations", [])
        paths = [v["path"] for v in violations]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 3. Scan function unit tests
# ---------------------------------------------------------------------------


class TestScanImportCompliance:
    """Unit tests for import compliance scan."""

    def test_clean_repo_no_violations(self, clean_synthetic_repo: Path) -> None:
        violations = scan_import_compliance(clean_synthetic_repo)
        assert violations == []

    def test_upward_import_detected(self, violating_synthetic_repo: Path) -> None:
        """L0 importing from L5 is an upward violation."""
        violations = scan_import_compliance(violating_synthetic_repo)
        assert len(violations) == 1
        v = violations[0]
        assert v["source_layer"] == "L0"
        assert v["target_layer"] == "L5"
        assert "bad_import.py" in v["path"]

    def test_downward_import_allowed(self, tmp_path: Path) -> None:
        """L5 importing from L0 is allowed (downward)."""
        ac = tmp_path / "agentic_core" / "L5_safety" / "reasoning"
        ac.mkdir(parents=True)
        (ac / "agent.py").write_text(
            "from agentic_core.L0_routing.types import x\n",
            encoding="utf-8",
        )
        violations = scan_import_compliance(tmp_path)
        assert violations == []

    def test_same_layer_import_allowed(self, tmp_path: Path) -> None:
        """Same-layer imports are allowed."""
        ac = tmp_path / "agentic_core" / "L2_execution" / "scripts"
        ac.mkdir(parents=True)
        (ac / "tool.py").write_text(
            "from agentic_core.L2_execution.types import y\n",
            encoding="utf-8",
        )
        violations = scan_import_compliance(tmp_path)
        assert violations == []


# ---------------------------------------------------------------------------
# 4. File collector
# ---------------------------------------------------------------------------


class TestFileCollector:
    """Verify file collector for architecture scanning."""

    def test_collects_agentic_core_only(self, clean_synthetic_repo: Path) -> None:
        files = _collect_python_files(clean_synthetic_repo)
        assert all("agentic_core" in str(f) for f in files)

    def test_sorted_output(self, clean_synthetic_repo: Path) -> None:
        files = _collect_python_files(clean_synthetic_repo)
        paths = [str(f) for f in files]
        assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# 5. No mutations (scan-only)
# ---------------------------------------------------------------------------


class TestNoMutations:
    """Verify guardian does not mutate the repo."""

    def test_no_files_created(self, clean_synthetic_repo: Path) -> None:
        before = set()
        for dirpath, _, filenames in os.walk(clean_synthetic_repo):
            for fname in filenames:
                before.add(os.path.join(dirpath, fname))

        run_architecture_governance_guardian(
            repo_root=clean_synthetic_repo,
            timestamp=FIXED_TIMESTAMP,
        )

        after = set()
        for dirpath, _, filenames in os.walk(clean_synthetic_repo):
            for fname in filenames:
                after.add(os.path.join(dirpath, fname))

        assert before == after, f"Guardian created files: {after - before}"
