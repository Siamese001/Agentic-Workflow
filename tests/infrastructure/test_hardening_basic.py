"""Simplified Infrastructure Hardening Tests

Basic validation tests for the five infrastructure hardening opportunities.
"""

import asyncio
import unittest
from datetime import datetime

from infrastructure.hardening.adaptive_optimizer import AdaptiveOptimizer, OptimizationStrategy
from infrastructure.hardening.cross_layer_coherence import CrossLayerCoherenceManager
from infrastructure.hardening.distributed_state_manager import DistributedStateManager, Region
from infrastructure.hardening.implementation_plan import LayerType, QueryRequest
from infrastructure.hardening.security_framework import (
    AccessLevel,
    DataClassification,
    SecurityContext,
    SecurityGateway,
)
from infrastructure.hardening.unified_query_router import UnifiedQueryRouter


class TestInfrastructureBasics(unittest.TestCase):
    """Basic infrastructure component tests."""

    def test_unified_query_router_setup(self):
        """Test unified query router basic setup."""
        router = UnifiedQueryRouter()

        # Add test instances
        router.add_layer_instances(LayerType.REDIS_EXACT_MATCH, [("redis_1", "redis://localhost:6379", 1)])

        # Verify setup
        self.assertEqual(len(router.load_balancers), 1)
        self.assertEqual(len(router.circuit_breakers), 1)
        self.assertIn(LayerType.REDIS_EXACT_MATCH, router.load_balancers)

        # Test routing stats
        stats = router.get_routing_stats()
        self.assertIn("query_stats", stats)
        self.assertIn("instance_count", stats)

    def test_cross_layer_coherence_setup(self):
        """Test cross-layer coherence manager setup."""
        coherence_manager = CrossLayerCoherenceManager()

        # Test adding cache entry
        success = asyncio.run(
            coherence_manager.add_cache_entry(
                LayerType.REDIS_EXACT_MATCH, "test_key", {"data": "test_value"}, "v1.0.0", 3600
            )
        )

        self.assertTrue(success)

        # Test retrieving entry
        entry = asyncio.run(coherence_manager.get_cache_entry(LayerType.REDIS_EXACT_MATCH, "test_key"))

        self.assertIsNotNone(entry)
        self.assertEqual(entry.key, "test_key")
        self.assertEqual(entry.value["data"], "test_value")

        # Test coherence status
        status = coherence_manager.get_coherence_status()
        self.assertIn("layer_status", status)
        self.assertIn("cache_sizes", status)

    def test_adaptive_optimizer_setup(self):
        """Test adaptive optimizer setup."""
        optimizer = AdaptiveOptimizer()

        # Test parameter management
        params = optimizer.get_parameters(LayerType.SEMANTIC_CACHE)
        self.assertEqual(params.layer_type, LayerType.SEMANTIC_CACHE)
        self.assertIsInstance(params.similarity_threshold, float)

        # Test optimization strategy
        optimizer.set_optimization_strategy(OptimizationStrategy.COST_MINIMIZATION)
        self.assertEqual(optimizer.strategy, OptimizationStrategy.COST_MINIMIZATION)

        # Test optimization status
        status = optimizer.get_optimization_status()
        self.assertIn("strategy", status)
        self.assertIn("current_parameters", status)

    def test_distributed_state_manager_setup(self):
        """Test distributed state manager setup."""
        state_manager = DistributedStateManager()

        # Test basic setup
        self.assertEqual(state_manager.primary_region, Region.US_EAST)
        self.assertEqual(len(state_manager.replica_regions), 3)

        # Test state storage
        state_data = {"test_key": "test_value"}
        snapshot_id = asyncio.run(state_manager.store_layer_state(LayerType.REDIS_EXACT_MATCH, state_data))

        self.assertIsNotNone(snapshot_id)
        self.assertTrue(snapshot_id.startswith("layer_state_"))

        # Test state retrieval
        retrieved_data = asyncio.run(
            state_manager.retrieve_layer_state(LayerType.REDIS_EXACT_MATCH, snapshot_id)
        )

        self.assertEqual(retrieved_data, state_data)

        # Test system status
        status = state_manager.get_system_status()
        self.assertIn("primary_region", status)
        self.assertIn("replica_regions", status)

    def test_security_gateway_setup(self):
        """Test security gateway setup."""
        security_gateway = SecurityGateway()

        # Test data classification
        classification = security_gateway.data_classifier.classify_text("This is a public announcement")
        self.assertEqual(classification, DataClassification.PUBLIC)

        # Test PII classification
        pii_classification = security_gateway.data_classifier.classify_text(
            "Contact john.doe@example.com for more info"
        )
        self.assertEqual(pii_classification, DataClassification.SENSITIVE_PII)

        # Test access control
        security_gateway.access_controller.assign_user_role("test_user", "user")
        has_access = asyncio.run(
            security_gateway.access_controller.check_access(
                "test_user", "query", "test_query", AccessLevel.READ, LayerType.REDIS_EXACT_MATCH
            )
        )
        self.assertTrue(has_access)

        # Test privacy masking
        masked_email = security_gateway.privacy_engine.mask_data(
            "test@example.com", DataClassification.SENSITIVE_PII
        )
        self.assertTrue("***" in masked_email)

        # Test security status
        status = security_gateway.get_security_status()
        self.assertIn("policies_count", status)
        self.assertIn("users_count", status)
        self.assertIn("audit_summary", status)


class TestInfrastructureIntegration(unittest.TestCase):
    """Integration tests for infrastructure components."""

    def test_basic_integration(self):
        """Test basic integration between components."""
        # Setup components
        router = UnifiedQueryRouter()
        coherence_manager = CrossLayerCoherenceManager()
        optimizer = AdaptiveOptimizer()
        state_manager = DistributedStateManager()
        security_gateway = SecurityGateway()

        # Add router instances
        router.add_layer_instances(LayerType.REDIS_EXACT_MATCH, [("redis_1", "redis://localhost:6379", 1)])

        # Create test query
        request = QueryRequest(
            query_id="integration_test",
            user_query="Integration test query",
            timestamp=datetime.now(),
            priority=1,
        )

        # Test query routing
        responses = asyncio.run(router.route_query(request, [LayerType.REDIS_EXACT_MATCH]))

        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].layer_type, LayerType.REDIS_EXACT_MATCH)

        # Test cache coherence
        asyncio.run(
            coherence_manager.add_cache_entry(
                LayerType.REDIS_EXACT_MATCH, "integration_key", {"query": request.user_query}, "v1.0.0", 3600
            )
        )

        entry = asyncio.run(coherence_manager.get_cache_entry(LayerType.REDIS_EXACT_MATCH, "integration_key"))

        self.assertIsNotNone(entry)
        self.assertEqual(entry.value["query"], request.user_query)

        # Test performance data collection
        for response in responses:
            asyncio.run(optimizer.add_performance_data(response.layer_type, response))

        # Test state management
        state_data = {
            "query_id": request.query_id,
            "responses": [{"status": r.status.value} for r in responses],
            "timestamp": datetime.now().isoformat(),
        }

        snapshot_id = asyncio.run(state_manager.store_layer_state(LayerType.REDIS_EXACT_MATCH, state_data))

        self.assertIsNotNone(snapshot_id)

        # Test security
        security_gateway.access_controller.assign_user_role("integration_user", "user")
        security_context = SecurityContext(
            user_id="integration_user",
            roles=["user"],
            data_classification=DataClassification.INTERNAL,
            compliance_requirements=[],
            access_permissions={"ip_address": "127.0.0.1", "user_agent": "test"},
        )

        is_authenticated = asyncio.run(security_gateway.authenticate_request(request, security_context))

        self.assertTrue(is_authenticated)

        # Test data filtering
        filtered_data = asyncio.run(
            security_gateway.filter_response_data(
                LayerType.REDIS_EXACT_MATCH, {"email": "test@example.com"}, security_context
            )
        )

        self.assertTrue("***" in filtered_data["email"])

        # Verify all components are operational
        router_status = router.get_routing_stats()
        coherence_status = coherence_manager.get_coherence_status()
        optimizer_status = optimizer.get_optimization_status()
        state_status = state_manager.get_system_status()
        security_status = security_gateway.get_security_status()

        self.assertIsNotNone(router_status)
        self.assertIsNotNone(coherence_status)
        self.assertIsNotNone(optimizer_status)
        self.assertIsNotNone(state_status)
        self.assertIsNotNone(security_status)


if __name__ == "__main__":
    unittest.main(verbosity=2)
