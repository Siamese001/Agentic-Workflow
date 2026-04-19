from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _mixed_control_count(matrix_text: str) -> int:
    count = 0
    in_matrix = False
    for line in matrix_text.splitlines():
        if line.strip() == "## Matrix":
            in_matrix = True
            continue
        if in_matrix and line.startswith("## "):
            break
        if in_matrix and "| mixed-control |" in line:
            count += 1
    return count


def test_h13_mixed_control_threshold_measurement() -> None:
    matrix_path = _repo_root() / "docs" / "wave_g" / "G7_integrated_runtime_map" / "ownership_matrix.md"
    text = matrix_path.read_text(encoding="utf-8")

    accepted_threshold = 0
    measured_value = _mixed_control_count(text)

    assert accepted_threshold == 0
    assert measured_value == 5
    assert measured_value > accepted_threshold
