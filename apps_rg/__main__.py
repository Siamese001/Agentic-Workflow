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
Résumé body generation is **modular section lanes only** (``APPS_RG_R4_GENERATION_MODE`` unset or ``modular_section_lanes``).
Offline batch orchestration is library-only under ``tests.helpers.offline_lane_orchestration`` (not product proof);
there is no separate offline orchestrate module CLI.

**L2 model execution (résumé body):** by default ``APPS_RG_L2_PROVIDER_MODE`` is unset
and the v4 envelope uses **local vLLM** (``ProviderGateway`` ``local_only``).
Section lanes and integrated runs require **live** ``qwen_vllm`` (no offline contract stub)
and **live X1D judges** (no ``--mock-judges`` on this CLI; pytest uses
``APPS_RG_TEST_HARNESS=1`` + ``APPS_RG_MOCK_JUDGES=1`` only).
Set ``APPS_RG_L2_PROVIDER_MODE=live_allowed`` when the compiled
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

from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache
from apps_rg.runtime.resume_resolution import DEFAULT_RESUME_SSOT_PATH
from apps_rg.runtime.cli_section_execution_report import (
    emit_cli_section_execution_summary,
    section_lane_process_exit_code,
)
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import find_repo_root
from apps_rg.runtime.section_cli_defaults import SectionCliConfigError

__all__ = [
    "_assert_artifact_matches_company",
    "_build_raw_request",
    "_prompt_jd_interactive",
    "check_r1a_cache",
    "compute_r1a_key",
    "main",
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
    exec_summary_lane = str(getattr(args, "section", "") or "").strip().lower() == "executive_summary"
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

        jd_prompt = (
            "\nJD — path to .txt/.json, paste JSON {{title, description}}, "
            "or a one-line summary (required):"
            if exec_summary_lane
            else "\nJD — path to .txt/.json, paste JSON {{title, description}}, "
            "or a one-line summary (Enter to skip):"
        )
        print(jd_prompt, flush=True)
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
        brief_prompt = (
            "\nResearch briefing — local file path, https URL, or short paste (required):"
            if exec_summary_lane
            else "\nResearch briefing — local file path, https URL, or short paste "
            "(optional, Enter to skip):"
        )
        print(brief_prompt, flush=True)
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
    from apps_rg.runtime.embedding_settings import semantic_cache_r1b_eligible

    return semantic_cache_r1b_eligible()


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
    p.add_argument(
        "--section",
        default="",
        choices=["", "headline", "executive_summary", "unify_bullets", "unify_narrative", "ibm_bullets", "ibm_narrative", "competencies"],
        help="Run a single section lane through the apps_rg orchestrator (default: full R4 product).",
    )
    p.add_argument(
        "--executive-summary",
        action="store_true",
        help="Alias for --section executive_summary.",
    )
    p.add_argument(
        "--unify-bullets",
        action="store_true",
        help="Alias for --section unify_bullets.",
    )
    p.add_argument(
        "--unify-narrative",
        action="store_true",
        help="Alias for --section unify_narrative.",
    )
    p.add_argument(
        "--ibm-bullets",
        action="store_true",
        help="Alias for --section ibm_bullets.",
    )
    p.add_argument(
        "--ibm-narrative",
        action="store_true",
        help="Alias for --section ibm_narrative.",
    )
    p.add_argument(
        "--competencies",
        action="store_true",
        help="Alias for --section competencies.",
    )
    p.add_argument(
        "--provider",
        default=argparse.SUPPRESS,
        choices=["qwen_vllm"],
        help=(
            "Optional override for section-only lanes (qwen_vllm only); when omitted, uses "
            "APPS_RG_MODULAR_LANE_PROVIDER (see apps_rg.l2_recipe.r4_generation_mode). "
            "Ignored for full R4 runs."
        ),
    )
    p.add_argument(
        "--allow-non-allow-exit-zero",
        action="store_true",
        help=(
            "Return process exit 0 even when X3 is not ALLOW for section-only lanes "
            "(override; may also set APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO). Does not change x3_disposition.json."
        ),
    )
    p.add_argument(
        "--x1d-judges",
        default=argparse.SUPPRESS,
        help=(
            "Optional comma-separated X1D judge keys for section lanes; when omitted, uses "
            "APPS_RG_E2E_X1D_JUDGES or the apps_rg default judge list."
        ),
    )
    p.add_argument("--mock-judges", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--allow-test-mock-judges", action="store_true", help=argparse.SUPPRESS)
    p.add_argument(
        "--temperature",
        type=float,
        default=0.45,
        help=(
            "LLM temperature for qwen_vllm in section lanes including competencies "
            "(each lane enforces its own allowed range)."
        ),
    )
    p.add_argument(
        "--selected-role-fact-set",
        default="",
        help=(
            "Optional SelectedRoleFactSet JSON path for generated apps_rg sections. Supplies section-specific "
            "proof pools through selected_facts_by_section.<section_id>. In SRFS mode, each section may only "
            "prove claims using facts assigned to that section."
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
    if getattr(args, "executive_summary", False):
        args.section = "executive_summary"
    if getattr(args, "unify_bullets", False):
        args.section = "unify_bullets"
    if getattr(args, "unify_narrative", False):
        args.section = "unify_narrative"
    if getattr(args, "ibm_bullets", False):
        args.section = "ibm_bullets"
    if getattr(args, "ibm_narrative", False):
        args.section = "ibm_narrative"
    if getattr(args, "competencies", False):
        args.section = "competencies"
    args.non_interactive = not args.interactive

    if not str(getattr(args, "resume", "") or "").strip():
        dr = _default_resume_path()
        if dr:
            args.resume = dr

    section_lane_ids = (
        "headline",
        "executive_summary",
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
        "competencies",
    )
    section_eff = str(getattr(args, "section", "") or "").strip().lower()

    from apps_rg.runtime.qwen_live_only_guard import assert_production_runtime

    if section_eff in section_lane_ids or not section_eff:
        assert_production_runtime(context="python -m apps_rg", args=args)

    from apps_rg.runtime.embedding_settings import (
        apply_apps_rg_embedding_env_guards,
        bootstrap_apps_rg_embedding_env,
        write_embedding_settings_receipt,
    )

    _emb_boot = bootstrap_apps_rg_embedding_env()
    if _emb_boot:
        print(f"embedding_bootstrap: {_emb_boot}", flush=True)
    _emb_settings = apply_apps_rg_embedding_env_guards(route_section=section_eff)
    _emb_ad = str(getattr(args, "artifact_dir", "") or "").strip()
    _emb_receipt = write_embedding_settings_receipt(_emb_ad, _emb_settings)
    print(
        f"embedding_settings: enabled={_emb_settings.embeddings_enabled} "
        f"required={_emb_settings.embedding_required} "
        f"route_result={_emb_settings.route_result} "
        f"semantic_cache_ineligible={_emb_settings.semantic_cache_ineligible} "
        f"chroma_default_ef_used={_emb_settings.chroma_default_ef_used}",
        flush=True,
    )
    if _emb_receipt is not None:
        print(f"embedding_settings_receipt={_emb_receipt.as_posix()}", flush=True)

    if args.interactive:
        _gather_interactive_fields(args)

    if section_eff == "executive_summary":
        from apps_rg.runtime.section_cli_defaults import (
            collect_executive_summary_mandatory_missing,
            validate_executive_summary_mandatory_inputs,
        )

        exec_missing = collect_executive_summary_mandatory_missing(args)
        if exec_missing and args.cursor_prompts:
            sentinel = (
                f"CASCADE_WIZARD_SENTINEL: mandatory inputs missing: "
                f"{', '.join(exec_missing)}. "
                "Please provide target company, target role, JD (--jd), and briefing "
                "(--manual-brief) to proceed."
            )
            print(sentinel, flush=True)
            return 7
        try:
            validate_executive_summary_mandatory_inputs(args)
        except SectionCliConfigError as exc:
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)
            return 2

    # Wizard / cursor-prompts mode: if mandatory inputs are missing, write a
    # sentinel line and exit 7 so the calling process (Cursor Agent IDE) can prompt
    # the user for the missing fields.
    mandatory_missing = []
    if section_eff not in section_lane_ids:
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

    lane_provider_eff: str | None = None
    lane_provider_resolution_source: str | None = None
    if section_eff in section_lane_ids:
        from apps_rg.runtime.section_cli_defaults import resolve_cli_lane_provider_with_source

        try:
            lane_provider_eff, lane_provider_resolution_source = resolve_cli_lane_provider_with_source(
                getattr(args, "provider", None)
            )
        except SectionCliConfigError as exc:
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)
            return 2

    _qdr: dict[str, Any] = {}
    if section_eff in section_lane_ids and lane_provider_eff is not None:
        from apps_rg.runtime.pre_dispatch_preflight import (
            evaluate_jd_cli_input,
            evaluate_manual_brief_cli_input,
            resolve_preflight_receipt_path,
            run_pre_dispatch_preflight,
            write_pre_dispatch_preflight_receipt,
        )

        jd_status, jd_path = evaluate_jd_cli_input(str(getattr(args, "jd", "") or ""))
        brief_status, brief_path = evaluate_manual_brief_cli_input(
            str(getattr(args, "manual_brief", "") or "")
        )
        if jd_status != "PASS" or brief_status != "PASS":
            blocked = run_pre_dispatch_preflight(
                section=section_eff,
                jd=str(getattr(args, "jd", "") or ""),
                manual_brief=str(getattr(args, "manual_brief", "") or ""),
                lane_provider=lane_provider_eff,
                provider_resolution_source=str(lane_provider_resolution_source or ""),
                docker_restart_audit=None,
            )
            receipt_path = resolve_preflight_receipt_path(
                artifact_dir=str(getattr(args, "artifact_dir", "") or ""),
                section=section_eff,
            )
            write_pre_dispatch_preflight_receipt(receipt_path, blocked)
            print(f"ERROR: {blocked.decisive_reason}", file=sys.stderr, flush=True)
            print(f"pre_dispatch_preflight_receipt={receipt_path.as_posix()}", flush=True)
            return 2

    # Optional local Qwen vLLM Docker restart (opt-in — see qwen_vllm_docker_restart module).
    from apps_rg.runtime.qwen_vllm_docker_restart import maybe_restart_qwen_vllm_for_apps_rg_run

    _qdr = maybe_restart_qwen_vllm_for_apps_rg_run(
        running_section_lane=section_eff in section_lane_ids,
        cli_provider=getattr(args, "provider", None),
    )
    if _qdr.get("performed"):
        print(
            f"[apps_rg] qwen_vllm docker restart: container={_qdr.get('container')!r} "
            f"ready={_qdr.get('ready')} probe={_qdr.get('probe_status')!r}",
            flush=True,
        )
    from apps_rg.runtime.qwen_transport_diag import persist_docker_restart_readiness_artifact, set_docker_restart_audit

    set_docker_restart_audit(dict(_qdr))
    _ad = str(getattr(args, "artifact_dir", "") or "").strip()
    if _ad:
        persist_docker_restart_readiness_artifact(_ad, dict(_qdr))

    if section_eff in section_lane_ids and lane_provider_eff is not None:
        from apps_rg.runtime.pre_dispatch_preflight import (
            enforce_pre_dispatch_preflight,
            resolve_preflight_receipt_path,
        )

        try:
            preflight = enforce_pre_dispatch_preflight(
                section=section_eff,
                jd=str(getattr(args, "jd", "") or ""),
                manual_brief=str(getattr(args, "manual_brief", "") or ""),
                lane_provider=lane_provider_eff,
                provider_resolution_source=str(lane_provider_resolution_source or ""),
                artifact_dir=_ad,
                docker_restart_audit=dict(_qdr),
            )
            receipt_path = resolve_preflight_receipt_path(artifact_dir=_ad, section=section_eff)
            print(
                f"pre_dispatch_preflight: dispatch_started={preflight.dispatch_started} "
                f"jd_status={preflight.jd_status} manual_brief_status={preflight.manual_brief_status} "
                f"qwen_health={preflight.qwen_health_status} "
                f"qwen_model_ready={preflight.qwen_model_ready_status}",
                flush=True,
            )
            print(f"pre_dispatch_preflight_receipt={receipt_path.as_posix()}", flush=True)
        except SectionCliConfigError as exc:
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)
            return 2

    if args.dry_run:
        print("DRY RUN: apps_rg pre-dispatch validation complete (no lane runtime).", flush=True)
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
        if section_eff in section_lane_ids:
            from apps_rg.runtime.orchestration.canonical_dispatch import (
                run_canonical_apps_rg_from_cli_primitives,
            )
            from apps_rg.runtime.qwen_live_only_guard import resolve_cli_mock_judges
            from apps_rg.runtime.section_cli_defaults import (
                resolve_allow_non_allow_exit_zero,
                resolve_cli_lane_provider_with_source,
                resolve_cli_x1d_judges,
            )

            if lane_provider_eff is None or lane_provider_resolution_source is None:
                try:
                    lane_provider_eff, lane_provider_resolution_source = (
                        resolve_cli_lane_provider_with_source(getattr(args, "provider", None))
                    )
                except SectionCliConfigError as exc:
                    print(f"ERROR: {exc}", file=sys.stderr, flush=True)
                    return 2
                except RuntimeError as exc:
                    print(f"ERROR: {exc}", file=sys.stderr, flush=True)
                    return 2

            lane_judges_eff = resolve_cli_x1d_judges(getattr(args, "x1d_judges", None))
            lane_mock_eff, lane_allow_test_mock_eff = resolve_cli_mock_judges()
            section_allow_exit = resolve_allow_non_allow_exit_zero(
                bool(getattr(args, "allow_non_allow_exit_zero", False))
            )

            result = run_canonical_apps_rg_from_cli_primitives(
                target_company=args.target_company,
                target_role=args.target_role,
                target_level=args.target_level,
                jd=args.jd,
                manual_brief=args.manual_brief,
                resume_path=args.resume,
                generation_mode=args.generation_mode,
                artifact_dir=args.artifact_dir,
                section=section_eff,
                lane_provider=lane_provider_eff,
                lane_provider_resolution_source=lane_provider_resolution_source,
                lane_temperature=args.temperature,
                lane_x1d_judges=lane_judges_eff,
                lane_mock_judges=lane_mock_eff,
                lane_allow_non_allow_exit_zero=bool(getattr(args, "allow_non_allow_exit_zero", False)),
                lane_allow_test_mock_judges=lane_allow_test_mock_eff,
                selected_role_fact_set=str(getattr(args, "selected_role_fact_set", "") or ""),
            )
        else:
            from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
                run_whole_run_with_route_governance,
            )

            os.environ["APPS_RG_WHOLE_RUN_ENVELOPE"] = "1"
            result = run_whole_run_with_route_governance(
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
            rbz = str((result or {}).get("review_bundle_zip") or "").strip()
            if rbz:
                print(f"review_bundle_zip={rbz}", flush=True)
            if not section_eff and isinstance(result, dict) and result.get("artifact_dir"):
                from apps_rg.runtime.full_run_section_status import emit_full_run_section_status
                from apps_rg.runtime.runtime_proof_layout import is_integrated_whole_run_dir_name

                ad = Path(str(result["artifact_dir"]))
                if is_integrated_whole_run_dir_name(ad.name) or result.get("full_run_section_status_md"):
                    emit_full_run_section_status(ad, print_stdout=True)
        if section_eff in section_lane_ids:
            res_dict = result if isinstance(result, dict) else {}
            allow_exit_flag = bool(getattr(args, "allow_non_allow_exit_zero", False))
            if res_dict.get("fault") == "temperature_range":
                err = str(res_dict.get("error") or "temperature out of range")
                print(err, file=sys.stderr, flush=True)
                emit_cli_section_execution_summary(
                    result=res_dict,
                    lane_provider_resolution_source=lane_provider_resolution_source,
                    allow_non_allow_exit_zero_effective=section_allow_exit,
                    allow_non_allow_cli_flag=allow_exit_flag,
                    process_exit_code=2,
                )
                return 2
            es_txt = str((result or {}).get("executive_summary_cli_output_text") or "").strip()
            if es_txt:
                print(es_txt, flush=True)
            ub_txt = str((result or {}).get("unify_bullets_cli_output_text") or "").strip()
            if ub_txt:
                print(ub_txt, flush=True)
            un_txt = str((result or {}).get("unify_narrative_cli_output_text") or "").strip()
            if un_txt:
                print(un_txt, flush=True)
            ib_txt = str((result or {}).get("ibm_bullets_cli_output_text") or "").strip()
            if ib_txt:
                print(ib_txt, flush=True)
            in_txt = str((result or {}).get("ibm_narrative_cli_output_text") or "").strip()
            if in_txt:
                print(in_txt, flush=True)
            co_txt = str((result or {}).get("competencies_cli_output_text") or "").strip()
            if co_txt:
                print(co_txt, flush=True)
            hl_txt = str((result or {}).get("headline_cli_output_text") or "").strip()
            if hl_txt:
                print(hl_txt, flush=True)
            rc = section_lane_process_exit_code(
                result=res_dict,
                allow_non_allow_exit_zero_effective=section_allow_exit,
            )
            emit_cli_section_execution_summary(
                result=res_dict,
                lane_provider_resolution_source=lane_provider_resolution_source,
                allow_non_allow_exit_zero_effective=section_allow_exit,
                allow_non_allow_cli_flag=allow_exit_flag,
                process_exit_code=rc,
            )
            return rc
        if status != "success" or not authorized:
            return 1
        return 0
    except SectionCliConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 2
    except Exception as exc:
        print(f"ERROR: apps_rg pipeline failed: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
