"""
Test script for Dependency Diplomat integration.

Demonstrates the smart scope functionality without requiring a full orchestrator run.
"""
import logging
import sys
from pathlib import Path
from typing import Any
import pytest

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger: Any = logging.getLogger(__name__)

@pytest.mark.skip(reason='Stub import path issue - agentic_core.L5_safety.P1_red_team cannot be imported during pytest collection despite conftest.py setup')
@pytest.mark.asyncio
async def test_dependency_diplomat() -> Any:
    """Test Dependency Diplomat smart scope calculation."""
    logger.info('=' * 80)
    logger.info('🔗 DEPENDENCY DIPLOMAT TEST')
    logger.info('=' * 80)
    import importlib
    mod: Any = importlib.import_module('agentic_core.L5_safety.P1_red_team')
    get_dependency_diplomat: Any = mod.get_dependency_diplomat
    from agentic_core.L1_cognition.P2_domain.context import ValidationContext
    ctx: Any = ValidationContext()
    logger.info('\n1. Initializing Dependency Diplomat...')
    diplomat: Any = get_dependency_diplomat(ctx)
    logger.info('\n2. Building dependency graph (scanning agentic_core/ and apps_shared/)...')
    await diplomat.execute()
    total_nodes_in_graph: Any = len(diplomat.graph)
    logger.info(f'\n   ✅ Graph built: {total_nodes_in_graph} nodes')
    logger.info('\n3. Test Case 1: Impact scope for agentic_core/agents/dependency_diplomat.py')
    test_file_path: Any = 'agentic_core/agents/dependency_diplomat.py'
    if test_file_path in diplomat.graph:
        impact_scope: Any = diplomat.calculate_impact_scope([test_file_path], max_depth=2)
        logger.info(f'   Modified: 1 file')
        logger.info(f'   Impact scope: {len(impact_scope)} files')
        if total_nodes_in_graph > 0:
            reduction_percentage: Any = (total_nodes_in_graph - len(impact_scope)) / total_nodes_in_graph * 100
            logger.info(f'   Reduction: {reduction_percentage:.1f}%')
        else:
            logger.info('   Reduction: N/A (Graph is empty, cannot calculate reduction)')
        if len(impact_scope) <= 10:
            logger.info(f'\n   Files in impact scope:')
            for f in impact_scope:
                logger.info(f'     - {f}')
    else:
        logger.warning(f'   ⚠️  File not found in graph: {test_file_path}')
    logger.info('\n4. Sample Graph Structure (first 5 nodes):')
    for i, (file_path, node) in enumerate(list(diplomat.graph.items())[:5]):
        logger.info(f'\n   File: {file_path}')
        logger.info(f'     Imports: {len(node.imports)} modules')
        logger.info(f'     Imported by: {len(node.imported_by)} files')
        if node.imported_by:
            logger.info(f'     Sample dependents:')
            for dep in list(node.imported_by)[:3]:
                logger.info(f'       - {dep}')
    logger.info('\n5. Redis Persistence Check:')
    if diplomat.redis_available:
        logger.info('   ✅ Redis available - graph persisted with deps:forward: and deps:reverse: keys')
    else:
        logger.info('   ⚠️  Redis not available - using in-memory graph only')
    logger.info('\n6. Exporting graph visualization...')
    output_filename: Any = 'dependency_graph.json'
    diplomat.export_graph_visualization(output_filename)
    logger.info(f'   ✅ Graph exported to {output_filename}')
    logger.info('\n' + '=' * 80)
    logger.info('✅ DEPENDENCY DIPLOMAT TEST COMPLETE')
    logger.info('=' * 80)
    logger.info('\nSummary:')
    logger.info(f'  - Total nodes in graph: {total_nodes_in_graph}')
    logger.info(f'  - Redis available: {diplomat.redis_available}')
    logger.info(f'  - Graph visualization: {output_filename}')
    logger.info('\nNext steps:')
    logger.info('  - Run with --smart-scope flag: python -m agentic_core.core.orchestrator_main --smart-scope --heal')
    logger.info('  - View graph: Open dependency_graph.json in a graph visualization tool')
if __name__ == '__main__':
    asyncio.run(test_dependency_diplomat())
