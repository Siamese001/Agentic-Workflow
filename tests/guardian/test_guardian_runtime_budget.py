"""
Phase E: Deterministic Performance Guard.

Asserts:
1. Each guardian runs under MAX_GUARDIAN_RUNTIME_MS in sandbox
2. Artifact JSON < MAX_ARTIFACT_SIZE_KB
3. Combined aggregator respects ceilings
4. Constants are reasonable and present
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.scripts.run_all_guardians import (
    run_all_guardians,
)
from agentic_core.L0_maintenance.scripts.run_guardian_hygiene import (
    run_hygiene_guardian,
)
from agentic_core.L0_maintenance.scripts.run_guardian_manifest import (
    run_manifest_guardian,
)
from agentic_core.L0_maintenance.types.guardian_contract import (
    GUARDIAN_ARTIFACT_DIR,
    MAX_ARTIFACT_SIZE_KB,
    MAX_GUARDIAN_RUNTIME_MS,
    MAX_SCAN_DEPTH,
)
from agentic_core.L0_maintenance.types.guardian_registry import (
    ALL_GUARDIANS,
)

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# Algorithmic ceilings (Phase 5: de-flake)
# ---------------------------------------------------------------------------

SANDBOX_FILE_COUNT = 9  # 3 folders × 3 files each
SANDBOX_FOLDER_DEPTH = 2  # Shallow depth for predictable runtime


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sandbox_repo(tmp_path: Path) -> Path:
    """Deterministic sandbox with controlled file count and depth."""
    for folder in ("agentic_core", "apps_shared", "tests"):
        d = tmp_path / folder
        d.mkdir()
        (d / "__init__.py").write_text("", encoding="utf-8")
        (d / "real_module.py").write_text("x = 1\n", encoding="utf-8")
        (d / "another_file.py").write_text("y = 2\n", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Constants are reasonable
# ---------------------------------------------------------------------------


class TestCeilingConstants:
    def test_max_runtime_is_positive(self):
        assert MAX_GUARDIAN_RUNTIME_MS > 0

    def test_max_runtime_under_60s(self):
        assert MAX_GUARDIAN_RUNTIME_MS <= 60_000, "Guardian ceiling > 60s is excessive"

    def test_max_artifact_size_positive(self):
        assert MAX_ARTIFACT_SIZE_KB > 0

    def test_max_artifact_size_under_2mb(self):
        assert MAX_ARTIFACT_SIZE_KB <= 2048, "Artifact ceiling > 2MB is excessive"

    def test_max_scan_depth_positive(self):
        assert MAX_SCAN_DEPTH > 0
        assert MAX_SCAN_DEPTH <= 20

    def test_registry_count_matches_aggregator_expectation(self):
        """Aggregator runtime ceiling assumes bounded guardian count."""
        enabled = [g for g in ALL_GUARDIANS if g.enabled_by_default]
        assert len(enabled) <= 10, f"Too many enabled guardians ({len(enabled)}) - reconsider runtime ceiling"


# ---------------------------------------------------------------------------
# 2. Individual guardian runtime
# ---------------------------------------------------------------------------


class TestGuardianRuntime:
    def test_hygiene_under_ceiling(self, sandbox_repo: Path):
        start = time.monotonic()
        run_hygiene_guardian(repo_root=sandbox_repo)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < MAX_GUARDIAN_RUNTIME_MS, (
            f"Hygiene guardian took {elapsed_ms:.0f}ms (ceiling: {MAX_GUARDIAN_RUNTIME_MS}ms)"
        )

    def test_manifest_under_ceiling(self, sandbox_repo: Path):
        start = time.monotonic()
        run_manifest_guardian(repo_root=sandbox_repo)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < MAX_GUARDIAN_RUNTIME_MS, (
            f"Manifest guardian took {elapsed_ms:.0f}ms (ceiling: {MAX_GUARDIAN_RUNTIME_MS}ms)"
        )

    def test_aggregator_under_ceiling(self, sandbox_repo: Path):
        start = time.monotonic()
        run_all_guardians(repo_root=sandbox_repo)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < MAX_GUARDIAN_RUNTIME_MS, (
            f"Aggregator took {elapsed_ms:.0f}ms (ceiling: {MAX_GUARDIAN_RUNTIME_MS}ms)"
        )


# ---------------------------------------------------------------------------
# 3. Artifact size
# ---------------------------------------------------------------------------


class TestArtifactSize:
    def test_hygiene_artifact_under_ceiling(self, sandbox_repo: Path):
        result = run_hygiene_guardian(repo_root=sandbox_repo)
        json_bytes = len(result.to_json().encode("utf-8"))
        size_kb = json_bytes / 1024
        assert size_kb < MAX_ARTIFACT_SIZE_KB, (
            f"Hygiene artifact is {size_kb:.1f}KB (ceiling: {MAX_ARTIFACT_SIZE_KB}KB)"
        )

    def test_manifest_artifact_under_ceiling(self, sandbox_repo: Path):
        result = run_manifest_guardian(repo_root=sandbox_repo)
        json_bytes = len(result.to_json().encode("utf-8"))
        size_kb = json_bytes / 1024
        assert size_kb < MAX_ARTIFACT_SIZE_KB, (
            f"Manifest artifact is {size_kb:.1f}KB (ceiling: {MAX_ARTIFACT_SIZE_KB}KB)"
        )

    def test_combined_artifact_under_ceiling(self, sandbox_repo: Path):
        result = run_all_guardians(repo_root=sandbox_repo)
        json_bytes = len(result.to_json().encode("utf-8"))
        size_kb = json_bytes / 1024
        assert size_kb < MAX_ARTIFACT_SIZE_KB, (
            f"Combined artifact is {size_kb:.1f}KB (ceiling: {MAX_ARTIFACT_SIZE_KB}KB)"
        )

    def test_written_artifact_under_ceiling(self, sandbox_repo: Path):
        result = run_hygiene_guardian(
            repo_root=sandbox_repo,
            write_artifacts_dir=GUARDIAN_ARTIFACT_DIR,
        )
        out = sandbox_repo / GUARDIAN_ARTIFACT_DIR / "guardian_hygiene_result.json"
        if out.exists():
            size_kb = out.stat().st_size / 1024
            assert size_kb < MAX_ARTIFACT_SIZE_KB
