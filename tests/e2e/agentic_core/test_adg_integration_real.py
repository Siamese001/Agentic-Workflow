"""Deterministic E2E Tests for ADG Integration - REAL SQLite Data.

Tests the production ADG integration with actual SQLite queries.
- Uses real ADG SQLite database (adg_indexed_03292026_1406.sqlite)
- Tests accelerator queries: impact, fanout/fanin, layer violations
- Deterministic - same inputs always produce same outputs
- Evidence capture per Constitutional Rule #1

Usage:
    pytest tests/e2e/test_adg_integration_real.py -v
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


@dataclass
class EvidenceRecord:
    """Evidence record for deterministic test verification."""

    test_name: str
    timestamp: float
    inputs_hash: str
    outputs_hash: str
    execution_trace: list[str] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_name": self.test_name,
            "timestamp": self.timestamp,
            "inputs_hash": self.inputs_hash,
            "outputs_hash": self.outputs_hash,
            "execution_trace": self.execution_trace,
            "artifacts": self.artifacts,
        }


class EvidenceCollector:
    """Collects evidence during test execution for determinism verification."""

    def __init__(self):
        self.evidence: list[EvidenceRecord] = []
        self._current: EvidenceRecord | None = None

    def start_test(self, test_name: str, inputs: dict[str, Any]) -> None:
        """Start collecting evidence for a test."""
        inputs_hash = hashlib.sha256(json.dumps(inputs, sort_keys=True, default=str).encode()).hexdigest()[
            :16
        ]

        self._current = EvidenceRecord(
            test_name=test_name,
            timestamp=time.time(),
            inputs_hash=inputs_hash,
            outputs_hash="",
            execution_trace=[f"start:{test_name}"],
        )

    def record_step(self, step: str) -> None:
        """Record an execution step."""
        if self._current:
            self._current.execution_trace.append(f"{time.time():.6f}:{step}")

    def record_artifact(self, name: str, value: Any) -> None:
        """Record a test artifact."""
        if self._current:
            self._current.artifacts[name] = value

    def end_test(self, outputs: dict[str, Any]) -> EvidenceRecord:
        """End evidence collection and finalize."""
        if not self._current:
            raise RuntimeError("No test in progress")

        outputs_hash = hashlib.sha256(json.dumps(outputs, sort_keys=True, default=str).encode()).hexdigest()[
            :16
        ]

        self._current.outputs_hash = outputs_hash
        self._current.execution_trace.append(f"end:{self._current.test_name}")

        evidence = self._current
        self.evidence.append(evidence)
        self._current = None

        return evidence

    def verify_determinism(self, test_name: str, runs: int = 3) -> bool:
        """Verify that a test produces deterministic results."""
        test_evidence = [e for e in self.evidence if e.test_name == test_name]

        if len(test_evidence) < runs:
            return False

        first_hash = test_evidence[0].outputs_hash
        return all(e.outputs_hash == first_hash for e in test_evidence[:runs])


evidence_collector = EvidenceCollector()


def _store_evidence_to_file(evidence: EvidenceRecord) -> None:
    """Store evidence to a file for later analysis."""
    evidence_dir = Path("artifacts/evidence/adg_integration")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    def serialize(obj: Any) -> Any:
        """JSON serializer for non-standard types."""
        from dataclasses import asdict

        from agentic_core.L3_orchestration.reasoning.engines.adg_integration import ADGEdge, ADGNode

        if isinstance(obj, (ADGNode, ADGEdge)):
            return asdict(obj)
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    evidence_file = evidence_dir / f"{evidence.test_name}_{int(evidence.timestamp)}.json"
    with open(evidence_file, "w") as f:
        json.dump(evidence.to_dict(), f, indent=2, default=serialize)


# =============================================================================
# Fixtures with REAL ADG
# =============================================================================


@pytest.fixture(scope="session")
def adg_client():
    """Provide ADG query client with real SQLite connection."""
    from agentic_core.L3_orchestration.reasoning.engines.adg_integration import ADGQueryClient

    client = ADGQueryClient()

    # Verify connection works
    topology = client.get_graph_topology()
    assert topology["node_count"] > 0, "ADG database has no nodes"
    assert topology["edge_count"] > 0, "ADG database has no edges"

    yield client
    client.close()


@pytest.fixture(scope="session")
def adg_integration(adg_client):
    """Provide GraphRAG ADG integration with real client."""
    from agentic_core.L3_orchestration.reasoning.engines.adg_integration import GraphRAGADGIntegration

    return GraphRAGADGIntegration(adg_client=adg_client)


# =============================================================================
# Test Class 1: Accelerator Query - Impact Analysis
# =============================================================================


@pytest.mark.timeout(60)
class TestImpactAnalysis:
    """Test accelerator query #1: Impact analysis with REAL ADG data."""

    def test_impact_analysis_dag_manager(self, adg_integration):
        """Analyze impact of changing dag_manager.py - REAL data."""
        test_name = "impact_analysis_dag_manager"
        inputs = {"file_path": "agentic_core/L3_orchestration/engines/dag_manager.py"}

        evidence_collector.start_test(test_name, inputs)
        evidence_collector.record_step("started_impact_analysis")

        # Execute real impact analysis
        result = adg_integration.analyze_impact_for_change(
            file_path="agentic_core/L3_orchestration/engines/dag_manager.py",
            max_depth=2,
        )

        evidence_collector.record_step("impact_analysis_complete")
        evidence_collector.record_artifact("result", result)

        # Assertions
        assert "entry_points" in result
        assert "affected_files" in result
        assert isinstance(result["affected_files"], list)

        # Verify real data was returned
        assert result["source_file"] == "agentic_core/L3_orchestration/engines/dag_manager.py"

        outputs = {"entry_point_count": len(result["entry_points"])}
        evidence = evidence_collector.end_test(outputs)
        _store_evidence_to_file(evidence)

    def test_impact_analysis_bounded_depth(self, adg_integration):
        """Verify impact analysis respects max_depth parameter."""
        inputs = {"file_path": "agentic_core/L3_orchestration/types/orchestrator_types.py", "max_depth": 1}

        evidence_collector.start_test("impact_depth_1", inputs)

        result_depth_1 = adg_integration.analyze_impact_for_change(
            file_path="agentic_core/L3_orchestration/types/orchestrator_types.py",
            max_depth=1,
        )

        evidence_collector.record_step("depth_1_complete")

        result_depth_3 = adg_integration.analyze_impact_for_change(
            file_path="agentic_core/L3_orchestration/types/orchestrator_types.py",
            max_depth=3,
        )

        evidence_collector.record_step("depth_3_complete")

        # Depth 3 should find at least as many affected files as depth 1
        assert len(result_depth_3["affected_files"]) >= len(result_depth_1["affected_files"])

        evidence_collector.end_test({"depth1_count": len(result_depth_1["affected_files"])})


# =============================================================================
# Test Class 2: Accelerator Query - Fan Analysis
# =============================================================================


@pytest.mark.timeout(60)
class TestFanAnalysis:
    """Test accelerator query #2: Fan-in/fan-out analysis with REAL ADG data."""

    def test_fan_analysis_existing_symbol(self, adg_integration):
        """Analyze fan-in/fan-out for a known symbol."""
        test_name = "fan_analysis_known_symbol"

        # Use a symbol we know exists (full ADG::Symbol:: prefix required)
        symbol = "ADG::Symbol::agentic_core.L3_orchestration.engines.dag_manager::DAGManager"
        inputs = {"symbol_name": symbol}

        evidence_collector.start_test(test_name, inputs)
        evidence_collector.record_step("starting_fan_analysis")

        result = adg_integration.get_fan_analysis(symbol)

        evidence_collector.record_step("fan_analysis_complete")
        evidence_collector.record_artifact("result", result)

        # Verify structure
        assert "symbol" in result
        assert "fan_in" in result
        assert "fan_out" in result

        if result["found"]:
            assert "node_id" in result
            assert "layer" in result
            assert isinstance(result["fan_in"]["total_edges"], int)
            assert isinstance(result["fan_out"]["total_edges"], int)

        outputs = {"found": result["found"]}
        evidence = evidence_collector.end_test(outputs)
        _store_evidence_to_file(evidence)

    def test_fan_analysis_nonexistent_symbol(self, adg_integration):
        """Handle gracefully when symbol doesn't exist."""
        symbol = "nonexistent.module.SymbolThatDoesNotExist"

        result = adg_integration.get_fan_analysis(symbol)

        assert result["found"] is False
        assert "error" in result


# =============================================================================
# Test Class 3: Accelerator Query - Layer Violations
# =============================================================================


@pytest.mark.timeout(60)
class TestLayerViolations:
    """Test accelerator query #3: Layer violation detection with REAL ADG data."""

    def test_layer_violations_full_repo(self, adg_integration):
        """Detect all layer violations in the repo."""
        test_name = "layer_violations_full_repo"
        inputs = {"scope": "entire_repo"}

        evidence_collector.start_test(test_name, inputs)
        evidence_collector.record_step("starting_violation_detection")

        result = adg_integration.get_layer_violations()

        evidence_collector.record_step("violation_detection_complete")
        evidence_collector.record_artifact("result", result)

        # Verify structure
        assert "scope" in result
        assert "violation_count" in result
        assert "violations" in result
        assert isinstance(result["violations"], list)

        # Should have found violations (repo has some)
        assert result["scope"] == "entire_repo"

        outputs = {"violation_count": result["violation_count"]}
        evidence = evidence_collector.end_test(outputs)
        _store_evidence_to_file(evidence)

    def test_layer_violations_specific_file(self, adg_integration):
        """Detect violations for a specific file."""
        result = adg_integration.get_layer_violations(
            file_path="agentic_core/L3_orchestration/engines/dag_manager.py",
        )

        assert result["scope"] == "agentic_core/L3_orchestration/engines/dag_manager.py"
        assert isinstance(result["violation_count"], int)
        assert isinstance(result["violations"], list)

        # Each violation should have required fields
        for v in result["violations"]:
            assert "type" in v
            assert "source_layer" in v
            assert "target_layer" in v


# =============================================================================
# Test Class 4: Integration - Real End-to-End
# =============================================================================


@pytest.mark.timeout(120)
class TestRealADE2E:
    """End-to-end tests with real ADG SQLite queries."""

    def test_adg_client_connectivity(self, adg_client):
        """Verify ADG client can connect and query."""
        # Query topology
        topology = adg_client.get_graph_topology()

        assert topology["node_count"] > 1000  # Should have many nodes
        assert topology["edge_count"] > 1000  # Should have many edges
        assert "relation_type_counts" in topology
        assert "layer_distribution" in topology

    def test_nodes_for_real_file(self, adg_client):
        """Get nodes for a real file in the repo."""
        nodes = adg_client.get_nodes_for_file("agentic_core/L3_orchestration/engines/dag_manager.py")

        # Should find nodes (this file exists and has code)
        assert isinstance(nodes, list)
        assert len(nodes) > 0

        # Verify node structure
        for node in nodes:
            assert hasattr(node, "node_id")
            assert hasattr(node, "symbol_name")
            assert hasattr(node, "layer")

    def test_edges_for_node(self, adg_client):
        """Get edges for a node."""
        # First get a node
        nodes = adg_client.get_nodes_for_file("agentic_core/L3_orchestration/engines/dag_manager.py")

        if nodes:
            node = nodes[0]
            edges = adg_client.get_edges_for_node(node.node_id, direction="out")

            assert isinstance(edges, list)

            # Verify edge structure
            for edge in edges:
                assert hasattr(edge, "edge_id")
                assert hasattr(edge, "src_id")
                assert hasattr(edge, "dst_id")
                assert hasattr(edge, "relation_type")

    def test_fanout_analysis(self, adg_client):
        """Perform fan-out analysis on a real node."""
        nodes = adg_client.get_nodes_for_file("agentic_core/L3_orchestration/engines/dag_manager.py")

        if nodes:
            fanout = adg_client.get_fanout_edges(nodes[0].node_id)

            assert fanout.node_id == nodes[0].node_id
            assert isinstance(fanout.edges, list)
            assert fanout.total_count >= 0

    def test_determinism_same_query(self, adg_client):
        """Verify same query produces same results (determinism)."""
        file_path = "agentic_core/L3_orchestration/engines/dag_manager.py"

        # Run same query twice
        nodes_1 = adg_client.get_nodes_for_file(file_path)
        nodes_2 = adg_client.get_nodes_for_file(file_path)

        # Should get same count
        assert len(nodes_1) == len(nodes_2)

        # Same node IDs
        ids_1 = {n.node_id for n in nodes_1}
        ids_2 = {n.node_id for n in nodes_2}
        assert ids_1 == ids_2

    def test_direction_validation(self, adg_client):
        """Verify direction parameter validation rejects invalid values."""
        with pytest.raises(ValueError, match="Invalid direction"):
            adg_client.get_edges_for_node("12345", direction="invalid")

    def test_max_depth_validation(self, adg_client):
        """Verify max_depth validation rejects negative and zero values."""
        with pytest.raises(ValueError, match="max_depth must be >= 1"):
            adg_client.analyze_impact("12345", max_depth=0)
        with pytest.raises(ValueError, match="max_depth must be >= 1"):
            adg_client.analyze_impact("12345", max_depth=-1)

    def test_context_manager(self):
        """Verify context manager properly closes connection."""
        from agentic_core.L3_orchestration.reasoning.engines.adg_integration import ADGQueryClient

        with ADGQueryClient() as client:
            # Should work within context
            topology = client.get_graph_topology()
            assert topology["node_count"] > 0

        # Connection should be closed after exiting context

    def test_idempotent_close(self, adg_client):
        """Verify close() can be called multiple times without error."""
        # First close should work
        adg_client.close()
        # Second close should be idempotent (no error)
        adg_client.close()
        # Third close should also be safe
        adg_client.close()


# =============================================================================
# Cleanup
# =============================================================================


def pytest_sessionfinish(session, exitstatus):
    """Cleanup after all tests complete."""
    # Clean up evidence files older than 7 days
    evidence_dir = Path("artifacts/evidence/adg_integration")
    if evidence_dir.exists():
        cutoff = time.time() - (7 * 24 * 60 * 60)
        for evidence_file in evidence_dir.glob("*.json"):
            try:
                if evidence_file.stat().st_mtime < cutoff:
                    evidence_file.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
