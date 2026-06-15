from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.judges import policy_backed_section_judges as judges


def test_policy_section_judges_builds_packet_filters_required_providers_and_invokes(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(judges, "normalize_section_id", lambda section_id: "executive_summary")
    monkeypatch.setattr(
        judges,
        "get_section_judge_policy",
        lambda section_id: SimpleNamespace(required_judge_providers=("openai_chatgpt",)),
    )

    def fake_packet(**kwargs):
        captured["packet_kwargs"] = kwargs
        return {"packet": True, "section_id": kwargs["section_id"]}

    def fake_write(path: Path, packet: dict[str, object]) -> str:
        captured["write"] = (path, packet)
        return "judge_packet.json"

    def fake_run(**kwargs):
        captured["run_kwargs"] = kwargs
        return ["judge-output"]

    monkeypatch.setattr(judges, "build_grade_only_judge_packet", fake_packet)
    monkeypatch.setattr(judges, "write_judge_packet", fake_write)
    monkeypatch.setattr(judges, "run_llm_judges", fake_run)

    out = judges.run_policy_section_judges(
        "Executive Summary",
        candidate_output={"headline_line": "Platform leader"},
        section_rubric="rubric",
        rubric_ref="rubric.md",
        claim_ledger=[{"claim_id": "c1"}],
        judge_keys=["anthropic_claude", "openai_chatgpt"],
        deterministic_gate_summary={"x2": {"pass": True}},
        judge_packet_path=tmp_path / "packet.json",
    )

    assert out == ["judge-output"]
    assert captured["packet_kwargs"] == {
        "section_id": "executive_summary",
        "candidate_output": {"headline_line": "Platform leader"},
        "section_rubric": "rubric",
        "rubric_ref": "rubric.md",
        "claim_ledger": [{"claim_id": "c1"}],
        "allowed_fact_packet": None,
        "targeting_context": None,
        "deterministic_gate_summary": {"x2": {"pass": True}},
        "proof_pool_metadata": None,
        "graph_binding_materiality_summary": None,
    }
    run_kwargs = captured["run_kwargs"]
    assert run_kwargs["judge_keys"] == ["openai_chatgpt"]
    assert run_kwargs["resume_display_text"] == "Platform leader"
    assert run_kwargs["judge_packet_ref"] == "judge_packet.json"
    assert run_kwargs["section_id"] == "executive_summary"
