"""W6A — semantic cache / Chroma shadow-write quarantine (classification only).

Proves the core D2 ``promote_to_long_term`` → GPTCache Chroma ``upsert`` path is
``NON_DURABLE_INDEX_WRITE`` unless a verified Exit → UWG → L4 → read_surface_refresh
chain is present in the run evidence package.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_NO_DIRECT_CHROMA_ASSERTION = "no_direct_chroma_write_bypass_assertion_v1"
SCHEMA_SEMANTIC_CACHE_SLOTS = "semantic_cache_persistence_slots_v1"
_CANONICAL_PRODUCER = "apps_rg_semantic_cache_persistence_quarantine"

NO_DIRECT_CHROMA_ASSERTION_ARTIFACT = "no_direct_chroma_write_bypass_assertion.json"
INDEX_REFRESH_RECEIPT_ARTIFACT = "IndexRefreshReceipt"
READ_SURFACE_REFRESH_CANONICAL = "read_surface_refresh_receipt.json"

CHROMA_CLASS_NON_DURABLE = "NON_DURABLE_INDEX_WRITE"
CHROMA_CLASS_GOVERNED_REFRESH = "GOVERNED_READ_SURFACE_REFRESH_AFTER_UWG_COMMIT"
CHROMA_CLASS_PROHIBITED_CLAIM = "PROHIBITED_DURABLE_PERSISTENCE_CLAIM"
W6C_READ_SURFACE_DEFERRED_REASON = "w6c_chroma_read_surface_projection_deferred"

# Static SSOT from W5/W6A read-only inspection (no runtime mutation).
CULPRIT_CALL_CHAIN: tuple[str, ...] = (
    "agentic_core/L0_routing/reasoning/execution_orchestrator.py::_populate_d2_cache_promote",
    "agentic_core/L4_state/utils/memory/semantic_cache_manager.py::promote_to_long_term",
    "agentic_core/L4_state/cache/gptcache_client.py::NativePersistentCacheClient.store",
    "agentic_core/L4_state/cache/gptcache_client.py::_chroma_collection.upsert",
)

PROMOTE_TO_LONG_TERM_CALLERS: tuple[dict[str, str], ...] = (
    {
        "caller": "agentic_core/L0_routing/reasoning/execution_orchestrator.py",
        "symbol": "_populate_d2_cache_promote → promote_to_long_term",
        "runtime_active": "yes",
        "uwg_gated": "no",
        "classification": CHROMA_CLASS_NON_DURABLE,
    },
    {
        "caller": "agentic_core/mixins/semantic_cache_mixin.py",
        "symbol": "promote_to_long_term",
        "runtime_active": "optional",
        "uwg_gated": "no",
        "classification": CHROMA_CLASS_NON_DURABLE,
    },
    {
        "caller": "agentic_core/utils/meta_learning_storage_util.py",
        "symbol": "promote_to_long_term",
        "runtime_active": "optional",
        "uwg_gated": "no",
        "classification": CHROMA_CLASS_NON_DURABLE,
    },
    {
        "caller": "agentic_core/L4_state/utils/memory/semantic_cache_manager.py",
        "symbol": "promote_to_long_term (internal DNA path)",
        "runtime_active": "yes",
        "uwg_gated": "no",
        "classification": CHROMA_CLASS_NON_DURABLE,
    },
    {
        "caller": "apps_rg/cache/r1b_uwg_promotion.py",
        "symbol": "promote_r1b_cache_via_uwg",
        "runtime_active": "post_exit_whole_run_only",
        "uwg_gated": "yes",
        "classification": "UWG_FILE_PROJECTION_NOT_CHROMA",
    },
)

CHROMA_UPSERT_PATHS: tuple[dict[str, str], ...] = (
    {
        "path": "agentic_core/L4_state/cache/gptcache_client.py",
        "operation": "NativePersistentCacheClient.store → _chroma_collection.upsert",
        "uwg_routed": "no",
        "classification": CHROMA_CLASS_NON_DURABLE,
    },
    {
        "path": "agentic_core/L4_state/utils/memory/semantic_cache_manager.py",
        "operation": "_gptcache._chroma_collection.query/delete",
        "uwg_routed": "no",
        "classification": CHROMA_CLASS_NON_DURABLE,
    },
)

UWG_CHAIN_ARTIFACTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("commit_request", ("commit_request.json",)),
    (
        "state_diff_validation_result",
        (
            "state_diff_validation_result.json",
            "uwg_validation_receipt.json",
        ),
    ),
    (
        "state_commit_receipt_or_blocked",
        (
            "state_commit_receipt.json",
            "uwg_commit_receipt.json",
            "blocked_write_receipt.json",
            "uwg_blocked_commit_receipt.json",
        ),
    ),
    (
        "read_surface_refresh_receipt",
        (READ_SURFACE_REFRESH_CANONICAL,),
    ),
    (
        "read_surface_refresh_receipt_noncanonical",
        ("uwg_refresh_receipts.json",),
    ),
    (
        "l4_namespace_object_ref",
        (
            "l4_namespace_object_ref.json",
            "commit_request.json",
            "state_commit_receipt.json",
            "uwg_commit_receipt.json",
        ),
    ),
    ("chroma_collection_index_ref", ("chroma_collection_index_ref.json",)),
    ("chroma_read_after_write", ("chroma_read_after_write_receipt.json",)),
    ("request_intent_embedding_ref", ("request_intent_embedding_ref.json",)),
    ("request_intent_embedding_ref_mapping_receipt", ("request_intent_embedding_ref_mapping_receipt.json",)),
    ("cache_embedding_ref", ("cache_embedding_ref.json",)),
    ("fact_vector_ref", ("fact_vector_ref.json",)),
    ("compatibility_proof", ("r1b_compatibility_proof.json", "r1b_compatibility_report.json")),
)

SEMANTIC_CACHE_SLOT_IDS: tuple[str, ...] = (
    "commit_request",
    "state_diff_validation_result",
    "state_commit_receipt_or_blocked",
    "read_surface_refresh_receipt",
    "l4_namespace_object_ref",
    "chroma_collection_index_ref",
    "chroma_read_after_write",
    "request_intent_embedding_ref",
    "cache_embedding_ref",
    "fact_vector_ref",
    "compatibility_proof",
    "no_direct_chroma_write_bypass_assertion",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_rel(repo_root: Path, path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix().replace("\\", "/")


def _sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except OSError:
        return ""
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _search_roots(
    artifact_dir: Path,
    integrated_dir: Path | None,
) -> list[Path]:
    roots: list[Path] = [artifact_dir]
    if integrated_dir is not None and integrated_dir.is_dir():
        roots.append(integrated_dir)
    return roots


def _find_first_existing(
    roots: list[Path],
    filenames: tuple[str, ...],
) -> tuple[Path | None, str | None]:
    for root in roots:
        for name in filenames:
            p = root / name
            if p.is_file():
                return p, name
    return None, None


def _payload(doc: Mapping[str, Any]) -> Mapping[str, Any]:
    p = doc.get("payload")
    return p if isinstance(p, Mapping) else doc


def assess_uwg_durable_write_chain(
    *,
    repo_root: Path,
    artifact_dir: Path,
    integrated_dir: Path | None,
) -> dict[str, Any]:
    """Return chain assessment from on-disk receipts in section + correlated integrated dirs."""
    roots = _search_roots(artifact_dir, integrated_dir)
    found: dict[str, Any] = {}
    for step, names in UWG_CHAIN_ARTIFACTS:
        path, fname = _find_first_existing(roots, names)
        found[step] = {
            "present": path is not None,
            "artifact_name": fname,
            "source_path": _repo_rel(repo_root, path) if path else None,
        }

    l4_path, l4_fname = _find_first_existing(roots, ("l4_namespace_object_ref.json",))
    l4_surfaces: list[str] = []
    if l4_path is not None:
        pay = _payload(_load_json(l4_path))
        for key in ("affected_state_surfaces", "target_l4_namespace"):
            val = pay.get(key)
            if isinstance(val, (list, tuple)):
                l4_surfaces.extend(str(x) for x in val)
            elif isinstance(val, str) and val:
                l4_surfaces.append(val)
        found["l4_namespace_object_ref"]["present"] = True
        found["l4_namespace_object_ref"]["artifact_name"] = l4_fname
        found["l4_namespace_object_ref"]["source_path"] = _repo_rel(repo_root, l4_path)
        found["l4_namespace_object_ref"]["surfaces"] = l4_surfaces
    else:
        cr_path, _ = _find_first_existing(roots, ("commit_request.json",))
        if cr_path is not None:
            pay = _payload(_load_json(cr_path))
            for key in ("affected_state_surfaces", "expected_read_surface_refreshes"):
                val = pay.get(key)
                if isinstance(val, (list, tuple)):
                    l4_surfaces.extend(str(x) for x in val)
                elif isinstance(val, str) and val:
                    l4_surfaces.append(val)
            found["l4_namespace_object_ref"]["surfaces"] = l4_surfaces

    chain_manifest_path = artifact_dir / "r1b_governed_receipt_chain.json"
    chain_manifest = _load_json(chain_manifest_path) if chain_manifest_path.is_file() else {}

    refresh_canonical = bool(found["read_surface_refresh_receipt"]["present"])
    refresh_noncanonical = bool(found["read_surface_refresh_receipt_noncanonical"]["present"])
    commit_ok = bool(found["commit_request"]["present"])
    validation_ok = bool(found["state_diff_validation_result"]["present"])
    commit_receipt_ok = bool(found["state_commit_receipt_or_blocked"]["present"])

    chroma_index_ok = bool(found["chroma_collection_index_ref"]["present"])
    read_after_ok = bool(found["chroma_read_after_write"]["present"])
    embedding_ok = bool(found["request_intent_embedding_ref"]["present"])
    mapping_ok = bool(found["request_intent_embedding_ref_mapping_receipt"]["present"])
    compat_ok = bool(found["compatibility_proof"]["present"])
    assertion_ok = (artifact_dir / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).is_file()

    r1b_uwg_chain_core = commit_ok and validation_ok and commit_receipt_ok
    read_surface_refresh_complete = refresh_canonical
    chroma_projection_complete = chroma_index_ok and read_after_ok
    chain_steps_ok = r1b_uwg_chain_core and read_surface_refresh_complete
    governed_chroma_refresh = (
        chain_steps_ok and chroma_projection_complete and assertion_ok
    )
    durable_vector_chain_artifacts_complete = (
        r1b_uwg_chain_core
        and read_surface_refresh_complete
        and chroma_projection_complete
        and l4_path is not None
        and embedding_ok
        and mapping_ok
        and compat_ok
        and read_after_ok
    )
    durable_vector_persistence_proven = (
        durable_vector_chain_artifacts_complete and assertion_ok
    )
    uwg_path_present = (
        commit_ok
        or validation_ok
        or commit_receipt_ok
        or refresh_canonical
        or refresh_noncanonical
        or chroma_index_ok
        or bool(chain_manifest)
    )

    return {
        "uwg_path_present": uwg_path_present,
        "r1b_uwg_chain_core_complete": r1b_uwg_chain_core,
        "read_surface_refresh_complete": read_surface_refresh_complete,
        "chroma_projection_complete": chroma_projection_complete,
        "durable_vector_chain_artifacts_complete": durable_vector_chain_artifacts_complete,
        "durable_vector_persistence_proven": durable_vector_persistence_proven,
        "durable_proof_chain_complete": governed_chroma_refresh,
        "governed_chroma_refresh_proven": governed_chroma_refresh,
        "refresh_noncanonical_without_canonical": refresh_noncanonical and not refresh_canonical,
        "r1b_governed_receipt_chain": chain_manifest,
        "commit_request_status": chain_manifest.get("commit_request_status"),
        "artifacts": found,
    }


def _detect_index_refresh_receipt_only(artifact_dir: Path, repo_root: Path) -> dict[str, Any] | None:
    """apps_rg IndexRefreshReceipt is not canonical read_surface_refresh without bridge."""
    for rel in (
        "artifacts/apps_rg/r1b_semantic_cache/derived_index/manifest.json",
        "derived_index/manifest.json",
    ):
        cand = repo_root / rel if not Path(rel).is_absolute() else Path(rel)
        if cand.is_file():
            return {
                "detected_artifact": INDEX_REFRESH_RECEIPT_ARTIFACT,
                "source_path": _repo_rel(repo_root, cand),
                "canonical_equivalent": READ_SURFACE_REFRESH_CANONICAL,
                "bridge_receipt_present": False,
                "status": "DRIFT",
                "notes": (
                    "IndexRefreshReceipt / derived_index manifest is not "
                    "read_surface_refresh_receipt unless an explicit bridge receipt maps it"
                ),
            }
    r1b_manifest = artifact_dir / "r1b_derived_index_manifest.json"
    if r1b_manifest.is_file():
        return {
            "detected_artifact": INDEX_REFRESH_RECEIPT_ARTIFACT,
            "source_path": _repo_rel(repo_root, r1b_manifest),
            "canonical_equivalent": READ_SURFACE_REFRESH_CANONICAL,
            "bridge_receipt_present": False,
            "status": "DRIFT",
            "notes": "lane-local derived index manifest is not spine read_surface_refresh_receipt",
        }
    return None


def _detect_request_intent_vector_without_mapping(artifact_dir: Path, repo_root: Path) -> dict[str, Any] | None:
    for root in (artifact_dir, repo_root / "artifacts" / "apps_rg" / "r1b_semantic_cache"):
        if not root.is_dir():
            continue
        for p in root.rglob("vectors/*.json"):
            return {
                "detected_field": "request_intent_vector_ref",
                "example_path": _repo_rel(repo_root, p),
                "canonical_field": "request_intent_embedding_ref",
                "mapping_receipt_present": False,
                "status": "MISSING",
                "notes": (
                    "request_intent_vector_ref must not be classified as "
                    "request_intent_embedding_ref without request_intent_embedding_ref_mapping_receipt"
                ),
            }
    return None


def classify_shadow_chroma_write_path(
    *,
    uwg_assessment: Mapping[str, Any],
) -> str:
    if uwg_assessment.get("governed_chroma_refresh_proven"):
        return CHROMA_CLASS_GOVERNED_REFRESH
    return CHROMA_CLASS_NON_DURABLE


def build_no_direct_chroma_write_bypass_assertion(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    uwg_assessment: Mapping[str, Any],
    chroma_classification: str,
) -> dict[str, Any]:
    durable = bool(uwg_assessment.get("durable_proof_chain_complete"))
    return {
        "schema_version": SCHEMA_NO_DIRECT_CHROMA_ASSERTION,
        "generated_at_utc": _utc_now(),
        "producer": _CANONICAL_PRODUCER,
        "section_id": section_id,
        "run_id": run_id,
        "culprit_path": list(CULPRIT_CALL_CHAIN),
        "primary_culprit": CULPRIT_CALL_CHAIN[0],
        "promote_to_long_term_callers": list(PROMOTE_TO_LONG_TERM_CALLERS),
        "chroma_upsert_paths": list(CHROMA_UPSERT_PATHS),
        "uwg_path_present": bool(uwg_assessment.get("uwg_path_present")),
        "durable_proof_present": durable,
        "durable_persistence_claim_allowed": False,
        "chroma_semantic_cache_classification": chroma_classification,
        "write_classifications": {
            "transient_or_test_index_chroma_upsert": {
                "allowed": True,
                "classification": CHROMA_CLASS_NON_DURABLE,
                "notes": "Core D2 promote may upsert Chroma for L2 recall; not durable proof",
            },
            "governed_read_surface_refresh_after_uwg_commit": {
                "allowed": True,
                "classification": CHROMA_CLASS_GOVERNED_REFRESH,
                "requires_chain": [
                    "Exit X3C",
                    "CommitRequest",
                    "StateDiffValidationResult",
                    "StateCommitReceipt or BlockedWriteReceipt",
                    "L4",
                    READ_SURFACE_REFRESH_CANONICAL,
                ],
                "proven_in_this_run": durable,
            },
            "prohibited_durable_persistence_claim": {
                "allowed": False,
                "classification": CHROMA_CLASS_PROHIBITED_CLAIM,
                "notes": "Direct Chroma collection existence or upsert without UWG chain is not persistence proof",
            },
        },
        "explicit_non_claims": [
            "direct Chroma upsert on core D2 promote path is not durable semantic-cache persistence",
            "Chroma collection presence is not persistence proof",
            "vector persistence not claimed for this section run",
            "99 RuntimeProofBundle not claimed",
        ],
    }


def _slot(
    slot_id: str,
    *,
    status: str,
    artifact_name: str | None = None,
    source_path: str | None = None,
    owner_class: str = "MISSING",
    notes: str = "",
    sha256: str = "",
) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "status": status,
        "artifact_name": artifact_name,
        "source_path": source_path,
        "sha256": sha256 or None,
        "owner_class": owner_class,
        "runtime_authority_claimed": False,
        "notes": notes,
    }


def build_semantic_cache_persistence_slots(
    *,
    repo_root: Path,
    artifact_dir: Path,
    integrated_dir: Path | None,
    uwg_assessment: Mapping[str, Any],
    assertion_path: str | None,
) -> dict[str, Any]:
    roots = _search_roots(artifact_dir, integrated_dir)
    artifacts = uwg_assessment.get("artifacts") or {}
    slots: dict[str, dict[str, Any]] = {}

    def _fill_from_chain(step: str, slot_id: str, *, owner: str = "CORE_UWG_WRITE_ADMISSION") -> None:
        row = artifacts.get(step) or {}
        if row.get("present"):
            p = row.get("source_path")
            fname = row.get("artifact_name")
            path = None
            if p:
                path = repo_root / p
            slots[slot_id] = _slot(
                slot_id,
                status="PRESENT",
                artifact_name=fname,
                source_path=p,
                owner_class=owner,
                sha256=_sha256_file(path) if path and path.is_file() else "",
                notes="verified in section or correlated integrated run folder",
            )
        else:
            slots[slot_id] = _slot(
                slot_id,
                status="MISSING",
                notes=f"no {slot_id} artifact in run bundle",
            )

    _fill_from_chain("commit_request", "commit_request")
    _fill_from_chain("state_diff_validation_result", "state_diff_validation_result")
    _fill_from_chain("state_commit_receipt_or_blocked", "state_commit_receipt_or_blocked")

    refresh_row = artifacts.get("read_surface_refresh_receipt") or {}
    if refresh_row.get("present"):
        p = refresh_row.get("source_path")
        path = repo_root / p if p else None
        slots["read_surface_refresh_receipt"] = _slot(
            "read_surface_refresh_receipt",
            status="PRESENT",
            artifact_name=READ_SURFACE_REFRESH_CANONICAL,
            source_path=p,
            owner_class="CORE_L4_DURABLE_STATE",
            sha256=_sha256_file(path) if path and path.is_file() else "",
        )
    else:
        noncan = artifacts.get("read_surface_refresh_receipt_noncanonical") or {}
        if noncan.get("present"):
            slots["read_surface_refresh_receipt"] = _slot(
                "read_surface_refresh_receipt",
                status="DRIFT",
                artifact_name="uwg_refresh_receipts.json",
                source_path=noncan.get("source_path"),
                owner_class="DRIFT",
                notes=(
                    "uwg_refresh_receipts.json is not canonical read_surface_refresh_receipt "
                    "without read_surface_refresh_bridge_receipt.json"
                ),
            )
        else:
            idx_drift = _detect_index_refresh_receipt_only(artifact_dir, repo_root)
            if idx_drift:
                slots["read_surface_refresh_receipt"] = _slot(
                    "read_surface_refresh_receipt",
                    status="DRIFT",
                    artifact_name=idx_drift["detected_artifact"],
                    source_path=idx_drift.get("source_path"),
                    owner_class="DRIFT",
                    notes=idx_drift["notes"],
                )
            else:
                defer_path, _ = _find_first_existing(
                    roots,
                    ("read_surface_refresh_receipt_w6b_status.json",),
                )
                if defer_path is not None:
                    defer_pay = _payload(_load_json(defer_path))
                    slots["read_surface_refresh_receipt"] = _slot(
                        "read_surface_refresh_receipt",
                        status=str(defer_pay.get("status") or "NOT_APPLICABLE"),
                        artifact_name="read_surface_refresh_receipt_w6b_status.json",
                        source_path=_repo_rel(repo_root, defer_path),
                        owner_class="NOT_APPLICABLE",
                        notes=str(defer_pay.get("notes") or W6C_READ_SURFACE_DEFERRED_REASON),
                    )
                else:
                    slots["read_surface_refresh_receipt"] = _slot(
                        "read_surface_refresh_receipt",
                        status="MISSING",
                        notes="no canonical read_surface_refresh_receipt.json",
                    )

    l4_row = artifacts.get("l4_namespace_object_ref") or {}
    surfaces = l4_row.get("surfaces") or []
    if surfaces:
        slots["l4_namespace_object_ref"] = _slot(
            "l4_namespace_object_ref",
            status="PRESENT",
            artifact_name="commit_request.json",
            source_path=l4_row.get("source_path") or (artifacts.get("commit_request") or {}).get("source_path"),
            owner_class="CORE_L4_DURABLE_STATE",
            notes=f"surfaces={surfaces!r}",
        )
    else:
        slots["l4_namespace_object_ref"] = _slot(
            "l4_namespace_object_ref",
            status="MISSING",
            notes="no L4 namespace/object ref in CommitRequest receipt",
        )

    chroma_row = artifacts.get("chroma_collection_index_ref") or {}
    if chroma_row.get("present"):
        p = chroma_row.get("source_path")
        path = repo_root / p if p else None
        slots["chroma_collection_index_ref"] = _slot(
            "chroma_collection_index_ref",
            status="PRESENT",
            artifact_name=chroma_row.get("artifact_name"),
            source_path=p,
            owner_class="CORE_L4_DURABLE_STATE",
            sha256=_sha256_file(path) if path and path.is_file() else "",
            notes="governed apps_rg read-surface Chroma collection ref (not core D2)",
        )
    else:
        slots["chroma_collection_index_ref"] = _slot(
            "chroma_collection_index_ref",
            status="MISSING",
            notes=(
                "core D2 shadow path uses agentic_core/L4_state/cache/gptcache_client Chroma upsert; "
                "classified NON_DURABLE_INDEX_WRITE without governed read_surface_refresh chain"
            ),
        )

    read_after_row = artifacts.get("chroma_read_after_write") or {}
    if read_after_row.get("present"):
        p = read_after_row.get("source_path")
        path = repo_root / p if p else None
        slots["chroma_read_after_write"] = _slot(
            "chroma_read_after_write",
            status="PRESENT",
            artifact_name=read_after_row.get("artifact_name"),
            source_path=p,
            owner_class="CORE_L4_DURABLE_STATE",
            sha256=_sha256_file(path) if path and path.is_file() else "",
        )
    else:
        slots["chroma_read_after_write"] = _slot(
            "chroma_read_after_write",
            status="MISSING",
            notes="no chroma_read_after_write_receipt.json after governed projection",
        )

    mapping_path, _ = _find_first_existing(
        roots,
        ("request_intent_embedding_ref_mapping_receipt.json",),
    )
    intent_emb_path, _ = _find_first_existing(roots, ("request_intent_embedding_ref.json",))
    vector_drift = _detect_request_intent_vector_without_mapping(artifact_dir, repo_root)
    if intent_emb_path and mapping_path:
        slots["request_intent_embedding_ref"] = _slot(
            "request_intent_embedding_ref",
            status="PRESENT",
            artifact_name="request_intent_embedding_ref.json",
            source_path=_repo_rel(repo_root, intent_emb_path),
            owner_class="APP_DOMAIN_EVIDENCE",
        )
    elif vector_drift:
        slots["request_intent_embedding_ref"] = _slot(
            "request_intent_embedding_ref",
            status="MISSING",
            owner_class="MISSING",
            notes=vector_drift["notes"],
        )
    else:
        slots["request_intent_embedding_ref"] = _slot(
            "request_intent_embedding_ref",
            status="MISSING",
            notes="no request_intent_embedding_ref or mapping receipt",
        )

    slots["cache_embedding_ref"] = _slot(
        "cache_embedding_ref",
        status="MISSING",
        notes="cache_embedding_ref not emitted on section path; core RETTerminalPacket field not materialized",
    )

    slots["fact_vector_ref"] = _slot(
        "fact_vector_ref",
        status="NOT_APPLICABLE",
        notes="C0 fact_vec refs are retrieval-only on this lane; not R1B cache_embedding_ref proof",
    )

    compat_path, compat_name = _find_first_existing(
        roots,
        ("r1b_compatibility_proof.json", "r1b_compatibility_report.json"),
    )
    if compat_path:
        slots["compatibility_proof"] = _slot(
            "compatibility_proof",
            status="PRESENT",
            artifact_name=compat_name,
            source_path=_repo_rel(repo_root, compat_path),
            owner_class="APP_DOMAIN_EVIDENCE",
            sha256=_sha256_file(compat_path),
        )
    else:
        slots["compatibility_proof"] = _slot(
            "compatibility_proof",
            status="MISSING",
            notes="no R1B compatibility proof artifact (request_intent vs cache embedding)",
        )

    slots["no_direct_chroma_write_bypass_assertion"] = _slot(
        "no_direct_chroma_write_bypass_assertion",
        status="PRESENT" if assertion_path else "MISSING",
        artifact_name=NO_DIRECT_CHROMA_ASSERTION_ARTIFACT,
        source_path=assertion_path,
        owner_class="APP_BINDING_MANIFEST",
        notes="W6A quarantine assertion for shadow Chroma write path",
    )

    missing_ids = [sid for sid in SEMANTIC_CACHE_SLOT_IDS if slots[sid]["status"] == "MISSING"]
    drift_ids = [sid for sid in SEMANTIC_CACHE_SLOT_IDS if slots[sid]["status"] == "DRIFT"]
    present_ids = [sid for sid in SEMANTIC_CACHE_SLOT_IDS if slots[sid]["status"] == "PRESENT"]

    chain_doc = uwg_assessment.get("r1b_governed_receipt_chain") or {}
    rs_chain_status = str(chain_doc.get("read_surface_refresh_status") or "") if chain_doc else ""
    if rs_chain_status == "NOT_APPLICABLE" and slots.get("read_surface_refresh_receipt", {}).get("status") == "MISSING":
        slots["read_surface_refresh_receipt"] = _slot(
            "read_surface_refresh_receipt",
            status="NOT_APPLICABLE",
            artifact_name="r1b_governed_receipt_chain.json",
            source_path=_repo_rel(repo_root, artifact_dir / "r1b_governed_receipt_chain.json"),
            owner_class="NOT_APPLICABLE",
            notes=str(chain_doc.get("reason") or W6C_READ_SURFACE_DEFERRED_REASON),
        )

    if uwg_assessment.get("durable_vector_persistence_proven"):
        persistence_status = "PROVEN_GOVERNED_VECTOR_CHAIN"
    elif isinstance(chain_doc, Mapping) and chain_doc.get("semantic_cache_persistence_status"):
        persistence_status = str(chain_doc["semantic_cache_persistence_status"])
    elif uwg_assessment.get("governed_chroma_refresh_proven"):
        persistence_status = "PROVEN_GOVERNED_VECTOR_CHAIN"
    elif uwg_assessment.get("durable_proof_chain_complete"):
        persistence_status = "PROVEN_UWG_CHAIN_ONLY"
    elif uwg_assessment.get("r1b_uwg_chain_core_complete"):
        persistence_status = "PROVEN_UWG_CHAIN_ONLY"
    elif uwg_assessment.get("uwg_path_present"):
        persistence_status = "PARTIAL_UWG_ARTIFACTS_ONLY"
    else:
        persistence_status = "NOT_PROVEN"

    return {
        "schema_version": SCHEMA_SEMANTIC_CACHE_SLOTS,
        "generated_at_utc": _utc_now(),
        "producer": _CANONICAL_PRODUCER,
        "semantic_cache_persistence_status": persistence_status,
        "vector_persistence_claimed": bool(uwg_assessment.get("durable_vector_persistence_proven")),
        "chroma_persistence_claimed": bool(uwg_assessment.get("chroma_projection_complete")),
        "durable_proof_present": bool(uwg_assessment.get("governed_chroma_refresh_proven")),
        "r1b_uwg_chain_core_complete": bool(uwg_assessment.get("r1b_uwg_chain_core_complete")),
        "read_surface_refresh_complete": bool(
            uwg_assessment.get("read_surface_refresh_complete")
        ),
        "chroma_projection_complete": bool(uwg_assessment.get("chroma_projection_complete")),
        "durable_vector_persistence_proven": bool(
            uwg_assessment.get("durable_vector_persistence_proven")
        ),
        "slots": slots,
        "missing_slot_ids": missing_ids,
        "drift_slot_ids": drift_ids,
        "present_slot_ids": present_ids,
        "explicit_non_claims": [
            "semantic cache persistence slots record audit posture only",
            "NOT_PROVEN unless full UWG/L4/refresh chain present with canonical receipts",
            "direct core D2 Chroma upsert remains NON_DURABLE_INDEX_WRITE",
            "request_intent_vector_ref is not request_intent_embedding_ref without mapping receipt",
            "IndexRefreshReceipt is not read_surface_refresh_receipt without bridge receipt",
        ],
    }


def finalize_semantic_cache_quarantine(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    integrated_dir: Path | None,
) -> dict[str, Any]:
    """Write assertion artifact; return bundle for evidence_package_index."""
    uwg = assess_uwg_durable_write_chain(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        integrated_dir=integrated_dir,
    )
    chroma_class = classify_shadow_chroma_write_path(uwg_assessment=uwg)
    assertion_path = artifact_dir / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT
    assertion = build_no_direct_chroma_write_bypass_assertion(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        uwg_assessment=uwg,
        chroma_classification=chroma_class,
    )
    assertion_path.write_text(
        json.dumps(assertion, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    uwg = assess_uwg_durable_write_chain(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        integrated_dir=integrated_dir,
    )
    chroma_class = classify_shadow_chroma_write_path(uwg_assessment=uwg)
    assertion = build_no_direct_chroma_write_bypass_assertion(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        uwg_assessment=uwg,
        chroma_classification=chroma_class,
    )
    assertion_path.write_text(
        json.dumps(assertion, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assertion_rel = _repo_rel(repo_root, assertion_path)
    slots_doc = build_semantic_cache_persistence_slots(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        integrated_dir=integrated_dir,
        uwg_assessment=uwg,
        assertion_path=assertion_rel,
    )
    return {
        "uwg_assessment": uwg,
        "chroma_classification": chroma_class,
        "no_direct_chroma_write_bypass_assertion": assertion,
        "no_direct_chroma_write_bypass_assertion_path": assertion_path,
        "semantic_cache_persistence_slots": slots_doc,
        "r1b_governed_receipt_chain": uwg.get("r1b_governed_receipt_chain") or {},
    }


__all__ = [
    "CHROMA_CLASS_GOVERNED_REFRESH",
    "CHROMA_CLASS_NON_DURABLE",
    "CHROMA_CLASS_PROHIBITED_CLAIM",
    "CHROMA_UPSERT_PATHS",
    "CULPRIT_CALL_CHAIN",
    "NO_DIRECT_CHROMA_ASSERTION_ARTIFACT",
    "PROMOTE_TO_LONG_TERM_CALLERS",
    "SEMANTIC_CACHE_SLOT_IDS",
    "assess_uwg_durable_write_chain",
    "build_no_direct_chroma_write_bypass_assertion",
    "build_semantic_cache_persistence_slots",
    "classify_shadow_chroma_write_path",
    "finalize_semantic_cache_quarantine",
]
