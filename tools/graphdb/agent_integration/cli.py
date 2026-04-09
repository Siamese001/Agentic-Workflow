"""CLI Interface for Phase 1 Agent Integration.

This module provides command-line interface for testing and validating
the Phase 1 GraphDB agent integration implementation.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add repo root to path for imports
repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(repo_root))

from tools.graphdb.project_graph import project_graph
from tools.graphdb.agent_integration.decision_engine import AgentDecisionEngine, ArchitecturalContext
from tools.graphdb.agent_integration.guardrails import ArchitecturalGuardrails
from tools.graphdb.agent_integration.cache import QueryCache
from tools.graphdb.agent_integration.validators import CompletionGates

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_completion_gates(graph_path: Path, verbose: bool = False) -> int:
    """Run all Phase 1 completion gates.

    Args:
        graph_path: Path to ADG SQLite file
        verbose: Enable verbose logging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    setup_logging(verbose)

    logger.info("Starting Phase 1 completion gate validation")

    try:
        # Load or project graph
        if graph_path.suffix == ".sqlite":
            # Load existing SQLite
            logger.info(f"Loading graph from SQLite: {graph_path}")
            from tools.graphdb.projection import GraphProjector

            projector = GraphProjector(graph_path)
            graph = projector.project_graph()
        else:
            # Project from SQLite
            logger.info(f"Projecting graph from: {graph_path}")
            output_dir = Path("artifacts/graphdb")
            output_dir.mkdir(parents=True, exist_ok=True)
            graph, metadata = project_graph(graph_path, output_dir)

        logger.info(f"Loaded graph with {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

        # Initialize components
        cache = QueryCache(max_size=1000, default_ttl=300.0)
        decision_engine = AgentDecisionEngine(graph, cache)
        guardrails = ArchitecturalGuardrails(decision_engine)
        completion_gates = CompletionGates(decision_engine, guardrails, cache)

        # Run all gates
        results = completion_gates.run_all_gates()

        # Get overall status
        overall_status, overall_score = completion_gates.get_overall_status(results)

        # Print results
        print("\n" + "=" * 80)
        print("PHASE 1 COMPLETION GATE RESULTS")
        print("=" * 80)

        for gate_name, result in results.items():
            status_symbol = "✓" if result.status.value == "passed" else "✗"
            print(
                f"{status_symbol} {gate_name}: {result.status.value} (score: {result.score:.2f}, time: {result.execution_time_seconds:.3f}s)"
            )

            if result.issues:
                for issue in result.issues:
                    print(f"    - Issue: {issue}")

            if result.recommendations:
                for rec in result.recommendations:
                    print(f"    - Recommendation: {rec}")

        print("\n" + "-" * 80)
        print(f"OVERALL STATUS: {overall_status.value}")
        print(f"OVERALL SCORE: {overall_score:.2f}")
        print("-" * 80)

        # Return appropriate exit code
        if overall_status.value == "passed":
            print("\n🎉 Phase 1 implementation PASSED all completion gates!")
            return 0
        else:
            print("\n❌ Phase 1 implementation FAILED completion gates.")
            print("Please address the issues above before proceeding to Phase 2.")
            return 1

    except (FileNotFoundError, RuntimeError, ValueError, KeyError, AttributeError, TypeError) as e:
        logger.error(f"Error running completion gates: {e}")
        print(f"\n❌ ERROR: {e}")
        return 1


def test_agent_integration(graph_path: Path, verbose: bool = False) -> int:
    """Test agent integration with sample scenarios.

    Args:
        graph_path: Path to ADG SQLite file
        verbose: Enable verbose logging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    setup_logging(verbose)

    logger.info("Testing agent integration scenarios")

    try:
        # Load graph
        from tools.graphdb.projection import GraphProjector

        projector = GraphProjector(graph_path)
        graph = projector.project_graph()

        # Initialize components
        cache = QueryCache(max_size=1000, default_ttl=300.0)
        decision_engine = AgentDecisionEngine(graph, cache)
        guardrails = ArchitecturalGuardrails(decision_engine)

        # Test scenarios
        scenarios = [
            {
                "name": "Low Risk File Read",
                "context": ArchitecturalContext(
                    agent_type="code_agent",
                    action_type="read_file",
                    target_modules=["safe_module"],
                    proposed_changes={"type": "read"},
                    session_id="test_session_1",
                ),
            },
            {
                "name": "High Risk Direct Write",
                "context": ArchitecturalContext(
                    agent_type="code_agent",
                    action_type="write_file",
                    target_modules=["critical_spine", "uwg_bypass"],
                    proposed_changes={"type": "direct_write", "bypass": True},
                    session_id="test_session_2",
                ),
            },
            {
                "name": "Module Import",
                "context": ArchitecturalContext(
                    agent_type="code_agent",
                    action_type="import_module",
                    target_modules=["new_dependency"],
                    proposed_changes={"type": "import", "source": "external"},
                    session_id="test_session_3",
                ),
            },
        ]

        print("\n" + "=" * 80)
        print("AGENT INTEGRATION TEST SCENARIOS")
        print("=" * 80)

        all_passed = True

        for scenario in scenarios:
            print(f"\n📋 Testing: {scenario['name']}")

            # Test decision engine
            decision_result = decision_engine.analyze_action(scenario["context"])
            print(
                f"  Decision Engine: {decision_result.risk_level.value} risk -> {'APPROVED' if decision_result.approved else 'BLOCKED'}"
            )

            if decision_result.insights:
                for insight in decision_result.insights:
                    print(f"    Insight: {insight}")

            if decision_result.warnings:
                for warning in decision_result.warnings:
                    print(f"    Warning: {warning}")

            # Test guardrails
            guardrail_result = guardrails.validate_action(scenario["context"])
            print(f"  Guardrails: {guardrail_result.action.value}")

            if guardrail_result.required_modifications:
                for mod in guardrail_result.required_modifications:
                    print(f"    Required: {mod}")

            # Check if scenario behaved as expected
            if scenario["name"] == "Low Risk File Read":
                if decision_result.risk_level not in ["low", "medium"] or not decision_result.approved:
                    print(f"    ❌ Unexpected: Low risk scenario should be approved")
                    all_passed = False
                else:
                    print(f"    ✓ Expected: Low risk scenario approved")

            elif scenario["name"] == "High Risk Direct Write":
                if decision_result.risk_level not in ["high", "critical"]:
                    print(f"    ❌ Unexpected: High risk scenario should be flagged")
                    all_passed = False
                else:
                    print(f"    ✓ Expected: High risk scenario flagged")

        print("\n" + "-" * 80)
        if all_passed:
            print("✅ All agent integration test scenarios PASSED!")
            return 0
        else:
            print("❌ Some agent integration test scenarios FAILED!")
            return 1

    except (FileNotFoundError, RuntimeError, ValueError, KeyError, AttributeError, TypeError) as e:
        logger.error(f"Error testing agent integration: {e}")
        print(f"\n❌ ERROR: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 1 Agent Integration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run completion gates
  python cli.py completion-gates artifacts/adg/adg_indexed_04082026_1914.sqlite

  # Run completion gates with verbose output
  python cli.py completion-gates --verbose artifacts/adg/adg_indexed_04082026_1914.sqlite

  # Test agent integration
  python cli.py test-integration artifacts/adg/adg_indexed_04082026_1914.sqlite
        """,
    )

    parser.add_argument("command", choices=["completion-gates", "test-integration"], help="Command to run")

    parser.add_argument("graph_path", type=Path, help="Path to ADG SQLite file")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Validate input
    if not args.graph_path.exists():
        print(f"Error: Graph file not found: {args.graph_path}", file=sys.stderr)
        return 1

    # Run command
    if args.command == "completion-gates":
        return run_completion_gates(args.graph_path, args.verbose)
    elif args.command == "test-integration":
        return test_agent_integration(args.graph_path, args.verbose)
    else:
        print(f"Error: Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
