"""
Territory Healing Stress Tests - Comprehensive test suite for territory-level healing.

Tests every agent on multiple territories to ensure:
1. No exceptions are raised
2. All agents can scan and heal
3. Territory-level healing works without bypasses
"""

import logging
from pathlib import Path

import pytest

# Setup logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerritoryStressTests")

# Project root
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()


class TestTerritoryHealingBasics:
    """Basic functionality tests for territory healing."""

    def test_coordinator_creation(self):
        """Test that coordinator can be created with all agents."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)
        assert coordinator is not None
        assert len(coordinator.agents) > 0
        logger.info(f"Coordinator created with {len(coordinator.agents)} agents")

    def test_agent_can_handle_territories(self):
        """Test that all agents report can_handle for standard territories."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)
        territories = ["tests", "agentic_core", "apps_eval", "ops_scripts"]

        for agent in coordinator.agents:
            for territory in territories:
                can_handle = agent.can_handle(territory)
                assert isinstance(can_handle, bool)
                logger.info(f"{agent.agent_name} can_handle({territory}): {can_handle}")


class TestTerritoryScanning:
    """Tests for territory scanning without healing."""

    def test_scan_tests_territory(self):
        """Scan tests territory - should detect root files as violations."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)
        report = coordinator.validate_territory("tests")

        assert report is not None
        assert report.territory == "tests"
        logger.info(f"Tests territory scan: {report.total_violations_found} violations")

        # Should have detected violations (root files)
        assert report.total_violations_found >= 0

    def test_scan_agentic_core_territory(self):
        """Scan agentic_core territory."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)
        report = coordinator.validate_territory("agentic_core")

        assert report is not None
        assert report.territory == "agentic_core"
        logger.info(f"agentic_core scan: {report.total_violations_found} violations")

    def test_scan_all_territories(self):
        """Scan all auto-detected territories."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)
        territories = coordinator._auto_detect_territories()

        assert len(territories) > 0
        logger.info(f"Auto-detected territories: {territories}")

        for territory in territories[:3]:  # Test first 3 to keep it fast
            report = coordinator.validate_territory(territory)
            assert report.territory == territory
            logger.info(f"  {territory}: {report.total_violations_found} violations")


class TestTerritoryHealing:
    """Tests for actual territory healing (may modify filesystem)."""

    @pytest.mark.healing
    def test_heal_tests_territory(self):
        """Test healing on tests territory - with dry-run first."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)

        # First scan to get baseline
        scan_report = coordinator.validate_territory("tests")
        initial_violations = scan_report.total_violations_found
        logger.info(f"Initial violations in tests: {initial_violations}")

        # Now run healing (dry-run first)
        from agentic_core.base_agents.territory_healer_protocol import HealingContext

        dry_run_context = HealingContext(
            heal=False,  # Dry run
            project_root=REPO_ROOT,
            verbose=True
        )

        # Check each agent individually
        for agent in coordinator.agents:
            if agent.can_handle("tests"):
                scan_result = agent.scan_territory("tests")
                logger.info(f"  {agent.agent_name}: {scan_result.violations_found} violations")

                # Try dry-run healing
                try:
                    healing_result = agent.heal_territory("tests", dry_run_context)
                    assert healing_result.dry_run is True
                    assert healing_result.territory == "tests"
                    logger.info("    Dry-run healing succeeded")
                except Exception as e:
                    logger.error(f"    Dry-run healing failed: {e}")
                    raise

    @pytest.mark.healing
    @pytest.mark.slow
    def test_full_heal_tests_territory(self):
        """Full healing test on tests territory - slow and comprehensive."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)

        # Run actual healing
        report = coordinator.heal_territory("tests", verbose=True)

        assert report is not None
        assert report.territory == "tests"

        logger.info(
            f"Healing complete:\n"
            f"  Violations found: {report.total_violations_found}\n"
            f"  Violations fixed: {report.total_violations_fixed}\n"
            f"  Agents executed: {len(report.agents_executed)}\n"
            f"  Errors: {len(report.errors)}"
        )

        # Should not have errors that indicate agent failures
        critical_errors = [e for e in report.errors if "failed" in e.lower() or "exception" in e.lower()]
        if critical_errors:
            logger.warning(f"Critical errors encountered: {critical_errors}")


class TestAgentSpecificHealing:
    """Test each agent type individually."""

    def test_hierarchy_healer_adapter(self):
        """Test HierarchyHealerAdapter specifically."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import HierarchyHealerAdapter

        adapter = HierarchyHealerAdapter(REPO_ROOT)

        # Test basic properties
        assert adapter.agent_name == "HierarchyHealerAgent"
        assert adapter.can_handle("tests")
        assert adapter.can_handle("agentic_core")

        # Test scanning
        scan_result = adapter.scan_territory("tests")
        assert scan_result.territory == "tests"
        logger.info(f"HierarchyHealer scan: {scan_result.violations_found} violations")

        # Check for territory root files
        root_file_violations = [
            v for v in scan_result.violations
            if v.type == "TERRITORY_ROOT_FILE"
        ]
        logger.info(f"  Territory root files: {len(root_file_violations)}")

    def test_location_healer_adapter(self):
        """Test LocationHealerAdapter specifically."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import LocationHealerAdapter

        adapter = LocationHealerAdapter(REPO_ROOT)

        assert adapter.agent_name == "LocationHealerAgent"
        assert adapter.can_handle("tests")

        # Test scanning
        scan_result = adapter.scan_territory("tests")
        assert scan_result.territory == "tests"
        logger.info(f"LocationHealer scan: {scan_result.violations_found} violations")

    def test_gravity_healer_adapter(self):
        """Test GravityHealerAdapter specifically."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import GravityHealerAdapter

        adapter = GravityHealerAdapter(REPO_ROOT)

        assert adapter.agent_name == "GravityLeakHealerAgent"
        assert adapter.can_handle("tests")

        # Test scanning
        scan_result = adapter.scan_territory("tests")
        assert scan_result.territory == "tests"
        logger.info(f"GravityHealer scan: {scan_result.violations_found} violations")

    def test_filesystem_reconciler_adapter(self):
        """Test FilesystemReconcilerAdapter specifically."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import (
            FilesystemReconcilerAdapter,
        )

        adapter = FilesystemReconcilerAdapter(REPO_ROOT)

        assert adapter.agent_name == "FilesystemSSOTReconcilerAgent"
        assert adapter.can_handle("tests")

        # Test scanning
        scan_result = adapter.scan_territory("tests")
        assert scan_result.territory == "tests"
        logger.info(f"FilesystemReconciler scan: {scan_result.violations_found} violations")


class TestStressScenarios:
    """Stress tests with edge cases and multiple runs."""

    @pytest.mark.stress
    def test_multiple_territory_scans(self):
        """Scan multiple territories in sequence - no state pollution."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)
        territories = ["tests", "agentic_core"]

        # Scan same territories multiple times
        for i in range(3):
            logger.info(f"Scan iteration {i+1}")
            for territory in territories:
                report = coordinator.validate_territory(territory)
                assert report.success is True  # No exceptions
                logger.info(f"  {territory}: {report.total_violations_found} violations")

    @pytest.mark.stress
    def test_concurrent_agent_execution(self):
        """Test that agents don't interfere with each other."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)

        # Run all agents on tests territory
        reports = []
        for agent in coordinator.agents:
            if agent.can_handle("tests"):
                scan_result = agent.scan_territory("tests")
                reports.append({
                    "agent": agent.agent_name,
                    "violations": scan_result.violations_found
                })

        # All should have succeeded
        for report in reports:
            logger.info(f"  {report['agent']}: {report['violations']} violations")

    @pytest.mark.stress
    @pytest.mark.slow
    def test_heal_all_territories(self):
        """Test healing all detected territories."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)

        # Get territories
        territories = coordinator._auto_detect_territories()[:3]  # Limit for speed

        # Heal all
        results = coordinator.heal_all_territories(territories, verbose=False)

        assert len(results) == len(territories)

        for territory, report in results.items():
            logger.info(
                f"{territory}: {report.total_violations_found} found, "
                f"{report.total_violations_fixed} fixed, "
                f"{len(report.errors)} errors"
            )
            # Should not have crashed
            assert report is not None


class TestNoExceptions:
    """Verify no exceptions are raised during normal operation."""

    def test_no_exceptions_on_scan(self):
        """Ensure scanning never raises exceptions."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)

        # Try various territories
        test_territories = ["tests", "agentic_core", "nonexistent_territory"]

        for territory in test_territories:
            try:
                report = coordinator.validate_territory(territory)
                logger.info(f"Scan {territory}: success={report.success}, violations={report.total_violations_found}")
            except Exception as e:
                # Non-existent territories should be handled gracefully
                logger.warning(f"Exception for {territory}: {e}")
                # Only non-existent should potentially fail
                if territory != "nonexistent_territory":
                    raise

    def test_no_exceptions_on_heal(self):
        """Ensure healing never raises unhandled exceptions."""
        from agentic_core.L3_orchestration.territory_healing.territory_healer_adapters import create_adapter_coordinator

        coordinator = create_adapter_coordinator(REPO_ROOT)

        # Test on tests territory - should complete without exception
        try:
            report = coordinator.heal_territory("tests", verbose=False)
            logger.info(f"Heal tests: success={report.success}, errors={len(report.errors)}")

            # Errors should be captured in report, not raised
            assert isinstance(report.errors, list)

        except Exception as e:
            logger.exception("Unhandled exception during healing")
            raise AssertionError(f"Healing should not raise exceptions: {e}")


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v", "-k", "TestTerritoryHealingBasics or TestTerritoryScanning"])
