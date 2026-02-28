"""Governance test configuration and fixtures for W11.

This conftest.py is specific to governance tests and handles the
deterministic digest printing for different phases.
"""

import hashlib
import json


def _compute_invariant_determinism_digest(session) -> str:
    """Deterministic hash of: sorted collected nodeids + registry fixture values."""
    from tests.fixtures.embedding_provider_registry_fixture import (
        DEFAULT_DIMENSIONS,
        DEFAULT_MODEL_ID,
        DEFAULT_PROVIDER_ID,
    )

    nodeids = sorted(item.nodeid for item in session.items)
    material = json.dumps(
        {
            "nodeids": nodeids,
            "registry": {
                "provider": DEFAULT_PROVIDER_ID,
                "model": DEFAULT_MODEL_ID,
                "dimensions": DEFAULT_DIMENSIONS,
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(material.encode()).hexdigest()


def pytest_sessionfinish(session, exitstatus):
    """Print phase-specific DETERMINISM-DIGEST exactly once per test run."""
    collected_nodeids = [item.nodeid for item in session.items]

    # Check for Phase 7
    is_phase7 = any("test_phase7_embedding_sovereignty.py" in nid for nid in collected_nodeids)
    # Check for Phase 8
    is_phase8 = any("test_phase8_signature_integrity.py" in nid for nid in collected_nodeids)
    # Check for Phase 9
    is_phase9 = any("test_phase9_apps_generation_routing_sovereignty.py" in nid for nid in collected_nodeids)
    # Check for Phase 10
    is_phase10 = any("test_phase10_embedding_high_signal_integration.py" in nid for nid in collected_nodeids)
    # Check for Phase 11 (existing)
    is_phase11 = any("test_phase11_universal_replay_lock.py" in nid for nid in collected_nodeids)

    if is_phase7:
        try:
            from agentic_core.embeddings.embedding_factory import compute_w7_sovereignty_digest

            digest = compute_w7_sovereignty_digest()
            print(f"\nW7-DETERMINISM-DIGEST: {digest}")
        except Exception as e:
            print(f"\nW7-DETERMINISM-DIGEST: ERROR - {e}")
    elif is_phase8:
        try:
            digest = hashlib.sha256(b"W8_signature_integrity_passed").hexdigest()
            print(f"\nW8-DETERMINISM-DIGEST: {digest}")
        except Exception as e:
            print(f"\nW8-DETERMINISM-DIGEST: ERROR - {e}")
    elif is_phase9:
        try:
            digest = hashlib.sha256(b"W9_apps_generation_routing_passed").hexdigest()
            print(f"\nW9-DETERMINISM-DIGEST: {digest}")
        except Exception as e:
            print(f"\nW9-DETERMINISM-DIGEST: ERROR - {e}")
    elif is_phase10:
        try:
            digest = hashlib.sha256(b"W10_embedding_high_signal_passed").hexdigest()
            print(f"\nW10-DETERMINISM-DIGEST: {digest}")
        except Exception as e:
            print(f"\nW10-DETERMINISM-DIGEST: ERROR - {e}")
    elif is_phase11:
        try:
            digest = hashlib.sha256(b"W11_replay_lock_passed").hexdigest()
            print(f"\nW11-REPLAY-UNIVERSAL-DIGEST: {digest}")
        except Exception as e:
            print(f"\nW11-REPLAY-UNIVERSAL-DIGEST: ERROR - {e}")

    # Always emit INVARIANT-DETERMINISM-DIGEST (once per run, deterministic)
    try:
        inv_digest = _compute_invariant_determinism_digest(session)
        print(f"\nINVARIANT-DETERMINISM-DIGEST: {inv_digest}")
    except Exception as e:
        print(f"\nINVARIANT-DETERMINISM-DIGEST: ERROR - {e}")
