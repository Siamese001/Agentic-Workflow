"""W5 Campaign Inventory for apps_lic Multi-Touch Migration.

W5.P1: Existing Campaign Inventory

This module provides campaign inventory and compatibility checking
for migrating existing apps_lic campaigns to the new multi-touch infrastructure.

App: apps_lic
Layer: Migration (apps_lic/migrations/)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class CampaignStatus(str, Enum):
    """Status of a campaign in the legacy system."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"
    ARCHIVED = "archived"


class CompatibilityLevel(str, Enum):
    """Compatibility level for migration."""
    FULL = "full"           # Can migrate completely
    PARTIAL = "partial"     # Can migrate with limitations
    BLOCKED = "blocked"     # Cannot migrate - requires manual intervention


@dataclass(frozen=True)
class CampaignRecord:
    """Record of a legacy campaign for inventory purposes.
    
    Fields
    ------
    campaign_id : str
        Unique campaign identifier
    campaign_name : str
        Human-readable name
    status : CampaignStatus
        Current status in legacy system
    created_at : datetime
        When campaign was created
    last_activity_at : datetime
        When last activity occurred
    recipient_count : int
        Number of recipients
    touch_count : int
        Number of touches sent
    has_custom_templates : bool
        Whether campaign uses custom templates
    has_automation_rules : bool
        Whether campaign has automation rules
    data_size_bytes : int
        Approximate data size
    """
    
    campaign_id: str
    campaign_name: str
    status: CampaignStatus
    created_at: datetime
    last_activity_at: datetime
    recipient_count: int
    touch_count: int
    has_custom_templates: bool
    has_automation_rules: bool
    data_size_bytes: int
    
    @property
    def is_migratable(self) -> bool:
        """Whether this campaign can be migrated."""
        if self.status == CampaignStatus.ARCHIVED:
            return False
        if self.has_custom_templates and self.has_automation_rules:
            return False  # Too complex
        return True
    
    @property
    def migration_priority(self) -> int:
        """Priority for migration (lower = higher priority)."""
        if self.status == CampaignStatus.ACTIVE:
            return 1
        if self.status == CampaignStatus.PAUSED:
            return 2
        if self.status == CampaignStatus.DRAFT:
            return 3
        return 4


@dataclass(frozen=True)
class CompatibilityReport:
    """Compatibility report for a campaign.
    
    Fields
    ------
    campaign_id : str
        Campaign identifier
    compatibility : CompatibilityLevel
        Overall compatibility level
    blockers : list[str]
        List of migration blockers
    warnings : list[str]
        List of migration warnings
    recommended_action : str
        Recommended migration action
    """
    
    campaign_id: str
    compatibility: CompatibilityLevel
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    recommended_action: str


@dataclass
class CampaignInventory:
    """Inventory of campaigns for migration planning.
    
    Fields
    ------
    campaigns : list[CampaignRecord]
        All discovered campaigns
    inventory_date : datetime
        When inventory was taken
    source_system : str
        Source system identifier
    """
    
    campaigns: list[CampaignRecord] = field(default_factory=list)
    inventory_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_system: str = "legacy_apps_lic"
    
    @property
    def total_campaigns(self) -> int:
        """Total number of campaigns."""
        return len(self.campaigns)
    
    @property
    def total_recipients(self) -> int:
        """Total recipients across all campaigns."""
        return sum(c.recipient_count for c in self.campaigns)
    
    @property
    def total_touches(self) -> int:
        """Total touches across all campaigns."""
        return sum(c.touch_count for c in self.campaigns)
    
    @property
    def migratable_count(self) -> int:
        """Number of campaigns that can be migrated."""
        return sum(1 for c in self.campaigns if c.is_migratable)
    
    @property
    def blocked_count(self) -> int:
        """Number of campaigns that cannot be migrated."""
        return sum(1 for c in self.campaigns if not c.is_migratable)
    
    def get_by_status(self, status: CampaignStatus) -> list[CampaignRecord]:
        """Get campaigns by status."""
        return [c for c in self.campaigns if c.status == status]
    
    def get_migratable(self) -> list[CampaignRecord]:
        """Get campaigns that can be migrated, sorted by priority."""
        migratable = [c for c in self.campaigns if c.is_migratable]
        return sorted(migratable, key=lambda c: c.migration_priority)
    
    def to_summary_dict(self) -> dict[str, Any]:
        """Convert to summary dictionary."""
        return {
            "total_campaigns": self.total_campaigns,
            "total_recipients": self.total_recipients,
            "total_touches": self.total_touches,
            "migratable_count": self.migratable_count,
            "blocked_count": self.blocked_count,
            "by_status": {
                status.value: len(self.get_by_status(status))
                for status in CampaignStatus
            },
            "inventory_date": self.inventory_date.isoformat(),
        }


class CampaignInventoryScanner:
    """Scanner for discovering and inventorying legacy campaigns.
    
    Decision-only invariants:
    - No durable writes. Only reads from legacy sources.
    - No provider API calls.
    - No subprocess calls.
    """
    
    def __init__(self, source_path: Optional[Path] = None) -> None:
        self._source_path = source_path or Path("data/apps_lic/legacy_campaigns")
    
    def scan(self) -> CampaignInventory:
        """Scan for legacy campaigns and build inventory.
        
        Returns
        -------
        CampaignInventory
            Complete inventory of discovered campaigns
        """
        campaigns: list[CampaignRecord] = []
        
        # Check if legacy data exists
        if self._source_path.exists():
            # Scan for campaign files
            for campaign_file in self._source_path.glob("*.json"):
                try:
                    campaign = self._parse_campaign_file(campaign_file)
                    if campaign:
                        campaigns.append(campaign)
                except Exception:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                    # Skip corrupted files
                    pass
        
        # If no legacy data found, return empty inventory
        # This is expected in development environments
        return CampaignInventory(
            campaigns=campaigns,
            source_system="legacy_apps_lic",
        )
    
    def _parse_campaign_file(self, path: Path) -> Optional[CampaignRecord]:
        """Parse a campaign file into a CampaignRecord."""
        import json
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return CampaignRecord(
                campaign_id=data.get("campaign_id", path.stem),
                campaign_name=data.get("campaign_name", "Unknown"),
                status=CampaignStatus(data.get("status", "draft")),
                created_at=datetime.fromisoformat(data.get("created_at", "2024-01-01T00:00:00")),
                last_activity_at=datetime.fromisoformat(data.get("last_activity_at", "2024-01-01T00:00:00")),
                recipient_count=data.get("recipient_count", 0),
                touch_count=data.get("touch_count", 0),
                has_custom_templates=data.get("has_custom_templates", False),
                has_automation_rules=data.get("has_automation_rules", False),
                data_size_bytes=path.stat().st_size,
            )
        except (json.JSONDecodeError, ValueError, KeyError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
            return None


class CompatibilityChecker:
    """Checker for campaign migration compatibility.
    
    Evaluates campaigns against new infrastructure requirements
    and produces compatibility reports.
    """
    
    def __init__(self) -> None:
        self._checks: list[callable] = [
            self._check_template_compatibility,
            self._check_automation_rules,
            self._check_data_completeness,
            self._check_recipient_count,
        ]
    
    def check(self, campaign: CampaignRecord) -> CompatibilityReport:
        """Check compatibility of a campaign.
        
        Parameters
        ----------
        campaign : CampaignRecord
            Campaign to check
        
        Returns
        -------
        CompatibilityReport
            Compatibility assessment
        """
        blockers: list[str] = []
        warnings: list[str] = []
        
        for check in self._checks:
            result = check(campaign)
            if result:
                if result.get("blocking", False):
                    blockers.append(result["message"])
                else:
                    warnings.append(result["message"])
        
        # Determine compatibility level
        if blockers:
            compatibility = CompatibilityLevel.BLOCKED
            recommended_action = "manual_review_required"
        elif warnings:
            compatibility = CompatibilityLevel.PARTIAL
            recommended_action = "migrate_with_limitations"
        else:
            compatibility = CompatibilityLevel.FULL
            recommended_action = "migrate_auto"
        
        return CompatibilityReport(
            campaign_id=campaign.campaign_id,
            compatibility=compatibility,
            blockers=tuple(blockers),
            warnings=tuple(warnings),
            recommended_action=recommended_action,
        )
    
    def check_all(self, inventory: CampaignInventory) -> list[CompatibilityReport]:
        """Check compatibility for all campaigns in inventory."""
        return [self.check(c) for c in inventory.campaigns]
    
    def _check_template_compatibility(self, campaign: CampaignRecord) -> Optional[dict]:
        """Check if campaign templates are compatible."""
        if campaign.has_custom_templates:
            return {
                "message": "Campaign uses custom templates - may need template migration",
                "blocking": False,
            }
        return None
    
    def _check_automation_rules(self, campaign: CampaignRecord) -> Optional[dict]:
        """Check if automation rules can be migrated."""
        if campaign.has_automation_rules and campaign.has_custom_templates:
            return {
                "message": "Campaign has complex automation rules with custom templates",
                "blocking": True,
            }
        if campaign.has_automation_rules:
            return {
                "message": "Campaign has automation rules - may need rule conversion",
                "blocking": False,
            }
        return None
    
    def _check_data_completeness(self, campaign: CampaignRecord) -> Optional[dict]:
        """Check if campaign has required data."""
        if campaign.recipient_count == 0:
            return {
                "message": "Campaign has no recipients",
                "blocking": True,
            }
        return None
    
    def _check_recipient_count(self, campaign: CampaignRecord) -> Optional[dict]:
        """Check recipient count for migration load."""
        if campaign.recipient_count > 10000:
            return {
                "message": f"Large recipient list ({campaign.recipient_count}) - consider batch migration",
                "blocking": False,
            }
        return None


__all__ = [
    "CampaignStatus",
    "CompatibilityLevel",
    "CampaignRecord",
    "CompatibilityReport",
    "CampaignInventory",
    "CampaignInventoryScanner",
    "CompatibilityChecker",
]
