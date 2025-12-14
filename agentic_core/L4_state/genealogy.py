import hashlib
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)
class GenealogyRegistry:
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self._fingerprints: Set[str] = set()
        self._lineage_depths: Dict[str, int] = {}

    def register_attempt(self, trace_id: str, prompt: str, context_hash: str):
        """
        Registers a 'healing' attempt.
        Raises RecursionError if we are spinning in circles.
        """
        # Create a unique fingerprint for this exact problem state
        fingerprint = hashlib.sha256(f"{prompt}:{context_hash}".encode()).hexdigest()

        if fingerprint in self._fingerprints:
            raise RecursionError(f"Duplicate strategy detected for trace {trace_id}. Halting.")

        current_depth = self._lineage_depths.get(trace_id, 0)
        if current_depth >= self.max_depth:
            raise RecursionError(f"Max mutation depth ({self.
                .max_depth}) exceeded for trace {trace_id}.
                .")

        self._fingerprints.add(fingerprint)
        self._lineage_depths[trace_id] = current_depth + 1
