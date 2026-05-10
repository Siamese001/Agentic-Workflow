"""W5 Migration Tests

Integration tests for W5 migration execution:
- W5.P1: Campaign inventory
- W5.P2: Migration script execution
- W5.P3: Rollback procedures
"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestW5P1CampaignInventory:
    """Test W5.P1: Campaign Inventory."""
    
    def test_campaign_record_creation(self):
        """Verify CampaignRecord dataclass."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignRecord, CampaignStatus
        )
        
        campaign = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Test Campaign",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=100,
            touch_count=50,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=1024,
        )
        
        assert campaign.campaign_id == "camp-001"
        assert campaign.status == CampaignStatus.ACTIVE
        assert campaign.is_migratable is True
    
    def test_campaign_migratable_logic(self):
        """Verify migratable logic."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignRecord, CampaignStatus
        )
        
        # Active campaign should be migratable
        active = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Active",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=10,
            touch_count=5,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=100,
        )
        assert active.is_migratable is True
        
        # Archived should not be migratable
        archived = CampaignRecord(
            campaign_id="camp-002",
            campaign_name="Archived",
            status=CampaignStatus.ARCHIVED,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=10,
            touch_count=5,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=100,
        )
        assert archived.is_migratable is False
        
        # Complex campaigns should not be migratable
        complex_campaign = CampaignRecord(
            campaign_id="camp-003",
            campaign_name="Complex",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=10,
            touch_count=5,
            has_custom_templates=True,
            has_automation_rules=True,
            data_size_bytes=100,
        )
        assert complex_campaign.is_migratable is False
    
    def test_campaign_migration_priority(self):
        """Verify migration priority ordering."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignRecord, CampaignStatus
        )
        
        active = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Active",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=10,
            touch_count=5,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=100,
        )
        
        draft = CampaignRecord(
            campaign_id="camp-002",
            campaign_name="Draft",
            status=CampaignStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=10,
            touch_count=5,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=100,
        )
        
        # Active should have higher priority (lower number) than draft
        assert active.migration_priority < draft.migration_priority
    
    def test_campaign_inventory_summary(self):
        """Verify CampaignInventory summary."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignInventory, CampaignRecord, CampaignStatus
        )
        
        campaigns = [
            CampaignRecord(
                campaign_id=f"camp-{i:03d}",
                campaign_name=f"Campaign {i}",
                status=CampaignStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=100,
                touch_count=50,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=1000,
            )
            for i in range(5)
        ]
        
        inventory = CampaignInventory(campaigns=campaigns)
        
        assert inventory.total_campaigns == 5
        assert inventory.total_recipients == 500
        assert inventory.total_touches == 250
        assert inventory.migratable_count == 5
        assert inventory.blocked_count == 0
    
    def test_campaign_inventory_get_by_status(self):
        """Verify filtering by status."""
        from apps_lic.migrations.campaign_inventory import (
            CampaignInventory, CampaignRecord, CampaignStatus
        )
        
        campaigns = [
            CampaignRecord(
                campaign_id="camp-001",
                campaign_name="Active",
                status=CampaignStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=10,
                touch_count=5,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=100,
            ),
            CampaignRecord(
                campaign_id="camp-002",
                campaign_name="Draft",
                status=CampaignStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                recipient_count=10,
                touch_count=5,
                has_custom_templates=False,
                has_automation_rules=False,
                data_size_bytes=100,
            ),
        ]
        
        inventory = CampaignInventory(campaigns=campaigns)
        
        active = inventory.get_by_status(CampaignStatus.ACTIVE)
        assert len(active) == 1
        assert active[0].campaign_id == "camp-001"


class TestW5CompatibilityChecker:
    """Test W5 compatibility checking."""
    
    def test_full_compatibility(self):
        """Verify full compatibility report."""
        from apps_lic.migrations.campaign_inventory import (
            CompatibilityChecker, CampaignRecord, CampaignStatus,
            CompatibilityLevel
        )
        
        campaign = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Simple",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=100,
            touch_count=50,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=1000,
        )
        
        checker = CompatibilityChecker()
        report = checker.check(campaign)
        
        assert report.compatibility == CompatibilityLevel.FULL
        assert len(report.blockers) == 0
        assert report.recommended_action == "migrate_auto"
    
    def test_partial_compatibility_custom_templates(self):
        """Verify partial compatibility with custom templates."""
        from apps_lic.migrations.campaign_inventory import (
            CompatibilityChecker, CampaignRecord, CampaignStatus,
            CompatibilityLevel
        )
        
        campaign = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Custom",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=100,
            touch_count=50,
            has_custom_templates=True,
            has_automation_rules=False,
            data_size_bytes=1000,
        )
        
        checker = CompatibilityChecker()
        report = checker.check(campaign)
        
        assert report.compatibility == CompatibilityLevel.PARTIAL
        assert len(report.warnings) > 0
        assert "template" in report.warnings[0].lower()
    
    def test_blocked_compatibility_no_recipients(self):
        """Verify blocked when no recipients."""
        from apps_lic.migrations.campaign_inventory import (
            CompatibilityChecker, CampaignRecord, CampaignStatus,
            CompatibilityLevel
        )
        
        campaign = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Empty",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=0,
            touch_count=0,
            has_custom_templates=False,
            has_automation_rules=False,
            data_size_bytes=100,
        )
        
        checker = CompatibilityChecker()
        report = checker.check(campaign)
        
        assert report.compatibility == CompatibilityLevel.BLOCKED
        assert len(report.blockers) > 0
    
    def test_blocked_complex_campaign(self):
        """Verify blocked for complex campaigns."""
        from apps_lic.migrations.campaign_inventory import (
            CompatibilityChecker, CampaignRecord, CampaignStatus,
            CompatibilityLevel
        )
        
        campaign = CampaignRecord(
            campaign_id="camp-001",
            campaign_name="Complex",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            recipient_count=100,
            touch_count=50,
            has_custom_templates=True,
            has_automation_rules=True,
            data_size_bytes=1000,
        )
        
        checker = CompatibilityChecker()
        report = checker.check(campaign)
        
        assert report.compatibility == CompatibilityLevel.BLOCKED


class TestW5P2MigrationScript:
    """Test W5.P2: Migration Script Execution."""
    
    def test_migration_runner_dry_run(self):
        """Verify dry-run mode."""
        from apps_lic.migrations.w5_migration import W5MigrationRunner
        
        runner = W5MigrationRunner(dry_run=True)
        results = runner.run()
        
        assert len(results) > 0
        assert all(r.status in ("success", "skipped") for r in results)
    
    def test_migration_runner_verify_only(self):
        """Verify verify-only mode."""
        from apps_lic.migrations.w5_migration import W5MigrationRunner
        
        runner = W5MigrationRunner(verify_only=True)
        results = runner.run()
        
        # Should only run verification phase
        assert len(results) == 1
        assert results[0].step_id == "w5_p3_verify"
    
    def test_migration_result_structure(self):
        """Verify MigrationResult structure."""
        from apps_lic.migrations.w5_migration import MigrationResult
        
        result = MigrationResult(
            step_id="test_step",
            status="success",
            message="Test completed",
            details={"count": 10},
            migrated_count=5,
            failed_count=0,
        )
        
        assert result.step_id == "test_step"
        assert result.migrated_count == 5
        assert result.failed_count == 0


class TestW5InventoryScanner:
    """Test W5 campaign inventory scanner."""
    
    def test_scanner_empty_directory(self):
        """Verify scanner handles empty/missing directory."""
        from apps_lic.migrations.campaign_inventory import CampaignInventoryScanner
        
        scanner = CampaignInventoryScanner(source_path=Path("/nonexistent"))
        inventory = scanner.scan()
        
        assert inventory.total_campaigns == 0
    
    def test_scanner_parses_campaign_file(self, tmp_path):
        """Verify scanner parses campaign files."""
        import json
        from apps_lic.migrations.campaign_inventory import CampaignInventoryScanner
        
        # Create test campaign file
        campaign_file = tmp_path / "camp_001.json"
        campaign_file.write_text(json.dumps({
            "campaign_id": "camp-001",
            "campaign_name": "Test Campaign",
            "status": "active",
            "created_at": "2024-01-01T00:00:00",
            "last_activity_at": "2024-06-01T00:00:00",
            "recipient_count": 100,
            "touch_count": 50,
            "has_custom_templates": False,
            "has_automation_rules": False,
        }))
        
        scanner = CampaignInventoryScanner(source_path=tmp_path)
        inventory = scanner.scan()
        
        assert inventory.total_campaigns == 1
        assert inventory.campaigns[0].campaign_id == "camp-001"
        assert inventory.campaigns[0].recipient_count == 100


class TestW5RollbackRunbook:
    """Test W5.P3: Rollback procedures documented."""
    
    def test_rollback_runbook_exists(self):
        """Verify rollback runbook exists."""
        runbook_path = Path("docs/runbooks/apps_lic_migration_rollback.md")
        assert runbook_path.exists()
        assert runbook_path.stat().st_size > 1000
    
    def test_rollback_runbook_contains_scenarios(self):
        """Verify runbook documents rollback scenarios."""
        runbook_path = Path("docs/runbooks/apps_lic_migration_rollback.md")
        content = runbook_path.read_text()
        
        assert "Scenario A" in content or "Dry-Run Failure" in content
        assert "Scenario B" in content or "Partial Migration" in content
        assert "Scenario C" in content or "Data Corruption" in content
    
    def test_rollback_runbook_has_procedures(self):
        """Verify runbook has rollback procedures."""
        runbook_path = Path("docs/runbooks/apps_lic_migration_rollback.md")
        content = runbook_path.read_text()
        
        assert "Standard Rollback" in content
        assert "Full System Rollback" in content or "emergency" in content.lower()
        assert "Verification" in content


class TestW5SpineWiring:
    """Test W5 components available to spine wiring."""
    
    def test_migration_modules_exist(self):
        """Verify W5 migration modules exist."""
        import apps_lic.migrations.campaign_inventory
        import apps_lic.migrations.w5_migration
        
        assert hasattr(apps_lic.migrations.campaign_inventory, 'CampaignInventory')
        assert hasattr(apps_lic.migrations.w5_migration, 'W5MigrationRunner')


# Import needed for tests
from pathlib import Path
