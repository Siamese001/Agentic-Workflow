#!/usr/bin/env python3
"""Create a CLEAN static ADG with zero runtime contamination.

STATIC ADG = what the system IS (design-time structure)
RUNTIME ADG = what the system DID (execution-time evidence)

This script builds a pure static ADG containing ONLY:
- Imports (design-time dependencies)
- Call graph (design-time structure)
- Class hierarchy (design-time inheritance)
- Module structure (design-time organization)
- Symbol definitions (design-time interface)

NEVER includes:
- Execution traces
- Runtime state
- Policy actions
- Guardrail applications
- Healing operations
- Learning signals
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.adg.artifact.builder_types import ADGArtifact, build_artifact
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner, Edge

# STATIC-ONLY relation types (design-time structure)
STATIC_RELATIONS = {
    # Core structural relations
    "imports",
    "calls",
    "implements",
    "instantiates",
    "exports",
    "belongs_to_layer",
    # Test structure (still design-time)
    "covers",
    "defines_test_case",
    "defines_test_suite",
    # Code quality (design-time analysis)
    "antipattern",
    "dead_imports",
    "violates",
    "duplicate_method",
    "unreachable_after_raise",
}

# RUNTIME relations to filter out (must NOT be in static ADG)
RUNTIME_RELATIONS = {
    # Execution traces
    "records_execution_trace",
    "emits_determinism_digest",
    "emits_replay_key",
    "signs_execution_trace",
    "snapshots_state",
    # Runtime policy actions
    "applies_guardrail",
    "validated_by_safety_plane",
    "verifies_policy",
    "reads_policy_state",
    "observes_policy_state",
    # Runtime state
    "observes_runtime_state",
    "reads_runtime_state",
    "pulls_context",
    "writes_through",
    # Runtime orchestration
    "agent_executes_agent",
    "orchestrates_workflow",
    "dispatches_execution_plan",
    "dispatches_healing_run",
    "escalates_to_human",
    # Runtime learning
    "captures_pattern",
    "records_learning_event",
    "feeds_meta_learning",
    "updates_routing_strategy",
    # Runtime observability
    "emits_metric_event",
    "records_incident_event",
    "captures_runtime_anomaly",
    "writes_observability_log",
    "triggers_alert",
    # Runtime evaluation
    "invokes_eval",
    "invokes_evaluation",
    "gated_by_confidence",
    "execution_terminates_at_uwg",
    # Runtime agent operations
    "checks_agent_registry",
    "validates_agent_capability",
    "routes_to_agent",
    "coordinates_agents",
    # Runtime tool operations
    "records_tool_invocation",
    "captures_execution_output",
    "authorize_and_execute",
    "writes_via_uwg",
    "blocks_direct_write",
    # Runtime evidence
    "transcripts_response",
    "proposal_commits_routing",
    "references_policy_hash",
    "stores_embedding",
}


def filter_static_edges(edges: list[Edge]) -> list[Edge]:
    """Filter out all runtime edges, keeping only static structure."""
    static_edges = []
    runtime_filtered = 0

    for edge in edges:
        if edge.relation_type in STATIC_RELATIONS:
            static_edges.append(edge)
        elif edge.relation_type in RUNTIME_RELATIONS:
            runtime_filtered += 1
        else:
            # Unknown relation - default to static if it looks structural
            if edge.relation_type in ["imports", "calls", "implements", "exports", "belongs_to_layer"]:
                static_edges.append(edge)
            else:
                runtime_filtered += 1

    print(f"[STATIC] Filtered edges: {len(static_edges)} static, {runtime_filtered} runtime removed")
    return static_edges


def create_clean_static_adg() -> ADGArtifact:
    """Create a pure static ADG with zero runtime contamination."""
    print("[STATIC] Creating clean static ADG...")
    print("[STATIC] Rule: IF it requires execution to observe → RUNTIME ADG")
    print("[STATIC] Rule: IF it exists without execution → STATIC ADG")

    # Scan all Python files
    scanner = ADGStaticScanner(
        repo_root=PROJECT_ROOT,
        include_tests=True,  # Include tests for complete static view
        cache_path=None,  # No cache to ensure clean scan
    )

    print("[STATIC] Scanning codebase...")
    result = scanner.scan()
    print(f"[STATIC] Raw scan: {len(result.modules)} modules, {len(result.edges)} edges")

    # Filter out ALL runtime contamination
    print("[STATIC] Filtering runtime edges...")
    static_edges = filter_static_edges(result.edges)

    # Create clean artifact
    print("[STATIC] Building static artifact...")
    artifact = build_artifact(result)

    # Override edges with clean static edges only
    artifact.edges = static_edges

    print(f"[STATIC] Clean ADG: {len(result.modules)} modules, {len(static_edges)} edges")

    # Verify no runtime contamination
    runtime_leak = []
    for edge in static_edges:
        if edge.relation_type in RUNTIME_RELATIONS:
            runtime_leak.append(edge.relation_type)

    if runtime_leak:
        print(f"[ERROR] Runtime contamination detected: {set(runtime_leak)}")
        raise RuntimeError("Static ADG still contains runtime relations!")

    print("[STATIC] ✅ Verified: Zero runtime contamination")
    return artifact


def verify_static_purity(artifact: ADGArtifact) -> bool:
    """Verify the ADG contains ONLY static relations."""
    print("\n[VERIFY] Checking static purity...")

    relation_counts = {}
    for edge in artifact.edges:
        relation_counts[edge.relation_type] = relation_counts.get(edge.relation_type, 0) + 1

    print("[VERIFY] Relation types found:")
    for rel_type, count in sorted(relation_counts.items()):
        category = "STATIC" if rel_type in STATIC_RELATIONS else "RUNTIME"
        print(f"  {rel_type}: {count} ({category})")

    # Check for any runtime relations
    runtime_found = []
    for rel_type in relation_counts:
        if rel_type in RUNTIME_RELATIONS:
            runtime_found.append(rel_type)

    if runtime_found:
        print(f"\n[VERIFY] ❌ FAILED: Runtime relations found: {runtime_found}")
        return False

    print("\n[VERIFY] ✅ PASSED: Pure static ADG")
    print(f"[VERIFY] Static modules: {len([e for e in artifact.entities if e.entity_type == 'module'])}")
    print(f"[VERIFY] Static edges: {len(artifact.edges)}")
    return True


def main():
    """Main entry point."""
    print("=" * 80)
    print("CLEAN STATIC ADG GENERATOR")
    print("=" * 80)
    print("STATIC ADG = what the system IS (design-time structure)")
    print("RUNTIME ADG = what the system DID (execution-time evidence)")
    print("=" * 80)

    try:
        # Create clean static ADG
        artifact = create_clean_static_adg()

        # Verify purity
        if not verify_static_purity(artifact):
            sys.exit(1)

        # Write clean ADG
        from datetime import datetime, timedelta, timezone

        from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

        # Timestamp
        est = timezone(timedelta(hours=-4))
        now_est = datetime.now(est)
        ts = now_est.strftime("%m%d%Y_%H%M")

        # Write to clean directory
        clean_dir = PROJECT_ROOT / "artifacts" / "adg_clean"
        clean_dir.mkdir(exist_ok=True)

        paths = write_all_artifacts(artifact, out_dir=clean_dir, ts=ts)

        print(f"\n[CLEAN] Static ADG written to: {clean_dir}")
        print(f"[CLEAN] SQLite: {paths.sqlite.name}")
        print(f"[CLEAN] Size: {paths.sqlite.stat().st_size / (1024 * 1024):.1f} MB")

        # Final verification
        print("\n" + "=" * 80)
        print("STATIC ADG VERIFICATION COMPLETE")
        print("=" * 80)
        print("✅ Zero runtime contamination")
        print("✅ Pure design-time structure")
        print("✅ Mental model enforced")
        print("=" * 80)

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
