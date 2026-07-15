"""Deterministic, explicitly non-authoritative C0.3 W6 proxy baseline.

This module preserves the representative score vector authorized by the user
for engineering continuation.  It is not a human-label simulator and its
closed schema is intentionally incompatible with the official W6 CI receipt.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import yaml

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest

REPORT_SCHEMA = "apps_rg.c03_proxy_eval.report.v1"
SUMMARY_SCHEMA = "apps_rg.c03_proxy_eval.summary.v1"
EVIDENCE_CLASS = "PROVISIONAL_MODEL_PROXY"
SCORER_KIND = "approved_representative_reference_vector_v1"

# Approved representative values from the controlled W6 proxy run.  These are
# advisory engineering measurements and are replaced, never promoted, when
# authorized human labels arrive.
REPRESENTATIVE_METRICS: dict[str, float] = {
    "authority_eligibility_accuracy": 1.0,
    "exact_path_accuracy": 1.0,
    "metric_binding_accuracy": 1.0,
    "claim_entailment_accuracy": 0.7142857142857143,
    "ece": 0.08184523809523811,
    "brier": 0.19606894841269842,
    "recall_at_10": 0.35560404848039256,
    "ndcg_at_10": 0.5257259181730278,
    "mrr": 0.5283403104831675,
}

_REPORT_KEYS = {
    "schema_version",
    "evidence_class",
    "scorer_kind",
    "score_origin",
    "source",
    "canonical_profile",
    "metrics",
    "target_disposition",
    "authority",
    "record_digest",
}
_SUMMARY_KEYS = {
    "schema_version",
    "evidence_class",
    "scorer_kind",
    "source",
    "canonical_profile",
    "metrics",
    "target_disposition",
    "official_status",
    "human_review_complete",
    "active_threshold",
    "release_gate_eligible",
    "promotion_eligible",
    "future_run_only",
    "superseded_by_human_labels",
    "protected_full_report_sha256",
    "protected_full_report_record_digest",
    "record_digest",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_profile(profile_path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("canonical profile must be an object")
    if raw.get("unknown_is_pass") is not False:
        raise ValueError("canonical profile must keep UNKNOWN non-PASS")
    if not isinstance(raw.get("release_targets"), Mapping):
        raise ValueError("canonical profile release_targets missing")
    repo_root = Path(__file__).resolve().parents[3]
    try:
        profile_ref = profile_path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        raise ValueError("canonical profile must remain inside the repository") from None
    return {
        "ref": profile_ref,
        "sha256": _sha256(profile_path),
        "profile_id": str(raw.get("profile_id") or ""),
        "policy_version": str(raw.get("policy_version") or ""),
        "status": str(raw.get("status") or ""),
    }


def _source_from_blocker(blocker_path: Path) -> dict[str, Any]:
    raw = json.loads(blocker_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("W6 blocker must be an object")
    freeze = raw.get("controlled_prelabel_freeze")
    if not isinstance(freeze, Mapping):
        raise ValueError("W6 blocker lacks controlled_prelabel_freeze")
    required = {
        "source_commit_sha",
        "packet_id",
        "source_freeze_receipt_digest",
        "packet_manifest_sha256",
        "packet_manifest_digest",
    }
    if not required.issubset(freeze):
        raise ValueError("W6 blocker freeze inventory incomplete")
    return {
        key: freeze[key]
        for key in (
            "source_commit_sha",
            "packet_id",
            "source_freeze_receipt_digest",
            "packet_manifest_sha256",
            "packet_manifest_digest",
            "case_count",
            "claim_item_count",
            "retrieval_query_count",
        )
    }


def _target_disposition(metrics: Mapping[str, float]) -> dict[str, list[str]]:
    meets = [
        "authority_eligibility_accuracy_minimum",
        "exact_path_accuracy_minimum",
        "metric_binding_accuracy_minimum",
    ]
    below = [
        "claim_entailment_accuracy_minimum",
        "ece_maximum",
        "ndcg_at_k_minimum",
        "proof_confidence_candidate_support_minimum",
        "recall_at_k_minimum",
    ]
    unmeasured = [
        "proof_confidence_candidate_floor_minimum",
        "proof_confidence_candidate_precision_minimum",
    ]
    if metrics != REPRESENTATIVE_METRICS:
        raise ValueError("representative metric vector drift")
    return {
        "meets_proxy_target": meets,
        "below_proxy_target": below,
        "not_measured": unmeasured,
    }


def build_proxy_report(*, profile_path: Path, blocker_path: Path) -> dict[str, Any]:
    body: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "evidence_class": EVIDENCE_CLASS,
        "scorer_kind": SCORER_KIND,
        "score_origin": "user_authorized_representative_proxy_for_engineering_only",
        "source": _source_from_blocker(blocker_path),
        "canonical_profile": _canonical_profile(profile_path),
        "metrics": dict(REPRESENTATIVE_METRICS),
        "target_disposition": _target_disposition(REPRESENTATIVE_METRICS),
        "authority": {
            "official_w6_status": "UNKNOWN",
            "human_review_complete": False,
            "active_threshold": None,
            "release_gate_eligible": False,
            "promotion_eligible": False,
            "future_run_only": True,
            "superseded_by_human_labels": True,
            "unknown_is_pass": False,
            "target_alignment_authoritative": False,
            "current_run_mutated": False,
        },
    }
    body["record_digest"] = stable_digest(body)
    validate_proxy_report(body)
    return body


def validate_proxy_report(value: Mapping[str, Any]) -> None:
    if set(value) != _REPORT_KEYS:
        raise ValueError("proxy report key inventory mismatch")
    if value.get("schema_version") != REPORT_SCHEMA:
        raise ValueError("proxy report schema mismatch")
    if value.get("evidence_class") != EVIDENCE_CLASS:
        raise ValueError("proxy evidence class mismatch")
    if value.get("scorer_kind") != SCORER_KIND:
        raise ValueError("proxy scorer kind mismatch")
    if value.get("metrics") != REPRESENTATIVE_METRICS:
        raise ValueError("proxy metric vector mismatch")
    authority = value.get("authority")
    if not isinstance(authority, Mapping):
        raise ValueError("proxy authority missing")
    required_false = (
        "human_review_complete",
        "release_gate_eligible",
        "promotion_eligible",
        "unknown_is_pass",
        "target_alignment_authoritative",
        "current_run_mutated",
    )
    if any(authority.get(key) is not False for key in required_false):
        raise ValueError("proxy authority cannot become official")
    if authority.get("official_w6_status") != "UNKNOWN":
        raise ValueError("proxy official W6 status must remain UNKNOWN")
    if authority.get("active_threshold") is not None:
        raise ValueError("proxy cannot activate a threshold")
    if authority.get("future_run_only") is not True:
        raise ValueError("proxy must remain future-run-only")
    if authority.get("superseded_by_human_labels") is not True:
        raise ValueError("proxy must be superseded by human labels")
    expected = stable_digest(
        {key: item for key, item in value.items() if key != "record_digest"}
    )
    if value.get("record_digest") != expected:
        raise ValueError("proxy report record_digest mismatch")


def _summary(report: Mapping[str, Any], full_sha: str) -> dict[str, Any]:
    authority = report["authority"]
    body: dict[str, Any] = {
        "schema_version": SUMMARY_SCHEMA,
        "evidence_class": EVIDENCE_CLASS,
        "scorer_kind": SCORER_KIND,
        "source": dict(report["source"]),
        "canonical_profile": dict(report["canonical_profile"]),
        "metrics": dict(report["metrics"]),
        "target_disposition": dict(report["target_disposition"]),
        "official_status": authority["official_w6_status"],
        "human_review_complete": authority["human_review_complete"],
        "active_threshold": authority["active_threshold"],
        "release_gate_eligible": authority["release_gate_eligible"],
        "promotion_eligible": authority["promotion_eligible"],
        "future_run_only": authority["future_run_only"],
        "superseded_by_human_labels": authority["superseded_by_human_labels"],
        "protected_full_report_sha256": full_sha,
        "protected_full_report_record_digest": report["record_digest"],
    }
    body["record_digest"] = stable_digest(body)
    validate_proxy_summary(body)
    return body


def validate_proxy_summary(value: Mapping[str, Any]) -> None:
    if set(value) != _SUMMARY_KEYS:
        raise ValueError("proxy summary key inventory mismatch")
    if value.get("schema_version") != SUMMARY_SCHEMA:
        raise ValueError("proxy summary schema mismatch")
    if value.get("evidence_class") != EVIDENCE_CLASS:
        raise ValueError("proxy summary evidence class mismatch")
    if value.get("official_status") != "UNKNOWN":
        raise ValueError("proxy summary cannot claim official PASS")
    if value.get("release_gate_eligible") is not False:
        raise ValueError("proxy summary cannot authorize release")
    if value.get("promotion_eligible") is not False:
        raise ValueError("proxy summary cannot authorize promotion")
    if value.get("active_threshold") is not None:
        raise ValueError("proxy summary cannot activate a threshold")
    expected = stable_digest(
        {key: item for key, item in value.items() if key != "record_digest"}
    )
    if value.get("record_digest") != expected:
        raise ValueError("proxy summary record_digest mismatch")


def _atomic_private_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    body = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def emit_proxy_artifacts(
    *,
    profile_path: Path,
    blocker_path: Path,
    report_path: Path,
    summary_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    report = build_proxy_report(profile_path=profile_path, blocker_path=blocker_path)
    _atomic_private_json(report_path, report)
    # Re-read and fully validate at the write boundary before deriving the
    # distributable summary; this closes write-time drift/TOCTOU mistakes.
    written = json.loads(report_path.read_text(encoding="utf-8"))
    validate_proxy_report(written)
    summary = _summary(written, _sha256(report_path))
    _atomic_private_json(summary_path, summary)
    validate_proxy_summary(json.loads(summary_path.read_text(encoding="utf-8")))
    return written, summary


__all__ = [
    "EVIDENCE_CLASS",
    "REPORT_SCHEMA",
    "REPRESENTATIVE_METRICS",
    "SCORER_KIND",
    "SUMMARY_SCHEMA",
    "build_proxy_report",
    "emit_proxy_artifacts",
    "validate_proxy_report",
    "validate_proxy_summary",
]
