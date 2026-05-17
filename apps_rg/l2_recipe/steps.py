"""apps_rg L2 recipe step classes.

Steps are callable objects that accept a context dict and return a result dict.
They are composed into a pipeline by the L2 recipe resolver.

Step classes:
- GenerateResumeStep  — main LLM-driven resume generation (REQUIRES_PA=True)
- NarrativePassStep   — optional narrative polish pass (REQUIRES_PA=False)
- DocxExportStep      — DOCX export from structured JSON (REQUIRES_PA=False)
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from apps_rg.l2_recipe.resume_generation_contract import (
    MODE_DIAGNOSTIC,
    MODE_FULL,
    MODE_STUB_RECEIPT,
    normalize_resume_artifact_contract_mode,
)
from apps_rg.l2_recipe.resume_output_shape import (
    STRUCTURED_RESUME_OK,
    FAILED_PROVIDER,
    ResumeShapeReport,
    classify_resume_payload,
)
from apps_rg.l2_recipe.resume_artifact_gate import (
    merge_manifest_after_artifact_gate,
    verify_full_resume_artifact_bundle,
)
from apps_rg.l2_recipe.r4_generation_mode import (
    MODE_LEGACY_FULL_RESUME,
    MODE_MODULAR_SECTION_LANES,
    resolve_apps_rg_modular_lane_provider,
    resolve_apps_rg_r4_generation_mode,
)
from apps_rg.l2_recipe.sealed_resume_extract import generated_resume_from_sealed_l2

__all__ = [
    "GenerateResumeStep",
    "NarrativePassStep",
    "DocxExportStep",
    "ResumeArtifactGateStep",
    "BaseRecipeStep",
    "PAGuardError",
    "write_modular_generate_step_receipt",
]


class PAGuardError(RuntimeError):
    """Raised when a step requiring a PA artifact is called without one."""


def _write_stub_or_diagnostic_snapshot(
    context: dict[str, Any],
    gr: dict[str, Any] | None,
    shape_rep: ResumeShapeReport,
    mode: str,
) -> None:
    """Emit a bounded diagnostic JSON under artifact_dir/outputs (no DOCX)."""
    art = context.get("artifact_dir")
    if art is None or not str(art).strip():
        return
    base = Path(str(art))
    out_dir = base / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "schema_version": "apps_rg.stub_receipt_diagnostic.v1",
        "resume_artifact_contract_mode": mode,
        "classified_generation_status": shape_rep.generation_status,
        "full_resume_generated": False,
        "resume_shape": shape_rep.resume_shape,
        "had_generated_resume_dict": isinstance(gr, dict) and bool(gr),
    }
    (out_dir / "stub_receipt_diagnostic.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class BaseRecipeStep:
    """Base class for all apps_rg L2 recipe steps."""

    REQUIRES_PA: bool = False
    STEP_NAME: str = "base"

    def _check_pa_guard(self, context: dict[str, Any]) -> None:
        """Raise PAGuardError if REQUIRES_PA=True and no PA artifact in context."""
        if not self.REQUIRES_PA:
            return
        has_pa = (
            context.get("compiled_prompt_artifact") is not None
            or context.get("pa_artifact") is not None
            or context.get("prompt_artifact") is not None
            or context.get("governed_context") is not None
        )
        if not has_pa:
            raise PAGuardError(
                f"PA_GUARD_FAILED: Step '{self.STEP_NAME}' requires a compiled PA "
                "artifact in context ('compiled_prompt_artifact', 'pa_artifact', "
                "'prompt_artifact', or 'governed_context'). "
                "Compile the prompt with apps_rg.prompt_assembly.compiler first."
            )

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"{self.__class__.__name__}.__call__ not implemented")


def write_modular_generate_step_receipt(
    artifact_dir: Path,
    *,
    modular_result: Any,
) -> Path:
    """Persist modular ``GenerateResumeStep`` refs next to ``modular_r4/`` outputs (no providers)."""
    mr = modular_result
    payload: dict[str, Any] = {
        "schema_version": "apps_rg.modular_generate_step_receipt.v1",
        "apps_rg_r4_generation_mode": MODE_MODULAR_SECTION_LANES,
        "section_provider_calls_ref": getattr(mr, "section_provider_calls_ref", None),
        "section_output_refs": getattr(mr, "section_output_refs", None),
        "merge_receipt_ref": getattr(mr, "merge_receipt_ref", None),
        "rg_output_merge_receipt_ref": getattr(mr, "rg_output_merge_receipt_ref", None),
        "schema_validation_receipt_ref": getattr(mr, "schema_validation_receipt_ref", None),
        "final_schema_valid": getattr(mr, "final_schema_valid", None),
        "lanes_executed": getattr(mr, "lanes_executed", None),
        "lane_outputs_valid": getattr(mr, "lane_outputs_valid", None),
        "final_merge_attempted": getattr(mr, "final_merge_attempted", None),
        "decisive_status": getattr(mr, "decisive_status", None),
        "failure_reason": getattr(mr, "failure_reason", None),
        "recipe_lane_policy": (
            getattr(mr, "extras", {}).get("recipe_lane_policy")
            if isinstance(getattr(mr, "extras", None), dict)
            else None
        ),
    }
    out = Path(artifact_dir) / "modular_r4" / "generate_resume_step_receipt.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


class GenerateResumeStep(BaseRecipeStep):
    """Main resume generation step — calls the PA compiler + LLM.

    REQUIRES_PA=True: if no compiled prompt artifact is in the context,
    this step raises PA_GUARD_FAILED (which surfaces as PA_COMPILE_FAILED
    when the compiler raised before reaching this step).
    """

    REQUIRES_PA: bool = True
    STEP_NAME: str = "generate_resume"

    def _legacy_envelope_generation(self, context: dict[str, Any]) -> dict[str, Any]:
        """Monolithic full-résumé path (``run_apps_rg_l2_envelope``)."""
        from apps_rg.runtime.bindings.l2_envelope_adapter import run_apps_rg_l2_envelope

        pa = (
            context.get("compiled_prompt_artifact")
            or context.get("pa_artifact")
            or context.get("prompt_artifact")
        )
        route = context.get("route_contract") or context.get("route")
        validated = context.get("validated_request") or context
        pa_effective = pa
        if pa is not None and not str(getattr(pa, "request_id", "") or "").strip():
            from apps_rg.l2_recipe.pa_to_core_cpa import adapt_apps_rg_cpa_for_l2_envelope

            pa_effective = adapt_apps_rg_cpa_for_l2_envelope(pa, context)
        art_dir = str(context.get("artifact_dir") or "").strip() or None
        result = run_apps_rg_l2_envelope(
            pa_effective,
            route,
            validated,
            resume_artifact_contract_mode=context.get("resume_artifact_contract_mode"),
            artifact_dir=art_dir,
        )
        exec_st = str(getattr(result, "execution_status", "") or "").strip().lower()
        diff = getattr(result, "proposed_state_diff", None) or {}
        if isinstance(diff, dict) and diff.get("provider_resolution_error"):
            raise RuntimeError(
                f"BLOCKED_PROVIDER_LANE: {diff.get('decisive_reason', 'provider profile unresolved')}"
            )
        if isinstance(diff, dict) and diff.get("provider_authenticity_block"):
            raise RuntimeError(
                f"BLOCKED_STUB_PROVIDER: {diff.get('decisive_reason', 'stub provider forbidden')}"
            )
        gr = generated_resume_from_sealed_l2(result)
        shape_rep = classify_resume_payload(gr)
        mode_contract = normalize_resume_artifact_contract_mode(
            context.get("resume_artifact_contract_mode")
        )

        if mode_contract in (MODE_STUB_RECEIPT, MODE_DIAGNOSTIC):
            _write_stub_or_diagnostic_snapshot(context, gr, shape_rep, mode_contract)
            raise RuntimeError(
                "STUB_RECEIPT: diagnostic/stub contract mode — snapshot emitted under "
                "outputs/stub_receipt_diagnostic.json; not eligible for full résumé "
                "authorization (full_resume_generated remains false)."
            )

        if exec_st != "completed":
            if isinstance(diff, dict) and diff.get("prompt_budget_block"):
                code = str(diff.get("e3_decisive_reason_code") or "E3_PROMPT_BUDGET")
                msg = str(diff.get("e3_error_summary") or "")
                raise RuntimeError(f"FAILED_PROVIDER: {code}: {msg}".strip())
            if isinstance(diff, dict) and diff.get("generation_status") == FAILED_PROVIDER:
                pe = diff.get("provider_error")
                msg = ""
                if isinstance(pe, dict):
                    msg = str(pe.get("message") or "")
                raise RuntimeError(
                    f"FAILED_PROVIDER: {msg or f'L2 envelope execution_status={exec_st!r}'}"
                )
            raise RuntimeError(
                f"FAILED_PROVIDER: L2 envelope execution_status={exec_st!r} "
                "(expected 'completed' for full résumé generation)"
            )
        if shape_rep.generation_status != STRUCTURED_RESUME_OK:
            raise RuntimeError(
                f"{shape_rep.generation_status}: full résumé artifact contract requires "
                f"{STRUCTURED_RESUME_OK}; resume_shape={shape_rep.resume_shape!r}"
            )

        out: dict[str, Any] = {
            "generated": result,
            "status": "ok",
            "step": self.STEP_NAME,
            "generation_status": shape_rep.generation_status,
            "full_resume_generated": shape_rep.full_resume_generated,
            "resume_shape": shape_rep.resume_shape,
            "apps_rg_r4_generation_mode": MODE_LEGACY_FULL_RESUME,
        }
        if gr is not None:
            out["generated_resume"] = gr
        return out

    def _modular_section_lanes_generation(self, context: dict[str, Any]) -> dict[str, Any]:
        """Seven-lane modular path (no ``run_apps_rg_l2_envelope``)."""
        from apps_rg.l2_recipe.modular_lane_adapter import modular_lane_targeting_from_recipe_context
        from apps_rg.l2_recipe.modular_resume_generation import (
            ModularResumeInputPackage,
            ModularResumeProfile,
            run_modular_resume_generation,
        )
        from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

        art_raw = context.get("artifact_dir")
        if art_raw is None or not str(art_raw).strip():
            raise RuntimeError("FAILED_MODULAR_R4: artifact_dir is required for modular_section_lanes mode")
        art_dir = Path(str(art_raw)).resolve()
        repo = find_repo_root()
        pa = (
            context.get("compiled_prompt_artifact")
            or context.get("pa_artifact")
            or context.get("prompt_artifact")
        )
        run_token = (
            str(context.get("run_id") or "").strip()
            or str(getattr(pa, "run_id", "") or "").strip()
            or str(getattr(pa, "request_id", "") or "").strip()
            or uuid.uuid4().hex[:16]
        )

        inp = ModularResumeInputPackage(
            repo_root=repo,
            target_company=str(context.get("target_company") or ""),
            target_role=str(context.get("target_role") or ""),
        )
        prof = ModularResumeProfile(
            phase1_invoke_real_lanes=True,
            phase1_lane_provider=resolve_apps_rg_modular_lane_provider(),
            run_phase0_synthetic_assembly=False,
            validate_rg_output_fixture=False,
        )
        mr = run_modular_resume_generation(
            inp,
            art_dir,
            run_token,
            prof,
            lane_targeting=modular_lane_targeting_from_recipe_context(context),
        )
        write_modular_generate_step_receipt(art_dir, modular_result=mr)

        if not mr.ok_for_recipe_context():
            reason = (
                f"decisive={mr.decisive_status!r} failure={mr.failure_reason!r} "
                f"schema_ok={mr.final_schema_valid} lane_ok={mr.lane_outputs_valid}"
            )
            raise RuntimeError(f"FAILED_MODULAR_R4: {reason}")

        gr = mr.generated_resume
        if not isinstance(gr, dict) or not gr:
            raise RuntimeError("FAILED_MODULAR_R4: ok_for_recipe_context true but generated_resume missing")

        shape_rep = classify_resume_payload(gr)
        if shape_rep.generation_status != STRUCTURED_RESUME_OK:
            raise RuntimeError(
                f"FAILED_MODULAR_R4: {shape_rep.generation_status} "
                f"(expected {STRUCTURED_RESUME_OK}); resume_shape={shape_rep.resume_shape!r}"
            )

        return {
            "generated": mr,
            "status": "ok",
            "step": self.STEP_NAME,
            "generation_status": shape_rep.generation_status,
            "full_resume_generated": shape_rep.full_resume_generated,
            "resume_shape": shape_rep.resume_shape,
            "apps_rg_r4_generation_mode": MODE_MODULAR_SECTION_LANES,
            "modular_r4_section_provider_calls_ref": mr.section_provider_calls_ref,
            "modular_r4_section_output_refs": dict(mr.section_output_refs),
            "modular_r4_merge_receipt_ref": mr.merge_receipt_ref,
            "modular_r4_rg_output_merge_receipt_ref": mr.rg_output_merge_receipt_ref,
            "modular_r4_schema_validation_receipt_ref": mr.schema_validation_receipt_ref,
            "modular_r4_final_schema_valid": mr.final_schema_valid,
            "modular_r4_lanes_executed": mr.lanes_executed,
            "modular_r4_lane_outputs_valid": mr.lane_outputs_valid,
            "generated_resume": gr,
        }

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run the resume generation step.

        Raises
        ------
        PAGuardError
            If the context lacks a compiled PA artifact.
        RuntimeError
            With message starting with ``PA_COMPILE_FAILED`` when the
            PA compiler raises before this step is reached; this step
            re-raises if it encounters a compiler error in the context.
        """
        # Check for a compile error stashed by an upstream step
        if "pa_compile_error" in context:
            err = context["pa_compile_error"]
            raise RuntimeError(f"PA_COMPILE_FAILED: {err}")

        # Attempt to compile if no artifact yet
        if not any(k in context for k in ("compiled_prompt_artifact", "pa_artifact",
                                            "prompt_artifact", "governed_context")):
            try:
                from apps_rg.l2_recipe.pa_context_bridge import (
                    build_prompt_assembly_input_from_l2_context,
                )
                from apps_rg.prompt_assembly.compiler import compile_prompt

                pa_input = build_prompt_assembly_input_from_l2_context(context)
                artifact = compile_prompt(pa_input)
                context = {**context, "compiled_prompt_artifact": artifact}
            except Exception as exc:
                raise RuntimeError(f"PA_COMPILE_FAILED: {exc}") from exc

        # PA guard check after attempting compilation
        self._check_pa_guard(context)

        gen_mode = resolve_apps_rg_r4_generation_mode()
        contract_mode = normalize_resume_artifact_contract_mode(
            context.get("resume_artifact_contract_mode"),
        )
        if gen_mode == MODE_MODULAR_SECTION_LANES:
            if contract_mode in (MODE_STUB_RECEIPT, MODE_DIAGNOSTIC):
                raise RuntimeError(
                    "MODULAR_MODE_INCOMPATIBLE: APPS_RG_R4_GENERATION_MODE=modular_section_lanes "
                    "cannot be used with resume_artifact_contract_mode stub_receipt/diagnostic; "
                    "use legacy_full_resume for diagnostic runs."
                )
            return self._modular_section_lanes_generation(context)

        return self._legacy_envelope_generation(context)


class NarrativePassStep(BaseRecipeStep):
    """Optional narrative polish pass — does NOT require PA artifact.

    Runs only when target_company is non-empty.  Skips cleanly otherwise.
    """

    REQUIRES_PA: bool = False
    STEP_NAME: str = "narrative_pass"

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        target_company = context.get("target_company", "") or ""
        if not target_company:
            return {
                "status": "skipped",
                "step": self.STEP_NAME,
                "reason": "no target_company",
            }
        try:
            from apps_rg.runtime.bindings.narrative_adapter import run_narrative_pass
            result = run_narrative_pass(context)
            return {"status": "ok", "step": self.STEP_NAME, "result": result}
        except ImportError:
            return {
                "status": "skipped",
                "step": self.STEP_NAME,
                "reason": "narrative_adapter not available",
            }
        except Exception as exc:
            return {"status": "error", "step": self.STEP_NAME, "error": str(exc)}


class DocxExportStep(BaseRecipeStep):
    """DOCX export — writes ``outputs/resume.docx`` under the R4 ``artifact_dir``.

    Consumes ``context["generated_resume"]`` populated by ``GenerateResumeStep``.
    """

    REQUIRES_PA: bool = False
    STEP_NAME: str = "docx_export"

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        art = context.get("artifact_dir")
        if art is None or not str(art).strip():
            return {
                "status": "error",
                "step": self.STEP_NAME,
                "error": "no artifact_dir in context",
            }
        base = Path(str(art))
        payload = context.get("generated_resume")
        if not isinstance(payload, dict) or not payload:
            return {
                "status": "skipped",
                "step": self.STEP_NAME,
                "reason": "no generated_resume in context",
            }
        try:
            from apps_rg.runtime.render.json_resume_docx import render_resume_dict_to_docx
            from apps_rg.runtime.render.resume_export_enrich import enrich_generated_resume_for_docx

            out_dir = base / "outputs"
            out_dir.mkdir(parents=True, exist_ok=True)
            json_path = out_dir / "generated_resume.json"
            enriched = enrich_generated_resume_for_docx(
                payload,
                str(context.get("master_resume_data") or "") or None,
            )
            json_path.write_text(
                json.dumps(enriched, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            docx_path = out_dir / "resume.docx"
            render_resume_dict_to_docx(
                enriched,
                docx_path,
                target_role=str(context.get("target_role") or ""),
                target_company=str(context.get("target_company") or ""),
            )
            if not docx_path.is_file():
                return {
                    "status": "error",
                    "step": self.STEP_NAME,
                    "error": "docx render did not create file",
                }
            rel_docx = "outputs/resume.docx"
            rel_json = "outputs/generated_resume.json"
            shape_rep = classify_resume_payload(payload)
            manifest: dict[str, Any] = {
                "schema_version": "apps_rg_output_manifest.v1",
                "resume_docx_relpath": rel_docx,
                "resume_docx_abspath": str(docx_path.resolve()),
                "generated_resume_json_relpath": rel_json,
                "docx_verified": docx_path.is_file(),
                "apps_rg_generation_status": shape_rep.generation_status,
                "full_resume_generated": shape_rep.full_resume_generated,
                "resume_shape": shape_rep.resume_shape,
                "required_artifacts": {
                    "generated_resume_json": "present",
                    "resume_docx": "present",
                    "output_manifest": "present",
                    "docx_verified": docx_path.is_file(),
                },
            }
            (base / "apps_rg_output_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return {
                "status": "ok",
                "step": self.STEP_NAME,
                "docx_path": str(docx_path),
                "generated_resume_json_path": str(json_path),
                "run_dir": str(base),
            }
        except Exception as exc:  # guardian: allow-broad-exception -- docx stack surfaces diverse failures
            return {"status": "error", "step": self.STEP_NAME, "error": str(exc)}


class ResumeArtifactGateStep(BaseRecipeStep):
    """W2 — fail-closed verification of JSON + DOCX + manifest before run success."""

    REQUIRES_PA: bool = False
    STEP_NAME: str = "resume_artifact_gate"

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        art = context.get("artifact_dir")
        if art is None or not str(art).strip():
            raise RuntimeError("FAILED_ARTIFACT_GATE: no artifact_dir in context")
        base = Path(str(art))
        rep = verify_full_resume_artifact_bundle(base)
        merge_manifest_after_artifact_gate(base, shape_rep=rep)
        return {
            "status": "ok",
            "step": self.STEP_NAME,
            "generation_status": rep.generation_status,
            "full_resume_generated": rep.full_resume_generated,
            "resume_shape": rep.resume_shape,
        }