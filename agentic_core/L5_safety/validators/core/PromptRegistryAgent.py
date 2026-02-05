from __future__ import annotations

"""Prompt Registry Agent - Runtime State Manager for Prompt Versioning.

ARCHITECTURAL HARDENING:
- Contract (immutable): sovereign_prompt_constitution.py defines base prompts
- State (mutable): This agent manages runtime versioning and active/inactive status
- Clear separation: Constitution = SSOT, Registry = Runtime tracking
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)

# HARDENING: Import immutable constitution as contract reference
try:
    from agentic_core.prompt_governance.prompt_entry_types import (
        PromptEntry,
        get_constitution,
    )

    CONSTITUTION_AVAILABLE = True
except ImportError:
    CONSTITUTION_AVAILABLE = False
    PromptEntry = None
    get_constitution = None

# Semantic deduplication imports
try:
    from agentic_core.semantic_memory.embeddings.core_embedder import get_embedding

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    get_embedding = None

SIMILARITY_THRESHOLD = 0.9
EMBEDDING_MODEL = "text-embedding-3-small"


# ARCHITECTURAL HARDENING: Removed L5 upward import.
# Placement validation is now handled via optional dependency injection
# or external registration to maintain Layer Boundary integrity.
def _default_placement_validator(path: Path, root: Path) -> tuple[bool, str]:
    """Default pass-through to prevent upward layer coupling."""
    return True, "Architecture Layer Neutral"


@dataclass
class PromptRegistryAgent(SovereignBaseAgent):
    """Runtime state manager for prompt versioning and activation.

    ARCHITECTURAL HARDENING:
    - CONTRACT (Immutable): sovereign_prompt_constitution.py defines base prompts
    - STATE (Mutable): This agent tracks runtime versions and active/inactive status
    - SEPARATION: Constitution is SSOT, Registry is runtime tracking layer

    Responsibilities:
    - Maintain versioned entries (v1, v2, ...) in registry.json
    - Track active/inactive status to prevent instruction drift
    - Provide metadata for L4 Ledger traceability
    - Ensure atomic JSON persistence
    - Sync with immutable Constitution on initialization
    """

    REGISTRY_FILE = Path(__file__).parent / "registry.json"

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal method for L5 safety compliance (HealerProtocol).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with canonical heal schema keys
        """
        return {"violations_found": 1, "violations_fixed": 0, "errors": [], "skipped": 1}

    def __init__(self, placement_validator=None) -> None:
        """Initialize the instance.

        HARDENING:
        1. Syncs with immutable Constitution on startup.
        2. Uses injected placement_validator to avoid L5 upward coupling.
        """
        self.registry: dict[str, list[dict[str, Any]]] = {}
        self._content_cache: dict[str, str] = {}  # cache for content hashing
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.embedding_model = EMBEDDING_MODEL

        # Dependency Injection for placement validation (Anti-Gravity)
        self.validator = placement_validator or _default_placement_validator

        # Validate placement without importing L5 directly
        is_valid, reason = self.validator(Path(__file__), Path.cwd())
        if not is_valid:
            Logger.warning(f"PromptRegistry placement violation: {reason}")

        self._load_registry()

        # HARDENING: Sync with immutable Constitution
        if CONSTITUTION_AVAILABLE:
            self._sync_with_constitution()

    def _sync_with_constitution(self) -> None:
        """Sync runtime registry with immutable Constitution.

        HARDENING: Ensures runtime state reflects canonical prompt definitions.
        This is a one-way sync: Constitution -> Registry (never reverse).
        """
        if not CONSTITUTION_AVAILABLE:
            return

        constitution = get_constitution()
        Logger.info(f"Syncing registry with {len(constitution.prompts)} canonical prompts")

        # Sync canonical prompts from Constitution
        for prompt_key, prompt_entry in constitution.prompts.items():
            # Check if this prompt is already registered
            if prompt_key not in self.registry:
                # Register from Constitution
                self.register_prompt(
                    template_name=prompt_key,
                    version=prompt_entry.version,
                    purpose="Canonical prompt from Constitution",
                    territory="constitution",
                    active=True,
                    author="PromptConstitution",
                    content=prompt_entry.content,
                )
                Logger.debug(f"Synced canonical prompt: {prompt_key}")

    def _load_registry(self) -> None:
        """Loads the registry from disk with defensive error handling."""
        if self.REGISTRY_FILE.exists():
            try:
                content = self.REGISTRY_FILE.read_text(encoding="utf-8")
                data = json.loads(content)
                self.registry = data.get("prompts", {})
                Logger.info(f"Loaded registry with {len(self.registry)} prompt families")
            except Exception as e:
                Logger.error(f"Failed to load {self.REGISTRY_FILE}: {e}")
                self.registry = {}
        else:
            Logger.info("No existing registry found, creating new")
            self.registry = {}
            self._save_registry()

    def _save_registry(self) -> None:
        """Saves the registry to disk using atomic-style write logic."""
        import tempfile
        from datetime import datetime

        data = {
            "sovereign_version": "1.0",
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "prompts": self.registry,
        }
        try:
            self.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write: temp file + rename for crash safety
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.REGISTRY_FILE.parent,
                delete=False,
                suffix=".tmp",
            ) as tmp:
                json.dump(data, tmp, indent=2)
                tmp_path = tmp.name

            # Atomic rename (POSIX-safe, Windows best-effort)
            Path(tmp_path).replace(self.REGISTRY_FILE)

        except OSError as e:
            Logger.error(f"PromptRegistry: Critical persistence failure: {e}")
            print(f"[!] PromptRegistry: Critical persistence failure: {e}")

    def _hash_content(self, content: str | None) -> str | None:
        """Generate content hash for deduplication. Returns None if no content."""
        if content is None:
            return None
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _compute_embedding(self, content: str | None) -> np.ndarray | None:
        """Compute normalized embedding for semantic similarity."""
        if content is None or not EMBEDDINGS_AVAILABLE:
            return None
        try:
            emb = get_embedding(content, model=self.embedding_model)
            vec = np.array(emb)
            norm = np.linalg.norm(vec)
            return vec / norm if norm != 0 else vec
        except Exception as e:
            Logger.warning(f"Failed to compute embedding: {e}")
            return None

    def _find_similar_prompts(self, new_emb: np.ndarray, template_name: str) -> list[dict]:
        """Find semantically similar prompts across registry."""
        similar = []
        for name, entries in self.registry.items():
            if name == template_name:
                continue  # Skip same template family
            for e in entries:
                if "embedding" in e and e["embedding"] is not None:
                    stored_emb = np.array(e["embedding"])
                    score = float(np.dot(new_emb, stored_emb))
                    if score >= self.similarity_threshold:
                        similar.append(
                            {
                                "name": name,
                                "version": e.get("version", "unknown"),
                                "similarity": score,
                                "prompt_snippet": e.get("content_hash", "")[:20],
                            }
                        )
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)

    def register_prompt(
        self,
        template_name: str,
        version: str = "v1",
        purpose: str = "",
        territory: str = "templates",
        active: bool = True,
        author: str = "SovereignOrchestrator",
        content: str | None = None,
    ) -> None:
        """
        Register or update a prompt version. Enforces single-active-version law.

        DEDUPLICATION: Prevents identical entries from accumulating.
        If an entry with same (template_name, version, purpose, author, content_hash, territory) exists,
        skip registration to prevent the 9-duplicate bug.

        SEMANTIC DEDUPLICATION: Checks for semantically similar prompts across registry
        using embedding-based similarity (threshold: 0.9). Raises DuplicatePromptError
        if a similar prompt is found to prevent sprawl.
        """
        # Compute embedding for semantic deduplication
        content_emb = self._compute_embedding(content) if content else None

        # Check for semantic duplicates across registry
        if content_emb is not None:
            similar = self._find_similar_prompts(content_emb, template_name)
            if similar:
                raise DuplicatePromptError(
                    f"Semantic duplicate detected (threshold {self.similarity_threshold}). "
                    f"Found {len(similar)} similar prompt(s): {similar[0]['name']} "
                    f"(similarity: {similar[0]['similarity']:.3f})",
                    similar,
                )

        if template_name not in self.registry:
            self.registry[template_name] = []

        # Compute content hash for deduplication
        content_hash = self._hash_content(content)

        # Define key fields for duplicate detection (ignores harmless differences like registered_date)
        DUPLICATE_KEY_FIELDS = {"version", "purpose", "author", "content_hash", "territory"}

        # DEDUPLICATION CHECK: Skip if identical entry already exists
        for existing_entry in self.registry[template_name]:
            # Compare only the key fields that matter for uniqueness
            if all(
                existing_entry.get(k) == v
                for k, v in {
                    "version": version,
                    "purpose": purpose,
                    "author": author,
                    "content_hash": content_hash,
                    "territory": territory,
                }.items()
                if k in DUPLICATE_KEY_FIELDS
            ):
                # Identical entry found
                if existing_entry["active"] == active:
                    Logger.debug(
                        f"Skipping duplicate registration: {template_name} {version} "
                        f"(author={author}, purpose={purpose[:30]}...)"
                    )
                    return  # Early exit - no changes needed
                else:
                    # Same entry but different active state - update it
                    existing_entry["active"] = active
                    self._save_registry()
                    Logger.info(f"Updated active state for {template_name} {version}")
                    return

        # Build new entry
        from datetime import datetime

        entry = {
            "version": version,
            "purpose": purpose,
            "territory": territory,
            "active": active,
            "author": author,
            "registered_date": datetime.now().strftime("%Y-%m-%d"),
        }
        if content_hash:
            entry["content_hash"] = content_hash
        if content_emb is not None:
            entry["embedding"] = content_emb.tolist()  # Store as list for JSON

        # Deactivate previous versions to ensure SSOT convergence (single active version)
        if active:
            for prev in self.registry[template_name]:
                prev["active"] = False

        # Append new entry and persist
        self.registry[template_name].append(entry)
        self._save_registry()
        Logger.info(
            f"Registered: {template_name} {version} (Territory: {territory}, Author: {author})"
        )
        print(f"    [REGISTERED] {template_name} {version} (Territory: {territory})")

    def get_active_version(self, template_name: str) -> dict[str, Any] | None:
        """Return the current active version metadata for a given template."""
        versions = self.registry.get(template_name, [])
        active = [v for v in versions if v.get("active", False)]
        return active[0] if active else None

    def list_active_prompts(self) -> list[str]:
        """List all currently active template names for mission planning."""
        return [
            name
            for name, versions in self.registry.items()
            if any(v.get("active") for v in versions)
        ]


class DuplicatePromptError(Exception):
    """Raised when a semantically duplicate prompt is detected."""

    def __init__(self, message, similar_entries) -> None:
        """Initialize the instance."""
        super().__init__(message)
        self.similar_entries = similar_entries


# Singleton Management
_global_registry: PromptRegistryAgent | None = None


def get_prompt_registry() -> PromptRegistryAgent:
    """Factory for singleton access. Bootstraps known templates on first call."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PromptRegistryAgent()

        # ===================================================================
        # Canonical Template Registry - FULLY MIGRATED TO AGENT-DRIVEN SSOT
        # ===================================================================
        # All canonical templates are now registered exclusively via @registers_prompt
        # decorators on their consuming agents. The registry is now a pure, self-maintaining
        # reflection of actual system prompt usage.
        #
        # Migration complete (agents with decorator):
        # ✅ gravity_repair.jinja          → ImportAgent
        # ✅ file_placement.jinja           → LocationAgent
        # ✅ red_team_governance.jinja      → RedTeamAgent
        # ✅ jailbreak_classic.jinja        → RedTeamAgent
        #
        # Templates without consuming agents (fallback-only, no decorator needed):
        # ⚠️  reasoning_chain.jinja          - No consuming agent found (template exists but unused)
        # ⚠️  type_inference.jinja           - No consuming agent found (template exists but unused)
        # ⚠️  code_healing.jinja             - No consuming agent found (template exists but unused)
        # ⚠️  sovereign_convergence_orchestrator.jinja - No consuming agent found (template exists but unused)
        #
        # These unused templates will NOT be registered until agents are created that use them.
        # This ensures the registry reflects actual usage, not aspirational templates.
        #
        # Registry maintenance:
        # - Deduplication: Handled by register_prompt() logic
        # - Runtime sync: ComplianceOrchestratorAgent._sync_agent_prompts_to_registry()
        # - Cleanup: Run cleanup_duplicates.py to remove historical duplicates
        #
        # Hardcoded registrations REMOVED - registry is now 100% agent-driven.
        # ===================================================================

        # No hardcoded registrations - all templates registered via @registers_prompt decorator
        pass
    return _global_registry


# ===================================================================
# DECORATOR: Agent-Driven Prompt Registration
# ===================================================================


def registers_prompt(
    template_name: str,
    purpose: str = "",
    version: str = "v1",
    territory: str = "templates",
    active: bool = True,
    content: str | None = None,
) -> Any:
    """
    Decorator for agents to declare their prompt template dependencies.

    Usage::

        @registers_prompt("gravity_repair.jinja", purpose="Fixes import violations")
        class ImportAgent:
            '''ImportAgent class.'''
            pass

    This enables:
    - Automatic registry updates when agents are imported
    - Runtime introspection via cls._registered_prompt
    - Agent-driven prompt discovery (no hardcoded lists)
    - Optional content hashing for version control
    """

    def decorator(cls) -> Any:
        """Execute decorator operation."""
        # Register at import time (safe due to deduplication)
        registry = get_prompt_registry()
        registry.register_prompt(
            template_name=template_name,
            version=version,
            purpose=purpose or f"Used by {cls.__name__}",
            territory=territory,
            author=cls.__name__,
            active=active,
            content=content,  # Passthrough for content-based hashing
        )

        # Store on class for runtime introspection
        cls._registered_prompt = template_name
        cls._prompt_version = version

        Logger.debug(f"Decorator registered prompt {template_name} for {cls.__name__}")
        return cls

    return decorator
