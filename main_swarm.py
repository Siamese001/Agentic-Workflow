"""
Main Entry Point - Hardened Swarm Architecture

Startup sequence for the L5 Multi-Agent System with
Canon-First enforcement.
"""

import json
import logging
import signal
import sys
from datetime import datetime
from typing import Any, Dict

from core.connections import SwarmNetwork
from core.exceptions import CANON_EXCEPTIONS, SwarmInitializationError
from orchestrator import SwarmOrchestrator

# Configure structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/swarm.log", mode="a")
    ]
)

logger = logging.getLogger(__name__)


class SystemSanityCheck:
    """Verifies system health before swarm startup."""

    @staticmethod
    def run() -> Dict[str, Any]:
        """
        Run comprehensive system checks.

        Returns:
            Dictionary with check results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "overall_status": "passed"
        }

        # Check Redis AOF
        try:
            network = SwarmNetwork.get_instance()
            network.connect()

            redis_info = network.gatekeeper.redis.info()
            aof_enabled = redis_info.get("aof_enabled", False)

            results["checks"]["redis_aof"] = {
                "status": "passed" if aof_enabled else "warning",
                "message": "AOF enabled" if aof_enabled else "AOF disabled - data may not persist"
            }

            if not aof_enabled:
                results["overall_status"] = "warning"

        except Exception as e:
            results["checks"]["redis_aof"] = {
                "status": "failed",
                "message": str(e)
            }
            results["overall_status"] = "failed"

        # Check Qdrant connectivity
        try:
            collections = network.qdrant_cache.client.get_collections()
            results["checks"]["qdrant"] = {
                "status": "passed",
                "message": f"Connected to {len(collections.collections)} collections"
            }
        except Exception as e:
            results["checks"]["qdrant"] = {
                "status": "failed",
                "message": str(e)
            }
            results["overall_status"] = "failed"

        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)

        results["checks"]["disk_space"] = {
            "status": "passed" if free_gb > 10 else "warning",
            "message": f"{free_gb}GB free"
        }

        if free_gb <= 10:
            if results["overall_status"] == "passed":
                results["overall_status"] = "warning"

        return results


def initialize_swarm() -> SwarmOrchestrator:
    """
    Initialize the swarm with all components.

    Returns:
        Initialized SwarmOrchestrator

    Raises:
        SwarmInitializationError: If initialization fails
    """
    logger.info("=" * 50)
    logger.info("HARDENED SWARM SYSTEM - L5 MULTI-AGENT")
    logger.info("=" * 50)

    # Step 1: Initialize SwarmNetwork
    logger.info("1. Initializing SwarmNetwork...")
    network = SwarmNetwork.get_instance()

    if not network.connect():
        raise SwarmInitializationError(
            "Failed to initialize SwarmNetwork",
            failed_component="SwarmNetwork"
        )

    logger.info("   SwarmNetwork connected successfully")

    # Step 2: Run System Sanity Check
    logger.info("2. Running System Sanity Check...")
    sanity_results = SystemSanityCheck.run()

    logger.info(f"   Sanity check status: {sanity_results['overall_status']}")
    for check, result in sanity_results["checks"].items():
        logger.info(f"   {check}: {result['status']} - {result['message']}")

    if sanity_results["overall_status"] == "failed":
        raise SwarmInitializationError(
            "System sanity check failed",
            failed_component="SystemCheck"
        )

    # Step 3: Initialize SwarmOrchestrator
    logger.info("3. Initializing SwarmOrchestrator...")
    orchestrator = SwarmOrchestrator({
        "max_retries": 3,
        "retry_delay": 1.0,
        "planner": {},
        "coder": {},
        "auditor": {}
    })

    if not orchestrator.initialize():
        raise SwarmInitializationError(
            "Failed to initialize SwarmOrchestrator",
            failed_component="SwarmOrchestrator"
        )

    logger.info("   SwarmOrchestrator initialized successfully")
    logger.info("System initialization complete!")

    return orchestrator


def run_test_mission(orchestrator: SwarmOrchestrator) -> Dict[str, Any]:
    """
    Run a test mission to demonstrate the system.

    Args:
        orchestrator: Initialized orchestrator

    Returns:
        Mission execution results
    """
    logger.info("\n" + "=" * 50)
    logger.info("RUNNING TEST MISSION")
    logger.info("=" * 50)

    mission = "Refactor DB schema"
    context = {
        "requirements": [
            "Maintain backward compatibility",
            "Add migration scripts",
            "Update documentation"
        ],
        "database": "postgresql",
        "tables": ["users", "orders", "products"]
    }

    logger.info(f"Mission: {mission}")
    logger.info(f"Context: {json.dumps(context, indent=2)}")

    # Execute mission
    start_time = datetime.utcnow()

    try:
        result = orchestrator.run_mission(mission, context)

        duration = (datetime.utcnow() - start_time).total_seconds()

        logger.info(f"\nMission completed in {duration:.2f} seconds")
        logger.info(f"Status: {result['status']}")

        if result['status'] == 'success':
            logger.info("\nGenerated Plan:")
            for step in result['plan']['plan']:
                logger.info(f"  Step {step['step']}: {step['action']}")

            logger.info("\nGenerated Code:")
            code_lines = result['code']['code'].split('\n')[:10]
            for line in code_lines:
                logger.info(f"  {line}")
            if len(result['code']['code'].split('\n')) > 10:
                logger.info("  ...")

            logger.info(
                f"\nAudit Result: {result['audit']['validation_result']['is_valid']}")

        return result

    except Exception as e:
        logger.error(f"Mission failed: {e}")
        raise


def print_system_metrics(orchestrator: SwarmOrchestrator):
    """Print comprehensive system metrics."""
    logger.info("\n" + "=" * 50)
    logger.info("SYSTEM METRICS")
    logger.info("=" * 50)

    metrics = orchestrator.get_swarm_metrics()

    # Network metrics
    net_metrics = metrics["network"]
    logger.info(f"\nNetwork Status:")
    logger.info(f"  Connected: {net_metrics['connected']}")
    logger.info(f"  Total Queries: {net_metrics['metrics']['total_queries']}")
    logger.info(f"  Cache Hits: {net_metrics['metrics']['cache_hits']}")
    logger.info(f"  Cache Misses: {net_metrics['metrics']['cache_misses']}")

    # Agent metrics
    logger.info(f"\nAgent Metrics:")
    for agent_name, agent_metrics in metrics["agents"].items():
        agent_stats = agent_metrics["metrics"]
        logger.info(f"  {agent_name.title()}:")
        logger.info(f"    Executions: {agent_stats['executions']}")
        logger.info(f"    Successes: {agent_stats['successes']}")
        logger.info(f"    Failures: {agent_stats['failures']}")
        logger.info(f"    Canon Violations: {agent_stats['canon_violations']}")

    # Orchestrator metrics
    orch_metrics = metrics["orchestrator"]
    logger.info(f"\nOrchestrator:")
    logger.info(f"  Total Missions: {orch_metrics['total_missions']}")
    logger.info(f"  Success Rate: {orch_metrics['success_rate']:.2%}")
    logger.info(f"  Current Mission: {orch_metrics['current_mission']}")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"\nReceived signal {signum}, shutting down gracefully...")

    # Shutdown orchestrator
    orchestrator = getattr(sys.modules[__name__], '_orchestrator', None)
    if orchestrator:
        orchestrator.shutdown()

    logger.info("Shutdown complete")
    sys.exit(0)


def main():
    """Main entry point for the Hardened Swarm."""
    global orchestrator

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize swarm
        orchestrator = initialize_swarm()
        sys.modules[__name__]._orchestrator = orchestrator

        # Run test mission
        result = run_test_mission(orchestrator)

        # Print metrics
        print_system_metrics(orchestrator)

        # Final summary
        logger.info("\n" + "=" * 50)
        logger.info("HARDENED SWARM DEMO COMPLETE")
        logger.info("=" * 50)
        logger.info("\nThe system demonstrates:")
        logger.info("  ✓ Canon-First architecture enforcement")
        logger.info("  ✓ Universal memory access for all agents")
        logger.info("  ✓ Mandatory compliance before execution")
        logger.info("  ✓ Unified meta-learning across swarm")
        logger.info("  ✓ Automatic retry on audit failures")
        logger.info("  ✓ Comprehensive metrics and logging")

        logger.info("\nSwarm is ready for production use!")

        return 0

    except CANON_EXCEPTIONS as e:
        logger.error(f"Canon error: {json.dumps(e.to_dict(), indent=2)}")
        return 1
    except Exception as e:
        logger.error(f"System error: {e}")
        return 1
    finally:
        # Cleanup
        if 'orchestrator' in locals():
            orchestrator.shutdown()


if __name__ == "__main__":
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)

    # Run main
    exit_code = main()
    sys.exit(exit_code)