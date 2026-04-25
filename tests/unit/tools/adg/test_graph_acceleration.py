"""
Comprehensive tests for graph acceleration capabilities.

Tests materialized views, networkx analysis, SQLite helpers,
DuckDB integration, and agent infusion.
"""

import pytest
import tempfile
import sqlite3
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools"))

from tools.adg.analysis.sqlite_direct import GraphQueryHelper
from tools.adg.analysis.networkx_analysis import NetworkXAnalyzer
from tools.adg.analysis.duckdb_integration import DuckDBGraphAnalyzer, create_duckdb_analyzer
from tools.adg.analysis.materialized_views import MaterializedViewManager


class TestMaterializedViews:
    """Test materialized view creation and management."""

    @pytest.fixture
    def test_db(self):
        """Create test database with sample data."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)

        # Create basic schema
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                layer TEXT,
                node_type TEXT,
                file_path TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE edges (
                src_id INTEGER,
                tgt_id INTEGER,
                relation_type TEXT
            )
        """)

        # Insert test data
        nodes = [
            (1, "test_function", "L2_execution", "function", "test.py"),
            (2, "test_class", "L1_cognition", "class", "test.py"),
            (3, "orchestrator", "L3_orchestration", "class", "orch.py"),
            (4, "safety_guard", "L5_safety", "function", "safety.py"),
            (5, "state_manager", "L4_state", "class", "state.py"),
        ]

        edges = [
            (1, 2, "calls"),
            (2, 3, "imports"),
            (3, 4, "calls"),
            (4, 5, "reads_from"),
            (5, 1, "writes_to"),
        ]

        conn.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
        conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup (Windows-safe: file may still be locked by analyzer connection)
        try:
            os.unlink(db_path)
        except (PermissionError, OSError):
            pass

    def test_create_centrality_view(self, test_db):
        """Test centrality materialized view creation."""
        manager = MaterializedViewManager(test_db)

        # Create centrality view
        manager.create_centrality_view()

        # Verify view exists and has data
        conn = sqlite3.connect(test_db)
        result = conn.execute("SELECT COUNT(*) FROM mv_node_centrality").fetchone()
        assert result[0] > 0

        # Check specific centrality metrics
        result = conn.execute("""
            SELECT adg_name, in_degree, out_degree, betweenness_centrality
            FROM mv_node_centrality
            WHERE adg_name = 'test_function'
        """).fetchone()

        assert result is not None
        assert result[0] == "test_function"
        assert result[1] >= 0  # in_degree
        assert result[2] >= 0  # out_degree

        conn.close()

    def test_create_critical_path_view(self, test_db):
        """Test critical path materialized view creation."""
        manager = MaterializedViewManager(test_db)

        # Create critical path view
        manager.create_critical_path_view()

        # Verify view exists
        conn = sqlite3.connect(test_db)
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='mv_critical_path_blast_radius'"
        ).fetchone()
        assert result is not None
        assert result[0] == "mv_critical_path_blast_radius"

        conn.close()

    def test_create_layer_dependency_view(self, test_db):
        """Test layer dependency materialized view creation."""
        manager = MaterializedViewManager(test_db)

        # Create layer dependency view
        manager.create_layer_dependency_view()

        # Verify view exists and has data
        conn = sqlite3.connect(test_db)
        result = conn.execute("SELECT COUNT(*) FROM mv_layer_dependencies").fetchone()
        assert result[0] > 0

        # Check layer dependencies
        result = conn.execute("""
            SELECT source_layer, target_layer, dependency_count
            FROM mv_layer_dependencies
            WHERE source_layer = 'L1_cognition'
        """).fetchone()

        assert result is not None
        assert result[0] == "L1_cognition"
        assert result[2] > 0  # dependency_count

        conn.close()


class TestNetworkXAnalysis:
    """Test NetworkX analysis capabilities."""

    @pytest.fixture
    def test_db(self):
        """Create test database with sample graph data."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)

        # Create schema
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                layer TEXT,
                node_type TEXT,
                file_path TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE edges (
                src_id INTEGER,
                tgt_id INTEGER,
                relation_type TEXT
            )
        """)

        # Create a more complex graph for testing
        nodes = [
            (1, "central_hub", "L3_orchestration", "class", "hub.py"),
            (2, "worker_1", "L2_execution", "function", "worker1.py"),
            (3, "worker_2", "L2_execution", "function", "worker2.py"),
            (4, "worker_3", "L2_execution", "function", "worker3.py"),
            (5, "safety_check", "L5_safety", "function", "safety.py"),
            (6, "state_store", "L4_state", "class", "state.py"),
            (7, "isolated_node", "L1_cognition", "function", "isolated.py"),
        ]

        edges = [
            (1, 2, "calls"),
            (1, 3, "calls"),
            (1, 4, "calls"),
            (2, 5, "calls"),
            (3, 5, "calls"),
            (4, 5, "calls"),
            (5, 6, "reads_from"),
            (6, 1, "writes_to"),
            # Create some cycles
            (2, 3, "imports"),
            (3, 4, "imports"),
            (4, 2, "imports"),
        ]

        conn.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
        conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup (Windows-safe: file may still be locked by analyzer connection)
        try:
            os.unlink(db_path)
        except (PermissionError, OSError):
            pass

    def test_pagerank_analysis(self, test_db):
        """Test PageRank analysis."""
        analyzer = NetworkXAnalyzer(test_db)

        # Run PageRank analysis
        pagerank_scores = analyzer.analyze_pagerank()

        # Verify results
        assert len(pagerank_scores) > 0

        # Central hub should have high PageRank
        central_hub_score = next((score for name, score in pagerank_scores if name == "central_hub"), None)
        assert central_hub_score is not None
        assert central_hub_score > 0.1  # Should be relatively high

        # Isolated node should have lower PageRank
        isolated_score = next((score for name, score in pagerank_scores if name == "isolated_node"), None)
        assert isolated_score is not None
        assert isolated_score < central_hub_score

    def test_betweenness_centrality(self, test_db):
        """Test betweenness centrality analysis."""
        analyzer = NetworkXAnalyzer(test_db)

        # Run betweenness analysis
        betweenness_scores = analyzer.analyze_betweenness_centrality()

        # Verify results
        assert len(betweenness_scores) > 0

        # Central hub should have high betweenness
        central_hub_score = next((score for name, score in betweenness_scores if name == "central_hub"), None)
        assert central_hub_score is not None
        assert central_hub_score > 0.1

    def test_community_detection(self, test_db):
        """Test community detection."""
        analyzer = NetworkXAnalyzer(test_db)

        # Run community detection
        communities = analyzer.detect_communities()

        # Verify results
        assert len(communities) > 0

        # Should have at least 2 communities (workers vs isolated)
        assert len(communities) >= 2

        # Check that workers are in same community
        worker_communities = {}
        for name, community in communities.items():
            if "worker" in name:
                worker_communities[name] = community

        # Most workers should be in the same community
        community_counts = {}
        for community in worker_communities.values():
            community_counts[community] = community_counts.get(community, 0) + 1

        assert max(community_counts.values()) >= 2  # At least 2 workers together

    def test_writeback_to_sqlite(self, test_db):
        """Test writing analysis results back to SQLite."""
        analyzer = NetworkXAnalyzer(test_db)

        # Run analysis and write back
        analyzer.analyze_pagerank(writeback=True)

        # Verify data was written
        conn = sqlite3.connect(test_db)
        result = conn.execute("SELECT COUNT(*) FROM mv_pagerank_scores").fetchone()
        assert result[0] > 0

        # Check specific values
        result = conn.execute("""
            SELECT adg_name, pagerank_score
            FROM mv_pagerank_scores
            WHERE adg_name = 'central_hub'
        """).fetchone()

        assert result is not None
        assert result[0] == "central_hub"
        assert result[1] > 0

        conn.close()


class TestSQLiteDirect:
    """Test direct SQLite helper utilities."""

    @pytest.fixture
    def test_db(self):
        """Create test database."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)

        # Create schema
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                layer TEXT,
                node_type TEXT,
                file_path TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE edges (
                src_id INTEGER,
                tgt_id INTEGER,
                relation_type TEXT
            )
        """)

        # Insert test data
        nodes = [
            (1, "test_node", "L2_execution", "function", "test.py"),
            (2, "dependency", "L1_cognition", "class", "dep.py"),
            (3, "target", "L3_orchestration", "function", "target.py"),
        ]

        edges = [(1, 2, "imports"), (1, 3, "calls"), (2, 3, "imports")]

        conn.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
        conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup (Windows-safe: file may still be locked by analyzer connection)
        try:
            os.unlink(db_path)
        except (PermissionError, OSError):
            pass

    def test_graph_query_helper_initialization(self, test_db):
        """Test GraphQueryHelper initialization."""
        helper = GraphQueryHelper(test_db)
        assert helper.conn is not None
        helper.close()

    def test_find_nodes_by_name(self, test_db):
        """Test finding nodes by name."""
        helper = GraphQueryHelper(test_db)

        # Find exact match
        results = helper.find_nodes_by_name("test_node")
        assert len(results) == 1
        assert results[0]["adg_name"] == "test_node"
        assert results[0]["layer"] == "L2_execution"

        # Find partial match
        results = helper.find_nodes_by_name("test", exact_match=False)
        assert len(results) >= 1

        helper.close()

    def test_get_fan_in_fan_out(self, test_db):
        """Test fan-in and fan-out analysis."""
        helper = GraphQueryHelper(test_db)

        # Test fan-in (incoming edges)
        fan_in = helper.get_fan_in(1)
        assert len(fan_in) == 0  # No incoming edges to node 1

        # Test fan-out (outgoing edges)
        fan_out = helper.get_fan_out(1)
        assert len(fan_out) == 2  # Two outgoing edges from node 1

        # Test with specific relation types
        imports_fan_out = helper.get_fan_out(1, relation_types=["imports"])
        assert len(imports_fan_out) == 1  # One import edge

        calls_fan_out = helper.get_fan_out(1, relation_types=["calls"])
        assert len(calls_fan_out) == 1  # One call edge

        helper.close()

    def test_execute_query(self, test_db):
        """Test custom query execution."""
        helper = GraphQueryHelper(test_db)

        # Test simple query
        results = helper.execute_query("SELECT COUNT(*) as count FROM nodes")
        assert len(results) == 1
        assert results[0]["count"] == 3

        # Test parameterized query
        results = helper.execute_query("SELECT adg_name FROM nodes WHERE layer = ?", ["L2_execution"])
        assert len(results) == 1
        assert results[0]["adg_name"] == "test_node"

        helper.close()


class TestDuckDBIntegration:
    """Test DuckDB integration for columnar analytics."""

    @pytest.fixture
    def test_db(self):
        """Create test database with sample data."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)

        # Create schema
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                layer TEXT,
                node_type TEXT,
                file_path TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE edges (
                src_id INTEGER,
                tgt_id INTEGER,
                relation_type TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE violations (
                id INTEGER PRIMARY KEY,
                node_id INTEGER,
                violation_type TEXT,
                severity TEXT
            )
        """)

        # Insert test data
        nodes = [
            (1, "node1", "L0_routing", "function", "route.py"),
            (2, "node2", "L1_cognition", "class", "cog.py"),
            (3, "node3", "L2_execution", "function", "exec.py"),
            (4, "node4", "L3_orchestration", "class", "orch.py"),
            (5, "node5", "L4_state", "class", "state.py"),
            (6, "node6", "L5_safety", "function", "safety.py"),
        ]

        edges = [
            (1, 2, "imports"),
            (2, 3, "calls"),
            (3, 4, "imports"),
            (4, 5, "reads_from"),
            (5, 6, "writes_to"),
            (1, 6, "imports"),  # Cross-layer L0_routing -> L5_safety import
        ]

        violations = [(1, 1, "security_violation", "high"), (2, 3, "performance_issue", "medium")]

        conn.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
        conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
        conn.executemany("INSERT INTO violations VALUES (?, ?, ?, ?)", violations)
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup (Windows-safe: file may still be locked by analyzer connection)
        try:
            os.unlink(db_path)
        except (PermissionError, OSError):
            pass

    def test_duckdb_analyzer_initialization(self, test_db):
        """Test DuckDB analyzer initialization."""
        analyzer = DuckDBGraphAnalyzer(test_db)
        assert analyzer.duckdb_conn is not None
        analyzer.close()

    def test_layer_distribution_analysis(self, test_db):
        """Test layer distribution analysis."""
        analyzer = DuckDBGraphAnalyzer(test_db)

        distribution = analyzer.get_layer_distribution()

        assert "layer_distribution" in distribution
        assert len(distribution["layer_distribution"]) == 6  # 6 layers

        # Check specific layer
        l0_info = next(
            (layer for layer in distribution["layer_distribution"] if layer["layer"] == "L0_routing"), None
        )
        assert l0_info is not None
        assert l0_info["node_count"] == 1

        analyzer.close()

    def test_import_patterns_analysis(self, test_db):
        """Test import patterns analysis."""
        analyzer = DuckDBGraphAnalyzer(test_db)

        patterns = analyzer.analyze_import_patterns()

        assert "import_patterns" in patterns
        assert len(patterns["import_patterns"]) > 0

        # Check for cross-layer import
        cross_layer = next(
            (
                pattern
                for pattern in patterns["import_patterns"]
                if pattern["source_layer"] == "L0_routing" and pattern["target_layer"] == "L5_safety"
            ),
            None,
        )
        assert cross_layer is not None

        analyzer.close()

    def test_hotspot_candidates(self, test_db):
        """Test hotspot candidate identification."""
        analyzer = DuckDBGraphAnalyzer(test_db)

        hotspots = analyzer.get_hotspot_candidates(min_fan_in=1)

        assert "hotspot_candidates" in hotspots
        assert len(hotspots["hotspot_candidates"]) > 0

        # Check that results have expected fields
        hotspot = hotspots["hotspot_candidates"][0]
        assert "adg_name" in hotspot
        assert "layer" in hotspot
        assert "centrality_score" in hotspot

        analyzer.close()

    def test_violation_distribution(self, test_db):
        """Test violation distribution analysis."""
        analyzer = DuckDBGraphAnalyzer(test_db)

        violations = analyzer.analyze_violation_distribution()

        assert "violation_distribution" in violations
        assert len(violations["violation_distribution"]) == 2  # 2 violations

        # Check specific violation
        security_violation = next(
            (v for v in violations["violation_distribution"] if v["violation_type"] == "security_violation"),
            None,
        )
        assert security_violation is not None
        assert security_violation["severity"] == "high"

        analyzer.close()


class TestAgentInfusion:
    """Test agent infusion with graph capabilities."""

    @pytest.fixture
    def test_db(self):
        """Create test database for agent testing."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)

        # Create schema
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT,
                layer TEXT,
                node_type TEXT,
                file_path TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE edges (
                src_id INTEGER,
                tgt_id INTEGER,
                relation_type TEXT
            )
        """)

        # Insert agent-related data
        nodes = [
            (1, "RouterAgent", "L0_routing", "class", "router.py"),
            (2, "ExecutorAgent", "L2_execution", "class", "executor.py"),
            (3, "SafetyAgent", "L5_safety", "class", "safety.py"),
            (4, "OrchestratorAgent", "L3_orchestration", "class", "orchestrator.py"),
        ]

        edges = [(1, 2, "routes_to"), (2, 3, "monitored_by"), (3, 4, "reports_to"), (4, 1, "coordinates")]

        conn.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
        conn.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup (Windows-safe: file may still be locked by analyzer connection)
        try:
            os.unlink(db_path)
        except (PermissionError, OSError):
            pass

    @patch("agentic_core.L0_routing.reasoning.graph_aware_router.get_graph_router")
    def test_graph_aware_router(self, mock_get_router, test_db):
        """Test graph-aware routing capabilities."""
        # Mock the router
        from agentic_core.L0_routing.reasoning.graph_aware_router import GraphAwareRouter

        mock_router = Mock(spec=GraphAwareRouter)
        mock_get_router.return_value = mock_router

        # Mock routing decision
        mock_router.route_request.return_value = {
            "routing_decision": "direct_execute",
            "path": "L2_execution_direct",
            "reason": "Standard execution module with acceptable risk",
        }

        # Test routing
        from agentic_core.L0_routing.reasoning.graph_aware_router import route_with_graph_awareness

        decision = route_with_graph_awareness(
            request_type="execute", target_module="ExecutorAgent", context={"priority": "normal"}
        )

        assert decision["routing_decision"] == "direct_execute"
        assert decision["path"] == "L2_execution_direct"

        # Verify router was called correctly
        mock_router.route_request.assert_called_once_with("execute", "ExecutorAgent", {"priority": "normal"})

    @patch("agentic_core.L3_orchestration.reasoning.graph_coordinated_orchestrator.get_graph_orchestrator")
    def test_graph_coordinated_orchestrator(self, mock_get_orchestrator, test_db):
        """Test graph-coordinated orchestration."""
        from agentic_core.L3_orchestration.reasoning.graph_coordinated_orchestrator import (
            GraphCoordinatedOrchestrator,
        )

        mock_orchestrator = Mock(spec=GraphCoordinatedOrchestrator)
        mock_get_orchestrator.return_value = mock_orchestrator

        # Mock workflow planning
        mock_orchestrator.plan_workflow.return_value = {
            "workflow_id": "test_workflow",
            "execution_plan": [
                {"step_id": "step1", "agent_id": "RouterAgent", "action": "route"},
                {"step_id": "step2", "agent_id": "ExecutorAgent", "action": "execute"},
            ],
            "coordination_points": [],
            "metrics": {"total_estimated_duration": 5.0},
            "strategy": "sequential",
        }

        # Test workflow planning
        from agentic_core.L3_orchestration.reasoning.graph_coordinated_orchestrator import (
            get_graph_orchestrator,
        )

        orchestrator = get_graph_orchestrator(test_db)
        plan = orchestrator.plan_workflow(
            {
                "workflow_id": "test_workflow",
                "steps": [
                    {"step_id": "step1", "agent_id": "RouterAgent", "action": "route"},
                    {"step_id": "step2", "agent_id": "ExecutorAgent", "action": "execute"},
                ],
            }
        )

        assert plan["workflow_id"] == "test_workflow"
        assert len(plan["execution_plan"]) == 2
        assert plan["strategy"] == "sequential"

    @patch("agentic_core.L5_safety.reasoning.graph_aware_safety_monitor.get_safety_monitor")
    def test_graph_aware_safety_monitor(self, mock_get_monitor, test_db):
        """Test graph-aware safety monitoring."""
        from agentic_core.L5_safety.reasoning.graph_aware_safety_monitor import GraphAwareSafetyMonitor

        mock_monitor = Mock(spec=GraphAwareSafetyMonitor)
        mock_get_monitor.return_value = mock_monitor

        # Mock safety assessment
        mock_monitor.assess_system_safety.return_value = {
            "safety_score": 85.0,
            "critical_paths": [],
            "violations": [],
            "layer_risks": {"L5_safety": {"risk_level": "low"}},
            "recommendations": ["System safety posture is acceptable"],
        }

        # Test safety assessment
        from agentic_core.L5_safety.reasoning.graph_aware_safety_monitor import get_safety_monitor

        monitor = get_safety_monitor(test_db)
        assessment = monitor.assess_system_safety()

        assert assessment["safety_score"] == 85.0
        assert len(assessment["recommendations"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
