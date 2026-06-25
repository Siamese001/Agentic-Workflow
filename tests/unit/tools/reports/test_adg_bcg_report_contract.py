from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]

BCG_REQUIRED_REPORTS = [
    "tools/reports/adg_burndown_report.py",
    "tools/reports/exhaustive_adg_ci_report.py",
    "tools/adg/integration/enforcement_report.py",
    "tools/reports/adg_dead_code_report.py",
    "tools/reports/adg_review_template.py",
    "tools/reports/adg_cleanup_queue_and_p2_blocker_trace.py",
    "tools/reports/adg_bcg_executive_synthesis.py",
    "tools/reports/adg_burndown_canvas.py",
]


def test_human_facing_adg_reports_use_bcg_adapter_or_persist_findings() -> None:
    missing: list[str] = []
    for rel in BCG_REQUIRED_REPORTS:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        has_adapter_import = "adg_bcg_adapter" in text or "build_burndown_bcg_findings" in text
        has_bcg_surface = "bcg_findings" in text or "build_report_bcg_findings" in text or "build_bcg_brief" in text
        has_exemption = "bcg_adapter_exempt_reason" in text
        if not ((has_adapter_import and has_bcg_surface) or has_exemption):
            missing.append(rel)
    assert not missing, "ADG reports missing BCG adapter contract: " + ", ".join(missing)


def test_adg_bcg_adapter_exposes_report_findings_contract() -> None:
    text = (REPO_ROOT / "tools/reports/adg_bcg_adapter.py").read_text(encoding="utf-8")
    assert "def build_report_bcg_findings" in text
    assert "def render_report_bcg_findings_md" in text
    assert "def has_bcg_findings" in text
