"""Wave 2 unit tests — req_compiler binding loader and PASS/PARTIAL upgrade.

Covers:
- ``load_bindings`` happy path + missing file + malformed schema
- ``Binding.matches`` for each match key (req_id, source_doc, section, line range)
- ``_link_evidence`` upgrades to PASS when coverage='full' AND glob resolves
- ``_link_evidence`` falls back to PARTIAL when coverage='full' AND glob does NOT resolve
- ``_link_evidence`` flips coverage='partial' bindings to PARTIAL with binding-derived
  actual_* fields (NOT the legacy keyword heuristic)
- A binding with NO match keys is rejected (would otherwise silently bind everything)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.proof.req_compiler import (
    Binding,
    Requirement,
    _link_evidence,
    load_bindings,
    STATUS_PARTIAL,
    STATUS_PASS,
    STATUS_UNVERIFIED,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_req(**overrides) -> Requirement:
    base = dict(
        req_id="REQ-E2E-99_4-000087-deadbeef",
        source_doc="docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance/99.4_E2E_OTEL_Trace_and_Span_Tree_Proof.md",
        source_section="",
        requirement_text="Parent span IDs must form a valid tree",
        owning_layer="E2E",
        line_no=87,
    )
    base.update(overrides)
    return Requirement(**base)


# ---------------------------------------------------------------------------
# load_bindings
# ---------------------------------------------------------------------------


def test_load_bindings_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_bindings(tmp_path / "no_such_file.json") == []


def test_load_bindings_happy_path(tmp_path: Path) -> None:
    p = tmp_path / "b.json"
    p.write_text(
        json.dumps(
            {
                "bindings": [
                    {
                        "binding_id": "b1",
                        "rationale": "test",
                        "req_id_pattern": "REQ-E2E-*",
                        "validator": "validate_replay",
                        "coverage": "full",
                    },
                ],
            },
        ),
        encoding="utf-8",
    )
    bindings = load_bindings(p)
    assert len(bindings) == 1
    assert bindings[0].binding_id == "b1"
    assert bindings[0].coverage == "full"
    assert bindings[0].req_id_pattern == "REQ-E2E-*"


def test_load_bindings_invalid_coverage_raises(tmp_path: Path) -> None:
    p = tmp_path / "b.json"
    p.write_text(
        json.dumps({"bindings": [{"req_id_pattern": "*", "coverage": "yolo"}]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="coverage"):
        load_bindings(p)


def test_load_bindings_missing_top_level_key_raises(tmp_path: Path) -> None:
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"not_bindings": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="bindings"):
        load_bindings(p)


# ---------------------------------------------------------------------------
# Binding.matches
# ---------------------------------------------------------------------------


def test_match_by_req_id_pattern() -> None:
    b = Binding(binding_id="b", rationale="", req_id_pattern="REQ-E2E-*")
    assert b.matches(_make_req())
    assert not b.matches(_make_req(req_id="REQ-L5G-99_4-000001-cafe"))


def test_match_by_source_doc_pattern() -> None:
    b = Binding(
        binding_id="b",
        rationale="",
        source_doc_pattern="*99.4_E2E_OTEL_Trace*",
    )
    assert b.matches(_make_req())
    assert not b.matches(_make_req(source_doc="docs/reference/foo.md"))


def test_match_by_line_range_inclusive() -> None:
    b = Binding(binding_id="b", rationale="", line_no_min=80, line_no_max=88)
    assert b.matches(_make_req(line_no=80))
    assert b.matches(_make_req(line_no=88))
    assert b.matches(_make_req(line_no=85))
    assert not b.matches(_make_req(line_no=79))
    assert not b.matches(_make_req(line_no=89))


def test_match_combined_logical_and() -> None:
    b = Binding(
        binding_id="b",
        rationale="",
        source_doc_pattern="*99.4*",
        line_no_min=80,
        line_no_max=88,
    )
    assert b.matches(_make_req(line_no=85))
    # Right doc, wrong line:
    assert not b.matches(_make_req(line_no=200))
    # Wrong doc, right line:
    assert not b.matches(_make_req(source_doc="x.md", line_no=85))


def test_match_with_no_keys_returns_false() -> None:
    """A binding with zero match keys must NOT silently bind everything."""
    b = Binding(binding_id="empty", rationale="")
    assert not b.matches(_make_req())


# ---------------------------------------------------------------------------
# _link_evidence — full coverage flips to PASS
# ---------------------------------------------------------------------------


def test_full_coverage_no_glob_promotes_to_pass(tmp_path: Path) -> None:
    """No runtime_artifact_glob declared = accepted on faith (validator/test
    are pinned by the binding itself)."""
    req = _make_req()
    b = Binding(
        binding_id="b",
        rationale="x",
        req_id_pattern="REQ-E2E-*",
        validator="validate_trace_tree",
        coverage="full",
    )
    _link_evidence(req, repo_root=tmp_path, bindings=[b])
    assert req.status == STATUS_PASS
    assert req.actual_validator == "validate_trace_tree"
    assert req.gap_reason == ""


def test_full_coverage_resolved_glob_promotes_to_pass(tmp_path: Path) -> None:
    """coverage=full + runtime_artifact_glob that resolves on disk -> PASS."""
    artifact_dir = tmp_path / "artifacts" / "traces"
    artifact_dir.mkdir(parents=True)
    artifact_path = artifact_dir / "apps_underwriting_ai_trace.json"
    artifact_path.write_text("[]", encoding="utf-8")  # non-empty

    req = _make_req()
    b = Binding(
        binding_id="b",
        rationale="x",
        req_id_pattern="REQ-E2E-*",
        validator="validate_trace_tree",
        runtime_artifact_glob="artifacts/traces/*_trace.json",
        coverage="full",
    )
    _link_evidence(req, repo_root=tmp_path, bindings=[b])
    assert req.status == STATUS_PASS
    assert req.actual_runtime_artifact == "artifacts/traces/apps_underwriting_ai_trace.json"


def test_full_coverage_unresolved_glob_falls_back_to_partial(tmp_path: Path) -> None:
    """coverage=full BUT runtime_artifact_glob does NOT resolve -> PARTIAL,
    with explicit gap_reason naming the binding."""
    req = _make_req()
    b = Binding(
        binding_id="trace_full",
        rationale="x",
        req_id_pattern="REQ-E2E-*",
        validator="validate_trace_tree",
        runtime_artifact_glob="artifacts/does_not_exist/*.json",
        coverage="full",
    )
    _link_evidence(req, repo_root=tmp_path, bindings=[b])
    assert req.status == STATUS_PARTIAL
    assert "trace_full" in req.gap_reason
    assert "did not resolve" in req.gap_reason


def test_partial_coverage_uses_binding_actuals_not_keyword_heuristic(
    tmp_path: Path,
) -> None:
    """coverage=partial means PARTIAL but with binding-derived actual_*
    fields (more honest than the legacy keyword heuristic)."""
    req = _make_req(requirement_text="Some requirement with no obvious keywords")
    b = Binding(
        binding_id="b_partial",
        rationale="span attrs not yet covered",
        req_id_pattern="REQ-E2E-*",
        validator="validate_trace_tree (structural only)",
        coverage="partial",
    )
    _link_evidence(req, repo_root=tmp_path, bindings=[b])
    assert req.status == STATUS_PARTIAL
    assert "b_partial" in req.gap_reason
    assert "span attrs" in req.gap_reason
    assert req.actual_validator == "validate_trace_tree (structural only)"


def test_no_binding_no_keyword_match_falls_through_to_unverified(
    tmp_path: Path,
) -> None:
    req = _make_req(
        requirement_text="bareword nothing here",  # no trigger keywords
    )
    _link_evidence(req, repo_root=tmp_path, bindings=[])
    assert req.status == STATUS_UNVERIFIED


def test_first_match_wins_ordering(tmp_path: Path) -> None:
    """Bindings checked in declaration order; first match wins."""
    req = _make_req()
    narrow = Binding(
        binding_id="narrow",
        rationale="r",
        req_id_pattern="REQ-E2E-99_4-*",
        validator="V_NARROW",
        coverage="full",
    )
    broad = Binding(
        binding_id="broad",
        rationale="r",
        req_id_pattern="REQ-*",
        validator="V_BROAD",
        coverage="full",
    )
    _link_evidence(req, repo_root=tmp_path, bindings=[narrow, broad])
    assert req.actual_validator == "V_NARROW"
    assert req.status == STATUS_PASS
