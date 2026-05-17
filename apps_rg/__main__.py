"""apps_rg entry point — resume generation CLI.

Usage:
    python -m apps_rg --target-company <co> --target-role <role> [options]

Interactive mode (``--interactive``) stores prompted JD and briefing under
``artifacts/apps_rg/cli_inputs/cli_<id>/`` (``jd.json``, ``research_brief.*``)
and passes those paths to dispatch.

Non-TTY runners (IDE agents, CI): set ``APPS_RG_INTERACTIVE_STDIN=1`` and pipe one
line per prompt (company, role, JD listing title, JD text, optional brief), or pass
``--jd`` / ``--manual-brief`` / ``--target-*`` explicitly.

When ``--resume`` is omitted (or empty), the CLI uses the canonical base resume JSON
(``apps_rg/resume/base/amit_ayer_base_resume_v1.json`` under the repo root). Pass
``--resume`` explicitly to override.

**Generation topology:** this CLI is the canonical **R4 integrated product** entry
(``dispatch_apps_rg_run`` → governed spine). **Default** résumé body generation is
**modular** (seven section lanes + deterministic merge) when
``APPS_RG_R4_GENERATION_MODE`` is unset — see ``apps_rg.l2_recipe.r4_generation_route``.
Set ``APPS_RG_R4_GENERATION_MODE=legacy_full_resume`` for explicit **rollback** to one
``run_apps_rg_l2_envelope`` call with a full tailor-existing CPA. Offline per-lane
orchestration under ``python -m apps_rg.runtime.orchestrate_full_resume`` is a separate
module entry from integrated dispatch.

**L2 model execution (résumé body):** by default ``APPS_RG_L2_PROVIDER_MODE`` is unset
and the v4 envelope uses **local vLLM** (``ProviderGateway`` ``local_only``).
Set ``APPS_RG_L2_PROVIDER_MODE=stub_only`` or ``APPS_RG_L2_FORCE_STUB=1`` for deterministic
stub JSON (CI / dry runs). Use ``APPS_RG_L2_PROVIDER_MODE=live_allowed`` when the compiled
CPA targets an external API lane (``anthropic``, ``openai``, ``google_gemini``) and keys
are present.

**JD normalization:** integrated dispatch uses ``build_raw_request_for_r4`` →
``build_canonical_jd_payload``. ``_build_raw_request`` (DS-R7, dry-run preview) now
delegates to the same helper for all real JD paths; only the DS-R7 stub for a missing
``.json`` path returns empty ``jd_payload`` / ``body_text`` (no digest parity).

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
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Callable

from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
    run_integrated_r4_deterministic_pipeline,
)
from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache
from apps_rg.runtime.resume_resolution import DEFAULT_RESUME_SSOT_PATH
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import find_repo_root

__all__ = [
    "_assert_artifact_matches_company",
    "_build_raw_request",
    "_prompt_jd_interactive",
    "_run_with_args",
    "check_r1a_cache",
    "compute_r1a_key",
    "main",
    "run_integrated_r4_deterministic_pipeline",
    "stamp_r1a_cache",
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


def _default_resume_path() -> str:
    """Absolute path to canonical base resume JSON, or ``""`` if missing."""
    p = DEFAULT_RESUME_SSOT_PATH
    return str(p.resolve()) if p.is_file() else ""


def _print_paths_for_cursor_workspace(artifact_dir_str: str) -> None:
    """Emit repo-relative POSIX paths and file:// URIs (Cursor/VS Code friendly).

    Raw Windows ``artifact_dir=C:\\...`` strings often do not linkify in the
    integrated terminal or chat; workspace-relative ``artifacts/...`` and
    ``file:///`` URIs are easier to open.
    """
    if not str(artifact_dir_str).strip():
        return
    root = _repo_root_for_cli_inputs().resolve()
    try:
        ad = Path(artifact_dir_str).resolve()
    except OSError:
        return
    try:
        rel = ad.relative_to(root).as_posix()
        print(f"artifact_dir_workspace={rel}", flush=True)
    except ValueError:
        print(f"artifact_dir_workspace={ad.as_posix()}", flush=True)
    try:
        print(f"artifact_dir_uri={ad.as_uri()}", flush=True)
    except ValueError:
        pass
    docx = ad / "outputs" / "resume.docx"
    if docx.is_file():
        try:
            dx_rel = docx.resolve().relative_to(root).as_posix()
            print(f"resume_docx_workspace={dx_rel}", flush=True)
        except ValueError:
            print(f"resume_docx_workspace={docx.resolve().as_posix()}", flush=True)
        try:
            print(f"resume_docx_uri={docx.resolve().as_uri()}", flush=True)
        except ValueError:
            pass


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


def _stdin_batch_interactive_enabled() -> bool:
    """Non-TTY stdin batching (one line per prompt) — opt-in to avoid hangs in tools/CI."""
    return os.environ.get("APPS_RG_INTERACTIVE_STDIN", "").strip().lower() in ("1", "true", "yes")


def _reject_interactive_without_stdin_batch() -> None:
    if sys.stdin.isatty() or _stdin_batch_interactive_enabled():
        return
    print(
        "apps_rg: --interactive needs an interactive terminal, or non-interactive stdin with "
        "APPS_RG_INTERACTIVE_STDIN=1 and one answer line per prompt (see --help). "
        "Otherwise pass --target-company, --target-role, --jd, etc.",
        file=sys.stderr,
        flush=True,
    )
    raise SystemExit(2)


def _cli_input() -> str:
    """Read one line from stdin; fail cleanly on EOF (empty pipe)."""
    try:
        return input()
    except EOFError:
        print(
            "apps_rg: EOF on stdin — with APPS_RG_INTERACTIVE_STDIN=1, pipe one line per prompt "
            "in the same order as the questions (company, role, JD listing title, JD body, brief). "
            "Or use an interactive terminal. You can also pass --jd / --manual-brief / --target-*.",
            file=sys.stderr,
            flush=True,
        )
        raise SystemExit(2) from None


def _prompt_jd_interactive() -> str:
    """Prompt for a JD path, JSON blob, or one-line description."""
    _reject_interactive_without_stdin_batch()
    print("JD file path, JSON, or one-line description:", flush=True)
    return _cli_input().strip()


def _gather_interactive_fields(args: argparse.Namespace) -> None:
    """Prompt for JD + briefing and save under ``artifacts/apps_rg/cli_inputs/cli_<id>/``."""
    _reject_interactive_without_stdin_batch()
    if not str(args.target_company).strip():
        print("Target company: ", end="", flush=True)
        args.target_company = _cli_input().strip()
    if not str(args.target_role).strip():
        print("Target role: ", end="", flush=True)
        args.target_role = _cli_input().strip()

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
        posting_title = _cli_input().strip() or str(args.target_role).strip()

        print(
            "\nJD — path to .txt/.json, paste JSON {{title, description}}, "
            "or a one-line summary (Enter to skip):",
            flush=True,
        )
        jd_guess = _cli_input().strip()
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
        brief_guess = _cli_input().strip()
        if brief_guess:
            brief_path = _materialize_brief_file(_session_dir(), brief_guess, _fetch_url_text)
            args.manual_brief = str(brief_path)
            print(f"  Briefing saved: {brief_path}", flush=True)

    if session is not None:
        print("\nCLI loads JD/brief from the files under the directory above.\n", flush=True)


def _build_raw_request(args: Any) -> dict[str, Any]:
    """Build raw_request for DS-R7, CLI dry-run preview, and diagnostics.

    **Certified JD parity:** after interactive JD resolution, this always delegates
    to :func:`apps_rg.runtime.orchestration.canonical_dispatch.build_raw_request_for_r4`
    (shared :func:`apps_rg.runtime.jd_resolution.build_canonical_jd_payload` /
    :func:`~apps_rg.runtime.jd_resolution.canonical_jd_digest`), except the DS-R7 stub
    when ``jd`` looks like a missing ``.json`` path only — that branch returns empty
    ``jd_payload`` / ``body_text`` and does **not** claim digest parity.
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

    return build_raw_request_for_r4(
        target_company=tc,
        target_role=tr,
        target_level=tl,
        jd=jd_val,
        manual_brief=manual_brief,
        resume_path=resume,
        generation_mode=generation_mode,
    )


def _semantic_cache_r1b_enabled() -> bool:
    return os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _run_with_args(
    args: Any,
    *,
    runs_dir: Path,
    artifact_dir_override: Path | None = None,
) -> None:
    """Exercise R4 + R1 cache wiring (canonical unit tests monkeypatch internals).

    CLI production path uses ``dispatch_apps_rg_run``. This shim mirrors the legacy
    L0 remediation tests that assert pre/post-flight cache bookkeeping.
    """
    from apps_rg.enforcement.cli_prerequisite_gate import (
        check_apps_rg_cli_prerequisites,
    )
    from apps_rg.cache import r1b_adapter as _r1b_mod
    from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4

    check_apps_rg_cli_prerequisites(
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
        policy_hash=os.environ.get("APPS_RG_POLICY_HASH", ""),
        blueprint_hash=os.environ.get("APPS_RG_BLUEPRINT_HASH", ""),
        trace_id=str(getattr(args, "tenant_id", "") or "default_cli"),
        manual_brief_path=str(getattr(args, "manual_brief", "") or ""),
    )

    raw_request = build_raw_request_for_r4(
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
        target_level=str(getattr(args, "target_level", "") or ""),
        jd=str(getattr(args, "jd", "") or ""),
        manual_brief=str(getattr(args, "manual_brief", "") or ""),
        resume_path=str(getattr(args, "resume", "") or ""),
        generation_mode=str(
            getattr(args, "generation_mode", None) or "strategic_tailor",
        ),
    )

    resume_snapshot = str(raw_request.get("resume_hash") or "")
    r1a_key = compute_r1a_key(
        source_resume_hash=resume_snapshot,
        target_company=str(getattr(args, "target_company", "") or ""),
        target_role=str(getattr(args, "target_role", "") or ""),
    )

    env_policy = os.environ.get("APPS_RG_POLICY_HASH")
    env_bp = os.environ.get("APPS_RG_BLUEPRINT_HASH")

    r1a_hit = check_r1a_cache(
        r1a_key,
        runs_dir=runs_dir,
        policy_hash=env_policy,
        blueprint_hash=env_bp,
    )
    if r1a_hit:
        raise SystemExit(0)

    if _semantic_cache_r1b_enabled():
        r1b_probe = _r1b_mod.check_r1b_for_apps_rg(
            raw_request=raw_request,
            runs_dir=str(runs_dir),
        )
        if isinstance(r1b_probe, dict) and bool(r1b_probe.get("cached")):
            raise SystemExit(0)

    artifact_root = (
        artifact_dir_override
        if artifact_dir_override is not None
        else (runs_dir / "_r4_artifact_scratch")
    )
    if artifact_dir_override is None:
        artifact_root.mkdir(parents=True, exist_ok=True)

    outcome = run_integrated_r4_deterministic_pipeline(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=artifact_root,
    )

    rid = str(getattr(outcome, "run_id", "") or "").strip()
    emit_integrated_run_bundle_index(
        find_repo_root(),
        Path(outcome.artifact_dir),
        run_id=rid or None,
        correlation_id=rid or None,
    )

    fault_txt = str(getattr(outcome, "fault", "") or "").strip()
    if fault_txt:
        raise SystemExit(1)
    if bool(getattr(outcome, "terminal_r5", False)):
        raise SystemExit(0)

    stamp_r1a_cache(
        r1a_key,
        Path(outcome.artifact_dir),
        policy_hash=env_policy,
        blueprint_hash=env_bp,
    )

    if _semantic_cache_r1b_enabled():
        generated = Path(outcome.artifact_dir) / "generated_resume.json"
        if generated.is_file():
            try:
                payload = json.loads(generated.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    semantic_writer = _r1b_mod.AppsRgR1BCacheAdapter(
                        runs_dir=str(runs_dir),
                    )
                    semantic_writer.store_intent_and_output(
                        intent=dict(raw_request),
                        chunks=payload,
                    )
            except (OSError, json.JSONDecodeError, TypeError):
                pass

    raise SystemExit(0)


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
    p.add_argument(
        "--resume",
        default="",
        help=(
            "Path to source resume (PDF/DOCX/JSON). "
            "Default: apps_rg/resume/base/amit_ayer_base_resume_v1.json when omitted."
        ),
    )
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
        help=(
            "Prompt for JD + briefing; with APPS_RG_INTERACTIVE_STDIN=1, read one line per prompt from "
            "stdin when not a TTY. Saves under artifacts/apps_rg/cli_inputs/cli_<id>/"
        ),
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

    if not str(getattr(args, "resume", "") or "").strip():
        dr = _default_resume_path()
        if dr:
            args.resume = dr

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
            ad_str = str(result["artifact_dir"])
            print(f"artifact_dir={ad_str}", flush=True)
            _print_paths_for_cursor_workspace(ad_str)
        if status != "success" or not authorized:
            return 1
        return 0
    except Exception as exc:
        print(f"ERROR: apps_rg pipeline failed: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
