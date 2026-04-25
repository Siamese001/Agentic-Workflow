"""Unit tests for :mod:`system_learning.rubrics.registry`.

Covers:

- Round-trip load of ``config/judges/rubrics.yaml`` (the in-repo SSOT).
- Hash stability under cosmetic YAML edits (whitespace, trailing newline).
- Hash sensitivity to semantic change (threshold bumps).
- ``reload`` picks up on-disk edits.
- Unknown rubric_id raises ``KeyError``.

Tests are hermetic where possible — they copy the SSOT into a temp dir and
edit the copy, so the real rubrics.yaml is never mutated.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from system_learning.rubrics import RubricRegistry, load_rubric_file


REPO_ROOT = Path(__file__).resolve().parents[4]
CANONICAL_RUBRICS = REPO_ROOT / "config" / "judges" / "rubrics.yaml"


@pytest.fixture()
def rubrics_yaml_copy(tmp_path: Path) -> Path:
    dst_dir = tmp_path / "config" / "judges"
    dst_dir.mkdir(parents=True)
    dst = dst_dir / "rubrics.yaml"
    dst.write_text(CANONICAL_RUBRICS.read_text(encoding="utf-8"), encoding="utf-8")
    return dst


def test_load_ssot_rubrics_yaml_roundtrip() -> None:
    rubric_file = load_rubric_file("rubrics", CANONICAL_RUBRICS)
    assert rubric_file.rubric_id == "rubrics"
    assert rubric_file.version >= 1
    assert "faithfulness" in rubric_file.dimensions
    faith = rubric_file.dimensions["faithfulness"]
    assert faith.scale_min == 1
    assert faith.scale_max == 5
    assert 0.0 < faith.pass_threshold <= 5.0
    assert faith.unknown_budget > 0.0
    assert rubric_file.rubric_hash  # non-empty hex
    assert len(rubric_file.rubric_hash) == 64


def test_hash_stable_under_trailing_whitespace(tmp_path: Path, rubrics_yaml_copy: Path) -> None:
    reg1 = RubricRegistry(tmp_path)
    hash_before = reg1.rubric_hash("rubrics")

    # Cosmetic edit: add trailing spaces on a few lines + extra newline at EOF.
    text = rubrics_yaml_copy.read_text(encoding="utf-8")
    mutated = text.replace("version: 1\n", "version: 1   \n") + "\n\n"
    rubrics_yaml_copy.write_text(mutated, encoding="utf-8")

    reg2 = RubricRegistry(tmp_path)
    hash_after = reg2.rubric_hash("rubrics")
    assert hash_before == hash_after, "cosmetic whitespace edits must not change the rubric hash"


def test_hash_changes_on_semantic_edit(tmp_path: Path, rubrics_yaml_copy: Path) -> None:
    reg1 = RubricRegistry(tmp_path)
    hash_before = reg1.rubric_hash("rubrics")

    text = rubrics_yaml_copy.read_text(encoding="utf-8")
    # Bump a pass_threshold — a real semantic change.
    mutated = text.replace("pass_threshold: 4.0", "pass_threshold: 4.5", 1)
    assert mutated != text, "fixture assumption: at least one pass_threshold: 4.0 must exist"
    rubrics_yaml_copy.write_text(mutated, encoding="utf-8")

    reg2 = RubricRegistry(tmp_path)
    hash_after = reg2.rubric_hash("rubrics")
    assert hash_before != hash_after, "semantic threshold change must change the rubric hash"


def test_reload_refreshes_cache(tmp_path: Path, rubrics_yaml_copy: Path) -> None:
    reg = RubricRegistry(tmp_path)
    first_hash = reg.rubric_hash("rubrics")

    text = rubrics_yaml_copy.read_text(encoding="utf-8")
    rubrics_yaml_copy.write_text(
        text.replace("pass_threshold: 4.0", "pass_threshold: 4.5", 1),
        encoding="utf-8",
    )

    # Without reload, cached value persists.
    cached = reg.rubric_hash("rubrics")
    assert cached == first_hash

    # After reload, the registry observes the new hash.
    refreshed = reg.reload("rubrics").rubric_file.rubric_hash
    assert refreshed != first_hash


def test_unknown_rubric_id_raises(tmp_path: Path, rubrics_yaml_copy: Path) -> None:
    reg = RubricRegistry(tmp_path)
    with pytest.raises(KeyError):
        reg.get("this_rubric_does_not_exist")


def test_version_and_known_ids(tmp_path: Path, rubrics_yaml_copy: Path) -> None:
    reg = RubricRegistry(tmp_path, sources={"rubrics": "config/judges/rubrics.yaml"})
    assert reg.known_rubric_ids() == ("rubrics",)
    assert reg.version("rubrics") >= 1
