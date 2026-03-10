"""Unit tests for ADG Drift Diff (Phase 7).

Tests cover:
- Same artifact compared against itself: passes, zero regressions
- Increased unresolved imports -> R1 regression (HIGH)
- Increased layer violations -> R2 regression (HIGH)
- Increased orphan modules > tolerance -> R3 regression (MEDIUM)
- strict=False: MEDIUM regressions don't fail
- strict=True: any regression fails
- DriftDiffResult.to_dict has required keys
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agentic_core.adg.applications.drift_diff import run_drift_diff

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_artifact(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _minimal_artifact(
    *,
    unresolved_count: int = 0,
    layer_violation_count: int = 0,
    orphan_module_count: int = 0,
    entity_count: int = 5,
    relation_count: int = 3,
    commit: str = "abc",
    digest: str = "a" * 64,
) -> dict:
    return {
        "schema_version": "3.0.0",
        "commit_sha": commit,
        "scanner_digest": "s" * 64,
        "artifact_digest": digest,
        "entities": [{"adg_name": f"ADG::Module::mod_{i}.py"} for i in range(entity_count)],
        "relations": [
            {
                "from_name": f"ADG::Module::mod_{i}.py",
                "relation_type": "imports",
                "to_name": f"ADG::Module::mod_{i + 1}.py",
            }
            for i in range(relation_count)
        ],
        "unresolved_imports": [{"raw_name": f"unresolved_{i}"} for i in range(unresolved_count)],
        "identity_health": {
            "by_identity_kind": {"unresolved_import": unresolved_count, "repo_module": entity_count},
            "by_confidence": {"HIGH": entity_count},
            "unresolved_import_count": unresolved_count,
        },
        "structural_metrics": {
            "total_entities": entity_count,
            "total_relations": relation_count,
            "unresolved_count": unresolved_count,
            "layer_violation_count": layer_violation_count,
            "orphan_module_count": orphan_module_count,
            "orphan_modules": [f"ADG::Module::orphan_{i}.py" for i in range(orphan_module_count)],
            "by_relation_type": {"imports": relation_count},
            "by_layer": {"L0": entity_count},
            "module_count": entity_count,
            "symbol_count": 0,
            "external_count": 0,
            "high_fan_in_modules": [],
            "high_fan_out_modules": [],
        },
        "blind_spots": {
            "dynamic_import_count": 0,
            "star_import_count": 0,
            "parse_failure_count": 0,
            "dynamic_import_locations": [],
            "star_import_locations": [],
            "parse_failure_files": [],
        },
    }


class TestSameArtifactNoDiff:
    """Comparing an artifact against itself produces zero regressions."""

    @pytest.mark.unit
    def test_same_artifact_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        assert result.passed is True

    @pytest.mark.unit
    def test_same_artifact_zero_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        assert len(result.regressions) == 0


class TestUnresolvedImportsRegression:
    """R1: increased unresolved imports -> HIGH regression."""

    @pytest.mark.unit
    def test_r1_fires_on_increase(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "baseline.json"
            c = Path(tmpdir) / "current.json"
            _write_artifact(_minimal_artifact(unresolved_count=2), b)
            _write_artifact(_minimal_artifact(unresolved_count=5), c)
            result = run_drift_diff(b, c)
        r1 = [r for r in result.regressions if r.rule == "R1"]
        assert len(r1) == 1
        assert r1[0].severity == "HIGH"

    @pytest.mark.unit
    def test_r1_fails_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(unresolved_count=0), b)
            _write_artifact(_minimal_artifact(unresolved_count=10), c)
            result = run_drift_diff(b, c)
        assert result.passed is False

    @pytest.mark.unit
    def test_r1_no_fire_on_decrease(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(unresolved_count=10), b)
            _write_artifact(_minimal_artifact(unresolved_count=5), c)
            result = run_drift_diff(b, c)
        r1 = [r for r in result.regressions if r.rule == "R1"]
        assert len(r1) == 0


class TestLayerViolationsRegression:
    """R2: increased layer violations -> HIGH regression."""

    @pytest.mark.unit
    def test_r2_fires_on_increase(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(layer_violation_count=5), b)
            _write_artifact(_minimal_artifact(layer_violation_count=10), c)
            result = run_drift_diff(b, c)
        r2 = [r for r in result.regressions if r.rule == "R2"]
        assert len(r2) == 1
        assert r2[0].severity == "HIGH"


class TestOrphanModulesRegression:
    """R3: orphan count increase > tolerance -> MEDIUM regression."""

    @pytest.mark.unit
    def test_r3_fires_above_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=10), c)
            result = run_drift_diff(b, c)
        r3 = [r for r in result.regressions if r.rule == "R3"]
        assert len(r3) == 1
        assert r3[0].severity == "MEDIUM"

    @pytest.mark.unit
    def test_r3_no_fire_within_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=3), c)
            result = run_drift_diff(b, c)
        r3 = [r for r in result.regressions if r.rule == "R3"]
        assert len(r3) == 0


class TestStrictMode:
    """strict=True fails on any regression; strict=False only fails on HIGH."""

    @pytest.mark.unit
    def test_strict_false_medium_only_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=10), c)
            result = run_drift_diff(b, c, strict=False)
        # R3 is MEDIUM, strict=False => should pass
        assert result.passed is True

    @pytest.mark.unit
    def test_strict_true_medium_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(orphan_module_count=0), b)
            _write_artifact(_minimal_artifact(orphan_module_count=10), c)
            result = run_drift_diff(b, c, strict=True)
        assert result.passed is False


class TestImprovementsTracked:
    """Improvements are recorded (not regressions)."""

    @pytest.mark.unit
    def test_decrease_in_unresolved_is_improvement(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            _write_artifact(_minimal_artifact(unresolved_count=10), b)
            _write_artifact(_minimal_artifact(unresolved_count=2), c)
            result = run_drift_diff(b, c)
        improvements = [i for i in result.improvements if i.get("metric") == "unresolved_imports"]
        assert len(improvements) == 1


class TestDriftDiffResultToDict:
    """to_dict has required keys."""

    @pytest.mark.unit
    def test_to_dict_has_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        d = result.to_dict()
        required = {
            "baseline_path",
            "current_path",
            "passed",
            "summary",
            "regressions",
            "improvements",
            "neutral_changes",
        }
        assert required <= set(d.keys())

    @pytest.mark.unit
    def test_summary_nonempty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "art.json"
            _write_artifact(_minimal_artifact(), p)
            result = run_drift_diff(p, p)
        assert len(result.summary) > 0


class TestR4EntityRemoval:
    """R4: >10 entities removed with 0 additions -> MEDIUM regression."""

    @pytest.mark.unit
    def test_r4_fires_on_mass_entity_removal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Path(tmpdir) / "b.json"
            c = Path(tmpdir) / "c.json"
            # baseline has 20 entities, current has 5 (15 removed, 0 added)
            _write_artifact(_minimal_artifact(entity_count=20, relation_count=0), b)
            _write_artifact(_minimal_artifact(entity_count=5, relation_count=0), c)
            result = run_drift_diff(b, c)
        r4 = [r for r in result.regressions if r.rule == "R4"]
        assert len(r4) == 1
        assert r4[0].severity == "MEDIUM"
