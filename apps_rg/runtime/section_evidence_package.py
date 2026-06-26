"""Section run evidence package — refs-only linkage to core spine artifacts (W1–W4).

Does not emit agentic_core L7 artifacts, 99 RuntimeProofBundle, or UWG/Chroma writes.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L2_execution.utils import write_gateway as _wg

from apps_rg.runtime.section_binding_taxonomy import (
    APPS_RG_DOMAIN_ARTIFACTS,
    APPS_RG_SECTION_SHIM_PREFERRED_NAMES,
    L7_CORE_ARTIFACTS,
    W4_INTEGRATED_PARENT_BUNDLE_INDEX,
    W4_VERIFIED_EXTERNAL_ARTIFACTS,
    design_law_owner_for_artifact,
)

EVIDENCE_PACKAGE_INDEX_ARTIFACT = "evidence_package_index.json"
SUBPHASE_COVERAGE_INDEX_ARTIFACT = "spine_subphase_coverage_index.json"
RUN_LINKS_LANE_FILENAME = "RUN_LINKS.json"

SCHEMA_EVIDENCE_PACKAGE_V2 = "evidence_package_index_v2"
SCHEMA_SUBPHASE_COVERAGE_V1 = "spine_subphase_coverage_v1"
_CANONICAL_PRODUCER = "apps_rg_section_evidence_package"

# Design-law owner taxonomy (W2)
OWNER_CORE_RUNTIME_CONTRACT = "CORE_RUNTIME_CONTRACT"
OWNER_CORE_RUNTIME_RECEIPT = "CORE_RUNTIME_RECEIPT"
OWNER_CORE_GATE_VERDICT = "CORE_GATE_VERDICT"
OWNER_CORE_L5_CERTIFICATION = "CORE_L5_CERTIFICATION"
OWNER_CORE_L7_PROJECTION = "CORE_L7_PROJECTION"
OWNER_CORE_99_PROOF = "CORE_99_PROOF"
OWNER_CORE_UWG_WRITE_ADMISSION = "CORE_UWG_WRITE_ADMISSION"
OWNER_CORE_L4_DURABLE_STATE = "CORE_L4_DURABLE_STATE"
OWNER_APP_DOMAIN_EVIDENCE = "APP_DOMAIN_EVIDENCE"
OWNER_APP_BINDING_MANIFEST = "APP_BINDING_MANIFEST"
OWNER_APP_ADAPTER = "APP_ADAPTER"
OWNER_APP_SHIM = "APP_SHIM"
OWNER_IMPORTED_CORE_SNAPSHOT = "IMPORTED_CORE_EVIDENCE_SNAPSHOT"
OWNER_VERIFIED_EXTERNAL_REF = "VERIFIED_EXTERNAL_REF"
OWNER_DESIGN_ONLY = "DESIGN_ONLY"
OWNER_MISSING = "MISSING"
OWNER_DRIFT = "DRIFT"
OWNER_NOT_APPLICABLE = "NOT_APPLICABLE"

REF_KIND_VERIFIED_EXTERNAL = "VERIFIED_EXTERNAL_REF"
REF_KIND_IMPORTED_SNAPSHOT = "IMPORTED_CORE_EVIDENCE_SNAPSHOT"

INTEGRATED_RUNS_REL = "artifacts/apps_rg/runs"
CORRELATED_CLI_RUN_ENV = "APPS_RG_CORRELATED_CLI_RUN"
CERTIFICATION_UWG_REL = (
    "artifacts/certification/integrated_runtime/uwg_commit_latest"
)

_CORRELATION_METHOD_ENV = "env_APPS_RG_CORRELATED_CLI_RUN"
_CORRELATION_METHOD_SECTION_MANIFEST = "section_run_manifest_integrated_ref"
_CORRELATION_METHOD_MODULAR_POINTER = "modular_r4_latest_real_run_pointer"
_CORRELATION_METHOD_RUN_LINKS = "integrated_RUN_LINKS_lane_bundle_refs"
_CORRELATION_METHOD_BUNDLE_INDEX = "integrated_RUN_BUNDLE_INDEX_entry"
_CORRELATION_METHOD_CORPUS = "integrated_top_level_json_corpus"
_CORRELATION_METHOD_PAYLOAD = "section_runtime_payload_correlation_id"
_CORRELATION_METHOD_ANCESTOR_CLI = "modular_r4_ancestor_cli_run_dir"

_L7_PRODUCER_HINTS: dict[str, str] = {
    "agentic_core_how_trace.json": "agentic_core.L7_auditability.how_trace.how_trace_builder",
    "agentic_core_l7_route_family_coverage.json": (
        "agentic_core.L7_auditability.coverage.route_family_l7_coverage"
    ),
    "agentic_core_spine_proof.json": "agentic_core.runtime.artifacts.spine_proof_bundle",
    "integrated_runtime_artifact_manifest.json": (
        "agentic_core.runtime.artifacts.integrated_runtime_emitter"
    ),
    "runtime_trace_snapshot.json": "agentic_core.runtime.artifacts.integrated_runtime_emitter",
    "runtime_gate_verdict_bundle.json": (
        "agentic_core.runtime.entrypoints.integrated_safe_reuse_run"
    ),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_rel(repo_root: Path, path: Path) -> str | None:
    if not path.is_file() and not path.is_dir():
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


def mirror_preferred_section_shim_names(artifact_dir: Path) -> list[dict[str, str]]:
    """Dual-write preferred app-owned names for legacy section shim receipts."""

    mirrored: list[dict[str, str]] = []
    for legacy, preferred in APPS_RG_SECTION_SHIM_PREFERRED_NAMES.items():
        legacy_path = artifact_dir / legacy
        preferred_path = artifact_dir / preferred
        if not legacy_path.is_file():
            continue
        if not preferred_path.exists():
            _wg.write_bytes(preferred_path, legacy_path.read_bytes())
        mirrored.append({"legacy": legacy, "preferred": preferred})
    return mirrored


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def build_evidence_ref_record(
    *,
    ref_kind: str,
    artifact_name: str,
    source_path: str | None,
    local_path: str | None,
    source_owner_layer: str,
    owner_class: str,
    producer_module: str,
    sha256: str,
    trust_status: str,
    trust_reason: str,
    runtime_authority_claimed: bool = False,
    explicit_non_claims: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ref_kind": ref_kind,
        "artifact_name": artifact_name,
        "source_path": source_path,
        "local_path": local_path,
        "source_owner_layer": source_owner_layer,
        "owner_class": owner_class,
        "producer_module": producer_module,
        "sha256": sha256,
        "trust_status": trust_status,
        "trust_reason": trust_reason,
        "runtime_authority_claimed": runtime_authority_claimed,
        "explicit_non_claims": explicit_non_claims or [],
    }


def assert_evidence_ref_shape(ref: Mapping[str, Any]) -> None:
    required = (
        "ref_kind",
        "artifact_name",
        "source_path",
        "local_path",
        "source_owner_layer",
        "owner_class",
        "producer_module",
        "sha256",
        "trust_status",
        "trust_reason",
        "runtime_authority_claimed",
        "explicit_non_claims",
    )
    for k in required:
        if k not in ref:
            raise ValueError(f"evidence ref missing key: {k}")
    if ref["ref_kind"] not in (REF_KIND_VERIFIED_EXTERNAL, REF_KIND_IMPORTED_SNAPSHOT):
        raise ValueError(f"invalid ref_kind: {ref['ref_kind']!r}")


@dataclass(frozen=True)
class IntegratedCorrelationResult:
    integrated_dir: Path | None
    correlation_method: str | None
    correlation_missing_reason: str | None


def _resolve_cli_run_dir(repo_root: Path, token: str) -> Path | None:
    raw = token.strip().replace("\\", "/")
    if not raw:
        return None
    cand = Path(raw)
    if not cand.is_absolute():
        cand = (repo_root / cand).resolve()
    else:
        cand = cand.resolve()
    if cand.is_dir() and cand.name.startswith("cli_"):
        return cand
    runs = repo_root / Path(*INTEGRATED_RUNS_REL.split("/"))
    by_name = runs / raw if not raw.startswith("cli_") else runs / raw.split("/")[-1]
    if by_name.is_dir():
        return by_name
    return None


def _section_id_from_artifact_dir(artifact_dir: Path) -> str | None:
    for name in ("run_manifest.json", "runtime_payload.json"):
        doc = _load_json(artifact_dir / name)
        sid = str(doc.get("section_id") or doc.get("lane") or "").strip()
        if sid:
            return sid
    return None


def _discover_by_env(repo_root: Path) -> tuple[Path | None, str | None]:
    raw = os.environ.get(CORRELATED_CLI_RUN_ENV, "").strip()
    if not raw:
        return None, None
    hit = _resolve_cli_run_dir(repo_root, raw)
    if hit is None:
        return None, f"{CORRELATED_CLI_RUN_ENV}={raw!r} did not resolve to an existing cli_* directory"
    return hit, _CORRELATION_METHOD_ENV


def _discover_by_section_manifest(repo_root: Path, artifact_dir: Path) -> tuple[Path | None, str | None]:
    for name in ("run_manifest.json", "runtime_payload.json"):
        doc = _load_json(artifact_dir / name)
        for key in ("integrated_cli_run_ref", "correlated_integrated_run_id", "integrated_run_id", "parent_run_id"):
            token = str(doc.get(key) or "").strip()
            if not token:
                continue
            hit = _resolve_cli_run_dir(repo_root, token)
            if hit is not None:
                return hit, _CORRELATION_METHOD_SECTION_MANIFEST
    return None, None


def _modular_pointer_run_dir(repo_root: Path, cli_dir: Path, section_id: str) -> Path | None:
    lane_base = cli_dir / "modular_r4" / "sections" / section_id
    if not lane_base.is_dir():
        return None
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    ptr_names = (
        ("latest_successful_real_run.json",)
        if product_fail_closed_runtime()
        else ("latest_real_run.json", "latest_successful_real_run.json")
    )
    for ptr_name in ptr_names:
        ptr = lane_base / ptr_name
        if not ptr.is_file():
            continue
        doc = _load_json(ptr)
        rel = str(doc.get("run_dir") or doc.get("artifact_dir") or "").strip()
        if not rel:
            continue
        rd = (repo_root / rel).resolve() if not Path(rel).is_absolute() else Path(rel).resolve()
        if rd.is_dir():
            return rd
    return None


def _discover_by_modular_pointer(
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
) -> tuple[Path | None, str | None]:
    runs_dir = repo_root / Path(*INTEGRATED_RUNS_REL.split("/"))
    if not runs_dir.is_dir():
        return None, None
    section_resolved = artifact_dir.resolve()
    candidates: list[tuple[float, Path]] = []
    for child in sorted(runs_dir.iterdir()):
        if not child.is_dir() or not child.name.startswith("cli_"):
            continue
        run_dir = _modular_pointer_run_dir(repo_root, child, section_id)
        if run_dir is not None and run_dir.resolve() == section_resolved:
            candidates.append((child.stat().st_mtime, child))
    if not candidates:
        return None, None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1], _CORRELATION_METHOD_MODULAR_POINTER


def _discover_by_integrated_bundle_index(
    repo_root: Path,
    section_root_posix: str,
) -> tuple[Path | None, str | None]:
    runs_dir = repo_root / Path(*INTEGRATED_RUNS_REL.split("/"))
    if not runs_dir.is_dir():
        return None, None
    candidates: list[tuple[float, Path]] = []
    for child in sorted(runs_dir.iterdir()):
        if not child.is_dir() or not child.name.startswith("cli_"):
            continue
        idx_path = child / "RUN_BUNDLE_INDEX.json"
        if not idx_path.is_file():
            continue
        doc = _load_json(idx_path)
        for entry in doc.get("entries") or []:
            if not isinstance(entry, dict):
                continue
            rel = str(entry.get("relative_path") or entry.get("path") or "")
            if section_root_posix in rel.replace("\\", "/"):
                candidates.append((child.stat().st_mtime, child))
                break
    if not candidates:
        return None, None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1], _CORRELATION_METHOD_BUNDLE_INDEX


def _discover_integrated_run_by_lane_path(
    repo_root: Path,
    section_root_posix: str,
) -> tuple[Path | None, str | None]:
    """Find cli_* integrated run whose RUN_LINKS references this lane proof root."""
    runs_dir = repo_root / Path(*INTEGRATED_RUNS_REL.split("/"))
    if not runs_dir.is_dir():
        return None, None
    candidates: list[tuple[float, Path, str]] = []
    for child in sorted(runs_dir.iterdir()):
        if not child.is_dir() or not child.name.startswith("cli_"):
            continue
        links_path = child / RUN_LINKS_LANE_FILENAME
        if links_path.is_file():
            doc = _load_json(links_path)
            for row in doc.get("lane_bundle_refs") or []:
                if not isinstance(row, dict):
                    continue
                root = str(row.get("root_path") or "")
                if root == section_root_posix or section_root_posix in root:
                    candidates.append((child.stat().st_mtime, child, _CORRELATION_METHOD_RUN_LINKS))
                    break
            continue
        corpus_parts: list[str] = []
        for p in child.glob("*.json"):
            if p.is_file() and p.stat().st_size < 512_000:
                corpus_parts.append(_safe_read(p))
        if section_root_posix in "\n".join(corpus_parts):
            candidates.append((child.stat().st_mtime, child, _CORRELATION_METHOD_CORPUS))
    if not candidates:
        return None, None
    candidates.sort(key=lambda x: x[0], reverse=True)
    hit = candidates[0]
    return hit[1], hit[2]


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _discover_by_payload_correlation(repo_root: Path, artifact_dir: Path) -> tuple[Path | None, str | None]:
    payload = _load_json(artifact_dir / "runtime_payload.json")
    for key in ("correlation_id", "integrated_run_id", "parent_run_id"):
        cid = str(payload.get(key) or "").strip()
        if not cid:
            continue
        runs_dir = repo_root / Path(*INTEGRATED_RUNS_REL.split("/"))
        if not runs_dir.is_dir():
            continue
        for child in runs_dir.glob("cli_*"):
            if child.is_dir() and (child.name == cid or cid in child.name):
                return child, _CORRELATION_METHOD_PAYLOAD
    return None, None


def build_correlation_missing_reason(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str | None,
    env_override_invalid: str | None = None,
) -> str:
    runs_dir = repo_root / Path(*INTEGRATED_RUNS_REL.split("/"))
    parts = [
        "no correlated integrated cli_* run discovered for this section proof root",
        f"section_root={_repo_rel(repo_root, artifact_dir)!r}",
    ]
    if section_id:
        parts.append(f"section_id={section_id!r}")
    if env_override_invalid:
        parts.append(env_override_invalid)
    if not runs_dir.is_dir():
        parts.append(f"integrated runs directory missing: {INTEGRATED_RUNS_REL}")
    else:
        cli_count = sum(1 for c in runs_dir.iterdir() if c.is_dir() and c.name.startswith("cli_"))
        parts.append(f"scanned_cli_run_dirs={cli_count}")
        parts.append(
            "tried: env_APPS_RG_CORRELATED_CLI_RUN, section_run_manifest, "
            "modular_r4/sections/<lane>/latest_real_run.json, integrated RUN_LINKS, "
            "integrated RUN_BUNDLE_INDEX, integrated top-level json corpus, runtime_payload correlation_id"
        )
    return "; ".join(parts)


def discover_integrated_correlation(
    repo_root: Path,
    artifact_dir: Path,
    *,
    section_id: str | None = None,
) -> IntegratedCorrelationResult:
    """Discover integrated cli_* run correlated to this section proof folder (W4)."""
    repo_root = Path(repo_root)
    artifact_dir = Path(artifact_dir)
    sid = section_id or _section_id_from_artifact_dir(artifact_dir)
    section_root = _repo_rel(repo_root, artifact_dir)
    env_invalid: str | None = None

    hit, method = _discover_by_env(repo_root)
    if hit is not None:
        return IntegratedCorrelationResult(hit, method, None)
    raw_env = os.environ.get(CORRELATED_CLI_RUN_ENV, "").strip()
    if raw_env:
        env_invalid = f"{CORRELATED_CLI_RUN_ENV}={raw_env!r} did not resolve to cli_* directory"

    from apps_rg.runtime.integrated_lane_evidence_packaging import (
        discover_integrated_cli_run_by_ancestor,
    )

    hit, method = discover_integrated_cli_run_by_ancestor(repo_root, artifact_dir)
    if hit is not None:
        return IntegratedCorrelationResult(hit, method, None)

    if section_root:
        hit, method = _discover_by_section_manifest(repo_root, artifact_dir)
        if hit is not None:
            return IntegratedCorrelationResult(hit, method, None)

        if sid:
            hit, method = _discover_by_modular_pointer(repo_root, artifact_dir, sid)
            if hit is not None:
                return IntegratedCorrelationResult(hit, method, None)

        hit, method = _discover_integrated_run_by_lane_path(repo_root, section_root)
        if hit is not None:
            return IntegratedCorrelationResult(hit, method, None)

        hit, method = _discover_by_integrated_bundle_index(repo_root, section_root)
        if hit is not None:
            return IntegratedCorrelationResult(hit, method, None)

    hit, method = _discover_by_payload_correlation(repo_root, artifact_dir)
    if hit is not None:
        return IntegratedCorrelationResult(hit, method, None)

    missing = build_correlation_missing_reason(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=sid,
        env_override_invalid=env_invalid,
    )
    return IntegratedCorrelationResult(None, None, missing)


def discover_correlated_integrated_run(
    repo_root: Path,
    artifact_dir: Path,
    *,
    section_id: str | None = None,
) -> Path | None:
    return discover_integrated_correlation(
        repo_root, artifact_dir, section_id=section_id
    ).integrated_dir


def _assess_l7_file(filename: str, doc: Mapping[str, Any]) -> tuple[bool, str]:
    from apps_rg.runtime.section_l7_binding_manifest import _L7_TRUST_ASSESSORS

    assessor = _L7_TRUST_ASSESSORS.get(filename)
    if assessor is None:
        return False, "no_assessor"
    return assessor(doc)


def build_verified_external_refs_for_integrated(
    repo_root: Path,
    integrated_dir: Path,
    *,
    section_artifact_dir: Path,
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    base_non_claims = [
        "verified external ref does not relocate core runtime authority into apps_rg section folder",
        "hash-only linkage; L7 artifacts are not copied into the section run folder",
        "apps_rg section folder remains narrative audit entrypoint only",
        "no semantic cache persistence claimed",
        "no Chroma vector persistence claimed",
        "no UWG/L4 durable write chain claimed from external refs alone",
        "99 RuntimeProofBundle not claimed",
    ]
    for filename in W4_VERIFIED_EXTERNAL_ARTIFACTS:
        local = section_artifact_dir / filename
        if local.is_file():
            continue
        source = integrated_dir / filename
        if not source.is_file():
            continue
        doc = _load_json(source)
        trusted, reason = _assess_l7_file(filename, doc)
        owner = OWNER_VERIFIED_EXTERNAL_REF if trusted else OWNER_DRIFT
        refs.append(
            build_evidence_ref_record(
                ref_kind=REF_KIND_VERIFIED_EXTERNAL,
                artifact_name=filename,
                source_path=_repo_rel(repo_root, source),
                local_path=None,
                source_owner_layer="agentic_core",
                owner_class=owner,
                producer_module=_L7_PRODUCER_HINTS.get(filename, "agentic_core.integrated_runtime"),
                sha256=_sha256_file(source),
                trust_status="trusted" if trusted else "untrusted",
                trust_reason=reason,
                runtime_authority_claimed=False,
                explicit_non_claims=list(base_non_claims),
            )
        )

    parent_idx = integrated_dir / W4_INTEGRATED_PARENT_BUNDLE_INDEX
    if parent_idx.is_file():
        refs.append(
            build_evidence_ref_record(
                ref_kind=REF_KIND_VERIFIED_EXTERNAL,
                artifact_name=W4_INTEGRATED_PARENT_BUNDLE_INDEX,
                source_path=_repo_rel(repo_root, parent_idx),
                local_path=None,
                source_owner_layer="apps_rg",
                owner_class=OWNER_VERIFIED_EXTERNAL_REF,
                producer_module="apps_rg.runtime.run_bundle_index",
                sha256=_sha256_file(parent_idx),
                trust_status="trusted",
                trust_reason="integrated_parent_run_bundle_index_present",
                runtime_authority_claimed=False,
                explicit_non_claims=[
                    *base_non_claims,
                    "parent integrated RUN_BUNDLE_INDEX is integrated-run catalog only",
                ],
            )
        )
    return refs


def build_certification_reference_hints(repo_root: Path) -> list[dict[str, Any]]:
    """Non-run certification paths for UWG/L5 design reference only (not imported by default)."""
    hints: list[dict[str, Any]] = []
    uwg_dir = repo_root / Path(*CERTIFICATION_UWG_REL.split("/"))
    if not uwg_dir.is_dir():
        return hints
    for name, owner, layer in (
        ("commit_request.json", OWNER_CORE_UWG_WRITE_ADMISSION, "agentic_core"),
        ("uwg_commit_receipt.json", OWNER_CORE_UWG_WRITE_ADMISSION, "agentic_core"),
        ("uwg_refresh_receipts.json", OWNER_CORE_L4_DURABLE_STATE, "agentic_core"),
    ):
        p = uwg_dir / name
        if not p.is_file():
            continue
        hints.append(
            build_evidence_ref_record(
                ref_kind=REF_KIND_VERIFIED_EXTERNAL,
                artifact_name=name,
                source_path=_repo_rel(repo_root, p),
                local_path=None,
                source_owner_layer=layer,
                owner_class=owner,
                producer_module="agentic_core.runtime.entrypoints.integrated_uwg_commit_run",
                sha256=_sha256_file(p),
                trust_status="reference_only",
                trust_reason="certification_fixture_not_section_run_correlated",
                runtime_authority_claimed=False,
                explicit_non_claims=[
                    "certification path is not proof for this section run unless correlated",
                    "semantic cache vector persistence not claimed from certification hint alone",
                ],
            )
        )
    return hints


@dataclass(frozen=True)
class _SubphaseSpec:
    subphase_id: str
    spine_group: str
    default_na: bool = False
    c07_kind: str | None = None  # real | alias | drift


def _subphase_catalog() -> tuple[_SubphaseSpec, ...]:
    specs: list[_SubphaseSpec] = []
    for i in range(1, 6):
        specs.append(_SubphaseSpec(f"U0.{i}", "U0"))
    for i in range(1, 7):
        specs.append(_SubphaseSpec(f"L1.{i}", "L1"))
    for i in range(1, 7):
        specs.append(_SubphaseSpec(f"L0.{i}", "L0"))
    for i in range(0, 7):
        specs.append(_SubphaseSpec(f"C0.{i}", "C0"))
    specs.append(_SubphaseSpec("C0.7", "C0", c07_kind="real"))
    for i in range(0, 8):
        specs.append(_SubphaseSpec(f"PA.{i}", "PA"))
    for i in range(1, 5):
        specs.append(_SubphaseSpec(f"L3.{i}", "L3", default_na=True))
    for e in ("E1", "E2", "E3", "E4", "E5"):
        specs.append(_SubphaseSpec(e, "L2"))
    for i in range(1, 8):
        specs.append(_SubphaseSpec(f"Exit.5.{i}", "Exit"))
    for letter in "ABCDEFGHIJ":
        specs.append(_SubphaseSpec(f"X1{letter}", "Exit"))
    specs.extend(
        [
            _SubphaseSpec("X2", "Exit"),
            _SubphaseSpec("X3", "Exit"),
        ]
    )
    for i in range(1, 8):
        specs.append(_SubphaseSpec(f"UWG.{i}", "UWG"))
    specs.append(_SubphaseSpec("L4.durable_write", "L4"))
    specs.append(_SubphaseSpec("L4.read_surface_refresh", "L4"))
    for i in range(1, 8):
        specs.append(_SubphaseSpec(f"L6.{i}", "L6"))
    for suffix in ("1", "2", "3", "4", "5", "6", "7", "8", "8a"):
        specs.append(_SubphaseSpec(f"00A.{suffix}", "L5"))
    for i in range(1, 30):
        specs.append(_SubphaseSpec(f"00C.G{i:02d}", "00C"))
    specs.extend(
        [
            _SubphaseSpec("L7", "L7"),
            _SubphaseSpec("99", "99"),
        ]
    )
    return tuple(specs)


def _present_local(artifact_dir: Path, name: str) -> bool:
    return (artifact_dir / name).is_file()


def _coverage_for_subphase(
    spec: _SubphaseSpec,
    *,
    artifact_dir: Path,
    verified_refs: list[dict[str, Any]],
    integrated_dir: Path | None,
) -> dict[str, Any]:
    refs_by_name = {r["artifact_name"]: r for r in verified_refs}
    sid = spec.subphase_id

    def row(
        status: str,
        *,
        evidence_ref: str | None = None,
        owner_class: str = OWNER_MISSING,
        notes: str = "",
    ) -> dict[str, Any]:
        out: dict[str, Any] = {
            "subphase_id": sid,
            "spine_group": spec.spine_group,
            "coverage_status": status,
            "evidence_ref": evidence_ref,
            "owner_class": owner_class,
            "notes": notes,
        }
        if spec.c07_kind:
            out["c07_classification"] = spec.c07_kind
        return out

    if spec.default_na:
        return row(
            OWNER_NOT_APPLICABLE,
            notes="section modular CLI path; managed workflow not exercised",
        )

    if sid.startswith("U0."):
        if _present_local(artifact_dir, "validated_request.json"):
            return row("PRESENT", evidence_ref="validated_request.json", owner_class=OWNER_APP_SHIM)
        return row(OWNER_MISSING, notes="ValidatedRequest shim absent")

    if sid.startswith("L1."):
        if _present_local(artifact_dir, "l1_plan_contract.json"):
            return row("PRESENT", evidence_ref="l1_plan_contract.json", owner_class=OWNER_APP_SHIM)
        return row(OWNER_MISSING)

    if sid.startswith("L0."):
        if _present_local(artifact_dir, "route_contract.json"):
            return row("PRESENT", evidence_ref="route_contract.json", owner_class=OWNER_APP_SHIM)
        return row(OWNER_MISSING)

    if sid.startswith("C0.") and sid != "C0.7":
        if _present_local(artifact_dir, "final_evidence_contract_bridge.json"):
            return row(
                "PRESENT",
                evidence_ref="final_evidence_contract_bridge.json",
                owner_class=OWNER_APP_SHIM,
                notes="bridge/snapshot shim; not spine FinalEvidenceContract",
            )
        return row(OWNER_MISSING, notes="C0 FEC bridge absent on section path")

    if sid == "C0.7":
        return row(
            OWNER_NOT_APPLICABLE,
            owner_class=OWNER_DESIGN_ONLY,
            notes=(
                "C0.7 is real agentic_core observability subphase (docs/tests); "
                "not emitted as section-run artifact — alias/drift if claimed via apps shim"
            ),
        )

    if sid.startswith("PA."):
        if _present_local(artifact_dir, "compiled_prompt_artifact.json"):
            return row("PRESENT", evidence_ref="compiled_prompt_artifact.json", owner_class=OWNER_APP_SHIM)
        return row(OWNER_MISSING)

    if sid in ("E1", "E2", "E3", "E4", "E5"):
        if _present_local(artifact_dir, "l2_execution_packet.json") or _present_local(
            artifact_dir, "sealed_l2_artifact.json"
        ):
            return row("PRESENT", evidence_ref="l2_execution_packet.json", owner_class=OWNER_APP_SHIM)
        return row(OWNER_MISSING)

    if sid.startswith("Exit.5.") or sid.startswith("X1"):
        if _present_local(artifact_dir, "exit_review_packet.json"):
            return row("PRESENT", evidence_ref="exit_review_packet.json", owner_class=OWNER_APP_SHIM)
        return row(OWNER_MISSING)

    if sid == "X2":
        if _present_local(artifact_dir, "x2_gate_outputs.json"):
            return row(
                "PRESENT",
                evidence_ref="x2_gate_outputs.json",
                owner_class=OWNER_APP_DOMAIN_EVIDENCE,
                notes="apps_rg lane X2; not 00C GateVerdict",
            )
        return row(OWNER_MISSING)

    if sid == "X3":
        if _present_local(artifact_dir, "x3_disposition.json"):
            return row(
                "PRESENT",
                evidence_ref="x3_disposition.json",
                owner_class=OWNER_APP_SHIM,
                notes="section_x3 not authoritative spine Exit X3",
            )
        return row(OWNER_MISSING)

    if sid.startswith("UWG.") or sid.startswith("L4."):
        local_uwg = any(
            _present_local(artifact_dir, n)
            for n in ("commit_request.json", "state_commit_receipt.json", "uwg_commit_receipt.json")
        )
        if local_uwg:
            return row("PRESENT", owner_class=OWNER_CORE_UWG_WRITE_ADMISSION)
        return row(
            OWNER_MISSING,
            owner_class=OWNER_MISSING,
            notes="no UWG/L4 commit in section folder; vector/Chroma persistence not proven",
        )

    if sid.startswith("L6."):
        if _present_local(artifact_dir, "l6_shadow_eval_package.json"):
            return row(
                "PRESENT",
                evidence_ref="l6_shadow_eval_package.json",
                owner_class=OWNER_APP_DOMAIN_EVIDENCE,
                notes="shadow only; post-runtime boundary",
            )
        return row(OWNER_MISSING)

    if sid.startswith("00A."):
        if _present_local(artifact_dir, "one_spine_certification_receipt.json"):
            return row(
                "PRESENT",
                evidence_ref="one_spine_certification_receipt.json",
                owner_class=OWNER_APP_SHIM,
                notes="apps one-spine checklist; not L5 00A child certifier packet",
            )
        return row(OWNER_DESIGN_ONLY, notes="L5 00A certification not in section package")

    if sid.startswith("00C.G"):
        ext = refs_by_name.get("runtime_gate_verdict_bundle.json")
        if ext:
            return row(
                REF_KIND_VERIFIED_EXTERNAL,
                evidence_ref=ext.get("source_path"),
                owner_class=OWNER_DRIFT,
                notes="W2 cache bundle if present externally; not substantive G01-G29 mesh in section run",
            )
        return row(OWNER_MISSING, notes="00C G01-G29 GateVerdict mesh not in section run")

    if sid == "L7":
        local_how = _present_local(artifact_dir, "agentic_core_how_trace.json")
        ext_how = refs_by_name.get("agentic_core_how_trace.json")
        if local_how:
            return row("PRESENT", evidence_ref="agentic_core_how_trace.json", owner_class=OWNER_CORE_L7_PROJECTION)
        if ext_how and ext_how.get("trust_status") == "trusted":
            return row(
                REF_KIND_VERIFIED_EXTERNAL,
                evidence_ref=ext_how.get("source_path"),
                owner_class=OWNER_VERIFIED_EXTERNAL_REF,
                notes="core L7 at integrated run; not copied into section folder",
            )
        if integrated_dir is not None:
            return row(OWNER_MISSING, notes="integrated run linked but L7 surfaces incomplete/untrusted")
        return row(OWNER_MISSING, notes="no correlated integrated cli_* run for L7 refs")

    if sid == "99":
        if _present_local(artifact_dir, "runtime_proof_bundle.json"):
            return row(OWNER_DRIFT, notes="unexpected runtime_proof_bundle in section dir")
        if _present_local(artifact_dir, "section_runtime_proof_bundle.json"):
            return row(
                OWNER_DESIGN_ONLY,
                evidence_ref="section_runtime_proof_bundle.json",
                owner_class=OWNER_APP_SHIM,
                notes="section bundle explicitly not 99 RuntimeProofBundle",
            )
        return row(OWNER_DESIGN_ONLY, notes="99 RuntimeProofBundle producer not active in repo")

    return row(OWNER_MISSING)


def build_spine_subphase_coverage_index(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    verified_external_refs: list[dict[str, Any]],
    integrated_dir: Path | None,
) -> dict[str, Any]:
    rows = [
        _coverage_for_subphase(
            spec,
            artifact_dir=artifact_dir,
            verified_refs=verified_external_refs,
            integrated_dir=integrated_dir,
        )
        for spec in _subphase_catalog()
    ]
    status_counts: dict[str, int] = {}
    for r in rows:
        st = str(r["coverage_status"])
        status_counts[st] = status_counts.get(st, 0) + 1
    return {
        "schema_version": SCHEMA_SUBPHASE_COVERAGE_V1,
        "generated_at_utc": _utc_now(),
        "producer": _CANONICAL_PRODUCER,
        "section_id": section_id,
        "run_id": run_id,
        "integrated_run_ref": _repo_rel(repo_root, integrated_dir) if integrated_dir else None,
        "subphases": rows,
        "subphase_count": len(rows),
        "coverage_status_counts": status_counts,
        "explicit_non_claims": [
            "coverage index records audit posture; not runtime PASS for core spine",
            "PRESENT on apps shim does not imply core runtime authority",
            "semantic cache vector persistence not proven without UWG/L4 receipts in package",
            "Chroma collection existence is not durable persistence proof",
        ],
    }


def build_lane_run_links_document(
    repo_root: Path,
    artifact_dir: Path,
    *,
    section_id: str,
    run_id: str,
    integrated_dir: Path | None,
    correlation_id: str | None = None,
    correlation_method: str | None = None,
    correlation_missing_reason: str | None = None,
) -> dict[str, Any]:
    from apps_rg.runtime.run_bundle_index import (
        RUN_BUNDLE_INDEX_FILENAME,
        build_log_discovery_metadata,
        load_apps_rg_pipeline_namespaces,
        repo_relative_posix,
    )

    art_ns, log_ns = load_apps_rg_pipeline_namespaces(repo_root)
    bundle_ref = artifact_dir / RUN_BUNDLE_INDEX_FILENAME
    lane_bundle_self = {
        "lane": section_id,
        "proof_mode": "real",
        "run_id": run_id,
        "bundle_index_ref": repo_relative_posix(repo_root, bundle_ref)
        if bundle_ref.is_file()
        else None,
        "root_path": repo_relative_posix(repo_root, artifact_dir.resolve()),
        "exists": bundle_ref.is_file(),
        "producer": "apps_rg.runtime.section_evidence_package.build_lane_run_links_document",
    }
    integrated_refs: list[dict[str, Any]] = []
    if integrated_dir is not None and integrated_dir.is_dir():
        integrated_refs.append(
            {
                "kind": "correlated_integrated_cli_run",
                "integrated_run_id": integrated_dir.name,
                "root_path": repo_relative_posix(repo_root, integrated_dir.resolve()),
                "run_links_ref": repo_relative_posix(repo_root, integrated_dir / RUN_LINKS_LANE_FILENAME)
                if (integrated_dir / RUN_LINKS_LANE_FILENAME).is_file()
                else None,
                "bundle_index_ref": repo_relative_posix(
                    repo_root, integrated_dir / RUN_BUNDLE_INDEX_FILENAME
                )
                if (integrated_dir / RUN_BUNDLE_INDEX_FILENAME).is_file()
                else None,
                "exists": True,
                "producer": _CANONICAL_PRODUCER,
            }
        )
    return {
        "schema_version": "1",
        "correlation_id": correlation_id,
        "integrated_run_id": integrated_dir.name if integrated_dir else None,
        "correlation_method": correlation_method,
        "correlation_missing_reason": correlation_missing_reason,
        "section_run_id": run_id,
        "section_id": section_id,
        "created_at": _utc_now(),
        "root_path": repo_relative_posix(repo_root, artifact_dir.resolve()),
        "artifact_namespace": art_ns,
        "log_namespace": log_ns,
        "log_discovery": build_log_discovery_metadata(repo_root),
        "lane_bundle_refs": [lane_bundle_self],
        "integrated_run_refs": integrated_refs,
        "aggregate_refs": [],
        "modular_sections_root": {
            "mode": "default",
            "source_env_var": "APPS_RG_MODULAR_R4_SECTIONS_ROOT",
            "manifest_ref": None,
            "root_path": None,
            "exists": False,
            "notes": "section proof root is narrative audit package for this lane run",
        },
    }


def build_evidence_package_index(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    binding_manifest: Mapping[str, Any],
    subphase_index: Mapping[str, Any],
    verified_external_refs: list[dict[str, Any]],
    imported_snapshots: list[dict[str, Any]],
    integrated_dir: Path | None,
    correlation_method: str | None = None,
    correlation_missing_reason: str | None = None,
    semantic_cache_quarantine: Mapping[str, Any] | None = None,
    r1b_governed_receipt_chain: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    owner_summary: dict[str, int] = {}
    for oc in binding_manifest.get("design_law_owner_classifications", {}).values():
        owner_summary[str(oc)] = owner_summary.get(str(oc), 0) + 1
    for ref in verified_external_refs:
        oc = str(ref.get("owner_class") or "")
        owner_summary[oc] = owner_summary.get(oc, 0) + 1

    missing_core = list(binding_manifest.get("missing_l7_surfaces") or [])
    missing_core.extend(
        n
        for n in (binding_manifest.get("missing_99_surfaces") or [])
        if n not in missing_core
    )
    if not binding_manifest.get("durable_write_evidence", {}).get("durable_write_claim_allowed"):
        missing_core.append("UWG/L4_durable_write_chain")

    sc_slots_doc = (semantic_cache_quarantine or {}).get("semantic_cache_persistence_slots") or {}
    sc_status = str(sc_slots_doc.get("semantic_cache_persistence_status") or "NOT_PROVEN")
    chroma_class = str((semantic_cache_quarantine or {}).get("chroma_classification") or "")
    missing_sc = list(sc_slots_doc.get("missing_slot_ids") or [])
    for slot_id in missing_sc:
        token = f"semantic_cache/{slot_id}"
        if token not in missing_core:
            missing_core.append(token)

    assertion_ref = None
    ap = (semantic_cache_quarantine or {}).get("no_direct_chroma_write_bypass_assertion_path")
    if ap is not None:
        assertion_ref = _repo_rel(repo_root, Path(ap)) if isinstance(ap, Path) else str(ap)

    return {
        "schema_version": SCHEMA_EVIDENCE_PACKAGE_V2,
        "generated_at_utc": _utc_now(),
        "producer": _CANONICAL_PRODUCER,
        "section_id": section_id,
        "run_id": run_id,
        "narrative_audit_root": _repo_rel(repo_root, artifact_dir),
        "integrated_run_ref": _repo_rel(repo_root, integrated_dir) if integrated_dir else None,
        "correlation_method": correlation_method,
        "correlation_missing_reason": correlation_missing_reason,
        "artifact_refs": {
            "section_l7_binding_manifest": "section_l7_binding_manifest.json",
            "spine_subphase_coverage_index": SUBPHASE_COVERAGE_INDEX_ARTIFACT,
            "artifact_inventory": "artifact_inventory.json",
            "run_bundle_index": "RUN_BUNDLE_INDEX.json",
            "run_links": RUN_LINKS_LANE_FILENAME,
            "section_runtime_proof_bundle": "section_runtime_proof_bundle.json",
            "no_direct_chroma_write_bypass_assertion": "no_direct_chroma_write_bypass_assertion.json",
            "r1b_governed_receipt_chain": "r1b_governed_receipt_chain.json",
        },
        "semantic_cache_persistence_status": sc_status,
        "semantic_cache_persistence_slots": sc_slots_doc.get("slots") or {},
        "semantic_cache_persistence_slot_schema": sc_slots_doc.get("schema_version"),
        "chroma_semantic_cache_classification": chroma_class,
        "no_direct_chroma_write_bypass_assertion_ref": assertion_ref,
        "r1b_governed_receipt_chain_ref": "r1b_governed_receipt_chain.json",
        "commit_request_status": (
            str((r1b_governed_receipt_chain or {}).get("commit_request_status") or "")
            or (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get("commit_request_status")
        ),
        "uwg_validation_status": (r1b_governed_receipt_chain or {}).get("uwg_validation_status"),
        "uwg_commit_or_block_status": (r1b_governed_receipt_chain or {}).get(
            "uwg_commit_or_block_status"
        ),
        "l4_object_ref_status": (r1b_governed_receipt_chain or {}).get("l4_object_ref_status"),
        "read_surface_refresh_status": (r1b_governed_receipt_chain or {}).get(
            "read_surface_refresh_status"
        ),
        "chroma_projection_status": (r1b_governed_receipt_chain or {}).get(
            "chroma_projection_status"
        ),
        "r1b_governed_receipt_chain_reason": (r1b_governed_receipt_chain or {}).get("reason"),
        "uwg_durable_write_chain_present": bool(
            (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get("uwg_path_present")
        ),
        "durable_semantic_cache_proof_present": bool(
            (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get(
                "governed_chroma_refresh_proven"
            )
        ),
        "read_surface_refresh_complete": bool(
            (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get(
                "read_surface_refresh_complete"
            )
            or (r1b_governed_receipt_chain or {}).get("read_surface_refresh_complete")
        ),
        "chroma_projection_complete": bool(
            (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get(
                "chroma_projection_complete"
            )
            or (r1b_governed_receipt_chain or {}).get("chroma_projection_complete")
        ),
        "durable_vector_persistence_proven": bool(
            (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get(
                "durable_vector_persistence_proven"
            )
            or (r1b_governed_receipt_chain or {}).get("durable_vector_persistence_proven")
        ),
        "r1b_uwg_chain_core_complete": bool(
            (semantic_cache_quarantine or {}).get("uwg_assessment", {}).get(
                "r1b_uwg_chain_core_complete"
            )
        ),
        "owner_class_summary": owner_summary,
        "verified_external_refs": verified_external_refs,
        "imported_core_evidence_snapshots": imported_snapshots,
        "missing_core_surfaces": sorted(set(missing_core)),
        "proof_classification": binding_manifest.get("proof_classification"),
        "shadow_path_quarantine": binding_manifest.get("shadow_path_quarantine") or {},
        "shadow_paths_present": bool(binding_manifest.get("shadow_paths_present")),
        "product_certification_impact": binding_manifest.get("product_certification_impact"),
        "explicit_non_claims": list(
            dict.fromkeys(
                [
                    *(binding_manifest.get("explicit_non_claims") or []),
                    *(subphase_index.get("explicit_non_claims") or []),
                    "evidence_package_index is the single-folder audit entrypoint",
                    "no semantic cache persistence claimed",
                    "no Chroma persistence claimed",
                    "no 99 RuntimeProofBundle claimed",
                    *(
                        (binding_manifest.get("shadow_path_quarantine") or {}).get(
                            "explicit_non_claims"
                        )
                        or []
                    ),
                    *(
                        sc_slots_doc.get("explicit_non_claims") or []
                    ),
                    *(
                        ((semantic_cache_quarantine or {}).get("no_direct_chroma_write_bypass_assertion") or {}).get(
                            "explicit_non_claims"
                        )
                        or []
                    ),
                    "core D2 Chroma upsert is NON_DURABLE_INDEX_WRITE unless governed UWG refresh chain proven",
                ]
            )
        ),
    }


def _patch_lane_run_bundle_index(
    artifact_dir: Path,
    *,
    verified_external_refs: list[dict[str, Any]],
    integrated_dir: Path | None,
    evidence_package_ref: str,
    correlation_method: str | None = None,
    correlation_missing_reason: str | None = None,
) -> None:
    from apps_rg.runtime.run_bundle_index import RUN_BUNDLE_INDEX_FILENAME

    idx_path = artifact_dir / RUN_BUNDLE_INDEX_FILENAME
    if not idx_path.is_file():
        return
    doc = _load_json(idx_path)
    if not doc:
        return
    doc["evidence_package_index_ref"] = evidence_package_ref
    doc["verified_external_refs"] = verified_external_refs
    doc["imported_core_evidence_snapshots"] = []
    doc["correlation_method"] = correlation_method
    doc["correlation_missing_reason"] = correlation_missing_reason
    if integrated_dir is not None:
        doc["correlated_integrated_run_id"] = integrated_dir.name
    _wg.write_text(idx_path, json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_binding_manifest_with_correlation(
    binding_manifest: dict[str, Any],
    *,
    correlation: IntegratedCorrelationResult,
    verified_external_refs: list[dict[str, Any]],
    repo_root: Path,
) -> dict[str, Any]:
    """Patch binding manifest fields after W4 correlation (refs-only; no L7 emit)."""
    doc = dict(binding_manifest)
    integrated = correlation.integrated_dir
    doc["integrated_run_ref"] = _repo_rel(repo_root, integrated) if integrated else None
    doc["correlation_method"] = correlation.correlation_method
    doc["correlation_missing_reason"] = correlation.correlation_missing_reason
    doc["verified_external_refs"] = verified_external_refs
    doc["imported_core_evidence_snapshots"] = []

    design_law_owner = dict(doc.get("design_law_owner_classifications") or {})
    artifact_classifications = dict(doc.get("artifact_classifications") or {})
    l7_artifact_refs = dict(doc.get("l7_artifact_refs") or {})
    l7_emitted_flags = {
        "agentic_core_how_trace.json": bool(doc.get("l7_how_trace_emitted")),
        "agentic_core_l7_route_family_coverage.json": bool(
            doc.get("l7_route_family_coverage_emitted")
        ),
        "agentic_core_spine_proof.json": bool(doc.get("l7_spine_proof_emitted")),
    }
    for ref in verified_external_refs:
        fname = str(ref.get("artifact_name") or "")
        if fname not in W4_VERIFIED_EXTERNAL_ARTIFACTS:
            continue
        if ref.get("trust_status") == "trusted":
            design_law_owner[fname] = OWNER_VERIFIED_EXTERNAL_REF
            artifact_classifications[fname] = "CORE_L7_REF"
            l7_artifact_refs[fname] = ref.get("source_path")
            if fname in l7_emitted_flags:
                l7_emitted_flags[fname] = True
        else:
            design_law_owner[fname] = OWNER_DRIFT
            artifact_classifications[fname] = OWNER_DRIFT
            l7_artifact_refs[fname] = ref.get("source_path")

    doc["design_law_owner_classifications"] = design_law_owner
    doc["artifact_classifications"] = artifact_classifications
    doc["l7_artifact_refs"] = l7_artifact_refs
    doc["l7_how_trace_emitted"] = l7_emitted_flags["agentic_core_how_trace.json"]
    doc["l7_route_family_coverage_emitted"] = l7_emitted_flags[
        "agentic_core_l7_route_family_coverage.json"
    ]
    doc["l7_spine_proof_emitted"] = l7_emitted_flags["agentic_core_spine_proof.json"]
    from apps_rg.runtime.section_l7_binding_manifest import DEFAULT_MISSING_L7_SURFACES

    missing_l7: list[str] = []
    for name in DEFAULT_MISSING_L7_SURFACES:
        if name in l7_emitted_flags:
            if not l7_emitted_flags[name]:
                missing_l7.append(name)
            continue
        if not any(
            r.get("artifact_name") == name and r.get("trust_status") == "trusted"
            for r in verified_external_refs
        ):
            missing_l7.append(name)
    doc["missing_l7_surfaces"] = missing_l7
    primary_l7 = all(l7_emitted_flags.values())
    doc["integrated_l7_invoked"] = primary_l7 and integrated is not None
    l7_untrusted = [u for u in doc.get("l7_untrusted_artifacts") or [] if isinstance(u, dict)]
    from apps_rg.runtime.section_l7_binding_manifest import _proof_classification

    doc["proof_classification"] = _proof_classification(
        integrated_l7_invoked=bool(doc.get("integrated_l7_invoked")),
        l7_trusted_count=sum(1 for v in l7_emitted_flags.values() if v),
        l7_untrusted=[str(u.get("artifact") or "") for u in l7_untrusted],
        runtime_proof_bundle_99_emitted=bool(doc.get("runtime_proof_bundle_99_emitted")),
    )
    return doc


def finalize_section_evidence_package(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    binding_manifest: dict[str, Any],
    correlation_id: str | None = None,
    correlation: IntegratedCorrelationResult | None = None,
) -> dict[str, Any]:
    """Write RUN_LINKS, subphase index, evidence package index; return summary for callers."""
    corr = correlation or discover_integrated_correlation(
        repo_root, artifact_dir, section_id=section_id
    )
    integrated = corr.integrated_dir
    verified = (
        build_verified_external_refs_for_integrated(
            repo_root, integrated, section_artifact_dir=artifact_dir
        )
        if integrated is not None
        else []
    )
    imported: list[dict[str, Any]] = []
    binding_synced = sync_binding_manifest_with_correlation(
        binding_manifest,
        correlation=corr,
        verified_external_refs=verified,
        repo_root=repo_root,
    )
    _wg.write_text(
        artifact_dir / "section_l7_binding_manifest.json",
        json.dumps(binding_synced, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    links_doc = build_lane_run_links_document(
        repo_root,
        artifact_dir,
        section_id=section_id,
        run_id=run_id,
        integrated_dir=integrated,
        correlation_id=correlation_id,
        correlation_method=corr.correlation_method,
        correlation_missing_reason=corr.correlation_missing_reason,
    )
    _wg.write_text(
        artifact_dir / RUN_LINKS_LANE_FILENAME,
        json.dumps(links_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    subphase_doc = build_spine_subphase_coverage_index(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        verified_external_refs=verified,
        integrated_dir=integrated,
    )
    _wg.write_text(
        artifact_dir / SUBPHASE_COVERAGE_INDEX_ARTIFACT,
        json.dumps(subphase_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    from apps_rg.cache.r1b_governed_receipt_emission import emit_section_r1b_governed_receipt_chain
    from apps_rg.runtime.semantic_cache_persistence_quarantine import finalize_semantic_cache_quarantine

    r1b_chain = emit_section_r1b_governed_receipt_chain(
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
    )

    sc_quarantine = finalize_semantic_cache_quarantine(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        integrated_dir=integrated,
    )

    pkg = build_evidence_package_index(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        binding_manifest=binding_synced,
        subphase_index=subphase_doc,
        verified_external_refs=verified,
        imported_snapshots=imported,
        integrated_dir=integrated,
        correlation_method=corr.correlation_method,
        correlation_missing_reason=corr.correlation_missing_reason,
        semantic_cache_quarantine=sc_quarantine,
        r1b_governed_receipt_chain=r1b_chain.to_dict(),
    )
    _wg.write_text(
        artifact_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT,
        json.dumps(pkg, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    _patch_lane_run_bundle_index(
        artifact_dir,
        verified_external_refs=verified,
        integrated_dir=integrated,
        evidence_package_ref=EVIDENCE_PACKAGE_INDEX_ARTIFACT,
        correlation_method=corr.correlation_method,
        correlation_missing_reason=corr.correlation_missing_reason,
    )

    return {
        "evidence_package_index_path": artifact_dir / EVIDENCE_PACKAGE_INDEX_ARTIFACT,
        "subphase_coverage_index_path": artifact_dir / SUBPHASE_COVERAGE_INDEX_ARTIFACT,
        "run_links_path": artifact_dir / RUN_LINKS_LANE_FILENAME,
        "binding_manifest_path": artifact_dir / "section_l7_binding_manifest.json",
        "verified_external_refs": verified,
        "imported_core_evidence_snapshots": imported,
        "integrated_run_dir": integrated,
        "correlation_method": corr.correlation_method,
        "correlation_missing_reason": corr.correlation_missing_reason,
        "certification_reference_hints": build_certification_reference_hints(repo_root),
        "semantic_cache_quarantine": sc_quarantine,
        "no_direct_chroma_write_bypass_assertion_path": sc_quarantine.get(
            "no_direct_chroma_write_bypass_assertion_path"
        ),
        "chroma_semantic_cache_classification": sc_quarantine.get("chroma_classification"),
        "semantic_cache_persistence_status": (
            sc_quarantine.get("semantic_cache_persistence_slots") or {}
        ).get("semantic_cache_persistence_status"),
        "r1b_governed_receipt_chain": r1b_chain.to_dict(),
        "commit_request_status": r1b_chain.commit_request_status,
        "uwg_validation_status": r1b_chain.uwg_validation_status,
        "uwg_commit_or_block_status": r1b_chain.uwg_commit_or_block_status,
        "l4_object_ref_status": r1b_chain.l4_object_ref_status,
        "read_surface_refresh_status": r1b_chain.read_surface_refresh_status,
        "chroma_projection_status": r1b_chain.chroma_projection_status,
    }


__all__ = [
    "EVIDENCE_PACKAGE_INDEX_ARTIFACT",
    "REF_KIND_IMPORTED_SNAPSHOT",
    "REF_KIND_VERIFIED_EXTERNAL",
    "RUN_LINKS_LANE_FILENAME",
    "SCHEMA_EVIDENCE_PACKAGE_V2",
    "SCHEMA_SUBPHASE_COVERAGE_V1",
    "SUBPHASE_COVERAGE_INDEX_ARTIFACT",
    "OWNER_APP_BINDING_MANIFEST",
    "OWNER_APP_DOMAIN_EVIDENCE",
    "OWNER_APP_SHIM",
    "OWNER_CORE_L7_PROJECTION",
    "OWNER_CORE_99_PROOF",
    "OWNER_DESIGN_ONLY",
    "OWNER_DRIFT",
    "OWNER_MISSING",
    "OWNER_NOT_APPLICABLE",
    "OWNER_VERIFIED_EXTERNAL_REF",
    "assert_evidence_ref_shape",
    "build_evidence_package_index",
    "build_evidence_ref_record",
    "build_lane_run_links_document",
    "build_spine_subphase_coverage_index",
    "build_verified_external_refs_for_integrated",
    "design_law_owner_for_artifact",
    "CORRELATED_CLI_RUN_ENV",
    "IntegratedCorrelationResult",
    "build_correlation_missing_reason",
    "discover_correlated_integrated_run",
    "discover_integrated_correlation",
    "finalize_section_evidence_package",
    "sync_binding_manifest_with_correlation",
]
