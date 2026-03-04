from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReplayKeyComponents:
    """A structured container for all components that define a replay key."""

    # Decision-specific context
    tier_selection: str
    retry_count: int

    # Configuration surfaces
    threshold_config: dict[str, float]  # e.g., {"X": 0.75, "Y": 0.40}
    tool_budget_caps: dict[str, int]
    freshness_windows: dict[str, int]
    config_surface_hash: str

    # Embedding context
    embedding_pack_hash: str
    embedding_model_version: str

    # C0 context for drift detection
    c0_context_hash: str


def compute_replay_key(components: ReplayKeyComponents) -> str:
    """
    Computes a deterministic replay key from a comprehensive set of components.

    This function enforces Guarantee #12 by creating a single, verifiable hash
    that represents the entire context of a governance decision. Any change to
    the inputs (e.g., a config change, a model update, or a different retry
    count) will produce a different key, ensuring that replays are always
    executed against the exact context of the original decision.

    The key is computed in L6 (Observability) and would be stored in L4 (State)
    alongside the decision record.

    Args:
        components: A structured dataclass containing all parts of the replay key.

    Returns:
        A SHA-256 hex digest representing the deterministic replay key.
    """

    # Use the canonical JSON serialization from the digest authority to ensure
    # deterministic output. For this standalone module, we define a local helper.
    def _canonical_json(data: Any) -> str:
        """Computes canonical JSON: sorted keys, UTF-8, no whitespace."""
        return json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    # The dictionary is created from the dataclass to ensure all fields are included.
    # Using asdict is a common pattern for this.
    from dataclasses import asdict

    material = asdict(components)

    # The canonical string is then hashed to produce the final key.
    canonical_string = _canonical_json(material)
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
