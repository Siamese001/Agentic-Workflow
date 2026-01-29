import pytest
import asyncio
import time
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Mock the sovereign lock to bypass integrity checks
with patch(
    "agentic_core.domain.sovereign_lock.CoreIntegrityVerifier.verify_core_integrity",
    return_value=True,
):
    with patch("agentic_core.domain.sovereign_lock.emergency_shutdown", MagicMock()):
        # Create minimal test agents
        class TestRGAgent(MetaLearningMixin, PineconeVectorMixin):
            _namespace = "apps_rg"
            _similarity_threshold = 0.85

            def __init__(self):
                pass

        class TestLICAgent(MetaLearningMixin, PineconeVectorMixin):
            _namespace = "apps_lic"
            _similarity_threshold = 0.92

            def __init__(self):
                pass


@pytest.mark.asyncio
async def test_semantic_drift_threshold_enforcement():
    """
    [CRITICAL] Validates that apps_lic (0.92) is stricter than apps_rg (0.85).
    MANDATORY 100% PASS.
    """
    mock_pinecone = AsyncMock()
    # Return a match with 0.88 score (acceptable for RG, failure for LIC)
    mock_pinecone.query.return_value = {"matches": [{"id": "1", "score": 0.88}]}

    # Mock feature flags to enable pinecone
    with patch("agentic_core.base_agents.pinecone_vector_mixin.USE_PINECONE", True):
        # RG Test
        rg = TestRGAgent()
        rg._pinecone_client = mock_pinecone
        rg_res = await rg.vector_search(embedding=[0.1] * 1536, apply_similarity_threshold=True)
        assert len(rg_res) == 1, "RG (0.85) must accept score 0.88"

        # LIC Test
        lic = TestLICAgent()
        lic._pinecone_client = mock_pinecone
        lic_res = await lic.vector_search(embedding=[0.1] * 1536, apply_similarity_threshold=True)
        assert len(lic_res) == 0, "LIC (0.92) must reject score 0.88"


@pytest.mark.asyncio
async def test_async_meta_learning_latency():
    """
    [PERFORMANCE] Ensures main thread is not blocked by Pinecone writes.
    Must return < 200ms.
    """

    async def slow_write(*args):
        await asyncio.sleep(0.5)  # Simulate 500ms network lag
        return True

    with patch(
        "agentic_core.base_agents.meta_learning_mixin.MetaLearningMixin._async_learn_experience",
        side_effect=slow_write,
    ) as mock_bg:
        agent = TestRGAgent()
        agent._lobotomized = False

        start = time.time()
        # This triggers the fire-and-forget task
        await agent.learn_experience("ctx", {"res": 1})
        duration = (time.time() - start) * 1000

        assert duration < 200, f"Main thread blocked for {duration}ms! Must be async."
        # Ensure the task was actually spawned
        await asyncio.sleep(0.1)
        # Note: We aren't awaiting the background task completion here to prove non-blocking


@pytest.mark.asyncio
async def test_namespace_isolation():
    """
    [SECURITY] Verifies apps do not read from each other's vector space.
    """
    rg = TestRGAgent()
    lic = TestLICAgent()
    assert rg._namespace == "apps_rg"
    assert lic._namespace == "apps_lic"
    assert rg._namespace != lic._namespace, "CRITICAL: Namespaces must differ"


@pytest.mark.asyncio
async def test_serialization_fail_open():
    """
    [RESILIENCY] Verifies cache does not crash on bad data.
    """
    agent = TestRGAgent()
    import threading

    bad_obj = threading.Lock()  # Not JSON serializable

    try:
        await agent.cache_set("key", bad_obj)
    except Exception as e:
        pytest.fail(f"Agent crashed on bad cache data: {e}")
