#!/usr/bin/env python3
"""W7 — optional live section spine smoke across modular W9 lanes.

Requires:
  - CHROMA_PERSIST_DIR (existing Chroma store)
  - Provider env for lane execution (e.g. vLLM endpoint) OR APPS_RG_LIVE_SMOKE_DRY_RUN=1

Without deps prints BLOCKED JSON and exits 2. Harness proof remains pytest E2E.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
W9_LANES = (
    "executive_summary",
    "headline",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

REPORT = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "live_section_spine_smoke_report.json"


def _blocked(reason: str, **extra: object) -> int:
    doc = {
        "status": "BLOCKED",
        "reason": reason,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
    print(json.dumps(doc, indent=2))
    return 2


def _deps_ok() -> tuple[bool, str]:
    chroma = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    if not chroma or not Path(chroma).is_dir():
        return False, "CHROMA_PERSIST_DIR missing or not a directory"
    if os.environ.get("APPS_RG_LIVE_SMOKE_DRY_RUN", "").strip().lower() in ("1", "true", "yes"):
        return True, "dry_run"
    if os.environ.get("APPS_RG_TEST_HARNESS", "").strip().lower() in ("1", "true", "yes"):
        return False, "APPS_RG_TEST_HARNESS=1 forbids live smoke (use harness E2E)"
    provider_hints = (
        "VLLM_BASE_URL",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "APPS_RG_LANE_PROVIDER",
    )
    if any(os.environ.get(k, "").strip() for k in provider_hints):
        return True, "provider_env"
    return False, "no provider env (set VLLM_BASE_URL or APPS_RG_LIVE_SMOKE_DRY_RUN=1)"


def main() -> int:
    ok, mode = _deps_ok()
    if not ok:
        return _blocked(mode, lanes=list(W9_LANES))

    out_root = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "live_section_smoke"
    out_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []

    for lane in W9_LANES:
        lane_dir = out_root / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        if mode == "dry_run":
            results.append({"lane": lane, "status": "SKIPPED_DRY_RUN", "artifact_dir": str(lane_dir)})
            continue
        cmd = [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            lane,
            "--artifact-dir",
            str(lane_dir),
        ]
        completed = subprocess.run(
            cmd,
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
            env=dict(os.environ),
        )
        results.append(
            {
                "lane": lane,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "returncode": completed.returncode,
                "artifact_dir": str(lane_dir),
                "stderr_tail": (completed.stderr or "")[-800:],
            }
        )

    failures = [r for r in results if r.get("status") == "FAIL"]
    doc = {
        "status": "PASS" if not failures else "FAIL",
        "proof_classification": "LIVE_SECTION_SMOKE" if mode != "dry_run" else "DRY_RUN_MANIFEST",
        "mode": mode,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "lane_count": len(W9_LANES),
        "failures": len(failures),
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": doc["status"], "report": str(REPORT.relative_to(REPO)).replace("\\", "/")}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
