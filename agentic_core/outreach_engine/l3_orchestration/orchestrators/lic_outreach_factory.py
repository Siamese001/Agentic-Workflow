"""Outreach factory for creating executors and orchestrators with routing."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from .lic_outreach_orchestrator import OutreachOrchestrator

@dataclass
class RoutingConfig:
    """Configuration for message routing."""
    routing_strategy: str = "archetype_based"
    fallback_enabled: bool = True
    priority_weights: Dict[str, float] = field(default_factory=lambda: {
        "C_LEVEL": 2.0,
        "EXECUTIVE": 1.5,
        "SENIOR_TA": 1.2,
        "RECRUITER": 1.0
    })
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MessageExecutorConfig:
    """Configuration for message executor with routing."""
    max_concurrent: int = 10
    timeout_seconds: int = 300
    retry_attempts: int = 3
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MessageExecutorWithRouting:
    """Message executor with routing capabilities."""

    def __init__(self, config: Optional[MessageExecutorConfig] = None):
        """Initialize with routing configuration."""
        self.config = config or MessageExecutorConfig()
        self.routing_config = self.config.routing
        self.active_executions = {}

    def execute_message_with_routing(self,
                                    contact: Dict[str, Any],
                                    message_template: str,
                                    archetype: str = None) -> Dict[str, Any]:
        """Execute message with routing based on archetype."""
        # Determine routing priority
        priority = self.routing_config.priority_weights.get(archetype, 1.0)

        # Mock execution with routing
        result = {
            "contact_id": contact.get("id", "unknown"),
            "message": f"Routed message for {contact.get('name', 'contact')}",
            "archetype": archetype,
            "routing_priority": priority,
            "execution_strategy": self.routing_config.routing_strategy,
            "executed_at": datetime.now().isoformat(),
            "template_used": message_template
        }

        return result

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing execution statistics."""
        return {
            "routing_strategy": self.routing_config.routing_strategy,
            "priority_weights": self.routing_config.priority_weights,
            "active_executions": len(self.active_executions),
            "config_metadata": self.routing_config.metadata
        }

def create_message_executor_with_routing(config: Optional[Dict[str, Any]] = None) -> MessageExecutorWithRouting:
    """Factory function to create message executor with routing configuration."""
    if config is None:
        config = {}

    # Extract routing configuration
    routing_config_data = config.get("routing", {})
    routing_config = RoutingConfig(**routing_config_data)

    # Create executor config
    executor_config_data = {
        "max_concurrent": config.get("max_concurrent", 10),
        "timeout_seconds": config.get("timeout_seconds", 300),
        "retry_attempts": config.get("retry_attempts", 3),
        "routing": routing_config,
        "metadata": config.get("metadata", {})
    }

    executor_config = MessageExecutorConfig(**executor_config_data)
    return MessageExecutorWithRouting(executor_config)

def create_outreach_orchestrator_with_routing(config: Optional[Dict[str, Any]] = None) -> OutreachOrchestrator:
    """Factory function to create outreach orchestrator with routing capabilities."""
    if config is None:
        config = {}

    # Add routing-specific configuration to orchestrator config
    enhanced_config = {
        **config,
        "routing_enabled": True,
        "routing_strategy": config.get("routing", {}).get("routing_strategy", "archetype_based"),
        "factory_created": True,
        "created_at": datetime.now().isoformat()
    }

    return OutreachOrchestrator(enhanced_config)

@dataclass
class RoutingIntegrationResult:
    """Result from routing integration tests."""
    test_name: str = ""
    routing_applied: bool = False
    priority_correct: bool = False
    fallback_used: bool = False
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class RoutingIntegrationTester:
    """Helper class for testing routing integration."""

    def __init__(self):
        self.test_results = []

    def test_archetype_routing(self, contacts: List[Dict[str, Any]], executor: MessageExecutorWithRouting) -> RoutingIntegrationResult:
        """Test archetype-based routing."""
        start_time = datetime.now()

        # Test routing for different archetypes
        routing_results = []
        for contact in contacts:
            archetype = contact.get("archetype", "RECRUITER")
            result = executor.execute_message_with_routing(contact, "test_template", archetype)
            routing_results.append(result)

        execution_time = (datetime.now() - start_time).total_seconds()

        # Validate routing priorities
        priority_correct = all(
            result["routing_priority"] == executor.routing_config.priority_weights.get(result["archetype"], 1.0)
            for result in routing_results
        )

        return RoutingIntegrationResult(
            test_name="archetype_routing",
            routing_applied=True,
            priority_correct=priority_correct,
            execution_time=execution_time,
            metadata={
                "contacts_tested": len(contacts),
                "routing_results": routing_results
            }
        )

    def test_fallback_routing(self, contacts: List[Dict[str, Any]], executor: MessageExecutorWithRouting) -> RoutingIntegrationResult:
        """Test fallback routing behavior."""
        start_time = datetime.now()

        # Test with invalid archetype to trigger fallback
        fallback_results = []
        for contact in contacts:
            result = executor.execute_message_with_routing(contact, "test_template", "INVALID_ARCHETYPE")
            fallback_results.append(result)

        execution_time = (datetime.now() - start_time).total_seconds()

        # Check if fallback was used (should default to priority 1.0)
        fallback_used = all(result["routing_priority"] == 1.0 for result in fallback_results)

        return RoutingIntegrationResult(
            test_name="fallback_routing",
            routing_applied=True,
            fallback_used=fallback_used,
            execution_time=execution_time,
            metadata={
                "contacts_tested": len(contacts),
                "fallback_results": fallback_results
            }
        )
