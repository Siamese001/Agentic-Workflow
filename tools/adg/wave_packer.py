#!/usr/bin/env python3
"""
Bin-packing optimizer for plan waves.
Groups plan phases into waves targeting a specific token context window (e.g., 150-160K).
Uses agentic_core.planning.token_estimator for accurate token counts.
"""

import os
import sys
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)

# Ensure we can import from agentic_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from agentic_core.planning.token_estimator import ContextWindowEstimator, TokenBudget
except ImportError as e:
    logging.error(f"Could not import token estimation utilities: {e}")
    sys.exit(1)

class WavePacker:
    def __init__(self, target_tokens: int = 155000, hard_limit: int = 200000):
        if target_tokens >= hard_limit:
            raise ValueError("target_tokens must be strictly less than hard_limit.")
            
        self.target_tokens = target_tokens
        self.hard_limit = hard_limit
        self.estimator = ContextWindowEstimator(TokenBudget(HARD_MAX_CONTEXT=hard_limit))
        # Account for overhead
        self.overhead = self.estimator.budget.DEFAULT_RESERVED_OUTPUT + self.estimator.budget.DEFAULT_SAFETY_BUFFER

    def pack_phases(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Greedy bin-packing of phases into waves.
        Preserves original order of phases.
        Raises ValueError if a single phase exceeds the hard limit.
        """
        if not phases:
            return []
            
        waves = []
        current_wave_phases = []
        current_wave_tokens = 0

        for phase in phases:
            if 'tokens' not in phase or not isinstance(phase['tokens'], (int, float)) or phase['tokens'] < 0:
                raise ValueError(f"Invalid or missing 'tokens' value in phase: {phase.get('id', 'Unknown')}")
                
            phase_tokens = int(phase['tokens'])
            
            # Strict enforcement: Check if this single phase is too big
            if phase_tokens + self.overhead > self.hard_limit:
                raise ValueError(
                    f"Phase {phase.get('id')} requires {phase_tokens + self.overhead:,} tokens "
                    f"(including overhead), exceeding the hard limit of {self.hard_limit:,}."
                )

            # If adding this phase exceeds target, finish current wave and start new one
            if current_wave_phases and (current_wave_tokens + phase_tokens + self.overhead > self.target_tokens):
                waves.append({
                    "phases": current_wave_phases,
                    "total_tokens": current_wave_tokens + self.overhead,
                    "input_tokens": current_wave_tokens
                })
                current_wave_phases = []
                current_wave_tokens = 0

            current_wave_phases.append(phase)
            current_wave_tokens += phase_tokens

        # Add the last wave
        if current_wave_phases:
            waves.append({
                "phases": current_wave_phases,
                "total_tokens": current_wave_tokens + self.overhead,
                "input_tokens": current_wave_tokens
            })

        return waves

def run_optimization():
    # Phase data from our previous analysis
    # P0: 9,261
    # P1: 46,755
    # P2: 4,269
    # P3: 92,401 (Original P3 before split)
    # P4: 64,104 (Original P4 before split)
    # P5: 1,926
    
    phases = [
        {"id": "P0", "name": "Token Optimization", "tokens": 9261},
        {"id": "P1", "name": "Inventory", "tokens": 46755},
        {"id": "P2", "name": "Archive", "tokens": 4269},
        {"id": "P3", "name": "Extract Capabilities", "tokens": 92401},
        {"id": "P4", "name": "CI Integration", "tokens": 64104},
        {"id": "P5", "name": "Enforcement", "tokens": 1926},
    ]

    print(f"--- Optimizing Wave Packing (Target: 150-160K) ---")
    packer = WavePacker(target_tokens=160000)
    waves = packer.pack_phases(phases)

    for i, wave in enumerate(waves):
        print(f"\nWave {i+1}:")
        phase_ids = [p['id'] for p in wave['phases']]
        print(f"  Phases:       {', '.join(phase_ids)}")
        print(f"  Input Tokens: {wave['input_tokens']:>8,}")
        print(f"  Total Context: {wave['total_tokens']:>8,}")
        status = "GREEN" if wave['total_tokens'] <= 150000 else "YELLOW" if wave['total_tokens'] <= 170000 else "RED"
        print(f"  Status:       {status}")

if __name__ == "__main__":
    run_optimization()
