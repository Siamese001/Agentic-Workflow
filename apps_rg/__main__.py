"""Canonical entrypoint for apps_rg — pure transport shim.

Usage:
    python -m apps_rg --target-company <company> --target-role <role>

Delegates immediately to ``agentic_core.runtime.entrypoints
.integrated_r4_deterministic_pipeline_run`` with ``app_name="apps_rg"``.

apps_rg MUST NOT:
  - resolve L2 recipe
  - construct or pass l2_callable
  - run HOPs, narrative pass, DOCX export
  - call models or build prompts
  - commit cache or write L4
  - call Exit or emit X3

All domain execution is owned by agentic_core via registered L2 step
adapters in ``apps_rg.l2_recipe.steps``.

If the agentic_core runner is unavailable, apps_rg **fails closed** (exit 1).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from apps_rg.cache.r1a_adapter import check_r1a_cache, compute_r1a_key, stamp_r1a_cache
from apps_rg.utils.intent_builder import build_intent_from_request

try:
    from opentelemetry import trace as _otel_trace

    _tracer = _otel_trace.get_tracer("apps_rg.cache")
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    _tracer = None  # type: ignore[assignment]


def _span(name: str):
    """Context manager: OTEL span when available, else no-op."""
    if _OTEL_AVAILABLE and _tracer is not None:
        return _tracer.start_as_current_span(name)
    import contextlib
    return contextlib.nullcontext()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("apps_rg")


# ---------------------------------------------------------------------------
# Fail-closed import of the R4 deterministic pipeline runner
# ---------------------------------------------------------------------------
try:
    from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
        run_integrated_r4_deterministic_pipeline,
        R4IntegratedRunResult,
    )

    _RUNNER_AVAILABLE = True
except ImportError as _import_err:
    _RUNNER_AVAILABLE = False
    _RUNNER_IMPORT_ERROR = _import_err


# ---------------------------------------------------------------------------
# Helpers — transport-level only, no domain logic
# ---------------------------------------------------------------------------


def _get_current_policy_hash() -> str:
    return os.environ.get("APPS_RG_POLICY_HASH", "policy_v1")


def _get_current_blueprint_hash() -> str:
    return os.environ.get("APPS_RG_BLUEPRINT_HASH", "blueprint_v1")


def _hash_file_content(path: Path) -> str:
    """SHA-256 of file content, first 32 hex chars."""
    if not path.exists():
        return "none"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:32]


_DEFAULT_JD_PATH = "apps_rg/scripts/job_description.json"
_DEFAULT_BRIEF_PATH = "apps_rg/scripts/company_research.json"
_DEFAULT_CANDIDATE_PATH = "apps_rg/scripts/candidate_profile.yaml"


def _assert_artifact_matches_company(
    path: Path, target_company: str, artifact_kind: str
) -> None:
    """Fail loud if a JD/briefing artifact references a different company.

    Prevents silent cross-company contamination from hand-authored default
    files tied to a previous target_company. The L0 prerequisite gate also
    catches mismatched briefings via ``_check_scope_match``, but this guard
    fires earlier at intake with an artifact-specific error message.

    No-op when the file is missing (the L0 gate's job) or carries no
    ``company`` field (e.g. master candidate profile).
    """
    if not path.exists() or not target_company:
        return
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(text)
        elif path.suffix.lower() in (".yaml", ".yml"):
            import yaml  # local import — yaml is optional for json-only paths

            data = yaml.safe_load(text)
        else:
            return
    except (OSError, json.JSONDecodeError, ValueError):
        return
    if not isinstance(data, dict):
        return
    file_company = str(data.get("company") or "").strip()
    if not file_company:
        return  # Artifact has no company assertion — nothing to contradict
    if file_company.lower() != target_company.strip().lower():
        raise SystemExit(
            f"FATAL: {artifact_kind} at {path} declares company={file_company!r} "
            f"but --target-company={target_company!r}. Refusing to proceed with a "
            f"cross-company contaminated artifact. Supply a {artifact_kind} matching "
            f"{target_company!r}, or omit --{artifact_kind.replace('_', '-')} to let "
            f"the L0 prerequisite gate route to apps_research."
        )


def _build_raw_request(args) -> dict[str, Any]:
    """Build the raw_request envelope from parsed CLI args.

    This dict is the contract surface between apps_rg and the R4 pipeline.
    It contains only transport-level data — no executable code.
    """
    target_company = (args.target_company or "").strip()

    jd_arg: str = getattr(args, "jd", "") or ""
    jd_path = Path(jd_arg or _DEFAULT_JD_PATH)
    _assert_artifact_matches_company(jd_path, target_company, "jd")

    # Brief path: pass through user-supplied path unchanged. NEVER silently
    # substitute a different company's briefing file. If user gave a path that
    # does not exist, the L0 prerequisite gate will see MISSING and route to
    # apps_research — that is the correct behavior, not a fallback.
    brief_arg: str = getattr(args, "manual_brief", "") or ""
    brief_path = Path(brief_arg or _DEFAULT_BRIEF_PATH)
    _assert_artifact_matches_company(brief_path, target_company, "manual_brief")

    candidate_path = (
        Path(args.candidate) if getattr(args, "candidate", None) else Path(_DEFAULT_CANDIDATE_PATH)
    )

    jd_payload: dict[str, Any] = {}
    if jd_path.exists():
        try:
            jd_payload = json.loads(jd_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    raw = {
        "transport": "api",
        "method": "POST",
        "jd_path_resolved": str(jd_path),
        "content_type": "application/json",
        "source_channel": "apps_rg_cli",
        "declared_schema": "apps_rg_jd_v1",
        "body_text": json.dumps(jd_payload) if jd_payload else "{}",
        "tenant_id": getattr(args, "tenant_id", "default"),
        "user_id": "u-apps_rg",
        "target_company": args.target_company or "",
        "target_role": args.target_role or "",
        "jd_payload": jd_payload,  # DS-R7: must be dict; consumed by L1_cognition
        "jd_hash": _hash_file_content(jd_path),
        "brief_hash": _hash_file_content(brief_path),
        "resume_hash": _hash_file_content(candidate_path),
        "policy_hash": _get_current_policy_hash(),
        "blueprint_hash": _get_current_blueprint_hash(),
        "manual_brief": str(brief_path),
        "research_via": getattr(args, "research_via", None),
        "auto_research_internal": getattr(args, "auto_research_internal", False),
        "auto_research_tavily": getattr(args, "auto_research_tavily", False),
    }
    assert isinstance(raw["jd_payload"], dict), (
        f"apps_rg: jd_payload must be a dict, got {type(raw['jd_payload']).__name__}"
    )
    return raw


# ---------------------------------------------------------------------------
# Core pipeline logic — extracted for testability
# ---------------------------------------------------------------------------


def _run_with_args(
    args: Any,
    runs_dir: Path | None = None,
    artifact_dir_override: Path | None = None,
) -> None:
    """Execute the full L0-wired pipeline given parsed CLI args.

    Extracted from ``main()`` so tests can inject args directly without
    going through argparse or subprocess.  Calls ``sys.exit`` on all paths.

    Parameters
    ----------
    args:
        Namespace-like object with target_company, target_role, candidate,
        jd, manual_brief, target_level, tenant_id, etc.
    runs_dir:
        Override the directory scanned for R1A cache entries.
        Defaults to ``artifacts/apps_rg/runs``.
    artifact_dir_override:
        Override the per-run artifact directory (used by tests to pre-seed
        ``generated_resume.json`` for R1B store testing).
    """
    raw_request = _build_raw_request(args)
    _runs_dir = runs_dir if runs_dir is not None else Path("artifacts/apps_rg/runs")
    artifact_dir = (
        artifact_dir_override
        if artifact_dir_override is not None
        else _runs_dir / f"r4_{raw_request['resume_hash'][:8]}"
    )

    # ── Single source of truth: resolve all paths from raw_request (not args) ──
    # The interactive wizard (TTY only, in main()) mutates args.* before this
    # point so that target_company / target_role / jd / manual_brief are
    # populated from prompts when not supplied on CLI. Non-TTY runs require
    # explicit flags (parser.error() in main()).
    jd_path = Path(raw_request.get("jd_path_resolved") or getattr(args, "jd", "") or "apps_rg/scripts/job_description.json")
    brief_path = Path(raw_request["manual_brief"])
    candidate_path = (
        Path(args.candidate) if getattr(args, "candidate", None)
        else Path("apps_rg/scripts/candidate_profile.yaml")
    )

    # ── L0 prerequisite gate: briefing validation before R4 ──
    try:
        from agentic_core.L0_routing.gates.apps_rg_prerequisite_gate import check_apps_rg_prerequisites
        _prereq = check_apps_rg_prerequisites(
            target_company=raw_request["target_company"],
            target_role=raw_request["target_role"],
            policy_hash=raw_request["policy_hash"],
            blueprint_hash=raw_request["blueprint_hash"],
            trace_id=raw_request.get("tenant_id", "default"),
            briefing_path=brief_path,
        )
        if _prereq is not None:
            from agentic_core.L0_routing.types.routing_artifact_types import L0Route
            _sel = _prereq.get("selected_route")
            if _sel == L0Route.R5:
                _log.error(
                    "[apps_rg] L0 prerequisite gate: briefing incompatible — %s. "
                    "Check briefing file at %s.",
                    _prereq.get("reason_codes"),
                    brief_path,
                )
                sys.exit(1)
            if _sel == L0Route.R3R4_MANAGED:
                _log.warning(
                    "[apps_rg] L0 prerequisite gate: briefing MISSING or STALE for '%s'. "
                    "Run apps_research first to generate a fresh briefing, "
                    "then re-run apps_rg with --manual-brief <path>.",
                    raw_request["target_company"],
                )
                sys.exit(1)
    except ImportError:
        _log.debug("[apps_rg] L0 prerequisite gate unavailable (fail-open)")
    except Exception as _gate_err:
        _log.warning("[apps_rg] L0 prerequisite gate failed (fail-soft): %s", _gate_err)

    # ── W1 / GAP-1: R1A exact-cache pre-flight ──
    r1a_key = compute_r1a_key(
        source_resume_hash=raw_request["resume_hash"],
        target_company=raw_request["target_company"],
        target_role=raw_request["target_role"],
        jd_hash=raw_request["jd_hash"],
        briefing_hash=raw_request["brief_hash"],
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )
    with _span("apps_rg.cache.r1a.check") as r1a_span:
        cached_run_dir = check_r1a_cache(
            r1a_key,
            runs_dir=_runs_dir,
            policy_hash=raw_request["policy_hash"],
            blueprint_hash=raw_request["blueprint_hash"],
        )
        if _OTEL_AVAILABLE and r1a_span is not None:
            r1a_span.set_attribute("cache.layer", "r1a")
            r1a_span.set_attribute("cache.result", "hit" if cached_run_dir else "miss")
            r1a_span.set_attribute("cache.key_prefix", r1a_key[:16])
    if cached_run_dir is not None:
        _log.info("[apps_rg] R1A exact cache hit — returning cached run at %s", cached_run_dir)
        sys.exit(0)

    # ── W2 / GAP-2: R1B semantic-cache pre-flight (gated by env flag) ──
    if os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1":
        try:
            from apps_rg.cache.r1b_adapter import check_r1b_for_apps_rg

            with _span("apps_rg.cache.r1b.check") as r1b_span:
                r1b_hit = check_r1b_for_apps_rg(
                    candidate_profile_path=str(candidate_path),
                    target_company=args.target_company,
                    target_role=args.target_role,
                    policy_hash=raw_request["policy_hash"],
                    blueprint_hash=raw_request["blueprint_hash"],
                    jd_path=jd_path,
                    briefing_path=brief_path,
                    tenant_id=raw_request.get("tenant_id", "default"),
                )
                if _OTEL_AVAILABLE and r1b_span is not None:
                    r1b_span.set_attribute("cache.layer", "r1b")
                    r1b_span.set_attribute("cache.result", "hit" if r1b_hit else "miss")
                    if r1b_hit is not None:
                        _sim = r1b_hit.get("_cache_similarity_score")
                        if _sim is not None:
                            r1b_span.set_attribute("cache.similarity_score", _sim)
            if r1b_hit is not None:
                _log.info("[apps_rg] R1B semantic cache hit — returning cached result")
                sys.exit(0)
        except Exception as _r1b_err:  # guardian: allow-broad-exception -- R1B recall is fail-soft; a miss is always safe
            _log.warning("[apps_rg] R1B recall failed (fail-soft): %s", _r1b_err)

    # ── Delegate to agentic_core R4 pipeline (core resolves L2 recipe) ──
    result: R4IntegratedRunResult = run_integrated_r4_deterministic_pipeline(
        app_name="apps_rg",
        raw_request=raw_request,
        artifact_dir=artifact_dir,
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )

    _log.info(
        "[apps_rg] R4 pipeline complete: run_id=%s x3=%s terminal_r5=%s fault=%s",
        result.run_id,
        result.x3_disposition,
        result.terminal_r5,
        result.fault or "(none)",
    )

    # ── W4 / GAP-4: R1A post-run stamp (only on clean execution) ──
    if not result.fault and not result.terminal_r5:
        try:
            with _span("apps_rg.cache.r1a.stamp") as r1a_stamp_span:
                stamp_r1a_cache(
                    r1a_key,
                    str(artifact_dir),
                    policy_hash=raw_request["policy_hash"],
                    blueprint_hash=raw_request["blueprint_hash"],
                )
                if _OTEL_AVAILABLE and r1a_stamp_span is not None:
                    r1a_stamp_span.set_attribute("cache.layer", "r1a")
                    r1a_stamp_span.set_attribute("cache.operation", "stamp")
            _log.debug("[apps_rg] R1A cache stamped for key=%s", r1a_key[:16])
        except Exception as _stamp_err:  # guardian: allow-broad-exception -- cache stamp is fail-soft; run already succeeded
            _log.warning("[apps_rg] R1A stamp failed (fail-soft): %s", _stamp_err)

    # ── W4 / GAP-5: R1B post-run store (only on clean execution, gated by env flag) ──
    if not result.fault and not result.terminal_r5 and os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1":
        try:
            from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter

            intent = build_intent_from_request(
                candidate_profile_path=candidate_path,
                target_company=args.target_company,
                target_role=args.target_role,
                target_level=getattr(args, "target_level", None),
                policy_hash=raw_request["policy_hash"],
                blueprint_hash=raw_request["blueprint_hash"],
                jd_path=jd_path,
                briefing_path=brief_path,
                tenant_id=raw_request.get("tenant_id", "default"),
                request_id=result.run_id,
            )
            generated_resume_path = artifact_dir / "generated_resume.json"
            output_chunks: list[dict] = []
            if generated_resume_path.exists():
                try:
                    resume_data = json.loads(generated_resume_path.read_text(encoding="utf-8"))
                    output_chunks = resume_data if isinstance(resume_data, list) else [resume_data]
                except (json.JSONDecodeError, OSError):
                    pass
            if output_chunks:
                adapter = AppsRgR1BCacheAdapter(
                    tenant_id=raw_request.get("tenant_id", "default")
                )
                with _span("apps_rg.cache.r1b.store") as r1b_store_span:
                    adapter.store_intent_and_output(
                        intent=intent,
                        output_chunks=output_chunks,
                        run_context={
                            "run_id": result.run_id,
                            "exit_disposition": result.x3_disposition,
                            "uwg_commit_receipt": result.run_id,
                            "policy_hash": raw_request["policy_hash"],
                            "blueprint_hash": raw_request["blueprint_hash"],
                        },
                    )
                    if _OTEL_AVAILABLE and r1b_store_span is not None:
                        r1b_store_span.set_attribute("cache.layer", "r1b")
                        r1b_store_span.set_attribute("cache.operation", "store")
                        r1b_store_span.set_attribute("cache.chunks_stored", len(output_chunks))
                _log.debug("[apps_rg] R1B semantic cache stored %d chunks", len(output_chunks))
        except Exception as _store_err:  # guardian: allow-broad-exception -- R1B store is fail-soft; run already succeeded
            _log.warning("[apps_rg] R1B store failed (fail-soft): %s", _store_err)

    if result.fault:
        _log.error("[apps_rg] Pipeline fault: %s", result.fault)
        sys.exit(1)

    sys.exit(0)


# ---------------------------------------------------------------------------
# Main entrypoint — pure shim
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse transport args → delegate to agentic_core R4 pipeline."""

    # ── Fail-closed guard ──
    if not _RUNNER_AVAILABLE:
        print(
            f"FATAL: agentic_core runner unavailable — apps_rg fails closed.\n"
            f"  ImportError: {_RUNNER_IMPORT_ERROR}",
            file=sys.stderr,
        )
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser(prog="apps_rg", add_help=True)
    parser.add_argument("--target-company", default=None, help="Target company")
    parser.add_argument("--target-role", default=None, help="Target role title")
    parser.add_argument("--research-via", default=None, choices=["apps_research"])
    parser.add_argument("--auto-research-internal", action="store_true")
    parser.add_argument("--auto-research-tavily", action="store_true")
    parser.add_argument("--manual-brief", default=None, help="Path to company briefing JSON. Must match --target-company; never falls back to a different company's file.")
    parser.add_argument("--candidate", default=None, help="Candidate profile path")
    parser.add_argument("--target-level", default=None)
    parser.add_argument("--jd", default=None, help="Job description JSON path")
    args, _unknown = parser.parse_known_args()

    # ── Interactive wizard (TTY only) ────────────────────────────────────
    # When stdin is attached to a TTY and any of the 3 mandatory inputs
    # (company, JD title+description, briefing document) is missing, run a
    # guided prompt instead of hard-failing. Non-TTY (CI/pipe) keeps the
    # strict parser.error path below to preserve scripted-run contracts.
    #
    # The wizard writes JD and briefing to dedicated _interactive_*.json
    # files (NOT the hand-authored default files) so the cross-company
    # contamination guard still validates them with the freshly-typed
    # company name, never with a stale prior-company artifact.
    if sys.stdin.isatty() and (
        not args.target_company or not args.target_role or not args.jd
    ):
        _interactive_wizard(args)

    # ── --target-company and --target-role MUST be supplied explicitly. ──
    # Auto-deriving from the hand-authored default JSONs (whoever last filled
    # apps_rg/scripts/company_research.json / job_description.json) is a
    # cross-company contamination risk: every prior-resume artifact in this
    # repo would silently re-target the previous company. Hardened intentionally.
    if not args.target_company:
        parser.error(
            "--target-company is required. Pass it explicitly; apps_rg refuses to "
            "infer it from a hand-authored default file (would risk silently using "
            "a prior company's research as the target)."
        )
    if not args.target_role:
        parser.error(
            "--target-role is required. Pass it explicitly; apps_rg refuses to "
            "infer it from a hand-authored default JD file (would risk silently "
            "reusing a prior role's framing)."
        )

    _run_with_args(args)


# ---------------------------------------------------------------------------
# Interactive wizard — TTY-only prompt for the 3 mandatory inputs
# ---------------------------------------------------------------------------


_WIZARD_JD_PATH = Path("apps_rg/scripts/_interactive_jd.json")
_WIZARD_BRIEF_PATH = Path("apps_rg/scripts/_interactive_brief.json")


def _read_multiline_or_file(prompt_label: str) -> tuple[str, str | None]:
    """Read input that may be (a) multiline pasted text terminated by 'END',
    or (b) ``@/abs/or/rel/path`` to load file content.

    Returns ``(text, source_marker)`` where ``source_marker`` is the file
    path when loaded from disk, else ``None``. Empty input returns
    ``("", None)``.
    """
    print(f"  Paste {prompt_label} (or '@path/to/file' to load, type 'END' on its own line to finish):")
    first = input("  > ").strip()
    if not first:
        return "", None
    if first.startswith("@"):
        path = first[1:].strip()
        try:
            return Path(path).read_text(encoding="utf-8"), path
        except OSError as exc:
            print(f"    [warn] could not read {path}: {exc}")
            return "", None
    if first == "END":
        return "", None
    lines = [first]
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines), None


def _interactive_wizard(args: Any) -> None:
    """Prompt the user for the 3 mandatory inputs and mutate ``args`` in place.

    The 3 items:
      1. **Company** — target company string
      2. **JD** — job title + full description (paste multiline, '@file' load)
      3. **Briefing** — company briefing document (paste, '@file', or 'auto'
         to delegate retrieval to apps_research / Tavily)

    Side effects:
      - Writes ``apps_rg/scripts/_interactive_jd.json``
      - Writes ``apps_rg/scripts/_interactive_brief.json`` (unless 'auto')
      - Sets ``args.target_company``, ``args.target_role``, ``args.jd``,
        ``args.manual_brief`` and/or ``args.auto_research_tavily``.
    """
    print()
    print("=" * 70)
    print("apps_rg interactive setup — 3 mandatory inputs")
    print("=" * 70)
    print(
        "Cascade discipline: this prompt fires because target_company / "
        "target_role / jd were not supplied on the command line. apps_rg "
        "refuses to auto-infer them from stale default files in "
        "apps_rg/scripts/ to prevent cross-company contamination."
    )
    print()

    # --- 1. Company ----------------------------------------------------
    while not args.target_company:
        company = input("[1/3] Target company (e.g. 'Brown & Brown'): ").strip()
        if company:
            args.target_company = company
    print(f"      → company = {args.target_company!r}")
    print()

    # --- 2. JD title + description -------------------------------------
    print("[2/3] Job description")
    title = ""
    while not title:
        title = (args.target_role or "").strip() or input("  Job title: ").strip()
    args.target_role = title

    description, source = _read_multiline_or_file("the full job description")
    if not description.strip():
        print("    [warn] empty JD description; using title-only stub")
        description = f"(no description provided — title only: {title})"

    jd_payload = {
        "title": title,
        "description": description,
        "requirements": [],
        "preferred": [],
        "_source": source or "interactive_paste",
        "company": args.target_company,
    }
    _WIZARD_JD_PATH.parent.mkdir(parents=True, exist_ok=True)
    _WIZARD_JD_PATH.write_text(json.dumps(jd_payload, indent=2), encoding="utf-8")
    args.jd = str(_WIZARD_JD_PATH)
    print(f"      → wrote JD to {args.jd}")
    print()

    # --- 3. Briefing document ------------------------------------------
    print("[3/3] Company briefing document")
    print("      Options:")
    print("        - 'auto'              → delegate to apps_research (Tavily)")
    print("        - '@path/to/file.json' → load existing brief from disk")
    print("        - paste multiline JSON or text, terminate with 'END'")
    choice = input("  > ").strip()

    if choice.lower() == "auto":
        args.auto_research_tavily = True
        args.manual_brief = None
        print("      → auto-research-tavily ENABLED; apps_research will produce briefing")
    elif choice.startswith("@"):
        path = choice[1:].strip()
        if not Path(path).exists():
            print(f"      [warn] {path} not found; falling back to auto-research")
            args.auto_research_tavily = True
            args.manual_brief = None
        else:
            args.manual_brief = path
            print(f"      → manual_brief = {path}")
    else:
        # Treat as start of multiline paste; read until 'END'
        lines = [choice] if choice else []
        while True:
            try:
                line = input("  > ")
            except EOFError:
                break
            if line.strip() == "END":
                break
            lines.append(line)
        text = "\n".join(lines).strip()
        if not text:
            print("      [warn] empty briefing; falling back to auto-research")
            args.auto_research_tavily = True
            args.manual_brief = None
        else:
            # Try parse as JSON; if not, wrap as plain-text briefing dict
            try:
                brief_payload = json.loads(text)
                if isinstance(brief_payload, dict) and "company" not in brief_payload:
                    brief_payload["company"] = args.target_company
            except json.JSONDecodeError:
                brief_payload = {
                    "company": args.target_company,
                    "_source": "interactive_paste_freeform",
                    "freeform_text": text,
                }
            _WIZARD_BRIEF_PATH.parent.mkdir(parents=True, exist_ok=True)
            _WIZARD_BRIEF_PATH.write_text(
                json.dumps(brief_payload, indent=2), encoding="utf-8"
            )
            args.manual_brief = str(_WIZARD_BRIEF_PATH)
            print(f"      → wrote briefing to {args.manual_brief}")
    print()
    print("=" * 70)
    print(f"Ready: company={args.target_company!r} role={args.target_role!r}")
    print(f"       jd={args.jd}")
    print(
        f"       brief={'auto-research-tavily' if args.auto_research_tavily else args.manual_brief}"
    )
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
