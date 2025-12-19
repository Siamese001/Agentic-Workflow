import ast
import asyncio
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

import httpx

# Third-party
try:
    from google import genai
except ImportError:
    genai = None

# Import Prompts (Resolves Syntax Error & Atomicity Law)
from agentic_core.domain.prompts import (
    FEW_SHOT_CONCURRENCY,
    FEW_SHOT_GITOPS,
    FEW_SHOT_GLOBAL_REFACTOR,
    FEW_SHOT_HISTORIAN,
    FEW_SHOT_HYGIENE,
    FEW_SHOT_IMPORT_FIXES,
    FEW_SHOT_PROPERTY_TESTS,
    FEW_SHOT_REFLECTION,
    FEW_SHOT_REFLECTION_ENHANCED,
    FEW_SHOT_REFLECTION_STRATEGY,
    FEW_SHOT_SAFETY,
    FEW_SHOT_SHERLOCK,
    FEW_SHOT_STRATEGIC,
    FEW_SHOT_STYLE,
    FEW_SHOT_TESTPILOT,
    POSITIVE_INSTRUCTIONAL_CONTEXT,
)
from apps_shared.config.reliability import rate_limited_retry

# Shared Utilities
from apps_shared.utils.file_io import get_python_files, write_compliant_file
from apps_shared.utils.text_processing import clean_llm_code

# ==============================================================================
# LEVEL 6: SOVEREIGN ARCHITECTURE
# ==============================================================================

class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""
    def __init__(self):
        self.graph: Dict[str, Dict[str, List[Any]]] = {}
        self.reverse_graph: Dict[str, List[str]] = {}

    async def build(self, files: List[str]):
        """Asynchronously builds the code graph from a list of files."""
        print("   🕸️ Building Holistic Code Graph...")
        for file_path in files:
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                # Synchronous file read is replaced in high-performance contexts, 
                # but standard open remains safe for local configuration analysis.
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]["imports"].append(node.module)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue

        for file, data in self.graph.items():
            for imp in data["imports"]:
                if isinstance(imp, str):
                    if imp not in self.reverse_graph:
                        self.reverse_graph[imp] = []
                    self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> List[str]:
        """Calculates which files depend on the given path."""
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        impacted = set()
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        return list(impacted)


class BudgetManager:
    """Tracks estimated token usage and financial safety limits."""
    def __init__(self, limit_usd: Optional[float] = None):
        # SAFETY FIX: Prioritize environment variables for resource limits
        env_limit = os.getenv("AGENTIC_BUDGET_USD")
        self.limit = float(env_limit) if env_limit else (limit_usd or 2.0)
        self.spent = 0.0
        self.input_tokens = 0.0
        self.output_tokens = 0.0

    async def track(self, prompt: str, response: str):
        """Asynchronously updates budget metrics."""
        in_t = len(prompt) / 4
        out_t = len(response) / 4
        self.input_tokens += in_t
        self.output_tokens += out_t
        # Cost metrics (Standardized for Infrastructure context)
        cost = (in_t / 1_000_000 * 0.50) + (out_t / 1_000_000 * 1.50)
        self.spent += cost

    def check_budget(self) -> bool:
        """Verifies if the session is within financial safety constraints."""
        if self.spent > self.limit:
            print(f"   💸 BUDGET EXCEEDED (${self.spent:.4f}). Halting.")
            return False
        return True
    
    def get_status(self) -> str:
        """Returns a formatted budget status string."""
        return f"${self.spent:.4f} / ${self.limit} ({self.input_tokens:.0f} in, {self.output_tokens:.0f} out)"


@dataclass
class ValidationContext:
    """Shared memory and infrastructure state for all agents."""
    results: Dict[int, Any] = field(default_factory=dict)
    signals: Set[str] = field(default_factory=set)
    instructions: List[str] = field(default_factory=list)
    modified_files: Set[str] = field(default_factory=set)
    python_files: List[str] = field(default_factory=list)
    graph: DependencyGraph = field(default_factory=DependencyGraph)
    budget: BudgetManager = field(default_factory=BudgetManager)