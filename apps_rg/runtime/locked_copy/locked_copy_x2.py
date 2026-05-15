"""Deterministic X2 gates for locked-copy proof (no LLM / provider)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.locked_copy.locked_copy_manifest import build_locked_sections, load_base_resume

FORBIDDEN_PROVIDER_ARTIFACTS = (
    "provider_request.json",
    "provider_response.json",
    "x1d_llm_judge_outputs.json",
)


@dataclass
class X2GateResult:
    gate_id: str
    gate_type: str
    pass_: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def _add(
    gates: list[X2GateResult],
    gate_id: str,
    passed: bool,
    observed: Any,
    *,
    threshold: Any = True,
    failure: str | None = None,
    evidence_ref: str = "",
) -> None:
    gates.append(
        X2GateResult(
            gate_id=gate_id,
            gate_type="deterministic",
            pass_=passed,
            observed_value=observed,
            threshold=threshold,
            failure_reason=failure,
            evidence_ref=evidence_ref,
        )
    )


def _section_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(s["section_id"]): s for s in manifest.get("sections") or []}


def run_locked_copy_x2_gates(
    *,
    manifest: dict[str, Any],
    artifact_dir: Path,
    repo_root: Path,
) -> list[X2GateResult]:
    gates: list[X2GateResult] = []
    sections = _section_map(manifest)
    base, _, _ = load_base_resume(repo_root)
    expected = {s.section_id: s for s in build_locked_sections(base)}

    _add(
        gates,
        "x2_locked_copy_source_present",
        bool(manifest.get("base_resume_json_ref")) and bool(sections),
        observed={"base_ref": manifest.get("base_resume_json_ref"), "section_count": len(sections)},
        evidence_ref=str(artifact_dir / "locked_copy_manifest.json"),
    )

    all_byte_match = all(bool(s.get("byte_for_byte_match")) for s in sections.values())
    _add(
        gates,
        "x2_locked_copy_byte_for_byte_match",
        all_byte_match,
        observed=all_byte_match,
        failure=None if all_byte_match else "One or more sections lack byte_for_byte_match",
    )

    all_hash_match = all(
        s.get("source_hash") == s.get("copied_hash") for s in sections.values()
    )
    _add(
        gates,
        "x2_locked_copy_hash_match",
        all_hash_match,
        observed=all_hash_match,
        failure=None if all_hash_match else "source_hash != copied_hash for one or more sections",
    )

    no_provider_artifacts = not any((artifact_dir / name).is_file() for name in FORBIDDEN_PROVIDER_ARTIFACTS)
    _add(
        gates,
        "x2_locked_copy_no_llm_provider",
        no_provider_artifacts and not manifest.get("provider_calls_made"),
        observed={
            "provider_calls_made": manifest.get("provider_calls_made"),
            "forbidden_artifacts_present": [
                n for n in FORBIDDEN_PROVIDER_ARTIFACTS if (artifact_dir / n).is_file()
            ],
        },
        failure=None if no_provider_artifacts else "Provider artifact present in locked_copy dir",
    )

    rewrite_false = all(s.get("rewrite_allowed") is False for s in sections.values())
    _add(
        gates,
        "x2_locked_copy_rewrite_allowed_false",
        rewrite_false and manifest.get("rewrite_allowed") is False,
        observed=rewrite_false,
    )

    def _preserve_gate(gate_id: str, section_id: str) -> None:
        sec = sections.get(section_id)
        exp = expected.get(section_id)
        ok = bool(sec) and exp is not None and sec.get("copied_text") == exp.copied_text
        _add(
            gates,
            gate_id,
            ok,
            observed=sec.get("copied_text")[:80] if sec else None,
            failure=None if ok else f"{section_id} copied_text does not match canonical base JSON",
            evidence_ref=section_id,
        )

    _preserve_gate("x2_company_names_preserved", "company_names")
    _preserve_gate("x2_titles_preserved", "titles")
    _preserve_gate("x2_locations_preserved", "locations")
    _preserve_gate("x2_dates_preserved", "dates")
    _preserve_gate("x2_education_preserved", "education")
    _preserve_gate("x2_certifications_preserved", "certifications")
    _preserve_gate("x2_insurtech_preserved", "insurtech")
    _preserve_gate("x2_ey_preserved", "ey")
    _preserve_gate("x2_early_career_preserved", "early_career")

    return gates


def write_x2_gate_outputs(path: Path, gates: list[X2GateResult]) -> dict[str, Any]:
    failed = [g.gate_id for g in gates if not g.pass_]
    payload = {
        "gates": [g.to_dict() for g in gates],
        "failed_gates": failed,
        "x2_passed": sum(1 for g in gates if g.pass_),
        "x2_failed": len(failed),
        "total_x2_gates": len(gates),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
