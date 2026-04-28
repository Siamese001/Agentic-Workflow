"""Fail-closed hardening tests for the Tier 0 / Tier 1 gates.

For each documented anti-cheat case, copy the relevant generated metadata
into a tmp directory, apply a controlled corruption, monkey-patch the
gate's module-level ``ARTIFACTS_DIR`` (and ``REPO_ROOT`` where relevant)
to point at the tmp tree, then assert ``evaluate()`` returns BLOCKED.

These tests do NOT execute replay machinery, OTEL exporters, the proof
harness, or the full pytest suite. They do NOT mutate any real repo
artifact or generated metadata file -- only tmp copies are touched.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Callable, List, Mapping, Sequence

import pytest

from agentic_core.runtime.prove_requirements import (
    tier0_enforcement_gate,
    tier0_runtime_proof_gate,
    tier1_enforcement_gate,
    tier1_runtime_proof_gate,
    tier2_runtime_proof_gate,
    tier3_runtime_proof_gate,
    tier_fixture_bootstrap,
)
from agentic_core.runtime.prove_requirements import (
    tier0_step1_metadata as _t0meta,
    tier1_step1_metadata as _t1meta,
    tier2_step1_metadata as _t2meta,
    tier3_step1_metadata as _t3meta,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_ARTIFACTS = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

T0_FILES = [
    "tier0_requirements_index.generated.json",
    "tier0_coverage_matrix.generated.json",
    "tier0_implementation_map.generated.json",
    "tier0_artifact_linkage.generated.json",
]
T1_FILES = [
    "tier1_requirements_index.generated.json",
    "tier1_coverage_matrix.generated.json",
    "tier1_implementation_map.generated.json",
    "tier1_artifact_linkage.generated.json",
]
T3_FILES = [
    "tier3_requirements_index.generated.json",
    "tier3_coverage_matrix.generated.json",
    "tier3_implementation_map.generated.json",
    "tier3_artifact_linkage.generated.json",
]
T2_FILES = [
    "tier2_requirements_index.generated.json",
    "tier2_coverage_matrix.generated.json",
    "tier2_implementation_map.generated.json",
    "tier2_artifact_linkage.generated.json",
]


# ---------------------------------------------------------------------------
# Module-level setup: ensure fresh deterministic fixtures + generated
# metadata exist on disk before any hardening test runs.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def _ensure_baseline() -> None:
    """Materialize fixtures and (re)generate metadata once for the module."""
    tier_fixture_bootstrap.materialize()
    _t0meta.generate()
    _t1meta.generate()
    _t2meta.generate()
    _t3meta.generate()


# ---------------------------------------------------------------------------
# Tmp-area helpers (no real-repo writes).
# ---------------------------------------------------------------------------


def _copy_metadata(tmp_path: Path, files: Sequence[str]) -> Path:
    dst = tmp_path / "artifacts" / "runtime" / "requirements_proof"
    dst.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(REAL_ARTIFACTS / f, dst / f)
    return dst


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _save(p: Path, data) -> None:
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _mutate_rows(
    metadata_dir: Path,
    files: Sequence[str],
    pick: Callable[[Mapping], bool],
    mutate: Callable[[dict], None],
) -> int:
    """Apply ``mutate`` to every row matching ``pick`` across ``files``.

    Returns the number of mutated rows.
    """
    n = 0
    for f in files:
        p = metadata_dir / f
        data = _load(p)
        for row in data.get("rows", []):
            if pick(row):
                mutate(row)
                n += 1
        _save(p, data)
    return n


def _first_req_id(metadata_dir: Path, index_file: str) -> str:
    data = _load(metadata_dir / index_file)
    return data["rows"][0]["step1_req_id"]


def _write_artifact_stub(
    tmp_path: Path,
    name: str,
    *,
    step1_req_id: str | None = None,
    expected_fail_reason: str | None = None,
    extra: dict | None = None,
) -> str:
    payload: dict = {"scenario_id": name, "schema_version": "1.0"}
    if step1_req_id is not None:
        payload["step1_req_id"] = step1_req_id
    if expected_fail_reason is not None:
        payload["expected_fail_reason"] = expected_fail_reason
    if extra:
        payload.update(extra)
    p = tmp_path / name
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(p)


def _digest(seed: str) -> str:
    return "sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Tier 0 enforcement gate (4 anti-cheat cases).
# ---------------------------------------------------------------------------


class TestTier0EnforcementGateFailsClosed:
    def _setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        d = _copy_metadata(tmp_path, T0_FILES)
        monkeypatch.setattr(tier0_enforcement_gate, "_ARTIFACTS_DIR", d)
        return d

    def test_missing_step1_req_id_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T0_FILES[0])
        n = _mutate_rows(
            d,
            [T0_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"step1_req_id": ""}),
        )
        assert n >= 1
        assert tier0_enforcement_gate.evaluate()["result"] == "BLOCKED"

    def test_unknown_tier0_req_id_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T0_FILES[0])
        # Rename in only the index file -> req appears in 3 of 4 surfaces.
        n = _mutate_rows(
            d,
            [T0_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"step1_req_id": "REQ-FAKE-UNKNOWN-001"}),
        )
        assert n >= 1
        assert tier0_enforcement_gate.evaluate()["result"] == "BLOCKED"

    def test_non_linked_literal_status_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T0_FILES[0])
        n = _mutate_rows(
            d,
            [T0_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"linkage_status": "PARTIAL_LINK"}),
        )
        assert n >= 1
        assert tier0_enforcement_gate.evaluate()["result"] == "BLOCKED"

    def test_non_empty_blockers_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T0_FILES[0])
        n = _mutate_rows(
            d,
            [T0_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"blockers": ["NEEDS_TEST_MAPPING"]}),
        )
        assert n >= 1
        assert tier0_enforcement_gate.evaluate()["result"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Tier 1 enforcement gate (4 anti-cheat cases).
# ---------------------------------------------------------------------------


class TestTier1EnforcementGateFailsClosed:
    def _setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        d = _copy_metadata(tmp_path, T1_FILES)
        monkeypatch.setattr(tier1_enforcement_gate, "ARTIFACTS_DIR", d)
        return d

    def test_missing_step1_req_id_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T1_FILES[0])
        _mutate_rows(
            d,
            T1_FILES,
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"step1_req_id": ""}),
        )
        assert tier1_enforcement_gate.evaluate()["result"] == "BLOCKED"

    def test_unknown_tier1_req_id_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T1_FILES[0])
        # Rename in only index surface -> seen count becomes 16 != 15.
        _mutate_rows(
            d,
            [T1_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"step1_req_id": "REQ-FAKE-UNKNOWN-T1-001"}),
        )
        assert tier1_enforcement_gate.evaluate()["result"] == "BLOCKED"

    def test_non_linked_literal_status_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T1_FILES[0])
        _mutate_rows(
            d,
            [T1_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"linkage_status": "PARTIAL_LINK"}),
        )
        assert tier1_enforcement_gate.evaluate()["result"] == "BLOCKED"

    def test_non_empty_blockers_blocks(self, tmp_path, monkeypatch):
        d = self._setup(tmp_path, monkeypatch)
        rid = _first_req_id(d, T1_FILES[0])
        _mutate_rows(
            d,
            [T1_FILES[0]],
            lambda r: r.get("step1_req_id") == rid,
            lambda r: r.update({"blockers": ["NEEDS_TEST_MAPPING"]}),
        )
        assert tier1_enforcement_gate.evaluate()["result"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Runtime-proof gate hardening helpers.
# ---------------------------------------------------------------------------


def _patch_runtime_t0(monkeypatch, metadata_dir: Path) -> None:
    monkeypatch.setattr(tier0_runtime_proof_gate, "ARTIFACTS_DIR", metadata_dir)
    # REPO_ROOT stays pointing at the real repo so non-corrupted refs resolve.


def _patch_runtime_t1(monkeypatch, metadata_dir: Path) -> None:
    monkeypatch.setattr(tier1_runtime_proof_gate, "ARTIFACTS_DIR", metadata_dir)


def _patch_runtime_t2(monkeypatch, metadata_dir: Path) -> None:
    monkeypatch.setattr(tier2_runtime_proof_gate, "ARTIFACTS_DIR", metadata_dir)


def _patch_runtime_t3(monkeypatch, metadata_dir: Path) -> None:
    monkeypatch.setattr(tier3_runtime_proof_gate, "ARTIFACTS_DIR", metadata_dir)


def _set_index_row_field(metadata_dir: Path, index_file: str, rid: str, field: str, value) -> None:
    p = metadata_dir / index_file
    data = _load(p)
    for row in data.get("rows", []):
        if row.get("step1_req_id") == rid:
            row[field] = value
    _save(p, data)


# ---------------------------------------------------------------------------
# Tier 0 runtime proof gate (5 anti-cheat cases).
# ---------------------------------------------------------------------------


class TestTier0RuntimeProofGateFailsClosed:
    def _setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str, dict]:
        d = _copy_metadata(tmp_path, T0_FILES)
        _patch_runtime_t0(monkeypatch, d)
        # Pick a row with non-empty artifact_refs and replay_refs.
        data = _load(d / T0_FILES[0])
        row = next(
            r
            for r in data["rows"]
            if r.get("artifact_refs")
            and any(rr.endswith("_run_1.json") for rr in (r.get("replay_refs") or []))
        )
        return d, row["step1_req_id"], dict(row)

    def test_missing_artifact_file_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        new_refs = list(row["artifact_refs"]) + [str(tmp_path / "_does_not_exist.json")]
        _set_index_row_field(d, T0_FILES[0], rid, "artifact_refs", new_refs)
        result = tier0_runtime_proof_gate.evaluate()
        assert result["result"] == "BLOCKED"

    def test_artifact_step1_req_id_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path,
            "_artifact_mismatch_id.json",
            step1_req_id="REQ-WRONG-ID-XYZ",
        )
        _set_index_row_field(d, T0_FILES[0], rid, "artifact_refs", [bad])
        assert tier0_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_efr_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path,
            "_artifact_mismatch_efr.json",
            step1_req_id=rid,
            expected_fail_reason="WRONG_EFR_VALUE",
        )
        _set_index_row_field(d, T0_FILES[0], rid, "artifact_refs", [bad])
        assert tier0_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_replay_pair_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        ghost = [
            str(tmp_path / "_ghost_run_1.json"),
            str(tmp_path / "_ghost_run_2.json"),
        ]
        _set_index_row_field(d, T0_FILES[0], rid, "replay_refs", ghost)
        assert tier0_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_replay_invariant_digest_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        run1 = tmp_path / "_replay_mismatch_run_1.json"
        run2 = tmp_path / "_replay_mismatch_run_2.json"
        run1.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("a")}),
            encoding="utf-8",
        )
        run2.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("b")}),
            encoding="utf-8",
        )
        _set_index_row_field(d, T0_FILES[0], rid, "replay_refs", [str(run1), str(run2)])
        assert tier0_runtime_proof_gate.evaluate()["result"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Tier 1 runtime proof gate (10 anti-cheat cases).
# ---------------------------------------------------------------------------


class TestTier1RuntimeProofGateFailsClosed:
    def _setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str, dict]:
        d = _copy_metadata(tmp_path, T1_FILES)
        _patch_runtime_t1(monkeypatch, d)
        data = _load(d / T1_FILES[0])
        row = next(
            r
            for r in data["rows"]
            if r.get("artifact_refs")
            and any(rr.endswith("_run_1.json") for rr in (r.get("replay_refs") or []))
            and r.get("negative_control_refs")
            and r.get("test_refs")
            and r.get("code_refs")
            and r.get("validator_refs")
            and r.get("otel_span_refs")
        )
        return d, row["step1_req_id"], dict(row)

    def test_missing_artifact_file_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["artifact_refs"]) + [str(tmp_path / "_no_artifact.json")]
        _set_index_row_field(d, T1_FILES[0], rid, "artifact_refs", bad)
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_step1_req_id_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path, "_t1_mismatch_id.json", step1_req_id="REQ-T1-WRONG-XYZ"
        )
        _set_index_row_field(d, T1_FILES[0], rid, "artifact_refs", [bad])
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_efr_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path,
            "_t1_mismatch_efr.json",
            step1_req_id=rid,
            expected_fail_reason="WRONG_T1_EFR",
        )
        _set_index_row_field(d, T1_FILES[0], rid, "artifact_refs", [bad])
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_replay_pair_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        ghost = [
            str(tmp_path / "_t1_ghost_run_1.json"),
            str(tmp_path / "_t1_ghost_run_2.json"),
        ]
        _set_index_row_field(d, T1_FILES[0], rid, "replay_refs", ghost)
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_replay_invariant_digest_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        run1 = tmp_path / "_t1_replay_mismatch_run_1.json"
        run2 = tmp_path / "_t1_replay_mismatch_run_2.json"
        run1.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("t1a")}),
            encoding="utf-8",
        )
        run2.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("t1b")}),
            encoding="utf-8",
        )
        _set_index_row_field(
            d, T1_FILES[0], rid, "replay_refs", [str(run1), str(run2)]
        )
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_negative_control_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["negative_control_refs"]) + [str(tmp_path / "_no_negctrl.json")]
        _set_index_row_field(d, T1_FILES[0], rid, "negative_control_refs", bad)
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_test_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["test_refs"]) + [str(tmp_path / "_no_test.py")]
        _set_index_row_field(d, T1_FILES[0], rid, "test_refs", bad)
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_code_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["code_refs"]) + [str(tmp_path / "_no_code.py")]
        _set_index_row_field(d, T1_FILES[0], rid, "code_refs", bad)
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_validator_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["validator_refs"]) + [str(tmp_path / "_no_validator.py")]
        _set_index_row_field(d, T1_FILES[0], rid, "validator_refs", bad)
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_otel_span_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        # Replace otel_span_refs with a single nonexistent path.
        _set_index_row_field(
            d, T1_FILES[0], rid, "otel_span_refs", [str(tmp_path / "_no_otel.py")]
        )
        assert tier1_runtime_proof_gate.evaluate()["result"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Tier 2 runtime proof gate (10 anti-cheat cases).
# ---------------------------------------------------------------------------


class TestTier2RuntimeProofGateFailsClosed:
    def _setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str, dict]:
        d = _copy_metadata(tmp_path, T2_FILES)
        _patch_runtime_t2(monkeypatch, d)
        data = _load(d / T2_FILES[0])
        row = next(
            r
            for r in data["rows"]
            if r.get("artifact_refs")
            and any(rr.endswith("_run_1.json") for rr in (r.get("replay_refs") or []))
            and r.get("negative_control_refs")
            and r.get("test_refs")
            and r.get("code_refs")
            and r.get("validator_refs")
            and r.get("otel_span_refs")
        )
        return d, row["step1_req_id"], dict(row)

    def test_missing_artifact_file_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["artifact_refs"]) + [str(tmp_path / "_no_t2_artifact.json")]
        _set_index_row_field(d, T2_FILES[0], rid, "artifact_refs", bad)
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_step1_req_id_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path, "_t2_mismatch_id.json", step1_req_id="REQ-T2-WRONG-XYZ"
        )
        _set_index_row_field(d, T2_FILES[0], rid, "artifact_refs", [bad])
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_efr_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path,
            "_t2_mismatch_efr.json",
            step1_req_id=rid,
            expected_fail_reason="WRONG_T2_EFR",
        )
        _set_index_row_field(d, T2_FILES[0], rid, "artifact_refs", [bad])
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_replay_pair_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        ghost = [
            str(tmp_path / "_t2_ghost_run_1.json"),
            str(tmp_path / "_t2_ghost_run_2.json"),
        ]
        _set_index_row_field(d, T2_FILES[0], rid, "replay_refs", ghost)
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_replay_invariant_digest_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        run1 = tmp_path / "_t2_replay_mismatch_run_1.json"
        run2 = tmp_path / "_t2_replay_mismatch_run_2.json"
        run1.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("t2a")}),
            encoding="utf-8",
        )
        run2.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("t2b")}),
            encoding="utf-8",
        )
        _set_index_row_field(
            d, T2_FILES[0], rid, "replay_refs", [str(run1), str(run2)]
        )
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_negative_control_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["negative_control_refs"]) + [str(tmp_path / "_no_t2_negctrl.json")]
        _set_index_row_field(d, T2_FILES[0], rid, "negative_control_refs", bad)
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_test_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["test_refs"]) + [str(tmp_path / "_no_t2_test.py")]
        _set_index_row_field(d, T2_FILES[0], rid, "test_refs", bad)
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_code_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["code_refs"]) + [str(tmp_path / "_no_t2_code.py")]
        _set_index_row_field(d, T2_FILES[0], rid, "code_refs", bad)
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_validator_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["validator_refs"]) + [str(tmp_path / "_no_t2_validator.py")]
        _set_index_row_field(d, T2_FILES[0], rid, "validator_refs", bad)
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_otel_span_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        _set_index_row_field(
            d, T2_FILES[0], rid, "otel_span_refs", [str(tmp_path / "_no_t2_otel.py")]
        )
        assert tier2_runtime_proof_gate.evaluate()["result"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Tier 3 runtime-proof gate fail-closed cases.
# ---------------------------------------------------------------------------


class TestTier3RuntimeProofGateFailsClosed:
    def _setup(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str, dict]:
        d = _copy_metadata(tmp_path, T3_FILES)
        _patch_runtime_t3(monkeypatch, d)
        data = _load(d / T3_FILES[0])
        row = next(
            r
            for r in data["rows"]
            if r.get("artifact_refs")
            and r.get("replay_refs")
            and r.get("negative_control_refs")
            and r.get("test_refs")
            and r.get("code_refs")
            and r.get("validator_refs")
            and r.get("otel_span_refs")
        )
        return d, row["step1_req_id"], row

    def test_missing_artifact_file_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["artifact_refs"]) + [str(tmp_path / "_no_t3_artifact.json")]
        _set_index_row_field(d, T3_FILES[0], rid, "artifact_refs", bad)
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_step1_req_id_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path, "_t3_mismatch_id.json", step1_req_id="REQ-T3-WRONG-XYZ"
        )
        _set_index_row_field(d, T3_FILES[0], rid, "artifact_refs", [bad])
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_artifact_efr_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        bad = _write_artifact_stub(
            tmp_path,
            "_t3_efr_mismatch.json",
            step1_req_id=rid,
            expected_fail_reason="WRONG_T3_EFR",
        )
        _set_index_row_field(d, T3_FILES[0], rid, "artifact_refs", [bad])
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_replay_pair_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        ghost = [
            str(tmp_path / "_t3_ghost_run_1.json"),
            str(tmp_path / "_t3_ghost_run_2.json"),
        ]
        _set_index_row_field(d, T3_FILES[0], rid, "replay_refs", ghost)
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_replay_invariant_digest_mismatch_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        run1 = tmp_path / "_t3_drifted_run_1.json"
        run2 = tmp_path / "_t3_drifted_run_2.json"
        run1.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("t3a")}),
            encoding="utf-8",
        )
        run2.write_text(
            json.dumps({"step1_req_id": rid, "invariant_digest": _digest("t3b")}),
            encoding="utf-8",
        )
        _set_index_row_field(
            d, T3_FILES[0], rid, "replay_refs", [str(run1), str(run2)]
        )
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_negative_control_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["negative_control_refs"]) + [str(tmp_path / "_no_t3_negctrl.json")]
        _set_index_row_field(d, T3_FILES[0], rid, "negative_control_refs", bad)
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_test_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["test_refs"]) + [str(tmp_path / "_no_t3_test.py")]
        _set_index_row_field(d, T3_FILES[0], rid, "test_refs", bad)
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_code_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["code_refs"]) + [str(tmp_path / "_no_t3_code.py")]
        _set_index_row_field(d, T3_FILES[0], rid, "code_refs", bad)
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_validator_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, row = self._setup(tmp_path, monkeypatch)
        bad = list(row["validator_refs"]) + [str(tmp_path / "_no_t3_validator.py")]
        _set_index_row_field(d, T3_FILES[0], rid, "validator_refs", bad)
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"

    def test_missing_otel_span_ref_blocks(self, tmp_path, monkeypatch):
        d, rid, _row = self._setup(tmp_path, monkeypatch)
        _set_index_row_field(
            d, T3_FILES[0], rid, "otel_span_refs", [str(tmp_path / "_no_t3_otel.py")]
        )
        assert tier3_runtime_proof_gate.evaluate()["result"] == "BLOCKED"
