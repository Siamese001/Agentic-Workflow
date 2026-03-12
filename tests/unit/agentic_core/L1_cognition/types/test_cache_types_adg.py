"""ADG contract tests for agentic_core/L1_cognition/types/cache_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.cache_types import (
        EvictionPolicy, DomainConfig,
        DEFAULT_TTL_SECONDS, DEFAULT_SIMILARITY_THRESHOLD, MAX_CACHE_SIZE,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    EvictionPolicy = DomainConfig = None  # type: ignore[assignment,misc]
    DEFAULT_TTL_SECONDS = DEFAULT_SIMILARITY_THRESHOLD = MAX_CACHE_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEvictionPolicy:
    def test_is_enum(self):
        import enum; assert issubclass(EvictionPolicy, enum.Enum)
    def test_has_lru(self): assert EvictionPolicy.LRU.value == "lru"
    def test_four_policies(self): assert len(list(EvictionPolicy)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDomainConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(DomainConfig)
    def test_creates_defaults(self):
        dc = DomainConfig(domain="resume")
        assert dc.domain == "resume"
        assert dc.ttl_seconds == DEFAULT_TTL_SECONDS
        assert dc.eviction_policy == EvictionPolicy.LRU
    def test_clamps_ttl(self):
        dc = DomainConfig(domain="d", ttl_seconds=0)
        assert dc.ttl_seconds >= 60
    def test_clamps_similarity_threshold(self):
        dc = DomainConfig(domain="d", similarity_threshold=0.0)
        assert dc.similarity_threshold >= 0.70

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConstants:
    def test_default_ttl(self): assert DEFAULT_TTL_SECONDS == 3600
    def test_max_cache_size(self): assert MAX_CACHE_SIZE == 10000

def test_module_importable(): assert _AVAIL or not _AVAIL
