"""Fixture builder for apps_rg U0 reflection harness tests.

Generates 5 fixture JSON files under ``tests/fixtures/apps_rg/`` from a single
canonical valid payload + 4 lawful mutations. Run as a module to regenerate.

Mutations:
    - invalid_missing_jd_hash:        /jd_payload/jd_hash blanked
    - invalid_unknown_generation_mode: /generation_mode set to bogus value
    - invalid_unmapped_field:         injected /unknown_top_level_key
    - invalid_missing_policy_ref:     /profile_manifest/prompt_registry_ref blanked

The valid fixture is the SSOT — any test that needs a "good" payload loads it.
The mutations are derived from the valid payload via lawful transforms; this
keeps the fixture set in sync without hand-editing 5 near-identical JSON files.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-rg-u0-reflection-harness-79d032.md (W3.P3.1)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "apps_rg"


# Deterministic SHA-256 placeholders. The U0 adapter doesn't recompute from
# source; it accepts any well-formed 64-char hex digest in /payload_digest,
# /jd_payload/jd_hash, /resume_payload/resume_hash, /profile_manifest/manifest_digest.
JD_HASH = "d23813412daefae270b46405ff2f2152879b69a5c1efd7db5816e819f78d7b16"
RESUME_HASH = "3ab879e02a8ac13b5248911206f24ced0cec4558dada4d81635b4b0735c1219a"
MANIFEST_DIGEST = "6a145ced49631ba8875cd082a05a912e5fe7601994e4a0708553a20c1b7a6a29"
PAYLOAD_DIGEST = "0" * 64  # placeholder — adapter computes its own canonical digest


VALID_PAYLOAD: dict[str, Any] = {
    "apps_rg_contract_version": "v1",
    "transport": {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "request_id": "req_01HZ7QZQZQZQZQZQZQZQZQZQZQ",
        "run_id": "run_01HZ7QZQZQZQZQZQZQZQZQZQZQ",
        "trace_id": "trace_01HZ7QZQZQZQZQZQZQZQZQZQZQ",
        "submitted_at": "2026-05-10T12:00:00+00:00",
        "tenant_id": "apps_rg",
    },
    "identity": {
        "actor_id": "user:amit.ayer",
        "actor_role": "candidate",
    },
    "replay": {
        "replay_key": "replay_01HZ7QZQZQZQZQZQZQZQZQZQZQ",
        "idempotency_key": "idem_01HZ7QZQZQZQZQZQZQZQZQZQZQ",
    },
    "jd_payload": {
        "jd_hash": JD_HASH,
        "jd_text": "Senior Director of AI Engineering at Acme Corp; lead applied research org; 12+ yrs.",
        "jd_ref": "ops_scripts/apps_rg/jd_acme_svp_ai.json",
        "jd_signals": {
            "seniority": "EXECUTIVE",
            "role_type": "leadership_ic_blend",
            "min_years_experience": 12,
        },
    },
    "resume_payload": {
        "resume_hash": RESUME_HASH,
        "source_resume_text": "Amit Ayer — Senior AI Engineering Leader. Education: ... Experience: ...",
        "source_resume_ref": "ops_scripts/apps_rg/AmitAyer_resume_master.json",
    },
    "target": {
        "company": "Acme Corp",
        "role": "Senior Director of AI Engineering",
        "level": "EXECUTIVE",
    },
    "generation_mode": "strategic_tailor",
    "capability_requirements": [
        "needs_strong_narrative",
        "needs_long_context",
    ],
    "profile_manifest": {
        "manifest_digest": MANIFEST_DIGEST,
        "profile_refs": {
            "rg_planning_profile": "sha256:placeholder_planning",
            "rg_thresholds": "sha256:placeholder_thresholds",
        },
        "prompt_registry_ref": "apps_rg/prompt_assembly/templates/registry.v1.yaml",
        "hitl_policy_ref": "apps_rg/config/hitl_trigger_policy.yaml",
        "l0_policy_ref": "apps_rg/config/l0_policy.yaml",
        "agent_spec_ref": "apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml",
        "thresholds_ref": "apps_rg/config/rg_thresholds.yaml",
    },
    "quality_thresholds": {
        "min_quality": 0.75,
        "min_ats": 70,
        "word_min": 400,
        "word_max": 1200,
    },
    "output_requirements": {
        "formats": ["json", "docx"],
        "provenance_required": True,
        "fact_checked_required": True,
    },
    "provenance_requirements": {
        "per_bullet_required": True,
        "source_quote_required": True,
    },
    "payload_digest": PAYLOAD_DIGEST,
}


def _build_invalid_missing_jd_hash() -> dict[str, Any]:
    """Mutation: blank out the required /jd_payload/jd_hash."""

    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["jd_payload"]["jd_hash"] = ""
    return payload


def _build_invalid_unknown_generation_mode() -> dict[str, Any]:
    """Mutation: set /generation_mode to a value outside the GenerationMode enum."""

    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["generation_mode"] = "wholly_invented_mode_xyz"
    return payload


def _build_invalid_unmapped_field() -> dict[str, Any]:
    """Mutation: inject a top-level field that has no field-map entry.

    Note: Pydantic with ``extra='forbid'`` will reject this BEFORE the
    reflection adapter walks pointers. The test asserts that any of:
        - AppsRgU0AdapterError (Pydantic validation)
        - SilentlyDroppedFieldError (reflection)
    is raised — both are valid fail-closed signals.
    """

    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["unknown_top_level_key"] = {"unmapped": "value"}
    return payload


def _build_invalid_missing_policy_ref() -> dict[str, Any]:
    """Mutation: blank out a required policy ref under /profile_manifest/."""

    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["profile_manifest"]["prompt_registry_ref"] = ""
    return payload


FIXTURES: dict[str, dict[str, Any]] = {
    "valid_ingress_contract.v1.json": VALID_PAYLOAD,
    "invalid_missing_jd_hash.json": _build_invalid_missing_jd_hash(),
    "invalid_unknown_generation_mode.json": _build_invalid_unknown_generation_mode(),
    "invalid_unmapped_field.json": _build_invalid_unmapped_field(),
    "invalid_missing_policy_ref.json": _build_invalid_missing_policy_ref(),
}


def write_fixtures() -> list[Path]:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in FIXTURES.items():
        path = FIXTURE_DIR / name
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.write("\n")
        written.append(path)
    return written


def load_fixture(name: str) -> dict[str, Any]:
    """Load a fixture by filename — used by tests."""

    path = FIXTURE_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    paths = write_fixtures()
    for p in paths:
        print(f"wrote {p.relative_to(REPO_ROOT)}")


__all__ = [
    "FIXTURES",
    "FIXTURE_DIR",
    "VALID_PAYLOAD",
    "load_fixture",
    "write_fixtures",
]
