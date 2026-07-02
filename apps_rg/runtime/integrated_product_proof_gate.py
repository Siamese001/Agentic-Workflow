"""Integrated-R4 whole-run product proof gate — canonical ``python -m apps_rg`` only."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from apps_rg.cache.cache_preflight_evidence import (
    CACHE_MISS_RECEIPT_NAME,
    CACHE_PREFLIGHT_MANIFEST_NAME,
)
from apps_rg.runtime.section_spine_terminology import (
    BINDING_CLASSIFICATION_FEC_SHAPE_ONLY,
    BINDING_CLASSIFICATION_FULL_C03,
    BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT,
)
from apps_rg.runtime.native_c03_skills_graph import validate_native_c03_contract
from apps_rg.runtime.non_product_proof_stamp import (
    CI_LANE_DEV_HARNESS_CLASSIFICATION,
    DEMO_HARNESS_PROOF_CLASSIFICATION,
    NON_PRODUCT_PROOF_CLASSIFICATIONS,
    ORCHESTRATOR_PROOF_CLASSIFICATION,
    PACKAGE_DISPOSITION_CLASSIFICATION,
    SECTION_L7_CORRELATION_CLASSIFICATION,
)

INTEGRATED_R4_PRODUCT_CLASSIFICATION = "INTEGRATED_R4_PRODUCT_RUNTIME"
CONTRACT_TEST_ONLY_CLASSIFICATION = "CONTRACT_TEST_PROOF"
CANONICAL_ENTRYPOINT_CMD = "python -m apps_rg"

REJECTED_NON_PRODUCT_CLASSIFICATIONS: frozenset[str] = frozenset(
    NON_PRODUCT_PROOF_CLASSIFICATIONS
    | {
        ORCHESTRATOR_PROOF_CLASSIFICATION,
        PACKAGE_DISPOSITION_CLASSIFICATION,
        DEMO_HARNESS_PROOF_CLASSIFICATION,
        CI_LANE_DEV_HARNESS_CLASSIFICATION,
        SECTION_L7_CORRELATION_CLASSIFICATION,
        "MOCK_PROOF",
        "FIXTURE_PROOF",
        "OFFLINE_STUB_PROOF",
        "CONTRACT_TEST_PROOF",
        "PLUMBING_ONLY",
        "OFFLINE_CONTRACT_STUB",
    }
)

PRODUCT_CLAIM_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("product_certification", ("CERTIFIED", "PASS", "CLAIMED")),
    ("l7_certification", ("CERTIFIED", "PASS", "CLAIMED")),
    ("fort_knox_certification", ("CERTIFIED", "PASS", "CLAIMED")),
    ("proof_classification", ("LIVE_RUNTIME_PROOF", "RELEASE_ELIGIBLE_PROOF")),
)

_REQUIRED_ARTIFACTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("agentic_core_how_trace.json", ("agentic_core_how_trace.json",)),
    ("agentic_core_spine_proof.json", ("agentic_core_spine_proof.json",)),
    (
        "agentic_core_l7_route_family_coverage.json",
        ("agentic_core_l7_route_family_coverage.json",),
    ),
    (
        "integrated_run_manifest",
        ("r4_run_manifest.json", "run_manifest.json", "integrated_runtime_artifact_manifest.json"),
    ),
    ("route_contract.json", ("route_contract.json",)),
    (
        "exit_disposition_receipt",
        (
            "exit_disposition_receipt.json",
            "x3_disposition_receipt.json",
            "exit_disposition_receipt.json",
        ),
    ),
    ("runtime_exhaust_bundle.json", ("runtime_exhaust_bundle.json",)),
)


@dataclass
class ProductProofValidationResult:
    status: str
    proof_classification: str
    canonical_entrypoint: bool
    integrated_r4_invoked: bool
    section_mode: bool
    required_artifacts_present: dict[str, bool] = field(default_factory=dict)
    required_artifacts_missing: list[str] = field(default_factory=list)
    rejected_non_product_classifications: list[str] = field(default_factory=list)
    exit_x3_present: bool = False
    package_x3_only: bool = False
    no_bypass_assertions_present: bool = False
    cache_preflight_evidence_present: bool = False
    fact_vector_writeback_evidence_present: bool = False
    fact_vector_writeback_status: str = ""
    explicit_non_claims: list[str] = field(default_factory=list)
    decisive_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else None
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


def _flatten_strings(obj: Any, out: list[str]) -> None:
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _flatten_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _flatten_strings(v, out)


def _collect_json_blobs(run_dir: Path, *, max_depth: int = 3) -> list[dict[str, Any]]:
    run_dir = run_dir.resolve()
    blobs: list[dict[str, Any]] = []
    for sub in run_dir.rglob("*.json"):
        if len(sub.relative_to(run_dir).parts) > max_depth:
            continue
        doc = _load_json(sub)
        if doc is not None:
            blobs.append(doc)
    return blobs


def _resolve_artifact_paths(run_dir: Path) -> dict[str, Path | None]:
    run_dir = run_dir.resolve()
    found: dict[str, Path | None] = {key: None for key, _ in _REQUIRED_ARTIFACTS}
    candidates: list[Path] = []
    for p in [run_dir, *run_dir.rglob("*")]:
        if p.is_file() and p.suffix.lower() == ".json":
            candidates.append(p)
    for key, names in _REQUIRED_ARTIFACTS:
        hits: list[Path] = []
        for name in names:
            for c in candidates:
                if c.name == name:
                    hits.append(c)
        if hits:
            hits.sort(key=lambda p: len(p.relative_to(run_dir).parts))
            found[key] = hits[0]
    # Section runs may reference integrated dir via manifest.
    for name in ("section_l7_binding_manifest.json", "evidence_package_index.json"):
        m = _load_json(run_dir / name)
        if not m:
            continue
        ref = str(m.get("integrated_run_ref") or "").strip()
        if ref:
            base = run_dir
            for parent in [run_dir, *run_dir.parents]:
                try:
                    integrated = (parent / ref).resolve()
                    if integrated.is_dir():
                        base = integrated
                        break
                except (OSError, ValueError):
                    continue
            sub = _resolve_artifact_paths(base)
            for k, pth in sub.items():
                if found[k] is None and pth is not None:
                    found[k] = pth
    return found


def _harvest_classifications(blobs: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for blob in blobs:
        for key in ("proof_classification", "package_disposition_classification"):
            val = blob.get(key)
            if isinstance(val, str) and val.strip():
                found.add(val.strip())
        texts: list[str] = []
        _flatten_strings(blob, texts)
        for t in texts:
            for token in REJECTED_NON_PRODUCT_CLASSIFICATIONS:
                if token in t:
                    found.add(token)
    return found


def _invalid_binding_classification_claims(blobs: list[dict[str, Any]]) -> list[str]:
    """Reject mislabeled C0.3 or section-local bindings posing as product proof."""
    reasons: list[str] = []
    for blob in blobs:
        bc = str(blob.get("binding_classification") or "")
        if bc == BINDING_CLASSIFICATION_FULL_C03:
            ok, missing = validate_native_c03_contract(blob)
            if not ok:
                reasons.append(f"false_full_c03:{','.join(missing)}")
        elif bc in (
            BINDING_CLASSIFICATION_SECTION_GRAPH_CONTEXT,
            BINDING_CLASSIFICATION_FEC_SHAPE_ONLY,
        ):
            if blob.get("can_satisfy_integrated_product_proof") or blob.get("product_proof_eligible"):
                reasons.append(f"section_binding_product_claim:{bc}")
        if blob.get("fec_shape_only") and blob.get("canonical_c0_3_claimed"):
            reasons.append("fec_shape_claims_full_c03")
    return reasons


def _detect_section_mode(run_dir: Path, blobs: list[dict[str, Any]]) -> bool:
    whole_run_markers = (
        run_dir / "r4_run_manifest.json",
        run_dir / "spine_run_manifest.json",
        run_dir / "integrated_runtime_artifact_manifest.json",
    )
    whole_run_layout = (run_dir / "lanes").is_dir() or (run_dir / "modular_r4" / "sections").is_dir()
    if whole_run_layout and any(marker.is_file() for marker in whole_run_markers):
        return False
    if (run_dir / "section_l7_binding_manifest.json").is_file():
        return True
    for blob in blobs:
        if str(blob.get("section_id") or "").strip():
            return True
        cmd = str(blob.get("command") or blob.get("command_surface") or "")
        if "--section" in cmd or "python -m apps_rg --section" in cmd:
            return True
        pc = str(blob.get("proof_classification") or "")
        if pc.startswith("SECTION_") or pc in REJECTED_NON_PRODUCT_CLASSIFICATIONS:
            if pc.startswith("SECTION_"):
                return True
    parts = run_dir.as_posix().lower()
    if "/runtime_proofs/" in parts and "/runs/" not in parts:
        return True
    return False


def _detect_canonical_entrypoint(blobs: list[dict[str, Any]]) -> bool:
    for blob in blobs:
        cmd = str(blob.get("command") or "")
        if "python -m apps_rg" in cmd and "--section" not in cmd:
            return True
        inv = blob.get("payload") if isinstance(blob.get("payload"), dict) else blob
        if isinstance(inv, dict):
            ep = str(inv.get("entry_point") or inv.get("canonical_entrypoint") or "")
            if "apps_rg" in ep and "dispatch_apps_rg" in ep:
                return True
            if inv.get("integrated_runtime_entrypoint_used") is True and "apps_rg" in str(
                inv.get("namespace") or ""
            ):
                return True
    for blob in blobs:
        if blob.get("apps_rg_product_outcome_authorized") is not None:
            return True
        if blob.get("apps_rg_generation_status"):
            return True
    return False


def _detect_cache_preflight_evidence(run_dir: Path, blobs: list[dict[str, Any]]) -> bool:
    """Whole-run product proof requires R1A/R1B preflight receipts in the run dir."""
    for name in (CACHE_PREFLIGHT_MANIFEST_NAME, CACHE_MISS_RECEIPT_NAME):
        if (run_dir / name).is_file():
            return True
    for blob in blobs:
        if blob.get("cache_preflight_completed") is True:
            return True
        if blob.get("whole_run_cache_preflight"):
            return True
    return False


def _fact_vector_writeback_blockers(run_dir: Path) -> tuple[list[str], bool, str]:
    """Require UWG + live Chroma retrieval proof when grounded rows were staged."""
    blockers: list[str] = []
    grounded_receipt_present = False
    completion_status = ""

    for path in run_dir.rglob("c02_fact_vectors_ingest_receipt.json"):
        doc = _load_json(path) or {}
        staged = int(doc.get("staged_count") or 0)
        promoted = int((doc.get("promotion") or {}).get("promoted_count") or 0)
        if staged > 0 or promoted > 0:
            grounded_receipt_present = True
        status = str(doc.get("status") or "")
        if staged > 0 and status == "FAIL":
            blockers.append(f"fact_vector_ingest_failed:{path.relative_to(run_dir).as_posix()}")

    completion = _load_json(run_dir / "apps_rg_post_x3_completion_receipt.json") or {}
    fv_completion = (
        completion.get("fact_vector_writeback")
        if isinstance(completion.get("fact_vector_writeback"), dict)
        else {}
    )
    if isinstance(fv_completion, dict) and fv_completion:
        completion_status = str(fv_completion.get("status") or "")
        if completion_status == "FAIL":
            blockers.append("fact_vector_writeback_completion_failed")

    if not grounded_receipt_present:
        return blockers, False, completion_status or "NOT_APPLICABLE"

    passing_promotions = 0
    for path in run_dir.rglob("fact_vector_promotion_receipt.json"):
        doc = _load_json(path) or {}
        if int(doc.get("promoted_count") or 0) <= 0 and str(doc.get("status") or "") != "PASS":
            continue
        status = str(doc.get("status") or "")
        uwg_status = str((doc.get("uwg") or {}).get("status") or "")
        retrieval_status = str((doc.get("retrieval_proof") or {}).get("status") or "")
        projection_status = str((doc.get("live_projection") or {}).get("status") or "")
        if status == "PASS" and uwg_status == "ADMITTED" and retrieval_status == "PASS":
            passing_promotions += 1
        else:
            rel = path.relative_to(run_dir).as_posix()
            blockers.append(
                "fact_vector_promotion_chain_incomplete:"
                f"{rel}:status={status}:uwg={uwg_status}:projection={projection_status}:retrieval={retrieval_status}"
            )

    if passing_promotions <= 0:
        blockers.append("fact_vector_writeback_promotion_proof_missing")
    return blockers, True, completion_status or ("PASS" if not blockers else "FAIL")


def _detect_integrated_r4(blobs: list[dict[str, Any]], paths: dict[str, Path | None]) -> bool:
    if paths.get("integrated_run_manifest") is not None:
        inv = _load_json(paths["integrated_run_manifest"]) if paths["integrated_run_manifest"] else None
        if inv and (
            "r4_run_manifest" in str(paths["integrated_run_manifest"])
            or inv.get("apps_rg_generation_status")
            or inv.get("chain_kind")
        ):
            return True
    for blob in blobs:
        pay = blob.get("payload") if isinstance(blob.get("payload"), dict) else {}
        if isinstance(pay, dict) and pay.get("integrated_runtime_entrypoint_used") is True:
            return True
        if blob.get("integrated_runtime_entrypoint_used") is True:
            return True
        if "integrated_runtime_artifact_manifest" in blob.get("artifact_filenames", []):
            return True
    if paths.get("agentic_core_how_trace.json") and paths.get("agentic_core_spine_proof.json"):
        return True
    return False


def _has_no_bypass_assertions(paths: dict[str, Path | None]) -> bool:
    how = paths.get("agentic_core_how_trace.json")
    if how is None:
        return False
    doc = _load_json(how)
    if not doc:
        return False
    pay = doc.get("payload") if isinstance(doc.get("payload"), dict) else doc
    if not isinstance(pay, dict):
        return False
    stages = pay.get("stages") or []
    if not isinstance(stages, list):
        return False
    for st in stages:
        if not isinstance(st, dict):
            continue
        assertions = st.get("forbidden_action_assertions") or st.get("no_bypass_assertions")
        if isinstance(assertions, list) and assertions:
            return True
    exhaust = paths.get("runtime_exhaust_bundle.json")
    if exhaust is not None:
        ex = _load_json(exhaust)
        if ex and ("no_bypass" in json.dumps(ex).lower() or "forbidden_action" in json.dumps(ex).lower()):
            return True
    return False


def _live_product_outcome_blockers(run_dir: Path, paths: dict[str, Path | None]) -> list[str]:
    """Block live product proof when apps_rg integrated run artifacts deny product outcome."""
    blockers: list[str] = []
    r4_path = paths.get("integrated_run_manifest")
    r4 = _load_json(r4_path) if r4_path is not None else None
    apps_rg_run = bool(
        r4
        and (
            r4.get("apps_rg_product_outcome_authorized") is not None
            or r4.get("apps_rg_generation_status")
            or str(r4.get("route_id") or "").startswith("apps_rg.")
        )
    )
    if not apps_rg_run:
        return blockers
    if r4.get("apps_rg_product_outcome_authorized") is False:
        blockers.append("apps_rg_product_outcome_authorized_false")
    fault = str(r4.get("l2_fault") or "").strip()
    if fault:
        blockers.append(f"l2_fault:{fault[:160]}")
    x3 = str(r4.get("x3_disposition") or "").strip()
    if x3 and x3 not in {"X3_ALLOW", "ALLOW"}:
        blockers.append(f"integrated_x3_disposition:{x3}")
    for name in ("x3_disposition_receipt.json", "exit_disposition_receipt.json"):
        x3_path = run_dir / name
        if not x3_path.is_file():
            continue
        x3_doc = _load_json(x3_path) or {}
        pay = x3_doc.get("payload") if isinstance(x3_doc.get("payload"), dict) else x3_doc
        disp = pay.get("disposition") or pay.get("x3_disposition")
        if isinstance(disp, dict):
            code = str(disp.get("x3_code") or disp.get("disposition") or "")
        else:
            code = str(disp or "")
        if code and code not in {"X3_ALLOW", "ALLOW"}:
            blockers.append(f"integrated_exit_x3:{code}")
        break
    spine_path = run_dir / "agentic_core_spine_proof.json"
    if spine_path.is_file():
        spine = _load_json(spine_path) or {}
        status = str(spine.get("agentic_core_spine_status") or "")
        if "BLOCKED" in status or "MISSING" in status:
            blockers.append(f"spine_status:{status}")
        gaps = spine.get("blocking_gaps")
        if isinstance(gaps, list) and gaps:
            blockers.append("spine_proof_blocking_gaps")
    return blockers


def _exit_x3_and_package_flags(paths: dict[str, Path | None], run_dir: Path) -> tuple[bool, bool]:
    exit_names = {
        "exit_disposition_receipt.json",
        "x3_disposition_receipt.json",
    }
    exit_present = any(
        (run_dir / n).is_file() or (paths.get("exit_disposition_receipt") is not None) for n in exit_names
    )
    package_present = (run_dir / "resume_package_x3_disposition.json").is_file() or any(
        p.name == "resume_package_x3_disposition.json" for p in run_dir.rglob("resume_package_x3_disposition.json")
    )
    package_only = package_present and not exit_present
    return exit_present, package_only


def validate_integrated_product_proof(
    run_dir: Path,
    *,
    require_canonical_command_evidence: bool = True,
) -> ProductProofValidationResult:
    """Validate run_dir for integrated-R4 product / L7 / Fort Knox proof claims."""
    run_dir = Path(run_dir)
    explicit_non_claims = [
        "section-only runs are lane-dev only",
        "package X3 is not Exit X3",
        "offline rollup and demo harnesses are non-product",
        "section L7 refs are correlation-only unless inside integrated whole-run dir",
    ]
    if not run_dir.is_dir():
        return ProductProofValidationResult(
            status="FAIL",
            proof_classification="MISSING_RUN_DIR",
            canonical_entrypoint=False,
            integrated_r4_invoked=False,
            section_mode=False,
            explicit_non_claims=explicit_non_claims,
            decisive_reason=f"run_dir not found: {run_dir}",
        )

    blobs = _collect_json_blobs(run_dir)
    paths = _resolve_artifact_paths(run_dir)
    classifications = _harvest_classifications(blobs)
    rejected = sorted(classifications & REJECTED_NON_PRODUCT_CLASSIFICATIONS)

    present_map: dict[str, bool] = {}
    missing: list[str] = []
    for key, _names in _REQUIRED_ARTIFACTS:
        ok = paths.get(key) is not None
        present_map[key] = ok
        if not ok:
            missing.append(key)

    section_mode = _detect_section_mode(run_dir, blobs)
    integrated_r4 = _detect_integrated_r4(blobs, paths)
    canonical = _detect_canonical_entrypoint(blobs)
    exit_x3, package_only = _exit_x3_and_package_flags(paths, run_dir)
    no_bypass = _has_no_bypass_assertions(paths)
    cache_preflight_ok = _detect_cache_preflight_evidence(run_dir, blobs)
    fact_vector_blockers, fact_vector_present, fact_vector_status = _fact_vector_writeback_blockers(run_dir)

    if section_mode:
        explicit_non_claims.append("section_mode=true: --section cannot satisfy product proof")
    if package_only:
        explicit_non_claims.append("package_x3_only: package rollup is not Exit X3")
    if rejected:
        explicit_non_claims.append(f"rejected_non_product_classifications={rejected}")

    binding_violations = _invalid_binding_classification_claims(blobs)

    hard_fail_reasons: list[str] = []
    if section_mode:
        hard_fail_reasons.append("section_mode")
    if binding_violations:
        hard_fail_reasons.append(f"binding_classification:{';'.join(binding_violations)}")
    if rejected:
        hard_fail_reasons.append("non_product_classification")
    if package_only:
        hard_fail_reasons.append("package_x3_only")
    if not integrated_r4:
        hard_fail_reasons.append("integrated_r4_not_invoked")
    if missing:
        hard_fail_reasons.append(f"missing_artifacts:{','.join(missing)}")
    if not exit_x3:
        hard_fail_reasons.append("exit_x3_missing")
    if not no_bypass:
        hard_fail_reasons.append("no_bypass_assertions_missing")
    if not section_mode and not cache_preflight_ok:
        hard_fail_reasons.append("cache_preflight_evidence_missing")
    if not section_mode and fact_vector_blockers:
        hard_fail_reasons.append(f"fact_vector_writeback:{';'.join(fact_vector_blockers)}")

    live_blockers = _live_product_outcome_blockers(run_dir, paths)
    if live_blockers:
        explicit_non_claims.append(f"live_product_blockers={live_blockers}")

    if hard_fail_reasons:
        return ProductProofValidationResult(
            status="FAIL",
            proof_classification="INTEGRATED_PRODUCT_PROOF_REJECTED",
            canonical_entrypoint=canonical,
            integrated_r4_invoked=integrated_r4,
            section_mode=section_mode,
            required_artifacts_present=present_map,
            required_artifacts_missing=missing,
            rejected_non_product_classifications=rejected,
            exit_x3_present=exit_x3,
            package_x3_only=package_only,
            no_bypass_assertions_present=no_bypass,
            cache_preflight_evidence_present=cache_preflight_ok,
            fact_vector_writeback_evidence_present=fact_vector_present,
            fact_vector_writeback_status=fact_vector_status,
            explicit_non_claims=explicit_non_claims,
            decisive_reason="; ".join(hard_fail_reasons),
        )

    if live_blockers:
        return ProductProofValidationResult(
            status="BLOCKED",
            proof_classification=INTEGRATED_R4_PRODUCT_CLASSIFICATION,
            canonical_entrypoint=canonical,
            integrated_r4_invoked=integrated_r4,
            section_mode=False,
            required_artifacts_present=present_map,
            required_artifacts_missing=missing,
            rejected_non_product_classifications=rejected,
            exit_x3_present=exit_x3,
            package_x3_only=package_only,
            no_bypass_assertions_present=no_bypass,
            cache_preflight_evidence_present=cache_preflight_ok,
            fact_vector_writeback_evidence_present=fact_vector_present,
            fact_vector_writeback_status=fact_vector_status,
            explicit_non_claims=explicit_non_claims,
            decisive_reason="; ".join(live_blockers),
        )

    if not canonical:
        if not require_canonical_command_evidence:
            return ProductProofValidationResult(
                status="PASS",
                proof_classification=CONTRACT_TEST_ONLY_CLASSIFICATION,
                canonical_entrypoint=False,
                integrated_r4_invoked=integrated_r4,
                section_mode=False,
                required_artifacts_present=present_map,
                required_artifacts_missing=missing,
                rejected_non_product_classifications=rejected,
                exit_x3_present=exit_x3,
                package_x3_only=package_only,
                no_bypass_assertions_present=no_bypass,
                cache_preflight_evidence_present=cache_preflight_ok,
                fact_vector_writeback_evidence_present=fact_vector_present,
                fact_vector_writeback_status=fact_vector_status,
                explicit_non_claims=explicit_non_claims
                + [
                    "contract_test_only: missing canonical python -m apps_rg command evidence"
                ],
                decisive_reason="integrated_artifacts_present_without_canonical_entrypoint_evidence",
            )
        return ProductProofValidationResult(
            status="BLOCKED",
            proof_classification=INTEGRATED_R4_PRODUCT_CLASSIFICATION,
            canonical_entrypoint=False,
            integrated_r4_invoked=integrated_r4,
            section_mode=False,
            required_artifacts_present=present_map,
            required_artifacts_missing=missing,
            rejected_non_product_classifications=rejected,
            exit_x3_present=exit_x3,
            package_x3_only=package_only,
            no_bypass_assertions_present=no_bypass,
            cache_preflight_evidence_present=cache_preflight_ok,
            fact_vector_writeback_evidence_present=fact_vector_present,
            fact_vector_writeback_status=fact_vector_status,
            explicit_non_claims=explicit_non_claims,
            decisive_reason="canonical_entrypoint_evidence_missing",
        )

    return ProductProofValidationResult(
        status="PASS",
        proof_classification=INTEGRATED_R4_PRODUCT_CLASSIFICATION,
        canonical_entrypoint=True,
        integrated_r4_invoked=True,
        section_mode=False,
        required_artifacts_present=present_map,
        required_artifacts_missing=[],
        rejected_non_product_classifications=[],
        exit_x3_present=True,
        package_x3_only=False,
        no_bypass_assertions_present=no_bypass,
        cache_preflight_evidence_present=cache_preflight_ok,
        fact_vector_writeback_evidence_present=fact_vector_present,
        fact_vector_writeback_status=fact_vector_status,
        explicit_non_claims=explicit_non_claims,
        decisive_reason="integrated_r4_product_proof_preconditions_satisfied",
    )


def _receipt_asserts_product_claim(receipt: Mapping[str, Any]) -> bool:
    if receipt.get("release_eligible") is True:
        return True
    for field, allowed in PRODUCT_CLAIM_MARKERS:
        val = receipt.get(field)
        if isinstance(val, str) and val.strip().upper() in {a.upper() for a in allowed}:
            return True
    return False


def reject_non_integrated_product_claim(
    receipt: Mapping[str, Any] | None,
    *,
    run_dir: Path | None = None,
    context: str = "",
) -> None:
    """Raise ValueError when a receipt asserts product/L7/Fort Knox without integrated proof."""
    if not receipt or not isinstance(receipt, Mapping):
        return
    pc = str(receipt.get("proof_classification") or receipt.get("package_disposition_classification") or "")
    if pc in REJECTED_NON_PRODUCT_CLASSIFICATIONS:
        raise ValueError(
            f"{context or 'product_claim'}: non-product proof {pc!r} cannot satisfy product/L7/Fort Knox certification"
        )
    if not _receipt_asserts_product_claim(receipt):
        return
    if run_dir is None:
        raise ValueError(
            f"{context or 'product_claim'}: product/L7/Fort Knox claim requires run_dir for integrated validation"
        )
    result = validate_integrated_product_proof(Path(run_dir))
    if result.status != "PASS" or result.proof_classification != INTEGRATED_R4_PRODUCT_CLASSIFICATION:
        raise ValueError(
            f"{context or 'product_claim'}: {result.decisive_reason} "
            f"(status={result.status}, proof_classification={result.proof_classification})"
        )


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate integrated-R4 product proof preconditions for a run directory."
    )
    parser.add_argument("run_dir", type=Path, help="Artifact directory to inspect")
    parser.add_argument(
        "--allow-contract-test-only",
        action="store_true",
        help="Treat CONTRACT_TEST_PROOF without canonical command as exit 0 (not product).",
    )
    parser.add_argument("--json", action="store_true", help="Emit full result JSON")
    args = parser.parse_args(argv)
    result = validate_integrated_product_proof(
        args.run_dir,
        require_canonical_command_evidence=not args.allow_contract_test_only,
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(json.dumps({"status": result.status, "decisive_reason": result.decisive_reason}, indent=2))
    if result.status == "PASS":
        return 0
    if result.status == "BLOCKED":
        return 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
