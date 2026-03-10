"""Unit tests for ADG Artifact Builder and Serializer (Phase 2).

Tests cover:
- ADGArtifactBuilder produces valid ADGArtifact from a minimal ScanResult
- Entities and relations are populated correctly
- Structural metrics are computed
- Blind spots are collected
- Digest is deterministic (same ScanResult -> same digest on two calls)
- Serializer round-trips correctly
- diff_artifacts produces expected delta structure
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agentic_core.adg.artifact.builder import (
    ADGArtifact,
    ADGArtifactBuilder,
    build_artifact,
)
from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_minimal_scan_result() -> ScanResult:
    """Build a deterministic minimal ScanResult for testing."""
    result = ScanResult(commit_sha="test-sha")
    result.modules = [
        "agentic_core/adg/schema.py",
        "agentic_core/adg/cli.py",
    ]
    result.edges = [
        Edge(
            from_name="ADG::Module::agentic_core/adg/cli.py",
            relation_type="imports",
            to_name="ADG::Module::agentic_core/adg/schema.py",
            edge_kind="import",
            source_file="agentic_core/adg/cli.py",
            line_no=5,
            symbol="schema",
        ),
        Edge(
            from_name="ADG::Module::agentic_core/adg/cli.py",
            relation_type="imports",
            to_name="ADG::Symbol::openai",
            edge_kind="import",
            source_file="agentic_core/adg/cli.py",
            line_no=10,
            symbol="openai",
        ),
    ]
    result.compute_digest()
    return result


class TestADGArtifactBuilderBasic:
    """Basic build contract tests."""

    @pytest.mark.unit
    def test_build_returns_adg_artifact(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert isinstance(artifact, ADGArtifact)

    @pytest.mark.unit
    def test_commit_sha_propagated(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.commit_sha == "test-sha"

    @pytest.mark.unit
    def test_entities_nonempty(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert len(artifact.entities) > 0

    @pytest.mark.unit
    def test_relations_nonempty(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert len(artifact.relations) > 0

    @pytest.mark.unit
    def test_artifact_digest_is_64_hex(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert len(artifact.artifact_digest) == 64
        assert all(c in "0123456789abcdef" for c in artifact.artifact_digest)

    @pytest.mark.unit
    def test_schema_version_is_v3(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.schema_version == "3.0.0"


class TestEntityPopulation:
    """Module and symbol entities are populated correctly."""

    @pytest.mark.unit
    def test_source_modules_create_module_entities(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        entity_adg_names = {e.adg_name for e in artifact.entities}
        assert "ADG::Module::agentic_core/adg/schema.py" in entity_adg_names
        assert "ADG::Module::agentic_core/adg/cli.py" in entity_adg_names

    @pytest.mark.unit
    def test_module_entity_has_layer(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        schema_entity = next(
            e for e in artifact.entities
            if e.adg_name == "ADG::Module::agentic_core/adg/schema.py"
        )
        assert schema_entity.layer != ""
        assert schema_entity.layer != "L_UNKNOWN"

    @pytest.mark.unit
    def test_external_symbol_classified_correctly(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        openai_entity = next(
            (e for e in artifact.entities if "openai" in e.adg_name),
            None,
        )
        assert openai_entity is not None
        assert openai_entity.identity_kind == "external_module"

    @pytest.mark.unit
    def test_no_duplicate_entities(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        adg_names = [e.adg_name for e in artifact.entities]
        assert len(adg_names) == len(set(adg_names)), "Duplicate entities found"


class TestIdentityHealth:
    """Identity health section is populated with correct keys."""

    @pytest.mark.unit
    def test_identity_health_has_required_keys(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        required = {"by_identity_kind", "by_confidence", "unresolved_import_count"}
        assert required <= set(artifact.identity_health.keys())

    @pytest.mark.unit
    def test_null_node_inflation_eliminated_flag(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.identity_health.get("null_node_inflation_eliminated") is True


class TestStructuralMetrics:
    """Structural metrics are computed deterministically."""

    @pytest.mark.unit
    def test_total_entities_matches_entity_list(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.structural_metrics.total_entities == len(artifact.entities)

    @pytest.mark.unit
    def test_total_relations_matches_relation_list(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        assert artifact.structural_metrics.total_relations == len(artifact.relations)

    @pytest.mark.unit
    def test_by_relation_type_sums_to_total(self) -> None:
        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        total = sum(artifact.structural_metrics.by_relation_type.values())
        assert total == artifact.structural_metrics.total_relations


class TestDeterminism:
    """Same ScanResult always produces same artifact_digest."""

    @pytest.mark.unit
    def test_digest_stable_across_two_builds(self) -> None:
        result = _make_minimal_scan_result()
        a1 = build_artifact(result, repo_root=_REPO_ROOT)
        a2 = build_artifact(result, repo_root=_REPO_ROOT)
        assert a1.artifact_digest == a2.artifact_digest

    @pytest.mark.unit
    def test_different_commit_sha_same_content_same_digest(self) -> None:
        """artifact_digest covers content, not commit_sha."""
        r1 = ScanResult(commit_sha="sha1")
        r1.modules = ["agentic_core/adg/schema.py"]
        r1.edges = []
        r1.compute_digest()

        r2 = ScanResult(commit_sha="sha2")
        r2.modules = ["agentic_core/adg/schema.py"]
        r2.edges = []
        r2.compute_digest()

        a1 = build_artifact(r1, repo_root=_REPO_ROOT)
        a2 = build_artifact(r2, repo_root=_REPO_ROOT)
        # Content is identical so digests should match
        assert a1.artifact_digest == a2.artifact_digest

    @pytest.mark.unit
    def test_added_edge_changes_digest(self) -> None:
        r1 = ScanResult(commit_sha="t")
        r1.modules = ["agentic_core/adg/schema.py"]
        r1.edges = []
        r1.compute_digest()

        r2 = ScanResult(commit_sha="t")
        r2.modules = ["agentic_core/adg/schema.py"]
        r2.edges = [
            Edge(
                "ADG::Module::agentic_core/adg/schema.py",
                "imports",
                "ADG::Symbol::json",
                "import",
                "agentic_core/adg/schema.py",
                1,
            )
        ]
        r2.compute_digest()

        a1 = build_artifact(r1, repo_root=_REPO_ROOT)
        a2 = build_artifact(r2, repo_root=_REPO_ROOT)
        assert a1.artifact_digest != a2.artifact_digest


class TestSerializer:
    """Serializer produces valid JSON and round-trips."""

    @pytest.mark.unit
    def test_serialize_produces_valid_json(self) -> None:
        from agentic_core.adg.artifact.serializer import serialize_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        json_str = serialize_artifact(artifact)
        parsed = json.loads(json_str)
        assert "schema_version" in parsed
        assert "artifact_digest" in parsed

    @pytest.mark.unit
    def test_serialize_is_deterministic(self) -> None:
        from agentic_core.adg.artifact.serializer import serialize_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)
        s1 = serialize_artifact(artifact)
        s2 = serialize_artifact(artifact)
        assert s1 == s2

    @pytest.mark.unit
    def test_write_and_load_roundtrip(self) -> None:
        from agentic_core.adg.artifact.serializer import load_artifact, write_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "artifact.json"
            write_artifact(artifact, out_path)
            loaded = load_artifact(out_path)

        assert loaded["schema_version"] == "3.0.0"
        assert loaded["artifact_digest"] == artifact.artifact_digest

    @pytest.mark.unit
    def test_diff_artifacts_returns_expected_keys(self) -> None:
        from agentic_core.adg.artifact.serializer import diff_artifacts, write_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)

        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "a1.json"
            p2 = Path(tmpdir) / "a2.json"
            write_artifact(artifact, p1)
            write_artifact(artifact, p2)
            diff = diff_artifacts(p1, p2)

        required_keys = {
            "digest_changed", "entities", "relations",
            "unresolved_imports", "layer_violations", "orphan_modules",
        }
        assert required_keys <= set(diff.keys())

    @pytest.mark.unit
    def test_diff_same_artifact_no_changes(self) -> None:
        from agentic_core.adg.artifact.serializer import diff_artifacts, write_artifact

        result = _make_minimal_scan_result()
        artifact = build_artifact(result, repo_root=_REPO_ROOT)

        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "a1.json"
            p2 = Path(tmpdir) / "a2.json"
            write_artifact(artifact, p1)
            write_artifact(artifact, p2)
            diff = diff_artifacts(p1, p2)

        assert diff["digest_changed"] is False
        assert diff["entities"]["added_count"] == 0
        assert diff["entities"]["removed_count"] == 0

    @pytest.mark.unit
    def test_set_diff_is_callable_as_module_function(self) -> None:
        """Regression: _set_diff must NOT have @staticmethod decorator at module level.

        If wrapped in staticmethod(), calling _set_diff([],[]) would raise
        TypeError: 'staticmethod' object is not callable.
        """
        from agentic_core.adg.artifact.serializer import _set_diff

        added, removed = _set_diff(["a", "b"], ["b", "c"])
        assert added == ["c"]
        assert removed == ["a"]

    @pytest.mark.unit
    def test_set_diff_returns_correct_added_and_removed(self) -> None:
        from agentic_core.adg.artifact.serializer import _set_diff

        added, removed = _set_diff(["x", "y", "z"], ["y", "z", "w"])
        assert added == ["w"]
        assert removed == ["x"]
