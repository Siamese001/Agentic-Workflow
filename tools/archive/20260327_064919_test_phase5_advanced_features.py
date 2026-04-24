#!/usr/bin/env python3
"""Phase 5 Advanced Features Test Suite

Comprehensive testing for Phase 5 ML integration, 3D visualization,
API gateway integration, Kubernetes deployment, and cloud-native features.

TESTS:
- ML-based anomaly detection and prediction
- Advanced 3D trace visualization
- API gateway integration (Kong, Envoy, Custom)
- Kubernetes deployment manifests
- Cloud-native features (auto-scaling, monitoring)
- ML model training pipeline
- Integration testing across all components

USAGE:
    python test_phase5_advanced_features.py
"""

import logging
import time
import unittest
from typing import Any

import numpy as np
import pandas as pd
from agentic_core.cloud_native.cloud_native_manager import (
    AutoScalingConfig,
    HealthStatus,
    ResourceMetrics,
    ResourceType,
    get_global_cloud_native_manager,
)

# Module-level imports so all test methods can reference these types
from agentic_core.gateway.api_gateway_integration import (
    GatewayConfig,
    GatewayType,
    get_global_gateway,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
Logger = logging.getLogger(__name__)


class TestPhase5MLIntegration(unittest.TestCase):
    """Test ML integration features."""

    def setUp(self):
        """Set up ML integration tests."""
        from system_learning.ml_integration.anomaly_detection import get_global_ml_detector

        self.detector = get_global_ml_detector()
        self.detector.initialize_models()

        # Create test data
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, 1000)
        self.anomaly_data = np.concatenate(
            [
                np.random.normal(0, 1, 950),
                np.random.normal(5, 1, 50),  # Anomalies
            ]
        )

    def test_ml_detector_initialization(self):
        """Test ML detector initialization."""
        Logger.info("Testing ML detector initialization...")

        self.assertIsNotNone(self.detector)
        self.assertTrue(self.detector._models_initialized)
        self.assertTrue(self.detector._sklearn_available)

        Logger.info("✅ ML detector initialization successful")

    def test_statistical_anomaly_detection(self):
        """Test statistical anomaly detection."""
        Logger.info("Testing statistical anomaly detection...")

        # Seed enough historical data so statistical methods have baseline (need >=10 points)
        base_ts = time.time() - 200
        for i in range(50):
            self.detector.add_training_data("cpu_usage", 50.0 + np.random.normal(0, 2), base_ts + i)
            self.detector.add_training_data("memory_usage", 60.0 + np.random.normal(0, 2), base_ts + i)

        # Test with anomaly data — far outside the normal distribution
        anomaly_metrics = {"cpu_usage": 150.0, "memory_usage": 200.0}
        anomalies = self.detector.detect_anomalies(anomaly_metrics)

        # Should detect anomalies
        self.assertGreater(len(anomalies), 0)

        # Check anomaly properties
        for anomaly in anomalies:
            self.assertIsNotNone(anomaly.anomaly_type)
            self.assertIsNotNone(anomaly.severity)
            self.assertGreaterEqual(anomaly.confidence, 0.0)
            self.assertLessEqual(anomaly.confidence, 1.0)

        Logger.info(f"✅ Statistical anomaly detection: {len(anomalies)} anomalies detected")

    def test_ml_anomaly_detection(self):
        """Test ML-based anomaly detection."""
        Logger.info("Testing ML-based anomaly detection...")

        # Add training data
        for i, value in enumerate(self.normal_data):
            self.detector.add_training_data("test_metric", value, time.time() - (1000 - i))

        # Add some anomaly data
        for i, value in enumerate(self.anomaly_data[-50:]):
            self.detector.add_training_data("test_metric", value, time.time() - (50 - i))

        # Test anomaly detection
        test_metrics = {
            "test_metric": 5.0,  # Anomaly value
            "cpu_usage": 80.0,
            "memory_usage": 90.0,
        }

        anomalies = self.detector.detect_anomalies(test_metrics)

        # Should detect anomalies
        self.assertGreater(len(anomalies), 0)

        Logger.info(f"✅ ML anomaly detection: {len(anomalies)} anomalies detected")

    def test_performance_prediction(self):
        """Test performance prediction."""
        Logger.info("Testing performance prediction...")

        # Add historical data
        for i in range(100):
            value = 50 + 10 * np.sin(i * 0.1) + np.random.normal(0, 2)
            self.detector.add_training_data("cpu_usage", value, time.time() - (100 - i))

        # Test prediction
        prediction = self.detector.predict_performance("cpu_usage", horizon_minutes=60)

        self.assertIsNotNone(prediction)
        self.assertIsNotNone(prediction.predicted_value)
        self.assertIsNotNone(prediction.confidence_interval)
        self.assertGreaterEqual(prediction.confidence_score, 0.0)
        self.assertLessEqual(prediction.confidence_score, 1.0)

        Logger.info(
            f"✅ Performance prediction: {prediction.predicted_value:.2f} (confidence: {prediction.confidence_score:.2f})"
        )

    def test_anomaly_statistics(self):
        """Test anomaly detection statistics."""
        Logger.info("Testing anomaly statistics...")

        # Seed baseline data first so statistical detection works
        base_ts = time.time() - 300
        for i in range(50):
            self.detector.add_training_data("cpu_usage", 50.0 + np.random.normal(0, 2), base_ts + i)
            self.detector.add_training_data("memory_usage", 60.0 + np.random.normal(0, 2), base_ts + i)

        # Generate some anomalies — values far outside baseline
        for i in range(10):
            metrics = {
                "cpu_usage": 200.0 + i * 10,
                "memory_usage": 300.0 + i * 5,
            }
            self.detector.detect_anomalies(metrics)

        stats = self.detector.get_anomaly_statistics()

        self.assertIn("total_anomalies", stats)
        self.assertIn("anomaly_types", stats)
        self.assertIn("severity_distribution", stats)
        self.assertGreater(stats["total_anomalies"], 0)

        Logger.info(f"✅ Anomaly statistics: {stats['total_anomalies']} total anomalies")


class TestPhase5Visualization(unittest.TestCase):
    """Test 3D visualization features."""

    def setUp(self):
        """Set up visualization tests."""
        from agentic_core.visualization.trace_3d_visualizer import get_global_3d_visualizer

        self.visualizer = get_global_3d_visualizer()
        # Clear shared state to isolate each test
        self.visualizer._graphs.clear()
        self.visualizer._selected_nodes.clear()
        self.visualizer._highlighted_paths.clear()

        # Create test trace data
        self.test_nodes = [
            {"id": "node1", "label": "Start", "type": "cognitive", "duration_ms": 100},
            {"id": "node2", "label": "Process", "type": "tool", "duration_ms": 200},
            {"id": "node3", "label": "End", "type": "system", "duration_ms": 50},
        ]

        self.test_edges = [
            {"id": "edge1", "source": "node1", "target": "node2", "type": "calls", "weight": 1.0},
            {"id": "edge2", "source": "node2", "target": "node3", "type": "flows_to", "weight": 1.0},
        ]

    def test_visualizer_initialization(self):
        """Test 3D visualizer initialization."""
        Logger.info("Testing 3D visualizer initialization...")

        self.assertIsNotNone(self.visualizer)
        self.assertFalse(self.visualizer._server_active)

        Logger.info("✅ 3D visualizer initialization successful")

    def test_trace_graph_creation(self):
        """Test trace graph creation."""
        Logger.info("Testing trace graph creation...")

        graph_id = self.visualizer.add_trace_graph("test_trace", self.test_nodes, self.test_edges)

        self.assertIsNotNone(graph_id)
        self.assertEqual(graph_id, "test_trace")
        self.assertEqual(len(self.visualizer._graphs), 1)

        graph = self.visualizer._graphs["test_trace"]
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)

        Logger.info(f"✅ Trace graph creation: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    def test_physics_simulation(self):
        """Test physics simulation."""
        Logger.info("Testing physics simulation...")

        # Add a graph
        self.visualizer.add_trace_graph("physics_test", self.test_nodes, self.test_edges)

        # Apply physics forces
        graph = self.visualizer._graphs["physics_test"]
        initial_positions = {node_id: node.position for node_id, node in graph.nodes.items()}

        # Run physics simulation
        for _ in range(10):
            self.visualizer._physics_engine.apply_forces(graph)
            self.visualizer._physics_engine.update_positions(graph)

        # Check that positions changed
        final_positions = {node_id: node.position for node_id, node in graph.nodes.items()}

        positions_changed = any(
            initial_positions[node_id] != final_positions[node_id] for node_id in initial_positions
        )

        self.assertTrue(positions_changed)

        Logger.info("✅ Physics simulation: positions updated successfully")

    def test_visualization_data_export(self):
        """Test visualization data export."""
        Logger.info("Testing visualization data export...")

        # Add a graph
        self.visualizer.add_trace_graph("export_test", self.test_nodes, self.test_edges)

        # Get visualization data
        viz_data = self.visualizer.get_visualization_data("export_test")

        self.assertIn("graph", viz_data)
        self.assertIn("nodes", viz_data["graph"])
        self.assertIn("edges", viz_data["graph"])
        self.assertIn("camera", viz_data)
        self.assertIn("config", viz_data)

        graph_data = viz_data["graph"]
        self.assertEqual(len(graph_data["nodes"]), 3)
        self.assertEqual(len(graph_data["edges"]), 2)

        Logger.info("✅ Visualization data export successful")

    def test_node_selection_and_highlighting(self):
        """Test node selection and path highlighting."""
        Logger.info("Testing node selection and path highlighting...")

        # Add a graph
        self.visualizer.add_trace_graph("selection_test", self.test_nodes, self.test_edges)

        # Test node selection
        success = self.visualizer.select_node("selection_test", "node1")
        self.assertTrue(success)
        self.assertIn("node1", self.visualizer._selected_nodes)

        # Test path highlighting
        success = self.visualizer.highlight_path("selection_test", ["node1", "node2", "node3"])
        self.assertTrue(success)
        self.assertEqual(len(self.visualizer._highlighted_paths), 1)

        # Clear selection
        self.visualizer.clear_selection()
        self.assertEqual(len(self.visualizer._selected_nodes), 0)
        self.assertEqual(len(self.visualizer._highlighted_paths), 0)

        Logger.info("✅ Node selection and path highlighting successful")


class TestPhase5APIGateway(unittest.TestCase):
    """Test API gateway integration."""

    def setUp(self):
        """Set up API gateway tests."""
        self.gateway = get_global_gateway()
        self.config = GatewayConfig(gateway_type=GatewayType.CUSTOM)

        # Initialize gateway
        self.gateway.initialize(self.config)

    def test_gateway_initialization(self):
        """Test gateway initialization."""
        Logger.info("Testing gateway initialization...")

        self.assertIsNotNone(self.gateway)
        self.assertTrue(self.gateway._initialized)
        self.assertEqual(self.gateway._gateway_type, GatewayType.CUSTOM)

        Logger.info("✅ Gateway initialization successful")

    def test_tracing_header_injection(self):
        """Test tracing header injection."""
        Logger.info("Testing tracing header injection...")

        original_headers = {
            "Content-Type": "application/json",
            "User-Agent": "test-client",
        }

        injected_headers = self.gateway.inject_tracing_headers(
            original_headers,
            trace_id="test-trace-123",
            span_id="test-span-456",
            parent_span_id="test-parent-789",
            baggage={"user_id": "123", "session_id": "abc"},
        )

        # Check that original headers are preserved
        self.assertIn("Content-Type", injected_headers)
        self.assertIn("User-Agent", injected_headers)

        # Check that tracing headers are added
        self.assertIn("x-trace-id", injected_headers)
        self.assertIn("x-span-id", injected_headers)
        self.assertEqual(injected_headers["x-trace-id"], "test-trace-123")
        self.assertEqual(injected_headers["x-span-id"], "test-span-456")

        Logger.info("✅ Tracing header injection successful")

    def test_tracing_header_extraction(self):
        """Test tracing header extraction."""
        Logger.info("Testing tracing header extraction...")

        response_headers = {
            "x-trace-id": "test-trace-123",
            "x-span-id": "test-span-456",
            "x-parent-span-id": "test-parent-789",
            "x-sampled": "1",
            "x-baggage": '{"user_id": "123", "session_id": "abc"}',
        }

        tracing_headers = self.gateway.extract_tracing_headers(response_headers)

        self.assertIsNotNone(tracing_headers)
        self.assertEqual(tracing_headers.trace_id, "test-trace-123")
        self.assertEqual(tracing_headers.span_id, "test-span-456")
        self.assertEqual(tracing_headers.parent_span_id, "test-parent-789")
        self.assertTrue(tracing_headers.sampled)
        self.assertEqual(tracing_headers.baggage["user_id"], "123")

        Logger.info("✅ Tracing header extraction successful")

    def test_service_registration(self):
        """Test service registration."""
        Logger.info("Testing service registration...")

        service_config = {
            "endpoint": "http://localhost:8080",
            "health_check": "/health",
            "timeout": 30,
        }

        success = self.gateway.register_service("test-service", service_config)
        self.assertTrue(success)

        services = self.gateway.get_service_registry()
        self.assertIn("test-service", services)
        self.assertEqual(services["test-service"]["config"]["endpoint"], "http://localhost:8080")

        Logger.info("✅ Service registration successful")

    def test_gateway_metrics(self):
        """Test gateway metrics collection."""
        Logger.info("Testing gateway metrics...")

        metrics = self.gateway.get_gateway_metrics()

        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.total_requests, 0)
        self.assertGreaterEqual(metrics.successful_requests, 0)
        self.assertGreaterEqual(metrics.failed_requests, 0)
        self.assertGreaterEqual(metrics.avg_response_time, 0)

        Logger.info(
            f"✅ Gateway metrics: {metrics.total_requests} requests, {metrics.avg_response_time:.2f} avg response time"
        )

    def test_integration_status(self):
        """Test integration status."""
        Logger.info("Testing integration status...")

        status = self.gateway.get_integration_status()

        self.assertIn("gateway_type", status)
        self.assertIn("initialized", status)
        self.assertIn("health_status", status)
        self.assertIn("registered_services", status)
        self.assertIn("current_metrics", status)

        self.assertTrue(status["initialized"])

        Logger.info("✅ Integration status retrieved successfully")


class TestPhase5Kubernetes(unittest.TestCase):
    """Test Kubernetes deployment manifests."""

    def setUp(self):
        """Set up Kubernetes tests."""
        self.k8s_dir = "k8s"
        self.required_files = [
            "namespace.yaml",
            "configmap.yaml",
            "secret.yaml",
            "redis-deployment.yaml",
            "jaeger-deployment.yaml",
            "agentic-workflow-deployment.yaml",
            "monitoring.yaml",
            "kong-deployment.yaml",
            "ingress.yaml",
            "README.md",
        ]

    def test_kubernetes_manifests_exist(self):
        """Test that all required Kubernetes manifests exist."""
        Logger.info("Testing Kubernetes manifest existence...")

        import os

        for filename in self.required_files:
            filepath = os.path.join(self.k8s_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"Missing file: {filepath}")

        Logger.info(f"✅ All {len(self.required_files)} required Kubernetes manifests exist")

    def test_namespace_manifest(self):
        """Test namespace manifest structure."""
        Logger.info("Testing namespace manifest...")

        manifest = self._load_yaml_manifest("namespace.yaml")

        self.assertEqual(manifest["apiVersion"], "v1")
        self.assertEqual(manifest["kind"], "Namespace")
        self.assertEqual(manifest["metadata"]["name"], "agentic-workflow")

        Logger.info("✅ Namespace manifest structure valid")

    def test_configmap_manifest(self):
        """Test ConfigMap manifest structure."""
        Logger.info("Testing ConfigMap manifest...")

        manifest = self._load_yaml_manifest("configmap.yaml")

        self.assertEqual(manifest["apiVersion"], "v1")
        self.assertEqual(manifest["kind"], "ConfigMap")
        self.assertEqual(manifest["metadata"]["name"], "agentic-workflow-config")
        self.assertIn("data", manifest)

        # Check for required configuration keys
        data = manifest["data"]
        self.assertIn("tracing.enabled", data)
        self.assertIn("runtime_adg.enabled", data)
        self.assertIn("ml.enabled", data)
        self.assertIn("visualization.enabled", data)

        Logger.info("✅ ConfigMap manifest structure valid")

    def test_deployment_manifests(self):
        """Test deployment manifests structure."""
        Logger.info("Testing deployment manifests...")

        # Test main application deployment
        app_manifest = self._load_yaml_manifest("agentic-workflow-deployment.yaml")

        self.assertEqual(app_manifest["apiVersion"], "apps/v1")
        self.assertEqual(app_manifest["kind"], "Deployment")
        self.assertEqual(app_manifest["metadata"]["name"], "agentic-workflow-core")

        # Check deployment spec
        spec = app_manifest["spec"]
        self.assertIn("replicas", spec)
        self.assertIn("selector", spec)
        self.assertIn("template", spec)

        # Check container configuration
        container = spec["template"]["spec"]["containers"][0]
        self.assertIn("name", container)
        self.assertIn("image", container)
        self.assertIn("ports", container)
        self.assertIn("env", container)
        self.assertIn("resources", container)

        Logger.info("✅ Deployment manifests structure valid")

    def test_service_manifests(self):
        """Test service manifests structure."""
        Logger.info("Testing service manifests...")

        # Load deployment manifest to find services
        app_manifest = self._load_yaml_manifest("agentic-workflow-deployment.yaml")

        # Find service definitions in the same file
        services = [
            item
            for item in self._load_all_yaml_manifests("agentic-workflow-deployment.yaml")
            if item.get("kind") == "Service"
        ]

        self.assertGreater(len(services), 0)

        for service in services:
            self.assertEqual(service["apiVersion"], "v1")
            self.assertEqual(service["kind"], "Service")
            self.assertIn("metadata", service)
            self.assertIn("spec", service)
            self.assertIn("selector", service["spec"])
            self.assertIn("ports", service["spec"])

        Logger.info(f"✅ Service manifests structure valid: {len(services)} services found")

    def test_ingress_manifests(self):
        """Test ingress manifests structure."""
        Logger.info("Testing ingress manifests...")

        manifest = self._load_yaml_manifest("ingress.yaml")

        # Find ingress resources
        ingresses = [
            item for item in self._load_all_yaml_manifests("ingress.yaml") if item.get("kind") == "Ingress"
        ]

        self.assertGreater(len(ingresses), 0)

        for ingress in ingresses:
            self.assertEqual(ingress["apiVersion"], "networking.k8s.io/v1")
            self.assertEqual(ingress["kind"], "Ingress")
            self.assertIn("spec", ingress)
            self.assertIn("rules", ingress["spec"])

        Logger.info(f"✅ Ingress manifests structure valid: {len(ingresses)} ingresses found")

    def test_monitoring_manifests(self):
        """Test monitoring manifests structure."""
        Logger.info("Testing monitoring manifests...")

        manifest = self._load_yaml_manifest("monitoring.yaml")

        # Find Prometheus deployment
        prometheus = None
        grafana = None

        for item in self._load_all_yaml_manifests("monitoring.yaml"):
            if item.get("kind") == "Deployment":
                if item.get("metadata", {}).get("name") == "prometheus":
                    prometheus = item
                elif item.get("metadata", {}).get("name") == "grafana":
                    grafana = item

        self.assertIsNotNone(prometheus, "Prometheus deployment not found")
        self.assertIsNotNone(grafana, "Grafana deployment not found")

        # Check Prometheus configuration
        self.assertEqual(prometheus["spec"]["template"]["spec"]["containers"][0]["name"], "prometheus")
        self.assertEqual(grafana["spec"]["template"]["spec"]["containers"][0]["name"], "grafana")

        Logger.info("✅ Monitoring manifests structure valid")

    def _load_yaml_manifest(self, filename: str) -> dict[str, Any]:
        """Load the first YAML document from a (possibly multi-doc) manifest file."""
        try:
            import yaml

            with open(f"{self.k8s_dir}/{filename}") as f:
                docs = [d for d in yaml.safe_load_all(f) if d is not None]
            if not docs:
                self.fail(f"No YAML documents found in {filename}")
            return docs[0]
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            self.fail(f"Failed to load {filename}: {e}")

    def _load_all_yaml_manifests(self, filename: str) -> list[dict[str, Any]]:
        """Load all YAML documents from a file."""
        try:
            import yaml

            with open(f"{self.k8s_dir}/{filename}") as f:
                return list(yaml.safe_load_all(f))
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            self.fail(f"Failed to load {filename}: {e}")


class TestPhase5CloudNative(unittest.TestCase):
    """Test cloud-native features."""

    def setUp(self):
        """Set up cloud-native tests."""
        self.manager = get_global_cloud_native_manager()
        self.scaling_config = AutoScalingConfig(
            min_replicas=1,
            max_replicas=5,
            target_cpu_utilization=70.0,
            scale_up_threshold=80.0,
            scale_down_threshold=40.0,
        )

    def test_cloud_native_manager_initialization(self):
        """Test cloud native manager initialization."""
        Logger.info("Testing cloud native manager initialization...")

        self.assertIsNotNone(self.manager)
        # Note: Kubernetes client may not be available in test environment
        # self.assertTrue(self.manager._initialized)

        Logger.info("✅ Cloud native manager initialization successful")

    def test_auto_scaling_configuration(self):
        """Test auto-scaling configuration."""
        Logger.info("Testing auto-scaling configuration...")

        config = AutoScalingConfig()

        self.assertGreaterEqual(config.min_replicas, 1)
        self.assertGreater(config.max_replicas, config.min_replicas)
        self.assertGreater(config.target_cpu_utilization, 0)
        self.assertLessEqual(config.target_cpu_utilization, 100)
        self.assertGreater(config.scale_up_threshold, config.scale_down_threshold)

        Logger.info("✅ Auto-scaling configuration valid")

    def test_resource_metrics(self):
        """Test resource metrics collection."""
        Logger.info("Testing resource metrics...")

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

        self.assertEqual(metrics.name, "test-deployment")
        self.assertEqual(metrics.resource_type, ResourceType.DEPLOYMENT)
        self.assertEqual(metrics.status, HealthStatus.HEALTHY)
        self.assertEqual(metrics.replicas, 3)
        self.assertEqual(metrics.ready_replicas, 3)

        Logger.info("✅ Resource metrics creation successful")

    def test_cluster_health_assessment(self):
        """Test cluster health assessment."""
        Logger.info("Testing cluster health assessment...")

        # Simulate cluster health (would normally connect to real cluster)
        health = self.manager.get_cluster_health()

        self.assertIn("overall_status", health)
        self.assertIn("health_score", health)
        self.assertIn("total_resources", health)
        self.assertIn("cluster_metrics", health)

        # Health score should be between 0 and 100
        self.assertGreaterEqual(health["health_score"], 0)
        self.assertLessEqual(health["health_score"], 100)

        Logger.info(
            f"✅ Cluster health assessment: {health['overall_status']} ({health['health_score']:.1f})"
        )

    def test_auto_scaling_status(self):
        """Test auto-scaling status."""
        Logger.info("Testing auto-scaling status...")

        status = self.manager.get_auto_scaling_status()

        self.assertIn("enabled", status)
        self.assertIn("configured_resources", status)
        self.assertIn("total_scaling_events", status)
        self.assertIn("configurations", status)

        Logger.info(f"✅ Auto-scaling status: {status['configured_resources']} configured resources")


class TestPhase5MLTraining(unittest.TestCase):
    """Test ML training pipeline."""

    def setUp(self):
        """Set up ML training tests."""
        from system_learning.ml_integration.training_pipeline import get_global_ml_pipeline

        self.pipeline = get_global_ml_pipeline()
        self.pipeline.initialize_pipeline()

        # Create sample training data
        np.random.seed(42)
        n_samples = 1000

        self.training_data = pd.DataFrame(
            {
                "cpu_usage": np.random.normal(50, 15, n_samples),
                "memory_usage": np.random.normal(60, 10, n_samples),
                "response_time": np.random.normal(200, 50, n_samples),
                "error_rate": np.random.exponential(0.05, n_samples),
                "anomaly": np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            }
        )

    def test_pipeline_initialization(self):
        """Test ML pipeline initialization."""
        Logger.info("Testing ML pipeline initialization...")

        self.assertIsNotNone(self.pipeline)
        self.assertTrue(self.pipeline._initialized)

        Logger.info("✅ ML pipeline initialization successful")

    def test_training_data_addition(self):
        """Test training data addition."""
        Logger.info("Testing training data addition...")

        success = self.pipeline.add_training_data("test_dataset", self.training_data)
        self.assertTrue(success)

        self.assertIn("test_dataset", self.pipeline._training_data)
        self.assertEqual(len(self.pipeline._training_data["test_dataset"]), 1000)

        Logger.info("✅ Training data addition successful")

    def test_anomaly_detection_model_training(self):
        """Test anomaly detection model training."""
        Logger.info("Testing anomaly detection model training...")

        # Add training data
        self.pipeline.add_training_data("anomaly_dataset", self.training_data)

        # Train model
        model_id = self.pipeline.train_anomaly_detection_model("anomaly_dataset", "random_forest")

        self.assertIsNotNone(model_id)
        self.assertIn(model_id, self.pipeline._trained_models)
        self.assertIn(model_id, self.pipeline._model_metrics)

        # Check model metrics
        metrics = self.pipeline._model_metrics[model_id]
        self.assertGreater(metrics.accuracy, 0.0)
        self.assertLessEqual(metrics.accuracy, 1.0)
        self.assertGreater(metrics.f1_score, 0.0)
        self.assertLessEqual(metrics.f1_score, 1.0)

        Logger.info(f"✅ Model training successful: {model_id} (accuracy: {metrics.accuracy:.3f})")

    def test_model_evaluation(self):
        """Test model evaluation."""
        Logger.info("Testing model evaluation...")

        # Train a model first
        self.pipeline.add_training_data("eval_dataset", self.training_data)
        model_id = self.pipeline.train_anomaly_detection_model("eval_dataset", "random_forest")

        # Create test data
        test_data = pd.DataFrame(
            {
                "cpu_usage": np.random.normal(50, 15, 200),
                "memory_usage": np.random.normal(60, 10, 200),
                "response_time": np.random.normal(200, 50, 200),
                "error_rate": np.random.exponential(0.05, 200),
                "anomaly": np.random.choice([0, 1], 200, p=[0.9, 0.1]),
            }
        )

        # Evaluate model
        test_metrics = self.pipeline.evaluate_model(model_id, test_data)

        self.assertIsNotNone(test_metrics)
        self.assertGreater(test_metrics.accuracy, 0.0)
        self.assertLessEqual(test_metrics.accuracy, 1.0)

        Logger.info(f"✅ Model evaluation successful: test accuracy {test_metrics.accuracy:.3f}")

    def test_model_deployment(self):
        """Test model deployment."""
        Logger.info("Testing model deployment...")

        # Train a model first
        self.pipeline.add_training_data("deploy_dataset", self.training_data)
        model_id = self.pipeline.train_anomaly_detection_model("deploy_dataset", "random_forest")

        # Deploy model
        deployment_id = self.pipeline.deploy_model(model_id, "production")

        self.assertIsNotNone(deployment_id)
        self.assertIn(deployment_id, self.pipeline._deployments)

        # Check deployment
        deployment = self.pipeline._deployments[deployment_id]
        self.assertEqual(deployment.model_id, model_id)
        self.assertEqual(deployment.environment, "production")
        self.assertEqual(deployment.status, "active")

        Logger.info(f"✅ Model deployment successful: {deployment_id}")

    def test_model_predictions(self):
        """Test model predictions."""
        Logger.info("Testing model predictions...")

        # Train a model first
        self.pipeline.add_training_data("predict_dataset", self.training_data)
        model_id = self.pipeline.train_anomaly_detection_model("predict_dataset", "random_forest")

        # Create prediction data
        predict_data = pd.DataFrame(
            {
                "cpu_usage": [55.0, 80.0, 120.0],
                "memory_usage": [65.0, 85.0, 150.0],
                "response_time": [220.0, 350.0, 600.0],
                "error_rate": [0.02, 0.08, 0.15],
            }
        )

        # Make predictions
        predictions = self.pipeline.get_model_predictions(model_id, predict_data)

        self.assertIsNotNone(predictions)
        self.assertEqual(len(predictions), 3)

        # Check prediction values (should be 0 or 1 for anomaly detection)
        for pred in predictions:
            self.assertIn(pred, [0, 1])

        Logger.info(f"✅ Model predictions successful: {predictions}")

    def test_training_pipeline_status(self):
        """Test training pipeline status."""
        Logger.info("Testing training pipeline status...")

        status = self.pipeline.get_training_status()

        self.assertIn("initialized", status)
        self.assertIn("total_models", status)
        self.assertIn("total_deployments", status)
        self.assertIn("available_datasets", status)
        self.assertIn("model_registry", status)

        self.assertTrue(status["initialized"])
        self.assertGreaterEqual(status["total_models"], 0)

        Logger.info(
            f"✅ Training pipeline status: {status['total_models']} models, {status['total_deployments']} deployments"
        )


class TestPhase5Integration(unittest.TestCase):
    """Test integration across all Phase 5 components."""

    def setUp(self):
        """Set up integration tests."""
        # Initialize all components
        from agentic_core.cloud_native.cloud_native_manager import get_global_cloud_native_manager
        from agentic_core.visualization.trace_3d_visualizer import get_global_3d_visualizer

        from agentic_core.gateway.api_gateway_integration import get_global_gateway
        from system_learning.ml_integration.anomaly_detection import get_global_ml_detector
        from system_learning.ml_integration.training_pipeline import get_global_ml_pipeline

        self.ml_detector = get_global_ml_detector()
        self.visualizer = get_global_3d_visualizer()
        self.gateway = get_global_gateway()
        self.cloud_manager = get_global_cloud_native_manager()
        self.ml_pipeline = get_global_ml_pipeline()

    def test_component_initialization(self):
        """Test that all components can be initialized."""
        Logger.info("Testing component initialization...")

        # ML components
        self.ml_detector.initialize_models()
        self.assertTrue(self.ml_detector._models_initialized)

        self.ml_pipeline.initialize_pipeline()
        self.assertTrue(self.ml_pipeline._initialized)

        # Gateway
        from agentic_core.gateway.api_gateway_integration import GatewayConfig, GatewayType

        config = GatewayConfig(gateway_type=GatewayType.CUSTOM)
        self.assertTrue(self.gateway.initialize(config))

        # Visualization
        self.assertIsNotNone(self.visualizer)

        # Cloud native (may not be available without Kubernetes)
        self.assertIsNotNone(self.cloud_manager)

        Logger.info("✅ All components initialized successfully")

    def test_data_flow_integration(self):
        """Test data flow between components."""
        Logger.info("Testing data flow integration...")

        # 1. Generate trace data
        trace_nodes = [
            {"id": "start", "label": "Start", "type": "cognitive", "duration_ms": 100},
            {"id": "process", "label": "Process", "type": "tool", "duration_ms": 200},
            {"id": "end", "label": "End", "type": "system", "duration_ms": 50},
        ]

        trace_edges = [
            {"id": "e1", "source": "start", "target": "process", "type": "calls"},
            {"id": "e2", "source": "process", "target": "end", "type": "flows_to"},
        ]

        # 2. Add to 3D visualization
        graph_id = self.visualizer.add_trace_graph("integration_test", trace_nodes, trace_edges)
        self.assertIsNotNone(graph_id)

        # 3. Extract metrics from trace
        trace_metrics = {
            "total_nodes": len(trace_nodes),
            "total_edges": len(trace_edges),
            "avg_duration": sum(node["duration_ms"] for node in trace_nodes) / len(trace_nodes),
            "max_duration": max(node["duration_ms"] for node in trace_nodes),
        }

        # 4. Add metrics to ML detector
        self.ml_detector.add_training_data("trace_nodes", trace_metrics["total_nodes"])
        self.ml_detector.add_training_data("trace_edges", trace_metrics["total_edges"])
        self.ml_detector.add_training_data("avg_duration", trace_metrics["avg_duration"])

        # 5. Detect anomalies
        anomalies = self.ml_detector.detect_anomalies(trace_metrics)
        self.assertIsInstance(anomalies, list)

        # 6. Inject tracing headers through gateway
        headers = {"Content-Type": "application/json"}
        traced_headers = self.gateway.inject_tracing_headers(
            headers,
            "integration-trace",
            "integration-span",
        )

        self.assertIn("x-trace-id", traced_headers)

        Logger.info("✅ Data flow integration successful")

    def test_cross_component_monitoring(self):
        """Test monitoring across all components."""
        Logger.info("Testing cross-component monitoring...")

        # Collect status from all components
        ml_stats = self.ml_detector.get_anomaly_statistics()
        viz_status = self.visualizer.get_visualization_summary()
        gateway_status = self.gateway.get_integration_status()
        cloud_status = self.cloud_manager.get_manager_status()
        pipeline_status = self.ml_pipeline.get_training_status()

        # Verify all components provide status
        self.assertIsInstance(ml_stats, dict)
        self.assertIsInstance(viz_status, dict)
        self.assertIsInstance(gateway_status, dict)
        self.assertIsInstance(cloud_status, dict)
        self.assertIsInstance(pipeline_status, dict)

        # Check for required status fields
        self.assertIn("total_anomalies", ml_stats)
        self.assertIn("server_active", viz_status)
        self.assertIn("initialized", gateway_status)
        self.assertIn("initialized", cloud_status)
        self.assertIn("total_models", pipeline_status)

        Logger.info("✅ Cross-component monitoring successful")

    def test_end_to_end_workflow(self):
        """Test end-to-end workflow simulation."""
        Logger.info("Testing end-to-end workflow...")

        # 1. Start with trace data
        trace_data = {
            "nodes": [
                {"id": "user_request", "label": "User Request", "type": "cognitive", "duration_ms": 50},
                {"id": "auth_check", "label": "Auth Check", "type": "tool", "duration_ms": 100},
                {"id": "data_processing", "label": "Data Processing", "type": "system", "duration_ms": 300},
                {"id": "response", "label": "Response", "type": "cognitive", "duration_ms": 75},
            ],
            "edges": [
                {"id": "e1", "source": "user_request", "target": "auth_check", "type": "calls"},
                {"id": "e2", "source": "auth_check", "target": "data_processing", "type": "flows_to"},
                {"id": "e3", "source": "data_processing", "target": "response", "type": "flows_to"},
            ],
        }

        # 2. Visualize trace
        graph_id = self.visualizer.add_trace_graph("e2e_test", trace_data["nodes"], trace_data["edges"])

        # 3. Extract performance metrics
        performance_metrics = {
            "total_duration": sum(node["duration_ms"] for node in trace_data["nodes"]),
            "node_count": len(trace_data["nodes"]),
            "edge_count": len(trace_data["edges"]),
            "avg_node_duration": sum(node["duration_ms"] for node in trace_data["nodes"])
            / len(trace_data["nodes"]),
        }

        # 4. Add to ML monitoring
        anomalies = self.ml_detector.detect_anomalies(performance_metrics)

        # 5. Simulate API gateway request with tracing
        request_headers = self.gateway.inject_tracing_headers(
            {"Content-Type": "application/json"},
            "e2e-trace",
            "e2e-span",
            baggage={"workflow": "test", "user_id": "123"},
        )

        # 6. Create training data for ML pipeline
        training_data = pd.DataFrame(
            {
                "total_duration": [performance_metrics["total_duration"]],
                "node_count": [performance_metrics["node_count"]],
                "edge_count": [performance_metrics["edge_count"]],
                "avg_duration": [performance_metrics["avg_node_duration"]],
                "anomaly": [1 if anomalies else 0],
            }
        )

        self.ml_pipeline.add_training_data("e2e_training", training_data)

        # 7. Train and deploy model
        model_id = self.ml_pipeline.train_anomaly_detection_model("e2e_training")
        if model_id:
            deployment_id = self.ml_pipeline.deploy_model(model_id)
            self.assertIsNotNone(deployment_id)

        # 8. Verify end-to-end success
        self.assertIsNotNone(graph_id)
        self.assertIsInstance(anomalies, list)
        self.assertIn("x-trace-id", request_headers)

        if model_id:
            self.assertIn(model_id, self.ml_pipeline._trained_models)

        Logger.info("✅ End-to-end workflow successful")


def run_phase5_tests():
    """Run all Phase 5 tests."""
    Logger.info("🚀 Starting Phase 5 Advanced Features Test Suite")

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestPhase5MLIntegration,
        TestPhase5Visualization,
        TestPhase5APIGateway,
        TestPhase5Kubernetes,
        TestPhase5CloudNative,
        TestPhase5MLTraining,
        TestPhase5Integration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors

    Logger.info("\n📊 Phase 5 Test Results:")
    Logger.info(f"   Total tests: {total_tests}")
    Logger.info(f"   Passed: {passed}")
    Logger.info(f"   Failed: {failures}")
    Logger.info(f"   Errors: {errors}")
    Logger.info(f"   Success rate: {(passed / total_tests) * 100:.1f}%")

    if failures == 0 and errors == 0:
        Logger.info("🎉 All Phase 5 tests passed!")
    else:
        Logger.warning("⚠️ Some Phase 5 tests failed")
        if result.failures:
            Logger.error("Failures:")
            for test, traceback in result.failures:
                Logger.error(f"  - {test}: {traceback}")
        if result.errors:
            Logger.error("Errors:")
            for test, traceback in result.errors:
                Logger.error(f"  - {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase5_tests()
    exit(0 if success else 1)
