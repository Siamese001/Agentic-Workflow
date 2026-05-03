"""tests/_apps_contract/test_rag_dims_active.py

Phase 5.2 — RAG dimension activation tests.

Plan: ``apps-core-contract-rectification-a8f3c2`` Phase 5.2

These tests verify the invariants that must hold when C0 retrieval is wired
and RAG dims are promoted from tracked-only to active:

1. While deferred (C0 not wired):
   - All 5 grounded apps have the 3 RAG dims declared in their rubric
   - All 3 RAG dims appear in ``intentional_failopen_dims``
   - weight == 0.0 and fail_closed_if_unknown == False (deferred state)

2. Gate behaviour:
   - ``check_grounded_rag_active`` reports INFO (not ERROR) for all deferred dims
   - Gate exits 0 in advisory mode regardless of deferred state

3. Activation invariants (enforced once C0 wired — future):
   - When a dim is removed from ``intentional_failopen_dims``, gate reports ERROR
     if weight == 0.0 or fail_closed_if_unknown == False
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.check_grounded_rag_active import (  # noqa: E402
    _GROUNDED_APPS,
    _RAG_DIMS,
    _intentional_failopen_dims_for_app,
    _rubric_dims_by_id,
    check_app,
    run,
)

_GROUNDED_APPS_SORTED = sorted(_GROUNDED_APPS)


# ---------------------------------------------------------------------------
# 1. Structural — all 5 grounded apps have RAG dims declared in rubric
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("app_id", _GROUNDED_APPS_SORTED)
def test_rag_dims_declared_in_rubric(app_id: str) -> None:
    dims = _rubric_dims_by_id(app_id)
    for rag_dim in _RAG_DIMS:
        assert rag_dim in dims, (
            f"{app_id}: RAG dim '{rag_dim}' not found in eval_rubrics.yaml. "
            "Add it with weight=0.0 and fail_closed_if_unknown=false until C0 wires."
        )


@pytest.mark.parametrize("app_id", _GROUNDED_APPS_SORTED)
def test_rag_dims_in_intentional_failopen_while_deferred(app_id: str) -> None:
    failopen = _intentional_failopen_dims_for_app(app_id)
    for rag_dim in _RAG_DIMS:
        assert rag_dim in failopen, (
            f"{app_id}: RAG dim '{rag_dim}' not in intentional_failopen_dims. "
            "Either add it (C0 not wired) or activate it (weight>0, fail_closed=true)."
        )


@pytest.mark.parametrize("app_id", _GROUNDED_APPS_SORTED)
def test_rag_dims_weight_zero_while_deferred(app_id: str) -> None:
    dims = _rubric_dims_by_id(app_id)
    for rag_dim in _RAG_DIMS:
        dim = dims.get(rag_dim, {})
        weight = float(dim.get("weight", 0.0))
        assert weight == 0.0, (
            f"{app_id}: RAG dim '{rag_dim}' weight={weight} but still in "
            "intentional_failopen_dims. Activate it: remove from failopen + set weight>0."
        )


@pytest.mark.parametrize("app_id", _GROUNDED_APPS_SORTED)
def test_rag_dims_fail_open_while_deferred(app_id: str) -> None:
    dims = _rubric_dims_by_id(app_id)
    for rag_dim in _RAG_DIMS:
        dim = dims.get(rag_dim, {})
        fail_closed = bool(dim.get("fail_closed_if_unknown", False))
        assert not fail_closed, (
            f"{app_id}: RAG dim '{rag_dim}' fail_closed_if_unknown=true but still in "
            "intentional_failopen_dims. Activate consistently: remove from failopen too."
        )


# ---------------------------------------------------------------------------
# 2. Gate behaviour — advisory mode
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("app_id", _GROUNDED_APPS_SORTED)
def test_gate_reports_only_info_for_deferred_apps(app_id: str) -> None:
    result = check_app(app_id)
    errors = result.errors
    assert not errors, (
        f"{app_id}: gate reported ERROR findings for deferred RAG dims: "
        + "; ".join(f.message for f in errors)
    )


def test_gate_run_all_apps_exits_clean() -> None:
    results = run()
    total_errors = sum(len(r.errors) for r in results)
    assert total_errors == 0, (
        f"check_grounded_rag_active reported {total_errors} ERROR(s) for deferred state"
    )


def test_gate_reports_info_for_all_rag_dims() -> None:
    results = run()
    info_check_ids = {f.check_id for r in results for f in r.infos}
    assert "RAG_DIM_DEFERRED" in info_check_ids, (
        "Expected RAG_DIM_DEFERRED INFO findings for all deferred dims — none found."
    )


# ---------------------------------------------------------------------------
# 3. Activation invariants — gate catches partially-activated dims
# ---------------------------------------------------------------------------


def test_gate_errors_on_dim_removed_from_failopen_but_weight_still_zero(
    tmp_path: Path,
) -> None:
    """Simulate a rubric dim removed from intentional_failopen_dims but weight still 0."""
    import importlib

    from ops_scripts.ci.check_grounded_rag_active import (
        _rubric_dims_by_id as _orig_rubric,
        _intentional_failopen_dims_for_app as _orig_failopen,
    )
    import ops_scripts.ci.check_grounded_rag_active as gate_mod

    # Patch: context_recall removed from failopen but weight still 0
    original_rubric = gate_mod._rubric_dims_by_id
    original_failopen = gate_mod._intentional_failopen_dims_for_app

    def _mock_rubric(app_id: str) -> dict:
        dims = original_rubric(app_id)
        if app_id == "apps_qna" and "context_recall" in dims:
            dims = dict(dims)
            dims["context_recall"] = dict(dims["context_recall"])
            dims["context_recall"]["weight"] = 0.0
        return dims

    def _mock_failopen(app_id: str) -> frozenset:
        orig = original_failopen(app_id)
        if app_id == "apps_qna":
            return orig - {"context_recall"}
        return orig

    gate_mod._rubric_dims_by_id = _mock_rubric  # type: ignore[assignment]
    gate_mod._intentional_failopen_dims_for_app = _mock_failopen  # type: ignore[assignment]
    try:
        result = gate_mod.check_app("apps_qna")
        error_ids = [f.check_id for f in result.errors]
        assert "RAG_DIM_WEIGHT_ZERO" in error_ids, (
            "Expected RAG_DIM_WEIGHT_ZERO ERROR when dim removed from failopen but weight=0"
        )
    finally:
        gate_mod._rubric_dims_by_id = original_rubric
        gate_mod._intentional_failopen_dims_for_app = original_failopen
