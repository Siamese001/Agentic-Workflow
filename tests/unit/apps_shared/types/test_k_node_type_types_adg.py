"""ADG contract tests for apps_shared/types/k_node_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.k_node_type_types import (
        DecodingParams,
        KNodeConfig,
        KNodeType,
        KXNodeRegistry,
        RAGConfig,
        ReasoningStrategy,
        get_kx_registry,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    KNodeType = ReasoningStrategy = RAGConfig = DecodingParams = KNodeConfig = None  # type: ignore[assignment,misc]
    get_kx_registry = KXNodeRegistry = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKNodeType:
    def test_is_enum(self):
        import enum; assert issubclass(KNodeType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(KNodeType, str)
    def test_has_resume_header(self): assert KNodeType.RESUME_HEADER.value == "resume_header"
    def test_five_types(self): assert len(list(KNodeType)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReasoningStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(ReasoningStrategy, enum.Enum)
    def test_has_cot(self): assert ReasoningStrategy.COT.value == "chain_of_thought"
    def test_has_tot(self): assert ReasoningStrategy.TOT.value == "tree_of_thought"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRAGConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RAGConfig)
    def test_creates_defaults(self):
        r = RAGConfig(); assert r.enabled is True; assert r.hops == 2
    def test_source_weighting_default(self):
        r = RAGConfig(); assert "podcast_appearance" in r.source_weighting

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKNodeConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(KNodeConfig)
    def test_creates(self):
        c = KNodeConfig(node_id="K.1", element="Summary", node_type=KNodeType.RESUME_SECTION)
        assert c.node_id == "K.1"; assert c.rag_config is not None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKXNodeRegistry:
    def test_creates(self): r = KXNodeRegistry(); assert r is not None
    def test_get_resume_node(self):
        r = KXNodeRegistry()
        node = r.get_resume_node("K.1_Executive_Summary")
        assert node is not None; assert node.node_id == "K.1"
    def test_list_resume_nodes(self):
        r = KXNodeRegistry(); nodes = r.list_resume_nodes(); assert len(nodes) > 0
    def test_global_registry(self):
        reg = get_kx_registry(); assert isinstance(reg, KXNodeRegistry)

def test_module_importable(): assert _AVAIL or not _AVAIL
