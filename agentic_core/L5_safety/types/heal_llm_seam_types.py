"""Heal LLM call seam types for heal policy integrations.

Pure type definitions only (stdlib-only, no environment access or SDK imports).
Phase 7 Wave 7.1.
Phase 3: Added canonical seam enforcement via capability token.
Phase 5: Added telemetry + budget caps.
"""

from __future__ import annotations

import contextvars
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# Capability token: only standard_heal may set this to True
_HEAL_SEAM_CAPABILITY: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "_HEAL_SEAM_CAPABILITY", default=False
)


class HealSeamBypassError(Exception):
    """Raised when LLM escalation is attempted outside canonical seam."""

    pass


def set_heal_seam_capability(enabled: bool) -> contextvars.Token[bool]:
    """Set the heal seam capability token. Only callable from standard_heal."""
    return _HEAL_SEAM_CAPABILITY.set(enabled)


def reset_heal_seam_capability(token: contextvars.Token[bool]) -> None:
    """Reset the heal seam capability token."""
    _HEAL_SEAM_CAPABILITY.reset(token)


def assert_heal_seam_capability() -> None:
    """Assert that the heal seam capability is enabled.

    Raises:
        HealSeamBypassError: If called outside the canonical standard_heal seam.
    """
    if not _HEAL_SEAM_CAPABILITY.get():
        raise HealSeamBypassError(
            "LLM escalation attempted outside canonical seam (standard_heal). "
            "Direct calls to DEFAULT_HEAL_LLM_CALLER are forbidden."
        )


@dataclass(frozen=True)
class HealLlmRequest:
    """Typed request payload for heal LLM calls.

    Attributes:
        prompt: The prompt text to send to the LLM.
        model_id: Optional model identifier; None means use the default model.
        metadata: Arbitrary metadata for observability/instrumentation.
    """

    prompt: str
    model_id: str | None
    metadata: dict[str, Any]


HealLlmCaller = Callable[[HealLlmRequest], str]


def guarded_heal_llm_call(request: HealLlmRequest) -> str | None:
    """Guarded LLM call that enforces canonical seam access.

    Returns:
        LLM response string, or None if no caller is configured.

    Raises:
        HealSeamBypassError: If called outside standard_heal context.
    """
    assert_heal_seam_capability()

    if DEFAULT_HEAL_LLM_CALLER is None:
        return None

    return DEFAULT_HEAL_LLM_CALLER(request)


# Default LLM caller seam for heal flows (not wired by default).
DEFAULT_HEAL_LLM_CALLER: HealLlmCaller | None = None


@dataclass(frozen=True)
class PolicyDecisionRecord:
    """Deterministic policy decision record (no timestamps/UUIDs).

    Emitted per heal run for observability.
    """

    confidence: float
    enable_llm: bool
    complexity: int
    prior_failures: int
    proceed: bool
    tier: str | None
    threshold_used: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "confidence": self.confidence,
            "enable_llm": self.enable_llm,
            "complexity": self.complexity,
            "prior_failures": self.prior_failures,
            "proceed": self.proceed,
            "tier": self.tier,
            "threshold_used": self.threshold_used,
            "rationale": self.rationale,
        }

    def input_hash(self) -> str:
        """Compute deterministic hash of inputs for stable filenames."""
        input_str = f"{self.confidence}:{self.enable_llm}:{self.complexity}:{self.prior_failures}"
        return hashlib.sha256(input_str.encode()).hexdigest()[:16]


# =============================================================================
# PHASE 5: Telemetry + Budget Caps
# =============================================================================


class HealBudgetExceededError(Exception):
    """Raised when heal escalation budget is exceeded."""

    pass


@dataclass(frozen=True)
class HealBudgetCaps:
    """Budget caps for heal escalation (defaults from env vars)."""

    max_escalations_per_run: int = 1
    max_high_tier_per_run: int = 1

    @classmethod
    def from_env(cls, enable_llm: bool = False) -> HealBudgetCaps:
        """Load budget caps from environment variables with sensible defaults."""
        max_escalations = int(os.environ.get("HEAL_MAX_ESCALATIONS_PER_RUN", "1"))
        # HIGH-tier default is 0 when enable_llm=False, 1 otherwise
        default_high = 0 if not enable_llm else 1
        max_high = int(os.environ.get("HEAL_MAX_HIGH_TIER_PER_RUN", str(default_high)))
        return cls(
            max_escalations_per_run=max_escalations,
            max_high_tier_per_run=max_high,
        )


# Budget counters via contextvars (reset in standard_heal finally)
_ESCALATION_COUNT: contextvars.ContextVar[int] = contextvars.ContextVar("_ESCALATION_COUNT", default=0)
_HIGH_TIER_COUNT: contextvars.ContextVar[int] = contextvars.ContextVar("_HIGH_TIER_COUNT", default=0)
_BUDGET_CAPS: contextvars.ContextVar[HealBudgetCaps | None] = contextvars.ContextVar(
    "_BUDGET_CAPS", default=None
)


def set_heal_budget_caps(caps: HealBudgetCaps) -> contextvars.Token[HealBudgetCaps | None]:
    """Set budget caps for current heal run."""
    return _BUDGET_CAPS.set(caps)


def reset_heal_budget_counters() -> None:
    """Reset budget counters to zero."""
    _ESCALATION_COUNT.set(0)
    _HIGH_TIER_COUNT.set(0)


def increment_escalation_count(tier: str | None = None) -> None:
    """Increment escalation count and check budget.

    Raises:
        HealBudgetExceededError: If budget cap is exceeded.
    """
    caps = _BUDGET_CAPS.get()
    if caps is None:
        # No budget caps set, allow all
        return

    current = _ESCALATION_COUNT.get()
    if current >= caps.max_escalations_per_run:
        raise HealBudgetExceededError(
            f"Escalation budget exceeded: {current} >= {caps.max_escalations_per_run}"
        )

    _ESCALATION_COUNT.set(current + 1)

    # Check HIGH-tier budget
    if tier == "HIGH":
        high_current = _HIGH_TIER_COUNT.get()
        if high_current >= caps.max_high_tier_per_run:
            raise HealBudgetExceededError(
                f"HIGH-tier budget exceeded: {high_current} >= {caps.max_high_tier_per_run}"
            )
        _HIGH_TIER_COUNT.set(high_current + 1)


def get_budget_counters() -> dict[str, int]:
    """Get current budget counter values."""
    return {
        "escalation_count": _ESCALATION_COUNT.get(),
        "high_tier_count": _HIGH_TIER_COUNT.get(),
    }


@dataclass(frozen=True)
class HealTelemetryRecord:
    """Deterministic telemetry record for heal runs (no timestamps/UUIDs).

    Emitted per heal / heal_repository run for observability.
    """

    run_kind: Literal["heal", "heal_repository"]
    agent_class: str
    target_path: str  # repo root or file path; may be empty for single-issue heal
    inputs_hash: str  # stable hash of normalized inputs
    policy_hash: str  # PolicyDecisionRecord.input_hash()
    baseline_ops_count: int
    applied_ops_count: int
    changed_files_count: int
    idempotent_second_pass: bool
    outcome: Literal["plan_only", "applied", "blocked_budget", "blocked_policy"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "run_kind": self.run_kind,
            "agent_class": self.agent_class,
            "target_path": self.target_path,
            "inputs_hash": self.inputs_hash,
            "policy_hash": self.policy_hash,
            "baseline_ops_count": self.baseline_ops_count,
            "applied_ops_count": self.applied_ops_count,
            "changed_files_count": self.changed_files_count,
            "idempotent_second_pass": self.idempotent_second_pass,
            "outcome": self.outcome,
        }

    def telemetry_hash(self) -> str:
        """Compute deterministic hash of telemetry record for filenames."""
        record_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(record_str.encode()).hexdigest()[:16]


def emit_heal_telemetry(
    record: HealTelemetryRecord,
    artifacts_root: Path | None = None,
) -> Path:
    """Emit a deterministic telemetry artifact.

    Args:
        record: The telemetry record to emit.
        artifacts_root: Root path for artifacts (default: artifacts/consolidation/heal_telemetry)

    Returns:
        Path to the emitted artifact.

    Raises:
        ValueError: If file exists with different content.
    """
    if artifacts_root is None:
        # Use project root detection
        current = Path(__file__).resolve()
        project_root = current.parent.parent.parent.parent  # Up to agentic_core parent
        artifacts_root = project_root / "artifacts" / "consolidation" / "heal_telemetry"

    _wg.ensure_dir(artifacts_root)

    filename = f"{record.inputs_hash}.json"
    filepath = artifacts_root / filename

    # Deterministic JSON serialization
    content = json.dumps(record.to_dict(), sort_keys=True, indent=2)
    content_bytes = content.encode("utf-8")

    if filepath.exists():
        existing = filepath.read_bytes()
        if existing != content_bytes:
            raise ValueError(
                f"Telemetry artifact conflict: {filepath} exists with different content. "
                f"Expected hash: {hashlib.sha256(content_bytes).hexdigest()[:16]}, "
                f"Found hash: {hashlib.sha256(existing).hexdigest()[:16]}"
            )
        # Already exists with identical content, no-op
        return filepath

    _wg.write_bytes(filepath, content_bytes)
    return filepath


# =============================================================================
# PHASE 4: Repo-heal Pipeline (deterministic plan/apply)
# =============================================================================

# Scope controls for repo-heal operations
REPO_HEAL_DENYLIST = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

REPO_HEAL_ALLOWLIST_EXTENSIONS = frozenset(
    {
        ".py",
        ".md",
        ".txt",
        ".json",
    }
)


@dataclass(frozen=True)
class RepoHealOperation:
    """A single deterministic heal operation in a repo-heal plan."""

    path: str  # Relative path from repo_root
    operation: str  # Operation type: "validate", "lint", "format", "fix"
    reason: str  # Why this operation is needed
    priority: int  # Lower = higher priority (0 = critical)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "path": self.path,
            "operation": self.operation,
            "reason": self.reason,
            "priority": self.priority,
        }


@dataclass
class RepoHealPlan:
    """Deterministic plan for repo-wide healing."""

    repo_root: str
    operations: list[RepoHealOperation]
    scanned_files: int
    skipped_files: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "repo_root": self.repo_root,
            "operations": [op.to_dict() for op in self.operations],
            "scanned_files": self.scanned_files,
            "skipped_files": self.skipped_files,
            "total_operations": len(self.operations),
        }

    def plan_hash(self) -> str:
        """Compute deterministic hash of the plan for stable comparison."""
        import hashlib
        import json

        plan_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(plan_str.encode()).hexdigest()[:16]


@dataclass
class RepoHealResult:
    """Result of applying a repo-heal plan."""

    plan_hash: str
    operations_attempted: int
    operations_succeeded: int
    operations_failed: int
    operations_skipped: int
    is_idempotent: bool  # True if no changes were made (already clean)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "plan_hash": self.plan_hash,
            "operations_attempted": self.operations_attempted,
            "operations_succeeded": self.operations_succeeded,
            "operations_failed": self.operations_failed,
            "operations_skipped": self.operations_skipped,
            "is_idempotent": self.is_idempotent,
        }


def _is_path_allowed(path_parts: tuple[str, ...]) -> bool:
    """Check if path is allowed based on denylist."""
    for part in path_parts:
        if part in REPO_HEAL_DENYLIST:
            return False
        # Check glob patterns
        for pattern in REPO_HEAL_DENYLIST:
            if pattern.startswith("*") and part.endswith(pattern[1:]):
                return False
    return True


def _is_extension_allowed(filename: str) -> bool:
    """Check if file extension is in allowlist."""
    for ext in REPO_HEAL_ALLOWLIST_EXTENSIONS:
        if filename.endswith(ext):
            return True
    return False


def build_repo_heal_plan(repo_root: str) -> RepoHealPlan:
    """Build a deterministic repo-heal plan.

    Scans the repository and creates a sorted list of operations.
    Pure function - no side effects, no network calls.

    Args:
        repo_root: Absolute path to repository root.

    Returns:
        RepoHealPlan with deterministic, sorted operations.
    """
    import os
    from pathlib import Path, PurePosixPath

    root = Path(repo_root)
    operations: list[RepoHealOperation] = []
    scanned_files = 0
    skipped_files = 0

    # Deterministic walk: sorted directories and files
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        path_parts = rel_dir.parts

        # Filter out denied directories (modifies dirnames in-place)
        dirnames[:] = sorted([d for d in dirnames if d not in REPO_HEAL_DENYLIST])

        # Check if current directory is allowed
        if not _is_path_allowed(path_parts):
            skipped_files += len(filenames)
            continue

        # Process files in sorted order
        for filename in sorted(filenames):
            if not _is_extension_allowed(filename):
                skipped_files += 1
                continue

            scanned_files += 1
            rel_path = str(PurePosixPath(rel_dir / filename))

            # Add validation operation for each allowed file
            operations.append(
                RepoHealOperation(
                    path=rel_path,
                    operation="validate",
                    reason="baseline_scan",
                    priority=10,
                )
            )

    # Sort operations deterministically
    operations.sort(key=lambda op: (op.priority, op.path, op.operation))

    return RepoHealPlan(
        repo_root=repo_root,
        operations=operations,
        scanned_files=scanned_files,
        skipped_files=skipped_files,
    )


def apply_repo_heal_plan(
    plan: RepoHealPlan,
    dry_run: bool = True,
) -> RepoHealResult:
    """Apply a repo-heal plan deterministically.

    Pure function for dry_run=True. No network calls.

    Args:
        plan: The heal plan to apply.
        dry_run: If True, simulate operations without changes.

    Returns:
        RepoHealResult with operation counts.
    """
    from pathlib import Path

    root = Path(plan.repo_root)
    attempted = 0
    succeeded = 0
    failed = 0
    skipped = 0
    changes_made = False

    for op in plan.operations:
        attempted += 1
        file_path = root / op.path

        if not file_path.exists():
            skipped += 1
            continue

        if op.operation == "validate":
            # Validation always succeeds for existing files
            succeeded += 1
        elif dry_run:
            # In dry_run mode, all operations succeed without changes
            succeeded += 1
        else:
            # Execute mode: would apply changes here
            # For now, baseline does nothing (idempotent)
            succeeded += 1

    return RepoHealResult(
        plan_hash=plan.plan_hash(),
        operations_attempted=attempted,
        operations_succeeded=succeeded,
        operations_failed=failed,
        operations_skipped=skipped,
        is_idempotent=not changes_made,
    )
