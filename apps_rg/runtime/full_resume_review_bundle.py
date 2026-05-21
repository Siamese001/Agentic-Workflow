"""External review bundle — zip entire full-resume run folder for ChatGPT/Gemini upload."""
from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REVIEW_BUNDLE_FILENAME = "review_bundle.zip"
REVIEW_INDEX_FILENAME = "REVIEW_INDEX.md"

_SKIP_IN_ZIP = frozenset({REVIEW_BUNDLE_FILENAME})


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iter_files(run_root: Path) -> Iterable[Path]:
    for path in sorted(run_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in _SKIP_IN_ZIP:
            continue
        if path.resolve() == (run_root / REVIEW_BUNDLE_FILENAME).resolve():
            continue
        yield path


def write_review_index(run_root: Path) -> Path:
    """Human-oriented index for external LLM review."""
    lanes = run_root / "lanes"
    lane_names = []
    if lanes.is_dir():
        lane_names = sorted(
            d.name for d in lanes.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
    lines = [
        "# Full resume run — review bundle",
        "",
        f"Generated: {_utc_now()}",
        f"Run folder: `{run_root.name}`",
        "",
        "Upload **`review_bundle.zip`** (this folder's sibling) to ChatGPT or Gemini.",
        "",
        "## Start here",
        "",
        "- `spine_run_manifest.json` — **whole-DAG proof** (L0 route, R3R4 research delegation)",
        "- `route_contract.json` — canonical L0 route decision",
        "- `research_bridge_request.json` / `research_bridge_response.json` — apps_research hop (when delegated)",
        "- `research/delegated_briefing.txt` — briefing consumed by draft leg",
        "- `r4_run_manifest.json` — **draft-leg only** (R4 single-action spine; not whole-DAG authority)",
        "- `rollup/generated_lane_rollup.json` — per-lane X2/X3 summary",
        "- `RUN_LINKS.json` / `RUN_BUNDLE_INDEX.json` — artifact index",
        "",
        "## Per-lane outputs (flat)",
        "",
    ]
    for lane in lane_names:
        base = f"lanes/{lane}/"
        lines.append(f"### {lane}")
        lines.append(f"- `{base}l2_output.json` — generated content")
        lines.append(f"- `{base}x2_gate_outputs.json` — deterministic gates")
        lines.append(f"- `{base}x1d_llm_judge_outputs.json` — judge scores")
        lines.append(f"- `{base}x3_disposition.json` — lane disposition")
        lines.append("")
    lines.extend(
        [
            "## Product outputs (when assembly succeeds)",
            "",
            "- `outputs/generated_resume.json`",
            "- `outputs/resume.docx`",
            "",
        ]
    )
    out = run_root / REVIEW_INDEX_FILENAME
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def emit_full_resume_review_bundle(run_root: Path) -> Path:
    """Write ``REVIEW_INDEX.md`` and ``review_bundle.zip`` under ``run_root``."""
    root = Path(run_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    write_review_index(root)
    zip_path = root / REVIEW_BUNDLE_FILENAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in _iter_files(root):
            arcname = file_path.relative_to(root).as_posix()
            zf.write(file_path, arcname)
    return zip_path


__all__ = [
    "REVIEW_BUNDLE_FILENAME",
    "REVIEW_INDEX_FILENAME",
    "emit_full_resume_review_bundle",
    "write_review_index",
]
