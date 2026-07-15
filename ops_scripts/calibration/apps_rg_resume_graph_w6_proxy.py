"""Emit the user-authorized, non-authoritative C0.3 W6 proxy baseline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.evals.c03_proxy_eval import emit_proxy_artifacts  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        default=REPO_ROOT
        / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml",
    )
    parser.add_argument(
        "--blocker",
        type=Path,
        default=REPO_ROOT / "docs/reports/apps_rg/c03_resume_graph_w6_blocker.json",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    args = parser.parse_args()
    report, summary = emit_proxy_artifacts(
        profile_path=args.profile.resolve(),
        blocker_path=args.blocker.resolve(),
        report_path=args.out.resolve(),
        summary_path=args.summary_out.resolve(),
    )
    print(
        json.dumps(
            {
                "status": "PROVISIONAL",
                "official_w6_status": "UNKNOWN",
                "report_record_digest": report["record_digest"],
                "summary_record_digest": summary["record_digest"],
                "protected_full_report_sha256": summary[
                    "protected_full_report_sha256"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
