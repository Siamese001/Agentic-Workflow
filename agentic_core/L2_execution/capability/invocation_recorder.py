"""C7 G7: INVOCATION RECORD - Audit logging.

10C-REQ-161: Record usage who used what provider tool compute cost audit log seal replay envelope
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class InvocationRecord:
    """Record of a capability invocation.
    
    10C-REQ-161: Who used what provider tool compute cost audit log seal replay envelope.
    """
    record_id: str
    actor_id: str
    capability_token: str
    provider: str
    tool: str
    timestamp: float
    cost_units: float
    status: str
    input_hash: str
    output_hash: str
    replay_envelope_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class InvocationRecorder:
    """C7 G7: Invocation recorder.
    
    10C-REQ-161: Record usage who used what provider tool compute cost.
    """
    
    COST_RATES = {
        "claude": 0.008,
        "gpt": 0.006,
        "gemini": 0.005,
        "local": 0.0,
    }
    
    def __init__(self, log_path: Path | None = None) -> None:
        self._records: list[InvocationRecord] = []
        self._log_path = log_path or Path("data/invocation_log.jsonl")
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._record_counter: int = 0
    
    def record(
        self,
        actor_id: str,
        capability_token: str,
        provider: str,
        tool: str,
        status: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        replay_envelope_hash: str = "",
    ) -> InvocationRecord:
        """Record an invocation."""
        self._record_counter += 1
        
        # Compute hashes
        input_hash = self._hash_dict(inputs)
        output_hash = self._hash_dict(outputs)
        
        # Calculate cost
        cost = self._calculate_cost(provider, tool)
        
        record = InvocationRecord(
            record_id=f"INV-{self._record_counter:08d}",
            actor_id=actor_id,
            capability_token=capability_token,
            provider=provider,
            tool=tool,
            timestamp=time.time(),
            cost_units=cost,
            status=status,
            input_hash=input_hash,
            output_hash=output_hash,
            replay_envelope_hash=replay_envelope_hash,
            metadata={
                "input_keys": list(inputs.keys()),
                "output_keys": list(outputs.keys()),
            },
        )
        
        self._records.append(record)
        self._append_to_log(record)
        
        return record
    
    def _hash_dict(self, data: dict[str, Any]) -> str:
        """Hash dictionary for integrity."""
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def _calculate_cost(self, provider: str, tool: str) -> float:
        """Calculate invocation cost."""
        rate = self.COST_RATES.get(provider, 0.001)
        # Add tool-specific multiplier
        if "embedding" in tool:
            return rate * 0.5
        if "completion" in tool:
            return rate * 2.0
        return rate
    
    def _append_to_log(self, record: InvocationRecord) -> None:
        """Append record to durable log."""
        with open(self._log_path, "a") as f:
            data = {
                "record_id": record.record_id,
                "actor_id": record.actor_id,
                "provider": record.provider,
                "tool": record.tool,
                "timestamp": record.timestamp,
                "cost": record.cost_units,
                "status": record.status,
                "input_hash": record.input_hash,
                "output_hash": record.output_hash,
            }
            f.write(json.dumps(data) + "\n")
            f.flush()
    
    def get_audit_trail(self, actor_id: str | None = None) -> list[InvocationRecord]:
        """Get audit trail for actor or all."""
        if actor_id:
            return [r for r in self._records if r.actor_id == actor_id]
        return list(self._records)
    
    def get_total_cost(self, actor_id: str | None = None) -> float:
        """Get total cost for actor or all."""
        records = self.get_audit_trail(actor_id)
        return sum(r.cost_units for r in records)
    
    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics."""
        if not self._records:
            return {"total_invocations": 0, "total_cost": 0.0}
        
        return {
            "total_invocations": len(self._records),
            "total_cost": sum(r.cost_units for r in self._records),
            "unique_actors": len(set(r.actor_id for r in self._records)),
            "unique_providers": len(set(r.provider for r in self._records)),
        }
