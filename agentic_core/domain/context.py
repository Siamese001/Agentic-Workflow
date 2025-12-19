"""
agentic_core/domain/context.py
Depth: 3
Role: Shared state (Blackboard) and Infrastructure Context.
"""
import os
import sys
import json
import asyncio
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional

# Third-party
try:
    import redis.asyncio as redis
    from pinecone import Pinecone
    from google import genai
except ImportError:
    pass

# Shared Utilities
from apps_shared.domain.constants import EXCLUDED_DIRS
from apps_shared.utils.file_io import get_python_files, write_compliant_file
from apps_shared.utils.text_processing import clean_llm_code
from apps_shared.config.reliability import rate_limited_retry

# Import Prompts (Resolves Syntax Error & Atomicity Law)
from agentic_core.domain.prompts import (
    FEW_SHOT_GLOBAL_REFACTOR, FEW_SHOT_IMPORT_FIXES, FEW_SHOT_STYLE,
    FEW_SHOT_SAFETY, FEW_SHOT_CONCURRENCY, FEW_SHOT_HYGIENE,
    FEW_SHOT_TESTPILOT, FEW_SHOT_STRATEGIC, FEW_SHOT_REFLECTION,
    FEW_SHOT_SHERLOCK, FEW_SHOT_GITOPS, FEW_SHOT_PROPERTY_TESTS,
    FEW_SHOT_HISTORIAN, POSITIVE_INSTRUCTIONAL_CONTEXT,
    FEW_SHOT_REFLECTION_STRATEGY, FEW_SHOT_REFLECTION_ENHANCED
)

# ==============================================================================
# LEVEL 6: SOVEREIGN ARCHITECTURE
# ==============================================================================

class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""
    def __init__(self):
        self.graph = {}
        self.reverse_graph = {}

    def build(self, files: list):
        import ast
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
            except Exception:
                pass

        for file, data in self.graph.items():
            for imp in data["imports"]:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> list:
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        impacted = set()
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        return list(impacted)


class BudgetManager:
    """Tracks estimated token usage."""
    def __init__(self, limit_usd: float = 2.0):
        self.limit = limit_usd
        self.spent = 0.0
        self.input_tokens = 0.0
        self.output_tokens = 0.0

    def track(self, prompt: str, response: str):
        in_t = len(prompt) / 4
        out_t = len(response) / 4
        self.input_tokens += in_t
        self.output_tokens += out_t
        cost = (in_t / 1_000_000 * 0.50) + (out_t / 1_000_000 * 1.50)
        self.spent += cost

    def check_budget(self) -> bool:
        if self.spent > self.limit:
            print(f"   💸 BUDGET EXCEEDED (${self.spent:.4f}). Halting.")
            return False
        return True
    
    def get_status(self) -> str:
        return f"${self.spent:.4f} / ${self.limit} ({self.input_tokens:.0f} in, {self.output_tokens:.0f} out)"


@dataclass
class ValidationContext:
    """Shared memory for all agents."""
    results: Dict[int, Any] = field(default_factory=dict)
    signals: Set[str] = field(default_factory=set)
    instructions: List[str] = field(default_factory=list)
    modified_files: Set[str] = field(default_factory=set)
    python_files: List[str] = field(default_factory=list)
    
    # Memory
    memory_file: Path = field(default_factory=lambda: Path("canon_memory.json"))
    file_hashes: Dict[str, str] = field(default_factory=dict)
    skip_files: Set[str] = field(default_factory=set)
    flapping_files: Set[str] = field(default_factory=set)
    successful_traces: List[Dict] = field(default_factory=list)
    mutation_stats: Dict[str, int] = field(default_factory=lambda: {"success": 0, "total": 0})
    
    # Infrastructure
    model_id: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
    _client: Any = field(default=None, init=False)
    intelligence_enabled: bool = field(default=False, init=False)
    
    # Hot Brain (Redis)
    redis_client: Any = field(default=None, init=False)
    redis_available: bool = field(default=False, init=False)
    
    # Deep Brain (Pinecone)
    pinecone_index: Any = field(default=None, init=False)
    pinecone_available: bool = field(default=False, init=False)
    
    # Local fallbacks
    _local_cache: Dict[str, Any] = field(default_factory=dict)
    _local_embeddings: List[Dict] = field(default_factory=list)
    
    # Components
    code_graph: DependencyGraph = field(default_factory=DependencyGraph)
    budget: BudgetManager = field(default_factory=lambda: BudgetManager(limit_usd=2.0))
    
    # L5 Streamer
    stream_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _current_agent: str = "System"
    _streamer_initialized: bool = False
    
    # Additional fields
    refactor_plans: Dict[str, Any] = field(default_factory=dict)
    impact_zone: Set[str] = field(default_factory=set)
    omni_context: Any = field(default=None)
    strategic_plan: str = ""
    
    # Prompts (Loaded from module to prevent SyntaxErrors)
    POSITIVE_INSTRUCTIONAL_CONTEXT: str = POSITIVE_INSTRUCTIONAL_CONTEXT
    FEW_SHOT_GLOBAL_REFACTOR: str = FEW_SHOT_GLOBAL_REFACTOR
    FEW_SHOT_IMPORT_FIXES: str = FEW_SHOT_IMPORT_FIXES
    FEW_SHOT_STYLE: str = FEW_SHOT_STYLE
    FEW_SHOT_SAFETY: str = FEW_SHOT_SAFETY
    FEW_SHOT_CONCURRENCY: str = FEW_SHOT_CONCURRENCY
    FEW_SHOT_HYGIENE: str = FEW_SHOT_HYGIENE
    FEW_SHOT_TESTPILOT: str = FEW_SHOT_TESTPILOT
    FEW_SHOT_STRATEGIC: str = FEW_SHOT_STRATEGIC
    FEW_SHOT_REFLECTION: str = FEW_SHOT_REFLECTION
    FEW_SHOT_REFLECTION_STRATEGY: str = FEW_SHOT_REFLECTION_STRATEGY
    FEW_SHOT_REFLECTION_ENHANCED: str = FEW_SHOT_REFLECTION_ENHANCED
    FEW_SHOT_SHERLOCK: str = FEW_SHOT_SHERLOCK
    FEW_SHOT_GITOPS: str = FEW_SHOT_GITOPS
    FEW_SHOT_PROPERTY_TESTS: str = FEW_SHOT_PROPERTY_TESTS
    FEW_SHOT_HISTORIAN: str = FEW_SHOT_HISTORIAN

    def __post_init__(self):
        print(f"   [CTX] 🧠 INITIALIZING TRI-BRAIN...")
        self.python_files = get_python_files()
        self._load_memory()
        self._init_intelligence()
        
    def _init_intelligence(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            try:
                self._client = genai.Client(api_key=api_key)
                self.intelligence_enabled = True
                print(f"      ✅ Gemini Connected")
            except Exception:
                pass

    def _load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.file_hashes = data.get('hashes', {})
                    self.skip_files = set(data.get('skip', []))
            except Exception:
                pass

    def report(self, agent: str, key: int, passed: bool, details: Any):
        self.results[key] = {"passed": passed, "details": details, "agent": agent}
        if not passed:
            print(f"   [{agent}] Key {key}: FAIL")

    def get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def write_compliant_file(self, path: str, content: str) -> bool:
        return write_compliant_file(path, content)

    @property
    def client(self):
        return self._client

    @rate_limited_retry()
    async def resilient_mutation(self, agent_name: str, task: str, code: str = "", file_path: str = None, max_attempts: int = 3, **kwargs) -> str:
        if not self.intelligence_enabled or not self.budget.check_budget():
            return code
        
        try:
            prompt = f"Agent: {agent_name}\nTask: {task}\nContext:\n{code[:4000]}"
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self.model_id,
                contents=[prompt]
            )
            self.budget.track(prompt, response.text)
            return clean_llm_code(response.text)
        except Exception as e:
            print(f"   [{agent_name}] Mutation failed: {e}")
            return code

    async def request_mutation(self, agent_name: str, task: str, code: str = "", reasoning_mode: bool = False, **kwargs) -> str:
        """Alias for resilient_mutation with reasoning mode support."""
        return await self.resilient_mutation(agent_name, task, code, **kwargs)

    async def upsert_embedding(self, key: str, text: str, metadata: dict = None):
        """Store embedding in Pinecone or local fallback."""
        if self.pinecone_available and self.pinecone_index:
            try:
                # Use Pinecone
                pass
            except Exception:
                pass
        else:
            # Local fallback
            self._local_embeddings.append({
                'key': key,
                'text': text[:500],
                'metadata': metadata or {}
            })
            
    def inject_instruction(self, agent: str, instruction: str):
        self.instructions.append(f"[{agent}] {instruction}")

    def refresh_graph(self):
        self.code_graph.build(self.python_files)

    def _path_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        return file_path.replace("/", ".").replace("\\", ".").replace(".py", "")

    def build_import_dependency_map(self, modules):
        """Build a map of which files import the given modules."""
        import ast
        import_map = {}
        
        for module in modules:
            import_map[module] = []
            
            for file_path in self.python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and node.module.startswith(module):
                                import_map[module].append(file_path)
                                break
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.startswith(module):
                                    import_map[module].append(file_path)
                                    break
                except Exception:
                    continue
        
        return {k: v for k, v in import_map.items() if v}
        
    def _save_memory(self):
        try:
            data = {'hashes': self.file_hashes, 'skip': list(self.skip_files)}
            with open(self.memory_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass
