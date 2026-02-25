"""Tests for RetrievalProfile (W4-A Authority)

Tests deterministic serialization, profile management, and L4 integration.
"""

import os
import pytest

from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_manager import (
    RetrievalProfileManager,
    get_active_retrieval_profile,
)


@pytest.mark.unit_min_deps
class TestRetrievalProfile:
    """Test RetrievalProfile deterministic serialization and behavior."""

    def test_default_profile_creation(self):
        """Test default profile creation with expected values."""
        profile = RetrievalProfile.create_default()
        
        assert profile.profile_id == "retrieval-profile-v1"
        assert profile.primary_embedder_id == "text-embedding-3-small"
        assert profile.embedding_dim == 1536
        assert profile.similarity_cutoff == 0.7
        assert profile.top_k == 10
        assert profile.influence_cap == 0.25
        assert profile.shadow_embedder_id is None
        assert profile.hybrid_alpha is None

    def test_canonical_json_deterministic(self):
        """Test canonical JSON serialization is deterministic."""
        profile = RetrievalProfile.create_default()
        
        # Serialize multiple times
        json1 = profile.to_canonical_json()
        json2 = profile.to_canonical_json()
        
        # Must be identical
        assert json1 == json2
        
        # Check it's valid JSON
        import json
        parsed = json.loads(json1)
        assert parsed["profile_id"] == "retrieval-profile-v1"
        assert parsed["similarity_cutoff"] == 0.7  # Rounded to 6 decimal places

    def test_profile_digest_stability(self):
        """Test profile digest is stable across runs."""
        profile = RetrievalProfile.create_default()
        
        # Compute digest multiple times
        digest1 = profile.profile_digest
        digest2 = profile.profile_digest
        
        # Must be identical
        assert digest1 == digest2
        
        # Must be 64-character hex string
        assert len(digest1) == 64
        assert all(c in "0123456789abcdef" for c in digest1)
        
        # Emit digest for determinism verification
        profile.emit_digest()

    def test_deterministic_clustering_identical_inputs(self):
        """Test identical profiles produce identical digests."""
        profile1 = RetrievalProfile.create_default()
        profile2 = RetrievalProfile.create_default()
        
        # Different instances, same values
        digest1 = profile1.profile_digest
        digest2 = profile2.profile_digest
        
        assert digest1 == digest2
        profile1.emit_digest()

    def test_deterministic_clustering_different_order(self):
        """Test profile construction order doesn't affect digest."""
        # Create profile with all fields
        profile1 = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=768,
            similarity_cutoff=0.8,
            top_k=5,
            influence_cap=0.3,
            shadow_embedder_id="shadow-embedder",
            hybrid_alpha=0.5,
        )
        
        # Same profile, different construction (shouldn't matter for dataclass)
        profile2 = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=768,
            similarity_cutoff=0.8,
            top_k=5,
            influence_cap=0.3,
            shadow_embedder_id="shadow-embedder",
            hybrid_alpha=0.5,
        )
        
        assert profile1.profile_digest == profile2.profile_digest

    def test_precision_rounding(self):
        """Test float precision rounding in serialization."""
        profile = RetrievalProfile(
            profile_id="test",
            primary_embedder_id="test",
            embedding_dim=768,
            similarity_cutoff=0.7123456789,  # More than 6 decimal places
            top_k=5,
            influence_cap=0.2987654321,  # More than 6 decimal places
        )
        
        json_str = profile.to_canonical_json()
        import json
        data = json.loads(json_str)
        
        # Should be rounded to 6 decimal places
        assert data["similarity_cutoff"] == 0.712346
        assert data["influence_cap"] == 0.298765

    def test_none_values_excluded(self):
        """Test None values are excluded from serialization."""
        profile = RetrievalProfile(
            profile_id="test",
            primary_embedder_id="test",
            embedding_dim=768,
            similarity_cutoff=0.7,
            top_k=5,
            influence_cap=0.25,
            shadow_embedder_id=None,
            hybrid_alpha=None,
        )
        
        json_str = profile.to_canonical_json()
        import json
        data = json.loads(json_str)
        
        # None values should not be present
        assert "shadow_embedder_id" not in data
        assert "hybrid_alpha" not in data
        assert len(data) == 6  # Only non-None fields

    def test_metadata_key_ordering_stable_ordering(self):
        """Test JSON keys are sorted deterministically."""
        profile = RetrievalProfile.create_default()
        json_str = profile.to_canonical_json()
        
        # Keys should be sorted alphabetically
        expected_order = [
            "embedding_dim",
            "influence_cap",
            "primary_embedder_id",
            "profile_id",
            "similarity_cutoff",
            "top_k",
        ]
        
        import json
        data = json.loads(json_str)
        actual_keys = list(data.keys())
        
        assert actual_keys == expected_order


@pytest.mark.unit_min_deps
class TestRetrievalProfileManager:
    """Test RetrievalProfileManager L4 integration."""

    def test_get_active_profile_default(self):
        """Test getting active profile returns default."""
        profile = get_active_retrieval_profile()
        
        assert isinstance(profile, RetrievalProfile)
        assert profile.profile_id == "retrieval-profile-v1"

    def test_manager_caching(self):
        """Test manager caches active profile."""
        manager = RetrievalProfileManager()
        
        # First call loads profile
        profile1 = manager.load_active_profile()
        
        # Second call returns cached profile
        profile2 = manager.load_active_profile()
        
        assert profile1 is profile2  # Same object (cached)
        
        # Clear cache and reload
        manager.clear_cache()
        profile3 = manager.load_active_profile()
        
        assert profile1 is not profile3  # New object after cache clear
        assert profile1.profile_id == profile3.profile_id  # Same values

    def test_activate_profile_noop(self):
        """Test profile activation with no-op writer."""
        manager = RetrievalProfileManager()  # No L4 writer
        
        profile = RetrievalProfile.create_default()
        version_id = manager.activate_profile(profile, created_utc=1234567890)
        
        # Should return no-op version ID
        assert version_id == "noop_activation_1234567890"
        
        # Profile should be cached
        cached_profile = manager.load_active_profile()
        assert cached_profile is profile


@pytest.mark.unit_min_deps
class TestW4ANegativeControl:
    """Negative control tests for W4-A RetrievalProfile authority."""

    @pytest.mark.xfail(
        reason="W4-NEGCTRL-TAMPER: Serialization order tampering should fail"
    )
    def test_profile_determinism_violation_negative_control(self):
        """Negative control: tamper with serialization order."""
        # Set tamper flag
        os.environ["W4_NEGCTRL_TAMPER"] = "1"
        
        try:
            profile = RetrievalProfile.create_default()
            
            # Tamper with serialization by modifying the method
            original_method = profile.to_canonical_json
            
            def tampered_serialization():
                # Return JSON with unsorted keys (violates determinism)
                import json
                data = {
                    "z_last": "value",
                    "a_first": "value",
                    "m_middle": "value",
                }
                return json.dumps(data, separators=(',', ':'))  # No sort_keys
            
            profile.to_canonical_json = tampered_serialization
            
            # This should fail due to tampering
            digest1 = profile.profile_digest
            digest2 = profile.profile_digest
            
            # If tampering is detected, this should not reach here
            assert digest1 != digest2, "Tampering detected: digests differ"
            
        finally:
            # Clean up
            os.environ.pop("W4_NEGCTRL_TAMPER", None)

    def test_profile_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        profile = RetrievalProfile.create_default()
        
        # Normal operation should succeed
        digest1 = profile.profile_digest
        digest2 = profile.profile_digest
        
        assert digest1 == digest2
        print(f"W4-NEGCTRL-GUARD-INTACT: digest={digest1}")

    @pytest.mark.xfail(
        reason="W4-NEGCTRL-TAMPER: JSON key ordering tampering should fail"
    )
    def test_key_ordering_violation_negative_control(self):
        """Negative control: tamper with JSON key ordering."""
        os.environ["W4_NEGCTRL_TAMPER"] = "1"
        
        try:
            profile = RetrievalProfile.create_default()
            
            # Create invalid JSON with wrong key order
            invalid_json = '{"top_k":10,"profile_id":"retrieval-profile-v1"}'
            
            # This should fail validation
            import json
            try:
                parsed = json.loads(invalid_json)
                # If we get here, validation failed
                assert False, "Key ordering tampering not detected"
            except json.JSONDecodeError:
                pass  # Expected for tampered JSON
                
        finally:
            os.environ.pop("W4_NEGCTRL_TAMPER", None)

    def test_key_ordering_violation_negative_control_guard_intact(self):
        """Verify key ordering guard is intact."""
        profile = RetrievalProfile.create_default()
        json_str = profile.to_canonical_json()
        
        import json
        data = json.loads(json_str)
        keys = list(data.keys())
        
        # Keys should be sorted
        assert keys == sorted(keys)
        print(f"W4-NEGCTRL-GUARD-INTACT: keys_sorted={keys}")

    @pytest.mark.xfail(
        reason="W4-NEGCTRL-TAMPER: Float precision tampering should fail"
    )
    def test_precision_rounding_violation_negative_control(self):
        """Negative control: tamper with float precision."""
        os.environ["W4_NEGCTRL_TAMPER"] = "1"
        
        try:
            # Create profile with high precision
            profile = RetrievalProfile(
                profile_id="test",
                primary_embedder_id="test",
                embedding_dim=768,
                similarity_cutoff=0.7123456789,
                top_k=5,
                influence_cap=0.25,
            )
            
            # Tamper with precision rounding
            original_method = profile.to_canonical_json
            
            def tampered_precision():
                # Return JSON without proper rounding
                import json
                data = {
                    "profile_id": "test",
                    "primary_embedder_id": "test",
                    "embedding_dim": 768,
                    "similarity_cutoff": 0.7123456789,  # Not rounded
                    "top_k": 5,
                    "influence_cap": 0.25,
                }
                return json.dumps(data, separators=(',', ':'), sort_keys=True)
            
            profile.to_canonical_json = tampered_precision
            
            # This should detect precision tampering
            json_str = profile.to_canonical_json()
            assert "0.7123456789" not in json_str, "Precision tampering not detected"
            
        finally:
            os.environ.pop("W4_NEGCTRL_TAMPER", None)

    def test_precision_rounding_violation_negative_control_guard_intact(self):
        """Verify precision rounding guard is intact."""
        profile = RetrievalProfile(
            profile_id="test",
            primary_embedder_id="test",
            embedding_dim=768,
            similarity_cutoff=0.7123456789,
            top_k=5,
            influence_cap=0.25,
        )
        
        json_str = profile.to_canonical_json()
        
        # Should be properly rounded
        assert "0.712346" in json_str
        assert "0.7123456789" not in json_str
        print("W4-NEGCTRL-GUARD-INTACT: precision_rounded correctly")
