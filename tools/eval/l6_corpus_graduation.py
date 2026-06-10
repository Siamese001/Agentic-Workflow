"""L6 exhaust-to-corpus graduation contract.

L6 observations may become eval corpus scenarios only through a sealed staging
candidate, a human review packet, and deterministic replay evidence. This
module is eval-side only; it never mutates runtime state or current-run verdicts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal


SCHEMA_VERSION = "l6_corpus_graduation.v1"
REQUIRED_EXHAUST_REFS = ("trace_refs", "gate_refs", "judge_refs", "exit_disposition_ref")


@dataclass(frozen=True, slots=True)
class L6Candidate:
    candidate_id: str
    source_exhaust_id: str
    finding_id: str
    failure_family: str
    scenario_seed: dict[str, Any]
    source_hash: str
    status: Literal["STAGED", "BLOCKED"]
    reason_codes: list[str]


@dataclass(frozen=True, slots=True)
class L6ReviewPacket:
    candidate_id: str
    blind: bool
    required_reviewer_count: int
    reviewer_instructions: list[str]
    scenario_seed: dict[str, Any]
    excluded_fields: list[str]


@dataclass(frozen=True, slots=True)
class L6GraduationDecision:
    candidate_id: str
    graduated: bool
    target_corpus_path: str | None
    reason_codes: list[str]


def _canonical_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _text(value: Any) -> str:
    return str(value or "").strip()


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_exhaust_package(exhaust: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for key in REQUIRED_EXHAUST_REFS:
        value = exhaust.get(key)
        if key.endswith("_refs"):
            if not _list(value):
                reasons.append(f"MISSING_{key.upper()}")
        elif not _text(value):
            reasons.append(f"MISSING_{key.upper()}")
    if exhaust.get("current_run_closed") is not True:
        reasons.append("CURRENT_RUN_NOT_CLOSED")
    if exhaust.get("created_after_exit") is not True:
        reasons.append("NOT_CREATED_AFTER_EXIT")
    if exhaust.get("no_l6_current_run_mutation_assertion") is not True:
        reasons.append("L6_MUTATION_ASSERTION_MISSING")
    if exhaust.get("l6_can_change_x3") is True or exhaust.get("l6_can_change_exit_disposition") is True:
        reasons.append("L6_RUNTIME_AUTHORITY_CLAIMED")
    return reasons


def stage_candidates(exhaust: dict[str, Any]) -> list[L6Candidate]:
    exhaust_id = _text(exhaust.get("runtime_exhaust_bundle_id") or exhaust.get("bundle_id"))
    if not exhaust_id:
        exhaust_id = _canonical_hash(exhaust)[:16]
    package_reasons = validate_exhaust_package(exhaust)
    findings = _list(exhaust.get("findings"))
    if not findings:
        return [
            L6Candidate(
                candidate_id=f"l6cand-{exhaust_id}-empty",
                source_exhaust_id=exhaust_id,
                finding_id="",
                failure_family="unknown",
                scenario_seed={},
                source_hash=_canonical_hash(exhaust),
                status="BLOCKED",
                reason_codes=package_reasons + ["NO_FINDINGS"],
            )
        ]

    candidates: list[L6Candidate] = []
    for index, raw in enumerate(findings):
        finding = raw if isinstance(raw, dict) else {}
        finding_id = _text(finding.get("finding_id") or f"finding-{index}")
        family = _text(finding.get("failure_family") or finding.get("family") or "unknown")
        scenario_seed = finding.get("scenario_seed") if isinstance(finding.get("scenario_seed"), dict) else {}
        reasons = list(package_reasons)
        if not scenario_seed:
            reasons.append("SCENARIO_SEED_MISSING")
        if not family or family == "unknown":
            reasons.append("FAILURE_FAMILY_MISSING")
        status: Literal["STAGED", "BLOCKED"] = "BLOCKED" if reasons else "STAGED"
        candidates.append(
            L6Candidate(
                candidate_id=f"l6cand-{exhaust_id}-{finding_id}",
                source_exhaust_id=exhaust_id,
                finding_id=finding_id,
                failure_family=family,
                scenario_seed=scenario_seed,
                source_hash=_canonical_hash({"exhaust": exhaust_id, "finding": finding}),
                status=status,
                reason_codes=reasons,
            )
        )
    return candidates


def build_review_packet(candidate: L6Candidate, *, required_reviewer_count: int = 2) -> L6ReviewPacket:
    return L6ReviewPacket(
        candidate_id=candidate.candidate_id,
        blind=True,
        required_reviewer_count=required_reviewer_count,
        reviewer_instructions=[
            "Review the scenario seed for deterministic replay suitability.",
            "Approve only if the failure is reproducible and not current-run rescue.",
            "Do not use judge scores, provider identities, or runtime verdicts as labels.",
        ],
        scenario_seed=dict(candidate.scenario_seed),
        excluded_fields=["judge_scores", "provider_identity", "x3_runtime_verdict_override"],
    )


def _approved_reviews(review_doc: dict[str, Any], candidate_id: str) -> list[dict[str, Any]]:
    rows = _list(review_doc.get("reviews"))
    out: list[dict[str, Any]] = []
    for raw in rows:
        row = raw if isinstance(raw, dict) else {}
        if _text(row.get("candidate_id")) != candidate_id:
            continue
        if row.get("decision") == "APPROVE":
            out.append(row)
    return out


def decide_graduation(
    candidate: L6Candidate,
    review_doc: dict[str, Any],
    replay_receipt: dict[str, Any],
    *,
    target_corpus_path: str,
) -> L6GraduationDecision:
    reasons: list[str] = []
    if candidate.status != "STAGED":
        reasons.append("CANDIDATE_NOT_STAGED")
    required = int(review_doc.get("required_reviewer_count") or 2)
    approved = _approved_reviews(review_doc, candidate.candidate_id)
    unique_reviewers = {_text(r.get("reviewer_id")) for r in approved if _text(r.get("reviewer_id"))}
    if len(unique_reviewers) < required:
        reasons.append("REVIEW_QUORUM_NOT_MET")
    if replay_receipt.get("passed") is not True:
        reasons.append("REPLAY_NOT_PASSED")
    baseline = replay_receipt.get("baseline") if isinstance(replay_receipt.get("baseline"), dict) else {}
    if baseline.get("status") == "REGRESSION":
        reasons.append("BASELINE_REGRESSION")
    if _text(replay_receipt.get("scenario_id")) != _text(candidate.scenario_seed.get("scenario_id")):
        reasons.append("REPLAY_SCENARIO_MISMATCH")

    return L6GraduationDecision(
        candidate_id=candidate.candidate_id,
        graduated=not reasons,
        target_corpus_path=target_corpus_path if not reasons else None,
        reason_codes=reasons,
    )


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    stage = sub.add_parser("stage", help="Stage candidates from an L6 exhaust package")
    stage.add_argument("--exhaust", type=Path, required=True)
    stage.add_argument("--out", type=Path, default=None)

    review = sub.add_parser("review-packet", help="Build a blind review packet for one candidate")
    review.add_argument("--candidate", type=Path, required=True)
    review.add_argument("--out", type=Path, default=None)

    grad = sub.add_parser("graduate", help="Decide whether a candidate can graduate")
    grad.add_argument("--candidate", type=Path, required=True)
    grad.add_argument("--reviews", type=Path, required=True)
    grad.add_argument("--replay-receipt", type=Path, required=True)
    grad.add_argument("--target-corpus-path", required=True)
    grad.add_argument("--out", type=Path, default=None)

    args = parser.parse_args(argv)
    try:
        if args.cmd == "stage":
            payload = {"schema_version": SCHEMA_VERSION, "candidates": [asdict(c) for c in stage_candidates(_load_json(args.exhaust))]}
            code = 0 if all(c["status"] == "STAGED" for c in payload["candidates"]) else 1
        elif args.cmd == "review-packet":
            candidate_doc = _load_json(args.candidate)
            candidate = L6Candidate(**candidate_doc)
            payload = asdict(build_review_packet(candidate))
            code = 0
        else:
            candidate = L6Candidate(**_load_json(args.candidate))
            payload = asdict(
                decide_graduation(
                    candidate,
                    _load_json(args.reviews),
                    _load_json(args.replay_receipt),
                    target_corpus_path=args.target_corpus_path,
                )
            )
            code = 0 if payload["graduated"] else 1
    except (OSError, ValueError, json.JSONDecodeError, TypeError) as exc:
        print(f"[CONFIG_ERROR] {exc}", file=sys.stderr)
        return 2

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
