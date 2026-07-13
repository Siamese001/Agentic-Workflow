"""RG-SPEARMAN-DATASET: validate human holdout and leakage controls."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._apps_rg_spearman_gate_common import (  # noqa: E402
    DATASET_PATH,
    PROFILE_PATH,
    configured_path,
    finish,
    load_yaml,
)

REQUIRED_FIELDS = frozenset(
    {
        "sample_id",
        "dataset_id",
        "dataset_version",
        "task_class",
        "judge_id",
        "rubric_hash",
        "rubric_version",
        "candidate_text",
        "target_role",
        "target_level",
        "target_company",
        "human_score",
        "human_rank_band",
        "reviewer_refs",
        "adjudication_ref",
        "label_policy",
        "label_source",
        "split",
        "tags",
        "content_digest",
        "created_at",
    }
)
_DIGEST_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{line_number}: row must be an object")
        rows.append(payload)
    return rows


def _fixture_rows(path: Path) -> Iterable[dict[str, Any]]:
    try:
        if path.suffix == ".jsonl":
            yield from _load_jsonl(path)
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return
    if isinstance(payload, dict):
        yield payload
    elif isinstance(payload, list):
        yield from (row for row in payload if isinstance(row, dict))


def validate_dataset(
    *,
    dataset_path: Path = DATASET_PATH,
    profile_path: Path = PROFILE_PATH,
    fixtures_root: Path | None = None,
) -> list[str]:
    if not dataset_path.is_file():
        try:
            display_path = dataset_path.relative_to(REPO_ROOT)
        except ValueError:
            display_path = dataset_path
        return [f"human semantic holdout is missing: {display_path}"]
    try:
        rows = _load_jsonl(dataset_path)
        profile = load_yaml(profile_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    errors: list[str] = []
    minimum = int((profile.get("semantic_alignment") or {}).get("minimum_samples", 40))
    if len(rows) < minimum:
        errors.append(f"sample count {len(rows)} is below semantic minimum {minimum}")

    sample_ids: set[str] = set()
    content_digests: set[str] = set()
    rank_bands: set[str] = set()
    dataset_ids: set[str] = set()
    dataset_versions: set[str] = set()
    for index, row in enumerate(rows, 1):
        missing = sorted(REQUIRED_FIELDS - row.keys())
        if missing:
            errors.append(f"row {index} missing fields: {','.join(missing)}")
            continue
        sample_id = str(row["sample_id"])
        digest = str(row["content_digest"])
        reviewer_payload = row.get("reviewer_refs", [])
        reviewers = (
            {str(ref) for ref in reviewer_payload if str(ref)}
            if isinstance(reviewer_payload, list)
            else set()
        )
        tag_payload = row.get("tags", [])
        tags = {str(tag) for tag in tag_payload} if isinstance(tag_payload, list) else set()
        if sample_id in sample_ids:
            errors.append(f"duplicate sample_id {sample_id}")
        sample_ids.add(sample_id)
        if digest in content_digests:
            errors.append(f"duplicate content_digest {digest}")
        content_digests.add(digest)
        if not _DIGEST_RE.fullmatch(digest):
            errors.append(f"row {index} content_digest is not SHA-256")
        else:
            expected_digest = hashlib.sha256(str(row.get("candidate_text", "")).encode("utf-8")).hexdigest()
            if digest.removeprefix("sha256:") != expected_digest:
                errors.append(f"row {index} content_digest does not bind candidate_text")
        if len(reviewers) < 2:
            errors.append(f"row {index} has fewer than two reviewer refs")
        if row.get("label_source") != "human_semantic_review":
            errors.append(f"row {index} is not human_semantic_review")
        if row.get("split") != "holdout":
            errors.append(f"row {index} split is not holdout")
        if "HUMAN_SEMANTIC_RELEASE_GATE" not in tags:
            errors.append(f"row {index} lacks HUMAN_SEMANTIC_RELEASE_GATE tag")
        if not str(row.get("label_policy", "")).strip():
            errors.append(f"row {index} label_policy is missing")
        try:
            human_score = float(row.get("human_score"))
            if not math.isfinite(human_score):
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"row {index} human_score is not finite")
        try:
            created_at = datetime.fromisoformat(str(row.get("created_at", "")))
            if created_at.tzinfo is None:
                raise ValueError
        except ValueError:
            errors.append(f"row {index} created_at is not timezone-aware ISO-8601")
        if row.get("promotion_eligible") and row.get("label_source") != "human_semantic_review":
            errors.append(f"row {index} permits synthetic promotion")
        for key in ("task_class", "judge_id", "rubric_hash", "rubric_version"):
            if str(row.get(key, "")) != str(profile.get(key, "")):
                errors.append(f"row {index} {key} differs from calibration profile")
        rank_bands.add(str(row.get("human_rank_band", "")))
        dataset_ids.add(str(row.get("dataset_id", "")))
        dataset_versions.add(str(row.get("dataset_version", "")))
    if len(rank_bands - {""}) < 4:
        errors.append("holdout has fewer than four human rank bands")
    if len(dataset_ids) != 1 or "" in dataset_ids:
        errors.append("holdout dataset_id is missing or mixed")
    elif dataset_ids != {str(profile.get("dataset_id", ""))}:
        errors.append("holdout dataset_id differs from calibration profile")
    if len(dataset_versions) != 1 or "" in dataset_versions:
        errors.append("holdout dataset_version is missing or mixed")
    elif dataset_versions != {str(profile.get("dataset_version", ""))}:
        errors.append("holdout dataset_version differs from calibration profile")

    root = fixtures_root or (REPO_ROOT / "apps_eval/fixtures")
    for path in root.rglob("*.json*"):
        if path.resolve() == dataset_path.resolve():
            continue
        for row in _fixture_rows(path):
            try:
                display_path = path.relative_to(REPO_ROOT)
            except ValueError:
                display_path = path
            if str(row.get("sample_id", "")) in sample_ids:
                errors.append(f"sample_id overlap with {display_path}")
            if str(row.get("content_digest", "")) in content_digests:
                errors.append(f"content digest overlap with {display_path}")
    return errors


def main() -> int:
    dataset = configured_path("APPS_RG_SPEARMAN_DATASET", DATASET_PATH)
    return finish(
        "RG-SPEARMAN-DATASET",
        validate_dataset(dataset_path=dataset),
        fail_closed_env="APPS_RG_SPEARMAN_DATASET_FAIL_CLOSED",
    )


if __name__ == "__main__":
    raise SystemExit(main())
