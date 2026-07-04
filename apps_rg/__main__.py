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
**modular** (eleven section lanes + deterministic merge) when
``APPS_RG_R4_GENERATION_MODE`` is unset — see ``apps_rg.l2_recipe.r4_generation_route``.
Résumé body generation is **modular section lanes only** (``APPS_RG_R4_GENERATION_MODE`` unset or ``modular_section_lanes``).
Offline batch orchestration is library-only under ``tests.helpers.offline_lane_orchestration`` (not product proof);
there is no separate offline orchestrate module CLI.

**L2 model execution (résumé body):** section lanes run on primary ``external_claude``
through ``ProviderGateway``; section policy controls whether any availability fallback
may replace the primary generator output.
Section lanes and integrated runs require a **live** provider bundle (no offline contract stub)
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
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from agentic_core.L2_execution.utils import write_gateway as _wg

from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache
from apps_rg.runtime.cli_section_execution_report import (
    emit_cli_section_execution_summary,
)
from apps_rg.runtime.resume_resolution import DEFAULT_RESUME_SSOT_PATH
from apps_rg.runtime.runtime_proof_layout import (
    find_repo_root,
    is_integrated_whole_run_artifact_dir,
    is_integrated_whole_run_dir_name,
)
from apps_rg.runtime.section_cli_defaults import SectionCliConfigError
from apps_rg.runtime.section_execution_plan import (
    GENERATED_CONTENT_LANES,
    MAX_SECTION_ATTEMPTS,
    is_hard_no_retry_runtime_status,
)

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
    """Emit repo-relative POSIX paths and file:// URIs (legacy editor/VS Code friendly).

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
    _wg.ensure_dir(out)
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
            _wg.copy_file(candidate, out)
            try:
                data = json.loads(out.read_text(encoding="utf-8"))
                if isinstance(data, dict) and company:
                    data.setdefault("company", company)
                    _wg.write_text(out, json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            except (OSError, json.JSONDecodeError, TypeError):
                pass
        else:
            desc = candidate.read_text(encoding="utf-8")
            payload = {
                "title": posting_title,
                "description": desc.strip(),
                "company": company,
            }
            _wg.write_text(out, json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
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
            _wg.write_text(out, json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
            return out

    payload = {
        "title": posting_title,
        "description": jd_guess.strip(),
        "company": company,
    }
    _wg.write_text(out, json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
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
        _wg.write_text(out, body, encoding="utf-8")
        return out

    bp = Path(s)
    if bp.is_file():
        ext = bp.suffix if bp.suffix else ".txt"
        out = session / f"research_brief{ext}"
        _wg.copy_file(bp, out)
        return out

    out = session / "research_brief.txt"
    _wg.write_text(out, s, encoding="utf-8")
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
            args._interactive_cli_inputs_dir = str(session)
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


# Mapping from section id to its primary text-output artifact name. Pinned sections all live
# under artifacts/apps_rg/_pinned/<section>/ with the same filename the lane writes during
# normal runs — see runtime_proofs/<section>/real/<run>/ for reference.
_PINNED_SECTION_TEXT_FILES: tuple[tuple[str, str, str], ...] = (
    ("headline", "headline_output.txt", "Headline"),
    ("executive_summary", "resume_display_text.txt", "Executive Summary"),
    ("competencies", "competencies_display.txt", "Core Competencies"),
    ("unify_bullets", "unify_bullets_output.txt", "Unify (Bullets)"),
    ("unify_narrative", "unify_narrative_output.txt", "Unify (Narrative)"),
    ("ibm_bullets", "ibm_bullets_output.txt", "IBM (Bullets)"),
    ("ibm_narrative", "ibm_narrative_output.txt", "IBM (Narrative)"),
)
_SECTION_PIN_MANIFEST_FILENAME = "section_pin_manifest.json"
_SECTION_PIN_CLEANUP_RECEIPT_FILENAME = "section_pin_cleanup_receipt.json"


def _integrated_run_id_for_path(path: Path) -> str | None:
    """Return the containing ``full_resume_<id>`` directory name, if any."""
    try:
        resolved = Path(path).resolve()
    except OSError:
        resolved = Path(path)
    for candidate in (resolved, *resolved.parents):
        if is_integrated_whole_run_dir_name(candidate.name):
            return candidate.name
    return None


def _read_json_dict(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _write_section_pin_manifest(
    pin_dir: Path,
    *,
    section_id: str,
    source_artifact_dir: Path,
) -> None:
    source_run_id = _integrated_run_id_for_path(source_artifact_dir)
    doc = {
        "schema": "apps_rg.section_pin_manifest.v1",
        "section_id": section_id,
        "source_artifact_dir": source_artifact_dir.as_posix(),
        "source_integrated_run_id": source_run_id,
        "same_e2e_run_required": True,
        "pinned_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _wg.ensure_dir(pin_dir)
    _wg.write_text(
        pin_dir / _SECTION_PIN_MANIFEST_FILENAME,
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _clear_section_pins_for_new_e2e_run(repo_root: Path, artifact_dir: str) -> dict[str, Any]:
    """Remove stale section pins at the start of a fresh whole-run E2E.

    Section pins are scoped to the E2E run that produced them. Starting a new
    whole run clears the carry-over cache before any section lane can consult it.
    """
    repo = Path(repo_root).resolve()
    pin_root = (repo / "artifacts" / "apps_rg" / "_pinned").resolve()
    removed: list[str] = []
    skipped: list[str] = []
    if pin_root.exists():
        for child in sorted(pin_root.iterdir(), key=lambda p: p.name):
            if child.name == "_cleanup_receipts":
                skipped.append(child.name)
                continue
            try:
                child.resolve().relative_to(pin_root)
            except ValueError:
                skipped.append(child.name)
                continue
            if child.is_dir() and not child.is_symlink():
                _wg.remove_tree(child)
            else:
                _wg.remove_file(child)
            removed.append(child.name)

    now = datetime.now(timezone.utc).isoformat()
    receipt: dict[str, Any] = {
        "schema": "apps_rg.section_pin_cleanup.v1",
        "reason": "new_e2e_run_started",
        "pin_validity_scope": "current_e2e_run_only",
        "pin_root": pin_root.as_posix(),
        "removed": removed,
        "removed_count": len(removed),
        "skipped": skipped,
        "cleared_at_utc": now,
    }
    explicit_artifact_dir = str(artifact_dir or "").strip()
    if explicit_artifact_dir:
        receipt_dir = Path(explicit_artifact_dir)
        if not receipt_dir.is_absolute():
            receipt_dir = repo / receipt_dir
        receipt_path = receipt_dir / _SECTION_PIN_CLEANUP_RECEIPT_FILENAME
    else:
        receipt_dir = pin_root / "_cleanup_receipts"
        receipt_path = receipt_dir / f"{now.replace(':', '').replace('+', 'Z')}.json"
    receipt["receipt_path"] = receipt_path.as_posix()
    _wg.ensure_dir(receipt_dir)
    _wg.write_text(
        receipt_path,
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return receipt


def _pin_matches_requested_run(sec_dir: Path, expected_run_id: str) -> tuple[bool, str, dict[str, Any] | None]:
    manifest_path = sec_dir / _SECTION_PIN_MANIFEST_FILENAME
    manifest = _read_json_dict(manifest_path)
    if not manifest:
        return False, "missing_or_unreadable_section_pin_manifest", None
    source_run_id = str(manifest.get("source_integrated_run_id") or "").strip()
    if not source_run_id:
        return False, "pin_has_no_source_integrated_run_id", manifest
    if source_run_id != expected_run_id:
        return False, f"pin_run_mismatch:{source_run_id}!={expected_run_id}", manifest
    return True, "same_e2e_run", manifest


def _assemble_from_pinned_dirs(repo_root: Path, artifact_dir: str) -> int:
    """Stitch artifacts/apps_rg/_pinned/<section>/ outputs into a single markdown resume.

    Each pinned dir is the result of ``--section <id> --attempts N --pin`` accepting at
    REAL_LLM with --accept allow|review. Assembly is mechanical: read the section's
    canonical text artifact, drop empty/missing sections with a clear note, write the
    combined markdown plus a small status JSON. A pin is only consumable by the same
    integrated ``full_resume_<id>`` run that produced it; this prevents a section from a
    prior run/day from being silently stitched into a fresh E2E run after API issues.
    The assembled status stays blocked until every expected pinned section is present,
    so a partial pin set can be inspected but never mislabeled as a finished 11/11.
    No re-validation of X2/X3 — the pin already encoded the disposition.
    """
    pin_root = repo_root / "artifacts" / "apps_rg" / "_pinned"
    out_dir = (
        Path(artifact_dir)
        if str(artifact_dir or "").strip()
        else (repo_root / "artifacts" / "apps_rg" / "_pinned" / "_assembled")
    )
    _wg.ensure_dir(out_dir)
    expected_run_id = _integrated_run_id_for_path(out_dir)
    md_lines: list[str] = []
    status: dict[str, Any] = {
        "sections": {},
        "missing": [],
        "invalid_pins": [],
        "assembled_at": out_dir.as_posix(),
        "expected_integrated_run_id": expected_run_id,
        "same_e2e_run_required": True,
    }
    if not expected_run_id:
        status["status"] = "blocked"
        status["reason"] = "missing_e2e_run_context"
        status_path = out_dir / "assemble_status.json"
        _wg.write_text(status_path, json.dumps(status, indent=2), encoding="utf-8")
        print(
            "PIN_ASSEMBLY_REFUSED reason=missing_e2e_run_context "
            "artifact_dir_must_be_inside_full_resume_run",
            file=sys.stderr,
            flush=True,
        )
        print(f"assemble_status={status_path.as_posix()}", flush=True)
        return 5
    for section_id, fname, label in _PINNED_SECTION_TEXT_FILES:
        sec_dir = pin_root / section_id
        text_path = sec_dir / fname
        x3_path = sec_dir / "x3_disposition.json"
        x3_code = ""
        if x3_path.is_file():
            try:
                x3_code = str(json.loads(x3_path.read_text(encoding="utf-8")).get("x3_code") or "")
            except (json.JSONDecodeError, OSError):
                x3_code = "UNREADABLE"
        if not text_path.is_file():
            status["missing"].append(section_id)
            status["sections"][section_id] = {"present": False, "x3": x3_code}
            md_lines.append(f"## {label}\n\n_(no pinned artifact for `{section_id}`)_\n")
            continue
        pin_ok, pin_reason, pin_manifest = _pin_matches_requested_run(sec_dir, expected_run_id)
        if not pin_ok:
            status["invalid_pins"].append(section_id)
            status["sections"][section_id] = {
                "present": True,
                "usable": False,
                "x3": x3_code,
                "source": text_path.as_posix(),
                "pin_reason": pin_reason,
                "pin_manifest": pin_manifest,
            }
            md_lines.append(
                f"## {label}\n\n_(pinned artifact for `{section_id}` refused: {pin_reason})_\n"
            )
            continue
        body = text_path.read_text(encoding="utf-8").strip()
        status["sections"][section_id] = {
            "present": True,
            "usable": True,
            "x3": x3_code,
            "source": text_path.as_posix(),
            "chars": len(body),
            "pin_reason": pin_reason,
        }
        md_lines.append(f"## {label}\n\n{body}\n")
    md = "# Resume (assembled from pinned sections)\n\n" + "\n".join(md_lines)
    md_path = out_dir / "resume_assembled.md"
    _wg.write_text(md_path, md, encoding="utf-8")
    status_path = out_dir / "assemble_status.json"
    complete = not status["missing"] and not status["invalid_pins"]
    status["complete"] = complete
    if complete:
        status["status"] = "assembled"
    else:
        status["status"] = "blocked"
        status["reason"] = (
            "invalid_section_pin_set"
            if status["invalid_pins"]
            else "incomplete_section_pin_set"
        )
    _wg.write_text(status_path, json.dumps(status, indent=2), encoding="utf-8")
    print(f"ASSEMBLED resume_md={md_path.as_posix()}", flush=True)
    print(f"ASSEMBLE_STATUS missing={','.join(status['missing']) or 'none'}", flush=True)
    if status["invalid_pins"]:
        print(
            f"ASSEMBLE_INVALID_PINS sections={','.join(status['invalid_pins'])}",
            file=sys.stderr,
            flush=True,
        )
    print(f"assemble_status={status_path.as_posix()}", flush=True)
    if status["invalid_pins"]:
        return 5
    return 0 if not status["missing"] else 4


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
        "--disable-existing-index-fallback",
        action="store_true",
        help=(
            "Require canonical non-dry fact-vector hydration proof and refuse fallback to an "
            "already-sufficient dense+sparse Chroma index."
        ),
    )
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
        choices=("", *GENERATED_CONTENT_LANES),
        help=(
            "Run a single section lane through the apps_rg orchestrator "
            "(bypasses whole-run R1A/R1B preflight; default: full R4 product)."
        ),
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
        choices=["external_claude", "external_openai"],
        help=(
            "Optional override for section-only lanes (external_claude or external_openai); when "
            "omitted, uses the lane default for that section. "
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
        "--best-effort-publish-allowed",
        action="store_true",
        help=(
            "Executive summary only: allow pool publish when X2 passes but model-backed judges "
            "do not all pass (publish_disposition=best_effort; proof_eligible=false). "
            "May also set APPS_RG_EXEC_SUMMARY_BEST_EFFORT_PUBLISH_ALLOWED=1."
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
            "LLM temperature for section lanes including competencies "
            "(each lane enforces its own allowed range)."
        ),
    )
    p.add_argument("--artifact-dir", default="", help="Override artifact output directory")
    # In-process best-of-N pin loop (collapses ops_scripts/apps_rg/best_of_n_section_harness.py).
    # Runs the section pipeline up to N times and stops on the first attempt whose runtime
    # disposition matches --accept. No subprocess parsing, no out-of-band re-scanning of
    # timestamped artifact dirs — the lane already returns the artifact dir in result.
    p.add_argument(
        "--attempts",
        type=int,
        default=1,
        help="Best-of-N attempts for a single --section run. Stops on first accepting attempt.",
    )
    p.add_argument(
        "--accept",
        choices=("allow", "review", "any"),
        default="allow",
        help="Acceptance policy for --attempts: allow=X3_ALLOW only; review=ALLOW+SOFT_FAIL; any=any REAL_LLM.",
    )
    p.add_argument(
        "--pin",
        action="store_true",
        help="On accepting attempt, copy the artifact dir to artifacts/apps_rg/_pinned/<section>/.",
    )
    p.add_argument(
        "--assemble-from-pinned",
        action="store_true",
        help="Stitch artifacts/apps_rg/_pinned/<section>/ outputs into a single resume markdown and exit.",
    )
    # W7.1 patch-run mode: re-dispatch ONLY failed lanes of an existing integrated run
    # dir, then re-run the same aggregation/evidence chain. Inputs are re-derived from
    # the run dir's persisted artifacts (never interactive).
    p.add_argument(
        "--patch-run",
        default="",
        help=(
            "Path to an existing integrated run dir: re-dispatch only non-authorized lanes "
            "into the SAME run dir, then re-aggregate. Combine with --sections/--force-lanes/"
            "--dry-run."
        ),
    )
    p.add_argument(
        "--sections",
        default="",
        help=(
            "Patch-run only: comma-separated lane ids to re-dispatch "
            "(default: auto = all non-authorized lanes)."
        ),
    )
    p.add_argument(
        "--force-lanes",
        default="",
        help=(
            "Patch-run only: comma-separated lane ids that MAY be re-dispatched even though "
            "they are currently authorized (without this, green lanes are refused)."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    """CLI entry point for apps_rg.

    Returns exit code (0 = success, 7 = cursor-prompts sentinel).
    """
    _argv = list(argv) if argv is not None else None
    # Diagnostic subcommands intercept the flat run-parser: they own a minimal arg surface and
    # must run on a clean checkout without the full generation schema (G1/G2-preflight,
    # plan apps-rg-e2e-gap-remediation-7e2d9c).
    _tokens = _argv if _argv is not None else sys.argv[1:]
    if _tokens and _tokens[0] == "doctor":
        from apps_rg.runtime.doctor import run_doctor_cli

        return run_doctor_cli(list(_tokens[1:]))
    if _tokens and _tokens[0] == "bootstrap":
        from apps_rg.runtime.fact_vectors_bootstrap import run_bootstrap_cli

        return run_bootstrap_cli(list(_tokens[1:]))
    from apps_rg.runtime.windows_sac_delegate import (
        delegate_apps_rg_to_wsl,
        should_delegate_apps_rg_to_wsl,
    )

    if should_delegate_apps_rg_to_wsl(_argv):
        return delegate_apps_rg_to_wsl(_argv)

    parser = _build_parser()
    args = parser.parse_args(argv)
    # Short-circuit: assemble previously-pinned section artifacts into a single resume.md.
    # Bypasses preflight/provider checks; pinning already proved REAL_LLM eligibility.
    if bool(getattr(args, "assemble_from_pinned", False)):
        return _assemble_from_pinned_dirs(
            repo_root=find_repo_root(),
            artifact_dir=str(getattr(args, "artifact_dir", "") or ""),
        )
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

    section_lane_ids = GENERATED_CONTENT_LANES
    section_eff = str(getattr(args, "section", "") or "").strip().lower()
    _repo_root = find_repo_root()
    from apps_rg.runtime.env_bootstrap import bootstrap_apps_rg_env

    bootstrap_apps_rg_env(repo_root=_repo_root)

    from apps_rg.runtime.live_judge_only_guard import assert_production_runtime, is_test_harness

    if section_eff in section_lane_ids or not section_eff:
        if not is_test_harness():
            assert_production_runtime(context="python -m apps_rg", args=args)

    # W7.1 patch-run mode — re-dispatch only failed lanes of an existing integrated run,
    # re-derive targeting inputs from the run dir's persisted artifacts, re-aggregate.
    # Handles --dry-run itself; never prompts interactively.
    if str(getattr(args, "patch_run", "") or "").strip():
        from apps_rg.runtime.orchestration.patch_run import run_patch_from_cli

        return run_patch_from_cli(args)

    from apps_rg.runtime.embedding_settings import (
        apply_apps_rg_embedding_env_guards,
        bootstrap_apps_rg_embedding_env,
        write_embedding_settings_receipt,
    )

    _emb_boot = bootstrap_apps_rg_embedding_env(repo_root=_repo_root)
    if _emb_boot:
        print(f"embedding_bootstrap: {_emb_boot}", flush=True)
    _emb_settings = apply_apps_rg_embedding_env_guards(route_section=section_eff)
    _emb_ad = str(getattr(args, "artifact_dir", "") or "").strip()
    _emb_receipt = write_embedding_settings_receipt(_emb_ad, _emb_settings)
    try:
        from apps_rg.runtime.c02_chroma_lifecycle import resolve_proof_class

        proof_class = resolve_proof_class()
    except Exception as exc:  # guardian: allow-broad-exception -- diagnostic print must not block pre-U0 readiness fallback
        proof_class = f"unavailable:{type(exc).__name__}"
    try:
        from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

        product_fail_closed = product_fail_closed_runtime()
    except Exception as exc:  # guardian: allow-broad-exception -- diagnostic print must not block pre-U0 readiness fallback
        product_fail_closed = f"unavailable:{type(exc).__name__}"

    print(
        f"embedding_settings: enabled={_emb_settings.embeddings_enabled} "
        f"required={_emb_settings.embedding_required} "
        f"route_result={_emb_settings.route_result} "
        f"semantic_cache_ineligible={_emb_settings.semantic_cache_ineligible} "
        f"chroma_default_ef_used={_emb_settings.chroma_default_ef_used} "
        f"product_fail_closed={product_fail_closed} "
        f"proof_class={proof_class}",
        flush=True,
    )
    if _emb_receipt is not None:
        print(f"embedding_settings_receipt={_emb_receipt.as_posix()}", flush=True)

    if section_eff in section_lane_ids or not section_eff:
        from apps_rg.runtime.fact_vector_readiness import (
            BLOCKED_PRE_U0_FACT_VECTOR_READINESS,
            FactVectorReadinessError,
            PRE_U0_GATE_ID,
            enforce_fact_vector_readiness,
        )

        try:
            pre_u0_receipt = enforce_fact_vector_readiness(
                artifact_dir=_emb_ad,
                gate_id=PRE_U0_GATE_ID,
                block_code=BLOCKED_PRE_U0_FACT_VECTOR_READINESS,
                section=section_eff or "all",
                target_context={
                    "phase": "pre_u0",
                    "section": section_eff or "all",
                    "target_company": str(getattr(args, "target_company", "") or ""),
                    "target_role": str(getattr(args, "target_role", "") or ""),
                },
                allow_existing_index_fallback=not bool(
                    getattr(args, "disable_existing_index_fallback", False)
                ),
            )
            print(
                "pre_u0_fact_vector_readiness: "
                f"status={pre_u0_receipt.get('status')} "
                f"sections={pre_u0_receipt.get('section_count')} "
                f"failed_sections={len(pre_u0_receipt.get('failed_sections') or [])} "
                f"fallback={((pre_u0_receipt.get('fallback') or {}).get('decision') or '—')}",
                flush=True,
            )
            if pre_u0_receipt.get("receipt_path"):
                print(
                    f"pre_u0_fact_vector_readiness_receipt={pre_u0_receipt.get('receipt_path')}",
                    flush=True,
                )
        except FactVectorReadinessError as exc:
            receipt = exc.receipt
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)
            if receipt.get("receipt_path"):
                print(
                    f"pre_u0_fact_vector_readiness_receipt={receipt.get('receipt_path')}",
                    flush=True,
                )
            return 2

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
    # sentinel line and exit 7 so the calling process (Codex IDE) can prompt
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
                getattr(args, "provider", None),
                section_id=section_eff,
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

    # Local-model Docker restart was removed; the external
    # generation provider owns its own transport and needs no container preflight.
    _ad = str(getattr(args, "artifact_dir", "") or "").strip()

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
                f"provider_health={preflight.provider_health_status} "
                f"provider_model_ready={preflight.provider_model_ready_status}",
                flush=True,
            )
            print(f"pre_dispatch_preflight_receipt={receipt_path.as_posix()}", flush=True)
        except SectionCliConfigError as exc:
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)
            return 2

    if section_eff in section_lane_ids or not section_eff:
        from apps_rg.runtime.fact_vector_readiness import (
            BLOCKED_POST_U0_SECTION_SUFFICIENCY,
            FactVectorReadinessError,
            POST_U0_GATE_ID,
            enforce_fact_vector_readiness,
        )

        try:
            post_u0_receipt = enforce_fact_vector_readiness(
                artifact_dir=_ad,
                gate_id=POST_U0_GATE_ID,
                block_code=BLOCKED_POST_U0_SECTION_SUFFICIENCY,
                section=section_eff or "all",
                target_context={
                    "phase": "post_u0_pre_c0",
                    "section": section_eff or "all",
                    "target_company": str(getattr(args, "target_company", "") or ""),
                    "target_role": str(getattr(args, "target_role", "") or ""),
                    "target_level": str(getattr(args, "target_level", "") or ""),
                    "jd_ref": str(getattr(args, "jd", "") or ""),
                    "manual_brief_ref": str(getattr(args, "manual_brief", "") or ""),
                    "lane_provider": str(lane_provider_eff or ""),
                    "provider_resolution_source": str(lane_provider_resolution_source or ""),
                },
                allow_existing_index_fallback=not bool(
                    getattr(args, "disable_existing_index_fallback", False)
                ),
            )
            print(
                "post_u0_section_sufficiency_preview: "
                f"status={post_u0_receipt.get('status')} "
                f"sections={post_u0_receipt.get('section_count')} "
                f"failed_sections={len(post_u0_receipt.get('failed_sections') or [])} "
                f"fallback={((post_u0_receipt.get('fallback') or {}).get('decision') or '—')}",
                flush=True,
            )
            if post_u0_receipt.get("receipt_path"):
                print(
                    f"post_u0_section_sufficiency_preview_receipt={post_u0_receipt.get('receipt_path')}",
                    flush=True,
                )
        except FactVectorReadinessError as exc:
            receipt = exc.receipt
            print(f"ERROR: {exc}", file=sys.stderr, flush=True)
            if receipt.get("receipt_path"):
                print(
                    f"post_u0_section_sufficiency_preview_receipt={receipt.get('receipt_path')}",
                    flush=True,
                )
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
            from apps_rg.runtime.live_judge_only_guard import resolve_cli_mock_judges
            from apps_rg.runtime.orchestration.canonical_dispatch import (
                run_canonical_apps_rg_from_cli_primitives,
            )
            from apps_rg.runtime.section_cli_defaults import (
                resolve_allow_non_allow_exit_zero,
                resolve_cli_lane_provider_with_source,
                resolve_cli_x1d_judges,
            )

            if lane_provider_eff is None or lane_provider_resolution_source is None:
                try:
                    lane_provider_eff, lane_provider_resolution_source = (
                        resolve_cli_lane_provider_with_source(
                            getattr(args, "provider", None),
                            section_id=section_eff,
                        )
                    )
                except SectionCliConfigError as exc:
                    print(f"ERROR: {exc}", file=sys.stderr, flush=True)
                    return 2
                except RuntimeError as exc:
                    print(f"ERROR: {exc}", file=sys.stderr, flush=True)
                    return 2

            lane_judges_eff = resolve_cli_x1d_judges(
                getattr(args, "x1d_judges", None),
                section_id=section_eff,
            )
            lane_mock_eff, lane_allow_test_mock_eff = resolve_cli_mock_judges()
            section_allow_exit = resolve_allow_non_allow_exit_zero(
                bool(getattr(args, "allow_non_allow_exit_zero", False))
            )

            # Best-of-N: rerun the lane up to args.attempts times, stopping on first
            # disposition matching --accept. Each call writes its own timestamped artifact
            # dir; we only PIN the last accepting one (or the final attempt's dir if none
            # accept). No subprocess boundary — the harness is gone.
            # Global retry cap: attempts default to 2 max. Retries are for LOCAL repair only
            # (weak phrasing, judge tie, repairable metric drift) — never to brute-force missing
            # upstream proof. Values above 2 are clamped so these content sections never
            # pay 4x preflight for a section whose dominant failure mode is mechanical or
            # upstream (which more attempts cannot fix).
            attempts = max(1, min(MAX_SECTION_ATTEMPTS, int(getattr(args, "attempts", 1) or 1)))
            accept_mode = str(getattr(args, "accept", "allow") or "allow").lower()
            accepting_dispositions: set[str] = {"X3_ALLOW"}
            if accept_mode in ("review", "any"):
                accepting_dispositions.add("X3_REVIEW_JUDGE_SOFT_FAIL")
                accepting_dispositions.add("X3_REVIEW")
            attempt_history: list[dict[str, Any]] = []
            result = None
            for _attempt_idx in range(1, attempts + 1):
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
                    lane_allow_non_allow_exit_zero=bool(
                        getattr(args, "allow_non_allow_exit_zero", False)
                    ),
                    lane_allow_test_mock_judges=lane_allow_test_mock_eff,
                )
                _res = result if isinstance(result, dict) else {}
                _ad = str(_res.get("artifact_dir") or "")
                # Authoritative source of truth: the section's x3_disposition.json. The CLI
                # result dict may not surface ``runtime_generation_status`` in every dispatch
                # path, but the disposition file always carries both fields.
                _x3 = str(_res.get("x3_disposition") or "")
                _gen = ""
                if _ad:
                    _disp_path = Path(_ad) / "x3_disposition.json"
                    if _disp_path.is_file():
                        try:
                            _disp_blob = json.loads(_disp_path.read_text(encoding="utf-8"))
                            _gen = str(_disp_blob.get("runtime_generation_status") or "")
                            if not _x3:
                                _x3 = str(_disp_blob.get("x3_code") or "")
                        except (json.JSONDecodeError, OSError):
                            pass
                if not _gen:
                    _gen = str(_res.get("runtime_generation_status") or "")
                _accept_any = (accept_mode == "any" and _gen == "REAL_LLM")
                _accept_match = (_gen == "REAL_LLM" and _x3 in accepting_dispositions)
                attempt_history.append(
                    {
                        "attempt": _attempt_idx,
                        "x3": _x3,
                        "runtime_generation_status": _gen,
                        "artifact_dir": _ad,
                        "accepted": bool(_accept_match or _accept_any),
                    }
                )
                if attempts > 1:
                    print(
                        f"[apps_rg --attempts] section={section_eff} "
                        f"attempt {_attempt_idx}/{attempts}: x3={_x3 or 'UNKNOWN'} "
                        f"gen={_gen or 'UNKNOWN'} accepted={_accept_match or _accept_any}",
                        flush=True,
                    )
                if _accept_match or _accept_any:
                    break
                # Variance-class triage: upstream-block runtime statuses are missing-evidence
                # failures (mental model: SC fixes generation variance, more judges fix
                # evaluation variance, deterministic gates fix mechanical rules, UPSTREAM FIXES
                # fix missing evidence). Retrying the same section with the same upstream state
                # cannot resolve any of them — break early so the sweep proceeds to the next
                # section instead of paying preflight again for a guaranteed-fail. The
                # dependency-ordered execution (competencies->bullets->narratives->exec->headline)
                # ensures dependent downstream sections also surface their own upstream block
                # rather than retrying.
                if is_hard_no_retry_runtime_status(_gen):
                    print(
                        f"[apps_rg --attempts] section={section_eff} "
                        f"upstream_blocked_after_attempt_{_attempt_idx} (status={_gen}) — "
                        f"stopping retries; resolve upstream and re-run.",
                        flush=True,
                    )
                    break
            if bool(getattr(args, "pin", False)) and isinstance(result, dict):
                _accepting = bool(attempt_history and attempt_history[-1].get("accepted"))
                _pin_src = str(result.get("artifact_dir") or "")
                if _accepting and _pin_src:
                    from shutil import copytree

                    _pin_dst = (
                        find_repo_root() / "artifacts" / "apps_rg" / "_pinned" / section_eff
                    )
                    _wg.ensure_dir(_pin_dst.parent)
                    if _pin_dst.exists():
                        _wg.remove_tree(_pin_dst)
                    try:
                        copytree(_pin_src, _pin_dst)
                        _write_section_pin_manifest(
                            _pin_dst,
                            section_id=section_eff,
                            source_artifact_dir=Path(_pin_src),
                        )
                        print(
                            f"PINNED section={section_eff} -> {_pin_dst.as_posix()}",
                            flush=True,
                        )
                    except OSError as _exc:
                        print(
                            f"PIN_FAILED section={section_eff} reason={_exc}",
                            file=sys.stderr,
                            flush=True,
                        )
                else:
                    print(
                        f"PIN_SKIPPED section={section_eff} reason=no_accepting_attempt "
                        f"attempts={len(attempt_history)}",
                        flush=True,
                    )
        else:
            from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import (
                run_whole_run_with_route_governance,
            )

            pin_cleanup_receipt: dict[str, Any] | None = None
            if not str(getattr(args, "patch_run", "") or "").strip():
                pin_cleanup_receipt = _clear_section_pins_for_new_e2e_run(
                    find_repo_root(),
                    str(getattr(args, "artifact_dir", "") or ""),
                )
                print(
                    "SECTION_PINS_CLEARED "
                    f"removed_count={pin_cleanup_receipt.get('removed_count', 0)} "
                    f"receipt={pin_cleanup_receipt.get('receipt_path', '')}",
                    flush=True,
                )

            os.environ["APPS_RG_WHOLE_RUN_ENVELOPE"] = "1"
            if bool(getattr(args, "allow_non_allow_exit_zero", False)):
                os.environ["APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO"] = "1"
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
            if pin_cleanup_receipt is not None and isinstance(result, dict):
                result["section_pin_cleanup_receipt"] = pin_cleanup_receipt
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
                from apps_rg.runtime.mandatory_run_outputs import emit_mandatory_run_outputs
                ad = Path(str(result["artifact_dir"]))
                if is_integrated_whole_run_artifact_dir(ad) or result.get("full_run_section_status_md"):
                    repo = find_repo_root()
                    emit_full_run_section_status(ad, repo_root=repo, print_stdout=True)
                    emit_mandatory_run_outputs(
                        ad,
                        result=result,
                        repo_root=repo,
                        print_stdout=True,
                    )
        if section_eff in section_lane_ids:
            res_dict = result if isinstance(result, dict) else {}
            from apps_rg.runtime.c0.c02_fact_vector_ingest import (
                promote_deferred_c02_fact_vectors_after_x3,
            )

            res_dict["fact_vector_deferred_promotion"] = promote_deferred_c02_fact_vectors_after_x3(
                res_dict,
                section_id=section_eff,
            )
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
            tb_op = str((result or {}).get("token_budget_operator_message") or "").strip()
            if tb_op:
                print(tb_op, file=sys.stderr, flush=True)
            for text_key in (
                "executive_summary_cli_output_text",
                "unify_bullets_cli_output_text",
                "unify_narrative_cli_output_text",
                "ibm_bullets_cli_output_text",
                "ibm_narrative_cli_output_text",
                "insurtech_bullets_cli_output_text",
                "insurtech_narrative_cli_output_text",
                "ey_bullets_cli_output_text",
                "ey_narrative_cli_output_text",
                "competencies_cli_output_text",
                "headline_cli_output_text",
            ):
                out_txt = str((result or {}).get(text_key) or "").strip()
                if out_txt:
                    print(out_txt, flush=True)
            if res_dict.get("artifact_dir"):
                from apps_rg.runtime.mandatory_run_outputs import emit_mandatory_run_outputs

                emit_mandatory_run_outputs(
                    Path(str(res_dict["artifact_dir"])),
                    result=res_dict,
                    section_id=section_eff,
                    print_stdout=True,
                )
            from apps_rg.runtime.cli_exit_codes import exit_code_from_lane_result

            rc = exit_code_from_lane_result(res_dict, section_id=section_eff)
            if allow_exit_flag and rc != 0:
                rc = 0
            emit_cli_section_execution_summary(
                result=res_dict,
                lane_provider_resolution_source=lane_provider_resolution_source,
                allow_non_allow_exit_zero_effective=section_allow_exit,
                allow_non_allow_cli_flag=allow_exit_flag,
                process_exit_code=rc,
            )
            return rc
        # Whole-run (no --section) exit code. A whole-run failure must never mask to 0
        # via one section's locally-clean artifact (gap G4). exit_status=="success" AND
        # outcome_authorized => 0; otherwise a specific non-zero code, never EXIT_SUCCESS.
        from apps_rg.runtime.cli_exit_codes import exit_code_from_whole_run_result

        return exit_code_from_whole_run_result(result)
    except SectionCliConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        return 2
    except Exception as exc:
        print(f"ERROR: apps_rg pipeline failed: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
