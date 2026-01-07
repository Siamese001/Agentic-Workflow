from __future__ import annotations
"""
Outreach Engine Context - Shared State for Autonomous Agents

Provides the shared context and state management for the autonomous
outreach engine, including campaign state, signals, and budget tracking.
"""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field
import time


import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


@dataclass
class OutreachBudgetManager:
    """Manages budget for outreach operations."""

    max_budget: float = 1.0
    current_cost: float = 0.0

    # Cost rates
    email_cost: float = 0.001
    api_call_cost: float = 0.0001
    llm_call_cost: float = 0.01

    def record_email(self, count: int = 1):
        """Record email send cost."""
        self.current_cost += self.email_cost * count

    def record_api_call(self, count: int = 1):
        """Record API call cost."""
        self.current_cost += self.api_call_cost * count

    def record_llm_call(self, tokens: int = 1000):
        """Record LLM call cost."""
        self.current_cost += self.llm_call_cost * (tokens / 1000)

    def check_budget(self) -> bool:
        """Check if budget is available."""
        return self.current_cost < self.max_budget

    def get_remaining(self) -> float:
        """Get remaining budget."""
        return max(0, self.max_budget - self.current_cost)

    def reset(self):
        """Reset budget tracking."""
        self.current_cost = 0.0


class OutreachEngineContext:
    """
    Shared context for all outreach agents.

    Manages:
    - Current campaign state
    - Lead/contact data
    - Signals and results
    - Budget tracking
    - Section backups for rollback
    """

    def __init__(self):
        # Campaign state
        self.current_campaign: Dict[str, Any] = {}
        self.leads: List[Dict[str, Any]] = []
        self.contacts: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, Any]] = []

        # Target information
        self.target_company: Optional[str] = None
        self.target_role: Optional[str] = None
        self.user_profile: Optional[Dict[str, Any]] = None

        # Signals and results
        self.signals: Set[str] = set()
        self.results: Dict[str, Any] = {}

        # Instructions from learning
        self.instructions: List[str] = []

        # Budget management
        self.budget = OutreachBudgetManager()

        # Backup for rollback
        self.campaign_backups: Dict[str, Any] = {}
        self.modified_sections: Set[str] = set()

        # Impact tracking
        self.impact_zone: Set[str] = set()

        # Gemini client initialization
        self._init_gemini()

    def _init_gemini(self):
        """Initialize Gemini client if available."""
        try:
            import google.generativeai as genai

            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model_id = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
                self.gemini_model = genai.GenerativeModel(model_id)
                self.intelligence_enabled = True
                print(f"   🧠 Outreach Engine: Gemini initialized ({model_id})")
            else:
                self.gemini_model = None
                self.intelligence_enabled = False
        except ImportError:
            self.gemini_model = None
            self.intelligence_enabled = False

    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self.signals.add(signal)

    def remove_signal(self, signal: str):
        """Remove a signal from the context."""
        self.signals.discard(signal)

    def has_signal(self, signal: str) -> bool:
        """Check if a signal is present."""
        return signal in self.signals

    def clear_signals(self):
        """Clear all signals."""
        self.signals.clear()

    def record_result(self, agent_name: str, passed: bool, details: str = ""):
        """Record an agent result."""
        self.results[agent_name] = {
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

    def is_converged(self) -> bool:
        """Check if all agents passed and no signals remain."""
        if self.signals:
            return False

        for result in self.results.values():
            if not result.get("passed", False):
                return False

        return True

    def backup_campaign(self, key: str = "default"):
        """Backup current campaign state."""
        import copy
        self.campaign_backups[key] = {
            "campaign": copy.deepcopy(self.current_campaign),
            "leads": copy.deepcopy(self.leads),
            "contacts": copy.deepcopy(self.contacts),
            "messages": copy.deepcopy(self.messages),
        }

    def restore_campaign(self, key: str = "default"):
        """Restore campaign from backup."""
        if key in self.campaign_backups:
            backup = self.campaign_backups[key]
            self.current_campaign = backup["campaign"]
            self.leads = backup["leads"]
            self.contacts = backup["contacts"]
            self.messages = backup["messages"]

    def rollback_all(self):
        """Rollback all changes."""
        if "default" in self.campaign_backups:
            self.restore_campaign("default")
        self.modified_sections.clear()

    def signal_healing_cycle(self, cycle_number: int):
        """Signal the start of a healing cycle."""
        print(f"   🔄 Healing Cycle {cycle_number}/{5}")

    def get_campaign_summary(self) -> str:
        """Get a summary of the current campaign."""
        return f"""
Campaign: {self.current_campaign.get('name', 'Unnamed')}
Target: {self.target_company or 'Not set'}
Leads: {len(self.leads)}
Contacts: {len(self.contacts)}
Messages: {len(self.messages)}
Signals: {list(self.signals)}
"""

    def inject_instruction(self, instruction: str, priority: int = 5):
        """Inject an instruction for agents."""
        self.instructions.append({
            "text": instruction,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
        })
        # Sort by priority (higher first)
        self.instructions.sort(key=lambda x: x.get("priority", 0), reverse=True)

    def get_instructions(self) -> List[str]:
        """Get all instructions as text."""
        return [i["text"] for i in self.instructions if isinstance(i, dict)]
