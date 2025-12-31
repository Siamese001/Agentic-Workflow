"""
Integrated Test Suite for MCP Hardening System

Tests the complete L1-L5 MCP architecture including:
- MCPRouter layer routing
- GitSafetyHandler rollback/commit operations
- ProactiveFissionScanner bloat detection
- End-to-end fission workflow with MCP coordination
"""
import re
import asyncio
import sys
from pathlib import Path
project_root: Any = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from agentic_core.core.proactive_audit import get_proactive_scanner
from agentic_core.L3_orchestration.S3_vitality.git_safety_handler import get_git_safety_handler
from agentic_core.L3_orchestration.S3_vitality.mcp_router import get_mcp_router

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class mcp_integration_tests:
    """Comprehensive test suite for MCP hardening system."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def log_test(self, test_name: str, passed: bool, message: str='') -> Any:
        """Log test result."""
        status: Any = '✅ PASS' if passed else '❌ FAIL'
        result: Any = f'{status} - {test_name}'
        if message:
            result += f': {message}'
        print(result)
        self.results.append(result)
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    async def test_mcp_router_initialization(self) -> Any:
        """Test MCPRouter initialization and registry."""
        print('\n🧪 Test 1: MCPRouter Initialization')
        try:
            router: Any = get_mcp_router()
            assert 'L1' in router.registry, 'L1 not in registry'
            assert 'L2' in router.registry, 'L2 not in registry'
            assert 'L3' in router.registry, 'L3 not in registry'
            assert 'L4' in router.registry, 'L4 not in registry'
            assert 'L5' in router.registry, 'L5 not in registry'
            assert 'sequential_thinking' in router.registry['L1'], 'Sequential Thinking not in L1'
            assert 'brave_search' in router.registry['L2'], 'Brave Search not in L2'
            assert 'redis' in router.registry['L3'], 'Redis not in L3'
            assert 'pinecone' in router.registry['L4'], 'Pinecone not in L4'
            assert 'gitkraken' in router.registry['L5'], 'GitKraken not in L5'
            self.log_test('MCPRouter Initialization', True, 'All layers registered correctly')
            return True
        except Exception as e:
            self.log_test('MCPRouter Initialization', False, str(e))
            return False

    async def test_mcp_router_layer_routing(self) -> Any:
        """Test MCPRouter layer-specific routing."""
        print('\n🧪 Test 2: MCPRouter Layer Routing')
        try:
            router: Any = get_mcp_router()
            result_l1: Any = await router.resolve_failure('L1', 'Complex reasoning loop detected')
            assert result_l1['status'] == 'success', 'L1 routing failed'
            assert result_l1['mcp'] == 'sequential_thinking', 'Wrong MCP for L1'
            result_l2: Any = await router.resolve_failure('L2', 'SyntaxError in module')
            assert result_l2['status'] == 'success', 'L2 routing failed'
            assert result_l2['mcp'] == 'brave_search', 'Wrong MCP for L2'
            result_l3: Any = await router.resolve_failure('L3', 'orchestration_state')
            assert result_l3['status'] == 'success', 'L3 routing failed'
            assert result_l3['mcp'] == 'redis', 'Wrong MCP for L3'
            result_l4: Any = await router.resolve_failure('L4', 'structural pattern needed')
            assert result_l4['status'] == 'success', 'L4 routing failed'
            assert result_l4['mcp'] == 'pinecone', 'Wrong MCP for L4'
            result_l5: Any = await router.resolve_failure('L5', 'nervous_system.py')
            assert result_l5['status'] == 'success', 'L5 routing failed'
            assert result_l5['mcp'] == 'gitkraken', 'Wrong MCP for L5'
            self.log_test('MCPRouter Layer Routing', True, 'All 5 layers route correctly')
            return True
        except Exception as e:
            self.log_test('MCPRouter Layer Routing', False, str(e))
            return False

    async def test_mcp_router_health_check(self) -> Any:
        """Test MCPRouter health check functionality."""
        print('\n🧪 Test 3: MCPRouter Health Check')
        try:
            router: Any = get_mcp_router()
            health: Any = await router.health_check()
            assert isinstance(health, dict), 'Health check should return dict'
            assert len(health) > 0, 'Health check should return MCP statuses'
            self.log_test('MCPRouter Health Check', True, f'Checked {len(health)} MCPs')
            return True
        except Exception as e:
            self.log_test('MCPRouter Health Check', False, str(e))
            return False

    async def test_git_safety_handler_initialization(self) -> Any:
        """Test GitSafetyHandler initialization."""
        print('\n🧪 Test 4: GitSafetyHandler Initialization')
        try:
            router: Any = get_mcp_router()
            git_safety: Any = get_git_safety_handler(router)
            assert git_safety.router is not None, 'Router not initialized'
            self.log_test('GitSafetyHandler Initialization', True, 'Handler initialized with router')
            return True
        except Exception as e:
            self.log_test('GitSafetyHandler Initialization', False, str(e))
            return False

    async def test_git_safety_handler_rollback_point(self) -> Any:
        """Test GitSafetyHandler rollback point creation."""
        print('\n🧪 Test 5: GitSafetyHandler Rollback Point')
        try:
            router: Any = get_mcp_router()
            git_safety: Any = get_git_safety_handler(router)
            branch_name: Any = await git_safety.create_rollback_point('test_file.py')
            assert branch_name is not None, 'Branch name should not be None'
            assert 'fission_backup_' in branch_name, 'Branch name should contain fission_backup_'
            self.log_test('GitSafetyHandler Rollback Point', True, f'Created branch: {branch_name}')
            return True
        except Exception as e:
            self.log_test('GitSafetyHandler Rollback Point', False, str(e))
            return False

    async def test_proactive_scanner_initialization(self) -> Any:
        """Test ProactiveFissionScanner initialization."""
        print('\n🧪 Test 6: ProactiveFissionScanner Initialization')
        try:
            router: Any = get_mcp_router()
            scanner: Any = get_proactive_scanner(router, line_threshold=600)
            assert scanner.threshold == 600, 'Threshold not set correctly'
            assert scanner.router is not None, 'Router not initialized'
            self.log_test('ProactiveFissionScanner Initialization', True, 'Scanner initialized with threshold 600')
            return True
        except Exception as e:
            self.log_test('ProactiveFissionScanner Initialization', False, str(e))
            return False

    async def test_proactive_scanner_line_count(self) -> Any:
        """Test ProactiveFissionScanner line counting."""
        print('\n🧪 Test 7: ProactiveFissionScanner Line Count')
        try:
            router: Any = get_mcp_router()
            scanner: Any = get_proactive_scanner(router)
            test_file: Any = __file__
            line_count: Any = scanner.get_line_count(test_file)
            assert line_count > 0, 'Line count should be greater than 0'
            self.log_test('ProactiveFissionScanner Line Count', True, f'Counted {line_count} lines')
            return True
        except Exception as e:
            self.log_test('ProactiveFissionScanner Line Count', False, str(e))
            return False

    async def test_proactive_scanner_severity_calculation(self) -> Any:
        """Test ProactiveFissionScanner severity calculation."""
        print('\n🧪 Test 8: ProactiveFissionScanner Severity Calculation')
        try:
            router: Any = get_mcp_router()
            scanner: Any = get_proactive_scanner(router)
            assert scanner._calculate_severity(650) == 'LOW', '650 lines should be LOW'
            assert scanner._calculate_severity(750) == 'MEDIUM', '750 lines should be MEDIUM'
            assert scanner._calculate_severity(900) == 'HIGH', '900 lines should be HIGH'
            assert scanner._calculate_severity(1100) == 'CRITICAL', '1100 lines should be CRITICAL'
            self.log_test('ProactiveFissionScanner Severity Calculation', True, 'All severity levels correct')
            return True
        except Exception as e:
            self.log_test('ProactiveFissionScanner Severity Calculation', False, str(e))
            return False

    async def test_proactive_scanner_repository_scan(self) -> Any:
        """Test ProactiveFissionScanner repository scanning."""
        print('\n🧪 Test 9: ProactiveFissionScanner Repository Scan')
        try:
            router: Any = get_mcp_router()
            scanner: Any = get_proactive_scanner(router, line_threshold=300)
            target_dir: Any = str(project_root / 'agentic_core')
            candidates: Any = await scanner.scan_repository(target_dir)
            assert isinstance(candidates, list), 'Scan should return list'
            if candidates:
                candidate: Any = candidates[0]
                assert 'path' in candidate, 'Candidate should have path'
                assert 'line_count' in candidate, 'Candidate should have line_count'
                assert 'severity' in candidate, 'Candidate should have severity'
                assert 'relative_path' in candidate, 'Candidate should have relative_path'
            self.log_test('ProactiveFissionScanner Repository Scan', True, f'Found {len(candidates)} candidates')
            return True
        except Exception as e:
            self.log_test('ProactiveFissionScanner Repository Scan', False, str(e))
            return False

    async def test_end_to_end_mcp_workflow(self) -> Any:
        """Test end-to-end MCP workflow integration."""
        print('\n🧪 Test 10: End-to-End MCP Workflow')
        try:
            router: Any = get_mcp_router()
            git_safety: Any = get_git_safety_handler(router)
            scanner: Any = get_proactive_scanner(router)
            print('   → Step 1: Create rollback point')
            backup_branch: Any = await git_safety.create_rollback_point('test_monolith.py')
            assert backup_branch is not None, 'Rollback point creation failed'
            print('   → Step 2: Route L1 failure to Sequential Thinking')
            l1_result: Any = await router.resolve_failure('L1', 'Complex reasoning needed')
            assert l1_result['status'] == 'success', 'L1 routing failed'
            print('   → Step 3: Route L4 failure to Pinecone')
            l4_result: Any = await router.resolve_failure('L4', 'Find structural pattern')
            assert l4_result['status'] == 'success', 'L4 routing failed'
            print('   → Step 4: Verify clean state')
            await git_safety.verify_clean_state('test_monolith.py')
            print('   → Step 5: Generate pre-emptive strategy')
            strategy: Any = await scanner.generate_pre_emptive_strategy(__file__)
            assert 'file_path' in strategy, 'Strategy generation failed'
            self.log_test('End-to-End MCP Workflow', True, 'All workflow steps completed')
            return True
        except Exception as e:
            self.log_test('End-to-End MCP Workflow', False, str(e))
            return False

    async def run_all_tests(self) -> Any:
        """Run all integration tests."""
        print('\n' + '=' * 70)
        print('🚀 MCP INTEGRATION TEST SUITE')
        print('=' * 70)
        await self.test_mcp_router_initialization()
        await self.test_mcp_router_layer_routing()
        await self.test_mcp_router_health_check()
        await self.test_git_safety_handler_initialization()
        await self.test_git_safety_handler_rollback_point()
        await self.test_proactive_scanner_initialization()
        await self.test_proactive_scanner_line_count()
        await self.test_proactive_scanner_severity_calculation()
        await self.test_proactive_scanner_repository_scan()
        await self.test_end_to_end_mcp_workflow()
        print('\n' + '=' * 70)
        print('📊 TEST SUMMARY')
        print('=' * 70)
        print(f'✅ Passed: {self.passed}')
        print(f'❌ Failed: {self.failed}')
        print(f'📈 Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%')
        print('=' * 70)
        if self.failed == 0:
            print('\n🎉 ALL TESTS PASSED - MCP HARDENING SYSTEM VERIFIED')
        else:
            print(f'\n⚠️  {self.failed} TEST(S) FAILED - REVIEW REQUIRED')
        return self.failed == 0

async def main() -> Any:
    """Main test runner."""
    tests: Any = MCPIntegrationTests()
    success: Any = await tests.run_all_tests()
    sys.exit(0 if success else 1)
if __name__ == '__main__':
    asyncio.run(main())
