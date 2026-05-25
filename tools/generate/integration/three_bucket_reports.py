"""Auto-emit three-bucket gap + authority audit reports after ADG enrichment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPORT_DIR = REPO_ROOT / "docs" / "reports" / "adg"
AUTHORITY_AUDIT_PATH = DEFAULT_REPORT_DIR / "before_after_adg_authority_counts.json"


def emit_three_bucket_reports(
    sqlite_path: Path,
    *,
    out_dir: Path | None = None,
    top_n: int = 10,
) -> dict[str, Path]:
    """Refresh gap report (JSON+MD) and authority audit JSON from *sqlite_path*.

    Returns paths written. Failures propagate to the caller (pipeline uses
    fail-soft skip ledger around this).
    """
    from tools.adg.audit_three_bucket_counts import run_authority_audit
    from tools.adg.three_bucket_gap_report import (
        DEFAULT_REPORT_DIR as _gap_default_dir,
        render_markdown,
        run_report,
    )

    sqlite_path = Path(sqlite_path).resolve()
    report_dir = Path(out_dir) if out_dir is not None else _gap_default_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = run_report(sqlite_path, top_n=top_n)

    gap_json = report_dir / "THREE_BUCKET_GAP_REPORT.json"
    gap_md = report_dir / "THREE_BUCKET_GAP_REPORT.md"
    gap_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    gap_md.write_text(render_markdown(report, require_runtime_proof=False), encoding="utf-8")

    audit_result = run_authority_audit(sqlite_path, out_path=AUTHORITY_AUDIT_PATH)

    from tools.adg.snapshot_fingerprint import print_audit_receipt

    print(
        f"[ADG] three-bucket reports: health={report['health_score_pct_triplet_attested']}% "
        f"runtime_present={report['runtime_view_present']} "
        f"proof_edges={audit_result.get('proof_count', 0)} "
        f"snapshot_sha256={report.get('source_snapshot_sha256', 'MISSING')}"
    )
    print(f"[ADG]   gap_json={gap_json.name} gap_md={gap_md.name} audit={AUTHORITY_AUDIT_PATH.name}")
    print_audit_receipt(report, prefix="THREE_BUCKET_AUDIT_RECEIPT")

    return {
        "gap_json": gap_json,
        "gap_md": gap_md,
        "authority_audit": AUTHORITY_AUDIT_PATH,
    }
