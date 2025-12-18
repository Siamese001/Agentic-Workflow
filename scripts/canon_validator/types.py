"""
Core types and dataclasses for Canon Validator.
ValidationContext is the shared memory (Blackboard) for all agents.
DependencyGraph and BudgetManager are infrastructure classes.
"""

import ast
import asyncio
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from .prompts import (
    POSITIVE_INSTRUCTIONAL_CONTEXT,
    FEW_SHOT_GLOBAL_REFACTOR,
    FEW_SHOT_IMPORT_FIXES,
    FEW_SHOT_PROPERTY_TESTS,
    FEW_SHOT_REFLECTION_STRATEGY,
    FEW_SHOT_CONCURRENCY,
    FEW_SHOT_SAFETY,
    FEW_SHOT_STYLE,
    FEW_SHOT_HYGIENE,
    FEW_SHOT_HISTORIAN,
    FEW_SHOT_TESTPILOT,
    FEW_SHOT_STRATEGIC,
    FEW_SHOT_REFLECTION_ENHANCED,
    FEW_SHOT_GITOPS,
    FEW_SHOT_SHERLOCK,
)


class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""

    def __init__(self):
        self.graph: Dict[str, Dict[str, List[str]]] = {}
        self.reverse_graph: Dict[str, List[str]] = {}

    def build(self, files: List[str]):
        """Build the dependency graph from a list of Python files."""
        print("   🕸️ Building Holistic Code Graph...")
        for file_path in files:
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]["imports"].append(node.module)
                    elif isinstance(node, ast.ClassDef):
                        self.graph[file_path]["classes"].append(node.name)
            except Exception:
                pass

        # Build Reverse Index for rapid lookup
        for file, data in self.graph.items():
            for imp in data["imports"]:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> List[str]:
        """Returns files that import modules defined in file_path."""
        impacted = set()
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")

        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])

        return list(impacted)


class BudgetManager:
    """Tracks estimated token usage and enforces stops."""

    def __init__(self, limit_usd: float = 2.0):
        self.limit = limit_usd
        self.spent = 0.0
        self.input_tokens = 0
        self.output_tokens = 0

    def track(self, prompt: str, response: str):
        """Track token usage from a prompt/response pair."""
        in_t = len(prompt) / 4
        out_t = len(response) / 4
        self.input_tokens += in_t
        self.output_tokens += out_t
        cost = (in_t / 1_000_000 * 0.50) + (out_t / 1_000_000 * 1.50)
        self.spent += cost

    def check_budget(self) -> bool:
        """Check if budget is exceeded."""
        if self.spent > self.limit:
            print(f"   💸 BUDGET EXCEEDED (${self.spent:.4f} / ${self.limit}). Halting Intelligence.")
            return False
        return True

    def get_status(self) -> str:
        """Get current budget status string."""
        return f"${self.spent:.4f} / ${self.limit} ({self.input_tokens:.0f} in, {self.output_tokens:.0f} out)"


@dataclass
class ValidationContext:
    """Shared memory for all agents with Tri-Brain infrastructure and persistence."""
    
    # Core state
    results: Dict[int, Any] = field(default_factory=dict)
    signals: Set[str] = field(default_factory=set)
    instructions: List[str] = field(default_factory=list)
    modified_files: Set[str] = field(default_factory=set)
    python_files: List[str] = field(default_factory=list)
    refactor_plans: Dict[str, Any] = field(default_factory=dict)

    # Memory persistence
    memory_file: Path = field(default_factory=lambda: Path("canon_memory.json"))
    file_hashes: Dict[str, str] = field(default_factory=dict)
    skip_files: Set[str] = field(default_factory=set)
    flapping_files: Set[str] = field(default_factory=set)

    # Tri-Brain Infrastructure
    model_id: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    _client: Any = field(default=None, init=False)
    intelligence_enabled: bool = field(default=False, init=False)

    # Hot Brain (Redis)
    redis_client: Any = field(default=None, init=False)
    redis_available: bool = field(default=False, init=False)

    # Deep Brain (Pinecone)
    pinecone_client: Any = field(default=None, init=False)
    pinecone_index: Any = field(default=None, init=False)
    pinecone_available: bool = field(default=False, init=False)

    # Local fallbacks
    _local_cache: Dict[str, Any] = field(default_factory=dict)
    _local_embeddings: List[Dict] = field(default_factory=list)

    # L5+ Few-Shot Prompts (reference from prompts.py)
    POSITIVE_INSTRUCTIONAL_CONTEXT: str = field(default_factory=lambda: POSITIVE_INSTRUCTIONAL_CONTEXT)
    FEW_SHOT_GLOBAL_REFACTOR: str = field(default_factory=lambda: FEW_SHOT_GLOBAL_REFACTOR)
    FEW_SHOT_IMPORT_FIXES: str = field(default_factory=lambda: FEW_SHOT_IMPORT_FIXES)
    FEW_SHOT_PROPERTY_TESTS: str = field(default_factory=lambda: FEW_SHOT_PROPERTY_TESTS)
    FEW_SHOT_REFLECTION_STRATEGY: str = field(default_factory=lambda: FEW_SHOT_REFLECTION_STRATEGY)
    FEW_SHOT_CONCURRENCY: str = field(default_factory=lambda: FEW_SHOT_CONCURRENCY)
    FEW_SHOT_SAFETY: str = field(default_factory=lambda: FEW_SHOT_SAFETY)
    FEW_SHOT_STYLE: str = field(default_factory=lambda: FEW_SHOT_STYLE)
    FEW_SHOT_HYGIENE: str = field(default_factory=lambda: FEW_SHOT_HYGIENE)
    FEW_SHOT_HISTORIAN: str = field(default_factory=lambda: FEW_SHOT_HISTORIAN)
    FEW_SHOT_TESTPILOT: str = field(default_factory=lambda: FEW_SHOT_TESTPILOT)
    FEW_SHOT_STRATEGIC: str = field(default_factory=lambda: FEW_SHOT_STRATEGIC)
    FEW_SHOT_REFLECTION_ENHANCED: str = field(default_factory=lambda: FEW_SHOT_REFLECTION_ENHANCED)
    FEW_SHOT_GITOPS: str = field(default_factory=lambda: FEW_SHOT_GITOPS)
    FEW_SHOT_SHERLOCK: str = field(default_factory=lambda: FEW_SHOT_SHERLOCK)

    # Level 5: Learning Infrastructure
    mutation_stats: Dict[str, int] = field(default_factory=lambda: {"success": 0, "total": 0})
    successful_traces: List[Dict] = field(default_factory=list)
    strategic_plan: str = field(default=None)

    # Level 5+: Safety Net (Automatic Rollback)
    file_backups: Dict[str, str] = field(default_factory=dict)

    # Level 5: The Streamer - Live Reasoning Broadcast
    stream_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    stream_task: asyncio.Task = field(default=None)
    _current_agent: str = field(default="System")
    _streamer_initialized: bool = field(default=False)

    # L5 Live Reasoning Stream via WebSockets
    websocket_clients: Set[Any] = field(default_factory=set)

    # Level 6: Sovereign Architecture
    code_graph: DependencyGraph = field(default_factory=DependencyGraph)
    budget: BudgetManager = field(default_factory=lambda: BudgetManager(limit_usd=2.0))

    @property
    def client(self):
        """Access to Gemini client for backward compatibility."""
        return self._client

    def report(self, agent: str, key: int, passed: bool, details: Any = None):
        """Report validation result for a specific key to the blackboard.
        
        Used by all agents to record pass/fail status.
        """
        status = "PASS" if passed else "FAIL"
        if not passed:
            print(f"   [{agent}] Key {key}: {status}")
        self.results[key] = {
            "passed": passed,
            "details": details or {}
        }
