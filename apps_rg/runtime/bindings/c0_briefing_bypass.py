"""W3: Briefing bypass gate for apps_rg C0.

Evaluates manual brief files for G_BRIEF_BYPASS gate eligibility.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class BriefEvaluationResult:
    """Result of evaluating a manual brief file."""
    
    brief_path: str
    authority_class: str
    is_fresh: bool
    is_authorized: bool
    can_read: bool
    file_exists: bool
    file_size_bytes: int
    file_mtime: str
    file_age_hours: float
    max_age_hours: int
    bypass_eligible: bool
    support_status: str
    reason: str
    
    def to_gate_verdict(self, evidence_digest: str) -> dict[str, Any]:
        """Convert to GateVerdict-compatible dict."""
        verdict_map = {
            "PASS": "PASS",
            "WEAK_WITH_CAVEATS": "PARTIAL",
            "BLOCKED": "FAIL",
            "NOT_APPLICABLE": "UNKNOWN",
            "UNREADABLE": "UNKNOWN",
        }
        
        return {
            "gate_id": "G_BRIEF_BYPASS",
            "result": verdict_map.get(self.support_status, "UNKNOWN"),
            "evidence_refs": [f"brief:{self.brief_path}"] if self.file_exists else [],
            "evidence_digest": evidence_digest,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "reason": self.reason,
        }


class BriefingBypassEvaluator:
    """Evaluator for manual briefing bypass eligibility."""
    
    PROFILE_PATH = Path("apps_rg/config/domain_contract/research_delegation_profile.yaml")
    
    def __init__(self):
        self._config: dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML."""
        if self.PROFILE_PATH.exists():
            with open(self.PROFILE_PATH, encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = self._default_config()
    
    def _default_config(self) -> dict[str, Any]:
        """Default configuration."""
        return {
            "max_age_hours": 168,  # 7 days
            "authority_classes": ["authoritative", "semi_authoritative", "unverified"],
            "bypass_rules": {
                "authoritative": {"requires_fresh": True, "allows_bypass": True},
                "semi_authoritative": {"requires_fresh": True, "allows_bypass": False},
                "unverified": {"requires_fresh": False, "allows_bypass": False},
            },
        }
    
    @property
    def max_age_hours(self) -> int:
        return self._config.get("max_age_hours", 168)
    
    @property
    def authority_classes(self) -> list[str]:
        return self._config.get("authority_classes", ["authoritative", "semi_authoritative", "unverified"])
    
    @property
    def bypass_rules(self) -> dict[str, Any]:
        return self._config.get("bypass_rules", {})
    
    def _determine_authority_class(self, brief_path: str) -> str:
        """Determine authority class from file path."""
        path_lower = brief_path.lower()
        
        authoritative_indicators = [
            "company_website", "official", "annual_report", "10-k", "sec_filing",
            "press_release", " investor_relations"
        ]
        semi_authoritative_indicators = [
            "industry_analyst", "analyst_report", "market_research",
            "linkedin_company", "crunchbase"
        ]
        
        for indicator in authoritative_indicators:
            if indicator in path_lower:
                return "authoritative"
        
        for indicator in semi_authoritative_indicators:
            if indicator in path_lower:
                return "semi_authoritative"
        
        return "unverified"
    
    def _is_authorized(self, brief_path: str) -> bool:
        """Check if brief path is authorized."""
        # For testing: allow paths with specific indicators
        # In production: check against ACL
        path_lower = brief_path.lower()
        
        authorized_indicators = [
            "company_website", "official", "annual_report", "industry_analyst",
            "research", "brief", "notes"
        ]
        
        return any(ind in path_lower for ind in authorized_indicators)
    
    def evaluate_brief(self, brief_path: str | None) -> BriefEvaluationResult:
        """Evaluate a brief file for bypass eligibility."""
        # Handle None or empty path
        if not brief_path:
            return BriefEvaluationResult(
                brief_path="",
                authority_class="not_applicable",
                is_fresh=False,
                is_authorized=False,
                can_read=False,
                file_exists=False,
                file_size_bytes=0,
                file_mtime="",
                file_age_hours=0.0,
                max_age_hours=self.max_age_hours,
                bypass_eligible=False,
                support_status="NOT_APPLICABLE",
                reason="No manual brief path provided",
            )
        
        path = Path(brief_path)
        
        # Check file exists and is readable
        file_exists = path.exists() and path.is_file()
        can_read = os.access(path, os.R_OK) if file_exists else False
        
        if not file_exists:
            return BriefEvaluationResult(
                brief_path=brief_path,
                authority_class="unverified",
                is_fresh=False,
                is_authorized=False,
                can_read=False,
                file_exists=False,
                file_size_bytes=0,
                file_mtime="",
                file_age_hours=0.0,
                max_age_hours=self.max_age_hours,
                bypass_eligible=False,
                support_status="UNREADABLE",
                reason=f"Brief file not found: {brief_path}",
            )
        
        # Get file stats
        stat = path.stat()
        file_size_bytes = stat.st_size
        file_mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        
        # Calculate age
        file_mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        file_age_hours = (now - file_mtime_dt).total_seconds() / 3600
        
        is_fresh = file_age_hours <= self.max_age_hours
        authority_class = self._determine_authority_class(brief_path)
        is_authorized = self._is_authorized(brief_path)
        
        # Determine support status and bypass eligibility
        rules = self.bypass_rules.get(authority_class, {})
        requires_fresh = rules.get("requires_fresh", True)
        allows_bypass = rules.get("allows_bypass", False)
        
        if authority_class == "authoritative":
            if is_fresh and is_authorized:
                support_status = "PASS"
                bypass_eligible = True
                reason = "Fresh authoritative brief"
            elif is_authorized:
                support_status = "WEAK_WITH_CAVEATS"
                bypass_eligible = False
                reason = "Stale authoritative brief"
            else:
                support_status = "BLOCKED"
                bypass_eligible = False
                reason = "Authoritative brief not authorized"
        elif authority_class == "semi_authoritative":
            if is_fresh and is_authorized:
                support_status = "WEAK_WITH_CAVEATS"
                bypass_eligible = False
                reason = "Fresh semi-authoritative brief (no bypass)"
            elif is_authorized:
                support_status = "BLOCKED"
                bypass_eligible = False
                reason = "Stale semi-authoritative brief"
            else:
                support_status = "BLOCKED"
                bypass_eligible = False
                reason = "Semi-authoritative brief not authorized"
        else:  # unverified
            support_status = "BLOCKED"
            bypass_eligible = False
            reason = f"Unverified source: {brief_path}"
        
        return BriefEvaluationResult(
            brief_path=brief_path,
            authority_class=authority_class,
            is_fresh=is_fresh,
            is_authorized=is_authorized,
            can_read=can_read,
            file_exists=file_exists,
            file_size_bytes=file_size_bytes,
            file_mtime=file_mtime,
            file_age_hours=file_age_hours,
            max_age_hours=self.max_age_hours,
            bypass_eligible=bypass_eligible,
            support_status=support_status,
            reason=reason,
        )


def evaluate_manual_brief(brief_path: str | None) -> BriefEvaluationResult:
    """Convenience function to evaluate a manual brief."""
    evaluator = BriefingBypassEvaluator()
    return evaluator.evaluate_brief(brief_path)


__all__ = [
    "BriefEvaluationResult",
    "BriefingBypassEvaluator",
    "evaluate_manual_brief",
]
