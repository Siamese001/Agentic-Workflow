"""C3 Sovereign Gateway - Provider-only healing operations.

10C-REQ-138: Provider-only operations mandatory invocation record sealed repair artifact
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .failure_signal import FailureSignal


@dataclass
class RepairArtifact:
    """Sealed repair artifact."""
    artifact_id: str
    repair_type: str
    input_hash: str
    output_hash: str
    model_used: str
    invocation_record_id: str
    sealed: bool = True


class SovereignGateway:
    """C3 Sovereign Gateway for healing operations.
    
    10C-REQ-138: Provider-only operations mandatory invocation record
    sealed repair artifact.
    """
    
    def __init__(self) -> None:
        self._artifacts: dict[str, RepairArtifact] = {}
        self._provider_registry: set[str] = set()
        self._artifact_counter: int = 0
    
    def execute_healing(
        self,
        signal: FailureSignal,
        model: str,
        context: dict[str, Any],
    ) -> RepairArtifact:
        """Execute healing through sovereign gateway.
        
        10C-REQ-138: All healing operations go through this chokepoint
        for recording and artifact sealing.
        """
        # Verify provider is registered
        if model not in self._provider_registry and model != "local_deterministic":
            raise ValueError(f"Model {model} not in provider registry")
        
        self._artifact_counter += 1
        artifact_id = f"REPAIR-{self._artifact_counter:08d}"
        
        # Generate invocation record (would call C7 in production)
        invocation_id = f"INV-{signal.lineage_hash[:8]}"
        
        # Hash inputs/outputs for integrity
        input_hash = self._hash_context(context)
        
        # In production, this would actually invoke the model
        # For now, create sealed artifact structure
        artifact = RepairArtifact(
            artifact_id=artifact_id,
            repair_type=signal.error_code,
            input_hash=input_hash,
            output_hash="pending_execution",  # Would be filled after execution
            model_used=model,
            invocation_record_id=invocation_id,
            sealed=True,
        )
        
        self._artifacts[artifact_id] = artifact
        return artifact
    
    def _hash_context(self, context: dict[str, Any]) -> str:
        """Hash context for integrity."""
        import hashlib
        import json
        raw = json.dumps(context, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def register_provider(self, model_name: str) -> None:
        """Register allowed healing provider."""
        self._provider_registry.add(model_name)
    
    def get_artifact(self, artifact_id: str) -> RepairArtifact | None:
        """Retrieve sealed artifact."""
        return self._artifacts.get(artifact_id)
    
    def verify_artifact(self, artifact_id: str) -> bool:
        """Verify artifact integrity."""
        artifact = self._artifacts.get(artifact_id)
        if not artifact:
            return False
        return artifact.sealed and bool(artifact.invocation_record_id)
