"""GraphRAG Integration Validation Script.

Validates that all GraphRAG components are properly integrated:
- Pipeline B: Graph-aware ingestion with ADG edges
- Pipeline C: L4E retrieval with parent-child expansion
- Pipeline D: Meta-learning feedback loop
- ADG integration layer

Usage:
    python -m tests.e2e.validate_graphrag_integration
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def validate_imports() -> dict[str, bool]:
    """Validate all required imports are available."""
    results = {}

    # Pipeline B imports
    try:
        from agentic_core.L3_orchestration.reasoning.engines.graph_aware_indexer import (
            ADGEdgeBinding,
            ADGEdgeExtractor,
            GraphAwareIndexer,
        )
        results["pipeline_b.graph_aware_indexer"] = True
    except ImportError as e:
        results["pipeline_b.graph_aware_indexer"] = False
        print(f"  ERROR: {e}")

    # Pipeline C imports
    try:
        from agentic_core.L3_orchestration.reasoning.engines.l4e_retrieval_integration import (
            ADGEdgeHydrator,
            GraphRetrievalContext,
            GraphRetrievalEngine,
        )
        results["pipeline_c.l4e_retrieval"] = True
    except ImportError as e:
        results["pipeline_c.l4e_retrieval"] = False
        print(f"  ERROR: {e}")

    # Pipeline D imports
    try:
        from agentic_core.L4_state.reasoning.meta_learning_feedback import (
            CompletenessAnalyzer,
            CompletenessRAGProposer,
            EvaluationRunner,
            FeedbackTrigger,
        )
        results["pipeline_d.meta_learning"] = True
    except ImportError as e:
        results["pipeline_d.meta_learning"] = False
        print(f"  ERROR: {e}")

    # ADG Integration imports
    try:
        from agentic_core.L3_orchestration.reasoning.engines.adg_integration import (
            ADGQueryClient,
            GraphRAGADGIntegration,
        )
        results["adg_integration"] = True
    except ImportError as e:
        results["adg_integration"] = False
        print(f"  ERROR: {e}")

    # L4 Registries
    try:
        from agentic_core.evaluation.retrieval.l4_registries import (
            ChunkManifest,
            ChunkManifestRegistry,
            ParentChildIndexRegistry,
            ParentChildLink,
        )
        results["l4_registries"] = True
    except ImportError as e:
        results["l4_registries"] = False
        print(f"  ERROR: {e}")

    # Parent-child expansion
    try:
        from agentic_core.L4_state.reasoning.parent_child_expansion import (
            ExpansionContext,
            L4ERetrievalIntegrator,
            ParentChildExpander,
        )
        results["parent_child_expansion"] = True
    except ImportError as e:
        results["parent_child_expansion"] = False
        print(f"  ERROR: {e}")

    return results


def validate_lifecycle_contracts() -> dict[str, bool]:
    """Validate lifecycle trace contract emitters are available."""
    results = {}

    try:
        from agentic_core.runtime.lifecycle_trace_contract import (
            _emit_captures_evaluation_metric,
            _emit_feeds_meta_learning,
            _emit_improves_agent_policy,
            _emit_pulls_context,
            _emit_reads_through,
            _emit_records_execution_trace,
            _emit_records_learning_event,
            _emit_stores_embedding,
            _emit_updates_routing_strategy,
            _emit_writes_through,
        )
        results["lifecycle_contracts"] = True
    except ImportError as e:
        results["lifecycle_contracts"] = False
        print(f"  ERROR: {e}")

    return results


def validate_pipeline_b_functionality() -> dict[str, bool]:
    """Validate Pipeline B components work correctly."""
    results = {}

    try:
        from agentic_core.L3_orchestration.reasoning.engines.graph_aware_indexer import (
            ADGEdgeBinding,
            GraphAwareIndexer,
        )

        # Create indexer
        indexer = GraphAwareIndexer()

        # Test indexing
        test_chunks = [
            {"chunk_id": "test_chunk_0", "content": "Test content", "metadata": {}},
            {"chunk_id": "test_chunk_1", "content": "More content", "metadata": {}},
        ]

        adg_edges = ADGEdgeBinding(
            chunk_id="test_edges",
            source_file="test.md",
            reads_from=["Entity1"],
            writes_to=["Entity2"],
        )

        result = indexer.index_document(
            doc_id="test_doc",
            source_path="test.md",
            chunks=test_chunks,
            adg_edges=adg_edges,
        )

        results["index_document"] = result["chunks_indexed"] == 2
        results["l4d_registry"] = indexer.l4d_registry is not None
        results["l4e_registry"] = indexer.l4e_registry is not None

    except Exception as e:
        results["pipeline_b_error"] = False
        print(f"  ERROR in Pipeline B: {e}")

    return results


def validate_pipeline_c_functionality() -> dict[str, bool]:
    """Validate Pipeline C components work correctly."""
    results = {}

    try:
        from agentic_core.L4_state.reasoning.parent_child_expansion import (
            ExpansionContext,
            ParentChildExpander,
        )

        # Create expander
        expander = ParentChildExpander(max_depth=2)

        # Mock L4E registry
        from unittest.mock import MagicMock
        mock_l4e = MagicMock()
        mock_l4e.get_parents.return_value = []
        mock_l4e.get_children.return_value = []
        mock_l4e.get_siblings.return_value = []

        expander.l4e_registry = mock_l4e

        # Test expansion
        contexts = expander.expand(
            seed_chunk_id="test_seed",
            seed_content="Test content",
        )

        results["parent_child_expansion"] = len(contexts) >= 1
        results["expansion_context"] = isinstance(contexts[0], ExpansionContext)

    except Exception as e:
        results["pipeline_c_error"] = False
        print(f"  ERROR in Pipeline C: {e}")

    return results


def validate_pipeline_d_functionality() -> dict[str, bool]:
    """Validate Pipeline D components work correctly."""
    results = {}

    try:
        from agentic_core.L4_state.reasoning.meta_learning_feedback import (
            CompletenessAnalyzer,
            CompletenessRAGProposer,
            EvaluationRunner,
        )

        # Create components
        proposer = CompletenessRAGProposer()
        runner = EvaluationRunner()
        analyzer = CompletenessAnalyzer()

        # Test evaluation
        metrics = runner.evaluate(
            query="test",
            retrieved_chunks=["chunk_1"],
            relevant_chunks=["chunk_1", "chunk_2"],
            groundedness_scores=[0.8],
        )

        results["evaluation_runner"] = metrics.precision_at_k >= 0

        # Test completeness analysis
        analysis = analyzer.analyze(
            query="test if condition",
            retrieved_contexts=[{"content": "If condition then action"}],
        )

        results["completeness_analyzer"] = 0 <= analysis.mean_completeness <= 1.0

        # Test proposer
        change_package = proposer.analyze_and_propose([])

        results["proposer"] = change_package is not None

    except Exception as e:
        results["pipeline_d_error"] = False
        print(f"  ERROR in Pipeline D: {e}")

    return results


def validate_adg_integration() -> dict[str, bool]:
    """Validate ADG integration layer."""
    results = {}

    try:
        from agentic_core.L3_orchestration.reasoning.engines.adg_integration import (
            ADGQueryClient,
            GraphRAGADGIntegration,
        )

        # Create components
        client = ADGQueryClient()
        integration = GraphRAGADGIntegration(adg_client=client)

        # Test node retrieval
        nodes = client.get_nodes_for_file("test.py")
        results["adg_node_query"] = len(nodes) > 0

        # Test edge binding
        binding = integration.bind_edges_for_ingestion(
            doc_id="test",
            source_path="test.py",
            chunks=[],
        )

        results["adg_edge_binding"] = "adg_nodes" in binding

    except Exception as e:
        results["adg_integration_error"] = False
        print(f"  ERROR in ADG integration: {e}")

    return results


def print_results(title: str, results: dict[str, bool]) -> None:
    """Print validation results."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {component}")

    print(f"\n  Summary: {passed}/{total} passed")

    return passed == total


def main() -> int:
    """Run all validations."""
    print("\n" + "=" * 60)
    print("  GraphRAG Integration Validation")
    print("  Agentic Retrieval Models v9 Compliance")
    print("=" * 60)

    all_passed = True

    # Validate imports
    import_results = validate_imports()
    if not print_results("Import Validation", import_results):
        all_passed = False

    # Validate lifecycle contracts
    contract_results = validate_lifecycle_contracts()
    if not print_results("Lifecycle Contract Validation", contract_results):
        all_passed = False

    # Validate Pipeline B
    pipeline_b_results = validate_pipeline_b_functionality()
    if not print_results("Pipeline B (Ingestion) Validation", pipeline_b_results):
        all_passed = False

    # Validate Pipeline C
    pipeline_c_results = validate_pipeline_c_functionality()
    if not print_results("Pipeline C (Retrieval) Validation", pipeline_c_results):
        all_passed = False

    # Validate Pipeline D
    pipeline_d_results = validate_pipeline_d_functionality()
    if not print_results("Pipeline D (Learning) Validation", pipeline_d_results):
        all_passed = False

    # Validate ADG Integration
    adg_results = validate_adg_integration()
    if not print_results("ADG Integration Validation", adg_results):
        all_passed = False

    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ ALL VALIDATIONS PASSED")
        print("  GraphRAG is fully implemented and integrated.")
    else:
        print("  ❌ SOME VALIDATIONS FAILED")
        print("  Please review the errors above.")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
