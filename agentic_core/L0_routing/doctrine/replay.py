"""03.5 L0 RouteReplayManifest.

Realizes 03.5 PHASE 4 ``RouteReplayManifest``.

Replay certification rule (03.5 §Replay certification):

    Same manifest inputs produce same selected_route_id.
    Same manifest inputs produce same route_digest.
    Same manifest inputs produce same downstream requirements.

This module provides the manifest type and a verifier that re-runs the
deterministic checks. Any drift fails replay certification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from . import DoctrineContractError

_MAX_STR = 512
_MAX_LIST = 64


def _need_str(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise DoctrineContractError(f"{name} must be str, got {type(value).__name__}")
    if len(value) > _MAX_STR:
        raise DoctrineContractError(f"{name} exceeds {_MAX_STR} chars")
    if not allow_empty and not value:
        raise DoctrineContractError(f"{name} must be non-empty")


def _need_str_tuple(values: object, name: str, *, max_len: int = _MAX_LIST) -> None:
    if not isinstance(values, tuple):
        raise DoctrineContractError(f"{name} must be tuple")
    if len(values) > max_len:
        raise DoctrineContractError(f"{name} exceeds {max_len}")
    for idx, item in enumerate(values):
        if not isinstance(item, str) or not item or len(item) > _MAX_STR:
            raise DoctrineContractError(f"{name}[{idx}] must be non-empty str <= {_MAX_STR}")


def _need_bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise DoctrineContractError(f"{name} must be bool")


@dataclass(frozen=True)
class RouteReplayManifest:
    """03.5 PHASE 4 RouteReplayManifest.

    All hashes are SHA-256 hex prefixed by their producer (e.g., ``rcf:``,
    ``order:``, ``sel:``, ``pf:``). The manifest is itself hashed via
    ``deterministic_route_digest``.
    """

    replay_manifest_id: str
    route_contract_id: str
    normalized_request_hash: str
    l1_plan_digest: str
    route_candidate_frame_hash: str
    route_score_vector_hash: str
    fixed_decision_order_hash: str
    policy_hash: str
    blueprint_hash: str
    snapshot_id: str
    source_availability_snapshot_hash: str
    registry_snapshot_hash: str
    deterministic_route_digest: str
    hmac_sig: str
    replay_certifiable: bool
    non_replayable_reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in (
            "replay_manifest_id",
            "route_contract_id",
            "normalized_request_hash",
            "l1_plan_digest",
            "route_candidate_frame_hash",
            "route_score_vector_hash",
            "fixed_decision_order_hash",
            "policy_hash",
            "blueprint_hash",
            "snapshot_id",
            "source_availability_snapshot_hash",
            "registry_snapshot_hash",
            "deterministic_route_digest",
        ):
            _need_str(getattr(self, name), f"RouteReplayManifest.{name}")
        _need_str(self.hmac_sig, "RouteReplayManifest.hmac_sig", allow_empty=True)
        _need_bool(self.replay_certifiable, "RouteReplayManifest.replay_certifiable")
        _need_str_tuple(
            self.non_replayable_reasons,
            "RouteReplayManifest.non_replayable_reasons",
        )
        # Coherence: replay_certifiable=True requires no non-replayable reasons.
        if self.replay_certifiable and self.non_replayable_reasons:
            raise DoctrineContractError(
                "replay_certifiable=True is incompatible with non-empty non_replayable_reasons",
            )
        if not self.replay_certifiable and not self.non_replayable_reasons:
            raise DoctrineContractError(
                "replay_certifiable=False requires at least one non_replayable_reason",
            )

    def canonical_payload(self) -> dict[str, object]:
        """JSON-friendly dict for digest computation. Excludes hmac_sig."""
        payload = asdict(self)
        payload.pop("hmac_sig", None)
        return payload

    def canonical_json_bytes(self) -> bytes:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def expected_digest(self) -> str:
        """Compute the deterministic SHA-256 digest of the canonical payload."""
        return f"manifest:{hashlib.sha256(self.canonical_json_bytes()).hexdigest()}"


def verify_replay(
    manifest_a: RouteReplayManifest,
    manifest_b: RouteReplayManifest,
) -> tuple[bool, tuple[str, ...]]:
    """Verify two manifests produce identical replay-bound facts.

    Returns ``(certifiable, reasons)``. ``certifiable=True`` requires:

    - both deterministic_route_digests match
    - both route_candidate_frame_hashes match
    - both fixed_decision_order_hashes match
    - both route_score_vector_hashes match
    - both source_availability_snapshot_hashes match

    All hashes are deterministic over the doctrine inputs; any difference is
    drift and fails replay certification.
    """
    if not isinstance(manifest_a, RouteReplayManifest) or not isinstance(
        manifest_b,
        RouteReplayManifest,
    ):
        raise DoctrineContractError(
            "verify_replay requires two RouteReplayManifest instances",
        )

    reasons: list[str] = []
    pairs = (
        (
            "deterministic_route_digest",
            manifest_a.deterministic_route_digest,
            manifest_b.deterministic_route_digest,
        ),
        (
            "route_candidate_frame_hash",
            manifest_a.route_candidate_frame_hash,
            manifest_b.route_candidate_frame_hash,
        ),
        (
            "fixed_decision_order_hash",
            manifest_a.fixed_decision_order_hash,
            manifest_b.fixed_decision_order_hash,
        ),
        ("route_score_vector_hash", manifest_a.route_score_vector_hash, manifest_b.route_score_vector_hash),
        (
            "source_availability_snapshot_hash",
            manifest_a.source_availability_snapshot_hash,
            manifest_b.source_availability_snapshot_hash,
        ),
        ("policy_hash", manifest_a.policy_hash, manifest_b.policy_hash),
        ("blueprint_hash", manifest_a.blueprint_hash, manifest_b.blueprint_hash),
        ("snapshot_id", manifest_a.snapshot_id, manifest_b.snapshot_id),
    )
    for label, a, b in pairs:
        if a != b:
            reasons.append(f"{label}_drift:{a}_vs_{b}")
    return (len(reasons) == 0, tuple(reasons))


__all__ = ["RouteReplayManifest", "verify_replay"]
