#!/usr/bin/env python3
"""post_write_cert_stage.py — auto-restage the certification review bundle.

Triggered on post_write_code. If the written file is a certification source
(compiler input, compiler script, verifier, runtime evidence under
`artifacts/certification/`, or canonical `certification/*.jsonl|*.json|schemas/`
inputs), re-run the staging script that populates
`certification/agentic_core/` and `certification/apps/`.

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
LOG = REPO_ROOT / "artifacts" / "cursor" / "cert_stage_hook.log"

# Paths that, when written, should trigger a restage. All repo-relative, forward slashes.
TRIGGER_PREFIXES = (
    "artifacts/certification/",
    "certification/evidence_assertions.jsonl",
    "certification/evidence_manifest.jsonl",
    "certification/apps_evidence_assertions.jsonl",
    "certification/apps_domain_evidence_assertions.jsonl",
    "certification/apps_negative_control_assertions.jsonl",
    "certification/requirements_source.json",
    "certification/apps_e2e_requirements_source.json",
    "certification/requirement_signoff_schema.json",
    "certification/schemas/",
    "scripts/compile_requirement_signoff.py",
    "scripts/compile_apps_e2e_signoff.py",
    "scripts/verify_final_requirement_signoff_bundle.py",
    "tools/certification/generate_100pct_runtime_proof.py",
    "tools/certification/generate_apps_100pct_runtime_proof.py",
)

# Exclude writes INTO the staged review bundle (prevents restage loop).
EXCLUDE_PREFIXES = (
    "certification/agentic_core/",
    "certification/apps/",
    "certification/README_REVIEW.md",
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
    # Strip drive/absolute prefix down to repo-relative.
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
        # Background, detached, non-blocking. Output discarded; stager is idempotent.
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
            creationflags=0x00000008 if sys.platform == "win32" else 0,  # DETACHED_PROCESS
        )
        _log(f"TRIGGER path={rel}")
    except (OSError, ValueError) as exc:
        _log(f"ERROR path={rel} err={exc}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
