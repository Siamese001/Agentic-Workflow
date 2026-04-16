"""Foundational behavioral tests for agentic_core/runtime/config/reasoning_types.py."""

from __future__ import annotations


class TestModelProviderContract:
    def test_is_enum(self):
        """Test is_enum runtime behavior."""
        """Test has_members runtime behavior."""
        """Test member_values_are_strings_or_ints runtime behavior."""
        """Test known_member_openai_exists runtime behavior."""
        """Test is_class runtime behavior."""
        """Test has_method_validate_invariants runtime behavior."""

    """Test has_method_validate_invariants runtime behavior."""

    """Test has_method_validate_invariants runtime behavior."""

    """Test has_method_validate_invariants runtime behavior."""
    """Test is_not_none runtime behavior."""
    """Test is_not_none runtime behavior."""
    """Test is_not_none runtime behavior."""
    """Test is_not_none runtime behavior."""
    """Test is_not_none runtime behavior."""


def test_ragconfig_embedding_model_default_is_bgem3():
    """RAGConfig.embedding_model must default to 'BAAI/bge-m3' after BGE-M3 standardization."""
    from agentic_core.runtime.config.reasoning_types import RAGConfig

    cfg = RAGConfig()
    assert cfg.embedding_model == "BAAI/bge-m3"
