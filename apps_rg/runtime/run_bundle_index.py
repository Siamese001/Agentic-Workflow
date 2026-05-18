"""RUN_BUNDLE_INDEX.json — discoverability index for apps_rg run directories.

Emitted at the root of ``artifacts/apps_rg/runs/<run_id>/`` (integrated R4) and
``artifacts/apps_rg/runtime_proofs/<lane>/{real|mock}/<run_id>/`` (lane seams).

Does not move or rename legacy artifacts; only adds a sidecar index.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, MutableMapping, cast

_log = logging.getLogger(__name__)

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

RUN_BUNDLE_INDEX_FILENAME = "RUN_BUNDLE_INDEX.json"

_SCHEMA_VERSION = "1"

ContentType = Literal[
    "application/json",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
    "unknown",
]


_WIN_DRIVE_PREFIX = re.compile(r"^[a-zA-Z]:")


def log_run_bundle_index_write_failed(context: str, exc: OSError) -> None:
    """Fail-soft visibility when the index file cannot be written (disk full, permissions)."""
    _log.warning("RUN_BUNDLE_INDEX write failed (%s): %s", context, exc)


def _assert_safe_repo_relative_posix(rel: str) -> None:
    """Reject absolute paths, Windows drive paths, and ``..`` segments (operator safety)."""
    if not rel:
        raise ValueError("empty relative_path")
    if rel.startswith(("/", "\\")):
        raise ValueError(f"absolute or rooted path forbidden: {rel!r}")
    if _WIN_DRIVE_PREFIX.match(rel):
        raise ValueError(f"drive-relative path forbidden: {rel!r}")
    for part in rel.split("/"):
        if part == "..":
            raise ValueError(f"path escape via .. forbidden: {rel!r}")


def _posix_relative_to_repo(repo_root: Path, path: Path) -> str:
    """Stable repo-relative POSIX path; raise if ``path`` is not under ``repo_root``."""
    rr = repo_root.resolve()
    pr = path.resolve()
    try:
        rel = pr.relative_to(rr)
    except ValueError as e:
        raise ValueError(f"path {pr} is not under repo_root {rr}") from e
    posix = rel.as_posix()
    _assert_safe_repo_relative_posix(posix)
    return posix


def repo_relative_posix(repo_root: Path, path: Path) -> str:
    """Public wrapper for validated repo-relative POSIX strings (RUN_LINKS, tooling)."""
    return _posix_relative_to_repo(repo_root, path)


def _finalize_entries(entries: list[dict[str, Any]]) -> None:
    """Ensure no duplicate ``relative_path`` values (final guard)."""
    seen: set[str] = set()
    for e in entries:
        rp = str(e.get("relative_path") or "")
        _assert_safe_repo_relative_posix(rp)
        if rp in seen:
            raise ValueError(f"duplicate RUN_BUNDLE_INDEX entry relative_path: {rp!r}")
        seen.add(rp)


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_apps_rg_namespace_defaults(repo_root: Path) -> dict[str, Any]:
    """SSOT read of ``namespace_defaults`` block (artifact + log + telemetry prefix)."""
    path = repo_root / "config" / "profiles" / "apps_rg" / "pipeline_defaults.yaml"
    default_art = "artifacts/apps_rg/runs"
    default_log = "apps_rg/pipeline_logs"
    out: dict[str, Any] = {
        "artifact_namespace": default_art,
        "log_namespace": default_log,
        "telemetry_prefix": None,
    }
    if not path.is_file() or yaml is None:
        return out
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, TypeError):
        return out
    if not isinstance(raw, MutableMapping):
        return out
    ns = raw.get("namespace_defaults")
    if not isinstance(ns, MutableMapping):
        return out
    art = str(ns.get("artifact_namespace") or "").strip() or default_art
    logn = str(ns.get("log_namespace") or "").strip() or default_log
    out["artifact_namespace"] = art
    out["log_namespace"] = logn
    tp = ns.get("telemetry_prefix")
    if tp is not None and str(tp).strip():
        out["telemetry_prefix"] = str(tp).strip()
    return out


def load_apps_rg_pipeline_namespaces(repo_root: Path) -> tuple[str, str | None]:
    """Read artifact_namespace and log_namespace from pipeline defaults (best-effort)."""
    d = _load_apps_rg_namespace_defaults(repo_root)
    return cast(str, d["artifact_namespace"]), cast(str | None, d.get("log_namespace"))


LogDiscoveryMode = Literal["disk", "telemetry_only", "unavailable"]


def build_log_discovery_metadata(repo_root: Path) -> dict[str, Any]:
    """W3.2 — whether pipeline logs are on disk, telemetry-only, or unknown at emit time.

    ``log_namespace`` is treated as a repo-relative directory intent (from ``pipeline_defaults.yaml``).
    ``mode`` is ``disk`` only when that directory exists. ``telemetry_only`` when it does not but
    ``telemetry_prefix`` is configured. Otherwise ``unavailable``.

    Path safety: unsafe ``log_namespace`` values raise ``ValueError`` (must not be swallowed).
    """
    d = _load_apps_rg_namespace_defaults(repo_root)
    log_ns = str(d.get("log_namespace") or "").strip() or "apps_rg/pipeline_logs"
    tel_raw = d.get("telemetry_prefix")
    telemetry_prefix = str(tel_raw).strip() if tel_raw is not None else ""
    tel_out: str | None = telemetry_prefix if telemetry_prefix else None

    norm = log_ns.replace("\\", "/").strip()
    if not norm:
        raise ValueError("empty log_namespace")
    if norm.startswith(("/", "\\")):
        raise ValueError(f"absolute or rooted log_namespace forbidden: {log_ns!r}")
    if _WIN_DRIVE_PREFIX.match(norm):
        raise ValueError(f"drive-relative log_namespace forbidden: {log_ns!r}")
    for part in norm.split("/"):
        if part == "..":
            raise ValueError(f"log_namespace path escape via .. forbidden: {log_ns!r}")

    abs_log = (repo_root / norm).resolve()
    log_root_rel = repo_relative_posix(repo_root, abs_log)

    mode: LogDiscoveryMode
    path_out: str | None
    notes: str

    if abs_log.is_dir():
        mode = "disk"
        path_out = log_root_rel
        notes = (
            "log_namespace directory exists under the repo; operators may find file logs here if a "
            "sink writes under this path (not guaranteed by apps_rg core emitters)."
        )
    elif tel_out:
        mode = "telemetry_only"
        path_out = None
        notes = (
            f"No on-disk directory at log_namespace `{log_ns}` at index time; "
            f"pipeline_defaults.yaml declares telemetry_prefix `{tel_out}` (OpenTelemetry spans/metrics)."
        )
    else:
        mode = "unavailable"
        path_out = None
        notes = (
            f"No on-disk directory at `{log_ns}` and no telemetry_prefix in pipeline_defaults; "
            "log discovery metadata unavailable."
        )

    return {
        "mode": mode,
        "log_namespace": log_ns,
        "log_root_path": path_out,
        "notes": notes,
    }


def _entry(
    *,
    role: str,
    relative_path: str,
    content_type: str,
    required: bool,
    exists: bool,
    producer: str,
    notes: str | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "role": role,
        "relative_path": relative_path,
        "content_type": content_type,
        "required": required,
        "exists": exists,
        "producer": producer,
    }
    if notes:
        out["notes"] = notes
    return out


def _file_entry(
    repo_root: Path,
    run_dir: Path,
    *,
    role: str,
    relative_suffix: str,
    content_type: str,
    required: bool,
    producer: str,
    notes: str | None = None,
) -> dict[str, Any]:
    norm = relative_suffix.replace("\\", "/")
    if ".." in norm.split("/"):
        raise ValueError(f"unsafe relative_suffix: {relative_suffix!r}")
    path = (run_dir / relative_suffix).resolve()
    exists = path.is_file()
    rel_str = _posix_relative_to_repo(repo_root, path)
    return _entry(
        role=role,
        relative_path=rel_str,
        content_type=content_type,
        required=required,
        exists=exists,
        producer=producer,
        notes=notes,
    )


def _extra_file_entries(
    repo_root: Path,
    run_dir: Path,
    indexed_relpaths: set[str],
    *,
    producer: str,
    role_prefix: str,
) -> list[dict[str, Any]]:
    """Pick up files under ``run_dir`` not listed in predefined roles (flat + ``outputs/``)."""
    out: list[dict[str, Any]] = []
    if not run_dir.is_dir():
        return out
    roots = [run_dir]
    out_sub = run_dir / "outputs"
    if out_sub.is_dir():
        roots.append(out_sub)
    for root in roots:
        for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_file():
                continue
            name = child.name
            if name == RUN_BUNDLE_INDEX_FILENAME:
                continue
            rel_from_bundle = child.resolve().relative_to(run_dir.resolve()).as_posix()
            if rel_from_bundle in indexed_relpaths:
                continue
            ct: ContentType = "application/json" if name.endswith(".json") else (
                "text/plain" if name.endswith(".txt") else "application/octet-stream"
            )
            rel_str = _posix_relative_to_repo(repo_root, child)
            out.append(
                _entry(
                    role=f"{role_prefix}_{name}",
                    relative_path=rel_str,
                    content_type=ct,
                    required=False,
                    exists=True,
                    producer=producer,
                    notes="discovered_at_index_time",
                )
            )
    return out


# Integrated run — known roles (flat + outputs/). required=T = spine contract expectation.
_INTEGRATED_KNOWN: tuple[tuple[str, str, str, bool, str], ...] = (
    ("spine_terminal_ret_packet", "terminal_ret_packet.json", "application/json", True, "integrated_r4_deterministic_pipeline"),
    ("spine_runtime_identity_envelope", "runtime_identity_envelope.json", "application/json", True, "integrated_r4_deterministic_pipeline"),
    ("spine_r4_run_manifest", "r4_run_manifest.json", "application/json", True, "integrated_r4_deterministic_pipeline"),
    ("audit_l7_route_family_coverage", "agentic_core_l7_route_family_coverage.json", "application/json", True, "integrated_r4_deterministic_pipeline"),
    ("audit_how_trace", "agentic_core_how_trace.json", "application/json", True, "integrated_r4_deterministic_pipeline"),
    ("audit_spine_proof", "agentic_core_spine_proof.json", "application/json", False, "integrated_r4_deterministic_pipeline"),
    ("narrative_run_report", "run_report.json", "application/json", False, "apps_rg_narrative_or_auxiliary"),
)

_INTEGRATED_OPTIONAL_OUTPUTS: tuple[tuple[str, str, str, bool, str], ...] = (
    ("product_resume_json_flat", "generated_resume.json", "application/json", False, "apps_rg_resume_assembly"),
    ("product_resume_docx_branded", "Amit_Ayer_Resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False, "apps_rg_docx_export"),
    ("product_resume_json_outputs", "outputs/generated_resume.json", "application/json", False, "apps_rg_resume_assembly"),
    ("product_resume_docx_outputs", "outputs/resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False, "apps_rg_docx_export"),
    ("spine_integrated_manifest", "integrated_runtime_artifact_manifest.json", "application/json", False, "integrated_r4_deterministic_pipeline"),
    ("spine_exit_review_packet", "exit_review_packet.json", "application/json", False, "integrated_r4_deterministic_pipeline"),
    ("spine_runtime_exhaust", "runtime_exhaust_bundle.json", "application/json", False, "integrated_r4_deterministic_pipeline"),
)

# Lane seam — filenames commonly emitted by section lanes (canonical ``python -m apps_rg --section`` runtime proofs).
_LANE_CORE: tuple[tuple[str, str, str, bool, str], ...] = (
    ("lane_run_manifest", "run_manifest.json", "application/json", True, "runtime_proof_layout.finalize_runtime_proof_run"),
    ("lane_l2_output", "l2_output.json", "application/json", True, "apps_rg_canonical_section_runtime"),
    ("lane_runtime_payload", "runtime_payload.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("prompt_compiled_text", "compiled_prompt.txt", "text/plain", False, "apps_rg_canonical_section_runtime"),
    ("prompt_compiled_artifact", "compiled_prompt_artifact.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("prompt_selection_trace", "prompt_selection_trace.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("provider_request", "provider_request.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("provider_response", "provider_response.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("judge_x1d_outputs", "x1d_llm_judge_outputs.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("gate_x2_outputs", "x2_gate_outputs.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("disposition_x3", "x3_disposition.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("l6_shadow_eval_package", "l6_shadow_eval_package.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("fact_check_result", "fact_check_result.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("repair_receipt", "repair_receipt.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("section_metric_receipt", "section_metric_receipt.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("claim_ledger", "claim_ledger.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("text_claim_coverage", "text_claim_coverage.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("selected_fact_plan", "selected_fact_plan.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("stage_sequence", "stage_sequence.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("artifact_inventory", "artifact_inventory.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("runtime_exhaust_bundle", "runtime_exhaust_bundle.json", "application/json", False, "apps_rg_canonical_section_runtime"),
    ("section_runtime_proof_bundle", "section_runtime_proof_bundle.json", "application/json", False, "apps_rg_canonical_section_runtime"),
)

_HEADLINE_PROOF_STRICT_SUFFIXES: frozenset[str] = frozenset(
    {
        "run_manifest.json",
        "l2_output.json",
        "provider_request.json",
        "provider_response.json",
        "prompt_selection_trace.json",
        "compiled_prompt_artifact.json",
        "x1d_llm_judge_outputs.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "claim_ledger.json",
        "selected_fact_plan.json",
        "l6_shadow_eval_package.json",
    }
)
_CANONICAL_HEADLINE_PRODUCER = "apps_rg_canonical_section_headline"


def build_integrated_run_bundle_document(
    repo_root: Path,
    artifact_dir: Path,
    *,
    run_id: str | None,
    correlation_id: str | None,
) -> dict[str, Any]:
    """Build index dict for an integrated R4 run directory."""
    art_ns, log_ns = load_apps_rg_pipeline_namespaces(repo_root)
    rid = str(run_id or "").strip() or artifact_dir.name
    entries: list[dict[str, Any]] = []
    indexed_relpaths: set[str] = set()
    for role, suffix, ct, req, prod in (*_INTEGRATED_KNOWN, *_INTEGRATED_OPTIONAL_OUTPUTS):
        indexed_relpaths.add(suffix.replace("\\", "/"))
        entries.append(_file_entry(repo_root, artifact_dir, role=role, relative_suffix=suffix, content_type=ct, required=req, producer=prod))
    entries.extend(
        _extra_file_entries(
            repo_root,
            artifact_dir,
            indexed_relpaths,
            producer="unknown_or_tests",
            role_prefix="integrated_emitted",
        )
    )
    _finalize_entries(entries)
    log_meta = build_log_discovery_metadata(repo_root)
    doc: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": rid,
        "correlation_id": correlation_id if (correlation_id and str(correlation_id).strip()) else None,
        "created_at": _ts(),
        "bundle_kind": "integrated_run",
        "root_path": _posix_relative_to_repo(repo_root, artifact_dir.resolve()),
        "artifact_namespace": art_ns,
        "log_namespace": log_ns,
        "entries": entries,
    }
    if log_meta.get("mode") == "disk" and log_meta.get("log_root_path"):
        doc["log_root_path"] = log_meta["log_root_path"]
    return doc


def build_lane_runtime_proof_bundle_document(
    repo_root: Path,
    artifact_dir: Path,
    *,
    lane: str,
    run_id: str,
    proof_contract_strict: bool = False,
) -> dict[str, Any]:
    art_ns, log_ns = load_apps_rg_pipeline_namespaces(repo_root)
    rid = str(run_id or "").strip() or artifact_dir.name
    entries: list[dict[str, Any]] = []
    indexed_relpaths: set[str] = set()
    for role, suffix, ct, req, prod in _LANE_CORE:
        indexed_relpaths.add(suffix.replace("\\", "/"))
        norm_suf = suffix.replace("\\", "/")
        if proof_contract_strict and lane == "headline" and norm_suf in _HEADLINE_PROOF_STRICT_SUFFIXES:
            req = True
            prod = _CANONICAL_HEADLINE_PRODUCER
        entries.append(
            _file_entry(
                repo_root,
                artifact_dir,
                role=role,
                relative_suffix=suffix,
                content_type=ct,
                required=req,
                producer=prod,
                notes=f"lane={lane}" if role in ("lane_run_manifest", "lane_l2_output") else None,
            )
        )
    extra_prod = (
        _CANONICAL_HEADLINE_PRODUCER
        if proof_contract_strict and lane == "headline"
        else "apps_rg_canonical_section_runtime"
    )
    entries.extend(
        _extra_file_entries(
            repo_root,
            artifact_dir,
            indexed_relpaths,
            producer=extra_prod,
            role_prefix=f"lane_{lane}_emitted",
        )
    )
    _finalize_entries(entries)
    doc: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": rid,
        "correlation_id": None,
        "created_at": _ts(),
        "bundle_kind": "lane_runtime_proof",
        "lane": lane,
        "root_path": _posix_relative_to_repo(repo_root, artifact_dir.resolve()),
        "artifact_namespace": art_ns,
        "log_namespace": log_ns,
        "entries": entries,
    }
    mf_path = artifact_dir / "run_manifest.json"
    if mf_path.is_file():
        try:
            mfd = json.loads(mf_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            mfd = {}
        if isinstance(mfd, dict):
            for key in (
                "proof_eligible",
                "proof_scope",
                "proof_status",
                "artifact_namespace_class",
                "offline_contract_stub_used",
                "offline_contract_stub_reason",
                "authorization_scope",
                "mocked_judges",
                "runtime_proof_placement_bucket",
                "judge_proof_eligible",
                "provider_proof_eligible",
                "test_only_mock_judges",
                "runtime_generation_status",
                "runtime_generation_status_class",
            ):
                if key in mfd:
                    doc[key] = mfd[key]
    return doc


def write_run_bundle_index(artifact_dir: Path, document: Mapping[str, Any]) -> None:
    path = artifact_dir / RUN_BUNDLE_INDEX_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(document), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def emit_integrated_run_bundle_index(
    repo_root: Path,
    artifact_dir: Path,
    *,
    run_id: str | None,
    correlation_id: str | None = None,
) -> Path:
    """Write RUN_BUNDLE_INDEX.json for an integrated run. Returns intended path (even if write failed)."""
    doc = build_integrated_run_bundle_document(
        repo_root,
        artifact_dir,
        run_id=run_id,
        correlation_id=correlation_id,
    )
    target = artifact_dir / RUN_BUNDLE_INDEX_FILENAME
    try:
        write_run_bundle_index(artifact_dir, doc)
    except OSError as exc:
        log_run_bundle_index_write_failed("emit_integrated_run_bundle_index", exc)

    # W3.1 — correlation manifest (after RUN_BUNDLE_INDEX emission attempt).
    from apps_rg.runtime.run_correlation_links import emit_integrated_run_links

    emit_integrated_run_links(
        repo_root,
        artifact_dir,
        integrated_run_id=run_id,
        correlation_id=correlation_id,
    )

    return target


def emit_lane_runtime_proof_bundle_index(
    repo_root: Path,
    lane: str,
    artifact_dir: Path,
    *,
    run_id: str,
    proof_contract_strict: bool = False,
    document_metadata: Mapping[str, Any] | None = None,
) -> Path:
    """Write RUN_BUNDLE_INDEX.json for a lane runtime proof directory."""
    doc = build_lane_runtime_proof_bundle_document(
        repo_root,
        artifact_dir,
        lane=lane,
        run_id=run_id,
        proof_contract_strict=proof_contract_strict,
    )
    if document_metadata:
        overlap = frozenset(document_metadata.keys()) & frozenset(doc.keys())
        if overlap - frozenset({"entries"}):
            raise ValueError(
                "document_metadata must not collide with canonical RUN_BUNDLE_INDEX keys "
                f"(overlap={sorted(overlap)})"
            )
        doc.update(dict(document_metadata))
    target = artifact_dir / RUN_BUNDLE_INDEX_FILENAME
    try:
        write_run_bundle_index(artifact_dir, doc)
    except OSError as exc:
        log_run_bundle_index_write_failed("emit_lane_runtime_proof_bundle_index", exc)
    return target


def assert_run_bundle_index_document_shape(doc: Mapping[str, Any]) -> None:
    """Validate required top-level keys and per-entry keys (W1/W2 contract tests)."""
    required_top = (
        "schema_version",
        "run_id",
        "correlation_id",
        "created_at",
        "bundle_kind",
        "root_path",
        "artifact_namespace",
        "log_namespace",
        "entries",
    )
    for k in required_top:
        if k not in doc:
            raise ValueError(f"RUN_BUNDLE_INDEX missing top-level key: {k}")
    entries = doc["entries"]
    if not isinstance(entries, list):
        raise ValueError("entries must be a list")
    for i, e in enumerate(entries):
        if not isinstance(e, Mapping):
            raise ValueError(f"entries[{i}] must be an object")
        for ek in ("role", "relative_path", "content_type", "required", "exists", "producer"):
            if ek not in e:
                raise ValueError(f"entries[{i}] missing key: {ek}")


__all__ = [
    "RUN_BUNDLE_INDEX_FILENAME",
    "assert_run_bundle_index_document_shape",
    "build_integrated_run_bundle_document",
    "build_lane_runtime_proof_bundle_document",
    "build_log_discovery_metadata",
    "emit_integrated_run_bundle_index",
    "emit_lane_runtime_proof_bundle_index",
    "load_apps_rg_pipeline_namespaces",
    "log_run_bundle_index_write_failed",
    "repo_relative_posix",
    "write_run_bundle_index",
]
