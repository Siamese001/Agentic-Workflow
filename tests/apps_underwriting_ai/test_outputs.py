"""Output renderer round-trip tests for apps_underwriting_ai."""

from __future__ import annotations

import json
from pathlib import Path

from apps_underwriting_ai.engines.underwriting_engine import UnderwritingEngine
from apps_underwriting_ai.outputs.decision_renderer import DecisionRenderer
from apps_underwriting_ai.outputs.enterprise_underwriting_renderer import (
    EnterpriseUnderwritingRenderer,
)
from apps_underwriting_ai.types.underwriting_types import UnderwritingRequest


def _result(rid: str = "out-1", n_docs: int = 2):
    request = UnderwritingRequest(
        request_id=rid,
        applicant_id="out-applicant",
        product_class="auto",
        documents=tuple({"kind": f"doc_{i}"} for i in range(n_docs)),
    )
    return UnderwritingEngine().run(request, trace_id=f"trace-{rid}")


# -- DecisionRenderer.to_json ------------------------------------------------


def test_to_json_returns_valid_json() -> None:
    result = _result()
    out = DecisionRenderer().to_json(result)
    parsed = json.loads(out)
    assert parsed["request_id"] == "out-1"
    assert parsed["decision"]["verdict"] in {
        "approve",
        "decline",
        "refer",
        "insufficient_evidence",
    }


def test_to_json_contains_decision_subkeys() -> None:
    result = _result()
    parsed = json.loads(DecisionRenderer().to_json(result))
    for k in ("verdict", "rationale", "evidence_refs", "feature_summary", "gate_violations"):
        assert k in parsed["decision"]


def test_to_json_contains_register_summary() -> None:
    result = _result()
    parsed = json.loads(DecisionRenderer().to_json(result))
    assert parsed["register"]["request_id"] == "out-1"
    assert parsed["register"]["record_count"] == 5


def test_to_json_preserves_trace_id() -> None:
    result = _result(rid="out-trace")
    parsed = json.loads(DecisionRenderer().to_json(result))
    assert parsed["trace_id"] == "trace-out-trace"


# -- DecisionRenderer.to_markdown -------------------------------------------


def test_to_markdown_contains_request_id() -> None:
    result = _result(rid="md-1")
    md = DecisionRenderer().to_markdown(result)
    assert "md-1" in md


def test_to_markdown_contains_verdict() -> None:
    result = _result()
    md = DecisionRenderer().to_markdown(result)
    assert result.decision.verdict.value in md


def test_to_markdown_lists_evidence_refs() -> None:
    result = _result()
    md = DecisionRenderer().to_markdown(result)
    for ref in result.decision.evidence_refs:
        assert ref in md


def test_to_markdown_lists_feature_keys() -> None:
    result = _result()
    md = DecisionRenderer().to_markdown(result)
    for key in result.features.feature_vector:
        assert key in md


def test_to_markdown_handles_empty_evidence() -> None:
    """When evidence_refs is empty, markdown shows '_none_' placeholder."""
    from apps_underwriting_ai.types.underwriting_types import (
        DecisionPacket,
        DecisionVerdict,
        EvidenceRegister,
        ReconciliationResult,
        RiskFeatures,
        UnderwritingResult,
    )
    decision = DecisionPacket(
        request_id="empty",
        verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE,
    )
    result = UnderwritingResult(
        request_id="empty",
        decision=decision,
        register=EvidenceRegister(request_id="empty"),
        features=RiskFeatures(),
        reconciliation=ReconciliationResult(),
    )
    md = DecisionRenderer().to_markdown(result)
    assert "_none_" in md


# -- EnterpriseUnderwritingRenderer.render_to_disk --------------------------


def test_enterprise_renderer_emits_both_files(tmp_path: Path) -> None:
    result = _result(rid="ent-1")
    renderer = EnterpriseUnderwritingRenderer(artifact_dir=tmp_path)
    paths = renderer.render_to_disk(result)
    assert "decision_md" in paths
    assert "run_summary_json" in paths
    assert Path(paths["decision_md"]).exists()
    assert Path(paths["run_summary_json"]).exists()


def test_enterprise_renderer_files_nonempty(tmp_path: Path) -> None:
    result = _result(rid="ent-2")
    paths = EnterpriseUnderwritingRenderer(artifact_dir=tmp_path).render_to_disk(result)
    assert Path(paths["decision_md"]).stat().st_size > 0
    assert Path(paths["run_summary_json"]).stat().st_size > 0


def test_enterprise_renderer_run_summary_is_valid_json(tmp_path: Path) -> None:
    result = _result(rid="ent-3")
    paths = EnterpriseUnderwritingRenderer(artifact_dir=tmp_path).render_to_disk(result)
    parsed = json.loads(Path(paths["run_summary_json"]).read_text(encoding="utf-8"))
    assert parsed["request_id"] == "ent-3"
    assert parsed["verdict"] == result.decision.verdict.value
    assert parsed["evidence_count"] == 5
    assert parsed["reconciled_count"] == 2


def test_enterprise_renderer_creates_dir_if_missing(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "subdir"
    assert not target.exists()
    result = _result(rid="ent-4")
    EnterpriseUnderwritingRenderer(artifact_dir=target).render_to_disk(result)
    assert target.exists()
