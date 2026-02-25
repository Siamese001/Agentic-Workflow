"""W11: Canonical Replay Envelope for End-to-End Determinism.

Defines the ReplayEnvelope, a universal artifact for capturing the complete
deterministic state of a generation or embedding operation.
"""

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ReplayEnvelope:
    """A universal replay artifact for tracking deterministic state."""

    routing_hash: str
    manifest_hash: str
    model_id: str
    model_version: str
    temperature: float
    allowed_model_policy_version: str
    embedder_provider: str
    embedder_model: str
    embedder_dim: int
    normalization_policy: str
    chunking_policy: str
    distance_metric: str
    retrieval_top_k: int
    retrieval_similarity_cutoff: float
    policy_version: str
    gateway_version: str
    agent_registry_hash: str
    code_commit_hash: str | None
    deterministic_engine_version: str

    def to_canonical_json(self) -> str:
        """Serialize to a sorted, minified JSON string."""
        # Use asdict to convert dataclass to dict, ensuring order doesn't matter here
        data = asdict(self)
        # Filter out None values to ensure deterministic output
        data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data, sort_keys=True, separators=(",", ":"))
