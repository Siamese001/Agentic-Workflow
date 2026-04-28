"""Tests for L5_safety/identity/data_authority_loader.py."""

import pytest

from agentic_core.L5_safety.identity.data_authority_loader import (
    clear_active_data_authority,
    get_active_data_authority_ledger,
    get_active_data_authority_resolution,
    get_active_policy_version,
    set_active_data_authority_ledger,
)
from agentic_core.L5_safety.identity.registries import (
    DataAuthorityResolution,
)


def test_set_and_get_active_data_authority_ledger(sample_data_authority_record):
    """Test setting and retrieving the active data authority ledger."""
    _ = set_active_data_authority_ledger(
        records=(sample_data_authority_record,),
        policy_version="v4.0.0",
    )
    
    retrieved = get_active_data_authority_resolution()
    
    assert retrieved is not None
    assert retrieved.all_match is True
    assert len(retrieved.records) == 1
    assert len(retrieved.drifts) == 0


def test_get_active_data_authority_resolution_returns_bootstrap_when_not_set():
    """Test that get_active_data_authority_resolution returns bootstrap when ledger not set."""
    # Clear any existing ledger
    clear_active_data_authority()
    retrieved = get_active_data_authority_resolution()
    
    assert retrieved is not None
    assert retrieved.all_match is True  # Empty ledger = all match
    assert len(retrieved.records) == 0
    assert len(retrieved.drifts) == 0


def test_get_active_data_authority_ledger_returns_empty_when_bootstrap():
    """Test that get_active_data_authority_ledger returns empty tuple when bootstrap."""
    clear_active_data_authority()
    ledger = get_active_data_authority_ledger()
    
    assert ledger == ()


def test_get_active_data_authority_ledger_returns_records_after_set(sample_data_authority_record):
    """Test that get_active_data_authority_ledger returns records after set."""
    set_active_data_authority_ledger(
        records=(sample_data_authority_record,),
        policy_version="v4.0.0",
    )
    
    ledger = get_active_data_authority_ledger()
    
    assert len(ledger) == 1
    assert ledger[0] is sample_data_authority_record


def test_get_active_policy_version_returns_bootstrap_when_not_set():
    """Test that get_active_policy_version returns bootstrap version when not set."""
    clear_active_data_authority()
    version = get_active_policy_version()
    
    assert version == "v4.0.0-bootstrap"


def test_get_active_policy_version_returns_set_version(sample_data_authority_record):
    """Test that get_active_policy_version returns the set policy version."""
    set_active_data_authority_ledger(
        records=(sample_data_authority_record,),
        policy_version="v4.1.0",
    )
    
    version = get_active_policy_version()
    
    assert version == "v4.1.0"


def test_set_active_data_authority_ledger_detects_drift(
    sample_data_authority_record, sample_drifted_data_authority_record
):
    """Test that set_active_data_authority_ledger detects drift in records."""
    resolution = set_active_data_authority_ledger(
        records=(sample_data_authority_record, sample_drifted_data_authority_record),
        policy_version="v4.0.0",
    )
    
    # One record has drift
    assert resolution.all_match is False
    assert len(resolution.drifts) == 1
    assert resolution.drifts[0] == "test_rag_index"  # drifts is a tuple of source_id strings


def test_set_active_data_authority_ledger_requires_policy_version(sample_data_authority_record):
    """Test that set_active_data_authority_ledger raises ValueError when policy_version is empty."""
    with pytest.raises(ValueError, match="policy_version required"):
        set_active_data_authority_ledger(
            records=(sample_data_authority_record,),
            policy_version="",
        )


def test_clear_active_data_authority_resets_to_bootstrap(sample_data_authority_record):
    """Test that clear_active_data_authority resets to bootstrap state."""
    # First set a ledger
    set_active_data_authority_ledger(
        records=(sample_data_authority_record,),
        policy_version="v4.0.0",
    )
    
    # Verify it's set
    assert len(get_active_data_authority_ledger()) == 1
    assert get_active_policy_version() == "v4.0.0"
    
    # Clear it
    clear_active_data_authority()
    
    # Verify it's back to bootstrap
    assert get_active_data_authority_ledger() == ()
    assert get_active_policy_version() == "v4.0.0-bootstrap"
    
    # Resolution should be bootstrap (empty, all_match=True)
    resolution = get_active_data_authority_resolution()
    assert resolution.all_match is True
    assert len(resolution.records) == 0


def test_set_active_data_authority_ledger_replaces_existing(sample_data_authority_record):
    """Test that set_active_data_authority_ledger replaces existing ledger."""
    # Set initial ledger
    set_active_data_authority_ledger(
        records=(sample_data_authority_record,),
        policy_version="v4.0.0",
    )
    
    assert len(get_active_data_authority_ledger()) == 1
    
    # Replace with different records
    from agentic_core.L5_safety.identity.registries import DataAuthorityRecord, DataSourceKind
    
    new_record = DataAuthorityRecord(
        source_id="new_source",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="new_digest",
        supply_chain_attestation="new_attestation",
        expected_digest="new_digest",
        policy_version="v4.0.0",
    )
    
    set_active_data_authority_ledger(
        records=(new_record,),
        policy_version="v4.1.0",
    )
    
    # Verify replacement
    ledger = get_active_data_authority_ledger()
    assert len(ledger) == 1
    assert ledger[0].source_id == "new_source"
    assert get_active_policy_version() == "v4.1.0"


def test_get_active_data_authority_resolution_is_memoized(sample_data_authority_record):
    """Test that get_active_data_authority_resolution is memoized."""
    clear_active_data_authority()
    
    # First call creates bootstrap
    resolution1 = get_active_data_authority_resolution()
    resolution2 = get_active_data_authority_resolution()
    
    # Should be the same object (memoized)
    assert resolution1 is resolution2
    
    # Set new ledger
    set_active_data_authority_ledger(
        records=(sample_data_authority_record,),
        policy_version="v4.0.0",
    )
    
    # New resolution should be different object
    resolution3 = get_active_data_authority_resolution()
    
    assert resolution3 is not resolution1
    assert resolution3 is not resolution2
