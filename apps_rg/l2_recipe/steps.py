"""apps_rg L2 recipe step classes.

Steps are callable objects that accept a context dict and return a result dict.
They are composed into a pipeline by the L2 recipe resolver.

Step classes:
- GenerateResumeStep  — main LLM-driven resume generation (REQUIRES_PA=True)
- ResumeArtifactGateStep — on-disk JSON + manifest bundle verification (REQUIRES_PA=False)
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
    persist_json_product_outputs,
    verify_full_resume_artifact_bundle,
)
from apps_rg.l2_recipe.r4_generation_mode import (
    MODE_MODULAR_SECTION_LANES,
    resolve_apps_rg_modular_lane_provider,
    resolve_apps_rg_r4_generation_mode,
)
from apps_rg.l2_recipe.sealed_resume_extract import generated_resume_from_sealed_l2

__all__ = [
    "GenerateResumeStep",
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
            except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                raise RuntimeError(f"PA_COMPILE_FAILED: {exc}") from exc

        # PA guard check after attempting compilation
        self._check_pa_guard(context)

        _ = resolve_apps_rg_r4_generation_mode()
        contract_mode = normalize_resume_artifact_contract_mode(
            context.get("resume_artifact_contract_mode"),
        )
        if contract_mode in (MODE_STUB_RECEIPT, MODE_DIAGNOSTIC):
            raise RuntimeError(
                "MODULAR_MODE_INCOMPATIBLE: modular_section_lanes generation cannot be used "
                "with resume_artifact_contract_mode stub_receipt/diagnostic."
            )
        return self._modular_section_lanes_generation(context)


class ResumeArtifactGateStep(BaseRecipeStep):
    """W2 — fail-closed verification of JSON + manifest before run success."""

    REQUIRES_PA: bool = False
    STEP_NAME: str = "resume_artifact_gate"

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        art = context.get("artifact_dir")
        if art is None or not str(art).strip():
            raise RuntimeError("FAILED_ARTIFACT_GATE: no artifact_dir in context")
        base = Path(str(art))
        gr = context.get("generated_resume")
        if isinstance(gr, dict) and gr:
            persist_json_product_outputs(base, generated_resume=gr)
        rep = verify_full_resume_artifact_bundle(base)
        merge_manifest_after_artifact_gate(base, shape_rep=rep)
        return {
            "status": "ok",
            "step": self.STEP_NAME,
            "generation_status": rep.generation_status,
            "full_resume_generated": rep.full_resume_generated,
            "resume_shape": rep.resume_shape,
        }