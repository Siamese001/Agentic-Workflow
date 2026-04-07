#!/usr/bin/env python3
"""
Wave packing optimizer with incremental token accounting.
Groups plan phases into waves targeting a specific token context window.
Uses incremental token growth model with shared prefix separation.
"""

from typing import Any

# ============================================================
# CONFIG (Aligned to OpenAI best practices)
# ============================================================

MAX_CONTEXT_TOKENS = 200_000

# Shared prefix = system prompt + static instructions + tools + schemas
# This SHOULD be measured once, not hardcoded
DEFAULT_SHARED_PREFIX_TOKENS = 4000

# Conversation history tokens (rolling window)
DEFAULT_HISTORY_TOKENS = 2000

# Reserve for output + reasoning (critical for correctness)
GENERATION_RESERVE_TOKENS = 25000

# Safety buffer for estimation drift
SAFETY_BUFFER_TOKENS = 5000


# ============================================================
# CORE PACKER (Incremental Token Accounting)
# ============================================================


def pack_waves(
    phases: list[dict[str, Any]],
    max_context_tokens: int = MAX_CONTEXT_TOKENS,
    shared_prefix_tokens: int = DEFAULT_SHARED_PREFIX_TOKENS,
    history_tokens: int = DEFAULT_HISTORY_TOKENS,
    generation_reserve_tokens: int = GENERATION_RESERVE_TOKENS,
    safety_buffer_tokens: int = SAFETY_BUFFER_TOKENS,
) -> list[dict[str, Any]]:
    """
    Packs phases into waves using:

    total_context =
        shared_prefix_tokens   (constant, cacheable)
      + history_tokens         (rolling)
      + incremental_phase_tokens (grows per phase)
      + generation_reserve_tokens (reserved output/reasoning)
      + safety_buffer_tokens

    KEY CHANGE:
    - Uses incremental token growth instead of naive per-phase tokens
    - Separates shared prefix (cacheable) vs dynamic tokens
    - Reserves output tokens explicitly
    """

    waves: list[dict[str, Any]] = []
    current_wave: list[dict[str, Any]] = []

    incremental_tokens = 0

    def compute_total_context(incremental: int) -> int:
        return (
            shared_prefix_tokens
            + history_tokens
            + incremental
            + generation_reserve_tokens
            + safety_buffer_tokens
        )

    for phase in phases:
        # New required field (fallback to legacy)
        inc_tokens = phase.get("incremental_input_tokens") or phase.get("tokens", 0)

        projected_total = compute_total_context(incremental_tokens + inc_tokens)

        if projected_total > max_context_tokens:
            waves.append(
                {
                    "phases": current_wave,
                    "tokens": compute_total_context(incremental_tokens),
                    "break_reason": "context_limit",
                },
            )

            current_wave = []
            incremental_tokens = 0

        current_wave.append(phase)
        incremental_tokens += inc_tokens

    if current_wave:
        waves.append(
            {
                "phases": current_wave,
                "tokens": compute_total_context(incremental_tokens),
                "break_reason": "end",
            },
        )

    return waves


# ============================================================
# OPTIONAL: REPORTING (Visibility + Debugging)
# ============================================================


def summarize_wave(wave: dict[str, Any]) -> dict[str, Any]:
    phases = wave["phases"]

    total_incremental = sum(p.get("incremental_input_tokens", p.get("tokens", 0)) for p in phases)

    return {
        "num_phases": len(phases),
        "incremental_tokens": total_incremental,
        "total_context_tokens": wave["tokens"],
        "phase_ids": [p.get("id") for p in phases],
    }


# ============================================================
# LEGACY COMPATIBILITY LAYER
# ============================================================


class WavePacker:
    """
    Legacy compatibility wrapper for existing code.
    Maps old API to new incremental token accounting.
    """

    def __init__(
        self,
        target_tokens: int = 155000,
        hard_limit: int = 200000,
        system_prompt_tokens: int = 2500,
        history_tokens: int = 1500,
    ):
        self.target_tokens = target_tokens
        self.hard_limit = hard_limit
        self.system_prompt_tokens = system_prompt_tokens
        self.history_tokens = history_tokens

    def pack_phases(self, phases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Legacy method that maps to new pack_waves function."""

        # Convert old format to new format expectations
        converted_phases = []
        for phase in phases:
            converted_phase = phase.copy()
            # Map old 'tokens' to 'incremental_input_tokens' if not present
            if "tokens" in phase and "incremental_input_tokens" not in phase:
                converted_phase["incremental_input_tokens"] = phase["tokens"]
            converted_phases.append(converted_phase)

        # Use new packer with legacy-compatible defaults
        waves = pack_waves(
            phases=converted_phases,
            max_context_tokens=self.hard_limit,
            shared_prefix_tokens=self.system_prompt_tokens,
            history_tokens=self.history_tokens,
        )

        # Convert back to legacy format for compatibility
        legacy_waves = []
        for wave in waves:
            legacy_wave = {
                "phases": wave["phases"],
                "total_tokens": wave["tokens"],
                "input_tokens": sum(
                    p.get("incremental_input_tokens", p.get("tokens", 0)) for p in wave["phases"]
                ),
            }
            legacy_waves.append(legacy_wave)

        return legacy_waves


def run_optimization():
    # Phase data from our previous analysis
    # P0: 9,261
    # P1: 46,755
    # P2: 4,269
    # P3: 92,401 (Original P3 before split)
    # P4: 64,104 (Original P4 before split)
    # P5: 1,926

    phases = [
        {"id": "P0", "name": "Token Optimization", "incremental_input_tokens": 9261},
        {"id": "P1", "name": "Inventory", "incremental_input_tokens": 46755},
        {"id": "P2", "name": "Archive", "incremental_input_tokens": 4269},
        {"id": "P3", "name": "Extract Capabilities", "incremental_input_tokens": 92401},
        {"id": "P4", "name": "CI Integration", "incremental_input_tokens": 64104},
        {"id": "P5", "name": "Enforcement", "incremental_input_tokens": 1926},
    ]

    print("--- Optimizing Wave Packing (Target: 150-160K) ---")
    waves = pack_waves(phases)

    for i, wave in enumerate(waves):
        print(f"\nWave {i + 1}:")
        summary = summarize_wave(wave)
        print(f"  Phases:       {', '.join(summary['phase_ids'])}")
        print(f"  Input Tokens: {summary['incremental_tokens']:>8,}")
        print(f"  Total Context: {summary['total_context_tokens']:>8,}")
        status = (
            "GREEN"
            if summary["total_context_tokens"] <= 180000
            else "YELLOW"
            if summary["total_context_tokens"] <= 200000
            else "RED"
        )
        print(f"  Status:       {status}")
        print(f"  Break Reason: {wave['break_reason']}")


if __name__ == "__main__":
    run_optimization()
