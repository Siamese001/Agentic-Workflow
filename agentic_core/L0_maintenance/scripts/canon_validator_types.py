"""
Core types and dataclasses for Canon Validator.
ValidationContext is the shared memory (Blackboard) for all agents.
DependencyGraph and BudgetManager are infrastructure classes.
"""

import ast
import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List, Set

from dotenv import load_dotenv

# Load .env file from repo root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

ALLOWED_ROOT_FILES = {
    "README.md", "LICENSE", "pyproject.toml", "setup.py", "setup.cfg",
    "requirements.txt", "Makefile", ".gitignore", ".pre-commit-config.yaml",
    "CHANGELOG.md", "CONTRIBUTING.md", "conftest.py", "pytest.ini", "tox.ini",
    ".env.example", ".dockerignore", "Dockerfile", "docker-compose.yml",
    "canon_memory.json"
}

from agentic_core.prompts import (
    FEW_SHOT_CONCURRENCY,
    FEW_SHOT_GITOPS,
    FEW_SHOT_GLOBAL_REFACTOR,
    FEW_SHOT_HISTORIAN,
    FEW_SHOT_HYGIENE,
    FEW_SHOT_IMPORT_FIXES,
    FEW_SHOT_PROPERTY_TESTS,
    FEW_SHOT_REFLECTION_ENHANCED,
    FEW_SHOT_REFLECTION_STRATEGY,
    FEW_SHOT_SAFETY,
    FEW_SHOT_SHERLOCK,
    FEW_SHOT_STRATEGIC,
    FEW_SHOT_STYLE,
    FEW_SHOT_TESTPILOT,
    POSITIVE_INSTRUCTIONAL_CONTEXT,
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

    def __post_init__(self):
        """Initialize Tri-Brain infrastructure (MANDATORY MODE - fail if keys missing)."""

        print("   [CTX] 🧠 INITIALIZING TRI-BRAIN (MANDATORY MODE)...")
        self.python_files = get_python_files()
        self._load_memory()

        # Hard-Gate: Gemini (REQUIRED)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("CRITICAL: GOOGLE_API_KEY environment variable is missing.")
        try:
            import google.genai as genai
            self._client = genai.Client(api_key=api_key)
            self.intelligence_enabled = True
            print("      ✅ Gemini Connected")
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Gemini connection failed: {e}")

        # Hard-Gate: Redis (REQUIRED)
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            raise RuntimeError("CRITICAL: REDIS_URL environment variable is missing.")
        try:
            import redis as redis_lib
            self.redis_client = redis_lib.from_url(redis_url, decode_responses=True)
            self.redis_available = True
            print("      ✅ Redis Connected")
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Redis connection failed: {e}")

        # Hard-Gate: Pinecone (REQUIRED)
        pine_key = os.environ.get("PINECONE_API_KEY")
        if not pine_key:
            raise RuntimeError("CRITICAL: PINECONE_API_KEY environment variable is missing.")
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=pine_key)
            self.pinecone_index = pc.Index("canon-memory-l2")
            self.pinecone_available = True
            print("      ✅ Pinecone Connected")
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Pinecone connection failed: {e}")

    def _load_memory(self):
        """Load canon memory from disk."""
        memory_file = Path("canon_memory.json")
        if memory_file.exists():
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.file_hashes = data.get("file_hashes", {})
                    self.skip_files = set(data.get("skip_files", []))
                print("      ✅ Memory loaded from canon_memory.json")
            except Exception as e:
                print(f"      ⚠️  Memory load failed: {e}")

    def _save_memory(self):
        """Save canon memory to disk."""
        memory_file = Path("canon_memory.json")
        try:
            data = {
                "file_hashes": self.file_hashes,
                "skip_files": list(self.skip_files)
            }
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"      ⚠️  Memory save failed: {e}")

    def report(self, agent: str, key: int, passed: bool, details: Any = None):
        """Report validation result for a specific key to the blackboard."""
        status = "PASS" if passed else "FAIL"
        if not passed:
            print(f"   [{agent}] Key {key}: {status}")
        self.results[key] = {"passed": passed, "details": details or {}}

    def signal_deps_valid(self):
        """Signal that dependency checks passed."""
        self.signals.add("DEPS_VALID")
        print("   ✅ SIGNAL: DEPS_VALID asserted on Blackboard.")

    def signal_ast_valid(self):
        """Signal that AST checks passed."""
        self.signals.add("AST_VALID")
        print("   ✅ SIGNAL: AST_VALID asserted on Blackboard.")

    def signal_secure(self):
        """Signal that security checks passed."""
        self.signals.add("SECURE")
        print("   ✅ SIGNAL: SECURE asserted on Blackboard.")

    def signal_healing_cycle(self, cycle_number: int, max_cycles: int = 5):
        """Signal the start of a healing cycle."""
        print(f"   🔄 Healing Cycle {cycle_number}/{max_cycles}")

    def signal_convergence(self):
        """Signal that the validation has converged."""
        print("   ✅ Convergence achieved - no modifications in this cycle")
        self.signals.add("CONVERGENCE")

    def rollback_changes(self):
        """Rollback changes from file backups."""
        if self.file_backups:
            for file_path, content in self.file_backups.items():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ↩️ Rolled back: {file_path}")
                except Exception as e:
                    print(f"   ⚠️ Rollback failed for {file_path}: {e}")
            self.file_backups.clear()

    def inject_instruction(self, source_agent: str, instruction: str):
        """Add a guiding hint to the blackboard for downstream agents."""
        self.instructions.append(f"[{source_agent}] {instruction}")

    def refresh_graph(self):
        """Rebuilds graph after mutations."""
        self.code_graph.build(self.python_files)

    def set_current_agent(self, agent_name: str):
        """Sets the current agent for broadcast context."""
        self._current_agent = agent_name

    async def broadcast(self, event: dict):
        """L5 Live Reasoning Stream: Broadcast event to WebSocket clients."""
        if not self.websocket_clients:
            return
        message = json.dumps(event)
        disconnected = set()
        for ws in list(self.websocket_clients):
            try:
                await ws.send(message)
            except Exception:
                disconnected.add(ws)
        self.websocket_clients -= disconnected

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped based on memory."""
        if file_path in self.skip_files:
            return True
        current_hash = self.calculate_file_hash(file_path)
        if not current_hash:
            return False
        saved_hash = self.file_hashes.get(file_path)
        if saved_hash and saved_hash == current_hash:
            return self.results.get(self._get_file_key(file_path), {}).get("passed", False)
        return False

    def _get_file_key(self, file_path: str) -> int:
        """Get the validation key associated with a file."""
        return hash(file_path) % 50

    def _path_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        return file_path.replace(os.sep, ".").replace(".py", "")

    def write_compliant_file(self, path: str, content: str, dry_run: bool = False) -> bool:
        """Enforces Laws and Syntax Safety before writing to disk."""
        clean_content = content
        if "```" in clean_content:
            clean_content = re.sub(r"```[a-z]*\n", "", clean_content)
            clean_content = clean_content.replace("```", "")
        clean_content = clean_content.strip()

        if path.endswith(".py"):
            try:
                ast.parse(clean_content)
            except SyntaxError as e:
                print(f"   🛑 BLOCKED WRITE: Invalid syntax for {path}: {e}")
                return False

        # Normalize path separators for cross-platform compatibility using pathlib
        normalized_path = os.path.normpath(path)
        parts = Path(normalized_path).parts
        # Check for root level files (single component path)
        if len(parts) == 1 and parts[0] not in ALLOWED_ROOT_FILES:
            print(f"   🛑 BLOCKED: {path} is an illegal root file.")
            return False

        if dry_run:
            print(f"   [GOVERNOR] ✅ Dry run: File would be written compliantly")
            return True

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.file_backups[path] = f.read()
            except Exception:
                pass

        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            self.modified_files.add(path)
            return True
        except Exception as e:
            print(f"   ❌ Write Failed: {e}")
            return False

    async def recall_memory(self, query: str, top_k: int = 3) -> List[Dict]:
        """Recall similar memories from embeddings (stub - returns empty if no Pinecone)."""
        return []

    async def upsert_embedding(self, key: str, text: str, metadata: dict):
        """Learns from success by saving to Deep Brain (stub if no Pinecone)."""
        if not self.pinecone_available or not self.intelligence_enabled:
            return

    async def resilient_mutation(self, agent_name: str, task: str, code: str = "",
                                  file_path: str = None, *, max_attempts: int = 4,
                                  diff_mode: bool = False, min_confidence: float = 0.7) -> str:
        """Level 6 Mutation with retry logic. Returns original code if intelligence disabled."""
        if not self.intelligence_enabled:
            print(f"   [{agent_name}] ⚠️ Intelligence disabled - skipping mutation")
            return code

        current_code = code or ""
        for attempt in range(1, max_attempts + 1):
            try:
                if not self.budget.check_budget():
                    return current_code

                prompt = f"{self.POSITIVE_INSTRUCTIONAL_CONTEXT}\n\nAgent: {agent_name}\nTask: {task}\nContext:\n{current_code[:4000]}"

                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self.model_id,
                    contents=[prompt]
                )

                self.budget.track(prompt, response.text)
                result_text = self._clean_llm_code(response.text)

                if result_text.strip() and (file_path and file_path.endswith('.py')):
                    ast.parse(result_text)

                self.mutation_stats["success"] += 1
                self.mutation_stats["total"] += 1
                print(f"   [{agent_name}] ✅ Success (Attempt {attempt})")
                return result_text

            except Exception as e:
                print(f"   [{agent_name}] ⚠️ Attempt {attempt} Error: {e}")
                self.mutation_stats["total"] += 1
                if "429" in str(e):
                    await asyncio.sleep(2 ** attempt)

        return current_code

    def _clean_llm_code(self, raw_code: str) -> str:
        """Extracts code from Chain-of-Thought responses."""
        raw_code = re.sub(r"<reasoning>.*?</reasoning>", "", raw_code, flags=re.DOTALL)
        code_match = re.search(r"```(?:python)?\n(.*?)```", raw_code, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        if raw_code.strip().startswith("```"):
            return raw_code.strip().strip("`").replace("python", "", 1).strip()
        return raw_code.strip()