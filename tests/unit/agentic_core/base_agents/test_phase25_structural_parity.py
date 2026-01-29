"""
tests/test_phase25_structural_parity.py

[PHASE 25] L0-L6 Structural Parity Edge Case Test Suite
BLOCKING RELEASE CRITERIA: 100% pass rate required for deployment.
"""

import pytest
import asyncio
import time
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps_rg"))
sys.path.insert(0, str(project_root / "apps_lic"))

# Mock the sovereign lock to bypass integrity checks
with patch(
    "agentic_core.domain.sovereign_lock.CoreIntegrityVerifier.verify_core_integrity",
    return_value=True,
):
    with patch("agentic_core.domain.sovereign_lock.emergency_shutdown", MagicMock()):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent as RGAgentBase
        from apps_lic.shared.core.agent_base import LICAgentBase

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_pinecone_response_rg():
    """Returns a match score of 0.88 (Pass for RG, Fail for LIC)"""
    return {"matches": [{"id": "doc_1", "score": 0.88, "metadata": {"text": "synonym"}}]}


# =============================================================================
# TEST 1: THE DRIFT (Refined)
# =============================================================================


@pytest.mark.asyncio
async def test_semantic_drift_threshold_enforcement(mock_pinecone_response_rg):
    """
    [CRITICAL] Validates that apps_lic (0.92) is stricter than apps_rg (0.85).
    Scenario: A vector match with score 0.88.
    - RG (0.85) -> Should RETURN result (Hit)
    - LIC (0.92) -> Should FILTER result (Miss)
    """
    mock_client = AsyncMock()
    mock_client.query.return_value = mock_pinecone_response_rg

    # Mock the cache metrics to avoid AttributeError
    mock_metrics = MagicMock()
    mock_metrics.record = MagicMock()
    mock_metrics.record_error = MagicMock()

    # We patch the property on the Mixin to force our mock client
    # This bypasses the lazy loading logic in the agent base
    with (
        patch.object(PineconeVectorMixin, "pinecone", mock_client),
        patch(
            "agentic_core.base_agents.pinecone_vector_mixin.get_cache_metrics",
            return_value=mock_metrics,
        ),
    ):
        # --- RG TEST (Threshold 0.85) ---
        rg_agent = RGAgentBase()
        # Force injection of mock to avoid internal connection logic
        rg_agent._pinecone_client = mock_client

        print(f"\n[DEBUG] RG Threshold: {rg_agent._similarity_threshold}")
        assert rg_agent._similarity_threshold == 0.85, "RG Threshold Configuration Drift!"

        rg_results = await rg_agent.vector_search(
            embedding=[0.1] * 1536, apply_similarity_threshold=True, use_cache=False
        )

        assert len(rg_results) == 1, (
            f"RG Agent (0.85) rejected score 0.88! Found {len(rg_results)} results."
        )

        # --- LIC TEST (Threshold 0.92) ---
        lic_agent = LICAgentBase()
        # Force injection of mock
        lic_agent._pinecone_client = mock_client

        print(f"[DEBUG] LIC Threshold: {lic_agent._similarity_threshold}")
        assert lic_agent._similarity_threshold == 0.92, "LIC Threshold Configuration Drift!"

        lic_results = await lic_agent.vector_search(
            embedding=[0.1] * 1536, apply_similarity_threshold=True, use_cache=False
        )

        assert len(lic_results) == 0, (
            f"LIC Agent (0.92) incorrectly accepted score 0.88! Found {len(lic_results)} results. "
            "Memory Drift detected."
        )


@pytest.mark.asyncio
async def test_async_meta_learning_latency():
    """
    [PERFORMANCE] Ensures main thread is not blocked by Pinecone writes.
    """

    async def slow_write(*args, **kwargs):
        await asyncio.sleep(0.3)  # 300ms latency (above 200ms threshold)
        return True

    # Patch the internal async implementation
    with patch(
        "agentic_core.base_agents.meta_learning_mixin.MetaLearningMixin._async_learn_experience",
        side_effect=slow_write,
    ) as mock_bg:
        agent = RGAgentBase()
        # Manually un-lobotomize for test
        agent._lobotomized = False
        agent._memory = MagicMock()  # Prevent direct memory access error

        start = time.time()
        # This triggers the fire-and-forget task
        await agent.learn_experience("ctx", {"res": 1})
        duration = (time.time() - start) * 1000

        print(f"\n[DEBUG] Async Dispatch Duration: {duration:.2f}ms")

        assert duration < 50, f"Main thread blocked for {duration}ms! Must be < 50ms for dispatch."

        # Verify the background task was actually scheduled (give it time to start)
        await asyncio.sleep(0.01)
        # Note: We don't await completion, we just verify dispatch speed.


# =============================================================================
# TEST 3: NAMESPACE ISOLATION
# =============================================================================


def test_namespace_isolation():
    """
    [SECURITY] Verifies apps do not read from each other's vector space.
    Static check of configuration injection.
    """
    rg = RGAgentBase()
    lic = LICAgentBase()

    print(f"\n[DEBUG] RG Namespace: {rg._namespace}")
    print(f"[DEBUG] LIC Namespace: {lic._namespace}")

    assert rg._namespace == "apps_rg", f"RG Namespace incorrect: {rg._namespace}"
    assert lic._namespace == "apps_lic", f"LIC Namespace incorrect: {lic._namespace}"
    assert rg._namespace != lic._namespace, (
        "CRITICAL: Namespaces must differ to prevent memory bleed"
    )


# =============================================================================
# TEST 4: SERIALIZATION SAFETY
# =============================================================================


@pytest.mark.asyncio
async def test_serialization_fail_open():
    """
    [RESILIENCY] Verifies cache does not crash on bad data.
    """
    agent = RGAgentBase()
    # Mock the internal cache dictionary to verify no-op
    agent._local_cache = {}

    import threading

    bad_obj = threading.Lock()  # Not JSON serializable

    try:
        await agent.cache_set("key_bad", bad_obj)
    except Exception as e:
        pytest.fail(f"Agent crashed on bad cache data: {e}")

    # Verify nothing was written (fail-open)
    assert "key_bad" not in agent._local_cache, "Bad object was cached locally!"
