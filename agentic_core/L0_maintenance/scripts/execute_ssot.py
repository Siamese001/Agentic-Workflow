#!/usr/bin/env python3
"""
Unified Sovereign Compliance Protocol (v4.0)
Merges SSOT Compliance Protocol (Autonomous Decision Engine) with Canon Validator (Observability & Discovery).

PRIMARY FEATURES:
- Autonomous Confidence-Based Healing (SSOT)
- Real-time Runtime State & Dashboard Integration (Canon)
- Multi-Domain Orchestration (Canon)
- Hybrid Agent Discovery (Canon)
- Comprehensive Audit Trail (SSOT)
"""

# [IMPORTS] Added for dynamic loading and signal handling
import argparse
import atexit  # [HARDENED] For guaranteed state cleanup
import builtins
import importlib.util
import inspect
import json
import logging
import os
import platform
import signal
import stat  # [HARDENED] For permission bits
import subprocess
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from subprocess import DEVNULL
from types import FrameType
from typing import Any, Optional


def _optional_v15_runtime_guard():
    """Lazy import to avoid import-time failure in bootstrap contexts.

    Fail-closed semantics: when V15_ENFORCEMENT=1 and the guard cannot be
    imported, re-raise so the caller sees a hard failure instead of a silent
    no-op.  When enforcement is off (or unset), fall back to a no-op decorator.
    """
    try:
        from agentic_core.L0_maintenance.enforcement.v15_runtime_guard import v15_runtime_guard

        return v15_runtime_guard
    # guardian: allow-silent-swallow
    except Exception:
        if os.getenv("V15_ENFORCEMENT") == "1":
            raise  # fail-closed: enforcement is on but guard is unavailable

        def _noop_guard(_entry_point_id: str):
            """No-op: accepts an ID string and returns an identity decorator."""

            def _identity(func):
                return func

            return _identity

        return _noop_guard


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import ast
import re

try:
    from agentic_core.base_agents.decorators import HEAL_RESULT_SCHEMA, standard_heal
except ImportError:
    # Fallback for bootstrapping scenarios
    def standard_heal(func):
        return func

    HEAL_RESULT_SCHEMA = {}

try:
    from agentic_core.base_agents.IHealerProtocol import IHealerProtocol, LegacyAgentAdapter
except ImportError:
    # Fallback for bootstrapping scenarios
    class IHealerProtocol:
        pass

    class LegacyAgentAdapter:
        def __init__(self, legacy_agent):
            self.agent = legacy_agent

        def heal(self, violation):
            return {"status": "failed", "errors": ["Adapter not available"]}


def resolve_repo_root(start=None):
    """Deterministic repo-root resolver.
    Walk upward from this file (or provided start) until we find repo markers.
    """
    cur = Path(start or __file__).resolve()
    for p in (cur, *cur.parents):
        if (p / "agentic_core").is_dir() and (p / "ops_scripts").is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


REPO_ROOT = resolve_repo_root()  # noqa: N816


def _apply_v15_enforcement_flag(args: argparse.Namespace) -> None:
    """CLI overrides env to ensure determinism in CI/smoke paths."""
    if getattr(args, "v15_enforcement", None) is None:
        return
    os.environ["V15_ENFORCEMENT"] = "1" if int(args.v15_enforcement) == 1 else "0"


def _configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )


def _maybe_force_utf8_console() -> None:
    """Opt-in Windows console UTF-8 coercion.  Called at runtime, NOT import time."""
    if not sys.platform.startswith("win"):
        return
    if os.getenv("EXECUTE_SSOT_FORCE_UTF8", "0") != "1":
        return
    try:
        subprocess.run(["chcp", "65001"], stdout=DEVNULL, stderr=DEVNULL, check=False)
    except FileNotFoundError:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    # guardian: allow-silent-swallow
    except Exception:
        return


# ============================================================================
# V15 MANIFEST CONSTRUCTION (§8.1e)
# ============================================================================


def _v15_build_ssot_manifest():
    """§8.1e — Construct SurgicalManifest for SSOT bootstrap entry.

    Returns None when V15 enforcement is off (zero overhead).
    Bootstrap-safe: lazy imports with fail-closed semantics.
    """
    try:
        from agentic_core.L0_maintenance.types.guardian_contract import is_v15_enforced

        if not is_v15_enforced():
            return None

        import hashlib as _hl

        from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_maintenance.types.v15_p2_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = _hl.sha256(b"execute_ssot._legacy_main").hexdigest()[:8].upper()
        trace_id = generate_trace_id(_hex8)

        ast_snippet = "execute_ssot._legacy_main()"
        return SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id="ExecuteSSOT",
            target_layer="L0",
            ast_snippet=ast_snippet,
            serialization_canon="execute_ssot",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=_hl.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )
    # guardian: allow-silent-swallow
    except Exception:
        if os.getenv("V15_ENFORCEMENT") == "1":
            raise  # fail-closed when hard enforcement is on
        return None


def _v15_ssot_gateway_audit(manifest, trace_id: str) -> None:
    """§8.1e — Invoke gateway.execute in LOG_ONLY mode for SSOT audit trail."""
    if manifest is None:
        return
    try:
        import hashlib as _hl

        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import (
            V15ExecutionGateway,
        )

        gw = V15ExecutionGateway()
        gw.execute(
            manifest,
            lambda m: {"status": "ssot_audit", "errors": 0},
            lambda: (
                _hl.sha256(b"fs_ssot").hexdigest(),
                _hl.sha256(b"git_ssot").hexdigest(),
                _hl.sha256(b"mem_ssot").hexdigest(),
            ),
            trace_id=trace_id,
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        logging.getLogger(__name__).warning("[V15] SSOT gateway audit failed (LOG_ONLY): %s", exc)


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ConfidenceScore:
    """[HARDENED] Environment-aware confidence score for autonomous healing."""

    value: float  # 0.0 to 1.0
    reasoning: str
    factors: dict[str, float] = field(default_factory=dict)

    @property
    def _high_threshold(self) -> float:
        """Sourced from .env: SOVEREIGN_HIGH_CONFIDENCE (default: 0.75)"""
        return float(os.getenv("SOVEREIGN_HIGH_CONFIDENCE", "0.75"))

    @property
    def _med_threshold(self) -> float:
        """Sourced from .env: SOVEREIGN_MEDIUM_CONFIDENCE (default: 0.50)"""
        return float(os.getenv("SOVEREIGN_MEDIUM_CONFIDENCE", "0.50"))

    @property
    def is_high_confidence(self) -> bool:
        return self.value > self._high_threshold

    @property
    def is_medium_confidence(self) -> bool:
        return self._med_threshold <= self.value <= self._high_threshold

    @property
    def is_low_confidence(self) -> bool:
        return self.value < self._med_threshold


# ============================================================================
# NEW DATA STRUCTURES FOR TELEMETRY AND VALIDATION
# ============================================================================


@dataclass
class ReconciliationViolation:
    """Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler)."""

    is_valid: bool
    message: str
    drift_type: str | None = None
    file_path: Path | None = None
    suggested_action: str | None = None
    severity: int = 5  # 1-10 scale

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "drift_type": self.drift_type,
            "file_path": str(self.file_path.as_posix()) if self.file_path else None,
            "severity": self.severity,
        }


@dataclass
class ReconciliationManifest:
    """Telemetry manifest for tracking all reconciliation changes."""

    mission_id: str
    territory: str
    start_time: str
    end_time: str | None = None
    violations_found: int = 0
    violations_attempted: int = 0
    violations_fixed: int = 0
    violations_failed: int = 0
    modifications: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    budget_consumed: int = 0
    confidence_scores: list[float] = field(default_factory=list)

    def add_modification(self, modification: dict[str, Any]) -> None:
        self.modifications.append(modification)
        self.violations_attempted += 1
        if modification.get("success", False):
            self.violations_fixed += 1
        else:
            self.violations_failed += 1

    def add_failure(self, failure: dict[str, Any]) -> None:
        self.failures.append(failure)
        self.violations_failed += 1

    def finalize(self) -> dict[str, Any]:
        self.end_time = datetime.now().isoformat()
        return {
            "mission_id": self.mission_id,
            "territory": self.territory,
            "duration": {
                "start": self.start_time,
                "end": self.end_time,
                "seconds": (
                    datetime.fromisoformat(self.end_time) - datetime.fromisoformat(self.start_time)
                ).total_seconds()
                if self.end_time
                else None,
            },
            "violations": {
                "found": self.violations_found,
                "attempted": self.violations_attempted,
                "fixed": self.violations_fixed,
                "failed": self.violations_failed,
                "success_rate": self.violations_fixed / max(self.violations_attempted, 1),
            },
            "budget": {
                "consumed": self.budget_consumed,
                "remaining": max(0, 100 - self.budget_consumed),  # Default max budget of 100
            },
            "confidence": {
                "scores": self.confidence_scores,
                "average": sum(self.confidence_scores) / len(self.confidence_scores)
                if self.confidence_scores
                else 0.0,
            },
            "modifications": self.modifications,
            "failures": self.failures,
        }


class ASTCodeQualityValidator:
    """AST-based code quality validation with memory guards (Ported from TypeMechanic)."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # [SAFETY] Prevent OOM on massive generated files
        # guardian: allow-magic-config
        self.max_file_size = 1_000_000  # 1MB limit

    def _read_and_parse_file(self, fp: str) -> tuple[ast.AST | None, str | None]:
        """Reads a file and parses it into an AST with strict size limits."""
        try:
            if os.path.getsize(fp) > self.max_file_size:
                return None, "File too large for AST analysis"

            with open(fp, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
                return tree, None
        except (OSError, SyntaxError) as e:
            return None, f"Error parsing {fp}: {str(e)}"

    # guardian: allow-type-erasure
    def check_file_quality(self, file_path: Path) -> dict:
        """Check file for code quality issues (missing types, etc)."""
        violations = []
        tree, error = self._read_and_parse_file(str(file_path))

        if error:
            return {"error": error, "violations": []}

        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignore dunders
                    if not node.returns and not node.name.startswith("__"):
                        violations.append(
                            {
                                "type": "MISSING_TYPE_HINT",
                                "file": str(file_path),
                                "line": node.lineno,
                                "message": f"Function '{node.name}' missing return type hint",
                            },
                        )

        return {
            "violations": violations,
            "violations_count": len(violations),
            "file": str(file_path),
        }


# ============================================================================
# ENHANCED DECISION ENGINE WITH SEMANTIC SCORING & CYCLE DETECTION
# ============================================================================


class AutonomousDecisionEngine:
    """Makes autonomous healing decisions based on confidence scores."""

    def __init__(self, enable_llm: bool = False, state_mgr: Optional["RuntimeStateManager"] = None):
        self.enable_llm = enable_llm
        self.decisions_made = []
        self.state_mgr = state_mgr
        # [SAFETY] Cycle Detection State
        self._healing_count: int = 0
        self._healing_enabled: bool = True
        self._max_healing_operations: int = 100
        self._call_path: set[str] = set()

    def _calculate_semantic_similarity(self, unknown: str, existing: list[str]) -> float:
        """Calculate Jaccard similarity for unknown items (Ported from LocationHealer)."""
        if not existing:
            return 0.0

        unknown_words = set(unknown.lower().replace("_", " ").replace("-", " ").split())
        max_similarity = 0.0

        for item in existing:
            existing_words = set(item.lower().replace("_", " ").replace("-", " ").split())
            intersection = unknown_words & existing_words
            union = unknown_words | existing_words

            if union:
                similarity = len(intersection) / len(union)
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _calculate_pattern_confidence(self, violation_type: str) -> float:
        """Regex-based pattern matching for known violation types."""
        high_confidence_patterns = [
            r".*NAMING.*",
            r".*HIERARCHY.*",
            r".*IMPORT.*",
            r".*SHALLOW.*",
            r".*DEEP.*",
            r".*VOID.*",
            r".*DUPLICATE.*",
            r".*ORPHAN.*",
        ]

        for pattern in high_confidence_patterns:
            if re.match(pattern, violation_type, re.IGNORECASE):
                return 0.9
        return 0.5

    # guardian: allow-magic-config
    def _check_healing_budget(self, agent_name: str, depth: int = 0, max_depth: int = 3) -> tuple[bool, str]:
        """Prevents infinite healing loops and budget exhaustion."""
        if agent_name in self._call_path:
            return False, f"Healing cycle detected: {agent_name}"
        if depth > max_depth:
            return False, f"Healing depth limit exceeded for {agent_name}"
        if self._healing_count >= self._max_healing_operations:
            return False, f"Budget exceeded ({self._healing_count})"
        return True, "OK"

    # guardian: allow-magic-config
    def calculate_healing_confidence(
        self,
        violations_count: int,
        violation_types: list[str],
        territory: str,
        historical_success_rate: float = 0.8,
    ) -> ConfidenceScore:
        """Calculates weighted confidence score."""
        # 1. Base Score (Inverse of violations, capped at 10)
        base_score = max(0.0, 1.0 - (min(violations_count, 10) * 0.1))

        # 2. Pattern Score
        pattern_score = 0.5
        if violation_types:
            scores = [self._calculate_pattern_confidence(v) for v in violation_types]
            pattern_score = sum(scores) / len(scores)

        # 3. Weighted Final Calculation
        final_value = (base_score * 0.4) + (pattern_score * 0.4) + (historical_success_rate * 0.2)

        # Boost for governance territories, penalty for safety critical
        if territory == "prompt_governance":
            final_value *= 1.1
        if territory.startswith("L5"):
            final_value *= 0.9

        return ConfidenceScore(
            value=min(1.0, final_value),
            reasoning=f"Base: {base_score:.2f}, Pattern: {pattern_score:.2f}",
        )

    def should_proceed_with_healing(
        self,
        confidence: ConfidenceScore,
        agent_name: str = "Unknown",
    ) -> tuple[bool, str]:
        """Determines if healing should proceed with mandatory safety checks."""
        # [SAFETY] Hard Gate: Check Budget/Cycles first
        is_safe, msg = self._check_healing_budget(agent_name)
        if not is_safe:
            return False, f"SAFETY LOCK: {msg}"

        # Decision tracking for enhanced reporting
        decision_data = {
            "agent": agent_name,
            "confidence": confidence.value,
            "reasoning": confidence.reasoning,
            "timestamp": datetime.now().isoformat(),
            "decision": None,
            "reason": None,
        }

        # [PHASE 4 FIX] High Confidence: Deterministic Sovereign Execution
        if confidence.is_high_confidence:
            self._healing_count += 1
            self._call_path.add(agent_name)
            reason = f"SOVEREIGN-AUTO ({confidence.value:.2f})"
            decision_data["decision"] = True
            decision_data["reason"] = reason
            self.decisions_made.append(decision_data)
            return True, reason

        # [PHASE 4 FIX] Medium Confidence: Standard Arbitration (Flash via .env)
        elif confidence.is_medium_confidence:
            if self.enable_llm:
                target_model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
                self._healing_count += 1
                self._call_path.add(agent_name)
                reason = f"LLM-ARBITRATED-FLASH ({confidence.value:.2f})"
                decision_data["decision"] = True
                decision_data["reason"] = reason
                decision_data["model"] = target_model
                self.decisions_made.append(decision_data)
                return True, reason
            else:
                reason = f"BLOCK: Confidence {confidence.value:.2f} requires LLM arbitration (Disabled)"
                decision_data["decision"] = False
                decision_data["reason"] = reason
                self.decisions_made.append(decision_data)
                return False, reason

        # [PHASE 4 FIX] Low Confidence: Advanced Reasoning Recovery (Pro via .env)
        else:
            if self.enable_llm:
                target_model = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
                logger.warning(
                    f"🚨 CRITICAL AMBIGUITY: Invoking Reasoning Model {target_model} for {agent_name}...",
                )
                self._healing_count += 1
                self._call_path.add(agent_name)
                reason = f"REASONING-RECOVERY-PRO ({confidence.value:.2f})"
                decision_data["decision"] = True
                decision_data["reason"] = reason
                decision_data["model"] = target_model
                self.decisions_made.append(decision_data)
                return True, reason
            else:
                reason = f"BLOCK: Confidence {confidence.value:.2f} requires advanced reasoning (Disabled)"
                decision_data["decision"] = False
                decision_data["reason"] = reason
                self.decisions_made.append(decision_data)
                return False, reason


# ============================================================================
# ENHANCED DECISION ENGINE WITH COGNITIVE DISPOSITION AGENT INTEGRATION
# ============================================================================


class EnhancedAutonomousDecisionEngine(AutonomousDecisionEngine):
    """Enhanced decision engine with CognitiveDispositionAgent integration."""

    def __init__(
        self,
        enable_llm: bool = False,
        state_mgr: Optional["RuntimeStateManager"] = None,
        enable_cda: bool = False,
    ):
        super().__init__(enable_llm=enable_llm, state_mgr=state_mgr)
        self.enable_cda = enable_cda
        # Initialize decisions_made if not already present from parent
        if not hasattr(self, "decisions_made"):
            self.decisions_made = []

    async def analyze_violations_with_cognitive_disposition(
        self,
        violations: list,
        territory: str,
        state_mgr,
    ):
        """Analyze violations using CognitiveDispositionAgent for enhanced confidence."""
        if not self.enable_cda:
            # Return default values if CDA is disabled
            return [], ConfidenceScore(value=0.5, reasoning="CDA disabled")

        try:
            # Dynamic import of CDA to avoid hard dependency
            from agentic_core.L5_safety.validators.CognitiveDispositionAgent import (
                CognitiveDispositionAgent,
            )

            cda = CognitiveDispositionAgent()

            # Analyze violations
            dispositions = await cda.analyze_violations(violations, territory)

            # Calculate enhanced confidence based on cognitive analysis
            if dispositions:
                avg_confidence = sum(d.confidence for d in dispositions) / len(dispositions)
                enhanced_confidence = ConfidenceScore(
                    value=avg_confidence,
                    reasoning=f"Cognitive analysis of {len(dispositions)} dispositions",
                )
            else:
                enhanced_confidence = ConfidenceScore(
                    value=0.5,
                    reasoning="No cognitive dispositions generated",
                )

            return dispositions, enhanced_confidence

        except ImportError:
            logger.warning("CognitiveDispositionAgent not available, using default confidence")
            return [], ConfidenceScore(value=0.5, reasoning="CDA unavailable")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Cognitive analysis failed: {e}")
            return [], ConfidenceScore(value=0.5, reasoning=f"CDA error: {str(e)}")


class SovereignDecisionEngine(EnhancedAutonomousDecisionEngine):
    """
    [HARDENED] Sovereign Decision Engine with strict token-based access control.
    Synthesizes patterns from FileClassificationAgent for cycle detection and resource protection.
    """

    def __init__(
        self,
        enable_llm: bool = False,
        state_mgr: Optional["RuntimeStateManager"] = None,
        enable_cda: bool = False,
    ):
        super().__init__(enable_llm, state_mgr, enable_cda)
        self._sovereignty_token: str | None = None
        self._operation_stack: list[str] = []
        # guardian: allow-magic-config
        self._max_stack_depth = 10  # Prevent infinite recursion
        self._atomic_lock = False

    def request_sovereignty_token(self, agent_name: str, operation: str) -> bool:
        """
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        """
        if self._atomic_lock:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Atomic lock active")
            return False

        if len(self._operation_stack) >= self._max_stack_depth:
            logging.critical(
                f"Sovereignty DENIED for {agent_name}: Stack depth exceeded ({len(self._operation_stack)})",
            )
            return False

        # Cycle detection
        op_signature = f"{agent_name}:{operation}"
        if op_signature in self._operation_stack:
            logging.warning(f"Sovereignty DENIED for {agent_name}: Cycle detected {op_signature}")
            return False

        self._operation_stack.append(op_signature)
        self._atomic_lock = True
        self._sovereignty_token = f"SOV_{int(time.time())}_{agent_name}"
        return True

    def release_sovereignty_token(self, agent_name: str, success: bool = True) -> None:
        """Release the lock after operation completion."""
        if not self._atomic_lock:
            return

        if self._operation_stack:
            self._operation_stack.pop()

        self._atomic_lock = False
        self._sovereignty_token = None

        if not success:
            logging.warning(f"Sovereignty released with FAILURE status for {agent_name}")


# ============================================================================
# PRE-FLIGHT VALIDATION LAYER (HARDENED)
# ============================================================================


class PreFlightValidator:
    """
    [ULTRA-HARDENED] Sovereign Contract Enforcer.
    Verifies environmental readiness and enforces strict agent signatures/imports.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_checks(self) -> tuple[bool, list[str]]:
        errors = []

        # 1. Windows Long Paths (System Stability)
        if platform.system() == "Windows":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\FileSystem",
                )
                val, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if val != 1:
                    errors.append("Windows LongPathsEnabled is NOT active (Set to 1 in Registry)")
            # guardian: allow-silent-swallow
            except Exception as e:
                logging.warning(f"Could not verify Windows LongPathsEnabled: {e}")

        # 2. Critical Directory Structure (SSOT Integrity)
        required_dirs = ["agentic_core", "agentic_core/L5_safety", "agentic_core/prompt_governance"]
        for d in required_dirs:
            if not (self.project_root / d).exists():
                errors.append(f"Critical directory missing: {d}")

        # 3. Write Permissions (Operational Readiness)
        try:
            test_file = self.project_root / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            errors.append("Project root is not writable")

        return len(errors) == 0, errors

    def validate_agent_integrity(self, agents: dict[str, Any]) -> list[str]:
        """
        [CONTRACT GUARD] Mandatory validation of all registered agents.
        Catches legacy signatures, broken mixins, and instantiation failures.
        """
        integrity_errors = []
        for name, agent_cls in agents.items():
            try:
                # Force instantiation to catch import/mixin errors immediately
                agent = agent_cls(project_root=self.project_root) if inspect.isclass(agent_cls) else agent_cls
            # guardian: allow-silent-swallow
            except Exception as e:
                integrity_errors.append(f"Agent {name} FAILED INSTANTIATION: {e}")
                continue

            # 1. Presence of 'heal' method
            if not hasattr(agent, "heal") or not callable(agent.heal):
                integrity_errors.append(f"Agent {name} violates Protocol: Missing 'heal' method")
                continue

            # 2. Signature Validation: heal(violation: dict)
            sig = inspect.signature(agent.heal)
            params = list(sig.parameters.keys())

            if "violation" not in params and "kwargs" not in params:
                if "path" in params and len(params) == 1:
                    integrity_errors.append(
                        f"Agent {name} has LEGACY SIGNATURE: heal(path). Must update to heal(violation).",
                    )
                else:
                    integrity_errors.append(
                        f"Agent {name} has INVALID SIGNATURE: {sig}. Expected heal(self, violation, ...).",
                    )

            # 3. Mixin Verification (MRO Audit)
            mro_names = [c.__name__ for c in inspect.getmro(agent.__class__)]
            if "NamingAgent" in name and "SubatomicTestingMixin" not in mro_names:
                integrity_errors.append(f"Agent {name} missing mandatory SubatomicTestingMixin in MRO.")

        return integrity_errors


# ============================================================================
# HARDENING UTILITIES (NEW)
# ============================================================================


class NonInteractiveGuard:
    """
    [HARDENED] Global overrides to prevent terminal prompts from hanging CI/CD.
    Now includes Resource Exhaustion Protection against infinite prompt loops.
    """

    # guardian: allow-magic-config
    def __init__(self, active: bool = True, max_blocked_prompts: int = 10):
        self.active = active
        self.max_blocked_prompts = max_blocked_prompts
        self.blocked_count = 0
        self.original_input = builtins.input

    def __enter__(self):
        if self.active:
            builtins.input = self._trap_input
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.input = self.original_input

    def _trap_input(self, prompt=None):
        self.blocked_count += 1
        logger.warning(
            f"BLOCKED PROMPT ({self.blocked_count}/{self.max_blocked_prompts}): Agent attempted input('{prompt}')",
        )

        # [HARDENED] Resource Exhaustion Protection
        if self.blocked_count > self.max_blocked_prompts:
            logger.critical("Infinite prompt loop detected - killing process capability")
            raise RecursionError("Interactive prompt limit exceeded (Infinite Loop Protection)")

        raise RuntimeError(f"Interactive prompt blocked in autonomous mode: {prompt}")


@_optional_v15_runtime_guard()("D.with_retry.execute_ssot")
# guardian: allow-magic-config
def with_retry(max_retries=3, delay=1.0):
    """
    [HARDENED] Decorator for transient failure resilience with exponential backoff.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                # guardian: allow-silent-swallow
                except Exception as e:
                    last_exception = e
                    # Don't retry on security guard or exhaustion errors
                    if isinstance(e, RuntimeError) and "prompt" in str(e):
                        raise e
                    if isinstance(e, RecursionError):
                        raise e

                    wait_time = delay * (2**attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} failed: {e}. Waiting {wait_time}s",
                    )
                    time.sleep(wait_time)
            logger.error(f"All retries failed for {func.__name__}")
            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# PHASE 2: RECONCILIATION (The Dangerous Phase)
# ============================================================================


# guardian: allow-magic-config
@with_retry(max_retries=2)
def execute_phase2_reconciliation(
    agents: dict[str, Any],
    territory: str,
    decision_engine: SovereignDecisionEngine,  # [HARDENED] Updated type
    state_mgr: "RuntimeStateManager",
    plan: dict[str, Any],
    dry_run: bool = False,
    **kwargs,
):
    """
    PHASE 2: EXECUTE HEALING (HARDENED)
    Critical Path: Modifications occur here. Must strictly adhere to decision engine.
    Enhanced with atomic operations and sovereignty patterns from FileClassificationAgent.
    Returns: Dict conforming to HEAL_RESULT_SCHEMA
    """
    reconciliation_log = []
    failed_fixes = []

    if not plan or not plan.get("violations_found"):
        logging.info("Phase 2: No violations to reconcile.")
        return {
            "violations_found": 0,
            "violations_fixed": 0,
            "status": "skipped",
            "errors": 0,
            "skipped": 0,
            "execution_time_ms": 0.0,
            "error_message": None,
        }

    logging.info(f"Phase 2: Attempting to reconcile {len(plan['violations_found'])} violations...")

    for violation in plan["violations_found"]:
        agent_name = violation.get("suggested_agent", "Unknown")
        file_path = violation.get("file")
        violation_type = violation.get("type", "UNKNOWN")

        confidence = decision_engine.calculate_healing_confidence(
            violations_count=1,
            violation_types=[violation_type],
            territory=territory,
        )

        allowed, reason = decision_engine.should_proceed_with_healing(confidence, agent_name)
        if not allowed:
            logging.warning(f"Skipping fix for {file_path}: {reason}")
            failed_fixes.append({"violation": violation, "reason": reason, "status": "blocked"})
            continue

        if dry_run:
            reconciliation_log.append({"action": "would_fix", "target": file_path, "agent": agent_name})
            continue

        if not decision_engine.request_sovereignty_token(agent_name, violation_type):
            failed_fixes.append(
                {"violation": violation, "reason": "Sovereignty Token Denied", "status": "locked"},
            )
            continue

        try:
            agent = agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")

            state_mgr.update_agent(agent_name, f"Executing Fix: {violation_type}")

            fix_result = agent.heal(violation)
            if not isinstance(fix_result, dict):
                fix_result = {"raw_output": str(fix_result)}

            fix_result["target"] = file_path
            fix_result["agent"] = agent_name

            if fix_result.get("success", True) is False:
                raise RuntimeError(f"Agent reported failure: {fix_result.get('error', 'Unknown')}")

            reconciliation_log.append(fix_result)
            decision_engine.release_sovereignty_token(agent_name, success=True)

        # guardian: allow-silent-swallow
        except Exception as e:
            logging.error(f"Fix failed for {agent_name} on {file_path}: {e}")
            failed_fixes.append({"violation": violation, "error": str(e), "status": "execution_error"})
            decision_engine.release_sovereignty_token(agent_name, success=False)

    return {
        "violations_found": len(plan["violations_found"]),
        "violations_fixed": len(reconciliation_log),
        "status": "success" if not failed_fixes else "partial_success",
        "errors": len(failed_fixes),
        "skipped": 0,
        "execution_time_ms": 0.0,
        "error_message": None if not failed_fixes else f"{len(failed_fixes)} fixes failed",
    }


# ============================================================================
# PHASE 3: FINAL VALIDATION (The Audit)
# ============================================================================


# [REMOVED DUPLICATE] execute_phase3_final_validation removed.
# Usage consolidated to execute_phase3_validation at line 1273.


# ============================================================================
# ENHANCED PHASE EXECUTION & INPUT VALIDATION
# ============================================================================


def validate_territory_input(territory: str) -> tuple[bool, str]:
    """Validate territory input with comprehensive security checks."""
    if not territory:
        return True, ""
    if len(territory) > 100:
        return False, "Name too long"
    if not re.match(r"^[A-Za-z0-9_]+$", territory):
        return False, "Invalid characters"
    if ".." in territory or territory.startswith(("/", "\\")):
        return False, "Path traversal attempt"
    # Additional security checks
    if ";" in territory or "|" in territory or "&" in territory:
        return False, "Injection attempt"
    if "<" in territory or ">" in territory:
        return False, "HTML/script injection attempt"
    return True, ""


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Directory Constants
AGENTIC_CORE_DIR = "agentic_core"
APPS_SHARED_DIR = "apps_shared"
APPS_LIC_DIR = "apps_lic"
APPS_RG_DIR = "apps_rg"
SCRIPTS_DIR = "scripts"
AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
RUNTIME_STATE_FILE = "runtime_state.json"

# Project Root Path — resolved lazily via module __getattr__ or REPO_ROOT.

# [ULTRA-HARDENED] Whitelist of allowed module prefixes for dynamic imports
# Prevents loading agents from unexpected packages (defense-in-depth against tampered discovery/cache)
ALLOWED_MODULE_PREFIXES = ("agentic_core", "apps_shared", "apps_lic", "apps_rg")

# Logging: configured once in _configure_logging() called from main().
logger = logging.getLogger("UnifiedSovereign")

# ============================================================================
# RUNTIME STATE MANAGEMENT (From Canon Validator)
# ============================================================================


class RuntimeStateManager:
    """Manages live state for dashboard observability."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()  # [ULTRA-HARDENED] Force real absolute path resolution
        self.state = {
            "status": "idle",
            "start_time": None,
            "end_time": None,
            "current_agent": None,
            "current_layer": None,
            "agents_order": [],
            "completed_agents": [],
            "events": [],
            # [INTEGRATION] Ported from Canon Validator
            "meta_learning": {
                "enabled": False,
                "total_experiences": 0,
                "patterns_extracted": 0,
                "strategy_weights": {"cot": 1.0, "tot": 1.0, "react": 1.0},
                "recent_experiences": [],
            },
            "compliance_scores": {},
            # [SILENT AGGREGATION] Track decisions for final report
            "decisions_made": [],
            "compliance_report": {},
        }
        # [HARDENED] Register exit handler to prevent 'zombie' running states
        atexit.register(self._emergency_cleanup)

    def start_mission(self, mission_type: str, agents_order: list[str]):
        self.state["status"] = "running"
        self.state["start_time"] = datetime.now().isoformat()
        self.state["agents_order"] = agents_order
        self.add_event("info", f"Mission started: {mission_type}")
        self.save()

    def update_agent(self, agent_name: str, layer: str):
        self.state["current_agent"] = agent_name
        self.state["current_layer"] = layer
        self.add_event("agent_start", f"→ Executing {agent_name} ({layer})")
        self.save()

    def complete_agent(self, agent_name: str, success: bool, details: str = ""):
        """
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        """
        self.state["completed_agents"].append(
            {
                "agent": agent_name,
                "time": datetime.now().isoformat(),
                "success": success,
                "details": details,
            },
        )
        # Log to file/state but DO NOT PRINT JSON to console here
        self.add_event("agent_end", f"{'✓' if success else '❌'} Completed {agent_name}")
        self.save()

    def add_event(self, event_type: str, message: str):
        self.state["events"].append(
            {"time": datetime.now().isoformat(), "type": event_type, "message": message},
        )
        # [SILENT AGGREGATION] Only log minimal status to console during execution
        # Full telemetry captured in state for final report
        if event_type == "error":
            logger.error(message)
        elif event_type == "warning":
            logger.warning(message)
        elif event_type in ["agent_start", "agent_end"]:
            # Keep minimal agent progress indicators
            logger.info(message)
        else:
            # Suppress other verbose intermediate logs
            pass

    def finish_mission(self, status="completed"):
        self.state["status"] = status
        self.state["end_time"] = datetime.now().isoformat()
        self.state["current_agent"] = None
        self.save()

    def save(self):
        """
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        """
        try:
            state_path = self.project_root / RUNTIME_STATE_FILE
            temp_dir = state_path.parent
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create temp file
            with tempfile.NamedTemporaryFile("w", dir=str(temp_dir), delete=False, encoding="utf-8") as tf:
                json.dump(self.state, tf, indent=2, default=str)
                temp_name = tf.name

            # [HARDENED] Set strict permissions (Owner Read/Write only) before moving
            # This prevents other users on shared CI runners from reading potential sensitive logs
            os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)

            # Atomic replacement
            os.replace(temp_name, state_path)

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
            try:
                # guardian: allow-path-string
                if "temp_name" in locals() and os.path.exists(temp_name):
                    os.remove(temp_name)
            # guardian: allow-silent-swallow
            except:
                pass

    def _emergency_cleanup(self):
        """Ensure state is finalized even on unhandled exit."""
        if self.state["status"] == "running":
            self.finish_mission("terminated")

    def update_meta_learning(self, experience_data: dict[str, Any]):
        """[INTEGRATION] Updates cognitive metrics for dashboard."""
        ml = self.state["meta_learning"]
        ml["enabled"] = True

        if "total_experiences" in experience_data:
            ml["total_experiences"] = experience_data["total_experiences"]

        if "strategy_weights" in experience_data:
            ml["strategy_weights"] = experience_data["strategy_weights"]

        if "experience" in experience_data:
            ml["recent_experiences"].insert(0, experience_data["experience"])
            ml["recent_experiences"] = ml["recent_experiences"][:5]  # Keep last 5

        self.save()


# ============================================================================
# AUTONOMOUS DECISION ENGINE (From SSOT Protocol)
# ============================================================================


def discover_agents_from_registry(project_root: Path, dedupe: bool = True) -> list[tuple[str, str]]:
    """Hybrid agent discovery: prefer cached JSON, fallback to live scan."""
    agents = []
    json_path = project_root / AGENT_DISCOVERY_JSON

    # Try Cache
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            for agent in data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)

                        # Convert path parts to module dot notation
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue

                        module_path = ".".join(clean_parts)

                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(
                            module_path == p or module_path.startswith(p + ".")
                            for p in ALLOWED_MODULE_PREFIXES
                        ):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue

                        agents.append((agent["class_name"], module_path))
                    # guardian: allow-silent-swallow
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            logger.info(f"Loaded {len(agents)} agents from cache")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")

    # Try Live Scan if empty
    if not agents:
        try:
            from agentic_core.utils.discovery.Full_Agent_discovery import discover_all_agents

            logger.info("Running live agent discovery...")
            discovery_data = discover_all_agents(project_root)
            for agent in discovery_data:
                if agent.get("class_name"):
                    # [HARDENED] Use pathlib for robust cross-platform path resolution
                    try:
                        raw_path = agent.get("path", "")
                        # Handle absolute or relative paths gracefully
                        if os.path.isabs(raw_path):
                            full_path = Path(raw_path)
                            rel_path = full_path.relative_to(project_root)
                        else:
                            rel_path = Path(raw_path)

                        # Convert path parts to module dot notation
                        clean_parts = rel_path.with_suffix("").parts
                        # [ULTRA-HARDENED] Reject any path containing navigation tokens (., ..) or empty segments
                        if any(p in {"", ".", ".."} for p in clean_parts):
                            logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
                            continue

                        module_path = ".".join(clean_parts)

                        # [ULTRA-HARDENED] Enforce module prefix whitelist before permitting dynamic import
                        if not any(
                            module_path == p or module_path.startswith(p + ".")
                            for p in ALLOWED_MODULE_PREFIXES
                        ):
                            logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
                            continue

                        agents.append((agent["class_name"], module_path))
                    # guardian: allow-silent-swallow
                    except Exception as p_err:
                        # Log but don't crash on single bad path
                        logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
                        continue
            # [ULTRA-HARDENED] Atomic write + strict 600 permissions for agent discovery cache
            try:
                temp_name = None
                with tempfile.NamedTemporaryFile(
                    "w",
                    delete=False,
                    dir=str(project_root),
                    encoding="utf-8",
                ) as tf:
                    json.dump(discovery_data, tf, indent=2)
                    temp_name = tf.name
                os.chmod(temp_name, stat.S_IRUSR | stat.S_IWUSR)
                os.replace(temp_name, json_path)
                logger.info(f"Discovered {len(agents)} agents (cached)")
            # guardian: allow-silent-swallow
            except Exception as cache_err:
                logger.warning(f"Failed to cache agent discovery: {cache_err}")
                # guardian: allow-path-string
                if temp_name and os.path.exists(temp_name):
                    os.remove(temp_name)
        except ImportError:
            logger.warning("Live discovery unavailable - Full_Agent_discovery not found")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Live discovery failed: {e}")

    if dedupe:
        agents = sorted(set(agents), key=lambda x: x[0])
    return agents


# ============================================================================
# PHASE 3: FINAL VALIDATION (The Audit)
# ============================================================================
@standard_heal
def execute_phase3_validation(
    agents: dict[str, Any],
    territory: str,
    original_violations: list[dict],
    dry_run: bool = False,
    **kwargs,
):
    """
    PHASE 3: POST-MORTEM VALIDATION

    Verifies that 'fixed' files now pass AST and SSOT checks.
    Does NOT blindly trust the agent's 'success' return value.
    """
    if dry_run:
        return {"status": "skipped", "message": "Dry run - validation skipped"}

    remaining_issues = []
    # [HARDENING] Use the memory-safe AST validator defined in Phase 1
    # guardian: allow-path-string
    validator = ASTCodeQualityValidator(REPO_ROOT)

    for v in original_violations:
        fpath = v.get("file")

        # 1. Existence Check
        # guardian: allow-path-string
        if not fpath or not os.path.exists(fpath):
            # If it was an orphan that was deleted, this is good.
            # If it was a missing file that was created, we check existence.
            drift_type = v.get("drift_type", "")
            if "ORPHAN" in drift_type:
                # File gone = Success
                continue
            elif "MISSING" in drift_type:
                remaining_issues.append({"file": fpath, "error": "File still missing after heal"})
                continue
            else:
                # Standard file modification - if gone, that's bad
                remaining_issues.append({"file": fpath, "error": "File vanished after heal"})
                continue

        # 2. AST Quality Check on Modified Files
        # We only check files that exist and were targets of modification
        quality_report = validator.check_file_quality(Path(fpath))
        if quality_report.get("violations"):
            for issue in quality_report["violations"]:
                issue["source"] = "post_heal_validation"
                remaining_issues.append(issue)

    status = "clean"
    if remaining_issues:
        status = "drift_detected"

    return {
        "status": status,
        "remaining_violations": remaining_issues,
        "verification_timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# EXECUTION PHASES (SSOT Logic + Canon Observability)
# ============================================================================


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase1_discovery(agents, territory, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 1: TERRITORIAL DISCOVERY (Retriable)"""
    return execute_phase1_discovery_impl(agents, territory, decision_engine, state_mgr, dry_run, auto_approve)


def execute_phase1_discovery_impl(
    agents,
    territory,
    decision_engine,
    state_mgr,
    dry_run=False,
    auto_approve=True,
):
    """PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration"""
    logger.info(f"=== PHASE 1: DISCOVERY - {territory} ===")

    state_mgr.update_agent("FilesystemSSOTReconcilerAgent", "L0 - Maintenance")

    reconciler = agents["reconciler"](project_root=REPO_ROOT)
    drift_report = reconciler.detect_root_drift()

    if drift_report is None:
        state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", False, "Returned None")
        return None, None

    violations_count = len(drift_report.get("violations", []))
    state_mgr.complete_agent("FilesystemSSOTReconcilerAgent", True, f"Drift violations: {violations_count}")

    # Location Validation
    state_mgr.update_agent("LocationAgent", "L5 - Safety")
    location_validator = agents["location"](project_root=REPO_ROOT)

    # [ULTRA-HARDENED] Explicit path traversal protection for user-supplied territory string
    agentic_core_base = (REPO_ROOT / "agentic_core").resolve()
    territory_path = (agentic_core_base / territory).resolve()
    if not territory_path.is_relative_to(agentic_core_base):
        logger.critical(f"SECURITY ALERT: Path traversal attempt detected for territory '{territory}'")
        state_mgr.add_event("security", "Path traversal blocked")
        state_mgr.complete_agent("LocationAgent", False, "Traversal blocked")
        return drift_report, []

    violations = []
    location_scan_result = {}
    if territory_path.exists():
        # Let LocationAgent do comprehensive file discovery
        location_scan_result = location_validator.run(target_territory=territory) or {}
        violations = location_scan_result.get("violations", [])
    else:
        logger.warning(f"Territory path does not exist: {territory_path}")

    # Enhanced confidence calculation with cognitive analysis
    if hasattr(decision_engine, "enable_cda") and decision_engine.enable_cda and violations:
        logger.info("🧠 Using CognitiveDispositionAgent for enhanced violation analysis...")

        # Create event loop for async cognitive analysis
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Get cognitive dispositions and enhanced confidence
        cognitive_dispositions, enhanced_confidence = loop.run_until_complete(
            decision_engine.analyze_violations_with_cognitive_disposition(violations, territory, state_mgr),
        )

        # Store cognitive dispositions in state for reporting
        state_mgr.state["cognitive_dispositions"] = [d.__dict__ for d in cognitive_dispositions]

        confidence = enhanced_confidence
        logger.info(f"🧠 Enhanced confidence with cognitive analysis: {confidence.value:.2f}")
    else:
        # Fallback to standard confidence calculation
        confidence = decision_engine.calculate_healing_confidence(
            len(violations),
            [str(v) for v in violations[:10]],
            territory,
        )

    state_mgr.state["compliance_scores"][territory] = confidence.value

    # [DETAILED TRACKING] Store actual LocationAgent violations for final report
    state_mgr.state["location_violations"] = violations
    state_mgr.state["location_scan_result"] = location_scan_result

    # [AUTO-HEALING] If confidence is high enough, trigger LocationAgent healing
    if len(violations) > 0:
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)
        state_mgr.add_event("decision", f"Location Healing: {reason}")
        logger.info(f"Location Decision: {reason}")

        if proceed and not dry_run:
            logger.info(f"🔧 Triggering LocationAgent auto-heal for {len(violations)} violations")
            # LocationAgent should have a heal method - call it
            if hasattr(location_validator, "heal_violations"):
                heal_result = location_validator.heal_violations(violations, auto_approve=auto_approve)
                healed_count = heal_result.get("healed", 0) if isinstance(heal_result, dict) else 0
                state_mgr.complete_agent(
                    "LocationAgent",
                    True,
                    f"Violations: {len(violations)} | Healed: {healed_count} | Conf: {confidence.value:.2f}",
                )
            else:
                logger.warning(
                    "LocationAgent has no heal_violations method - violations detected but not healed",
                )
                state_mgr.complete_agent(
                    "LocationAgent",
                    True,
                    f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (no heal method)",
                )
        else:
            state_mgr.complete_agent(
                "LocationAgent",
                True,
                f"Violations: {len(violations)} | Conf: {confidence.value:.2f} (healing skipped)",
            )
    else:
        state_mgr.complete_agent("LocationAgent", True, f"Violations: 0 | Conf: {confidence.value:.2f}")

    # [PHASE 1 ENHANCEMENT] Early File Classification Detection
    # Run FileClassificationAgent in discovery phase to catch naming violations early
    classification_violations = []
    classification_scan_result = {}
    try:
        state_mgr.update_agent("FileClassificationAgent", "L5 - Safety (Early Detection)")
        file_classifier = agents["file_classification"](project_root=REPO_ROOT)

        # Run classification scan on territory (validate_only mode for detection)
        file_classifier.validate_only = True
        file_classifier.dry_run = True  # Don't make changes during discovery
        classification_scan_result = file_classifier.run(target_territory=territory) or {}

        # Extract violations from stats
        if hasattr(file_classifier, "stats") and file_classifier.stats.get("violations"):
            for vtype, count in file_classifier.stats["violations"].items():
                if count > 0:
                    classification_violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": territory,
                        },
                    )

        classification_count = len(classification_violations)
        state_mgr.complete_agent(
            "FileClassificationAgent",
            True,
            f"Early detection: {classification_count} classification issues",
        )

        # Store classification results for later phases
        state_mgr.state["classification_violations"] = classification_violations
        state_mgr.state["classification_scan_result"] = classification_scan_result

        logger.info(f"📋 FileClassificationAgent early detection: {classification_count} issues found")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.warning(f"FileClassificationAgent early detection failed: {e}")
        state_mgr.complete_agent("FileClassificationAgent", False, f"Early detection error: {e}")
        state_mgr.state["classification_violations"] = []
        state_mgr.state["classification_scan_result"] = {}

    return drift_report, violations, location_scan_result


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase2_alignment(agents, territory, decision_engine, state_mgr, dry_run=False, auto_approve=True):
    """PHASE 2: STRUCTURAL ALIGNMENT (Retriable)"""
    return execute_phase2_alignment_impl(agents, territory, decision_engine, state_mgr, dry_run, auto_approve)


def execute_phase2_alignment_impl(
    agents,
    territory,
    decision_engine,
    state_mgr,
    dry_run=False,
    auto_approve=True,
):
    """PHASE 2: STRUCTURAL ALIGNMENT - Implementation"""
    logger.info(f"=== PHASE 2: ALIGNMENT - {territory} ===")

    state_mgr.update_agent("HierarchyAgent", "L5 - Safety")
    hierarchy = agents["hierarchy"](project_root=REPO_ROOT)

    # [STRICT SCOPE] Pass territory to scan only the target root
    scan = hierarchy.scan_root_violations(target_territory=territory)
    violations = scan.get("violations_found", 0)

    # Check if we found violations in the returned dict format (list vs count)
    if "violations" in scan and isinstance(scan["violations"], list):
        violations = len(scan["violations"])

    if violations > 0:
        confidence = decision_engine.calculate_healing_confidence(violations, ["HIERARCHY"], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)

        state_mgr.add_event("decision", f"Hierarchy Healing: {reason}")
        logger.info(f"Decision: {reason}")

        if proceed:
            # [SOVEREIGN DEFAULT] Propagate active/dry-run status to HierarchyAgent
            res = hierarchy.heal_hierarchy(
                create_structure=True,
                relocate_files=True,
                enforce_depth=True,
                purge_orphans=False,
                target_territory=territory,  # [STRICT SCOPE] Already correct here, but ensuring strict adherence
                dry_run=dry_run,
                auto_approve=auto_approve,
            )
            healed = res.get("total_healed", 0)
            state_mgr.complete_agent("HierarchyAgent", True, f"Healed: {healed}")
            return res
        else:
            state_mgr.complete_agent("HierarchyAgent", False, "Skipped - Low Confidence")
    else:
        state_mgr.complete_agent("HierarchyAgent", True, "No violations found")

    return None


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase3_architectural_validation(agents, territory, state_mgr):
    """PHASE 3: ARCHITECTURAL VALIDATION (Retriable) - renamed to avoid shadowing execute_phase3_validation"""
    return execute_phase3_validation_impl(agents, territory, state_mgr)


def execute_phase3_validation_impl(agents, territory, state_mgr):
    """PHASE 3: ARCHITECTURAL VALIDATION - Implementation"""
    logger.info(f"=== PHASE 3: VALIDATION - {territory} ===")

    state_mgr.update_agent("ArchitectureGovernorAgent", "L5 - Safety")
    arch_gov = agents["arch_governor"](project_root=REPO_ROOT)
    gov_report = arch_gov.comprehensive_territory_audit(
        target_territories=[territory],
        check_layer_boundaries=True,
        check_naming_conventions=True,
    )

    if gov_report is None:
        state_mgr.complete_agent("ArchitectureGovernorAgent", False, "Returned None")
        return None, None

    violations = len(gov_report.get("layer_violations", [])) + len(gov_report.get("naming_violations", []))
    state_mgr.complete_agent("ArchitectureGovernorAgent", True, f"Violations: {violations}")

    state_mgr.update_agent("SystemArchitectAgent", "L5 - Safety")
    sys_arch = agents["system_architect"](project_root=REPO_ROOT)
    arch_report = sys_arch.validate_core_architecture(f"agentic_core/{territory}")

    if arch_report is None:
        state_mgr.complete_agent("SystemArchitectAgent", False, "Returned None")
        return gov_report, None

    if not arch_report.get("imports_valid", True):
        circular = arch_report.get("circular_dependencies", [])
        state_mgr.add_event("error", f"Circular dependencies detected: {circular}")
        state_mgr.complete_agent("SystemArchitectAgent", False, "Circular Dependencies")
        return gov_report, arch_report

    state_mgr.complete_agent("SystemArchitectAgent", True, "Architecture Valid")
    return gov_report, arch_report


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase4_healing(
    agents,
    territory,
    gov_report,
    decision_engine,
    state_mgr,
    dry_run=False,
    auto_approve=True,
):
    """PHASE 4: HEALING (Retriable)"""
    # [STRICT SCOPE] Gatekeeper check
    if not gov_report:
        logger.warning("Skipping healing: No governance report available.")
        return None

    return execute_phase4_healing_impl(
        agents,
        territory,
        gov_report,
        decision_engine,
        state_mgr,
        dry_run,
        auto_approve,
    )


def execute_phase4_healing_impl(
    agents,
    territory,
    gov_report,
    decision_engine,
    state_mgr,
    dry_run=False,
    auto_approve=True,
):
    """PHASE 4: HEALING - Implementation"""
    logger.info(f"=== PHASE 4: HEALING - {territory} ===")

    if gov_report is None:
        logger.warning("No governance report - skipping healing")
        return None

    arch_gov = agents["arch_governor"](project_root=REPO_ROOT)
    plan = arch_gov.generate_healing_plan(gov_report)

    if plan is None:
        logger.warning("No healing plan generated")
        return None

    if plan.get("requires_healing", False):
        fixes = len(plan.get("naming_fixes", []))
        confidence = decision_engine.calculate_healing_confidence(fixes, ["NAMING"], territory)
        proceed, reason = decision_engine.should_proceed_with_healing(confidence)

        state_mgr.add_event("decision", f"Arch Healing: {reason}")
        logger.info(f"Decision: {reason}")

        if proceed:
            state_mgr.update_agent("ArchitectureGovernorAgent", "HEALING MODE")
            # [SOVEREIGN DEFAULT] Pass orchestration flags to the Governor healing plan
            res = arch_gov.execute_healing_plan(plan, dry_run=dry_run, auto_approve=auto_approve)
            success = res.get("success", False)
            state_mgr.complete_agent("ArchitectureGovernorAgent", success, f"Healed: {success}")
            return res
        else:
            state_mgr.add_event("warning", "Healing skipped - Low confidence")

    return None


# guardian: allow-magic-config
@with_retry(max_retries=3)
def execute_phase5_final(agents, territory, state_mgr, decision_engine=None):
    """PHASE 5: CERTIFICATION (Retriable)"""
    return execute_phase5_final_impl(agents, territory, state_mgr, decision_engine)


def execute_phase5_final_impl(agents, territory, state_mgr, decision_engine=None):
    """PHASE 5: CERTIFICATION - Implementation with Silent Aggregation"""
    logger.info(f"=== PHASE 5: CERTIFICATION - {territory} ===")

    state_mgr.update_agent("SovereignCertifier", "L5 - Compliance")

    # [UNIFIED MANIFEST] Aggregate all findings from the state manager
    compliance_report = state_mgr.state.get("compliance_report", {})
    state_mgr.state.get("decision_history", [])

    # [CRITICAL FIX] Aggregate violations from ALL agents, not just ArchitectureGovernor
    # The compliance_report only has ArchitectureGovernor violations
    # We need to include LocationAgent violations from Phase 1
    all_violations = []

    # Get ArchitectureGovernor violations
    arch_violations = compliance_report.get("violations", [])
    all_violations.extend(arch_violations)

    # Get LocationAgent violations from Phase 1 (stored in state)
    location_violations = state_mgr.state.get("location_violations", [])
    for loc_violation in location_violations:
        # LocationAgent violations are tuples: (Path, message)
        if isinstance(loc_violation, tuple) and len(loc_violation) >= 2:
            file_path = str(loc_violation[0])
            message = str(loc_violation[1])
        else:
            file_path = str(getattr(loc_violation, "file", "unknown"))
            message = str(loc_violation)

        # Generate specific, actionable recommendations based on violation type
        if "Missing sovereign root:" in message:
            dir_name = message.split("Missing sovereign root:")[1].strip().strip("')")
            action = f"Create directory: {dir_name}"
        elif "Forbidden keyword 'def test_'" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"Move {filename} to tests/ directory (contains test functions)"
        elif "Forbidden keyword 'class Sovereign'" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"Move {filename} to agentic_core/base_agents/ or agentic_core/L5_safety/"
        elif "Forbidden extension .py for destination docs/reports" in message:
            path_parts = file_path.replace("\\", "/").split("/")
            filename = path_parts[-1]
            action = f"RENAME: '{filename}' has audit/report naming but is a Python script. Either: 1) Rename to avoid audit patterns (e.g., registry_linkage_checker.py) OR 2) Move to agentic_core/L0_maintenance/scripts/ where audit scripts belong"
        else:
            action = f"Fix location/naming issue: {message[:60]}"

        # Calculate individual confidence for each violation based on specific violation characteristics
        violation_type = "LOCATION"
        if "Forbidden keyword 'def test_'" in message:
            violation_type = "TEST_FILE_LOCATION"
        elif "Forbidden keyword 'class Sovereign'" in message:
            violation_type = "SOVEREIGN_CLASS_LOCATION"
        elif "Forbidden extension .py for destination docs/reports" in message:
            violation_type = "PYTHON_IN_DOCS"
        elif "BROKEN BACKUP FILE" in message:
            violation_type = "STALE_BACKUP"
        elif "Forbidden keyword 'import '" in message:
            violation_type = "IMPORT_IN_DOCS"

        # Add file-specific factors for confidence calculation
        {
            "has_test_functions": "def test_" in message,
            "has_sovereign_class": "class Sovereign" in message,
            "is_python_file": file_path.endswith(".py"),
            "is_backup_file": file_path.endswith(".backup"),
            "is_in_docs": "docs/reports" in message,
        }

        violation_confidence = decision_engine.calculate_healing_confidence(
            violations_count=1,  # Single violation
            violation_types=[violation_type],  # Use specific violation type
            territory=territory,
        ).value

        # Check if LLM was actually used in the decision process (look for LLM decisions in decision engine)
        llm_decisions = [d for d in decision_engine.decisions_made if "LLM" in d.get("reason", "")]
        llm_was_triggered = decision_engine.enable_llm and len(llm_decisions) > 0

        # Convert LocationAgent violation object to detailed dict
        violation_dict = {
            "type": "LOCATION",
            "source": "LocationAgent",
            "file": file_path,
            "message": message,
            "severity": "medium",
            "recommended_action": action,
            "llm_triggered": llm_was_triggered,
            "confidence": round(violation_confidence, 3),
        }
        all_violations.append(violation_dict)

    # Get DebateSynthesisAgent violations
    debate_synthesis_agent = agents["conversational_repair"](project_root=REPO_ROOT)
    debate_synthesis_result = debate_synthesis_agent.scan_violations(target_territory=territory)
    conversational_violations = debate_synthesis_result.get("violations", [])
    for conv_violation in conversational_violations:
        if isinstance(conv_violation, dict):
            violation_dict = {
                **conv_violation,
                "source": "DebateSynthesisAgent",
                "file": conv_violation.get("file", "unknown"),
                "message": conv_violation.get("message", str(conv_violation)),
                "severity": conv_violation.get("severity", "medium"),
                "recommended_action": conv_violation.get(
                    "recommended_action",
                    "Review conversational pattern",
                ),
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(conv_violation.get("confidence", 0.5), 3),
            }
            all_violations.append(violation_dict)

    # Get RootHygieneAgent violations
    hygiene_violations = state_mgr.state.get("hygiene_violations", [])
    for hygiene_violation in hygiene_violations:
        if isinstance(hygiene_violation, dict):
            violation_dict = {
                "type": hygiene_violation.get("type", "HYGIENE"),
                "source": "RootHygieneAgent",
                "file": hygiene_violation.get("file", "unknown"),
                "message": hygiene_violation.get("message", str(hygiene_violation)),
                "severity": hygiene_violation.get("severity", "medium"),
                "recommended_action": hygiene_violation.get("recommended_action", "Clean root directory"),
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(hygiene_violation.get("confidence", 0.5), 3),
            }
            all_violations.append(violation_dict)

    # [PHASE 3 ENHANCEMENT] Get FileClassificationAgent violations from early detection
    classification_violations = state_mgr.state.get("classification_violations", [])
    for class_violation in classification_violations:
        if isinstance(class_violation, dict):
            subtype = class_violation.get("subtype", "UNKNOWN")
            count = class_violation.get("count", 1)
            violation_dict = {
                "type": "CLASSIFICATION",
                "subtype": subtype,
                "source": "FileClassificationAgent",
                "file": class_violation.get("file", "multiple"),
                "message": f"{subtype} violation: {count} file(s) need attention",
                "severity": "medium",
                "recommended_action": f"Run FileClassificationAgent to fix {subtype} issues",
                "llm_triggered": decision_engine.enable_llm,
                "confidence": round(class_violation.get("confidence", 0.7), 3),
                "count": count,
            }
            all_violations.append(violation_dict)

    violation_count = len(all_violations)
    status = "COMPLIANT" if violation_count == 0 else "NON-COMPLIANT"

    # [LOGIC FIX] Recalculate confidence based on FINAL violation count, not Phase 1
    # Get the decision engine to recalculate confidence for the final state
    decision_engine = getattr(state_mgr, "_decision_engine", None)
    if decision_engine is None:
        # Fallback: create a temporary decision engine for final calculation
        decision_engine = AutonomousDecisionEngine(enable_llm=False)

    final_confidence = decision_engine.calculate_healing_confidence(
        violations_count=violation_count,
        violation_types=[v.get("type", "UNKNOWN") for v in all_violations[:10]],
        territory=territory,
    )
    confidence_avg = final_confidence.value

    drift_count = compliance_report.get("stats", {}).get("drift_detected", 0)

    # Build detailed decision log with LLM status
    decisions_made = state_mgr.state.get("decisions_made", [])

    # Get location scan result from state manager
    location_scan_result = state_mgr.state.get("location_scan_result", {})

    # [DYNAMIC] Track actual agents executed from state manager
    completed_agents = state_mgr.state.get("completed_agents", [])
    # Extract unique agent names from completion history
    agents_executed = list({agent["agent"] for agent in completed_agents})

    detailed_cert = {
        "meta": {
            "territory": territory,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "sovereignty_level": "L5",
        },
        "metrics": {
            "confidence_score": round(confidence_avg, 3),
            "violation_count": violation_count,
            "drift_count": drift_count,
            "errors": compliance_report.get("stats", {}).get("errors", 0),
            "violations_fixed": compliance_report.get("stats", {}).get("violations_fixed", 0),
        },
        "governance_log": {"decisions": decisions_made, "files_processed": []},
        "unified_violations": all_violations,  # Use all_violations instead of just arch violations
        "agents_executed": agents_executed,
    }

    # Add comprehensive file statistics
    file_stats = location_scan_result.get("file_stats", {})
    # Format compliance rate to one decimal place
    if "compliance_rate" in file_stats:
        file_stats["compliance_rate"] = round(file_stats["compliance_rate"], 1)
    detailed_cert["file_scan_stats"] = file_stats

    # Add violations to file log
    files_affected = set()
    for v in all_violations:  # Use all_violations instead of violations
        files_affected.add(v.get("file", "unknown"))

    detailed_cert["governance_log"]["files_processed"] = list(files_affected)
    detailed_cert["governance_log"]["scan_summary"] = {
        "total_files_scanned": file_stats.get("total_files", 0),
        "files_with_violations": len(files_affected),
        "files_compliant": file_stats.get("valid_files", 0),
        "compliance_rate": round(file_stats.get("compliance_rate", 0), 1),
        "file_types": file_stats.get("file_types", {}),
    }

    # Generate Markdown Executive Summary
    file_stats = location_scan_result.get("file_stats", {})
    total_files = file_stats.get("total_files", 0)
    compliance_rate = file_stats.get("compliance_rate", 0)
    file_types = file_stats.get("file_types", {})

    markdown_summary = [
        f"# 🛡️ Sovereign Compliance Report: {territory}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Status:** {status}",
        "",
        "## 📊 Executive Summary",
        "",
        f"* **Confidence Score:** {confidence_avg:.1%}",
        f"* **Violations Detected:** {violation_count}",
        f"* **Integrity Drift:** {drift_count}",
        f"* **Violations Fixed:** {detailed_cert['metrics']['violations_fixed']}",
        "",
        "## 📁 Scan Scope",
        "",
        f"* **Total Files Scanned:** {total_files}",
        f"* **Files Compliant:** {file_stats.get('valid_files', 0)}",
        f"* **Files with Violations:** {len(files_affected)}",
        f"* **Compliance Rate:** {compliance_rate:.1f}%",
        "",
        "### File Types Analyzed",
        "",
    ]

    # Add file type breakdown
    if file_types:
        for ext, count in sorted(file_types.items()):
            ext_display = ext if ext else "(no extension)"
            markdown_summary.append(f"* **{ext_display}:** {count} files")

    markdown_summary.extend(["", "## 🚨 Violations Detected", ""])

    # Add detailed violations table
    if violation_count > 0:
        markdown_summary.extend(
            [
                "| # | Type | File | Issue | Severity | LLM | Confidence | Action |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ],
        )

        for idx, violation in enumerate(all_violations, 1):
            v_type = violation.get("type", "UNKNOWN")
            v_file = violation.get("file", "unknown")
            # Extract just the filename from full path
            if "/" in v_file or "\\" in v_file:
                v_file = v_file.split("/")[-1].split("\\")[-1]

            # Parse message to get the actual issue
            v_message = violation.get("message", "")
            if "ARTIFACT ROUTING VIOLATION:" in v_message:
                issue = v_message.split("ARTIFACT ROUTING VIOLATION:")[1].split("'")[0].strip()
            elif "Missing sovereign root:" in v_message:
                issue = v_message.split("Missing sovereign root:")[1].strip().strip("')")
            else:
                issue = v_message[:50] + "..." if len(v_message) > 50 else v_message

            v_severity = violation.get("severity", "medium")
            v_llm = "Yes" if violation.get("llm_triggered", False) else "No"
            v_conf = violation.get("confidence", 0.0)
            # Convert to percentage if it's a decimal (0-1) or keep as is if already percentage
            if v_conf <= 1.0:
                v_conf_display = f"{v_conf:.1%}"
            else:
                v_conf_display = f"{v_conf:.1f}%"
            v_action = violation.get("recommended_action", "Review")[:30] + "..."

            markdown_summary.append(
                f"| {idx} | {v_type} | `{v_file}` | {issue} | {v_severity} | {v_llm} | {v_conf_display} | {v_action} |",
            )
    else:
        markdown_summary.append("*No violations detected - territory is compliant.*")

    markdown_summary.extend(
        [
            "",
            "## 🧠 AI Governance Log",
            "",
            "| Decision Context | Confidence | LLM Triggered | Outcome |",
            "| :--- | :--- | :--- | :--- |",
        ],
    )

    # Add decision details to markdown table
    for decision in decisions_made:
        confidence = decision.get("confidence", 0.0)
        llm_triggered = confidence <= 0.75
        outcome = "PROCEED" if decision.get("decision", False) else "SKIP"
        context = decision.get("reason", "Unknown")
        # Format confidence as percentage
        if confidence <= 1.0:
            conf_display = f"{confidence:.1%}"
        else:
            conf_display = f"{confidence:.1f}%"

        markdown_summary.append(
            f"| {context} | {conf_display} | {'Yes' if llm_triggered else 'No'} | {outcome} |",
        )

    # Print JSON Manifest
    print(json.dumps(detailed_cert, indent=2))

    # Print Markdown Summary
    print("\n" + "\n".join(markdown_summary))
    if files_affected:
        print("\n### 📂 Affected Files")
        for f in sorted(files_affected):
            print(f"* `{f}`")
    else:
        print("\n*No files required remediation.*")

    # [COMPREHENSIVE REPORTS] Save detailed reports to files
    save_comprehensive_reports(
        territory,
        detailed_cert,
        markdown_summary,
        files_affected,
        state_mgr.project_root,
    )

    logger.info(f"📜 CERTIFICATE ISSUED: {territory}")
    state_mgr.complete_agent("SovereignCertifier", True, "Certificate Issued")
    return detailed_cert


def save_comprehensive_reports(
    territory: str,
    detailed_cert: dict,
    markdown_summary: list,
    files_affected: set,
    project_root: Path,
):
    """
    [COMPREHENSIVE REPORTS] Save detailed JSON manifest and Markdown summary to persistent files.
    Creates timestamped reports in logs/compliance_reports/ directory.
    """
    try:
        # Create reports directory
        reports_dir = project_root / "logs" / "compliance_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save only final files (no timestamped versions to reduce sprawl)
        json_filename = f"compliance_report_{territory}.json"
        md_filename = f"executive_summary_{territory}.md"
        json_path = reports_dir / json_filename
        md_path = reports_dir / md_filename

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(detailed_cert, f, indent=2, default=str)

        # Save Markdown Executive Summary (using the md_path already defined above)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_summary))
            if files_affected:
                f.write("\n\n### 📂 Affected Files\n\n")
                for f_sorted in sorted(files_affected):
                    f.write(f"* `{f_sorted}`\n")
            else:
                f.write("\n\n*No files required remediation.*\n")

        logger.info("📁 Final compliance reports saved:")
        logger.info(f"   JSON: {json_path.relative_to(project_root)}")
        logger.info(f"   Markdown: {md_path.relative_to(project_root)}")

    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"Failed to save comprehensive reports: {e}")
        # Don't fail the entire process if report saving fails


# ============================================================================
# L3 ORCHESTRATION INTEGRATION
# ============================================================================


def try_summon_orchestrator(project_root: Path, targets: list[str], execute: bool):
    """
    [INTEGRATION] Attempts to load L3 Orchestrator for smart execution.
    Returns: (success: bool, results: List|None)
    """
    try:
        # Dynamic import to avoid hard dependency on L3 (Graceful Degradation)
        from agentic_core.L0_maintenance.reasoning.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,  # noqa: F401
        )
        from agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent import (
            get_consolidated_orchestrator,
        )
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent
        from agentic_core.L5_safety.reasoning.SystemArchitectAgent import (
            SystemArchitectAgent,  # noqa: F401
        )

        orchestrator = get_consolidated_orchestrator(project_root)
        logger.info("🧠 L3 ORCHESTRATOR SUMMONED: Delegating command.")

        # Assemble Roster for L3
        active_roster = [
            ("LocationAgent", LocationAgent(project_root)),
            ("HierarchyAgent", HierarchyAgent(project_root)),
            ("ArchitectureGovernorAgent", ArchitectureGovernorAgent(project_root)),
        ]

        mission_context = {
            "dry_run": not execute,
            "execute": execute,
            "domains": targets,
            "scan_mode": "leveraged",
        }

        # Execute via L3
        mission_results = orchestrator.run_mission(active_roster, mission_context)
        return True, mission_results

    except ImportError:
        logger.warning("L3 Orchestrator not found. Falling back to L5 iteration.")
        return False, None
    # guardian: allow-silent-swallow
    except Exception as e:
        logger.error(f"L3 Orchestration failed: {e}. Falling back to L5 iteration.")
        return False, None


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================


def main() -> int:
    """Deterministic wrapper: logging, V15 enforcement, console, then legacy body."""
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--v15-enforcement",
        type=int,
        choices=(0, 1),
        default=None,
        help="Override V15_ENFORCEMENT for this run (0=off, 1=on).",
    )
    pre_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity (repeatable).",
    )
    pre_args, remaining = pre_parser.parse_known_args()
    _configure_logging(int(pre_args.verbose))
    _apply_v15_enforcement_flag(pre_args)
    _maybe_force_utf8_console()

    try:
        _legacy_main(remaining, repo_root=REPO_ROOT)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    return 0


@_optional_v15_runtime_guard()("E.execute_ssot_main.execute_ssot")
def _legacy_main(extra_argv=None, *, repo_root: Path | None = None):
    # §8.1e — V15 manifest at SSOT bootstrap entry (AGGREGATE, L0 bootstrap)
    _v15_manifest = _v15_build_ssot_manifest()
    if _v15_manifest is not None:
        _v15_ssot_gateway_audit(_v15_manifest, trace_id=_v15_manifest.correlation_id)

    project_root = repo_root if repo_root is not None else REPO_ROOT
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

    parser = argparse.ArgumentParser(
        description="Unified Sovereign Compliance Protocol v4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single territory scan (LLM enabled by default)
  python execute_ssot_script.py --territory prompt_governance

  # Multi-domain sweep
  python execute_ssot_script.py --domains

  # Dry run (no LLM healing)
  python execute_ssot_script.py --territory L5_safety --dry-run

  # List all discoverable agents
  python execute_ssot_script.py --list-agents

  # Run specific agent directly
  python execute_ssot_script.py --agent NamingAgent
        """,
    )
    parser.add_argument("--territory", type=str, help="Specific territory to scan")
    parser.add_argument("--domains", action="store_true", help="Scan all major domains (Multi-Domain Mode)")
    parser.add_argument("--agent", type=str, help="Run specific agent directly")
    parser.add_argument("--list-agents", action="store_true", help="List discoverable agents")
    parser.add_argument(
        "--enable-cda",
        action="store_true",
        help="Enable CognitiveDispositionAgent for enhanced AI-powered violation analysis",
    )
    parser.add_argument("--dry-run", action="store_true", help="Run in preview mode (no changes applied)")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable human-in-the-loop prompts (Default: Auto-Approve)",
    )
    parser.add_argument("--manual", action="store_true", help="Disable autonomous mode (legacy)")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run in validation-only mode (CI/Dry-Run Mode)",
    )
    # [PHASE 8] New Flag for Golden Baseline capture
    parser.add_argument("--capture-baseline", action="store_true", help="Capture new Golden Baseline")
    parser.add_argument(
        "--v15-enforcement",
        type=int,
        choices=(0, 1),
        default=None,
        help="Override V15_ENFORCEMENT for this run (0=off, 1=on).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity (repeatable).",
    )
    args = parser.parse_args(extra_argv)

    # [HARDENED] 0. Pre-Flight Validation
    validator = PreFlightValidator(project_root)
    env_ok, env_errors = validator.run_checks()
    if not env_ok:
        logger.critical("🛑 PRE-FLIGHT CHECK FAILED:")
        for err in env_errors:
            logger.error(f"  - {err}")
        if not args.list_agents:
            sys.exit(1)

    # [ULTRA-HARDENED] Validate user-supplied territory name format via regex
    if args.territory and not re.match(r"^[A-Za-z0-9_]+$", args.territory):
        parser.error("Invalid territory name: only alphanumeric and underscores allowed.")

    # 1. Handle Discovery
    if args.list_agents:
        logger.info("DISCOVERABLE AGENTS:")
        agents_list = list_available_agents(project_root)
        for i, (name, path) in enumerate(agents_list, 1):
            print(f"   {i:3}. {name:<40} [{path}]")
        print(f"\nTotal: {len(agents_list)} agents")
        return

    # [PHASE 8] Handle baseline capture command
    if args.capture_baseline:
        print("\n🔒 INITIATING BASELINE CAPTURE PROTOCOL...")
        try:
            from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
                ArchitectureGovernorAgent,
            )

            governor = ArchitectureGovernorAgent(project_root=project_root)
            manifest = governor.capture_golden_baseline()
            print(f"✨ Golden Baseline captured at: {manifest}")
            sys.exit(0)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Baseline capture failed: {e}")
            sys.exit(1)

    # 2. Handle Direct Agent Invocation (Developer Mode)
    if args.agent:
        logger.info(f"DIRECT AGENT EXECUTION: {args.agent}")
        try:
            found = [x for x in list_available_agents(project_root) if args.agent.lower() in x[0].lower()]
            if not found:
                logger.error(f"Agent {args.agent} not found.")
                logger.info("Use --list-agents to see available agents")
                return

            name, path = found[0]
            logger.info(f"Found: {name} at {path}")

            module = importlib.import_module(path)

            # Try instantiation strategies
            agent = None
            if hasattr(module, f"get_{name.lower()}"):
                agent = getattr(module, f"get_{name.lower()}")(project_root)
            elif hasattr(module, name):
                agent_cls = getattr(module, name)
                agent = agent_cls(project_root=project_root)
            else:
                logger.error(f"Could not instantiate {name}")
                return

            logger.info(f"Running {name}...")

            # Prefer standard methods
            if hasattr(agent, "run"):
                result = agent.run()
            elif hasattr(agent, "scan_root_violations"):
                result = agent.scan_root_violations()
            elif hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=True)
            else:
                result = "Agent instantiated but no standard run method found."

            logger.info(f"Result: {result}")

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to run agent: {e}")
            traceback.print_exc()
        return

    # 3. Initialize Sovereign State & Agents
    state_mgr = RuntimeStateManager(project_root)

    # [SIMPLIFIED] Parse arguments first
    dry_run = args.dry_run or args.validate
    auto_approve = not args.interactive

    # [SIMPLIFIED] LLM enabled by default for healing, disabled in dry-run mode
    enable_llm = not dry_run

    # [NEW] Enable CognitiveDispositionAgent if requested
    enable_cda = getattr(args, "enable_cda", False)

    # [HARDENED] Use Sovereign Decision Engine instead of standard Enhanced engine
    decision_engine = SovereignDecisionEngine(
        enable_llm=enable_llm,
        state_mgr=state_mgr,
        enable_cda=enable_cda,
    )

    logger.info("🏛️ UNIFIED SOVEREIGN PROTOCOL STARTED")
    logger.info(f"  Mode: {'AUTONOMOUS' if not args.manual else 'MANUAL'}")
    logger.info(f"  LLM: {'ENABLED' if enable_llm else 'DISABLED'}")
    logger.info(f"  CDA: {'ENABLED' if enable_cda else 'DISABLED'}")
    logger.info(f"  HEALING: {'ACTIVE' if not dry_run else 'DRY-RUN'}")
    logger.info(f"  APPROVAL: {'AUTO' if auto_approve else 'INTERACTIVE'}")

    # [HARDENED] Mandatory Hard Imports for Total Awareness
    try:
        from agentic_core.L0_maintenance.reasoning.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )
        from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent
        from agentic_core.L5_safety.reasoning.RootHygieneAgent import (
            RootHygieneAgent,  # noqa: F401
        )
        from agentic_core.L5_safety.reasoning.SystemArchitectAgent import SystemArchitectAgent
        from agentic_core.L5_safety.validators.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L6_observability.reasoning.DebateSynthesisAgent import (
            DebateSynthesisAgent,
        )
        # Note: NamingAgent is a dependency for FileClassificationAgent, checked during instantiation

        agents = {
            "reconciler": FilesystemSSOTReconcilerAgent,
            "location": LocationAgent,
            "hierarchy": HierarchyAgent,
            "arch_governor": ArchitectureGovernorAgent,
            "system_architect": SystemArchitectAgent,
            "file_classification": FileClassificationAgent,
            "conversational_repair": DebateSynthesisAgent,
            "cognitive_disposition": CognitiveDispositionAgent,
        }

        logger.info("Total Awareness: Mandatory agent roster registered.")

        # [HARDENED] Blocking Integrity Check
        integrity_errors = validator.validate_agent_integrity(agents)
        if integrity_errors:
            logger.critical("🛑 SOVEREIGN CONTRACT BREACH - AGENT INTEGRITY FAILED:")
            for err in integrity_errors:
                logger.error(f"  - {err}")
            if not args.list_agents:
                sys.exit(1)  # Halt mission if any agent is non-compliant

    except ImportError as e:
        logger.critical(f"🛑 FATAL: Mandatory agent or dependency missing: {e}")
        sys.exit(1)

    # 4. Determine Targets
    targets = []
    mission_mode = ""
    if args.territory:
        targets = [args.territory]
        mission_mode = f"Territory Scan: {args.territory}"
    elif args.domains:
        # Multi-domain sweep
        targets = [
            "prompt_governance",
            "L5_safety",
            "L3_orchestration",
            "L2_execution",
            "L0_maintenance",
        ]
        mission_mode = "Multi-Domain Sweep (L3 Attempt)"
    else:
        targets = ["prompt_governance"]  # Default safe target
        mission_mode = "Default Scan"

    # 5. Execute Mission
    # [HARDENED] Wrap entire autonomous execution in NonInteractiveGuard
    is_autonomous = not args.manual

    try:
        with NonInteractiveGuard(active=is_autonomous):
            state_mgr.start_mission(f"Unified Protocol: {mission_mode}", [f"{t}" for t in targets])

            # [PHASE 8] Integrated Integrity Check
            # [HARDENED] Pass territory targets to ensure integrity check is also scoped.
            if is_autonomous:
                logger.info(f"🔍 [PHASE 8] Running integrity check (Scope: {targets})...")
                try:
                    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
                        ArchitectureGovernorAgent,
                    )

                    governor = ArchitectureGovernorAgent(project_root=project_root, ci_mode=True)
                    # Use provided targets to prevent global scanning during pre-flight check
                    audit_results = governor.run_audit(target_territories=targets)

                    # [UNIFIED AUDIT] Persist all identified violations to the runtime state
                    state_mgr.state["compliance_report"] = audit_results

                    if audit_results["stats"]["violations_found"] > 0:
                        logger.warning(
                            f"⚠️  {audit_results['stats']['violations_found']} total violations identified.",
                        )

                    if audit_results["stats"]["drift_detected"] > 0:
                        logger.error(
                            f"🛑 CRITICAL: {audit_results['stats']['drift_detected']} integrity drift detected.",
                        )
                        if args.validate:
                            state_mgr.finish_mission(status="failed_integrity")
                            sys.exit(1)  # Fatal in CI
                        else:
                            logger.warning("⚠️  Proceeding with caution (Heal mode active)...")
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.warning(f"Integrity check failed, continuing: {e}")

            # [INTEGRATION] Attempt L3 Smart Orchestration first
            if args.domains:
                l3_success, l3_results = try_summon_orchestrator(project_root, targets, execute=is_autonomous)
                if l3_success:
                    state_mgr.update_meta_learning(
                        {"total_experiences": 1, "experience": "L3 Mission Complete"},
                    )
                    state_mgr.finish_mission("completed")
                    logger.info("🎉 L3 MISSION COMPLETED")
                    return l3_results

            # [HARDENED] Universal Compliance Persistence
            results = []
            for territory in targets:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"🚀 PROCESSING TERRITORY: {territory}")
                logger.info(f"{'=' * 60}")

                # Update State with Target
                state_mgr.state["current_territory"] = territory
                state_mgr.save()
                state_mgr.add_event("domain_start", f"Entering Domain: {territory}")

                try:
                    # [UNIVERSAL HEALING] Unified Execution Phase
                    # All agents now receive the 'Heal' signal if confidence is met
                    p1_drift, p1_loc, p1_scan_result = execute_phase1_discovery(
                        agents,
                        territory,
                        decision_engine,
                        state_mgr,
                        dry_run,
                        auto_approve,
                    )

                    if p1_drift is not None:
                        # Phase 2: Reconciliation (Write/Heal Phase)
                        # Create plan from Phase 1 results
                        plan = {"violations_found": p1_drift.get("violations", [])}

                        # Execute Phase 2 with decision engine gating
                        phase2_result = execute_phase2_reconciliation(
                            agents,
                            territory,
                            decision_engine,
                            state_mgr,
                            plan,
                            dry_run,
                        )

                        # Log Phase 2 results
                        raw = phase2_result.get("_raw_result", {})
                        if raw.get("modifications"):
                            logger.info(f"✅ Phase 2: {len(raw['modifications'])} fixes applied")
                        if raw.get("failures"):
                            logger.warning(f"⚠️ Phase 2: {len(raw['failures'])} fixes failed")

                        # Phase 3: Final Validation (Post-heal AST checks)
                        # Use the original violations from Phase 1
                        phase3_result = execute_phase3_validation(
                            agents,
                            territory,
                            p1_drift.get("violations", []),
                            dry_run,
                        )

                        if phase3_result["status"] == "clean":
                            logger.info("✅ Phase 3: All files pass validation")
                        else:
                            remaining_count = len(phase3_result.get("remaining_violations", []))
                            logger.warning(f"⚠️ Phase 3: {remaining_count} issues detected")

                        # Continue with existing phases
                        # Phase 2.5: Structural Alignment (Hierarchy) - Legacy
                        execute_phase2_alignment(
                            agents,
                            territory,
                            decision_engine,
                            state_mgr,
                            dry_run,
                            auto_approve,
                        )

                        # [UNIVERSAL HEALING] Phase 2.5: Sovereignty Enforcement (Pascal/Header/Naming)
                        # Now integrated with confidence-based decision engine
                        # [PHASE 2 ENHANCEMENT] Include classification violations in confidence calc
                        classification_violations = state_mgr.state.get("classification_violations", [])
                        total_violations = (len(p1_loc) if p1_loc else 0) + len(classification_violations)
                        violation_types = ["SOVEREIGNTY", "NAMING", "HEADER"]
                        # Add CLASSIFICATION type if we have classification violations
                        if classification_violations:
                            violation_types.append("CLASSIFICATION")
                        pascal_confidence = decision_engine.calculate_healing_confidence(
                            violations_count=total_violations,
                            violation_types=violation_types,
                            territory=territory,
                        )
                        pascal_proceed, pascal_reason = decision_engine.should_proceed_with_healing(
                            pascal_confidence,
                        )

                        state_mgr.add_event("decision", f"Sovereignty Healing: {pascal_reason}")
                        logger.info(f"Sovereignty Decision: {pascal_reason}")

                        if pascal_proceed and not dry_run:
                            logger.info(f"🛡️ Triggering Sovereignty Purge: {territory}")
                            state_mgr.update_agent("FileClassificationAgent", "L5 - Safety")
                            pascal = agents["file_classification"](project_root=REPO_ROOT)
                            # Force the agent to fix headers and rename files with proper parameters
                            if hasattr(pascal, "heal_repository"):
                                res = pascal.heal_repository(
                                    target_territory=territory,
                                    dry_run=dry_run,
                                    auto_approve=auto_approve,
                                )
                                healed = res.get("files_healed", 0) if isinstance(res, dict) else 0
                                state_mgr.complete_agent("FileClassificationAgent", True, f"Healed: {healed}")
                            else:
                                state_mgr.complete_agent(
                                    "FileClassificationAgent",
                                    False,
                                    "No heal_repository method",
                                )
                        elif not pascal_proceed:
                            state_mgr.add_event("warning", f"Sovereignty healing skipped - {pascal_reason}")
                        elif dry_run:
                            state_mgr.add_event("info", "Sovereignty healing skipped - Dry run mode")

                        # Phase 3: Validation (Legacy)
                        gov, arch = execute_phase3_architectural_validation(agents, territory, state_mgr)

                        # Persist full work to state
                        state_mgr.state["compliance_report"] = gov
                        state_mgr.save()

                        # Phase 4: Final Healing (Governor)
                        execute_phase4_healing(
                            agents,
                            territory,
                            gov,
                            decision_engine,
                            state_mgr,
                            dry_run,
                            auto_approve,
                        )

                        # Phase 4.5: Additional Agent Execution (Conversational Repair & Root Hygiene)
                        logger.info(f"=== PHASE 4.5: ADDITIONAL AGENTS - {territory} ===")

                        # Execute DebateSynthesisAgent
                        logger.info(f"🤖 Triggering Debate Synthesis: {territory}")
                        state_mgr.update_agent("DebateSynthesisAgent", "Prompt Governance")
                        try:
                            conversational_agent = agents["conversational_repair"](project_root=REPO_ROOT)
                            if hasattr(conversational_agent, "scan_violations"):
                                conv_results = conversational_agent.scan_violations(
                                    target_territory=territory,
                                )
                                conv_violations = conv_results.get("violations", [])
                                state_mgr.complete_agent(
                                    "DebateSynthesisAgent",
                                    True,
                                    f"Violations: {len(conv_violations)}",
                                )
                                # Store violations for aggregation
                                if not state_mgr.state.get("conversational_violations"):
                                    state_mgr.state["conversational_violations"] = []
                                state_mgr.state["conversational_violations"].extend(conv_violations)
                            else:
                                state_mgr.complete_agent(
                                    "DebateSynthesisAgent",
                                    False,
                                    "No scan_violations method",
                                )
                        # guardian: allow-silent-swallow
                        except Exception as e:
                            logger.warning(f"DebateSynthesisAgent failed: {e}")
                            state_mgr.complete_agent("DebateSynthesisAgent", False, str(e))

                        # Execute RootHygieneAgent
                        try:
                            state_mgr.update_agent("RootHygieneAgent", "L0 - Maintenance")
                            hygiene_agent = agents["root_hygiene"](project_root=REPO_ROOT)
                            if hasattr(hygiene_agent, "scan_root_violations"):
                                hygiene_results = hygiene_agent.scan_root_violations(
                                    target_territory=territory,
                                )
                                hygiene_violations = hygiene_results.get("violations", [])
                                state_mgr.complete_agent(
                                    "RootHygieneAgent",
                                    True,
                                    f"Violations: {len(hygiene_violations)}",
                                )
                                # Store violations for aggregation
                                if not state_mgr.state.get("hygiene_violations"):
                                    state_mgr.state["hygiene_violations"] = []
                                state_mgr.state["hygiene_violations"].extend(hygiene_violations)
                            else:
                                state_mgr.complete_agent(
                                    "RootHygieneAgent",
                                    False,
                                    "No scan_root_violations method",
                                )
                        # guardian: allow-silent-swallow
                        except Exception as e:
                            logger.warning(f"RootHygieneAgent failed: {e}")
                            state_mgr.complete_agent("RootHygieneAgent", False, str(e))

                        # Phase 5
                        cert = execute_phase5_final(agents, territory, state_mgr, decision_engine)
                        results.append(cert)
                    else:
                        logger.error(f"Phase 1 failed for {territory} - skipping")
                        state_mgr.add_event("error", f"Phase 1 failure in {territory}")

                except RuntimeError as runtime_err:
                    # Catch the NonInteractiveGuard trap specifically
                    if "Interactive prompt blocked" in str(runtime_err):
                        logger.critical(f"🛑 BLOCKED INTERACTIVE PROMPT in {territory}: {runtime_err}")
                        state_mgr.add_event("error", f"Blocked Prompt in {territory}")
                        continue  # Skip this territory, try next
                    raise runtime_err
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.error(f"❌ Protocol crashed on {territory}: {e}")
                    traceback.print_exc()
                    state_mgr.add_event("error", f"Crash in {territory}: {str(e)[:200]}")
                    if is_autonomous:
                        continue
                    else:
                        state_mgr.finish_mission(status="error")
                        sys.exit(1)

            # Only mark completed if we got here
            state_mgr.finish_mission(status="completed")

            # Final Summary
            logger.info(f"\n{'=' * 60}")
            logger.info("🎉 UNIFIED PROTOCOL COMPLETED")
            logger.info(f"{'=' * 60}")
            logger.info(f"Territories processed: {len(results)}/{len(targets)}")
            logger.info(f"Decisions made: {len(decision_engine.decisions_made)}")

            # Decision breakdown
            high_conf = sum(1 for d in decision_engine.decisions_made if d["confidence"] > 0.75)
            med_conf = sum(1 for d in decision_engine.decisions_made if 0.5 <= d["confidence"] <= 0.75)
            low_conf = sum(1 for d in decision_engine.decisions_made if d["confidence"] < 0.5)
            logger.info(f"  High confidence: {high_conf}, Medium: {med_conf}, Low: {low_conf}")

            return results

    # guardian: allow-silent-swallow
    except Exception as fatal_e:
        # Catch-all for top-level crashes (e.g., initialization failure)
        logger.critical(f"🔥 FATAL PROTOCOL ERROR: {fatal_e}")
        traceback.print_exc()
        state_mgr.finish_mission(status="fatal_error")
        sys.exit(1)


# ============================================================================
# DYNAMIC AGENT DISCOVERY (Step 1 Implementation)
# ============================================================================
def load_agents(project_root: Path | None = None) -> dict[str, Any]:
    """
    Dynamically discovers and loads compliant Healer Agents.
    Wraps non-compliant agents in LegacyAgentAdapter.

    Scans 'agentic_core' and 'apps_*' for classes that:
    1. Have 'Agent' or 'Validator' in their name.
    2. Implement the 'heal' method (Standard Heal Interface) OR can be adapted.

    Returns:
        Dict[str, Any]: Map of agent_name -> initialized_instance (or adapter)
    """
    if project_root is None:
        project_root = REPO_ROOT
    logging.info("Starting dynamic agent discovery...")
    discovered_agents = {}

    # Define search paths relative to project root
    search_paths = [
        project_root / "agentic_core",
        # Add other apps_* folders if needed, e.g., apps_private
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Walk directory
        for root, _, files in os.walk(search_path):
            for file in files:
                if not file.endswith(".py") or file.startswith("__"):
                    continue

                # Heuristic: Check file content for 'class' and 'Agent' before importing
                file_path = Path(root) / file
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if "class " not in content or (
                            "Agent" not in content and "Validator" not in content and "Fixer" not in content
                        ):
                            continue
                # guardian: allow-silent-swallow
                except Exception:
                    continue

                # Construct module path for import
                try:
                    rel_path = file_path.relative_to(project_root)
                    module_name = str(rel_path).replace(os.sep, ".")[:-3]  # strip .py

                    # Safe Import
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if not spec or not spec.loader:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # Inspect classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Broaden search to include anything that LOOKS like a healer
                        is_likely_agent = (
                            obj.__module__ == module_name
                            and ("Agent" in name or "Fixer" in name or "Validator" in name)
                            and not name.startswith("Base")
                        )

                        if is_likely_agent:
                            try:
                                instance = obj()

                                # CHECK 1: Does it strictly implement the Protocol?
                                if isinstance(instance, IHealerProtocol):
                                    discovered_agents[name] = instance
                                    logging.debug(f"Loaded Standard Agent: {name}")

                                # CHECK 2: Does it have a 'heal' method (Duck Typing)?
                                elif hasattr(instance, "heal") and callable(instance.heal):
                                    discovered_agents[name] = instance
                                    logging.debug(f"Loaded Duck-Typed Agent: {name}")

                                # CHECK 3: Legacy Fallback (Wrap it)
                                else:
                                    logging.info(f"Wrapping Legacy Agent: {name}")
                                    discovered_agents[name] = LegacyAgentAdapter(instance)

                            # guardian: allow-silent-swallow
                            except Exception as e:
                                logging.warning(f"Failed to instantiate {name}: {e}")

                # guardian: allow-silent-swallow
                except Exception as e:
                    logging.debug(f"Skipping module {file_path}: {e}")

    logging.info(f"Discovery complete. Loaded {len(discovered_agents)} agents (including adapters).")
    return discovered_agents


# ============================================================================
# SIGNAL HANDLING (Graceful Shutdown)
# ============================================================================
class GracefulExitHandler:
    """Captures SIGINT/SIGTERM to allow Phase 2 writes to finish safely."""

    def __init__(self, state_mgr: RuntimeStateManager):
        self.state_mgr = state_mgr
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum: int, frame: FrameType | None):
        """Signal handler."""
        if self.kill_now:
            logging.critical("Force quitting on second signal...")
            sys.exit(1)

        logging.warning("\n[!] Shutdown signal received. Finishing current agent operation...")
        self.kill_now = True
        self.state_mgr.finish_mission("aborted_by_user")
        # The logic in Phase 2 should check self.kill_now if loop is tight,
        # but for now we rely on the loop completing the current atomic fix.


# [REMOVED DUPLICATE] main_legacy removed to resolve dual-main entry point confusion.
# The unified main() function below is the single source of truth.


if __name__ == "__main__":
    raise SystemExit(main())
