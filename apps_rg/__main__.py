"""apps_rg entry point — resume generation CLI.

Usage:
    python -m apps_rg --target-company <co> --target-role <role> [options]

Interactive mode (``--interactive``) stores prompted JD and briefing under
``artifacts/apps_rg/cli_inputs/cli_<id>/`` (``jd.json``, ``research_brief.*``)
and passes those paths to dispatch.

Cross-company contamination guard:
    _assert_artifact_matches_company(path, target_company, artifact_type)
    raises SystemExit if the artifact's declared `company` does not match the
    target. Guards are fail-soft on parse errors (missing file, corrupt JSON,
    non-dict YAML, unsupported extension) — those cases are left to the L0 gate.

Exit codes:
    0   — success
    1   — unhandled error
    2   — argument error
    7   — wizard / cursor-prompts sentinel mode (missing required inputs)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Callable

__all__ = [
    "_assert_artifact_matches_company",
    "_build_raw_request",
    "_prompt_jd_interactive",
    "main",
]


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


def _repo_root_for_cli_inputs() -> Path:
    """Resolve repo root (same strategy as canonical_dispatch artifact dirs)."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return Path.cwd()


def _new_interactive_inputs_session_dir() -> Path:
    """Create ``artifacts/apps_rg/cli_inputs/cli_<id>/`` for this interactive run."""
    rid = uuid.uuid4().hex[:12]
    out = _repo_root_for_cli_inputs() / "artifacts" / "apps_rg" / "cli_inputs" / f"cli_{rid}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _materialize_jd_file(
    session: Path,
    *,
    company: str,
    posting_title: str,
    jd_guess: str,
) -> Path:
    """Write ``jd.json`` under ``session`` and return its path."""
    out = session / "jd.json"
    candidate = Path(jd_guess)
    if candidate.is_file():
        if candidate.suffix.lower() == ".json":
            shutil.copy2(candidate, out)
            try:
                data = json.loads(out.read_text(encoding="utf-8"))
                if isinstance(data, dict) and company:
                    data.setdefault("company", company)
                    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            except (OSError, json.JSONDecodeError, TypeError):
                pass
        else:
            desc = candidate.read_text(encoding="utf-8")
            payload = {
                "title": posting_title,
                "description": desc.strip(),
                "company": company,
            }
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return out

    if jd_guess.lstrip().startswith("{"):
        try:
            obj = json.loads(jd_guess)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, dict):
            obj.setdefault("company", company or obj.get("company", ""))
            if not str(obj.get("title", "")).strip():
                obj["title"] = posting_title
            out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
            return out

    payload = {
        "title": posting_title,
        "description": jd_guess.strip(),
        "company": company,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _materialize_brief_file(
    session: Path,
    brief_guess: str,
    fetch_url: Callable[[str], str],
) -> Path:
    """Write briefing under ``session`` (file copy, URL fetch, or inline text)."""
    s = brief_guess.strip()
    if s.startswith(("http://", "https://")):
        body = fetch_url(s)
        out = session / "research_brief.txt"
        out.write_text(body, encoding="utf-8")
        return out

    bp = Path(s)
    if bp.is_file():
        ext = bp.suffix if bp.suffix else ".txt"
        out = session / f"research_brief{ext}"
        shutil.copy2(bp, out)
        return out

    out = session / "research_brief.txt"
    out.write_text(s, encoding="utf-8")
    return out


def _prompt_jd_interactive() -> str:
    """Prompt for a JD path, JSON blob, or one-line description (TTY only)."""
    if not sys.stdin.isatty():
        msg = "apps_rg: non-interactive mode — stdin is not a TTY; provide --jd"
        print(msg, file=sys.stderr, flush=True)
        raise SystemExit(msg)
    print("JD file path, JSON, or one-line description:", flush=True)
    return input().strip()


def _gather_interactive_fields(args: argparse.Namespace) -> None:
    """Prompt for JD + briefing and save under ``artifacts/apps_rg/cli_inputs/cli_<id>/``."""
    if not sys.stdin.isatty():
        print("apps_rg: --interactive requires a TTY stdin.", file=sys.stderr, flush=True)
        raise SystemExit(2)

    if not str(args.target_company).strip():
        args.target_company = input("Target company: ").strip()
    if not str(args.target_role).strip():
        args.target_role = input("Target role: ").strip()

    session: Path | None = None

    def _session_dir() -> Path:
        nonlocal session
        if session is None:
            session = _new_interactive_inputs_session_dir()
            setattr(args, "_interactive_cli_inputs_dir", str(session))
            print(f"\nInteractive inputs directory:\n  {session}\n", flush=True)
        return session

    from apps_rg.runtime.orchestration.canonical_dispatch import _fetch_url_text

    if not str(args.jd).strip():
        print("Job posting title as listed on the JD (Enter to use target role):", flush=True)
        posting_title = input().strip() or str(args.target_role).strip()

        print(
            "\nJD — path to .txt/.json, paste JSON {{title, description}}, "
            "or a one-line summary (Enter to skip):",
            flush=True,
        )
        jd_guess = input().strip()
        if jd_guess.strip():
            jd_path = _materialize_jd_file(
                _session_dir(),
                company=str(args.target_company).strip(),
                posting_title=posting_title,
                jd_guess=jd_guess.strip(),
            )
            args.jd = str(jd_path)
            print(f"  JD saved: {jd_path}", flush=True)

    if not str(args.manual_brief).strip():
        print(
            "\nResearch briefing — local file path, https URL, or short paste (optional, Enter to skip):",
            flush=True,
        )
        brief_guess = input().strip()
        if brief_guess:
            brief_path = _materialize_brief_file(_session_dir(), brief_guess, _fetch_url_text)
            args.manual_brief = str(brief_path)
            print(f"  Briefing saved: {brief_path}", flush=True)

    if session is not None:
        print("\nCLI loads JD/brief from the files under the directory above.\n", flush=True)


def _build_raw_request(args: Any) -> dict[str, Any]:
    """Build raw_request for DS-R7 contract tests and diagnostics.

    Mirrors :func:`build_raw_request_for_r4` except when ``jd`` names a missing
    ``.json`` path (returns empty ``jd_payload``) or a JSON file (forwards parsed
    dict into ``jd_payload`` / ``body_text``).
    """
    from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4

    tc = getattr(args, "target_company", None) or ""
    tr = getattr(args, "target_role", None) or ""
    tl = getattr(args, "target_level", None) or ""
    manual_brief = getattr(args, "manual_brief", None) or ""
    resume = getattr(args, "resume", None) or ""
    generation_mode = getattr(args, "generation_mode", "strategic_tailor") or "strategic_tailor"

    jd_val = getattr(args, "jd", None)
    if jd_val is None:
        jd_val = ""
    else:
        jd_val = str(jd_val)

    non_interactive = getattr(args, "non_interactive", True)
    if not jd_val.strip() and not non_interactive:
        jd_val = _prompt_jd_interactive()

    st = jd_val.strip()
    if st:
        p = Path(jd_val)
        if p.suffix.lower() == ".json" and not p.is_file() and not st.lstrip().startswith("{"):
            return {"jd_payload": {}, "body_text": ""}

        if p.is_file() and p.suffix.lower() == ".json":
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    base = build_raw_request_for_r4(
                        target_company=tc,
                        target_role=tr,
                        target_level=tl,
                        jd="",
                        manual_brief=manual_brief,
                        resume_path=resume,
                        generation_mode=generation_mode,
                    )
                    base["jd_payload"] = data
                    base["body_text"] = json.dumps(data)
                    return base
            except (OSError, json.JSONDecodeError):
                pass

    return build_raw_request_for_r4(
        target_company=tc,
        target_role=tr,
        target_level=tl,
        jd=jd_val,
        manual_brief=manual_brief,
        resume_path=resume,
        generation_mode=generation_mode,
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
    p.add_argument("--manual-brief", default="", help="Path or https URL to pre-built research brief")
    p.add_argument("--resume", default="", help="Path to source resume (PDF/DOCX/JSON)")
    p.add_argument(
        "--generation-mode",
        default="strategic_tailor",
        choices=["strategic_tailor", "keyword_match", "generate_scratch"],
    )
    p.add_argument("--dry-run", action="store_true", help="Validate inputs without calling LLM")
    p.add_argument(
        "--cursor-prompts",
        action="store_true",
        help="Wizard mode — write sentinel and exit 7 when inputs are missing",
    )
    p.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="TTY: prompt for JD + briefing; save under artifacts/apps_rg/cli_inputs/cli_<id>/",
    )
    p.add_argument("--artifact-dir", default="", help="Override artifact output directory")
    return p


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    """CLI entry point for apps_rg.

    Returns exit code (0 = success, 7 = cursor-prompts sentinel).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.non_interactive = not args.interactive

    # Wizard / cursor-prompts mode: if mandatory inputs are missing, write a
    # sentinel line and exit 7 so the calling process (Cursor Agent IDE) can prompt
    # the user for the missing fields.
    mandatory_missing = []
    if not args.target_company:
        mandatory_missing.append("--target-company")
    if not args.target_role:
        mandatory_missing.append("--target-role")

    if mandatory_missing and args.cursor_prompts:
        sentinel = (
            f"CASCADE_WIZARD_SENTINEL: mandatory inputs missing: "
            f"{', '.join(mandatory_missing)}. "
            f"Please provide target company and role to proceed."
        )
        print(sentinel, flush=True)
        return 7

    if args.interactive:
        _gather_interactive_fields(args)

    if args.dry_run:
        print("DRY RUN: apps_rg pipeline validation complete (no LLM call).", flush=True)
        cli_in = getattr(args, "_interactive_cli_inputs_dir", "")
        if cli_in:
            print(f"cli_inputs_dir={cli_in}", flush=True)
        if args.interactive or args.jd or args.manual_brief:
            preview = _build_raw_request(args)
            jp = preview.get("jd_payload")
            if isinstance(jp, dict) and jp:
                print(f"jd_payload title={jp.get('title', '')!r}", flush=True)
            mb = str(args.manual_brief or "").strip()
            if mb:
                src = "url" if mb.startswith(("http://", "https://")) else "path"
                print(f"manual_brief ({src}): {mb[:120]}{'…' if len(mb) > 120 else ''}", flush=True)
        return 0

    # Cross-company contamination guards
    if args.target_company:
        if args.manual_brief and not str(args.manual_brief).startswith(("http://", "https://")):
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
        authorized = (
            bool(result.get("outcome_authorized"))
            if isinstance(result, dict)
            else False
        )
        print(
            f"apps_rg completed: exit_status={status} outcome_authorized={authorized}",
            flush=True,
        )
        if isinstance(result, dict) and result.get("artifact_dir"):
            print(f"artifact_dir={result['artifact_dir']}", flush=True)
        if status != "success" or not authorized:
            return 1
        return 0
    except Exception as exc:
        print(f"ERROR: apps_rg pipeline failed: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
