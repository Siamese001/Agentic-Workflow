"""apps_rg-local executive-summary regen support protocols.

These helpers mirror the small stable shapes apps_rg needs while the lean-core
binding work removes direct imports from concrete L2 regen internals.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

REGEN_DELTA_HEADER = "REGEN_DELTA_v1"
PROMPT_LOCK_GENERIC = (
    "PROMPT_LOCK: The frozen compiled prompt remains authoritative. "
    "Apply only the bounded judge/gate delta below. Do not restate system rules, "
    "rubrics, schemas, or synthesis instructions."
)

REPAIR_TACTIC_INCREMENTAL_DELTA = "incremental_delta_turn_v1"
CONTRACT_VERSION = "1.0.0"
DEFAULT_MAX_DELTA_LINES = 20
DEFAULT_MAX_DELTA_TOKENS = 1024
DEFAULT_MAX_SEMANTIC_REGEN_ATTEMPTS = 1


def format_regen_delta_user_turn(delta_lines: tuple[str, ...]) -> str:
    """Build the bounded REGEN_DELTA user message from app-owned delta lines."""

    body = "\n".join(line.rstrip() for line in delta_lines if line.strip())
    return f"{REGEN_DELTA_HEADER}\n{PROMPT_LOCK_GENERIC}\n{body}"


class JudgeDirectedRegenStep(str, Enum):
    EVALUATE_TRIGGER = "evaluate_trigger"
    SAME_AUTHORITY_REGEN = "same_authority_regen"
    PREPARE_CANDIDATE = "prepare_candidate"
    X2_PRE_SNAPSHOT = "x2_pre_snapshot"
    X2_POST_REGEN = "x2_post_regen"
    X2_REPAIR = "x2_repair"
    JUDGE_RESCORE = "judge_rescore"
    EMIT_RECEIPTS = "emit_receipts"


DEFAULT_STEP_ORDER: tuple[JudgeDirectedRegenStep, ...] = (
    JudgeDirectedRegenStep.EVALUATE_TRIGGER,
    JudgeDirectedRegenStep.SAME_AUTHORITY_REGEN,
    JudgeDirectedRegenStep.PREPARE_CANDIDATE,
    JudgeDirectedRegenStep.X2_PRE_SNAPSHOT,
    JudgeDirectedRegenStep.X2_POST_REGEN,
    JudgeDirectedRegenStep.X2_REPAIR,
    JudgeDirectedRegenStep.JUDGE_RESCORE,
    JudgeDirectedRegenStep.EMIT_RECEIPTS,
)


@dataclass(frozen=True, slots=True)
class JudgeDirectedRegenPlan:
    """Immutable apps_rg regen loop plan."""

    steps: tuple[JudgeDirectedRegenStep, ...] = DEFAULT_STEP_ORDER
    require_x2_pass_before_rescore: bool = True
    allow_x2_repair: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "judge_directed_regen_plan_v1",
            "steps": [s.value for s in self.steps],
            "require_x2_pass_before_rescore": self.require_x2_pass_before_rescore,
            "allow_x2_repair": self.allow_x2_repair,
        }


@dataclass(frozen=True)
class PromptMessages:
    """Structured slot envelope consumed by same-authority regen adapters."""

    slot_map: dict[str, str] = field(default_factory=dict)
    ordered_slots: tuple[str, ...] = ()
    exemplars: tuple[tuple[str, str], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def system_text(self, separator: str = "\n\n") -> str:
        if "SYSTEM" in self.slot_map and not any(
            code in self.slot_map for code in ("S0", "I0", "D0", "C0", "E0", "M0", "H0")
        ):
            return self.slot_map["SYSTEM"]
        ordered = self.ordered_slots or tuple(self.slot_map)
        parts = [
            self.slot_map[code]
            for code in ordered
            if code in ("S0", "I0", "D0", "C0", "E0", "M0", "H0") and code in self.slot_map
        ]
        return separator.join(part for part in parts if part)

    def user_text(self) -> str:
        if "U0" in self.slot_map:
            return self.slot_map["U0"]
        return self.slot_map.get("USER", "")

    def to_flat(self) -> tuple[str, str]:
        return self.system_text(), self.user_text()

    def as_dict(self) -> dict[str, Any]:
        return {
            "slot_map": dict(self.slot_map),
            "ordered_slots": list(self.ordered_slots),
            "exemplars": [list(pair) for pair in self.exemplars],
            "metadata": dict(self.metadata),
        }


def sha256_hex(text: str) -> str:
    """Return a deterministic SHA-256 hex digest for text."""

    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def compute_system_prefix_hash(system_text: str) -> str:
    """Compute the same prefix digest shape apps_rg persists in regen receipts."""

    return sha256_hex(str(system_text or "").rstrip())


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_MAX_DELTA_LINES",
    "DEFAULT_MAX_DELTA_TOKENS",
    "DEFAULT_MAX_SEMANTIC_REGEN_ATTEMPTS",
    "DEFAULT_STEP_ORDER",
    "JudgeDirectedRegenPlan",
    "JudgeDirectedRegenStep",
    "PROMPT_LOCK_GENERIC",
    "PromptMessages",
    "REGEN_DELTA_HEADER",
    "REPAIR_TACTIC_INCREMENTAL_DELTA",
    "compute_system_prefix_hash",
    "format_regen_delta_user_turn",
    "sha256_hex",
]
