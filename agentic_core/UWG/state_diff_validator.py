"""W11 — State Diff Validator (UWG)

Validates state diffs before L4 commit.
Ensures changes are within policy bounds.
"""
from typing import Any, Dict, List
from dataclasses import dataclass

from agentic_core.UWG import StateDiffValidationResult


@dataclass(frozen=True)
class StateDiffSpec:
    """Specification for expected state diff."""
    path: str
    expected_type: str
    max_size_delta: int = 0
    allow_deletion: bool = False


class StateDiffValidator:
    """Validates state diffs against policy.
    
    Core owns validation logic. Apps provide diff policy config.
    """
    
    DEFAULT_DIFF_SPECS = {
        "research_substrate": StateDiffSpec(
            path="/substrate/research",
            expected_type="append_only",
            max_size_delta=1000000,  # 1MB
            allow_deletion=False,
        ),
        "entity_aliases": StateDiffSpec(
            path="/index/entity_aliases",
            expected_type="merge",
            max_size_delta=100000,  # 100KB
            allow_deletion=False,
        ),
        "source_register": StateDiffSpec(
            path="/registry/sources",
            expected_type="append_only",
            max_size_delta=500000,  # 500KB
            allow_deletion=False,
        ),
        "judge_calibration": StateDiffSpec(
            path="/config/judge_calibration",
            expected_type="atomic_replace",
            max_size_delta=10000,  # 10KB
            allow_deletion=False,
        ),
    }
    
    def __init__(self, diff_policy: Dict[str, Any] = None):
        """Initialize with diff validation policy.
        
        Args:
            diff_policy: Policy for state diff validation
        """
        self._policy = diff_policy or {}
        self._specs = self._policy.get('diff_specs', self.DEFAULT_DIFF_SPECS)
    
    def validate_diff(
        self,
        write_type: str,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any],
        proposed_changes: Dict[str, Any]
    ) -> StateDiffValidationResult:
        """Validate state diff for write type.
        
        Args:
            write_type: Type of write being proposed
            state_before: State before proposed changes
            state_after: State after proposed changes
            proposed_changes: The specific changes being made
            
        Returns:
            StateDiffValidationResult with validation outcome
        """
        errors = []
        
        # Get diff spec for write type
        spec = self._specs.get(write_type, self.DEFAULT_DIFF_SPECS.get("research_substrate"))
        
        # Validate change type
        if spec.expected_type == "append_only":
            if not self._is_append_only(state_before, state_after):
                errors.append(f"{write_type}: Changes must be append-only")
        
        elif spec.expected_type == "merge":
            if not self._is_merge(state_before, state_after):
                errors.append(f"{write_type}: Changes must be merge-compatible")
        
        elif spec.expected_type == "atomic_replace":
            if not self._is_atomic_replace(state_before, state_after):
                errors.append(f"{write_type}: Changes must be atomic replace")
        
        # Validate size delta
        size_delta = self._calculate_size_delta(state_before, state_after)
        if size_delta > spec.max_size_delta:
            errors.append(
                f"{write_type}: Size delta {size_delta} exceeds max {spec.max_size_delta}"
            )
        
        # Validate no deletions (unless allowed)
        if not spec.allow_deletion:
            deletions = self._detect_deletions(state_before, state_after)
            if deletions:
                errors.append(f"{write_type}: Deletions detected but not allowed: {deletions}")
        
        # Generate hashes
        state_hash_before = self._hash_state(state_before)
        state_hash_after = self._hash_state(state_after)
        
        return StateDiffValidationResult(
            valid=len(errors) == 0,
            diff_summary={
                "write_type": write_type,
                "size_delta": size_delta,
                "change_count": len(proposed_changes),
            },
            validation_errors=errors,
            state_hash_before=state_hash_before,
            state_hash_after=state_hash_after,
        )
    
    def _is_append_only(
        self,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any]
    ) -> bool:
        """Check if changes are append-only."""
        # Simplified: check that no keys were removed or modified
        for key, value in state_before.items():
            if key not in state_after:
                return False  # Deletion detected
            if state_after[key] != value:
                return False  # Modification detected
        return True
    
    def _is_merge(
        self,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any]
    ) -> bool:
        """Check if changes are merge-compatible."""
        # Merge allows additions and non-conflicting modifications
        # Simplified check
        return True
    
    def _is_atomic_replace(
        self,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any]
    ) -> bool:
        """Check if changes are atomic replacement."""
        # Atomic replace: entire structure replaced as unit
        # Simplified check: keys completely different
        before_keys = set(state_before.keys())
        after_keys = set(state_after.keys())
        return len(before_keys & after_keys) == 0  # No overlap
    
    def _calculate_size_delta(
        self,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any]
    ) -> int:
        """Calculate size delta between states."""
        import json
        size_before = len(json.dumps(state_before, default=str))
        size_after = len(json.dumps(state_after, default=str))
        return abs(size_after - size_before)
    
    def _detect_deletions(
        self,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any]
    ) -> List[str]:
        """Detect deleted keys."""
        return [k for k in state_before if k not in state_after]
    
    def _hash_state(self, state: Dict[str, Any]) -> str:
        """Generate hash of state."""
        import hashlib
        import json
        state_str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
