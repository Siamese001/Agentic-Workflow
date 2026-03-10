"""
PHASE 4 WAVE 2 tests — VLLMInfrastructureFingerprint unit tests.

Tests deterministic serialization, hashing, and field change detection.
No GPU imports. Pure L2.
"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import (
    VLLMInfrastructureFingerprint,
    canonical_json,
    sha256_hex,
)


def test_fingerprint_canonical_serialization_stable():
    """Canonical JSON serialization is stable across calls."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    json1 = fp.canonical_json()
    json2 = fp.canonical_json()
    assert json1 == json2
    # Verify no whitespace and sorted keys
    assert " " not in json1
    assert "\n" not in json1
    # Keys should be in alphabetical order
    keys = list(json.loads(json1).keys())
    assert keys == sorted(keys)


def test_fingerprint_hash_changes_on_field_change():
    """Fingerprint hash changes when any field changes."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    original_hash = fp.fingerprint_hash()

    # Change each field and verify hash changes
    fields_to_change = {
        "model_name": "DifferentModel",
        "model_revision_sha": "def456abc123",
        "vllm_version": "0.6.4",
        "transformers_version": "4.46.1",
        "torch_version": "2.5.2",
        "cuda_version": "12.5",
        "driver_version": "550.54.15",
    }

    for field, new_value in fields_to_change.items():
        kwargs = fp.as_dict()
        kwargs[field] = new_value
        modified_fp = VLLMInfrastructureFingerprint(**kwargs)
        modified_hash = modified_fp.fingerprint_hash()
        assert modified_hash != original_hash
        assert len(modified_hash) == 64  # SHA256 hex length


def test_fingerprint_deterministic_test_instance():
    """Deterministic test instance always produces same values."""
    fp1 = VLLMInfrastructureFingerprint.deterministic_test_instance()
    fp2 = VLLMInfrastructureFingerprint.deterministic_test_instance()
    assert fp1 == fp2
    assert fp1.fingerprint_hash() == fp2.fingerprint_hash()
    assert fp1.model_name == "Qwen2.5-7B-Instruct"


def test_canonical_json_stable_keys():
    """canonical_json produces stable key ordering."""
    data = {"z": 1, "a": 2, "m": 3}
    json1 = canonical_json(data)
    json2 = canonical_json(data)
    assert json1 == json2
    assert json1 == '{"a":2,"m":3,"z":1}'


def test_sha256_hex_consistent():
    """sha256_hex produces consistent hashes."""
    data = "test string"
    hash1 = sha256_hex(data)
    hash2 = sha256_hex(data)
    assert hash1 == hash2
    assert len(hash1) == 64
    # Verify against known SHA256 of "test string"
    expected = "d5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b"
    assert hash1 == expected


def test_fingerprint_as_dict_roundtrip():
    """as_dict() produces values that can reconstruct fingerprint."""
    fp = VLLMInfrastructureFingerprint.deterministic_test_instance()
    data = fp.as_dict()
    fp2 = VLLMInfrastructureFingerprint(**data)
    assert fp == fp2
    assert fp.fingerprint_hash() == fp2.fingerprint_hash()
