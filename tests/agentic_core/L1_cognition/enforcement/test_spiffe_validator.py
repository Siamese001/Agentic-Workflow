"""Tests for SpiffeValidator - SPIFFE identity validation."""
import pytest
from agentic_core.L1_cognition.enforcement.spiffe_validator import SpiffeValidator


class TestSpiffeValidator:
    def test_init(self):
        v = SpiffeValidator(trust_domain="example.org")
        assert v.trust_domain == "example.org"

    def test_validate_spiffe_id(self):
        v = SpiffeValidator(trust_domain="example.org")
        assert v.validate("spiffe://example.org/agent/a1") is True

    def test_invalid_trust_domain(self):
        v = SpiffeValidator(trust_domain="example.org")
        assert v.validate("spiffe://other.org/agent/a1") is False

    def test_invalid_format(self):
        v = SpiffeValidator(trust_domain="example.org")
        assert v.validate("not-a-spiffe-id") is False

    def test_extract_path(self):
        v = SpiffeValidator(trust_domain="example.org")
        path = v.extract_path("spiffe://example.org/agent/a1")
        assert path == "/agent/a1"

    def test_match_pattern(self):
        v = SpiffeValidator(trust_domain="example.org")
        assert v.match_pattern("spiffe://example.org/agent/a1", "/agent/*") is True

    def test_pattern_no_match(self):
        v = SpiffeValidator(trust_domain="example.org")
        assert v.match_pattern("spiffe://example.org/service/s1", "/agent/*") is False
