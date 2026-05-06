"""Calibrate the W9 anti-overfit threshold against actual apps_rg output.

Loads the most recent generated_resume_*.json + the current
job_description.json, runs the detector exactly the way the orchestrator
hook does, and prints the score, signals, and flags. Used to set the
warning/escalate thresholds that won't trip on every run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from agentic_core.L5_safety.validators.anti_overfit_detector_validator import (  # noqa: E402
    OverfitProfile,
    SealedOutput,
    UserSample,
    detect,
)


def render_text(artifact: dict) -> str:
    chunks: list[str] = []
    if h := artifact.get("headline"):
        chunks.append(str(h))
    if s := artifact.get("summary"):
        chunks.append(str(s))
    for exp in artifact.get("experience", []) or []:
        if isinstance(exp, dict):
            chunks.append(f"{exp.get('company','')} - {exp.get('title','')}")
            for b in exp.get("bullets", []) or []:
                chunks.append(str(b))
    for sk in artifact.get("skills", []) or []:
        chunks.append(str(sk))
    return "\n".join(c for c in chunks if c)


def main() -> int:
    gen_files = sorted((REPO / "apps_rg/scripts").glob("generated_resume_*.json"))
    if not gen_files:
        print("no generated resume found")
        return 1
    gen = json.loads(gen_files[-1].read_text(encoding="utf-8"))
    print(f"resume_file={gen_files[-1].name}")
    # Reads the wizard-managed JD (apps_rg/scripts/_interactive_jd.json) written
    # by apps_rg's interactive wizard. Prior hand-authored job_description.json
    # was deleted 2026-05-06 (W1 plan apps-rg-vllm-followup-blocked-c4e8b2).
    jd_path = REPO / "apps_rg/scripts/_interactive_jd.json"
    if not jd_path.exists():
        print(
            f"[calibrate] ERROR: {jd_path} missing. Run apps_rg interactively "
            "first (TTY) or supply a JD JSON at this path before calibrating."
        )
        return 1
    jd = json.loads(jd_path.read_text(encoding="utf-8"))
    print(f"jd_title={jd['title']}, jd_company={jd['company']}")
    print()

    sealed_text = render_text(gen)
    print(f"sealed_text_chars={len(sealed_text)}")
    print(f"sealed_text_preview[:300]={sealed_text[:300]}")
    print()

    profile = OverfitProfile(
        mimicry_max=0.30,
        repeated_user_phrase_max=2,
        forced_warmth_threshold=0.10,
        fake_history_tolerance=0.0,
        persona_token_cap=600,
        certainty_calibration_required=True,
    )
    report = detect(
        sealed_output=SealedOutput(text=sealed_text, turn_index=0),
        user_samples=[UserSample(text=jd["description"], sample_ref="job_description")],
        profile=profile,
        spec_id="agt_rgresume000000000000001",
        spec_version="0.1.0",
    )
    print(f"aggregate_overfit_score={report.aggregate_overfit_score}")
    print(f"flags={report.flags}")
    print()
    print("=== signals ===")
    for k, v in (report.signals or {}).items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
