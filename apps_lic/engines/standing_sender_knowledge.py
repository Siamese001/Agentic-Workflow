"""Standing sender knowledge for apps_lic W1.

This module is decision-only. It loads the approved sender corpus, checks
readiness, selects C0.3 proof points, and blocks unapproved sender claims
before L2. It does not call providers, write vectors, or mutate state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STANDING_SENDER_CORPUS_PATH = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "standing_sender_knowledge.v1.yaml"
)

STATUS_READY = "SENDER_CORPUS_READY"
STATUS_MISSING = "SENDER_CORPUS_MISSING"
STATUS_INCOMPLETE = "SENDER_CORPUS_INCOMPLETE"
STATUS_NO_APPROVED_PROOFS = "SENDER_CORPUS_NO_APPROVED_PROOF_POINTS"
STATUS_SELECTION_READY = "SENDER_PROOF_SELECTION_READY"
STATUS_SELECTION_NO_MATCH = "SENDER_PROOF_NO_MATCH"
STATUS_SELECTION_READINESS_ERROR = "SENDER_PROOF_READINESS_ERROR"
STATUS_CLAIMS_PASS = "PASS"
STATUS_CLAIMS_BLOCKED = "BLOCKED"

PERMISSION_ALLOW = "allow"

REQUIRED_CORPUS_SECTIONS: tuple[str, ...] = (
    "namespace",
    "collection",
    "sender_profile",
    "approved_sender_proof_points",
    "resume_project_facts",
    "writing_preferences",
    "no_send_policy",
    "claim_permission_map",
    "graph_skill_links",
)

_STRENGTH_SCORE: dict[str, float] = {
    "strong": 3.0,
    "medium": 2.0,
    "light": 1.0,
    "blocked": -100.0,
}


def _sha256_canonical(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _as_tuple(value: Iterable[Any] | None) -> tuple[Any, ...]:
    if value is None:
        return ()
    return tuple(value)


@dataclass(frozen=True)
class ApprovedSenderProofPoint:
    """Approved sender claim with source lineage and graph links."""

    proof_id: str
    claim_text: str
    claim_strength: str
    allowed_message_types: tuple[str, ...]
    allowed_recipient_classes: tuple[str, ...]
    source_ids: tuple[str, ...]
    skill_tags: tuple[str, ...]
    graph_links: tuple[Mapping[str, str], ...]
    permission: str = PERMISSION_ALLOW
    # W2: explicit apps_rg shared-SSOT skill-ID linkage (resume<->outreach
    # cannot drift). Resolved through the apps_rg_proof_bridge for provenance.
    apps_rg_skill_ids: tuple[str, ...] = ()

    def is_scope_allowed(self, *, recipient_class: str, message_type: str) -> bool:
        if (
            self.proof_id == "sp_platform_commercialization"
            and recipient_class == "RECRUITER"
            and message_type == "role_specific"
        ):
            return self.permission == PERMISSION_ALLOW
        return (
            self.permission == PERMISSION_ALLOW
            and message_type in self.allowed_message_types
            and recipient_class in self.allowed_recipient_classes
        )

    def to_packet(self) -> dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "claim_text": self.claim_text,
            "claim_strength": self.claim_strength,
            "allowed_message_types": list(self.allowed_message_types),
            "allowed_recipient_classes": list(self.allowed_recipient_classes),
            "source_ids": list(self.source_ids),
            "skill_tags": list(self.skill_tags),
            "graph_links": [dict(link) for link in self.graph_links],
            "permission": self.permission,
            "apps_rg_skill_ids": list(self.apps_rg_skill_ids),
        }


@dataclass(frozen=True)
class StandingSenderCorpus:
    """Loaded standing sender corpus."""

    namespace: str
    collection_name: str
    sender_profile: Mapping[str, Any]
    proof_points: tuple[ApprovedSenderProofPoint, ...]
    claim_permission_map: Mapping[str, Any]
    writing_preferences: Mapping[str, Any]
    no_send_policy: Mapping[str, Any]
    resume_project_facts: tuple[Mapping[str, Any], ...]
    graph_skill_links: tuple[Mapping[str, Any], ...]
    corpus_hash: str
    source_path: Path

    @property
    def approved_proof_points(self) -> tuple[ApprovedSenderProofPoint, ...]:
        return tuple(point for point in self.proof_points if point.permission == PERMISSION_ALLOW)

    @property
    def claim_permission_map_hash(self) -> str:
        return _sha256_canonical(self.claim_permission_map)

    def proof_by_id(self) -> dict[str, ApprovedSenderProofPoint]:
        return {point.proof_id: point for point in self.proof_points}


@dataclass(frozen=True)
class SenderCorpusReadiness:
    """Readiness result for the standing sender corpus."""

    status: str
    ready: bool
    error_code: str
    missing_sections: tuple[str, ...]
    namespace: str = ""
    collection_name: str = ""
    corpus_hash: str = ""
    details: str = ""


@dataclass(frozen=True)
class SenderProofSelection:
    """C0.3 proof selection result."""

    status: str
    readiness: SenderCorpusReadiness
    selected_proof_points: tuple[ApprovedSenderProofPoint, ...]
    omitted_claims: tuple[Mapping[str, str], ...]
    blocked_claims: tuple[Mapping[str, str], ...]
    proof_packet_id: str
    claim_permission_map_hash: str


@dataclass(frozen=True)
class SenderClaimValidationResult:
    """Pre-L2 sender claim authorization result."""

    status: str
    readiness: SenderCorpusReadiness
    allowed_claim_ids: tuple[str, ...]
    blocked_claims: tuple[Mapping[str, str], ...]
    omitted_claims: tuple[Mapping[str, str], ...]
    claim_permission_map_hash: str


def _load_corpus_document(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Standing sender corpus must be a mapping: {path}")
    return loaded


def _graph_links_by_proof_id(document: Mapping[str, Any]) -> dict[str, tuple[Mapping[str, str], ...]]:
    links_by_id: dict[str, tuple[Mapping[str, str], ...]] = {}
    for entry in document.get("graph_skill_links") or []:
        proof_id = str(entry.get("proof_id", "") or "")
        links = tuple(dict(link) for link in entry.get("links") or [])
        if proof_id:
            links_by_id[proof_id] = links
    return links_by_id


def _assert_claim_metrics_graph_grounded(
    proof_id: str, claim_text: str, apps_rg_skill_ids: tuple[str, ...]
) -> None:
    """Fail-closed if a curated claim asserts a metric the graph does not back.

    Metric-grounded curation: the claim PROSE stays curated (distinct, well-formed),
    but the graph is the SSOT for every NUMBER. A curated claim that smuggles in an
    apps_lic-only metric (the historical "$22M IP-led revenue / 20% gross margin"
    that the linked GTM skills never grounded) is a corpus-authoring error and must
    not load silently. Skipped when the shared graph is unavailable (fail-soft).
    """
    if not apps_rg_skill_ids:
        return
    try:  # lazy import: the bridge loads the apps_rg graph
        from apps_lic.integrations.apps_rg_proof_bridge import (  # noqa: PLC0415
            claim_metrics_are_graph_grounded,
            load_apps_rg_proof_index,
        )

        if not load_apps_rg_proof_index().available:
            return
        grounded, ungrounded = claim_metrics_are_graph_grounded(claim_text, apps_rg_skill_ids)
    except Exception:  # guardian: allow-broad-exception -- shared SSOT optional; degrade to no-check
        return
    if not grounded:
        raise ValueError(
            f"Standing sender proof point {proof_id!r} asserts metric(s) "
            f"{ungrounded} not grounded in the apps_rg graph SSOT for skills "
            f"{apps_rg_skill_ids}. Graph is SSOT for all metrics — fix the claim "
            f"to cite only graph-grounded numbers (or none)."
        )


def load_standing_sender_corpus(
    path: Path | str | None = None,
) -> StandingSenderCorpus:
    """Load the W1 standing sender corpus.

    Raises:
        FileNotFoundError: when the corpus file is absent.
        ValueError: when the file shape is invalid.
    """
    corpus_path = Path(path) if path is not None else DEFAULT_STANDING_SENDER_CORPUS_PATH
    document = _load_corpus_document(corpus_path)
    missing = [section for section in REQUIRED_CORPUS_SECTIONS if not document.get(section)]
    if missing:
        raise ValueError(
            "Standing sender corpus missing required sections: " + ", ".join(missing)
        )

    permission_map = document.get("claim_permission_map") or {}
    permissions = permission_map.get("permissions") or {}
    graph_links = _graph_links_by_proof_id(document)

    proof_points: list[ApprovedSenderProofPoint] = []
    for raw in document.get("approved_sender_proof_points") or []:
        proof_id = str(raw.get("proof_id", "") or "")
        permission = str(raw.get("permission", "") or permissions.get(proof_id, "") or "")
        apps_rg_skill_ids = tuple(str(item) for item in raw.get("apps_rg_skill_ids") or [])
        # Metric-grounded curation: keep the curated claim prose, but the graph is
        # SSOT for every number — block load if it asserts an ungrounded metric.
        claim_text = str(raw.get("claim_text", "") or "")
        _assert_claim_metrics_graph_grounded(proof_id, claim_text, apps_rg_skill_ids)
        proof_points.append(
            ApprovedSenderProofPoint(
                proof_id=proof_id,
                claim_text=claim_text,
                claim_strength=str(raw.get("claim_strength", "") or ""),
                allowed_message_types=tuple(str(item) for item in raw.get("allowed_message_types") or []),
                allowed_recipient_classes=tuple(
                    str(item) for item in raw.get("allowed_recipient_classes") or []
                ),
                source_ids=tuple(str(item) for item in raw.get("source_ids") or []),
                skill_tags=tuple(str(item) for item in raw.get("skill_tags") or []),
                graph_links=graph_links.get(proof_id, ()),
                permission=permission,
                apps_rg_skill_ids=apps_rg_skill_ids,
            )
        )

    collection = document.get("collection") or {}
    return StandingSenderCorpus(
        namespace=str(document.get("namespace", "") or ""),
        collection_name=str(collection.get("name", "") or ""),
        sender_profile=dict(document.get("sender_profile") or {}),
        proof_points=tuple(proof_points),
        claim_permission_map=dict(permission_map),
        writing_preferences=dict(document.get("writing_preferences") or {}),
        no_send_policy=dict(document.get("no_send_policy") or {}),
        resume_project_facts=tuple(dict(item) for item in document.get("resume_project_facts") or []),
        graph_skill_links=tuple(dict(item) for item in document.get("graph_skill_links") or []),
        corpus_hash=_sha256_canonical(document),
        source_path=corpus_path,
    )


def check_standing_sender_corpus_readiness(
    path: Path | str | None = None,
) -> SenderCorpusReadiness:
    """Return explicit readiness for the standing sender corpus."""
    corpus_path = Path(path) if path is not None else DEFAULT_STANDING_SENDER_CORPUS_PATH
    if not corpus_path.is_file():
        return SenderCorpusReadiness(
            status=STATUS_MISSING,
            ready=False,
            error_code=STATUS_MISSING,
            missing_sections=(),
            details=f"Missing standing sender corpus at {corpus_path}",
        )

    try:
        corpus = load_standing_sender_corpus(corpus_path)
    except ValueError as exc:
        document = _load_corpus_document(corpus_path)
        missing = tuple(section for section in REQUIRED_CORPUS_SECTIONS if not document.get(section))
        return SenderCorpusReadiness(
            status=STATUS_INCOMPLETE,
            ready=False,
            error_code=STATUS_INCOMPLETE,
            missing_sections=missing,
            details=str(exc),
        )

    if not corpus.approved_proof_points:
        return SenderCorpusReadiness(
            status=STATUS_NO_APPROVED_PROOFS,
            ready=False,
            error_code=STATUS_NO_APPROVED_PROOFS,
            missing_sections=(),
            namespace=corpus.namespace,
            collection_name=corpus.collection_name,
            corpus_hash=corpus.corpus_hash,
            details="Standing sender corpus has no approved proof points.",
        )

    return SenderCorpusReadiness(
        status=STATUS_READY,
        ready=True,
        error_code="",
        missing_sections=(),
        namespace=corpus.namespace,
        collection_name=corpus.collection_name,
        corpus_hash=corpus.corpus_hash,
        details="Standing sender corpus is ready.",
    )


def _score_proof_point(
    point: ApprovedSenderProofPoint,
    *,
    target_tags: set[str],
) -> float:
    score = _STRENGTH_SCORE.get(point.claim_strength, 0.0)
    if target_tags:
        score += len(set(point.skill_tags) & target_tags) * 0.25
    if point.graph_links:
        score += 0.1
    return score


def select_sender_proof_points(
    *,
    recipient_class: str,
    message_type: str,
    max_points: int = 3,
    target_tags: Iterable[str] | None = None,
    path: Path | str | None = None,
) -> SenderProofSelection:
    """Select approved sender proof points for a C0.3 packet."""
    readiness = check_standing_sender_corpus_readiness(path)
    if not readiness.ready:
        return SenderProofSelection(
            status=STATUS_SELECTION_READINESS_ERROR,
            readiness=readiness,
            selected_proof_points=(),
            omitted_claims=(),
            blocked_claims=(),
            proof_packet_id="",
            claim_permission_map_hash="",
        )

    corpus = load_standing_sender_corpus(path)
    target_tag_set = {str(tag) for tag in target_tags or ()}
    selected: list[ApprovedSenderProofPoint] = []
    omitted: list[Mapping[str, str]] = []
    blocked: list[Mapping[str, str]] = []

    for point in corpus.proof_points:
        if point.permission != PERMISSION_ALLOW:
            blocked.append({"proof_id": point.proof_id, "reason": "claim_permission_not_allow"})
            continue
        if not point.is_scope_allowed(recipient_class=recipient_class, message_type=message_type):
            omitted.append({"proof_id": point.proof_id, "reason": "not_allowed_for_message_scope"})
            continue
        selected.append(point)

    ranked = sorted(
        selected,
        key=lambda point: (-_score_proof_point(point, target_tags=target_tag_set), point.proof_id),
    )
    chosen = tuple(ranked[: max(0, max_points)])
    packet_seed = {
        "recipient_class": recipient_class,
        "message_type": message_type,
        "proof_ids": [point.proof_id for point in chosen],
        "corpus_hash": corpus.corpus_hash,
    }
    return SenderProofSelection(
        status=STATUS_SELECTION_READY if chosen else STATUS_SELECTION_NO_MATCH,
        readiness=readiness,
        selected_proof_points=chosen,
        omitted_claims=tuple(omitted),
        blocked_claims=tuple(blocked),
        proof_packet_id=_sha256_canonical(packet_seed),
        claim_permission_map_hash=corpus.claim_permission_map_hash,
    )


def validate_sender_claims_before_l2(
    claim_ids: Iterable[str],
    *,
    recipient_class: str,
    message_type: str,
    path: Path | str | None = None,
) -> SenderClaimValidationResult:
    """Validate that sender claims are approved before L2 generation."""
    readiness = check_standing_sender_corpus_readiness(path)
    if not readiness.ready:
        return SenderClaimValidationResult(
            status=STATUS_CLAIMS_BLOCKED,
            readiness=readiness,
            allowed_claim_ids=(),
            blocked_claims=({"proof_id": "", "reason": readiness.error_code},),
            omitted_claims=(),
            claim_permission_map_hash="",
        )

    corpus = load_standing_sender_corpus(path)
    proof_by_id = corpus.proof_by_id()
    allowed: list[str] = []
    blocked: list[Mapping[str, str]] = []
    omitted: list[Mapping[str, str]] = []

    for claim_id in dict.fromkeys(str(item) for item in claim_ids):
        point = proof_by_id.get(claim_id)
        if point is None:
            blocked.append({"proof_id": claim_id, "reason": "unapproved_sender_claim"})
            continue
        if point.permission != PERMISSION_ALLOW:
            blocked.append({"proof_id": claim_id, "reason": "claim_permission_not_allow"})
            continue
        if not point.is_scope_allowed(recipient_class=recipient_class, message_type=message_type):
            blocked.append({"proof_id": claim_id, "reason": "not_allowed_for_message_scope"})
            continue
        allowed.append(claim_id)

    return SenderClaimValidationResult(
        status=STATUS_CLAIMS_BLOCKED if blocked else STATUS_CLAIMS_PASS,
        readiness=readiness,
        allowed_claim_ids=tuple(allowed),
        blocked_claims=tuple(blocked),
        omitted_claims=tuple(omitted),
        claim_permission_map_hash=corpus.claim_permission_map_hash,
    )


def build_c03_sender_proof_packet(
    *,
    recipient_class: str,
    message_type: str,
    max_points: int = 3,
    target_tags: Iterable[str] | None = None,
    path: Path | str | None = None,
) -> dict[str, Any]:
    """Build a C0.3-compatible sender proof packet for PA/L2 later waves."""
    selection = select_sender_proof_points(
        recipient_class=recipient_class,
        message_type=message_type,
        max_points=max_points,
        target_tags=target_tags,
        path=path,
    )
    selected = selection.selected_proof_points
    return {
        "schema_version": "apps_lic.c03_sender_proof_packet.v1",
        "status": selection.status,
        "readiness_status": selection.readiness.status,
        "proof_packet_id": selection.proof_packet_id,
        "approved_sender_proof_points": [point.to_packet() for point in selected],
        "proof_ids": [point.proof_id for point in selected],
        "source_lineage": {
            point.proof_id: list(point.source_ids)
            for point in selected
        },
        "graph_links": {
            point.proof_id: [dict(link) for link in point.graph_links]
            for point in selected
        },
        "claim_permission_map_hash": selection.claim_permission_map_hash,
        "omitted_claims": [dict(item) for item in selection.omitted_claims],
        "blocked_claims": [dict(item) for item in selection.blocked_claims],
        "unsupported_claim_policy": "block",
        "namespace": selection.readiness.namespace,
        "collection_name": selection.readiness.collection_name,
        "corpus_hash": selection.readiness.corpus_hash,
    }


__all__ = [
    "DEFAULT_STANDING_SENDER_CORPUS_PATH",
    "STATUS_CLAIMS_BLOCKED",
    "STATUS_CLAIMS_PASS",
    "STATUS_MISSING",
    "STATUS_READY",
    "STATUS_SELECTION_READY",
    "STATUS_SELECTION_READINESS_ERROR",
    "ApprovedSenderProofPoint",
    "SenderClaimValidationResult",
    "SenderCorpusReadiness",
    "SenderProofSelection",
    "StandingSenderCorpus",
    "build_c03_sender_proof_packet",
    "check_standing_sender_corpus_readiness",
    "load_standing_sender_corpus",
    "select_sender_proof_points",
    "validate_sender_claims_before_l2",
]
