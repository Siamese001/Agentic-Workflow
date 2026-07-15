from __future__ import annotations

from pathlib import Path

from apps_rg.evals.c03_ci_ratchet import build_ratchet_receipt


def _junit(path: Path, *, failing: bool = False, fragment: str = "augmented_skills_graph") -> None:
    failure = f'<failure message="{fragment}">{fragment}</failure>' if failing else ""
    failure_count = 1 if failing else 0
    path.write_text(
        f"<testsuites><testsuite tests=\"1\" failures=\"{failure_count}\" errors=\"0\" skipped=\"0\">"
        "<testcase classname=\"tests._apps_contract.test_apps_rg_c0_ownership_split."
        "TestAgenticCoreGraphSkillBoundary\" name=\"test_agentic_core_does_not_embed_"
        f"resume_graph_skill_authority_literals\">{failure}</testcase></testsuite></testsuites>",
        encoding="utf-8",
    )


def test_ratchet_accepts_only_exact_known_external_failure(tmp_path: Path) -> None:
    strict = tmp_path / "strict.xml"
    baseline = tmp_path / "baseline.xml"
    _junit(strict)
    _junit(baseline, failing=True)
    receipt = build_ratchet_receipt(
        strict_junit=strict,
        baseline_junit=baseline,
        source_commit="a" * 40,
        base_commit="b" * 40,
    )
    assert receipt["status"] == "PASS"
    assert (
        receipt["accepted_external_baseline_debt"]["status"]
        == "ACCEPTED_EXTERNAL_BASELINE_DEBT"
    )
    assert receipt["documentation_gates_included"] is False


def test_ratchet_accepts_baseline_improvement(tmp_path: Path) -> None:
    strict = tmp_path / "strict.xml"
    baseline = tmp_path / "baseline.xml"
    _junit(strict)
    _junit(baseline)
    receipt = build_ratchet_receipt(
        strict_junit=strict,
        baseline_junit=baseline,
        source_commit="a" * 40,
        base_commit="b" * 40,
    )
    assert receipt["status"] == "PASS"
    assert receipt["accepted_external_baseline_debt"]["status"] == "IMPROVED"


def test_ratchet_rejects_changed_signature(tmp_path: Path) -> None:
    strict = tmp_path / "strict.xml"
    baseline = tmp_path / "baseline.xml"
    _junit(strict)
    _junit(baseline, failing=True, fragment="different failure")
    receipt = build_ratchet_receipt(
        strict_junit=strict,
        baseline_junit=baseline,
        source_commit="a" * 40,
        base_commit="b" * 40,
    )
    assert receipt["status"] == "FAIL"
    assert "external_baseline_signature_changed" in receipt["failure_codes"]
