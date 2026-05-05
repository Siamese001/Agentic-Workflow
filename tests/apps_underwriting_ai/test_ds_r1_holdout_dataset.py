"""DS-R1 validator — rationale_judge_holdout.yaml acceptance gate.

Enforces the DS-R1 acceptance criteria:
  - File exists and parses cleanly.
  - >= 100 examples total.
  - Each required dim_id has >= 20 examples.
  - All required fields present, typed, and non-placeholder.
  - human_score in [0.0, 1.0].
  - decision_id unique and PII-free.
  - labeler_id is not a placeholder value.
  - synthetic_seed files are explicitly NOT counted.

DS-R1 is complete only when a qualified underwriting analyst has reviewed
and labeled all records — synthetic_cascade_v1 as the sole labeler_id
causes this test to FAIL by design.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_PATH = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"
SYNTHETIC_SEED_PATH = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.synthetic_seed.yaml"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUIRED_DIMS = {
    "evidence_sufficiency",
    "feature_derivation_correctness",
    "policy_compliance",
    "explainability",
    "fairness",
}
MIN_TOTAL = 100
MIN_PER_DIM = 20

# labeler_ids that are NOT analyst-provided — records bearing these values
# do not count toward DS-R1 acceptance.
SYNTHETIC_LABELER_IDS = {
    "synthetic_cascade_v1",
    "synthetic_cascade_v2",
    "synthetic",
}

# Placeholder values that MUST NOT appear in any field of a qualifying record.
PLACEHOLDER_PATTERNS = re.compile(
    r"\b(TODO|TBD|analyst_x|labeler_unknown|lorem\s+ipsum|fake_score|PLACEHOLDER|N/A)\b",
    re.IGNORECASE,
)

# Patterns that suggest PII in decision_id.
PII_PATTERNS = re.compile(
    r"\b(\d{3}-\d{2}-\d{4}|ssn|email|@|\bphone\b|\bcell\b|\bname\b)\b",
    re.IGNORECASE,
)

MIN_RATIONALE_LENGTH = 20


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_holdout() -> list[dict]:
    """Load rationale_judge_holdout.yaml and return the examples list."""
    assert HOLDOUT_PATH.exists(), (
        f"Holdout file not found: {HOLDOUT_PATH}\n"
        "DS-R1 BLOCKED — file must be created before acceptance."
    )
    with HOLDOUT_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "Top-level YAML structure must be a mapping."
    assert "examples" in data, "Top-level key 'examples' must be present."
    examples = data["examples"]
    assert isinstance(examples, list), "'examples' must be a list."
    return examples


def _load_synthetic_seed() -> list[dict]:
    """Return examples from the synthetic seed file, or empty list if absent."""
    if not SYNTHETIC_SEED_PATH.exists():
        return []
    with SYNTHETIC_SEED_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return []
    assert isinstance(data, dict), "Synthetic seed top-level must be a mapping."
    meta = data.get("dataset_metadata", {})
    assert meta.get("may_satisfy_ds_r1") is False, (
        "synthetic_seed file must have dataset_metadata.may_satisfy_ds_r1: false"
    )
    assert meta.get("acceptance_status") == "not_ds_r1_compliant", (
        "synthetic_seed file must have acceptance_status: not_ds_r1_compliant"
    )
    return data.get("examples", [])


def _analyst_examples(examples: list[dict], seed_ids: set[str]) -> list[dict]:
    """Return only examples that are analyst-provided (not synthetic).

    Exclusion criteria:
      - decision_id appears in the synthetic seed file.
      - labeler_id is in SYNTHETIC_LABELER_IDS.
    """
    qualified = []
    for ex in examples:
        labeler = str(ex.get("labeler_id", ""))
        did = str(ex.get("decision_id", ""))
        if labeler in SYNTHETIC_LABELER_IDS:
            continue
        if did in seed_ids:
            continue
        qualified.append(ex)
    return qualified


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHoldoutFileStructure:
    """Basic file existence and YAML structure."""

    def test_file_exists(self):
        assert HOLDOUT_PATH.exists(), (
            f"rationale_judge_holdout.yaml not found at {HOLDOUT_PATH}"
        )

    def test_yaml_parses_cleanly(self):
        with HOLDOUT_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert data is not None

    def test_top_level_has_examples_key(self):
        with HOLDOUT_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert "examples" in data, "Top-level key 'examples' is required."
        assert isinstance(data["examples"], list)


class TestSyntheticSeedFile:
    """Synthetic seed file integrity and non-DS-R1-compliance markers."""

    def test_seed_file_has_non_compliance_markers(self):
        if not SYNTHETIC_SEED_PATH.exists():
            pytest.skip("No synthetic seed file present — nothing to validate.")
        with SYNTHETIC_SEED_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert data is not None
        meta = data.get("dataset_metadata", {})
        assert meta.get("dataset_status") == "synthetic_seed_only", (
            "dataset_metadata.dataset_status must be 'synthetic_seed_only'"
        )
        assert meta.get("acceptance_status") == "not_ds_r1_compliant", (
            "dataset_metadata.acceptance_status must be 'not_ds_r1_compliant'"
        )
        assert meta.get("may_satisfy_ds_r1") is False, (
            "dataset_metadata.may_satisfy_ds_r1 must be false"
        )

    def test_seed_examples_have_synthetic_labeler(self):
        if not SYNTHETIC_SEED_PATH.exists():
            pytest.skip("No synthetic seed file present.")
        with SYNTHETIC_SEED_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        for ex in data.get("examples", []):
            assert ex.get("labeler_id") in SYNTHETIC_LABELER_IDS, (
                f"Seed example {ex.get('decision_id')} has unexpected labeler_id "
                f"'{ex.get('labeler_id')}' — seed records must use a synthetic labeler."
            )


class TestDS_R1AcceptanceCriteria:
    """Core DS-R1 acceptance gate — WILL FAIL until analyst labels land."""

    @pytest.fixture(scope="class")
    def all_examples(self):
        return _load_holdout()

    @pytest.fixture(scope="class")
    def seed_ids(self):
        seed_examples = _load_synthetic_seed()
        return {str(ex.get("decision_id", "")) for ex in seed_examples}

    @pytest.fixture(scope="class")
    def analyst_examples(self, all_examples, seed_ids):
        return _analyst_examples(all_examples, seed_ids)

    # ------------------------------------------------------------------
    # Count gates
    # ------------------------------------------------------------------

    def test_total_analyst_count_gte_100(self, analyst_examples):
        n = len(analyst_examples)
        assert n >= MIN_TOTAL, (
            f"DS-R1 BLOCKED: only {n} analyst-labeled examples; need >= {MIN_TOTAL}.\n"
            "Current records use labeler_id=synthetic_cascade_v1 and do NOT count.\n"
            "A qualified underwriting analyst must label >= 100 records."
        )

    def test_per_dim_count_gte_20(self, analyst_examples):
        dim_counts: dict[str, int] = {}
        for ex in analyst_examples:
            dim_counts[ex.get("dim_id", "")] = dim_counts.get(ex.get("dim_id", ""), 0) + 1
        failures = []
        for dim in REQUIRED_DIMS:
            count = dim_counts.get(dim, 0)
            if count < MIN_PER_DIM:
                failures.append(f"  {dim}: {count} (need >= {MIN_PER_DIM})")
        assert not failures, (
            "DS-R1 BLOCKED — insufficient analyst-labeled examples per dimension:\n"
            + "\n".join(failures)
        )

    # ------------------------------------------------------------------
    # Field presence and type checks (run on ALL records)
    # ------------------------------------------------------------------

    def test_required_fields_present(self, all_examples):
        required = {"decision_id", "dim_id", "rationale_text", "labeler_id"}
        missing_field_records = []
        for ex in all_examples:
            missing = required - set(ex.keys())
            if missing:
                missing_field_records.append(
                    f"  {ex.get('decision_id', '<unknown>')} missing: {missing}"
                )
        assert not missing_field_records, (
            "Records missing required fields:\n" + "\n".join(missing_field_records)
        )

    def test_human_score_field_present(self, all_examples):
        """human_score OR ground_truth_score must be present and numeric."""
        bad = []
        for ex in all_examples:
            score = ex.get("human_score", ex.get("ground_truth_score"))
            if score is None:
                bad.append(f"  {ex.get('decision_id')}: missing human_score/ground_truth_score")
        assert not bad, "Records missing score field:\n" + "\n".join(bad)

    def test_human_score_in_range(self, all_examples):
        bad = []
        for ex in all_examples:
            score = ex.get("human_score", ex.get("ground_truth_score"))
            if score is None:
                continue
            try:
                v = float(score)
            except (TypeError, ValueError):
                bad.append(f"  {ex.get('decision_id')}: score not numeric: {score!r}")
                continue
            if not (0.0 <= v <= 1.0):
                bad.append(
                    f"  {ex.get('decision_id')}: score {v} out of [0.0, 1.0]"
                )
        assert not bad, "Records with out-of-range scores:\n" + "\n".join(bad)

    def test_dim_id_is_canonical(self, all_examples):
        bad = []
        for ex in all_examples:
            dim = ex.get("dim_id", "")
            if dim not in REQUIRED_DIMS:
                bad.append(
                    f"  {ex.get('decision_id')}: invalid dim_id '{dim}'"
                )
        assert not bad, (
            f"Records with non-canonical dim_id (must be one of {REQUIRED_DIMS}):\n"
            + "\n".join(bad)
        )

    def test_decision_id_unique(self, all_examples):
        seen: dict[str, int] = {}
        for ex in all_examples:
            did = str(ex.get("decision_id", ""))
            seen[did] = seen.get(did, 0) + 1
        dups = [did for did, cnt in seen.items() if cnt > 1]
        assert not dups, f"Duplicate decision_ids: {dups}"

    def test_decision_id_no_pii(self, all_examples):
        flagged = []
        for ex in all_examples:
            did = str(ex.get("decision_id", ""))
            if PII_PATTERNS.search(did):
                flagged.append(f"  {did}: PII pattern detected")
        assert not flagged, "decision_ids with potential PII:\n" + "\n".join(flagged)

    def test_rationale_text_non_empty_for_analyst_records(self, analyst_examples):
        """Analyst records must have rationale_text of meaningful length."""
        short = []
        for ex in analyst_examples:
            text = str(ex.get("rationale_text", "") or "")
            if len(text.strip()) < MIN_RATIONALE_LENGTH:
                short.append(
                    f"  {ex.get('decision_id')}: rationale_text too short "
                    f"({len(text.strip())} chars, min {MIN_RATIONALE_LENGTH})"
                )
        assert not short, (
            "Analyst records with rationale_text too short:\n" + "\n".join(short)
        )

    def test_no_placeholder_values(self, analyst_examples):
        flagged = []
        for ex in analyst_examples:
            for field in ("rationale_text", "labeler_id", "decision_id"):
                val = str(ex.get(field, "") or "")
                if PLACEHOLDER_PATTERNS.search(val):
                    flagged.append(
                        f"  {ex.get('decision_id')}.{field}: placeholder detected in {val!r}"
                    )
        assert not flagged, (
            "Analyst records with placeholder values:\n" + "\n".join(flagged)
        )

    def test_labeler_id_non_empty(self, analyst_examples):
        """Each analyst example must have a non-empty, non-placeholder labeler_id."""
        bad = []
        for ex in analyst_examples:
            lid = str(ex.get("labeler_id", "") or "").strip()
            if not lid:
                bad.append(f"  {ex.get('decision_id')}: empty labeler_id")
        assert not bad, "Analyst records with empty labeler_id:\n" + "\n".join(bad)
