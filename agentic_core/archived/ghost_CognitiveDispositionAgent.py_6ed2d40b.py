"""
[PHASE 11/12/14/16] Cognitive Disposition Agent - AI-Powered Architectural Triage.

Uses NEW SDK (google.genai) to analyze structural violations and determine intelligent resolutions.
This agent provides "Intelligent Triage" for files flagged by the ArchitectureGovernorAgent.

Phase 11: Heuristic-based analysis
Phase 12: Gemini LLM integration with JSON enforcement
Phase 14: Environment loading with python-dotenv
Phase 16: Migration to google.genai SDK (deprecated google-generativeai)
Phase 33e: cache-First Governance (Redis + Pinecone)
Phase 33h: Hardened Semantic Broadening (Parallel Execution)

Responsibilities:
- Analyze ORPHAN violations and recommend proper SSOT locations
- Analyze GRAVITY violations and suggest refactoring strategies
- Analyze DUPLICATE violations and recommend consolidation targets
- Return structured DispositionDecision with action, target, and confidence

Actions:
- MOVE: Relocate file to suggested target_path
- REFACTOR: Apply suggested code changes
- ARCHIVE: Move to archives for later review
- IGNORE: No action needed (false positive)
- MANUAL_REVIEW: Requires human decision

[SSOT] Integrates with ArchitectureGovernorAgent for violation resolution.
"""

from typing import Any
from pathlib import Path
from dataclasses import dataclass, field
import hashlib
import json
import logging
import os
import re
import time

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

# [PHASE 16] Modern SDK Imports
try:
    from google import genai
    from google.genai import types
except ImportError:
    # Graceful fallback if SDK not installed (handled in _get_client)
    genai = None
    types = None

# [PHASE 33e] Vector DB Imports
try:
    from pinecone import Pinecone
except ImportError:
    Pinecone = None

# [PHASE 14] Environment Imports
try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:
    find_dotenv = None
    load_dotenv = None


# Placeholder for embedding utility (assumed to exist in codebase)
# from agentic_core.utils.embeddings import get_gemini_embedder
def get_gemini_embedder():
    """Mock/Placeholder if utility not in path."""
    return None


Logger = logging.getLogger(__name__)

# [PHASE 33e] cache-First LLM Governance configuration
BYPASS_CACHE_ENV = "BYPASS_CACHE"
SEMANTIC_SIMILARITY_THRESHOLD = 0.95  # 95% similarity for Pinecone matches


@dataclass
class DispositionDecision:
    """Structured decision from cognitive analysis."""

    action: str  # MOVE, REFACTOR, ARCHIVE, IGNORE, MANUAL_REVIEW
    target_path: str | None = None
    reason: str = ""
    confidence: float = 0.0
    suggested_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate action is one of the allowed values."""
        valid_actions = {"MOVE", "REFACTOR", "ARCHIVE", "IGNORE", "MANUAL_REVIEW"}
        if self.action not in valid_actions:
            raise ValueError(f"Invalid action: {self.action}. Must be one of {valid_actions}")

        # Clamp confidence to [0.0, 1.0]
        self.confidence = max(0.0, min(1.0, self.confidence))


class CognitiveDispositionAgent(SovereignBaseAgent):
    """
    AI-Powered Architectural Triage Agent.

    Analyzes structural violations and determines intelligent resolutions
    using LLM capabilities.

    Attributes:
        project_root: Root directory of the project
        confidence_threshold: Minimum confidence to auto-execute decisions
        llm_enabled: Whether to use actual LLM calls (vs mock responses)
    """

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        # Placeholder for full healing logic implementation
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(
        self,
        project_root: Path | None = None,
        confidence_threshold: float = 0.8,
        llm_enabled: bool = False,
        api_key: str | None = None,
    ):
        """
        Initialize the Cognitive Disposition Agent.

        Args:
            project_root: Project root directory
            confidence_threshold: Minimum confidence for auto-execution
            llm_enabled: Enable actual LLM API calls
            api_key: API key for LLM service (defaults to env var)
        """
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold
        self.llm_enabled = llm_enabled

        # Phase 14: Force load .env from project root if variable is missing
        if not os.getenv("GEMINI_API_KEY") and not api_key:
            if load_dotenv and find_dotenv:
                # usecwd=True ensures we look in project root regardless of execution dir
                try:
                    env_file = find_dotenv(usecwd=True)
                    if env_file:
                        load_dotenv(env_file)
                        Logger.info(f"[COGNITIVE] Loaded environment from: {env_file}")
                    else:
                        Logger.debug("[COGNITIVE] No .env file found")
                except OSError:
                    # Handle cases where starting path is invalid (e.g., in tests)
                    Logger.debug("[COGNITIVE] Could not search for .env file")
            else:
                Logger.debug("[COGNITIVE] python-dotenv not installed, skipping .env loading")

        # Get API key from argument or environment
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        # Phase 14: API key validation with graceful degradation
        if not self.api_key:
            Logger.warning(
                "[COGNITIVE] GEMINI_API_KEY not found. Agent will use heuristic mode only."
            )
            Logger.info(
                "[COGNITIVE] To enable LLM: Set GEMINI_API_KEY in .env or pass api_key parameter"
            )
        else:
            Logger.info("[COGNITIVE] API key configured successfully")

        self._client = None  # Lazy-loaded google.genai Client (Phase 16)

        # [PHASE 29/33e] cache-First LLM Governance
        self._decision_cache = {}  # Local fallback cache
        self._redis_client = None
        self._pinecone_index = None
        self._embedder = None
        self._cache_stats = {
            "redis_hits": 0,
            "pinecone_hits": 0,
            "llm_calls": 0,
            "total_requests": 0,
        }
        self._init_redis_cache()
        self._init_pinecone_cache()
        self._init_embedder()

        # Layer mapping for SSOT compliance
        self.layer_map = {
            "L0_maintenance": "Maintenance and tooling",
            "L1_cognition": "Cognitive processing and thought engines",
            "L2_execution": "Execution and tool orchestration",
            "L3_orchestration": "Workflow orchestration",
            "L4_state": "State management and persistence",
            "L5_safety": "Safety, validation, and governance",
            "L6_observability": "observability and telemetry",
        }

    def _init_redis_cache(self):
        """[PHASE 29] Initialize Redis connection for LLM decision caching."""
        try:
            import redis

            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self._redis_client = redis.from_url(redis_url, decode_responses=True)
            self._redis_client.ping()
            Logger.info("[COGNITIVE] Redis cache connected for exact-match lookups")
        except Exception as e:
            Logger.debug(f"[COGNITIVE] Redis unavailable, using local cache: {e}")
            self._redis_client = None

    def _init_pinecone_cache(self):
        """[PHASE 33e] Initialize Pinecone for semantic similarity lookups."""
        try:
            pinecone_key = os.environ.get("PINECONE_API_KEY")
            if not pinecone_key or not Pinecone:
                Logger.debug(
                    "[COGNITIVE] PINECONE_API_KEY not set or lib missing, semantic cache disabled"
                )
                return

            pc = Pinecone(api_key=pinecone_key)
            index_name = os.environ.get("PINECONE_INDEX_NAME", "agentic-memory")
            existing_indexes = [idx.name for idx in pc.list_indexes()]

            if index_name in existing_indexes:
                self._pinecone_index = pc.Index(index_name)
                Logger.info(f"[COGNITIVE] Pinecone connected for semantic lookups: {index_name}")
            else:
                Logger.warning(f"[COGNITIVE] Pinecone index '{index_name}' not found")
        except Exception as e:
            Logger.debug(f"[COGNITIVE] Pinecone unavailable: {e}")
            self._pinecone_index = None

    def _init_embedder(self):
        """[PHASE 33e] Initialize Gemini embedder for semantic vectors."""
        try:
            self._embedder = get_gemini_embedder()
            if self._embedder:
                Logger.info("[COGNITIVE] Gemini embedder initialized for semantic caching")
        except Exception as e:
            Logger.debug(f"[COGNITIVE] Embedder unavailable: {e}")
            self._embedder = None

    def _get_cache_key(self, file_path: Path, violation_type: str) -> str:
        """Generate cache key based on file pattern and violation type."""
        # Use file extension + violation type as key (not full path)
        # This allows caching decisions for similar files
        file_ext = file_path.suffix
        file_name = file_path.name
        # For __init__.py, use parent folder pattern
        if file_name == "__init__.py":
            parent = file_path.parent.name
            return f"cda:init:{parent}:{violation_type}"
        return f"cda:{file_ext}:{violation_type}"

    def _get_cached_decision(self, cache_key: str) -> DispositionDecision | None:
        """[PHASE 29] Check Redis/local cache for existing decision."""
        try:
            # Try Redis first
            if self._redis_client:
                cached = self._redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    Logger.info(f"[COGNITIVE] cache HIT: {cache_key}")
                    return DispositionDecision(
                        action=data["action"],
                        target_path=data.get("target_path"),
                        reason=f"[CACHED] {data.get('reason', '')}",
                        confidence=data.get("confidence", 0.8),
                    )
            # Fallback to local cache
            if cache_key in self._decision_cache:
                Logger.info(f"[COGNITIVE] Local cache HIT: {cache_key}")
                return self._decision_cache[cache_key]
        except Exception as e:
            Logger.debug(f"[COGNITIVE] cache lookup failed: {e}")
        return None

    def _cache_decision(self, cache_key: str, decision: DispositionDecision):
        """[PHASE 29] Store decision in Redis/local cache."""
        try:
            data = {
                "action": decision.action,
                "target_path": decision.target_path,
                "reason": decision.reason,
                "confidence": decision.confidence,
            }
            # Store in Redis with 24h TTL
            if self._redis_client:
                self._redis_client.setex(cache_key, 86400, json.dumps(data))
                Logger.info(f"[COGNITIVE] Cached to Redis: {cache_key}")
            # Always store in local cache too
            self._decision_cache[cache_key] = decision
        except Exception as e:
            Logger.debug(f"[COGNITIVE] cache store failed: {e}")

    # ========================================================================
    # [PHASE 33e] cache-First LLM Governance - Semantic Lookup
    # ========================================================================

    def _get_prompt_hash(self, file_path: Path, violation_type: str, context: dict) -> str:
        """Generate a hash of the prompt for exact-match Redis lookup."""
        prompt_key = f"{file_path.suffix}:{violation_type}:{sorted(context.items())}"
        return f"cda:hash:{hashlib.sha256(prompt_key.encode()).hexdigest()[:16]}"

    def _semantic_lookup(self, file_path: Path, violation_type: str) -> DispositionDecision | None:
        """
        [PHASE 33e] Perform semantic similarity lookup in Pinecone.

        Returns cached decision if 95%+ similarity match found.
        """
        if not self._pinecone_index or not self._embedder:
            return None

        try:
            # Generate embedding for this query
            query_text = f"violation:{violation_type} file:{file_path.suffix} name:{file_path.stem}"
            embedding = self._embedder.embed(query_text)

            if not embedding:
                return None

            # Query Pinecone for similar decisions
            results = self._pinecone_index.query(
                vector=embedding, top_k=1, include_metadata=True, namespace="cda_decisions"
            )

            if results.matches and results.matches[0].score >= SEMANTIC_SIMILARITY_THRESHOLD:
                match = results.matches[0]
                metadata = match.metadata or {}
                Logger.info(f"[COGNITIVE] Pinecone HIT: {match.score:.3f} similarity")
                self._cache_stats["pinecone_hits"] += 1

                return DispositionDecision(
                    action=metadata.get("action", "MANUAL_REVIEW"),
                    target_path=metadata.get("target_path"),
                    reason=f"[SEMANTIC_CACHED] {metadata.get('reason', '')}",
                    confidence=metadata.get("confidence", 0.8),
                )
        except Exception as e:
            Logger.debug(f"[COGNITIVE] Semantic lookup failed: {e}")

        return None

    def _cache_to_pinecone(
        self, file_path: Path, violation_type: str, decision: DispositionDecision
    ):
        """[PHASE 33e] Store decision in Pinecone for semantic retrieval."""
        if not self._pinecone_index or not self._embedder:
            return

        try:
            # Generate embedding
            query_text = f"violation:{violation_type} file:{file_path.suffix} name:{file_path.stem}"
            embedding = self._embedder.embed(query_text)

            if not embedding:
                return

            # Generate unique ID
            vector_id = f"cda:{hashlib.sha256(query_text.encode()).hexdigest()[:16]}"

            # Upsert to Pinecone
            self._pinecone_index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "action": decision.action,
                            "target_path": decision.target_path or "",
                            "reason": decision.reason,
                            "confidence": decision.confidence,
                            "violation_type": violation_type,
                            "file_ext": file_path.suffix,
                        },
                    }
                ],
                namespace="cda_decisions",
            )
            Logger.info(f"[COGNITIVE] Cached to Pinecone: {vector_id}")
        except Exception as e:
            Logger.debug(f"[COGNITIVE] Pinecone cache failed: {e}")

    def _log_cache_stats(self):
        """[PHASE 33e] Log cache hit/miss statistics for observability."""
        stats = self._cache_stats
        total = stats["total_requests"]
        if total == 0:
            return

        redis_rate = (stats["redis_hits"] / total) * 100
        pinecone_rate = (stats["pinecone_hits"] / total) * 100
        llm_rate = (stats["llm_calls"] / total) * 100

        Logger.info(
            f"[COGNITIVE] cache Stats: Redis={redis_rate:.1f}%, Pinecone={pinecone_rate:.1f}%, LLM={llm_rate:.1f}% (n={total})"
        )

    def analyze_violation(
        self,
        file_path: str | Path,
        violation_type: str,
        context: dict[str, Any] | None = None,
    ) -> DispositionDecision:
        """
        Analyze a violation and return a disposition decision.

        [PHASE 33e] cache-First LLM Governance:
        1. Exact match (Redis) - hash lookup
        2. Semantic match (Pinecone) - 95%+ similarity
        3. Heuristic analysis - pattern-based
        4. LLM call - only if all above fail

        Args:
            file_path: Path to the file with the violation
            violation_type: Type of violation (ORPHAN, GRAVITY, DUPLICATE, etc.)
            context: Additional context about the violation

        Returns:
            DispositionDecision with recommended action
        """
        start_time = time.time()
        file_path = Path(file_path)
        context = context or {}

        # Track stats
        self._cache_stats["total_requests"] += 1

        Logger.info(f"[COGNITIVE] Analyzing disposition for {file_path.name} ({violation_type})...")

        # [PHASE 33e] Check BYPASS_CACHE for forced refresh
        bypass_cache = os.environ.get(BYPASS_CACHE_ENV, "").lower() in ("1", "true", "yes")

        if not bypass_cache:
            # Step 1: Exact match (Redis) - fastest
            cache_key = self._get_cache_key(file_path, violation_type)
            cached_decision = self._get_cached_decision(cache_key)
            if cached_decision:
                self._cache_stats["redis_hits"] += 1
                elapsed = (time.time() - start_time) * 1000
                Logger.info(f"[COGNITIVE] Redis HIT in {elapsed:.1f}ms")
                return cached_decision

            # Step 2: Semantic match (Pinecone) - 95%+ similarity
            semantic_decision = self._semantic_lookup(file_path, violation_type)
            if semantic_decision:
                elapsed = (time.time() - start_time) * 1000
                Logger.info(f"[COGNITIVE] Pinecone HIT in {elapsed:.1f}ms")
                # Also cache to Redis for faster future lookups
                self._cache_decision(cache_key, semantic_decision)
                return semantic_decision

        # Step 3: Heuristic analysis - pattern-based (no LLM cost)
        heuristic_decision = self._analyze_heuristic(file_path, violation_type, context)

        if heuristic_decision.confidence >= 0.8:
            Logger.info(
                f"[COGNITIVE] High-confidence heuristic: {heuristic_decision.action} ({heuristic_decision.confidence:.2f})"
            )
            cache_key = self._get_cache_key(file_path, violation_type)
            self._cache_decision(cache_key, heuristic_decision)
            self._cache_to_pinecone(file_path, violation_type, heuristic_decision)
            return heuristic_decision

        # Step 4: LLM call - only if all above fail
        if self.llm_enabled and self.api_key:
            self._cache_stats["llm_calls"] += 1
            Logger.info("[COGNITIVE] cache MISS - calling LLM...")
            llm_decision = self._generate_llm_decision(file_path, violation_type, context)

            if llm_decision.action != "MANUAL_REVIEW":
                # cache to both Redis and Pinecone for future reuse
                cache_key = self._get_cache_key(file_path, violation_type)
                self._cache_decision(cache_key, llm_decision)
                self._cache_to_pinecone(file_path, violation_type, llm_decision)

                elapsed = (time.time() - start_time) * 1000
                Logger.info(f"[COGNITIVE] LLM decision in {elapsed:.1f}ms (cached for future)")
                return llm_decision

        # Fallback to heuristic decision
        return heuristic_decision

    def _analyze_heuristic(
        self,
        file_path: Path,
        violation_type: str,
        context: dict[str, Any],
    ) -> DispositionDecision:
        """
        Heuristic-based analysis when LLM is not available.

        Uses file naming patterns and location to suggest disposition.
        """
        file_name = file_path.name
        file_stem = file_path.stem

        # ORPHAN violations - suggest based on naming patterns
        if violation_type == "ORPHAN":
            return self._analyze_orphan_heuristic(file_path, file_name, file_stem)

        # GRAVITY violations - suggest archive for failed repairs
        elif violation_type in ("GRAVITY", "GRAVITY_FAIL"):
            return DispositionDecision(
                action="ARCHIVE",
                target_path="archives/gravity_violations",
                reason=f"Gravity violation requires import refactoring: {file_name}",
                confidence=0.6,
                metadata={"original_path": str(file_path)},
            )

        # DUPLICATE violations - suggest archive
        elif violation_type == "DUPLICATE":
            return DispositionDecision(
                action="ARCHIVE",
                target_path="archives/deduplication_cleanup",
                reason=f"Duplicate detected, archiving for consolidation review: {file_name}",
                confidence=0.7,
                metadata={"original_path": str(file_path)},
            )

        # [PHASE 33e] Hygiene violations - high-confidence heuristics
        elif violation_type == "debug_print":
            return DispositionDecision(
                action="REFACTOR",
                reason=f"Remove debug print statements from {file_name}",
                confidence=0.95,  # High confidence - always safe to remove prints
                metadata={"surgery_type": "print_removal"},
            )

        elif violation_type == "missing_docstring":
            return DispositionDecision(
                action="REFACTOR",
                reason=f"Add TODO docstrings to public functions in {file_name}",
                confidence=0.90,  # High confidence - safe to add docstrings
                metadata={"surgery_type": "docstring_addition"},
            )

        elif violation_type == "orphaned_init":
            return DispositionDecision(
                action="IGNORE",
                reason=f"Protect __init__.py to maintain package structure: {file_name}",
                confidence=0.95,  # High confidence - never delete __init__.py
                metadata={"protected": True},
            )

        elif violation_type == "empty_file":
            # Non-init empty files can be archived
            if file_name != "__init__.py":
                return DispositionDecision(
                    action="ARCHIVE",
                    target_path="archives/empty_files",
                    reason=f"Empty file can be safely archived: {file_name}",
                    confidence=0.85,
                    metadata={"original_path": str(file_path)},
                )
            else:
                return DispositionDecision(
                    action="IGNORE",
                    reason=f"Protect empty __init__.py: {file_name}",
                    confidence=0.95,
                )

        # Default: manual review
        return DispositionDecision(
            action="MANUAL_REVIEW",
            reason=f"Unknown violation type requires human review: {violation_type}",
            confidence=0.0,
        )

    def _analyze_orphan_heuristic(
        self,
        file_path: Path,
        file_name: str,
        file_stem: str,
    ) -> DispositionDecision:
        """
        Heuristic analysis for ORPHAN violations.

        Suggests target location based on file naming patterns.
        """
        # Agent files -> L5_safety or appropriate layer
        if file_name.endswith("Agent.py"):
            # Check for layer hints in the name
            if any(x in file_stem.lower() for x in ["validator", "enforcer", "governor", "safety"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L5_safety/validators",
                    reason=f"Agent with safety/validator pattern: {file_name}",
                    confidence=0.75,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["healer", "repair", "fixer"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L5_safety/repair",
                    reason=f"Agent with healer/repair pattern: {file_name}",
                    confidence=0.75,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["orchestrat", "workflow", "coordinator"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L3_orchestration",
                    reason=f"Agent with orchestration pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["observ", "telemetry", "metric", "monitor"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L6_observability",
                    reason=f"Agent with observability pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["state", "checkpoint", "persist", "ledger"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L4_state",
                    reason=f"Agent with state management pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["tool", "execute", "mcp"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L2_execution",
                    reason=f"Agent with execution pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            elif any(x in file_stem.lower() for x in ["thought", "cognit", "reason", "prompt"]):
                return DispositionDecision(
                    action="MOVE",
                    target_path="agentic_core/L1_cognition",
                    reason=f"Agent with cognition pattern: {file_name}",
                    confidence=0.7,
                    metadata={"original_path": str(file_path)},
                )
            else:
                # Default: archive for review
                return DispositionDecision(
                    action="ARCHIVE",
                    target_path="archives/orphan_agents",
                    reason=f"Orphan agent with unclear layer affinity: {file_name}",
                    confidence=0.5,
                    metadata={"original_path": str(file_path)},
                )

        # Test files -> tests directory
        if file_name.startswith("test_") or file_name.endswith("_test.py"):
            return DispositionDecision(
                action="MOVE",
                target_path="tests/unit",
                reason=f"Test file should be in tests directory: {file_name}",
                confidence=0.85,
                metadata={"original_path": str(file_path)},
            )

        # Script files -> scripts directory
        if "script" in str(file_path).lower() or file_name.startswith("run_"):
            return DispositionDecision(
                action="MOVE",
                target_path="scripts/maintenance",
                reason=f"Script file should be in scripts directory: {file_name}",
                confidence=0.7,
                metadata={"original_path": str(file_path)},
            )

        # Default: archive for review
        return DispositionDecision(
            action="ARCHIVE",
            target_path="archives/orphan_files",
            reason=f"Orphan file with unclear destination: {file_name}",
            confidence=0.4,
            metadata={"original_path": str(file_path)},
        )

    def _get_client(self):
        """
        [PHASE 16] Lazy-load the google.genai Client.

        Returns:
            google.genai.Client instance or None if not configured
        """
        if self._client is None and self.api_key and genai:
            try:
                self._client = genai.Client(api_key=self.api_key)
                Logger.info("[COGNITIVE] google.genai Client initialized")
            except Exception as e:
                Logger.error(f"[COGNITIVE] Failed to initialize google.genai: {e}")
                return None
        return self._client

    def _generate_llm_decision(
        self,
        file_path: Path,
        violation_type: str,
        context: dict[str, Any],
    ) -> DispositionDecision:
        """
        [PHASE 16] Generate disposition decision using google.genai SDK.

        Uses response_mime_type='application/json' for strict JSON enforcement.

        Args:
            file_path: Path to the file with violation
            violation_type: Type of violation
            context: Additional context

        Returns:
            DispositionDecision from LLM analysis
        """
        try:
            client = self._get_client()
            if client is None:
                return DispositionDecision(
                    action="MANUAL_REVIEW",
                    reason="google.genai client not available",
                    confidence=0.0,
                )

            # Get model from environment
            model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

            # Read file content safely
            content = self._read_file_safe(file_path)

            # Build strict JSON-enforcing prompt
            prompt = self._build_strict_json_prompt(file_path, violation_type, content, context)

            Logger.info(f"[COGNITIVE] Calling Gemini ({model_name}) for {file_path.name}...")

            # Phase 16: Use new SDK with JSON response mode
            if types:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                return self._parse_llm_json_response(response.text)
            else:
                # Fallback if types not loaded (should not happen if client loaded)
                return DispositionDecision(action="MANUAL_REVIEW", reason="SDK Types Error")

        except Exception as e:
            Logger.error(f"[COGNITIVE] LLM analysis failed: {e}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"LLM Error: {e}",
                confidence=0.0,
            )

    def _read_file_safe(self, file_path: Path) -> str:
        """
        Safely read file content with size limits.

        Args:
            file_path: Path to file

        Returns:
            File content (truncated if needed) or empty string
        """
        try:
            if not file_path.exists():
                return ""
            if file_path.stat().st_size > 50000:  # 50KB limit
                return ""
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return content[:3000]  # Truncate to 3000 chars for prompt
        except Exception:
            return ""

    def _build_strict_json_prompt(
        self,
        file_path: Path,
        violation_type: str,
        content: str,
        context: dict[str, Any],
    ) -> str:
        """
        [PHASE 12] Build a strict JSON-enforcing prompt for LLM.

        Uses explicit instructions to ensure valid JSON output.
        """
        layer_desc = "\n".join(f"- {k}: {v}" for k, v in self.layer_map.items())

        return f"""You are a Senior Software Architect analyzing an architectural violation.

TASK: Determine the correct disposition for this file in a standard Agentic L0-L6 architecture.

FILE INFORMATION:
- Path: {file_path}
- Name: {file_path.name}
- Violation Type: {violation_type}

LAYER STRUCTURE (SSOT):
{layer_desc}

FILE CONTENT (truncated):
```python
{content}
```

INSTRUCTIONS:
1. Analyze the file's purpose based on its name and content
2. Determine which layer it belongs to based on the SSOT
3. Return ONLY a valid JSON object, no other text

VALID ACTIONS:
* "MOVE": File should be moved to target_path
* "ARCHIVE": File should be archived (unclear purpose or duplicate)
* "IGNORE": File is correctly placed or is a false positive

OUTPUT FORMAT (JSON ONLY - NO MARKDOWN, NO EXPLANATION):
{{"action": "MOVE", "target_path": "agentic_core/L5_safety/validators", "reason": "brief explanation", "confidence": 0.85}}

RESPOND WITH ONLY THE JSON OBJECT:"""

    def _parse_llm_json_response(self, response_text: str) -> DispositionDecision:
        """
        [PHASE 12] Parse LLM response with strict JSON extraction.

        Handles various response formats including markdown code blocks.

        Args:
            response_text: Raw LLM response

        Returns:
            DispositionDecision parsed from response
        """
        try:
            # Clean response - remove markdown code blocks
            cleaned = response_text.strip()
            cleaned = re.sub(r"```json\s*", "", cleaned)
            cleaned = re.sub(r"```\s*", "", cleaned)
            cleaned = cleaned.strip()

            # Try to find JSON object in response
            json_match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)

            # Parse JSON
            data = json.loads(cleaned)

            # Extract and validate fields
            action = data.get("action", "MANUAL_REVIEW").upper()
            if action not in {"MOVE", "REFACTOR", "ARCHIVE", "IGNORE", "MANUAL_REVIEW"}:
                action = "MANUAL_REVIEW"

            target_path = data.get("target_path")
            reason = data.get("reason", "LLM Generated")
            confidence = float(data.get("confidence", 0.5))

            Logger.info(f"[COGNITIVE] LLM decision: {action} -> {target_path} ({confidence:.2f})")

            return DispositionDecision(
                action=action,
                target_path=target_path,
                reason=reason,
                confidence=confidence,
                metadata={"source": "gemini"},
            )

        except json.JSONDecodeError as e:
            Logger.warning(f"[COGNITIVE] Failed to parse LLM JSON: {e}")
            Logger.debug(f"[COGNITIVE] Raw response: {response_text[:500]}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"JSON parse error: {e}",
                confidence=0.0,
            )
        except Exception as e:
            Logger.error(f"[COGNITIVE] Error parsing LLM response: {e}")
            return DispositionDecision(
                action="MANUAL_REVIEW",
                reason=f"Parse error: {e}",
                confidence=0.0,
            )

    def _build_analysis_prompt(
        self,
        file_path: Path,
        violation_type: str,
        content: str,
        context: dict[str, Any],
    ) -> str:
        """Build the analysis prompt for LLM."""
        return f"""Analyze this architectural violation and recommend a disposition.

File: {file_path}
Violation Type: {violation_type}
Context: {context}

Layer Structure (SSOT):
{self.layer_map}

File Content (truncated):
```python
{content[:2000]}
```

Respond with JSON:
{{
    "action": "MOVE|REFACTOR|ARCHIVE|IGNORE",
    "target_path": "suggested/path/if/MOVE",
    "reason": "explanation",
    "confidence": 0.0-1.0
}}
"""

    def should_auto_execute(self, decision: DispositionDecision) -> bool:
        """
        Determine if a decision should be auto-executed.

        Args:
            decision: The disposition decision

        Returns:
            True if confidence meets threshold and action is executable
        """
        executable_actions = {"MOVE", "ARCHIVE"}
        return (
            decision.action in executable_actions
            and decision.confidence >= self.confidence_threshold
        )

    # ========================================================================
    # [PHASE 33h] Hardened Semantic Broadening (Parallel Execution)
    # ========================================================================

    async def semantic_broadening_search(
        self, query_embedding: list[float], violation_type: str, context_metadata: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Performs a parallelized multi-tiered semantic search to broaden context retrieval.

        Hardening:
        - Uses asyncio.gather for parallel execution (Latency Reduction)
        - Implements ID-based deduplication
        - Handles partial failures gracefully

        Strategy:
        1. Primary: Broad search on violation type (30 results)
        2. Secondary: Standard search on related file patterns (15 results)
        3. Tertiary: Narrow search on high-success patterns (5 results)
        """
        import asyncio
        from agentic_core.utils.core_extensions.pinecone_vector_mixin import RetrievalBroadness

        # Define search tasks for parallel execution to minimize latency
        tasks = [
            # Tier 1: Primary Broad Search (Violation Focus)
            self.vector_search(
                embedding=query_embedding,
                broadness=RetrievalBroadness.BROAD,
                metadata_filter={"violation_type": violation_type},
            ),
            # Tier 2: Secondary Context Search (File Context)
            self.vector_search(
                embedding=query_embedding,
                broadness=RetrievalBroadness.STANDARD,
                metadata_filter={"file_type": context_metadata.get("file_type", "unknown")},
            ),
            # Tier 3: High Precision Search (Success Patterns)
            self.vector_search(
                embedding=query_embedding,
                broadness=RetrievalBroadness.NARROW,
                metadata_filter={"validation_outcome": "success"},
            ),
        ]

        # Execute all searches concurrently
        # return_exceptions=True ensures one failure doesn't crash the entire broadening operation
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate and Deduplicate
        valid_matches = []
        seen_ids = set()

        for batch in results_list:
            if isinstance(batch, Exception):
                # Log failure but continue with other batches
                Logger.warning(f"[COGNITIVE] Semantic broadening sub-search failed: {str(batch)}")
                continue

            if not batch:
                continue

            for match in batch:
                match_id = match.get("id")
                # Critical: Deduplicate by ID to prevent context pollution
                if match_id and match_id not in seen_ids:
                    seen_ids.add(match_id)
                    valid_matches.append(match)

        # Sort by score descending (primary sort) to ensure highest relevance is kept
        # Note: Pinecone results come sorted, but mixing batches requires re-sorting
        valid_matches.sort(key=lambda x: x.get("score", 0.0), reverse=True)

        # Return top 50 unique results
        return valid_matches[:50]
