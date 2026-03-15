"""
SovereignBaseAgent - Sovereign Single Source of Truth (SSOT) Root.

Provides foundational capabilities for agents with sovereign authority.

PHASE 9 MIGRATION (Jan 2026):
- Global Injection of Phase 4-6 Architectures.
- Native capabilities: Config, LLM, Embedding, Healing, Validation.
- Resolves "Opt-In" drift by enforcing capabilities at the root.

PHASE 2 META-LEARNING (Feb 2026):
- MetaLearningClientMixin integration for healing pattern memory.
- Redis hot-path caching for expensive AST analysis results.
- Pinecone semantic retrieval for successful HealerMixin strategies.
- Domain isolation for apps_lic and apps_rg territories.

L0 DNA FLATTENING:
infrastructure_mixin consolidates core capabilities (legacy).
New Mixins provide Gateway access (modern).

MRO HARDENING:
- This is the ROOT of the agent hierarchy
- infrastructure_mixin is injected HERE so all agents get full infrastructure
- Layer bases add specialized mixins BEFORE SovereignBaseAgent
- MRO Flow: Specialized -> Layer -> SovereignBaseAgent -> [Mixins] -> object
"""

import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.enforcement.execution_gateway import (
    V15ExecutionGateway,
)
from agentic_core.L0_routing.enforcement.runtime_guard import (
    runtime_guard,
)
from agentic_core.L0_routing.enforcement.traceability_contracts import (
    generate_trace_id,
)
from agentic_core.L0_routing.types.determinism_types import (
    SurgicalManifest,
)
from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced
from agentic_core.L0_routing.utils.core_integrity_util import (
    CoreIntegrityVerifier,
    emergency_shutdown,
)
from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin
from agentic_core.mixins.audit_trail_mixin import AuditTrailMixin

# [PHASE 9] Global Architecture Injection
from agentic_core.mixins.configuration_mixin import ConfigMixin
from agentic_core.mixins.embedding_mixin import EmbeddingMixin

# [COGNITIVE HARDENING] Anti-Context Drift and Token Overload
from agentic_core.mixins.golden_context_mixin import GoldenContextMixin
from agentic_core.mixins.infrastructure_mixin import infrastructure_mixin
from agentic_core.mixins.llm_provider_mixin import LLMProviderMixin
from agentic_core.mixins.meta_learning_client_mixin import MetaLearningClientMixin
from agentic_core.mixins.runtime_safety_mixin import RuntimeSafetyMixin
from agentic_core.mixins.validator_mixin import ValidatorMixin
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


def _get_configuration_error():
    from agentic_core.runtime.exceptions.healer_exceptions import ConfigurationError

    return ConfigurationError


def _get_sovereign_error():
    from agentic_core.runtime.exceptions.SovereignError import SovereignError

    return SovereignError


def _get_sanitize_tool_output():
    from agentic_core.L4_state.utils.sanitize_telemetry_util import sanitize_tool_output

    return sanitize_tool_output


logger = logging.getLogger(__name__)


class SovereignBaseAgent(
    infrastructure_mixin,  # Provides the core set of mixins
    AtomicExecutionMixin,  # Not in infrastructure_mixin
    ConfigMixin,  # Not in infrastructure_mixin
    LLMProviderMixin,  # Not in infrastructure_mixin
    EmbeddingMixin,  # Not in infrastructure_mixin
    ValidatorMixin,  # Not in infrastructure_mixin
    AuditTrailMixin,  # Not in infrastructure_mixin
    MetaLearningClientMixin,  # Not in infrastructure_mixin
    GoldenContextMixin,  # Not in infrastructure_mixin
    RuntimeSafetyMixin,  # Not in infrastructure_mixin
    ADGBehavioralMixin,  # ADG behavioral score + antipattern signals for all agents
):
    """
    Sovereign Single Source of Truth (SSOT) Root.
    HARDENED: SSOT Root with comprehensive type safety and security validation.
    """

    def __init__(self, project_root: Path = None, **kwargs: Any) -> None:
        """
        Initialize sovereign capabilities with Hardening AND Integrity Lock.
        """
        super().__init__(**kwargs)
        self._sovereign_init(project_root=project_root)

    def __post_init__(self) -> None:
        """Cooperative MRO post-init for dataclass subclasses.

        Dataclass agents call super().__post_init__() instead of __init__.
        This method bridges the dataclass protocol into sovereign initialization,
        then propagates cooperative __post_init__ up the MRO chain.
        """
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        project_root = getattr(self, "project_root", None)
        self._sovereign_init(project_root=project_root)

    def _sovereign_init(self, project_root: Path = None) -> None:
        """Shared initialization body called by both __init__ and __post_init__."""
        if getattr(self, "_initialized", False):
            return

        if project_root is not None:
            self.project_root = project_root
        elif not hasattr(self, "project_root") or self.project_root is None:
            self.project_root = Path.cwd()

        self._initialized: bool = False
        self._security_validator: Any = None
        if not hasattr(self, "_state") or not isinstance(self._state, dict):
            self._state: dict = {"status": "booting", "health": "nominal"}
        if not hasattr(self, "_call_path") or not isinstance(self._call_path, set):
            self._call_path: set = set()

        # 1. THE IMMUTABLE LOCK CHECK
        try:
            CoreIntegrityVerifier.verify_core_integrity()
        # guardian: allow-silent-swallow
        except Exception as e:
            emergency_shutdown(f"CORE INTEGRITY COMPROMISED. TERMINATING AGENT. {e}")

        # 2. Security Validation
        self._security_hardening_validation()

        # 3. Telemetry Signal
        self.log_sovereign_event(
            "BOOT",
            {"status": "initialized", "mode": "hardened", "integrity_verified": True},
        )

        # V15: Conditionally instantiate gateway singleton (per-agent scope)
        self._v15_gateway = V15ExecutionGateway() if is_v15_enforced() else None

        self._initialized = True
        self._sovereign_initialized: bool = True

    def _security_hardening_validation(self) -> None:
        """
        Validate security constraints during initialization.
        HARDENED: Prevents insecure configurations and validates project structure.
        """
        try:
            # Validate project root is within allowed boundaries
            if not self._is_safe_path(self.project_root):
                raise ConfigurationError(f"Unsafe project root: {self.project_root}")

            # Validate required directories exist and are secure
            required_dirs = [AGENTIC_CORE_DIR]
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if dir_path.exists() and not self._is_safe_directory(dir_path):
                    raise ConfigurationError(f"Unsafe directory detected: {dir_path}")

        # guardian: allow-silent-swallow
        except Exception as e:
            raise ConfigurationError(f"Security validation failed: {str(e)}") from e

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe for access."""
        try:
            path.resolve().relative_to(Path.cwd().resolve())
            return True
        except ValueError:
            return False

    def _is_safe_directory(self, dir_path: Path) -> bool:
        """Check if directory is safe for modification."""
        return self._is_safe_path(dir_path) and dir_path.is_dir()

    def get_sovereign_capabilities(self) -> dict[str, Any]:
        """
        Get comprehensive list of sovereign capabilities.
        HARDENED: Returns capability map with security metadata.
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SovereignBaseAgent.get_sovereign_capabilities")
        if not self._initialized:
            raise SovereignError("SovereignBaseAgent not properly initialized")

        return {
            "healing": hasattr(self, "heal_repository"),
            "validation": hasattr(self, "validate_repository"),
            "testing": hasattr(self, "run_subatomic_tests"),
            "meta_learning": hasattr(self, "ml_recall_healing_pattern"),
            "security_validated": True,
            "mro_hardened": True,
            "project_root": str(self.project_root),
        }

    # Base execute method returns Any - subclasses should override with specific types
    @runtime_guard("B.execute.SovereignBaseAgent")
    # guardian: allow-type-erasure
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")

    def get_state(self, key: str) -> Any | None:
        """Get state value."""
        return getattr(self, "_state", {}).get(key)

    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        if not hasattr(self, "_state"):
            self._state = {}
        self._state[key] = value

    def get_authority_level(self) -> str:
        """Get the agent's authority level."""
        return getattr(self, "_authority_level", "standard")

    def elevate_authority(self, level: str) -> None:
        """Elevate the agent's authority level."""
        self._authority_level = level
        logger.info(f"Authority elevated to: {level}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{getattr(self, 'name', 'SovereignAgent')}] {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{getattr(self, 'name', 'SovereignAgent')}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{getattr(self, 'name', 'SovereignAgent')}] {message}")

    def log_feedback(
        self,
        workflow_id: str,
        action: str,
        status: str,
        details: dict[str, Any] = None,
    ) -> None:
        """Log feedback for a workflow action."""
        logger.info(
            f"[{getattr(self, 'name', 'SovereignAgent')}] Workflow {workflow_id}: "
            f"{action} - {status} - {details or {}}",
        )

    def heal(self, violation: dict[str, Any], **kwargs) -> dict[str, Any]:
        """
        Enhanced healing interface with meta-learning integration and V15 enforcement.

        Args:
            violation: Dictionary detailing the detected violation.
            **kwargs: Future-proofing for protocol expansions.

        Returns:
            Dict containing status and metadata with meta-learning enhancement.
        """
        # Phase 1: Route through V15ExecutionGateway when V15 enforcement is enabled
        if is_v15_enforced():
            return self._v15_enhanced_heal(violation, **kwargs)

        # Use meta-learning enhanced heal if available
        if hasattr(self, "ml_enhanced_heal") and hasattr(self, "_do_heal"):
            return self.ml_enhanced_heal(violation, self._do_heal, **kwargs)

        # Fallback to default implementation
        return {
            "status": "skipped",
            "reason": "default_base_implementation",
            "handler": self.__class__.__name__,
            "violation_id": violation.get("id", "unknown"),
        }

    def _v15_enhanced_heal(self, violation: dict[str, Any], **kwargs) -> dict[str, Any]:
        """V15-enforced healing through V15ExecutionGateway."""
        import hashlib as _hl

        # §15.5 — Generate V15-compliant trace ID: CC3AL1-{8 uppercase hex}
        # Derive deterministic 8-char hex suffix from violation + agent class name
        _seed = f"{self.__class__.__name__}:{violation.get('id', 'unknown')}:{id(violation)}"
        _hex8 = _hl.sha256(_seed.encode()).hexdigest()[:8].upper()
        trace_id = kwargs.get("trace_id", generate_trace_id(_hex8))

        # Convert violation to SurgicalManifest (Phase 1 simplified version)
        import hashlib

        from agentic_core.L0_routing.types.determinism_types import FixConstraint

        ast_snippet = f"heal({violation.get('id', 'unknown')})"

        manifest = SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id=self.__class__.__name__,
            target_layer="L2",
            ast_snippet=ast_snippet,
            serialization_canon="heal_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

        # Use per-agent gateway singleton (set in __post_init__)
        gateway = self._v15_gateway
        if gateway is None:
            raise RuntimeError(
                "V15ExecutionGateway is None but V15_ENFORCEMENT is active. "
                "Agent was likely instantiated before enforcement was enabled.",
            )

        def heal_fn(manifest: SurgicalManifest) -> dict[str, Any]:
            """Actual healing function passed to gateway."""
            # Use meta-learning enhanced heal if available
            if hasattr(self, "ml_enhanced_heal") and hasattr(self, "_do_heal"):
                return self.ml_enhanced_heal(violation, self._do_heal, **kwargs)

            # Default healing implementation
            return {
                "status": "completed",
                "reason": "v15_enforced_healing",
                "handler": self.__class__.__name__,
                "violation_id": violation.get("id", "unknown"),
                "trace_id": trace_id,
            }

        def state_hash_fn() -> tuple[str, str, str]:
            """Return current state hashes for rollback verification.

            §10.2 — Three-tuple: (filesystem_hash, git_state_hash, agent_memory_hash).
            - filesystem_hash: SHA-256 of sorted mtimes+sizes of .py files under
              project_root/agentic_core (first 200 entries, deterministic order).
            - git_state_hash: SHA-256 of .git/HEAD content (tracks branch/commit).
            - agent_memory_hash: SHA-256 of agent class name + _initialized flag
              (stable identity; changes only on hot-reload).
            """
            import os as _os

            from agentic_core.L5_safety.config.structure_blueprint.ssot import (
                SOVEREIGN_EXCLUDED_FOLDERS as _SEF,
            )

            # fs_hash: aggregate mtime+size of .py files under agentic_core/
            _core_dir = self.project_root / AGENTIC_CORE_DIR
            _fs_parts: list[str] = []
            if _core_dir.is_dir():
                for _root, _dirs, _files in _os.walk(str(_core_dir)):
                    _dirs[:] = sorted(d for d in _dirs if d not in _SEF)
                    for _f in sorted(_files):
                        if _f.endswith(".py"):
                            _fp = _os.path.join(_root, _f)
                            try:
                                _st = _os.stat(_fp)
                                _fs_parts.append(f"{_fp}:{_st.st_mtime_ns}:{_st.st_size}")
                            except OSError:
                                pass
                            if len(_fs_parts) >= 200:
                                break
                    if len(_fs_parts) >= 200:
                        break
            _fs_hash = _hl.sha256("\n".join(_fs_parts).encode()).hexdigest()

            # git_hash: SHA-256 of .git/HEAD content
            _git_head = self.project_root / ".git" / "HEAD"
            try:
                _git_bytes = _git_head.read_bytes()
            except OSError:
                _git_bytes = b"no-git"
            _git_hash = _hl.sha256(_git_bytes).hexdigest()

            # mem_hash: stable agent identity hash
            _mem_seed = f"{self.__class__.__name__}:{self._initialized}"
            _mem_hash = _hl.sha256(_mem_seed.encode()).hexdigest()

            return (_fs_hash, _git_hash, _mem_hash)

        # Execute through gateway
        result = gateway.execute(
            execution_input=manifest,
            heal_fn=heal_fn,
            state_hash_fn=state_hash_fn,
            trace_id=trace_id,
            agent_id="sovereign_base",
        )

        # Return gateway result in expected format
        if result.success:
            return {
                "status": "completed",
                "reason": "v15_enforced_healing",
                "handler": self.__class__.__name__,
                "violation_id": violation.get("id", "unknown"),
                "trace_id": trace_id,
                "semantic_clock_tick": result.semantic_clock_tick,
                "gateway_result": result.healing_output,
            }
        else:
            return {
                "status": "failed",
                "reason": result.error or "v15_gateway_failure",
                "handler": self.__class__.__name__,
                "violation_id": violation.get("id", "unknown"),
                "trace_id": trace_id,
                "error": result.error,
            }

    def _do_heal(self, violation: dict[str, Any], **kwargs) -> dict[str, Any]:
        """
                Actual healing implementation to be called by meta-learning enhanced heal.

                Subclasses should override this method instead of heal() to benefit
                from meta-learning capabilities.
        from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

                Args:
                    violation: Dictionary detailing the detected violation.
                    **kwargs: Additional arguments for healing.

                Returns:
                    Dict containing healing result.
        """
        return {
            "status": "skipped",
            "reason": "default_base_implementation",
            "handler": self.__class__.__name__,
            "violation_id": violation.get("id", "unknown"),
        }

    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        _call_path: set | None = None,
        depth: int = 0,
        max_depth: int = 8,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Repository-wide healing interface with deterministic baseline.

        Phase 2: Deterministic file operations only by default. No LLM calls unless:
        - enable_llm=True (env: HEAL_POLICY_MODEL_ESCALATION=1) AND
        - policy returns proceed=True with tier != None

        Args:
            dry_run: If True, report violations without fixing (default: True)
            execute: If True, apply fixes (default: False)
            **kwargs: Additional parameters including _confidence, _task_complexity

        Returns:
            Dict containing healing result with canonical HealResult schema.
        """
        import os
        import time

        # Cycle detection: if this agent class is already in the call path, skip
        agent_name = self.__class__.__name__
        active_path = _call_path if _call_path is not None else set()
        if agent_name in active_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "status": "SKIPPED",
                "errors": 0,
                "skipped": 1,
            }
        # Max depth guard
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "status": "SKIPPED",
                "errors": 0,
                "skipped": 1,
            }

        from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier

        start_time = time.time()

        # Extract inputs from kwargs
        confidence_value = kwargs.pop("_confidence", 0.75)
        kwargs.pop("_task_complexity", None)
        kwargs.pop("_prior_failures", None)
        retry_count = kwargs.pop("_retry_count", 0)

        # Delegate to canonical routing choke-point
        heal_decision = route_by_confidence(
            confidence=confidence_value,
            retry_count=retry_count,
        )

        # Hard gate: FAIL_CLOSED → refusal (routing always proceeds for other tiers)
        if heal_decision.tier not in (
            HealingTier.LOCAL_AGENT,
            HealingTier.QWEN_VLLM,
            HealingTier.GEMINI_2_5_PRO,
        ):
            execution_time_ms = (time.time() - start_time) * 1000
            rationale = " | ".join(heal_decision.reason_codes)
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "status": "BLOCKED",
                "errors": 0,
                "skipped": 0,
                "execution_time_ms": execution_time_ms,
                "error_message": rationale,
                "_policy_decision": {
                    "proceed": False,
                    "tier": None,
                    "threshold_used": "CANONICAL_ROUTER",
                    "rationale": rationale,
                },
            }

        # Phase 4: Use deterministic repo-heal pipeline (baseline first)
        from agentic_core.L5_safety.types.heal_llm_seam_types import (
            apply_repo_heal_plan,
            build_repo_heal_plan,
        )

        violations_found = 0
        violations_fixed = 0
        errors = 0
        plan_result = None

        try:
            # Step 1: Build deterministic baseline plan (no LLM)
            if hasattr(self, "project_root") and self.project_root.exists():
                plan = build_repo_heal_plan(str(self.project_root))
                plan_result = apply_repo_heal_plan(plan, dry_run=dry_run)

                # Baseline reports validation-only operations
                violations_found = plan_result.operations_failed
                violations_fixed = 0 if dry_run else plan_result.operations_succeeded

                # Step 2: Check if unresolved issues remain AND LLM escalation allowed
                unresolved = plan_result.operations_failed > 0
                if unresolved and policy_decision.tier is not None and enable_llm:
                    # LLM escalation would happen here via guarded_heal_llm_call
                    # But we don't actually call it in baseline - just log intent
                    logger.debug(
                        f"[heal_repository] {agent_name} would escalate to LLM "
                        f"tier={policy_decision.tier.name} (unresolved={unresolved})"
                    )

        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-silent-swallower
            errors = 1
            logger.error(f"[heal_repository] {agent_name} error: {e}")

        execution_time_ms = (time.time() - start_time) * 1000
        status = "PASS" if violations_found == 0 and errors == 0 else "FAIL"

        return {
            "violations_found": violations_found,
            "violations_fixed": violations_fixed,
            "status": status,
            "errors": errors,
            "skipped": 0,
            "execution_time_ms": execution_time_ms,
            "error_message": None,
            "_policy_decision": {
                "proceed": policy_decision.proceed,
                "tier": policy_decision.tier.name if policy_decision.tier else None,
                "threshold_used": policy_decision.threshold_used,
            },
            "_deterministic_baseline": True,
        }

    # =========================================================================
    # COGNITIVE ENDURANCE INFRASTRUCTURE (Feb 2026)
    # Landmine #3 & #4 Prevention: Context Drift and Token Overload
    # =========================================================================

    # Default max_chars for output sanitization
    # guardian: allow-magic-config
    def sanitize_output(self, output: str, max_chars: int = 2000) -> str:
        """
        Sanitize tool output to prevent token overload.

        Wraps the telemetry_sanitizer.sanitize_tool_output function for
        convenient access from agent instances.

        Args:
            output: The raw tool output string.
            max_chars: Maximum allowed characters before pruning.

        Returns:
            Sanitized output string, pruned if necessary.
        """
        return sanitize_tool_output(output, max_chars=max_chars)

    # Default context_threshold for message preparation
    # guardian: allow-magic-config
    def prepare_messages_for_llm(
        self,
        messages: list[dict[str, Any]],
        inject_context: bool = True,
        context_threshold: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Prepare messages for LLM call with cognitive hardening.

        This method should be called before any LLM invocation to:
        1. Optionally inject golden context (anti-drift)
        2. Future: Apply other cognitive safeguards

        Args:
            messages: The current message list.
            inject_context: Whether to inject golden context.
            context_threshold: Message count threshold for injection.

        Returns:
            Prepared message list ready for LLM call.
        """
        if inject_context and self.should_inject_golden_context(messages, context_threshold):
            return self.inject_golden_context(messages)
        return messages


__all__ = ["SovereignBaseAgent", "sanitize_tool_output", "RuntimeSafetyMixin"]
