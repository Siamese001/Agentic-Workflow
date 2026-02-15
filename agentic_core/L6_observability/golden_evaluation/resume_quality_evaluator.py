"""
Resume Quality Evaluator - Deterministic Evaluation Contract.

Provides deterministic evaluation of resume quality against golden dataset.
No timestamps, UUIDs, or nondeterministic fields in output.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResumeQualityResult:
    """Deterministic result of resume quality evaluation."""

    total_samples: int
    passing_samples: int
    certification_hash: str
    quality_distribution: dict[str, int]
    average_score: float
    error_message: str = ""


def evaluate_resume_quality(data_root: str = None, limit: int = None) -> ResumeQualityResult:
    """Evaluate resume quality against golden dataset deterministically.

    Args:
        data_root: Root directory containing data/golden/ subdirectory
        limit: Optional limit on number of samples to process

    Returns:
        ResumeQualityResult with deterministic certification hash
    """
    if data_root is None:
        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"

    golden_dir = Path(data_root) / "golden"
    resume_file = golden_dir / "lic_resume_quality_500.jsonl"

    if not resume_file.exists():
        # Create minimal deterministic result for missing data
        result = ResumeQualityResult(
            total_samples=0,
            passing_samples=0,
            certification_hash=hashlib.sha256(b"no_data").hexdigest(),
            quality_distribution={},
            average_score=0.0,
            error_message="Golden dataset not found",
        )
        return result

    # Load and process samples
    samples = []
    with open(resume_file, encoding="utf-8") as f:
        for line in f:
            if limit and len(samples) >= limit:
                break
            samples.append(json.loads(line))

    # Deterministic evaluation logic
    passing_count = 0
    quality_dist = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
    total_score = 0.0

    for sample in samples:
        score = sample.get("score", 0)
        total_score += score

        if score >= 8:
            quality_dist["excellent"] += 1
            passing_count += 1
        elif score >= 6:
            quality_dist["good"] += 1
            passing_count += 1
        elif score >= 4:
            quality_dist["fair"] += 1
        else:
            quality_dist["poor"] += 1

    avg_score = total_score / len(samples) if samples else 0.0

    # Create deterministic hash
    hash_data = {
        "total_samples": len(samples),
        "passing_samples": passing_count,
        "quality_distribution": quality_dist,
        "average_score": avg_score,
    }
    cert_hash = hashlib.sha256(
        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    return ResumeQualityResult(
        total_samples=len(samples),
        passing_samples=passing_count,
        certification_hash=cert_hash,
        quality_distribution=quality_dist,
        average_score=avg_score,
    )
