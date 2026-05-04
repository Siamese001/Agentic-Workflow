"""L2 step adapters for apps_rg deterministic resume-generation recipe.

Each step is a callable class with ``__call__(context) -> dict`` interface.
Steps are **app-specific implementations only** — they must not:
  - decide route (L0 owns that)
  - emit X3 (Exit V6 owns that)
  - write L4 (UWG owns that)
  - bypass Prompt Assembly for model calls
  - silently call external research

These classes are imported by ``agentic_core.runtime.l2_recipe_resolver``
and chained into the L2 execution sequence.  They are NEVER called directly
by ``apps_rg.__main__``.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

_log = logging.getLogger("apps_rg.l2_recipe.steps")


class _PAGuard:
    """Fail-closed guard: LLM-backed steps must have a PA-compatible artifact."""

    @staticmethod
    def check(context: dict[str, Any], step_name: str) -> None:
        """Raise if the context lacks PA artifact evidence for model calls.

        Current implementation checks for ``prompt_bom_dir`` OR
        ``pa_artifact_ref`` in context.  Full CompiledPromptArtifact
        enforcement is tracked separately — this is the hard fail-closed
        stub.
        """
        has_pa = bool(
            context.get("prompt_bom_dir")
            or context.get("pa_artifact_ref")
            or context.get("pa_compatible")
        )
        if not has_pa:
            raise RuntimeError(
                f"PA_GUARD_FAILED: {step_name} requires PA-compatible prompt "
                f"artifact before model invocation. Set 'pa_compatible=True' "
                f"or provide 'prompt_bom_dir' in L2 context."
            )


class GenerateResumeStep:
    """HOP-4: Run generate_resume main pipeline (HOPs 1-3, K-nodes).

    Wraps ``apps_rg.scripts.generate_resume.main()`` as an L2 step adapter.
    This step contains LLM calls and therefore requires PA-compatible
    prompt artifacts.
    """

    STEP_ID = "hop_4_generate_resume"
    REQUIRES_PA = True

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        import asyncio
        from apps_rg.scripts.generate_resume import main as _generate

        _PAGuard.check(context, self.STEP_ID)

        _log.info("[L2 step] %s: starting generate_resume", self.STEP_ID)
        asyncio.run(_generate())

        runs_root = Path("artifacts/apps_rg/runs")
        run_dir = None
        if runs_root.exists():
            candidates = sorted(
                (p for p in runs_root.iterdir() if p.is_dir()),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                run_dir = str(candidates[0])

        _log.info("[L2 step] %s: complete, run_dir=%s", self.STEP_ID, run_dir)
        return {
            "step_id": self.STEP_ID,
            "exit_code": 0,
            "run_dir": run_dir,
        }


class NarrativePassStep:
    """HOP-5: Narrative Pass (HOPs 4A-4H, in-process subprocess).

    Wraps ``apps_rg.scripts.narrative_pass`` as an L2 step adapter.
    """

    STEP_ID = "hop_5_narrative_pass"
    REQUIRES_PA = False

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        run_dir = context.get("run_dir")
        target_company = context.get("target_company", "")
        target_role = context.get("target_role", "")

        if not target_company:
            _log.info("[L2 step] %s: skipped (no target_company)", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 0, "skipped": True}

        if not run_dir:
            _log.error("[L2 step] %s: no run_dir in context", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 1, "error": "no run_dir"}

        run_dir = Path(run_dir)
        input_resume = run_dir / "generated_resume.json"
        if not input_resume.exists():
            _log.error("[L2 step] %s: %s missing", self.STEP_ID, input_resume)
            return {"step_id": self.STEP_ID, "exit_code": 1, "error": "generated_resume.json missing"}

        cmd = [
            sys.executable, "-m", "apps_rg.scripts.narrative_pass",
            "--target-company", target_company,
            "--input-resume", str(input_resume),
            "--out-dir", str(run_dir),
            "--manual-brief", context.get("manual_brief", "apps_rg/scripts/company_research.json"),
        ]
        if context.get("research_via"):
            cmd.extend(["--research-via", context["research_via"]])
        if context.get("auto_research_internal"):
            cmd.append("--auto-research-internal")
        if context.get("auto_research_tavily"):
            cmd.append("--auto-research-tavily")
        if target_role:
            cmd.extend(["--target-role", target_role])

        _log.info("[L2 step] %s: starting narrative pass", self.STEP_ID)
        try:
            result = subprocess.run(cmd, timeout=600, shell=False)
        except subprocess.TimeoutExpired:
            _log.error("[L2 step] %s: narrative pass timed out", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 124, "error": "timeout"}

        _log.info("[L2 step] %s: exit_code=%s", self.STEP_ID, result.returncode)
        return {"step_id": self.STEP_ID, "exit_code": result.returncode}


class DocxExportStep:
    """HOP-6: DOCX Export (in-process subprocess).

    Wraps ``apps_rg.outputs.docx_exporter`` as an L2 step adapter.
    """

    STEP_ID = "hop_6_docx_export"
    REQUIRES_PA = False

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        run_dir = context.get("run_dir")
        target_company = context.get("target_company", "")
        target_role = context.get("target_role", "")

        if not run_dir:
            _log.error("[L2 step] %s: no run_dir in context", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 1, "error": "no run_dir"}

        cmd = [
            sys.executable, "-m", "apps_rg.outputs.docx_exporter",
            "--run-dir", str(run_dir),
        ]
        if target_role and target_company:
            cmd.extend(["--target-role", target_role, "--target-company", target_company])

        _log.info("[L2 step] %s: starting DOCX export", self.STEP_ID)
        try:
            result = subprocess.run(cmd, timeout=120, shell=False)
        except subprocess.TimeoutExpired:
            _log.error("[L2 step] %s: DOCX export timed out", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 124, "error": "timeout"}

        _log.info("[L2 step] %s: exit_code=%s", self.STEP_ID, result.returncode)
        return {"step_id": self.STEP_ID, "exit_code": result.returncode}
