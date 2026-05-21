"""RUN_LINKS.json — correlation manifest beside integrated runs (W3.1).

Emits ``artifacts/apps_rg/runs/<run_id>/RUN_LINKS.json`` next to ``RUN_BUNDLE_INDEX.json``.
Lane linkage is conservative: literal repo paths under ``artifacts/apps_rg/runtime_proofs/…``
found in integrated-run JSON/text (shallow scan). Optional correlation filter when lane
``RUN_BUNDLE_INDEX`` carries a non-null ``correlation_id``.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.run_bundle_index import (
    RUN_BUNDLE_INDEX_FILENAME,
    build_log_discovery_metadata,
    load_apps_rg_pipeline_namespaces,
    repo_relative_posix,
)
from apps_rg.runtime.runtime_proof_layout import (
    MODULAR_R4_SECTIONS_ROOT_ENV,
    modular_sections_root_from_env,
)
from apps_rg.runtime.sections_root_manifest import SECTIONS_ROOT_MANIFEST_FILENAME
RUN_LINKS_FILENAME = "RUN_LINKS.json"

_SCHEMA_VERSION = "1"

AGG_ROLLUP_REL = "artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json"

_LOG = logging.getLogger(__name__)

_lane_path_re = re.compile(
    r"artifacts/apps_rg/runtime_proofs/"
    r"(?!generated_lane_rollup/?)(?!final_resume_assembly/?)(?!locked_copy/?)(?!docx/?)"
    r"([^/\\\s\"\]]+)/(real|mock)/([^/\\\s\"\]]+)",
)

_final_resume_re = re.compile(
    r"artifacts/apps_rg/runtime_proofs/final_resume_assembly[^\s\"\]]+\.json",
)

_POSIX_UNSAFE_DRIVE = re.compile(r"^[a-zA-Z]:")


def _assert_run_links_posix_path(rel: str, ctx: str) -> None:
    """Match RUN_BUNDLE_INDEX path-safety for operator-facing relative strings."""
    if not rel:
        raise ValueError(f"{ctx}: empty path")
    if rel.startswith(("/", "\\")):
        raise ValueError(f"{ctx}: absolute or rooted path forbidden: {rel!r}")
    if _POSIX_UNSAFE_DRIVE.match(rel):
        raise ValueError(f"{ctx}: drive-relative path forbidden: {rel!r}")
    for part in rel.split("/"):
        if part == "..":
            raise ValueError(f"{ctx}: path escape via .. forbidden: {rel!r}")


def log_run_links_write_failed(context: str, exc: OSError) -> None:
    _LOG.warning("RUN_LINKS write failed (%s): %s", context, exc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _gather_integrated_corpus(integrated_dir: Path, *, max_chars: int = 512_000) -> str:
    chunks: list[str] = []
    total = 0
    for d in (integrated_dir, integrated_dir / "contracts", integrated_dir / "outputs"):
        if not d.is_dir():
            continue
        for pattern in ("*.json", "*.txt"):
            for p in sorted(d.glob(pattern)):
                if not p.is_file():
                    continue
                raw = _safe_read_text(p)
                if not raw:
                    continue
                if total + len(raw) > max_chars:
                    return "\n".join(chunks)
                chunks.append(raw)
                total += len(raw)
    return "\n".join(chunks)


def _proof_mode(bucket: str) -> str:
    b = bucket.strip().lower()
    if b == "real":
        return "real"
    if b == "mock":
        return "mock"
    return "unknown"


def _lane_index_doc(run_dir: Path) -> Mapping[str, Any] | None:
    p = run_dir / RUN_BUNDLE_INDEX_FILENAME
    if not p.is_file():
        return None
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return j if isinstance(j, Mapping) else None


def finalize_lane_bundle_ref_rows(
    triple_map: dict[tuple[str, str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    """Dedupe rows that share ``bundle_index_ref``; lexicographically smallest triple wins."""

    by_bundle_index: dict[str, dict[str, Any]] = {}
    for _k, entry in sorted(triple_map.items(), key=lambda kv: kv[0]):
        bref = entry["bundle_index_ref"]
        if bref not in by_bundle_index:
            by_bundle_index[bref] = entry
            continue
        prev = by_bundle_index[bref]
        prev_k = (prev["lane"], prev["proof_mode"], prev["run_id"])
        new_k = (entry["lane"], entry["proof_mode"], entry["run_id"])
        if new_k < prev_k:
            by_bundle_index[bref] = entry

    return sorted(by_bundle_index.values(), key=lambda e: (e["lane"], e["proof_mode"], e["run_id"]))


def discover_lane_bundle_refs(
    repo_root: Path,
    corpus: str,
    *,
    correlation_id: str | None,
) -> list[dict[str, Any]]:
    """One deterministic row per ``(lane, proof_mode, run_id)``.

    If the discovered ``RUN_BUNDLE_INDEX`` has a non-empty ``correlation_id`` that
    disagrees with the integrated ``correlation_id`` argument, the candidate is skipped.

    Dedupes conflicting ``bundle_index_ref`` collisions by retaining the smallest
    ``(lane, proof_mode, run_id)`` lexicographically.
    """
    rr = repo_root.resolve()
    corr_strip = str(correlation_id).strip() if correlation_id else ""

    triple_map: dict[tuple[str, str, str], dict[str, Any]] = {}

    for lane_raw, bucket_raw, rid_raw in sorted(set(_lane_path_re.findall(corpus))):
        lane = lane_raw.strip()
        bucket = bucket_raw.strip()
        rid = rid_raw.strip()
        pmode = _proof_mode(bucket)
        if pmode == "unknown":
            continue
        run_abs = rr / "artifacts" / "apps_rg" / "runtime_proofs" / lane / bucket / rid
        try:
            root_posix = repo_relative_posix(repo_root, run_abs)
        except ValueError:
            continue

        idx = _lane_index_doc(run_abs) if run_abs.is_dir() else None
        if corr_strip and idx is not None:
            lc = idx.get("correlation_id")
            if lc is not None and str(lc).strip() != "" and str(lc).strip() != corr_strip:
                continue

        bundle_abs = run_abs / RUN_BUNDLE_INDEX_FILENAME
        try:
            bundle_ix_posix = repo_relative_posix(repo_root, bundle_abs)
        except ValueError:
            continue

        entry = {
            "lane": lane,
            "proof_mode": pmode,
            "run_id": rid,
            "bundle_index_ref": bundle_ix_posix,
            "root_path": root_posix,
            "exists": run_abs.is_dir() and bundle_abs.is_file(),
            "producer": "apps_rg.runtime.run_correlation_links.discover_explicit_paths_v1",
        }
        triple = (lane, pmode, rid)
        if triple not in triple_map:
            triple_map[triple] = entry
        else:
            prev = triple_map[triple]
            if entry["bundle_index_ref"] != prev["bundle_index_ref"]:
                raise ValueError(
                    f"conflicting lane bundle refs for {triple}: "
                    f"{prev['bundle_index_ref']!r} vs {entry['bundle_index_ref']!r}"
                )

    return finalize_lane_bundle_ref_rows(triple_map)


def discover_aggregate_refs(repo_root: Path, corpus: str) -> list[dict[str, Any]]:
    """Aggregate hints from corpus (rollup + final assembly JSON paths)."""
    aggs: list[dict[str, Any]] = []
    rr = repo_root.resolve()
    if AGG_ROLLUP_REL in corpus:
        pth = rr / Path(*AGG_ROLLUP_REL.split("/"))
        aggs.append(
            {
                "kind": "generated_lane_rollup",
                "relative_path": AGG_ROLLUP_REL,
                "exists": pth.is_file(),
                "producer": "apps_rg.runtime.run_correlation_links.hint_aggregate_v1",
            }
        )
    seen: set[str] = set()
    for match in sorted(set(_final_resume_re.findall(corpus))):
        if match in seen:
            continue
        seen.add(match)
        pth = rr / Path(*match.split("/"))
        aggs.append(
            {
                "kind": "final_resume_assembly",
                "relative_path": match,
                "exists": pth.is_file(),
                "producer": "apps_rg.runtime.run_correlation_links.hint_aggregate_v1",
            }
        )
    aggs.sort(key=lambda x: (x["kind"], x["relative_path"]))
    return aggs


def build_modular_sections_root_attachment(repo_root: Path) -> dict[str, Any]:
    """Describe ``APPS_RG_MODULAR_R4_SECTIONS_ROOT`` for correlation (W4.1).

    Raises ``ValueError`` when the env var is set without the required sibling manifest.
    """
    raw = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV, "").strip()
    env_lit = MODULAR_R4_SECTIONS_ROOT_ENV

    default_notes = (
        f"{env_lit} is not set; lane runtime proofs default under artifacts/apps_rg/runtime_proofs."
    )

    if not raw:
        return {
            "mode": "default",
            "source_env_var": env_lit,
            "manifest_ref": None,
            "root_path": None,
            "exists": False,
            "notes": default_notes,
        }

    sr = modular_sections_root_from_env(repo_root)
    mf = sr / SECTIONS_ROOT_MANIFEST_FILENAME
    if not mf.is_file():
        raise ValueError(
            f"{env_lit} is set but `{SECTIONS_ROOT_MANIFEST_FILENAME}` is missing beside `{sr}` "
            "(W4.1 — no silent third root)."
        )
    manifest_ref = repo_relative_posix(repo_root, mf.resolve())
    root_path = repo_relative_posix(repo_root, sr.resolve())
    return {
        "mode": "env_manifest",
        "source_env_var": env_lit,
        "manifest_ref": manifest_ref,
        "root_path": root_path,
        "exists": True,
        "notes": (
            f"{env_lit} is active; lane prepare/finalize uses modular pointers under `{root_path}`."
        ),
    }


def build_run_links_document(
    repo_root: Path,
    integrated_dir: Path,
    *,
    integrated_run_id: str,
    correlation_id: str | None,
    notes: str | None = None,
    lane_bundle_refs_override: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build RUN_LINKS payload (repo-relative POSIX only)."""
    corpus = _gather_integrated_corpus(integrated_dir)
    iid = str(integrated_run_id or "").strip() or integrated_dir.name
    cid = str(correlation_id).strip() if correlation_id and str(correlation_id).strip() else None
    art_ns, log_ns = load_apps_rg_pipeline_namespaces(repo_root)

    bundle_ref = integrated_dir / RUN_BUNDLE_INDEX_FILENAME
    integrated_bundle_index_ref = repo_relative_posix(repo_root, bundle_ref)

    modular_root = integrated_dir / "modular_r4" / "sections"
    if lane_bundle_refs_override is not None:
        lane_refs = lane_bundle_refs_override
    elif modular_root.is_dir():
        from apps_rg.runtime.integrated_lane_evidence_packaging import (
            discover_integrated_modular_lane_bundle_refs,
        )

        lane_refs = discover_integrated_modular_lane_bundle_refs(repo_root, integrated_dir)
    else:
        lane_refs = discover_lane_bundle_refs(repo_root, corpus, correlation_id=cid)

    doc: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "correlation_id": cid,
        "integrated_run_id": iid,
        "created_at": _utc_now(),
        "root_path": repo_relative_posix(repo_root, integrated_dir.resolve()),
        "artifact_namespace": art_ns,
        "log_namespace": log_ns,
        "log_discovery": build_log_discovery_metadata(repo_root),
        "integrated_bundle_index_ref": integrated_bundle_index_ref,
        "lane_bundle_refs": lane_refs,
        "aggregate_refs": discover_aggregate_refs(repo_root, corpus),
        "modular_sections_root": build_modular_sections_root_attachment(repo_root),
    }
    if notes:
        doc["notes"] = notes
    if modular_root.is_dir():
        doc["lane_bundle_refs_source"] = (
            "modular_r4_sections_tree_v1"
            if lane_bundle_refs_override is not None
            else "modular_r4_sections_tree_auto"
        )
    return doc


def write_run_links(integrated_dir: Path, document: Mapping[str, Any]) -> None:
    path = integrated_dir / RUN_LINKS_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(document), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def emit_integrated_run_links(
    repo_root: Path,
    integrated_dir: Path,
    *,
    integrated_run_id: str | None,
    correlation_id: str | None = None,
    notes: str | None = None,
) -> Path:
    """Write RUN_LINKS.json beside an integrated run. OSError on write suppressed with warning."""
    doc = build_run_links_document(
        repo_root,
        integrated_dir,
        integrated_run_id=str(integrated_run_id or integrated_dir.name),
        correlation_id=correlation_id,
        notes=notes,
    )
    target = integrated_dir / RUN_LINKS_FILENAME
    try:
        write_run_links(integrated_dir, doc)
    except OSError as exc:
        log_run_links_write_failed("emit_integrated_run_links", exc)
    return target


def assert_run_links_document_shape(doc: Mapping[str, Any]) -> None:
    req = (
        "schema_version",
        "correlation_id",
        "integrated_run_id",
        "created_at",
        "root_path",
        "artifact_namespace",
        "log_namespace",
        "log_discovery",
        "integrated_bundle_index_ref",
        "lane_bundle_refs",
        "aggregate_refs",
        "modular_sections_root",
    )
    for k in req:
        if k not in doc:
            raise ValueError(f"RUN_LINKS missing key: {k}")
    ld = doc["log_discovery"]
    if not isinstance(ld, Mapping):
        raise ValueError("log_discovery must be an object")
    for lk in ("mode", "log_namespace", "log_root_path", "notes"):
        if lk not in ld:
            raise ValueError(f"log_discovery missing {lk}")
    if ld["mode"] not in ("disk", "telemetry_only", "unavailable"):
        raise ValueError("log_discovery.mode invalid")
    lp = ld["log_root_path"]
    if lp is not None and not isinstance(lp, str):
        raise ValueError("log_discovery.log_root_path must be string or null")
    if ld["mode"] == "disk" and not lp:
        raise ValueError("log_discovery disk mode requires non-null log_root_path")
    if ld["mode"] in ("telemetry_only", "unavailable") and lp is not None:
        raise ValueError(f"log_discovery.mode {ld['mode']} must have null log_root_path")
    if lp is not None:
        _assert_run_links_posix_path(lp, "log_discovery.log_root_path")
    if not isinstance(ld.get("notes"), str):
        raise ValueError("log_discovery.notes must be a string")

    modular = doc["modular_sections_root"]
    if not isinstance(modular, Mapping):
        raise ValueError("modular_sections_root must be an object")
    mod_req = ("mode", "source_env_var", "manifest_ref", "root_path", "exists")
    for mk in mod_req:
        if mk not in modular:
            raise ValueError(f"modular_sections_root missing {mk}")
    if modular["mode"] not in ("default", "env_manifest"):
        raise ValueError("modular_sections_root.mode invalid")
    mr = modular["manifest_ref"]
    mroot = modular["root_path"]
    if modular["mode"] == "default":
        if mr is not None or mroot is not None:
            raise ValueError("modular_sections_root default mode expects null refs")
        if modular["exists"] is not False:
            raise ValueError("modular_sections_root default mode expects exists=false")
    elif modular["mode"] == "env_manifest":
        if modular["exists"] is not True:
            raise ValueError("env_manifest implies exists=true")
        if not isinstance(mr, str) or not isinstance(mroot, str):
            raise ValueError("env_manifest requires string manifest_ref and root_path")
        _assert_run_links_posix_path(mr, "modular_sections_root.manifest_ref")
        _assert_run_links_posix_path(mroot, "modular_sections_root.root_path")
    if "notes" in modular and not isinstance(modular["notes"], str):
        raise ValueError("modular_sections_root notes must be a string")

    lanes = doc["lane_bundle_refs"]
    if not isinstance(lanes, list):
        raise ValueError("lane_bundle_refs must be a list")
    for i, row in enumerate(lanes):
        if not isinstance(row, Mapping):
            raise ValueError(f"lane_bundle_refs[{i}] invalid")
        status = str(row.get("status") or "EXECUTED")
        if status == "NOT_RUN":
            for fk in ("lane", "status", "missing_reason", "producer"):
                if fk not in row:
                    raise ValueError(f"lane_bundle_refs[{i}] NOT_RUN missing {fk}")
            continue
        for fk in ("lane", "proof_mode", "run_id", "root_path", "exists", "producer"):
            if fk not in row:
                raise ValueError(f"lane_bundle_refs[{i}] missing {fk}")
        if row["proof_mode"] not in ("real", "mock", "unknown"):
            raise ValueError(f"lane_bundle_refs[{i}] invalid proof_mode")

    aggs = doc["aggregate_refs"]
    if not isinstance(aggs, list):
        raise ValueError("aggregate_refs must be a list")
    for i, row in enumerate(aggs):
        if not isinstance(row, Mapping):
            raise ValueError(f"aggregate_refs[{i}] invalid")
        for fk in ("kind", "relative_path", "exists", "producer"):
            if fk not in row:
                raise ValueError(f"aggregate_refs[{i}] missing {fk}")


__all__ = [
    "RUN_LINKS_FILENAME",
    "AGG_ROLLUP_REL",
    "assert_run_links_document_shape",
    "build_modular_sections_root_attachment",
    "build_run_links_document",
    "discover_aggregate_refs",
    "discover_lane_bundle_refs",
    "emit_integrated_run_links",
    "finalize_lane_bundle_ref_rows",
    "log_run_links_write_failed",
    "write_run_links",
]
