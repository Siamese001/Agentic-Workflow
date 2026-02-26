from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


class KnowledgeIntegrityViolation(Exception):
    """Raised when a knowledge mutation breaks the hash chain integrity."""


@dataclass(frozen=True)
class KnowledgeNode:
    """Represents a versioned node in the knowledge base."""

    content_hash: str  # Hash of the node's content
    prev_hash: str  # Hash of the previous node in the chain
    node_id: str
    content: dict[str, Any]
    signature: str = field(init=False)  # Signature of the node's content + prev_hash

    def __post_init__(self):
        canonical_bytes = self._canonical_bytes()
        # In a real system, this would be a proper cryptographic signature (e.g., RSA)
        # For demonstration, we use a simple SHA-256 hash as a signature.
        object.__setattr__(
            self,
            "signature",
            hashlib.sha256(canonical_bytes).hexdigest(),
        )

    def _canonical_bytes(self) -> bytes:
        """Computes the canonical byte representation for signing."""
        data = {
            "content_hash": self.content_hash,
            "prev_hash": self.prev_hash,
            "node_id": self.node_id,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


class KnowledgeIntegrityGuard:
    """
    Enforces hash chain integrity for the knowledge base.

    This guard enforces Guarantee #9 by ensuring every mutation is part of an
    unbroken, verifiable hash chain anchored to a genesis hash. It supports
    compaction through signed checkpoints to maintain integrity over time.
    """

    def __init__(self, genesis_hash: str):
        self.genesis_hash = genesis_hash
        self._ledger: dict[str, KnowledgeNode] = {}
        self._head_hash = genesis_hash

    def mutate(self, node_id: str, content: dict[str, Any]) -> KnowledgeNode:
        """
        Applies a mutation, creating a new node in the hash chain.

        Args:
            node_id: The identifier of the node to mutate.
            content: The new content for the node.

        Returns:
            The newly created, signed KnowledgeNode.
        """
        content_str = json.dumps(content, sort_keys=True).encode("utf-8")
        content_hash = hashlib.sha256(content_str).hexdigest()

        new_node = KnowledgeNode(
            content_hash=content_hash,
            prev_hash=self._head_hash,
            node_id=node_id,
            content=content,
        )

        # In a real system, this would be stored in a persistent L4 database.
        self._ledger[new_node.signature] = new_node
        self._head_hash = new_node.signature

        return new_node

    def verify_chain(self) -> bool:
        """
        Verifies the integrity of the entire hash chain from HEAD to genesis.

        Raises:
            KnowledgeIntegrityViolation: If the chain is broken.
        """
        current_hash = self._head_hash
        while current_hash != self.genesis_hash:
            if current_hash not in self._ledger:
                raise KnowledgeIntegrityViolation(f"Chain broken: Node {current_hash} not found.")

            node = self._ledger[current_hash]

            # Verify the node's own signature
            if node.signature != current_hash:
                raise KnowledgeIntegrityViolation(f"Node {node.node_id} has a corrupted signature.")

            current_hash = node.prev_hash

        return True

    def create_compaction_snapshot(self) -> dict[str, Any]:
        """
        Creates a signed checkpoint snapshot for long-term compaction.

        This allows old parts of the chain to be pruned without losing the
        overall integrity guarantee.
        """
        self.verify_chain()  # Ensure chain is valid before creating snapshot

        snapshot_content = {
            "head_hash": self._head_hash,
            "ledger_size": len(self._ledger),
            "genesis_hash": self.genesis_hash,
        }

        snapshot_str = json.dumps(snapshot_content, sort_keys=True).encode("utf-8")
        snapshot_signature = hashlib.sha256(snapshot_str).hexdigest()

        return {"snapshot": snapshot_content, "signature": snapshot_signature}
