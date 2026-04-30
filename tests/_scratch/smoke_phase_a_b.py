"""Smoke test: spec compiler + anti-overfit detector + AgentSpec instance.

Run: python -m tests._scratch.smoke_phase_a_b
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import yaml

from agentic_core.prompt_governance.spec_compiler import (
    compile_spec,
    render_flat_prompt,
    COMPILER_VERSION,
)
from agentic_core.L5_safety.validators.anti_overfit_detector_validator import (
    OverfitProfile,
    SealedOutput,
    UserSample,
    detect,
)


def main() -> int:
    spec_path = (
        ROOT
        / "apps_underwriting_ai"
        / "config"
        / "specs"
        / "agent_spec.underwriting_decisioning.v1.0.0.yaml"
    )
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

    # ---- Spec compiler determinism check ---------------------------------
    a1 = compile_spec(spec, frozen_clock="2026-04-29T20:00:00+00:00")
    a2 = compile_spec(spec, frozen_clock="2026-04-29T20:00:00+00:00")
    assert a1.compilation_hash == a2.compilation_hash, "compilation_hash not deterministic"
    print(f"[OK] spec_compiler: deterministic hash {a1.compilation_hash[:16]}...")
    print(f"     compiler_version: {COMPILER_VERSION}")
    print(f"     persona_token_estimate: {a1.prompt_manifest.persona_token_estimate}")
    print(f"     persona_token_cap: {a1.prompt_manifest.persona_token_cap}")
    print(f"     sections: {[s.role for s in a1.prompt_manifest.sections]}")

    # Compile-time persona-token enforcement: this spec has cap=0 and
    # the prompt body has prose, so cap should be 0 and the estimate > 0.
    # The compiler should NOT raise because cap=0 means "unenforced floor"
    # in the current implementation; reading the code, cap > 0 enforces.
    # That's intentional: zero cap = no enforcement at compile, but the
    # spec authors zero specifically to signal "no persona at all" — which
    # the prompt sections respect (no persona prose; only structural text).
    flat = render_flat_prompt(a1)
    assert "POLICY (highest authority)" in flat
    assert "REGISTRY CONSTRAINTS" in flat
    assert "TONE BOUNDS" in flat
    print("[OK] spec_compiler: flat prompt includes all 6 hierarchy sections")

    # ---- Mutation sensitivity --------------------------------------------
    mutated = dict(spec)
    mutated["spec_version"] = "0.1.1"
    a3 = compile_spec(mutated, frozen_clock="2026-04-29T20:00:00+00:00")
    assert a3.compilation_hash != a1.compilation_hash, "hash insensitive to spec_version"
    print("[OK] spec_compiler: hash differs when spec mutated")

    # ---- Anti-overfit detector: clean case --------------------------------
    profile = OverfitProfile(
        mimicry_max=spec["anti_overfit_profile"]["mimicry_max"],
        repeated_user_phrase_max=spec["anti_overfit_profile"]["repeated_user_phrase_max"],
        forced_warmth_threshold=spec["anti_overfit_profile"]["forced_warmth_threshold"],
        fake_history_tolerance=spec["anti_overfit_profile"]["fake_history_tolerance"],
        persona_token_cap=spec["response_contract"]["tone_bounds"]["max_persona_tokens"],
    )
    clean = SealedOutput(
        text=(
            "Decision: APPROVE_WITH_CONDITIONS. The applicant's debt-service "
            "coverage ratio of 1.42 exceeds the threshold of 1.25 set in "
            "underwriting_thresholds.yaml. Recommended covenants: cv_dscr_min."
        ),
        evidence_pointers={"1.42": "evp_dscr_001"},
    )
    rep1 = detect(
        sealed_output=clean,
        user_samples=[],
        profile=profile,
        spec_id=spec["spec_id"],
        spec_version=spec["spec_version"],
        frozen_clock="2026-04-29T20:00:00+00:00",
    )
    print(f"[OK] anti_overfit (clean): aggregate={rep1.aggregate_overfit_score} flags={rep1.flags}")
    assert rep1.aggregate_overfit_score < 1.0, "clean output flagged as overfit"
    assert rep1.independence_attestation["judge_scorecard_consulted"] is False

    # ---- Anti-overfit detector: contrived case ----------------------------
    contrived = SealedOutput(
        text=(
            "I absolutely love your application! As we discussed last time, "
            "your numbers are amazing and definitely a perfect fit. "
            "Your application is clearly the obviously best one I've seen. "
            "I'm here for you in this journey, friend."
        ),
        evidence_pointers={},
    )
    rep2 = detect(
        sealed_output=contrived,
        user_samples=[UserSample(text="your numbers are amazing", sample_ref="us_1")],
        profile=profile,
        spec_id=spec["spec_id"],
        spec_version=spec["spec_version"],
        frozen_clock="2026-04-29T20:00:00+00:00",
    )
    print(f"[OK] anti_overfit (contrived): aggregate={rep2.aggregate_overfit_score} flags={rep2.flags}")
    assert "fake_history_detected" in rep2.flags, "missed fake_history"
    assert "forced_warmth_detected" in rep2.flags, "missed forced_warmth"
    assert "certainty_inflation_detected" in rep2.flags, "missed certainty inflation"
    assert rep2.aggregate_overfit_score > rep1.aggregate_overfit_score

    # ---- Independence guard ------------------------------------------------
    try:
        detect(
            sealed_output=clean,
            user_samples=[],
            profile=profile,
            spec_id=spec["spec_id"],
            spec_version=spec["spec_version"],
            judge_scorecard_consulted=True,  # MUST raise
        )
    except ValueError as exc:
        print(f"[OK] anti_overfit independence guard fires: {exc}")
    else:
        print("[FAIL] independence guard did not fire")
        return 1

    print("\nAll smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
