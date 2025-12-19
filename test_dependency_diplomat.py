"""
Test script for Dependency Diplomat integration.

Demonstrates the smart scope functionality without requiring a full orchestrator run.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.domain.context import ValidationContext
from agentic_core.agents import get_dependency_diplomat

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


async def test_dependency_diplomat():
    """Test Dependency Diplomat smart scope calculation."""
    
    logger.info("="*80)
    logger.info("🔗 DEPENDENCY DIPLOMAT TEST")
    logger.info("="*80)
    
    # Create context
    ctx = ValidationContext()
    
    # Get Dependency Diplomat
    logger.info("\n1. Initializing Dependency Diplomat...")
    diplomat = get_dependency_diplomat(ctx)
    
    # Build dependency graph
    logger.info("\n2. Building dependency graph (scanning agentic_core/ and apps_shared/)...")
    await diplomat.execute()
    
    logger.info(f"\n   ✅ Graph built: {len(diplomat.graph)} nodes")
    
    # Test 1: Calculate impact for a specific file
    logger.info("\n3. Test Case 1: Impact scope for agentic_core/agents/dependency_diplomat.py")
    test_file = "agentic_core/agents/dependency_diplomat.py"
    
    if test_file in diplomat.graph:
        impact_scope = diplomat.calculate_impact_scope([test_file], max_depth=2)
        logger.info(f"   Modified: 1 file")
        logger.info(f"   Impact scope: {len(impact_scope)} files")
        logger.info(f"   Reduction: {((1900 - len(impact_scope)) / 1900 * 100):.1f}%")
        
        if len(impact_scope) <= 10:
            logger.info(f"\n   Files in impact scope:")
            for f in impact_scope:
                logger.info(f"     - {f}")
    else:
        logger.warning(f"   ⚠️  File not found in graph: {test_file}")
    
    # Test 2: Show sample of graph structure
    logger.info("\n4. Sample Graph Structure (first 5 nodes):")
    for i, (file_path, node) in enumerate(list(diplomat.graph.items())[:5]):
        logger.info(f"\n   File: {file_path}")
        logger.info(f"     Imports: {len(node.imports)} modules")
        logger.info(f"     Imported by: {len(node.imported_by)} files")
        
        if node.imported_by:
            logger.info(f"     Sample dependents:")
            for dep in list(node.imported_by)[:3]:
                logger.info(f"       - {dep}")
    
    # Test 3: Redis persistence check
    logger.info("\n5. Redis Persistence Check:")
    if diplomat.redis_available:
        logger.info("   ✅ Redis available - graph persisted with deps:forward: and deps:reverse: keys")
    else:
        logger.info("   ⚠️  Redis not available - using in-memory graph only")
    
    # Test 4: Export graph visualization
    logger.info("\n6. Exporting graph visualization...")
    diplomat.export_graph_visualization("dependency_graph.json")
    logger.info("   ✅ Graph exported to dependency_graph.json")
    
    logger.info("\n" + "="*80)
    logger.info("✅ DEPENDENCY DIPLOMAT TEST COMPLETE")
    logger.info("="*80)
    logger.info("\nSummary:")
    logger.info(f"  - Total nodes in graph: {len(diplomat.graph)}")
    logger.info(f"  - Redis available: {diplomat.redis_available}")
    logger.info(f"  - Graph visualization: dependency_graph.json")
    logger.info("\nNext steps:")
    logger.info("  - Run with --smart-scope flag: python -m agentic_core.core.orchestrator_main --smart-scope --heal")
    logger.info("  - View graph: Open dependency_graph.json in a graph visualization tool")


if __name__ == "__main__":
    asyncio.run(test_dependency_diplomat())
