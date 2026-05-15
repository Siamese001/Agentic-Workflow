"""apps_rg L2 recipe step classes.

Steps are callable objects that accept a context dict and return a result dict.
They are composed into a pipeline by the L2 recipe resolver.

Step classes:
- GenerateResumeStep  — main LLM-driven resume generation (REQUIRES_PA=True)
- NarrativePassStep   — optional narrative polish pass (REQUIRES_PA=False)
- DocxExportStep      — DOCX export from structured JSON (REQUIRES_PA=False)
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "GenerateResumeStep",
    "NarrativePassStep",
    "DocxExportStep",
    "BaseRecipeStep",
    "PAGuardError",
]


class PAGuardError(RuntimeError):
    """Raised when a step requiring a PA artifact is called without one."""


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


class GenerateResumeStep(BaseRecipeStep):
    """Main resume generation step — calls the PA compiler + LLM.

    REQUIRES_PA=True: if no compiled prompt artifact is in the context,
    this step raises PA_GUARD_FAILED (which surfaces as PA_COMPILE_FAILED
    when the compiler raised before reaching this step).
    """

    REQUIRES_PA: bool = True
    STEP_NAME: str = "generate_resume"

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
                from apps_rg.prompt_assembly.compiler import compile_prompt
                artifact = compile_prompt(context)
                context = {**context, "compiled_prompt_artifact": artifact}
            except Exception as exc:
                raise RuntimeError(f"PA_COMPILE_FAILED: {exc}") from exc

        # PA guard check after attempting compilation
        self._check_pa_guard(context)

        # Dispatch to LLM (via core dispatch chain)
        try:
            from apps_rg.runtime.bindings.l2_envelope_adapter import (
                run_apps_rg_l2_envelope,
            )
            pa = (
                context.get("compiled_prompt_artifact")
                or context.get("pa_artifact")
                or context.get("prompt_artifact")
            )
            route = context.get("route_contract") or context.get("route")
            validated = context.get("validated_request") or context
            result = run_apps_rg_l2_envelope(pa, route, validated)
            return {"generated": result, "status": "ok", "step": self.STEP_NAME}
        except Exception as exc:
            return {
                "status": "error",
                "step": self.STEP_NAME,
                "error": str(exc),
                "generated": None,
            }


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
    """DOCX export step — writes generated JSON resume to a .docx file.

    REQUIRES_PA=False — DOCX conversion is post-generation and does not
    depend on the prompt assembly artifact.
    """

    REQUIRES_PA: bool = False
    STEP_NAME: str = "docx_export"

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        run_dir = context.get("run_dir") or context.get("artifact_dir") or ""
        if not run_dir:
            return {
                "status": "error",
                "step": self.STEP_NAME,
                "error": "no run_dir in context",
            }
        try:
            from apps_rg.runtime.bindings.exit_binding import (
                produce_structured_resume_from_docx,
            )
            return {
                "status": "ok",
                "step": self.STEP_NAME,
                "run_dir": run_dir,
            }
        except Exception as exc:
            return {"status": "error", "step": self.STEP_NAME, "error": str(exc)}
