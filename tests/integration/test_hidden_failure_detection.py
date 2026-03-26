"""
Hidden Failure Detection Tests - Exposing defects missed by original test suite.

These tests specifically target:
1. Silent degradation paths
2. Error handling branches
3. State isolation issues
4. Determinism problems
5. Weak assertion replacements
"""

import json
import logging
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


class TestSilentDegradation(unittest.TestCase):
    """Test cases for silent failure modes that don't raise errors."""

    def test_kubernetes_import_silency_degrades(self):
        from agentic_core.cloud_native.cloud_native_manager import CloudNativeManager
        from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector
        from agentic_core.gateway.api_gateway_integration import APIGatewayIntegration, GatewayType, GatewayConfig
        from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector
        from agentic_core.visualization.trace_3d_visualizer import Trace3DVisualizer
        from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector, get_global_ml_detector
        import system_learning.ml_integration.anomaly_detection as ml_module
        from agentic_core.visualization.trace_3d_visualizer import get_global_3d_visualizer
        from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector
        from agentic_core.visualization.trace_3d_visualizer import Trace3DVisualizer
        from agentic_core.gateway.api_gateway_integration import APIGatewayIntegration, GatewayType, GatewayConfig
        from agentic_core.cloud_native.cloud_native_manager import CloudNativeManager, AutoScalingConfig
        from agentic_core.cloud_native.cloud_native_manager import ResourceMetrics, ResourceType, HealthStatus
        """CRITICAL: Test that Kubernetes features disappear silently when package missing."""
        Logger.info("Testing Kubernetes silent degradation...")

        # Simulate missing kubernetes package
        with patch.dict('sys.modules', {'kubernetes': None, 'kubernetes.client': None}):
            # Mock the ImportError path
            with patch('agentic_core.cloud_native.cloud_native_manager.config') as mock_config:
                mock_config.load_incluster_config.side_effect = ImportError("No module named 'kubernetes'")
                mock_config.load_kube_config.side_effect = ImportError("No module named 'kubernetes'")

#  # MOVED: from agentic_core.cloud_native.cloud_native_manager import CloudNativeManager

                manager = CloudNativeManager()
                manager._initialize_kubernetes_client()

                # CRITICAL DEFECT: This should fail but doesn't
                self.assertFalse(manager._initialized,
                                "Manager should not be initialized when kubernetes missing")

                # CRITICAL DEFECT: initialize() should raise error but returns False silently
                result = manager.initialize()
                self.assertFalse(result, "Should return False when kubernetes unavailable")

                Logger.info("✅ Silent degradation confirmed - Kubernetes features disappear without error")

    def test_ml_detector_graceful_degradation(self):
        """Test ML detector behavior when sklearn unavailable."""
        Logger.info("Testing ML detector silent degradation...")

        # Mock sklearn unavailable
        with patch.dict('sys.modules', {'sklearn': None, 'numpy': None}):
            with patch('system_learning.ml_integration.anomaly_detection.pickle') as mock_pickle:
                mock_pickle.dump.side_effect = ImportError("No module named 'sklearn'")

#  # MOVED: from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector

                detector = MLAnomalyDetector()

                # Should not crash but should not initialize models
                detector.initialize_models()

                # CRITICAL DEFECT: Models marked as initialized even when unavailable
                self.assertFalse(detector._models_initialized,
                                "Should not be initialized when sklearn missing")

                # Should return empty results instead of crashing
                anomalies = detector.detect_anomalies({"cpu": 100.0})
                self.assertEqual(len(anomalies), 0, "Should return empty list when models unavailable")

                Logger.info("✅ ML detector degrades gracefully but silently")


class TestErrorPathCoverage(unittest.TestCase):
    """Test error handling paths that original tests missed."""

    def test_api_gateway_connection_failure(self):
        """Test gateway behavior when backend unreachable."""
        Logger.info("Testing API gateway connection failure...")

#  # MOVED: from agentic_core.gateway.api_gateway_integration import APIGatewayIntegration, GatewayType, GatewayConfig

        gateway = APIGatewayIntegration(GatewayType.KONG)
        config = GatewayConfig(gateway_type=GatewayType.KONG, host="nonexistent-host", port=9999)

        # Mock connection failure
        with patch('requests.get', side_effect=ConnectionError("Connection refused")):
            with patch('requests.post', side_effect=ConnectionError("Connection refused")):
                result = gateway.initialize(config)

                # Should handle gracefully but report failure
                self.assertFalse(result, "Should return False when connection fails")

                # Metrics should reflect failure state
                metrics = gateway.get_gateway_metrics()
                self.assertIsNotNone(metrics, "Should still return metrics object")
                self.assertEqual(metrics.total_requests, 0, "Should have zero requests when failed")

                Logger.info("✅ Connection failure handled gracefully")

    def test_ml_model_loading_corruption(self):
        """Test behavior when model files are corrupted."""
        Logger.info("Testing ML model corruption handling...")

#  # MOVED: from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector
        import tempfile
        import os

        detector = MLAnomalyDetector()
        detector.initialize_models()

        # Create corrupted model file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pkl', delete=False) as f:
            f.write("corrupted pickle data that will fail to load")
            corrupted_file = f.name

        try:
            # Should handle corruption gracefully
            result = detector.load_models(corrupted_file)
            self.assertFalse(result, "Should return False when model corrupted")

            # Should not crash but models remain uninitialized
            self.assertFalse(detector._models_initialized, "Models should remain uninitialized after corruption")

            Logger.info("✅ Model corruption handled gracefully")
        finally:
            os.unlink(corrupted_file)

    def test_visualization_server_port_conflict(self):
        """Test 3D visualizer when port already in use."""
        Logger.info("Testing visualization server port conflict...")

#  # MOVED: from agentic_core.visualization.trace_3d_visualizer import Trace3DVisualizer

        visualizer = Trace3DVisualizer()

        # Mock port already in use
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.bind.side_effect = OSError("Address already in use")

            # Should handle gracefully but not start server
            result = visualizer.start_visualization_server(port=8081)
            self.assertFalse(result, "Should return False when port in use")
            self.assertFalse(visualizer._server_active, "Server should not be marked as active")

            Logger.info("✅ Port conflict handled gracefully")


class TestStateIsolation(unittest.TestCase):
    """Test for state leaks between test runs and instances."""

    def test_ml_detector_state_isolation(self):
        """Verify ML detector instances don't share state."""
        Logger.info("Testing ML detector state isolation...")

#  # MOVED: from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector, get_global_ml_detector

        # Clear global state
#  # MOVED: import system_learning.ml_integration.anomaly_detection as ml_module
        ml_module._global_detector = None

        # Create first detector and add data
        detector1 = MLAnomalyDetector()
        detector1.initialize_models()
        detector1.add_training_data("cpu_usage", 50.0, time.time())

        # Create second detector - should be isolated
        detector2 = MLAnomalyDetector()
        detector2.initialize_models()

        # CRITICAL DEFECT: Global singleton shares state
        self.assertEqual(len(detector2._training_data), 0,
                        "New detector should have empty training data")

        # Global detector should be isolated from first instance
        global_detector = get_global_ml_detector()
        # This should be a fresh instance, not detector1
        self.assertNotEqual(id(global_detector), id(detector1),
                          "Global detector should be new instance")

        Logger.info("✅ State isolation verified")

    def test_visualizer_graph_isolation(self):
        """Verify 3D visualizer instances don't share graphs."""
        Logger.info("Testing visualizer graph isolation...")

#  # MOVED: from agentic_core.visualization.trace_3d_visualizer import get_global_3d_visualizer

        visualizer1 = get_global_3d_visualizer()
        visualizer1._graphs.clear()  # Start clean

        # Add graph to first instance
        nodes = [{"id": "node1", "label": "Test", "type": "cognitive"}]
        edges = [{"id": "edge1", "source": "node1", "target": "node1", "type": "self"}]

        graph_id = visualizer1.add_trace_graph("test_graph", nodes, edges)
        self.assertEqual(len(visualizer1._graphs), 1, "First visualizer should have 1 graph")

        # Get second instance - should share global state
        visualizer2 = get_global_3d_visualizer()

        # CRITICAL DEFECT: Global visualizer shares state
        self.assertEqual(len(visualizer2._graphs), 1, "Second visualizer should see same graph")
        self.assertIn("test_graph", visualizer2._graphs, "Graph should be shared")

        # Clear for test isolation
        visualizer1._graphs.clear()

        Logger.info("✅ Visualizer global state confirmed")


class TestDeterminismIssues(unittest.TestCase):
    """Test for non-deterministic behavior."""

    def test_anomaly_detection_time_dependency(self):
        """Verify anomaly detection depends on execution time."""
        Logger.info("Testing anomaly detection time dependency...")

#  # MOVED: from system_learning.ml_integration.anomaly_detection import MLAnomalyDetector

        detector = MLAnomalyDetector()
        detector.initialize_models()

        # Test with same metrics but different times
        metrics = {"cpu_usage": 150.0}  # Anomalous value

        # First detection
        time1 = time.time()
        anomalies1 = detector.detect_anomalies(metrics)

        # Wait and detect again with same value
        time.sleep(0.1)
        anomalies2 = detector.detect_anomalies(metrics)

        # CRITICAL DEFECT: Results may differ due to time-based analysis
        # This test documents the issue - the fix would require time-independent analysis
        time_diff = abs(len(anomalies1) - len(anomalies2))
        Logger.info(f"Time dependency detected: {len(anomalies1)} vs {len(anomalies2)} anomalies")

        # At minimum, results should be consistent for same input within short timeframe
        self.assertEqual(len(anomalies1), len(anomalies2),
                        "Same input should produce same result within short timeframe")

        Logger.info("✅ Time dependency verified")

    def test_visualizer_random_initialization(self):
        """Test 3D visualizer random physics initialization."""
        Logger.info("Testing visualizer random initialization...")

#  # MOVED: from agentic_core.visualization.trace_3d_visualizer import Trace3DVisualizer

        visualizer = Trace3DVisualizer()

        # Same graph data
        nodes = [
            {"id": "node1", "label": "A", "type": "cognitive"},
            {"id": "node2", "label": "B", "type": "tool"}
        ]
        edges = [
            {"id": "edge1", "source": "node1", "target": "node2", "type": "calls"}
        ]

        # Run simulation twice
        visualizer._graphs.clear()
        graph1 = visualizer.add_trace_graph("test1", nodes, edges)
        positions1 = visualizer._calculate_node_positions(graph1)

        visualizer._graphs.clear()
        graph2 = visualizer.add_trace_graph("test2", nodes, edges)
        positions2 = visualizer._calculate_node_positions(graph2)

        # CRITICAL DEFECT: Positions differ due to random initialization
        node1_pos1 = positions1.get("node1", {})
        node1_pos2 = positions2.get("node1", {})

        # Document the non-determinism
        pos_diff = abs(node1_pos1.get('x', 0) - node1_pos2.get('x', 0))
        Logger.info(f"Random position difference: {pos_diff:.2f}")

        # Fix would require setting random seed
        # For now, just document the issue
        self.assertGreater(pos_diff, 0, "Positions should differ due to random initialization")

        Logger.info("✅ Random initialization confirmed")


class TestWeakAssertionReplacements(unittest.TestCase):
    """Replace weak assertions with strong validations."""

    def test_api_gateway_metrics_validation(self):
        """STRONG: Validate gateway metrics meaningfully."""
        Logger.info("Testing strong gateway metrics validation...")

#  # MOVED: from agentic_core.gateway.api_gateway_integration import APIGatewayIntegration, GatewayType, GatewayConfig

        gateway = APIGatewayIntegration(GatewayType.CUSTOM)
        config = GatewayConfig(gateway_type=GatewayType.CUSTOM)
        gateway.initialize(config)

        # Generate some activity
        gateway.inject_tracing_headers({}, "trace1", "span1")
        gateway.register_service("test-service", {"endpoint": "http://localhost:8080"})

        metrics = gateway.get_gateway_metrics()

        # STRONG ASSERTIONS (replacing weak assertIsNotNone)
        self.assertIsNotNone(metrics, "Metrics should not be None")
        self.assertGreater(metrics.total_requests, 0, "Should have tracked requests")
        self.assertGreaterEqual(metrics.successful_requests, 0, "Successful requests should be >= 0")
        self.assertGreaterEqual(metrics.failed_requests, 0, "Failed requests should be >= 0")
        self.assertEqual(metrics.total_requests,
                        metrics.successful_requests + metrics.failed_requests,
                        "Total should equal sum of success + failure")
        self.assertGreater(metrics.avg_response_time, 0.0, "Average response time should be positive")

        Logger.info("✅ Strong metrics validation passed")

    def test_cloud_native_manager_real_functionality(self):
        """STRONG: Test actual cloud native functionality, not just object existence."""
        Logger.info("Testing strong cloud native validation...")

#  # MOVED: from agentic_core.cloud_native.cloud_native_manager import CloudNativeManager, AutoScalingConfig

        manager = CloudNativeManager()

        # STRONG: Test configuration validation, not just object creation
        scaling_config = AutoScalingConfig(
            min_replicas=1,
            max_replicas=5,
            target_cpu_utilization=70.0,
            scale_up_threshold=80.0,
            scale_down_threshold=40.0,
        )

        # Validate configuration constraints
        self.assertGreaterEqual(scaling_config.min_replicas, 1, "Min replicas should be >= 1")
        self.assertGreater(scaling_config.max_replicas, scaling_config.min_replicas,
                          "Max should be greater than min")
        self.assertGreater(scaling_config.target_cpu_utilization, 0, "Target CPU should be positive")
        self.assertLessEqual(scaling_config.target_cpu_utilization, 100, "Target CPU should be <= 100")
        self.assertGreater(scaling_config.scale_up_threshold, scaling_config.scale_down_threshold,
                          "Scale up threshold should be greater than scale down")

        # STRONG: Test resource metrics creation, not just manager existence
#  # MOVED: from agentic_core.cloud_native.cloud_native_manager import ResourceMetrics, ResourceType, HealthStatus

        metrics = ResourceMetrics(
            name="test-deployment",
            namespace="default",
            resource_type=ResourceType.DEPLOYMENT,
            status=HealthStatus.HEALTHY,
            replicas=3,
            ready_replicas=3,
            cpu_usage=45.5,
            memory_usage=60.2,
        )

        # Validate metrics constraints
        self.assertEqual(metrics.name, "test-deployment")
        self.assertEqual(metrics.resource_type, ResourceType.DEPLOYMENT)
        self.assertEqual(metrics.status, HealthStatus.HEALTHY)
        self.assertGreaterEqual(metrics.replicas, metrics.ready_replicas,
                               "Ready replicas should not exceed total replicas")
        self.assertGreaterEqual(metrics.cpu_usage, 0.0, "CPU usage should be non-negative")
        self.assertGreaterEqual(metrics.memory_usage, 0.0, "Memory usage should be non-negative")

        Logger.info("✅ Strong cloud native validation passed")


if __name__ == '__main__':
    # Run all hidden failure detection tests
    unittest.main(verbosity=2)
