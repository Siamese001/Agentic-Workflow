"""Read-only companion lane L2 context for multi-lane compile/support blobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.runtime_proof_layout import resolve_effective_lane_l2_path

COMPANION_LANES: tuple[tuple[str, str], ...] = (
    ("executive_summary", "executive_summary"),
    ("unify_narrative", "unify_narrative"),
    ("unify_bullets", "unify_bullets"),
    ("ibm_bullets", "ibm_bullets"),
    ("ibm_narrative", "ibm_narrative"),
)


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


_REPO_ROOT = _find_repo_root()


def load_companion_context() -> str:
    parts: list[str] = []
    for label, lane in COMPANION_LANES:
        path = resolve_effective_lane_l2_path(_REPO_ROOT, lane)
        if path is None or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        chunk_lines = [f"### {label}"]
        if label == "executive_summary":
            t = str(data.get("resume_display_text") or "").strip()
            if t:
                chunk_lines.append(t)
        elif label == "unify_narrative":
            t = str(data.get("narrative_sentence") or "").strip()
            if t:
                chunk_lines.append(t)
        elif label == "ibm_narrative":
            t = str(data.get("narrative_sentence") or "").strip()
            if t:
                chunk_lines.append(t)
        elif label in ("unify_bullets", "ibm_bullets"):
            for b in data.get("bullets") or []:
                chunk_lines.append(f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}")
        if len(chunk_lines) > 1:
            parts.append("\n".join(chunk_lines))
    return "\n\n".join(parts)


def build_resume_support_blob(bullet_rows: list[dict[str, Any]], companion_blob: str) -> str:
    chunks: list[str] = []
    for row in bullet_rows:
        chunks.append(str(row.get("claim_text", "")))
        for tech in row.get("technologies") or []:
            chunks.append(str(tech))
    chunks.append(companion_blob)
    return " ".join(chunks).lower()


def build_c0_proof_support_blob(bullet_rows: list[dict[str, Any]]) -> str:
    """C0 employment bullets + technologies only — excludes companion/U-tier for proof overlap."""
    chunks: list[str] = []
    for row in bullet_rows:
        chunks.append(str(row.get("claim_text", "")))
        for tech in row.get("technologies") or []:
            chunks.append(str(tech))
    return " ".join(chunks).lower()
