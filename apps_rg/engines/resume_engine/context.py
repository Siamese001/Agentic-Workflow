from __future__ import annotations
"""
ResumeEngineContext - Central state management for autonomous resume generation.

This module provides the core context class that maintains state across all agents,
including signals, results, backups, budget tracking, and learning data.
"""
from typing import Any, Optional, Protocol, Dict, List
import time


import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Set

from dotenv import load_dotenv

load_dotenv()


class BudgetManager:
    """Manages token budget and cost tracking for LLM calls."""

    def __init__(self, max_cost_usd: float = 2.0):
        from agentic_core.config.P1_core.sovereign_config import config
        
        self.max_cost = max_cost_usd
        self.current_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

        # Pricing flows from Sovereign Constitution (Phase 8A)
        self.pricing = config.MODEL_PRICING
        self.default_model = config.DEFAULT_COST_MODEL

    def check_budget(self) -> bool:
        """Returns True if budget is available."""
        return self.current_cost < self.max_cost

    def get_remaining_budget(self) -> float:
        """Returns remaining budget in USD."""
        return max(0.0, self.max_cost - self.current_cost)

    def track_tokens(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track token usage and return cost for this call."""
        pricing = self.pricing.get(model, {"input": 0.10, "output": 0.30})

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        call_cost = input_cost + output_cost

        self.current_cost += call_cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.call_count += 1

        return call_cost

    def get_stats(self) -> Dict[str, Any]:
        """Returns budget statistics."""
        return {
            "current_cost_usd": round(self.current_cost, 6),
            "max_cost_usd": self.max_cost,
            "remaining_usd": round(self.get_remaining_budget(), 6),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "call_count": self.call_count,
            "budget_exhausted": not self.check_budget(),
        }


class SectionDependencyGraph:
    """Tracks dependencies between resume sections for blast radius analysis."""

    def __init__(self):
        self.graph: Dict[str, List[str]] = {}
        self._build_default_graph()

    def _build_default_graph(self):
        """Build default resume section dependency graph."""
        # Section -> sections that depend on it
        self.graph = {
            "contact": [],  # No dependencies
            "summary": ["experience", "skills", "education"],  # Summary depends on these
            "experience": [],  # Core section
            "skills": ["experience"],  # Skills derived from experience
            "education": [],  # Core section
            "projects": ["skills"],  # Projects showcase skills
            "certifications": ["skills"],  # Certifications validate skills
            "achievements": ["experience"],  # Achievements from experience
        }

    def get_impact_radius(self, modified_section: str) -> List[str]:
        """Returns sections that may be impacted by changes to the given section."""
        impacted = []
        for section, dependencies in self.graph.items():
            if modified_section in dependencies:
                impacted.append(section)
        return impacted

    def get_dependencies(self, section: str) -> List[str]:
        """Returns sections that the given section depends on."""
        return self.graph.get(section, [])

    def add_dependency(self, section: str, depends_on: str):
        """Add a dependency relationship."""
        if section not in self.graph:
            self.graph[section] = []
        if depends_on not in self.graph[section]:
            self.graph[section].append(depends_on)


@dataclass
class ResumeEngineContext:
    """
    Central context for autonomous resume generation.

    Maintains state across all agents including:
    - LLM client configuration
    - Signal-based communication
    - Results tracking
    - Section backups for rollback
    - Budget management
    - Learning data
    """

    # Configuration
    model_id: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"))

    # LLM Client (initialized in __post_init__)
    client: Any = field(default=None, init=False)
    intelligence_enabled: bool = field(default=False, init=False)

    # Signal-based communication between agents
    signals: Set[str] = field(default_factory=set)

    # Modified sections tracking
    modified_sections: Set[str] = field(default_factory=set)

    # Results from each agent
    results: Dict[str, Any] = field(default_factory=dict)

    # Section backups for rollback
    section_backups: Dict[str, Any] = field(default_factory=dict)

    # Current resume state
    current_resume: Dict[str, Any] = field(default_factory=dict)

    # Job description being targeted
    JobDescription: str = field(default="")

    # User profile data
    user_profile: Dict[str, Any] = field(default_factory=dict)

    # Learning data
    successful_generations: List[Dict] = field(default_factory=list)
    generation_stats: Dict[str, int] = field(default_factory=lambda: {"total": 0, "success": 0, "failed": 0})

    # Dynamic instructions for agent steering
    instructions: List[str] = field(default_factory=list)

    # Budget management
    budget: BudgetManager = field(default=None, init=False)

    # Section dependency graph
    section_graph: SectionDependencyGraph = field(default=None, init=False)

    # Healing cycle tracking
    current_cycle: int = field(default=0, init=False)
    max_cycles: int = field(default=5, init=False)

    # Impact zone for blast radius
    impact_zone: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Initialize components after dataclass creation."""
        self.budget = BudgetManager(max_cost_usd=2.0)
        self.section_graph = SectionDependencyGraph()
        self._init_llm_client()

    def _init_llm_client(self):
        """Initialize the LLM client."""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.client = genai
                self.intelligence_enabled = True
                print(f"   🧠 Resume Engine: Gemini initialized ({self.model_id})")
            else:
                print("   ⚠️ Resume Engine: No API key found, running in limited mode")
        except ImportError:
            print("   ⚠️ Resume Engine: google-generativeai not installed")
        except Exception as e:
            print(f"   ⚠️ Resume Engine: Failed to initialize LLM: {e}")

    def signal_healing_cycle(self, cycle: int):
        """Signal the start of a new healing cycle."""
        self.current_cycle = cycle
        print(f"   🔄 Healing Cycle {cycle}/{self.max_cycles}")

    def add_signal(self, signal: str):
        """Add a signal for inter-agent communication."""
        self.signals.add(signal)

    def remove_signal(self, signal: str):
        """Remove a signal."""
        self.signals.discard(signal)

    def has_signal(self, signal: str) -> bool:
        """Check if a signal is present."""
        return signal in self.signals

    def backup_section(self, section_name: str, content: Any):
        """Backup a section before modification."""
        if section_name not in self.section_backups:
            self.section_backups[section_name] = content

    def rollback_section(self, section_name: str) -> bool:
        """Rollback a section to its backup."""
        if section_name in self.section_backups:
            self.current_resume[section_name] = self.section_backups[section_name]
            del self.section_backups[section_name]
            return True
        return False

    def rollback_all(self):
        """Rollback all sections to their backups."""
        for section_name in list(self.section_backups.keys()):
            self.rollback_section(section_name)
        self.modified_sections.clear()
        print("   ⏪ Rolled back all sections")

    def update_section(self, section_name: str, content: Any):
        """Update a section with backup."""
        # Backup first
        if section_name in self.current_resume:
            self.backup_section(section_name, self.current_resume[section_name])

        # Update
        self.current_resume[section_name] = content
        self.modified_sections.add(section_name)

        # Calculate blast radius
        impacted = self.section_graph.get_impact_radius(section_name)
        self.impact_zone.update(impacted)

    def record_result(self, agent_name: str, passed: bool, details: str = "", data: Any = None):
        """Record an agent's result."""
        self.results[agent_name] = {
            "passed": passed,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

    def get_failed_results(self) -> Dict[str, Any]:
        """Get all failed results."""
        return {k: v for k, v in self.results.items() if not v.get("passed", True)}

    def is_converged(self) -> bool:
        """Check if the system has converged (no failures, no modifications needed)."""
        has_failures = any(not r.get("passed", True) for r in self.results.values())
        has_critical_signals = any(s in self.signals for s in [
            "QUALITY_FAILURE", "HALLUCINATION_DETECTED", "ATS_FAILURE", "BRAND_VIOLATION"
        ])
        return not has_failures and not has_critical_signals

    def record_success(self, resume_data: Dict[str, Any], quality_score: float):
        """Record a successful generation for learning."""
        self.generation_stats["success"] += 1
        self.successful_generations.append({
            "resume_sections": list(resume_data.keys()),
            "quality_score": quality_score,
            "job_description_preview": self.JobDescription[:200] if self.JobDescription else "",
            "timestamp": datetime.now().isoformat(),
        })

    def record_failure(self, reason: str):
        """Record a failed generation."""
        self.generation_stats["failed"] += 1
        self.generation_stats["total"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "generation_stats": self.generation_stats,
            "budget_stats": self.budget.get_stats(),
            "current_cycle": self.current_cycle,
            "signals": list(self.signals),
            "modified_sections": list(self.modified_sections),
            "impact_zone": list(self.impact_zone),
            "failed_agents": list(self.get_failed_results().keys()),
        }
