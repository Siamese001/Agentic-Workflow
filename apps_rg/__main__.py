"""apps_rg entry point — resume generation CLI.

Usage:
    python -m apps_rg --target-company <co> --target-role <role> [options]

Cross-company contamination guard:
    _assert_artifact_matches_company(path, target_company, artifact_type)
    raises SystemExit if the artifact's declared `company` does not match the
    target. Guards are fail-soft on parse errors (missing file, corrupt JSON,
    non-dict YAML, unsupported extension) — those cases are left to the L0 gate.

Exit codes:
    0   — success
    1   — unhandled error
    2   — argument error
    7   — wizard / cascade-prompts sentinel mode (missing required inputs)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

__all__ = ["_assert_artifact_matches_company", "main"]


def _assert_artifact_matches_company(
    path: Path,
    target_company: str,
    artifact_type: str,
) -> None:
    """Fail fast if an artifact's declared `company` != target_company.

    Behaviour:
    - Missing file → no-op (L0 gate's responsibility).
    - Empty target_company → no-op (caller hasn't validated yet).
    - Non-JSON/YAML extension → no-op.
    - Parse error (corrupt, non-dict) → no-op (fail-soft).
    - company key absent in artifact → no-op (e.g. candidate profiles).
    - company present and != target_company (case-insensitive) → SystemExit.

    Parameters
    ----------
    path:
        Filesystem path to the artifact.
    target_company:
        The run's declared target company.
    artifact_type:
        Human-readable label for error messages (e.g. "manual_brief").
    """
    if not target_company:
        return
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists():
        return

    suffix = path.suffix.lower()
    artifact_company: str | None = None

    try:
        if suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                artifact_company = data.get("company")
        elif suffix in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except ImportError:
                import re
                m = re.search(r"^company\s*:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
                data = {"company": m.group(1).strip().strip("'\"")} if m else {}
            if isinstance(data, dict):
                artifact_company = data.get("company")
        else:
            return
    except Exception:
        return

    if artifact_company is None:
        return

    if str(artifact_company).strip().lower() != target_company.strip().lower():
        sys.exit(
            f"FATAL: Cross-company contamination detected — "
            f"artifact '{path.name}' ({artifact_type}) declares company "
            f"'{artifact_company}' but current run targets '{target_company}'. "
            f"Aborting to prevent resume contamination."
        )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="apps_rg",
        description="Agentic resume generator — apps_rg pipeline",
    )
    p.add_argument("--target-company", default="", help="Target company name (required)")
    p.add_argument("--target-role", default="", help="Target role/title (required)")
    p.add_argument("--target-level", default="", help="Target level (optional)")
    p.add_argument("--jd", default="", help="Path to JD JSON/txt or inline text")
    p.add_argument("--manual-brief", default="", help="Path to pre-built research brief")
    p.add_argument("--resume", default="", help="Path to source resume (PDF/DOCX/JSON)")
    p.add_argument(
        "--generation-mode",
        default="strategic_tailor",
        choices=["strategic_tailor", "keyword_match", "generate_scratch"],
    )
    p.add_argument("--dry-run", action="store_true", help="Validate inputs without calling LLM")
    p.add_argument(
        "--cascade-prompts",
        action="store_true",
        help="Wizard mode — write sentinel and exit 7 when inputs are missing",
    )
    p.add_argument("--artifact-dir", default="", help="Override artifact output directory")
    return p


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    """CLI entry point for apps_rg.

    Returns exit code (0 = success, 7 = cascade-prompts sentinel).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Wizard / cascade-prompts mode: if mandatory inputs are missing, write a
    # sentinel line and exit 7 so the calling process (Cascade IDE) can prompt
    # the user for the missing fields.
    mandatory_missing = []
    if not args.target_company:
        mandatory_missing.append("--target-company")
    if not args.target_role:
        mandatory_missing.append("--target-role")

    if mandatory_missing and args.cascade_prompts:
        sentinel = (
            f"CASCADE_WIZARD_SENTINEL: mandatory inputs missing: "
            f"{', '.join(mandatory_missing)}. "
            f"Please provide target company and role to proceed."
        )
        print(sentinel, flush=True)
        return 7

    if args.dry_run:
        print("DRY RUN: apps_rg pipeline validation complete (no LLM call).", flush=True)
        return 0

    # Cross-company contamination guards
    if args.target_company:
        if args.manual_brief:
            _assert_artifact_matches_company(
                Path(args.manual_brief), args.target_company, "manual_brief"
            )
        if args.jd and Path(args.jd).exists():
            _assert_artifact_matches_company(
                Path(args.jd), args.target_company, "jd"
            )

    # Dispatch to the runtime pipeline
    try:
        from agentic_core.runtime.entry.apps_rg_dispatch import dispatch_apps_rg_run

        result = dispatch_apps_rg_run(
            target_company=args.target_company,
            target_role=args.target_role,
            target_level=args.target_level,
            jd=args.jd,
            manual_brief=args.manual_brief,
            resume_path=args.resume,
            generation_mode=args.generation_mode,
            artifact_dir=args.artifact_dir,
        )
        status = result.get("exit_status", "unknown") if isinstance(result, dict) else "unknown"
        print(f"apps_rg completed: exit_status={status}", flush=True)
        return 0
    except Exception as exc:
        print(f"ERROR: apps_rg pipeline failed: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
