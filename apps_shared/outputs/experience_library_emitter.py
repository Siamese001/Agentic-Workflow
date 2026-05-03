"""Emit ExperienceLibraryEnvelope sidecar for apps_shared master_resume.

Plan: apps-cross-app-precursors-c94c71 Wave 3.1 (GAP-2).

Dual-write: the master_resume.json file is untouched; a sibling
master_resume.envelope.json (or master_resume_svp.envelope.json) is produced.

CLI:
    python -m apps_shared.outputs.experience_library_emitter
    python -m apps_shared.outputs.experience_library_emitter --svp
    python -m apps_shared.outputs.experience_library_emitter --source <path>
"""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from apps_shared.contracts.cross_app.experience_library import (
    ExperienceBullet,
    ExperienceLibraryEnvelope,
    ExperienceLibraryPayload,
)

_DEFAULT_DATA_DIR = Path("apps_shared/data")
_DEFAULT_SOURCE = _DEFAULT_DATA_DIR / "master_resume.json"
_SVP_SOURCE = _DEFAULT_DATA_DIR / "master_resume_svp.json"


def _bullets_from_role(role: dict, fallback_title: str = "") -> list[ExperienceBullet]:
    bullets: list[ExperienceBullet] = []
    role_title = role.get("title", fallback_title) or fallback_title
    for raw in role.get("bullet_pool", []) or []:
        if isinstance(raw, str):
            text = raw.strip()
            if text:
                bullets.append(
                    ExperienceBullet(text=text, role_title=role_title)
                )
        elif isinstance(raw, dict):
            text = (raw.get("text") or "").strip()
            if not text:
                continue
            bullets.append(
                ExperienceBullet(
                    label=(raw.get("label") or "").strip(),
                    text=text,
                    tags=list(raw.get("tags") or []),
                    role_title=role_title,
                )
            )
    return bullets


def build_payload(source_path: Path, *, variant: str) -> ExperienceLibraryPayload:
    data = json.loads(source_path.read_text(encoding="utf-8"))
    bullets: list[ExperienceBullet] = []
    for role in data.get("professional_experience", []) or []:
        bullets.extend(_bullets_from_role(role))

    # Competency areas — new OR legacy schema
    areas = data.get("engineering_and_platform_competencies")
    if not isinstance(areas, list):
        areas = data.get("strategic_and_technical_competencies") or []

    summary = data.get("executive_summary")
    summary = summary if isinstance(summary, str) and summary.strip() else None

    return ExperienceLibraryPayload(
        source_file=str(source_path).replace("\\", "/"),
        variant=variant,
        executive_summary=summary,
        competency_areas=list(areas),
        bullets=bullets,
    )


def emit(
    *,
    source_path: Path | None = None,
    prefer_svp: bool = False,
    trace_id: str | None = None,
    out_path: Path | None = None,
) -> Path:
    """Emit an ExperienceLibraryEnvelope sidecar. Returns the written path."""
    if source_path is None:
        source_path = (
            _SVP_SOURCE if (prefer_svp and _SVP_SOURCE.is_file()) else _DEFAULT_SOURCE
        )
    variant = "svp" if "svp" in source_path.stem else "default"
    payload = build_payload(source_path, variant=variant)
    trace_id = trace_id or uuid.uuid4().hex[:12]
    env = ExperienceLibraryEnvelope.emit(trace_id=trace_id, payload=payload)
    if out_path is None:
        out_path = env.default_sidecar_path(_DEFAULT_DATA_DIR)
    env.write_sidecar(out_path)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--svp", action="store_true", help="prefer the SVP variant")
    parser.add_argument("--trace-id", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    written = emit(
        source_path=args.source,
        prefer_svp=args.svp,
        trace_id=args.trace_id,
        out_path=args.out,
    )
    print(f"Wrote {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
