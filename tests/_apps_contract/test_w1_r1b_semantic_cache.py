"""Tests for apps_rg R1B semantic cache (W1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.types.intent_payload import ResumeGenerationIntent
from apps_rg.utils.intent_builder import build_intent_from_request, derive_intent_hash


class TestIntentBuilder:
    """Test intent payload normalization."""

    def test_build_intent_normalizes_company_name(self, tmp_path: Path):
        """Company names are lowercased and stripped."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="  TechCorp  ",
            target_role="Engineer",
        )

        assert intent.target_company == "techcorp"

    def test_build_intent_normalizes_role_name(self, tmp_path: Path):
        """Role names are lowercased and stripped."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="  Senior Engineer  ",
        )

        assert intent.target_role == "senior engineer"

    def test_build_intent_normalizes_level_variations(self, tmp_path: Path):
        """Level variations normalized to canonical form."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        # Test "sr" → "senior"
        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
            target_level="sr",
        )
        assert intent.target_level == "senior"
        assert intent.role_seniority == "senior"

    def test_build_intent_normalizes_junior_variations(self, tmp_path: Path):
        """Junior level variations normalized."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        for variation in ["jr", "jnr", "junior"]:
            intent = build_intent_from_request(
                candidate_profile_path=profile,
                target_company="Acme",
                target_role="Engineer",
                target_level=variation,
            )
            assert intent.target_level == "junior", f"Failed for {variation}"

    def test_build_intent_sorts_tech_stack(self, tmp_path: Path):
        """Tech stack is sorted and deduplicated."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("skills: [Python, ML, Python, Rust]\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
        )

        # Should be sorted and deduplicated
        assert intent.role_tech_stack == ("ml", "python", "rust")

    def test_build_intent_stable_hash(self, tmp_path: Path):
        """Same inputs produce same intent hash."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("consistent content\n")

        intent1 = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
        )
        intent2 = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
        )

        assert intent1.source_resume_hash == intent2.source_resume_hash

    def test_build_intent_generates_request_id(self, tmp_path: Path):
        """Request ID is generated if not provided."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
        )

        assert intent.request_id is not None
        assert len(intent.request_id) > 0

    def test_build_intent_uses_provided_request_id(self, tmp_path: Path):
        """Provided request ID is used."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
            request_id="custom_req_123",
        )

        assert intent.request_id == "custom_req_123"

    def test_build_intent_derives_tech_industry(self, tmp_path: Path):
        """Tech companies get technology industry."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="AI Tech Corp",
            target_role="Engineer",
        )

        assert intent.target_industry == "technology"

    def test_build_intent_default_tenant(self, tmp_path: Path):
        """Default tenant is 'default'."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
        )

        assert intent.tenant_id == "default"

    def test_build_intent_custom_tenant(self, tmp_path: Path):
        """Custom tenant is used when provided."""
        profile = tmp_path / "profile.yaml"
        profile.write_text("name: Candidate\n")

        intent = build_intent_from_request(
            candidate_profile_path=profile,
            target_company="Acme",
            target_role="Engineer",
            tenant_id="enterprise_123",
        )

        assert intent.tenant_id == "enterprise_123"


class TestIntentHash:
    """Test intent hash derivation."""

    def test_derive_intent_hash_consistent(self):
        """Same intent produces same hash."""
        intent = ResumeGenerationIntent(
            source_resume_hash="abc123",
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python", "ml"),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        hash1 = derive_intent_hash(intent)
        hash2 = derive_intent_hash(intent)

        assert hash1 == hash2

    def test_derive_intent_hash_different_intents(self):
        """Different intents produce different hashes."""
        intent1 = ResumeGenerationIntent(
            source_resume_hash="abc123",
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python", "ml"),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        intent2 = ResumeGenerationIntent(
            source_resume_hash="def456",  # Different!
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python", "ml"),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        hash1 = derive_intent_hash(intent1)
        hash2 = derive_intent_hash(intent2)

        assert hash1 != hash2


class TestIntentPayload:
    """Test ResumeGenerationIntent dataclass."""

    def test_to_embedding_text_format(self):
        """Embedding text has expected format."""
        intent = ResumeGenerationIntent(
            source_resume_hash="abc123",
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python", "ml"),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        text = intent.to_embedding_text()

        assert "acme" in text.lower()
        assert "engineer" in text.lower()
        assert "cand1" in text

    def test_to_cache_key_dict(self):
        """Cache key dict has expected structure."""
        intent = ResumeGenerationIntent(
            source_resume_hash="abc123",
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python", "ml"),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        key_dict = intent.to_cache_key_dict()

        assert key_dict["source_resume_hash"] == "abc123"
        assert key_dict["target_company"] == "acme"
        assert key_dict["target_role"] == "engineer"
        assert "tenant_id" in key_dict

    def test_frozen_dataclass(self):
        """Intent is immutable."""
        intent = ResumeGenerationIntent(
            source_resume_hash="abc123",
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python",),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        with pytest.raises(AttributeError):
            intent.target_company = "other"


class TestR1BCacheAdapter:
    """Test R1B cache adapter (requires SemanticCacheManager)."""

    def test_adapter_initialization(self):
        """Adapter can be initialized."""
        from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter

        adapter = AppsRgR1BCacheAdapter(tenant_id="test")
        assert adapter.tenant_id == "test"

    def test_namespace_constant(self):
        """Namespace constant is correct."""
        from apps_rg.cache.r1b_adapter import APPS_RG_CACHE_NAMESPACE

        assert APPS_RG_CACHE_NAMESPACE == "apps_rg.resume_generation"

    def test_check_r1b_for_apps_rg_function_exists(self):
        """High-level check function exists."""
        from apps_rg.cache.r1b_adapter import check_r1b_for_apps_rg

        assert callable(check_r1b_for_apps_rg)


class TestIntentToEmbedding:
    """Test intent to embedding text conversion."""

    def test_embedding_text_includes_all_fields(self):
        """Embedding text captures all semantic fields."""
        intent = ResumeGenerationIntent(
            source_resume_hash="hash123",
            candidate_identifier="cand_abc",
            target_company="TechGiant",
            target_role="Senior ML Engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python", "tensorflow", "aws"),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req_xyz",
            tenant_id="default",
        )

        text = intent.to_embedding_text()

        # Check key components are present
        assert "Senior ML Engineer" in text
        assert "TechGiant" in text
        assert "cand_abc" in text
        assert "formal" in text

    def test_embedding_text_consistency(self):
        """Same intent produces same embedding text."""
        intent = ResumeGenerationIntent(
            source_resume_hash="hash123",
            candidate_identifier="cand1",
            target_company="acme",
            target_role="engineer",
            target_level="senior",
            target_function="engineering",
            target_industry="technology",
            role_seniority="senior",
            role_tech_stack=("python",),
            output_target="markdown",
            max_pages=2,
            tone_profile="formal",
            request_id="req1",
            tenant_id="default",
        )

        text1 = intent.to_embedding_text()
        text2 = intent.to_embedding_text()

        assert text1 == text2
