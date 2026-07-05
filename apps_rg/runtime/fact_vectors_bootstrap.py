"""apps_rg ``bootstrap fact-vectors`` — build the C0.2 fact_vectors collection from tracked sources.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (W3; gaps G2-build, G3, G10, G14).

Source = first-principles, tracked inputs: the canonical **candidate fact ledger** plus the
canonical base-resume employment fact blocks. Each eligible HIGH / proof-eligible source fact
becomes one embeddable atom, assigned to the resume lanes it can enrich, embedded with BGE-M3,
and upserted **idempotently** (stable chunk ids) into the Chroma ``fact_vectors`` collection.
A manifest + checksum is emitted as the pre-run index receipt.

``--strict`` fails loud (non-zero) when the build produces no eligible atoms or leaves the collection
empty or any generated section has zero hydrated targets — a fresh checkout must be able to detect a
failed bootstrap, not silently proceed. Generated section runs consume this index read-only; generated
outputs may only enter the delayed staging/promotion loop after validation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import sqlite3
import sys
import time
import uuid
from collections import Counter
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import Any

from apps_rg.runtime.c0.constants import PROOF_ELIGIBLE, SOURCE_BASE_RESUME
from apps_rg.runtime.cli_exit_codes import EXIT_GENERIC_FAILURE, EXIT_SUCCESS

# Generated resume lanes that draw dense enrichment from fact_vectors. Keep this in the same
# dependency order as apps_rg.runtime.internal.generated_lane_rollup.GENERATED_LANES; this module is
# intentionally import-light because it runs during bootstrap/index maintenance.
GENERATED_LANES: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)
# Any HIGH fact can enrich these cross-section lanes.
CROSS_SECTION_TARGETS: tuple[str, ...] = ("competencies", "headline", "executive_summary")
# No generated lane is excluded from pre-C0 fact-vector hydration. A section may still be
# deterministic in prose generation, but its C0 retrieval/handoff contract must have index coverage.
LOCKED_DETERMINISTIC_LANES: tuple[str, ...] = ()

_BASE_RESUME_EMPLOYER_LANES: tuple[tuple[tuple[str, ...], list[str]], ...] = (
    (("ibm",), ["ibm_bullets", "ibm_narrative"]),
    (("unify",), ["unify_bullets", "unify_narrative"]),
    (("insurtech",), ["insurtech_bullets", "insurtech_narrative"]),
    (("ernst", "young"), ["ey_bullets", "ey_narrative"]),
)

MANIFEST_REL = "artifacts/apps_rg/c0/fact_vectors_bootstrap_manifest.json"
FALLBACK_MANIFEST_NAME = "fact_vectors_bootstrap_fallback_manifest.json"
BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME = "BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME"
BLOCKED_FACT_VECTOR_HYDRATION_LOCK = "BLOCKED_FACT_VECTOR_HYDRATION_LOCK"
HYDRATION_LOCK_FILENAME = ".apps_rg_fact_vector_hydration.lock"
HYDRATION_SNAPSHOT_ROOT_REL = "artifacts/apps_rg/c0/chroma_snapshots"
_REQUIRED_HYDRATION_IMPORTS = ("redis", "yaml", "chromadb", "sentence_transformers", "torch")
_CANONICAL_BGE_HF_ID = "BAAI/bge-m3"
_DEFAULT_EMBEDDING_MODEL_ID_SLUG = "bge-m3-v1"


def _repo_root() -> Path:
    # apps_rg/runtime/fact_vectors_bootstrap.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


class FactVectorHydrationRuntimeError(RuntimeError):
    """Raised when the hydration writer is not allowed to run."""

    def __init__(self, receipt: dict[str, Any]) -> None:
        self.receipt = receipt
        block_code = str(receipt.get("block_code") or BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME)
        reasons = ", ".join(str(r) for r in receipt.get("reasons") or []) or "unknown"
        super().__init__(f"{block_code}: {reasons}")


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


def required_hydration_device() -> str:
    """Resolve the worker device. Product hydration defaults to CUDA."""
    return (
        os.environ.get("APPS_RG_HYDRATION_DEVICE", "").strip()
        or os.environ.get("EMBEDDING_DEVICE", "").strip()
        or os.environ.get("VECTOR_DB_DEVICE", "").strip()
        or "cuda"
    ).lower()


def _chroma_dir(chroma_path: str | Path) -> Path:
    path = Path(str(chroma_path)).expanduser()
    if path.suffix.lower() == ".sqlite3":
        return path.parent
    return path


def _env_truthy(name: str, *, default: str = "") -> bool:
    raw = os.environ.get(name, default).strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


def _embedding_explicitly_disabled() -> bool:
    for name in ("EMBEDDING_ENABLED", "APPS_RG_EMBEDDING_ENABLED"):
        raw = os.environ.get(name, "").strip().lower()
        if raw in {"0", "false", "no"}:
            return True
    return False


def _embedding_env_unset() -> bool:
    return not any(
        os.environ.get(name, "").strip()
        for name in ("EMBEDDING_ENABLED", "APPS_RG_EMBEDDING_ENABLED")
    )


def _hf_hub_bge_snapshot_dir(model_id: str) -> tuple[str, str | None]:
    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    hub_root = hf_home / "hub"
    cache_name = f"models--{model_id.replace('/', '--')}"
    snaps = hub_root / cache_name / "snapshots"
    if not snaps.is_dir():
        return "missing", None
    try:
        candidates = sorted(snaps.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return "unreadable", None
    for snap in candidates:
        if not snap.is_dir():
            continue
        if (snap / "config.json").is_file() or (snap / "modules.json").is_file():
            return "found", str(snap.resolve())
    return "no_model_files", None


def _resolve_local_bge_path_import_light(*, repo_root: Path, model_id: str) -> tuple[str | None, str]:
    explicit = os.environ.get("APPS_RG_EMBEDDING_MODEL_PATH", "").strip()
    if explicit:
        path = Path(explicit)
        if path.is_dir() and any(path.iterdir()):
            return str(path.resolve()), "local"
        return None, "explicit_unavailable"

    candidates: list[Path] = []
    if model_id and ("/" in model_id or model_id.startswith("BAAI")):
        candidates.append(repo_root / "artifacts" / "models" / model_id.replace("/", os.sep))
        candidates.append(repo_root / "models" / model_id.replace("/", os.sep))
    candidates.append(repo_root / "artifacts" / "models" / "BAAI" / "bge-m3")
    candidates.append(repo_root / "artifacts" / "models" / "bge-m3")

    for cand in candidates:
        if cand.is_dir() and any(cand.iterdir()):
            return str(cand.resolve()), "pre_provisioned"

    hf_status, hf_path = _hf_hub_bge_snapshot_dir(model_id or _CANONICAL_BGE_HF_ID)
    if hf_path:
        return hf_path, "pre_provisioned"
    return None, f"unavailable:{hf_status}"


def prepare_fact_vector_hydration_env(
    *,
    repo_root: Path | str,
    chroma_path: str | None = None,
) -> dict[str, Any]:
    """Prepare hydration env without importing agentic_core or heavy ML packages."""
    repo = Path(repo_root).resolve()
    applied: dict[str, str] = {}
    os.environ.setdefault("AGENTIC_REPO_ROOT", str(repo))
    if os.environ.get("AGENTIC_REPO_ROOT") == str(repo):
        applied["AGENTIC_REPO_ROOT"] = str(repo)

    resolved_chroma = (
        (chroma_path or "").strip()
        or os.environ.get("CHROMA_PERSIST_DIR", "").strip()
        or str((repo / "data" / "cache" / "chromadb").resolve())
    )
    if not os.environ.get("CHROMA_PERSIST_DIR", "").strip():
        os.environ["CHROMA_PERSIST_DIR"] = resolved_chroma
        applied["CHROMA_PERSIST_DIR"] = resolved_chroma

    embeddings_disabled = _embedding_explicitly_disabled()
    if not embeddings_disabled and _embedding_env_unset():
        os.environ["EMBEDDING_ENABLED"] = "true"
        os.environ["APPS_RG_EMBEDDING_ENABLED"] = "true"
        applied["EMBEDDING_ENABLED"] = "true"
        applied["APPS_RG_EMBEDDING_ENABLED"] = "true"

    model_id = (
        os.environ.get("APPS_RG_EMBEDDING_MODEL_NAME", "").strip()
        or os.environ.get("EMBEDDING_MODEL_ID", "").strip()
        or _CANONICAL_BGE_HF_ID
    )
    if model_id == _DEFAULT_EMBEDDING_MODEL_ID_SLUG:
        model_id = _CANONICAL_BGE_HF_ID

    model_path: str | None = None
    model_source = "not_applicable"
    if not embeddings_disabled:
        model_path, model_source = _resolve_local_bge_path_import_light(
            repo_root=repo,
            model_id=model_id,
        )
        if model_path and not os.environ.get("APPS_RG_EMBEDDING_MODEL_PATH", "").strip():
            os.environ["APPS_RG_EMBEDDING_MODEL_PATH"] = model_path
            applied["APPS_RG_EMBEDDING_MODEL_PATH"] = model_path
        os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
        os.environ.setdefault("APPS_RG_R1B_SEMANTIC_PROOF", "ELIGIBLE")
        os.environ.setdefault("EMBEDDING_MODEL_ID", _DEFAULT_EMBEDDING_MODEL_ID_SLUG)
        os.environ.setdefault("APPS_RG_EMBEDDING_MODEL_NAME", _CANONICAL_BGE_HF_ID)
        os.environ.setdefault("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "1")
        os.environ.setdefault("APPS_RG_C0_SPARSE_ENABLED", "1")
        os.environ.setdefault("APPS_RG_C03_GRAPH_MANDATORY", "1")

    return {
        "schema_version": "apps_rg.fact_vector_hydration_env.v1",
        "chroma_path": resolved_chroma,
        "embedding_enabled": not embeddings_disabled,
        "embedding_model_id": model_id,
        "embedding_model_path": model_path or "",
        "embedding_model_source": model_source,
        "device": required_hydration_device(),
        "allow_cpu": _env_truthy("APPS_RG_FACT_VECTOR_ALLOW_CPU"),
        "applied_env": applied,
    }


def _module_probe() -> tuple[dict[str, str], dict[str, Any]]:
    failures: dict[str, str] = {}
    modules: dict[str, Any] = {}
    for name in _REQUIRED_HYDRATION_IMPORTS:
        try:
            modules[name] = importlib.import_module(name)
        except (ImportError, OSError, RuntimeError) as exc:
            failures[name] = f"{type(exc).__name__}: {exc}"
    return failures, modules


def validate_fact_vector_hydration_runtime(
    *,
    embedding_model_path: str | None,
    require_cuda: bool | None = None,
    raise_on_block: bool = False,
) -> dict[str, Any]:
    """Validate the heavy dependency/runtime boundary for live hydration writes."""
    device = required_hydration_device()
    if require_cuda is None:
        require_cuda = not _truthy_env("APPS_RG_FACT_VECTOR_ALLOW_CPU")
    failures, modules = _module_probe()
    reasons = [f"missing_or_blocked_dependency:{name}" for name in sorted(failures)]

    torch_mod = modules.get("torch")
    cuda_available = False
    cuda_device_name = ""
    if torch_mod is not None:
        try:
            cuda_available = bool(torch_mod.cuda.is_available())
            if cuda_available:
                cuda_device_name = str(torch_mod.cuda.get_device_name(0))
        except (AttributeError, OSError, RuntimeError, TypeError) as exc:
            reasons.append(f"torch_cuda_probe_failed:{type(exc).__name__}")
    if require_cuda and device != "cuda":
        reasons.append(f"hydration_device_not_cuda:{device}")
    if require_cuda and not cuda_available:
        reasons.append("torch_cuda_unavailable")

    model_path = Path(str(embedding_model_path or "")).expanduser()
    model_path_present = bool(embedding_model_path) and model_path.is_dir()
    if not model_path_present:
        reasons.append("local_bge_model_path_missing")

    receipt = {
        "schema_version": "apps_rg.fact_vector_hydration_runtime.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not reasons else "BLOCKED",
        "block_code": BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME,
        "reasons": reasons,
        "dependency_failures": failures,
        "required_modules": list(_REQUIRED_HYDRATION_IMPORTS),
        "device": device,
        "require_cuda": bool(require_cuda),
        "torch_cuda_available": cuda_available,
        "cuda_device_name": cuda_device_name,
        "embedding_model_path": str(model_path) if embedding_model_path else "",
        "embedding_model_path_present": model_path_present,
        "offline_model_required": True,
        "hf_hub_offline": True,
        "transformers_offline": True,
    }
    if receipt["status"] != "PASS" and raise_on_block:
        raise FactVectorHydrationRuntimeError(receipt)
    return receipt


class FactVectorHydrationLock(AbstractContextManager[dict[str, Any]]):
    """Cross-process single-writer lock for local Chroma hydration."""

    def __init__(self, *, chroma_path: str | Path, repo_root: Path | None = None) -> None:
        del repo_root  # reserved for future lock relocation; lock lives beside Chroma.
        self.chroma_dir = _chroma_dir(chroma_path)
        self.lock_path = self.chroma_dir / HYDRATION_LOCK_FILENAME
        self.token = uuid.uuid4().hex
        self.receipt: dict[str, Any] = {
            "schema_version": "apps_rg.fact_vector_hydration_lock.v1",
            "lock_path": str(self.lock_path),
            "status": "PENDING",
            "block_code": BLOCKED_FACT_VECTOR_HYDRATION_LOCK,
            "token": self.token,
            "acquired_at_utc": "",
            "released": False,
            "reasons": [],
        }

    def __enter__(self) -> dict[str, Any]:
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "token": self.token,
            "pid": os.getpid(),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with self.lock_path.open("x", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        except FileExistsError as exc:
            try:
                existing = self.lock_path.read_text(encoding="utf-8")[:1000]
            except OSError:
                existing = "<unreadable>"
            self.receipt.update(
                {
                    "status": "BLOCKED",
                    "reasons": ["fact_vector_hydration_lock_exists"],
                    "existing_lock_excerpt": existing,
                }
            )
            raise FactVectorHydrationRuntimeError(self.receipt) from exc
        self.receipt.update(
            {
                "status": "ACQUIRED",
                "acquired_at_utc": payload["created_at_utc"],
                "pid": os.getpid(),
            }
        )
        return self.receipt

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool | None:
        del exc_type, exc, tb
        try:
            current = json.loads(self.lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            current = {}
        if current.get("token") == self.token:
            try:
                self.lock_path.unlink()
                self.receipt["released"] = True
                self.receipt["released_at_utc"] = datetime.now(timezone.utc).isoformat()
            except OSError as unlink_exc:
                self.receipt["release_error"] = f"{type(unlink_exc).__name__}: {unlink_exc}"
        return None


def snapshot_chroma_before_hydration(
    *,
    chroma_path: str | Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Copy the local Chroma directory before live hydration mutates it."""
    source = _chroma_dir(chroma_path)
    receipt: dict[str, Any] = {
        "schema_version": "apps_rg.fact_vector_chroma_snapshot.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source),
        "status": "SKIPPED",
        "snapshot_path": "",
        "reasons": [],
    }
    if _truthy_env("APPS_RG_FACT_VECTOR_SKIP_CHROMA_SNAPSHOT"):
        receipt["reasons"].append("snapshot_disabled_by_env")
        return receipt
    if not source.exists():
        receipt["reasons"].append("chroma_path_missing")
        return receipt
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest = (
        repo_root
        / HYDRATION_SNAPSHOT_ROOT_REL
        / f"fact_vectors_chroma_{stamp}_{time.time_ns()}"
    )
    try:
        shutil.copytree(
            source,
            dest,
            ignore=shutil.ignore_patterns(HYDRATION_LOCK_FILENAME, "*.tmp"),
        )
    except (OSError, shutil.Error) as exc:
        receipt.update(
            {
                "status": "BLOCKED",
                "reasons": [f"snapshot_failed:{type(exc).__name__}"],
                "error": str(exc),
            }
        )
        return receipt
    receipt.update({"status": "PASS", "snapshot_path": str(dest)})
    return receipt


def _employer_sections(company: str) -> list[str]:
    c = (company or "").strip().lower()
    if "ibm" in c:
        return ["ibm_bullets", "ibm_narrative"]
    if c and ("unify" in c or "current" in c or "platform" in c):
        return ["unify_bullets", "unify_narrative"]
    if "insurtech" in c:
        return ["insurtech_bullets", "insurtech_narrative"]
    if "ey" in c or ("ernst" in c and "young" in c):
        return ["ey_bullets", "ey_narrative"]
    return []


def assign_sections_for_fact(row: dict[str, Any]) -> list[str]:
    """Generated lanes a HIGH ledger fact can meaningfully enrich (generous union, recall only)."""
    sections: set[str] = set(CROSS_SECTION_TARGETS)
    sections.update(_employer_sections(str(row.get("company") or "")))
    role_families = {str(r).upper() for r in (row.get("role_families_supported") or [])}
    if {"ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE", "PRODUCT_TECHNICAL_STRATEGY"} & role_families:
        sections.update({"unify_bullets", "unify_narrative"})
    return sorted(s for s in sections if s in GENERATED_LANES)


def build_section_atoms(*, repo_root: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build one atom per eligible ledger fact (tracked source), tagged with generated-lane targets."""
    from apps_rg.fact_inventory.candidate_fact_ledger import (
        default_ledger_path,
        load_master_candidate_fact_ledger,
    )
    from apps_rg.runtime.c0.c02_evidence_fetch import _atom_from_ledger_row
    from apps_rg.runtime.c0.c02_fact_vector_ingest import c02_atom_ingest_eligible

    root = repo_root or _repo_root()
    ledger = load_master_candidate_fact_ledger(repo_root=root, path=default_ledger_path(root))
    facts = [r for r in (ledger.get("candidate_facts") or []) if isinstance(r, dict)]
    atoms: list[dict[str, Any]] = []
    section_counts: Counter[str] = Counter()
    skipped: list[dict[str, str]] = []
    for row in facts:
        atom = _atom_from_ledger_row(row, section_id="competencies")
        atom["allowed_sections"] = assign_sections_for_fact(row)
        # Dense-lane grounding requires BOTH candidate_profile AND project_evidence source classes
        # (c0_binding fv_normative). Quantified-achievement facts (with metrics) are project_evidence;
        # capability/profile facts are candidate_profile — so each section's dense atoms span both.
        atom["source_class"] = (
            "project_evidence" if (row.get("metric_values") or []) else "candidate_profile"
        )
        ok, reason = c02_atom_ingest_eligible(atom)
        if not ok:
            skipped.append({"fact_id": atom["fact_id"], "reason": reason})
            continue
        atoms.append(atom)
        for section in atom["allowed_sections"]:
            section_counts[section] += 1
    # Every generated lane appears in the manifest (0 where no fact supports it) for auditability.
    per_section = {lane: int(section_counts.get(lane, 0)) for lane in GENERATED_LANES}
    summary = {
        "ledger_path": default_ledger_path(root).as_posix(),
        "total_ledger_facts": len(facts),
        "eligible_atoms": len(atoms),
        "skipped_count": len(skipped),
        "skipped": skipped[:50],
        "per_section_target_counts": per_section,
    }
    return atoms, summary


def build_base_resume_employment_atoms(
    *,
    repo_root: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build one grounded atom per canonical base-resume employment bullet.

    These are first-principles source facts, not generated output. They hydrate employer-specific
    bullet and narrative lanes before C0 so those sections are not dependent on same-run writeback.
    """
    from apps_rg.runtime.c0.c02_fact_vector_ingest import c02_atom_ingest_eligible
    from apps_rg.runtime.resume_resolution import load_lane_base_resume_json

    root = repo_root or _repo_root()
    atoms: list[dict[str, Any]] = []
    section_counts: Counter[str] = Counter()
    skipped: list[dict[str, str]] = []
    try:
        base, base_path, base_digest = load_lane_base_resume_json(
            source_resume_ref=None,
            repo_root=root,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        return atoms, {
            "base_resume_error": f"{type(exc).__name__}:{exc}",
            "base_resume_path": "",
            "base_resume_digest": "",
            "base_resume_employment_atoms": 0,
            "base_resume_skipped": [],
            "base_resume_per_section_counts": {lane: 0 for lane in GENERATED_LANES},
        }

    employment = ((base.get("facts") or {}).get("employment")) or []
    for block in employment:
        if not isinstance(block, dict):
            continue
        label = str(block.get("employer") or block.get("company") or "").lower()
        lanes: list[str] = []
        for needles, sections in _BASE_RESUME_EMPLOYER_LANES:
            if any(n in label for n in needles):
                lanes = sections
                break
        if not lanes:
            continue
        targets = sorted((set(lanes) | set(CROSS_SECTION_TARGETS)) & set(GENERATED_LANES))
        for bullet in block.get("bullets") or []:
            if not isinstance(bullet, dict):
                continue
            bid = str(bullet.get("bullet_id") or "").strip()
            text = str(bullet.get("text") or bullet.get("bullet_text") or "").strip()
            if not bid or not text:
                continue
            atom: dict[str, Any] = {
                "fact_id": bid,
                "text_to_embed": text[:2000],
                "source_type": SOURCE_BASE_RESUME,
                "fact_vector_source_class": "project_evidence",
                "source_ref": "apps_rg/resume/base",
                "source_span_ref": f"base_resume:{bid}",
                "confidence": "HIGH",
                "domain_tags": [str(bullet.get("domain"))] if bullet.get("domain") else [],
                "skill_tags": [
                    str(t) for t in (bullet.get("technologies") or []) if str(t).strip()
                ],
                "metric_refs": [str(bullet.get("metric_raw"))] if bullet.get("metric_raw") else [],
                "career_phase_refs": [],
                "graph_node_refs": [],
                "allowed_sections": targets,
                "blocked_sections": [],
                "proof_status": PROOF_ELIGIBLE,
                "requires_trace_audit": False,
                "retrieval_score": 1.0,
                "rejected_reason": "",
            }
            ok, reason = c02_atom_ingest_eligible(atom)
            if not ok:
                skipped.append({"fact_id": bid, "reason": reason})
                continue
            atoms.append(atom)
            for section in targets:
                section_counts[section] += 1
    return atoms, {
        "base_resume_path": base_path.as_posix(),
        "base_resume_digest": str(base_digest),
        "base_resume_employment_atoms": len(atoms),
        "base_resume_skipped": skipped[:50],
        "base_resume_per_section_counts": {
            lane: int(section_counts.get(lane, 0)) for lane in GENERATED_LANES
        },
    }


def _merge_per_section_counts(*parts: dict[str, Any]) -> dict[str, int]:
    merged: Counter[str] = Counter()
    for part in parts:
        for lane, count in (part or {}).items():
            if lane in GENERATED_LANES:
                merged[lane] += int(count or 0)
    return {lane: int(merged.get(lane, 0)) for lane in GENERATED_LANES}


def _reset_collection(chroma_path: str, collection_name: str = "fact_vectors") -> int:
    from apps_rg.runtime.chroma_precomputed_collection import persistent_chroma_client

    client = persistent_chroma_client(chroma_path)
    try:
        existing = client.get_collection(collection_name)
        count = int(existing.count())
    except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError):
        return 0
    client.delete_collection(collection_name)
    return count


def _build_sparse_sidecar(
    chroma_path: str,
    manifest: dict[str, Any],
    *,
    chunks: list[Any] | None = None,
    atoms: list[dict[str, Any]] | None = None,
) -> None:
    """G22: build the FTS5/BM25 sparse sidecar so the mandatory C0.2 sparse lane is available.

    Reads the just-upserted fact_vectors collection and writes data/cache/sparse/fact_vectors.db
    (read by agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index). Best-effort; the
    outcome is recorded in the manifest so --strict can gate on it.
    """
    try:
        from tools.generate.ingestion import build_sparse_index as sparse_builder

        sparse_dir = _repo_root() / "data" / "cache" / "sparse"
        if chunks:
            from apps_rg.runtime.c0.c02_fact_vector_ingest import chunk_to_chroma_document

            atom_list = atoms if atoms is not None and len(atoms) == len(chunks) else [None] * len(chunks)
            rows = []
            for chunk, atom in zip(chunks, atom_list, strict=True):
                doc = chunk_to_chroma_document(chunk, atom)
                rows.append(
                    {
                        "id": doc["id"],
                        "document": doc["text"],
                        "metadata": doc["metadata"],
                    }
                )
            stats = sparse_builder.upsert_documents(
                "fact_vectors",
                rows,
                sparse_dir=sparse_dir,
            )
        else:
            stats = sparse_builder.build_for_collection(
                "fact_vectors",
                chroma_path=chroma_path,
                sparse_dir=sparse_dir,
            )
        from agentic_core.L4_state.utils.memory.bm25_store import sparse_sidecar_exists

        manifest["sparse_sidecar_built"] = bool(sparse_sidecar_exists("fact_vectors"))
        manifest["sparse_doc_count"] = int(stats.get("doc_count") or 0)
        manifest["sparse_term_count"] = int(stats.get("term_count") or 0)
    except (AttributeError, ImportError, OSError, RuntimeError, sqlite3.Error, TypeError, ValueError) as exc:
        manifest["sparse_sidecar_built"] = False
        manifest["sparse_sidecar_error"] = f"{type(exc).__name__}: {exc}"


def _collection_count(chroma_path: str, collection_name: str = "fact_vectors") -> int:
    from apps_rg.runtime.chroma_precomputed_collection import persistent_chroma_client

    client = persistent_chroma_client(chroma_path)
    try:
        return int(client.get_collection(collection_name).count())
    except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError):
        return 0


def _sha256_json(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _write_manifest(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    dry_run: bool = False,
    blocked: bool = False,
) -> Path:
    path = repo_root / MANIFEST_REL
    if dry_run:
        path = path.with_name("fact_vectors_bootstrap_dry_run_manifest.json")
    elif blocked:
        path = path.with_name("fact_vectors_bootstrap_blocked_manifest.json")
    elif str(manifest.get("status") or "") == "FALLBACK_ALLOWED":
        path = path.with_name(FALLBACK_MANIFEST_NAME)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _finalize_manifest(
    *,
    root: Path,
    manifest: dict[str, Any],
    dry_run: bool = False,
    blocked: bool = False,
) -> None:
    manifest["manifest_checksum"] = _sha256_json(
        {k: v for k, v in manifest.items() if k != "manifest_checksum"}
    )
    manifest["manifest_path"] = _write_manifest(
        root,
        manifest,
        dry_run=dry_run,
        blocked=blocked,
    ).as_posix()


def _existing_index_fallback_receipt(
    *,
    root: Path,
    chroma: str,
    strict_block_receipt: dict[str, Any],
    target_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from apps_rg.runtime.fact_vector_readiness import (
        FALLBACK_DECISION_BLOCKED,
        FALLBACK_DECISION_USED_EXISTING_INDEX,
        build_fact_vector_readiness_receipt,
    )

    readiness = build_fact_vector_readiness_receipt(
        repo_root=root,
        chroma_path=chroma,
        target_context={
            "phase": "bootstrap_hydration_fallback",
            **dict(target_context or {}),
        },
        require_manifest_alignment=False,
    )
    decision = (
        FALLBACK_DECISION_USED_EXISTING_INDEX
        if readiness.get("status") == "PASS"
        else FALLBACK_DECISION_BLOCKED
    )
    return {
        "schema_version": "apps_rg.fact_vector_hydration_fallback.v1",
        "decision": decision,
        "fallback_mode": "existing_dense_sparse_fact_vectors_index",
        "live_hydration_status": strict_block_receipt.get("status"),
        "live_hydration_block_code": strict_block_receipt.get("block_code"),
        "live_hydration_reasons": list(strict_block_receipt.get("reasons") or []),
        "readiness": readiness,
        "policy": (
            "Prefer live source-ingestion hydration. If that writer cannot run, "
            "generation may use the existing dense+sparse index only when read-only "
            "sufficiency passes without manifest alignment."
        ),
    }


def run_bootstrap_fact_vectors(
    *,
    strict: bool,
    reset: bool = False,
    dry_run: bool = False,
    chroma_path: str | None = None,
    repo_root: Path | None = None,
    timestamp: str | None = None,
    allow_existing_index_fallback: bool = True,
) -> tuple[dict[str, Any], int]:
    """Build + upsert fact_vectors from first-principles source facts; return manifest/code."""
    root = repo_root or _repo_root()
    from apps_rg.runtime.c0.c02_fact_vector_ingest import (
        _ledger_version_hash,
        atoms_to_fact_vector_chunks,
        upsert_fact_vector_chunks,
    )

    resolved = (
        (chroma_path or "").strip()
        or os.environ.get("CHROMA_PERSIST_DIR", "").strip()
        or str(root / "data" / "cache" / "chromadb")
    )
    os.environ.setdefault("CHROMA_PERSIST_DIR", resolved)
    chroma = os.environ.get("CHROMA_PERSIST_DIR", resolved)
    hydration_env: dict[str, Any] | None = None
    if not dry_run:
        hydration_env = prepare_fact_vector_hydration_env(repo_root=root, chroma_path=chroma)
        chroma = str(hydration_env.get("chroma_path") or chroma)

    ledger_atoms, summary = build_section_atoms(repo_root=root)
    base_atoms, base_summary = build_base_resume_employment_atoms(repo_root=root)
    atoms = ledger_atoms + base_atoms
    summary.update(base_summary)
    summary["eligible_atoms"] = len(atoms)
    summary["ledger_eligible_atoms"] = len(ledger_atoms)
    summary["per_section_target_counts"] = _merge_per_section_counts(
        summary.get("per_section_target_counts") or {},
        base_summary.get("base_resume_per_section_counts") or {},
    )
    missing_required_lanes = [
        lane for lane, count in summary["per_section_target_counts"].items() if int(count) <= 0
    ]
    manifest: dict[str, Any] = {
        "schema_version": "apps_rg.fact_vectors_bootstrap_manifest.v1",
        "plan": "apps-rg-e2e-gap-remediation-7e2d9c",
        "generated_at_utc": timestamp or datetime.now(timezone.utc).isoformat(),
        "source": (
            "candidate_fact_ledger + base_resume_employment_bullets "
            "(tracked first-principles sources); generated output is never a live fact source"
        ),
        "chroma_path": chroma,
        "dry_run": bool(dry_run),
        "ledger_version_hash": _ledger_version_hash(root),
        "locked_deterministic_lanes": list(LOCKED_DETERMINISTIC_LANES),
        "required_lanes": list(GENERATED_LANES),
        "missing_required_lane_targets": missing_required_lanes,
        **summary,
        "chunks_built": 0,
        "upserted_count": 0,
        "collection_count_after": None,
        "sparse_sidecar_built": False,
    }

    if not dry_run:
        runtime_receipt = validate_fact_vector_hydration_runtime(
            embedding_model_path=str((hydration_env or {}).get("embedding_model_path") or ""),
            raise_on_block=False,
        )
        manifest["hydration_env"] = hydration_env or {}
        manifest["hydration_runtime"] = runtime_receipt
        if runtime_receipt.get("status") != "PASS":
            if allow_existing_index_fallback:
                fallback = _existing_index_fallback_receipt(
                    root=root,
                    chroma=chroma,
                    strict_block_receipt=runtime_receipt,
                    target_context={"block_stage": "hydration_runtime"},
                )
                manifest["hydration_fallback"] = fallback
                if fallback.get("decision") == "USED_EXISTING_FACT_VECTOR_INDEX":
                    readiness = fallback.get("readiness") if isinstance(fallback.get("readiness"), dict) else {}
                    summary = readiness.get("summary") if isinstance(readiness.get("summary"), dict) else {}
                    manifest["status"] = "FALLBACK_ALLOWED"
                    manifest["fallback_mode"] = "existing_dense_sparse_fact_vectors_index"
                    manifest["upserted_count"] = 0
                    manifest["chunks_built"] = 0
                    manifest["collection_count_after"] = int(summary.get("collection_doc_count") or 0)
                    manifest["sparse_sidecar_built"] = int(summary.get("sparse_sidecar_doc_count") or 0) > 0
                    _finalize_manifest(root=root, manifest=manifest)
                    return manifest, EXIT_SUCCESS
            manifest["status"] = "BLOCKED"
            manifest["block_code"] = BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME
            _finalize_manifest(root=root, manifest=manifest, blocked=True)
            return manifest, EXIT_GENERIC_FAILURE
        try:
            with FactVectorHydrationLock(chroma_path=chroma, repo_root=root) as lock_receipt:
                manifest["hydration_lock"] = lock_receipt
                snapshot_receipt = snapshot_chroma_before_hydration(
                    chroma_path=chroma,
                    repo_root=root,
                )
                manifest["chroma_snapshot"] = snapshot_receipt
                if snapshot_receipt.get("status") != "PASS":
                    if allow_existing_index_fallback:
                        fallback = _existing_index_fallback_receipt(
                            root=root,
                            chroma=chroma,
                            strict_block_receipt={
                                "status": "BLOCKED",
                                "block_code": "BLOCKED_FACT_VECTOR_CHROMA_SNAPSHOT",
                                "reasons": list(snapshot_receipt.get("reasons") or []),
                            },
                            target_context={"block_stage": "chroma_snapshot"},
                        )
                        manifest["hydration_fallback"] = fallback
                        if fallback.get("decision") == "USED_EXISTING_FACT_VECTOR_INDEX":
                            readiness = fallback.get("readiness") if isinstance(fallback.get("readiness"), dict) else {}
                            summary = readiness.get("summary") if isinstance(readiness.get("summary"), dict) else {}
                            manifest["status"] = "FALLBACK_ALLOWED"
                            manifest["fallback_mode"] = "existing_dense_sparse_fact_vectors_index"
                            manifest["upserted_count"] = 0
                            manifest["chunks_built"] = 0
                            manifest["collection_count_after"] = int(summary.get("collection_doc_count") or 0)
                            manifest["sparse_sidecar_built"] = int(summary.get("sparse_sidecar_doc_count") or 0) > 0
                            _finalize_manifest(root=root, manifest=manifest)
                            return manifest, EXIT_SUCCESS
                    manifest["status"] = "BLOCKED"
                    manifest["block_code"] = "BLOCKED_FACT_VECTOR_CHROMA_SNAPSHOT"
                    _finalize_manifest(root=root, manifest=manifest, blocked=True)
                    return manifest, EXIT_GENERIC_FAILURE
                if reset:
                    manifest["reset_deleted_count"] = _reset_collection(chroma)
                ledger_hash = _ledger_version_hash(root)
                chunks, chunk_atoms, chunk_skipped = atoms_to_fact_vector_chunks(
                    atoms,
                    section_id="competencies",
                    ledger_version_hash=ledger_hash,
                    enforce_writeback_decision=False,
                )
                upserted = upsert_fact_vector_chunks(chunks, chroma_path=chroma, atoms=chunk_atoms)
                manifest["chunks_built"] = len(chunks)
                manifest["chunk_skipped"] = chunk_skipped[:50]
                manifest["upserted_count"] = upserted
                manifest["collection_count_after"] = _collection_count(chroma)
                # G22 (W6): the C0.2 sparse lane is independently mandatory — build its FTS5/BM25 sidecar
                # from the same fact_vectors collection so generated lanes are not blocked on sparse.
                _build_sparse_sidecar(chroma, manifest, chunks=chunks, atoms=chunk_atoms)
        except FactVectorHydrationRuntimeError as exc:
            manifest["hydration_lock"] = exc.receipt
            manifest["status"] = "BLOCKED"
            manifest["block_code"] = (
                str(exc.receipt.get("block_code") or BLOCKED_FACT_VECTOR_HYDRATION_LOCK)
            )
            _finalize_manifest(root=root, manifest=manifest, blocked=True)
            return manifest, EXIT_GENERIC_FAILURE

    _finalize_manifest(root=root, manifest=manifest, dry_run=dry_run)

    exit_code = EXIT_SUCCESS
    if strict:
        if int(summary.get("eligible_atoms") or 0) == 0:
            exit_code = EXIT_GENERIC_FAILURE
        elif missing_required_lanes:
            exit_code = EXIT_GENERIC_FAILURE
        elif not dry_run and int(manifest.get("collection_count_after") or 0) <= 0:
            exit_code = EXIT_GENERIC_FAILURE
        elif not dry_run and not manifest.get("sparse_sidecar_built"):
            exit_code = EXIT_GENERIC_FAILURE
    return manifest, exit_code


def run_bootstrap_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m apps_rg bootstrap",
        description="Build apps_rg C0.2 retrieval state from tracked sources (plan apps-rg-e2e-gap-remediation-7e2d9c).",
    )
    parser.add_argument(
        "resource",
        choices=["fact-vectors"],
        help="What to bootstrap (currently: fact-vectors).",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on an empty/unpopulated build.")
    parser.add_argument("--reset", action="store_true", help="Delete the collection before ingest.")
    parser.add_argument("--dry-run", action="store_true", help="Build + report atoms without writing to Chroma.")
    parser.add_argument("--chroma-path", default=None, help="Override CHROMA_PERSIST_DIR for this build.")
    parser.add_argument(
        "--disable-existing-index-fallback",
        action="store_true",
        help=(
            "Hard-block if live hydration cannot run instead of accepting an already-sufficient "
            "dense+sparse fact_vectors index."
        ),
    )
    namespace = parser.parse_args(argv)

    manifest, exit_code = run_bootstrap_fact_vectors(
        strict=namespace.strict,
        reset=namespace.reset,
        dry_run=namespace.dry_run,
        chroma_path=namespace.chroma_path,
        allow_existing_index_fallback=not bool(namespace.disable_existing_index_fallback),
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False), flush=True)
    if str(manifest.get("status") or "") == "FALLBACK_ALLOWED":
        print(
            "BOOTSTRAP FALLBACK_ALLOWED: live hydration blocked, "
            "using existing sufficient dense+sparse fact_vectors index.",
            flush=True,
        )
    if namespace.strict and exit_code != EXIT_SUCCESS:
        if str(manifest.get("status") or "") == "BLOCKED":
            print(
                "BOOTSTRAP BLOCKED (strict): "
                f"{manifest.get('block_code') or 'unknown_block'}. "
                "See manifest hydration_runtime / hydration_lock details.",
                flush=True,
            )
        else:
            print(
                "BOOTSTRAP FAILED (strict): no eligible atoms, missing generated-lane targets, "
                "empty collection, or sparse sidecar unavailable. Check first-principles sources "
                "and EMBEDDING_ENABLED / BGE model path.",
                flush=True,
            )
    return exit_code


__all__ = [
    "GENERATED_LANES",
    "LOCKED_DETERMINISTIC_LANES",
    "assign_sections_for_fact",
    "build_base_resume_employment_atoms",
    "build_section_atoms",
    "run_bootstrap_cli",
    "run_bootstrap_fact_vectors",
]


if __name__ == "__main__":
    raise SystemExit(run_bootstrap_cli(sys.argv[1:]))
