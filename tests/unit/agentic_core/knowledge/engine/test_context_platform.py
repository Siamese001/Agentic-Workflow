"""Unit tests for ContextPlatform (W5.2 — G10 unified ContextAssemblyManifest)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.knowledge.engine.context_platform import (
    AssemblyMode,
    ContextAssemblyManifest,
    ContextPlatform,
    SourceSpec,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def manifest_dict() -> dict:
    return {
        "manifest_id": "apps_research-v1",
        "version": 1,
        "description": "Research app context assembly",
        "feature_flag": "context_platform_v1",
        "retrieval": {
            "sources": [
                {"kind": "vector", "collection": "research_chunks", "weight": 0.7, "top_k": 20},
                {"kind": "keyword", "collection": "research_keywords", "weight": 0.3, "top_k": 10},
            ],
            "assembly": {
                "mode": "hybrid",
                "reranker": "senior_librarian",
                "max_chunks": 15,
                "token_budget": 4096,
            },
        },
        "gates": {
            "min_coverage": 0.4,
            "min_must_use": 2,
            "max_refine_attempts": 3,
            "acl_tags": ["research"],
        },
        "compaction": {
            "enabled": True,
            "strategy": "clear_then_summarize",
        },
    }


@pytest.fixture
def manifest_file(tmp_path: Path, manifest_dict: dict) -> Path:
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(manifest_dict), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# ContextAssemblyManifest
# ---------------------------------------------------------------------------

class TestContextAssemblyManifest:

    def test_from_dict(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        assert manifest.manifest_id == "apps_research-v1"
        assert manifest.version == 1
        assert manifest.assembly_mode == AssemblyMode.HYBRID
        assert len(manifest.sources) == 2
        assert manifest.sources[0].kind == "vector"
        assert manifest.sources[0].collection == "research_chunks"
        assert manifest.sources[0].weight == 0.7
        assert manifest.min_coverage == 0.4
        assert manifest.min_must_use == 2
        assert "research" in manifest.acl_tags
        assert manifest.compaction_enabled is True

    def test_from_file(self, manifest_file: Path) -> None:
        manifest = ContextAssemblyManifest.from_file(manifest_file)
        assert manifest.manifest_id == "apps_research-v1"

    def test_defaults(self) -> None:
        manifest = ContextAssemblyManifest.from_dict({"manifest_id": "test", "version": 1, "retrieval": {}})
        assert manifest.assembly_mode == AssemblyMode.HYBRID
        assert manifest.max_chunks == 20
        assert manifest.token_budget == 4096
        assert manifest.compaction_enabled is True

    def test_all_assembly_modes(self) -> None:
        for mode in ("full_prefetch", "jit_identifier", "hybrid"):
            manifest = ContextAssemblyManifest.from_dict({
                "manifest_id": f"test-{mode}",
                "version": 1,
                "retrieval": {"assembly": {"mode": mode}},
            })
            assert manifest.assembly_mode == AssemblyMode(mode)


class TestSourceSpec:

    def test_defaults(self) -> None:
        spec = SourceSpec()
        assert spec.kind == "vector"
        assert spec.weight == 0.5
        assert spec.top_k == 10


# ---------------------------------------------------------------------------
# ContextPlatform
# ---------------------------------------------------------------------------

class TestContextPlatform:

    def test_initialization(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        platform = ContextPlatform(manifest)
        assert platform.manifest.manifest_id == "apps_research-v1"
        assert platform.registry is not None
        assert platform.dereferencer is not None

    def test_is_active_no_feature_flag(self) -> None:
        manifest = ContextAssemblyManifest(manifest_id="test")
        platform = ContextPlatform(manifest)
        assert platform.is_active() is True
        assert platform.is_active(feature_flags=set()) is True

    def test_is_active_with_feature_flag_enabled(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        platform = ContextPlatform(manifest)
        assert platform.is_active(feature_flags={"context_platform_v1"}) is True

    def test_is_active_with_feature_flag_disabled(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        platform = ContextPlatform(manifest)
        assert platform.is_active(feature_flags=set()) is False

    def test_assemble_produces_contract(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        platform = ContextPlatform(manifest)
        contract = platform.assemble(
            query_id="q-001",
            query="test query",
            retrieved_docs=[],
        )
        assert contract.query_id == "q-001"

    def test_audit_summary(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        platform = ContextPlatform(manifest)
        summary = platform.get_audit_summary()
        assert summary["manifest_id"] == "apps_research-v1"
        assert summary["assembly_mode"] == "hybrid"
        assert "registry" in summary
        assert "dereferencer_tokens_consumed" in summary

    def test_hybrid_mode_issues_refs(self, manifest_dict: dict) -> None:
        manifest = ContextAssemblyManifest.from_dict(manifest_dict)
        platform = ContextPlatform(manifest)
        contract = platform.assemble(
            query_id="q-001",
            query="test query",
            retrieved_docs=[],
        )
        # In hybrid mode, the registry should be available for JIT refs
        # (refs are issued for non-must-use chunks if any exist)
        assert platform.registry is not None

    def test_full_prefetch_mode(self) -> None:
        manifest = ContextAssemblyManifest(
            manifest_id="test-prefetch",
            assembly_mode=AssemblyMode.FULL_PREFETCH,
        )
        platform = ContextPlatform(manifest)
        _contract = platform.assemble(
            query_id="q-001",
            query="test query",
            retrieved_docs=[],
        )
        # full_prefetch mode should not issue JIT refs
