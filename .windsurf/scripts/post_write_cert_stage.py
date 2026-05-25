#!/usr/bin/env python3
"""post_write_cert_stage.py — auto-restage the certification review bundle.

Triggered on post_write_code. If the written file is a certification source
(compiler input, compiler script, verifier, runtime evidence under
`artifacts/certification/`, or canonical `data/certification/*.jsonl|*.json`
and `config/certification/schemas/` inputs), re-run the staging script that
populates `artifacts/certification/review/agentic_core/` and
`artifacts/certification/review/apps/`.

Excludes writes inside the target directories themselves (avoid loop).
Fail-open: any error → exit 0.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STAGER = REPO_ROOT / "tools" / "certification" / "_stage_review_bundle.ps1"
LOG = REPO_ROOT / "artifacts" / "windsurf" / "cert_stage_hook.log"

# Paths that, when written, should trigger a restage. All repo-relative, forward slashes.
TRIGGER_PREFIXES = (
    "artifacts/certification/",
    "data/certification/evidence_assertions.jsonl",
    "data/certification/evidence_manifest.jsonl",
    "data/certification/apps_evidence_assertions.jsonl",
    "data/certification/apps_domain_evidence_assertions.jsonl",
    "data/certification/apps_negative_control_assertions.jsonl",
    "data/certification/requirements_source.json",
    "data/certification/apps_e2e_requirements_source.json",
    "data/certification/requirement_signoff_schema.json",
    "config/certification/schemas/",
    "tools/cert/compile_requirement_signoff.py",
    "tools/cert/compile_apps_e2e_signoff.py",
    "ops_scripts/ci/verify_final_requirement_signoff_bundle.py",
    "tools/certification/generate_100pct_runtime_proof.py",
    "tools/certification/generate_apps_100pct_runtime_proof.py",
)

# Exclude writes INTO the staged review bundle (prevents restage loop).
EXCLUDE_PREFIXES = (
    "artifacts/certification/review/agentic_core/",
    "artifacts/certification/review/apps/",
    "docs/certification/README_REVIEW.md",
)


def _log(msg: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except OSError:
        pass


def _normalize(raw: str) -> str:
    p = raw.replace("\\", "/")
    root = str(REPO_ROOT).replace("\\", "/") + "/"
    if p.lower().startswith(root.lower()):
        p = p[len(root):]
    return p.lstrip("/")


def _should_trigger(rel: str) -> bool:
    if any(rel.startswith(x) for x in EXCLUDE_PREFIXES):
        return False
    return any(rel.startswith(x) for x in TRIGGER_PREFIXES)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        return 0

    file_path = (payload.get("tool_info") or {}).get("file_path") or ""
    if not file_path:
        return 0

    rel = _normalize(file_path)
    if not _should_trigger(rel):
        return 0

    if not STAGER.exists():
        _log(f"SKIP stager-missing path={rel}")
        return 0

    try:
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(STAGER),
            ],
            cwd=str(REPO_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            creationflags=0x00000008 if sys.platform == "win32" else 0,
        )
        _log(f"TRIGGER path={rel}")
    except (OSError, ValueError) as exc:
        _log(f"ERROR path={rel} err={exc}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
