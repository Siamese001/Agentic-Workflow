from __future__ import annotations

from pathlib import Path


MANDATORY_BLOCKERS = {
    "B7-G4-03",
    "B7-G6-03",
    "B7-G6-05",
    "B7-G6-02",
    "B7-G2b-06",
    "DISABLE_RUNTIME_MUTATION_GUARD",
    "B7-G6-04",
    "B7-G3-05",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _parse_scores(scorecard: Path, score_column: str) -> dict[str, int]:
    text = scorecard.read_text(encoding="utf-8")
    scores: dict[str, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("| "):
            continue
        if "blocker_id" in line or line.startswith("|---"):
            continue
        parts = [segment.strip() for segment in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        blocker_id = parts[0]
        if blocker_id not in MANDATORY_BLOCKERS:
            continue
        if score_column == "h11":
            value = int(parts[2])
        else:
            value = int(parts[2])
        scores[blocker_id] = value
    return scores


def test_h14_gate_requires_all_mandatory_blockers_at_three() -> None:
    root = _repo_root()
    h11_scorecard = (
        root
        / "docs"
        / "wave_h"
        / "H11_ratification_ingestion_and_gate_qualification"
        / "updated_closure_scorecard.md"
    )
    h13_scorecard = root / "docs" / "wave_h" / "H13_technical_remediation" / "updated_closure_scorecard.md"

    h11_scores = _parse_scores(h11_scorecard, "h11")
    h13_scores = _parse_scores(h13_scorecard, "h13")

    consolidated: dict[str, int] = {}
    consolidated.update(h11_scores)
    consolidated.update(h13_scores)

    assert set(consolidated.keys()) == MANDATORY_BLOCKERS
    assert all(score == 3 for score in consolidated.values())
