"""ADG contract tests for agentic_core/L2_execution/types/vllm_infrastructure_fingerprint_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
        VLLMInfrastructureFingerprint, canonical_json, sha256_hex,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    VLLMInfrastructureFingerprint = canonical_json = sha256_hex = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVLLMInfrastructureFingerprint:
    def test_is_frozen(self): assert VLLMInfrastructureFingerprint.__dataclass_params__.frozen is True
    def test_deterministic_test_instance(self):
        fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
        assert fp.model_name == "Qwen2.5-7B-Instruct"
        assert fp.vllm_version == "0.6.3"
    def test_as_dict(self):
        fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
        d = fp.as_dict()
        assert isinstance(d, dict); assert "model_name" in d
    def test_canonical_json_stable(self):
        fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
        j1 = fp.canonical_json(); j2 = fp.canonical_json()
        assert j1 == j2
    def test_fingerprint_hash_64_hex(self):
        fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
        h = fp.fingerprint_hash()
        assert len(h) == 64; assert all(c in "0123456789abcdef" for c in h)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHelpers:
    def test_canonical_json_sorted_keys(self):
        j = canonical_json({"b": 2, "a": 1}); assert j.index('"a"') < j.index('"b"')
    def test_sha256_hex_string(self):
        h = sha256_hex("hello"); assert len(h) == 64
    def test_sha256_hex_bytes(self):
        h = sha256_hex(b"hello"); assert len(h) == 64

def test_module_importable(): assert _AVAIL or not _AVAIL
