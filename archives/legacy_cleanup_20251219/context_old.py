"""
agentic_core/domain/context.py
Depth: 3
Role: Shared state (Blackboard) and Infrastructure Context.
"""
import asyncio
import datetime
import hashlib
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Third-party hard-gates (Tri-Brain)
try:
    import redis.asyncio as redis
    from google import genai
    from pinecone import Pinecone
except ImportError:
    pass  # Handled by dependency checks in runner

from apps_shared.config.reliability import rate_limited_retry

# Shared Utilities
from apps_shared.domain.constants import EXCLUDED_DIRS
from apps_shared.utils.file_io import get_python_files, write_compliant_file
from apps_shared.utils.text_processing_validator import clean_llm_code

# ==============================================================================
# LEVEL 6: SOVEREIGN ARCHITECTURE
# ==============================================================================

class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""
    def __init__(self):
        self.graph = {}  # file_path -> {imports: [], defined_classes: []}
        self.reverse_graph = {}  # dependency -> [file_paths]

    def build(self, files: list):
        import ast
        print("   🕸️ Building Holistic Code Graph...")
        for file_path in files:
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                # Extract Imports and Definitions
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
                pass  # Skip unparseable files

        # Build Reverse Index for rapid lookup
        for file, data in self.graph.items():
            for imp in data["imports"]:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> list:
        """Returns files that import modules defined in file_path."""
        impacted = set()
        # Heuristic: map file path back to module name (e.g. apps/utils.py -> apps.utils)
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")

        # Direct imports
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
        in_t = len(prompt) / 4  # Rough estimate
        out_t = len(response) / 4
        self.input_tokens += in_t
        self.output_tokens += out_t

        # Calculate Cost ($0.50 / 1M input, $1.50 / 1M output)
        cost = (in_t / 1_000_000 * 0.50) + (out_t / 1_000_000 * 1.50)
        self.spent += cost

    def check_budget(self) -> bool:
        if self.spent > self.limit:
            print(f"   💸 BUDGET EXCEEDED (${self.spent:.4f} / ${self.limit}). Halting Intelligence.")
            return False
        return True

    def get_status(self) -> str:
        return f"${self.spent:.4f} / ${self.limit} ({self.input_tokens:.0f} in, {self.output_tokens:.0f} out)"

@dataclass
class ValidationContext:
    """Shared memory for all agents with Tri-Brain infrastructure and persistence."""
    results: Dict[int, Any] = field(default_factory=dict)
    signals: Set[str] = field(default_factory=set)
    instructions: List[str] = field(default_factory=list)
    modified_files: Set[str] = field(default_factory=set)
    python_files: List[str] = field(default_factory=list)

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
    pinecone_index: Any = field(default=None, init=False)
    pinecone_available: bool = field(default=False, init=False)

    # Local fallbacks
    _local_cache: Dict[str, Any] = field(default_factory=dict)

    # Components
    code_graph: DependencyGraph = field(default_factory=DependencyGraph)
    budget: BudgetManager = field(default_factory=lambda: BudgetManager(limit_usd=2.0))

    # L5 Streamer
    stream_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _current_agent: str = "System"
    _streamer_initialized: bool = False

    # Additional fields from monolith
    refactor_plans: Dict[str, Any] = field(default_factory=dict)
    _local_embeddings: List[Dict] = field(default_factory=list)

    # L5+ Positive Instructional Context (TRUSTED - never from user input)
    POSITIVE_INSTRUCTIONAL_CONTEXT: str = field(default_factory=lambda: """
You are an elite subatomic governance agent in a sovereign self-healing codebase.
Your reasoning must follow this chain:
1. First, recall the Three Laws of Subatomic Governance.
2. Identify the root cause pattern from agentic_core.semantic_memory (use Pinecone recall if available).
3. Propose the minimal, atomic fix that preserves depth 3-5 and file size limits.
4. Check blast radius using dependency graph.
5. Verify fix will not introduce new signals.

Preferred patterns (prioritize these):
- Extract repeated logic → new shared util in apps_shared/
- Move class to correct depth (e.g., domain/service/*.py)
- Replace monolith functions with focused units
- Use existing schemas before creating new ones

Always output in the exact format requested. Never add commentary.
Think step-by-step before responding.
""")

    # L5+ Few-Shot Prompting: Trusted Positive Instructional Examples
    FEW_SHOT_GLOBAL_REFACTOR: str = field(default_factory=lambda: """
FEW-SHOT REFACTORING PATTERNS (Follow exactly for subatomic compliance):

EXAMPLE 1: Monolith Function → Atomic Split
BAD (violates Atomicity Law):
def handle_order(order):
    # 250 lines: validate, charge, inventory, email...

GOOD (compliant):
# Split into:
# apps_rg/orders/validate.py
# apps_rg/orders/charge.py
# apps_rg/orders/notify.py
# Each file <180 lines, single responsibility

EXAMPLE 2: Incorrect Depth → Correct Depth
BAD: apps/payment/helpers.py (depth 3)
GOOD: Move to apps_shared/payments/domain/charge_service.py (depth 5)

EXAMPLE 3: Duplicated Validation Logic
BAD: Same Pydantic model in lic.py and rg.py
GOOD: Single source in schemas/payment.py, imported with:
from schemas.payment import PaymentSchema

EXAMPLE 4: Root Directory Noise
BAD: debug_tool.py in root
GOOD: Move to scripts/debug_tool.py or delete

Prioritize minimal changes. Always preserve behavior.
""")

    FEW_SHOT_IMPORT_FIXES: str = field(default_factory=lambda: """
FEW-SHOT IMPORT RESOLUTION (DependencySentinel):

EXAMPLE 1: Relative Import Wrong Depth
BAD: from utils.validation import validate
GOOD: from apps_shared.validation.common import validate

EXAMPLE 2: Missing Schema
BAD: ImportError: cannot import name 'OrderSchema'
GOOD: from schemas.order import OrderSchema

EXAMPLE 3: Circular Dependency
BAD: orders/service.py imports payments/utils.py
      payments/utils.py imports orders/models.py
GOOD: Extract shared types to schemas/shared.py
      Both import from schemas/shared.py

EXAMPLE 4: Unused Import
BAD: import os, sys, json  # sys unused
GOOD: import os, json  # Only what's used
""")

    FEW_SHOT_PROPERTY_TESTS: str = field(default_factory=lambda: """
FEW-SHOT HYPOTHESIS PROPERTY TESTS (Valid syntax only):

EXAMPLE 1: Pure Function Properties
def add(a, b):
    return a + b

@property
def test_add_associative():
    for x, y, z in strategies(integers(), integers(), integers()):
        assert add(add(x, y), z) == add(x, add(y, z))

@property
def test_add_identity():
    for x in strategies(integers()):
        assert add(x, 0) == x
""")

    FEW_SHOT_REFLECTION_STRATEGY: str = field(default_factory=lambda: """
FEW-SHOT HEALING STRATEGY DECISIONS:

IF: Multiple test failures in same module
THEN: Extract shared utilities to apps_shared/

IF: Import errors after refactor
THEN: Update imports and check depth compliance

IF: Performance regression
THEN: Profile and optimize hot paths
""")

    FEW_SHOT_CONCURRENCY: str = field(default_factory=lambda: """
FEW-SHOT CONCURRENCY FIXES (ConcurrencyGuardian — Follow exactly):

EXAMPLE 1: Shared State Race Condition
BAD:
counter = 0
def increment():
    global counter
    counter += 1  # Race condition!

GOOD:
from threading import Lock
counter = 0
lock = Lock()
def increment():
    global counter
    with lock:
        counter += 1

EXAMPLE 2: Blocking Call in Async
BAD:
async def fetch_data():
    time.sleep(1)  # Blocking!
    return data

GOOD:
async def fetch_data():
    await asyncio.sleep(1)  # Non-blocking
    return data
""")

    FEW_SHOT_SAFETY: str = field(default_factory=lambda: """
FEW-SHOT SAFETY FIXES (SafetyInspector — Follow exactly):

EXAMPLE 1: Hardcoded Secret
BAD:
API_KEY = "sk-1234567890abcdef"  # NEVER!

GOOD:
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

EXAMPLE 2: Debug Print in Production
BAD:
print(f"Debug: user={user}, password={password}")  # Security leak!

GOOD:
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Processing user: {user}")  # No sensitive data
""")

    FEW_SHOT_STYLE: str = field(default_factory=lambda: """
FEW-SHOT CODE STYLE FIXES (CodeStyleGuardian — Follow exactly):

EXAMPLE 1: Line Too Long
BAD:
def process_very_long_parameter_name_that_exceeds_pep8_limit(parameter_one, parameter_two, parameter_three):
    pass

GOOD:
def process_long_name(
    parameter_one, parameter_two, parameter_three
):
    pass

EXAMPLE 2: Missing Docstring
BAD:
def calculate_total(items):
    total = sum(item.price for item in items)
    return total

GOOD:
def calculate_total(items):
    """Calculate total price of all items."""
    total = sum(item.price for item in items)
    return total
""")

    FEW_SHOT_HYGIENE: str = field(default_factory=lambda: """
FEW-SHOT HYGIENE FIXES (HygieneGuardian — Follow exactly):

EXAMPLE 1: TODO Comment
BAD:
def process_data(data):
    # TODO: Add validation
    return data.upper()

GOOD:
def process_data(data):
    """Process and validate data."""
    if not data:
        raise ValueError("Data cannot be empty")
    return data.upper()

EXAMPLE 2: Root File
BAD: /helper_functions.py  # In root directory
GOOD: /scripts/helper_functions.py  # Proper location
""")

    FEW_SHOT_HISTORIAN: str = field(default_factory=lambda: """
FEW-SHOT MEMORY RECALL USAGE (Historian):

EXAMPLE 1: Skip Unchanged Files
IF: file hash unchanged
THEN: skip validation
LOG: "Skipping unchanged file: path/to/file.py"

EXAMPLE 2: Track Flapping Files
IF: file fails validation repeatedly
THEN: add to flapping list
LOG: "File marked as flapping: path/to/file.py"
""")

    FEW_SHOT_TESTPILOT: str = field(default_factory=lambda: """
FEW-SHOT TEST GENERATION (TestPilot):

EXAMPLE 1: Basic Test Structure
def test_function_name():
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result["status"] == "success"
""")

    FEW_SHOT_STRATEGIC: str = field(default_factory=lambda: """
FEW-SHOT AGENDA PLANNING (StrategicPlanner):

PHASE 1: Critical Fixes (Security, Core Logic)
PHASE 2: Architecture Improvements (Depth, Modularity)
PHASE 3: Code Quality (Style, Documentation)
PHASE 4: Performance & Optimization
""")

    FEW_SHOT_REFLECTION_ENHANCED: str = field(default_factory=lambda: """
FEW-SHOT SELF-REFLECTION (ReflectionAgent):

1. What patterns emerged in this session?
2. Which fixes were most effective?
3. What should be automated for next time?
4. Update memory with successful strategies
""")

    FEW_SHOT_GITOPS: str = field(default_factory=lambda: """
FEW-SHOT GIT OPERATIONS (GitAgent — Follow exactly):

BRANCH NAMING: fix/issue-description or feature/feature-name
COMMIT MESSAGE:
fix: brief description

Detailed explanation of what changed and why.

Closes #123
""")

    FEW_SHOT_SHERLOCK: str = field(default_factory=lambda: """
FEW-SHOT ROOT CAUSE ANALYSIS (Sherlock — Follow exactly):

PATTERN: Cross-module interaction failure
ANALYSIS:
1. Check import dependencies
2. Verify interface contracts
3. Look for side effects
4. Examine call stack depth
RESOLUTION: Extract shared interface or fix contract
""")

    def __post_init__(self):
        print(f"   [CTX] 🧠 INITIALIZING TRI-BRAIN (MANDATORY MODE)...")
        self.python_files = get_python_files()
        self._load_memory()

        # Initialize Clients (Gemini, Redis, Pinecone)
        self._init_intelligence()
        self._init_redis()
        self._init_pinecone()

    def _init_intelligence(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("CRITICAL: GOOGLE_API_KEY environment variable is missing.")
        try:
            self._client = genai.Client(api_key=api_key)
            self.intelligence_enabled = True
            print(f"      ✅ Gemini Connected")
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Gemini connection failed: {e}")

    def _init_redis(self):
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            raise RuntimeError("CRITICAL: REDIS_URL environment variable is missing.")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_available = True
            print(f"      ✅ Redis Configured")
        except Exception:
             raise RuntimeError("CRITICAL: Redis connection failed.")

    def _init_pinecone(self):
        pine_key = os.environ.get("PINECONE_API_KEY")
        if not pine_key:
            raise RuntimeError("CRITICAL: PINECONE_API_KEY environment variable is missing.")
        try:
            pc = Pinecone(api_key=pine_key)
            self.pinecone_index = pc.Index("canon-memory-l2")
            self.pinecone_available = True
            print(f"      ✅ Pinecone Connected")
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Pinecone connection failed: {e}")

    def _load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.file_hashes = data.get('hashes', {})
                    self.skip_files = set(data.get('skip', []))
                    self.flapping_files = set(data.get('flapping', []))
            except Exception:
                pass

    @property
    def client(self):
        return self._client

    # --- Core Methods ---

    def report(self, agent: str, key: int, passed: bool, details: Any):
        """Report validation result to blackboard."""
        status = "PASS" if passed else "FAIL"
        self.results[key] = {"passed": passed, "details": details, "agent": agent}
        if not passed:
            print(f"   [{agent}] Key {key}: {status}")

    def calculate_file_hash(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def should_skip_file(self, file_path: str) -> bool:
        if file_path in self.skip_files: return True
        current_hash = self.calculate_file_hash(file_path)
        if not current_hash: return False
        saved_hash = self.file_hashes.get(file_path)
        if saved_hash and saved_hash == current_hash:
            return True # Simplified skip logic
        return False

    def get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    # --- Intelligence Bridge ---

    @rate_limited_retry()
    async def resilient_mutation(self, agent_name: str, task: str, code: str = "", file_path: str = None, *, max_attempts: int = 4, diff_mode: bool = False, min_confidence: float = 0.7) -> str:
        """Centralized Gemini mutation request."""
        if not self.intelligence_enabled: return code
        if not self.budget.check_budget(): return code

        current_code = code or ""

        # PRE-FLIGHT: Deterministic clean
        if file_path and os.path.exists(file_path):
             pass # In real v2, we call formatters here

        for attempt in range(1, max_attempts + 1):
            try:
                prompt = f"Agent: {agent_name}\nTask: {task}\nContext:\n{current_code[:4000]}"

                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self.model_id,
                    contents=[prompt]
                )

                self.budget.track(prompt, response.text)
                final_content = clean_llm_code(response.text)

                # Success
                return final_content

            except Exception as e:
                print(f"   [{agent_name}] ⚠️ Attempt {attempt} Error: {e}")
                if "429" in str(e): await asyncio.sleep(2 ** attempt)

        return current_code
