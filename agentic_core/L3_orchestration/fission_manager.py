#!/usr/bin/env python3
"""
L3 Orchestration: FissionManager
Determines when a file is too large or an agent is exhausted.
"""

import os
from typing import Optional, Tuple


class FissionManager:
    """Determines when a file is too large or an agent is exhausted."""
    
    def __init__(self, line_limit: int = 800, max_rounds: int = 3):
        """
        Initialize FissionManager.
        
        Args:
            line_limit: Maximum lines before triggering fission
            max_rounds: Maximum healing rounds before exhaustion
        """
        self.line_limit = line_limit
        self.max_rounds = max_rounds

    def should_trigger_fission(
        self, 
        file_path: str, 
        current_round: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if fission should be triggered based on file size or healing exhaustion.
        
        Args:
            file_path: Path to file being validated
            current_round: Current healing round number
            
        Returns:
            Tuple of (should_trigger, reason)
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                line_count = len(f.readlines())
                if line_count > self.line_limit:
                    return True, f"L4 State Bloat: {line_count} lines exceeds limit."
        
        if current_round >= self.max_rounds:
            return True, "Cognitive Exhaustion: Round 3 reached."
        
        return False, None
