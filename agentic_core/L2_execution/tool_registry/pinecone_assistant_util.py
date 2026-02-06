from __future__ import annotations

"""
[DEPRECATED] This script is OBSOLETE as of Phase 1 Migration.

All Pinecone operations now route through PineconeSovereignAgent,
which provides:
- Automatic index creation with dimension guarding
- Redis-cached embeddings
- Audit logging
- Graceful degradation

Use PineconeSovereignAgent.bootstrap_territory_vectors() instead.
"""
from pathlib import Path

print("=" * 80)
print("[DEPRECATED] pinecone_assistant_util.py is OBSOLETE")
print("=" * 80)
print()
print("This script has been replaced by the Sovereign Gateway pattern.")
print("Redirecting to PineconeSovereignAgent...")
print()

try:
    from agentic_core.L5_safety.validators.PineconeSovereignAgent import PineconeSovereignAgent

    project_root = Path(__file__).resolve().parents[3]
    gateway = PineconeSovereignAgent(project_root=project_root)

    print(f"Gateway Status: {gateway.status}")

    if gateway.status == "ONLINE":
        print(f"✅ Connected to Pinecone index: {gateway.index_name}")
        print(f"   Dimension: {gateway.dimension}")
        print(f"   Cloud: {gateway.cloud}")
        print(f"   Region: {gateway.region}")
        print()
        print("The gateway handles index creation and dimension guarding automatically.")
        print("All operations are now audited and cached via Redis.")
    else:
        print(f"❌ Gateway initialization failed: {gateway.status}")
        print()
        print("Please check:")
        print("  1. PINECONE_API_KEY is set in environment")
        print("  2. SovereignEnv configuration is correct")

except Exception as e:
    print(f"❌ Failed to initialize Sovereign Gateway: {e}")
    print()
    print("Fallback: Direct SDK initialization (NOT RECOMMENDED)")
    print("Please fix the gateway configuration instead.")

print()
print("=" * 80)
