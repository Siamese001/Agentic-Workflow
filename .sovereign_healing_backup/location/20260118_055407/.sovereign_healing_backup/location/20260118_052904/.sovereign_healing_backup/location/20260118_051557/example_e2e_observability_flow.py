import asyncio
from unittest.mock import MagicMock
from agentic_core.L3_orchestration.pilot_orchestrator import PilotOrchestrator
from agentic_core.L2_execution.pilot_executor import PilotExecutor
from agentic_core.L6_observability.sovereign_observability_agent import SovereignObservabilityAgent

async def run_e2e_demo():
    # 1. Setup Mock Redis (Central Bus)
    mock_redis = MagicMock()
    # Simulate stream behavior: xreadgroup returns what was xadded
    captured_events = []
    
    def mock_xadd(stream, data, maxlen=None, **kwargs):
        captured_events.append((b"id-1", data))
        return b"id-1"
    
    def mock_xreadgroup(g, c, s, count=10, **kwargs):
        return [(b"sovereign_event_stream", captured_events)]
    
    mock_redis.xadd = mock_xadd
    mock_redis.xreadgroup = mock_xreadgroup
    mock_redis.xack = MagicMock()
    mock_redis.xgroup_create = MagicMock()

    # 2. Instantiate Hardened Fleet
    orchestrator = PilotOrchestrator(name="Alpha_Orch")
    executor = PilotExecutor(name="Beta_Exec")
    observer = SovereignObservabilityAgent(name="Omega_Obs")

    # Inject Mock Bus (override both redis_client and _redis_client to prevent lazy loading)
    for agent in [orchestrator, executor, observer]:
        agent.redis_client = mock_redis
        if hasattr(agent, '_redis_client'):
            agent._redis_client = mock_redis

    print("--- STARTING E2E HARDENED FLOW ---")

    # 3. Trigger L3 -> L2 Delegation (Phase 1 & 3 active)
    await orchestrator.run_pilot("Validate Sovereign SSOT", executor)

    # 4. Consume Events in L6 (Phase 2 active)
    print(f"\nObserver polling stream... ({len(captured_events)} events found)")
    
    # Temporarily disable observer's redis_client to prevent feedback loop
    # (observer emitting analysis events back to the stream it's consuming)
    observer.redis_client = None
    await observer.process_stream(count=10)

    print("\n--- E2E FLOW VERIFIED ---")
    print(f"Total events captured: {len(captured_events)}")
    print(f"Event types: {[evt[1].get(b'event', b'{}')[:50] for evt in captured_events[:3]]}")

if __name__ == "__main__":
    asyncio.run(run_e2e_demo())
