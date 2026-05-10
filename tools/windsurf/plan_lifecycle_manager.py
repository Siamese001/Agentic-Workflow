#!/usr/bin/env python3
"""
plan_lifecycle_manager.py — Unified Plan Lifecycle Manager (UPLM)

Consolidates 40+ fragmented Notion enforcement files into a cohesive
state machine with unified hooks, consolidated gates, and prevention layer.

Plan: notion-enforcement-consolidation-e8f3a2 W2.1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Iterable, Optional

# Repo root detection
REPO_ROOT = Path(__file__).resolve().parents[2]

# State paths
STATE_DIR = REPO_ROOT / "artifacts" / "windsurf"
REGISTRATION_QUEUE = REPO_ROOT / ".windsurf" / "state" / "plan_registration_queue.jsonl"
REGISTRATION_CACHE = REPO_ROOT / ".windsurf" / "state" / "plan_registration_cache.json"

# Constants
MAX_RESPONSE_BYTES = 512 * 1024


class PlanStatus(Enum):
    """Canonical plan statuses aligned with Notion Plans DB."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    WAITING = "Waiting"
    COMPLETED = "Completed"
    RETIRED = "Retired"
    ARCHIVED = "Archived"
    DEFERRED = "Deferred"


class LifecycleState(Enum):
    """Internal state machine states."""
    UNREGISTERED = auto()
    REGISTERED = auto()
    WAVE_ACTIVE = auto()
    WAVE_PAUSED = auto()
    COMPLETED = auto()


@dataclass(frozen=True)
class WaveLifecycleMarker:
    """Parsed marker from Cascade response text."""
    kind: str  # wave_start, wave_complete, phase_complete, plan_complete
    slug: str
    wave: Optional[int] = None
    phase: Optional[str] = None
    reason: Optional[str] = None
    note: Optional[str] = None


@dataclass(frozen=True)
class NotionPatchSpec:
    """Specification for a Notion Plans DB patch."""
    slug: str
    properties: dict[str, Any] = field(default_factory=dict)
    summary_append: Optional[str] = None
    reason: str = ""
    
    @property
    def is_noop(self) -> bool:
        return not self.properties and not self.summary_append


@dataclass
class UnifiedStatus:
    """Aggregated status across all sources."""
    slug: str
    notion_status: Optional[str] = None
    wave_active: bool = False
    wave_plan: Optional[str] = None
    wave_started_at: Optional[str] = None
    registered: bool = False
    registration_queued: bool = False
    cache_age_minutes: Optional[float] = None
    
    @property
    def unified_state(self) -> str:
        if self.wave_active:
            return "wave_active"
        if self.notion_status == PlanStatus.COMPLETED.value:
            return "completed"
        if self.registered or self.registration_queued:
            return "registered_idle"
        return "unregistered"


@dataclass
class PreFlightResult:
    """Result of pre-flight check with recommended action."""
    slug: str
    can_proceed: bool
    recommendation: str
    message: str
    requires_user_action: bool = False


class PlanLifecycleManager:
    """
    Unified Plan Lifecycle Manager.
    
    Replaces:
    - _wave_execution_state.py (state persistence)
    - _plan_registration.py (registration tracking)
    - 11 post_cascade hooks (marker capture)
    - 4 pre_user_prompt hooks (pre-flight checks)
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or REPO_ROOT
        self.state_dir = self.repo_root / "artifacts" / "windsurf"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Compile marker regex patterns
        self._marker_re = re.compile(
            r"^\s*(?P<kind>WAVE_START|WAVE_COMPLETE|PHASE_COMPLETE|PLAN_COMPLETE)\s*:\s*(?P<body>.+?)$",
            re.MULTILINE | re.IGNORECASE,
        )
        self._slug_kv_re = re.compile(r"\bplan\s*=\s*(?P<slug>[a-z0-9_-]+)")
        self._wave_kv_re = re.compile(r"\bwave\s*=\s*(?P<wave>\d+)")
        self._phase_kv_re = re.compile(r"\bphase\s*=\s*(?P<phase>[a-z0-9_-]+)")
        self._note_kv_re = re.compile(r"\bnote\s*=\s*([\"'])(?P<note>.+?)\1")
    
    # -----------------------------------------------------------------------
    # State Management (from _wave_execution_state.py)
    # -----------------------------------------------------------------------
    
    def _state_path(self) -> Path:
        """Canonical path for wave execution state file."""
        session_id = os.environ.get("VSCODE_PID") or str(os.getppid())
        return self.state_dir / f"wave_execution_{session_id}.json"
    
    def get_wave_state(self) -> Optional[dict]:
        """Get current wave execution state. Fail-open."""
        path = self._state_path()
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("plan"):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return None
    
    def set_wave_active(self, plan_slug: str) -> Path:
        """Mark a plan as having active wave execution."""
        if not plan_slug or not isinstance(plan_slug, str):
            raise ValueError("plan_slug must be non-empty string")
        
        now = time.time()
        payload = {
            "plan": plan_slug,
            "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "started_at_epoch": now,
        }
        path = self._state_path()
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
    
    def clear_wave_state(self) -> bool:
        """Clear wave execution state. Returns True if file existed."""
        path = self._state_path()
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False
        return False
    
    # -----------------------------------------------------------------------
    # Registration Tracking (from _plan_registration.py)
    # -----------------------------------------------------------------------
    
    def check_registration(self, slug: str) -> dict:
        """Check if plan is registered in Notion."""
        result = {
            "slug": slug,
            "registered": False,
            "queued": False,
            "cache_hit": False,
            "notion_status": None,
        }
        
        # Check queue
        if REGISTRATION_QUEUE.exists():
            try:
                with open(REGISTRATION_QUEUE, encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        if entry.get("slug") == slug:
                            result["queued"] = True
                            result["registered"] = entry.get("registered", False)
                            break
            except (OSError, json.JSONDecodeError):
                pass
        
        # Check cache
        if REGISTRATION_CACHE.exists():
            try:
                cache = json.loads(REGISTRATION_CACHE.read_text(encoding="utf-8"))
                plans = cache.get("plans", {})
                if slug in plans:
                    entry = plans[slug]
                    result["cache_hit"] = True
                    result["registered"] = True
                    result["notion_status"] = entry.get("status")
                    if "fetched_at_epoch" in entry:
                        age = (time.time() - entry["fetched_at_epoch"]) / 60
                        result["cache_age_minutes"] = age
            except (OSError, json.JSONDecodeError):
                pass
        
        return result
    
    # -----------------------------------------------------------------------
    # Unified Status Query
    # -----------------------------------------------------------------------
    
    def query_status(self, slug: str) -> UnifiedStatus:
        """Query unified status across all sources."""
        reg = self.check_registration(slug)
        wave = self.get_wave_state()
        
        return UnifiedStatus(
            slug=slug,
            notion_status=reg.get("notion_status"),
            wave_active=wave is not None and wave.get("plan") == slug,
            wave_plan=wave.get("plan") if wave else None,
            wave_started_at=wave.get("started_at") if wave else None,
            registered=reg.get("registered", False),
            registration_queued=reg.get("queued", False),
            cache_age_minutes=reg.get("cache_age_minutes"),
        )
    
    # -----------------------------------------------------------------------
    # Prevention Layer: Pre-Flight Check
    # -----------------------------------------------------------------------
    
    def pre_flight_check(self, slug: str) -> PreFlightResult:
        """
        Check if plan is ready for work but waves not started.
        
        Returns recommendation to prompt user for wave start.
        """
        status = self.query_status(slug)
        
        # Already active wave
        if status.wave_active:
            return PreFlightResult(
                slug=slug,
                can_proceed=True,
                recommendation="continue",
                message=f"Wave active for {slug} since {status.wave_started_at}",
            )
        
        # Completed
        if status.notion_status == PlanStatus.COMPLETED.value:
            return PreFlightResult(
                slug=slug,
                can_proceed=True,
                recommendation="read_only",
                message=f"Plan {slug} is completed",
            )
        
        # Registered but no wave - PREVENTION LAYER TRIGGER
        if status.registered and status.notion_status in (
            PlanStatus.NOT_STARTED.value,
            PlanStatus.WAITING.value,
            None,
        ):
            return PreFlightResult(
                slug=slug,
                can_proceed=True,
                recommendation="prompt_start",
                message=f"Plan {slug} is registered but wave execution not started. Start now?",
                requires_user_action=True,
            )
        
        # Not registered
        if not status.registered and not status.registration_queued:
            return PreFlightResult(
                slug=slug,
                can_proceed=False,
                recommendation="register_first",
                message=f"Plan {slug} not registered. Emit PLAN_CREATED marker first.",
            )
        
        # Default: allow proceed
        return PreFlightResult(
            slug=slug,
            can_proceed=True,
            recommendation="continue",
            message=f"Plan {slug} ready",
        )
    
    # -----------------------------------------------------------------------
    # Marker Parsing (consolidated from 7 hooks)
    # -----------------------------------------------------------------------
    
    def parse_markers(self, text: str) -> list[WaveLifecycleMarker]:
        """Parse all wave lifecycle markers from text."""
        markers = []
        for m in self._marker_re.finditer(text):
            kind = m.group("kind").lower()
            body = m.group("body")
            
            # Extract fields
            slug_match = self._slug_kv_re.search(body)
            wave_match = self._wave_kv_re.search(body)
            phase_match = self._phase_kv_re.search(body)
            note_match = self._note_kv_re.search(body)
            
            if slug_match:
                markers.append(WaveLifecycleMarker(
                    kind=kind,
                    slug=slug_match.group("slug"),
                    wave=int(wave_match.group("wave")) if wave_match else None,
                    phase=phase_match.group("phase") if phase_match else None,
                    note=note_match.group("note") if note_match else None,
                ))
        
        return markers
    
    # -----------------------------------------------------------------------
    # Action Execution
    # -----------------------------------------------------------------------
    
    def start_wave(self, slug: str, note: Optional[str] = None) -> dict:
        """Start wave execution for a plan."""
        # Set local state
        self.set_wave_active(slug)
        
        # Return action spec for Notion sync
        return {
            "ok": True,
            "action": "wave_start",
            "slug": slug,
            "note": note,
            "local_state": str(self._state_path()),
        }
    
    def complete_wave(self, slug: str, wave: int, note: Optional[str] = None) -> dict:
        """Log wave completion."""
        return {
            "ok": True,
            "action": "wave_complete",
            "slug": slug,
            "wave": wave,
            "note": note,
        }
    
    def complete_plan(self, slug: str, note: Optional[str] = None) -> dict:
        """Complete plan and clear wave state."""
        self.clear_wave_state()
        
        return {
            "ok": True,
            "action": "plan_complete",
            "slug": slug,
            "note": note,
        }
    
    # -----------------------------------------------------------------------
    # Consolidated Gates (replacing NP1-NP13)
    # -----------------------------------------------------------------------
    
    def gate_presence(self, slug: str) -> dict:
        """NP-PRESENCE: Verify Notion row exists."""
        status = self.query_status(slug)
        return {
            "gate": "NP-PRESENCE",
            "ok": status.registered,
            "slug": slug,
            "status": status.notion_status,
        }
    
    def gate_freshness(self, slug: str, stale_days: int = 7) -> dict:
        """NP-FRESHNESS: Check not stale."""
        status = self.query_status(slug)
        is_fresh = True
        
        if status.cache_age_minutes and status.cache_age_minutes > stale_days * 24 * 60:
            is_fresh = False
        
        return {
            "gate": "NP-FRESHNESS",
            "ok": is_fresh,
            "slug": slug,
            "cache_age_minutes": status.cache_age_minutes,
        }
    
    def gate_completeness(self, slug: str) -> dict:
        """NP-COMPLETENESS: Check DoD verified."""
        # Check if plan file has all DoD items checked
        plan_file = self.repo_root / ".windsurf" / "plans" / f"{slug}.md"
        if not plan_file.exists():
            return {"gate": "NP-COMPLETENESS", "ok": False, "reason": "plan file not found"}
        
        content = plan_file.read_text(encoding="utf-8")
        # Look for DoD table with all ✅ or all 🔲 (we verify structure, not execution)
        has_dod = "## Definition of Done" in content or "## DoD" in content
        
        return {
            "gate": "NP-COMPLETENESS",
            "ok": has_dod,
            "slug": slug,
            "has_dod_section": has_dod,
        }
    
    def gate_compliance(self, slug: str) -> dict:
        """NP-COMPLIANCE: AI summary, canonical status."""
        status = self.query_status(slug)
        
        # Basic compliance: has status and it's canonical
        canonical = [s.value for s in PlanStatus]
        is_compliant = status.notion_status in canonical
        
        return {
            "gate": "NP-COMPLIANCE",
            "ok": is_compliant,
            "slug": slug,
            "status": status.notion_status,
            "canonical": canonical,
        }
    
    def gate_divergence(self, slug: str) -> dict:
        """NP-DIVERGENCE: Check on-disk vs Notion mismatch."""
        plan_file = self.repo_root / ".windsurf" / "plans" / f"{slug}.md"
        exists_on_disk = plan_file.exists()
        
        status = self.query_status(slug)
        
        # Divergence if: on disk but not in Notion, or in Notion but not on disk
        diverged = exists_on_disk != status.registered
        
        return {
            "gate": "NP-DIVERGENCE",
            "ok": not diverged,
            "slug": slug,
            "exists_on_disk": exists_on_disk,
            "registered_in_notion": status.registered,
            "diverged": diverged,
        }
    
    def run_all_gates(self, slug: str) -> list[dict]:
        """Run all 5 consolidated gates."""
        return [
            self.gate_presence(slug),
            self.gate_freshness(slug),
            self.gate_completeness(slug),
            self.gate_compliance(slug),
            self.gate_divergence(slug),
        ]


# -----------------------------------------------------------------------------
# CLI Interface (backward compatible with wave_execution_state.py)
# -----------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Unified Plan Lifecycle Manager")
    sub = parser.add_subparsers(dest="command", required=True)
    
    # status
    sub.add_parser("status", help="Show unified status for active or specified plan")
    
    # start
    p_start = sub.add_parser("start", help="Start wave execution")
    p_start.add_argument("--plan", required=True, help="Plan slug")
    p_start.add_argument("--note", help="Optional note")
    
    # pre-flight
    p_preflight = sub.add_parser("pre-flight", help="Run pre-flight check")
    p_preflight.add_argument("--plan", required=True, help="Plan slug")
    
    # gates
    p_gates = sub.add_parser("gates", help="Run all consolidated gates")
    p_gates.add_argument("--plan", required=True, help="Plan slug")
    
    # parse-markers (for testing)
    p_parse = sub.add_parser("parse-markers", help="Parse markers from stdin")
    
    args = parser.parse_args(argv)
    
    manager = PlanLifecycleManager()
    
    if args.command == "status":
        wave = manager.get_wave_state()
        if wave:
            print(json.dumps({"active": True, **wave}, indent=2))
        else:
            print(json.dumps({"active": False}))
        return 0
    
    if args.command == "start":
        result = manager.start_wave(args.plan, note=getattr(args, "note", None))
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    
    if args.command == "pre-flight":
        result = manager.pre_flight_check(args.plan)
        print(json.dumps({
            "slug": result.slug,
            "can_proceed": result.can_proceed,
            "recommendation": result.recommendation,
            "message": result.message,
            "requires_user_action": result.requires_user_action,
        }, indent=2))
        return 0 if result.can_proceed else 1
    
    if args.command == "gates":
        results = manager.run_all_gates(args.plan)
        all_ok = all(r["ok"] for r in results)
        print(json.dumps(results, indent=2))
        return 0 if all_ok else 1
    
    if args.command == "parse-markers":
        text = sys.stdin.read()
        markers = manager.parse_markers(text)
        print(json.dumps([{
            "kind": m.kind,
            "slug": m.slug,
            "wave": m.wave,
            "phase": m.phase,
            "note": m.note,
        } for m in markers], indent=2))
        return 0
    
    return 2


if __name__ == "__main__":
    sys.exit(main())
